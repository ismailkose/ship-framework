#!/usr/bin/env python3
"""Ship review helper — scope, validate, consolidate, freshness.

Used by /shipmate review (scope → reviewers → consolidate) and /shipmate launch (freshness).
Standard library only; Python 3.8+.

  review.py scope [--base REF | --since-review] [--depth quick|standard|full]
                  [--only crit,pol,...] [--case ID] [--json]
      Fingerprints the working tree, picks the base, lists reviewed paths, selects depth and
      reviewers, and creates a run folder with scope.json + diff.patch (base → exact snapshot).
  review.py validate FILE [FILE ...]
      Checks reviewer output against the schema in references/reviewer-output.schema.json.
  review.py consolidate RUN_DIR [--draft] [--mode isolated|single-context]
      Merges reviewer outputs: dedups by location + claim (merges recorded), applies
      Adversarial verdicts (disputes kept, both sides shown). --draft writes RUN_DIR/merged.json
      for the second wave; without it, writes the record to .ship/reviews/<run>.json + latest.json.
  review.py freshness [--record PATH] [--json]
      Current fingerprint vs the last review record → FRESH (exit 0) / STALE (1) / NO_REVIEW (3).
      Freshness only: it says nothing about whether the review was complete.
  review.py gate [--record PATH] [--json]
      What /shipmate launch checks: PASS (0) only when the last review is fresh, every selected
      reviewer completed on this snapshot, and no blocker is open. Otherwise STALE (1),
      INCOMPLETE (2), NO_REVIEW (3), or BLOCKERS (4).
  review.py fingerprint
      Prints the working-tree fingerprint (same as bin/review-fingerprint.sh).

Records live in .ship/reviews/ (created with its own .gitignore of `*`, so they're ignored by
default and never change the fingerprint). .ship/framework.yaml is the only managed file in
.ship/ — updates don't touch this folder.
"""

import argparse
import copy
import datetime as _dt
import importlib.util
import json
import os
import re
import glob
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FINGERPRINT_SH = os.path.join(HERE, "review-fingerprint.sh")
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

REVIEWERS = ["crit", "pol", "eye", "test", "adversarial"]
FIRST_WAVE = ["crit", "pol", "eye", "test"]
SEVERITIES = ["blocker", "major", "minor", "nit"]
SEV_RANK = {s: i for i, s in enumerate(SEVERITIES)}
VERDICTS = ["confirmed", "disputed", "needs-evidence"]
DIM_RESULTS = ["pass", "concerns", "not-checked", "not-applicable"]
CHECKED = ("pass", "concerns")
# The dimensions each reviewer's agent file declares; an unreported one is recorded as not-checked.
DECLARED_DIMENSIONS = {
    "pol": ["tokens", "components", "typography", "color", "spacing", "states", "copy", "motion"],
    "eye": ["layout", "sizes", "text scaling", "contrast", "states", "interaction", "dark mode"],
    "test": ["existing tests", "symptom reproduced / behaviour exercised", "regressions", "edge inputs"],
}
# A care pass (review --care): one lens per reviewer — care-lens.md. Declared like the review dimensions.
CARE_DIMENSIONS = {"crit": ["journey"], "pol": ["expression"], "eye": ["task walk"]}
CARE_REVIEWERS = ["crit", "pol", "eye"]
STATUSES = ["completed", "partial", "skipped"]
BANNED_KEYS = {"score", "health", "health_score", "confidence", "confidence_score",
               "readiness", "readiness_score", "rating"}

QUICK_MAX_LINES = 20
QUICK_MAX_FILES = 3
FULL_MIN_LINES = 200

# Consequence signals → full depth. Matched against changed paths (and added lines for CONTENT).
RISK_PATHS = [
    # "session" only as a whole web/server name (session.ts, sessions/): SessionListView or a Session.swift
    # model in a workout app isn't auth — native auth shows up in content (Keychain, SecItem, signIn).
    ("auth", r"(^|/)(auth|login|logout|signin|signup|oauth|password|keychain|credential)|(^|/)sessions?(/|\.(ts|tsx|js|jsx|mjs|go|py|rb|php|java)$)"),
    ("payments", r"(payment|billing|checkout|stripe|storekit|purchase|subscription|paywall|invoice|revenuecat)"),
    ("data", r"(migration|migrations/|schema|\.sql$|prisma|coredata|swiftdata|\.xcdatamodel|(^|/)db/|database|firestore\.rules|supabase/)"),
    ("navigation", r"(navigation|router|routes?[./]|(^|/)app/.*/(layout|page)\.(t|j)sx?$|deeplink|universal.?link|info\.plist$|androidmanifest\.xml$)"),
]
RISK_CONTENT = [
    ("auth", r"(Keychain|SecItem|signIn|signOut|jwt|bcrypt|setCookie|httpOnly|OAuth)"),
    ("payments", r"(StoreKit|Product\.purchase|stripe|PaymentIntent|RevenueCat|BillingClient)"),
    ("data", r"(ALTER TABLE|DROP TABLE|CREATE TABLE|\bmigrate\b|ModelContainer|NSPersistentContainer|deleteAll|\.delete\()"),
    ("navigation", r"(NavigationStack|NavigationPath|useRouter|router\.push|redirect\(|NavHost|navigate\()"),
]
RELEASE_BRANCH = r"(^|/)(release|hotfix|deploy)"

UI_EXT = (".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss", ".sass", ".less", ".html",
          ".xib", ".storyboard", ".svg", ".png", ".jpg", ".jpeg", ".webp")
UI_PATH = r"(view|screen|component|page|layout|theme|style|ui/|/ui|\.xcassets|res/layout|res/drawable|compose)"
DESIGN_FILES = ("design-model.yaml", "design/components.yaml", "DESIGN.md", "PDC.md", "TASTE.md")
TEST_PATH = r"(^|/)(tests?|__tests__|spec|e2e|fixtures?|\w*uitests?|\w+tests)(/|$)|(\.|_)(test|spec)\.[a-z]+$|tests?\.(swift|kt)$"
DOC_EXT = (".md", ".txt", ".rst")


# ── git plumbing ─────────────────────────────────────────────────────────

def git(args, check=True, cwd=None):
    p = subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       cwd=cwd, universal_newlines=True)
    if check and p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr.strip()))
    return p.stdout


def git_ok(args, cwd=None):
    return subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          cwd=cwd).returncode == 0


def toplevel():
    try:
        return git(["rev-parse", "--show-toplevel"]).strip()
    except RuntimeError:
        sys.exit("review: not inside a git repository")


def fingerprint():
    p = subprocess.run(["bash", FINGERPRINT_SH], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
    if p.returncode != 0:
        sys.exit("review: fingerprint failed: %s" % p.stderr.strip())
    return p.stdout.strip()


def rev(ref):
    out = subprocess.run(["git", "rev-parse", "--verify", "-q", ref], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, universal_newlines=True)
    return out.stdout.strip() if out.returncode == 0 else None


def object_exists(sha):
    return git_ok(["cat-file", "-e", sha])


def default_branch(current=None):
    """origin/HEAD, else main/master (local, then origin/) — never the current branch."""
    out = subprocess.run(["git", "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    cand = [out.stdout.strip()] if out.returncode == 0 and out.stdout.strip() else []
    cand += ["main", "master", "origin/main", "origin/master"]
    for b in cand:
        if b.split("/", 1)[-1] == current or b == current:
            continue
        if rev(b if b.startswith("origin/") else "refs/heads/" + b) or \
                (b.startswith("origin/") and rev("refs/remotes/" + b)):
            return b
    return None


def now():
    return _dt.datetime.now(_dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def records_dir(root):
    d = os.path.join(root, ".ship", "reviews")
    os.makedirs(d, exist_ok=True)
    gi = os.path.join(d, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w") as f:
            f.write("# Ship review records — local state, ignored by default.\n"
                    "# Delete this file if your team wants to commit review records.\n*\n")
    return d


# ── scope ────────────────────────────────────────────────────────────────

def resolve_base(tree, head, branch, base_arg, since_review, root):
    """Return (ref_label, object_sha, reason)."""
    if since_review:
        rec = load_latest(root)
        if not rec:
            sys.exit("review: --since-review needs an earlier review record (none found)")
        t = rec["fingerprint"]["tree"]
        if not object_exists(t):
            sys.exit("review: the last review's snapshot %s is no longer in .git/objects "
                     "(pruned by git gc) — pass --base instead" % t[:12])
        return ("last review " + rec["id"], t, "changes since the last review")
    if base_arg:
        sha = rev(base_arg) if rev(base_arg + "^{tree}") else None
        if not sha:
            sys.exit("review: unknown base %r" % base_arg)
        return (base_arg, sha, "given with --base")
    if not head:
        return ("(empty)", EMPTY_TREE, "repository has no commits yet")
    dflt = default_branch(branch)
    if dflt and branch:
        mb = subprocess.run(["git", "merge-base", "HEAD", dflt], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True)
        if mb.returncode == 0 and mb.stdout.strip() and mb.stdout.strip() != head:
            return ("merge-base(HEAD, %s)" % dflt, mb.stdout.strip(),
                    "branch %s vs %s" % (branch, dflt))
    if changed_paths(head, tree):
        return ("HEAD", head, "uncommitted work on top of HEAD")
    parent = rev("HEAD~1")
    if parent:
        return ("HEAD~1", parent, "clean tree — reviewing the last commit")
    return ("(empty)", EMPTY_TREE, "clean tree with a single commit — reviewing it whole")


def fingerprint_excludes():
    return subprocess.run(["bash", FINGERPRINT_SH, "--excludes"], stdout=subprocess.PIPE,
                          universal_newlines=True).stdout.split()


def product_diff(opts, base, tree, left_out=()):
    """git diff limited to product paths. The snapshot leaves Ship's own files out, so a base
    commit that contains them would otherwise show them as deleted."""
    specs = [(":(exclude,glob)" if "*" in e else ":(exclude)") + e for e in fingerprint_excludes()]
    specs += [":(exclude,literal)" + p for p in left_out]
    return git(["diff", "--no-renames", "--no-ext-diff"] + opts + [base, tree, "--", "."] + specs)


# Files on disk that git doesn't track and that aren't the product: Claude Code's local settings,
# Ship's taste record, and leftovers (a saved patch, a backup, a log). They stay in the snapshot, so
# a later edit still makes a review stale, but they aren't reviewed and don't size the review.
# knowledge.py and ship.py leave out the same files.
LEFTOVER_EXT = (".patch", ".diff", ".orig", ".rej", ".bak", ".log", ".tmp", ".swp")


def left_out_reason(path, untracked):
    if path not in untracked:
        return None
    if path.startswith(".claude/"):
        return "Claude Code's local settings"
    if path == "design/taste.yaml":
        return "Ship's taste record"
    if path.lower().endswith(LEFTOVER_EXT):
        return "a leftover %s file" % os.path.splitext(path)[1]
    return None


def changed_paths(base, tree):
    num = product_diff(["--numstat", "-z"], base, tree)
    stat = product_diff(["--name-status", "-z"], base, tree)
    status = {}
    parts = stat.split("\0")
    i = 0
    while i + 1 < len(parts):
        if parts[i]:
            status[parts[i + 1]] = parts[i][0]
        i += 2
    out = []
    for rec in num.split("\0"):
        if not rec:
            continue
        a, d, path = rec.split("\t", 2)
        out.append({"path": path, "status": status.get(path, "M"),
                    "added": None if a == "-" else int(a),
                    "deleted": None if d == "-" else int(d)})
    return out


def added_lines_by_file(diff):
    out, cur = {}, None
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/(.*) b/(.*)$", line)
            cur = m.group(2) if m else None
            out.setdefault(cur, [])
        elif cur is not None and line.startswith("+") and not line.startswith("+++"):
            out[cur].append(line[1:])
    return out


def classify(paths, added_by_file, branch):
    lines = sum((p["added"] or 0) + (p["deleted"] or 0) for p in paths)
    names = [p["path"] for p in paths]
    low = [n.lower() for n in names]
    ui = [n for n, l in zip(names, low)
          if l.endswith(UI_EXT) or n in DESIGN_FILES or n.endswith(DESIGN_FILES)
          or (re.search(UI_PATH, l) and not re.search(TEST_PATH, l))]
    tests = [n for n, l in zip(names, low) if re.search(TEST_PATH, l)]
    docs = [n for n, l in zip(names, low) if l.endswith(DOC_EXT) and n not in DESIGN_FILES]
    code = [n for n in names if n not in ui and n not in tests and n not in docs]
    # Risk comes from code and UI files only — docs and tests mention "auth" without being auth.
    risky = [n for n in names if n not in docs and n not in tests]
    added_text = "\n".join(l for n in risky for l in added_by_file.get(n, []))
    risks = {}
    for label, rx in RISK_PATHS:
        hits = [n for n in risky if re.search(rx, n.lower())]
        if hits:
            risks.setdefault(label, []).extend("path " + h for h in hits[:3])
    for label, rx in RISK_CONTENT:
        m = re.search(rx, added_text)
        if m:
            risks.setdefault(label, []).append("added line mentions %r" % m.group(0))
    release = bool(branch and re.search(RELEASE_BRANCH, branch))
    return {"lines_changed": lines, "files": len(names), "ui_paths": ui, "test_paths": tests,
            "doc_paths": docs, "code_paths": code, "risks": risks, "release_branch": release}


def select_depth(c):
    reasons = []
    if c["release_branch"]:
        reasons.append("release/hotfix/deploy branch")
    for label, why in sorted(c["risks"].items()):
        reasons.append("%s risk (%s)" % (label, "; ".join(why[:2])))
    if c["lines_changed"] > FULL_MIN_LINES:
        reasons.append("%d lines changed (> %d)" % (c["lines_changed"], FULL_MIN_LINES))
    if reasons:
        return "full", reasons
    if c["files"] == 0:
        return "quick", ["nothing changed against the base"]
    if c["lines_changed"] <= QUICK_MAX_LINES and c["files"] <= QUICK_MAX_FILES:
        return "quick", ["small change: %d lines in %d file(s), no risk signals"
                         % (c["lines_changed"], c["files"])]
    return "standard", ["%d lines in %d files, no risk signals" % (c["lines_changed"], c["files"])]


def select_reviewers(depth, c):
    ui = bool(c["ui_paths"])
    if depth == "full":
        return list(REVIEWERS)
    if depth == "standard":
        r = ["crit"] + (["pol"] if ui else []) + ["test"] + (["eye"] if ui else [])
        return r
    # quick: 1–2 reviewers most relevant to what changed
    if c["files"] == 0:
        return []
    if c["test_paths"] and not (c["code_paths"] or ui or c["doc_paths"]):
        return ["test"]
    if c["doc_paths"] and not (c["code_paths"] or ui or c["test_paths"]):
        return ["crit"]
    if ui and not c["code_paths"]:
        return ["pol"]
    if ui:
        return ["pol", "test"]
    return ["test", "crit"]


def _knowledge():
    """The knowledge router, imported from its sibling skill (project or plugin layout)."""
    for rel in (("knowledge",), ("ship-knowledge",)):
        cand = os.path.join(HERE, "..", "..", *rel, "bin", "knowledge.py")
        if os.path.isfile(cand):
            spec = importlib.util.spec_from_file_location("ship_knowledge", cand)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


def reference_check(root, paths, added_by_file):
    """Knowledge areas this change touches — by its added code and specific file names — against
    the route the session recorded (.ship/state/route.json). A touched area that wasn't routed is a
    REF_SKIP candidate. The record is evidence of selection, not proof anything was read."""
    out = {"record": None, "touched": [], "gaps": []}
    files = [p["path"] for p in paths if p.get("status") != "D"]
    kn = _knowledge() if files else None
    if kn is None:
        return out
    from pathlib import Path as _P
    stacks = kn.task_target(_P(root), None, files)["stacks"]
    code = "\n".join(l for f in files for l in added_by_file.get(f, []))
    picked, _context, why = kn.match_domains(kn.load_routing(), [], "", files, stacks, code)
    touched = [d for d in picked if why.get(d["id"]) in ("code in the change", "file name")]
    out["touched"] = [d["id"] for d in touched]
    recorded = []
    rec_path = os.path.join(root, ".ship", "state", "route.json")
    if os.path.isfile(rec_path):
        try:
            with open(rec_path, encoding="utf-8") as f:
                rec = json.load(f)
            recorded = rec.get("domains") or []
            out["record"] = {"at": rec.get("at"), "domains": recorded,
                             "notes": rec.get("notes") or []}   # what the stage says it read (self-reported)
        except ValueError:
            pass
    stack = stacks[0] if len(stacks) == 1 else None
    out["gaps"] = [{"domain": d["id"], "label": d["label"],
                    "refs": [kn.display_ref(r) for r in kn.refs_for(d, stack)]}
                   for d in touched if d["id"] not in recorded]
    return out


def cmd_scope(a):
    root = toplevel()
    os.chdir(root)
    started = now()
    tree = fingerprint()
    head = rev("HEAD")
    branch = subprocess.run(["git", "symbolic-ref", "-q", "--short", "HEAD"],
                            stdout=subprocess.PIPE, universal_newlines=True).stdout.strip() or None
    base_label, base_sha, base_reason = resolve_base(tree, head, branch, a.base, a.since_review, root)
    untracked = set(git(["ls-files", "--others", "--exclude-standard", "-z"]).split("\0")) - {""}
    paths, left_out = [], []
    for p in changed_paths(base_sha, tree):
        why = left_out_reason(p["path"], untracked)
        (left_out.append({"path": p["path"], "reason": why}) if why else paths.append(p))
    diff = product_diff([], base_sha, tree, [x["path"] for x in left_out])
    journey = None
    if a.care:
        picked = []
        for pat in a.paths or []:
            hits = sorted(glob.glob(pat, recursive=True)) if any(ch in pat for ch in "*?[") else [pat]
            picked += [h for h in hits if os.path.isfile(h) and h not in picked]
        if not picked and not paths:
            sys.exit("review: a care pass needs the journey's files (--paths) when nothing changed")
        if picked:
            paths = [{"path": h, "status": "J", "added": None, "deleted": None} for h in picked]
        journey = {"task": a.journey or "", "paths": [x["path"] for x in paths]}
    added_by_file = added_lines_by_file(diff)
    c = classify(paths, added_by_file, branch)
    auto_depth, reasons = select_depth(c)
    if a.commitment == "promise" and auto_depth == "quick" and c["files"]:
        auto_depth, reasons = "standard", reasons + ["a promise: the core journey gets at least a standard review"]
    depth = a.depth or auto_depth
    reviewers = select_reviewers(depth, c)
    if journey is not None:
        depth, auto_depth = "care", "care"
        reasons = ["care pass: the whole journey, one lens per reviewer (care-lens.md) — preview"]
        reviewers = list(CARE_REVIEWERS)
    only = None
    if a.only:
        only = [r.strip() for r in a.only.split(",") if r.strip()]
        bad = [r for r in only if r not in REVIEWERS]
        if bad:
            sys.exit("review: unknown reviewer(s): %s" % ", ".join(bad))
        reviewers = only
    run_id = started.strftime("%Y%m%dT%H%M%SZ") + "-" + tree[:8]
    temporary = journey is not None and not os.path.isdir(os.path.join(root, ".ship"))
    if temporary:   # a care report in a project without Ship's files writes nothing into it
        run_dir = tempfile.mkdtemp(prefix="ship-care-")
    else:
        run_dir = os.path.join(records_dir(root), "runs", run_id)
    os.makedirs(os.path.join(run_dir, "shots"), exist_ok=True)
    with open(os.path.join(run_dir, "diff.patch"), "w") as f:
        f.write(diff)
    scope = {
        "schema": "ship-review-scope/1",
        "run_id": run_id,
        "started_at": iso(started),
        "fingerprint": {"tree": tree, "method": "temp index: read-tree HEAD + add -A + write-tree",
                        "excludes": fingerprint_excludes()},
        "head": head, "branch": branch,
        "base": {"ref": base_label, "object": base_sha, "reason": base_reason},
        "reviewed_paths": paths,
        "left_out": left_out,
        "signals": c,
        "depth": {"selected": depth, "auto": auto_depth, "reasons": reasons,
                  "override": a.depth if a.depth and a.depth != auto_depth else None},
        "reviewers": reviewers,
        "kind": "care" if journey is not None else "change",
        "journey": journey,
        "commitment": a.commitment,
        "temporary": temporary,
        "reference_check": ({"record": None, "touched": [], "gaps": [], "note": "not for care runs"}
                            if journey is not None else reference_check(root, paths, added_by_file)),
        "only": only if a.only else None,
        "second_wave": "adversarial" in reviewers,
        "case_id": a.case or os.environ.get("SHIP_EVAL_CASE") or None,
        "run_dir": run_dir if temporary else os.path.relpath(run_dir, root),
        "diff": os.path.join(run_dir, "diff.patch") if temporary else os.path.relpath(os.path.join(run_dir, "diff.patch"), root),
    }
    with open(os.path.join(run_dir, "scope.json"), "w") as f:
        json.dump(scope, f, indent=2, ensure_ascii=False)
    if a.json:
        print(json.dumps(scope, indent=2, ensure_ascii=False))
        return 0
    if journey is not None:
        print("Care pass (preview) — run %s%s" % (run_id, " · temporary folder: no .ship/ in this project" if temporary else ""))
        print("  journey: %s · %d file(s)" % (journey["task"] or "(unnamed)", len(journey["paths"])))
        print("  reviewers: crit (editor), pol (expression), eye (task walk) — care-lens.md")
        print("  run folder: %s" % scope["run_dir"])
        return 0
    print("Review scope — run %s" % run_id)
    print("  fingerprint %s · base %s (%s) — %s" % (tree[:12], base_label, base_sha[:8], base_reason))
    print("  %d file(s), %d line(s) changed%s" % (c["files"], c["lines_changed"],
          " · UI changed" if c["ui_paths"] else ""))
    if left_out:
        print("  left out, not in git and not the product: %s" % ", ".join(
            "%s (%s)" % (x["path"], x["reason"]) for x in left_out[:5]) + (" …" if len(left_out) > 5 else ""))
    note = " (auto)" if not a.depth else (" (override; auto was %s)" % auto_depth
                                          if a.depth != auto_depth else " (given)")
    print("  depth: %s%s — %s" % (depth, note, "; ".join(reasons)))
    print("  reviewers: %s%s" % (", ".join(reviewers) or "none",
          " · Adversarial runs as second wave" if "adversarial" in reviewers else ""))
    rc = scope["reference_check"]
    if rc["touched"]:
        print("  references: the change touches %s · recorded %s%s" % (
            ", ".join(rc["touched"]), ", ".join((rc["record"] or {}).get("domains") or []) or "no route",
            (" · REF_SKIP candidates: " + ", ".join(g["domain"] for g in rc["gaps"])) if rc["gaps"] else ""))
    print("  run folder: %s  (scope.json, diff.patch, shots/)" % scope["run_dir"])
    return 0


# ── validate ─────────────────────────────────────────────────────────────

def _nonempty(v):
    return isinstance(v, str) and v.strip() != ""


def _scan_banned(obj, path, errs):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in BANNED_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool):
                errs.append("%s.%s: numeric scores/confidence are not part of Ship reviews — "
                            "use severity + evidence + confidence_reason" % (path, k))
            _scan_banned(v, "%s.%s" % (path, k), errs)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _scan_banned(v, "%s[%d]" % (path, i), errs)
    elif isinstance(obj, str) and re.search(r"\b\d{1,3}\s?%\s*(confiden|sure|certain)", obj, re.I):
        errs.append("%s: confidence percentage in text — say why you believe it instead" % path)


def _check_evidence(ev, where, reviewer, errs):
    if not isinstance(ev, dict):
        errs.append("%s.evidence: must be an object" % where)
        return
    allowed = {"file", "line", "line_note", "screenshot", "command", "output", "quote", "locations"}
    extra = set(ev) - allowed
    if extra:
        errs.append("%s.evidence: unknown key(s) %s" % (where, ", ".join(sorted(extra))))
    for k in ("file", "screenshot", "command", "output", "quote", "line_note"):
        if k in ev and not isinstance(ev[k], str):
            errs.append("%s.evidence.%s: one string%s" % (where, k,
                        " — one capture per finding; list every capture you looked at in artifacts" if k == "screenshot" else ""))
    if not any(_nonempty(ev.get(k)) for k in ("file", "screenshot", "command", "quote")):
        errs.append("%s.evidence: needs at least one of file, screenshot, command+output, quote"
                    % where)
    if _nonempty(ev.get("command")) and not _nonempty(ev.get("output")):
        errs.append("%s.evidence: command given without its output" % where)
    if "line" in ev:
        ln = ev["line"]
        ok = (isinstance(ln, int) and not isinstance(ln, bool) and ln >= 1) or \
             (isinstance(ln, str) and re.match(r"^\d+(-\d+)?$", ln))
        if not ok:
            errs.append("%s.evidence.line: positive integer or \"start-end\"" % where)
        if not _nonempty(ev.get("file")):
            errs.append("%s.evidence: line without file" % where)
    if "locations" in ev:
        locs = ev["locations"]
        if not isinstance(locs, list) or not locs or not all(
                isinstance(l, dict) and _nonempty(l.get("file")) for l in locs):
            errs.append("%s.evidence.locations: list of {file, line} — every place one root cause shows up"
                        % where)
    if reviewer == "eye" and not _nonempty(ev.get("screenshot")):
        errs.append("%s.evidence: Eye findings need a screenshot/recording path — "
                    "no visual verdict from code alone" % where)


def validate_output(d, name="output"):
    errs = []
    if not isinstance(d, dict):
        return ["%s: top level must be a JSON object" % name]
    r = d.get("reviewer")
    if r not in REVIEWERS:
        errs.append("reviewer: one of %s" % ", ".join(REVIEWERS))
    mode = d.get("mode", "review")
    if mode not in ("review", "plan", "care"):
        errs.append("mode: review, plan or care")
    st = d.get("status")
    if st not in STATUSES:
        errs.append("status: one of %s" % ", ".join(STATUSES))
    if st == "skipped" and not _nonempty(d.get("skipped_reason")):
        errs.append("skipped_reason: required when status is skipped")
    if mode in ("review", "care") and not _nonempty(d.get("fingerprint")):
        errs.append("fingerprint: echo the fingerprint you reviewed (from scope.json)")
    if "model" in d and d["model"] is not None and not isinstance(d["model"], str):
        errs.append("model: string (exact model ID from your environment) or null")
    findings = d.get("findings")
    if not isinstance(findings, list):
        errs.append("findings: list (may be empty)")
        findings = []
    ids = set()
    for i, f in enumerate(findings):
        w = "findings[%d]" % i
        if not isinstance(f, dict):
            errs.append("%s: object" % w)
            continue
        fid = f.get("id")
        if not _nonempty(fid):
            errs.append("%s.id: required" % w)
        elif r in REVIEWERS and not fid.startswith(r + "-"):
            errs.append("%s.id: prefix it with the reviewer name, e.g. %s-1" % (w, r))
        elif fid in ids:
            errs.append("%s.id: duplicate %r" % (w, fid))
        else:
            ids.add(fid)
        if f.get("severity") not in SEVERITIES:
            errs.append("%s.severity: one of %s" % (w, "|".join(SEVERITIES)))
        for k in ("claim", "why_it_matters", "suggested_fix", "confidence_reason"):
            if not _nonempty(f.get(k)):
                errs.append("%s.%s: required, non-empty" % (w, k))
        _check_evidence(f.get("evidence"), w, r, errs)
    dims = d.get("dimensions", [])
    if not isinstance(dims, list):
        errs.append("dimensions: list")
        dims = []
    for i, dm in enumerate(dims):
        if not isinstance(dm, dict) or not _nonempty(dm.get("name")) \
                or dm.get("result") not in DIM_RESULTS:
            errs.append("dimensions[%d]: {name, result: pass|concerns|not-checked|not-applicable, note}" % i)
        elif dm.get("result") == "not-applicable" and not _nonempty(dm.get("note")):
            errs.append("dimensions[%d]: not-applicable needs a reason in `note`" % i)
    if r == "eye" and st in ("completed", "partial") and mode == "review":
        arts = d.get("artifacts")
        if not isinstance(arts, list) or not [a for a in arts if _nonempty(a)]:
            errs.append("artifacts: Eye must list the screenshots/recordings it looked at "
                        "(or report status skipped with a reason)")
    if r == "test" and st in ("completed", "partial") and mode == "review":
        cr = d.get("commands_run")
        if not isinstance(cr, list) or not cr:
            hint = (" — your notes describe commands; move each into commands_run with its exit code"
                    if re.search(r"xcodebuild|npm |pytest|swift test|gradle|command", str(d.get("notes") or ""), re.I) else "")
            errs.append("commands_run: Test must list what it ran [{command, exit_code, summary}] "
                        "(or report status skipped with a reason)" + hint)
        else:
            for i, c in enumerate(cr):
                if not isinstance(c, dict) or not _nonempty(c.get("command")) \
                        or not isinstance(c.get("exit_code"), int) or not _nonempty(c.get("summary")):
                    errs.append("commands_run[%d]: {command, exit_code (int), summary}" % i)
    if r == "adversarial":
        vs = d.get("verdicts")
        if mode == "review" and not isinstance(vs, list):
            errs.append("verdicts: list of {finding_id, status, reason}")
            vs = []
        for i, v in enumerate(vs or []):
            if not isinstance(v, dict) or not _nonempty(v.get("finding_id")) \
                    or v.get("status") not in VERDICTS or not _nonempty(v.get("reason")):
                errs.append("verdicts[%d]: {finding_id, status: %s, reason}" % (i, "|".join(VERDICTS)))
            elif "evidence" in v:
                _check_evidence(v["evidence"], "verdicts[%d]" % i, "adversarial", errs)
        if mode == "plan" and d.get("plan_verdict") not in ("approved", "needs-revision"):
            errs.append("plan_verdict: approved or needs-revision")
    _scan_banned(d, "$", errs)
    return errs


def load_json(path):
    with open(path) as f:
        return json.load(f)


# ── normalize: accept the citation forms reviewers write, without losing any of it ──
# A reviewer who cites "9, 112-133" or "55-105 (submitEval), 107-112 (resetCurrent)" has given
# real evidence in a looser shape. Split it: the first range stays in `line` (its label in
# `line_note`), the others become `locations` entries. Anything that isn't a list of line ranges is
# left alone — validation still rejects it. Every change is listed in `normalized`, never silent.

_LINE_SEG = re.compile(r"\s*(?:lines?\s*|L)?(\d+)(?:\s*[-\u2013]\s*L?(\d+))?\s*(?:\(([^()]*)\))?\s*$", re.I)


def _top_split(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch in ",;" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p for p in parts if p.strip()]


def _line_parts(value):
    """"9, 112-133" → [("9", None), ("112-133", None)]; None when it isn't only line ranges."""
    if not isinstance(value, str) or re.match(r"^\d+(-\d+)?$", value):
        return None
    out = []
    for chunk in _top_split(value):
        m = _LINE_SEG.match(chunk)
        if not m:
            return None
        a, b, label = m.groups()
        out.append(("%s-%s" % (a, b) if b else a, (label or "").strip() or None))
    return out or None


def _normalize_evidence(ev, where, notes):
    if not isinstance(ev, dict):
        return
    locs = ev.get("locations")
    if isinstance(locs, dict) and isinstance(locs.get("file"), str) and locs["file"].strip():
        ev["locations"] = locs = [locs]              # one location given as an object: same data, as a list
        notes.append("%s.evidence.locations: single object → list of 1" % where)
    elif "locations" in ev and not isinstance(locs, list):
        return                                       # unrecognized shape: leave everything for validation to reject
    if isinstance(locs, list):                       # split loose location lines first (original indexes)
        new = []
        for i, loc in enumerate(locs):
            lp = _line_parts(loc.get("line")) if isinstance(loc, dict) else None
            if lp and _nonempty(loc.get("file")):
                for ln, lb in lp:
                    item = dict(loc, line=ln)
                    if lb:
                        item["note"] = (loc.get("note") + "; " if loc.get("note") else "") + lb
                    new.append(item)
                notes.append("%s.evidence.locations[%d].line %r → %d location(s)" % (where, i, loc["line"], len(lp)))
            else:
                new.append(loc)
        ev["locations"] = new
    parts = _line_parts(ev.get("line"))
    if parts and _nonempty(ev.get("file")):
        orig = ev["line"]
        ev["line"] = parts[0][0]
        if parts[0][1]:
            ev["line_note"] = parts[0][1]
        have = {(l.get("file"), str(l.get("line"))) for l in ev.get("locations") or [] if isinstance(l, dict)}
        extra = [dict({"file": ev["file"], "line": ln}, **({"note": lb} if lb else {}))
                 for ln, lb in parts[1:] if (ev["file"], ln) not in have]
        if extra:
            ev["locations"] = extra + (ev.get("locations") if isinstance(ev.get("locations"), list) else [])
        notes.append("%s.evidence.line %r → line %s%s" % (
            where, orig, ev["line"],
            (" + %d new location(s)" % len(extra)) if extra else " (the other ranges were already in locations)"))


def safe_normalize(d):
    """normalize_output that can't abort a review: an unexpected shape is left for validation."""
    try:
        return normalize_output(d)
    except Exception as e:                               # defensive: never lose the other reviewers' work
        return ["normalization skipped (%s: %s) — report validated as sent" % (type(e).__name__, e)]


def normalize_output(d):
    """Reshape loose-but-real citations; returns what changed (also stored in d["normalized"])."""
    notes = []
    if not isinstance(d, dict):
        return notes
    findings = d.get("findings") if isinstance(d.get("findings"), list) else []
    verdicts = d.get("verdicts") if isinstance(d.get("verdicts"), list) else []
    for i, f in enumerate(findings):
        if isinstance(f, dict):
            _normalize_evidence(f.get("evidence"), "findings[%d]" % i, notes)
    for i, v in enumerate(verdicts):
        if isinstance(v, dict) and "evidence" in v:
            _normalize_evidence(v["evidence"], "verdicts[%d]" % i, notes)
    if d.get("reviewer") == "eye" and d.get("artifacts") is None:   # only when absent — a malformed value stays for validation
        shots = []
        for f in findings:
            ev = f.get("evidence") if isinstance(f, dict) else None
            s = ev.get("screenshot") if isinstance(ev, dict) else None
            if not isinstance(s, str):
                continue                                  # a list or other shape isn't guessed at
            for m in re.findall(r"[\w./-]+\.(?:png|jpe?g|gif|heic|mov|mp4|webm)", s, re.I):
                if m not in shots:
                    shots.append(m)
        if shots:
            d["artifacts"] = shots
            notes.append("artifacts missing → %d screenshot(s) cited in findings (list every capture you looked at)" % len(shots))
    if notes:
        d["normalized"] = notes
    return notes


def cmd_validate(a):
    bad = 0
    for p in a.files:
        try:
            d = load_json(p)
        except (OSError, ValueError) as e:
            print("✗ %s: %s" % (p, e))
            bad += 1
            continue
        norm = safe_normalize(d)
        for n in norm:
            print("  ~ normalized %s" % n)
        errs = validate_output(d, p)
        if errs:
            bad += 1
            print("✗ %s" % p)
            for e in errs:
                print("  - " + e)
        else:
            print("✓ %s (%s, %d finding(s))" % (p, d.get("reviewer"), len(d.get("findings", []))))
    return 1 if bad else 0


# ── consolidate ──────────────────────────────────────────────────────────

STOP = set("the a an and or of to in on for with is are be this that it its as at by from not "
           "no when than then there into only has have should would could does do can will "
           "missing user users screen view file line code".split())


def tokens(s):
    return set(w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 2 and w not in STOP)


def jaccard(a, b):
    return len(a & b) / float(len(a | b)) if (a or b) else 0.0


def line_range(ln):
    if isinstance(ln, int):
        return (ln, ln)
    if isinstance(ln, str) and re.match(r"^\d+(-\d+)?$", ln):
        p = [int(x) for x in ln.split("-")]
        return (p[0], p[-1])
    return None


def location(f):
    ev = f.get("evidence") or {}
    fl = (ev.get("file") or "").strip()
    if fl.startswith("./"):
        fl = fl[2:]
    return fl or None, line_range(ev.get("line"))


def same_issue(a, b):
    """Return a reason string when a and b describe the same issue, else None."""
    fa, la = location(a)
    fb, lb = location(b)
    sim = jaccard(tokens(a["claim"]), tokens(b["claim"]))
    if fa and fb:
        if fa != fb:
            return None
        if la and lb:
            overlap = la[0] <= lb[1] and lb[0] <= la[1]
            near = la[0] - 3 <= lb[1] and lb[0] - 3 <= la[1]
            # Same lines: differently worded claims about one spot are one issue (measured on a
            # live review: 0.23 / 0.31 for true duplicates vs 0.11 for distinct issues).
            if overlap and sim >= 0.2:
                return "same lines (%s:%s~%s) and related claim (%.2f)" % (fa, la[0], lb[0], sim)
            if near and sim >= 0.35:
                return "same place (%s:%s~%s) and overlapping claim (%.2f)" % (fa, la[0], lb[0], sim)
            return None
        if sim >= 0.5:
            return "same file (%s) and overlapping claim (%.2f)" % (fa, sim)
        return None
    if not fa and not fb and sim >= 0.6:
        return "no file on either; claims overlap (%.2f)" % sim
    return None


def dedup(raw):
    clusters, merges = [], []
    for f in raw:
        target, why = None, None
        for c in clusters:
            if f["reviewer"] in c["raised_by"]:
                continue  # never merge two findings from the same reviewer
            why = None
            for member in c.get("_members", [c["_primary"]]):
                why = same_issue(member, f)
                if why:
                    break
            if why:
                target = c
                break
        if target is None:
            clusters.append({
                "id": f["uid"], "_primary": f, "_members": [f], "raised_by": [f["reviewer"]],
                "severity": f["severity"], "severity_votes": {f["reviewer"]: f["severity"]},
                "claim": f["claim"], "why_it_matters": f["why_it_matters"],
                "suggested_fix": f["suggested_fix"],
                "confidence_reason": f["confidence_reason"],
                "evidence": [dict(f["evidence"], reviewer=f["reviewer"])],
                "location": {"file": location(f)[0], "line": f["evidence"].get("line"),
                             "more": len(f["evidence"].get("locations") or [])},
                "aliases": [], "also_claimed": [],
                "status": "unchallenged", "adversarial": None,
            })
        else:
            target["raised_by"].append(f["reviewer"])
            target["_members"].append(f)
            target["severity_votes"][f["reviewer"]] = f["severity"]
            if SEV_RANK[f["severity"]] < SEV_RANK[target["severity"]]:
                target["severity"] = f["severity"]
            target["evidence"].append(dict(f["evidence"], reviewer=f["reviewer"]))
            target["aliases"].append(f["uid"])
            target["also_claimed"].append({"id": f["uid"], "claim": f["claim"],
                                           "suggested_fix": f["suggested_fix"]})
            merges.append({"kept": target["id"], "merged": f["uid"], "reason": why})
    return clusters, merges


def gather(run_dir, include_adversarial):
    raw, reviewers, dims, problems = [], [], [], []
    for r in REVIEWERS:
        if r == "adversarial" and not include_adversarial:
            continue
        p = os.path.join(run_dir, r + ".json")
        if not os.path.exists(p):
            continue
        try:
            d = load_json(p)
        except ValueError as e:
            reviewers.append({"name": r, "status": "invalid-output", "errors": [str(e)]})
            problems.append("%s: unreadable JSON" % r)
            continue
        norm = safe_normalize(d)
        errs = validate_output(d, p)
        if not errs and d.get("reviewer") != r:
            errs = ["file %s.json holds output for reviewer %r" % (r, d.get("reviewer"))]
        entry = {"name": r, "status": d.get("status") if not errs else "invalid-output",
                 "model": d.get("model"),
                 "model_source": "self-reported" if d.get("model") else "unknown",
                 "skipped_reason": d.get("skipped_reason"), "notes": d.get("notes"),
                 "artifacts": d.get("artifacts"), "commands_run": d.get("commands_run"),
                 "fingerprint_echoed": d.get("fingerprint"), "mode": d.get("mode", "review"),
                 "dimensions": d.get("dimensions") if isinstance(d.get("dimensions"), list) else []}
        if norm:
            entry["normalized"] = norm
        if errs:
            entry["errors"] = errs
            problems.append("%s: output failed validation (%d problem(s))" % (r, len(errs)))
            reviewers.append(entry)
            continue
        reviewers.append(entry)
        for dm in d.get("dimensions", []):
            dims.append(dict(dm, reviewer=r))
        if d.get("status") in ("completed", "partial") and d.get("mode", "review") in ("review", "care"):
            reported = {str(dm.get("name", "")).lower() for dm in d.get("dimensions", [])}
            declared = CARE_DIMENSIONS if d.get("mode") == "care" else DECLARED_DIMENSIONS
            for name in declared.get(r, []):
                if name not in reported:   # silence isn't a pass: record the gap
                    dims.append({"name": name, "result": "unreported", "reviewer": r,
                                 "note": "not reported by %s — counts as a coverage gap" % r})
        if r == "adversarial":
            continue  # its findings are added after verdicts
        for f in d.get("findings", []):
            raw.append(dict(f, reviewer=r, uid=f["id"]))
    return raw, reviewers, dims, problems


def agent_definition(name):
    """Requested settings from the reviewer's agent file (.claude/agents/ship-<name>.md in a project
    install, <plugin>/agents/ship-<name>.md in the plugin). What the runtime actually used is recorded
    separately — a definition is a request, not evidence."""
    here = os.path.abspath(HERE)
    for base in (os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here)))), "agents"),
                 os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(here))), "agents")):
        path = os.path.join(base, "ship-%s.md" % name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            head = text[4:].split("\n---", 1)[0] if text.startswith("---\n") else ""
            fields = dict(l.split(":", 1) for l in head.splitlines() if ":" in l and not l.startswith(" "))
            return {"model": fields.get("model", "").strip() or None,
                    "effort": fields.get("effort", "").strip() or None,
                    "source": os.path.relpath(path, toplevel()) if path.startswith(toplevel()) else path}
    return {"model": None, "effort": None, "source": None}


def record_settings(reviewers):
    for e in reviewers:
        e["requested"] = agent_definition(e["name"])
        e["observed"] = {"model": e.get("model"), "model_source": e.get("model_source", "unknown"),
                         "effort": e.get("effort_observed") or "unverified (the runtime doesn't report it to the reviewer)"}


def apply_usage(run_dir, reviewers):
    p = os.path.join(run_dir, "usage.json")
    if not os.path.exists(p):
        return
    try:
        usage = load_json(p)
    except ValueError:
        return
    for e in reviewers:
        u = usage.get(e["name"]) or {}
        for k in ("tokens", "tool_uses", "duration_ms", "cost_usd"):
            if k in u:
                e[k] = u[k]
        if u.get("model"):
            e["model"], e["model_source"] = u["model"], "runtime-reported"
        if u.get("effort"):
            e["effort_observed"] = "%s (runtime-reported)" % u["effort"]


def adjudicate(clusters, run_dir, reviewers, dims, problems):
    p = os.path.join(run_dir, "adversarial.json")
    if not os.path.exists(p):
        return clusters, [], []
    try:
        d = load_json(p)
    except ValueError:
        problems.append("adversarial: unreadable JSON")
        reviewers.append({"name": "adversarial", "status": "invalid-output", "errors": ["unreadable JSON"]})
        return clusters, [], []
    safe_normalize(d)
    errs = validate_output(d, p)
    if not errs and d.get("reviewer") != "adversarial":
        errs = ["file adversarial.json holds output for reviewer %r" % d.get("reviewer")]
    entry = {"name": "adversarial", "status": d.get("status") if not errs else "invalid-output",
             "model": d.get("model"), "model_source": "self-reported" if d.get("model") else "unknown",
             "notes": d.get("notes"), "skipped_reason": d.get("skipped_reason"),
             "fingerprint_echoed": d.get("fingerprint")}
    if errs:
        entry["errors"] = errs
        problems.append("adversarial: output failed validation (%d problem(s))" % len(errs))
        reviewers.append(entry)
        return clusters, [], []
    reviewers.append(entry)
    for dm in d.get("dimensions", []):
        dims.append(dict(dm, reviewer="adversarial"))
    index = {}
    for c in clusters:
        index[c["id"]] = c
        for al in c["aliases"]:
            index[al] = c
    unknown = []
    for v in d.get("verdicts", []):
        c = index.get(v["finding_id"])
        if not c:
            unknown.append(v["finding_id"])
            continue
        c["status"] = v["status"]
        c["adversarial"] = {"status": v["status"], "reason": v["reason"],
                            "evidence": v.get("evidence")}
    new, merges = [], []
    for f in d.get("findings", []):
        f = dict(f, reviewer="adversarial", uid=f["id"])
        hit = None
        for c in clusters:
            why = None
            for member in c.get("_members", [c["_primary"]]):
                why = same_issue(member, f)
                if why:
                    break
            if why:
                hit = (c, why)
                break
        if hit:
            c, why = hit
            c["raised_by"].append("adversarial")
            c["aliases"].append(f["uid"])
            c["evidence"].append(dict(f["evidence"], reviewer="adversarial"))
            merges.append({"kept": c["id"], "merged": f["uid"], "reason": why})
        else:
            nc, _ = dedup([f])
            nc[0]["status"] = "raised-by-adversarial"
            new.append(nc[0])
    if unknown:
        problems.append("adversarial: verdicts for unknown finding ids: %s" % ", ".join(unknown))
    return clusters + new, merges, unknown


# ── coverage: did every reviewer that was selected actually review this snapshot? ──

COMPLETION_REASONS = {
    "missing": "no output in the run folder — the reviewer didn't run, or its output was lost",
    "failed": "its output was unreadable, failed validation, or belongs to another reviewer",
    "wrong-snapshot": "it reviewed a different snapshot than this run",
    "skipped": "the reviewer reported it could not run",
    "partial": "the reviewer covered only part of the change",
    "wrong-kind": "it answered as the other kind of review (a care pass and a change review aren't interchangeable)",
}


def dimension_coverage(r, e):
    """What a completed reviewer actually covered. Checked = pass/concerns; not-applicable needs a
    reason and is a legitimate exclusion (narrow reviews stay complete); not-checked (reported but
    unverified) and declared-but-unreported are gaps. A reviewer that checked nothing is never complete."""
    if r == "adversarial" or e.get("mode", "review") not in ("review", "care") or e.get("status") != "completed":
        return None
    declared = CARE_DIMENSIONS if e.get("mode") == "care" else DECLARED_DIMENSIONS
    reported = {}
    for dm in e.get("dimensions") or []:
        reported[str(dm.get("name", "")).lower()] = dm
    out = {"checked": [n for n, d in reported.items() if d.get("result") in CHECKED],
           "not_applicable": [{"name": n, "reason": d.get("note")} for n, d in reported.items()
                              if d.get("result") == "not-applicable"],
           "unverified": [n for n, d in reported.items() if d.get("result") == "not-checked"],
           "unreported": [n for n in declared.get(r, []) if n not in reported]}
    gaps = []
    if not out["checked"]:
        gaps.append("no dimension actually checked")
    if out["unverified"]:
        gaps.append("applicable but not verified: " + ", ".join(out["unverified"]))
    if out["unreported"]:
        gaps.append("not reported (check it, or mark not-applicable with a reason): " + ", ".join(out["unreported"]))
    out["gaps"] = gaps
    return out


def coverage(scope, reviewers, include_adversarial=True):
    """Selected reviewers reconciled with what came back. Separate from findings and from
    freshness: a review can be fresh and still incomplete."""
    selected = [r for r in scope.get("reviewers", []) if include_adversarial or r != "adversarial"]
    got = {e["name"]: e for e in reviewers}
    tree = scope["fingerprint"]["tree"]
    rows = []
    for r in REVIEWERS:
        if r not in scope.get("reviewers", []):
            rows.append({"reviewer": r, "selected": False, "completion": "not-selected",
                         "reason": ("not requested (--only %s)" % ",".join(scope["only"]) if scope.get("only")
                                    else "not selected at %s depth" % scope["depth"]["selected"])})
            continue
        if r not in selected:
            continue  # adversarial during the first-wave draft
        e = got.get(r)
        if e is None:
            comp, extra = "missing", None
        elif e.get("status") == "invalid-output":
            comp, extra = "failed", "; ".join(e.get("errors") or [])[:300] or None
        elif e.get("fingerprint_echoed") != tree:
            comp, extra = "wrong-snapshot", "echoed %s, run is %s" % (
                str(e.get("fingerprint_echoed"))[:12], tree[:12])
        elif e.get("mode", "review") in ("review", "care") and e.get("mode", "review") != (
                "care" if scope.get("kind") == "care" else "review"):
            comp, extra = "wrong-kind", "mode %s in a %s review" % (e.get("mode", "review"), scope.get("kind", "change"))
        elif e.get("status") == "skipped":
            comp, extra = "skipped", e.get("skipped_reason")
        elif e.get("status") == "partial":
            comp, extra = "partial", None
        else:
            comp, extra = "completed", None
        dim = dimension_coverage(r, e) if e is not None and e.get("status") != "invalid-output" else None
        if comp == "completed" and dim and dim["gaps"]:
            comp, extra = "partial", "; ".join(dim["gaps"])
        row = {"reviewer": r, "selected": True, "completion": comp}
        if dim:
            row["dimensions"] = {k: dim[k] for k in ("checked", "not_applicable", "unverified", "unreported")}
        if comp != "completed":
            row["reason"] = COMPLETION_REASONS[comp] + (": %s" % extra if extra else "")
        rows.append(row)
    sel_rows = [x for x in rows if x["selected"]]
    done = [x["reviewer"] for x in sel_rows if x["completion"] == "completed"]
    if not sel_rows:
        state = "none"
    elif len(done) == len(sel_rows):
        state = "complete"
    elif not done:
        state = "none"
    else:
        state = "incomplete"
    return {"state": state, "selected": selected, "completed": done,
            "not_completed": [x["reviewer"] for x in sel_rows if x["completion"] != "completed"],
            "not_selected": [x["reviewer"] for x in rows if not x["selected"]],
            "reviewers": rows,
            "note": "complete = every selected reviewer returned a valid, completed review of this "
                    "snapshot. Findings and freshness are tracked separately."}


def summarize(findings, reviewers, problems, cov=None):
    counts = {"total": len(findings), "by_severity": {s: 0 for s in SEVERITIES},
              "confirmed": 0, "disputed": 0, "needs_evidence": 0, "unchallenged": 0,
              "raised_by_adversarial": 0}
    for f in findings:
        counts["by_severity"][f["severity"]] += 1
        key = {"confirmed": "confirmed", "disputed": "disputed", "needs-evidence": "needs_evidence",
               "unchallenged": "unchallenged", "raised-by-adversarial": "raised_by_adversarial"}[f["status"]]
        counts[key] += 1
    blocking = [f for f in findings if f["severity"] == "blocker" and f["status"] != "disputed"]
    open_q = [f for f in findings if f["severity"] in ("blocker", "major")
              and f["status"] in ("disputed", "needs-evidence")]
    majors = [f for f in findings if f["severity"] == "major" and f["status"] != "disputed"]
    incomplete = [e["name"] for e in reviewers if e.get("status") in ("partial", "invalid-output", "skipped")]
    if blocking:
        verdict = "blockers"          # a confirmed blocker stands whatever the coverage
    elif cov is not None and cov["state"] != "complete":
        verdict = "incomplete"        # missing/skipped/failed reviewers never imply clearance
    elif majors or open_q or incomplete or problems:
        verdict = "concerns"
    else:
        verdict = "clear"
    return counts, verdict


def order_key(f):
    status_rank = {"confirmed": 0, "raised-by-adversarial": 1, "unchallenged": 1,
                   "needs-evidence": 2, "disputed": 3}
    return (SEV_RANK[f["severity"]], status_rank.get(f["status"], 9), f["id"])


def render(record):
    L = []
    mode = record["mode"]
    L.append("# Review %s — %s depth" % (record["id"], record["depth"]["selected"]))
    if mode == "single-context":
        L.append("")
        L.append("**SINGLE-CONTEXT REVIEW — NOT INDEPENDENT.** Every reviewer pass ran in one "
                 "context and could see the earlier passes. Treat agreement between passes as one "
                 "opinion, not several.")
    L.append("")
    L.append("Snapshot `%s` · base %s (`%s`) · %d path(s) · %s" % (
        record["fingerprint"]["tree"][:12], record["base"]["ref"], record["base"]["object"][:8],
        len(record["reviewed_paths"]), record["depth"]["reasons"][0] if record["depth"]["reasons"] else ""))
    rv = []
    for e in record["reviewers"]:
        s = "%s (%s" % (e["name"], e.get("status"))
        req = e.get("requested") or {}
        if req.get("model"):
            s += ", asked %s/%s" % (req["model"], req.get("effort") or "session effort")
        if e.get("model"):
            s += ", ran %s [%s]" % (e["model"], e.get("model_source", "unknown"))
        s += ")"
        rv.append(s)
    L.append("Reviewers: " + (", ".join(rv) or "none"))
    cov = record.get("coverage")
    if cov:
        if cov["state"] == "complete":
            L.append("Coverage: **complete** — all %d selected reviewer(s) completed on this snapshot"
                     % len(cov["selected"]))
        else:
            L.append("Coverage: **%s** — %d of %d selected reviewer(s) completed. This is not a clear "
                     "review." % (cov["state"].upper(), len(cov["completed"]), len(cov["selected"])))
            for x in cov["reviewers"]:
                if x["selected"] and x["completion"] != "completed":
                    L.append("  - %s: %s — %s" % (x["reviewer"], x["completion"], x["reason"]))
        if cov["not_selected"]:
            L.append("Not selected (intentional at this depth): " + ", ".join(cov["not_selected"]))
    if record.get("tree_changed_during_review"):
        L.append("")
        L.append("⚠ The working tree changed while the review ran — findings may not match the "
                 "current files. Re-run the review.")
    for p in record["problems"]:
        L.append("⚠ " + p)
    F = sorted(record["findings"], key=order_key)

    def block(title, items, both_sides=False):
        if not items:
            return
        L.append("")
        L.append("## " + title)
        for f in items:
            loc = f["location"]["file"] or "—"
            if f["location"].get("line"):
                loc += ":%s" % f["location"]["line"]
            loc = "`%s`" % loc
            if f["location"].get("more"):
                more = f["location"]["more"]
                loc += " + %d more place%s" % (more, "s" * (more != 1))
            L.append("- **%s** [%s] %s — %s (%s)" % (f["id"], f["severity"], f["claim"], loc,
                                                     "+".join(f["raised_by"])))
            L.append("  - why: %s" % f["why_it_matters"])
            L.append("  - fix: %s" % f["suggested_fix"])
            if f.get("adversarial"):
                label = "Adversarial %s" % f["adversarial"]["status"]
                if both_sides:
                    L.append("  - reviewer's case: %s" % f["confidence_reason"])
                L.append("  - %s: %s" % (label, f["adversarial"]["reason"]))

    block("Must fix", [f for f in F if f["severity"] in ("blocker", "major")
                       and f["status"] in ("confirmed", "unchallenged", "raised-by-adversarial")])
    block("Needs your call — disputed (both sides)", [f for f in F if f["status"] == "disputed"],
          both_sides=True)
    block("Needs evidence before acting", [f for f in F if f["status"] == "needs-evidence"])
    block("Minor and nits", [f for f in F if f["severity"] in ("minor", "nit")
                             and f["status"] not in ("disputed", "needs-evidence")])
    if record["dimensions"]:
        L.append("")
        L.append("## Dimensions")
        for dm in record["dimensions"]:
            L.append("- %s · %s: **%s**%s" % (dm["reviewer"], dm["name"], dm["result"],
                                              (" — " + dm["note"]) if dm.get("note") else ""))
    c = record["counts"]
    L.append("")
    L.append("Findings %d (blocker %d · major %d · minor %d · nit %d) · confirmed %d · disputed %d · "
             "needs evidence %d · unchallenged %d · duplicates merged %d · %ss" % (
                 c["total"], c["by_severity"]["blocker"], c["by_severity"]["major"],
                 c["by_severity"]["minor"], c["by_severity"]["nit"], c["confirmed"], c["disputed"],
                 c["needs_evidence"], c["unchallenged"], record["duplicates_merged"],
                 record["elapsed_seconds"]))
    L.append("Verdict: **%s**" % record["verdict"])
    return "\n".join(L)


def strip_private(findings):
    out = []
    for f in findings:
        g = {k: v for k, v in f.items() if not k.startswith("_")}
        out.append(g)
    return out


def cmd_consolidate(a):
    root = toplevel()
    run_dir = os.path.abspath(a.run_dir)
    scope_p = os.path.join(run_dir, "scope.json")
    if not os.path.exists(scope_p):
        sys.exit("review: %s has no scope.json — run `review.py scope` first" % run_dir)
    scope = load_json(scope_p)
    raw, reviewers, dims, problems = gather(run_dir, include_adversarial=False)
    for e in reviewers:
        fe = e.get("fingerprint_echoed")
        if fe and fe != scope["fingerprint"]["tree"]:
            problems.append("%s reviewed snapshot %s, not %s" % (e["name"], fe[:12],
                                                                 scope["fingerprint"]["tree"][:12]))
    # A reviewer that looked at another snapshot contributes no findings to this run.
    wrong = {e["name"] for e in reviewers if e.get("fingerprint_echoed") not in (None, scope["fingerprint"]["tree"])
             and e.get("status") != "invalid-output"}
    if wrong:
        raw = [f for f in raw if f["reviewer"] not in wrong]
    clusters, merges = dedup(raw)
    if a.draft:
        cov = coverage(scope, reviewers, include_adversarial=False)
        for x in cov["reviewers"]:
            if x["selected"] and x["completion"] != "completed":
                problems.append("%s: %s" % (x["reviewer"], x["reason"]))
        draft = {"schema": "ship-review-merged/1", "run_id": scope["run_id"],
                 "fingerprint": scope["fingerprint"]["tree"], "first_wave_coverage": cov,
                 "findings": strip_private(clusters), "merges": merges, "problems": problems}
        out = os.path.join(run_dir, "merged.json")
        with open(out, "w") as f:
            json.dump(draft, f, indent=2, ensure_ascii=False)
        print("✓ %d raw finding(s) → %d after merging %d duplicate(s) → %s"
              % (len(raw), len(clusters), len(merges), os.path.relpath(out, root)))
        for p in problems:
            print("⚠ " + p)
        print("First-wave coverage: %s (%d of %d selected completed)" % (
            cov["state"], len(cov["completed"]), len(cov["selected"])))
        return 0
    n_before, n_dims = len(reviewers), len(dims)
    before_adv = copy.deepcopy(clusters)
    findings, adv_merges, _ = adjudicate(clusters, run_dir, reviewers, dims, problems)
    adv = reviewers[n_before:]
    if adv and adv[0].get("status") != "invalid-output" and adv[0].get("fingerprint_echoed") != scope["fingerprint"]["tree"]:
        problems.append("adversarial reviewed snapshot %s, not %s — its verdicts and findings are ignored"
                        % (str(adv[0].get("fingerprint_echoed"))[:12], scope["fingerprint"]["tree"][:12]))
        findings, adv_merges = before_adv, []
        del dims[n_dims:]
    merges += adv_merges
    apply_usage(run_dir, reviewers)
    record_settings(reviewers)
    os.chdir(root)
    current = fingerprint()
    cov = coverage(scope, reviewers)
    for x in cov["reviewers"]:
        if x["selected"] and x["completion"] != "completed":
            problems.append("%s: %s" % (x["reviewer"], x["reason"]))
    counts, verdict = summarize(findings, reviewers, problems, cov)
    finished = now()
    started = _dt.datetime.strptime(scope["started_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=_dt.timezone.utc)
    mode = a.mode
    record = {
        "schema": "ship-review-record/1",
        "id": scope["run_id"],
        "created_at": iso(finished),
        "elapsed_seconds": int((finished - started).total_seconds()),
        "mode": mode,
        "independence": ("isolated: first-wave reviewers ran in separate subagent contexts and "
                         "did not see each other's findings" if mode == "isolated" else
                         "single-context review — not independent"),
        "fingerprint": scope["fingerprint"],
        "head": scope["head"], "branch": scope["branch"], "base": scope["base"],
        "reviewed_paths": scope["reviewed_paths"],
        "depth": scope["depth"],
        "reviewers_planned": scope["reviewers"],
        "reviewers": reviewers,
        "coverage": cov,
        "tree_changed_during_review": current != scope["fingerprint"]["tree"],
        "findings": strip_private(sorted(findings, key=order_key)),
        "raw_findings": [{"uid": f["uid"], "reviewer": f["reviewer"], "severity": f["severity"],
                          "claim": f["claim"], "file": location(f)[0],
                          "line": f["evidence"].get("line")} for f in raw],
        "merges": merges,
        "duplicates_merged": len(merges),
        "dimensions": dims,
        "counts": counts,
        "verdict": verdict,
        "problems": problems,
        "eval": {"case_id": scope.get("case_id"),
                 "match_on": "findings[].location.file + line range + claim; raw_findings keep "
                             "per-reviewer attribution before merging"},
        "usage_note": "tokens/duration come from the runtime's subagent report when the "
                      "orchestrator saved usage.json; cost is null unless the runtime reports it",
        "run_dir": scope["run_dir"],
        "kind": scope.get("kind", "change"),
        "journey": scope.get("journey"),
        "commitment": scope.get("commitment"),
    }
    if scope.get("temporary"):
        out = os.path.join(run_dir, "record.json")
        with open(out, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
    else:
        rdir = records_dir(root)
        if record["kind"] == "care":   # a care pass isn't a change review: the launch gate never reads it
            rdir = os.path.join(rdir, "care")
            os.makedirs(rdir, exist_ok=True)
        out = os.path.join(rdir, record["id"] + ".json")
        with open(out, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        shutil.copyfile(out, os.path.join(rdir, "latest-care.json" if record["kind"] == "care" else "latest.json"))
    print(render(record))
    print("")
    print("Record: %s" % (out if scope.get("temporary") else os.path.relpath(out, root)))
    return 0


# ── freshness ────────────────────────────────────────────────────────────

def load_latest(root, path=None):
    p = path or os.path.join(root, ".ship", "reviews", "latest.json")
    if not os.path.exists(p):
        return None
    try:
        return load_json(p)
    except ValueError:
        return None


def cmd_freshness(a):
    root = toplevel()
    os.chdir(root)
    rec = load_latest(root, a.record)
    if not rec:
        res = {"state": "NO_REVIEW", "message": "No review record in .ship/reviews/ — run /shipmate review."}
        print(json.dumps(res, indent=2, ensure_ascii=False) if a.json else res["message"])
        return 3
    current = fingerprint()
    reviewed = rec["fingerprint"]["tree"]
    open_blockers = [f["id"] for f in rec.get("findings", [])
                     if f["severity"] == "blocker" and f.get("status") != "disputed"]
    res = {"state": "FRESH" if current == reviewed else "STALE", "record": rec["id"],
           "reviewed_at": rec.get("created_at"), "reviewed_tree": reviewed, "current_tree": current,
           "verdict": rec.get("verdict"), "open_blockers_at_review": open_blockers,
           "coverage": (rec.get("coverage") or {}).get("state", "unknown (record predates coverage tracking)"),
           "mode": rec.get("mode"), "changed_since_review": []}
    if res["state"] == "STALE":
        if object_exists(reviewed):
            res["changed_since_review"] = changed_paths(reviewed, current)
        else:
            res["note"] = ("the reviewed snapshot is no longer in .git/objects (pruned by git gc); "
                           "can't list what changed")
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        if res["state"] == "FRESH":
            print("FRESH — the files match review %s (%s, verdict %s)." % (
                rec["id"], rec.get("created_at"), rec.get("verdict")))
        else:
            print("STALE — files changed since review %s (%s):" % (rec["id"], rec.get("created_at")))
            for p in res["changed_since_review"]:
                print("  %s %s" % (p["status"], p["path"]))
            if res.get("note"):
                print("  (%s)" % res["note"])
        if rec.get("mode") == "single-context":
            print("Note: that review was single-context (not independent).")
        if res["coverage"] != "complete":
            print("Coverage: %s — freshness alone doesn't make it a complete review (see `review.py gate`)."
                  % res["coverage"])
        if open_blockers:
            print("Blockers open at review time: %s" % ", ".join(open_blockers))
    return 0 if res["state"] == "FRESH" else 1


GATE_EXIT = {"PASS": 0, "STALE": 1, "INCOMPLETE": 2, "NO_REVIEW": 3, "BLOCKERS": 4}


def cmd_gate(a):
    """/shipmate launch's review check: fresh AND complete AND no open blocker."""
    root = toplevel()
    os.chdir(root)
    rec = load_latest(root, a.record)
    if not rec:
        res = {"gate": "NO_REVIEW", "message": "No review record in .ship/reviews/ — run /shipmate review."}
    elif rec.get("kind") == "care":   # Codex release review R2: a care pass never satisfies launch
        res = {"gate": "NO_REVIEW", "record": rec["id"], "kind": "care",
               "message": "That record is a care pass, which never counts as the review launch needs — run /shipmate review."}
    else:
        current = fingerprint()
        reviewed = rec["fingerprint"]["tree"]
        cov = rec.get("coverage")
        blockers = [f["id"] for f in rec.get("findings", [])
                    if f["severity"] == "blocker" and f.get("status") != "disputed"]
        res = {"record": rec["id"], "reviewed_at": rec.get("created_at"), "mode": rec.get("mode"),
               "fresh": current == reviewed, "coverage": cov["state"] if cov else None,
               "not_completed": [x for x in (cov or {}).get("reviewers", [])
                                 if x.get("selected") and x.get("completion") != "completed"],
               "open_blockers": blockers, "verdict": rec.get("verdict")}
        if current != reviewed:
            res["gate"] = "STALE"
            res["message"] = "Files changed since the review — review the changes before launch."
            if object_exists(reviewed):
                res["changed_since_review"] = changed_paths(reviewed, current)
        elif not cov:
            res["gate"] = "INCOMPLETE"
            res["message"] = "The review record predates coverage tracking — re-run /shipmate review."
        elif cov["state"] != "complete":
            res["gate"] = "INCOMPLETE"
            res["message"] = ("Not every selected reviewer completed (%s) — finish or re-run them, or the "
                              "founder accepts launching on a partial review (log it in DECISIONS.md)."
                              % ", ".join("%s %s" % (x["reviewer"], x["completion"]) for x in res["not_completed"]))
        elif blockers:
            res["gate"] = "BLOCKERS"
            res["message"] = "Blockers open at review time: %s" % ", ".join(blockers)
        else:
            res["gate"] = "PASS"
            res["message"] = "Fresh, complete review with no open blockers."
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("%s — %s" % (res["gate"], res["message"]))
        for p in res.get("changed_since_review", []):
            print("  %s %s" % (p["status"], p["path"]))
        if res.get("mode") == "single-context":
            print("Note: that review was single-context (not independent).")
    return GATE_EXIT[res["gate"]]


def cmd_fingerprint(_a):
    toplevel()
    print(fingerprint())
    return 0


def use_side_object_store():
    """Mirror review-fingerprint.sh: when .git/objects isn't writable (sandboxed agents), snapshot
    objects live in .ship/state/git-objects; every git call here must be able to read them."""
    try:
        root = git(["rev-parse", "--show-toplevel"]).strip()
        objects = git(["rev-parse", "--git-path", "objects"]).strip()
    except RuntimeError:
        return
    objects = objects if os.path.isabs(objects) else os.path.join(root, objects)
    side = os.path.join(root, ".ship", "state", "git-objects")
    if not os.access(objects, os.W_OK):
        os.makedirs(side, exist_ok=True)
        os.environ["GIT_OBJECT_DIRECTORY"], os.environ["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = side, objects
    elif os.path.isdir(side):
        os.environ["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = side


def main(argv=None):
    use_side_object_store()
    ap = argparse.ArgumentParser(prog="review.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("scope")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--base")
    g.add_argument("--since-review", action="store_true")
    s.add_argument("--depth", choices=["quick", "standard", "full"])
    s.add_argument("--only", help="comma-separated reviewers, e.g. pol or crit,test")
    s.add_argument("--case", help="evaluation case id (also SHIP_EVAL_CASE)")
    s.add_argument("--care", action="store_true", help="care pass over a whole journey (care-lens.md) — preview")
    s.add_argument("--journey", help="the task the care pass walks, in plain words")
    s.add_argument("--paths", nargs="*", help="the journey's files (globs allowed); default: what changed")
    s.add_argument("--commitment", choices=["probe", "experiment", "promise"],
                   help="the task's commitment (ship.py state); a promise gets at least a standard review")
    s.add_argument("--json", action="store_true")
    v = sub.add_parser("validate")
    v.add_argument("files", nargs="+")
    c = sub.add_parser("consolidate")
    c.add_argument("run_dir")
    c.add_argument("--draft", action="store_true")
    c.add_argument("--mode", choices=["isolated", "single-context"], default="isolated")
    f = sub.add_parser("freshness")
    f.add_argument("--record")
    f.add_argument("--json", action="store_true")
    g = sub.add_parser("gate")
    g.add_argument("--record")
    g.add_argument("--json", action="store_true")
    sub.add_parser("fingerprint")
    a = ap.parse_args(argv)
    fn = {"scope": cmd_scope, "validate": cmd_validate, "consolidate": cmd_consolidate,
          "freshness": cmd_freshness, "gate": cmd_gate, "fingerprint": cmd_fingerprint}.get(a.cmd)
    if not fn:
        ap.print_help()
        return 2
    return fn(a)


if __name__ == "__main__":
    sys.exit(main())

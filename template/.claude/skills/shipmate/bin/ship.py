#!/usr/bin/env python3
"""/shipmate's facts and first guess — the deterministic half of "Ship figures it out".

  ship.py state [--root R] [--json]                what the project looks like now (reads only)
  ship.py route --text "<request>" [--root R] [--json]   a candidate stage from tested rules
  ship.py start --text "<request>" [--root R] [--json]   both, plus the knowledge route for the
                                                          request, recorded for review

The model makes the final call: it takes the candidate or overrides it with a stated reason (the
conversation can say more than the words). `ask` marks requests where two stages fit and would
lead to different work. Nothing is written except the knowledge route record under .ship/state/.
Design notes: SHIP-NEXT-PLAN.md §4.2 in the Ship Framework repository.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent.parent            # project: .claude/skills · plugin: skills

STAGES = ("think", "design", "plan", "build", "review", "qa", "browse", "perf", "fix", "launch",
          "money", "retro", "variants", "html", "team", "codex", "careful", "freeze", "unfreeze",
          "guard", "update")

# (stage, weight, pattern) — the entry's "Use for" column, as tested rules. Weight 3 = unmistakable,
# 2 = a clear phrase, 1 = a generic verb that only decides when nothing clearer matched.
RULES = [
    ("think", 2, r"\b(worth building|validate (this|the|my) idea|(?<!how )(?<!what )should (we|i) (even )?build|new idea|i'?m thinking about|thinking of building)\b"),
    ("design", 2, r"\b(design system|design this|create a design|visual direction|style guide|brand|design tokens?|tokens|theme|adopt|use my existing design|we already have a theme|colou?r palette)\b"),
    ("plan", 2, r"\b(plan (this|it|the|a|out)|how should (we|i) build|architecture|what'?s the approach|design the system|spec (this|it) out|break (this|it) down)\b"),
    ("build", 1, r"\b(build|make|implement|code|create|add|let'?s make)\b"),
    ("build", 2, r"\b(animation|animate|transitions?|dismiss|janky|jank|snappier|smoother|timing is off|feels? (off|heavy|abrupt|jumpy|stiff|floaty)|spring|easing)\b"),
    ("review", 2, r"\b(review (this|it|my|the)|is (this|it) ready|check my changes|is (this|it) good enough|code review|audit|what needs fixing|look it over)\b"),
    # the care pass (review --care): what's missing, not what's wrong
    ("review", 3, r"\b(feels? (generic|soulless|bland|flat|lifeless|cheap|like every other app)|looks? generic|what'?s missing|cared for|care pass|no soul|make it feel special)\b"),
    # watching real people use it: the care pass plans the sessions and reads the notes as evidence
    ("review", 3, r"\b(watch (\w+ )?(people|users|customers|someone) (use|try|book|sign up|order|pay)|usability (tests?|sessions?|testing)|user testing|test (it |this )?with (real )?(people|users))\b"),
    ("qa", 2, r"\b(run (the )?tests|test this|qa)\b"),
    ("browse", 2, r"\b(check the ui|how does it look|visual check|screenshots?|browse)\b"),
    ("perf", 3, r"\b(core web vitals|lcp|inp|cls|bundle size|lighthouse|load times?|slow to load|page (is )?slow|performance|speed (it )?up|optimi[sz]e)\b"),
    ("fix", 3, r"\b(fix (this|it|the|my)|something broke|broken|bug|not working|doesn'?t work|crash(es|ed|ing)?|regression|stopped working)\b"),
    # "launch" alone is often the app starting ("slow on launch", "launch screen") — only deploy phrases count
    ("launch", 3, r"\b(ship it|deploy\w*|go live|push to production|release (it|this|the app|to \w+|now|a new version)|let'?s launch|launch (it|this|the app|now|today|to \w+)|ready to launch|testflight|submit to the app store)\b"),
    # "revenue" alone is often data on a screen ("revenue over 12 months"): only money intent counts
    ("money", 2, r"\b(add payments|payments?|monetiz\w*|pricing(?! (page|table|section|cards?))|revenue (model|streams?)|(grow|increase|more) revenue|make money|subscriptions?|paywall)\b"),
    ("retro", 2, r"\b(retro|retrospective|what did we learn|weekly review|how did we do)\b"),
    ("variants", 2, r"\b(show (me )?options|design variants|variants|explore layouts|which design|compare approaches)\b"),
    ("html", 2, r"\b(prototype|quick html|mockup|proof of concept)\b"),
    ("team", 2, r"\b(what should we build next|prioriti[sz]e|roadmap|take over this project|assess this codebase|health check|state of things|add tasks|update tasks|on my plate|show me the board)\b"),
    ("codex", 3, r"\b(codex|second opinion|cross-model)\b"),
    ("careful", 3, r"\b(be careful|destructive commands?)\b"),
    ("freeze", 3, r"\b(freeze|lock (edits|it|this|the)|don'?t touch)\b"),
    ("unfreeze", 3, r"\b(unfreeze|unlock)\b"),
    ("guard", 3, r"\b(guard mode|freeze and careful)\b"),
    ("update", 3, r"\b(update ship|update (the )?framework|upgrade ship)\b"),
]
ERROR_SIGNS = re.compile(
    r"(Traceback \(most recent call last\)|^\s*at .+\(.+:\d+(:\d+)?\)|Thread \d+:|EXC_[A-Z_]+|Fatal error:|"
    r"Uncaught |\w+Error: |\w+Exception\b|SIGABRT|panic:|error: |Error: )", re.M)
CONTINUE = re.compile(r"^(continue|what'?s next|keep going|next|go on|carry on|pick up where we left off)[.!?]*$")
PAIR = re.compile(r"^(plan and build|build and review|fix and review|design and build|review and (ship|launch))\b")
MULTI = re.compile(r"\b(and then|then review|then ship|end to end|all the way|build and review|plan and build|fix and review)\b")
SLOW = re.compile(r"\b(slow|slower|laggy|lag|lags|sluggish)\b")
MOTION_TOKEN = re.compile(r"\b(motion|animation|spring|easing|duration)s? tokens?\b|\btokens? for (the )?(motion|animation)")
SEQUENCES = {("plan", "build"), ("build", "review"), ("fix", "review"), ("review", "launch"), ("design", "build")}
REDIRECT = {"build": "say 'plan it first' to change it", "fix": "say 'just diagnose' to stop before a fix",
            "review": "say 'quick' or 'full' to change the depth", "design": "say 'just show me' to stop before writing",
            "plan": "say 'just build it' to skip the plan", "team": "name a stage to go straight there",
            "launch": "say 'just check' to stop before deploying"}
# How the founder hears a stage's path: Ship's flags and area names stay in the record.
SAY_PATH = {"--care": "Care review", "--tokens": "Design, new motion tokens", "--motion-tune": "Design, tuning motion",
            "adopt": "Design, starting from the app's current look", "extend": "Design, extending the system",
            "seed": "Design, a first direction"}
SKIP_DIRS = {".git", "node_modules", ".build", "build", "dist", "DerivedData", ".claude", ".ship", "Pods",
             ".next", "coverage", ".venv", "vendor", ".gradle"}


def tool(skill, name):
    """A sibling Ship tool in either layout (project: ship/<skill>/, plugin: ship-<skill>/)."""
    for cand in (SKILLS / "ship" / skill / "bin" / name, SKILLS / ("ship-" + skill) / "bin" / name):
        if cand.is_file():
            return cand
    return None


def run(cmd, root):
    try:
        r = subprocess.run(cmd, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def git(root, *args):
    code, out = run(["git", *args], root)
    return out if code == 0 else None


def tasks(root):
    """In progress, up next and blocked items from TASKS.md (comments and blanks skipped)."""
    f = root / "TASKS.md"
    out = {"in_progress": [], "up_next": [], "blocked": []}
    if not f.is_file():
        return out
    section, text = None, re.sub(r"<!--.*?-->", "", f.read_text(encoding="utf-8", errors="replace"), flags=re.S)
    for line in text.splitlines():
        h = re.match(r"^##\s+(.*)", line)
        if h:
            title = h.group(1).lower()
            section = ("in_progress" if title.startswith("in progress") else "up_next" if title.startswith("up next")
                       else "blocked" if title.startswith("blocked") else None)
            continue
        # "---" rules aren't items; a ticked box ("- [x]", "1. [x]", "- 1a. [x]") is done, not active
        item = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(?:\d+[a-z]?[.)]\s+)?(\[[ xX]\]\s*)?(.+\S)", line)
        if section and item and (item.group(1) or "").strip().lower() != "[x]":
            out[section].append(re.sub(r"\s+", " ", item.group(2).replace("[IN PROGRESS]", "")).strip())
    if not any(out.values()):   # a flat checklist (no template sections): what SessionStart counts
        for line in text.splitlines():
            m = re.match(r"^\s*[-*]\s+\[ \]\s+(.+\S)", line)
            if m:
                key = "in_progress" if "[IN PROGRESS]" in m.group(1) else "up_next"
                out[key].append(re.sub(r"\s+", " ", m.group(1).replace("[IN PROGRESS]", "")).strip())
    return out


def ui_code(root):
    """Is there UI code to adopt? git-tracked files first (respects .gitignore), else a bounded walk."""
    listed = git(root, "ls-files")
    paths = listed.splitlines() if listed else []
    if not paths:
        for d, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            paths += [os.path.relpath(os.path.join(d, f), root) for f in files]
            if len(paths) > 4000:
                break
    for p in paths[:6000]:
        if any(part in SKIP_DIRS for part in Path(p).parts):
            continue
        if p.endswith((".tsx", ".jsx", ".vue", ".svelte")):
            return p
        if p.endswith((".swift", ".kt")):
            try:
                body = (root / p).read_text(encoding="utf-8", errors="replace")[:20000]
            except OSError:
                continue
            if re.search(r"\bimport SwiftUI\b|: View\b|@Composable", body):
                return p
    return None


def unwired_skills(root, claude_text):
    """The founder's own skills (.claude/skills/your-skills/<name>/SKILL.md) that CLAUDE.md never names —
    wired, or declined with a note — so /shipmate offers to wire each one once."""
    out, wiring = [], re.sub(r"<!--.*?-->", "", claude_text, flags=re.S)   # examples in comments don't count
    for f in sorted((root / ".claude/skills/your-skills").glob("*/SKILL.md")):
        m = re.search(r"^name:\s*[\"']?([\w.-]+)", f.read_text(encoding="utf-8", errors="replace"), re.M)
        name = m.group(1) if m else f.parent.name
        if not re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", wiring):
            out.append(name)
    return out


GENERIC_TITLES = re.compile(r"^(agents?(\.md)?|agent instructions|repository guidelines|project guide|readme)$", re.I)


def product_name(root, claude_text):
    """CLAUDE.md's title; else AGENTS.md's, before a dash or colon ("CoachEva — Codex Project Guide");
    else the app project's own name (an .xcodeproj, package.json)."""
    h1 = re.search(r"^#\s+(.+)$", claude_text, re.M)
    if h1:
        return h1.group(1).strip()
    agents = root / "AGENTS.md"
    if agents.is_file():
        h1 = re.search(r"^#\s+(.+)$", agents.read_text(encoding="utf-8", errors="replace"), re.M)
        name = re.split(r"\s+[—–-]\s+|:\s", h1.group(1).strip())[0].strip() if h1 else ""
        if name and not GENERIC_TITLES.match(name):
            return name
    for proj in sorted(root.glob("*.xcodeproj")) + sorted(root.glob("*/*.xcodeproj")):
        if not any(part in SKIP_DIRS for part in proj.relative_to(root).parts):
            return proj.stem
    try:
        name = json.loads((root / "package.json").read_text(encoding="utf-8")).get("name") or ""
        return name.split("/")[-1] or None
    except (OSError, ValueError):
        return None


def state(root):
    facts = {"root": str(root)}
    k = tool("knowledge", "knowledge.py")
    proj = {}
    if k:
        code, out = run([sys.executable, str(k), "project", "--root", str(root), "--json"], root)
        if code == 0:
            proj = json.loads(out)
    claude = root / "CLAUDE.md"
    text = claude.read_text(encoding="utf-8", errors="replace") if claude.is_file() else ""
    product = product_name(root, text)
    ship_section = bool(proj.get("ship_section_in_claude_md"))
    facts.update({
        "product": product, "stack": proj.get("stack", []), "stack_from": proj.get("stack_from"),
        "ship_section": ship_section,
        "setup_needed": ship_section and (not product or product.startswith("[") or not proj.get("stack")),
        "memory": proj.get("memory", []), "design_contract": proj.get("design_contract", []),
        "registry": (root / "design-model.yaml").is_file(), "pdc": (root / "PDC.md").is_file(),
        "point_of_view": bool(re.search(r"^##\s+Point of view\b", (root / "DESIGN.md").read_text(encoding="utf-8", errors="replace"), re.M))
        if (root / "DESIGN.md").is_file() else False,
    })
    facts["ui_code"] = ui_code(root)
    porcelain = git(root, "status", "--porcelain", "--untracked-files=all")
    ship_own = (".ship/", ".claude/skills/ship/", ".claude/skills/shipmate/", ".claude/skills/ship-",
                ".claude/agents/ship-", ".claude/commands/ship-", ".claude/team-rules.md")
    # untracked files that aren't the founder's work: knowledge.py's and review.py's list
    leftover = lambda p: p.startswith((".claude/", "design/taste.yaml")) or p.lower().endswith(
        (".patch", ".diff", ".orig", ".rej", ".bak", ".log", ".tmp", ".swp"))
    changed = [l[3:] for l in (porcelain or "").splitlines()
               if l[3:] and not l[3:].startswith(ship_own) and not (l.startswith("??") and leftover(l[3:]))]
    facts["git"] = porcelain is not None
    facts["changes"] = changed
    facts["tasks"] = tasks(root)
    tagged = [re.search(r"\[(probe|experiment|promise)\]", x, re.I) for x in facts["tasks"]["in_progress"]]
    facts["commitment"] = next((m.group(1).lower() for m in tagged if m), None)   # care-lens.md §6
    facts["unwired_skills"] = unwired_skills(root, text)
    r = tool("review", "review.py")
    facts["review"] = "unknown"
    if r and facts["git"]:
        code, out = run([sys.executable, str(r), "freshness", "--json"], root)
        try:
            facts["review"] = json.loads(out).get("state", "unknown")
        except (json.JSONDecodeError, ValueError):
            pass
    rec = root / ".ship/state/route.json"
    facts["last_route"] = None
    if rec.is_file():
        try:
            d = json.loads(rec.read_text(encoding="utf-8"))
            facts["last_route"] = {"at": d.get("at"), "domains": d.get("domains", [])}
        except json.JSONDecodeError:
            pass
    return facts


def route(text, facts):
    """The candidate stage for a request, with the rule that picked it."""
    raw = (text or "").strip()
    t = raw.lower()
    stack = [s.lower() for s in facts.get("stack") or []]
    out = {"stage": "team", "why": "", "ask": False, "alternatives": [], "request": raw, "path": None, "then": []}
    first = t.partition(" ")[0].rstrip(":,.!?")
    if not t or CONTINUE.match(t):
        out["why"] = "nothing after /shipmate or 'continue' — pick up the next task"
        return out
    if first in ("help", "status") and len(t.split()) <= 2:
        out.update(stage=first, why="asked for " + first)
        return out
    # Order: a pasted error beats setup (a crash gets fixed); setup beats everything else (old rule 4);
    # a named stage beats pattern matching.
    if ERROR_SIGNS.search(raw):
        out.update(stage="fix", why="an error message or stack trace in the request")
        return out
    if facts.get("setup_needed"):
        out["why"] = "CLAUDE.md still has unfilled fields (product name or stack) — team setup first"
        return out
    pair = PAIR.match(t)
    if pair:
        out.update(why=f"'{pair.group(0)}' — team runs both stages in order",
                   alternatives=[w for w in re.findall(r"[a-z]+", pair.group(0)) if w in STAGES or w == "ship"][:2])
        return out
    if first in STAGES:
        out.update(stage=first, why="named the stage", request=raw.split(" ", 1)[1] if " " in raw else "")
        after = t.split("then", 1)[1] if MULTI.search(t) and "then" in t else ""
        out["then"] = [s for s, w, rx in RULES if w >= 2 and s != first and after and re.search(rx, after)][:2]
        return _paths(out, t, facts)
    scores = {}
    hits = {}
    for stage, weight, rx in RULES:
        m = re.search(rx, t)
        if m and weight > scores.get(stage, 0):
            scores[stage], hits[stage] = weight, m.group(0)
    if SLOW.search(t) and "perf" not in scores and "build" not in (s for s, w in scores.items() if w >= 2):
        if "web" in stack:
            out.update(stage="perf", ask=True, alternatives=["fix"],
                       why=f"'{SLOW.search(t).group(0)}' without load or animation words — measure (perf) or debug (fix)?")
        else:
            out.update(stage="fix", why=f"'{SLOW.search(t).group(0)}' on {', '.join(stack) or 'this stack'} — debug it (perf measures web vitals)")
        return out
    if MOTION_TOKEN.search(t) and facts.get("registry"):
        out.update(stage="design", why="motion tokens in the design system", path="--tokens" if re.search(r"\bnew\b", t) else "--motion-tune")
        return out
    strong = sorted((s for s, w in scores.items() if w >= 2), key=lambda s: -scores[s])
    if MULTI.search(t) or (len(strong) >= 2 and (strong[0], strong[1]) in SEQUENCES | {(b, a) for a, b in SEQUENCES}):
        out["why"] = "several stages in one request — team runs them in order"
        out["alternatives"] = strong[:2]
        return out
    if not scores:
        out["why"] = "no stage fits clearly — team works out the sequence"
        return out
    ranked = sorted(scores, key=lambda s: -scores[s])
    best = ranked[0]
    if (best == "build" and scores[best] < 2 and not facts.get("registry") and not facts.get("ui_code")
            and UI_WORK.search(t)):
        out.update(stage="design", then=["build"],
                   why="a new product with no design yet: the design stage sets the direction, then build")
        return _paths(out, t, facts)
    out.update(stage=best, why=f"matched \"{hits[best]}\"")
    if len(ranked) > 1 and scores[ranked[1]] == scores[best] and scores[best] >= 2:
        out.update(ask=True, alternatives=[ranked[1]],
                   why=f"matched \"{hits[best]}\" ({best}) and \"{hits[ranked[1]]}\" ({ranked[1]}) equally")
    return _paths(out, t, facts)


# UI work asked for in plain words ("make a website where…", "create the app"): on a product with no
# design yet, the design stage sets the direction first; the design gate would stop UI edits anyway.
UI_WORK = re.compile(r"\b(web ?site|site|web ?page|page|landing|app|screens?|ui|interface|looks?|home ?page)\b")

CARE = re.compile(r"\b(feels? (generic|soulless|bland|flat|lifeless|cheap|like every other app)|looks? generic|what'?s missing|cared for|care pass|no soul|make it feel special|watch (\w+ )?(people|users|customers|someone) (use|try|book|sign up|order|pay)|usability (tests?|sessions?|testing)|user testing|test (it |this )?with (real )?(people|users))\b")


def _paths(out, t, facts):
    if out["stage"] == "review" and not out.get("path") and CARE.search(t):
        out["path"] = "--care"
    if out["stage"] == "design" and not out.get("path"):
        out["path"] = ("adopt" if "adopt" in t else "extend" if facts.get("registry")
                       else "adopt" if facts.get("ui_code") else "seed")
    return out


def knowledge_route(root, text):
    k = tool("knowledge", "knowledge.py")
    if not k or not text:
        return None
    code, out = run([sys.executable, str(k), "route", "--root", str(root), "--text", text,
                     "--changed", "--record", "--json"], root)
    if code != 0:
        return None
    r = json.loads(out)
    return {"domains": r["domains"],
            "refs": [ref["path"] for s in r["sources"] for ref in s["ship_refs"]],
            "context": r.get("context", [])}


def summary(facts):
    tk = facts["tasks"]
    setup = "needed" if facts["setup_needed"] else "ok" if facts["ship_section"] else "not bootstrapped (works without it)"
    lines = [
        f"Ship · {facts.get('product') or 'unnamed'} · {', '.join(facts['stack']) or 'stack unknown'}"
        f" ({facts.get('stack_from') or '—'}) · setup: {setup}",
        f"Design: registry {'yes' if facts['registry'] else 'no'} · UI code {'yes' if facts['ui_code'] else 'no'}"
        f" · PDC {'yes' if facts['pdc'] else 'no'} · point of view {'yes' if facts['point_of_view'] else 'no'}",
        f"Work: {len(facts['changes'])} changed file(s)"
        + (f" · in progress: {tk['in_progress'][0]!r}" if tk["in_progress"] else "")
        + (f" · up next: {tk['up_next'][0]!r}" if tk["up_next"] else "")
        + (f" · blocked: {len(tk['blocked'])}" if tk["blocked"] else "")
        + (f" · commitment: {facts['commitment']}" if facts.get("commitment") else "")
        + f" · last review: {facts['review']}",
    ]
    if facts.get("unwired_skills"):
        lines.append("Your skills not wired in CLAUDE.md yet: " + ", ".join(facts["unwired_skills"])
                     + " (offer once to wire each)")
    return lines


def main():
    ap = argparse.ArgumentParser(description="/shipmate's facts and first guess")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("state", "route", "start"):
        p = sub.add_parser(name)
        p.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR") or ".")
        p.add_argument("--json", action="store_true")
        if name != "state":
            p.add_argument("--text", default="")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    facts = state(root)
    if a.cmd == "state":
        if a.json:
            print(json.dumps(facts, indent=2))
        else:
            print("\n".join(summary(facts)))
        return 0
    cand = route(a.text, facts)
    if a.cmd == "route":
        print(json.dumps(cand, indent=2) if a.json else
              f"{cand['stage']}" + (f" ({cand['path']})" if cand.get("path") else "") + f" — {cand['why']}"
              + (f" · then {', '.join(cand['then'])}" if cand["then"] else "")
              + (f" · also fits: {', '.join(cand['alternatives'])}" if cand["alternatives"] else "")
              + (" · ASK" if cand["ask"] else ""))
        return 0
    ask_text = cand["request"] or (facts["tasks"]["in_progress"][:1] or [""])[0]
    kr = knowledge_route(root, ask_text) if cand["stage"] not in ("help", "status") else None
    if a.json:
        print(json.dumps({"facts": facts, "candidate": cand, "knowledge": kr}, indent=2))
        return 0
    print("\n".join(summary(facts)))
    stage = cand["stage"] + (f" ({cand['path']})" if cand.get("path") else "")
    print(f"Stage: {stage} — {cand['why']}" + (f" · then {', '.join(cand['then'])}" if cand["then"] else "")
          + (f" · also fits: {', '.join(cand['alternatives'])}" if cand["alternatives"] else "")
          + (" · ASK before starting" if cand["ask"] else ""))
    if kr:
        areas = ", ".join(kr["domains"]) or "none beyond product sources"
        print(f"References (recorded for review): {areas}" + (f" — {len(kr['refs'])} file(s)" if kr["refs"] else ""))
        for r in kr["refs"]:
            print("  " + r)
    if cand["stage"] not in ("help", "status"):
        label = SAY_PATH.get(cand.get("path")) or cand["stage"].capitalize()
        redirect = ("say 'normal review' for a change review instead, or name another flow"
                    if cand.get("path") == "--care" else REDIRECT.get(cand["stage"], "name another stage to change it"))
        print(f"Say it: \"{label} · {redirect}.\"")   # reference areas stay in the record, not the reply
    return 0


if __name__ == "__main__":
    sys.exit(main())

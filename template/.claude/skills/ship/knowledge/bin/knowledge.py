#!/usr/bin/env python3
"""Ship knowledge routing — which sources to consult for a task, in precedence order,
and whether the skills and tools Ship routes to are installed.

    knowledge.py route   [--domain D[,D]] [--text "task"] [--files F ...] [--changed] [--record]
                         [--stack S] [--json]
    knowledge.py doctor  [--stack S] [--brief] [--record] [--json]
    knowledge.py versions [--json]
    knowledge.py note    [--stage S] [--read R] [--applied A] [--not-read N] [--verified V]
                         [--taste IDS] [--conflict C]
    knowledge.py check

`route` answers "what should I read before this change?" — product sources first, then
platform, Ship references, and installed skills, with a fallback for anything missing.
Selection, strongest first: domains you name (`--domain`, chosen by what the task means);
code the change touches (`--changed` reads the git diff, `--files` reads the files — animation,
form, gesture APIs…); words in `--text` (word forms match: animations → animation). Domains
that only match a file type are listed as context, not opened. `--record` saves the selection
to .ship/state/route.json — evidence of what was selected, not of what was read. `note` adds
what the stage says it read, applied and verified to the same record, for review: that
bookkeeping never goes in the founder's reply.
`doctor` reports dependency status; `--record` remembers versions in .ship/state/ so a
changed dependency is announced (it never overrides product decisions). `versions` prints
the knowledge versions in use, for review and evaluation records. `check` validates the
routing table itself (used by maintainers and CI).

Data: routing.json next to this skill — generated from .ship/framework.yaml by
scripts/render_ship_core.py. Never edit routing.json by hand. Stdlib only.
"""

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
PLUGIN_LAYOUT = SKILL_DIR.name == "ship-knowledge"
SKILLS_ROOT = SKILL_DIR.parent          # .claude/skills/ship  or  <plugin>/skills
ROUTING = SKILL_DIR / "routing.json"
STATE_FILE = Path(".ship") / "state" / "knowledge.json"
REF_HEADER = "<!-- ship-reference"


# ── Loading ──────────────────────────────────────────────────────────────────

def load_routing():
    try:
        return json.loads(ROUTING.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"knowledge.py: missing {ROUTING} — rebuild with scripts/render_ship_core.py")
    except json.JSONDecodeError as exc:
        sys.exit(f"knowledge.py: {ROUTING} is not valid JSON: {exc}")


def project_root(arg):
    return Path(arg or os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()


def resolve_ref(path):
    """Template path (.claude/skills/ship/<skill>/...) → file in this install's layout."""
    m = re.match(r"^\.claude/skills/ship/([a-z0-9-]+)/(.+)$", path)
    if not m:
        return None
    skill, rest = m.groups()
    return SKILLS_ROOT / (f"ship-{skill}" if PLUGIN_LAYOUT else skill) / rest


def display_ref(path):
    if not PLUGIN_LAYOUT:
        return path
    resolved = resolve_ref(path)
    return str(resolved) if resolved else path


def read_stack(root, override):
    if override:
        return override.lower()
    env = os.environ.get("SHIP_STACK")
    if env:
        return env.lower()
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        for line in claude_md.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("Stack:"):
                value = line.split(":", 1)[1].strip().lower()
                for stack in ("ios", "web", "android"):
                    if stack in value:
                        return stack
                return value or None
    found = [s for s, _ in detected_stacks(root) if s != "macos"]
    return found[0] if len(found) == 1 else None


def declared_stacks(root):
    """Every platform the Stack: line names (a repo can hold an iOS app and a website)."""
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        for line in claude_md.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("Stack:"):
                value = line.split(":", 1)[1].lower()
                return [s for s in ("ios", "web", "android") if s in value]
    return []


SKIP_DIRS = {".git", "node_modules", "Pods", "build", "DerivedData", ".build", ".ship", ".claude", "dist", ".next"}


def _project_files(root, depth=3):
    """Files near the top of the project (no vendored or build folders) — enough to spot its platform."""
    out, stack = [], [(root, 0)]
    while stack:
        d, lvl = stack.pop()
        try:
            entries = list(d.iterdir())
        except OSError:
            continue
        for e in entries:
            if e.is_dir() and e.name not in SKIP_DIRS and not e.name.endswith((".xcassets", ".lproj")):
                if e.suffix in (".xcodeproj", ".xcworkspace"):
                    out.append(e)
                if lvl < depth:
                    stack.append((e, lvl + 1))
            elif e.is_file():
                out.append(e)
    return out


def detected_stacks(root):
    """Platforms the project's own files show when CLAUDE.md declares none: [(stack, evidence)].
    An Apple project that only targets macOS isn't a Ship stack — reported as ("macos", evidence)."""
    found, macos = {}, None

    def read(f):
        try:
            return f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    for f in _project_files(root):
        rel = str(f.relative_to(root))
        if f.suffix == ".xcodeproj":
            text = read(f / "project.pbxproj")
            if re.search(r"SDKROOT = iphoneos|IPHONEOS_DEPLOYMENT_TARGET", text):
                found.setdefault("ios", rel)
            elif "SDKROOT = macosx" in text:
                macos = macos or rel
        elif f.name in ("project.yml", "project.yaml") and re.search(r"(?im)^\s*(iOS\s*:|platform\s*:\s*iOS)", read(f)):
            found.setdefault("ios", rel)
        elif f.name == "Package.swift" and ".iOS(" in read(f):
            found.setdefault("ios", rel)
        elif f.name in ("build.gradle", "build.gradle.kts") and "com.android" in read(f):
            found.setdefault("android", rel)
        elif f.name == "package.json" and "node_modules" not in rel:
            fw = detect_framework(f.parent)
            if fw and fw["id"] in WEB_FRAMEWORKS:
                found.setdefault("web", f"{rel} ({fw['id']})")
    out = sorted(found.items())
    if not out and macos:
        out = [("macos", macos)]
    return out


PLATFORM_EXT = {"ios": (".swift", ".xcstrings", ".xcprivacy", ".storyboard", ".xib"),
                "android": (".kt", ".kts"),
                "web": (".css", ".scss", ".html", ".vue", ".svelte", ".astro")}
# JS/TS is judged by the package that owns it: a website, a React Native app, a shared library,
# a server or tooling all use the same extensions.
JS_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts")
WEB_FRAMEWORKS = ("next", "svelte", "vue", "astro", "react")


def platform_of(path):
    name = str(path).lower()
    return next((p for p, exts in PLATFORM_EXT.items() if name.endswith(exts)), None)


def owning_package(root, f):
    """The directory of the package.json nearest a file, inside the project; None if there isn't one."""
    d = (root / f).parent
    while True:
        if (d / "package.json").is_file():
            return d
        if d == root or d.parent == d or root not in d.parents:
            return None
        d = d.parent


def task_target(root, override, files):
    """What this task targets: --stack, else the task's files, else Stack: in CLAUDE.md.
    Returns a dict — stacks, how (said in the route), pkg (where to detect the web framework),
    native_js (a React Native framework, if that's what owns the files) and unproven: the platforms
    whose own recipes are reference only here, because the target is uncertain or the code isn't
    the native UI toolkit those recipes are written for."""
    env = os.environ.get("SHIP_STACK")
    declared = [env.lower()] if env else declared_stacks(root)
    touched, pkg, native_js, loose = set(), None, None, []
    for f in files or []:
        if str(f).lower().endswith(JS_EXT):
            own = owning_package(root, f)
            fw = detect_framework(own) if own else None
            fid = (fw or {}).get("id")
            if fid == "react-native":
                native_js = native_js or fw
            elif fid in WEB_FRAMEWORKS or (not fw and str(f).lower().endswith((".tsx", ".jsx"))):
                touched.add("web")
                pkg = pkg or own
            else:
                loose.append((f, own))          # a shared library, a server, tooling — no UI of its own
        elif platform_of(f):
            touched.add(platform_of(f))
            if platform_of(f) == "web":
                pkg = pkg or owning_package(root, f)
    rel = lambda d: str(d.relative_to(root)) + "/package.json" if d and d != root else "package.json"
    out = {"pkg": pkg or root, "native_js": native_js, "unproven": set()}
    if override:
        out.update(stacks=[override.lower()], how="--stack")
    elif touched and (len(declared) != 1 or touched - set(declared)):
        out.update(stacks=sorted(touched), how="the task's files" + (f" (CLAUDE.md lists {', '.join(declared)})" if declared else ""))
    elif native_js and not touched:
        out.update(stacks=[s for s in declared if s != "web"] or declared, how="the task's files: a React Native package")
    elif loose and not touched and declared != ["web"]:
        f, own = loose[0]
        out.update(stacks=declared, how=f"uncertain — {f} belongs to {rel(own) if own else 'no package'}, which has no UI "
                   "framework (shared, server or tooling code?); pass --stack if it belongs to one platform")
        out["unproven"] = set(declared)
    elif declared:
        out.update(stacks=declared, how="CLAUDE.md")
        if len(declared) > 1:
            out["how"] = "uncertain — CLAUDE.md lists several platforms; pass the task's files or --stack"
            out["unproven"] = set(declared)
    else:
        found = [(s, ev) for s, ev in detected_stacks(root) if s != "macos"]
        if len(found) == 1:
            out.update(stacks=[found[0][0]], how=f"detected — {found[0][1]} (no Stack: line in CLAUDE.md)")
        elif found:
            out.update(stacks=[s for s, _ in found],
                       how="uncertain — the project holds " + ", ".join(f"{s} ({ev})" for s, ev in found)
                       + "; pass the task's files or --stack")
            out["unproven"] = {s for s, _ in found}
        else:
            out.update(stacks=[], how="unset")
    if native_js:
        # Ship has no React Native reference: SwiftUI / Compose recipes aren't its implementation
        out["unproven"] |= {"ios", "android"} & set(out["stacks"])
        out["how"] += (" — Ship has no React Native reference; SwiftUI/Compose recipes are reference only"
                       if out["how"].endswith("React Native package") else
                       " — React Native: Ship has no React Native reference; SwiftUI/Compose recipes are reference only")
    return out


# ── Skill + tool detection ───────────────────────────────────────────────────

def skill_dirs(root):
    """Where installed skills live, most specific first. SHIP_SKILL_PATHS (colon-separated)
    replaces the defaults — used by tests."""
    override = os.environ.get("SHIP_SKILL_PATHS")
    if override:
        return [(Path(p), "override") for p in override.split(":") if p]
    home = Path.home()
    return [
        (root / ".claude" / "skills", "project (Claude)"),
        (root / ".agents" / "skills", "project (Codex)"),
        (home / ".claude" / "skills", "user (Claude)"),
        (home / ".codex" / "skills", "user (Codex)"),
        (home / ".agents" / "skills", "user (Codex)"),
        (home / ".claude" / "plugins", "plugin (Claude)"),
        (home / ".codex" / "plugins", "plugin (Codex)"),
    ]


def find_skill(names, root, verify=None):
    """First installed skill folder named in `names`. `verify` is a file that must exist inside
    it — distinguishes two skills that share a folder name (e.g. two `swift-concurrency`s)."""
    def ok(cand):
        return (cand / "SKILL.md").is_file() and (not verify or (cand / verify).exists())

    for base, where in skill_dirs(root):
        if not base.is_dir():
            continue
        if where.startswith("plugin"):
            for dirpath, dirnames, _ in os.walk(base):
                depth = len(Path(dirpath).relative_to(base).parts)
                if depth > 7:
                    dirnames[:] = []
                    continue
                if Path(dirpath).name == "skills":
                    for name in names:
                        cand = Path(dirpath) / name
                        if ok(cand):
                            return cand, where
            continue
        for name in names:
            cand = base / name
            if ok(cand):
                return cand, where
    return None, None


# Generated or cached files that don't carry guidance; everything else in a skill package
# (SKILL.md, references/, scripts, templates, data) is substantive and part of its identity.
CACHE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache", ".pytest_cache",
              ".ruff_cache", ".cache"}
CACHE_FILES = {".DS_Store", "Thumbs.db"}
CACHE_SUFFIXES = (".pyc", ".pyo")


def content_identity(path):
    """Deterministic hash of the installed package's substantive files (paths + bytes).
    This is WHAT is installed now — independent of where it says it came from."""
    h, n = hashlib.sha256(), 0
    for dirpath, dirnames, files in os.walk(path):
        dirnames[:] = sorted(d for d in dirnames if d not in CACHE_DIRS)
        for name in sorted(files):
            if name in CACHE_FILES or name.endswith(CACHE_SUFFIXES):
                continue
            fp = Path(dirpath) / name
            rel = fp.relative_to(path).as_posix()
            try:
                data = ("symlink:" + os.readlink(fp)).encode() if fp.is_symlink() else fp.read_bytes()
            except OSError:
                data = b"<unreadable>"
            h.update(rel.encode("utf-8") + b"\0" + hashlib.sha256(data).digest())
            n += 1
    return "sha256:" + h.hexdigest()[:16], n


def skill_version(path, root=None):
    """Compatibility name (earlier callers and the 2026-09-23 review's reproduction script):
    the content identity of the installed package."""
    return content_identity(path)[0]


def skill_origin(path, root):
    """WHERE the skill says it came from — provenance, not proof of content. A git checkout
    reports its commit and whether the skill's files are modified; a skills-lock.json entry
    reports the hash the installer recorded (which may no longer match the files)."""
    try:
        top = subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
        repo = Path(top.stdout.strip()).resolve() if top.returncode == 0 and top.stdout.strip() else None
        proj = Path(root).resolve()
        # A skill inside the user's own project repo isn't versioned by that repo.
        if repo and repo != proj and repo not in proj.parents:
            head = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                                  capture_output=True, text=True, timeout=5)
            rel = os.path.relpath(str(Path(path).resolve()), str(repo))
            dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", rel],
                                   capture_output=True, text=True, timeout=10)
            if head.returncode == 0 and head.stdout.strip():
                return {"kind": "git", "commit": head.stdout.strip(),
                        "dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None}
    except (OSError, subprocess.SubprocessError):
        pass
    lock = root / "skills-lock.json"
    if lock.is_file():
        try:
            entry = json.loads(lock.read_text(encoding="utf-8")).get("skills", {}).get(path.name)
            if entry and entry.get("computedHash"):
                return {"kind": "lock", "hash": entry["computedHash"][:16], "source": entry.get("source")}
        except (json.JSONDecodeError, AttributeError):
            pass
    return {"kind": "unknown"}


def dependency_status(dep, root):
    path, where = find_skill(dep.get("detect") or [dep["skill"]], root, dep.get("verify"))
    # A "correction" is a verified fact that overrides a wrong claim in the skill — shown either way.
    if path:
        content, files = content_identity(path)
        return {"skill": dep["skill"], "installed": True, "where": where, "path": str(path),
                "content": content, "files": files, "origin": skill_origin(path, root),
                "version": content, "correction": dep.get("correction")}
    return {"skill": dep["skill"], "installed": False, "install": dep.get("install"),
            "fallback": dep.get("fallback"), "correction": dep.get("correction")}


def origin_label(o):
    if o.get("kind") == "git":
        return "git %s%s" % (o["commit"], " + local edits" if o.get("dirty") else "")
    if o.get("kind") == "lock":
        return "lock %s" % o["hash"][:12]
    return "origin unknown"


def compare_identity(name, prev, cur):
    """None when nothing to report; otherwise a reassessment note. Content decides; provenance
    explains. A changed hash means 'look again', never 'the new guidance is right'."""
    if not isinstance(prev, dict):
        return None  # older state format (one opaque string) — re-baselined silently
    if prev.get("content") == cur["content"]:
        return None
    po, co = prev.get("origin") or {}, cur["origin"]
    why = "installed files changed"
    if co.get("kind") == "git" and po.get("commit") == co.get("commit"):
        why += " with no new commit (local edits)" if co.get("dirty") else " at the same commit"
    elif co.get("kind") == "lock" and po.get("hash") == co.get("hash"):
        why += " but skills-lock.json still records the old hash — the lock entry is stale or the files were edited"
    elif po and po != co:
        why += " (%s → %s)" % (origin_label(po), origin_label(co))
    return {"skill": name, "reason": why}


def tool_status(tool):
    found = shutil.which(tool["check"])
    return {"tool": tool["name"], "installed": bool(found), "purpose": tool.get("purpose"),
            "install": None if found else tool.get("install")}


def expand_path(path):
    """~ and $(xcode-select -p) — Xcode's bundled guidance lives inside whichever Xcode is selected."""
    if "$(xcode-select -p)" in path:
        dev = "/Applications/Xcode.app/Contents/Developer"
        try:
            out = subprocess.run(["xcode-select", "-p"], capture_output=True, text=True, timeout=5)
            if out.returncode == 0 and out.stdout.strip():
                dev = out.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
        path = path.replace("$(xcode-select -p)", dev)
    return os.path.normpath(os.path.expanduser(path))


def point_status(point):
    out = dict(point)
    if point.get("path"):
        out["path"] = expand_path(point["path"])
        out["present"] = Path(out["path"]).exists()
    return out


# ── Routing ──────────────────────────────────────────────────────────────────

def word_hit(trigger, text):
    return re.search(r"(?<![a-z0-9])" + re.escape(trigger.lower()) + r"(?![a-z0-9])", text) is not None


WORD = re.compile(r"[a-z0-9@#+][a-z0-9@#+.\-]*")


def _strip(w):
    if len(w) > 5 and w.endswith("ier"):
        return w[:-3] + "y"
    for suf in ("ing", "ed", "es", "er", "ly", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            w = w[: -len(suf)]
            break
    return w[:-1] if len(w) > 4 and w.endswith("e") else w


def stem(word):
    """Light, predictable word forms, applied until stable so both sides agree:
    animations→animation, stutters/stutter→stutt, animating/animate→animat, calmer→calm,
    snappier→snappy. Not linguistics — enough that plural/-ing/-ed phrasing matches."""
    w = word.rstrip(".")
    for _ in range(3):
        nxt = _strip(w)
        if nxt == w:
            break
        w = nxt
    return w


# Pronouns never name an area; left in, "ask them" would match "theme" (both reduce to "them").
PRONOUNS = frozenset({"them", "they", "then", "there", "these", "those", "their"})


def stems(text):
    return " " + " ".join("·" if w in PRONOUNS else stem(w) for w in WORD.findall((text or "").lower())) + " "


def phrase_hit(trigger, text_lower, text_stems):
    """Exact phrase (keeps punctuation triggers like next.js, @state, prefers-reduced-motion), or the
    same words in their stemmed forms."""
    if word_hit(trigger, text_lower):
        return True
    t = " ".join(stem(w) for w in WORD.findall(trigger.lower()))
    return bool(t) and f" {t} " in text_stems


# Ship's own files in a project (an update rewrites them): never "the change" (ship.py's list too).
SHIP_OWN = (".ship/", ".claude/skills/ship/", ".claude/skills/shipmate/", ".claude/skills/ship-",
            ".claude/agents/ship-", ".claude/commands/ship-", ".claude/team-rules.md", "CHEATSHEET.md",
            "ship-update.sh")


# Untracked files that aren't the change: Claude Code's local settings, Ship's taste record, and
# leftovers such as a saved patch (review.py and ship.py leave out the same files).
NOT_THE_CHANGE = (".claude/", "design/taste.yaml")
LEFTOVER_EXT = (".patch", ".diff", ".orig", ".rej", ".bak", ".log", ".tmp", ".swp")


def changed_code(root, files, changed):
    """Text the change touches: added lines from the git diff (--changed), else the named files."""
    chunks, names = [], list(files or [])
    if changed:
        try:
            diff = subprocess.run(["git", "diff", "HEAD", "-U0", "--no-color"], cwd=root, capture_output=True,
                                  text=True, timeout=20).stdout
            keep = True
            for line in diff.splitlines():
                if line.startswith("diff --git "):
                    keep = not line.split(" b/", 1)[-1].startswith(SHIP_OWN)
                elif keep and line.startswith("+++ b/"):
                    names.append(line[6:])
                elif keep and line.startswith("+") and not line.startswith("+++"):
                    chunks.append(line[1:])
            untracked = [f for f in subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root,
                                                   capture_output=True, text=True, timeout=20).stdout.split()
                         if not f.startswith(SHIP_OWN + NOT_THE_CHANGE) and not f.lower().endswith(LEFTOVER_EXT)]
            names += untracked
            files = list(files or []) + untracked
        except (OSError, subprocess.SubprocessError):
            pass
    for f in files or []:
        path = (root / f) if not Path(f).is_absolute() else Path(f)
        if path.is_file() and path.stat().st_size < 400_000:
            try:
                chunks.append(path.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                pass
    return sorted(set(names)), "\n".join(chunks)


def detect_framework(root):
    """The web framework this project runs, with the installed version when node_modules has it."""
    pkg = root / "package.json"
    if not pkg.is_file():
        return None
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    deps = {**(data.get("dependencies") or {}), **(data.get("devDependencies") or {})}

    def version(name):
        installed = root / "node_modules" / name / "package.json"
        try:
            return json.loads(installed.read_text())["version"] + " (installed)"
        except (OSError, ValueError, KeyError):
            return (deps.get(name) or "?") + " (declared)"

    for fw, pkgs in (("next", ["next"]), ("svelte", ["@sveltejs/kit", "svelte"]), ("vue", ["nuxt", "vue"]),
                     ("astro", ["astro"]), ("react-native", ["react-native", "expo"]), ("react", ["react"])):
        hit = next((p for p in pkgs if p in deps), None)
        if hit:
            out = {"id": fw, "package": hit, "version": version(hit)}
            if fw in ("next", "react") and "react" in deps:
                out["react"] = version("react")
            if fw == "react" and "vite" in deps:
                out["bundler"] = "vite " + version("vite")
            if fw == "react":
                out["ssr"] = react_ssr_evidence(root, deps)
            return out
    return None


SSR_PACKAGES = ("@react-router/dev", "@remix-run/react", "@remix-run/node", "vike", "vite-plugin-ssr",
                "@tanstack/react-start", "react-server-dom-webpack", "react-server-dom-parcel")
SSR_CODE = re.compile(r"\b(hydrateRoot|renderToPipeableStream|renderToReadableStream|renderToString|"
                      r"prerenderToNodeStream|prerender)\s*\(")


def react_ssr_evidence(root, deps):
    """Server rendering outside Next.js — packages that server-render, or SSR/hydration calls in the
    source. Empty = no evidence found (a client-only app, as far as the project shows)."""
    found = [f"package {p}" for p in SSR_PACKAGES if p in deps]
    seen = 0
    for base in ("src", "app", "server", "."):
        d = root / base
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.[jt]s*") if base == "." else d.rglob("*.[jt]s*")):
            if "node_modules" in f.parts or seen > 400 or not f.is_file():
                continue
            seen += 1
            if f.stem.startswith("entry-server") or f.stem.startswith("entry.server"):
                found.append(f"file {f.relative_to(root)}")
            try:
                m = SSR_CODE.search(f.read_text(encoding="utf-8", errors="replace")[:200_000])
            except OSError:
                continue
            if m:
                found.append(f"{m.group(1)}() in {f.relative_to(root)}")
        if len(found) >= 3:
            break
    return sorted(set(found))[:3]


def framework_key(framework):
    """Note key: React outside Next.js splits on actual server-rendering evidence."""
    if not framework:
        return None
    if framework["id"] == "react" and framework.get("ssr"):
        return "react-ssr"
    return framework["id"]


# Other Ship tools' names for the same domains (taste.py says color/type/layout) — accepted, not an error.
DOMAIN_ALIASES = {"color": "colour", "colors": "colour", "colours": "colour", "type": "typography",
                  "layout": "layout-spacing", "spacing": "layout-spacing", "animation": "motion"}


def ensure_state_dir(root):
    """.ship/state/ with its own .gitignore — session state, never project history."""
    state = root / ".ship" / "state"
    state.mkdir(parents=True, exist_ok=True)
    ignore = state / ".gitignore"
    if not ignore.exists():
        ignore.write_text("# Ship session state — not project history\n*\n", encoding="utf-8")
    return state


def same_task(prev, text, window_minutes=30):
    """Is this route for the task the last record was about? Same words — or no words (a stage
    routing by meaning) within half an hour of it. A different task replaces the record."""
    if text:
        return prev.get("text") == text
    try:
        at = __import__("datetime").datetime.fromisoformat(prev.get("at", ""))
        age = __import__("datetime").datetime.now().astimezone() - at
    except (TypeError, ValueError):
        return False
    return age.total_seconds() < window_minutes * 60


def match_domains(routing, domains, text, files, stack, code="", framework=None):
    """Selected domains (named, code signals, task words) and context domains (file type only).
    `stack` is the target platform (or a list, for a task spanning a mixed repo). A named domain
    written for another platform is kept — deliberate cross-platform research — but marked
    cross-platform, never as directly applicable."""
    stacks = [x for x in ([stack] if isinstance(stack, str) else (stack or [])) if x]
    table = {d["id"]: d for d in routing["domains"]}
    picked, why = [], {}
    for d in [x.strip() for arg in (domains or []) for x in arg.split(",") if x.strip()]:
        d = DOMAIN_ALIASES.get(d, d)
        if d not in table:
            sys.exit(f"knowledge.py: unknown domain '{d}' (known: {', '.join(sorted(table))})")
        if table[d] not in picked:
            picked.append(table[d])
            dom_st, dom_fw = table[d].get("stacks"), table[d].get("frameworks")
            if stacks and dom_st and not set(stacks) & set(dom_st):
                why[d] = f"named — cross-platform: written for {', '.join(dom_st)}, target is {', '.join(stacks)} (reference only, not a requirement here)"
            elif dom_fw and framework and framework["id"] not in dom_fw:
                why[d] = f"named — cross-framework: written for {', '.join(dom_fw)}, project is {framework['id']} (reference only)"
            else:
                why[d] = "named"
    lowered, stemmed = (text or "").lower(), stems(text)
    context = []
    for d in routing["domains"]:
        if d in picked:
            continue
        if stacks and d.get("stacks") and not set(stacks) & set(d["stacks"]):
            continue
        fws = d.get("frameworks")
        if fws and framework and framework["id"] not in fws:
            continue
        # `unless`: phrases removed from the task before this domain's triggers are matched — "core
        # motion" stops "motion" matching the animation domain, "animate" still does. Code and
        # file-name signals below still apply.
        text_l, text_s = lowered, stemmed
        for phrase in d.get("unless", []):
            text_l = re.sub(r"\b" + re.escape(phrase) + r"\b", " ", text_l)
        if d.get("unless"):
            text_s = stems(text_l)
        if text_l.strip() and any(phrase_hit(t, text_l, text_s) for t in d.get("triggers", [])):
            picked.append(d)
            why[d["id"]] = "task words"
        elif code and any(re.search(rx, code) for rx in d.get("code", [])):
            picked.append(d)
            why[d["id"]] = "code in the change"
        else:
            hits = [g for g in d.get("globs", []) for f in files or []
                    if fnmatch.fnmatch(f, g) or fnmatch.fnmatch(Path(f).name, g)]
            if any(not BROAD_GLOB.match(g) for g in hits):     # *Animation*, components.json, error.tsx…
                picked.append(d)
                why[d["id"]] = "file name"
            elif hits:                                          # *.tsx, *.swift: any UI file — context only
                context.append(d)
    return picked, context, why


BROAD_GLOB = re.compile(r"^\*\.[A-Za-z0-9]+$")


def refs_for(domain, stack):
    refs = list((domain.get("ship_refs") or {}).get("all", []))
    if stack:
        refs += (domain.get("ship_refs") or {}).get(stack, [])
    return refs


def product_sources(routing, root, domains, stack):
    taste_domain = next((d["taste_domain"] for d in domains if d.get("taste_domain")), "<domain>")
    out = []
    for src in routing.get("product_sources", []):
        item = {"id": src["id"], "label": src["label"]}
        if src.get("path"):
            item["path"] = src["path"]
            item["present"] = (root / src["path"]).exists()
        if src.get("command") and item.get("present", True):
            item["command"] = (src["command"].replace("{stack}", stack or "<stack>")
                               .replace("{taste_domain}", taste_domain))
            script = resolve_ref(src["requires"]) if src.get("requires") else None
            if script is not None and not script.exists():
                item.pop("command")
        out.append(item)
    return out


def route(args):
    routing = load_routing()
    root = project_root(args.root)
    files, code = changed_code(root, args.files, args.changed)
    tgt = task_target(root, args.stack, files)
    stacks, how, unproven = tgt["stacks"], tgt["how"], tgt["unproven"]
    stack = stacks[0] if len(stacks) == 1 else None
    framework = tgt["native_js"] or (detect_framework(tgt["pkg"]) if (not stacks or "web" in stacks) else None)
    domains, context, why = match_domains(routing, args.domain, args.text, files, stacks, code, framework)
    fw_key = framework_key(framework)
    fw_note = (routing.get("framework_notes") or {}).get(fw_key) if framework else None
    result = {"stack": stack, "targets": stacks, "target_from": how, "framework": framework, "framework_note": fw_note,
              "domains": [d["id"] for d in domains], "why": why,
              "context": [d["id"] for d in context if d not in domains],
              "precedence": routing["precedence"], "product": product_sources(routing, root, domains, stack),
              "sources": []}
    for d in domains:
        cross = why.get(d["id"], "").startswith("named — cross")
        # a cross-platform domain shows its own platform's material, labelled as reference only
        view = list(d.get("stacks") or []) if cross and "cross-platform" in why[d["id"]] else stacks
        refs, ref_only = [], []
        for st in (view or [None]):
            for r in refs_for(d, st):
                bucket = ref_only if (st in unproven and not cross and r not in refs_for(d, None)) else refs
                if r not in refs + ref_only:
                    bucket.append(r)
        applies = "applies"
        if cross:
            applies = why[d["id"]]
        elif d.get("frameworks") and not framework and (not stacks or "web" in stacks):
            applies = (f"reference only — written for {', '.join(d['frameworks'])}; no framework found for this "
                       "task's package (confirm before applying)")
        elif not refs and ref_only:
            applies = "reference only — " + how.split(" — ", 1)[-1]
        if applies != "applies":
            refs, ref_only = [], refs + ref_only
        result["sources"].append({
            "domain": d["id"], "label": d["label"], "applicability": applies,
            "platform": [point_status(p) for p in d.get("points", [])
                         if not p.get("stacks") or not view or set(view) & set(p["stacks"])],
            "ship_refs": [{"path": display_ref(r), "exists": bool(resolve_ref(r) and resolve_ref(r).exists())}
                          for r in refs],
            "reference_only_refs": [display_ref(r) for r in ref_only],
            "skills": [dependency_status(dep, root) for dep in d.get("depends", [])
                       if not dep.get("stacks") or not view or set(view) & set(dep["stacks"])],
            "calls": d.get("calls", []),
            "note": ((d.get("framework_notes") or {}).get(fw_key) if framework else None) or d.get("note"),
        })
    if args.record:
        state = ensure_state_dir(root)
        rec = {"at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
               "text": args.text, "files": files, "targets": stacks, "framework": framework,
               "domains": result["domains"], "why": why, "context": result["context"],
               "target_from": how,
               "refs": [r["path"] for s_ in result["sources"] for r in s_["ship_refs"]],
               "reference_only": [r for s_ in result["sources"] for r in s_["reference_only_refs"]],
               "evidence": "selected — not proof that a reference was read or applied"}
        path = state / "route.json"
        prev = None
        if path.is_file():
            try:
                prev = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                prev = None
        if prev and same_task(prev, args.text):
            # /shipmate records the request's route; the stage then routes by meaning. Keep both.
            for key in ("domains", "context", "refs", "reference_only", "files"):
                rec[key] = list(prev.get(key) or []) + [x for x in rec[key] if x not in (prev.get(key) or [])]
            rec["why"] = {**(prev.get("why") or {}), **why}
            rec["text"] = args.text or prev.get("text")
            rec["selections"] = int(prev.get("selections") or 1) + 1
            if prev.get("notes"):
                rec["notes"] = prev["notes"]
        path.write_text(json.dumps(rec, indent=2) + "\n")
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    if framework:
        extra = "".join(f" · {k} {framework[k]}" for k in ("react", "bundler") if framework.get(k))
        if framework.get("id") == "react":
            extra += (" · server rendering: " + "; ".join(framework["ssr"])) if framework.get("ssr") \
                else " · no server-rendering entry found (createRoot only, as far as the project shows)"
        print(f"Framework: {framework['id']} {framework['version']}{extra}" + (f"\n  {fw_note}" if fw_note else ""))
    if not domains:
        print("No knowledge domain matched. If the task needs one, name it with --domain "
              f"({', '.join(d['id'] for d in routing['domains'])}); otherwise proceed without references.")
        if result["context"]:
            print("Context (file type only): " + ", ".join(result["context"]))
        return 0
    target = (f"target uncertain ({' or '.join(stacks) or 'unset'}) — {how[len('uncertain — '):]}"
              if how.startswith("uncertain — ") else f"target {', '.join(stacks) or 'unset'} (from {how})")
    print(f"Knowledge route — {target} · "
          + ", ".join(f"{s_['domain']} ({why[s_['domain']] if s_['applicability'] == 'applies' else 'reference only'})"
                      for s_ in result["sources"]))
    print("Precedence: " + " › ".join(p["label"] for p in routing["precedence"]))
    print("\nProduct (wins over everything below except platform requirements):")
    for p in result["product"]:
        where = p.get("path") or p.get("command")
        flag = "" if p.get("present", True) else "  (not present)"
        print(f"  - {p['label']}: {where}{flag}")
        if p.get("command") and p.get("path"):
            print(f"      {p['command']}")
    for s in result["sources"]:
        print(f"\n{s['label']}" + ("" if s["applicability"] == "applies" else f"  — {s['applicability']}"))
        for p in s["platform"]:
            loc = p.get("url") or p.get("path")
            flag = "" if p.get("present", True) else "  (not on this machine)"
            kind = p.get("kind", "platform")   # an expert link ranks below platform guidance
            print(f"  {kind:<9}· {p['label']}: {loc}{flag}")
        for r in s["ship_refs"]:
            print(f"  ship     · {r['path']}" + ("" if r["exists"] else "  (MISSING — report this)"))
        for r in s["reference_only_refs"]:
            print(f"  ship     · {r}  (reference only — not a rule for this target)")
        for k in s["skills"]:
            # Ship never asks to install a skill (plan §3d P1); one the builder installed on their own is
            # listed so its known mistakes get Ship's correction (P9).
            if k["installed"]:
                print(f"  skill    · {k['skill']} — installed ({k['where']}, {k['version']}); a checked Ship line outranks it")
            if k.get("correction"):
                print(f"      Ship correction: {k['correction']}")
        for c in s["calls"]:
            print(f"  tool     · {c['tool']}: {c['command']} — {c['when']} (if unavailable: {c['fallback']})")
        if s["note"]:
            print(f"  note     · {s['note']}")
    if result["context"]:
        labels = {d["id"]: d["label"] for d in routing["domains"]}
        print("\nContext (matched a file type only — open if the change affects it): "
              + "; ".join(f"{labels[c]} ({c})" for c in result["context"]))
    return 0


# ── Doctor + versions ────────────────────────────────────────────────────────

def all_dependencies(routing, stack):
    seen, deps = set(), []
    for d in routing["domains"]:
        if stack and d.get("stacks") and stack not in d["stacks"]:
            continue
        for dep in d.get("depends", []):
            if stack and dep.get("stacks") and stack not in dep["stacks"]:
                continue
            if dep["skill"] not in seen:
                seen.add(dep["skill"])
                deps.append(dep)
    return deps


def doctor(args):
    routing = load_routing()
    root = project_root(args.root)
    stack = read_stack(root, args.stack)
    skills = [dependency_status(dep, root) for dep in all_dependencies(routing, stack)]
    tools = [tool_status(t) for t in routing.get("tools", [])
             if not t.get("stacks") or not stack or stack in t["stacks"]]
    changed = []
    state_path = root / STATE_FILE
    if args.record:
        previous = {}
        if state_path.is_file():
            try:
                previous = json.loads(state_path.read_text(encoding="utf-8")).get("skills", {})
            except json.JSONDecodeError:
                previous = {}
        current = {s["skill"]: {"content": s["content"], "origin": s["origin"]} for s in skills if s["installed"]}
        changed = [c for c in (compare_identity(n, previous.get(n), cur) for n, cur in current.items()
                               if n in previous) if c]
        ensure_state_dir(root)
        state_path.write_text(json.dumps({"skills": current}, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps({"stack": stack, "skills": skills, "tools": tools, "changed": changed}, indent=2))
        return 0
    missing_tools = [t for t in tools if not t["installed"]]
    if args.brief:
        # Skills a builder hasn't installed are never mentioned: Ship's own references cover them.
        if missing_tools:
            print("Tools not found: " + ", ".join(t["tool"] for t in missing_tools) + " (optional).")
        for c in changed:
            print(f"Knowledge: {c['skill']} changed since last session ({c['reason']}). Reassess before"
                  " relying on it — new advice doesn't override this product's decisions; adopt it deliberately.")
        return 0
    print(f"Ship knowledge doctor — stack {stack or 'unset'}")
    for s in skills:
        if s["installed"]:
            print(f"  ✓ {s['skill']} ({s['where']}) · content {s['content']} ({s['files']} files) · "
                  f"{origin_label(s['origin'])}")
    for t in tools:
        print(f"  {'✓' if t['installed'] else '-'} {t['tool']}" +
              ("" if t["installed"] else f" not found — {t['purpose']}; install: {t['install']}"))
    for c in changed:
        print(f"  ! {c['skill']} changed since the last recorded session: {c['reason']} — reassess")
    print("Missing optional dependencies never block Ship; routes fall back as listed.")
    return 0


NOTE_FIELDS = ("stage", "read", "applied", "not_read", "verified", "taste", "conflict")


def note(args):
    """Record what the stage relied on next to its route, for review (never the founder's reply)."""
    root = project_root(args.root)
    entry = {k: getattr(args, k) for k in NOTE_FIELDS if getattr(args, k)}
    if not entry or set(entry) == {"stage"}:
        print("note: nothing to record (give --read, --applied, --not-read, --verified, --taste or --conflict)",
              file=sys.stderr)
        return 2
    path = ensure_state_dir(root) / "route.json"
    rec = {}
    if path.is_file():
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            rec = {}
    entry = {"at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
             **entry, "evidence": "self-reported"}
    rec.setdefault("notes", []).append(entry)
    path.write_text(json.dumps(rec, indent=2) + "\n")
    print("Recorded for review (.ship/state/route.json): " + ", ".join(k for k in NOTE_FIELDS if k in entry))
    return 0


def versions(args):
    routing = load_routing()
    root = project_root(args.root)
    stack = read_stack(root, None)
    refs = {}
    for d in routing["domains"]:
        for r in refs_for(d, None) + [x for k, v in (d.get("ship_refs") or {}).items() if k != "all" for x in v]:
            path = resolve_ref(r)
            if path and path.is_file() and r not in refs:
                head = path.read_text(encoding="utf-8", errors="replace")[:600]
                m = re.search(r"reviewed:\s*(\S+)", head)
                refs[r] = {"reviewed": m.group(1) if m else None,
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()[:12]}
    skills = {s["skill"]: {"content": s["content"], "files": s["files"], "origin": s["origin"]} for s in
              (dependency_status(dep, root) for dep in all_dependencies(routing, stack)) if s["installed"]}
    out = {"ship_version": routing.get("ship_version"), "routing_sha256":
           hashlib.sha256(ROUTING.read_bytes()).hexdigest()[:12], "references": refs, "skills": skills}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"Ship {out['ship_version']} · routing {out['routing_sha256']} · "
              f"{len(refs)} references · skills: " +
              (", ".join(f"{k} {v['content']} ({origin_label(v['origin'])})" for k, v in skills.items())
               or "none installed"))
    return 0


# ── Integrity check ──────────────────────────────────────────────────────────

def check(_args):
    routing = load_routing()
    errors = []
    ids = [d["id"] for d in routing["domains"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate domain ids")
    routed = set()
    for d in routing["domains"]:
        for key in ("id", "label", "triggers", "consumers"):
            if not d.get(key):
                errors.append(f"domain {d.get('id', '?')}: missing {key}")
        for refs in (d.get("ship_refs") or {}).values():
            for r in refs:
                path = resolve_ref(r)
                if not path or not path.is_file():
                    errors.append(f"domain {d['id']}: reference not found: {r}")
                    continue
                routed.add(path.resolve())
                if path.name != "SKILL.md" and not path.read_text(encoding="utf-8", errors="replace").lstrip().startswith(REF_HEADER):
                    errors.append(f"{r}: missing <!-- ship-reference --> header")
        for dep in d.get("depends", []):
            for key in ("skill", "detect"):
                if not dep.get(key):
                    errors.append(f"domain {d['id']}: dependency {dep.get('skill', '?')} missing {key}")
            if dep.get("install"):
                errors.append(f"domain {d['id']}: dependency {dep['skill']} has an install line; Ship suggests no installs")
        for rx in d.get("code", []):
            try:
                re.compile(rx)
            except re.error as exc:
                errors.append(f"domain {d['id']}: invalid code signal {rx!r} ({exc})")
    for ref in SKILLS_ROOT.glob("*/references/**/*.md"):
        if ref.resolve() not in routed:
            errors.append(f"unrouted reference (no domain lists it): {ref.relative_to(SKILLS_ROOT)}")
    for e in errors:
        print(f"✗ {e}")
    if errors:
        print(f"routing check failed ({len(errors)} problems)")
        return 1
    print(f"✓ routing valid — {len(ids)} domains, {len(routed)} references, all headed and routed")
    return 0


INSTRUCTION_FILES = ("CLAUDE.md", "AGENTS.md", ".cursorrules", ".github/copilot-instructions.md")
SHIP_MEMORY = ("TASKS.md", "DECISIONS.md", "CONTEXT.md", "LEARNINGS.md")
DESIGN_CONTRACT = ("PDC.md", "DESIGN.md", "design-model.yaml", "design/components.yaml", "design/taste.yaml")


def project(args):
    """What a Ship command needs before it starts: the stack, the project's own instructions (they
    come first), and Ship's state. Reads only — never creates CLAUDE.md or Ship's files."""
    root = project_root(args.root)
    declared = declared_stacks(root)
    env = os.environ.get("SHIP_STACK")
    found = detected_stacks(root)
    if env:
        stack, how = [env.lower()], "SHIP_STACK"
    elif declared:
        stack, how = declared, "declared — Stack: in CLAUDE.md"
    elif [s for s, _ in found if s != "macos"]:
        ok = [(s, ev) for s, ev in found if s != "macos"]
        stack, how = [s for s, _ in ok], "detected — " + ", ".join(ev for _, ev in ok)
    else:
        stack, how = [], ("not a Ship stack — macOS only (" + found[0][1] + ")") if found else "unknown — ask what you're building"
    claude_md = root / "CLAUDE.md"
    text = claude_md.read_text(encoding="utf-8", errors="replace") if claude_md.exists() else ""
    ship_section = bool(re.search(r"^## (Ship Framework|/team)\b", text, re.M))
    instructions = []
    for name in INSTRUCTION_FILES:
        f = root / name
        if f.is_file():
            body = f.read_text(encoding="utf-8", errors="replace")
            owner = "Ship's Codex bridge" if "managed by Ship" in body and name == "AGENTS.md" else "the project's"
            instructions.append({"file": name, "owner": owner})
    result = {
        "root": str(root), "stack": stack, "stack_from": how, "detected": found,
        "instructions": instructions, "ship_section_in_claude_md": ship_section,
        "team_rules_in_project": (root / ".claude/team-rules.md").is_file(),
        "memory": [m for m in SHIP_MEMORY if (root / m).is_file()],
        "design_contract": [m for m in DESIGN_CONTRACT if (root / m).exists()],
        "ship_state": (root / ".ship").is_dir(),
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(f"Project: {root}")
    print(f"Stack: {', '.join(stack) or '—'} ({how})")
    if instructions:
        print("Instructions (the project's own come first; Ship's rules fill gaps): "
              + ", ".join(f"{i['file']} ({i['owner']})" for i in instructions))
    else:
        print("Instructions: none in the project")
    if ship_section:
        print("Ship setup: CLAUDE.md has Ship's section — keep it current there.")
    else:
        print("Ship setup: not bootstrapped — every command works without it. Don't create CLAUDE.md, "
              ".claude/team-rules.md or other Ship files unless the founder asks "
              "(then: bin/bootstrap-project.sh for a plugin install, setup.sh otherwise).")
    print("Memory: " + (", ".join(result["memory"]) or "none") + " · Design contract: "
          + (", ".join(result["design_contract"]) or "none") + " · .ship/: " + ("yes" if result["ship_state"] else "no"))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("route")
    r.add_argument("--domain", action="append")
    r.add_argument("--text")
    r.add_argument("--files", nargs="*")
    r.add_argument("--changed", action="store_true", help="read changed files + added lines from git")
    r.add_argument("--record", action="store_true", help="save the selection to .ship/state/route.json")
    r.add_argument("--stack")
    r.add_argument("--root")
    r.add_argument("--json", action="store_true")
    d = sub.add_parser("doctor")
    d.add_argument("--stack")
    d.add_argument("--root")
    d.add_argument("--brief", action="store_true")
    d.add_argument("--record", action="store_true")
    d.add_argument("--json", action="store_true")
    v = sub.add_parser("versions")
    v.add_argument("--root")
    v.add_argument("--json", action="store_true")
    n = sub.add_parser("note", help="record what the stage read, applied and verified, for review")
    n.add_argument("--root")
    n.add_argument("--stage")
    n.add_argument("--read")
    n.add_argument("--applied")
    n.add_argument("--not-read", dest="not_read")
    n.add_argument("--verified")
    n.add_argument("--taste", help="taste ids followed")
    n.add_argument("--conflict", help="a precedence conflict and how it was resolved")
    sub.add_parser("check")
    pj = sub.add_parser("project", help="stack, the project's own instructions, Ship state (reads only)")
    pj.add_argument("--root")
    pj.add_argument("--json", action="store_true")
    args = ap.parse_args()
    return {"route": route, "doctor": doctor, "versions": versions, "check": check, "project": project,
            "note": note}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())

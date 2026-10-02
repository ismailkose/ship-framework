#!/usr/bin/env python3
"""Ship Framework install/update engine (setup.sh route). Stdlib only, Python 3.8+.

    ship-install.py apply  --source REPO --target DIR [--dry-run]
    ship-install.py record-hashes --source REPO            (maintainers)

`apply` is the one code path for fresh installs, adoption into existing projects, and
updates. setup.sh and ship-update.sh both call it; it never overwrites a user-owned file.

Ownership (the contract — CAPABILITIES.md explains it for users):

  Framework-owned (Ship replaces these; an edited copy is backed up first):
    .claude/team-rules.md
    .claude/skills/ship/**
    .claude/skills/shipmate/**   the /shipmate entry and its stages (the pre-/shipmate
                                 .claude/commands/ship-*.md and .claude/skills/ship-*/SKILL.md
                                 mirrors stay in the namespace so updates can retire them)
    .claude/agents/<files Ship ships>
    .claude/skills/README.md, CHEATSHEET.md, ship-update.sh
    AGENTS.md                    only while it says "Managed by Ship Framework"
    .ship/framework.yaml         only while it says "managed_by": "Ship Framework"
    .ship/manifest.json, .ship/AGENTS.ship.md
    CLAUDE.md                    only the <!-- BEGIN/END:ship-generated|ship-managed:* --> blocks
                                 and the "> Ship Framework v…" footer line
  User-owned (created when missing, never overwritten or removed):
    everything else — CLAUDE.md, TASKS/DECISIONS/CONTEXT/LEARNINGS/DESIGN/PDC.md,
    design-model.yaml, design/**, taste stores, references/**, .claude/skills/your-skills/**,
    other .claude/agents and commands, settings (Ship only adds its hooks), generated code.

Knowing "edited": .ship/manifest.json records the git-blob hash of every framework file Ship
wrote. Projects from before manifests (≤ 2026.09.22) are matched against
template/.ship/release-hashes.txt — every framework file of every past release.

Retiring: template/.ship/retired.txt (one project path per line; `dir/` or globs allowed).
Files Ship installed last time (manifest) and no longer ships are retired the same way.
Unedited → deleted. Edited → moved to .ship/backups/<stamp>/. Outside Ship's namespace a
file is only ever deleted when it is byte-identical to something Ship shipped.
"""

import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MANIFEST = ".ship/manifest.json"
BACKUPS = ".ship/backups"
AGENTS_SIDECAR = ".ship/AGENTS.ship.md"
SECTION_HASHES = ".ship/claude-section-hashes.txt"
INSTALLER_METADATA = {".ship/retired.txt", ".ship/release-hashes.txt", SECTION_HASHES}
GUIDE = "ship-managed:claude-ship-guide"   # Ship's own wording in CLAUDE.md's Ship section
SKIP_NAMES = {".DS_Store", "__pycache__", ".git"}
MEMORY_FILES = ["TASKS.md", "DECISIONS.md", "CONTEXT.md", "LEARNINGS.md"]
CLAUDE_SHIP_MARKERS = ("## Ship Framework", "<!-- Ship Framework team definitions below -->", "## /team")
BLOCK_RE = re.compile(
    r"<!-- BEGIN:(ship-(?:generated|managed):[A-Za-z0-9_.-]+) -->.*?<!-- END:\1 -->", re.DOTALL)
FOOTER_RE = re.compile(r"^>.*Ship Framework v[^\n]*$", re.MULTILINE)
REPO_URL = "https://github.com/ismailkose/ship-framework"

HOOK_SCRIPTS = {
    "sessionstart": ".claude/skills/ship/sessionstart/bin/session-start.sh",
    "refgate": ".claude/skills/ship/refgate/bin/check-refgate.sh",
    "aftershell": ".claude/skills/ship/refgate/bin/check-after-shell.sh",
}


def hook_cmd(key):
    return 'bash "$CLAUDE_PROJECT_DIR/%s"' % HOOK_SCRIPTS[key]


WANTED_HOOKS = [  # (event, matcher, key, extra)
    ("SessionStart", None, "sessionstart", {"timeout": 10}),
    ("PreToolUse", "Edit", "refgate", {}),
    ("PreToolUse", "Write", "refgate", {}),
    ("PostToolUse", "Bash", "aftershell", {"timeout": 15}),
]


# ── helpers ──────────────────────────────────────────────────────────────────

def blob_hash(data):
    """git's blob id — lets release-hashes.txt come straight from `git ls-tree`."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def in_namespace(rel):
    """Paths only Ship would create. Everything else is presumed the user's."""
    return (rel.startswith(".claude/skills/ship/")
            or rel.startswith(".claude/skills/shipmate/")
            or rel == ".claude/team-rules.md"
            or rel in (MANIFEST, AGENTS_SIDECAR, ".ship/framework.yaml")
            or re.match(r"^\.claude/commands/ship-[^/]+\.md$", rel) is not None
            or re.match(r"^\.claude/skills/ship-[^/]+/SKILL\.md$", rel) is not None
            or re.match(r"^\.claude/agents/ship-[^/]+\.md$", rel) is not None)


def walk(base):
    """Relative file paths under base, skipping OS/cache junk. Sorted for stable output."""
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_NAMES)
        for f in sorted(filenames):
            if f in SKIP_NAMES or f.endswith(".pyc"):
                continue
            out.append(os.path.relpath(os.path.join(dirpath, f), base).replace(os.sep, "/"))
    return out


def normalize_for_hash(rel, data):
    """Rendered files compare against their template form (version placeholder restored)."""
    if rel in ("AGENTS.md", AGENTS_SIDECAR):
        text = data.decode("utf-8", errors="replace")
        text = re.sub(r"Ship Framework v[0-9A-Za-z.\-]+ —", "Ship Framework v__VERSION__ —", text)
        return text.encode("utf-8")
    return data


class Plan:
    def __init__(self, target, dry_run):
        self.target = target
        self.dry = dry_run
        self.stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.created, self.updated, self.unchanged = [], [], []
        self.backed_up, self.removed, self.kept_user, self.notes = [], [], [], []
        self.manifest_files = {}

    def path(self, rel):
        return self.target / rel

    def backup(self, rel):
        dst = self.target / BACKUPS / self.stamp / rel
        self.backed_up.append(rel)
        if not self.dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(self.path(rel)), str(dst))
        return dst

    def write(self, rel, data, executable=False):
        p = self.path(rel)
        if self.dry:
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".ship-tmp")
        tmp.write_bytes(data)
        if p.exists():
            shutil.copymode(str(p), str(tmp))
        if executable:
            os.chmod(str(tmp), 0o755)
        os.replace(str(tmp), str(p))

    def delete(self, rel):
        self.removed.append(rel)
        if self.dry:
            return
        p = self.path(rel)
        p.unlink()
        parent = p.parent
        while parent != self.target and in_namespace_dir(parent, self.target):
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent


def in_namespace_dir(d, target):
    rel = os.path.relpath(str(d), str(target)).replace(os.sep, "/")
    return rel.startswith(".claude/skills/ship") or rel.startswith(".claude/skills/ship-") \
        or rel in (".claude/commands", ".claude/agents")


# ── source ───────────────────────────────────────────────────────────────────

class Source:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.template = self.root / "template"
        if not (self.template / ".claude" / "skills" / "ship").is_dir():
            raise SystemExit("ship-install: %s doesn't look like a Ship Framework checkout" % self.root)
        v = self.root / "VERSION"
        self.version = v.read_text().strip() if v.is_file() else "unknown"

    def render(self, data):
        return data.replace(b"__VERSION__", self.version.encode())

    def framework_files(self):
        """dest rel → (bytes, executable). The complete set Ship owns in a project."""
        t = self.template
        files = {}

        def add(rel, src, render=False):
            data = src.read_bytes()
            exe = os.access(str(src), os.X_OK) or rel == "ship-update.sh" or "/bin/" in rel
            files[rel] = (self.render(data) if render else data, exe)

        add(".claude/team-rules.md", t / ".claude/team-rules.md")
        for rel in walk(t / ".claude/skills/ship"):
            add(".claude/skills/ship/" + rel, t / ".claude/skills/ship" / rel)
        for rel in walk(t / ".claude/skills/shipmate"):    # /shipmate: one skill, its stages beside it
            add(".claude/skills/shipmate/" + rel, t / ".claude/skills/shipmate" / rel)
        agents = t / ".claude/agents"
        if agents.is_dir():
            for rel in walk(agents):
                add(".claude/agents/" + rel, agents / rel)
        if (t / ".claude/skills/README.md").is_file():
            add(".claude/skills/README.md", t / ".claude/skills/README.md")
        if (self.root / "CHEATSHEET.md").is_file():
            add("CHEATSHEET.md", self.root / "CHEATSHEET.md")
        if (t / "ship-update.sh").is_file():
            add("ship-update.sh", t / "ship-update.sh")
        for rel in walk(t / ".ship") if (t / ".ship").is_dir() else []:
            full = ".ship/" + rel
            if full not in INSTALLER_METADATA:
                add(full, t / ".ship" / rel)
        return files

    def seed_files(self, framework):
        """Template files the user owns once created (memory files, READMEs, future seeds)."""
        seeds = {}
        for rel in walk(self.template):
            if rel in framework or rel in ("CLAUDE.md", "AGENTS.md") or rel in INSTALLER_METADATA:
                continue
            if rel.startswith(".claude/commands/") or rel.startswith(".claude/skills/ship/") \
                    or rel.startswith(".claude/skills/shipmate/") or rel.startswith(".claude/agents/"):
                continue
            seeds[rel] = self.render((self.template / rel).read_bytes())
        return seeds

    def retired(self):
        p = self.template / ".ship/retired.txt"
        if not p.is_file():
            return []
        out = []
        for line in p.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line.lstrip("./") if line.startswith("./") else line)
        return out

    def section_hashes(self):
        """Hashes of the Ship section's own wording (normalised) in every past CLAUDE.md template."""
        p = self.template / SECTION_HASHES
        return {l.split()[0] for l in p.read_text().splitlines() if l.strip() and not l.startswith("#")} \
            if p.is_file() else set()

    def known_hashes(self):
        p = self.template / ".ship/release-hashes.txt"
        known = {}
        if p.is_file():
            for line in p.read_text().splitlines():
                if line and not line.startswith("#"):
                    h, _, rel = line.partition(" ")
                    known.setdefault(rel, set()).add(h)
        return known


# ── apply ────────────────────────────────────────────────────────────────────

def load_manifest(target):
    p = target / MANIFEST
    if p.is_file():
        try:
            data = json.loads(p.read_text())
            return data.get("files", {}), data.get("version")
        except (ValueError, OSError):
            pass
    return {}, None


def is_ship_project(target):
    if (target / MANIFEST).is_file() or (target / ".claude/skills/ship").is_dir():
        return True
    c = target / "CLAUDE.md"
    return c.is_file() and any(m in c.read_text(errors="replace") for m in CLAUDE_SHIP_MARKERS)


def pristine(rel, data, manifest, known):
    h = blob_hash(normalize_for_hash(rel, data))
    return h == manifest.get(rel) or h in known.get(rel, ())


def sync_framework(plan, src, framework, manifest, known):
    for rel, (data, exe) in sorted(framework.items()):
        p = plan.path(rel)
        if rel == "AGENTS.md" or rel == ".ship/framework.yaml":
            continue  # handled with their managed-marker rules
        if not p.exists():
            plan.write(rel, data, exe)
            plan.created.append(rel)
            plan.manifest_files[rel] = blob_hash(normalize_for_hash(rel, data))
            continue
        if p.is_dir():
            plan.notes.append("%s is a directory in your project; Ship skipped the file it ships there" % rel)
            continue
        current = p.read_bytes()
        if current == data:
            plan.unchanged.append(rel)
            if exe and not os.access(str(p), os.X_OK) and not plan.dry:
                os.chmod(str(p), 0o755)
            plan.manifest_files[rel] = blob_hash(normalize_for_hash(rel, data))
            continue
        if pristine(rel, current, manifest, known):
            plan.write(rel, data, exe)
            plan.updated.append(rel)
        elif in_namespace(rel) or rel in manifest:
            plan.backup(rel)
            plan.write(rel, data, exe)
            plan.updated.append(rel)
        else:
            # A file with the same name that Ship never installed (adoption): it's the user's.
            plan.kept_user.append(rel)
            continue
        plan.manifest_files[rel] = blob_hash(normalize_for_hash(rel, data))


def sync_managed_file(plan, rel, data, marker, manifest, known, label):
    p = plan.path(rel)
    if not p.exists():
        plan.write(rel, data)
        plan.created.append(rel)
    else:
        current = p.read_bytes()
        if marker not in current:
            plan.kept_user.append(rel)
            return False
        if current == data:
            plan.unchanged.append(rel)
        else:
            if not pristine(rel, current, manifest, known):
                plan.backup(rel)
            plan.write(rel, data)
            plan.updated.append(rel)
    plan.manifest_files[rel] = blob_hash(normalize_for_hash(rel, data))
    return True


FOREIGN_BLOCK = re.compile(rb"<!-- BEGIN:(?!ship-)([\w.-]+) -->.*?<!-- END:\1 -->", re.S)


def keep_foreign_blocks(current, data):
    """Other tools manage their own blocks inside AGENTS.md (e.g. Next.js 16.3 writes
    <!-- BEGIN:nextjs-agent-rules -->). An update replaces Ship's text, never theirs."""
    for m in FOREIGN_BLOCK.finditer(current):
        if m.group(0) not in data:
            data = data.rstrip(b"\n") + b"\n\n" + m.group(0) + b"\n"
    return data


def sync_agents_bridge(plan, src, manifest, known):
    tpl = src.template / "AGENTS.md"
    if not tpl.is_file():
        return
    data = src.render(tpl.read_bytes())
    current = plan.path("AGENTS.md")
    if current.is_file():
        data = keep_foreign_blocks(current.read_bytes(), data)
    if sync_managed_file(plan, "AGENTS.md", data, b"Managed by Ship Framework", manifest, known, "AGENTS.md"):
        # A sidecar from an earlier adoption is obsolete once AGENTS.md is Ship's.
        side = plan.path(AGENTS_SIDECAR)
        if side.is_file():
            plan.delete(AGENTS_SIDECAR)
        return
    # The user's own AGENTS.md: never edited. Ship's bridge goes next to it; one line links it.
    plan.kept_user.remove("AGENTS.md")
    sync_managed_file(plan, AGENTS_SIDECAR, data, b"Managed by Ship Framework", manifest, known, AGENTS_SIDECAR)
    linked = AGENTS_SIDECAR.encode() in plan.path("AGENTS.md").read_bytes()
    if not linked:
        plan.notes.append(
            "Your AGENTS.md is yours, so Ship didn't edit it. For Codex to use Ship, add this line to it:\n"
            "      Ship Framework: read .ship/AGENTS.ship.md and follow it.")


def sync_core_manifest(plan, src, manifest, known):
    tpl = src.template / ".ship/framework.yaml"
    if tpl.is_file():
        rel = ".ship/framework.yaml"
        sync_managed_file(plan, rel, tpl.read_bytes(), b'"managed_by": "Ship Framework"',
                          manifest, known, rel)


def block_re(name):
    n = re.escape(name)
    return re.compile(r"<!-- BEGIN:%s -->.*?<!-- END:%s -->" % (n, n), re.DOTALL)


def refresh_blocks(template_text, project_text):
    """Replace each Ship block the project has with the template's. Blocks can nest (the Ship guide
    holds the generated tables): outer blocks come first, so a refreshed outer block carries its
    inner ones, and a project without the outer block still gets its inner ones refreshed."""
    names = list(dict.fromkeys(re.findall(r"<!-- BEGIN:(ship-(?:generated|managed):[A-Za-z0-9_.-]+) -->",
                                          template_text)))
    changed, text = [], project_text
    for name in names:
        new = block_re(name).search(template_text).group(0)
        m = block_re(name).search(text)
        if m and m.group(0) != new:
            text = text[:m.start()] + new + text[m.end():]
            changed.append(name)
    return text, changed


def guide_region(text):
    """Where the Ship section's own wording sits in an older CLAUDE.md: after `## Ship Framework`,
    up to the **Skills:** line (what follows holds the founder's wiring and references)."""
    m = re.search(r"^## Ship Framework[ \t]*\n", text, re.M)
    if not m:
        return None
    end = text.find("\n**Skills:**", m.end())
    return (m.end(), end + 1) if end != -1 else None


def guide_hash(region_text):
    """The wording, not what Ship regenerates inside it or the version it names."""
    t = re.sub(r"(<!-- BEGIN:(ship-generated:[A-Za-z0-9_.-]+) -->).*?(<!-- END:\2 -->)", r"\1\3",
               region_text, flags=re.DOTALL)
    t = re.sub(r"v(__VERSION__|\d{4}\.\d{2}\.\d{2})", "v<version>", t)
    t = "\n".join(l.rstrip() for l in t.strip().splitlines())
    return hashlib.sha1(t.encode("utf-8")).hexdigest()


def migrate_guide(template_text, project_text, known):
    """An older Ship section gets the current wording only when it's exactly what an older Ship wrote.
    Returns (text, "replaced" | "edited" | "none")."""
    tpl = block_re(GUIDE).search(template_text)
    region = guide_region(project_text)
    if not tpl or block_re(GUIDE).search(project_text):
        return project_text, "none"
    if not region:
        return project_text, "edited"
    s, e = region
    body = project_text[s:e]
    if guide_hash(body) not in known:
        return project_text, "edited"
    lead = "\n" if body.startswith("\n") else ""
    return project_text[:s] + lead + tpl.group(0) + "\n\n" + project_text[e:], "replaced"


def without_placeholders(template_text):
    """The template for a CLAUDE.md that already exists: no title placeholder and no empty headings.
    The founder's file already says what the product is; empty fill-ins would only add noise."""
    keep = []
    for part in re.split(r"(?m)^(?=#{1,2} )", template_text):
        head, _, body = part.partition("\n")
        if head.startswith("# ["):
            continue
        filled = re.sub(r"(?m)^\s*-{3,}\s*$", "", re.sub(r"<!--.*?-->", "", body, flags=re.S))
        if head.startswith("#") and not filled.strip():
            continue
        keep.append(part)
    return "".join(keep)


def sync_claude_md(plan, src):
    rel = "CLAUDE.md"
    p = plan.path(rel)
    template_text = src.render((src.template / "CLAUDE.md").read_bytes()).decode("utf-8")
    footer = "> Ship Framework v%s — [github.com/ismailkose/ship-framework](%s)" % (src.version, REPO_URL)
    if not p.exists():
        plan.write(rel, template_text.encode("utf-8"))
        plan.created.append(rel)
        return
    text = p.read_text(encoding="utf-8", errors="replace")
    if not any(m in text for m in CLAUDE_SHIP_MARKERS):
        plan.backup(rel)
        merged = (text.rstrip() + "\n\n---\n\n<!-- Ship Framework team definitions below -->\n\n"
                  + without_placeholders(template_text))
        plan.write(rel, merged.encode("utf-8"))
        plan.updated.append(rel + " (Ship section appended; your content above it is unchanged)")
        return
    new, blocks = refresh_blocks(template_text, text)
    new, guide = migrate_guide(template_text, new, src.section_hashes())
    if guide == "replaced":
        blocks.append(GUIDE + " — the Ship section's wording, from an older Ship")
    elif guide == "edited":
        plan.notes.append("CLAUDE.md: Ship didn't recognise your Ship section's wording (you edited it, or "
                          "it's from an early version), so it left it as it was. The current wording (one "
                          "command, /shipmate) is in Ship's CLAUDE.md template; copy what you want.")
    if FOOTER_RE.search(new):
        new = FOOTER_RE.sub(lambda m: footer, new, count=1)
    else:
        new = new.rstrip() + "\n\n---\n\n" + footer + "\n"
    if new != text:
        if blocks:
            plan.backup(rel)
            plan.updated.append(rel + " (Ship-managed blocks: %s)" % ", ".join(blocks))
        else:
            plan.updated.append(rel + " (version line)")
        plan.write(rel, new.encode("utf-8"))


def sync_seeds(plan, seeds):
    for rel, data in sorted(seeds.items()):
        if not plan.path(rel).exists():
            plan.write(rel, data)
            plan.created.append(rel)


def retire(plan, src, framework, manifest, known):
    """Remove what Ship no longer ships: the explicit list, the last manifest, stale Ship copies."""
    patterns = src.retired()
    existing = set()
    for base in (".claude", ".ship", "references"):
        if plan.path(base).is_dir():
            existing.update(base + "/" + r for r in walk(plan.path(base)))
    for rel in ("CHEATSHEET.md", "ship-update.sh"):
        if plan.path(rel).is_file():
            existing.add(rel)

    def listed(rel):
        for pat in patterns:
            if pat.endswith("/") and rel.startswith(pat):
                return True
            if rel == pat or fnmatch.fnmatchcase(rel, pat):
                return True
        return False

    for bad in patterns:
        head = bad.split("*")[0]
        if not (in_namespace(head) or head.startswith(".claude/skills/ship") or head in known
                or any(k.startswith(head) for k in known)):
            plan.notes.append("retired.txt entry ignored (not a Ship path): %s" % bad)

    shipped_but_listed = sorted({pat for pat in patterns for rel in framework
                                 if (pat.endswith("/") and rel.startswith(pat)) or rel == pat
                                 or fnmatch.fnmatchcase(rel, pat)})
    for pat in shipped_but_listed:
        plan.notes.append("retired.txt lists %s but Ship still ships it — kept. "
                          "(Maintainers: remove it from template/ or from retired.txt.)" % pat)

    for rel in sorted(existing):
        # the Codex bridge sidecar is written (and removed) by sync_agents_bridge on every run
        if rel in framework or rel in (MANIFEST, AGENTS_SIDECAR) or rel.startswith(BACKUPS + "/"):
            continue
        data = plan.path(rel).read_bytes()
        clean = pristine(rel, data, manifest, known)
        was_ours = rel in manifest
        if listed(rel):
            if in_namespace(rel) or was_ours:
                if not clean:
                    plan.backup(rel)
                plan.delete(rel)
            elif clean:
                plan.delete(rel)
            else:
                plan.notes.append("kept %s: listed as retired but it isn't an unedited Ship file" % rel)
        elif (was_ours or in_namespace(rel)) and (rel in manifest or rel in known):
            if clean:
                plan.delete(rel)
            elif was_ours:
                plan.backup(rel)
                plan.delete(rel)
            elif in_namespace(rel):
                plan.notes.append("kept %s: Ship no longer ships it, but you edited it" % rel)


def merge_hooks(plan):
    rel = ".claude/settings.json"
    p = plan.path(rel)
    if p.exists():
        try:
            data = json.loads(p.read_text())
        except ValueError:
            plan.notes.append(".claude/settings.json isn't valid JSON — Ship's hooks weren't added. "
                              "Add them by hand (see CAPABILITIES.md › Hooks).")
            return
    else:
        data = {}
    existed = p.exists()
    hooks = data.setdefault("hooks", {})
    changed = 0
    for event, matcher, key, extra in WANTED_HOOKS:
        script = HOOK_SCRIPTS[key]
        want = dict({"type": "command", "command": hook_cmd(key)}, **extra)
        entries = hooks.setdefault(event, [])
        found = False
        for e in entries:
            if e.get("matcher") != matcher:
                continue
            for h in e.get("hooks", []):
                if script in h.get("command", ""):
                    found = True
                    # Upgrade older Ship forms in place: relative path, 5000 "ms" timeout.
                    if h != want and h.get("command", "").startswith("bash ") and \
                            h.get("command") in ("bash " + script, want["command"]):
                        h.clear()
                        h.update(want)
                        changed += 1
        if not found:
            entries.append({"matcher": matcher, "hooks": [want]} if matcher else {"hooks": [want]})
            changed += 1
    if changed:
        if not plan.dry:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data, indent=2) + "\n")
        (plan.updated if existed else plan.created).append(
            rel + " (Ship hooks: design gate, session start)")


def write_manifest(plan, src):
    if plan.dry:
        return
    p = plan.path(MANIFEST)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = {"managed_by": "Ship Framework", "schema_version": 1, "version": src.version,
            "note": "Hashes of the framework files Ship installed. Ship uses them to tell your edits "
                    "from its own files on update. Don't edit.",
            "files": dict(sorted(plan.manifest_files.items()))}
    p.write_text(json.dumps(body, indent=2) + "\n")


def run_doctor(target):
    kp = target / ".claude/skills/ship/knowledge/bin/knowledge.py"
    if not kp.is_file():
        return None
    try:
        r = subprocess.run([sys.executable, str(kp), "doctor", "--root", str(target), "--brief"],
                           cwd=str(target), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return "  Knowledge check didn't run (%s). Ship works without it." % exc.__class__.__name__
    if r.returncode != 0:
        tail = ((r.stderr or r.stdout).strip().splitlines()[-1:] or ["no output"])[0]
        tail = tail.replace(str(target) + "/", "")[:240]
        return "  Knowledge check didn't finish (%s). Ship works without it." % tail
    out = r.stdout.strip()
    return "\n".join("  " + l for l in out.splitlines())   # empty: nothing needs attention


def optional_tools(target):
    """Fallback when knowledge.py isn't installed: what's reduced, and how to add it."""
    lines = []
    ios = any(target.glob("*.xcodeproj")) or (target / "project.yml").is_file()
    checks = [
        ("npx", "visual QA screenshots (Playwright) and the web scan",
         "install Node.js — https://nodejs.org"),
        ("codex", "/shipmate codex second opinion", "npm install -g @openai/codex"),
    ]
    if ios:
        checks.append(("xcodegen", "regenerating the Xcode project from project.yml", "brew install xcodegen"))
    for tool, what, how in checks:
        if shutil.which(tool) is None:
            lines.append("  - %s not found: %s unavailable. Add it: %s" % (tool, what, how))
    return "\n".join(lines)


def report(plan, src, fresh, prior_version):
    pre = "Would " if plan.dry else ""
    print("")
    if plan.dry:
        print("Dry run — nothing was written.")
    print("%s%s: %d new, %d updated, %d unchanged" % (
        pre, "install" if (fresh and plan.dry) else ("update" if plan.dry else ("Install" if fresh else "Update")),
        len(plan.created), len(plan.updated), len(plan.unchanged)))
    visible = lambda x: not x.startswith(".claude/") or x.startswith(".claude/settings")
    for label, items in (("created", [c for c in plan.created if visible(c)]),
                         ("updated", [u for u in plan.updated if visible(u)])):
        for it in items:
            print("  %s %s" % (label, it))
    if plan.backed_up:
        where = "%s/%s/" % (BACKUPS, plan.stamp)
        print("%s %d file(s) before changing them → %s" % (
            "Would save a copy of" if plan.dry else "Saved a copy of", len(plan.backed_up), where))
        for b in plan.backed_up:
            print("  " + b)
    if plan.removed:
        print("%s %d file(s) Ship no longer ships:" % ("Would remove" if plan.dry else "Removed", len(plan.removed)))
        for r in plan.removed[:40]:
            print("  " + r)
        if len(plan.removed) > 40:
            print("  … and %d more" % (len(plan.removed) - 40))
    if plan.kept_user:
        print("Left your own files alone (same name as a Ship file, but not Ship's):")
        for k in plan.kept_user:
            print("  " + k)
    for n in plan.notes:
        print("Note: " + n)


def apply(args):
    src = Source(args.source)
    target = Path(args.target).resolve()
    if not target.is_dir():
        raise SystemExit("ship-install: directory not found: %s" % target)
    fresh = not is_ship_project(target)
    manifest, prior_version = load_manifest(target)
    known = src.known_hashes()
    plan = Plan(target, args.dry_run)

    framework = src.framework_files()
    sync_framework(plan, src, framework, manifest, known)
    sync_agents_bridge(plan, src, manifest, known)
    sync_core_manifest(plan, src, manifest, known)
    sync_claude_md(plan, src)
    sync_seeds(plan, src.seed_files(framework))
    retire(plan, src, framework, manifest, known)
    merge_hooks(plan)
    write_manifest(plan, src)
    report(plan, src, fresh, prior_version)

    if not args.dry_run and not args.no_doctor:
        doc = run_doctor(target)
        tools = optional_tools(target) if doc is None else ""
        if doc or tools:
            print("Optional capabilities (never required):")
            if doc:
                print(doc)
            if tools:
                print(tools)
    return 0


# ── maintainers: release hashes ──────────────────────────────────────────────

def project_paths(template_rel):
    """Where a template file lands in a project (setup.sh layout, all releases)."""
    out = [template_rel]
    m = re.match(r"^\.claude/commands/(ship-[^/]+)\.md$", template_rel)
    if m:
        out.append(".claude/skills/%s/SKILL.md" % m.group(1))
    return out


def record_section_hashes(root):
    git = ["git", "-C", str(root)]
    rows = {}
    for c in subprocess.check_output(git + ["log", "--format=%H %ad", "--date=short", "--", "template/CLAUDE.md"],
                                     text=True).splitlines():
        sha, date = c.split()
        try:
            text = subprocess.check_output(git + ["show", "%s:template/CLAUDE.md" % sha], text=True)
        except subprocess.CalledProcessError:
            continue
        region = guide_region(text)
        if region and GUIDE not in text:
            rows.setdefault(guide_hash(text[region[0]:region[1]]), "%s %s" % (sha[:7], date))
    out = root / "template" / SECTION_HASHES
    out.write_text("# The Ship section's own wording (normalised: see guide_hash) in every past CLAUDE.md\n"
                   "# template. An update replaces a project's section only when it matches one of these.\n"
                   "# Regenerate (maintainers only): python3 scripts/ship-install.py record-hashes --source .\n"
                   + "".join("%s %s\n" % (h, where) for h, where in sorted(rows.items(), key=lambda r: r[1].split()[1])))
    print("wrote %s (%d past wordings)" % (out.relative_to(root), len(rows)))


def record_hashes(args):
    root = Path(args.source).resolve()
    git = ["git", "-C", str(root)]
    commits = subprocess.check_output(git + ["log", "--format=%H", "--", "VERSION"], text=True).split()
    tags = subprocess.check_output(git + ["tag", "--list", "v*"], text=True).split()
    commits += [subprocess.check_output(git + ["rev-list", "-n1", t], text=True).strip() for t in tags]
    pairs = set()
    for c in dict.fromkeys(commits):
        listing = subprocess.check_output(git + ["ls-tree", "-r", c, "--", "template", "CHEATSHEET.md"], text=True)
        for line in listing.splitlines():
            meta, path = line.split("\t", 1)
            blob = meta.split()[2]
            rel = path[len("template/"):] if path.startswith("template/") else path
            if rel in ("CLAUDE.md",) + tuple(MEMORY_FILES) or rel.endswith(".DS_Store"):
                continue  # user-owned from the moment they're created
            for dest in project_paths(rel):
                pairs.add((blob, dest))
    record_section_hashes(root)
    out = root / "template/.ship/release-hashes.txt"
    header = ("# Ship files as shipped in every past release (git blob id, project path).\n"
              "# The installer treats a matching file as unedited. Static: projects installed from\n"
              "# 2026.09.23 on carry .ship/manifest.json instead. Regenerate (maintainers only):\n"
              "#   python3 scripts/ship-install.py record-hashes --source .\n")
    out.write_text(header + "".join("%s %s\n" % p for p in sorted(pairs, key=lambda x: (x[1], x[0]))))
    print("wrote %s (%d entries from %d release commits)" % (out.relative_to(root), len(pairs), len(set(commits))))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Ship Framework install/update engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply")
    a.add_argument("--source", required=True)
    a.add_argument("--target", required=True)
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--no-doctor", action="store_true")
    r = sub.add_parser("record-hashes")
    r.add_argument("--source", required=True)
    args = ap.parse_args()
    return apply(args) if args.cmd == "apply" else record_hashes(args)


if __name__ == "__main__":
    sys.exit(main())

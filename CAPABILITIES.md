# Ship Framework: install routes and what each runtime can do

Ship ships the same files to Claude Code and Codex, but **the same files don't mean the same
execution**. This page says plainly what works where, how each claim was checked, and what
you lose when an optional tool is missing.

**Status key.** **Verified**: exercised on 2026-09-23 with Claude Code 2.1.144 and Codex CLI
0.155.0-alpha (isolated config dirs, Ship's install checks). **Tested locally**: Ship's own
checks cover it; not yet seen in a live session. **Replayed**: a fresh agent followed Ship's files
on a sample app, outside a live Claude Code session. **Documented**: vendor docs say so; not
exercised here. **Not supported**: Ship doesn't do this in that runtime.

---

## Pick an install route

| Route | For | Install | Update |
|---|---|---|---|
| **Plugin via marketplace** (recommended for Claude Code) | Claude Code | `/plugin marketplace add ismailkose/ship-framework` → `/plugin install ship-framework@ship-framework` | `claude plugin marketplace update ship-framework` then `claude plugin update ship-framework@ship-framework`, or enable auto-update in `/plugin` › Marketplaces (off by default for third-party marketplaces) |
| **`.plugin` file** | Cowork / Claude desktop; one-off CLI sessions | Open `ship-framework.plugin` from the [latest release](https://github.com/ismailkose/ship-framework/releases). CLI: `claude --plugin-dir ship-framework.plugin` loads it **for that session only** | Install the newer file |
| **Project install** (`setup.sh`) | Codex, or anyone who wants Ship's files inside the repo | `git clone https://github.com/ismailkose/ship-framework.git && bash ship-framework/setup.sh [project]` | `/shipmate update` in Claude Code, or `bash ship-update.sh` |

Pick **one** route per project. With both, Claude Code loads Ship's skills twice and runs the
design gate and session start twice (plugin hooks and project hooks don't de-duplicate). If you
use Codex on the project, use the project install.

`setup.sh` handles three cases with one command: an empty folder (fresh install), an existing
project (adoption: Ship adds its files and never overwrites yours), and an existing Ship
project (update). `--dry-run` shows what would change without writing.

---

## What each runtime can do

| Capability | Claude plugin | Claude project install | Codex project install |
|---|---|---|---|
| Ship context on session start (one line, plus notes when something needs attention) | Hook + `CLAUDE.md` · **Verified live** (both SessionStart hooks ran in installed-plugin sessions, 2026-09-23, with the earlier, longer banner; the one-line version is **tested locally**) | Hook + `CLAUDE.md` · **Verified** | `AGENTS.md` is injected into Codex's prompt · **Verified**. `CLAUDE.md` isn't injected; `AGENTS.md` tells Codex to read it first |
| `/shipmate`, **the one command** (since 2026-09-27; say what you need, or `help`, `status`, or a stage name to steer) | Plugin skill `skills/shipmate`, shown as `/ship-framework:shipmate` · **Verified live** (CoachEva trial, 2026-09-30): a bare `/shipmate` resolves, the request arrives, and the stage, the review and its reviewers ran on a real app | `/shipmate` (`.claude/skills/shipmate/`: the entry and its stage files) · **Unverified** in a live session (installed and checked by the install tests) | **Not supported** as a literal command. Say what you want; `AGENTS.md` has Codex follow the same entry and stage files |
| Picking the stage (`ship.py start`: the project's facts, a suggested stage from tested rules, the references it routes, a one-line announcement) | Needs `python3` · **Tested locally** (routing suite 55/55) | Same · **Replayed** on sample apps installed with `setup.sh` (2026-09-27) | Same entry and `ship.py`, followed as instructions · **Unverified** |
| Starting a workflow from a plain request ("something broke", "take care of #3") | Router skill (Claude decides whether to invoke it; it points at the same entry) + the session line naming `/ship-framework:shipmate` · **Measured under plugin eval** (2026-09-29): of 20 requests, it started Ship for all 10 product requests and stayed out of the 10 others (59 of 60 runs right) | Session line + `CLAUDE.md` · **Unverified** | `AGENTS.md` maps requests to workflows · **Observed once** (2026-09-23 journey read Ship's instructions, references, registry, taste and review tools unprompted) |
| Ship skills (routing, platform, design, knowledge) | Plugin skills · **Verified** (`claude plugin details`) | `.claude/skills/ship/` · **Verified** | **Not supported** as Codex skills: Codex discovers `~/.agents/skills`, `$CODEX_HOME/skills`, and `<repo>/.agents/skills`, not `.claude/skills` (**Verified**). Codex reads Ship references as plain files when `AGENTS.md` points it there |
| Isolated reviewers (product review, design review, visual check, tests, second look) | Plugin agents `ship-framework:ship-crit` … · **Verified** (5 agents load) | `.claude/agents/ship-*.md` · **Verified** (files installed) | **Not supported.** The review stage runs the reviewers one after another in a single context. Independent judgments, parallelism, and per-reviewer models are Claude-only |
| Care pass (`review --care`, **preview**: what a product is missing, not only what's wrong) | Product review, design review and the visual check as subagents · **Tested locally** (scope; records kept out of, and refused by, the launch gate). **Paid evaluation** on two sample apps (2026-09-29 to 10-01) passed on one and slipped once in four runs on the other, so there's no measured claim yet. Not yet run live in a simulator task walk | Same · **Replayed once**, single-context, on a sample app installed with `setup.sh` (2026-09-27) | One context, labelled **not independent** |
| Design gate (a *new* UI/motion/copy file needs `PDC.md`; edits to existing files are allowed) | Plugin `PreToolUse` hook, registered for every session (not tied to a skill) · **Verified live** (denied a new view, 2026-09-23) | `.claude/settings.json` hook · **Verified** | **Instructions only**: `AGENTS.md` states the rule; nothing blocks the edit. (Codex has a hooks feature; Ship doesn't wire it) |
| Design gate after shell commands (reports a hand-edited generated file or a gated new file written by `sed`/scripts; **detects, doesn't prevent**) | Plugin `PostToolUse` hook on Bash · **Tested locally** (trial bypass reproduced), not yet observed live | `.claude/settings.json` hook · **Tested locally** | **Not wired** |
| Blocks from the `careful`, `freeze` and `guard` stages | Skill-scoped hooks · **Documented** | Same · **Documented** | **Not supported** (advice only) |
| Reviewer agent `hooks` / `mcpServers` / `permissionMode` frontmatter | **Ignored** for plugin agents · **Documented** | Honoured · **Documented** | Not applicable |
| Knowledge routing + `knowledge.py doctor` | Yes, needs `python3` | Yes, needs `python3` | Yes, needs `python3` |
| The `codex` stage (a second opinion) | Needs the `codex` CLI | Needs the `codex` CLI | Not needed: you're already in Codex |
| Updates | Marketplace version bump → `claude plugin update` · **Verified** (5.1.0 → next in an isolated config) | `ship-update.sh`, including from a 5.1.0 project through its old self-updating script · **Verified** | Same as project install |

---

## What updates touch

Ship's update (project install) replaces **Ship's files** and never overwrites **yours**.

**Ship's files** are replaced on update. If you edited one, your copy is saved to
`.ship/backups/<date-time>/` first:

- `.claude/team-rules.md`, everything under `.claude/skills/ship/`
- `.claude/skills/shipmate/`: the `/shipmate` entry and its stage files (the old `.claude/commands/ship-*.md`
  and their `.claude/skills/ship-*/SKILL.md` mirrors are removed on update)
- Ship's review agents in `.claude/agents/` (`ship-*.md`)
- `CHEATSHEET.md`, `ship-update.sh`, `.claude/skills/README.md` (only if Ship put them there)
- `AGENTS.md` and `.ship/framework.yaml` (only while they say they're managed by Ship)
- In `CLAUDE.md`: only the `<!-- BEGIN/END:ship-generated:… -->` / `ship-managed:…` blocks and
  the `> Ship Framework v…` line

**Your files** are created if missing and never overwritten or removed: the rest of `CLAUDE.md`,
`TASKS.md`, `DECISIONS.md`, `CONTEXT.md`, `LEARNINGS.md`, `DESIGN.md`, `PDC.md`,
`design-model.yaml`, `design/`, taste stores, `references/`, `.claude/skills/your-skills/`,
your own agents and commands, generated platform files, and your code. Settings: Ship only adds
its hooks next to yours (and upgrades its own older hook entries).

**Retired files.** When Ship stops shipping a file, the update removes it; an edited copy goes to
`.ship/backups/` instead. Ship recognises its own files by hash (`.ship/manifest.json`, written
on every install), so a file you added, even inside `.claude/skills/ship/`, is never removed
for being unknown.

**An existing `AGENTS.md` that isn't Ship's** stays untouched. Ship writes its Codex bridge to
`.ship/AGENTS.ship.md`; add one line to your `AGENTS.md` so Codex uses it:
`Ship Framework: read .ship/AGENTS.ship.md and follow it.`

**Plugin installs** keep Ship's files in the plugin, not your project. The project gets
`CLAUDE.md` (appended to yours if you have one; a copy is backed up), the memory files, and
Ship's managed `.claude/team-rules.md`, which the plugin refreshes after a plugin update.

---

## Missing optional tools

Nothing optional ever fails an install. After install/update Ship prints what's missing and how
to add it (`python3 .claude/skills/ship/knowledge/bin/knowledge.py doctor` for the full list).

| Missing | What's reduced | Add it |
|---|---|---|
| Node.js / `npx` | No Playwright screenshots for visual QA (the visual check reads code instead) | Install Node.js, then `npm install -D @playwright/test && npx playwright install chromium` |
| `codex` CLI | The `codex` stage is unavailable | `npm install -g @openai/codex` |
| `xcodegen` (iOS projects using `project.yml`) | Ship can't regenerate the Xcode project after adding files | `brew install xcodegen` |
| `python3` | Install can't run; knowledge routing and design registry tools unavailable | macOS: `xcode-select --install` |

Playwright is only installed by `setup.sh` into an empty folder or a project that already has
`package.json`, never into an existing non-JS project. Skip it with `--no-playwright`.

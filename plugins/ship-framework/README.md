# Ship Framework

A design-led AI product team for one-person teams. Think, design, plan, build, review, and ship —
with your decisions, design system, and taste carried through every step.

## One Command

Plugin commands show namespaced, so it's `/ship-framework:shipmate`. Say what you need after it:

```
/ship-framework:shipmate the login crashes
/ship-framework:shipmate make onboarding feel warmer
/ship-framework:shipmate the booking flow feels generic
/ship-framework:shipmate ship it
/ship-framework:shipmate                   # continue where you left off
/ship-framework:shipmate help              # example requests
/ship-framework:shipmate status            # where things stand
```

Ship reads the project first (setup, stack, design system, changes, tasks, the last review), picks
the stage, and says in one line what it's doing and how to redirect. It asks only when two readings
lead to different work or a step is hard to undo. Stages chain (build, then review) and pause only
for your decisions; Ship continues or asks, and never tells you to type another command.

The command hasn't been run in a live Claude Code session yet, in either form; if a bare `/shipmate`
doesn't resolve, use the namespaced one. Plain requests without the command can also be routed: the
plugin's router skill points Claude at the same entry, but Claude decides whether to use it. If a
reply skips the stage you wanted, name it.

## How It Works

The journey: Setup → Think → Design → Plan → Build → Review → Launch → Retro, with depth scaled to
the task — a copy fix goes straight to build and a quick check. A small fix stays small even in
shared code: one line names every screen or caller it reaches, and each one is checked. Existing
projects are adopted: "adopt my design system" drafts the registry from your code and keeps your
names.

Stage names are optional steering words — put one first to go straight there
(`/ship-framework:shipmate review --full`): `think` · `design` · `plan` · `build` · `review` ·
`launch` · `retro` · `fix` · `variants` (design options; your pick becomes taste) · `html`
(prototype) · `qa` (tests only) · `browse` (visual QA) · `perf` (web speed gate) · `money`
(pricing) · `codex` (second opinion) · `careful` · `freeze` · `guard` · `unfreeze` (safety) ·
`team` (the whole team: continue, multi-stage requests, the roadmap) · `update`.

A product lead, tech lead, builder, debugger, release lead, and business lead work in your
conversation. Reviewers run as isolated subagents (`ship-framework:ship-crit` …), sized to the
change's risk:

- **Product review** — can real users finish the task: flows, states, edge cases, copy
- **Design review** — consistency with your registry, product decisions, and taste
- **Visual check** — judges only what it has seen rendered, with screenshots
- **Tests** — runs the tests, reproduces the symptom, pass/fail with output
- **Second look** — challenges every finding by name and looks for what was missed

Findings carry evidence (file and line, screenshot, command output) — no scores.

**Care pass (preview).** "Feels generic" or "what's missing" gets a proposed point of view, what to
keep, at most three gaps ranked by what they cost the user — each with evidence, a fix and a check —
and what wasn't checked. It's report-first, and it never counts as the review launch needs.

Hooks: the design gate (a new UI file needs `PDC.md`; generated themes aren't hand-edited) and
session start (one line, plus notes when they matter). Both stay silent outside Ship projects.

## Install

```
/plugin marketplace add ismailkose/ship-framework
/plugin install ship-framework@ship-framework
```

Or open `ship-framework.plugin` from the [latest release](https://github.com/ismailkose/ship-framework/releases)
(Cowork / Claude desktop). In the CLI, `claude --plugin-dir ship-framework.plugin` loads it for one session.

Ship works in a project as it is: `knowledge.py project` reads the stack (declared in `CLAUDE.md`,
or detected from the project's Xcode/Gradle/package files) and the project's own instructions
(`AGENTS.md`, `CLAUDE.md`), which come first. To add Ship's files — `CLAUDE.md` with Ship's section,
`TASKS.md`, `DECISIONS.md`, `CONTEXT.md`, `LEARNINGS.md`, and the managed `.claude/team-rules.md` —
ask `/ship-framework:shipmate` to set up the project (its first-run setup) or run
`bootstrap-project.sh`; Ship asks first when the project already has its own instructions. It never
overwrites your files.

## Updating

`claude plugin marketplace update ship-framework`, then `claude plugin update ship-framework@ship-framework`
(or turn on auto-update for the marketplace in `/plugin` › Marketplaces). Restart or `/reload-plugins`.
Your project files are never touched; Ship's managed `.claude/team-rules.md` refreshes at the next session.

Coming from 5.1: the 21 separate commands are gone — they're stages of `/ship-framework:shipmate`
now. Say what you need, or put the old command's stage name first (`fix`, `review`, `launch` …).

## Codex

The plugin is Claude-only. For Codex, use the project install (`setup.sh`), which adds `AGENTS.md` and
the references Codex reads. Codex has no isolated reviewers: reviews run in one context and are
labelled not independent. Full comparison:
[CAPABILITIES.md](https://github.com/ismailkose/ship-framework/blob/main/CAPABILITIES.md).

## What's Included

- **Knowledge routing** — `knowledge.py route` lists what to read for a task, in one precedence
  order: platform requirements › your decisions › your taste › platform guidance › expert sources ›
  Ship defaults. `knowledge.py doctor` lists any expert skill you installed yourself; the route adds Ship's corrections.
- **References** — UX, components, hardening, iOS, web, motion (Emil Kowalski's motion skills,
  ported under MIT), and the care lens. Android routes to Google's developer docs.
- **Design registry** — `design-model.yaml` + `design/components.yaml`, emitted to SwiftUI, CSS,
  Tailwind v4, and Compose.
- **Taste** — `design/taste.yaml` and `~/.ship/taste.yaml`, recorded in your words.

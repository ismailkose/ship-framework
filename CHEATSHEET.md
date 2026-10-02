# Ship Framework Cheatsheet

One page. Full picture: `README.md` · what works where: `CAPABILITIES.md`.

---

## One command

`/shipmate`, then what you need in your own words. In the plugin: `/ship-framework:shipmate`.

```
/shipmate the login crashes
/shipmate make onboarding feel warmer
/shipmate the booking flow feels generic
/shipmate ship it
/shipmate                    # continue where you left off
/shipmate help               # example requests
/shipmate status             # where things stand
```

Ship reads the project first, picks the stage, and says in one line what it's doing and how to
redirect ("say 'plan it first' to change it"). It asks only when two readings lead to different
work or a step is hard to undo. Stages chain, and Ship continues or asks; you never have to type
another command.

A plain request without `/shipmate` can be routed too, but Claude decides whether to use Ship's
router. If a reply skips the stage you wanted, name it: `/shipmate fix`.

## Runtime

- `CLAUDE.md`: canonical project context. Yours.
- `AGENTS.md`: Ship's managed Codex bridge back to `CLAUDE.md` (or `.ship/AGENTS.ship.md` if you have your own `AGENTS.md`).
- `.ship/framework.yaml`: Ship's managed core (journey workflows + knowledge map).
- In Codex, `/shipmate` stage names are workflow labels, and reviews run in one context, labelled **not independent**. Isolated reviewers, hooks, and slash commands are Claude-only.

---

## The journey

**Setup → Think → Design → Plan → Build → Review → Launch → Retro.** Ship picks where a request
starts and how deep it goes. Stage names are optional: put one first to steer
(`/shipmate plan the sync feature`).

| Stage | Who | One-liner |
|-------|-----|-----------|
| `think` | Product lead | Ask only the questions whose answers change what gets built. |
| `design` | Design lead + visual check | Adopt an existing app's system, plant a seed, or extend, proven on a real screen. |
| `plan` | Product lead + tech lead (+ design review, second look) | Resolve choices and risks, then a build order. Light or full. |
| `build` | Builder | One feature, on your registry, with evidence it works. |
| `review` | Product review · design review · visual check · tests · second look | Isolated reviewers sized to risk. Evidence, not scores. |
| `launch` | Release lead | Review gate (fresh + complete + no blockers), evidence gates, deploy, post-deploy check. |
| `retro` | Retro | Git history, what actually happened, lessons kept. |

**Small fixes stay small**, even in shared code: one line names every screen or caller the change
reaches, and each is checked. A declared scope and a plan are for new behaviour and structural
changes.

Existing project? Say "adopt my design system": Ship drafts the registry from your code, keeps
your names, and your views don't change.

---

## Other stages

| Stage | Situation |
|---------|-----------|
| `fix [error]` | Something broke. Reproduce first, then investigate. |
| `variants` | Theory-backed design options; your pick becomes taste. `--quick` · `--refine` · `--taste` · `--mockup` |
| `html` | Responsive single-file HTML prototype. `--quick` · `--dark` · `--form` |
| `qa` | Same as `review --test`. |
| `browse` | Visual QA in a browser. `--watch` headed · `--auth` cookies · `--perf` vitals |
| `perf` | Core Web Vitals gate: PASS / WARN / FAIL per route. `--compare` · `--ci` |
| `money` | Pricing strategy. |
| `codex` | Codex second opinion from inside Claude (needs the `codex` CLI). |
| `update` | Update a project install (plugin: `claude plugin update ship-framework@ship-framework`). |
| `careful` · `freeze [dir]` · `guard` · `unfreeze` | Destructive-command warnings · edit lock · both · unlock. |

`/shipmate` alone, "continue", requests that span stages ("plan and build the sync"), the roadmap,
a takeover ("take over this project"), and task lists run as the whole team (`team`).

**Hooks (Claude):** the design gate stops a *new* UI/motion/copy file until `PDC.md` exists, and
refuses hand edits to generated files. Session start is one line (version, product, stack, open
tasks), plus notes only when they matter.

---

## Review: depth and flags

| Flag | What runs |
|------|-----------|
| (none) | Auto depth: **quick** (1 or 2 reviewers) · **standard** (product review + tests, + design review and the visual check on UI) · **full** (all four, then the second look) |
| `--quick` · `--standard` · `--full` | Force a depth |
| `--product` · `--design` · `--visual` · `--test` | Only product review · design review · visual check · tests (combine them) |
| `--base <ref>` | Review against a specific commit/branch |
| `--since-review` | Only what changed since the last review |
| `--report` | Findings only, no fixes |
| `--care "<the task>"` | **Care pass (preview).** What one journey is missing: a point of view, what to keep, at most 3 gaps with evidence, a fix and a check each, what wasn't checked. Report-first. Also: "feels generic", "what's missing" |

Every finding cites file:line, a screenshot, or command output. The record in `.ship/reviews/`
tracks coverage (did every selected reviewer complete?) separately from findings, and launch runs
`review.py gate`: **PASS**, **STALE**, **INCOMPLETE**, **NO_REVIEW**, or **BLOCKERS**. A care pass
is recorded apart and never satisfies that gate.

## Plan and design modes

| Flag | Mode |
|------|------|
| `plan --dream` · `--focus` · `--strip` | Expand · hold · reduce scope |
| `design adopt` · `--init` | Draft the registry from code · what the design gate asks for |
| `design --tokens` · `--audit` · `--preview` · `--motion-tune` | Edit tokens · check the system against its scale · regenerate previews · tune motion |

---

## Knowledge

```bash
python3 .claude/skills/ship/knowledge/bin/knowledge.py route --text "<the task>"   # what to read, in order
python3 .claude/skills/ship/knowledge/bin/knowledge.py doctor                      # installed / missing skills
```

**Precedence:** platform requirements & accessibility › your product decisions › your preferences › platform guidance › expert sources › Ship defaults › agent guesses.

Recommended skills: AvdLee SwiftUI + Swift Concurrency (iOS), Vercel React skills, shadcn skill (web), Google Android skills + chrisbanes Compose skills (Android). `doctor` prints each install line. Motion follows Emil Kowalski.

---

## Design registry and taste

```bash
python3 .claude/skills/ship/design/bin/design_model.py match --role <role>   # before any UI element
python3 .claude/skills/ship/design/bin/design_model.py validate              # after a registry change
python3 .claude/skills/ship/design/bin/design_model.py emit all              # SwiftUI · CSS · Tailwind v4 · Compose
python3 .claude/skills/ship/design/bin/design_model.py docs
python3 .claude/skills/ship/taste/bin/taste.py query --surface <screen>      # before UI, copy, motion work
```

Build loop verdicts: **reuse** · **extend** (new variant on your tokens, no interruption) · **planned** (build it) · **founder** / **conflict** (one question) · **miss** (reusable → register; one-off → keep local).

---

## Key files

| File | Purpose | Who writes |
|------|---------|-----------|
| `CLAUDE.md` | Product, founder profile, stack, your skill wiring | You |
| `TASKS.md` · `DECISIONS.md` · `CONTEXT.md` · `LEARNINGS.md` | Shared memory | The team, you |
| `PDC.md` | Design contract; indexes the files below | Design stage |
| `design-model.yaml` | Every token value (source of truth) | Design stage, you |
| `design/components.yaml` | Registered components: role, API, when to use | Design stage, builder |
| `DESIGN.md` | Design intent in prose, including the point of view; no values | Design stage, you |
| `design/taste.yaml` · `~/.ship/taste.yaml` | Your taste: this product · across products | Recorded from your words |
| Generated themes, previews, `design/COMPONENTS.md` | Emitted from the registry, never hand-edited | `design_model.py` |
| `.ship/reviews/` | Review records (coverage + freshness, checked at launch); care passes kept apart | Review stage |
| `.ship/state/` | Session state, git-ignored: the references routed for the current task (review checks against them), skill versions | `knowledge.py` |
| `AGENTS.md` · `.ship/framework.yaml` · `.claude/team-rules.md` | Ship-managed | Ship |
| `PERF-REPORT.md` | Performance results | `perf` stage |

---

## The Founder section

In `CLAUDE.md`, it shapes how every role works with you: Background · Technical comfort · Decision style · Communication · Taste · Context need · Focus awareness.

## Status messages

| | Status | Sounds like |
|---|--------|------------|
| ✓ | DONE | "Plan is locked. Starting on the first build item." |
| → | DONE_WITH_CONCERNS | "Works, but the loading state feels abrupt." |
| ⏸ | BLOCKED | "Over to you: safe layout or bold bento grid?" |
| ? | NEEDS_CONTEXT | "Is onboarding for the admin who signs up, or the teammates they invite?" |

Then the next step: Ship continues into it, or asks.

---

## What blocks shipping

| Gate | Rule |
|------|------|
| Contrast | Text 4.5:1 (large 3:1); UI parts and focus rings 3:1, in every mode and state |
| Operable | Keyboard reachable, visible focus, not obscured |
| Targets | ≥ 24×24 CSS px (WCAG AA); Ship default 44 pt iOS · 48 dp Android · 44 px touch web |
| Alternatives | Every gesture and drag has a single-pointer alternative |
| Text scaling | Dynamic Type / font scale / 200% zoom and 320 px reflow without loss |
| Forms | Visible labels, autocomplete, errors in text next to the field, paste allowed |
| Motion | Reduce Motion / `prefers-reduced-motion` honoured |
| Registry | No literal colors/sizes/spacing; reusable components registered |

---

## Quick frameworks

**JTBD:** "When I [situation], I want to [motivation], so I can [outcome]."
**HEART:** Happiness · Engagement · Adoption · Retention · Task success
**RICE:** (Reach × Impact × Confidence) / Effort. A thinking tool; it never overrules a founder decision.

## Core rules (`.claude/team-rules.md`)

1 · Restate the request; ask the one question that changes the approach, or state your assumption
2 · One precedence order everywhere
3 · References on demand: name what you relied on
4 · Plan when it's consequential; small fixes go straight to build
5 · Verify before claiming: show the output; UI needs a screenshot
6 · DONE or BLOCKED, never "mostly done"
7 · Platform first: a custom build needs a reason
8 · Log decisions, and whether each is a one-way or two-way door
9 · The founder decides
10 · Decisions by kind: mechanical (just do it) · taste (surfaced to you) · challenging your direction (always asks)
11 · One decision per question, with a recommendation
12 · Flag costs; real users beat hypothetical ones

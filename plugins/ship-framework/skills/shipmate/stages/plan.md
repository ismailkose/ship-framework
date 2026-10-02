Plan a feature — resolve implementation choices and real risks, then a build order. Depth scales with the change.

Read CLAUDE.md, DECISIONS.md, and LEARNINGS.md before planning. If the product has a design registry (`PDC.md`, `design-model.yaml`, `design/components.yaml`), plan against it — the direction is set; don't re-propose it.

## Plan depth — pick one and say which

- **Light** — one obvious approach, low risk, reversible (a new list row, a settings toggle, a copy flow). Write: approach, files, risks, how it will be verified → TASKS.md. No personas, no stress test.
- **Full** — a new product or feature area, data model, auth, payments, navigation, sync, or anything hard to undo. Run the product lead → tech lead → design review → second look below. Name them by role for the founder; the persona names are internal.

Existing project: plan against the code, registry, and decisions that exist. Settled decisions in DECISIONS.md stand unless the founder reopens them.

## Check for `think` output

Before the product lead starts, check DECISIONS.md for an **IDEA BRIEF** entry from `think`.

**If an idea brief exists:**
- The product lead reads it and skips the forcing questions (Q1-Q4) — they were already answered
- It still runs the Three Ways This Could Work and The Product Brief
- Inherit the scope mode from the idea brief (dream/focus/strip)
- It can refine the idea brief but doesn't restart from scratch

**If no idea brief exists:**
- Ask only the forcing questions whose answers are open and would change the plan (see `think`'s sorting: known / doesn't matter / open)
- When the idea itself is unclear, offer `think` first (optional; it saves time on ideas that need more research).

**Skills:** the route below names the ones this plan needs; don't preload the rest. Also load the
founder's own skills that CLAUDE.md's skill wiring gives to plan.

**Project:** `python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-knowledge/bin/knowledge.py project` — the stack (declared, or detected from the project's files), the project's own instructions (they come first), and Ship's state. Unknown stack → ask what you're building. Don't create `CLAUDE.md` or Ship's files unless the founder asks; write the Stack into `CLAUDE.md` only when it already has Ship's section.

<!-- BEGIN:ship-generated:command-plan-load-references -->
## Knowledge

Product first — `DECISIONS.md`, `design-model.yaml`, `design/components.yaml`, `design/taste.yaml`, `DESIGN.md`. They win over everything but platform requirements and accessibility (precedence: `${CLAUDE_PLUGIN_ROOT}/skills/ship-knowledge/SKILL.md`).

`/shipmate` already routed the request (`.ship/state/route.json`). When the change touches more,
route the extra areas **by what they mean** (a jumpy button is `motion`, however it's phrased);
the router lists the files for this stack and version, with installed skills, and records them:

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-knowledge/bin/knowledge.py route --domain <id>,<id> --changed --record`

Read only the parts the change needs. Areas:
`accessibility` · `ux-foundations` · `layout-spacing` · `product-psychology` · `navigation` ·
`components` · `motion` · `ios-swiftui` · `ios-27` · `ios-frameworks` · `ios-swiftui-building` ·
`ios-swift-practice` · `ios-data-sync` · `ios-commerce-identity` · `ios-notifications-background` ·
`ios-media` · `ios-system-integration` · `ios-device-data` · `ios-intelligence` ·
`ios-accessibility` · `ios-accessories` · `android-compose` · `web-react` · `web-a11y` · `web-perf` ·
`design-system` · `review-process`.

Record what you relied on, for review, never in the reply: `knowledge.py note --read "<files §>"
--applied "<what it changed, where>" --not-read "<file, why>" --verified "<check → result>"`.
Routed isn't read and read isn't applied. The founder hears only what changes for them.
<!-- END:ship-generated:command-plan-load-references -->

## Flag Handling

Available flags: vi-only (product lead), arc-only (tech lead), pol-only (design review), with-monetization, --dream, --focus, --strip. Auto-detect scope mode (dream/focus/strip) from idea maturity if no flag given. Announce selection before proceeding.

## ━━━ Product lead (Vi) ━━━

**Voice:** Think in user moments, not features. Push for the magic moment—the thing someone would screenshot to show a friend.

**Step 0: Sharpen the Idea** — Restate in one sentence. Ask ONE clarifying question if vague (core rules › One decision per question).

**Pushback Posture** — Challenge undefined terms and hidden assumptions ("You said 'simple' — simple to build or simple to use? Usually opposite things."). If founder says "just build it," ask TWO more pointed questions (the two most likely to reveal a fatal flaw). If they still insist, proceed but log to DECISIONS.md: "Founder skipped product challenge. Unresolved: [list]."

**Four Forcing Questions:**
- Q1: Who has this problem, and how do you know?
- Q2: What do people do today instead?
- Q3: Show me exactly how one person uses this.
- Q4: What's the smallest version that would feel COMPLETE?

**Three Ways This Could Work** — Describe 3 user experiences (simplest flow, most delightful, most different). Founder picks one. Can't pick, and it's cheap to undo? Build the two leading ones as `[probe]` tasks and look, in place of more debate (`variants` when only the look differs).

**The Product Brief (one line each — fill the items this feature actually needs; mark the rest n/a):**
1. The Bar Test (one-sentence explanation)
2. The Existing Workaround (and what makes leaving it feel risky: their data, their habits)
3. The Job Statement (When I..., I want to..., so I can...)
4. The Magic Moment
5. The Kill List (features NOT in v1)
6. The 2-Week Bet
7. The Success Metric (a HEART dimension + number; while users are few, count people, not percentages: "by [date], 6 of my 12 users [do the core action] in two separate weeks")
8. Who Pays
9. The PMF Signal
10. Growth Mechanism (viral, content, product-led, or paid)
11. **The Aesthetic Direction** — if a design registry exists, cite it (brand feel, the registered components this feature reuses) and stop. If not, name the direction in words ("warm, quiet, precise") and continue into `design` for the seed — tokens and hex values live only in `design-model.yaml`, never in the plan.
12. **The Experience Walk-Through** — "You open the app. The first thing you see is ___. You tap ___. The moment that makes you think 'oh, this is good' is when ___." Present tense, second person, 100 words max. Cover: first launch, magic moment, return visit. This walk-through is the north star — if the technical plan conflicts with it, the walk-through wins.

## ━━━ Tech lead (Arc) ━━━

**Voice:** Bridge design intent and code reality. Explain user-facing consequences (e.g., "data syncs automatically" not "CloudKit").

**The Technical Plan (8 items, one line each):**
1. Stack Decision (platform-appropriate, include setup command)
2. Data Model (tables, fields, relationships; each field people type has a named use, or it isn't asked)
3. Screen Map (journey order, apply Hick's Law; long or branching data entry gets a start screen, one question per screen, a task list, check answers and a confirmation: `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/forms-feedback.md` §3)
4. Build Order (dependencies first, then the magic moment; mark [COMPLEX] features; RICE only to break a real tie between candidates; size each step from similar past work, since plans run long, and give polish a timebox, since it fills whatever time it gets)
5. Motion Map (what moves, how often users see it — frequency decides whether it animates at all — which motion tokens it uses, and the Reduce Motion behaviour; decisions per `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/SKILL.md`)
6. Risks & Unknowns (what could break technically)
7. Disagreements with the product brief (if it asks for something risky)
8. State Diagrams (for 3+ state features: onboarding, forms, auth, sync), and four lines per new interaction: what starts it (and what starts it without a tap, changeable where), what it shows before it's used, what happens the tenth time, and whether it creates a mode and how that ends

**Dual-Approach Planning** — Present Approach A (minimal/fastest) and Approach B (clean/best architecture) with tradeoffs and recommendation.

**Dependency Analysis** — Build item dependencies as table. Flag parallel-safe and sequential items.

**Security Check** — Before finalizing plan, verify:
   - ALL: No hardcoded secrets in source, HTTPS for network, user input validated, env vars for credentials
   - iOS: Keychain (not UserDefaults) for sensitive data, ATS not globally disabled, Data Protection class set
   - Web: No secrets in client code, CORS not wildcard in prod, auth tokens in httpOnly cookies (not localStorage), CSP headers, server-side validation mirrors client
   - Android: EncryptedSharedPreferences/Keystore, network security config, ProGuard/R8 for release

## ━━━ Design review (Pol, agent call) ━━━

**Design readiness (Full depth).** In Claude, run the `ship-pol` subagent (plugin install: `ship-framework:ship-pol`; isolated context) on the brief + plan, telling it `"mode": "plan"`; in runtimes without subagents, read `.claude/agents/ship-pol.md`, apply it yourself, and label the result **NOT INDEPENDENT**. Seven dimensions — Information Architecture, Interaction State Coverage, User Journey, Generic-AI Risk, Design System Alignment (reuses registered components; new ones justified), Responsive & Accessibility, Unresolved Design Decisions — each **pass** or **concern** with the specific gap. No numeric scores. The plan proceeds when no concern is a blocker the founder hasn't accepted.

## ━━━ Second look (Adversarial, the stress test) ━━━

**Stress test (Full depth).** In Claude, run the `ship-adversarial` subagent (plugin install: `ship-framework:ship-adversarial`) in plan mode (`"mode": "plan"`) with the brief, the plan, and the design review's concerns. It attacks: Missing States, Race Conditions, Edge Cases, Contradictions, Scope Creep, Security, Generic Design — challenges the design review's concerns by name — and returns `plan_verdict`: `approved` or `needs-revision`. The plan graduates when every blocker is resolved or explicitly accepted by the founder.

## Open decisions

**Only the founder approves** (core rules › Decisions by kind). Don't log a founder decision for mechanical choices, or for anything the
founder already settled — in this request or an active DECISIONS.md entry. A Taste or User Challenge
call the founder hasn't answered is **open**: ask it now if the plan can't proceed without it;
otherwise log it with `**Status:** pending`, `**Recommended by:** tech lead — <your recommendation>`, and
`**Blocks:** <the TASKS items that depend on it>` (not `**Called by:** founder`). Your recommendation
is not an approval. When the founder answers, set `**Called by:** founder`, `**Status:** active`.

Before printing the status:
`python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-knowledge/bin/decisions.py check --status <STATUS>` — with an open
decision the plan is `BLOCKED`, never `APPROVED`: name the question and the items that can start
without it.

## Cross-Model Verification

Optional: Check if Codex is available. If yes, run in challenge mode and compare findings to the second look. If disagreement, present both to founder.

## Design direction

Design direction belongs to the design registry, written by the `design` stage. If this plan changed it (founder picked a new direction), log the decision in DECISIONS.md and continue into `design` to update the registry — don't record fonts or hex values here.

Save the plan to TASKS.md — each build order item becomes a task.
Log architecture decisions to DECISIONS.md.
Write project learnings to CONTEXT.md.

<!-- BEGIN:ship-generated:command-plan-status-footer -->
## Status

End with where things stand, in plain words (core rules › Status). Ship's names, for its records:
- `APPROVED` — plan approved; the build order is in TASKS.md.
- `NEEDS_REVISION` — revise the flagged sections and stress-test again.
- `BLOCKED` — waiting on founder input. Name each open decision (DECISIONS.md, `Status: pending`) and the build items that can start without it.

**Next:** `build` — the first item in the build order. Continue into it when the request covers it;
otherwise offer it in one line. Never tell the founder to type a command.
<!-- END:ship-generated:command-plan-status-footer -->

The founder's request: what they typed after `/shipmate` (without the stage name).

# Ship Framework — Cheatsheet

---

## Commands

| Command | When to use |
|---------|-------------|
| `/team [task]` | Default for everything. Routes to the right agents. |
| `/team continue` | Start of day. Picks up from TASKS.md. |
| `/health` | Full strategic review — product fit, tech, UX, business, visual. |
| `/team Take over` | Existing codebase. Assess → audit → strategy → roadmap. |
| `/status` | Quick progress check. |
| `/visionary [idea]` | Validate an idea before building. 10 items: bar test, workaround, JTBD, magic moment, kill list, 2-week bet, North Star metric, who pays, PMF signal, growth mechanism. |
| `/architect [brief]` | Plan how to build something. |
| `/build` | Code one feature. |
| `/browse` | Visual QA — 6 phases: setup, screen map, mobile, interaction walkthrough, bug checklist, report. |
| `/qa` | Test + fix — 8 phases: scope, run tests, explore like a user, document issues, write tests, health score, fix loop, report. |
| `/critic` | HEART review of what was built. |
| `/polish` | Refine design details. |
| `/ship` | Deploy — 9 phases: branch resolution, pre-flight, tests, quality gate, readiness + growth checks, deploy, post-deploy verify, report, measurement plan. |
| `/money` | Pricing strategy — 9 steps: WTP, model, free line, price, free-tier, self-serve ceiling, implementation, iteration, disagreements. |
| `/fix [error]` | Debug systematically — 4 phases: investigate, find pattern, hypothesize, fix + verify. 3-strikes rule. |
| `/retro` | Weekly retro — 10 steps: data, metrics, streak, time patterns, hotspots, task health, decision + measurement review, narrative, trends, update CONTEXT.md. |

---

## JTBD

Two levels — product and feature:

```
"When I [situation], I want to [motivation], so I can [expected outcome]."
```

Vi writes the product-level JTBD. Arc writes one per feature in the build order.
No JTBD = don't build it.

---

## HEART

Crit picks 2-3 per review:

| H | Happiness | Does the user feel good using this? |
|---|-----------|-------------------------------------|
| E | Engagement | How deeply do they interact? |
| A | Adoption | Can new users figure it out? |
| R | Retention | Do they come back? |
| T | Task success | Can they complete the core flow? |

Vi picks one HEART dimension as the success metric for each feature.

---

## RICE

Arc scores every item in the build order. /team uses it to break priority ties.

```
Score = (Reach × Impact × Confidence) / Effort
```

| Reach | Users affected per week | number |
|-------|------------------------|--------|
| Impact | How much it moves the needle | 3 / 2 / 1 / 0.5 / 0.25 |
| Confidence | How sure are we | 100% / 80% / 50% |
| Effort | Person-weeks to build | number |

Magic moment feature always goes first regardless of score.

---

## QA Health Score

/qa computes a health score after testing:

```
Start at 100. Critical: -25, High: -15, Medium: -8, Low: -3
```

| 90-100 | Ship it |
| 70-89 | Fix criticals and highs first |
| 50-69 | Needs work |
| Below 50 | Don't ship |

---

## Motion Budget

Arc defines, Crit checks. Limit competing patterns per screen, not element count.

| Level | Motion | Example |
|-------|--------|---------|
| Magic moment | Most expressive | Check-in completion reveal |
| Primary actions | Clear, purposeful | Navigation slide, submit confirmation |
| Secondary UI | Functional, quick | Tooltip, dropdown, toast |
| Background | Subtle | Loading skeleton, pulse |
| Repeated (50x/day) | Minimal or none | Button tap, list scroll |

**1-2 simultaneous motion patterns per screen.** A staggered group counts as one.

9 animation principles: anticipation, staging, follow-through, secondary action, squash & stretch, exaggeration, arcs, solid drawing, appeal.

8 pattern foundations: reveal on hover, stacking, staggered reveal, shared element transition, dynamic resize, directional navigation, inline expansion, element-to-view expansion.

Deep-dives (loaded only when needed): `animation-css.md` (universal, includes View Transitions API), `animation-framer-motion.md` (React, includes advanced AnimatePresence), `animation-performance.md` (universal).

6 agents check: Arc (spec + restraint) → Dev (build + adapt) → Pol (feel) → Eye (visual) → Test (accessibility) → Crit (balance)

---

## Component Architecture

Three layers: **Primitives** (headless — behavior + accessibility) → **Styled** (your design tokens applied) → **Product** (your features + business logic).

**The layering rule:** Your design system overrides where it has opinions. Primitives fill the gaps.

For React web: Base UI (primitives) + shadcn/ui (styled). Native stacks use platform primitives.

Never rebuild accessibility (focus trapping, keyboard nav, ARIA) — use a primitive. Check `references/components.md`.

**Extend:** Add `references/design-system.md` with your tokens and component rules. See `references/README.md` for the template.

6 agents check: Arc (spec architecture) → Dev (build from primitives) → Pol (feel + keyboard) → Eye (visual consistency) → Test (keyboard + screen reader) → Crit (adoption + accessibility)

---

## UX Principles

20 principles in 4 groups. `references/ux-principles.md`.

**Making Decisions Easy:** Hick's Law (fewer choices), Miller's Law (chunk data ~7 items), Cognitive Load (remove noise), Progressive Disclosure (basics first), Tesler's Law (system absorbs complexity), Pareto (optimize the 20%).

**Making Interactions Work:** Fitts's Law (44px targets, expand hit areas), Doherty Threshold (<400ms or fake it), Postel's Law (accept messy input), Goal Gradient (show progress).

**Making Layout Communicate:** Proximity (spacing = grouping), Similarity (same function = same look), Common Region (boundaries group), Uniform Connectedness (lines link), Von Restorff (different = remembered), Prägnanz (simplify), Serial Position (key items first/last).

**Making Experiences Stick:** Peak-End Rule (invest in endings), Zeigarnik (show incomplete), Jakob's Law (use familiar patterns), Aesthetic-Usability (polish = trust).

5 agents use: Arc (screen planning) → Dev (build patterns) → Vi (magic moment) → Pol (layout craft) → Crit (HEART psychology)

---

## Apple HIG — iOS/SwiftUI (when stack includes iOS)

`references/hig-ios.md`. Only loaded for iOS/SwiftUI projects.

**Navigation:** Tab bar (max 5, 49pt), NavigationStack (push/pop, large titles), sheets (half/full, swipe dismiss). Don't mix at the same level.

**Layout:** Safe areas always respected. Status bar 59pt (Dynamic Island), nav bar 44pt, tab bar 49pt, home indicator 34pt. Margins 16pt iPhone, 20pt Pro Max.

**Typography:** Dynamic Type scale — Large Title 34pt, Title 28pt, Body 17pt, Caption 12pt. Always use `.font(.body)`, never hardcode sizes.

**Colors:** Semantic system colors (`.background`, `.primary`, `.secondary`) — auto dark mode. One tint color for the app. 4.5:1 contrast ratio.

**Touch:** 44×44pt minimum. 8pt between targets. Never disable swipe-back. Use system haptics.

**Motion:** Spring animations (response: 0.35, damping: 0.85), not CSS easing. Under 0.4s. `matchedGeometryEffect` for hero transitions.

**Components:** System first (`List`, `Form`, `NavigationStack`, `TabView`, `.sheet`, `.alert`, `.searchable`). SF Symbols for icons.

---

## Disagreements

1. State what the previous agent decided
2. State why you disagree
3. Offer the alternative
4. Minor → /team decides, explains in one sentence
5. Significant → /team stops, asks you
6. Priority tie → RICE score wins, show the math

---

## TDD (Test-Driven Development)

Dev's default for new functions, bug fixes, and behavior changes:

```
RED:    Write failing test → run → verify fails for the right reason
GREEN:  Write minimal code → run → verify passes
REFACTOR: Clean up → keep tests green → commit
```

Skip for: config files, pure layout, generated code, or when founder says "skip tests."
Iron rule: wrote code before the test? Delete it. Start with the test.

---

## Verification Rule

Rule #12: Never claim something works without running the command and showing the output.

No "should work." No "looks correct." Run it. Show it. Then claim it.

For changes under 10 lines: manual check with explanation is OK.

---

## Skill Conflict Detection

Rule #13: Team agents own their domains. If external skills overlap, team warns once and overrides.

/team checks at session start for skills that overlap with Vi, Arc, Dev, Bug, Crit, Pol, Test, Cap, or Eye.

---

## Decision Log

Rule #14: Every significant decision gets logged to DECISIONS.md automatically.

Format: date, decision, type (one-way door / two-way door), reasoning, who called it.

One-way door = irreversible, spend more time. Two-way door = reversible, decide fast.

/team reads at session start. Retro reviews weekly.

---

## Scope Guard

Rule #15: No unplanned work without an explicit override.

/team checks tasks against Arc's build order. Not in the plan → backlog, swap, or override.
Arc sets appetite per item. Exceeding appetite → "cut scope or extend?"
Override = one word. Logged to DECISIONS.md.

---

## Post-Launch Loop

Cap writes a measurement plan after every ship (Phase 9):
- Feature, metric, how to measure, when to check, success/failure thresholds
- Filed to DECISIONS.md + CONTEXT.md

Retro enforces: surfaces due measurements every weekly retro. Never drops them.

---

## Context File

CONTEXT.md = institutional memory. Agents write, /team reads at session start.

- Bug writes after fixes (Tech Learnings)
- Arc writes after planning (Tech Learnings)
- Retro writes after retros (Product Learnings, Patterns)
- Cap writes after shipping (Active Experiments)

---

## PMF + North Star + Growth

Vi's brief now includes:
- Item 9: PMF Signal — "Would 40%+ be very disappointed without this?"
- Item 10: Growth Mechanism — viral, content, product-led, or paid
- Item 7: North Star metric — value delivered, not captured

Cap checks growth basics at ship time: sharing, invite flow, SEO, attribution.

---

## Pricing Strategy

Biz expanded from 5 to 9 steps:
1. WTP first (ask before guessing)
2-4. Model, free line, price point
5. Free-tier: sample premium in free
6. Self-serve ceiling (~$10K)
7. Implementation (Stripe)
8. Iterate every 6 months
9. Disagreements

---

## Rules

1. No code before Vi + Arc are done
2. One feature at a time (unless /team dispatches 3+ independent tasks in parallel)
3. Commit before starting the next thing
4. Takes more than a day → break it down
5. Working > pretty
6. Real users > hypothetical users
7. Agents disagree → you decide
8. Every agent references what came before
9. Every feature needs a JTBD + HEART metric before building
10. Always flag cost implications
11. Team orchestrates — external skills supplement, not replace
12. Verify before claiming done — evidence, not hope
13. Team agents own their domains — external skills don't override
14. Log every significant decision to DECISIONS.md — one-way/two-way door
15. No unplanned work without override — scope guard enforces the plan

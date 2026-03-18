# Ship Framework — Cheatsheet

---

## Commands

| Command | When to use |
|---------|-------------|
| `/team [task]` | Default for everything. Routes to the right agents. |
| `/team continue` | Start of day. Picks up from TASKS.md. |
| `/team Health check` | Full strategic review — product fit, tech, UX, business, visual. |
| `/team Take over` | Existing codebase. Assess → audit → strategy → roadmap. |
| `/status` | Quick progress check. |
| `/visionary [idea]` | Validate an idea before building. |
| `/architect [brief]` | Plan how to build something. |
| `/build` | Code one feature. |
| `/browse` | Visual QA — 6 phases: setup, screen map, mobile, interaction walkthrough, bug checklist, report. |
| `/qa` | Test + fix — 8 phases: scope, run tests, explore like a user, document issues, write tests, health score, fix loop, report. |
| `/critic` | HEART review of what was built. |
| `/polish` | Refine design details. |
| `/ship` | Deploy — 7 phases: pre-flight, tests, quality gate, readiness, deploy, post-deploy verify, report. |
| `/money` | Pricing + payments. |
| `/fix [error]` | Debug + explain. |
| `/retro` | Weekly retro — 9 steps: data, metrics, streak, time patterns, hotspots, task health, narrative, trends, update. |

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

8 pattern foundations in `references/animation.md`: reveal on hover, stacking, staggered reveal, shared element transition, dynamic resize, directional navigation, inline expansion, element-to-view expansion.

Deep-dives (loaded only when needed): `animation-css.md` (universal), `animation-framer-motion.md` (React), `animation-performance.md` (universal).

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

## Disagreements

1. State what the previous agent decided
2. State why you disagree
3. Offer the alternative
4. Minor → /team decides, explains in one sentence
5. Significant → /team stops, asks you
6. Priority tie → RICE score wins, show the math

---

## Rules

1. No code before Vi + Arc are done
2. One feature at a time
3. Commit before starting the next thing
4. Takes more than a day → break it down
5. Working > pretty
6. Real users > hypothetical users
7. Agents disagree → you decide
8. Every agent references what came before
9. Every feature needs a JTBD + HEART metric before building
10. Always flag cost implications

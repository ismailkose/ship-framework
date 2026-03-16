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

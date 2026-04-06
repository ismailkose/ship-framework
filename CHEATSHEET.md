# Ship Framework — Cheatsheet

---

## Start Here

```
/ship-team [anything you want]
```

Routes everything. You don't need to remember any other command.

---

## 🔄 Core Loop — every feature

| Command | Who | One-liner |
|---------|-----|-----------|
| `/ship-think` | Vi | Validate the idea first. Six forcing questions that kill bad ideas early. |
| `/ship-plan` | Vi + Pol + Arc | Plan the product, score design readiness, architect the code. Battle-tested plan. |
| `/ship-build` | Dev | Build one feature. Scope enforcement, atomic commits. |
| `/ship-review` | Crit + Pol + Eye + Test | The quality gate. UX, design, visual QA, tests, health score. |
| `/ship-launch` | Cap | Deploy + measurement plan. |

---

## 🎨 Design Tools

| Command | Who | One-liner |
|---------|-----|-----------|
| `/ship-design` | Pol + Eye | Create a design system from scratch — research, propose, preview, document. |
| `/ship-variants` | Pol | Generate 3 theory-backed design options. Compare, rate, learn your taste. |
| `/ship-html` | Dev + Pol | Production-quality responsive HTML prototype. No framework needed. |

---

## 🔧 When You Need It

| Command | Situation |
|---------|-----------|
| `/ship-fix [error]` | Something broke. Paste the error. Checks known patterns first. |
| `/ship-browse` | Visual QA with browser power. `--watch` for headed mode, `--auth` for cookies. |
| `/ship-perf` | Measure Core Web Vitals. Before/after comparison. CI assertions. |
| `/ship-money` | Need pricing strategy. |
| `/ship-retro` | End of week. What actually happened. |

---

## 🛡️ Safety Net — set once

| Command | Protects against |
|---------|-----------------|
| `/ship-careful` | Destructive commands (rm -rf, DROP TABLE, etc.) |
| `/ship-freeze [dir]` | Edits outside a locked directory |
| `/ship-guard` | Both combined |
| `/ship-unfreeze` | Removes the lock |

---

## ⚡ Optional

| Command | What |
|---------|------|
| `/ship-codex` | Second opinion from Codex (review / challenge / consult) |
| `/ship-update` | Update Ship Framework |

---

## /ship-review Flags

The single quality gate. Use flags for partial runs:

| Flag | What runs |
|------|-----------|
| (no flag) | Everything — Crit + Pol + Eye + Test + Adversarial |
| `--product` | Crit only (HEART dimensions, UX) |
| `--design` | Pol only (design craft, anti-slop) |
| `--visual` | Eye only (screenshots, same as /ship-browse) |
| `--test` | Test only (automated + manual, health score) |
| `--report` | Full run, report only, no fixes |
| `--fix` | Full run + auto-fix obvious issues |

---

## /ship-plan Scope Modes

| Flag | Mode |
|------|------|
| `--dream` | Expand scope — find the 10-star version |
| `--focus` | Hold scope — execute exactly what's described |
| `--strip` | Reduce scope — fastest path to validation |

---

## /ship-browse Flags

| Flag | What it does |
|------|-------------|
| `--watch` | Headed mode — visible browser, watch Eye navigate |
| `--auth` | Import cookies from your real browser for authenticated testing |
| `--perf` | Include Core Web Vitals snapshot in visual QA |

---

## Key Files

| File | Purpose | Who writes |
|------|---------|-----------|
| `CLAUDE.md` | Product context, founder profile, stack | You |
| `TASKS.md` | Task backlog | All personas |
| `DECISIONS.md` | Settled decisions | Vi, Arc, you |
| `CONTEXT.md` | Session context | All personas |
| `LEARNINGS.md` | Patterns across sessions | Bug, Crit, Pol, Cap |
| `DESIGN.md` | Design system tokens | Pol (via /ship-design) |
| `PERF-REPORT.md` | Performance benchmarks | Eye (via /ship-perf) |

---

## The Founder Section

In CLAUDE.md — shapes how every persona works with you:

| Field | Controls |
|-------|---------|
| Background | How they pitch explanations |
| Technical comfort | Depth of technical detail |
| Decision style | Options vs. one recommendation |
| Communication | Verbose vs. concise, visual vs. text |
| Taste | Quality bar |
| Context need | How much "why" before "what" |
| Focus awareness | When to flag the detail trap |

---

## Status Messages

Every command ends with a status — written like a teammate, not a log:

| | Status | Sounds like |
|---|--------|------------|
| ✓ | DONE | "Plan is locked. Ready for /ship-build." |
| → | DONE_WITH_CONCERNS | "Works, but loading state feels abrupt." |
| ⏸ | BLOCKED | "Over to you: safe layout or bold bento grid?" |
| ? | NEEDS_CONTEXT | "What should onboarding feel like?" |

---

## Decision Types

| Type | Who decides | Example |
|------|-----------|---------|
| Mechanical | Persona auto-decides | File naming, imports |
| Taste | Surfaces for your input | Color, layout approach |
| User-challenge | Always asks you | Architecture, feature cuts |

---

## Quick Frameworks

**JTBD:** "When I [situation], I want to [motivation], so I can [outcome]."

**HEART:** Happiness · Engagement · Adoption · Retention · Task success

**RICE:** (Reach × Impact × Confidence) / Effort

**Health Score:** Start at 100. Critical: -25, High: -15, Medium: -8, Low: -3. Above 90 = ship it.

**Design Readiness:** 7 dimensions scored 0-10 during /ship-plan. Must average ≥7 to proceed.

---

## Stack

Declare in CLAUDE.md. Commands only load relevant references:

```
Stack: web (Next.js, Tailwind, Vercel)
Stack: ios (SwiftUI, CloudKit)
Stack: android (Jetpack Compose, Material 3)
```

---

## Skills + References

Skills are thin routers (~60-80 lines). They tell personas WHEN to read WHICH reference. References are the brain (200-700+ lines) — deep reasoning, correct/incorrect examples, anti-patterns.

**Framework skills:** ux, web, components, motion, ios, android + safety hooks. Auto-loaded per command.

**References (shared):** ux-principles, typography-color, interaction-design, spatial-design, copy-clarity, hardening-guide, forms-feedback, navigation, layout-responsive, touch-interaction, dark-mode, design-quality, design-research, components, animation (4 files)

**References (web):** react-patterns, web-accessibility, web-performance

**References (ios):** swiftui-core, hig-ios, swift-essentials, 61 framework guides (core: swiftdata, storekit, networking, cloudkit, coreml; gaming: gamekit, spritekit, scenekit, tabletopkit; common: avkit, pdfkit, cryptokit, financekit; specialized: accessorysetupkit, dockkit, sensorkit, browserenginekit, appmigrationkit, cryptotokenkit + 47 others)

**Yours:** Skills in `.claude/skills/your-skills/`. References in `references/`. Wire in CLAUDE.md. Ship auto-detects new skills.

### Priority Gates — What Blocks Shipping

| Priority | What | Threshold |
|----------|------|-----------|
| CRITICAL | Contrast | 4.5:1 ratio |
| CRITICAL | Touch targets | ≥44px / 48dp |
| MANDATORY | Reduced motion | `prefers-reduced-motion` respected |
| HIGH | Mobile-first | No horizontal scroll, consistent spacing |
| HIGH | Typography | 16px min body, 1.5 line-height |
| HIGH | Forms | Visible labels, inline errors, empty states |

---

## Key Rules

0 · Restate request before starting
1 · No code before /ship-plan
2 · One feature at a time
12 · Verify before claiming done — evidence, not hope
16 · 3 attempts then escalate
17 · Screenshots required for UI claims
20 · Finish the last 10% — DONE or BLOCKED
21 · Search before building
22 · Atomic commits
24 · No sycophancy — substance over flattery

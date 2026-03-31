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
| `/ship-plan` | Vi + Arc | Plan the product and architecture. They argue, you get a battle-tested plan. |
| `/ship-build` | Dev | Build one feature. Scope enforcement, atomic commits. |
| `/ship-review` | Crit + Pol + Eye | Review quality. Confidence score 0-100. |
| `/ship-qa` | Test | Run tests, write missing ones, health score. |
| `/ship-launch` | Cap | Deploy + measurement plan. |

---

## 🔧 When You Need It

| Command | Situation |
|---------|-----------|
| `/ship-fix [error]` | Something broke. Paste the error. |
| `/ship-money` | Need pricing strategy. |
| `/ship-browse` | Quick visual QA with screenshots. |
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

**References (shared):** ux-principles, typography-color, interaction-design, copy-clarity, hardening-guide, forms-feedback, navigation, layout-responsive, touch-interaction, dark-mode, design-quality, design-research, components, animation (4 files)

**References (web):** react-patterns, web-accessibility, web-performance

**References (ios):** swiftui-core, hig-ios, swift-essentials, 47 framework guides

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

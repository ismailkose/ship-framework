# Ship Framework

An AI product team for one-person teams. Plan, build, review, and ship — with agents that argue, catch problems, and make your decisions better.

## What It Does

Ship Framework gives you a team of specialist agents that work together on your product:

- **Vi** (Product Strategist) — validates ideas, writes briefs, kills bad features early
- **Arc** (Technical Lead) — plans architecture, scores priorities, designs systems
- **Dev** (Builder) — writes code, enforces scope, makes atomic commits
- **Crit** (Product Reviewer) — reviews quality with HEART framework, catches edge cases
- **Pol** (Design Director) — audits typography, color, spacing, design readiness
- **Eye** (Visual QA) — takes screenshots, verifies design tokens, cross-references reviews
- **Test** (QA Tester) — runs tests, explores like a user, generates health scores
- **Cap** (Release Manager) — deployment checklists, post-deploy verification
- **Bug** (Debugger) — systematic debugging with hypothesis tracking
- **Biz** (Business Brain) — pricing, monetization, cost math

## How It Works

**Auto-routing**: Just describe what you want in natural language. Ship Framework detects intent and engages the right agent automatically.

- "Build me a login screen" → Dev builds it
- "Something broke" → Bug debugs it
- "Is this ready to ship?" → Full review pipeline
- "New idea: weekly digest emails" → Vi validates it
- "Continue" → Picks up next task from your board

**No commands required** — but you can use them directly if you prefer (`/ship-plan`, `/ship-build`, `/ship-review`, etc.).

## Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/ship-think` | Vi | Validate ideas with 6 forcing questions |
| `/ship-plan` | Vi + Arc | Product brief + technical architecture |
| `/ship-build` | Dev | Build one feature at a time |
| `/ship-review` | Crit + Pol + Eye + Test | Full quality gate |
| `/ship-qa` | Test | Run and write tests, health score |
| `/ship-fix` | Bug | Systematic debugging |
| `/ship-launch` | Cap | Deploy checklist + verification |
| `/ship-money` | Biz | Monetization strategy |
| `/ship-design` | Pol | Design system creation |
| `/ship-variants` | Pol | Explore design options |
| `/ship-html` | Dev + Pol | Quick HTML prototyping |
| `/ship-browse` | Eye | Visual QA (screenshot mode) |
| `/ship-perf` | Eye + Test | Performance benchmarking |
| `/ship-retro` | Retro | Weekly retrospective |
| `/ship-team` | Orchestrator | Auto-delegates to the right agents |
| `/ship-codex` | — | Cross-model verification (optional) |
| `/ship-careful` | — | Destructive command warnings |
| `/ship-freeze` | — | Lock edits to a directory |
| `/ship-guard` | — | Both freeze + careful |
| `/ship-unfreeze` | — | Remove directory lock |
| `/ship-update` | — | Update Ship Framework |

## Setup

No setup required. On first use, Ship detects an empty project and asks for:

1. Product name and description
2. Tech stack (iOS / Web / Android / cross-platform)
3. Any existing code to assess

It then creates the project files (CLAUDE.md, TASKS.md, DECISIONS.md, CONTEXT.md, LEARNINGS.md) and you're ready to go.

## Included References

Ship bundles design and development references for three stacks:

- **UX**: principles, typography, color, layout, navigation, forms, dark mode, copy clarity, interaction design, spatial design, touch targets
- **Components**: component catalog, design tokens
- **Motion**: CSS animation, Framer Motion, performance, timing
- **Web**: React patterns, accessibility, performance
- **iOS**: SwiftUI core, HIG, Swift essentials, 60+ framework references (HealthKit, GameKit, CloudKit, etc.)
- **Android**: Jetpack Compose, Material 3
- **Hardening**: error boundaries, edge cases, pre-launch checklist

## Version

Ship Framework v5.0.0

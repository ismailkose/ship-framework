# [Your Product Name]

> You are the founder. The team reports to you. You make final calls.

## The Product

<!-- Describe your product in 2-3 sentences. What does it do? Who is it for? -->

## The Founder

<!-- This tells the team how to work with YOU. Every persona reads this
     and adapts how they communicate, present decisions, and explain work.
     Delete the examples and fill in your own. Keep it short — a few words each. -->

Background: Product designer, design engineer, product manager — or someone who wants to thrive in these areas
Technical comfort: Can read code, review diffs, and tweak. Not architecting from scratch. For unfamiliar technologies, assume I need the concept explained before the implementation.
Decision style: One strong recommendation with clear reasoning. I need to understand how it impacts the product overall — not just the technical side. I'll push back if it doesn't click.
Communication: Short and direct. Show, don't explain. Use visuals, screen maps, and concrete examples over abstract explanations. If I'm not getting it, the explanation is too abstract — try a real scenario.
Taste: Craft-obsessed. I study best-in-class apps and frameworks. If it feels off, it's not shipping — but I know when to skip something and come back later.
Context need: I need to understand the "why" before I commit. Don't just recommend — show me what problem it solves and what happens if we skip it.
Focus awareness: I can get deep into details that are already shippable. When this happens, show me the bigger picture — what's missing, what users will actually hit — and let me decide when to move on.

## Stack

<!-- Your stack. Determines which platform context loads.
     Examples:
       Stack: web (Next.js, Tailwind, Vercel)
       Stack: ios (SwiftUI, CloudKit)
       Stack: android (Jetpack Compose, Material 3, Kotlin)
       Stack: cross-platform (React Native)
     If blank, Ship asks on your first /ship-plan or /ship-build. -->

## Design Principles

- Mobile-first, responsive
- 44px minimum tap targets
- Typography hierarchy clear and consistent (2 fonts max)
- Consistent spacing system — no magic numbers
- Ship ugly but working over pretty but broken

<!-- Add your product's specific design vibe below.
     Have a design system? Add it to references/design-system.md. -->

## Key Files

<!-- List the most important files so the team can orient quickly. -->

## Running Locally

```bash
npm install
npm run dev
```

## Environment Variables

<!-- List required env vars (never put real values here). -->

Copy `.env.example` to `.env.local` and fill in your keys.

---

## Ship Framework

**Rules, personas, and workflows:** `.claude/team-rules.md`
That file is managed by Ship Framework — don't edit it. This file is yours.

**Commands:**

| Command | What it does |
|---|---|
| `/ship-plan` | Vi + Arc + Adversarial argue → battle-tested plan |
| `/ship-build` | Dev builds one feature at a time |
| `/ship-review` | Crit + Pol + Eye + Adversarial → quality verdict |
| `/ship-qa` | Test runs and writes tests, health score |
| `/ship-launch` | Cap's release checklist → deploy |
| `/ship-fix` | Bug debugs systematically |
| `/ship-money` | Biz figures out monetization |
| `/ship-browse` | Visual QA (Eye only, screenshot mode) |
| `/ship-team` | Orchestrator — delegates to the right agents |
| `/ship-retro` | Weekly retrospective with data |
| `/ship-codex` | Cross-model verification via Codex (optional) |
| `/ship-careful` | Destructive command warnings (rm -rf, DROP TABLE, etc.) |
| `/ship-freeze` | Lock edits to a specific directory |
| `/ship-guard` | Both: destructive warnings + directory lock |
| `/ship-unfreeze` | Remove directory edit lock |
| `/ship-update` | Update Ship Framework to latest |

**Skills:** `.claude/skills/ship/` (framework defaults) and `.claude/skills/your-skills/` (yours).
Ship skills load automatically per command. Your skills activate based on wiring below.

<!-- Your skill wiring (plain English):
     Example:
       tailwind-patterns: load during /ship-build and /ship-review when working on frontend files
       content-writing: load during /ship-plan when writing copy
     Ship reads these and activates your skills alongside its defaults. -->

**Custom References:**

<!-- The references/ directory has guides agents read automatically.
     Your references override framework defaults where they conflict.
     Format:
       - references/your-file.md — Which agents read it and when
     See references/README.md for the design system template. -->

**Precedence:** team-rules.md > your skills > framework defaults

> Ship Framework v__VERSION__ — [github.com/ismailkose/ship-framework](https://github.com/ismailkose/ship-framework)

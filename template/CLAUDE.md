# [Your Product Name] — Team Framework

> This file turns Claude Code into a team of opinionated specialists.
> You are the founder. The team reports to you. You make final calls.

---

## The Product

<!-- Describe your product in 2-3 sentences. What does it do? Who is it for? -->

## Who I Am

I'm a one-person team building this product. I handle product vision, design,
business, and decisions — Claude Code handles engineering. The agents below are
my team. They each have a specialty, but I need ALL of them because I wear every
hat.

When I get stuck on something technical, don't just give me the answer — explain
the *why* in one sentence so I learn over time.

**How I think:**
- Show me screens and user flows before database schemas
- Frame technical decisions as tradeoffs: time, cost, quality, flexibility
- When something has a business impact (API costs, hosting, pricing), say so
- I care about how things look AND how they perform AND whether they make money
- I want to ship fast, but not sloppy

---

## Tech Stack

<!-- List your stack. Arc uses this to plan, Dev uses this to code.
     You can list without versions — Arc will use the latest stable.

     Recommended stacks (pick one or write your own):
     • Web App:          Next.js, React, TypeScript, Tailwind CSS, shadcn/ui (Base UI), Supabase, Vercel
     • Mobile App:       React Native (Expo), TypeScript, Supabase, EAS Build
     • iOS App:          SwiftUI, Swift, CloudKit, Xcode
     • Full-Stack Python: FastAPI, Python, PostgreSQL, HTMX, Tailwind CSS, Uvicorn
     • Static Site:      Astro, Tailwind CSS, Markdown, Vercel
-->

-
-
-

## Design Principles

- Mobile-first, responsive
- Animations are subtle, 150-250ms, ease-out timing
- 44px minimum tap targets
- Typography hierarchy clear and consistent (2 fonts max)
- Consistent spacing system — no magic numbers
- Ship ugly but working over pretty but broken

<!-- Add your product's specific design vibe below:
     e.g., "Warm and soft", "Clean and minimal", "Bold and energetic"

     Have a design system with tokens, components, or patterns?
     Add them to references/design-system.md — agents will use your
     rules automatically. See references/README.md for the template. -->

## Key Files

<!-- List the most important files so the team can orient quickly.
     Update this as your project grows. -->

## Running Locally

```bash
npm install
npm run dev
```

## Environment Variables

<!-- List required env vars (never put real values here). -->

Copy `.env.example` to `.env.local` and fill in your keys.

---

## Custom References

<!-- The references/ directory contains guides agents read automatically.
     Framework references (animation, components) are always available.
     Add your own to extend the team's knowledge.

     Your references override where they have opinions. Where they're silent,
     agents fall back to framework defaults. For example: your design system
     defines Button and Card but not Dialog — agents use yours for Button/Card
     and reach for a headless primitive for Dialog, styled to match your tokens.

     Format:
     - references/your-file.md — Which agents read it and when

     Example:
     - references/design-system.md — Arc reads when planning UI. Dev reads
       when building components. Pol reads when auditing design.
     - references/api-patterns.md — Arc reads when planning data layer.
       Dev reads when building API calls.

     See references/README.md for the design system template. -->

---

> **Team rules, agent definitions, and product frameworks** are in `.claude/team-rules.md`.
> That file is managed by Ship Framework and updated automatically — don't edit it.
> This file (CLAUDE.md) is yours to customize. It's never overwritten by updates.

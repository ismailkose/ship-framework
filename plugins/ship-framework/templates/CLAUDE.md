# [Your Product Name]

> You are the founder. The team reports to you. You make final calls.

## The Product

<!-- Describe your product in 2-3 sentences. What does it do? Who is it for? -->

## The Founder

<!-- This tells Ship how to work with YOU. Every stage reads it and adapts
     how it communicates, presents decisions, and explains work.
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
     If blank, Ship detects it from your project files, or asks when it needs it. -->

## Design Principles

- Mobile-first, responsive
- 44pt/px minimum tap targets (48dp on Android)
- Typography hierarchy clear and consistent (2 fonts max)
- Consistent spacing system — no magic numbers
- Ship ugly but working over pretty but broken

<!-- Add your product's specific design vibe below.
     Have a design system already? Tell /shipmate "adopt my design system" — it drafts the registry
     from your code and keeps your names. Token values live in design-model.yaml, not here. -->

## Key Files

<!-- List the most important files so the team can orient quickly. -->

## Running Locally

<!-- How to run and test the app, e.g. `npm install && npm run dev`, or open the Xcode project and
     run the app's scheme. Ship uses these commands to verify its work. -->

## Environment Variables

<!-- Required env vars or secrets and where they live (never put real values here). -->

---

## Ship Framework

<!-- BEGIN:ship-managed:claude-ship-guide -->
**One command:** `/shipmate`. Say what you need in your own words ("the login crashes", "make
onboarding feel warmer", "ship it"), or nothing to continue where you left off. Ship picks the
stage and says so in one line. `/shipmate help` shows example requests, `/shipmate status` where
things stand. Naming a stage steers it (`/shipmate review --full`):

<!-- BEGIN:ship-generated:claude-core-loop-table -->
| Stage | What it does |
|---|---|
| `think` | Clarify consequential uncertainty about the idea — ask only what isn't already known. |
| `design` | Establish or extend a visible, reusable direction — adopt an existing app's system or plant a small seed, proven on a real screen. |
| `plan` | Resolve implementation choices and meaningful risks, then a build order — light or full depth. |
| `build` | Build one feature with the product's system and relevant expertise; verify the outcome with evidence. |
| `review` | Verify the actual outcome with isolated reviewers sized to the change's risk, and record what was reviewed. |
| `launch` | Verify delivery when a release is intended — fresh review, evidence-based gates, deploy, post-deploy check. |
| `retro` | Preserve decisions, corrections, and lessons so the next cycle starts better. |
<!-- END:ship-generated:claude-core-loop-table -->

Also: `fix` (debugging), `variants` (design options; your pick is recorded as taste), `html`
(prototype), `perf` (web speed gate), `money` (pricing), `browse` (visual QA), `qa` (tests only),
`codex` (a second opinion), `careful` · `freeze` · `guard` · `unfreeze` (safety), `update`.

<!-- BEGIN:ship-generated:claude-runtime-note -->
In Codex, the stage names are the same vocabulary; `AGENTS.md` maps them to natural-language requests instead of a slash command.
If a user switches between Claude and Codex mid-project, continue from the same shared context instead of re-planning from scratch.
<!-- END:ship-generated:claude-runtime-note -->

**Core rules:** `${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` — managed by Ship Framework; don't edit it. This file is yours.

**Codex bridge:** `AGENTS.md` when Ship created it. If your AGENTS.md is your own, Ship keeps the
bridge in `.ship/AGENTS.ship.md` and your AGENTS.md needs one line pointing at it. Keep all real
project context in this file.

**References (on demand):** Before writing code, generating a design, or making a technical recommendation, load the references the change actually touches — `python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-knowledge/bin/knowledge.py route --text "<the task>" --changed --record` (add `--domain <ids>` for what the change means) lists them in precedence order (with Ship's corrections for any expert skill you installed yourself) and records the selection for review; `knowledge.py note` records what was read and applied. Your replies stay plain: no reference names or file paths from Ship. Issues a reference would have prevented are flagged `REF_SKIP` in review.

**Design gate (enforced by hook):** UI, motion, and copy edits need the design contract — `PDC.md`, which indexes `DESIGN.md`, `design-model.yaml`, and `design/components.yaml`. Files Ship generated — they carry a "Generated by Ship" header (Theme.swift, tokens.css, previews, `design/COMPONENTS.md`) — are never hand-edited: change `design-model.yaml`, then re-emit. A hand-written theme in a project without a registry is the project's own code.

**Taste:** your design judgments, in your words — `design/taste.yaml` (this product) and `~/.ship/taste.yaml` (across products). Agents query it before UI, copy, or motion work and record your approvals and corrections the moment you make them (`${CLAUDE_PLUGIN_ROOT}/skills/ship-taste/SKILL.md`).
<!-- END:ship-managed:claude-ship-guide -->

**Skills:** `${CLAUDE_PLUGIN_ROOT}/skills/` (Ship's) and `.claude/skills/your-skills/` (yours). Ship's load
when a change needs them. Yours activate by the wiring lines below; `/shipmate` offers to add a line
when it finds a skill of yours that isn't wired yet.

<!-- Your skill wiring, one plain-English line per skill:
       tailwind-patterns: load during build and review when working on frontend files
       content-writing: load during plan when writing copy -->

**Custom References:**

<!-- Framework references live in ${CLAUDE_PLUGIN_ROOT}/skills/*/references/.
     Your custom references go in references/ at project root.
     Your references override framework defaults where they conflict.
     Format:
       - references/your-file.md — Which agents read it and when -->

**Precedence (one order everywhere):** platform requirements & accessibility › your product decisions › your preferences › platform guidance › expert sources (your skills and references included) › Ship defaults › agent guesses. Details: `${CLAUDE_PLUGIN_ROOT}/skills/ship-knowledge/SKILL.md`.

> Ship Framework v2026.10.01 — [github.com/ismailkose/ship-framework](https://github.com/ismailkose/ship-framework)

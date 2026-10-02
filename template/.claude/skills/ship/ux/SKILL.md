---
name: ship-ux
description: |
  UX design intelligence — routing to design references. (ship)
  Use when a UI decision needs UX guidance; knowledge routing names the reference to open.
user-invocable: false
---

# UX — routing and road signs

Open only the reference the decision needs. Every reference is on demand.

## 1. Check the project's registry first

Before any generic guidance, read what the product already decided:
`PDC.md` (index) → `DESIGN.md` (intent, feel words, voice, do/don't) → `design-model.yaml`
(tokens: color, type, spacing, radius, motion, modes) → `design/components.yaml` (what exists)
→ `DECISIONS.md`. **Registry decisions win over everything in these references** except
accessibility requirements. A needed value that isn't in the registry is a registry change
(`/shipmate design --tokens`), never an inline literal. Schema:
`.claude/skills/ship/design/references/design-model-schema.md`.

## 2. Precedence (one order everywhere)

1. Platform requirements & accessibility (WCAG 2.2 AA, App Review, Reduce Motion)
2. Explicit product decisions (registry, `DECISIONS.md`, product taste)
3. Founder preferences
4. Platform design guidance (Apple HIG, Material 3)
5. Expert sources (Practical UI, Laws of UX, GOV.UK, Nielsen, Butterick, Saffer, Albers …)
6. Ship defaults
7. Agent inferences — surface for confirmation, never override 1–6

References tag their rules: **REQ** (1) · **PLATFORM** (4) · **EXPERT** (5) · **SHIP** (6).

## 3. Which reference for which decision

All paths are under `.claude/skills/ship/ux/references/`.

| Deciding… | Open |
|---|---|
| Contrast, target size, focus, keyboard, screen readers, text scaling, drag alternatives, login/auth rules — what's required vs recommended | `accessibility.md` |
| How many options/actions on a screen, primary action, thumb reach, onboarding, feedback weight, inclusion, branding | `ux-principles.md` |
| Type scale, fonts, Dynamic Type / rem, line length, weights, font loading | `typography.md` |
| Palette, token roles, OKLCH / P3, brand-color usage, contrast pairs, CVD, elevation | `color.md` |
| Dark mode values, depth in dark, theme switching, flash prevention | `dark-mode.md` |
| Breakpoints, size classes, spacing scale, density, safe areas, z-index, radius scale | `layout-responsive.md` |
| Interaction states, press feedback, haptics, hover, gestures, swipe actions | `interaction-design.md` |
| Fields, validation, multi-step flows, toasts, empty/loading/disabled states | `forms-feedback.md` |
| Tab bar vs sidebar, back behaviour, deep links, state restoration | `navigation.md` |
| Button labels and order, errors, empty-state text, confirmations, voice, AI copy slop | `copy-clarity.md` |
| First run and empty states, paywalls and pricing pages, cancel flows, reminders and streaks, reviews and counts, long waits, honest persuasion | `psychology.md` |
| Competitor research, feel words, direction, where decisions are written, adopting an existing app | `design-research.md` |
| Review taste: first impression, AI slop patterns, consistency, coherence | `design-quality.md` |
| Components, layers, variants, button weights | `.claude/skills/ship/components/` |
| Animation timing, easing, springs, Reduce Motion values | `.claude/skills/ship/motion/` (authority: motion) |
| Web implementation (ARIA, React forms, CSS) · iOS implementation (SwiftUI, HIG) | web skill · ios skill |

## 4. Blocks shipping

| Gate | Rule | Reference |
|---|---|---|
| REQ contrast | Text 4.5:1 (large 3:1); UI parts and focus rings 3:1 — every mode and state | `accessibility.md` §1, §4 |
| REQ operable | Keyboard reachable, visible focus, not obscured; actions on release | `accessibility.md` §1 |
| REQ targets | ≥ 24×24 CSS px (AA); Ship: 44 pt iOS / 48 dp Android / 44 px touch web | `accessibility.md` §1, §3 |
| REQ alternatives | Every gesture and drag has a single-pointer, non-drag alternative | `interaction-design.md` §5 |
| REQ text scaling | Dynamic Type / font scale / 200% zoom and 320 px reflow without loss | `typography.md` §1, `layout-responsive.md` §5 |
| REQ forms | Visible labels, autocomplete, errors in text next to the field, paste allowed | `forms-feedback.md` §1–2 |
| REQ motion | Reduce Motion / `prefers-reduced-motion` honoured | motion skill |
| Registry | No literal colors/sizes/spacing; reusable components registered | `color.md` §2, components skill |
| SHIP | One primary action per view; all component states designed; empty/loading/error screens exist; both themes pass | `ux-principles.md` §1, `interaction-design.md` §1, `forms-feedback.md` §4, `dark-mode.md` |

## 5. By phase

**Plan (/shipmate plan, /shipmate — Vi, Arc, Pol):** `design-research.md` (direction, registry
landing spots) → `ux-principles.md` §1 (screen content) → `navigation.md` §1 (pattern) →
`layout-responsive.md` §1 (size classes, widths). New or changed tokens go to the registry
before build starts.

**Build (/shipmate build — Dev):** registry check first (§1). Then per element: states
(`interaction-design.md` §1), fields (`forms-feedback.md`), type and color via tokens only,
dark mode values from `semantic_dark`, words (`copy-clarity.md` §2). Name the references you
opened in the handoff.

**Review (/shipmate review — Pol, Eye, Crit):** `design-quality.md` flow: first impression → pre-pass
tools → slop scan → consistency → coherence. Web pre-pass:
the web scan (`python3 .claude/skills/ship/web/bin/scan.py <files|URL>`, exit 2 = findings) and the web
interface checklist, fetched at review time; both run as the web skill describes.
Accessibility REQ rows are blockers regardless of taste.

**QA (/shipmate review --test — Test):** the QA checklists at the end of `accessibility.md`,
`forms-feedback.md`, `navigation.md`, `layout-responsive.md`, `dark-mode.md`,
`interaction-design.md`. Minimums: keyboard walk, screen-reader pass on the primary flow,
largest text size, 320 px, both themes, rapid-tap, empty/error states.

## 6. Road signs (apply without opening a reference)

- One filled primary action per view; the action colour only on interactive things (a field colour
  may own regions on a persuading surface).
- Every interactive element: default, pressed, focus, disabled (+ loading/error where it can happen).
- Show a pressed state on touch-down; never wait on the network to acknowledge input.
- Labels above fields, hints before the input, errors below it; never disable submit to mean "incomplete".
- Wrap, don't truncate; tabular figures for changing numbers.
- Spacing and radius from the registry scale; inside-group gaps tighter than between-group gaps.
- System back and edge gestures always work; state survives Back.
- Specific verbs on buttons; errors say what happened and how to fix it; no "we" in system messages.
- The word people scan for comes first: in headings, labels, links, buttons and messages.
- Help people decide, never trick them: no fake urgency or scarcity, decoy tiers, guilt-trip
  declines, hidden costs or hard cancels; what's close to the line is the founder's call, run
  through the balance check (`psychology.md` §7).
- Test light + dark, largest text, smallest width before calling UI done.

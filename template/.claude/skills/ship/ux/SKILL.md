---
name: ship-ux
description: |
  UX design intelligence — routing to design references. (ship)
  Loaded by /ship-plan, /ship-build, /ship-review, /ship-qa, /ship-team.
---

# UX Design Intelligence Skill

This skill routes personas to the right design knowledge at the right time. The deep rules, reasoning, and examples live in reference files.

**Reference files:**
- `references/shared/ux-principles.md` — Cognitive psychology: Hick's, Miller's, Fitts's, Peak-End, Goal Gradient, Doherty, HEART framework
- `references/shared/typography-color.md` — Type scale, font pairing, semantic color tokens, contrast, dark mode color strategy
- `references/shared/forms-feedback.md` — Input patterns, validation, error handling, empty states, toasts, confirmations, progressive disclosure
- `references/shared/navigation.md` — Nav architecture, bottom nav, back behavior, deep linking, adaptive patterns, URL state
- `references/shared/layout-responsive.md` — Mobile-first, breakpoints, spacing scale, viewport, z-index, safe areas
- `references/shared/touch-interaction.md` — Tap targets, gesture handling, press feedback, haptics, safe areas, platform gestures
- `references/shared/dark-mode.md` — Theming strategy, semantic tokens, elevation, contrast in both themes, system preference
- `references/shared/design-quality.md` — First impression assessment, AI slop detection, cross-page consistency, visual coherence
- `references/shared/design-research.md` — Competitive design research, design direction decisions, design system creation (DESIGN.md)

## Priority Enforcement — What Blocks Shipping

| Priority | Domain | Gate | Reference |
|---|---|---|---|
| CRITICAL | Accessibility | Contrast 4.5:1, keyboard nav, aria-labels, semantic HTML | ux-principles.md Section 5 |
| CRITICAL | Touch | ≥44pt/48dp/44px targets, 8px spacing, press feedback <100ms | touch-interaction.md Section 1 |
| MANDATORY | Reduced Motion | `prefers-reduced-motion` respected — see motion skill | motion SKILL.md |
| HIGH | Layout | Mobile-first, consistent spacing, no horizontal scroll | layout-responsive.md |
| HIGH | Typography | 16px min body, 1.5 line-height, semantic tokens | typography-color.md Section 1 |
| HIGH | Forms | Visible labels, inline errors, empty states, destructive confirmation | forms-feedback.md |
| HIGH | Navigation | Predictable back, deep linking, ≤5 bottom nav | navigation.md |
| HIGH | Style | Consistent style, one primary CTA/screen, state clarity | typography-color.md Section 3 |
| MEDIUM | Dark Mode | Semantic tokens, test both themes, desaturate for dark | dark-mode.md |
| LOW | Charts | Accessible colors, legends, responsive, empty states | ux-principles.md Section 6 |

## For Planning (/ship-plan, /ship-team)

When Vi defines the product or Arc plans screens:

1. **Design research** — read `references/shared/design-research.md` Sections 1-2 for competitive analysis and design direction decisions.
2. **Design system** — read `references/shared/design-research.md` Section 3 for creating DESIGN.md (color tokens, typography, spacing, component rules).
3. **Cognitive principles** — read `references/shared/ux-principles.md` Sections 1-4 for decision architecture, information display, interaction patterns, experience shaping.
4. **Navigation architecture** — read `references/shared/navigation.md` Section 1 for pattern selection based on screen count and hierarchy depth.
5. **Layout strategy** — read `references/shared/layout-responsive.md` Section 1 for mobile-first planning and breakpoint decisions.
6. **Typography & color** — read `references/shared/typography-color.md` Sections 1-2 for type scale and color palette decisions.

## For Building (/ship-build)

When Dev builds UI:

1. **Touch & interaction** — read `references/shared/touch-interaction.md` for tap targets, press feedback, gesture handling on every interactive element.
2. **Forms** — read `references/shared/forms-feedback.md` for input implementation, validation, error states, empty states.
3. **Layout** — read `references/shared/layout-responsive.md` Section 2 for spacing, viewport handling, responsive patterns.
4. **Typography** — read `references/shared/typography-color.md` Section 1 for type scale implementation, token compliance.
5. **Dark mode** — read `references/shared/dark-mode.md` for theme implementation. Use semantic tokens only.

## For Review (/ship-review)

When Crit, Pol, or Eye review:

1. **First impression** — read `references/shared/design-quality.md` Section 1. Step back, feel the whole before auditing parts.
2. **AI slop check** — read `references/shared/design-quality.md` Section 2. Flag generic heroes, card sameness, decoration over meaning, spacing off-grid.
3. **Cross-page consistency** — read `references/shared/design-quality.md` Section 3. Same component = same everywhere.
4. **Visual coherence** — read `references/shared/design-quality.md` Section 4. Does everything feel like one product?
5. **Accessibility audit** — read `references/shared/ux-principles.md` Section 5 for full accessibility checklist.
6. **Touch audit** — read `references/shared/touch-interaction.md` Section 1 for tap target and interaction verification.
7. **Typography & color audit** — read `references/shared/typography-color.md` Section 3 for token compliance, contrast, hierarchy.
8. **Navigation audit** — read `references/shared/navigation.md` Section 2 for consistency, state preservation, deep link verification.
9. **Form audit** — read `references/shared/forms-feedback.md` Section 2 for label visibility, error placement, empty states.

## For QA (/ship-qa)

When Test verifies:

1. **Mobile test** — test at 375px width minimum. Read `references/shared/layout-responsive.md` Section 3.
2. **Touch test** — tap targets on mobile viewport, rapid interaction. Read `references/shared/touch-interaction.md` Section 2.
3. **Accessibility test** — keyboard nav through entire flow, screen reader on primary actions, contrast check. Read `references/shared/ux-principles.md` Section 5.
4. **Form test** — submit empty required fields, invalid data, rapid submit, paste into all fields. Read `references/shared/forms-feedback.md` Section 3.
5. **Dark mode test** — every screen in both themes, contrast passes in both. Read `references/shared/dark-mode.md` Section 2.
6. **Edge cases** — empty states, error states, loading states, long text overflow.

## See Also

- **Web skill** — web-specific accessibility, React form implementation, web performance, dark mode CSS
- **Motion skill** — animation timing, motion budget, reduced motion implementation
- **Components skill** — three-layer model, composition patterns, design tokens

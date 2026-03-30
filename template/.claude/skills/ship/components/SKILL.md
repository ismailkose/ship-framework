---
name: ship-components
description: |
  Component architecture routing — three-layer model, composition, tokens. (ship)
  Loaded by /ship-build, /ship-review, /ship-team.
---

# Component Architecture Skill

This skill routes personas to component architecture knowledge. The three-layer model, composition patterns, and design token rules live in the reference file.

**Reference files:**
- `references/shared/components.md` — Three-layer model (Section 1-2), primitives + shadcn setup, 46 component catalog, theming, CVA, forms, review checklist
- `references/web/react-patterns.md` — React composition patterns (Section 3), React 19 APIs (Section 5)

## The Three Layers (always enforce)

1. **Layer 1: Primitives** — Headless behavioral components. Accessibility, keyboard nav, ARIA, focus. Zero styling.
2. **Layer 2: Styled** — Primitives + design tokens. Colors, typography, spacing, variants.
3. **Layer 3: Product** — Styled components + business logic composed into features.

**The rule:** Check Layer 1 → 2 → 3 in order. Never rebuild what a lower layer handles.

| Stack | Layer 1 (Primitives) | Layer 2 (Styled) |
|---|---|---|
| Web (React) | Radix UI, React Aria, Headless UI | shadcn/ui, Ark UI |
| iOS | SwiftUI built-in views + modifiers | Custom design system |
| Android | Material 3 Compose | Custom theme overlay |

## Composition Gates — What Blocks Shipping

| Gate | Signal | Action |
|---|---|---|
| Boolean accumulation | 3+ boolean props on one component | Refactor to variants or compound pattern |
| Prop drilling | Same prop passed through 3+ levels | Lift to context provider |
| Layer violation | Manually implementing focus trap, keyboard nav, ARIA | Use Layer 1 primitive |
| Token violation | Hardcoded hex, px, or font values in components | Use semantic tokens |
| Duplicate component | Two different components for the same UI pattern | Consolidate |

## For Planning (/ship-plan, /ship-team)

When Arc plans component architecture:

1. **Inventory check** — list existing components before speccing new ones.
2. **Primitive selection** — read `references/shared/components.md` Section 2 for stack-specific primitives.
3. **Composition plan** — for complex interactive components, plan compound pattern upfront. Read `references/web/react-patterns.md` Section 3.
4. **Token definition** — if no design tokens exist, define them before building UI.

## For Building (/ship-build)

When Dev builds UI:

1. **Before ANY component** — does the design system have it? Does a primitive handle it? Read `references/shared/components.md` Section 1-2.
2. **Token compliance** — all values reference tokens. No hardcoded colors, sizes, spacing.
3. **Composition** — tabs, panels, toggle groups, internal navigation = compound pattern. Read `references/web/react-patterns.md` Section 3.
4. **Prop check** — adding a 3rd boolean prop? Stop and refactor.

## For Review (/ship-review)

When reviewing components:

1. **Layer audit** — read `references/shared/components.md` Section 1. Anyone rebuilding primitives?
2. **Token audit** — any hardcoded values? Flag them.
3. **Composition audit** — read `references/web/react-patterns.md` Section 4. Boolean accumulation? Prop drilling? Missing compound pattern?
4. **Consistency** — similar patterns should use same components.

## See Also

- **UX skill** — cognitive principles for component decisions, accessibility requirements
- **Web skill** — React 19 APIs, web-specific patterns, anti-patterns checklist
- **Motion skill** — motion tokens, animation patterns for component transitions

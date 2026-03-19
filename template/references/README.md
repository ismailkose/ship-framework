# References

This directory contains reference files that agents read automatically when
they're relevant. You don't need to invoke them — the slash commands know
when to load them.

## What Ships with the Framework

- `animation.md` — Motion budget, build rules, 8 pattern foundations
- `animation-css.md` — CSS transforms, transitions, keyframes (universal)
- `animation-framer-motion.md` — Framer Motion API (React only)
- `animation-performance.md` — 60fps optimization, reduced motion testing
- `components.md` — Headless component architecture, three-layer model
- `ux-principles.md` — 20 UX principles with incorrect/correct code examples

## Adding Your Own

Create any `.md` file in this directory and add a routing note in your
CLAUDE.md under the Custom References section. The routing note tells agents
when to read it.

Example — you've documented your design system:

```markdown
## Custom References

- `references/design-system.md` — Arc reads when planning UI. Dev reads when
  building components. Pol reads when auditing design. Eye reads when checking
  visuals.
```

**The layering rule:** Framework references are always loaded. Your custom
references override where they have opinions. Where your references are silent,
agents fall back to framework defaults.

For example: your design system defines Button and Card but not Dialog. Agents
use your Button and Card. For Dialog, they use a headless primitive from
`components.md` and style it to match your existing tokens.

## Design System Template

If you have a design system, create `references/design-system.md` with
the sections below. Fill in what you have, delete what you don't — agents
work with whatever level of detail you provide.

```markdown
# Design System

## Color Tokens
<!-- token name → value → where it's used -->

## Typography
<!-- font families, sizes, weights, line heights -->

## Spacing Scale
<!-- your spacing system: 4px base, 8px, 16px, etc. -->

## Border Radius
<!-- radius values and where each is used -->

## Shadows
<!-- elevation levels and their shadow values -->

## Component Rules
<!-- which component library, naming conventions, any overrides -->

## Patterns
<!-- common UI patterns agents should reuse: cards, forms, lists, nav -->

## Do / Don't
<!-- explicit rules: "always use X for Y", "never use Z" -->
```

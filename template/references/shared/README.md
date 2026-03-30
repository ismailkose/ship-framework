# References

This directory contains reference files that agents read automatically when
they're relevant. You don't need to invoke them — the slash commands know
when to load them.

## What Ships with the Framework

### Shared (all platforms)

- `ux-principles.md` — 20 UX principles with incorrect/correct code examples. Cognitive psychology: Hick's, Miller's, Fitts's, Peak-End, Goal Gradient, Doherty
- `typography-color.md` — Type scale reasoning, font pairing logic, semantic color tokens, contrast, dark mode color strategy, style selection
- `forms-feedback.md` — Form architecture, validation patterns, error handling, empty states, toasts, confirmations, loading states
- `navigation.md` — Nav architecture decisions, pattern selection, back behavior, deep linking, adaptive patterns, URL state
- `layout-responsive.md` — Mobile-first philosophy, breakpoints, spacing scale, viewport handling, z-index management
- `touch-interaction.md` — Tap target reasoning, gesture handling, press feedback, haptics, safe areas, platform gestures
- `dark-mode.md` — Theme strategy, semantic tokens, elevation, contrast in both themes, platform implementation
- `animation.md` — Motion budget, build rules, 8 pattern foundations
- `animation-css.md` — CSS transforms, transitions, keyframes, View Transitions API (universal)
- `animation-framer-motion.md` — Framer Motion API (React only)
- `animation-performance.md` — 60fps optimization, reduced motion testing
- `components.md` — Three-layer component model, Base UI + shadcn setup, 46 component catalog, theming, CVA, forms, review checklist

### Web (React/Next.js)

- `web/react-patterns.md` — Server vs Client Components, data fetching, re-render optimization, composition patterns, hydration safety
- `web/web-accessibility.md` — Semantic HTML, ARIA, focus management, screen reader patterns, skip links, form accessibility
- `web/web-performance.md` — Core Web Vitals, image optimization, font loading, virtualization, caching, anti-patterns

### iOS (SwiftUI)

- `ios/swiftui-core.md` — SwiftUI navigation, concurrency, Liquid Glass, animation, gestures, layout, architecture, No-Hack APIs
- `ios/hig-ios.md` — Human Interface Guidelines: navigation, color, components, lifecycle, design checklists
- `ios/swift-essentials.md` — Swift language features, Codable, Swift Testing
- `ios/frameworks/[name].md` — Per-framework guides (HealthKit, StoreKit, CloudKit, etc.)

## How Skills and References Work Together

**Skills** are thin routing tables (~60-80 lines). They tell each persona WHEN to read WHICH reference, for WHICH command.

**References** are the brain (200-500 lines). They teach Claude HOW to think about a domain — with reasoning, correct vs incorrect examples, and anti-patterns.

Example flow:
1. You run `/ship-build`
2. Dev persona activates and loads `ship/ux/SKILL.md`
3. Skill says: "read `references/shared/forms-feedback.md` Section 1 for form implementation"
4. Dev reads the reference and applies the reasoning to the specific form being built

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

## Design System Template

If you have a design system, create `references/design-system.md`. See
`references/shared/design-research.md` Section 3 for the full template
with inline comments explaining each decision. The short version:

- Brand Personality (3-5 adjectives)
- Color Tokens (primary, surface, error, success + on-variants)
- Typography (families, scale, weights)
- Spacing Scale (base unit, values)
- Border Radius, Shadows, Component Rules
- Do / Don't (explicit rules for this product)

Fill in what you have, delete what you don't — agents work with whatever
level of detail you provide.

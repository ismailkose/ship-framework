---
name: ship-web
description: |
  Web platform skill. React/Next.js routing to web references. (ship)
  Only loaded when Stack is web. Loaded by all commands.
---

# Web Platform Skill

This skill routes personas to web-specific knowledge. Only loaded when `Stack: web` is declared in CLAUDE.md.

**Reference files:**
- `references/web/react-patterns.md` — React/Next.js patterns: Server Components, data fetching, re-render optimization, bundle size, composition, React 19 APIs
- `references/web/web-accessibility.md` — Semantic HTML, ARIA, focus management, screen reader patterns, skip links, form accessibility
- `references/web/web-performance.md` — Core Web Vitals, image optimization, font loading, virtualization, lazy loading, caching, anti-patterns

## Priority Enforcement — What Blocks Shipping

| Priority | Domain | Gate | Reference |
|---|---|---|---|
| CRITICAL | Accessibility | Semantic HTML, keyboard nav, aria-labels, no `<div onClick>` | web-accessibility.md Section 1 |
| CRITICAL | Performance | LCP < 2.5s, CLS < 0.1, no `transition: all` | web-performance.md Section 1 |
| HIGH | React patterns | Server Components by default, no unnecessary `'use client'` | react-patterns.md Section 1 |
| HIGH | Composition | No boolean prop proliferation, compound pattern for complex components | react-patterns.md Section 3 |
| HIGH | Forms | `autocomplete` on all inputs, never block paste, inline errors | shared/forms-feedback.md + web-forms below |
| MEDIUM | Dark mode | `color-scheme: dark`, no theme flash, cookie-based override | shared/dark-mode.md Section 2 |
| MEDIUM | i18n | `Intl.DateTimeFormat`, `Intl.NumberFormat`, no hardcoded formats | web-performance.md Section 3 |
| MEDIUM | Hydration | No SSR/client mismatch, guard browser APIs in `useEffect` | react-patterns.md Section 5 |

## For Planning (/ship-plan, /ship-team)

When Arc plans web features:

1. **React architecture** — read `references/web/react-patterns.md` Section 1 for Server vs Client Components, data fetching strategy, rendering approach.
2. **Component architecture** — read `references/web/react-patterns.md` Section 3 for composition patterns. Use compound pattern for complex components.
3. **Performance budget** — read `references/web/web-performance.md` Section 1 for Core Web Vitals targets and initial performance decisions.

## For Building (/ship-build)

When Dev builds web features:

1. **React patterns** — read `references/web/react-patterns.md` Sections 1-4 for Server Components, data fetching, re-renders, bundle optimization.
2. **Accessibility** — read `references/web/web-accessibility.md` for semantic elements, ARIA, focus management on every component.
3. **Performance** — read `references/web/web-performance.md` Section 2 for image optimization, font loading, virtualization, lazy loading.
4. **Forms** — read `references/shared/forms-feedback.md` + web-specific: `autocomplete`, `inputmode`, `spellCheck`, `defaultValue` over `value`, `beforeunload` for dirty forms.
5. **Dark mode** — read `references/shared/dark-mode.md` Section 2 for `color-scheme: dark`, CSS custom properties, flash prevention, cookie storage.

## For Review (/ship-review)

When Crit or Pol review web code:

1. **Anti-patterns scan** — read `references/web/web-performance.md` Section 4 for the full anti-patterns checklist. Flag immediately: `<div onClick>`, `transition: all`, `outline: none` without replacement, `<img>` without dimensions, inputs without labels, `forwardRef` in React 19+.
2. **React review** — read `references/web/react-patterns.md` Section 4 for: unnecessary `'use client'`, boolean prop accumulation, prop drilling, missing Suspense boundaries.
3. **Accessibility review** — read `references/web/web-accessibility.md` Section 2 for: semantic elements, keyboard navigation, focus order, screen reader labels.
4. **Performance review** — read `references/web/web-performance.md` Section 2 for: un-virtualized long lists, missing preconnect, unoptimized images, layout-triggering animations.

## For QA (/ship-qa)

When Test verifies web builds:

1. **Lighthouse** — run Lighthouse. Read `references/web/web-performance.md` Section 3 for score interpretation and targets.
2. **Accessibility** — tab through entire flow, screen reader test, skip link verification. Read `references/web/web-accessibility.md` Section 3.
3. **Hydration** — check console for hydration warnings. Read `references/web/react-patterns.md` Section 5.
4. **Cross-browser** — verify in Chrome, Safari, Firefox at minimum.

## Web-Specific Form Rules

These extend `references/shared/forms-feedback.md` for web:

- `autocomplete` attribute on all inputs — browsers and password managers depend on it
- `inputmode` for mobile keyboard control — `numeric`, `decimal`, `email`
- `type` attribute — semantic types trigger correct validation and keyboard
- `spellCheck={false}` on email, code, username fields
- Never `onPaste` with `preventDefault()` — blocks password managers
- `defaultValue` over `value` for submit-only forms — better performance
- `beforeunload` listener for dirty form state
- Placeholder format: end with `…`, show example pattern

## Web-Specific Content Rules

- Active voice: "Install the CLI" not "The CLI will be installed"
- Title Case on headings and buttons (Chicago style)
- Numerals for counts: "8 deployments" not "eight deployments"
- Specific button labels: "Save API Key" not "Continue"
- Error messages include the fix: "Email is required" not "Invalid input"
- Loading text ends with `…`: "Saving…", "Loading…"
- Use `…` (ellipsis character) not three periods
- Curly quotes `"` `"` not straight quotes

## See Also

- **UX skill** — core accessibility, cognitive principles, touch/interaction, forms, navigation, typography, dark mode
- **Components skill** — three-layer model, compound components, design tokens
- **Motion skill** — animation timing, reduced motion, web-specific: no `transition: all`, `transform-origin`

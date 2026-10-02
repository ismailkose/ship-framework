<!-- ship-reference
id: web-react
kind: mixed
sources: Next 16.3.7 bundled docs, App Router › Getting started › Error handling (unhandled errors in startTransition reach the nearest error boundary; 2026-09-29); vercel-agent-skills@063bee9 (skills/react-best-practices, skills/composition-patterns: reviewed 2026-09-28, not suggested, nothing copied); https://react.dev/blog/2026/09/09/react-19-3 (2026-09-23); https://nextjs.org/docs/app/api-reference/config/next-config-js/optimizePackageImports (the packages optimized by default, as in Next 16.2's config; 2026-09-28); https://react.dev/versions (2026-09-23); https://nextjs.org/blog/next-16 (2026-09-23); https://nextjs.org/blog/next-16-3 (2026-09-23); https://nextjs.org/docs/app/guides/ai-agents (2026-09-23); https://nextjs.org/docs/app/api-reference/components/image (2026-09-23)
reviewed: 2026-09-29
-->

# React & Next.js — Ship contracts and current-version facts

> **Agent routing:** Arc → Sections 1–3 · Dev → 1–5 · Crit → 4 · Pol → 3 · Test → 5
>
> **Truth order:** the installed framework's docs (`node_modules/next/dist/docs/`, Next 16.2+)
> beat this file; this file beats training data. General React/Next performance rules live in
> the `vercel-react-best-practices` and `vercel-composition-patterns` skills (see web/SKILL.md
> for install); this file keeps only road signs, post-2025 facts, and Ship's own contracts.

**Version baseline (checked 2026-09-23):** React 19.3 (2026-09-09) · React Compiler 1.0
(2025-10-07) · Next.js 16.3 (2026-08-03). If `package.json` says otherwise, the installed docs
win — check before applying a version-specific line below.

---

## Section 1: Server vs Client

- Server Components are the default. Add `'use client'` only for state, effects, event
  handlers, or browser APIs — and on the smallest leaf that needs it, not its page or layout.
- Props crossing into a Client Component must be serializable. Pass Server Components *into*
  a client wrapper as `children` instead of importing them there.
- Modules holding secrets or DB access start with `import 'server-only'`.
- **Server Actions are public POST endpoints.** Every `'use server'` function validates its
  input and checks authentication *and* authorization itself. `proxy.ts` (or legacy
  middleware) is not an auth boundary.
- **Browser-only UI:** React 19.3 adds `browser()` in `react-dom`: calling `use(browser())`
  in a component skips it during SSR and shows the nearest `<Suspense>` fallback in the HTML.
  Older React: render after mount, or `next/dynamic(..., { ssr: false })` — allowed only inside
  a Client Component.
- **Streaming:** slow data sits under `<Suspense>` with a skeleton that holds the final
  layout's size (no CLS). With Cache Components on, uncached data outside `<Suspense>` is a
  build error offering three fixes — `[stream]` Suspense, `[cache]` `'use cache'`, `[block]`
  `export const instant = false`. Ship default: stream; cache only data shared across users.

## Section 2: Data, caching, mutations (Next.js 16)

- **Async request APIs** (sync access removed in 16): `await params`, `await searchParams`,
  `await cookies()`, `await headers()`, `await draftMode()`.
- **Caching is opt-in.** `cacheComponents: true` in `next.config.ts` enables `'use cache'` on
  pages, components and functions, with `cacheLife(...)` and `cacheTag(...)`. `fetch` is not
  cached by default (since 15). `experimental.ppr` and `experimental.dynamicIO` are gone.
  Before mixing `unstable_cache` or route-segment `revalidate` with Cache Components, read
  the bundled caching guide.
- **Invalidation after a mutation:**
  - `updateTag(tag)` — Server Actions only; read-your-writes (forms, settings).
  - `revalidateTag(tag, 'max')` — stale-while-revalidate; the one-argument form is deprecated.
  - `refresh()` — Server Actions only; re-renders uncached data, leaves caches alone.
- **`proxy.ts`** (exported function `proxy`, Node runtime) replaces `middleware.ts`, which is
  deprecated and kept only for Edge.
- **Removed in 16:** `next lint` (run ESLint or Biome directly), AMP, `serverRuntimeConfig` /
  `publicRuntimeConfig`. Turbopack is the default bundler (`--webpack` opts out).
- **`next/image`:** `priority` is deprecated → `preload`; for the LCP image prefer
  `loading="eager"` or `fetchPriority="high"`. Local `src` with a query string needs
  `images.localPatterns`.
- **Independent fetches start together** (`Promise.all`, or start early and await late).
  The `async-*` rules in `vercel-react-best-practices` cover the rest.
- **Mutations in forms:** `<form action={serverAction}>`, `useActionState` for the result and
  field errors, `useFormStatus` for the pending state inside the submit button,
  `useOptimistic` for optimistic UI (it reverts when the action settles).
- **An action call can still fail on the way** (a dropped connection, a server that no longer has
  that action): inside `startTransition` the rejection reaches the nearest error boundary, which
  replaces the page and loses what was typed. Catch around calls made from handlers and
  transitions, show the error where the action was, keep the input.
- **Memoization:** if `reactCompiler: true` is set (Babel plugin
  `babel-plugin-react-compiler`; 16.3 adds `experimental.turbopackRustReactCompiler`), new code
  relies on the compiler; `useMemo`/`useCallback` stay as an escape hatch where you need control
  (e.g. a value used as an effect dependency). Leave existing memoization in place unless you
  test its removal — removing it can change the compiled output. Check the file is actually
  compiled (compiler config, `"use no memo"`). Without the compiler, add memoization only after
  measuring a slow render.
- **React 19 idioms:** `ref` is a regular prop (no `forwardRef` in new code); render
  `<Context value={…}>` as the provider (19.3 also lets Server Components render it directly
  from a `'use client'` module); in Next, page metadata goes through `metadata` /
  `generateMetadata`.
- **React 19.2–19.3 additions:** `<Activity mode="hidden">` keeps hidden UI's state;
  `useEffectEvent` for non-reactive logic read inside effects; Fragment refs (19.3);
  `<ViewTransition>` and `addTransitionType` are stable in 19.3 — whether and how anything
  animates is the motion skill's call.
- **Next 16.3 opt-ins worth knowing:** `catchError` from `next/error` (error boundary with
  `retry()` that re-renders Server Components, and doesn't swallow `notFound`/`redirect`);
  `partialPrefetching: true` with Cache Components; `instant()` from `@next/playwright` to
  test what a navigation shows immediately; `next/root-params`; `experimental.useOffline` +
  `useOffline()` from `next/offline`.

## Section 3: Ship contracts — tokens, registry, composition

**Tokens (product decision, precedence line 2).**
- `design-model.yaml` is the source of truth. The web theme — CSS custom properties, or a
  Tailwind v4 `@theme` block — is generated from it by the design tooling; the project's emit
  command is recorded in `PDC.md`.
- Never hand-edit the generated theme file. Change `design-model.yaml`, then re-emit.
- Use semantic token names (`var(--color-surface)`, `bg-surface`), never a raw hex, px or ms
  value where a token exists. A value the model lacks is a design decision: add it to
  `design-model.yaml` first (UI edits already need the design contract, `PDC.md`).
- Light/dark comes from the emitted variables, not per-component `dark:` hex overrides.

**Registered components (product decision).**
- Before creating a component, read `design/components.yaml`. Reuse a registered one, or add
  a variant to it; don't fork a copy into a feature folder.
- A new shared component is registered with its source `file:` (`design_model.py validate`
  rejects entries whose file doesn't exist; use `planned: true` before it's built).

**Composition (expert road signs; detail in `vercel-composition-patterns`).**
- Variants as string unions (`variant="danger"`), not stacked booleans.
- Compound components (`Tabs.List`, `Tabs.Trigger`, `Tabs.Panel`) for tabs, menus, dialogs,
  selects. Children over render props. Shared state lifted into a provider with state +
  actions.
- **Ship default:** build composite widgets on a headless, APG-conformant primitive (Radix,
  React Aria, Base UI, Headless UI) styled with tokens. Don't hand-roll focus management.

## Section 4: Review — flag these

- `'use client'` on a component with no state, effect, handler, or browser API.
- Server Action without input validation or an auth/authorization check.
- A server-only module (secrets, DB, `server-only`) reachable from a client module;
  a secret in a `NEXT_PUBLIC_*` variable.
- Sync `params` / `searchParams` / `cookies()` / `headers()` access (breaks on Next 16).
- `middleware.ts` in a Next 16 project without an Edge reason; one-argument `revalidateTag`;
  `priority` on `next/image`.
- New `useMemo`/`useCallback`/`memo` in a compiled file with no stated reason (effect-dependency
  stability, measured cost) — ask for the reason; don't flag existing or justified ones.
- `forwardRef` in new code.
- Signals, not blockers: several booleans shaping one component's look (→ variants/compound
  components) or a prop threaded through many levels (→ context/composition) — raise only when
  it causes a real problem (conflicting states, repeated bugs, hard-to-add variant).
- Raw colors/spacing/durations where a token exists; a new shared component missing from
  `design/components.yaml`; a copy of a registered component.
- Slow data outside `<Suspense>`; sequential `await`s of independent data.
- Barrel imports of large libraries in client code, unless Next already optimizes that package (its
  default `optimizePackageImports` list includes `lucide-react`, `date-fns`, `lodash-es`,
  `@mui/material` and `recharts`); a heavy client-only library not loaded with a dynamic import.

## Section 5: Hydration safety

- The server HTML and the first client render must match. In render, never read
  `Date.now()`, `Math.random()`, `window`/`localStorage`, or format dates/numbers with the
  device locale or time zone. Use `useId` for ids.
- Browser-only values: `use(browser())` (19.3), or set state after mount. Format dates with an
  explicit `timeZone` when the server renders them.
- Invalid nesting (`<div>` or `<p>` inside `<p>`, `<a>` inside `<a>`, `<button>` inside
  `<button>`) causes hydration errors — fix the markup, don't suppress.
- `suppressHydrationWarning` only on the single element with an intended difference (e.g.
  the theme attribute an inline script sets on `<html>`). Never as a blanket.
- Theme flash: an inline script sets the theme before paint (ux/references/dark-mode.md).
- A controlled input needs `onChange`; submit-only forms use `defaultValue`.
- Before chasing a mismatch, reproduce in a clean browser profile — extensions inject
  attributes.
- **QA gate:** zero hydration errors in the dev console on primary routes.

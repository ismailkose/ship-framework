<!-- ship-reference
id: web-perf
kind: mixed
sources: https://web.dev/articles/vitals (2026-09-23; page updated 2024-10-31); https://web.dev/blog/inp-cwv-launch (2026-09-23); https://web.dev/articles/ttfb (2026-09-23); https://web.dev/articles/fcp (2026-09-23); https://nextjs.org/docs/app/api-reference/components/image (2026-09-23); https://nextjs.org/blog/next-16-3 (2026-09-23)
reviewed: 2026-09-23
-->

# Web Performance — Core Web Vitals and how Ship gates them

> **Agent routing:** Arc → Section 1 · Dev → Section 2 · Crit, Pol → Section 4 ·
> Test, Eye (/shipmate perf) → Sections 1 and 3
>
> Thresholds in Section 1 are Google's published Core Web Vitals (platform guidance). Budgets
> marked **Ship default** are Ship's and only warn.

---

## Section 1: Core Web Vitals — targets and the gate

INP replaced FID as the responsiveness vital on 2024-03-12. The three stable vitals:

| Metric | Measures | Good | Needs improvement | Poor |
|---|---|---|---|---|
| **LCP** Largest Contentful Paint | loading | ≤ 2.5 s | ≤ 4.0 s | > 4.0 s |
| **INP** Interaction to Next Paint | responsiveness | ≤ 200 ms | ≤ 500 ms | > 500 ms |
| **CLS** Cumulative Layout Shift | visual stability | ≤ 0.1 | ≤ 0.25 | > 0.25 |

- Judge the **75th percentile** of page loads, **mobile and desktop separately**.
- Diagnostics, not vitals: TTFB good ≤ 0.8 s; FCP good ≤ 1.8 s. Use them to find *why* LCP is
  slow; don't gate on them.
- **Field data wins over lab data.** Field = real users (CrUX, RUM). Lab = one synthetic run —
  a stand-in before launch or for low-traffic sites.

**The gate (per primary route, mobile first):**

| Result | Status |
|---|---|
| All three "good" | PASS |
| Any "needs improvement", none "poor" | WARN — founder decides; record in `DECISIONS.md` |
| Any "poor" | FAIL — fix before launch |

With no field data yet: gate LCP and CLS on the lab run (mobile throttling), and INP on an
interaction trace of the route's main actions (Section 3). Lighthouse's 0–100 Performance
score is not a gate.

**Ship default budgets (warn only):** first-load JS per route ≤ 200 KB compressed; no single
image > 200 KB on a mobile viewport; ≤ 2 font families. Breaking one prompts a look, not a
block — the vitals decide.

## Section 2: What moves each metric

**LCP**
- The LCP element (usually the hero image or headline) is in the server HTML — not rendered
  after a client fetch.
- LCP image: `loading="eager"` + `fetchpriority="high"` (Next 16: `preload` replaces the
  deprecated `priority`). Never `loading="lazy"` on it.
- Modern formats (AVIF/WebP) at the displayed size: `next/image` or `<picture>` with
  `srcset` + `sizes`.
- Fast server response: static or cached shells (`'use cache'`, react-patterns.md Section 2),
  CDN, no blocking redirects.
- Fonts: `next/font` or self-hosted `woff2`, preload only the critical face, `font-display:
  swap` (or `optional` for body text when layout stability matters more than the face).
- Render-blocking: no synchronous third-party scripts in `<head>`; non-critical scripts via
  `next/script` `strategy="lazyOnload"` or after hydration.

**INP**
- Keep event handlers short; move non-urgent work out of the input's frame
  (`startTransition`, `useDeferredValue`, or yield — `scheduler.yield()` where supported,
  else `setTimeout`).
- Break long tasks (> 50 ms) — the Performance panel marks them.
- Don't read layout (`getBoundingClientRect`, `offsetHeight`) right after writing styles in
  the same handler.
- Virtualize long lists (> ~50 rows) or `content-visibility: auto`.
- Compiler on (react-patterns.md Section 2) removes most wasted re-renders.
- Third-party widgets (chat, analytics, A/B) are a common INP cost: load late, measure with and
  without.

**CLS**
- Every image, video, iframe and ad slot has `width`/`height` or `aspect-ratio`.
- Skeletons and Suspense fallbacks occupy the final size.
- Nothing inserts above existing content after load unless the user asked (banners overlay
  or reserve space).
- Font swaps don't shift: `next/font` applies metric overrides; otherwise `size-adjust` /
  `ascent-override` on the fallback.
- Animate `transform`/`opacity`, not layout properties (motion skill).

**Navigation**
- Back/forward cache: no `unload` listeners; avoid `Cache-Control: no-store` on HTML unless
  the page is private.
- Next 16.3: Instant Insights in the dev tools flags navigations that aren't instant; the
  `instant()` Playwright helper locks the fix in (react-patterns.md Section 2).

## Section 3: Measuring

**Field (after launch, or any public URL with traffic):**
- PageSpeed Insights / CrUX shows p75 LCP, INP, CLS for real Chrome users (needs enough
  traffic).
- RUM for everything else: the `web-vitals` library (`onLCP`, `onINP`, `onCLS` → your
  analytics), or the host's built-in (e.g. Vercel Speed Insights).

**Lab (before launch; /shipmate perf):**
- Production build (`next build && next start`), not the dev server.
- Chromium via Playwright or Lighthouse CLI, mobile emulation with CPU + network throttling.
- **3 runs per route, report the median** (single runs are noisy).
- INP needs interactions: run the route's main actions (open menu, submit form, switch tab)
  with `web-vitals` injected, or record them in the DevTools Performance panel (live metrics
  show INP for your own interactions). Total Blocking Time is only a proxy.
- CLS in the lab misses shifts that happen after load — scroll and interact during the run.
- Bundle size: Next's build output per route, or the Next.js bundle analyzer (16.1+,
  experimental), or `source-map-explorer`.

**Reporting:** per route — metric, value, threshold, PASS/WARN/FAIL (Section 1 gate), and the
element or task responsible (LCP element, longest interaction, largest shift source). No
aggregate score.

## Section 4: Review — performance flags

The long tail (barrel imports, waterfalls, re-render rules) belongs to
the recommended React skills and the web interface checklist (web/SKILL.md). Ship's
short list:

- Image without dimensions or `aspect-ratio`; lazy-loaded LCP image; unoptimized format or
  oversized source.
- Render-blocking resources: sync scripts in `<head>`, unused CSS frameworks, `@import` chains.
- Content inserted above existing content after load; fallback smaller than the final UI.
- Web fonts without `font-display` or preloading every weight.
- A route's client JS over the Ship default budget; heavy libraries (charts, editors, maps)
  not code-split with a dynamic import.
- Sequential awaits of independent data on the server (react-patterns.md Section 2).
- Unvirtualized lists over ~50 rows.
- Layout reads inside scroll/resize/input handlers; unthrottled scroll listeners.
- Synchronous third-party scripts; analytics loaded before the page is interactive.
- Missing caching headers on static assets (hashed assets: long `max-age` + `immutable`).
- `transition: all` or animating layout properties → motion skill.

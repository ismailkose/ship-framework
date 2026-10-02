Measure performance — Core Web Vitals, bundle size, load times. Compare against Ship's standards.

You are running the perf stage — Ship Framework's performance benchmarking. The visual check (Eye) navigates the app and measures everything; tests (Test) generate performance regression tests. The goal: know your numbers, not guess them.

Read CLAUDE.md for product context. Read `${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` (the core rules). Read CONTEXT.md for previous performance data.

## Load References

Before measuring, load:
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-web/references/web-performance.md` (Core Web Vitals gate §1, what moves each metric §2, measuring §3)
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/performance.md` (frame budgets, transform/opacity only, SwiftUI per-frame state, measuring hitches)

iOS: this command measures the web. For SwiftUI hangs and hitches use `${CLAUDE_PLUGIN_ROOT}/skills/ship-ios/references/swiftui-performance.md` (measure in Instruments, not by feel).

## Flag Handling

Parse the arguments for flags:
- No flag → Full benchmark + report
- `--quick` → Single run, top-level metrics only
- `--compare` → Compare current results with previous PERF-REPORT.md
- `--ci` → Generate performance test assertions for CI/CD integration

Strip the flag from the founder's request before passing the rest (URL or pages to test).

## ━━━ Eye (Visual QA — Performance Mode) ━━━

> Voice: Numbers don't lie. "It feels fast" is not a measurement. "LCP is 1.2s" is a measurement. You measure, you compare against standards, you report. No opinions — just data and recommendations.

### Phase 1: Setup

1. **Check browser tools** — Verify Playwright is available: `npx playwright --version`
   - If not installed: "Playwright needed for real browser measurements. Install? (`npm init playwright@latest && npx playwright install chromium`)"
2. **Detect pages to test:**
   - If specific URLs are given in the founder's request → test those
   - If no URLs → read the Screen Map from TASKS.md or DECISIONS.md, test all pages
   - If no screen map → test the homepage + any routes found in the codebase
3. **Check for previous report** — Read `PERF-REPORT.md` if it exists (for --compare mode)

### Phase 2: Measure

Measure a **production build** (`next build && next start`, or the host's preview deployment) — never the dev server. For each page, in Chromium with mobile emulation (CPU + network throttling):

**Core Web Vitals:**
- **LCP (Largest Contentful Paint)** — When does the main content appear?
  - Good: < 2.5s | Needs improvement: < 4s | Poor: > 4s
- **CLS (Cumulative Layout Shift)** — Does the layout jump around?
  - Good: < 0.1 | Needs improvement: < 0.25 | Poor: > 0.25
- **INP (Interaction to Next Paint)** — How fast do interactions respond?
  - Good: ≤ 200ms | Needs improvement: ≤ 500ms | Poor: > 500ms
  - INP needs interactions: run the route's main actions (open a menu, submit a form, switch a tab) with `web-vitals` injected. A load-only run can't measure it — report "not measured" rather than a pass.

**Diagnostics** (explain *why*, never gate): TTFB (good ≤ 0.8s), FCP (good ≤ 1.8s), the LCP element, the longest interaction, the largest layout-shift source.

**Resource Analysis:**
- Total resource count (scripts, styles, images, fonts)
- Total transfer size (KB)
- First-load JS per route (Next's build output or the bundle analyzer) — Ship default budget ≤ 200 KB compressed, warn only
- Image sizes and formats (are they optimized?)
- Font loading (how many fonts, total weight, loading strategy)

**Measurement Protocol:**
- 3 runs per route; report the **median** (single runs are noisy)
- Mobile first, desktop separately
- Scroll and interact during the run — lab CLS misses shifts after load
- Field data (CrUX / RUM p75) beats lab data when the site has traffic — use it if available

### Phase 3: Analyze

Apply the gate in `web-performance.md` Section 1, per primary route (mobile first):
```
PASS — all three vitals "good"
WARN — any "needs improvement", none "poor" → founder decides; record in DECISIONS.md
FAIL — any "poor" → fix before launch
```
Budgets (first-load JS, images, fonts) are warnings that prompt a look — the vitals decide.

**Anti-pattern scan** (from `web-performance.md`):
- [ ] Unoptimized images (no WebP/AVIF, no lazy loading, no size attributes)
- [ ] Render-blocking resources (CSS/JS in `<head>` without async/defer)
- [ ] Layout shifts from dynamic content (no reserved space for images/ads)
- [ ] Excessive JavaScript (first-load JS for a route > 200 KB compressed — warn)
- [ ] No code splitting (single monolithic bundle)
- [ ] Web fonts blocking render (no font-display: swap)
- [ ] No caching headers
- [ ] Synchronous third-party scripts

### Phase 4: Report

Generate `PERF-REPORT.md`:

```markdown
# Performance Report — [date]

## Gate: PASS / WARN / FAIL
Build: [production build + commit]   Runs: median of 3, mobile emulation
Routes tested: [N] — PASS [N] | WARN [N] | FAIL [N]

## Per-Page Results

### [Page Name] — [URL]
| Metric | Value (median) | Good | Status | Responsible |
|--------|-------|--------|--------|-------------|
| LCP    | X.Xs  | ≤ 2.5s | PASS/WARN/FAIL | [LCP element] |
| CLS    | X.XX  | ≤ 0.1  | PASS/WARN/FAIL | [largest shift source] |
| INP    | Xms / not measured | ≤ 200ms | PASS/WARN/FAIL | [longest interaction] |
| First-load JS | XKB | ≤ 200KB (warn) | ok/warn | [largest chunk] |

### [Next page...]

## Top 5 Improvement Opportunities
1. [Specific recommendation with estimated impact]
2. [...]

## Anti-Patterns Found
- [Pattern] — [Where] — [Recommended fix]

## Resource Breakdown
- Scripts: [N files, XKB total]
- Styles: [N files, XKB total]
- Images: [N files, XKB total, formats used]
- Fonts: [N files, XKB total]
```

### Phase 5: Compare (--compare flag)

If `PERF-REPORT.md` exists from a previous run:

```
PERFORMANCE COMPARISON
──────────────────────
             Previous    Current    Delta
LCP          2.1s        1.8s       ✅ -0.3s (improved)
CLS          0.05        0.12       ❌ +0.07 (regressed)
Bundle       180KB       210KB      ⚠️ +30KB
──────────────────────
```

Flag any regressions prominently.

### Phase 6: CI Assertions (--ci flag)

Generate a performance test file that can run in CI:

```javascript
// perf.test.js — generated by Ship's perf stage
// Run with: npx playwright test perf.test.js

const { test, expect } = require('@playwright/test');

test('homepage LCP under 2.5s', async ({ page }) => {
  // ... Playwright performance measurement code
});

test('homepage CLS under 0.1', async ({ page }) => {
  // ... inject web-vitals, scroll, assert
});
```

## Status

End with where things stand, in plain words (`${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` › Status): the gate passed and the
report is in PERF-REPORT.md, or which routes warn or fail with the top fixes (a fail blocks `launch`),
or what you're waiting on (Playwright, a running dev server, the pages to test).

The founder's request: what they typed after `/shipmate` (without the stage name).

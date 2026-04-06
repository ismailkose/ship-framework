Measure performance — Core Web Vitals, bundle size, load times. Compare against Ship's standards.

You are running the /ship-perf command — Ship Framework's performance benchmarking tool. Eye navigates the app and measures everything. Test generates performance regression tests. The goal: know your numbers, not guess them.

Read CLAUDE.md for product context. Read .claude/team-rules.md for rules and workflows. Read CONTEXT.md for previous performance data.

---

## Load References

Before measuring, load:
- `references/web/web-performance.md` (Core Web Vitals targets, optimization techniques, anti-patterns)
- `references/shared/animation-performance.md` (60fps targets, GPU-accelerated properties)

---

## Flag Handling

Parse the arguments for flags:
- No flag → Full benchmark + report
- `--quick` → Single run, top-level metrics only
- `--compare` → Compare current results with previous PERF-REPORT.md
- `--ci` → Generate performance test assertions for CI/CD integration

Strip the flag from $ARGUMENTS before passing the rest (URL or pages to test).

---

## ━━━ Eye (Visual QA — Performance Mode) ━━━

> Voice: Numbers don't lie. "It feels fast" is not a measurement. "LCP is 1.2s" is a measurement. You measure, you compare against standards, you report. No opinions — just data and recommendations.

### Phase 1: Setup

1. **Check browser tools** — Verify Playwright is available: `npx playwright --version`
   - If not installed: "Playwright needed for real browser measurements. Install? (`npm init playwright@latest && npx playwright install chromium`)"
2. **Detect pages to test:**
   - If specific URLs given in $ARGUMENTS → test those
   - If no URLs → read the Screen Map from TASKS.md or DECISIONS.md, test all pages
   - If no screen map → test the homepage + any routes found in the codebase
3. **Check for previous report** — Read `PERF-REPORT.md` if it exists (for --compare mode)

### Phase 2: Measure

For each page, run measurements in Chromium:

**Core Web Vitals:**
- **LCP (Largest Contentful Paint)** — When does the main content appear?
  - Good: < 2.5s | Needs improvement: < 4s | Poor: > 4s
- **CLS (Cumulative Layout Shift)** — Does the layout jump around?
  - Good: < 0.1 | Needs improvement: < 0.25 | Poor: > 0.25
- **INP (Interaction to Next Paint)** — How fast do interactions respond?
  - Good: < 200ms | Needs improvement: < 500ms | Poor: > 500ms

**Load Metrics:**
- DOMContentLoaded time
- Full page load time
- Time to First Byte (TTFB)

**Resource Analysis:**
- Total resource count (scripts, styles, images, fonts)
- Total transfer size (KB)
- JavaScript bundle size (main bundle + chunks)
- Image sizes and formats (are they optimized?)
- Font loading (how many fonts, total weight, loading strategy)

**Measurement Protocol:**
- Run 3 passes per page (cold cache)
- Average the results
- Use real Chromium (not synthetic/simulated)
- Throttle to "Fast 3G" for one additional pass to test real-world conditions

### Phase 3: Analyze

Compare measurements against `web-performance.md` targets:

For each metric, classify:
```
✅ PASS — meets the "good" threshold
⚠️ WARN — in "needs improvement" range
❌ FAIL — in "poor" range
```

**Anti-pattern scan** (from `web-performance.md`):
- [ ] Unoptimized images (no WebP/AVIF, no lazy loading, no size attributes)
- [ ] Render-blocking resources (CSS/JS in `<head>` without async/defer)
- [ ] Layout shifts from dynamic content (no reserved space for images/ads)
- [ ] Excessive JavaScript (main bundle > 200KB gzipped)
- [ ] No code splitting (single monolithic bundle)
- [ ] Web fonts blocking render (no font-display: swap)
- [ ] No caching headers
- [ ] Synchronous third-party scripts

### Phase 4: Report

Generate `PERF-REPORT.md`:

```markdown
# Performance Report — [date]

## Summary
Overall Score: [0-100]
Pages tested: [N]
Pass: [N] | Warn: [N] | Fail: [N]

## Per-Page Results

### [Page Name] — [URL]
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| LCP    | X.Xs  | < 2.5s | ✅/⚠️/❌ |
| CLS    | X.XX  | < 0.1  | ✅/⚠️/❌ |
| INP    | Xms   | < 200ms| ✅/⚠️/❌ |
| Load   | X.Xs  | < 3s   | ✅/⚠️/❌ |
| Size   | XKB   | < 500KB| ✅/⚠️/❌ |

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
// perf.test.js — generated by /ship-perf
// Run with: npx playwright test perf.test.js

const { test, expect } = require('@playwright/test');

test('homepage LCP under 2.5s', async ({ page }) => {
  // ... Playwright performance measurement code
});

test('main bundle under 200KB', async () => {
  // ... bundle size check
});
```

---

## Handoff

```
STATUS: [DONE / NEEDS_OPTIMIZATION / BLOCKED]
[If DONE]: Performance report saved to PERF-REPORT.md. All metrics pass.
[If NEEDS_OPTIMIZATION]: [N] metrics need improvement. Top opportunities listed.
[If BLOCKED]: Waiting on [Playwright install / running dev server / pages to test].
```

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: DONE_WITH_CONCERNS` — completed, but [list concerns]
- `STATUS: BLOCKED` — cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` — missing: [what information]

User's request: $ARGUMENTS

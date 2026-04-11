# Production Hardening Reference

> Before shipping, every product needs hardening — the unglamorous work that turns a demo into a real product. This reference covers edge cases, error boundaries, defensive patterns, and the gaps between "it works on my machine" and "it works for everyone."
>
> **Agent routing:**
> Dev → Sections 1-3 (implement error boundaries, defensive patterns, edge case handling)
> Test → Sections 2-3 (verify edge cases, stress test, environmental testing)
> Crit → Section 1 (error recovery affects task success and retention)
> Arc → Section 1 (error strategy should be planned, not patched)

---

## Section 1: Error Boundaries & Recovery

### Philosophy: Errors Are Features

Errors aren't exceptional — they're expected. Network fails. APIs change. Users paste garbage. Servers timeout. The question isn't "will errors happen" but "what does the user experience when they do?"

**The hierarchy of error handling:**

1. **Prevent** — Don't let the error happen (validation, type checking, rate limiting)
2. **Recover** — Fix it automatically (retry, fallback data, cache)
3. **Inform** — Tell the user what happened and what to do (clear message, retry button)
4. **Degrade** — Show a reduced experience rather than nothing (offline mode, cached content)
5. **Crash** — Last resort. Even crashes should have a recovery path (error boundary with retry)

### Error Boundaries (React)

Every distinct UI section should have its own error boundary. One broken widget shouldn't take down the entire page.

```tsx
// Incorrect — one error boundary for the whole app
<ErrorBoundary>
  <App /> {/* one broken component = white screen */}
</ErrorBoundary>

// Correct — granular error boundaries
<Layout>
  <ErrorBoundary fallback={<NavFallback />}>
    <Navigation />
  </ErrorBoundary>
  <ErrorBoundary fallback={<ContentError onRetry={refresh} />}>
    <MainContent />
  </ErrorBoundary>
  <ErrorBoundary fallback={<SidebarFallback />}>
    <Sidebar />
  </ErrorBoundary>
</Layout>
```

**Error boundary fallbacks should:**
- Explain what broke (not "Something went wrong" — be specific: "Couldn't load your projects")
- Offer a retry action (button, not just text)
- Preserve surrounding layout (the fallback should occupy the same space)
- Log the error for debugging (send to error tracking service)

### Network Error Patterns

```tsx
// The retry pattern with exponential backoff
async function fetchWithRetry(url, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt)));
    }
  }
}
```

**User-facing network errors:**
- **Timeout** → "Taking longer than expected. Retry?" (with retry button)
- **Offline** → "You're offline. Changes will sync when you're back." (with offline indicator)
- **Server error (5xx)** → "Our servers are having trouble. We're on it." (with retry + status page link)
- **Not found (404)** → "This page doesn't exist." (with link to home or search)
- **Rate limited (429)** → "Too many requests. Try again in a moment." (with countdown)

### Optimistic UI Recovery

Optimistic updates feel fast but need rollback when the server disagrees.

```tsx
// Pattern: optimistic update with rollback
function useOptimisticAction(serverFn) {
  const [state, setState] = useState(null);

  async function execute(optimisticValue, ...args) {
    const previousState = state;
    setState(optimisticValue); // immediate UI update

    try {
      const result = await serverFn(...args);
      setState(result); // confirm with server data
    } catch (error) {
      setState(previousState); // rollback on failure
      toast.error("Couldn't save. Your changes have been reverted.");
    }
  }

  return [state, execute];
}
```

---

## Section 2: Edge Cases That Break Products

These are the patterns that work in demos but break with real users.

### Text Content Edge Cases

| Edge Case | What Breaks | Fix |
|-----------|-------------|-----|
| Empty string | Layout collapses, no content indicator | Show empty state, min-height |
| Very long text (500+ chars) | Overflow, layout break | Truncation + tooltip, max-width |
| Special characters (`<>&"'`) | XSS, display corruption | Sanitize input, escape output |
| Unicode/emoji (👋🏽) | Layout shift, font fallback | Test with emoji, use Unicode-safe fonts |
| RTL text (Arabic, Hebrew) | Layout mirrored incorrectly | `dir="auto"` on user content, test RTL |
| Single very long word | Horizontal overflow | `overflow-wrap: break-word` |
| Pasted rich text | Unwanted formatting | Strip HTML on paste for plain text fields |

### Numeric Edge Cases

| Edge Case | What Breaks | Fix |
|-----------|-------------|-----|
| Zero | Division errors, "0 items" phrasing | Handle zero state explicitly |
| Negative numbers | Progress bars break, display issues | Clamp to valid range |
| Very large numbers (1000000+) | Layout overflow | Format with separators, abbreviate (1M) |
| Decimals (0.1 + 0.2) | Floating point display (0.30000000000000004) | Round for display, use cents for money |
| NaN / undefined | "NaN" displayed to user | Fallback display, validate before render |

### Timing Edge Cases

| Edge Case | What Breaks | Fix |
|-----------|-------------|-----|
| Double-click | Duplicate submissions | Disable button during request, debounce |
| Rapid navigation | Race conditions, stale data | Cancel previous requests (AbortController) |
| Back button after submit | Re-submission, stale state | Replace history entry after success |
| Session timeout mid-action | Lost work | Save draft locally, restore on re-auth |
| Slow network (3G) | No feedback, timeout | Loading states, optimistic UI, timeout message |
| Clock skew (user's device) | Wrong timestamps, expired tokens | Use server time for critical operations |

### File Upload Edge Cases

| Edge Case | What Breaks | Fix |
|-----------|-------------|-----|
| File too large | Server rejection, browser crash | Client-side size check before upload |
| Wrong file type | Server error, processing failure | Accept attribute + client validation |
| Upload interrupted | Partial file, no recovery | Resumable uploads, progress indicator |
| Filename with spaces/special chars | URL encoding issues | Sanitize filename on upload |
| Zero-byte file | Processing errors | Reject empty files with message |

### Authentication Edge Cases

| Edge Case | What Breaks | Fix |
|-----------|-------------|-----|
| Token expires during use | 401 errors mid-action | Silent refresh, queue failed requests |
| Multiple tabs | Session conflicts | SharedWorker or BroadcastChannel sync |
| Password manager autofill | Overwritten fields, wrong data | Proper autocomplete attributes |
| Social login popup blocked | Silent failure | Detect blocked popup, offer redirect flow |

---

## Section 3: Environmental Hardening

### Browser & Device Testing Matrix

Don't test on one browser and call it done. Minimum coverage:

**Desktop:** Chrome (latest), Firefox (latest), Safari (latest), Edge (latest)
**Mobile:** iOS Safari (latest + previous), Chrome Android (latest)
**Screen sizes:** 320px, 375px, 768px, 1024px, 1440px, 1920px

**Common cross-browser issues:**
- Safari date input: doesn't support `type="date"` the same way — test explicitly
- Firefox focus styles: renders focus rings differently — test `:focus-visible`
- Mobile Safari: `100vh` includes the address bar — use `100dvh` instead
- Chrome Android: bottom nav bar overlaps fixed-bottom elements

### Performance Hardening

Before shipping, verify:

- **First Contentful Paint < 1.8s** — If slower, optimize critical CSS, defer non-essential JS
- **Largest Contentful Paint < 2.5s** — If slower, optimize images (WebP/AVIF, lazy loading)
- **Cumulative Layout Shift < 0.1** — If higher, set explicit dimensions on images/videos
- **Interaction to Next Paint < 200ms** — If slower, reduce JS on main thread

```html
<!-- Image hardening: prevent layout shift -->
<img
  src="hero.webp"
  alt="Product screenshot"
  width="1200"
  height="800"
  loading="lazy"
  decoding="async"
/>
```

### Security Basics

- **Sanitize all user input** — Never render raw user content. Use `textContent` not `innerHTML`.
- **CSRF protection** — Include CSRF tokens in state-changing requests.
- **Content Security Policy** — Set CSP headers to prevent XSS.
- **HTTPS everywhere** — No mixed content. Redirect HTTP to HTTPS.
- **Rate limiting** — Protect auth endpoints, file uploads, and API routes.
- **Dependency auditing** — Run `npm audit` before shipping. Fix critical/high vulnerabilities.

### Accessibility Hardening

Final accessibility pass before launch:

- [ ] Tab through entire app — logical order, no traps, visible focus
- [ ] Screen reader test (VoiceOver on Mac, NVDA on Windows) — all content announced
- [ ] Zoom to 200% — no horizontal scroll, no overlapping content
- [ ] Keyboard-only navigation — every feature accessible without mouse
- [ ] Color contrast verified — 4.5:1 body text, 3:1 UI components
- [ ] Reduced motion tested — no unnecessary animation
- [ ] Error messages announced to screen readers (`aria-live="polite"`)

### Pre-Launch Checklist

- [ ] Error boundaries on every distinct UI section
- [ ] Loading states for every async operation
- [ ] Empty states for every list/collection
- [ ] Offline behavior defined (even if it's just a message)
- [ ] Form validation on client AND server
- [ ] 404 page designed and routed
- [ ] Favicon, meta tags, Open Graph images set
- [ ] Analytics/error tracking installed and verified
- [ ] Performance budget met (LCP < 2.5s, CLS < 0.1)
- [ ] Cross-browser tested (Chrome, Firefox, Safari, mobile)
- [ ] Accessibility audit passed

---

*Based on production patterns from Vercel's deployment checklist, web.dev performance guidelines, and OWASP security practices.*

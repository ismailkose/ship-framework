<!-- ship-reference
id: hardening
kind: mixed
sources: https://react.dev/reference/react-dom/client/createRoot (2026-09-23); https://nextjs.org/docs/app/getting-started/error-handling (2026-09-23); https://nextjs.org/blog/next-16-3 (2026-09-23); https://nextjs.org/docs/app/guides/testing (2026-09-23); https://playwright.dev/docs/accessibility-testing (2026-09-23); https://top10.owasp.org/2025 (2026-09-23); https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components (2026-09-23); https://developer.apple.com/documentation/testing (2026-09-23); https://developer.apple.com/app-store/review/guidelines/ (2026-09-23)
reviewed: 2026-09-23
-->

# Production Hardening — errors, edge cases, launch gate, tests, security

> **Agent routing:** Arc → Sections 1 and 4 (plan error strategy and tests) · Dev → Sections
> 1, 2, 4, 5 · Crit → Sections 1–2 · Test → Sections 2 and 4 · Cap (/shipmate launch) → Section 3
>
> Web mechanics are named where they differ; iOS specifics (App Store, Keychain, XCUITest
> setup) live in the iOS skill — this file points there.

---

## Section 1: Error handling and recovery

**Order of preference:** prevent (validate, type, disable while pending) → recover
automatically (retry idempotent reads, fall back to cache) → inform (say what happened and
what to do, with a retry) → degrade (cached/offline view) → contain (boundary with retry).
Never a blank screen.

**Every async UI has four states:** loading, success, empty, error. Empty and error are
designed, not default text. (State model: `ux/references/interaction-design.md` Section 1.)

**Web — boundaries (React 19 / Next 16):**
- Route level: `error.tsx` (a Client Component) per route segment that fetches;
  `global-error.tsx` (own `<html>`/`<body>`) for the root layout; `not-found.tsx` for 404s.
  Next 16.3 passes `retry()` (re-fetches and re-renders) — prefer it to `reset()` (re-renders
  only); older versions have `reset` only.
- Section level: wrap independent widgets so one failure doesn't blank the page. Next 16.3:
  `catchError` from `next/error` gives a boundary whose `retry()` re-renders Server
  Components and doesn't swallow `notFound()`/`redirect()`.
- Boundaries don't catch event-handler or async errors — handle those in the handler
  (`try/catch` → error state or toast), and in Server Actions return an error result for
  `useActionState` rather than throwing for expected failures.
- Report everything: `createRoot(el, { onCaughtError, onUncaughtError })` (React 19) or the
  error-tracking SDK's React integration; server errors via Next's `instrumentation.ts`
  `onRequestError`.

**Fallback content:** name what failed ("Couldn't load your projects"), offer a retry
button, keep the surrounding layout and the fallback's size, log with enough context to
reproduce (route, action, user id — not personal data).

**Network failures — user-facing:**

| Failure | Tell the user | Offer |
|---|---|---|
| Timeout / slow | "Taking longer than usual…" after a few seconds | Keep waiting or retry |
| Offline | "You're offline — changes will sync" (or "can't save offline") | Queue or disable writes; Next 16.3 `useOffline()` |
| 5xx | "Something went wrong on our side" | Retry; status link if one exists |
| 401 mid-session | Nothing, if a silent refresh works | Otherwise re-auth, then resume the action |
| 403 | "You don't have access to this" | Way back / request access |
| 404 | "This page doesn't exist" | Home or search |
| 429 | "Too many tries — wait a moment" | Retry after the server's `Retry-After` |

Retries: only idempotent requests, exponential backoff with jitter, a small cap (e.g. 3),
cancel on unmount/navigation (`AbortController`).

**Optimistic updates** roll back and say so ("Couldn't save — your change was undone") —
`useOptimistic` reverts automatically when the action settles.

**iOS:** error presentation and recovery patterns → iOS skill; the four-state rule applies
unchanged.

## Section 2: Edge cases that break products

Test each row that applies to the feature. They pass in demos and fail with real users.

**Text**

| Case | Breaks | Fix |
|---|---|---|
| Empty string / whitespace only | Collapsed layout, blank rows | Trim; empty state; `min-height` |
| Very long text, one long word, URL | Overflow, broken layout | `overflow-wrap: anywhere`, `line-clamp`, `min-w-0` on flex children |
| Markup / `<>&"'` in user content | XSS, garbled display | Render as text; sanitize any HTML you must render |
| Emoji, combining marks, CJK | Wrong length counts, clipped glyphs | Count graphemes (`Intl.Segmenter`), test real strings |
| RTL (Arabic, Hebrew) | Mirrored layout wrong | `dir="auto"` on user content; logical CSS properties |
| Pasted rich text | Hidden formatting | Strip to plain text for plain fields |

**Numbers and money**

| Case | Breaks | Fix |
|---|---|---|
| 0, 1, many | "1 items", divide by zero | Plurals via `Intl.PluralRules`; zero state |
| Negative / out of range | Broken bars and charts | Clamp and validate |
| Large (1,000,000+) | Overflow | `Intl.NumberFormat` (compact notation where fitting) |
| Floating point (0.1 + 0.2) | 0.30000000000000004 | Integer minor units for money; round for display |
| `NaN`, `null`, `undefined` | "NaN" on screen | Validate before render; explicit fallback |

**Time and concurrency**

| Case | Breaks | Fix |
|---|---|---|
| Double click / double submit | Duplicate records, double charges | Pending state disables; idempotency key on the server |
| Rapid navigation | Stale data overwrites fresh | Abort previous requests; ignore late responses |
| Back after submit | Resubmission | Redirect after POST; replace history entry |
| Session expiry mid-task | Lost work | Keep drafts locally; resume after re-auth |
| Two tabs | Conflicting state | `BroadcastChannel` or refetch on focus |
| Time zones / DST / device clock | Wrong dates, "expired" tokens | Store UTC; format with explicit zone; server time for expiry |

**Files**

| Case | Breaks | Fix |
|---|---|---|
| Too large / wrong type | Server errors, crashes | Check size and MIME before upload *and* on the server |
| Zero bytes, odd names | Processing errors, bad URLs | Reject empties; store under generated names |
| Interrupted upload | Partial files | Progress + resumable or clean retry |

**Auth**

| Case | Breaks | Fix |
|---|---|---|
| Token expires during use | 401s mid-action | Silent refresh, then replay the request |
| Password manager / passkey autofill | Wrong fields filled | Correct `autocomplete`; never block paste (WCAG 3.3.8) |
| OAuth popup blocked | Silent failure | Redirect flow fallback |

**Environment (web)**
- Browsers: current Chrome, Safari, Firefox, Edge; iOS Safari (current and previous major);
  Chrome Android. Widths: 320, 375, 768, 1024, 1440.
- Mobile viewport height: `100dvh`/`svh`, not `100vh`; respect `env(safe-area-inset-*)`.
- Slow network: throttle to a slow mobile profile once per primary flow.
- **iOS:** device sizes, Dynamic Type sizes, dark mode, low-power and offline → iOS skill.

## Section 3: Pre-launch gate (pass/fail)

Cap runs this in /shipmate launch. Rows adapt to the Stack; skip what doesn't apply, never fake
it. **FAIL** blocks the release until fixed or the founder explicitly accepts it in
`DECISIONS.md`. **WARN** is reported; the founder decides. Accessibility and security FAILs
are not waivable by taste.

| # | Check | FAIL when | WARN when |
|---|---|---|---|
| 1 | Tests | An in-branch test fails | Pre-existing failures on main |
| 2 | Change evidence | A flow changed in this release has neither a test nor a recorded manual verification (screenshot/recording, realistic data) | Evidence is manual only for a flow that is easy to automate |
| 3 | States | A primary flow lacks loading, error or empty state, or can blank the screen | Secondary flows lack designed states |
| 4 | Accessibility | Any WCAG 2.2 A/AA failure in a primary flow (web-accessibility.md §4; iOS → iOS skill) | AA issues in secondary flows |
| 5 | Performance (web) | A Core Web Vital "poor" on a primary route (web-performance.md §1) | "Needs improvement" |
| 6 | Security | Secret in repo or client bundle; server data access without an auth check; high/critical advisory in production dependencies | Missing security headers (Section 5) |
| 7 | Design registry | `design_model.py validate` fails (when `design-model.yaml` exists) | — |
| 8 | Data safety | A destructive migration without a backup or reversal path | No restore ever tested |
| 9 | Config | Production env vars missing; HTTPS off | — |
| 10 | Observability | — | No error tracking receiving events from the production build; no analytics for the success metric |
| 11 | Rollback | — | No known way back (web: promote the previous deployment; iOS: pause phased release, keep the previous build ready) |
| 12 | Polish | — | No 404 page; missing title/description/OG image/favicon; not smoke-tested in Safari and one mobile browser |
| 13 | Store (iOS) | Anything the iOS skill's App Store checklist marks blocking (App Review Guidelines: developer.apple.com/app-store/review/guidelines/) | — |

Coverage percentages are reported as information, never as a gate: line coverage shows what
ran, not what was checked, and a fixed number rewards testing trivia over the flows that
matter. Rows 1–2 gate on evidence instead.

## Section 4: Testing

**What to test (Ship default for a solo builder):**
- **Every plan acceptance criterion** maps to a test or a recorded manual check (gate row 2).
- **Every bug fix** starts with a test that reproduces the bug and fails, then passes.
- **Unit:** pure logic with real rules — pricing, validation, date math, parsers, reducers.
- **UI/component:** interactive components with states (form errors, disabled, empty).
- **End-to-end:** each primary flow — the happy path plus one failure path (network error,
  validation error).
- Skip: snapshot tests of whole pages, tests of framework behaviour, getters.

**Web**
- Unit/component: Vitest + Testing Library; query by role and name
  (`getByRole('button', { name: 'Save' })`) — a failing query is often an a11y bug.
- Async Server Components: test through e2e; unit tools don't fully support them (Next docs).
- E2E: Playwright. Run against a production build; a mobile project (e.g. 390×844) alongside
  desktop; mock failures with `page.route`; web-first assertions
  (`await expect(locator).toBeVisible()`), never fixed `waitForTimeout`.
- A11y in e2e: `@axe-core/playwright` on each primary page, fail on violations
  (web-accessibility.md §3).
- Next 16.3 with Cache Components: `instant()` from `@next/playwright` asserts what a
  navigation shows immediately.

**iOS** (pointers — setup and APIs in the iOS skill)
- Unit: Swift Testing (`import Testing`, `@Test`, `#expect`) for new tests; XCTest remains for
  existing suites and performance tests.
- UI: XCUITest for primary flows; seed state with launch arguments; query by accessibility
  identifier and label.
- Run: `xcodebuild test -scheme <App> -destination 'platform=iOS Simulator,name=<device>'`.

**Flakiness:** a flaky test is a bug — fix it or quarantine it with an owner and a date.
No blanket retries that hide failures.

## Section 5: Security basics

Map to the OWASP Top 10:2025 (top10.owasp.org/2025). The checks that most often matter for
Ship's products:

- **Access control (A01):** every server read and write checks that the signed-in user may
  touch *that* record (no trusting ids from the client). Server Actions and route handlers
  check auth themselves; `proxy.ts`/middleware is not enough.
- **Secrets:** none in git history, none in client code (`NEXT_PUBLIC_*` is public). `.env*`
  gitignored. Anything ever committed gets rotated.
- **Input (A05):** validate on the server with a schema (every action/route); parameterized
  queries or an ORM; render user content as text — raw-HTML injection props only with
  sanitized input; no `eval`.
- **Supply chain (A03):** lockfile committed; `npm audit --omit=dev` shows no high/critical;
  React and Next on current patched releases — check react.dev/blog and nextjs.org/blog
  security posts before launch (e.g. CVE-2025-55182 in React Server Components, fixed in
  19.0.1 / 19.1.2 / 19.2.1, with follow-up fixes on 2025-12-11).
- **Configuration (A02):** HTTPS + HSTS; `Content-Security-Policy` (nonce-based for Next),
  `X-Content-Type-Options: nosniff`, `frame-ancestors`, `Referrer-Policy`. Session cookies
  `HttpOnly; Secure; SameSite=Lax`. Custom cookie-authenticated route handlers check
  `Origin` (Server Actions already compare Origin and Host).
- **Authentication (A07):** rate-limit sign-in, sign-up, reset, OTP; allow paste and
  password managers; prefer passkeys or a proven auth provider over hand-rolled auth.
- **Exceptional conditions (A10):** fail closed on auth/permission errors; users never see
  stack traces.
- **Logging (A09):** log auth failures and admin actions; never log secrets, tokens or
  personal data.
- **AI features:** treat model output as untrusted input; keep secrets out of prompts;
  authorize tool calls on the server (OWASP Top 10 for LLM Applications).
- **iOS:** Keychain, App Transport Security, privacy manifests → iOS skill.

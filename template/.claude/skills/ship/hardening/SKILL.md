---
name: ship-hardening
description: |
  Pre-launch hardening — error states and recovery, edge cases, testing, security basics, and
  the pass/fail launch gate. (ship)
  Loaded by /shipmate launch, /shipmate review and /shipmate build when assessing release readiness.
user-invocable: false
---

# Hardening Skill

Turns a working demo into something that holds up for real users. Road signs here; tables,
checklists and the launch gate live in `references/hardening-guide.md`.

## Precedence

Platform requirements, accessibility (WCAG 2.2 AA; Apple's App Review Guidelines on iOS) and
security basics come first — a product decision or taste can't waive them. Next: explicit
product decisions (`DECISIONS.md`), then founder preferences, platform guidance, expert
sources (OWASP, framework docs), and Ship's defaults in this skill.

## Where each answer lives

| Need | Where |
|---|---|
| Error states, boundaries, network failures, retries | hardening-guide.md §1 |
| Edge-case tables (text, numbers, time, files, auth, environment) | hardening-guide.md §2 |
| Launch gate — FAIL / WARN rows | hardening-guide.md §3 |
| What to test, and how (web + iOS pointers) | hardening-guide.md §4 |
| Security basics mapped to OWASP Top 10:2025 | hardening-guide.md §5 |
| Web accessibility checklist | `.claude/skills/ship/web/references/web-accessibility.md` §4 |
| Web performance gate | `.claude/skills/ship/web/references/web-performance.md` §1 |
| iOS tests, App Store review, Keychain, privacy manifests | `.claude/skills/ship/ios/` |
| Next.js API details for the installed version | `node_modules/next/dist/docs/` |

## Build (/shipmate build) — road signs

- Every async UI ships with loading, empty and error states; never a blank screen.
- Web: `error.tsx` per data-fetching route; wrap independent widgets; handle event-handler and
  async errors in the handler — boundaries don't see them.
- Expected failures (validation, 4xx) return a result the UI shows; unexpected ones throw to a
  boundary and get reported.
- Double submits can't happen: pending state disables the control; the server uses an
  idempotency key for anything that charges or creates.
- Every server read/write checks the user may touch that record; Server Actions validate input
  with a schema and check auth themselves.
- A bug fix starts with a test that reproduces it.
- New logic with real rules (money, dates, permissions, parsing) gets unit tests; each primary
  flow gets an end-to-end test (Playwright on web, XCUITest on iOS).

## Review (/shipmate review) — what Crit and Test check

- Walk the edge-case tables (§2) that apply to the changed feature; report the rows that fail
  with the input that breaks them.
- Error and empty states exist, name what failed, and offer a way forward.
- Tests: each changed flow has a test or a recorded manual verification. Flaky tests are
  findings, not noise.
- Security (§5): secrets, auth checks, input validation, dependency advisories.

## Launch (/shipmate launch) — the gate

Cap runs hardening-guide.md §3 row by row, adapting to the Stack:

- **FAIL** blocks the release until fixed, or until the founder explicitly accepts it in
  `DECISIONS.md`. Accessibility and security FAILs are not waived for taste or speed.
- **WARN** is listed in the Ship Report; the founder decides.
- Gate on evidence (passing tests, recorded verification), not on a coverage percentage;
  report coverage as information when a tool exists.
- iOS releases add the iOS skill's App Store checklist (row 13).

## Testing tools — detect, don't install silently

| Stack | Detect | If missing |
|---|---|---|
| Web unit | `vitest` / `jest` in `package.json` | Suggest Vitest + Testing Library once |
| Web e2e | `@playwright/test` in `package.json` | Suggest `npm init playwright@latest`; meanwhile record manual verification |
| Web a11y | `@axe-core/playwright` | Suggest it with Playwright; meanwhile the keyboard walk (web-accessibility.md §3) |
| iOS | a test target in the Xcode project | Suggest a Swift Testing target; meanwhile record simulator verification |

Never block a build on a missing tool; the launch gate's row 2 accepts recorded manual
verification.

## See also

Web (framework facts, performance, accessibility) · iOS (App Store, device testing) · UX
(state model, error copy) · Design (registry validation).

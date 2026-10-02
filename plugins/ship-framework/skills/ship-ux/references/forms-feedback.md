<!-- ship-reference
id: ux-forms-feedback
kind: mixed
sources: https://www.w3.org/TR/WCAG22/ (1.3.5, 2.2.1, 3.3.1–3.3.3, 3.3.7, 3.3.8, 4.1.3; 2026-09-23); https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill (2026-09-23); https://developer.apple.com/design/human-interface-guidelines/entering-data (2026-09-23); https://m3.material.io/foundations/interaction/states (disabled opacity; 2026-09-23); https://design-system.service.gov.uk/patterns/ (2026-09-23, rechecked 2026-10-01); https://pages.nist.gov/800-63-4/sp800-63b.html (passwords: length, no composition rules; 2026-10-01); books-and-sites (Adham Dannaway, Practical UI; Jakob Nielsen's heuristics)
reviewed: 2026-10-01
-->

# Forms & Feedback

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`).
**Registry first:** use the project's form components from `design/components.yaml` (and on
shadcn stacks, its `Field` family — `${CLAUDE_PLUGIN_ROOT}/skills/ship-components/references/shadcn.md`).
Words for errors, empty states and confirmations → `copy-clarity.md`.

---

## 1. Field rules

| Rule | Level | Notes |
|---|---|---|
| Visible label on every field; placeholder is never the label | REQ 3.3.2 | Placeholders vanish on input and usually fail contrast. |
| Declare input purpose | REQ 1.3.5 | `autocomplete` (`email`, `given-name`, `street-address`, `one-time-code`, `new-password` …) / iOS `textContentType`. |
| Right keyboard | PLATFORM | `type`/`inputmode` (`email`, `tel`, `numeric`, `decimal`); iOS `keyboardType`, `submitLabel`. |
| Allow paste and password managers everywhere | REQ 3.3.8 | Never block paste in password, confirm-password or OTP fields. Prefer passkeys / Sign in with Apple / magic links over passwords. |
| Don't ask twice | REQ 3.3.7 | Prefill from earlier steps; "Same as shipping address". |
| Mark the exceptions: "(optional)" on optional fields | EXPERT (GOV.UK) | If you must mark required fields instead, explain the marker once at the top. Expose the required state (`required` / `aria-required`). |
| Hint text between label and field | EXPERT (Practical UI, GOV.UK) | Read before typing; the error goes below the field. |
| Field width matches expected length | EXPERT (Practical UI) | Postcode, CVC, year: short; name, email, address: full. |
| Radio buttons while the options fit (up to about 10); select or combobox for more | EXPERT (Practical UI) | All choices visible, one tap. iOS: a segmented control for 2 to 4 short options, a Picker for more. |
| A stepper for small counts; a checkbox applies on submit, a switch applies now and says what on means | EXPERT (Practical UI) | iOS has no checkbox: `Toggle` (applies now) or a checkmark row. |
| An opt-in that needs detail reveals its field (tick, then the required field), never an optional field beside it | EXPERT (Practical UI) | |
| One column | EXPERT (Baymard, Practical UI) | Exception: tightly related short fields on one row (city + postcode). |
| Accept messy input | SHIP (Postel) | Strip spaces/dashes in card and phone numbers; don't impose one national phone format. |
| Ask only what has a known use; a hard field explains itself inline | EXPERT (GOV.UK, Nielsen) | Name the use in the hint ("For booking reminders by text"); failure states link to help. |
| Memorable dates (a birthday, an expiry): day, month and year fields with a numeric keyboard and an example | EXPERT (GOV.UK) | A calendar only for near dates (a booking). iOS: `DatePicker` (compact) fits both. |
| Names: one full-name field unless a use needs the parts; any characters, long values | EXPERT (GOV.UK) | `autocomplete="name"`, iOS `.name`. |
| Addresses: a lookup with a manual fallback; only line 1 required; free text abroad | EXPERT (GOV.UK) | iOS: MapKit search completion. |
| Passwords: a Show toggle, never a confirm field; one length rule shown before typing, no composition rules | EXPERT (NIST 800-63B, GOV.UK) | Passkeys first (row above). iOS: a custom Show keeps the same `textContentType` on both fields. |
| Email: an email keyboard and autofill, no autocorrect, no confirm field; verify by a code or a link | EXPERT (GOV.UK) | |

## 2. Validation

- **When (SHIP):** validate a field on blur, not on every keystroke. Once a field shows an error,
  re-validate as the user types so the error clears the moment it's fixed. Validate everything on
  submit. Live checks are fine where they help the user decide (username availability, a
  password's length as it's typed).
- **Where (REQ 3.3.1/3.3.3):** error text directly below its field, tied to it
  (`aria-describedby` + `aria-invalid`), with an icon so it isn't color-only. On submit with
  several errors, also show a summary at the top that links to each field and move focus to it
  (or to the first invalid field). The summary counts the problems and uses the inline words; on
  the web the page title starts "Error:"; on iOS, move VoiceOver focus to the first error and
  announce the count.
- **What:** say what's wrong and how to fix it, in the user's terms ("Enter a date in the past",
  not "Invalid input"). Words → `copy-clarity.md` §2.
- **Don't disable submit to signal "incomplete" (SHIP).** Disabled buttons drop out of focus
  order and explain nothing; keep submit enabled and show errors on submit. Exception:
  type-to-confirm for irreversible destructive actions.
- **Double submit:** submit shows a loading state and ignores repeats until the request settles.

## 3. Multi-step flows

- Show position and remaining effort ("Step 2 of 4").
- Back never loses data; long flows save progress and can resume.
- Put the costly questions after the user has seen value (sign-up after a first result, payment last).
- One topic per step on phones; review screen before an irreversible submit.
- **Long or branching entry (EXPERT, GOV.UK):** one question (or one tight group) per screen, with
  the question as the heading; a start screen saying what it's for, what to have ready and how
  long; a task list with a status per section; check answers, each with a Change link that
  returns to the list; a confirmation that says it's done, gives a reference and says what
  happens next and when. Steps say Continue; the last button names the commitment ("Pay £20").
  Edit and settings screens stay one form.
- On the web the primary sits under the fields and Back is a quiet link at the top; native flows
  use the system back.

## 4. Feedback patterns

Match feedback weight to the event (`ux-principles.md` §5):

| Event | Pattern |
|---|---|
| Routine success (saved, copied) | The control changes first ("Saving…", then "Saved"); a toast only when the result is off screen; status announced (REQ 4.1.3) |
| Reversible destructive (archive, remove) | Do it, then toast with **Undo** — no confirm dialog |
| Irreversible / high-impact (delete account, send money) | Confirmation dialog naming the object and consequence; type-to-confirm for the worst cases |
| Cancel or downgrade a plan | As easy as joining: one confirmation at most, then what stops, what's kept, and the date (`psychology.md` §4). Never type-to-confirm |
| Field error | Inline below the field |
| System failure (offline, server error) | Inline banner near the affected content with Retry; keep the user's input |

**Toasts (REQ 2.2.1 + 4.1.3, SHIP timing):**
- Text-only confirmations may auto-dismiss — SHIP default ≥ 4 s, longer for longer text, paused
  while hovered or focused; announced via `role="status"` / an accessibility announcement.
- Toasts with an action (Undo, Retry, View) persist until dismissed, or the action is also
  reachable elsewhere (e.g. Undo in the menu). Errors that need action aren't toasts.
- Placement: consistent per app; on phones keep clear of the tab bar and home indicator.
- Stack or replace — never pile more than a few.

**Disabled states:** dimmed (Material: 38% content, 12% container), not interactive, still
recognisable, and explained nearby ("Add a payment method to continue"). Disabled controls are
exempt from contrast rules — the explanation text is not. Prefer an enabled control that explains
on use; one that must be disabled stays focusable (`aria-disabled`). A paid feature shows a lock and
opens the upgrade, never a dead button.

**Loading states:** skeletons that match the final layout for content (no layout shift when it
arrives); a spinner or inline progress for short actions; progress with an estimate for long
jobs. Give skeletons an accessible "Loading …" label rather than announcing every placeholder.

**Empty states:** say what will appear here, why it's empty (first use, no results, filtered
out, cleared), and offer the next action. A filtered-out empty state offers "Clear filters".

## 5. QA (Test)

- [ ] Submit empty → every required field shows a specific inline error; focus moves to the summary or first error; no request sent.
- [ ] Invalid values per type (email without domain, Feb 30, letters in numbers, emoji in names) → specific errors.
- [ ] Valid edge values accepted: international phone numbers, apostrophes and hyphens in names, long addresses, non-Latin scripts.
- [ ] Rapid submit (5×) on a throttled network → one request; button stays busy until done.
- [ ] Paste and password-manager/passkey autofill work in every field, including OTP; iOS shows the one-time-code suggestion.
- [ ] Back and forward through a multi-step flow keeps entered data; reload/resume works if promised.
- [ ] Every empty state (first use, no results, filtered, cleared) renders intentionally.
- [ ] Toasts: announced by the screen reader; action toasts don't disappear before they can be reached; timing consistent.
- [ ] Keyboard only: every field and error reachable; errors read with their field.

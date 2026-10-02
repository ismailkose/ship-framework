<!-- ship-reference
id: web-a11y
kind: platform
sources: https://www.w3.org/TR/WCAG22/ (2026-09-23); https://github.com/jsx-eslint/eslint-plugin-jsx-a11y (rules; 2026-09-28); eslint-config-next 16.2.1 (its six jsx-a11y rules, all warnings; 2026-09-28); https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/ (2026-09-23); https://www.w3.org/WAI/ARIA/apg/patterns/ (2026-09-23); https://www.w3.org/TR/using-aria/ (2026-09-23); https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element (2026-09-23)
reviewed: 2026-09-23
-->

# Web Accessibility — WCAG 2.2 AA on the web

> **Agent routing:** Arc → Section 1 · Dev → Sections 1–2 · Crit, Pol → Sections 2 and 4 ·
> Eye → Section 4 · Test → Sections 3–4
>
> **Requirement:** WCAG 2.2 Level AA (W3C Recommendation since 2023-10-05) — precedence
> line 1. Nothing below it (product decision, taste, expert source) waives an A/AA criterion.
> **Scope:** how to meet and test it *on the web* — HTML, ARIA, APG patterns, browser tooling.
> The platform-neutral requirement map, Ship's defaults above AA, contrast method and
> verification passes live in `ux/references/accessibility.md` (§1, §3, §4, §6); this file
> doesn't restate them.

---

## Section 1: Semantic HTML first

The native element brings keyboard support, focus, role and name for free. Pick it before
reaching for ARIA.

| Purpose | Element | Never |
|---|---|---|
| Action on this page | `<button type="button">` (`type="submit"` in forms) | `<div onClick>`, `<a href="#">` |
| Go to a URL or anchor | `<a href>` / framework `<Link>` | `<button>` or `onClick` navigation |
| Page regions | one `<main>`, `<header>`, `<nav>` (labelled if more than one), `<footer>`, `<aside>` | div-only layout |
| Headings | `<h1>`–`<h6>` in outline order; one `<h1>` per page | styled `<div>` as heading |
| Form field | `<label for>` + `<input>`; `<fieldset>` + `<legend>` for groups | placeholder as label |
| Modal | `<dialog>` opened with `showModal()` | a positioned `<div>` |
| Disclosure | `<details>`/`<summary>` when styling allows | custom toggle without state |
| Data grid | `<table>` with `<th scope>` | div grid for tabular data |

- `<html lang="…">` set; `lang` on inline passages in another language.
- Unique, descriptive `<title>` per route (Next: `metadata.title`).
- `<dialog>` + `showModal()` makes the rest of the page inert, closes on Esc, and restores
  focus to the opener when it closes — prefer it to hand-built modals.

## Section 2: ARIA, focus and APG patterns

**ARIA rules of use.**
1. If a native element or attribute does the job, use it — no ARIA.
2. Don't change native semantics (`<h2 role="tab">` → wrap instead).
3. Every interactive ARIA control is keyboard operable.
4. Never `role="presentation"` or `aria-hidden="true"` on a focusable element.
5. Every interactive element has an accessible name.

**Names.** Visible text is the name. Icon-only controls get `aria-label` (or visually hidden
text). The name contains the visible label text (2.5.3). `title` alone is not a name.
Decorative images `alt=""`; decorative SVG `aria-hidden="true"`.

**Composite widgets follow the APG pattern** — keyboard contract, roles and states. Link the
pattern in the PR or plan; use a headless primitive that implements it (react-patterns.md
Section 3).

| Widget | APG pattern | Keyboard contract (essentials) |
|---|---|---|
| Modal | [Dialog (Modal)](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) | Focus moves in; Tab cycles inside; Esc closes; focus returns to opener |
| Menu from a button | [Menu Button](https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/) | Enter/Space/↓ opens to first item; arrows move; Esc closes to button |
| Tabs | [Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) | One tab stop; ←/→ between tabs; `aria-selected`; panel labelled by tab |
| Autocomplete | [Combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) | Focus stays in input; ↓/↑ move `aria-activedescendant`; Enter selects; Esc clears/closes |
| Show/hide | [Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) | Button with `aria-expanded`; Enter/Space toggles |
| Accordion | [Accordion](https://www.w3.org/WAI/ARIA/apg/patterns/accordion/) | Header buttons with `aria-expanded`; panels follow |
| Listbox | [Listbox](https://www.w3.org/WAI/ARIA/apg/patterns/listbox/) | Arrows move; selection state announced |
| Tooltip | [Tooltip](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) | Shows on hover *and* focus; Esc dismisses; hoverable (1.4.13) |
| Switch | [Switch](https://www.w3.org/WAI/ARIA/apg/patterns/switch/) | `role="switch"` + `aria-checked`, or a checkbox |

**Focus management.**
- Visible focus on everything focusable: `:focus-visible` with an outline that contrasts ≥ 3:1
  against its surroundings. `outline: none` only with a replacement.
- Focus isn't hidden behind sticky headers, cookie bars or chat widgets (2.4.11): set
  `scroll-padding-top` to the sticky height; dismiss or avoid overlays that cover focus.
- Client-side route change: move focus to the new page's `<h1>` (or `<main>` with
  `tabindex="-1"`) and let the title change announce it.
- After deleting the focused item, move focus to a sensible neighbour — never to `<body>`.
- Background content behind a non-`<dialog>` overlay gets `inert`.
- DOM order = visual order; no positive `tabindex`.

**Status messages (4.1.3).** Toasts, "Saved", result counts: a `role="status"` (polite) or
`role="alert"` (errors, sparingly) region that is **already in the DOM** before its text
changes — a region inserted together with its message is often not announced. Keep it rendered
while empty: `display: none` (`hidden`, Tailwind's `empty:hidden`) takes it out of the tree too.

**Forms.** Label every control; group radios/checkboxes with `<fieldset>`/`<legend>`; tie
errors to the field with `aria-describedby` and `aria-invalid="true"`; on submit, move focus to
the first invalid field (or an error summary linking to fields). Rules for wording and timing:
`ux/references/forms-feedback.md`.

## Section 3: QA — web tooling and test steps

The platform-neutral passes (keyboard walk, screen reader, text size, contrast in every mode,
target measurement) are defined in `ux/references/accessibility.md` §6. On the web, run them
with these tools, on the primary flow of every screen that changed:

1. **Automated, in the e2e suite:** `@axe-core/playwright` —
   `new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze()`;
   fail the test on any violation. Open every dialog, menu and sheet before its scan: closed
   overlays aren't in the page. In review, the web scan adds design-quality checks
   (web/SKILL.md). Automated green is not conformance.
   **Lint:** axe can't see click handlers, and Next's default lint config only warns on six
   `jsx-a11y` rules, none about them. Add `jsx-a11y/click-events-have-key-events`,
   `no-static-element-interactions`, `no-noninteractive-element-interactions` and
   `interactive-supports-focus` as errors, so a clickable `<div>` fails the build.
2. **Keyboard:** Tab/Shift+Tab, Enter/Space, arrows inside composite widgets, Esc on overlays;
   watch that focus is never lost to `<body>` after route changes or deletions.
3. **Screen readers:** VoiceOver + Safari and NVDA + Firefox or Chrome. Check the headings and
   landmarks lists, not only linear reading.
4. **Reflow and zoom:** Playwright viewport 320×800 for 1.4.10; browser zoom 200% for 1.4.4.
5. **Text spacing (1.4.12):** inject
   `* { line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important } p { margin-bottom: 2em !important }`
   and look for clipped or overlapping text.
6. **User preferences:** emulate `prefers-reduced-motion: reduce` and
   `prefers-color-scheme: dark` (`page.emulateMedia`), and `forced-colors: active` (Windows
   contrast themes: focus, borders and icons must stay visible — use `currentColor`/system
   colors, not background images, for meaning).
7. **Target size (2.5.8):** measure the hit box in DevTools (computed width/height including
   padding), not the icon.

## Section 4: WCAG 2.2 AA — web checks (pass/fail)

The requirement text for every A/AA criterion is in `ux/references/accessibility.md` §1 —
this table adds only how each one fails *on the web* and how to check it. Any failure in a
primary flow blocks shipping (hardening-guide.md §3, row 4). ★ = new in 2.2.

| SC | Common web failure | Check |
|---|---|---|
| 1.1.1 | `<img>` without `alt`; icon `<button>` with no name; informative CSS background image | axe; every `<img>` has `alt` (empty when decorative) |
| 1.3.1 | Styled `<div>` headings, lists, tables; radio group without `<fieldset>` | Headings/landmarks list in the screen reader |
| 1.3.5 | Personal-data inputs without `autocomplete` tokens (`name`, `email`, `tel`, `street-address`, `cc-number`…) | Inspect each input |
| 1.4.3 / 1.4.11 | Token pair passes in light, fails in dark or on hover; placeholder too faint; focus ring ≤ 3:1 | Measure rendered colors in both themes and each state |
| 1.4.10 | Fixed-width containers, `min-width` layouts, horizontal scroll at 320px | Section 3 step 4 |
| 1.4.12 | Fixed `height` on text boxes, `overflow: hidden` clipping | Section 3 step 5 |
| 1.4.13 | Tooltip that vanishes when the pointer moves onto it, or can't be closed with Esc | Hover, move onto it, press Esc |
| 2.1.1 / 2.1.2 | `onClick` on non-focusable elements; custom widget without arrow keys; focus stuck in an embed | Section 3 step 2 |
| 2.4.1 | No skip link; no `<main>` | First Tab shows "Skip to content"; landmarks list |
| 2.4.2 | Same `<title>` on every route | Check `document.title` per route |
| 2.4.3 | Positive `tabindex`; DOM order differs from visual order (CSS `order`, absolute positioning) | Tab order matches reading order |
| 2.4.7 | `outline: none` with no `:focus-visible` replacement | Tab through; focus always visible |
| ★ 2.4.11 | Sticky header, cookie bar or chat bubble covers the focused element | Tab down a long page; `scroll-padding-top` set |
| 2.5.3 | `aria-label` that differs from the visible text ("Submit form" on a "Send" button) | Name starts with the visible label |
| ★ 2.5.7 | Sortable list, slider, kanban or map with drag only — or drag plus arrow keys and nothing clickable | A click/tap path does the same thing (move buttons, a "Move to…" menu, tap-to-place, click on a slider track). Keyboard support is required too, but it doesn't satisfy 2.5.7 |
| ★ 2.5.8 | 16px icon buttons packed together; tiny close buttons on chips | Hit box ≥ 24×24 CSS px or spacing rule (Section 3 step 7) |
| 3.1.1 | Missing `<html lang>` | Inspect root element |
| 3.2.1 / 3.2.2 | `<select onChange>` that navigates; auto-submit on blur | Changing a value never changes context by itself |
| ★ 3.2.6 | Help/contact link moves between layouts | Compare page templates |
| 3.3.1 / 3.3.3 | Error shown only by red border; message not tied via `aria-describedby` | Screen reader reads the error on the field |
| ★ 3.3.7 | Checkout asks for the same address twice | Prefill or "same as" option |
| ★ 3.3.8 | Paste blocked on password/OTP; OTP without `autocomplete="one-time-code"`; CAPTCHA without an alternative | Paste works; password manager fills; passkeys offered where auth is custom |
| 4.1.2 | Custom toggle/menu/tabs without APG roles and states | Screen reader announces name, role, state changes |
| 4.1.3 | Toast or "Saved" rendered into a new live region | Section 2 status messages rule |

Ship's defaults above the AA floor (44px touch targets, focus ring, contrast aims) are set in
`ux/references/accessibility.md` §3; product decisions in `design-model.yaml` override them,
never the AA floor.

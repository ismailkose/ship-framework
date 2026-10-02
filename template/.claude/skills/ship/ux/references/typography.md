<!-- ship-reference
id: ux-typography
kind: mixed
sources: https://developer.apple.com/design/human-interface-guidelines/typography (2026-09-23); https://m3.material.io/styles/typography (2026-09-23); https://www.w3.org/TR/WCAG22/ (1.4.4, 1.4.12; 2026-09-23); https://www.w3.org/TR/css-fonts-4/ (2026-09-23); books-and-sites (Matthew Butterick, Practical Typography; Robert Bringhurst, The Elements of Typographic Style; Adham Dannaway, Practical UI)
reviewed: 2026-09-28
-->

# Typography

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`).
**Registry first:** if `design-model.yaml` has `primitives.type` (family, scale) and semantic
text roles, use them — this file is for choosing a system or auditing one, never for overriding it.
A new size or family is a registry change (`/shipmate design --tokens`), not an inline value.

---

## 1. Hard requirements

- **REQ 1.4.4:** text scales to 200% without loss. Native: use text styles that follow the user's
  size setting. Web: size in `rem`/`em`, never set `html { font-size }` in px, never disable zoom
  (`user-scalable=no`, `maximum-scale=1`).
- **REQ 1.4.12:** layouts survive line-height 1.5 / letter-spacing 0.12em / word-spacing 0.16em /
  paragraph spacing 2em set by the user — no fixed-height text containers, no clipped labels.
- **REQ 1.4.3:** text contrast 4.5:1 (3:1 at ≥ 24 px, or ≥ 18.7 px bold). Thin weights read worse
  than their ratio — pair light weights with larger sizes.

## 2. Platform type systems (PLATFORM)

**iOS / iPadOS.** Default body 17 pt, minimum 11 pt (HIG). Use the built-in text styles
(`.largeTitle … .caption2`) so Dynamic Type works, including the five accessibility sizes. The
system fonts (SF Pro, New York) are variable with dynamic optical sizes — don't hand-pick
Text/Display cuts. Custom fonts must scale: `Font.custom(_:size:relativeTo:)` or `UIFontMetrics`.
Test at the largest accessibility size — layouts switch to vertical stacks
(`ViewThatFits`, `dynamicTypeSize` checks) rather than truncating.

**Android / Material 3.** Type roles: Display, Headline, Title, Body, Label (each L/M/S). Size in
`sp`; since Android 14 font scaling is nonlinear up to 200%, so large text grows less than small.

**Web.** Browsers default to 16 px; Ship's body default is `1rem` (SHIP). On iOS Safari,
`font: -apple-system-body` opts web text into Dynamic Type. Fluid sizes must keep a `rem` term
so zoom still works:

```css
--text-body: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);   /* never pure vw */
--text-display: clamp(2rem, 1.4rem + 3vw, 3.5rem);
```

## 3. Choosing a scale (SHIP defaults unless the registry says otherwise)

- **Ratio:** 1.2 (minor third) or 1.25 (major third) for dense product UI; 1.333 (perfect fourth)
  or 1.5 (perfect fifth) for expressive/marketing surfaces; 1.618 is the golden ratio, rarely
  useful beyond 3 steps. Round results to whole px/pt on a 4-pt grid for line heights.
- **Hierarchy must be visible at a glance:** adjacent heading levels differ by size *and* weight
  or color. If H2 and H3 look alike at 25% zoom, collapse a level or increase the step.
- **Roles, not raw sizes:** name tokens by role (`display`, `title`, `body`, `label`, `caption`)
  so iOS text styles, Material roles and CSS variables map 1:1 from `design-model.yaml`.
- **Line height:** body ~1.4–1.6 (web default 1.5); headings 1.1–1.3; small labels ~1.3–1.4.
  Bringhurst and Butterick put comfortable body leading around 120–145% — 1.5 is Ship's web
  default because it also matches the 1.4.12 stress test.
- **Line length:** 45–75 characters for reading text (`max-width: 65ch`); UI strings can be shorter.
- **Weights:** at most three in a product (e.g. 400 / 600 / 700). Avoid thin/light weights
  for body and small text (HIG says the same).
- **Letter-spacing:** tighten large display sizes slightly; add tracking to all-caps labels;
  never track body text (system fonts track themselves). All caps only for a few words.
- **Reading text (EXPERT: Butterick, Practical UI):** aligned to the start; justified only with
  hyphenation; centered only for short display lines; never hyphenate headings, labels or URLs.
  Paragraphs get a space or an indent, never both. In reading text, three heading levels at
  most, set apart by weight and space before size, with more space above than below. Long
  reading surfaces on the web set body at 18 px or more; native text follows Dynamic Type.

## 4. Choosing faces (EXPERT: Butterick, Practical UI · SHIP limits)

- **Two families maximum** (SHIP; `design-model.yaml` requires a documented reason for a second).
  One well-drawn family with a real weight range beats a decorative pair.
- **Pair by contrast** — differ clearly in structure (serif/sans, geometric/humanist), share a
  similar x-height and mood. Two near-identical sans faces look like a mistake.
- **Body face:** the platform system face or a text face drawn for screens (good x-height, open
  apertures, distinct Il1 and 0O). Display faces are for display sizes only.
- **Licensing:** confirm the license covers app embedding / web serving before it enters the registry.
- **The system face has its own range:** SF Rounded, New York (serif), SF Mono and condensed or
  expanded widths give a product a voice without a licensed font (`type.design`, `type.width` in
  `design-model.yaml`; web falls back to `ui-rounded`, `ui-serif`, `ui-monospace`).

Starting points when nothing better exists — these are the probable pick for each feel. A face taken
from the product's own world (its signage, packaging, menu) beats them (`design-research.md` §2):

| Product feel | Display | Body |
|---|---|---|
| Calm utility | System (SF / Roboto / system-ui) | System |
| Editorial, warm | A text serif (e.g. Source Serif, Newsreader) | Its sans companion or system |
| Precise, technical | A grotesk or mono accent | System or a neutral grotesk |
| Expressive consumer | One distinctive display face | System |

## 5. Details that separate crafted from default

- **Numbers:** tabular figures anywhere numbers align or update — tables, prices, timers,
  counters (`font-variant-numeric: tabular-nums`; SwiftUI `.monospacedDigit()`).
- **Wrapping over truncation.** Truncate only single-line UI (table cells, tabs, breadcrumbs), and
  make the full text reachable by focus and touch (a detail view or an accessible tooltip —
  `title` alone isn't reachable on touch or by most AT). Clamp previews to 2–3 lines.
- **Headings:** `text-wrap: balance` (Baseline 2024) for short headings; `pretty` for paragraphs
  where supported — both progressive enhancement.
- **Real punctuation:** curly quotes, the ellipsis character, a non-breaking space between number
  and unit ("10 MB"). No dashes as punctuation in product copy (`copy-clarity.md` §3).
- **Case:** sentence case for UI labels and buttons unless the registry chose title case — pick
  one per element type and keep it (`copy-clarity.md`).
- **Emphasis:** bold or italic, sparingly, never both; never underline or capitals for emphasis.
  In a sans face, weight reads better than italic.
- **Links in text:** one quiet cue, a thin offset underline, or a colour 3:1 against the text
  around it plus a focus cue (REQ 1.4.1); underline only links. iOS shows links in the tint:
  check that 3:1, or underline them.
- **On one line:** mixed sizes share a baseline; an icon beside text matches its size and weight
  (a meaningful icon keeps 3:1). Truncate in the middle when items share a prefix (file names).

## 6. Loading fonts (web)

- Self-host WOFF2; subset to the scripts you ship. Variable fonts need only `format("woff2")`
  and a `font-weight` range in `@font-face`; `font-optical-sizing: auto` uses an `opsz` axis if present.
- `font-display: swap` for display faces; consider `optional` for body text to avoid layout
  shift. Match fallback metrics with `size-adjust` / `ascent-override` to cut CLS.
- Preload only the one or two files used above the fold. Next.js: `next/font` handles
  self-hosting and fallback metrics — web skill owns the details.

## 7. Audit checklist (Pol, Eye)

- [ ] Every text uses a registry role/token; no raw sizes, families or weights in components.
- [ ] Text follows the user's size setting (Dynamic Type / sp / rem); largest size tested, nothing clipped.
- [ ] Hierarchy readable at 25% zoom; adjacent levels clearly distinct.
- [ ] Body line length ≤ ~75 characters; line height within the ranges above.
- [ ] ≤ 3 weights, ≤ 2 families; no thin weights at small sizes.
- [ ] Contrast meets REQ in every mode (check muted/secondary text first).
- [ ] Tabular figures on aligned/changing numbers; no truncation without a way to read the rest.

<!-- ship-reference
id: ux-color
kind: mixed
sources: https://www.w3.org/TR/WCAG22/ (1.4.1, 1.4.3, 1.4.11; 2026-09-23); https://www.w3.org/TR/css-color-4/ and https://www.w3.org/TR/css-color-5/ (2026-09-23); https://web.dev/baseline (2026-09-23); https://developer.apple.com/design/human-interface-guidelines/color (2026-09-23); https://m3.material.io/styles/color/roles (2026-09-23); books-and-sites (Josef Albers, Interaction of Color; Adham Dannaway, Practical UI); impeccable@9d715cc (ideas only: action vs field colour by surface, text on a coloured field; pbakaus/impeccable, Apache-2.0)
reviewed: 2026-09-28
-->

# Color

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`).

**Registry first.** Color values live only in `design-model.yaml` → `primitives.color` (hex);
`semantic` roles reference primitives by dot-path; components reference semantic roles only
(`.claude/skills/ship/design/references/design-model-schema.md`). `DESIGN.md` explains *why*
(intent, mood, rationale) and never carries values. Changing a color = editing the registry,
then `design_model.py validate`; never a hex in a component.

---

## 1. Requirements (REQ)

| Rule | Check |
|---|---|
| 1.4.3 text contrast | 4.5:1; 3:1 for ≥ 24 px (≥ 18.7 px bold). Every mode and state. |
| 1.4.11 non-text contrast | 3:1 for control boundaries, state indicators (checked/selected), focus rings, meaningful icons and chart marks. |
| 1.4.1 use of color | Meaning never by hue alone: error = color + icon + text; chart series = color + label/pattern/marker. |

Reference grays on white (WCAG 2 ratio): `#949494` 3.0:1 (large text / non-text only) ·
`#767676` 4.5:1 (lightest passing body gray) · `#666666` 5.7:1 · `#595959` 7.0:1 · `#333333` 12.6:1.
Compute real pairs — don't estimate from lightness. APCA is not a requirement (`accessibility.md` §4).

## 2. Token architecture

```
primitives (ramps, hex)  →  semantic roles  →  component tokens
brand.500, ink.900          primary, on-primary     button.primary.bg = primary
                            surface, on-surface     card.bg = surface.raised
                            error, on-error …
```

- **Pairs, not singles:** every background role has an `on-` role that passes contrast against
  it, in every mode (Material's naming; Ship's registry uses the same idea).
- **Intent roles are reserved:** `error`, `warning`, `success`, `info` mean exactly that — never
  reuse `error` red as a brand accent.
- **States derive from roles:** hover/pressed/selected as overlays or adjacent ramp steps; define
  them once in the registry rather than per component.
- **Modes:** `design-model.yaml` defaults to `modes: [light, dark]`. Add increased-contrast
  variants for key pairs on Apple platforms (HIG asks for them; system colors already have them).

Platform mapping: iOS → emitted `Theme.swift` / asset catalog with Any/Dark (+ High Contrast)
appearances · Android → M3 color roles (`primary`, `onPrimary`, `surfaceContainer*` …; dynamic
color is an option, not a default, when the brand matters) · Web → CSS variables (shadcn's role
names if the project uses shadcn — `.claude/skills/ship/components/references/shadcn.md`).

## 3. Building palettes

- **Work in OKLCH** for ramps: equal steps in L look like equal steps, unlike HSL. Keep hue
  roughly constant, lower chroma toward the lightest and darkest stops, and check that each stop
  is in gamut. OKLCH is CSS Color 4 and Baseline 2023 (Chrome 111, Safari 15.4, Firefox 113).
- **OKLCH L is not contrast.** Pick candidates by L, then verify with the WCAG ratio.
- **Wide gamut (P3):** most Apple displays and many phones show Display P3. On the web,
  `color(display-p3 …)` or out-of-sRGB `oklch()` behind `@media (color-gamut: p3)` with an sRGB
  fallback; the browser gamut-maps otherwise. On iOS, author P3 in the asset catalog. The
  registry stores sRGB hex today — P3 variants are a product decision, record them in `DECISIONS.md`.
- **Modern CSS helpers:** `color-mix(in oklch, …)` (Baseline 2023) for tints and overlays;
  relative color syntax `oklch(from var(--x) calc(l - .08) c h)` and `light-dark()` (both
  Baseline 2024). Emitters may use them; hand-written component CSS still references tokens.
- **Neutrals carry the UI.** Most pixels are neutral. A tinted ramp can read more cohesive than pure
  gray when the hue comes from the product (its material, its accent). A warm tint by habit is how
  pages drift to cream paper — `design-quality.md` §3, AI default look.

## 4. Applying color (EXPERT: Practical UI, Albers · SHIP)

- **Grayscale first:** hierarchy must work in black and white; color then amplifies it. If the
  screen collapses without color, fix size/weight/spacing first.
- **The action colour is for interaction:** links, primary buttons, selected tabs, focus,
  toggles-on. Not headings, static badges or decoration — when everything is in the action colour,
  nothing reads as tappable.
- **A field colour may own whole regions** on surfaces that persuade (a landing page, onboarding, a
  paywall) when the direction commits to one (`design-research.md` §2, colour strategy). Keep it a
  separate token from the action colour; on working screens, colour marks actions and state.
- **Text on a coloured field** takes the field's own hue (a darker or lighter step), never gray:
  gray on colour looks washed out. Check the ratio on the field, not on white.
- **One primary action per view** carries the filled brand color; others go secondary/tertiary
  (`.claude/skills/ship/components/references/components.md` §4).
- **A brand too light or too dark to pass** on its ground: actions take the text colour (outlined
  or underlined) and the brand turns decorative. A brand hue that already means something (red)
  stays off actions (EXPERT, Practical UI). The validator checks the action colour on every ground.
- **Tinted transparency:** hover fills, selection, subtle surfaces and borders as low-alpha tints
  of the ink/brand hue (e.g. `rgb(0 20 120 / .04)`), so they sit on any surface in either mode.
- **Context shifts color:** the same swatch looks different on different grounds (Albers) — judge
  colors in place, on real surfaces, in both modes, never as isolated chips.
- **Category mood is a starting point, not a rule.** "Finance = blue" gives you the median app.
  Start from the product's own material and the direction's idea (`design-research.md` §2).

## 5. States and special cases

- **Disabled:** Material dims disabled content to 38% and containers to 12% opacity. Disabled
  controls are exempt from contrast, but must still read as the same control, and should say
  why they're disabled (`forms-feedback.md`).
- **Color vision deficiency:** roughly 1 in 12 men and 1 in 200 women have some form. Check
  red/green and blue/yellow pairs with a simulator (browser DevTools vision emulation, macOS/iOS
  Color Filters) and add icons/labels where hue carries meaning.
- **Charts:** a categorical palette with distinguishable lightness steps, direct labels over
  legends, and a data table or text summary.
- **Text on imagery or glass:** measure against the worst region or add a scrim/solid layer.
- **Dark mode** is its own pass → `dark-mode.md`.

## 6. Elevation (SHIP)

3–5 elevation levels, each visibly distinct: flat → raised (cards) → overlay (menus, popovers)
→ modal. In light mode, shadows carry it (soft, low-alpha, consistent light direction); in dark
mode, lighter surfaces carry it (`dark-mode.md` §2). Shadow values belong in the registry.

## 7. Audit checklist (Pol, Eye, Crit)

- [ ] No raw color literals in components; every color resolves to a semantic role.
- [ ] Every text/background and control/background pair passes REQ in light, dark and increased contrast, in every state.
- [ ] No meaning by hue alone (errors, status, charts, required fields).
- [ ] The action colour only on interactive elements (a field colour only by the direction's colour
  strategy); text on a coloured field in its hue, not gray; one filled primary per view.
- [ ] Intent colors used only for their intent.
- [ ] Ramps built on perceptual steps; neutrals tinted consistently.
- [ ] CVD simulation run on status-heavy screens and charts.

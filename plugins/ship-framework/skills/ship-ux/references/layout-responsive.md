<!-- ship-reference
id: ux-layout-spacing
kind: mixed
sources: https://www.w3.org/TR/WCAG22/ (1.4.10 Reflow; 2026-09-23); https://developer.apple.com/design/human-interface-guidelines/layout (2026-09-23); https://m3.material.io/foundations/layout/applying-layout/window-size-classes (2026-09-23); https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes (large and extra-large; 2026-09-28); https://developer.android.com/develop/ui/views/layout/edge-to-edge (2026-09-23); https://web.dev/baseline (container queries; 2026-09-23); books-and-sites (Nathan Curtis, Space in Design Systems; Adham Dannaway, Practical UI)
reviewed: 2026-09-23
-->

# Layout, Spacing & Responsive

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`).
**Registry first:** `design-model.yaml` → `primitives.spacing` (`unit`, optional named `scale`)
and `primitives.radius` are the only spacing/radius values a component may use. A new value is
a registry change, not a one-off.

---

## 1. Plan the layout (Arc)

- **Smallest screen first.** Designing for the narrowest width forces the priority call: what
  must be visible, what can wait, what goes behind disclosure. Larger layouts add, they don't rescue.
- **Content decides breakpoints.** Break where the content breaks, not at device names. Prefer
  intrinsic layouts (`grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr))`, flex-wrap)
  and **container queries** (Baseline 2023) for components that live in different widths.
- **Native adapts to size classes, not devices.**
  - iOS/iPadOS: compact vs regular size classes; iPad apps run in resizable windows, so any width
    can happen — use `ViewThatFits`, adaptive stacks, `NavigationSplitView` that collapses.
  - Android: window size classes by width: compact (under 600 dp), medium (600 to 839), expanded
    (840 to 1199), large (1200 to 1599) and extra-large (1600 and up). Large and extra-large are
    reported only when the app opts in (`supportLargeAndXLargeWidth = true`).
- **Test widths (SHIP):** 320 (REQ 1.4.10 reflow), 375 and ~430 (small/large phones), 768, 1024,
  1440. Also landscape phone and a split-screen tablet.

## 2. Spacing system

- **Base unit (SHIP):** 4 (registry default `unit: 4`); common steps 4, 8, 12, 16, 24, 32, 48, 64, 96.
  Off-scale values (13, 18, 22) are the tell of an unsystematic layout.
- **Proximity rule (SHIP):** space inside a group is clearly tighter than space between groups —
  roughly half or less. Label→field 4–8, field→helper 4, field group→next group 24+.
- **Name spacing by intent (EXPERT, Curtis):** inset (padding inside a container), stack
  (vertical between items), inline (horizontal between items). Registry names like
  `space.stack.md` map cleanly to CSS variables, SwiftUI constants and Compose dimens.
- **Density is a product decision**, recorded in `DECISIONS.md`: dense for tools people use for
  hours (tables, dashboards), spacious for consumer and first-run flows. If both audiences exist,
  a density setting scales spacing tokens (e.g. × 0.75 / 1 / 1.25) — hit areas never shrink.
  Between two steps with no density decision, take the larger (EXPERT, Practical UI).

## 3. Hierarchy with space

- **More space = more importance.** Hero and key sections get the largest gaps; footers the smallest.
- **One alignment per component or section** (EXPERT, Practical UI); actions sit beside the content
  they affect, on its reading edge, so people zoomed in or using a magnifier still find them.
- **Active vs passive whitespace:** passive keeps things from touching; active isolates what
  matters. Use active whitespace on purpose around the one thing per screen.
- **Content over chrome (SHIP heuristic):** on content screens, chrome (bars, toolbars, filters,
  tabs) should take a small share of the first viewport — collapse filters into a sheet/menu,
  let bars minimise on scroll.
- **Contained vs edge-to-edge:** text and forms contained (`max-width: 65ch` for reading,
  ~72–80rem for app shells); media, maps and heroes may bleed to the edges.
- **Radius scale:** small controls get smaller radii than cards and sheets; nested corners are
  concentric (inner radius = outer radius − inset). One radius everywhere looks unconsidered.

## 4. Safe areas, insets and stacking

- **iOS:** respect safe-area insets (never hard-code status bar/home indicator heights);
  backgrounds may extend under bars (`ignoresSafeArea` on backgrounds only), controls may not.
- **Android:** apps targeting Android 15+ are edge-to-edge by default — pad content with
  `WindowInsets` (system bars, IME, display cutout).
- **Web:** `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`
  then `padding: max(1rem, env(safe-area-inset-left))` etc. Use `dvh`/`svh` rather than `100vh`
  for full-height mobile layouts.
- **Fixed/sticky UI** must not cover focused elements (REQ 2.4.11): add `scroll-padding-top/bottom`.
- **Z-index scale (SHIP):** named layers only — base, dropdown, sticky, overlay, modal, toast,
  tooltip — defined once as tokens.

## 5. QA (Test, Eye)

- [ ] No horizontal scroll at 320 px or at 200% zoom (tables/maps excepted).
- [ ] Every test width above: nothing overlaps, truncates unexpectedly, or strands a primary action.
- [ ] Largest text size (Dynamic Type AX / 200% font scale): layouts reflow instead of clipping.
- [ ] Landscape phone: sticky bars leave room for content; sheets and keyboards don't hide the focused field.
- [ ] Real content lengths (long names, 6-digit numbers, other languages) — lorem ipsum hides overflow.
- [ ] Notch / Dynamic Island / home indicator / gesture bar: nothing tappable underneath.
- [ ] All spacing and radius values come from the registry scale.
- [ ] Media has intrinsic size/aspect ratio (no layout shift).

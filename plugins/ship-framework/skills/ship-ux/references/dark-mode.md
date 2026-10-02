<!-- ship-reference
id: ux-dark-mode
kind: mixed
sources: https://developer.apple.com/design/human-interface-guidelines/dark-mode (2026-09-23); https://developer.apple.com/design/human-interface-guidelines/color (2026-09-23); https://m3.material.io/styles/color/roles (2026-09-23); https://www.w3.org/TR/css-color-adjust-1/ (color-scheme; 2026-09-23); https://www.w3.org/TR/WCAG22/ (2026-09-23); impeccable@9d715cc (idea only: light text on dark needs air and no thin weights; pbakaus/impeccable, Apache-2.0)
reviewed: 2026-09-28
-->

# Dark Mode & Theming

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`).
**Registry first:** `design-model.yaml` defaults to `modes: [light, dark]` and requires
`semantic_dark` with the same keys as `semantic` (`background`, `surface`, `text`, `muted`,
`hairline`, `action`, …). Light-only needs `modes: [light]` plus a documented reason in
`DESIGN.md`. Dark values are chosen in the registry — components never branch on the mode.

---

## 1. Design it as a second pass, not an inversion

- **REQ:** every pair meets contrast in dark too (4.5:1 text, 3:1 non-text). HIG adds: for custom
  colors, strive for 7:1 on small text. Check hover/pressed/selected/disabled states in dark separately.
- **Lighter, calmer accents.** Saturated mid-tones vibrate on dark grounds. Move accents to a
  lighter, lower-chroma step of the same hue (Material 3 uses the light tones of its tonal
  palette — around tone 80 — for `primary` in dark). Re-check `on-action` text: it often flips
  from white to near-black.
- **Soften pure white text** on large dark areas (off-white at high contrast reads calmer), but
  never below the REQ ratio.
- **Light text on dark** needs a touch more line height and tracking, and no thin weights: fine
  strokes break up on dark grounds, especially at small sizes.
- **Backgrounds.** iOS: use the system background colors — the base dark background is true
  black and grouped/elevated levels step up. Custom palettes (web, Android) usually use a
  near-black tinted neutral; M3's dark surface is a very dark neutral, not #000.
- **Images and brand assets:** supply dark variants for logos and line illustrations; photos
  usually stay; never `filter: invert()` a UI.
- **Liquid Glass / materials (iOS 26+ design):** HIG asks for both light and dark colors even in
  a single-appearance app, because system materials adapt to what's behind them.

## 2. Depth in the dark

Shadows barely register on dark surfaces. Express elevation with **lighter surfaces**:
- iOS: HIG's *base* and *elevated* background sets — elevated is brighter so a sheet or popover
  over dark content still separates. Use the system colors or mirror their steps in the registry.
- Material 3: `surfaceContainerLowest … surfaceContainerHighest` roles carry elevation.
- SHIP: 3–4 dark surface steps, each visibly lighter; hairline borders help where steps are close.

## 3. Theme selection behaviour

- **Default to the system setting** on every platform, unless a product decision says otherwise.
- **iOS / iPadOS (PLATFORM):** HIG advises against an app-specific appearance setting — honour the
  system. Offer an in-app override only when the product has a real reason (e.g. a reading or
  photo app), recorded in `DECISIONS.md`.
- **Web (SHIP):** follow `prefers-color-scheme`; a System / Light / Dark choice is common and fine.
- **When a choice is offered (any platform, SHIP):** three options — System, Light, Dark. Store the
  *choice*, not the resolved mode: System stays System (never saved as whatever was showing), and
  while it's selected the app follows OS changes live. Light or Dark overrides the OS. One resolved
  appearance drives everything — tokens, native controls, scrollbars, images. If the app already
  has an appearance controller (next-themes, a settings store), keep it and check it against
  these rules rather than adding a second one.

## 4. Implementation road signs

**Web**
- `color-scheme` follows the *resolved* appearance, like the tokens: `light dark` on `:root` only
  while the page follows the OS; `dark`/`light` wherever a theme is pinned (the emitted `tokens.css`
  does this for both `theme_selector` modes). Otherwise native controls and scrollbars can go dark
  on a light page.
- Tokens as CSS variables emitted from the registry; switch with `[data-theme="dark"]` or
  `@media (prefers-color-scheme: dark)` — or `light-dark()` (Baseline 2024) inside token definitions.
- **No flash:** resolve the choice before first paint — an inline `<head>` script reading the stored
  choice, or server-render it from the cookie. (`next-themes` does this for Next.js.) Without a
  controller, this is the whole of it (for `theme_selector: class`, toggle `.dark`/`.light` instead
  of `data-theme`):

```html
<script> /* first thing in <head> */
(() => {
  const key = "appearance", root = document.documentElement, os = matchMedia("(prefers-color-scheme: dark)");
  const choice = () => { try { return localStorage.getItem(key) || "system"; } catch { return "system"; } };
  const apply = (c) => { root.dataset.theme = c === "system" ? (os.matches ? "dark" : "light") : c; };
  apply(choice());
  os.addEventListener("change", () => { if (choice() === "system") apply("system"); });
  window.setAppearance = (c) => { try { localStorage.setItem(key, c); } catch {} apply(c); };
})();
</script>
```
- `<meta name="theme-color" media="(prefers-color-scheme: dark)" content="…">` for browser chrome.

**iOS (SwiftUI)**
- Colors from the emitted theme / asset catalog with Any + Dark (+ High Contrast) appearances;
  prefer semantic system colors (`Color(.systemBackground)`, `.primary`, `.secondary`) where the
  registry maps to `system.*`.
- Read `@Environment(\.colorScheme)` only for assets that truly differ; never to pick token values in views.
- An override, if approved, is `.preferredColorScheme(_:)` at the root (`nil` = follow system — the
  system then updates it live). Store the choice, not the mode:

```swift
enum Appearance: String, CaseIterable {
    case system, light, dark
    var scheme: ColorScheme? { self == .light ? .light : self == .dark ? .dark : nil }
}

struct AppearanceRoot<Content: View>: View {
    @AppStorage("appearance") private var appearance: Appearance = .system
    @ViewBuilder var content: Content
    var body: some View { content.preferredColorScheme(appearance.scheme) }
}
```

**Android (Compose)**
- `darkColorScheme()` / `lightColorScheme()` from the registry; `isSystemInDarkTheme()` for the default;
  dynamic color (Android 12+) only if the brand allows it.

## 5. QA (Test, Eye)

- [ ] Every screen captured in light and dark (native: `xcrun simctl ui booted appearance dark`).
- [ ] Contrast checked per mode and per state, including muted text, borders and focus rings.
- [ ] Elevation still reads in dark (sheets, menus, cards distinguishable).
- [ ] Logos, illustrations, charts and empty-state art legible on both backgrounds.
- [ ] System change while the app is open updates the UI without relaunch (while System is chosen).
- [ ] If a choice is offered: Light/Dark override the OS; switching back to System follows the OS
      again and survives a relaunch/reload as System.
- [ ] Web: no wrong-theme flash on hard reload with a throttled network; form controls and
      scrollbars match the theme.
- [ ] Increase Contrast (iOS) / high-contrast text (Android) still passes and still looks designed.

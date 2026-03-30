# Dark Mode & Theming Reference

> **Agent routing:**
> - **Eve** → Sections 1–2 (design both themes together, color strategy, semantic tokens)
> - **Dev** → Section 2 (implement tokens, theme switching, platform specifics)
> - **Pol** → Section 1 (audit: contrast in both themes, token compliance, wcag ratios)
> - **Eye** → Section 1 (visual quality: desaturation, elevation, image handling, readability)
> - **Test** → Section 3 (verify both themes, contrast, system preference, flash prevention)

---

## Section 1: Dark Mode Design Strategy

### Dark Mode Is Not Inverted Colors

Dark mode is a **separate design system**. It shares the same component structure and layout grid as light mode, but treats surface, color, and depth fundamentally differently. Designing dark mode as an afterthought—inverting hex values or reducing opacity—breaks contrast ratios, makes text unreadable, and feels cheap.

**Start with two parallel systems from day one.** Light and dark themes are co-equal design surfaces, not variants.

### Color Desaturation in Dark Mode

Fully saturated colors on dark backgrounds cause **halation**—bright colors appear to bleed and vibrate into the dark surroundings, creating eye strain and visual discomfort. This is physics: your eye can't resolve the boundary between a bright, saturated blue and black.

**Solution:** Reduce saturation by 15–25% when moving from light to dark theme.
- Light theme primary: `hsl(220, 90%, 56%)` (saturated, punchy)
- Dark theme primary: `hsl(220, 65%, 65%)` (desaturated, lifted luminance)

The shift in both saturation *and* lightness prevents halation while maintaining recognizable color identity.

### Elevation via Luminance, Not Shadow

In light mode, shadows create depth: darker elements recede, lighter elements come forward. On dark backgrounds, **shadows disappear**—a `rgba(0,0,0,0.2)` shadow on `#1a1a1a` is invisible.

Dark mode uses **surface color levels** instead:
- Background: `#0f0f0f` (darkest, furthest back)
- Surface 0: `#1a1a1a` (cards, dialogs)
- Surface 1: `#242424` (hovered cards, subtle lift)
- Surface 2: `#2e2e2e` (floating elements, closest to user)

Each step up increases luminance by ~8–10%. Depth emerges from the **lightness hierarchy**, not shadows.

### Image Handling Across Themes

Logos, illustrations, and photography need careful treatment:
- **White logos** on white cards → invisible in dark mode. Provide dark variants or use transparent backgrounds.
- **Illustrations** with dark outlines on light fills may need complete redraws for dark theme.
- **Photography** often works unchanged, but watch background colors bleeding into text overlays.

Audit every image asset in both themes before shipping.

### Why Semantic Tokens Are Mandatory

Raw hex values (`color: #3b82f6`) break theme switching instantly:
- You can't swap a light-mode blue for a dark-mode blue at runtime.
- Contrast audits become nightmares (is this blue 4.5:1 in dark mode?).
- Maintenance: change one color, find all 47 places it's hardcoded.

**Use semantic tokens instead:**

```
--color-primary: hsl(220, 90%, 56%)    /* light mode */
--color-primary: hsl(220, 65%, 65%)    /* dark mode */

--color-on-primary: hsl(0, 0%, 100%)   /* light: white text */
--color-on-primary: hsl(0, 0%, 5%)     /* dark: dark text */
```

Tokens decouple color logic from component CSS. Theme switching becomes a single operation: swap the token root.

---

## Section 2: Implementation

### Semantic Token Architecture

Build tokens in pairs: **surface + on-surface** pattern.

```
Surface tokens:
  --color-background (main page bg)
  --color-surface (cards, containers)
  --color-surface-variant (subtle fills, borders)

Content tokens:
  --color-on-background (body text)
  --color-on-surface (card text, secondary content)
  --color-on-surface-variant (labels, hints, tertiary)

Intent tokens:
  --color-primary / --color-on-primary
  --color-secondary / --color-on-secondary
  --color-error / --color-on-error
  --color-success / --color-on-success
```

Every "on" token ensures sufficient contrast against its paired surface, verified in both themes.

### System Preference Detection & Manual Override

Respect the user's OS setting via `prefers-color-scheme`, but **allow manual override that persists**.

**Flow:**
1. On first visit, detect `prefers-color-scheme: dark` (CSS media query or JS `window.matchMedia`).
2. Apply matching theme.
3. User clicks "switch theme" → store choice in cookie or localStorage (prefixed `ship_theme_preference`).
4. On return visits, read stored preference *before* rendering to prevent flash.

**SSR requirement:** Read the cookie server-side. Render the correct theme in initial HTML.

### Flash Prevention

A flash of wrong theme on page load = broken UX. Users notice.

**Prevention strategy:**
1. Read theme preference in an inline `<script>` (before any CSS/JS loads).
2. Apply a data attribute to `<html>` immediately: `data-theme="dark"`.
3. All CSS uses this attribute selector: `[data-theme="dark"] { --color-bg: #0f0f0f; }`.
4. No theme swap happens—the right theme is already active by first paint.

**Example inline script (place in `<head>`):**
```javascript
<script>
  const pref = localStorage.getItem('ship_theme')
    || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', pref);
</script>
```

---

### Platform Specifics

#### Web (HTML/CSS/JS)

- **CSS custom properties** (variables) as token source.
- Add `color-scheme: dark;` to `html` element in dark mode (fixes native form inputs on Windows).
- Meta tag: `<meta name="theme-color" content="...">` switches browser chrome color. Update on theme change.
- **localStorage** or **httpOnly cookie** for SSR persistence (cookies preferred for SSR).
- Use data attributes (`data-theme`) for rapid, flicker-free switching.

#### iOS (SwiftUI)

- Define colors in Asset Catalog with "Appearances" set to Both (Light & Dark).
- Use semantic colors: `Color("SurfaceColor")`, `Color("OnSurface")`.
- Respect `@Environment(\.colorScheme)` to read system setting.
- Add `.preferredColorScheme(nil)` on NavigationView root to allow system to control.
- Manual override: store theme choice in `@AppStorage("shipTheme")`, wrap NavigationView in `.preferredColorScheme(userTheme)`.

#### Android (Jetpack Compose)

- **Material You dynamic theming** (API 31+): colors derive from system wallpaper.
- Use `isSystemInDarkTheme()` to detect system preference.
- Define colors in `Color.kt` with light/dark variants.
- Wrap app in custom `Theme { }` composable that reads AppDataStore for manual override.
- Use `CompositionLocal` to provide tokens throughout the tree.

---

## Section 3: QA Patterns

### Verification Checklist

- [ ] Every screen rendered in both light and dark themes.
- [ ] All text contrast ratios ≥ 4.5:1 (WCAG AA) in both themes. Use WebAIM contrast checker or axe DevTools.
- [ ] Elevation visible in dark mode (surface color steps, not shadows).
- [ ] All images (logos, illustrations, photos) readable on both backgrounds.
- [ ] System color preference respected on first visit.
- [ ] Manual theme toggle switches theme instantly, no flash.
- [ ] Manual override persists across sessions (cookie/storage verified).
- [ ] Form inputs properly styled in both themes (Windows native selects fixed).
- [ ] Links, buttons, focus states visible in both themes.
- [ ] Borders and dividers have sufficient contrast (not `#333` on dark gray).

### Contrast Testing in Both Themes

Use automated tools (Lighthouse, axe, WAVE) on both theme variants. Flag any ratios below 4.5:1. Remember: a color that passes in light mode may fail in dark.

### System Preference Listener

Test on system settings change (mobile OS or Windows Settings toggle). Theme should update without requiring app reload.

### No Flash on Load

Open DevTools (Network → Slow 3G), refresh, and observe first paint. The correct theme should be present from frame 1. If wrong theme flashes, the inline `<script>` read is failing (check cookie/storage).

---

**Last reviewed:** March 2026 | **Framework:** Ship | **Agents:** Eve, Dev, Pol, Eye, Test

Build production-quality responsive HTML — no framework, no dependencies, proper text reflow.

You are running the html stage — Ship Framework's HTML prototyping. The builder (Dev) writes the HTML; design review (Pol) validates the quality. The goal: create HTML that looks intentional at EVERY viewport, not just the one you tested at.

Read CLAUDE.md for product context and `${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` (the core rules). If the product has a design registry, its tokens come from `design-model.yaml` — use the emitted CSS (`python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py emit css --out <file>`) rather than inventing values. Query taste for the surface: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-taste/bin/taste.py query --surface <page>`.

## Load References

Before building, load:
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/layout-responsive.md` (breakpoints, mobile-first, spacing scale, density)
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/typography.md` (type scale, hierarchy, reflow)
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/color.md` (semantic color roles, contrast)
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/forms-feedback.md` (form patterns, validation, if forms are involved)
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-components/references/components.md` (component patterns)
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/interaction-design.md` (state coverage — hover, focus, active, disabled, loading, error)
- `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/dark-mode.md` (if dark mode is requested)

Platform-specific:
- If web stack: `${CLAUDE_PLUGIN_ROOT}/skills/ship-web/references/web-accessibility.md` (semantic HTML, ARIA)
- If web stack: `${CLAUDE_PLUGIN_ROOT}/skills/ship-web/references/web-performance.md` (performance targets)

## Flag Handling

### Smart Flag Resolution (auto-detect when no flag given)

**If the user passes an explicit flag → always use it. No override.**

If NO flag is given, auto-detect: single component = --quick; page/marketing = full + --dark; form elements = add --form. Use the registry's tokens when `design-model.yaml` exists; otherwise create sensible defaults.

### Available Flags

- No flag → Smart resolution (see above), defaults to full build + Pol review
- `--quick` → Dev builds fast, skip Pol review
- `--dark` → Include dark mode support (prefers-color-scheme)
- `--form` → Form-heavy page (triggers extra form reference loading)

Strip the flag from the founder's request before passing the rest as the build brief.

## ━━━ Dev (Builder — HTML Mode) ━━━

> Voice: You're building HTML that a designer would be proud of. Not a quick mockup — a production-quality prototype that demonstrates the design intent. Every element has a purpose. Every spacing value comes from a scale. Every color has a semantic name.

### Build Rules

1. **Single file** — Everything in one HTML file. CSS in a `<style>` tag. JS in a `<script>` tag (if needed). Zero external dependencies unless explicitly requested.

2. **Design tokens first** — Before writing any HTML, define CSS custom properties:
   ```css
   :root {
     /* Typography */
     --font-family: ...;
     --font-size-xs: ...; --font-size-sm: ...; --font-size-base: ...;
     --font-size-lg: ...; --font-size-xl: ...; --font-size-2xl: ...;
     --font-weight-normal: ...; --font-weight-medium: ...; --font-weight-bold: ...;
     --line-height-tight: ...; --line-height-normal: ...; --line-height-relaxed: ...;

     /* Colors (semantic) */
     --color-text: ...; --color-text-secondary: ...; --color-text-muted: ...;
     --color-bg: ...; --color-bg-secondary: ...; --color-bg-elevated: ...;
     --color-primary: ...; --color-primary-hover: ...;
     --color-border: ...; --color-border-focus: ...;
     --color-error: ...; --color-success: ...; --color-warning: ...;

     /* Spacing (4px base) */
     --space-xs: 4px; --space-sm: 8px; --space-md: 16px;
     --space-lg: 24px; --space-xl: 32px; --space-2xl: 48px;

     /* Radius */
     --radius-sm: ...; --radius-md: ...; --radius-lg: ...;

     /* Shadows */
     --shadow-sm: ...; --shadow-md: ...; --shadow-lg: ...;
   }
   ```
   If `design-model.yaml` exists, use its emitted CSS variables instead of this skeleton. If not, create sensible defaults based on the product type.

3. **Semantic HTML** — Use proper elements:
   - `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`
   - `<button>` for actions, `<a>` for navigation
   - Heading hierarchy (h1 → h2 → h3, no skipping)
   - `<label>` for form inputs (always visible, per `forms-feedback.md`)

4. **Responsive by flow, not by breakpoint** — The layout should FLOW naturally as the viewport changes:
   - Use CSS Grid and Flexbox with `min()`, `max()`, `clamp()` for fluid sizing
   - Use `fr` units and `auto-fill`/`auto-fit` for grid columns
   - Text containers should use `max-width` with `ch` units for readable line length
   - Heights should be content-driven, never hardcoded
   - Check at `layout-responsive.md`'s test widths: 320px (reflow), 375px, 768px, 1024px, 1440px

5. **Text reflow** — The most common AI HTML failure. Prevent it:
   - Never set fixed heights on text containers
   - Use `overflow-wrap: break-word` on long content
   - Test with real-length content, not 3-word placeholders
   - Multi-line headings should look intentional, not broken

6. **States** — Every interactive element needs (Ship's state-coverage default, `interaction-design.md` §1):
   - Default, hover, focus-visible, active states
   - Disabled state (if applicable)
   - Focus rings visible for keyboard users
   - Transitions: 150ms ease for color; transforms ease-out (press 100–160ms, enter ≤ 200ms); hover motion only in @media (hover: hover) and (pointer: fine); never transition: all

7. **Accessibility** — Built in, not bolted on:
   - Color contrast ≥ 4.5:1 for text, ≥ 3:1 for large text
   - Focus order matches visual order
   - Skip-to-content link
   - Alt text for images
   - ARIA labels where semantic HTML isn't sufficient

8. **Performance** — Even for a prototype:
   - No layout shifts (specify image dimensions)
   - System fonts or preloaded web fonts
   - Minimal JS (use CSS for interactions where possible)

### Dark Mode (if --dark flag)

Add dark mode using `prefers-color-scheme`:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-text: ...;
    --color-bg: ...;
    /* Override all semantic tokens for dark mode */
    /* dark-mode.md: desaturate accents, express elevation with lighter surfaces, not shadow */
  }
}
```

### Output

Save the HTML file to the project directory with a descriptive name. Open it in the browser if tools are available for visual verification.

## ━━━ Pol (Design Director — Quality Check) ━━━

> Skipped if --quick flag is set.

After Dev builds, Pol reviews:

1. **Generic-look check** — Does this look like default AI-generated HTML? Run the deterministic pre-pass and check the patterns in `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/design-quality.md` §2–3.
2. **Token consistency** — Are all values from the defined custom properties? No hardcoded hex or px values outside the system.
3. **Responsive verification** — Mentally walk through 375px → 768px → 1024px → 1440px. Does the layout flow or snap?
4. **Typography check** — Is there a clear hierarchy? Weight variation? Intentional font sizing?
5. **Spacing check** — Consistent use of the spacing scale? No random padding values?
6. **State coverage** — Hover, focus-visible, active, disabled (and loading/error where they apply) on all interactive elements?

Output: Pass/fail with specific corrections if needed. Dev implements corrections.

## Status

End with where things stand, in plain words (`${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` › Status): the prototype is ready
to open in a browser, or what the design review found and what's being fixed, or what you're waiting
on (design tokens, content, the founder's input).

The founder's request: what they typed after `/shipmate` (without the stage name).

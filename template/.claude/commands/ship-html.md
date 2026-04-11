---
description: "Build production-quality responsive HTML — no framework, no dependencies, proper text reflow."
disable-model-invocation: true
---

Build production-quality responsive HTML — no framework, no dependencies, proper text reflow.

You are running the /ship-html command — Ship Framework's HTML prototyping tool. Dev builds the HTML, Pol validates the quality. The goal: create HTML that looks intentional at EVERY viewport, not just the one you tested at.

Read CLAUDE.md for product context. Read .claude/team-rules.md for rules and workflows. Read DESIGN.md for design tokens (if exists). Read LEARNINGS.md for design preferences.

---

## Load References

Before building, load:
- `references/shared/layout-responsive.md` (breakpoints, mobile-first, content priority)
- `references/shared/typography-color.md` (type scale, color tokens, contrast)
- `references/shared/forms-feedback.md` (form patterns, validation, if forms are involved)
- `references/shared/spatial-design.md` (spacing scale, density)
- `references/shared/components.md` (component patterns)
- `references/shared/interaction-design.md` (states — hover, focus, active, disabled)
- `references/shared/dark-mode.md` (if dark mode is requested)

Platform-specific:
- If web stack: `references/web/web-accessibility.md` (semantic HTML, ARIA)
- If web stack: `references/web/web-performance.md` (performance targets)

## Reference Gate (Rule 25 — mandatory)

**STOP.** Before writing any HTML, you MUST read the references listed above and print a receipt:

```
REFERENCES LOADED:
- [filename] ✓
- [filename] ✓
```

Then run: touch .claude/.refgate-loaded

Do NOT proceed to Dev's build until this receipt is printed.

---

## Flag Handling

### Smart Flag Resolution (auto-detect when no flag given)

**If the user passes an explicit flag → always use it. No override.**

If NO flag is given, the team decides based on context:

```
1. CHECK scope of the build brief:
   - Single component or small element       → auto-select --quick (skip Pol review)
   - Full page or multi-section layout       → full run (Dev builds + Pol reviews)
   - Landing page or marketing page          → full run + auto-add --dark (most landing pages need it)

2. CHECK for form elements:
   - Brief mentions form, input, signup, login, checkout → auto-add --form

3. CHECK for dark mode signals:
   - DESIGN.md has dark mode tokens          → auto-add --dark
   - Brief mentions "dark mode" or "both modes" → auto-add --dark

4. CHECK DESIGN.md:
   - If exists → Dev uses those tokens (no defaults needed)
   - If missing → Dev creates sensible defaults, suggests running /ship-design first

ANNOUNCE the decision: "Auto-selecting --quick (single component). Add --dark or --form explicitly if you need those."
```

### Available Flags

- No flag → Smart resolution (see above), defaults to full build + Pol review
- `--quick` → Dev builds fast, skip Pol review
- `--dark` → Include dark mode support (prefers-color-scheme)
- `--form` → Form-heavy page (triggers extra form reference loading)

Strip the flag from $ARGUMENTS before passing the rest as the build brief.

---

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
   If DESIGN.md exists, use those tokens. If not, create sensible defaults based on the product type.

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
   - Reference `layout-responsive.md` breakpoints: 375px, 768px, 1024px, 1440px

5. **Text reflow** — The most common AI HTML failure. Prevent it:
   - Never set fixed heights on text containers
   - Use `overflow-wrap: break-word` on long content
   - Test with real-length content, not 3-word placeholders
   - Multi-line headings should look intentional, not broken

6. **States** — Every interactive element needs (per `interaction-design.md`):
   - Default, hover, focus-visible, active states
   - Disabled state (if applicable)
   - Focus rings visible for keyboard users
   - Transitions: 150ms ease for color, 200ms ease for transform

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
    /* Reference dark-mode.md: desaturate colors, elevation via luminance not shadow */
  }
}
```

### Output

Save the HTML file to the project directory with a descriptive name. Open it in the browser if tools are available for visual verification.

---

## ━━━ Pol (Design Director — Quality Check) ━━━

> Skipped if --quick flag is set.

After Dev builds, Pol reviews:

1. **Anti-slop check** — Does this look like AI-generated HTML? Check against `design-quality.md` Section 2 flags.
2. **Token consistency** — Are all values from the defined custom properties? No hardcoded hex or px values outside the system.
3. **Responsive verification** — Mentally walk through 375px → 768px → 1024px → 1440px. Does the layout flow or snap?
4. **Typography check** — Is there a clear hierarchy? Weight variation? Intentional font sizing?
5. **Spacing check** — Consistent use of the spacing scale? No random padding values?
6. **State coverage** — Hover, focus, active states on all interactive elements?

Output: Pass/fail with specific corrections if needed. Dev implements corrections.

---

## Handoff

```
STATUS: [DONE / NEEDS_POLISH / BLOCKED]
[If DONE]: HTML prototype ready. Open in browser to preview.
[If NEEDS_POLISH]: Pol found [N] issues. Dev is fixing.
[If BLOCKED]: Waiting on [design tokens / content / founder input].
```

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: DONE_WITH_CONCERNS` — completed, but [list concerns]
- `STATUS: BLOCKED` — cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` — missing: [what information]

User's request: $ARGUMENTS

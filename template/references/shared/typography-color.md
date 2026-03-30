# Typography & Color Reference

> Type and color are the foundation of visual communication. These aren't decorative choices — they're functional systems that affect readability, hierarchy, consistency, and accessibility. This reference teaches the "why" behind type scales, color tokens, and audit strategies so you build systems that scale and don't decay.
>
> **Agent routing:**
> Eve → Sections 1-2 (define type scale and color palette during planning). Type scale affects layout rhythm; color palette sets mood and accessibility baseline.
> Arc → Section 1 (type scale impacts layout grid, line length, and spacing decisions). Small type forces narrow columns; large type needs broader layouts.
> Dev → Sections 1-3 (implement as design tokens, never hardcode raw values). Tokens enable theme switching, consistency, and maintainability.
> Pol → Section 3 (audit token compliance, contrast ratios, color-not-only principle). Accessibility audit. Spot hard-coded colors. Verify contrast.
> Eye → Sections 1-3 (visual consistency checks: type rendering at all sizes, color harmony across themes, dark mode saturation). QA visual polish.
> Crit → Section 3 (accessibility review: contrast, color vision deficiency, color-only patterns, dark mode legibility). WCAG AA minimum.

---

## Section 1: Typography System

Why typography matters: type is the dominant interface element. Most of what users read is
text. A type system that works creates invisible clarity — users don't notice it because
it just works. A broken system creates friction at every line.

### Base Size & Minimum Readability

**The Rule: 16px is the baseline for body text. Not arbitrary — it's the threshold where
most users (including those with mild visual impairment) can read without zooming.**

Below 16px, readability drops sharply. At 14px, users with 20/40 vision (legally requiring
glasses) need to zoom. At 12px, reading becomes uncomfortable for 15% of your audience.
This isn't about "looking bigger" — it's about inclusion.

`16px` on desktop. On mobile, can compress to `15px` because users hold the device closer.
Never go below 14px for any body text, ever. Line length at 16px should be 55-75 characters
— too narrow and eyes move too much; too wide and readers lose their place between lines.

```css
/* Incorrect — too small, excludes readers */
body {
  font-size: 13px; /* forces zoom for many users */
  line-height: 1.3; /* not enough whitespace, hard to track lines */
}

/* Correct — readable baseline, sustainable */
body {
  font-size: 16px;
  line-height: 1.5; /* 24px spacing for body */
  max-width: 65ch; /* 55-75 characters per line */
}
```

### Type Scale & Modular Ratios

A type scale creates visual harmony. Don't pick sizes randomly (16, 18, 22, 28, 36, 52...).
Use a modular scale based on a mathematical ratio. Common ratios:

- **1.25** (major third): safe, conservative. Good for prose-heavy products (blogs, docs).
- **1.333** (perfect fourth): balanced. Works for most apps. Most versatile.
- **1.5** (golden ratio): large jumps between sizes. Better for design-forward products.

Example using 1.333 ratio with 16px base:

```
xs:  12px   (16 ÷ 1.333)
sm:  16px   (base)
md:  21px   (16 × 1.333)
lg:  28px   (21 × 1.333)
xl:  37px   (28 × 1.333)
2xl: 49px   (37 × 1.333)
```

Why ratios matter: they create predictable intervals. Your eye recognizes the progression
as intentional, not random. Users subconsciously trust systems that feel coherent.

```css
/* Incorrect — random sizes, no visual logic */
h1 { font-size: 42px; }
h2 { font-size: 26px; }
h3 { font-size: 19px; }
p { font-size: 16px; }
small { font-size: 12px; }

/* Correct — consistent ratio (1.333), scalable */
:root {
  --font-xs: 12px;
  --font-sm: 16px;
  --font-base: 16px;
  --font-md: 21px;
  --font-lg: 28px;
  --font-xl: 37px;
  --font-2xl: 49px;
}

h1 { font-size: var(--font-2xl); }
h2 { font-size: var(--font-xl); }
h3 { font-size: var(--font-lg); }
p { font-size: var(--font-base); }
small { font-size: var(--font-xs); }
```

### Line Height for Readability

**Line height of 1.5 for body text. This creates 24px vertical spacing at 16px font.**

At 1.5, readers' eyes have enough whitespace to track lines without getting lost.
Too tight (1.2 or less) and lines blur together. Too loose (1.8+) and the connection
between lines weakens — paragraphs feel disconnected.

For headings, reduce line-height proportionally (1.1-1.3) because headings are larger
and need tighter spacing to feel cohesive. For UI labels and small text, 1.4 is tighter
and still readable.

```css
/* Incorrect — line height inconsistent with size */
p {
  font-size: 16px;
  line-height: 1.2; /* 19px spacing — lines feel cramped */
}

h1 {
  font-size: 49px;
  line-height: 1.5; /* 73px spacing — headline feels loose */
}

/* Correct — line height scaled to font size */
p {
  font-size: 16px;
  line-height: 1.5; /* 24px spacing — readable rhythm */
}

h1 {
  font-size: 49px;
  line-height: 1.2; /* 59px spacing — cohesive block */
}

h2 {
  font-size: 37px;
  line-height: 1.3; /* 48px spacing */
}

small {
  font-size: 12px;
  line-height: 1.4; /* 17px spacing — still scannable */
}
```

### Font Pairing: The Contrast Principle

Pair fonts that **differ in at least 2 of these dimensions**: serif/sans, geometric/humanist,
weight, x-height. Fonts that differ in one dimension feel confused. Fonts that differ in
two+ feel intentional.

**Bad pairing:** Two similar sans-serifs (e.g., Helvetica for headings, Open Sans for body).
Both are geometric sans-serifs with similar x-heights. Users can't tell them apart. Looks
like an accident.

**Good pairing:** Serif for headings (Georgia), sans-serif for body (Inter). Differ in:
serif/sans (1), x-height (2). Serves a purpose — serif suggests authority; sans-serif
suggests clarity.

**Another good pairing:** Geometric sans for headings (Futura), Humanist sans for body (Trebuchet).
Differ in: geometric/humanist (1), weight customization (2). Geometric feels designed; humanist
feels approachable.

Don't pair fonts that are too similar. Don't use more than 2-3 fonts total.

```css
/* Incorrect — fonts too similar, looks accidental */
h1, h2, h3, h4 { font-family: Helvetica, sans-serif; }
p { font-family: Arial, sans-serif; } /* imperceptibly different from Helvetica */

/* Correct — contrasting fonts, clear hierarchy */
h1, h2, h3 { font-family: Georgia, serif; } /* serif, traditional, 1em x-height */
p { font-family: Inter, sans-serif; } /* sans-serif, modern, 0.7em x-height */

/* Good alternative — both sans, but clearly different */
h1, h2, h3 { font-family: "Space Mono", monospace; } /* geometric, distinctive */
p { font-family: -apple-system, BlinkMacSystemFont, sans-serif; } /* humanist, friendly */
```

### Weight Hierarchy: 3 Weights Max

Use 3 weights maximum. More creates decision fatigue:

1. **Regular (400)**: body text, default state
2. **Medium (500) or Semibold (600)**: labels, buttons, callouts
3. **Bold (700)**: headings, emphasis

Never use 5+ weights. It signals "we don't know when to use each weight" and makes the
interface feel noisy.

**Light (300)** is decorative. Avoid for readability. If you need lighter, use opacity.

```css
/* Incorrect — too many weights, unclear intent */
.hero { font-weight: 200; }
.heading { font-weight: 700; }
.label { font-weight: 500; }
.button { font-weight: 600; }
.card-title { font-weight: 800; }
.overline { font-weight: 300; }
/* User: which one should I use for what? */

/* Correct — 3 weights, clear semantic meaning */
:root {
  --font-weight-base: 400; /* body, default */
  --font-weight-medium: 600; /* labels, buttons, raised elements */
  --font-weight-bold: 700; /* headings, strong emphasis */
}

body { font-weight: var(--font-weight-base); }
h1, h2, h3, strong { font-weight: var(--font-weight-bold); }
button, label, .emphasis { font-weight: var(--font-weight-medium); }
```

### Text Truncation & Wrapping Strategy

When text might overflow:

1. **Wrap by default.** Truncation hides information. Wrapping is honest.
2. **Truncate with tooltip only when necessary.** Single-line text inputs, table cells,
   breadcrumbs. Always show full text on hover or focus.
3. **Line clamp (ellipsis after 2-3 lines) for preview text.** Card descriptions,
   search results.

Never truncate without a way to reveal the full content.

```css
/* Incorrect — truncates with no way to see full content */
.card-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  /* user hovers: nothing happens. Frustrated. */
}

/* Correct — truncation with tooltip fallback */
.card-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-title:hover::after {
  content: attr(data-tooltip); /* show full text on hover */
  position: absolute;
  background: black;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 10;
}

/* Even better — browser title attribute */
<h3 class="card-title" title={fullTitle}>{truncatedTitle}</h3>
```

### Tabular Numbers for Data

Use monospace or tabular-figure numbers when displaying data (tables, prices, metrics).
Proportional numbers (default) align by width, causing everything to jiggle.

```css
/* Incorrect — prices in tables jump around */
.price {
  font-family: Inter; /* proportional */
  /* 111 → 222 causes alignment shift */
}

/* Correct — numbers line up vertically */
.price {
  font-variant-numeric: tabular-nums;
  font-family: monospace; /* or use tabular-nums on any font */
  /* 111 and 222 take the same width */
}
```

---

## Section 2: Color System

### Semantic Tokens: Why We Abstract

Raw hex in components is a disease. It spreads, mutates, and becomes impossible to change.

`color: #0066CC;` appears 47 times across the codebase. Marketing says "blue is wrong,
use our new blue." You search, find 47 instances (but miss 3), update them manually, and
discover 6 components now have two different blues. Disaster.

**Semantic tokens solve this.** Tokens have meaning, not just values.

```css
/* Incorrect — raw hex scattered everywhere */
.button-primary { background: #0066CC; }
.link-active { color: #0066CC; }
.border-focus { border-color: #0066CC; }
.background-hover { background: #E6F0FF; }
/* Now change blue. Where is it? */

/* Correct — semantic tokens */
:root {
  --color-primary: #0066CC;
  --color-primary-hover: #0052A3;
  --color-primary-active: #003D7A;
  --color-primary-light: #E6F0FF;

  --color-surface: #FFFFFF;
  --color-surface-hover: #F7F7F7;
  --color-border: #D0D0D0;
  --color-text: #1A1A1A;
  --color-text-muted: #666666;
}

.button-primary { background: var(--color-primary); }
.button-primary:hover { background: var(--color-primary-hover); }
.link-active { color: var(--color-primary); }
.border-focus { border-color: var(--color-primary); }
/* Change blue once, everything updates */
```

Tokens enable:
- **Theme switching:** Light mode and dark mode share token names, different values.
- **Consistency:** Same token name = same visual meaning across the app.
- **Maintainability:** Change at the token level, not in 47 places.

### Building a Palette from Product Type

Color choices should reflect the product's purpose. This isn't arbitrary — it shapes user
mental models.

**Finance / Banking → Trust → Blues and greens.** Cool, stable colors signal reliability.
Avoid reds (signals error, risk). Palette: Navy, Teal, Gold accents.

**Creative / Social → Expression → Broader palette.** Warm, vibrant colors signal playfulness
and energy. Palette: Coral, Purple, Teal, Gold.

**Health / Wellness → Calm → Muted, warm colors.** Avoid harsh contrasts. Desaturated
teals, warm grays, soft greens. Signal safety and peace.

**Productivity / Dev tools → Clarity → Neutral with sharp accent.** Dark backgrounds,
high contrast. Accent in Electric Blue or Neon Green. Signal speed and precision.

```css
/* Finance app — trust palette */
:root {
  --color-primary: #0052A3; /* navy blue, trustworthy */
  --color-accent: #2D7A4A; /* teal green, growth */
  --color-warning: #D97706; /* amber, caution (not red) */
  --color-success: #059669; /* green, confidence */
  --color-text: #1F2937; /* very dark gray, readable */
}

/* Creative app — expression palette */
:root {
  --color-primary: #FF6B6B; /* coral, warm */
  --color-accent: #845EF7; /* purple, creative */
  --color-highlight: #15AABF; /* cyan, pop */
  --color-text: #1A1A1A; /* almost black, high contrast */
}

/* Wellness app — calm palette */
:root {
  --color-primary: #4F9B8E; /* muted teal */
  --color-accent: #B8A989; /* warm tan */
  --color-background: #F5F1ED; /* warm off-white */
  --color-text: #3D3D3D; /* soft dark gray */
}
```

### Accessible Color Pairs: The 4.5:1 Ratio

**WCAG AA requires 4.5:1 contrast ratio for body text.** This isn't arbitrary. It comes from
vision research — 4.5:1 is the threshold where people with moderate vision loss (20/40)
can comfortably read body text. Below it, words blur.

**3:1 for large text (18pt+) and UI components.** Larger text is easier to perceive, so it
can tolerate lower contrast.

**Tools:** Use a contrast checker (WebAIM, Stark, etc.). Don't eyeball it. Your monitor might
be bright; users' might be dim, outdoors, or viewed at an angle.

```css
/* Incorrect — insufficient contrast */
.text-muted {
  color: #AAAAAA; /* 4.5:1 on white? No. ~3:1. Fails. */
  background: white;
}

/* Correct — meets WCAG AA */
.text-muted {
  color: #666666; /* 7.3:1 on white. Passes. */
  background: white;
}

/* Button: text on colored background */
.button-primary {
  background: #0052A3; /* navy */
  color: white; /* 13.2:1. Excellent. */
}

/* Not: */
.button-primary {
  background: #6B9FD9; /* lighter blue */
  color: #4A6FA5; /* slightly darker blue — 1.2:1. Fails. */
}
```

### Color Vision Deficiency: Color-Not-Only

**8% of men and 0.5% of women have color vision deficiency (CVD).** Red-green is most common.
To them, a red error and green success look the same.

**Rule: Never use color alone to convey meaning. Pair with icon, text, or shape.**

```jsx
/* Incorrect — color only, fails for colorblind users */
<div style={{ color: isValid ? "green" : "red" }}>
  {field.value}
</div>

/* Correct — color + icon + text */
<div style={{
  color: isValid ? "green" : "red",
  display: "flex",
  gap: "8px",
  alignItems: "center"
}}>
  {isValid ? <CheckIcon /> : <XIcon />}
  <span>{isValid ? "Valid" : "Invalid"}</span>
  {field.value}
</div>

/* Another example — status indicator */
/* Incorrect */
<span style={{ color: status === "ready" ? "green" : "red" }}>●</span>

/* Correct */
<span aria-label={status === "ready" ? "Ready" : "Not ready"}>
  {status === "ready" ? "✓ Ready" : "✗ Not ready"}
</span>
```

### State Colors: Default, Hover, Active, Disabled, Error, Success, Warning

Define all states for every color token. This prevents ad-hoc color decisions.

```css
/* Define state colors explicitly */
:root {
  /* Button Primary */
  --button-primary-default: #0052A3;
  --button-primary-hover: #003D7A;
  --button-primary-active: #002E5C;
  --button-primary-disabled: #D0D0D0;

  /* Button Secondary */
  --button-secondary-default: transparent;
  --button-secondary-border: #0052A3;
  --button-secondary-hover: #E6F0FF;
  --button-secondary-active: #CCE1FF;
  --button-secondary-disabled: #D0D0D0;

  /* Semantic states */
  --color-error: #DC2626;
  --color-error-light: #FEE2E2;
  --color-success: #059669;
  --color-success-light: #D1FAE5;
  --color-warning: #D97706;
  --color-warning-light: #FEF3C7;
}

/* Use consistently */
.button-primary {
  background: var(--button-primary-default);
  transition: background 0.2s;
}

.button-primary:hover {
  background: var(--button-primary-hover);
}

.button-primary:active {
  background: var(--button-primary-active);
}

.button-primary:disabled {
  background: var(--button-primary-disabled);
  cursor: not-allowed;
}
```

### Dark Mode: Desaturation Strategy

**Most products copy their light palette and invert it for dark mode. This fails.**

Fully saturated colors on dark backgrounds cause vibration and eye strain. `#FF0000` on
black is unreadable. The solution: **desaturate colors in dark mode.**

Desaturated colors appear less vibrant but remain readable. A teal `#2D9CDE` in light mode
becomes `#7FA8C2` in dark mode — same hue, lower saturation.

```css
/* Incorrect — naive inversion */
@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: #FFB3FF; /* inverted from #00CC00 — vibrates */
    --color-text: #FFFFFF; /* inverted from #000000 */
  }
}

/* Correct — desaturated for dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: #7FA8C2; /* same hue, lower saturation — readable */
    --color-text: #E5E5E5; /* high contrast but not pure white (less harsh) */
    --color-background: #1A1A1A; /* not pure black (less harsh) */
    --color-border: #404040; /* subtle borders */
  }
}
```

---

## Section 3: Style Selection & Audit

### Matching Style to Product Type & Audience

Design style should match user expectations. A meditation app styled like a stock trading
platform will confuse users because it violates their mental model of what meditation
apps should feel like.

**Mental models are built from experience.** Users have seen 50+ meditation apps. They
expect: soft colors, gentle motion, organic shapes, warm typography. If yours has hard
edges, high contrast, and geometric precision, it signals "this isn't a meditation app,
it's something else."

This doesn't mean all X-type apps look the same. But they share certain characteristics
that signal purpose.

```
Finance app:
  Fonts: Traditional serif or geometric sans
  Colors: Blues, teals, golds — conservative palette
  Shapes: Sharp corners, clean grids
  Motion: Minimal, precise — not playful

Creative tool:
  Fonts: Modern sans-serif or script accents
  Colors: Vibrant, broad palette
  Shapes: Mixed, playful proportions
  Motion: Smooth, expressive — delightful

SaaS productivity:
  Fonts: Humanist sans-serif, easy to read
  Colors: Neutral background, electric accent
  Shapes: Rounded corners, spacious layout
  Motion: Quick, responsive — efficient

Wellness app:
  Fonts: Warm serif or geometric sans
  Colors: Muted palette, warm neutrals
  Shapes: Soft corners, organic spacing
  Motion: Slow, calming — meditative
```

If styles mix (finance colors + meditation shapes), users get cognitive dissonance.

### Consistency & Mental Models

**Consistent visual language lets users predict what will happen next.**

If primary actions are always blue buttons in the top right, users learn this pattern.
When a primary action suddenly appears as a green link in the bottom left, they miss it.
They don't think "it's still a primary action, just styled differently." They think
"that's probably secondary."

Mixing metaphors breaks mental models:

```
Incorrect — inconsistent button patterns:
- "Save" is a blue button (primary action)
- "Publish" is a green link (also primary action??)
- "Submit" is a gray button (is this primary or secondary?)
User: which one should I click? All three seem different.

Correct — consistent primary pattern:
- "Save", "Publish", "Submit" are all blue buttons
- "Cancel" and "Delete" are secondary patterns
- User knows: blue button = what I want to do; gray = alternative
```

### Elevation Systems: 3-5 Levels Maximum

Shadow and elevation convey depth. Too many levels and they're indistinguishable. Use 3-5.

```css
/* Incorrect — too many shadow levels, users can't distinguish them */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px rgba(0,0,0,0.1);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.15);
--shadow-xl: 0 20px 25px rgba(0,0,0,0.2);
--shadow-2xl: 0 25px 50px rgba(0,0,0,0.25);
--shadow-3xl: 0 35px 60px rgba(0,0,0,0.3); /* can't see the difference from 2xl */

/* Correct — 4 clearly distinguishable levels */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05); /* cards, subtle lift */
--shadow-md: 0 4px 12px rgba(0,0,0,0.1); /* popovers, menus */
--shadow-lg: 0 12px 32px rgba(0,0,0,0.15); /* modals, floats */
--shadow-xl: 0 25px 50px rgba(0,0,0,0.25); /* dropdowns from top, hovering */
```

### Icon Consistency: Why Mixed Styles Feel Unprofessional

Mixed icon styles signal "multiple designers with no shared system." Users subconsciously
process this as "this app is disorganized."

All icons should use the same:
- **Stroke width** (all 1.5px or all 2px, not mixed)
- **Corner radius** (all sharp or all rounded, not mixed)
- **Design philosophy** (all minimal or all detailed, not mixed)
- **Size grid** (all on 24px or 20px grids, not random sizes)

```
Incorrect — mixed icon styles:
[outline close icon] [filled check icon] [3D folder icon]
User: wait, are these three different things? Different importance levels?

Correct — consistent icon system:
[outline close icon] [outline check icon] [outline folder icon]
User: these are all the same type of object, same visual weight
```

### Primary Action Per Screen: Hick's Law Applied

Screens with multiple competing CTAs create decision paralysis. Hick's Law: decision time
increases with option count.

**One primary CTA per screen.** Everything else is secondary. This doesn't mean one button
total — it means one action that's the "happy path."

```jsx
/* Incorrect — too many equally prominent actions */
<div className={styles.actions}>
  <button className={styles.primary}>Create New</button>
  <button className={styles.primary}>Import</button>
  <button className={styles.primary}>Connect</button>
  <button className={styles.primary}>Template</button>
</div>
/* User: what should I do? All look equally important. Paralysis. */

/* Correct — one primary, rest secondary */
<div className={styles.actions}>
  <button className={styles.primary}>Create New</button>
  <button className={styles.secondary}>
    More options
    <DropdownMenu>
      <Item>Import</Item>
      <Item>Connect</Item>
      <Item>Template</Item>
    </DropdownMenu>
  </button>
</div>
/* User: the blue button is what I should do. Clear path forward. */
```

### Audit Checklist: Type, Color, Consistency

Run this audit periodically:

**Typography audit:**
- [ ] All body text 16px or larger
- [ ] Type scale uses consistent ratio (1.25, 1.333, or 1.5)
- [ ] Line heights match font size (1.5 for body, 1.2-1.3 for headings)
- [ ] Font weights: 3 maximum, semantic purpose clear
- [ ] No raw font-size declarations — all use tokens
- [ ] Fonts pair by at least 2 dimensions (serif/sans, geometric/humanist, weight)

**Color audit:**
- [ ] All colors are semantic tokens, no raw hex in components
- [ ] Every color has state variants (default, hover, active, disabled)
- [ ] Contrast ratios: 4.5:1 for text, 3:1 for UI elements (WCAG AA minimum)
- [ ] No color-only meaning (red for error + icon, not red alone)
- [ ] Dark mode uses desaturated colors, not inverted
- [ ] Tokens work for colorblind users (red-green CVD check)

**Consistency audit:**
- [ ] Primary action pattern consistent across all screens
- [ ] Secondary action pattern consistent
- [ ] Icon style unified (stroke width, corners, design philosophy)
- [ ] Elevation system: 3-5 levels, clearly distinguishable
- [ ] Color usage matches product type (finance ≠ creative)
- [ ] No mixed metaphors or surprise style changes

---

*Based on typographic standards from Butterick's Practical Typography, WCAG 2.1 guidelines,
and color theory from Interaction of Color by Josef Albers.*

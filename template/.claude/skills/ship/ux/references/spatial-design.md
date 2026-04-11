# Spatial Design Reference

> Space is the invisible structure of every interface. Good spacing feels intentional — users don't notice it. Bad spacing feels off — users can't name why, but they distrust the product. This reference teaches the systems behind spacing decisions so they're deliberate, not eyeballed.
>
> **Agent routing:**
> Arc → Sections 1-2 (spatial system affects layout architecture, density decisions)
> Dev → Sections 1-3 (implement spacing tokens, density modes, whitespace rules)
> Pol → Sections 1-3 (audit spacing consistency, density appropriateness, whitespace usage)
> Eye → Section 3 (visual whitespace audit — does the layout breathe?)
>
> **Relationship to other references:**
> - `layout-responsive.md` covers breakpoints, mobile-first, and grid systems (the structural layer)
> - This file covers spacing philosophy, density strategy, and whitespace as a design tool (the spatial layer)
> - `typography-color.md` Section 1 covers line height and text spacing (the typographic layer)
> - Read layout-responsive.md for structure, this file for spatial intention.

---

## Section 1: Spacing Systems

### The 4px/8px Base Unit

Every spacing value in your product should be a multiple of a base unit. The industry standard is 4px (for fine control) or 8px (for broader systems). Pick one and commit.

**Why multiples matter:** Random spacing values (13px here, 17px there, 22px somewhere else) create subtle visual dissonance. The eye detects irregularity even when the brain can't name it. Consistent multiples create rhythm — the design equivalent of a steady heartbeat.

**The 8px scale:**
```
8   → tight internal padding (input fields, badges)
16  → standard padding (cards, buttons)
24  → comfortable padding (sections within cards)
32  → section separation (between card groups)
48  → major section gaps (between page sections)
64  → large section gaps (hero to content)
96  → dramatic separation (sparse, design-forward layouts)
```

**The 4px scale** (when 8px is too coarse):
```
4   → micro spacing (icon-to-label gap)
8   → tight padding
12  → compact padding (dense UIs)
16  → standard padding
20  → comfortable padding
24  → relaxed padding
32  → section gaps
48  → major gaps
64  → dramatic gaps
```

### Spacing Tokens: Name the Intent

Don't use raw pixel values in code. Name your spacing by purpose, not value.

```css
:root {
  /* Semantic spacing tokens */
  --space-inline-xs: 4px;    /* icon ↔ label */
  --space-inline-sm: 8px;    /* between inline elements */
  --space-inline-md: 12px;   /* button padding, input padding */

  --space-stack-xs: 4px;     /* label ↔ input (tight coupling) */
  --space-stack-sm: 8px;     /* between related items */
  --space-stack-md: 16px;    /* between card sections */
  --space-stack-lg: 24px;    /* between distinct groups */
  --space-stack-xl: 48px;    /* between page sections */

  --space-inset-sm: 12px;    /* compact card padding */
  --space-inset-md: 16px;    /* standard card padding */
  --space-inset-lg: 24px;    /* spacious card padding */
  --space-inset-xl: 32px;    /* hero section padding */
}
```

**Three types of spacing:**
- **Inline** — horizontal gaps between elements on the same line
- **Stack** — vertical gaps between stacked elements
- **Inset** — padding inside a container (all sides)

Naming by type prevents confusion: `--space-stack-md` is always vertical, `--space-inline-sm` is always horizontal. No ambiguity.

### Proximity Creates Meaning

Spacing is not just visual — it communicates relationships. Elements close together are perceived as related (Gestalt proximity principle). Elements far apart are perceived as separate.

```
Incorrect — uniform spacing hides relationships:
  Label          16px
  Input          16px
  Helper text    16px
  Label          16px
  Input          16px
  Helper text    16px

Correct — proximity creates field groups:
  Label          4px   ← tight: label belongs to input
  Input          2px   ← tight: helper belongs to input
  Helper text    24px  ← gap: separates from next field
  Label          4px
  Input          2px
  Helper text    24px
```

**The rule:** Spacing within a group should be 2-4x tighter than spacing between groups. If items within a group are 4-8px apart, groups should be 16-32px apart. This ratio creates obvious visual grouping without borders or dividers.

---

## Section 2: Density Strategy

### Why Density Is a Product Decision

Density isn't about cramming more in or spreading things out — it's about matching spatial behavior to user needs.

**High density** works for:
- Data-heavy dashboards (users scan, compare, cross-reference)
- Power-user tools (users spend hours, know the interface, need efficiency)
- Tables and spreadsheets (data alignment matters more than breathing room)
- Admin panels (functionality > aesthetics)

**Low density** works for:
- Consumer products (first-time users need guidance and focus)
- Marketing sites (one message per section, room to breathe)
- Wellness/meditation apps (space = calm)
- Onboarding flows (one concept per screen)

**Medium density** works for:
- Most SaaS products (balance between information and clarity)
- Messaging apps (content-dense but needs readability)
- E-commerce (product info + navigation + actions)

### Implementing Density Modes

Some products need multiple density levels for different users or contexts.

```css
/* Density modes via CSS custom properties */
:root {
  --density: 1; /* default: comfortable */
}

[data-density="compact"] {
  --density: 0.75;
}

[data-density="spacious"] {
  --density: 1.25;
}

/* Spacing scales with density */
.card {
  padding: calc(var(--space-inset-md) * var(--density));
  gap: calc(var(--space-stack-sm) * var(--density));
}

.table-row {
  padding-block: calc(8px * var(--density));
}
```

**When to offer density toggle:**
- Data-heavy apps with both power users and casual users (Gmail, Notion)
- Products used on screens of very different sizes
- Enterprise products where some teams need density, others don't

**When not to:** Consumer products with one audience. Simplicity > choice when the audience is uniform.

### The Density Audit

Check density by squinting at the screen:

- **Too dense:** Everything blurs together. Can't tell where sections start and end. Eyes feel fatigued after 30 seconds.
- **Too sparse:** Content feels insignificant. Lots of scrolling to see basic info. Feels "unfinished."
- **Just right:** Sections are clearly grouped. Eyes rest on important elements. Scrolling feels proportional to content amount.

---

## Section 3: Whitespace as a Design Tool

### Active vs. Passive Whitespace

Not all whitespace is the same:

**Passive whitespace** — the default gaps between elements from margins and padding. This is structural — it exists because elements need space to not overlap.

**Active whitespace** — intentional emptiness that draws attention, creates emphasis, or provides breathing room. This is a design choice.

```
Passive whitespace:
  [Logo]  [Nav Item]  [Nav Item]  [Nav Item]  [CTA]
  (The gaps between nav items are passive — functional spacing)

Active whitespace:
  [Logo]                                        [CTA]

  [Large heading with lots of room above and below]

  (The empty space around the heading is active — it says "this matters")
```

### Whitespace Creates Hierarchy

More space around an element = more importance. This is why hero sections have massive padding — the empty space signals "look here first."

```css
/* Incorrect — all sections equally spaced */
section { padding: 32px 0; }  /* hero, features, testimonials — all same */

/* Correct — whitespace scales with importance */
.hero     { padding: 96px 0; }  /* most important — most space */
.features { padding: 64px 0; }  /* secondary — moderate space */
.cta      { padding: 48px 0; }  /* tertiary — tighter */
.footer   { padding: 32px 0; }  /* least important — compact */
```

### The Content-to-Chrome Ratio

**Content** = what the user came for (text, data, images, interactions)
**Chrome** = everything else (navigation, headers, footers, sidebars, toolbars)

**Good ratio:** 70-80% content, 20-30% chrome. Users came for the content.

**Bad ratio:** 50% chrome, 50% content. Half the screen is navigation, toolbars, and headers. The user feels like they're looking through a narrow window.

```
Incorrect — too much chrome:
  ┌─────────────────────────────┐
  │ [Header bar]                │  ← chrome
  │ [Search + filters toolbar]  │  ← chrome
  │ [Tab navigation]            │  ← chrome
  │ [Breadcrumbs]               │  ← chrome
  │ ─────────────────────────── │
  │ Content starts here         │  ← finally!
  │ ...                         │
  └─────────────────────────────┘

Correct — content-forward:
  ┌─────────────────────────────┐
  │ [Compact header with search]│  ← minimal chrome
  │ ─────────────────────────── │
  │ Content fills the space     │  ← immediate
  │ ...                         │
  │ ...                         │
  │ ...                         │
  └─────────────────────────────┘
```

### Edge-to-Edge vs. Contained

**Edge-to-edge** (content fills the viewport): Immersive — images, maps, video, full-bleed backgrounds. Creates impact.

**Contained** (content has max-width with side margins): Readable — text, forms, data. `max-width: 1200px` with `margin: 0 auto` is the standard pattern.

**Mix them:** Hero sections go edge-to-edge for impact. Text content stays contained for readability. This contrast creates visual interest without sacrificing usability.

```css
/* Edge-to-edge hero, contained content */
.hero { width: 100%; padding: 96px 24px; }

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* For text-heavy content, narrower max-width */
.article {
  max-width: 65ch; /* optimal reading width */
  margin: 0 auto;
}
```

---

## Audit Checklist

**Spacing system:**
- [ ] All spacing values are multiples of base unit (4px or 8px)
- [ ] No random values (13px, 17px, 22px)
- [ ] Spacing tokens defined with semantic names (not raw pixels in components)
- [ ] Within-group spacing is 2-4x tighter than between-group spacing

**Density:**
- [ ] Density matches product type (dashboard = dense, consumer = spacious)
- [ ] Squint test passes — sections clearly grouped, not blurred or barren
- [ ] Content-to-chrome ratio is 70%+ content

**Whitespace:**
- [ ] Active whitespace used intentionally for hierarchy (hero > features > footer)
- [ ] Text content has max-width (65ch for articles, 1200px for layouts)
- [ ] Edge-to-edge used for impact, contained for readability

---

*Based on spacing principles from Nathan Curtis's Space in Design Systems, density patterns from Material Design, and whitespace theory from The Elements of Typographic Style by Robert Bringhurst.*

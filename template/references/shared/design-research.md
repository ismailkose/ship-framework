# Design Research & System Creation Reference

> From "I have nothing" to "I have a design system." This reference teaches how to research, decide, and document design direction.
>
> **Agent routing:**
> - **Vi** → Sections 1–2 (product vision shapes design direction)
> - **Eve** → Sections 1–3 (Eve drives the design system creation)
> - **Arc** → Section 3 (design system affects architecture decisions)
> - **Dev** → Section 3 (design tokens guide implementation)
> - **Pol** → Section 2 (design decisions should be justified, not arbitrary)

---

## Section 1: Competitive Design Research

### Why Research Competitors

Competitive analysis is not about copying. It's about understanding the *conventions your users already expect* and finding opportunities where competitors are weak. Users bring expectations from the category they know—a project management app should feel organized, a social app should feel social. Breaking conventions has a cost.

### What to Extract

When analyzing competitors, look for:

- **Navigation patterns**: What's the industry standard? Is the nav top, side, or bottom? How deep does the hierarchy go? Most users prefer one tap from home to any major feature.
- **Information hierarchy**: How do competitors prioritize content? What's above the fold? What requires scrolling? What's hidden in menus?
- **Interaction patterns**: What gestures do users already know? Swipe to delete? Long-press to edit? Double-tap to favorite? These are learned behaviors—reuse them or explicitly break them with clear affordance.
- **Visual language**: What's the expected aesthetic for this space? Banking needs to feel stable (blues, clean typography). Gaming can be playful (bold colors, dynamic layouts). A banking app that looks like TikTok will confuse users.
- **Where they're weak**: Generic design, poor mobile experience, bad empty states, missing dark mode, slow interactions—these are your differentiation opportunities.

### How to Analyze

Don't just screenshot. *Use the product.* Go through the core flows:
- Onboarding—how do they introduce new users?
- Primary action—how easy is the main task?
- Error states—what happens when something breaks?
- Empty states—what do users see with no data?
- Mobile experience—is it responsive or an afterthought?
- Accessibility—can you navigate with keyboard? Is text readable?

Take notes in context, not in a vacuum.

### Sample Size

**3–5 competitors is the sweet spot.**
- Fewer than 3 gives too narrow a view (you might miss category norms).
- More than 5 creates analysis paralysis (diminishing returns on insights).

### What NOT to Do

- Don't copy layouts. Don't adopt their color palette. Don't replicate their patterns blindly.
- Do extract the *why* behind their choices, then make your own.

### Competitor Analysis Template

```markdown
## Competitor: [Name]

**Category:** [Type of product]
**Target audience:** [Who uses this]
**URL:** [Link]

### Navigation
- Primary nav location: [Top/Side/Bottom]
- Depth: [How many taps to reach features]
- Mobile behavior: [Changes? Adaptive?]

### Information Hierarchy
- Hero/above fold: [What's most prominent]
- Secondary content: [What's visible below]
- Hidden content: [Behind menus/progressive disclosure]

### Interaction Patterns
- Gestures: [Swipe, long-press, pinch, etc.]
- Micro-interactions: [Loading states, confirmations]
- Primary action affordance: [Button, FAB, etc.]

### Visual Language
- Color palette: [Primary colors, accents]
- Typography: [Font families, scale]
- Mood: [Professional, playful, minimal, dense]

### Strengths
- [Pattern we should understand]
- [Pattern we should understand]

### Weaknesses / Opportunities
- [Gap in experience]
- [Outdated pattern]
- [Missing feature/state]
```

---

## Section 2: Design Direction Decisions

### How Product Type Shapes Aesthetic

The product category *pre-loads* user expectations. Ignore them at your cost.

**Finance/Banking** → Trust, stability
- Blue (security), clean typography, generous whitespace, minimal decoration
- Example: Stripe, Mercury

**Health/Wellness** → Calm, approachable
- Soft colors (greens, warm neutrals), rounded corners, breathing space, nature imagery
- Example: Calm, Headspace

**Productivity/SaaS** → Efficient, professional
- Neutral palette with accent, dense information architecture, clear hierarchy
- Example: Notion, Slack

**Creative tools** → Expressive, bold
- Wider color palette, dynamic layouts, strong typography, animation
- Example: Figma, Adobe

**Social/Entertainment** → Energetic, engaging
- Bright colors, visual-heavy, animation-forward, fast feedback
- Example: TikTok, Discord

**Developer tools** → Precise, technical
- Monospace fonts, dark themes, high information density, minimal decoration
- Example: GitHub, VS Code

### How Audience Shapes Decisions

**Consumer vs enterprise:**
- Consumer: Simpler, more visual, fewer options, onboarding-forward
- Enterprise: Denser layouts, more configuration, power-user features

**Technical vs non-technical:**
- Technical users tolerate complexity—expose power features
- Non-technical users need progressive disclosure—hide advanced options, offer templates

**Frequency of use:**
- Daily tools need efficiency (keyboard shortcuts, keyboard-first nav)
- Occasional tools need discoverability (visual guides, help panels)

**Age range (accessibility, familiarity):**
- Older users need larger text, higher contrast
- Younger users expect smooth animations, fast interactions
- Don't stereotype—but accessibility needs genuinely differ

### Brand Personality Exercise

Pick 3–5 adjectives that describe how the product should *feel*:

Examples:
- Notion: *powerful, flexible, collaborative*
- Apple: *simple, premium, intuitive*
- Slack: *friendly, efficient, trustworthy*
- GitHub: *transparent, developer-first, open*

Every design decision should reinforce these adjectives. If one of your adjectives is "professional," playful animations that bounce and wiggle are a contradiction. If you're "simple," a dense feature-packed interface violates the promise.

---

## Section 3: Design System Creation

### What Goes in DESIGN.md

Your project's design source of truth. This file should be filled *before* building any UI.

```markdown
# DESIGN.md

## Brand Personality
[3–5 adjectives]. How does this product feel?

## Color Tokens
### Base Palette
- **Primary**: [Value + hex + usage]
- **Secondary**: [Value + hex + usage]
- **Surface**: [Value + hex + usage]
- **Error**: [Value + hex + usage]
- **Success**: [Value + hex + usage]
- **Warning**: [Value + hex + usage]

### On-Variants (Text/content colors)
- **On Primary**: [Contrast-safe text on primary]
- **On Secondary**: [Contrast-safe text on secondary]
- **On Surface**: [Default text color]

## Typography
- **Font families**: [Sans-serif, serif, mono + use case]
- **Type scale**: [12px, 14px, 16px, 18px, 24px, 32px—justify the scale]
- **Weight assignments**:
  - Regular (400): Body text, labels
  - Medium (500): Emphasis, secondary headings
  - Bold (700): Headings, CTA labels

## Spacing
- **Base unit**: [8px or 4px?—be consistent]
- **Scale**: [8, 12, 16, 24, 32, 48, 64...]
- **Usage**: Padding, margin, gaps—all use tokens

## Border Radius
- **Sharp** (0–2px): Utilitarian, technical
- **Rounded** (6–8px): Approachable, friendly
- **Pill** (9999px): Special emphasis, badges

## Shadows & Elevation
- **Level 1** (subtle): Hover states
- **Level 2** (medium): Modals, popovers
- **Level 3** (prominent): Important overlays, tooltips

## Component Rules
- **Library source**: [shadcn/ui, custom, Material Design]
- **Naming convention**: [button-primary, Button/Primary]
- **Overrides allowed**: [Yes—explain limits. No—explain why.]
- **Custom components**: [List unique-to-product components]

## Do/Don't
- DO: [Reinforce brand personality]
- DON'T: [Violate personality or accessibility]
```

### Make Decisions That Cohere

Every design choice reinforces the brand personality:

**If you're "minimal":**
- Shadows should be subtle (don't use Level 3 elevation for routine elements)
- Palette should be restrained (don't add 10 accent colors)
- Typography should be clean (avoid decorative fonts)
- Spacing should breathe (don't cram content)

**If you're "expressive":**
- Use a wider color palette
- Animations should be present and energetic
- Typography can be bold
- Spacing can be tighter (more visual density is OK)

### Coherence Validation Checklist

After defining your system, audit it:

- ✓ Does the color palette match the typography personality?
- ✓ Does spacing feel right for the information density?
- ✓ Do border radii match the brand (sharp = technical, rounded = friendly)?
- ✓ Do shadows support the visual hierarchy without creating visual noise?
- ✓ Can all colors meet WCAG AA contrast ratios for text?
- ✓ Are spacing increments consistent (no random 13px or 37px values)?

### When to Create DESIGN.md

**BEFORE building any UI.** If you build first and document later, the system documents inconsistency. You'll be retrofitting design decisions instead of building from a vision.

### How Design Tokens Flow to Code

```
DESIGN.md
  ↓
CSS Custom Properties (web) / Swift Constants (iOS) / Compose Theme (Android)
  ↓
Components reference tokens (never hardcoded values)
  ↓
Product UI consumes components
```

Example:
```css
/* DESIGN.md says primary = #0066FF */
/* tokens.css */
:root {
  --color-primary: #0066FF;
  --color-on-primary: #FFFFFF;
}

/* Button.tsx */
export function Button() {
  return <button style={{ backgroundColor: 'var(--color-primary)' }} />;
}
```

If you change the primary color in DESIGN.md, update tokens.css *once*, and the change cascades everywhere.

---

## Quick Start: Fill This In First

1. **Competitive research**: Pick 3 competitors, spend 30 min each, fill the template above
2. **Brand personality**: Write 3–5 adjectives
3. **Product type**: Identify your category (finance, health, social, etc.)
4. **Audience**: Who are you building for?
5. **DESIGN.md**: Fill the template above with your decisions
6. **Coherence check**: Run the validation checklist
7. **Build**: Now you can build—every component will have a system to reference

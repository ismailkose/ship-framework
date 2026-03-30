# Layout & Responsive Design Reference

> **Agent routing:**
> - **Arc** → Section 1 (plan layout strategy, breakpoints, content priority)
> - **Dev** → Sections 1–2 (build mobile-first, spacing tokens, viewport handling)
> - **Pol** → Sections 1–2 (layout affects visual hierarchy and product feel, audit spacing consistency, responsive behavior)
> - **Test** → Section 3 (verify at all breakpoints, orientation, overflow)

---

## Section 1: Mobile-First Philosophy

### Why Mobile-First Is a Prioritization Framework

Mobile-first design is not just a CSS technique—it's a **forced prioritization process**. When you design for 375px first, you cannot hide behind space. Every element must justify its existence. On a 375px screen, you decide:
- What *must* be visible (core functionality)
- What can *wait* (secondary features)
- What gets *hidden* or *deferred* (edge cases, nice-to-haves)

This constraint produces better desktop layouts than designing for 1440px first and then removing elements. Why? Because you've already made the hard design choices. Desktop then becomes an *expansion* of that solid mobile foundation, not a scramble to fit unused elements.

**Impact on product feel:** Users sense when a layout feels thoughtful vs. bloated. Mobile-first forces thoughtfulness.

### Breakpoint Philosophy

The standard breakpoint scale is not arbitrary—each reflects a real device constraint:

- **375px**: iPhone SE/iPhone mini minimum. Represents the tightest constraint. If it works here, it works everywhere.
- **768px**: iPad portrait. Where single-column layouts can safely transition to two-column grids or sidebar patterns.
- **1024px**: iPad landscape / small laptop. Desktop patterns emerge. Two-column layouts stabilize.
- **1440px**: Standard desktop monitor. The space where full-width designs can breathe without becoming hard to read.

**Why these specific values?** They align with *actual market device distributions*, not arbitrary "mobile/tablet/desktop" buckets. Designing to 768px alone leaves gaps at 600px, 650px, 700px—untested regions where your layout may break.

### Content Priority and Paint Order

"First paint" determines the user's first impression. On a mobile network (3G, 4G LTE):
- Content that renders first is content that *exists* for users on slow connections
- If your primary call-to-action is behind a 2MB hero image, slow-network users won't see it for seconds
- Mobile-first design forces you to ask: *What is the actual job this page does?* Load that first.

**Real-world impact:** 60%+ of web traffic is mobile. Even if you serve desktop users, most of your audience is on mobile. That's not a side case—that's the primary spec.

---

## Section 2: Spacing & Grid System

### 4pt/8dp Base Unit Philosophy

A consistent spacing scale creates **visual rhythm**. Every margin, padding, and gap becomes a multiple of a base unit:

```
4pt scale: 4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 56, 64...
8dp scale: 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128...
```

Why this matters:
- **Designers and developers speak the same language.** "Add 16px margin" is unambiguous. No guessing.
- **Every element relates to every other element.** If your card padding is 16px, your gap between cards should also be 16px (or 24px, 32px—multiples of the base). This creates coherence users feel but don't consciously see.
- **Consistency is harder to break.** A random 13px padding stands out immediately against a scale.

### The Magic Number Problem

Hardcoded spacing like `margin: 7px` or `padding: 13px` creates visual inconsistency that's invisible in code but *felt* in the product:

❌ **Bad:**
```css
.card { padding: 14px; margin-bottom: 11px; }
.header { padding: 18px; margin-bottom: 13px; }
.button { padding: 8px 13px; margin-right: 7px; }
```
Result: Everything feels slightly off. Rhythm is broken. Users describe it as "janky."

✅ **Good:**
```css
.card { padding: 16px; margin-bottom: 16px; }
.header { padding: 16px; margin-bottom: 16px; }
.button { padding: 8px 16px; margin-right: 8px; }
```
Result: Visual coherence. Pattern recognition works. Feels polished.

### Line Length and Readability

**Optimal line length for body text: 60–75 characters.** This is based on eye-tracking research. When reading left-to-right:
- At 60–75 characters per line, the eye easily returns to the left margin
- Beyond 100 characters, the eye loses its place when returning to the next line
- Full-width text at 1440px can exceed 150 characters—making it taxing to read

**Container max-width strategy:**
- Wrap long-form content in a `max-width: 720px` container
- Images at full bleed can extend beyond text (visual contrast)
- Sidebars and secondary content can sit beside the max-width container

### Z-Index Management

Without a documented scale, z-index becomes an arms race:

❌ **Bad:**
```css
.modal { z-index: 100; }
.dropdown { z-index: 50; }
.header { z-index: 10; }
/* 6 months later, someone adds z-index: 999 for a "temporary" tooltip */
```

✅ **Good:**
```css
/* Define and document the scale */
--z-base: 0;
--z-dropdown: 100;
--z-sticky-header: 200;
--z-modal: 300;
--z-tooltip: 400;

.modal { z-index: var(--z-modal); }
.dropdown { z-index: var(--z-dropdown); }
```
Result: Predictable stacking. No surprises. Changes ripple logically through the system.

---

## Section 3: QA Patterns

### Test Coverage Checklist

1. **Every breakpoint** (375, 768, 1024, 1440)
   - Content is readable
   - Touch targets are ≥44px (mobile)
   - Images scale without distortion

2. **Landscape orientation**
   - Viewport height shrinks on mobile landscape
   - Sticky headers don't consume >50% of viewport
   - Forms and modals don't force scroll-on-scroll

3. **Horizontal scroll** (instant failure)
   - No element should overflow the viewport width
   - Check at 100% zoom and user zoom levels (200%)
   - Test with `overflow: visible` elements

4. **Content length variation**
   - Single word vs. 50-word strings in buttons/labels
   - Short vs. long form content in cards
   - URLs, email addresses, numbers with many digits
   - Test with actual content—Lorem ipsum masks overflow bugs

5. **System font scaling**
   - Browser zoom to 150% and 200%
   - OS-level font size increases (accessibility)
   - Ensure no text clipping or layout shift

### Common Failure Patterns to Watch

- Flexbox `width: 100%` on children causes overflow in constrained parents
- Padding without `box-sizing: border-box` causes invisible overflow
- Images without explicit aspect ratio cause layout shift
- Sticky elements on mobile that consume header space
- Touch targets smaller than 44px on mobile (WCAG failure)

---

## Rationale

Layout and responsive design are *architectural decisions*, not surface-level styling. The choices you make about breakpoints, spacing, and content priority determine how your product feels at scale. Mobile-first ensures you're solving for constraint, not abundance. Consistent spacing creates subconscious trust. QA coverage prevents the "something's off" feeling that shipwrecks user experience.

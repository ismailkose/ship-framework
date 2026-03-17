# Animation Reference

> Agents read the section relevant to their role.
> Arc → Section 1 + 2 (plan the motion system). Dev → Section 3 (build it right).
> Pol → Section 1 (audit the feel). Eye → Section 2 (check what's on screen).
> Test → Section 2 (verify it works).

---

## Section 1: Design Principles

Animation should be invisible. When done right, users don't notice animation —
they notice that the interface feels good. The moment someone says "nice
animation," you've probably overdone it.

### Easing

| Animation Type | Easing | Duration |
|----------------|--------|----------|
| Element entering | ease-out / `cubic-bezier(.23, 1, .32, 1)` | 200-300ms |
| Element moving on screen | ease-in-out / `cubic-bezier(.645, .045, .355, 1)` | 200-300ms |
| Element exiting | ease-in / `cubic-bezier(.32, 0, .67, 0)` | 150-200ms |
| Hover effects | ease | 150ms |
| Micro-interactions | ease-out | 100-150ms |
| Page transitions | ease-out | 300-400ms |

### Golden Rules

1. **Exits are ~75% of enter duration.** If enter is 300ms, exit is ~200ms.
2. **Only animate transform and opacity.** These are GPU-accelerated. Everything else causes layout recalculation.
3. **200-300ms is the sweet spot.** Most UI animations should be in this range.
4. **Smaller elements = faster animations.** Scale duration with element size.
5. **User-initiated = faster response.** Direct actions should feel immediate.
6. **System-initiated = can be slower.** Background transitions can take longer.

### Default Patterns

- **Content appearing:** fade + rise (`opacity: 0, y: 8` → `opacity: 1, y: 0`). The classic — use it as your default.
- **Modals/dialogs:** scale + fade (`opacity: 0, scale: 0.95` → `opacity: 1, scale: 1`).
- **Navigation:** translate (slide). Moving to a new view = slide. Opening something important = scale.
- **Lists/grids:** stagger children 50-100ms apart. More than 8 items? Don't stagger — too slow.
- **Button press:** `scale(0.97)` on active, 100ms ease-out.
- **Hover lift:** `translateY(-4px)` + shadow increase, 200ms ease-out.

### Spring Animations

Springs feel more natural than duration-based timing for interactive elements:

| Personality | Stiffness | Damping | Use Case |
|-------------|-----------|---------|----------|
| **Snappy** | 400 | 30 | Buttons, toggles, tabs, UI controls |
| **Gentle** | 200 | 20 | Larger elements, panels, drawers |
| **Bouncy** | 300 | 10 | Playful interactions, celebrations |

Match the spring to the product's personality. Health apps feel gentle. Games feel bouncy. Productivity tools feel snappy.

### Motion Hierarchy

Not everything deserves the same level of motion:

1. **Magic moment** (the core value moment) → most expressive animation
2. **Primary actions** (submit, save, navigate) → clear, purposeful motion
3. **Secondary UI** (tooltips, dropdowns, toasts) → functional, quick
4. **Background elements** (loading, skeleton) → subtle, non-distracting
5. **Repeated actions** (button clicked 50x/day) → minimal or no animation

### When NOT to Animate

- Loading states that block interaction — don't make people wait for an animation to finish
- Error messages that need immediate attention — show them instantly
- Actions the user performs very frequently — animation becomes annoying
- When it adds no value to the experience — remove it
- When `prefers-reduced-motion` is set — always respect this

### CSS Custom Properties

Define these in your project for consistent easing:

```css
:root {
  --ease-out-quint: cubic-bezier(.23, 1, .32, 1);
  --ease-in-out-cubic: cubic-bezier(.645, .045, .355, 1);
  --ease-out-cubic: cubic-bezier(.33, 1, .68, 1);
  --ease-in-cubic: cubic-bezier(.32, 0, .67, 0);
}
```

---

## Section 2: Audit Checklist

Use this when reviewing animations on screen or in code.

### Timing Check
- [ ] Micro-interactions under 200ms?
- [ ] Standard transitions between 200-300ms?
- [ ] Page transitions under 400ms?
- [ ] Nothing over 1 second?
- [ ] Exits faster than enters (~75%)?

### Easing Check
- [ ] Entrances use ease-out? (decelerate in)
- [ ] Exits use ease-in? (accelerate out)
- [ ] On-screen movement uses ease-in-out?
- [ ] No linear easing on UI elements? (exception: opacity-only, progress bars)

### Performance Check
- [ ] Only `transform` and `opacity` being animated?
- [ ] No animation on `width`, `height`, `top`, `left`, `margin`, `padding`?
- [ ] `will-change` used sparingly? (only on elements that actually animate)
- [ ] No more than 3-4 elements animating simultaneously?
- [ ] No layout thrashing? (batch DOM reads/writes)

### Accessibility Check
- [ ] `prefers-reduced-motion` respected?
- [ ] Content is accessible without animation?
- [ ] No flashing more than 3 times per second?
- [ ] Animations don't block interaction?
- [ ] Focus management correct after animated transitions? (e.g., focus moves to modal after enter animation)

### Feel Check
- [ ] Does the motion feel intentional or decorative?
- [ ] Does it guide the user's eye to the right place?
- [ ] Does the app feel fast? (perceived performance > actual performance)
- [ ] Would removing this animation make the experience worse? If not, remove it.
- [ ] Does the motion match the product's personality?

---

## Section 3: Build Rules

Follow these when writing animation code.

### Properties

**Animate these (GPU-accelerated):**
- `transform` — translate, scale, rotate
- `opacity` — fade effects

**Never animate these (cause layout recalculation):**
- `width`, `height`
- `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `border-width`, `font-size`

Use `transform: scale()` instead of width/height. Use `transform: translate()` instead of top/left.

### Reduced Motion (required)

**CSS:**
```css
@media (prefers-reduced-motion: reduce) {
  .element {
    transition: none;
    /* or minimal: */
    transition: opacity 200ms ease-out;
  }
}
```

**React (Framer Motion):**
```tsx
import { useReducedMotion } from "framer-motion"

function Component() {
  const reduced = useReducedMotion()
  return (
    <motion.div
      initial={{ opacity: 0, y: reduced ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduced ? 0 : 0.3 }}
    />
  )
}
```

**Global (Framer Motion):**
```tsx
import { MotionConfig, useReducedMotion } from "framer-motion"

function App() {
  const reduced = useReducedMotion()
  return (
    <MotionConfig reducedMotion={reduced ? "always" : "never"}>
      <YourApp />
    </MotionConfig>
  )
}
```

### Exit Animations

Always wrap removable elements in `AnimatePresence`:
```tsx
<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
    />
  )}
</AnimatePresence>
```

Exit duration should be ~75% of enter duration.

### Staggered Lists

```tsx
const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } }
}
const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

<motion.ul variants={container} initial="hidden" animate="visible">
  {items.map(i => <motion.li key={i} variants={item}>{i}</motion.li>)}
</motion.ul>
```

Don't stagger more than 8 items — it's too slow.

### Spring Configs

```tsx
// Snappy — UI controls
{ type: "spring", stiffness: 400, damping: 30 }

// Gentle — larger elements
{ type: "spring", stiffness: 200, damping: 20 }

// Bouncy — playful
{ type: "spring", stiffness: 300, damping: 10 }

// Duration-based spring
{ type: "spring", duration: 0.3, bounce: 0.2 }
```

### Layout Animations

`layout` prop is expensive. Use sparingly:
```tsx
<motion.div layout>           // Position AND size — most expensive
<motion.div layout="position"> // Position only — cheaper
<motion.div layout="size">     // Size only
```

### Performance Tips

- `will-change: transform, opacity` — only on elements that actually animate. Remove after animation if possible.
- Avoid creating new objects during animation (causes GC pauses)
- Monitor with Chrome DevTools: Performance tab → record during animation. Target 60fps (16.67ms per frame).

---

*Based on principles from [Emil Kowalski's "Animations on the Web"](https://animations.dev/) and the [animate-skill](https://github.com/delphi-ai/animate-skill).*

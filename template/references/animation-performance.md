# Animation Performance & Accessibility

> **Stack-agnostic.** Everything here applies regardless of framework.
> Dev reads this when building animations. Eye reads this to catch perf issues.
> Test reads this for reduced motion testing. Crit reads this to diagnose why
> something feels off.

---

## Performance Target: 60 FPS

Animations should run at 60 frames per second — 16.67ms per frame. If a frame
takes longer, the animation stutters. Users notice jank at ~45fps.

---

## GPU-Accelerated Properties

Only these properties are hardware-accelerated:

| Property | Notes |
|----------|-------|
| `transform` | translate, scale, rotate — all GPU |
| `opacity` | Fade effects — GPU |

### Properties to Avoid Animating

These trigger layout recalculation and are expensive:

| Property | Alternative |
|----------|------------|
| `width`, `height` | Use `transform: scale()` |
| `top`, `left`, `right`, `bottom` | Use `transform: translate()` |
| `margin`, `padding` | Use `transform: translate()` |
| `border-width` | Use `transform: scale()` or `box-shadow` |
| `font-size` | Use `transform: scale()` |

---

## will-change

Hints to the browser that an element will animate:

```css
.will-animate {
  will-change: transform, opacity;
}
```

**Rules:**
- Only apply to elements that actually animate
- Remove after animation completes if possible
- Don't use on more than a handful of elements — each one creates a new compositor layer
- Overuse hurts performance more than it helps
- Never `will-change: all` — that's always wrong

### Hardware Acceleration Hack

Force GPU layer creation when `will-change` isn't enough:

```css
.force-gpu {
  transform: translateZ(0);
  /* or */
  backface-visibility: hidden;
}
```

Use sparingly. Each GPU layer consumes memory.

---

## Common Performance Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Janky scrolling | Animating `top`/`left` | Use `transform: translate()` |
| Slow animations | Too many elements animating | Reduce count, stagger, or remove |
| Memory spikes | Creating new objects during animation | Cache animation objects outside render |
| Layout thrashing | Reading then writing DOM in a loop | Batch reads, then batch writes |
| Paint flashing | Animating non-composited properties | Stick to `transform` + `opacity` |
| Stuttering on mobile | Complex animations on low-end devices | Simplify or remove for mobile |

### Object Creation During Animation

Bad — creates new object every frame:

```tsx
// React re-renders create new transition objects
<motion.div transition={{ duration: 0.3, ease: "easeOut" }} />
```

Good — cached outside component:

```tsx
const transition = { duration: 0.3, ease: "easeOut" }

function Component() {
  return <motion.div transition={transition} />
}
```

---

## Monitoring Performance

### Chrome DevTools

1. **Performance tab** — Record during animation. Look for:
   - Long frames (red bars above 16.67ms)
   - Layout shifts (purple blocks)
   - Paint events (green blocks) — should be minimal during animation

2. **Rendering tab** (More tools → Rendering):
   - **FPS meter** — real-time frame rate overlay
   - **Paint flashing** — green rectangles show what's being repainted
   - **Layout shift regions** — blue rectangles show layout shifts
   - **Layer borders** — orange/olive borders show compositor layers

3. **Layers panel** (More tools → Layers):
   - See all compositor layers
   - Check layer memory usage
   - Find unnecessary layers

### Performance Checklist

- [ ] Animations run at 60fps on target devices?
- [ ] No layout thrashing visible in Performance tab?
- [ ] Paint flashing only on expected elements?
- [ ] `will-change` used on ≤5 elements?
- [ ] No memory growth during repeated animations?
- [ ] Works on mid-range mobile devices?

---

## Accessibility

### prefers-reduced-motion

Users can indicate they prefer reduced motion in OS settings. **Always respect this.**

#### CSS Implementation

```css
/* Full animation by default */
.element {
  transition: transform 300ms var(--ease-out-quint);
}

/* Reduced or no motion */
@media (prefers-reduced-motion: reduce) {
  .element {
    transition: none;
  }
}
```

#### Global CSS Reset

Remove all motion for users who prefer it:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

#### Per-Element (keep subtle fades)

```css
@media (prefers-reduced-motion: reduce) {
  .element {
    /* Remove movement, keep opacity transition */
    transition: opacity 200ms ease-out;
  }
}
```

#### React (Framer Motion)

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

#### Global (Framer Motion)

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

| MotionConfig value | Effect |
|--------------------|--------|
| `"never"` | Normal animations (default) |
| `"always"` | Skip all animations |
| `"user"` | Respect system setting |

---

## Testing Reduced Motion

### How to Enable on Each OS

| OS | Path |
|----|------|
| **macOS** | System Settings → Accessibility → Display → Reduce motion |
| **Windows** | Settings → Ease of Access → Display → Show animations (off) |
| **iOS** | Settings → Accessibility → Motion → Reduce Motion |
| **Android** | Settings → Accessibility → Remove animations |

### Chrome DevTools Emulation

1. Open DevTools → More tools → Rendering
2. Scroll to "Emulate CSS media feature prefers-reduced-motion"
3. Select "reduce"

This lets you test without changing OS settings.

### What to Verify

- [ ] All transform-based animations disabled or simplified?
- [ ] Opacity-only transitions still work? (fades are usually acceptable)
- [ ] Content is fully accessible without any animation?
- [ ] No layout jumps from removed animations?
- [ ] Page transitions still make sense without motion?
- [ ] Loading states visible without animation?

---

## Accessible Animation Guidelines

1. **Content accessible without animation** — animation enhances but isn't required
2. **No flashing** — nothing flashes more than 3 times per second (WCAG 2.3.1)
3. **Don't block interaction** — users should never wait for an animation to finish
4. **Keep it brief** — long animations frustrate users
5. **Purposeful motion** — only animate when it adds value
6. **Pause controls** — for continuous/looping animations, provide pause/stop
7. **No auto-play video with motion** — can trigger vestibular disorders

### Focus Management with Animations

When animated elements receive focus (modals, drawers, dialogs):

```tsx
function Modal({ isOpen }) {
  const modalRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      // Wait for enter animation to complete before focusing
      const timer = setTimeout(() => {
        modalRef.current?.focus()
      }, 300) // Match your animation duration
      return () => clearTimeout(timer)
    }
  }, [isOpen])

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={modalRef}
          tabIndex={-1}
          role="dialog"
          aria-modal="true"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          Modal content
        </motion.div>
      )}
    </AnimatePresence>
  )
}
```

**Key:** Focus moves to the modal *after* the enter animation completes, not during.
Screen readers announce the content when it's fully visible.

---

*Reference adapted from [Emil Kowalski's "Animations on the Web"](https://animations.dev/).*

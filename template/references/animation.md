# Animation Reference

> Agents read the section relevant to their role.
> Arc → Sections 1 + 2 (plan the motion system, set the motion budget).
> Dev → Sections 3 + 4 (build it right, learn from patterns).
> Pol → Sections 1 + 2 (audit the feel).
> Eye → Section 2 (check what's on screen).
> Test → Section 2 (verify it works).
> Crit → Section 1 (check animation balance — is motion earning its place?).

---

## Section 1: Design Principles

Animation should be invisible. When done right, users don't notice animation —
they notice that the interface feels good. The moment someone says "nice
animation," you've probably overdone it.

### Motion Budget

Every screen gets a motion budget. Spend it on what matters most — don't spread
it everywhere.

**The rule: limit competing motion patterns per screen, not animated elements.**
A dashboard with 4 cards staggering in is one pattern — that's fine. A screen
with a staggered list + a sliding drawer + a pulsing notification + a bouncing
button is four patterns fighting for attention — that's too much. Count the
*distinct motions happening at the same time*, not the total number of elements
that move.

Guidelines:
- **1-2 simultaneous motion patterns per screen** is the sweet spot
- A staggered group (e.g., 6 cards fading in) counts as one pattern
- The magic moment screen can be more expressive
- Settings pages, forms, and utility screens need zero or minimal motion
- When in doubt, start with less — you can always add, but removing feels like regression

Before adding any animation, ask:
1. How many motion patterns are already on this screen? Would a new one compete?
2. Is this animation serving the user or decorating the interface?
3. Will the user see this animation 100+ times? If yes, make it minimal or remove it.
4. Would the experience feel broken without it? If not, it's optional — skip it for v1.

Arc sets the budget when defining the motion system. Crit checks it after
the fact. If you can't justify an animation in one sentence, cut it.

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
- When the motion budget for this screen is already spent — resist the urge

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

### Balance Check
- [ ] How many distinct motion patterns compete on each screen? (aim for 1-2 simultaneous)
- [ ] Is any animation purely decorative with no functional purpose?
- [ ] Would a first-time user notice the motion, or does it feel natural?
- [ ] Are repeated interactions (used 50x/day) animation-free or minimal?
- [ ] Does the overall motion level match the product's personality?

### Feel Check
- [ ] Does the motion feel intentional or decorative?
- [ ] Does it guide the user's eye to the right place?
- [ ] Does the app feel fast? (perceived performance > actual performance)
- [ ] Would removing this animation make the experience worse? If not, remove it.
- [ ] Does the motion match the product's personality?

---

## Section 3: Build Rules

These rules apply regardless of framework. The foundations are the same whether
you're using CSS, Framer Motion, GSAP, Svelte transitions, Vue's `<Transition>`,
or anything else. Learn the principles, adapt the syntax.

### 3A: CSS Foundations (works everywhere)

#### GPU-Accelerated Properties

**Animate these:**
- `transform` — translate, scale, rotate
- `opacity` — fade effects

**Never animate these (cause layout recalculation):**
- `width`, `height`
- `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `border-width`, `font-size`

Use `transform: scale()` instead of width/height. Use `transform: translate()` instead of top/left.

#### Transitions

```css
/* Standard entrance */
.element {
  transition: transform 250ms var(--ease-out-quint),
              opacity 250ms var(--ease-out-quint);
}

/* Hover lift */
.card {
  transition: transform 200ms var(--ease-out-quint),
              box-shadow 200ms var(--ease-out-quint);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* Button press */
.button {
  transition: transform 100ms ease-out;
}
.button:active {
  transform: scale(0.97);
}
```

#### Keyframe Animations

```css
/* Fade + rise — the universal default entrance */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.element-enter {
  animation: fade-in-up 250ms var(--ease-out-quint);
}

/* Staggered children — use CSS custom property for delay */
.stagger-item {
  animation: fade-in-up 300ms cubic-bezier(.19, 1, .22, 1);
  animation-fill-mode: backwards;
  animation-delay: calc(var(--index) * 0.05s);
}
```

#### Reduced Motion (required — every project)

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

Or per-element if you want to keep subtle opacity fades:

```css
@media (prefers-reduced-motion: reduce) {
  .element {
    transition: opacity 200ms ease-out;
    /* remove transform-based motion, keep opacity */
  }
}
```

#### Data-Attribute Triggers

Use `data-*` attributes to trigger animations from JS without a framework:

```css
.toast {
  transform: translateY(100%);
  opacity: 0;
  transition: transform 350ms ease, opacity 350ms ease;
}

.toast[data-mounted="true"] {
  transform: translateY(0);
  opacity: 1;
}
```

```js
// Trigger from JS
element.dataset.mounted = "true";
```

This pattern works in any stack — React, Vue, Svelte, vanilla JS, server-rendered HTML.

#### CSS Custom Properties for Dynamic Values

```css
/* Stack position calculated from index */
.stack-item {
  transform: translateY(calc(var(--index) * -110%));
}

/* Stagger delay calculated from index */
.stagger-item {
  animation-delay: calc(var(--index) * 50ms);
}
```

Set `--index` from your template/framework. Keeps animation logic in CSS, triggering in JS.

### 3B: Framer Motion (React)

If your stack uses React with Framer Motion, these are the framework-specific patterns.
The foundations from 3A still apply — Framer Motion is just a nicer API for the same CSS concepts.

#### Reduced Motion

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

Global setting:

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

#### Exit Animations

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

#### Staggered Lists

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

#### Spring Configs

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

#### Layout Animations

`layout` prop is expensive. Use sparingly:

```tsx
<motion.div layout>           // Position AND size — most expensive
<motion.div layout="position"> // Position only — cheaper
<motion.div layout="size">     // Size only
```

#### Shared Layout (layoutId)

When two elements represent the same thing in different states, give them the
same `layoutId` — Framer Motion animates the transition automatically:

```tsx
{tabs.map(tab => (
  <button key={tab} onClick={() => setActive(tab)}>
    {tab}
    {active === tab && (
      <motion.div
        layoutId="tab-indicator"
        className="indicator"
        transition={{ type: "spring", stiffness: 400, damping: 30 }}
      />
    )}
  </button>
))}
```

Set `borderRadius` in the `style` prop (not CSS class) to prevent distortion during layout animation.

#### Directional Variants

For navigation that slides in the direction of travel:

```tsx
const variants = {
  initial: (direction: number) => ({
    x: `${110 * direction}%`,
    opacity: 0,
  }),
  active: { x: "0%", opacity: 1 },
  exit: (direction: number) => ({
    x: `${-110 * direction}%`,
    opacity: 0,
  }),
}

// direction = 1 for forward, -1 for back
<AnimatePresence mode="popLayout" custom={direction}>
  <motion.div
    key={currentStep}
    variants={variants}
    initial="initial"
    animate="active"
    exit="exit"
    custom={direction}
  />
</AnimatePresence>
```

#### Dynamic Height

Use `react-use-measure` to animate container height when content changes:

```tsx
import useMeasure from "react-use-measure"

const [ref, bounds] = useMeasure()

<motion.div animate={{ height: bounds.height }}>
  <div ref={ref}>
    {/* content that changes size */}
  </div>
</motion.div>
```

### Performance Tips (all stacks)

- `will-change: transform, opacity` — only on elements that actually animate. Remove after animation if possible.
- Avoid creating new objects during render/animation (causes GC pauses).
- Monitor with Chrome DevTools: Performance tab → record during animation. Target 60fps (16.67ms per frame).
- If an animation stutters on mid-range devices, simplify or remove it.

---

## Section 4: Pattern Library

These patterns teach **foundations**, not recipes. Each one solves a common UI
problem. Learn the underlying technique, then adapt it to your stack and product.

Arc: use these to know what's possible when speccing interactions.
Dev: study the techniques, then build what Arc specced — don't copy blindly.
The code is Framer Motion / CSS because that's the most common React stack,
but every pattern here translates to Vue, Svelte, vanilla JS, or native platforms.

---

### Pattern 1: Reveal on Hover

**Foundation:** CSS-only transitions using transform + opacity. No JavaScript
framework needed. The simplest animation pattern — start here.

**Where you'd use it:** Cards, thumbnails, portfolio grids, product listings,
any container where secondary info appears on interaction.

**Key techniques:**
- `overflow: hidden` on parent clips the sliding content
- `transform: translateY()` slides content in/out
- Combined transition on transform + opacity for polish
- `:focus-visible` makes it keyboard-accessible (not just mouse hover)

```css
.card {
  overflow: hidden;
}

.card-description {
  transform: translateY(calc(100% + 8px));
  opacity: 0;
  transition: transform 350ms ease, opacity 350ms ease;
}

.card:hover .card-description,
.card:focus-visible .card-description {
  transform: translateY(0%);
  opacity: 1;
}
```

**The principle:** Content that slides in from a natural origin (bottom of card)
feels physically correct. Content that just appears (opacity alone) feels flat.
Combine movement with fade for the most polished result.

---

### Pattern 2: Stacking & Positioning

**Foundation:** CSS custom properties (`--index`) for dynamic layout calculations.
Data attributes trigger mount animations. No animation library required.

**Where you'd use it:** Toast notifications, stacked cards, notification centers,
layered UI elements, badge counters, queue displays.

**Key techniques:**
- `--index` custom property drives position with `calc()`
- `data-mounted="true"` triggers CSS transition (works in any stack)
- Stack position is computed: `translateY(calc(var(--index) * -110%))`
- Mount animation: start off-screen, transition to calculated position

```css
.toast {
  transform: translateY(100%);
  opacity: 0;
  transition: transform 350ms ease, opacity 350ms ease;
}

.toast[data-mounted="true"] {
  transform: translateY(calc(var(--index) * (100% + var(--gap)) * -1));
  opacity: 1;
}
```

```js
// In any framework or vanilla JS:
element.style.setProperty("--index", index);
element.dataset.mounted = "true";
```

**The principle:** CSS custom properties make animation data-driven without
coupling to a framework. The same pattern works if you're calculating position
from a data source, a list index, or a scroll position.

---

### Pattern 3: Staggered Reveal

**Foundation:** CSS `@keyframes` with `calc()`-based delays. Each element
animates in sequence using its index — pure CSS, no JS orchestration.

**Where you'd use it:** Hero text, feature lists, landing page sections,
onboarding steps, grid items loading in, dashboard cards appearing.

**Key techniques:**
- Split content into individual elements (letters, words, cards)
- `--index` custom property controls `animation-delay` via `calc()`
- `animation-fill-mode: backwards` keeps elements hidden before their delay
- Single `@keyframes` definition reused across all children

```css
.item {
  animation: reveal 300ms cubic-bezier(.19, 1, .22, 1);
  animation-fill-mode: backwards;
  animation-delay: calc(var(--index) * 0.05s);
}

@keyframes reveal {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
}
```

**The principle:** Stagger creates rhythm and draws the eye through content in
a deliberate order. But stagger more than 8 items and the last ones feel slow —
past 8, load them all at once. The delay between items (30-80ms) controls the
feel: shorter = snappier, longer = more dramatic.

---

### Pattern 4: Shared Element Transition

**Foundation:** One visual identity, two states. The element morphs between
position, size, and shape — the user perceives continuity instead of a jump cut.

**Where you'd use it:** Tab indicators, selected states, thumbnail-to-detail
views, avatar-to-profile, any "same thing, different context" transition.

**Key techniques:**
- Same identity key links two different DOM elements
- Framework animates position + size between the two states automatically
- `borderRadius` must be in `style` prop (not CSS class) to animate correctly
- The visual stays on screen throughout — no disappear/reappear

```tsx
{/* Framer Motion example */}
{items.map(item => (
  <button key={item} onClick={() => setActive(item)}>
    {item}
    {active === item && (
      <motion.div
        layoutId="indicator"
        style={{ borderRadius: 8 }}
        transition={{ type: "spring", stiffness: 400, damping: 30 }}
      />
    )}
  </button>
))}
```

**The principle:** Shared element transitions eliminate the cognitive gap between
"I was looking at X" and "now I'm looking at Y." The brain tracks the moving
element and understands the relationship. This is the same foundation behind
iOS hero transitions, Material Design container transforms, and macOS window
morphing. In CSS-only stacks, you can approximate this with `View Transitions API`.

---

### Pattern 5: Dynamic Resize

**Foundation:** Measure real content bounds, then animate the container to match.
Solves the "animate height: auto" problem that CSS can't do natively.

**Where you'd use it:** Accordions, expandable drawers, collapsible sections,
FAQ lists, settings panels, any content that grows or shrinks.

**Key techniques:**
- Inner element is measured (ref + bounds)
- Outer element animates `height` to measured value
- `overflow: hidden` on outer clips during transition
- This is one exception to "never animate height" — the outer container
  animates height while inner content uses transform

```tsx
{/* Framer Motion + react-use-measure */}
const [ref, bounds] = useMeasure()

<motion.div animate={{ height: bounds.height }} style={{ overflow: "hidden" }}>
  <div ref={ref}>
    {/* Content that changes size */}
    {expanded && <p>Extra content here</p>}
  </div>
</motion.div>
```

**The principle:** Users expect containers to grow and shrink smoothly — a
sudden height jump feels broken. The measure-then-animate pattern works in
any framework. In CSS-only stacks, `calc-size(auto)` is emerging but not widely
supported yet. Until then, you need JS measurement.

---

### Pattern 6: Directional Navigation

**Foundation:** Step content slides in from the direction of travel. Forward =
slides from right. Back = slides from left. The container height adapts to
each step's content size.

**Where you'd use it:** Onboarding flows, wizards, checkout steps, multi-step
forms, settings panels, tab content transitions.

**Key techniques:**
- Direction state (`1` or `-1`) drives variant selection
- Enter slides from `110% * direction`, exit slides to `-110% * direction`
- Reduced motion fallback: fade only (no slide)
- Container animates height to content using measure pattern (Pattern 5)
- `AnimatePresence mode="popLayout"` handles overlap during transition

```tsx
const variants = {
  initial: (dir: number) => ({ x: `${110 * dir}%`, opacity: 0 }),
  active: { x: "0%", opacity: 1 },
  exit: (dir: number) => ({ x: `${-110 * dir}%`, opacity: 0 }),
}

// Reduced motion: just fade
const reducedVariants = {
  initial: { opacity: 0 },
  active: { opacity: 1 },
  exit: { opacity: 0 },
}

<MotionConfig transition={{ duration: 0.5, type: "spring", bounce: 0 }}>
  <motion.div animate={{ height: bounds.height }}>
    <div ref={ref}>
      <AnimatePresence mode="popLayout" custom={direction}>
        <motion.div
          key={currentStep}
          variants={reduced ? reducedVariants : variants}
          initial="initial"
          animate="active"
          exit="exit"
          custom={direction}
        />
      </AnimatePresence>
    </div>
  </motion.div>
</MotionConfig>
```

**The principle:** Directional motion communicates progress. Sliding forward
means "advancing." Sliding back means "returning." This spatial metaphor is
universal — it works in any culture, any platform, any stack. The reduced
motion fallback (fade-only) preserves the state change without the movement.

---

### Pattern 7: Inline Expansion

**Foundation:** A small element (button, chip, avatar) morphs into a larger
element (form, popover, card) using shared identity. Multiple nested elements
can participate in the same transition.

**Where you'd use it:** Feedback buttons that expand into forms, user avatars
that expand into profile cards, action chips that expand into detail views,
compose buttons that expand into editors, quick-reply that expands into full response.

**Key techniques:**
- `layoutId` on both the trigger and the expanded element
- Nested `layoutId` elements (e.g., button text → form placeholder)
- Form state transitions: idle → loading → success (each state animates)
- Click-outside and Escape to dismiss
- `borderRadius` in style prop prevents distortion

```tsx
{/* Button state */}
<motion.button layoutId="container" style={{ borderRadius: 8 }}>
  <motion.span layoutId="label">Feedback</motion.span>
</motion.button>

{/* Expanded state */}
<AnimatePresence>
  {open && (
    <motion.div layoutId="container" style={{ borderRadius: 12 }}>
      <motion.span layoutId="label" style={{ opacity: 0.5 }}>
        Feedback
      </motion.span>
      <textarea autoFocus />
      <button type="submit">
        <AnimatePresence mode="popLayout">
          <motion.span
            key={formState}
            initial={{ opacity: 0, y: -25 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 25 }}
          >
            {formState === "loading" ? "Sending..." : "Send"}
          </motion.span>
        </AnimatePresence>
      </button>
    </motion.div>
  )}
</AnimatePresence>
```

**The principle:** The user's eye tracks the expanding element — there's no
"where did that form come from?" moment. Nested shared identities (the label
moving from button to placeholder) reinforce that this is the *same thing*
in a new shape. The state transitions inside (idle → loading → success) keep
the user informed without leaving the expanded context.

---

### Pattern 8: Element-to-View Expansion

**Foundation:** An element in a grid or list expands to fill the viewport.
Multiple child elements (image, title, description) animate together as a
coordinated group. An overlay dims the background.

**Where you'd use it:** Product detail views, image galleries, portfolio
pieces, article previews, dashboard cards that expand to full reports,
playlist items expanding to now-playing view, any list → detail transition.

**Key techniques:**
- Multiple `layoutId` elements animate in concert (image, heading, description)
- `whileTap={{ scale: 0.98 }}` gives press feedback before expansion
- Overlay fades in/out independently with `AnimatePresence`
- Dismiss via click-outside and Escape key
- Hidden content (long description) becomes visible in expanded state
- `borderRadius` transitions from rounded (card) to square (fullscreen)

```tsx
{/* Card in grid */}
<motion.div layoutId={`card-${id}`} whileTap={{ scale: 0.98 }}
  style={{ borderRadius: 20 }}>
  <motion.img layoutId={`image-${id}`} src={image} />
  <motion.h2 layoutId={`title-${id}`}>{title}</motion.h2>
  <motion.p layoutId={`desc-${id}`}>{shortDesc}</motion.p>
</motion.div>

{/* Expanded view */}
<AnimatePresence>
  {active && (
    <>
      <motion.div className="overlay"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
      <motion.div layoutId={`card-${id}`} style={{ borderRadius: 0 }}>
        <motion.img layoutId={`image-${id}`} src={image} />
        <motion.h2 layoutId={`title-${id}`}>{title}</motion.h2>
        <motion.p layoutId={`desc-${id}`}>{shortDesc}</motion.p>
        <p>{fullDescription}</p>
        <button onClick={close}>✕</button>
      </motion.div>
    </>
  )}
</AnimatePresence>
```

**The principle:** This is Pattern 4 (shared element transition) scaled up.
Instead of one element morphing, a *group* of elements morph together — they
maintain their spatial relationship throughout the animation. The user never
loses context because every piece of the card is visually tracked to its new
position. The press feedback (`whileTap`) tells the user "this is interactive"
before the big transition happens. In CSS-only stacks, the `View Transitions
API` with `view-transition-name` achieves a similar coordinated morph.

---

*Based on principles from [Emil Kowalski's "Animations on the Web"](https://animations.dev/) and the [animate-skill](https://github.com/delphi-ai/animate-skill).*

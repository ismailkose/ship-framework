# Framer Motion Deep-Dive

> **React only.** This file applies when the stack uses React + Framer Motion.
> If your stack doesn't use Framer Motion, skip this file — the CSS deep-dive
> and performance reference still apply.
>
> Arc scans this to know what's possible before speccing interactions.
> Dev reads the sections relevant to what they're building.
> Pol reads this for specific feedback on motion implementation.

---

## Installation

```bash
npm install framer-motion
# Optional — for dynamic height measurement:
npm install react-use-measure
# Optional — for click-outside detection:
npm install usehooks-ts
```

---

## Motion Components

Any HTML element becomes animatable by prefixing with `motion.`:

```tsx
import { motion } from "framer-motion"

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, ease: "easeOut" }}
>
  Content
</motion.div>
```

### Props Reference

| Prop | Description |
|------|-------------|
| `initial` | Starting state (or `false` to skip mount animation) |
| `animate` | Target state |
| `exit` | Exit state (requires `AnimatePresence`) |
| `transition` | Animation config (duration, easing, spring) |
| `whileHover` | State while hovered |
| `whileTap` | State while pressed |
| `whileFocus` | State while focused |
| `whileInView` | State while in viewport |
| `whileDrag` | State while dragging |
| `layout` | Animate layout changes automatically |
| `layoutId` | Shared identity for cross-element transitions |

---

## AnimatePresence

Required for exit animations. Wraps elements that may be removed from DOM.

```tsx
import { AnimatePresence, motion } from "framer-motion"

<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  )}
</AnimatePresence>
```

### Modes

```tsx
<AnimatePresence
  mode="sync"       // Default — enter and exit happen simultaneously
  mode="wait"       // Wait for exit to complete before enter
  mode="popLayout"  // Remove exiting elements from layout flow
  initial={false}   // Skip animation on first mount
  onExitComplete={() => {}}  // Callback when all exits finish
>
```

| Mode | Behavior | Use when |
|------|----------|----------|
| `sync` | Enter + exit overlap | Crossfade, parallel transitions |
| `wait` | Exit completes, then enter starts | Sequential page transitions. Note: nearly doubles perceived duration — adjust timing |
| `popLayout` | Exiting element removed from flow | Step wizards, tabs with different heights, list reordering |

### Reading Presence State

Components can detect they're exiting and change behavior:

```tsx
import { useIsPresent } from "framer-motion"

function Card() {
  const isPresent = useIsPresent()
  // true while mounted normally, false during exit animation

  return (
    <motion.div
      style={{ position: isPresent ? "static" : "absolute" }}
      // Disable interactions during exit:
      // pointerEvents: isPresent ? "auto" : "none"
    >
      {isPresent ? "Normal content" : "Exiting..."}
    </motion.div>
  )
}
```

**Important:** `useIsPresent` must be called from a child component of
AnimatePresence — not in the parent where you conditionally render. This
means you need a separate component, not inline JSX.

### Manual Exit Control

For async cleanup (saving drafts, network requests) before unmounting:

```tsx
import { usePresence } from "framer-motion"

function Notification() {
  const [isPresent, safeToRemove] = usePresence()

  useEffect(() => {
    if (!isPresent) {
      // Do async cleanup, then signal safe to unmount
      saveDraft().then(() => safeToRemove())
    }
  }, [isPresent, safeToRemove])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {isPresent ? "Active" : "Saving..."}
    </motion.div>
  )
}
```

The exit animation runs in parallel with your async work. The element
unmounts when both the animation finishes and `safeToRemove` is called.

### Nested Exit Coordination

By default, nested AnimatePresence children vanish instantly when the parent
exits. The `propagate` prop triggers exit animations on both levels:

```tsx
<AnimatePresence>
  {show && (
    <motion.div exit={{ opacity: 0 }} transition={{ duration: 0.8 }}>
      <AnimatePresence propagate>
        {items.map(item => (
          <motion.div
            key={item}
            exit={{ opacity: 0, filter: "blur(10px)" }}
            transition={{ duration: 0.5 }}
          >
            {item}
          </motion.div>
        ))}
      </AnimatePresence>
    </motion.div>
  )}
</AnimatePresence>
```

Without `propagate`, the children disappear immediately when the parent
exits. With it, both parent and children animate their exits. Coordinate
the durations — child exits should complete within the parent's exit
duration.

---

## Variants

Define named animation states. Parent variants can orchestrate children.

```tsx
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,   // Delay between each child
      delayChildren: 0.2,      // Initial delay before children start
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

<motion.ul variants={container} initial="hidden" animate="visible">
  {items.map(i => (
    <motion.li key={i} variants={item}>{i}</motion.li>
  ))}
</motion.ul>
```

### Custom Variants (Directional)

Pass dynamic values with the `custom` prop:

```tsx
const slideVariants = {
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

<AnimatePresence mode="popLayout" custom={direction}>
  <motion.div
    key={step}
    variants={slideVariants}
    initial="initial"
    animate="active"
    exit="exit"
    custom={direction}  // 1 = forward, -1 = back
  />
</AnimatePresence>
```

---

## Layout Animations

Animate position and size changes automatically.

```tsx
// Animate position AND size (most expensive)
<motion.div layout>

// Position only (cheaper)
<motion.div layout="position">

// Size only
<motion.div layout="size">
```

**Important:** `layout` is expensive. Use sparingly. Prefer `layout="position"`
when you only need position changes.

### Shared Layout (layoutId)

Two elements with the same `layoutId` animate between each other:

```tsx
{tabs.map(tab => (
  <button key={tab} onClick={() => setActive(tab)}>
    {tab}
    {active === tab && (
      <motion.div
        layoutId="tab-indicator"
        className="indicator"
        style={{ borderRadius: 8 }}  // Must be in style, not CSS class
        transition={{ type: "spring", stiffness: 400, damping: 30 }}
      />
    )}
  </button>
))}
```

**`borderRadius` must be in the `style` prop** — not a CSS class. Otherwise it
distorts during the layout animation.

### LayoutGroup

Prevent independent layout animations from interfering:

```tsx
import { LayoutGroup } from "framer-motion"

<LayoutGroup>
  <TabsA />  {/* These layout animations */}
</LayoutGroup>
<LayoutGroup>
  <TabsB />  {/* Won't conflict with these */}
</LayoutGroup>
```

### Nested layoutId

Multiple elements can participate in the same shared transition:

```tsx
{/* Collapsed state */}
<motion.button layoutId="container" style={{ borderRadius: 8 }}>
  <motion.span layoutId="label">Feedback</motion.span>
</motion.button>

{/* Expanded state */}
<motion.div layoutId="container" style={{ borderRadius: 12 }}>
  <motion.span layoutId="label">Feedback</motion.span>
  <textarea />
</motion.div>
```

Both `container` and `label` morph together — the user sees one smooth expansion.

---

## Gestures

### Hover and Tap

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.97 }}
  transition={{ type: "spring", stiffness: 400, damping: 30 }}
>
  Click me
</motion.button>
```

### Drag

```tsx
<motion.div
  drag              // Both axes
  drag="x"          // Horizontal only
  drag="y"          // Vertical only
  dragConstraints={{ left: 0, right: 300, top: 0, bottom: 200 }}
  dragElastic={0.2}       // Elasticity outside constraints (0 = none, 1 = full)
  dragMomentum={true}     // Continue after release
  dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
  onDragStart={(event, info) => {}}
  onDrag={(event, info) => {}}
  onDragEnd={(event, info) => {}}
>
  Drag me
</motion.div>
```

### Drag Info Object

```tsx
onDrag={(event, info) => {
  info.point     // { x, y } current position
  info.delta     // { x, y } change since last frame
  info.offset    // { x, y } offset from drag start
  info.velocity  // { x, y } current velocity
}}
```

---

## Hooks

### useMotionValue

Values that update without re-rendering the component:

```tsx
import { motion, useMotionValue, useTransform } from "framer-motion"

function Component() {
  const x = useMotionValue(0)

  // Derive other values from x
  const opacity = useTransform(x, [-100, 0, 100], [0, 1, 0])
  const rotate = useTransform(x, [-100, 100], [-10, 10])

  return (
    <motion.div
      drag="x"
      style={{ x, opacity, rotate }}
    />
  )
}
```

### useSpring

Spring-animated motion value — follows a target with spring physics:

```tsx
import { useSpring, useMotionValue } from "framer-motion"

function Component() {
  const x = useMotionValue(0)
  const springX = useSpring(x, { stiffness: 300, damping: 30 })

  return (
    <motion.div
      onMouseMove={(e) => x.set(e.clientX)}
      style={{ x: springX }}
    />
  )
}
```

### useScroll

Track scroll progress of the page or a container:

```tsx
import { useScroll, useTransform, motion } from "framer-motion"

// Page scroll progress bar
function ProgressBar() {
  const { scrollYProgress } = useScroll()

  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-1 bg-blue-500 origin-left"
      style={{ scaleX: scrollYProgress }}
    />
  )
}

// Container scroll
const { scrollYProgress } = useScroll({
  target: containerRef,
  offset: ["start end", "end start"]  // When to start/end tracking
})
```

### useInView

Detect when an element enters the viewport:

```tsx
import { useInView } from "framer-motion"
import { useRef } from "react"

function Component() {
  const ref = useRef(null)
  const isInView = useInView(ref, {
    once: true,        // Only trigger once
    margin: "-100px"   // Trigger 100px before entering
  })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
    />
  )
}
```

### useReducedMotion

Respect the user's OS reduced motion setting:

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

---

## Transition Options

### Duration-Based

```tsx
{
  duration: 0.3,
  delay: 0.1,
  ease: "easeOut",              // Named easing
  ease: [0.23, 1, 0.32, 1],    // Cubic bezier array
}
```

### Spring Physics

```tsx
{
  type: "spring",
  stiffness: 400,    // Tightness (higher = snappier)
  damping: 30,       // Resistance (higher = less oscillation)
  mass: 1,           // Weight (higher = slower, more momentum)
}
```

### Duration-Based Spring

```tsx
{
  type: "spring",
  duration: 0.3,
  bounce: 0.2,       // 0 = no bounce, 1 = max bounce
}
```

### Per-Property

```tsx
{
  opacity: { duration: 0.2 },
  x: { type: "spring", stiffness: 300 },
}
```

### Repeat

```tsx
{
  repeat: Infinity,
  repeatType: "reverse",    // "loop" | "reverse" | "mirror"
  repeatDelay: 0.5,
}
```

---

## Keyframes in Framer Motion

Multi-step animations using arrays:

```tsx
<motion.div
  animate={{
    x: [0, 100, 0],
    opacity: [0, 1, 1, 0],
    scale: [1, 1.2, 1],
  }}
  transition={{
    duration: 2,
    times: [0, 0.5, 1],    // When each keyframe occurs (0-1)
    ease: "easeInOut",
  }}
/>
```

---

## MotionConfig

Set default transition for all nested motion components:

```tsx
import { MotionConfig } from "framer-motion"

<MotionConfig transition={{ duration: 0.5, type: "spring", bounce: 0 }}>
  {/* All motion components inside inherit this transition */}
  <YourApp />
</MotionConfig>
```

### Global Reduced Motion

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

| Value | Effect |
|-------|--------|
| `"never"` | Normal animations (default) |
| `"always"` | Skip all animations |
| `"user"` | Respect system `prefers-reduced-motion` |

---

## Dynamic Height Animation

Use `react-use-measure` to animate container height when content changes:

```tsx
import { motion } from "framer-motion"
import useMeasure from "react-use-measure"

function Expandable() {
  const [ref, bounds] = useMeasure()
  const [expanded, setExpanded] = useState(false)

  return (
    <motion.div
      animate={{ height: bounds.height }}
      transition={{ duration: 0.3 }}
      style={{ overflow: "hidden" }}
    >
      <div ref={ref}>
        <p>Always visible content</p>
        {expanded && <p>Extra content that changes the height</p>}
      </div>
    </motion.div>
  )
}
```

Outer div animates height. Inner div is measured. Content changes trigger smooth resize.

---

*Based on Framer Motion API. Reference adapted from [Emil Kowalski's "Animations on the Web"](https://animations.dev/).*

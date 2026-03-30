# CSS Animation Deep-Dive

> **Stack-agnostic.** Everything here works in any framework or vanilla HTML/CSS.
> Dev reads this when building CSS animations. Pol reads this for specific feedback.

---

## Transforms

Transforms change position, size, or rotation without affecting layout. GPU-accelerated.

### Transform Functions

```css
/* Translation (movement) */
transform: translateX(10px);
transform: translateY(-20px);
transform: translate(10px, -20px);     /* X, Y */
transform: translate3d(10px, 20px, 0); /* X, Y, Z */

/* Scale */
transform: scale(1.1);        /* Uniform */
transform: scaleX(0.5);
transform: scale(0.5, 1.5);   /* X, Y */

/* Rotation */
transform: rotate(45deg);
transform: rotateX(45deg);    /* 3D — around X axis */
transform: rotateY(45deg);    /* 3D — around Y axis */

/* Combining — order matters */
transform: translateY(-10px) scale(1.05) rotate(5deg);
```

### Transform Origin

Controls the point around which transforms occur:

```css
transform-origin: center;       /* Default */
transform-origin: top left;
transform-origin: 50% 100%;     /* Center bottom */
transform-origin: 0 0;          /* Top left corner */
```

Scale from a corner, rotate from an edge — `transform-origin` makes it feel
physically grounded.

### 3D Transforms

```css
/* Enable 3D space on parent */
.parent {
  perspective: 1000px;           /* Distance from viewer — lower = more dramatic */
  perspective-origin: center;
}

/* 3D transforms on children */
.child {
  transform: rotateY(45deg);
  transform-style: preserve-3d;  /* Maintain 3D for nested elements */
  backface-visibility: hidden;   /* Hide back of element during rotation */
}
```

Use 3D sparingly. Card flips, subtle parallax, and tilt effects are the common
use cases. If it feels like a tech demo, dial it back.

---

## Transitions

Transitions animate property changes over time — the simplest way to add motion.

### Syntax

```css
/* Individual properties */
transition-property: transform, opacity;
transition-duration: 200ms;
transition-timing-function: ease-out;
transition-delay: 0ms;

/* Shorthand */
transition: transform 200ms ease-out, opacity 150ms ease-out 50ms;
/*          property  duration timing   property duration timing  delay */
```

### Common Patterns

```css
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

/* Fade toggle */
.element {
  opacity: 0;
  transition: opacity 200ms ease-out;
}
.element.visible {
  opacity: 1;
}

/* Slide in from bottom */
.panel {
  transform: translateY(calc(100% + 8px));
  opacity: 0;
  transition: transform 300ms var(--ease-out-quint),
              opacity 300ms var(--ease-out-quint);
}
.panel.open {
  transform: translateY(0);
  opacity: 1;
}
```

### Transition Tips

- Only transition `transform` and `opacity` — everything else causes layout recalculation
- Use separate durations per property when needed: fade can be faster than movement
- `transition: all` is tempting but expensive — list specific properties
- Don't transition on page load — use `@keyframes` for mount animations

---

## Keyframe Animations

For multi-step animations and mount effects.

### Basic Syntax

```css
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.element-enter {
  animation: fade-in-up 300ms var(--ease-out-quint);
}
```

### Multi-Step

```css
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}
```

### Animation Properties

```css
animation-name: fade-in-up;
animation-duration: 300ms;
animation-timing-function: ease-out;
animation-delay: 0ms;
animation-iteration-count: 1;       /* or 'infinite' */
animation-direction: normal;        /* 'reverse', 'alternate', 'alternate-reverse' */
animation-fill-mode: forwards;      /* 'none', 'forwards', 'backwards', 'both' */
animation-play-state: running;      /* or 'paused' */

/* Shorthand */
animation: fade-in-up 300ms ease-out 0ms 1 normal forwards;
```

### Fill Modes

This trips people up — here's what each does:

| Mode | Before animation | After animation |
|------|-----------------|-----------------|
| `none` | Element's own styles | Element's own styles |
| `forwards` | Element's own styles | Keeps final keyframe |
| `backwards` | Applies first keyframe during delay | Element's own styles |
| `both` | Applies first keyframe during delay | Keeps final keyframe |

**For staggered children:** use `backwards` so elements stay hidden during their delay:

```css
.stagger-item {
  animation: fade-in-up 300ms cubic-bezier(.19, 1, .22, 1);
  animation-fill-mode: backwards;
  animation-delay: calc(var(--index) * 0.05s);
}
```

---

## Clip-Path Animations

Clip-path creates masked areas that can be animated — reveals, wipes, shape morphs.

### Common Shapes

```css
/* Circle — expands from center */
clip-path: circle(0% at center);     /* Hidden */
clip-path: circle(50% at center);    /* Full */

/* Inset — rectangle crop */
clip-path: inset(0);                 /* Full visibility */
clip-path: inset(50%);               /* Collapsed to center */
clip-path: inset(0 50% 0 0);        /* Right half hidden */
/* inset(top right bottom left) */

/* Polygon — any shape */
clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);  /* Rectangle */
clip-path: polygon(50% 0, 100% 100%, 0 100%);         /* Triangle */
```

### Animated Reveal

```css
.reveal {
  clip-path: circle(0% at center);
  transition: clip-path 500ms var(--ease-out-quint);
}
.reveal.visible {
  clip-path: circle(100% at center);
}
```

### Tab Indicator with Clip-Path

```css
/* Background slides via clip-path — no layout animation needed */
.tab-indicator {
  position: absolute;
  inset: 0;
  background: var(--accent);
  border-radius: 8px;
  transition: clip-path 200ms var(--ease-out-quint);
}
```

Update `clip-path` via JS based on active tab position. Cheaper than animating
`left` + `width`.

---

## Data-Attribute Patterns

Trigger animations from any framework (or vanilla JS) using data attributes:

```css
/* Toast mount animation */
.toast {
  transform: translateY(100%);
  opacity: 0;
  transition: transform 350ms ease, opacity 350ms ease;
}
.toast[data-mounted="true"] {
  transform: translateY(0);
  opacity: 1;
}

/* Accordion expand */
.accordion-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 300ms var(--ease-out-quint);
}
.accordion-content[data-open="true"] {
  grid-template-rows: 1fr;
}
.accordion-content > div {
  overflow: hidden;
}
```

```js
// Trigger from any framework
element.dataset.mounted = "true";
element.dataset.open = "true";
```

---

## CSS Custom Properties for Animation

Dynamic values controlled from JS, animated in CSS:

```css
/* Position from index */
.stack-item {
  transform: translateY(calc(var(--index) * -110%));
  transition: transform 350ms ease;
}

/* Stagger delay from index */
.stagger-item {
  animation-delay: calc(var(--index) * 50ms);
}

/* Progress-driven animation */
.progress-bar {
  transform: scaleX(var(--progress, 0));
  transform-origin: left;
  transition: transform 300ms var(--ease-out-quint);
}
```

```js
// Set from JS
element.style.setProperty("--index", index);
element.style.setProperty("--progress", 0.75);
```

Keeps animation logic in CSS, data in JS. Clean separation, works everywhere.

---

## View Transitions API

CSS-native shared element transitions — no libraries needed. The browser snapshots
the current state, applies your DOM changes, then animates between them.

### Basic Usage

```css
/* Give elements a shared identity */
.thumbnail { view-transition-name: hero; }
.detail-image { view-transition-name: hero; }

/* Control the transition animation */
::view-transition-group(hero) {
  animation-duration: 300ms;
  animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
}

/* Style the old/new snapshots individually */
::view-transition-old(hero) { animation: fade-out 200ms ease; }
::view-transition-new(hero) { animation: fade-in 300ms ease; }
```

```js
// Trigger from JS
document.startViewTransition(() => {
  // Make your DOM changes here
  dialog.showModal();
});
```

### When to Use

- **Lightbox/detail views** — thumbnail morphs to full image
- **Page transitions** — elements glide to new positions across navigations
- **State changes** — card expands to detail, list item opens to form

### When NOT to Use

- High-frequency interactions (tabs, toggles) — too slow
- Elements that don't share visual identity — confusing morph
- When Framer Motion `layoutId` is available — more control, better DX

This is Pattern 4 (shared element transition) from `animation.md` implemented
in pure CSS. Use when you don't have Framer Motion or want zero-JS transitions.

---

*Reference adapted from [Emil Kowalski's "Animations on the Web"](https://animations.dev/) and [Raphael Salaja's userinterface.wiki](https://www.userinterface.wiki/).*

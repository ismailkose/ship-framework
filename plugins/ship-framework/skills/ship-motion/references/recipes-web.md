<!-- ship-reference
id: motion-recipes-web
kind: expert
sources: emil-skills@d16ebe6 (skills/animate/RECIPES.md; skills/emil-design-eng/SKILL.md "Component Building Principles", "CSS Transform Mastery", "clip-path for Animation"); https://motion.dev/docs (2026-09-23); https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API (2026-09-23); impeccable@9d715cc (idea only: a reveal keeps content visible by default; pbakaus/impeccable, Apache-2.0)
reviewed: 2026-09-28
-->

# Motion recipes — web

Ready-to-build implementations for the cases that come up most, from the motion
authority's recipes and design-engineering notes (license notice at the end). Start from the
recipe, then adapt — don't rebuild from scratch. SwiftUI versions: `recipes-swiftui.md`.

Curves are the tokens from `animation.md`:

```css
:root {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
}
```

The recipes show the full-motion version. **Reduced motion is one rule for all of them:** keep
opacity and colour changes, drop translate/scale — movement becomes a short fade or an instant
change, never nothing (`reduced-motion.md`). For the two recipes most products have:

```css
@media (prefers-reduced-motion: reduce) {
  .button:active { transform: none; }                     /* no squash; the pressed colour still acknowledges */
  .drawer { transition: opacity 150ms var(--ease-out); }
  .drawer[data-closed] { transform: none; opacity: 0; }   /* slide becomes a fade; keep it inert when closed */
}
```

Apply the same shape to each recipe you use. Hover motion also gets the
`@media (hover: hover) and (pointer: fine)` gate. (`scripts/checks/web-behaviour.sh` in the Ship repo renders these
two in Chromium with reduced motion on and off.)

## Button press

Any pressable element. `scale()` scales children too — label and icons come along, which is
what makes it read as a physical press. Keep it subtle (0.95–0.98).

```css
.button {
  transition: transform 160ms var(--ease-out);
}
.button:active {
  transform: scale(0.97);
}
```

No hover gating needed — `:active` is a real press on touch. Gate any `:hover` styling separately.

## Dropdown, popover, menu, select

Scales out of its trigger, not out of thin air. The `transform-origin` is the whole point.

```css
.popover {
  transform-origin: var(--transform-origin); /* Base UI supplies this */
  transition:
    opacity 200ms var(--ease-out),
    transform 200ms var(--ease-out);
}
.popover[data-starting-style],
.popover[data-ending-style] {
  opacity: 0;
  transform: scale(0.95);
}
```

## Tooltip

Same shape as a popover, faster. The initial delay prevents accidental activation; once one
tooltip is open, neighbours open instantly — skipping both delay and animation makes the
whole toolbar feel faster.

```css
.tooltip {
  transform-origin: var(--transform-origin);
  transition:
    transform 125ms var(--ease-out),
    opacity 125ms var(--ease-out);
}
.tooltip[data-starting-style],
.tooltip[data-ending-style] {
  opacity: 0;
  transform: scale(0.97);
}
/* Once one tooltip is open, neighbours open instantly */
.tooltip[data-instant] {
  transition-duration: 0ms;
}
```

## Modal

The one popover that stays centered — it isn't anchored to a trigger. Animate the backdrop's
opacity alongside it so they read as one surface.

```css
.modal {
  transform-origin: center; /* exempt — not anchored to a trigger */
  transition:
    opacity 250ms var(--ease-out),
    transform 250ms var(--ease-out);
}
.modal[data-starting-style],
.modal[data-ending-style] {
  opacity: 0;
  transform: scale(0.96);
}
.backdrop {
  transition: opacity 250ms var(--ease-out);
}
```

## Drawer / sheet

`translateY(100%)` moves by the drawer's own height, whatever its content — how Vaul hides a
drawer before animating it in. Add drag and it becomes a gesture problem (`fluid-interfaces.md`).

```css
.drawer {
  transform: translateY(0);
  transition: transform 500ms var(--ease-drawer);
}
.drawer[data-closed] {
  transform: translateY(100%);
}
```

## Toast

`ease` rather than ease-out, slightly slower than typical UI: Sonner reads as elegant partly
because its motion is tuned to the component's personality rather than the generic UI budget.
Transitions, not keyframes — toasts are added rapidly and must retarget.

```css
.toast {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity 400ms ease,
    transform 400ms ease;

  @starting-style {
    opacity: 0;
    transform: translateY(100%);
  }
}
```

Without `@starting-style`, fall back to a mount flag (this replaces the React
`useEffect`-sets-mounted pattern where supported):

```jsx
useEffect(() => { setMounted(true); }, []);
// <div data-mounted={mounted}>
```

When toasts stack and the list reflows, the opacity change has to work against the height
change — there's no formula for that pair; adjust until it feels right, then check again the
next day. Invisible edge cases that make it feel loved: pause timers while the tab is hidden,
fill the gaps between stacked toasts (a pseudo-element) so hover holds, capture the pointer
during drag.

## Accordion / collapse

One of the few animations that costs layout every frame — keep it short. Measure the content
height in JS (or use a headless primitive that supplies it) rather than animating to `auto`.

```css
.content {
  overflow: hidden;
  transition:
    height 200ms var(--ease-out),
    opacity 200ms var(--ease-out);
}
```

With Motion, measure with an inner element and animate the outer one — never both on the same
element (measure → animate → measure loop); guard the first render so it doesn't animate from 0.

## Stagger a group entrance

For a list or grid seen occasionally — not one scrolled past all day. Decorative: never block
interaction while it plays. 30–80ms apart.

```css
.item {
  opacity: 0;
  transform: translateY(8px);
  animation: fadeIn 300ms var(--ease-out) forwards;
}
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
.item:nth-child(4) { animation-delay: 150ms; }

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

(Keyframes are fine here: a one-shot entrance isn't re-triggered rapidly.) For long lists, set
the delay from an index: `animation-delay: calc(var(--index) * 50ms)`.

## Hold to confirm

For destructive actions where a plain click is too easy. Slow where the user decides, snappy
where the system responds. `linear` is correct for the fill — it's progress, and progress
shouldn't ease.

```css
.overlay {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 200ms var(--ease-out); /* release: snappy */
}
.button:active .overlay {
  clip-path: inset(0 0 0 0);
  transition: clip-path 2s linear; /* press: slow and deliberate */
}
.button:active {
  transform: scale(0.97);
}
```

## Tab indicator with a color transition

Timing individual color transitions across a tab list never quite lands. Duplicate the tab
list, style the copy as active (background and text color), clip the copy so only the active
tab shows, and animate the clip. Text and background change in perfect sync because they're one
element being revealed, not two colors interpolated.

```css
.tabs-active-copy {
  clip-path: inset(0 60% 0 20%); /* driven by the active tab's position */
  transition: clip-path 250ms var(--ease-in-out);
}
```

## Scroll reveal

Marketing surfaces only — never functional UI visited daily. Fire once; re-animating on every
scroll-by is an interface fighting its reader.

```css
.reveal { transition: clip-path 600ms var(--ease-in-out); }
/* hidden only once the script that reveals it is running — if it never runs, the content shows */
.reveal-ready .reveal:not([data-visible]) { clip-path: inset(0 0 100% 0); }
@media (prefers-reduced-motion: reduce) {
  .reveal-ready .reveal:not([data-visible]) { clip-path: none; }
}
```

Trigger with `IntersectionObserver`, or Motion's `useInView` with
`{ once: true, margin: "-100px" }`; the same script adds `reveal-ready` to `<html>` just before it
starts observing. Content is visible by default: a reveal enhances a page that already works.

## More clip-path tools

`clip-path: inset(top right bottom left)` — each value eats into the element from that side.
- **Image reveal on scroll:** `inset(0 0 100% 0)` → `inset(0 0 0 0)` (above).
- **Comparison slider:** overlay two images, clip the top one with `inset(0 50% 0 0)`, and
  drive the right inset from the drag position. No extra DOM, hardware-accelerated.

## Masking a crossfade that won't settle

When two states overlap visibly and no easing or duration fixes it, blur the seam. Without
blur the eye reads two objects swapping; blur blends them into one transformation. Keep it
under 20px — heavy blur is expensive, especially in Safari. Pair with the 0.97 press for a
polished button state change. Under reduced motion, drop the blur and keep the fade.

```css
.button-content {
  transition:
    filter 200ms ease,
    opacity 200ms ease;
}
.button-content.transitioning {
  filter: blur(2px);
  opacity: 0.7;
}
```

## Programmatic, without a library

WAAPI gives JS control with CSS performance — hardware-accelerated, interruptible, no bundle
cost.

```js
element.animate(
  [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
  { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' }
);
```

## Shared element / page transitions

- **View Transitions API** (no library): give both states the same `view-transition-name`,
  wrap the DOM change in `document.startViewTransition(() => …)`, and style
  `::view-transition-group(name)` with the curves above. For list → detail, lightbox, and
  route changes; not for tabs or toggles (too slow for high frequency).
- **Motion `layoutId`**: the same element identity in two places animates between them. Put
  `borderRadius` in `style` so it doesn't distort. Use a critically damped spring
  (`{ type: "spring", duration: 0.35, bounce: 0 }`).
- **Direction-aware steps** (wizards, onboarding): content slides in from the direction of
  travel (forward from the trailing edge, back from the leading edge) with
  `AnimatePresence mode="popLayout"` and a `custom` direction; reduced motion → fade only.

## Motion (motion.dev) essentials

The library knows its own API; these are the Ship-specific rules on top:
- Use the full `transform` string when the page is busy (`performance.md`).
- `AnimatePresence` for exit animations; exits ease-out and never slower than enters.
- Springs: `{ type: "spring", duration, bounce }`; bounce 0 by default, ≤0.3 when used.
- `useSpring` only for decorative, pointer-driven values.
- `<MotionConfig reducedMotion="user">` at the app root (`reduced-motion.md`).
- Cache transition objects outside render so a re-render doesn't allocate new ones.

## Transforms worth knowing

- **Percentages in `translate()`** are relative to the element — prefer them to hardcoded px.
- **3D:** `rotateX()` / `rotateY()` with `transform-style: preserve-3d` give real depth — orbits,
  coin flips — without JS (and a reduced-motion path without them).
- **`transform-origin`:** every transform runs from an anchor; default center. Set it to where
  the trigger lives.

<!--
Portions of this file are adapted from emilkowalski/skills (https://github.com/emilkowalski/skills), MIT License.

Copyright (c) 2026 Emil Kowalski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-->

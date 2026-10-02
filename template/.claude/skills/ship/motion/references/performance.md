<!-- ship-reference
id: motion-performance
kind: mixed
sources: emil-skills@d16ebe6 (performance-cheatsheet.md; skills/emil-design-eng/SKILL.md "Performance Rules", "Debugging Animations"; skills/review-animations/STANDARDS.md "Performance"); /Applications/Xcode.app/.../IDEIntelligenceChat.framework/Versions/A/Resources/swiftui-specialist-ref-environment.md.packaged (Xcode 27.0, 2026-09-23) — pointed to, not copied
reviewed: 2026-09-23
-->

# Motion performance and debugging

The motion authority's frame-rate rules (license notice at the end), with the SwiftUI equivalents.

## Cheatsheet

| Problem | Solution |
| --- | --- |
| Animation stutters | Animate `transform`/`opacity`, not `width`/`top` |
| Long list scrolls slowly | Virtualize — only render what's visible (`List` / `LazyVStack` on iOS) |
| Blur causes perf issues | Keep animated `blur()` under 20px |
| Motion's `x`/`y` drops frames | Animate the full `transform` string instead |
| Random properties animate | Don't do `transition: all`; list exact properties |
| React re-renders every frame | Write to `ref.current.style`, not state |
| Element shifts 1px as motion starts | `will-change: transform` (only once you see it) |

## Web rules

- **Only `transform` and `opacity`.** They skip layout and paint and run on the compositor.
  `padding`, `margin`, `height`, `width`, `top`, `left` (also `border-width`, `font-size`)
  trigger layout, paint, and composite on every frame.
- **CSS variables are inherited.** Changing one on a parent recalculates styles for every child
  — updating `--swipe-amount` on a drawer container with many items is a recalc storm. Set
  `transform` on the element directly:

```js
element.style.setProperty('--swipe-amount', `${distance}px`); // ✗ recalc on all children
element.style.transform = `translateY(${distance}px)`;        // only this element
```

- **Motion shorthands are not hardware-accelerated.** `x`, `y`, `scale` run through
  `requestAnimationFrame` on the main thread and drop frames when the page is busy loading,
  scripting, or painting. Use the full transform string:

```jsx
<motion.div animate={{ x: 100 }} />                          // ✗ drops frames under load
<motion.div animate={{ transform: "translateX(100px)" }} />  // hardware accelerated
```

  At Vercel, a dashboard tab animation built on shared layout animations dropped frames during
  page loads; moving it to CSS (off the main thread) fixed it.
- **CSS animations beat JS under load.** CSS for predetermined motion; JS for dynamic,
  interruptible motion; **WAAPI** when JS control is needed at CSS performance.
- **`will-change`** only on elements that actually animate, only once a problem is visible (the
  1px shift), and never on more than a handful — each promoted layer costs memory. Never
  `will-change: all`.
- Cache animation config objects outside render; batch DOM reads before writes (no layout
  thrashing).

## SwiftUI rules

- **Animate render-time modifiers** (`opacity`, `scaleEffect`, `offset`, `rotationEffect`,
  `blur`) for anything per-frame; frame and layout changes re-run layout each frame — fine for
  an accordion, not for a drag.
- **Per-frame values don't belong in `@State` read by big view trees.** Drag translation,
  scroll offset, and timeline progress invalidate every view that reads them. Keep them local
  to the moving view, or in an `@Observable` model read only where needed, coarsened to
  thresholds when possible. Xcode 27's bundled SwiftUI guidance covers the pattern in depth:
  `swiftui-specialist-ref-environment` in
  `/Applications/Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/`.
- **Scroll-driven visuals:** `.scrollTransition` and `.visualEffect` run in the renderer
  without re-evaluating `body` — prefer them to reading scroll offsets into state.
- **Stable identity** in `ForEach` (stable, unique ids) is what lets insertions, removals, and
  moves animate; unstable ids turn every update into remove + insert.
- Don't branch a view with `if`/`else` just to change a modifier — it breaks identity and the
  animation becomes a remove/insert. Use a ternary on the modifier's value.
- `.geometryGroup()` when a parent's animated geometry makes children interpolate oddly.
- Keep animated `blur` radii small (≈2pt) and avoid stacking many live materials.

## Measuring

- **Web:** DevTools › Performance (long frames over 16.7ms at 60Hz / 8.3ms at 120Hz, purple
  layout blocks, green paint); Rendering › FPS meter, Paint flashing, Layer borders; the
  Animations panel for speed and frame stepping.
- **iOS:** Instruments › Animation Hitches and the SwiftUI template (body updates per frame);
  test on a real device — the Simulator doesn't represent GPU cost or ProMotion.
- Target 60fps everywhere, 120fps on ProMotion displays; a hitch in a gesture is worse than a
  hitch in a fade.

## Debugging feel

Motion can be mechanically correct and still feel wrong.
- **Slow motion:** run at 2–5× duration (web: DevTools Animations panel playback; iOS
  Simulator: Debug › Slow Animations). Look for: colors crossfading cleanly vs two states
  overlapping; easing that starts or stops abruptly; the wrong `transform-origin` / anchor;
  opacity, transform, and color out of sync.
- **Frame by frame:** DevTools Animations panel reveals timing drift between coordinated
  properties.
- **Real devices for touch:** drawers and swipes need a phone — hit the dev server by IP and
  use Safari remote devtools; on iOS, run on device. The Simulator is a fallback, not a test.
- **Fresh eyes the next day:** imperfections invisible during development surface later.

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

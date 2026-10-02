<!-- ship-reference
id: motion-vocabulary
kind: expert
sources: emil-skills@d16ebe6 (skills/animation-vocabulary/SKILL.md); iPhoneSimulator27.0.sdk SwiftUI/SwiftUICore .swiftinterface (2026-09-23)
reviewed: 2026-09-23
-->

# Motion vocabulary

A reverse-lookup glossary: a vague description of a motion effect → its exact term, so the
founder (or a prompt) can ask for it by name. The glossary is the motion
authority's, quoted verbatim (license notice at the end); the native-name table after
it is Ship's. For naming an effect — building it is `animation.md` and the recipes.

## How to answer

1. **Read for intent, not keywords.** People describe what they see or feel ("springy", "slides
   off", "draws itself in"); map the sensation to a term.
2. **Quote the glossary verbatim** — its descriptions are authoritative.
3. **Disambiguate close terms** — *Clip-path* vs *Mask*, *Pop in* vs *Bounce*, *Shared element
   transition* vs *Layout animation* — so the person can pick.
4. **No exact match:** name the closest term and say it's an approximation, or describe the
   effect in glossary words ("a *stagger* of *scale-in* entrances").
5. **Stay within the glossary.** If a term isn't here, say so rather than inventing one.
6. **Keep it tight** — lead with the term; expand only if asked. On iOS, add the SwiftUI name
   from the table below.

Format — best match first, then 1–2 alternates with how they differ:

```text
**Morph** — One shape smoothly turns into another shape, e.g. Dynamic Island.

Close alternates:
- **Crossfade** — if they simply fade over each other in the same spot.
- **Shared element transition** — if an element travels and transforms from one position into another.
```

Examples: "a popover that grows out of the button instead of its middle" → **Origin-aware
animation**; "the iOS scroll that resists and snaps back when pulled too far" →
**Rubber-banding**.

## Glossary

### Entrances & Exits — how elements appear and disappear
- **Fade in / Fade out** — Element appears or disappears by changing opacity.
- **Slide in** — Element enters by sliding in from off-screen (left, right, top, or bottom).
- **Scale in** — Element grows from smaller to full size as it appears, often paired with a fade.
- **Pop in** — Element appears with a slight overshoot, like it bounces into place.
- **Reveal** — Content is uncovered gradually, often by animating a clip-path or mask.
- **Enter / Exit** — The animation an element plays when it's added to or removed from the screen.

### Sequencing & Timing — coordinating multiple elements or moments
- **Keyframes** — Defined points in an animation (0%, 50%, 100%) that the browser fills the gaps between.
- **Interpolation / Tween** — Generating all the in-between frames between a start and end value, so motion is continuous.
- **Stagger** — Animate several items one after another with a small delay between each, creating a cascade.
- **Orchestration** — Deliberately timing multiple animations so they feel like one coordinated motion.
- **Delay** — Time before an animation starts.
- **Duration** — How long an animation takes.
- **Fill mode** — Whether an element keeps its first or last frame's styles before the animation starts or after it ends (e.g. forwards).
- **Stepped animation** — An animation that is divided into discrete steps, like a countdown timer.

### Movement & Transforms — changing an element's position, size, or angle
- **Translate** — Move an element along the X or Y axis.
- **Scale** — Make an element bigger or smaller.
- **Rotate** — Spin an element around a point.
- **Skew** — Slant an element along the X or Y axis, shearing it out of its rectangular shape.
- **3D tilt / Flip** — Rotate in 3D space (rotateX / rotateY) to add depth.
- **Perspective** — How strong the 3D effect looks — a lower value exaggerates depth, like the viewer is closer.
- **Transform origin** — The anchor point a scale or rotation grows or spins from.
- **Origin-aware animation** — An element animates out of its trigger, like a popover growing from the button that opened it instead of from its own center which is the default in CSS.

### Transitions Between States — connecting one state, view, or element to another
- **Crossfade** — One element fades out as another fades in, in the same spot.
- **Continuity transition** — A change that keeps the user oriented by visually connecting before and after. For example, making the same rectangle bigger and smaller.
- **Morph** — One shape smoothly turns into another shape, e.g. Dynamic Island.
- **Shared element transition** — An element travels and transforms from one position into another, like a thumbnail expanding into a card.
- **Layout animation** — When an element's size or position changes, it animates to the new spot instead of snapping.
- **Accordion / Collapse** — A section smoothly expands and collapses its height to show or hide content.
- **Direction-aware transition** — Content slides one way going forward and the opposite way going back, so navigation has a sense of direction.

### Scroll — motion tied to scrolling or navigating between views
- **Scroll reveal** — Elements fade or slide into place as they enter the viewport.
- **Scroll-driven animation** — An animation whose progress is tied directly to scroll position.
- **Parallax** — Background and foreground move at different speeds while scrolling, creating depth.
- **Page transition** — An animation that plays when navigating from one page or route to another.
- **View transition** — The browser morphs between two states or pages, connecting shared elements.

### Feedback & Interaction — responding to the user's actions
- **Hover effect** — Visual change when the cursor moves over an element.
- **Press / Tap feedback** — A subtle scale-down when an element is clicked, so it feels physical.
- **Hold to confirm** — A progress effect that fills up while the user holds a button.
- **Drag** — Moving an element by grabbing it, often with momentum when released.
- **Drag to reorder** — Dragging items in a list to rearrange them, while the others shift to make room.
- **Swipe to dismiss** — Dragging an element off-screen to close it, like a drawer or toast.
- **Rubber-banding** — Resistance and snap-back when you drag past a boundary (the iOS overscroll feel).
- **Shake / Wiggle** — A quick side-to-side jitter signaling an error or rejected input.
- **Ripple** — A circle expanding from the point of a tap, confirming the press.

### Easing — how speed changes over an animation
- **Easing** — The rate at which an animation speeds up or slows down.
- **Ease-out** — Starts fast, ends slow. The default for most UI and anything responding to the user.
- **Ease-in** — Starts slow, ends fast. Usually avoided; can feel sluggish.
- **Ease-in-out** — Slow, fast, slow. Good for elements already on screen moving from A to B.
- **Linear** — Constant speed. Avoid for UI; reserve for spinners or marquees.
- **Cubic-bezier** — A custom easing curve you define for precise control.
- **Asymmetric easing** — A curve that accelerates and decelerates at different rates. Feels more alive than a symmetric one.

### Spring Animations — physics-based motion as an alternative to fixed-duration easing
- **Spring** — Motion driven by physics (tension, mass, damping) rather than a set duration.
- **Stiffness / Tension** — How strongly the spring pulls toward its target. Higher feels snappier.
- **Damping** — How quickly a spring settles. Lower damping means more bounce and oscillation.
- **Mass** — How heavy the animated element feels. More mass makes it slower and more sluggish.
- **Bounce** — A spring that overshoots and settles, adding playfulness.
- **Perceptual duration** — How long a spring feels finished, even though it keeps micro-settling underneath.
- **Momentum** — Motion that carries velocity, especially after a drag or interruption.
- **Velocity** — How fast and in which direction an element is moving. A spring carries it into the next animation when interrupted, so a flicked element keeps its speed.
- **Interruptible animation** — An animation that can be smoothly redirected mid-flight instead of finishing first.

### Looping & Ambient Motion — animations that run on their own
- **Marquee** — Text or content that scrolls continuously in a loop.
- **Loop** — An animation that repeats, a set number of times or infinitely.
- **Alternate (yoyo)** — A loop that plays forward then reverses each iteration, instead of jumping back to the start.
- **Orbit** — An element circling around another in a continuous path.
- **Pulse** — A gentle repeating scale or opacity change to draw attention.
- **Float** — A gentle, continuous up-and-down drift that makes a static element feel alive and weightless.
- **Idle animation** — Subtle motion that plays while an element is just sitting there, waiting to be interacted with.

### Polish & Effects — the small touches that separate good from great
- **Blur** — A blur filter used to soften an element or mask tiny imperfections.
- **Clip-path** — Clipping an element to a shape, used for reveals, masks, and before/after sliders.
- **Mask** — Hiding or revealing parts of an element using a shape or gradient — like clip-path, but with soft, fadeable edges.
- **Before / after slider** — A draggable divider that wipes between two overlaid images to compare them.
- **Line drawing** — An SVG path that draws itself in, like an invisible pen tracing it.
- **Text morph** — Text that animates character by character when it changes, drawing attention to the new value.
- **Skeleton / Shimmer** — A placeholder with a moving sheen shown while content loads.
- **Number ticker** — Digits rolling or counting up to a value.
- **Tabular numbers** — Fixed-width digits so numbers don't shift around as they change. Essential for tickers, timers, and counters.
- **Typewriter** — Text appearing one character at a time, as if being typed.

### Performance — what keeps motion smooth instead of stuttering
- **Frame rate (FPS)** — Frames drawn per second. 60fps is the baseline for smooth motion; 120fps on newer displays.
- **Jank** — Visible stutter when the browser drops frames because it can't keep up with the animation.
- **Dropped frame** — A frame the browser missed its deadline to draw, causing a tiny hitch in motion.
- **Compositing** — Letting the GPU move or fade an element on its own layer without redoing layout or paint.
- **will-change** — A CSS hint that an element is about to animate, so the browser can promote it to its own layer ahead of time.
- **Layout thrashing** — Animating properties like width, height, top, or left that force the browser to recalculate layout every frame, causing jank.

### Principles to Know — concepts that guide when and how to animate
- **Purposeful animation** — Motion should serve a function — orient, give feedback, show relationships — not just decorate.
- **Anticipation** — A small wind-up in the opposite direction before a move, hinting at what's about to happen.
- **Follow-through** — Parts of an element keep moving and settle slightly after the main motion stops, adding weight.
- **Squash & stretch** — Deforming an element as it moves to convey weight, speed, and flexibility.
- **Perceived performance** — The right animation makes an interface feel faster, even when it isn't.
- **Frequency of use** — The more often a user sees an animation, the shorter and subtler it should be.
- **Spatial consistency** — Animating so an element keeps its identity and position across states, so users never lose track of where things went.
- **Hardware acceleration** — Animating transform and opacity lets the GPU keep motion smooth.
- **Reduced motion** — Respecting the user's prefers-reduced-motion setting by toning down or removing motion.

## Native names (SwiftUI)

| Term | SwiftUI |
| --- | --- |
| Fade in / out | `.transition(.opacity)` |
| Slide in | `.transition(.move(edge:))`, `.transition(.push(from:))` |
| Scale in | `.transition(.scale(scale: 0.95).combined(with: .opacity))` (never bare `.scale` — it starts at ~0) |
| Pop in | spring with bounce 0.2–0.3 on a scale-in — delight tier only |
| Enter / Exit | `.transition(_:)`; different paths: `.asymmetric(insertion:removal:)` |
| Keyframes | `KeyframeAnimator` / `.keyframeAnimator` |
| Stagger | per-item `.animation(_:value:)` with `.delay(index * 0.05)` |
| Orchestration | `PhaseAnimator`, `withAnimation(_:completion:)` |
| Transform origin | `anchor:` on `.scaleEffect` / `.rotationEffect` / `.scale(scale:anchor:)` |
| Crossfade | `.transition(.opacity)`, `.contentTransition(.opacity)` |
| Morph | `glassEffectID` in a `GlassEffectContainer` (iOS 26), `matchedGeometryEffect` |
| Shared element transition | `matchedGeometryEffect`; `.navigationTransition(.zoom(sourceID:in:))` (iOS 18) |
| Layout animation | any animated layout change (`withAnimation`), `.geometryGroup()` |
| Accordion / Collapse | `DisclosureGroup` |
| Direction-aware transition | `NavigationStack` push/pop; `.push(from:)` |
| Scroll-driven animation | `.scrollTransition`, `.visualEffect` |
| Page transition / View transition | `NavigationStack`, `.navigationTransition` |
| Press / Tap feedback | `ButtonStyle` using `configuration.isPressed` |
| Hold to confirm | `onLongPressGesture(minimumDuration:perform:onPressingChanged:)` |
| Drag / Swipe to dismiss | `DragGesture`; sheets: `.sheet` (native) |
| Drag to reorder | `List` + `.onMove`, `.draggable`/`.dropDestination` |
| Rubber-banding | built into `ScrollView`; custom drags: see `fluid-interfaces.md` |
| Spring / Bounce / Damping | `Spring(duration:bounce:)`, `Spring(response:dampingRatio:)` |
| Perceptual duration | `Spring.duration` / `response` (not `settlingDuration`) |
| Momentum / Velocity | `DragGesture.Value.velocity`, `predictedEndTranslation`, `Transaction.tracksVelocity` |
| Interruptible animation | state-driven `withAnimation` / `.animation(_:value:)` (retargets by default) |
| Loop / Pulse | `.repeatForever(autoreverses:)`, `.symbolEffect(.pulse)` |
| Text morph / Number ticker | `.contentTransition(.numericText(value:))` |
| Tabular numbers | `.monospacedDigit()` |
| Skeleton / Shimmer | `.redacted(reason: .placeholder)` |
| Blur | `.blur(radius:)`, `.transition(.blurReplace)` |
| Mask / Clip-path | `.mask { }`, `.clipShape(_:)` |
| Line drawing | `Shape.trim(from:to:)` animated |
| Reduced motion | `@Environment(\.accessibilityReduceMotion)` |
| Frame rate / Dropped frame | Instruments › Animation Hitches |

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

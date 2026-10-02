<!-- ship-reference
id: motion-fluid-interfaces
kind: mixed
sources: emil-skills@d16ebe6 (skills/apple-design/SKILL.md §1–11; skills/emil-design-eng/SKILL.md "Gesture and Drag Interactions"; skills/animate/RECIPES.md "Drag to dismiss"); https://developer.apple.com/tutorials/data/documentation/swiftui/transaction/tracksvelocity.json (2026-09-23); iPhoneSimulator27.0.sdk SwiftUI .swiftinterface (2026-09-23)
reviewed: 2026-09-23
-->

# Fluid interfaces — gestures, springs, interruption

Apple's fluid-interface principles (WWDC 2018 *Designing Fluid Interfaces*) as distilled in
the motion authority's Apple-design rules (license notice at the end), plus its drag rules from
its toast and drawer components. Web code as written upstream; SwiftUI code verified against the iOS 27 SDK.

**The through-line:** an interface feels alive when motion starts from the current on-screen
value, inherits the user's velocity, projects momentum forward, and can be grabbed and reversed
at any instant. Springs make all of this natural — they're interruptible and velocity-aware by
construction. An interface is fluid when it behaves like the physical world: it responds
instantly, moves continuously, carries momentum, resists at boundaries, and can be redirected
mid-motion. Apple frames design as serving four needs — safety/predictability, understanding,
achievement, joy; every rule here serves one.

## 1. Response — kill latency

The moment lag appears, the feeling of directness falls off a cliff.
- **Respond on press-down, not release.** Highlight the instant it's pressed.
  SwiftUI `ButtonStyle.isPressed` and `onLongPressGesture(onPressingChanged:)` fire on
  touch-down; web `:active` / `pointerdown`.
- **Audit every latency on the input path** — debounces, artificial timers, transition waits,
  the web's ~300ms tap delay. Anything not essential is a regression.
- **Feedback is continuous during the interaction**, not only at the end: a drag, slider, or
  drawer tracks the pointer 1:1 the whole way — never animate only when the gesture completes.

## 2. Direct manipulation — 1:1 tracking

Touch and content move together. Keep the grab offset — snapping the element's center to the
finger breaks the illusion.
- Web: Pointer Events + `setPointerCapture` so tracking continues outside the element; keep a
  short position/time history for release velocity.
- SwiftUI: `DragGesture.Value.translation` is relative to where the drag started, so applying it
  as an offset preserves the grab point; `value.velocity` (iOS 17) gives release velocity in
  points per second.

## 3. Interruptibility — the most important principle

The thought and the gesture happen in parallel. A user can grab an element mid-flight and
reverse it without waiting; a closing panel that's grabbed again follows the finger instead of
finishing its close first.
- **Never lock out input during a transition** (no `allowsHitTesting(false)` / disabled
  controls for the duration of an animation).
- **Always animate from the presentation (current on-screen) value**, never the logical target
  — starting from the target causes a visible jump. SwiftUI does this for you: a new
  `withAnimation` on a property that's mid-animation blends from where it is, and springs
  merge the in-flight velocity. On the web, read the live transform before retargeting.
- **Gesture-driven motion uses springs**, not CSS transitions or keyframes — neither can be
  grabbed and reversed smoothly. (CSS transitions *do* retarget, which is why they're right for
  rapidly toggled UI like toasts; a finger needs a spring.)
- **Blend velocity at a reversal** — replacing one animation with another creates a velocity
  discontinuity, a brick wall. iOS's additive animations and velocity-carrying spring libraries
  avoid it.
- **Decompose 2D motion into independent X and Y springs** — one spring on a 2D distance
  desyncs when the axes have different velocities. SwiftUI animates a `CGSize` / `CGPoint`
  offset per component, so this holds by default.

## 4. Behavior over animation — springs

Animation is a conversation between the person and the object, not a script. A fixed-duration
animation can't respond to new input; a spring can — new input just moves the target. Use
springs for anything a user can touch.

Apple replaced mass/stiffness/damping with two designer-friendly parameters:
- **Damping ratio** — overshoot. 1.0 = critically damped, no bounce. Below 1.0 overshoots and
  oscillates; lower is bouncier.
- **Response** — how quickly the value reaches the target, in seconds. **Not a duration** — a
  spring's settle time emerges from its parameters (`Spring.settlingDuration`).

Defaults: most UI at damping 1.0; bounce (damping ≈0.8) **only when the gesture itself carried
momentum**. Values Apple ships:

| Interaction | Damping | Response | SwiftUI |
| --- | --- | --- | --- |
| Move / reposition (PiP) | 1.0 | 0.4 | `.spring(response: 0.4, dampingFraction: 1.0)` |
| Rotation | 0.8 | 0.4 | `.spring(response: 0.4, dampingFraction: 0.8)` |
| Drawer / sheet (released from a drag) | 0.8 | 0.3 | `.spring(response: 0.3, dampingFraction: 0.8)` |

Web (Motion): the `bounce` + `duration` API maps closely to damping + response —
`{ type: 'spring', bounce: 0, duration: 0.4 }` by default,
`{ type: 'spring', bounce: 0.2, duration: 0.4 }` only because a flick preceded it.

## 5. Velocity handoff — the seam between drag and animation

When the gesture ends, the animation continues at the finger's exact velocity — no visible seam
between dragging and animating. This is the detail that most separates fluid from fine.
- **SwiftUI: automatic.** Gesture `onChanged` / `updating` callbacks set
  `Transaction.tracksVelocity`, so a spring started in `onEnded` begins at the tracked
  velocity. Update state *without* an animation during the drag, then animate with a spring on
  release. (Outside gestures — a slider, a stream of server updates — set
  `transaction.tracksVelocity = true` yourself on the intermediate changes.)
- **APIs that take relative velocity** (`Animation.interpolatingSpring(_:initialVelocity:)`,
  UIKit `initialSpringVelocity`) want it normalised by the remaining distance:
  `relativeVelocity = gestureVelocity / (target − current)`. Element at 50, target 150 (100
  to go), finger at 50 pt/s → 0.5. Motion takes absolute px/s (`velocity`) directly.

## 6. Momentum projection — animate to where the gesture is going

Don't snap to the nearest point from the release position. Project the resting point from
velocity — exactly like scroll deceleration — then snap to the target nearest *that*. This is
what makes a flick throw the element. Apple's function (from the *Designing Fluid Interfaces*
sample code; not the textbook `v²/(2·decel)`):

```js
// decelerationRate ≈ 0.998 for normal scroll feel; 0.99 for snappier
function project(initialVelocity /* px/s */, decelerationRate = 0.998) {
  return (initialVelocity / 1000) * decelerationRate / (1 - decelerationRate);
}
const projectedEndpoint = currentPosition + project(releaseVelocity);
const target = nearestSnapPoint(projectedEndpoint);    // choose from the projection
animateSpringTo(target, { velocity: releaseVelocity }); // then hand off velocity (§5)
```

In SwiftUI, `DragGesture.Value.predictedEndTranslation` is the system's own projection; the
function below reproduces Apple's for custom deceleration rates (`UIScrollView` uses 0.998
normal, 0.99 fast). **Decide commit vs reverse by the velocity's sign**, not by position.

## 7. Spatial consistency

If something disappears one way, it's expected to come back from there.
- **Enter and exit along the same path.** In from the right, out to the right.
- **Anchor to the source** — menus, popovers, sheets originate from their trigger.
- **Mirror the easing on reversible transitions** — the return path uses the inverse curve
  (swap and invert the cubic-bézier control points: `(x1, y1, x2, y2)` →
  `(1 − x2, 1 − y2, 1 − x1, 1 − y1)`).

## 8. Hint in the direction of the gesture

People predict the end state from the trajectory. In-between frames should telegraph where
things are going — Control Center modules grow up and out toward the finger — not interpolate
blindly.

## 9. Rubber-banding — soft boundaries

At an edge, resist progressively instead of stopping hard. A hard stop reads as frozen; rising
resistance reads as "responsive, but there's nothing more here". SwiftUI `ScrollView` already
does this; custom drags need it:

```js
// The further past the bound, the less the element follows
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

The authority's drawer rules say the same: **damping at boundaries** (dragging a drawer up when it's
already open moves it less the further it goes) and **friction instead of hard stops**.

## 10. Gesture details — the feel checklist

- **Tap:** highlight on touch-down, commit on touch-up; ~10pt of hysteresis around the target;
  allow cancel by dragging away and back (SwiftUI `Button` does all three).
- **Drag / swipe:** a small movement threshold (~10pt) before committing to a direction, then
  1:1. `DragGesture(minimumDistance:)` defaults to 10.
- **Detect plausible gestures in parallel** from the first move, then cancel the losers once
  intent is clear (`simultaneousGesture`, `highPriorityGesture`). Avoid recognisers that only
  report a final state — they throw away the continuous tracking feedback needs.
- **Minimise disambiguation delays** — double-tap detection delays every single tap; pay it
  only where double-tap truly exists.
- **Pointer capture** once a drag starts (web: `setPointerCapture`).
- **Multi-touch protection** — ignore extra touches after the drag begins
  (`if (isDragging) return`), or switching fingers makes the element jump.
- **Momentum dismissal** (Sonner): don't require a distance threshold alone — dismiss when
  `Math.abs(distance) / elapsedMs > 0.11` (average speed over the drag) *or* the distance
  threshold is crossed. A quick flick is enough.

## 11. Frame-level smoothness

Smoothness is what's in the frames, not just the frame rate. Keep per-frame positional change
under the strobing threshold; for very fast motion a subtle blur/stretch encodes speed better
than a sharp streak. The display-synced clock is `requestAnimationFrame` on the web,
`CADisplayLink` / `TimelineView(.animation)` on iOS. Animate compositor-friendly properties
(`transform`, `opacity`; SwiftUI render modifiers) — see `performance.md`.

## Drag to dismiss — web

Springs, not durations, because the user can reverse mid-motion. Set the transform on the
dragged element directly — a CSS variable on the parent restyles every child.

```js
// Dismiss on a flick, not just on distance
const timeTaken = Date.now() - dragStartTime.current;
const velocity = Math.abs(swipeAmount) / timeTaken;
if (Math.abs(swipeAmount) >= SWIPE_THRESHOLD || velocity > 0.11) {
  dismiss();
}
element.style.transform = `translateY(${distance}px)`;
// Settle with a spring so an interrupted drag keeps its velocity
// { type: "spring", duration: 0.5, bounce: 0.2 }
```

## Drag to dismiss — SwiftUI

A card that follows the finger 1:1, rubber-bands when dragged up past its resting point,
dismisses on distance *or* a flick (Sonner's average-speed rule and Apple's projection both
shown), and settles with a momentum spring that inherits the finger's velocity. Under Reduce
Motion the finger still drives it directly (tracking gestures is fine); the release settles
without overshoot.

```swift
import SwiftUI

/// Apple's momentum projection (Designing Fluid Interfaces). 0.998 ≈ normal scroll, 0.99 ≈ fast.
func project(velocity: CGFloat, decelerationRate: CGFloat = 0.998) -> CGFloat {
    (velocity / 1000) * decelerationRate / (1 - decelerationRate)
}

/// Progressive resistance past a boundary.
func rubberband(_ overshoot: CGFloat, dimension: CGFloat, constant: CGFloat = 0.55) -> CGFloat {
    (overshoot * dimension * constant) / (dimension + constant * abs(overshoot))
}

struct DismissibleCard: View {
    var onDismiss: () -> Void
    @State private var offsetY: CGFloat = 0
    @State private var dragStart: Date?
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private let dismissDistance: CGFloat = 120
    private let cardHeight: CGFloat = 320

    var body: some View {
        RoundedRectangle(cornerRadius: 24)
            .fill(.background)
            .frame(height: cardHeight)
            .offset(y: offsetY)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        if dragStart == nil { dragStart = value.time }
                        let dy = value.translation.height
                        // 1:1 downward; rubber-band upward. No animation here — velocity is tracked.
                        offsetY = dy >= 0 ? dy : rubberband(dy, dimension: cardHeight)
                    }
                    .onEnded { value in
                        let elapsedMs = max(value.time.timeIntervalSince(dragStart ?? value.time) * 1000, 1)
                        let averageSpeed = abs(value.translation.height) / elapsedMs   // pt per ms
                        let projected = value.translation.height + project(velocity: value.velocity.height)
                        dragStart = nil
                        let flick = averageSpeed > 0.11 && value.velocity.height > 0
                        if value.translation.height >= dismissDistance || flick || projected > cardHeight / 2 {
                            // motion: momentum — the tracked drag velocity carries into this spring
                            withAnimation(reduceMotion ? .spring(duration: 0.3, bounce: 0) : .spring(duration: 0.4, bounce: 0.2)) {
                                offsetY = cardHeight + 80
                            } completion: {
                                onDismiss()
                            }
                        } else {
                            withAnimation(reduceMotion ? .spring(duration: 0.3, bounce: 0) : .spring(duration: 0.4, bounce: 0.2)) {
                                offsetY = 0
                            }
                        }
                    }
            )
            .accessibilityAction(.escape) { onDismiss() }
    }
}
```

`accessibilityAction(.escape)` gives VoiceOver users (two-finger scrub) the same dismissal
without the gesture.

## Snap points (sheets, carousels)

Choose the snap point nearest the *projected* position, then spring there. Prefer the system:
`.presentationDetents` for sheets, `.scrollTargetBehavior(.paging)` / `.viewAligned` for
carousels — both already project and hand off velocity.

```swift
import SwiftUI

struct SnappingPanel: View {
    let snapPoints: [CGFloat] = [0, 240, 480]    // offsets from the top resting position
    @State private var restingY: CGFloat = 240
    @GestureState private var dragY: CGFloat = 0

    var body: some View {
        RoundedRectangle(cornerRadius: 24)
            .fill(.thinMaterial)
            .offset(y: restingY + dragY)
            .gesture(
                DragGesture()
                    .updating($dragY) { value, state, _ in state = value.translation.height }
                    .onEnded { value in
                        let projected = restingY + value.predictedEndTranslation.height
                        let target = snapPoints.min { abs($0 - projected) < abs($1 - projected) } ?? restingY
                        // motion: momentum — drawer released from a drag (Apple: damping 0.8, response 0.3)
                        withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                            restingY = target
                        }
                    }
            )
    }
}
```

## Quick reference

| Need | Technique | Value |
| --- | --- | --- |
| Default UI spring | Critically damped | damping 1.0, response 0.3–0.4 |
| Momentum / flick spring | Slight bounce | damping ≈0.8, response 0.3–0.4 |
| Gesture → spring velocity | Hand off release velocity | SwiftUI automatic; else `v / (target − current)` if normalised |
| Flick landing point | Project momentum | `current + (v/1000)·d/(1−d)`, d ≈ 0.998 |
| Interrupt cleanly | Start from the presentation value | read the live transform |
| Avoid the reversal brick wall | Carry velocity through retarget | spring that blends velocity |
| Reversible transition | Mirror the curve | inverse cubic-bézier |
| Commit vs reverse | Velocity **sign**, not position | at release |
| 1:1 drag | Pointer capture / `DragGesture` | keep the grab offset |
| Feedback | On press-down, continuous | never only at the end |
| Boundary | Rubber-band | progressive resistance |
| Flick dismissal | Average speed | `> 0.11` px/ms, or distance threshold |

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

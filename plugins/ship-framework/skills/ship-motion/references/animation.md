<!-- ship-reference
id: motion-decisions
kind: mixed
sources: emil-skills@d16ebe6 (skills/emil-design-eng/SKILL.md; skills/animate/SKILL.md; skills/review-animations/STANDARDS.md); https://developer.apple.com/design/human-interface-guidelines/motion (2026-09-23); iPhoneSimulator27.0.sdk SwiftUICore.swiftinterface (2026-09-23); https://developer.android.com/develop/ui/compose/animation/customize (2026-09-23)
reviewed: 2026-09-23
-->

# Motion decisions

The order in which motion decisions get made — whether it animates at all, why, with what
tool, which properties, which curve or spring, how it interrupts and exits. From Ship's designated
motion authority (license notice at the end); iOS values
verified against the iOS 27 SDK.

**Tags.** `[platform]` SDK / HIG / WCAG fact or requirement · `[expert]` the motion authority ·
`[ship]` Ship default. **Precedence:** platform & accessibility > product decisions
(`design-model.yaml` motion tokens, `DECISIONS.md`, taste entries) > founder preferences >
HIG/Material guidance > `[expert]` > `[ship]`. A project token that differs from a value here
is a decision, not a bug — use the token; a validator warning is a prompt to confirm, not to
rewrite.

Two failure modes, the first worse: animating something that shouldn't animate; animating the
right thing with the wrong ingredients (`ease-in` on an entrance, `scale(0)`, keyframes on a
toast, a sluggish duration). Don't present motion options as a menu — make the call, give the
reason in one line, write the code.

## 1. Should this animate at all? `[expert]`

| Frequency | Decision |
| --- | --- |
| 100+ times/day (keyboard shortcuts, command palette toggle) | **No animation. Ever.** Stop here. |
| Tens of times/day (hover effects, list navigation) | Remove, or near-imperceptible only (fast, subtle) |
| Occasional (modals, drawers, toasts) | Standard animation |
| Rare / first-time (onboarding, success, celebration) | The delight budget lives here |

- **Keyboard-initiated actions are a disqualifier, not a judgment call.** They repeat hundreds
  of times a day; animation makes them feel slow and disconnected. Raycast has no open/close
  animation — correct for something opened hundreds of times a day.
- Failing the gate is a result, not a dodge: say so, and offer the non-motion alternative
  (instant state change, a static affordance).
- `[platform]` HIG agrees: avoid adding motion to frequent UI interactions; standard elements
  already carry subtle system animation. Let people cancel motion — never make them wait.

## 2. What is the purpose? `[expert]`

Name it in one word before continuing:

- **Feedback** — confirming the interface heard the user (press scale, hold-to-confirm fill)
- **Spatial consistency** — where something came from or went (toast enters and exits the same
  edge, which is what makes swipe-to-dismiss obvious)
- **State indication** — making a state change legible (a morphing button)
- **Preventing a jarring change** — bridging content that would otherwise teleport
- **Explanation** — showing how something works (marketing / onboarding only)
- **Delight** — allowed *only* at the rare / first-time tier

Can't name it → don't build it. "It looks cool" on a frequently seen element is a reason to stop.
**Function check:** data the user reads or acts on doesn't move for style — a decorative
mouse-tracking effect belongs on a marketing page, not on a graph in a banking app.

## 3. Pick the tool — cheapest that works

**Web** `[expert]` — walk down, stop at the first that fits:

| Need | Tool |
| --- | --- |
| Hover, press, color, a toggle driven by a class/attribute | CSS transition |
| Entry on mount, no JS state | CSS `@starting-style` |
| Predetermined motion that must stay smooth while the page is busy | CSS animation (off main thread) |
| Programmatic control with CSS performance, no library | WAAPI `element.animate()` |
| Springs, layout animations, exit animations, gesture-driven values | Motion (`motion.dev`) |

CSS animations beat JS under load: rAF-driven animation drops frames while the browser loads,
scripts, or paints. CSS for predetermined motion, JS for dynamic and interruptible motion. Don't
install a motion library for a fade.

**iOS / SwiftUI** `[platform]` — the same "cheapest first" order, native edition:

| Need | Tool |
| --- | --- |
| Sheets, navigation push/pop, menus, popovers, alerts, context menus, swipe actions | **The system component.** Its motion, gestures, and Reduce Motion behaviour are already right — don't re-animate or replace it. |
| A state change on screen | `.animation(_:value:)` or `withAnimation` (both retarget mid-flight) |
| Insert / remove | `.transition(...)` inside a conditional, animated by the state change |
| Same element, new place or size | `matchedGeometryEffect`; list → detail: `.navigationTransition(.zoom(sourceID:in:))` + `.matchedTransitionSource` (iOS 18) |
| Text / number / symbol change | `.contentTransition(.numericText(value:))`, `.contentTransition(.opacity)`, `.symbolEffect` |
| Drag, swipe, flick, anything the finger drives | Gesture + spring (see `fluid-interfaces.md`) |
| Scroll-position effects | `.scrollTransition` / `.visualEffect` (renderer-side, no body re-evaluation) |
| Predetermined multi-step motion | `PhaseAnimator` / `KeyframeAnimator` — restart from the start, so decorative only |

**Android / Compose** — `animate*AsState` and `updateTransition` for state changes,
`AnimatedVisibility` for enter/exit, `Animatable.animateTo(initialVelocity =)` for gestures.
Values below are given for Compose where a direct equivalent exists; Compose snippets are not
compiler-checked by Ship.

If the task needs a *component* (toast, drawer, command menu, dropdown) rather than an
animation, use the platform's component or the project's component library first —
hand-rolled dropdowns lose focus management.

## 4. Pick the properties

- **Web: `transform` and `opacity` only** `[expert]`. They skip layout and paint.
  `width`/`height`/`margin`/`padding`/`top`/`left` trigger all three. `clip-path` is the
  sanctioned fourth; `height` is tolerated only for accordions.
- **Never `scale(0)`** `[expert]`. Start from 0.9–0.97 plus opacity 0 — nothing in the real
  world appears from nothing. SwiftUI: `.scale(scale: 0.95).combined(with: .opacity)`, never
  `.scale` alone (its default scale is 0).
- **Origin at the trigger** for popovers, dropdowns, menus, tooltips — CSS
  `transform-origin: var(--transform-origin)` (Base UI); SwiftUI
  `.scale(scale:anchor:)` / `.scaleEffect(_:anchor:)` with the anchor on the trigger side.
  **Modals are exempt** — not anchored to a trigger, they stay centered.
- **Percentages in `translate()`** are relative to the element's own size —
  `translateY(100%)` moves by its own height whatever the content. SwiftUI's
  `.move(edge:)` does the same.
- **Motion (JS): full transform string** — `x`/`y`/`scale` shorthands aren't
  hardware-accelerated and drop frames under load (see `performance.md`).
- **Never drive a child's transform from a CSS variable on the parent** — every child restyles.
- **SwiftUI:** prefer render-time modifiers (`opacity`, `scaleEffect`, `offset`,
  `rotationEffect`) for per-frame motion; frame/layout changes animate too but re-run layout.

## 5. Easing `[expert]`

| Situation | Easing | Web | SwiftUI |
| --- | --- | --- | --- |
| Entering **or exiting** | ease-out | `var(--ease-out)` | `.timingCurve(0.23, 1, 0.32, 1, duration:)` or a critically damped spring |
| Moving / morphing on screen | ease-in-out | `var(--ease-in-out)` | `.timingCurve(0.77, 0, 0.175, 1, duration:)` or spring |
| Hover / color change | ease | `ease` | `.timingCurve(0.25, 0.1, 0.25, 1, duration:)` |
| Constant motion (marquee, progress, hold fill) | linear | `linear` | `.linear(duration:)` |
| Default | ease-out | `var(--ease-out)` | — |

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);     /* strong ease-out for UI */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1); /* strong ease-in-out for on-screen movement */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);  /* iOS-like drawer curve (Ionic) */
```

- **Never ease-in on UI — exits included.** It starts slow, delaying the exact moment the user
  watches. Ease-out at 200ms *feels* faster than ease-in at 200ms. (Ship previously taught
  ease-in for exits; that rule is retired.)
- **Built-in easings are too weak** for deliberate motion; use the three curves above. Need
  another? Take it from easing.dev or easings.co — don't hand-roll one, and never approximate
  a curve from memory (no `cubic-bezier(0.4, 0, 0.2, 1)` because it looks familiar).
- **Extend the codebase's tokens, don't fork them.** An existing `--ease-out` or duration scale
  wins; a parallel system is a defect.
- **iOS:** springs are the native idiom for UI that moves; timing curves suit fades, color, and
  progress. `[platform]` System layout animations carry built-in easing you can't change —
  leave them alone.
- **Compose:** `tween(durationMillis, easing = CubicBezierEasing(0.23f, 1f, 0.32f, 1f))`.

## 6. Duration `[expert]`

| Element | Duration |
| --- | --- |
| Button press feedback | 100–160ms |
| Tooltips, small popovers | 125–200ms |
| Dropdowns, selects | 150–250ms |
| Modals, drawers | 200–500ms |
| Marketing / explanatory | Can be longer |

**UI animations stay under 300ms.** A 180ms dropdown feels more responsive than a 400ms one.
If it feels slow, shorten it before touching the curve. Exits are never slower than entrances.

**Perceived performance:** a faster spinner makes the same load feel faster; instant tooltips
after the first one (skip delay *and* animation) make a whole toolbar feel faster.

## 7. Springs

**When** `[expert]`: drag with momentum; elements that should feel alive (Dynamic Island);
gestures the user can interrupt or reverse; decorative mouse-tracking. Springs keep velocity
when interrupted — CSS keyframes restart from zero.

**Two parameterisations, same spring** `[platform]` — SwiftUI's
`Spring(duration:bounce:)` and `Spring(response:dampingRatio:)` describe one spring:
`duration == response`, `bounce == 1 − dampingRatio` (for bounce ≥ 0). Measured with the iOS
27 SDK:

| Character | duration / bounce | response / dampingFraction | ≈ stiffness / damping (mass 1) |
| --- | --- | --- | --- |
| Default UI (no overshoot) | `0.35` / `0` | `0.35` / `1.0` | 322 / 35.9 |
| Quick settle | `0.3` / `0` | `0.3` / `1.0` | 439 / 41.9 |
| Large surface | `0.5` / `0` | `0.5` / `1.0` | 158 / 25.1 |
| Momentum (after a flick) | `0.4` / `0.2` | `0.4` / `0.8` | 247 / 25.1 |

Compose uses the stiffness form with unit mass:
`spring(dampingRatio = 1f, stiffness = 322f)`; its default spring is already
`DampingRatioNoBouncy`.

**Overshoot rule** `[expert]` (the motion authority and Apple's *Designing Fluid Interfaces*):
- Default to **critically damped** (bounce 0 / damping 1.0) — graceful, non-distracting.
- Add bounce (≈0.2 / damping ≈0.8) **only when the gesture carried momentum** — a flick, a
  throw, a drag release — or at the rare delight tier. Overshoot on a card you flicked feels
  right; on a menu that just appeared, or a button you tapped, it feels wrong.
- When bounce is used, keep it 0.1–0.3.

**SDK presets** `[platform]` — know what they do before using them on a tap:

| SwiftUI | Actual spring | On a plain tap / menu |
| --- | --- | --- |
| `.spring`, `.smooth`, `.spring(duration: d)` | bounce 0 | ✓ |
| `.snappy` | bounce 0.15 | overshoots — use `.snappy(extraBounce: -0.15)` or bounce 0 |
| `.bouncy` | bounce 0.3 | momentum / delight only |
| `.spring(response:dampingFraction:)` with defaults | dampingFraction **0.825** | overshoots — pass `dampingFraction: 1` |
| `.interactiveSpring` | duration 0.15, bounce 0.15, blend 0.25 | for tracking a finger, not for taps |

**Web (Motion):** `{ type: "spring", duration: 0.5, bounce: 0.2 }` (Apple-style, easier to
reason about) or `{ type: "spring", mass: 1, stiffness: 100, damping: 10 }` (physics form).
That physics example is dampingRatio 0.5 — very bouncy; reserve it for the decorative
mouse-tracking it was written for. `useSpring` interpolates a mouse-driven value so it has
momentum instead of snapping — only when the motion is decorative.

```swift
import SwiftUI

/// Ship's spring vocabulary in both SwiftUI forms. Project tokens in design-model.yaml win.
enum MotionSprings {
    // Critically damped — taps, menus, state changes. No overshoot.
    static let standard = Animation.spring(duration: 0.35, bounce: 0)
    static let standardPhysics = Animation.spring(response: 0.35, dampingFraction: 1.0)
    // Only after a flick / throw / drag release.
    static let momentum = Animation.spring(duration: 0.4, bounce: 0.2)
    static let momentumPhysics = Animation.spring(response: 0.4, dampingFraction: 0.8)
    // Snappy without the preset's 0.15 overshoot.
    static let snappyNoBounce = Animation.snappy(duration: 0.3, extraBounce: -0.15)
}
```

## 8. Interruption and exit `[expert]`

- **Transitions, not keyframes, for anything triggered rapidly** — toasts, toggles, anything a
  user can fire twice in a second. Transitions retarget from the current value; keyframes
  restart from zero. SwiftUI: state-driven animations (`withAnimation`, `.animation(_:value:)`)
  retarget and springs carry velocity; `KeyframeAnimator` / `PhaseAnimator` restart — keep
  them for predetermined, decorative motion.
- **Springs for gestures** — they carry velocity through an interruption.
- **Exit the way it entered.** A toast that slides in from the bottom leaves through the
  bottom. SwiftUI's `.move(edge:)` removal already mirrors its insertion.
- **Asymmetric timing where the user is deciding** — slow on the deliberate phase (hold to
  confirm: 2s linear), snappy on the system's response (release: 200ms ease-out). Symmetric
  timing on press-and-release or hold interactions is a finding.
- `[platform]` Never lock out input during a transition; let people cancel motion.

## 9. Stagger `[expert]`

30–80ms between items; longer feels slow. Stagger is decorative — never block interaction
while it plays. Only for groups seen occasionally, not a list scrolled past all day.
`[ship]` Cap the cascade around 8 items; past that, enter the rest together.

## 10. Reduced motion and pointer gating — ship with the animation, not after

- **Reduced motion means fewer and gentler, not zero** `[expert]`: keep opacity and color
  changes that aid comprehension, drop movement and position changes. `[platform]` iOS: read
  `accessibilityReduceMotion`; system components adapt on their own. Full rules, per platform:
  `reduced-motion.md`.
- **Hover motion on the web is gated** behind `@media (hover: hover) and (pointer: fine)` —
  touch fires false hovers on tap. SwiftUI `.onHover` / `.hoverEffect` only fire with a pointer.

## 11. Cohesion `[expert]`

Match motion to the component's personality and the product: playful can be bouncier, a
professional dashboard stays crisp and fast. Sonner feels right partly because everything is in
harmony — its motion is slightly slower than typical UI and uses `ease` rather than ease-out to
feel elegant, matching the toast design, the page, even the name. The opacity + height pair in
entering/exiting lists has no formula — adjust until it feels right. When unsure whether
motion feels right, deleting it is often the strongest move.

**Building components people love** (Sonner principles): developer experience first (no
setup); good defaults matter more than options — most users never customize, so the default
easing, timing, and visuals must be excellent; naming creates identity; handle edge cases
invisibly (pause toast timers when the tab is hidden, fill gaps between stacked toasts so
hover holds, capture the pointer during drag); transitions, not keyframes, for dynamic UI;
a documentation site people can touch.

## 12. Ship contracts `[ship]`

- **Motion tokens:** when `design-model.yaml` has `primitives.motion`, use its named springs
  and durations (generated as `Theme.Motion.*` / CSS variables). A new motion goes through
  a motion token (`/shipmate design --tokens`), not an inline value.
- **Named primitives:** tag each animation with its primitive —
  `// motion: <name>` (Swift/JS) or `/* motion: <name> */` (CSS). Raw values without a tag
  are flagged when a design contract exists.
- **Motion budget:** 1–2 distinct motion patterns running at once per screen (a staggered group
  counts as one). Settings, forms, and utility screens need little or none; the magic moment
  can be the most expressive.
- **Direction:** forward navigation enters from the trailing edge, back returns toward the
  leading edge (the system push/pop already does this).

## 13. Never ship

Each is an automatic block in review (`review-standards.md`):

| Never | Instead |
| --- | --- |
| `transition: all` | Name the exact properties |
| `scale(0)` / `.scale` / `scaleEffect(0)` entrance | 0.95 + opacity 0 |
| ease-in (`.easeIn`) on a UI element, including exits | ease-out or the strong custom curve |
| Built-in ease-out on a deliberate animation | `cubic-bezier(0.23, 1, 0.32, 1)` |
| Animation on a keyboard shortcut or 100+/day action | No animation |
| UI duration over 300ms with no reason | 150–250ms |
| Overshooting spring on a plain tap, toggle, or menu | bounce 0 / dampingFraction 1.0 |
| `transform-origin: center` on a trigger-anchored popover | trigger origin (modals exempt) |
| Keyframes on toasts, toggles, rapidly triggered elements | Transitions / state-driven animation |
| Animating `width`/`height`/`margin`/`padding`/`top`/`left` | `transform` / `opacity` |
| Motion `x`/`y`/`scale` props under load | Full `transform` string |
| Ungated `:hover` motion | `@media (hover: hover) and (pointer: fine)` |
| Missing reduced-motion path on movement | Gentler variant (crossfade), not zero |
| Everything entering at once | 30–80ms stagger |
| Hand-rolled sheet / navigation / menu transition on iOS | The system component |

## 14. After writing it

Write the code, then at most a few lines: **the gate** (frequency tier + named purpose; what
was rejected and why), **the ingredients** (tool, properties, curve, duration or spring — one
line each), **what to feel-check** when feel can't be judged from code (a crossfade, a spring's
bounce, the opacity/height balance). Feel checks: play it at 2–5× duration (web: DevTools
Animations panel; iOS Simulator: Debug › Slow Animations), step frame by frame, test gestures on
a real device, and look again the next day with fresh eyes. The code is the deliverable — no
report.

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

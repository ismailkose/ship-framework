<!-- ship-reference
id: motion-review-standards
kind: mixed
sources: emil-skills@d16ebe6 (skills/review-animations/SKILL.md; skills/review-animations/STANDARDS.md; skills/emil-design-eng/SKILL.md "Review Format", "Review Checklist"); https://developer.apple.com/design/human-interface-guidelines/accessibility (2026-09-23); iPhoneSimulator27.0.sdk SwiftUICore .swiftinterface (2026-09-23); impeccable@9d715cc (idea only: row 24, content hidden until a script runs; pbakaus/impeccable, Apache-2.0)
reviewed: 2026-09-28
-->

# Motion review standards — for Pol, Crit, Eye

The motion authority's review bar (license notice at the end),
written so any reviewer model can apply it mechanically. **Default to flagging; approval is
earned.** A transition that runs but feels sluggish, lands from the wrong origin, fires too
often, or drops frames is a regression, not a pass. Precise values: `animation.md`; SwiftUI
equivalents: `recipes-swiftui.md`.

**Before flagging, check the project's contract.** A value that matches a token in
`design-model.yaml` (`primitives.motion`), a `DECISIONS.md` entry, or a taste entry is a product
decision — don't flag it as wrong; put the tension in `notes`. Platform and accessibility rules
(Reduce Motion, flashing) still apply to product tokens.

## The ten standards

1. **Justified motion** — answers "why does this animate?": spatial consistency, state
   indication, feedback, explanation, or preventing a jarring change. "Looks cool" on a
   frequently seen element blocks.
2. **Frequency-appropriate** — keyboard-initiated and 100+/day actions get **no** animation;
   tens/day get reduced; occasional gets standard; rare/first-time can delight.
3. **Responsive easing** — entering *and exiting* use ease-out or a strong custom curve.
   ease-in on UI blocks. Built-in easings are too weak for deliberate motion.
4. **Sub-300ms UI** — slower needs a reason (modals/drawers up to 500ms; marketing longer).
5. **Origin and physicality** — popovers, dropdowns, tooltips scale from their trigger; never
   from `scale(0)` — start 0.9–0.97 + opacity. Modals are exempt (centered).
6. **Interruptibility** — rapidly triggered or gesture-driven motion retargets from the current
   state (transitions, state-driven SwiftUI animation, springs), not restarting keyframes.
7. **GPU-only properties** (web) — `transform` and `opacity`; layout properties or Motion
   `x`/`y`/`scale` under load are performance findings.
8. **Accessibility** — reduced motion honored, gentler not zero; web hover motion gated behind
   `@media (hover: hover) and (pointer: fine)`.
9. **Asymmetric enter/exit** — deliberate phases (press, hold, destructive confirm) slower;
   system responses snap. Symmetric timing on press-and-release or hold is a finding.
10. **Cohesion** — motion matches the component's personality and the product; a jarring
    crossfade where a subtle blur would bridge the states is a finding. When unsure, deleting
    the motion is often the strongest move.

## Detection table — see this, flag this

`sev` uses Ship's severities (`review-protocol.md`). "Block" in the authority's terms = `major` or
`blocker` here.

| # | In the diff | Finding | sev | Fix (exact) |
| --- | --- | --- | --- | --- |
| 1 | `transition: all` | unbounded properties animate off-GPU | major | `transition: transform 200ms var(--ease-out), opacity 200ms var(--ease-out)` |
| 2 | `scale(0)`, `.scaleEffect(0)`, `.transition(.scale)` alone, fade-only entrance with no initial transform on a popover | comes from nowhere | major | `scale(0.95)` + `opacity: 0`; SwiftUI `.scale(scale: 0.95).combined(with: .opacity)` |
| 3 | `ease-in` / `.easeIn` on any UI enter **or exit** | delays the moment the user watches | major | `cubic-bezier(0.23, 1, 0.32, 1)` / `.timingCurve(0.23, 1, 0.32, 1, duration:)` |
| 4 | Bare `ease` / `linear` / `.easeOut` on a deliberate entrance | weak built-in easing | minor | the strong ease-out curve |
| 5 | Animation on a `.keyboardShortcut`, `onKeyPress`, command palette, or other 100+/day action | fires on a high-frequency action | major | delete the animation |
| 6 | UI duration > 0.3s (not a modal, drawer, or marketing surface) | sluggish | minor (major if > 0.5s) | 150–250ms |
| 7 | Press/tap/toggle/menu using `.snappy`, `.bouncy`, `.spring(response:dampingFraction:)` with defaults or dampingFraction < 1, `bounce` > 0 | overshoot on a plain tap | minor (major on a primary control) | `.spring(duration: 0.3, bounce: 0)` or 160ms ease-out |
| 8 | `transform-origin: center` / `anchor: .center` on a trigger-anchored popover | wrong origin | minor | `var(--transform-origin)` / anchor on the trigger side (modals exempt — don't flag) |
| 9 | `@keyframes`, `PhaseAnimator`, `keyframeAnimator` on toasts, toggles, anything added or fired rapidly | restarts from zero | minor | CSS transitions / state-driven `withAnimation` |
| 10 | Animating `width`/`height`/`margin`/`padding`/`top`/`left` (accordion height excepted) | layout every frame | major if an easy transform fix exists | `transform` / `opacity` |
| 11 | Motion `animate={{ x, y, scale }}` on a page that loads or scripts while animating | main-thread, drops frames | minor | `animate={{ transform: "translateX(…)" }}` |
| 12 | `style.setProperty('--x', …)` on a parent to drive a child's transform | style recalc storm | minor | set `element.style.transform` directly |
| 13 | Movement (`translate`, `.offset`, `.move`, `.scale`, slide, parallax) with no `prefers-reduced-motion` / `accessibilityReduceMotion` path | platform accessibility | major | crossfade variant (`reduced-motion.md`) |
| 14 | Reduced-motion path that removes *all* feedback (`0.01ms` kill switch, `.animation(nil)` everywhere, `duration: 0`) | not gentler — zero | minor | keep a ~200ms opacity fade; drop only movement |
| 15 | Ungated `:hover` transform/scale | false hovers on touch | minor | wrap in `@media (hover: hover) and (pointer: fine)` |
| 16 | Same duration for press and release on a hold / confirm | symmetric where it should be asymmetric | minor | press 2s linear, release 200ms ease-out |
| 17 | A group of 3+ items entering at once where the view is seen occasionally | missing stagger | nit | 30–80ms stagger, never blocking input |
| 18 | Custom transition / animation override on a system sheet, navigation push, menu, or alert (iOS) | fights the platform, breaks Reduce Motion | major | remove it; use the system presentation |
| 19 | `allowsHitTesting(false)`, `disabled(true)`, or `pointer-events: none` for the length of an animation | input locked during a transition | major | keep it interactive; retarget on new input |
| 20 | Drag that animates only on release, snaps to center on grab, or dismisses on distance only | not fluid | minor | 1:1 tracking, keep grab offset, velocity/projection dismissal (`fluid-interfaces.md`) |
| 21 | Animated `blur` > 20px, or blur transitions with no reduced-motion fallback | expensive / vestibular | minor | ≤ 2–4px; opacity under Reduce Motion |
| 22 | `DispatchQueue.main.asyncAfter` / `setTimeout` chaining animation steps | brittle, not interruptible | minor | `withAnimation(_:completion:)`, `PhaseAnimator`, `transitionend` |
| 23 | Looping or auto-moving content > 5s with no pause control; flashing > 3/s | WCAG 2.2.2 / 2.3.1 | blocker (flashing) / major | pause control; remove flashing |
| 24 | Content that starts hidden (`opacity: 0`, fully clipped) until a script reveals it | if the script is slow, blocked or fails, the content never appears | major | visible by default; hide only under a class the revealing script sets (`recipes-web.md` › Scroll reveal) |

When a value is needed, copy it from `animation.md` — never approximate.

## Remedial preference — prefer earlier moves

1. **Delete** the animation (high-frequency, no purpose, keyboard-triggered).
2. **Reduce** — shorter duration, smaller transform, fewer properties.
3. **Fix the easing** — ease-in → ease-out / strong curve.
4. **Fix origin / physicality** — correct anchor; 0.95 + opacity instead of 0.
5. **Make it interruptible** — keyframes → transitions / state-driven; springs for gestures.
6. **Move it to the GPU** — layout props → transform/opacity; shorthand → full transform; WAAPI.
7. **Asymmetric timing** — slow the deliberate phase, snap the response.
8. **Polish** — blur to mask crossfades, stagger for groups, `@starting-style` for entry,
   springs for "alive" elements.
9. **Accessibility and cohesion** — reduced-motion + hover gating; tune to the personality.

## Reporting

**Inside `/shipmate review`** — use the JSON finding shape from `review-protocol.md`, one finding
per root cause (the same issue in several places → one finding, every place in
`evidence.locations`), mapped from the authority's table: `claim` = the *Before* (what's wrong, with the code),
`suggested_fix` = the *After* (exact value), `why_it_matters` = the *Why*. Set the `motion`
dimension to `concerns` if any finding is `major`/`blocker` (the authority's **Block**); `pass` when there
is no feel-breaking regression, no motion that should be deleted, durations and easing in
bounds, interruptibility handled, and reduced motion respected (the authority's **Approve**). If feel
can't be judged from code (a crossfade, a spring's bounce), say so in `confidence_reason` and
recommend slow-motion / frame-by-frame review or a next-day look — don't guess a value.

**Standalone** ("review these animations" outside `/shipmate review`) — one markdown table, one row
per issue, never a "Before:/After:" list:

| Before | After | Why |
| --- | --- | --- |
| `transition: all 300ms` | `transition: transform 200ms var(--ease-out)` | Name exact properties; `all` animates unintended properties off-GPU |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | Nothing appears from nothing |
| `ease-in` on dropdown | `cubic-bezier(0.23, 1, 0.32, 1)` | ease-in delays the moment the user watches most |
| `.snappy` on a button tap | `.spring(duration: 0.3, bounce: 0)` | `.snappy` has 0.15 bounce — overshoot on a plain tap |
| `transform-origin: center` on popover | `var(--transform-origin)` | Popovers scale from their trigger (modals exempt) |

Then the verdict, grouped by impact tier (omit empty tiers): 1. feel-breaking regressions
(sluggish easing, comes-from-nowhere, fires on high-frequency/keyboard actions); 2. missed
simplifications (should be removed or reduced); 3. performance; 4. interruptibility and timing;
5. origin, physicality, cohesion; 6. accessibility. Close with **Block** (any feel-breaking
regression, animation on a keyboard/high-frequency action, `scale(0)` or ease-in on UI, a
non-GPU animation with an easy GPU fix, missing reduced motion on movement) or **Approve**.
Cite `file:line` for every row.

## Eye (rendered checks)

Eye judges what code can't: record the interaction (simulator or browser) and check it in slow
motion. Look for: the panel growing from its trigger; nothing popping from a point; exits not
slower than entries; no overshoot on taps; two states double-exposing in a crossfade; motion
continuing smoothly when interrupted (tap again mid-animation); with Reduce Motion on, movement
gone but fades present. Evidence is the recording or screenshot sequence.

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

<!-- ship-reference
id: motion-reduced-motion
kind: mixed
sources: emil-skills@d16ebe6 (skills/emil-design-eng/SKILL.md "Accessibility"; skills/apple-design/SKILL.md §14; skills/review-animations/STANDARDS.md "Accessibility"); https://developer.apple.com/design/human-interface-guidelines/accessibility (2026-09-23); https://www.w3.org/TR/WCAG22/ (2026-09-23); https://motion.dev/docs/react-motion-config (2026-09-23); iPhoneSimulator27.0.sdk SwiftUICore .swiftinterface (2026-09-23)
reviewed: 2026-09-23
-->

# Reduced motion, transparency, contrast

Reduced motion ships *with* the animation, never as a follow-up. The motion
authority's rules, reconciled with the platform requirements they sit under.

## The rule

**Reduced motion means fewer and gentler animations, not zero.** `[expert]` Keep opacity and
color transitions that aid comprehension; remove movement and position changes. A reduced-motion
path that nukes all feedback is a finding, and so is a global `0.01ms` kill switch.

**Why that satisfies the platform** `[platform]`:
- **Apple HIG (Reduce Motion on):** reduce automatic and repetitive animation — zooming,
  scaling, peripheral motion. Its recommended techniques: tighten springs to reduce bounce;
  track animations directly with people's gestures; avoid animating depth changes on the z-axis;
  replace x/y/z transitions with fades; avoid animating into and out of blurs.
- **WCAG 2.2:** 2.3.3 Animation from Interactions (AAA) — non-essential motion triggered by
  interaction can be disabled; a crossfade isn't motion animation, so swapping movement for a
  fade meets it. 2.2.2 Pause, Stop, Hide (A) — anything that moves, blinks, or auto-updates for
  more than 5 seconds alongside other content needs a pause control. 2.3.1 Three Flashes (A) —
  nothing flashes more than three times per second.
- **App Store:** a product that claims Reduced Motion support in its App Store accessibility
  label has to honor it on every screen.

Precedence: these requirements beat product tokens and the authority's defaults. A founder can choose how
the reduced path looks; not whether it exists.

## What changes

| Keep (short, ~150–200ms) | Replace with a crossfade or remove |
| --- | --- |
| Opacity fades, color / tint changes | Slides, pushes, `translate` / `.offset` / `.move(edge:)` |
| Progress bars and fills (functional) | Scale-in / zoom (`scale`, `.scaleEffect`, `.scale` transitions) |
| Gesture-driven tracking (the finger moves it) | Overshoot / bounce (tighten to bounce 0) |
| Content changes that explain state (`numericText`, symbol replace) | Parallax, full-viewport moving backgrounds, auto-playing loops |
| Haptics and sound (non-visual feedback) | Blur-in/out transitions (`blurReplace`, animated `filter: blur`) |
| | Depth / z-axis animation, 3D flips |

Also avoid for everyone (Apple): slow sustained oscillation near 0.2 Hz (one cycle per 5s),
abrupt brightness jumps (ease dark ↔ light changes), large objects moving opaquely — make them
semi-transparent while they travel, or fade out, move, fade back in once settled.

## Web

```css
@media (prefers-reduced-motion: reduce) {
  .sheet {
    transition: opacity 200ms ease; /* keep the fade */
    transform: none;                /* drop the movement */
  }
}
@media (prefers-reduced-transparency: reduce) {
  .toolbar { background: white; backdrop-filter: none; }
}
@media (prefers-contrast: more) {
  .toolbar { background: white; border: 1px solid black; }
}
```

In JS, branch the movement, not the fade:

```jsx
const reduce = useReducedMotion();
const closedX = reduce ? 0 : '-100%';
```

App-wide with Motion: `<MotionConfig reducedMotion="user">` — with the OS setting on, Motion
disables transform and layout animations and keeps opacity and color. That is exactly the
gentler path. `"always"` applies the same policy regardless of the setting (useful for testing
the reduced path); `"never"` ignores it. The policy only covers Motion's transform/layout
animations — CSS transitions, other libraries and custom JS still need their own branch.

With a token system, set distance tokens to `0px` under the media query and leave opacity
durations short but non-zero — the fades carry continuity.

## iOS / SwiftUI

- `@Environment(\.accessibilityReduceMotion)` — read it in every view that moves something.
- **Don't override the system.** Sheets, navigation push/pop, zoom transitions, menus, and
  alerts adapt to Reduce Motion themselves (for example, iOS swaps slides for crossfades when
  *Prefer Cross-Fade Transitions* is on). Custom transitions on them defeat that.
- `accessibilityPrefersCrossFadeTransitions` (SwiftUI environment, iOS 26.4+;
  `UIAccessibility.prefersCrossFadeTransitions` since iOS 14) — when true, custom screen-level
  transitions should crossfade too.
- `accessibilityReduceTransparency` — make materials and glass frostier or solid; raise
  opacity, drop blur.
- Gesture tracking stays 1:1 (Apple lists it as a *good* reduced-motion technique); only the
  settle loses its bounce.

A small vocabulary keeps the branch in one place:

```swift
import SwiftUI

extension AnyTransition {
    /// Movement when allowed; a crossfade under Reduce Motion.
    static func motion(_ movement: AnyTransition, reduceMotion: Bool) -> AnyTransition {
        reduceMotion ? .opacity : movement
    }
}

extension Animation {
    /// The requested animation, or a short ease-out fade under Reduce Motion.
    static func motion(_ animation: Animation, reduceMotion: Bool) -> Animation {
        reduceMotion ? .easeOut(duration: 0.2) : animation
    }
}

struct SlideInBanner: View {
    let isVisible: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        VStack {
            if isVisible {
                Text("Back online")
                    .padding()
                    .transition(.motion(.move(edge: .top).combined(with: .opacity), reduceMotion: reduceMotion))
            }
            Spacer()
        }
        .animation(.motion(.spring(duration: 0.35, bounce: 0), reduceMotion: reduceMotion), value: isVisible)
    }
}
```

Screen-level custom transitions also honor the cross-fade preference where available:

```swift
import SwiftUI

@available(iOS 26.4, *)
struct OnboardingPager: View {
    @State private var page = 0
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.accessibilityPrefersCrossFadeTransitions) private var prefersCrossFade

    var body: some View {
        ZStack {
            Text("Step \(page + 1)")
                .id(page)
                .transition(reduceMotion || prefersCrossFade ? .opacity : .push(from: .trailing))
        }
        .onTapGesture { page += 1 }
        .animation(.spring(duration: 0.35, bounce: 0), value: page)
    }
}
```

## Android

Android has no separate "reduce motion" flag: *Settings › Accessibility › Remove animations*
sets the system animator duration scale to 0 (`Settings.Global.ANIMATOR_DURATION_SCALE`;
`ValueAnimator.areAnimatorsEnabled()` reports it). That is "none", not "gentler" — so when it's
off, keep essential state changes legible without motion (instant, with color/opacity end
states). Gap: Ship hasn't verified how Compose animation specs respond to a 0 scale in the
current Compose release — check before relying on it, and prefer `AnimatedVisibility` with
`fadeIn`/`fadeOut` for anything that must stay legible.

## Focus and assistive tech

- Motion is never the only signal: announce toasts and status changes
  (`AccessibilityNotification.Announcement`, `aria-live`), and pair haptics with visual state.
- Move focus into a dialog when it opens — don't wait for the entrance animation to finish
  (keyboard and VoiceOver users shouldn't wait on decoration). `[ship]`
- Give gesture-only interactions an accessible action (`accessibilityAction`, a visible
  button).

## Testing

| Where | How |
| --- | --- |
| iOS device / Simulator | Settings › Accessibility › Motion › Reduce Motion (and Prefer Cross-Fade Transitions) |
| Xcode | Debug bar › Environment Overrides › Accessibility |
| macOS | System Settings › Accessibility › Display › Reduce motion |
| Windows | Settings › Accessibility › Visual effects › Animation effects (off) |
| Android | Settings › Accessibility › Remove animations |
| Chrome | DevTools › Rendering › Emulate `prefers-reduced-motion: reduce` (also `prefers-reduced-transparency`, `prefers-contrast`) |

Verify: movement is gone but fades and color feedback remain; state changes still read without
motion; progress and loading states still show; nothing jumps in layout where an animation was
removed; loops can be paused; no flashing above 3/s.

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

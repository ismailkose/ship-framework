<!-- ship-reference
id: motion-recipes-swiftui
kind: mixed
sources: emil-skills@d16ebe6 (skills/animate/RECIPES.md; skills/emil-design-eng/SKILL.md); iPhoneSimulator27.0.sdk SwiftUI/SwiftUICore .swiftinterface (2026-09-23); https://developer.apple.com/design/human-interface-guidelines/accessibility (2026-09-23)
reviewed: 2026-09-23
-->

# Motion recipes — SwiftUI

The motion authority's web recipes (license notice at the end), translated to
SwiftUI. Translation rule: keep the *intent and numbers*, use the native mechanism — system
components first, state-driven animation (which retargets mid-flight), springs for anything the
finger drives, and `accessibilityReduceMotion` on every movement. Every block here type-checks
against the iOS 27 SDK with an iOS 18 deployment target (`scripts/checks/motion.sh` in the Ship repo).

Curves used below (from `animation.md`): ease-out `(0.23, 1, 0.32, 1)`, ease-in-out
`(0.77, 0, 0.175, 1)`, drawer `(0.32, 0.72, 0, 1)`. Project tokens (`Theme.Motion.*`) replace
these values when `design-model.yaml` defines them, or, with no registry, the project's own
hand-written theme does.

## System first — what not to rebuild

| Web recipe | iOS: use this, don't hand-roll |
| --- | --- |
| Dropdown / select / menu | `Menu`, `Picker(.menu)`, `.contextMenu` — they grow from their source |
| Popover | `.popover(isPresented:)` (sheet on compact width, anchored bubble on iPad) |
| Modal | `.sheet`, `.fullScreenCover`, `.alert`, `.confirmationDialog` |
| Drawer / sheet | `.sheet` + `.presentationDetents([.medium, .large])` — interactive dismiss and velocity are native |
| List → detail expansion | `.navigationTransition(.zoom(sourceID:in:))` + `.matchedTransitionSource(id:in:)` (iOS 18) |
| Accordion | `DisclosureGroup` |
| Tooltip | `.help("…")` (pointer hover on iPad/Mac); no touch tooltip pattern on iPhone |

System components already follow Reduce Motion, keep the platform's timing, and stay
interruptible; re-animating them fights the platform (a review finding). Build custom motion
only where no system component fits.

## Button press

Instant feedback on touch-*down* (`isPressed` flips on touch-down, not on release). 0.97,
160ms ease-out, no overshoot. `scaleEffect` scales the label and icon too — that's what makes
it read as a physical press. Under Reduce Motion the scale becomes a brief dim.

```swift
import SwiftUI

struct PressableButtonStyle: ButtonStyle {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed && !reduceMotion ? 0.97 : 1)
            .opacity(configuration.isPressed && reduceMotion ? 0.7 : 1)
            // motion: press
            .animation(.timingCurve(0.23, 1, 0.32, 1, duration: 0.16), value: configuration.isPressed)
    }
}
```

A spring works too — `.spring(duration: 0.16, bounce: 0)` — but never SwiftUI's `.snappy` or
`.bouncy` presets here: both overshoot on a plain tap.

## Custom anchored panel (when `Menu`/`.popover` can't do it)

Scales out of its trigger, from 0.95 with opacity, 200ms ease-out. The anchor is the whole
point — the panel should look like it came out of the thing tapped.

```swift
import SwiftUI

struct FilterPanel: View {
    @State private var isOpen = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private var panelTransition: AnyTransition {
        reduceMotion
            ? .opacity
            : .scale(scale: 0.95, anchor: .topLeading).combined(with: .opacity)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button("Filter") { isOpen.toggle() }
            if isOpen {
                Text("Panel content")
                    .padding()
                    .background(.regularMaterial, in: .rect(cornerRadius: 12))
                    .transition(panelTransition)
            }
        }
        // motion: popover — ease-out both ways; exit mirrors entry
        .animation(.timingCurve(0.23, 1, 0.32, 1, duration: 0.2), value: isOpen)
    }
}
```

## Custom modal overlay

The one panel that stays centered (not anchored to a trigger). 0.96 + opacity, 250ms ease-out;
the scrim fades with it so they read as one surface. Prefer `.sheet` / `.fullScreenCover`.

```swift
import SwiftUI

struct CenteredDialog<Content: View>: View {
    @Binding var isPresented: Bool
    @ViewBuilder var content: Content
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack {
            if isPresented {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()
                    .onTapGesture { isPresented = false }
                    .transition(.opacity)
                content
                    .padding(24)
                    .background(.background, in: .rect(cornerRadius: 20))
                    .transition(reduceMotion ? .opacity : .scale(scale: 0.96).combined(with: .opacity))
            }
        }
        // motion: modal
        .animation(.timingCurve(0.23, 1, 0.32, 1, duration: 0.25), value: isPresented)
    }
}
```

## Custom drawer

Use `.sheet` with detents unless the design needs a non-system surface. A custom drawer rides
the drawer curve at 500ms when opened by a tap; when released from a drag it settles with a
spring (drag-to-dismiss and snap points: `fluid-interfaces.md`). `.move(edge: .bottom)` moves by the
drawer's own height, like `translateY(100%)`.

```swift
import SwiftUI

struct BottomDrawer<Content: View>: View {
    @Binding var isOpen: Bool
    @ViewBuilder var content: Content
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack(alignment: .bottom) {
            if isOpen {
                content
                    .frame(maxWidth: .infinity)
                    .padding(.bottom, 24)
                    .background(.background, in: .rect(topLeadingRadius: 24, topTrailingRadius: 24))
                    .transition(reduceMotion ? .opacity : .move(edge: .bottom))
            }
        }
        // motion: drawer
        .animation(reduceMotion ? .easeOut(duration: 0.2) : .timingCurve(0.32, 0.72, 0, 1, duration: 0.5),
                   value: isOpen)
    }
}
```

## Toast

Enters and leaves through the same edge (spatial consistency makes swipe-to-dismiss obvious).
The authority's toast tuning (`ease`, 400ms, slightly slower than generic UI — is a personality
choice for toasts; a crisper product can use the 250ms ease-out instead. Toasts are added
rapidly, so the animation must be state-driven (retargets), never a restarting keyframe.
Pause the auto-dismiss timer while the app is inactive (`scenePhase`).

```swift
import SwiftUI

struct ToastHost: View {
    @State private var message: String?
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack(alignment: .bottom) {
            Button("Save") { message = "Saved" }
            if let message {
                Text(message)
                    .padding(.horizontal, 16).padding(.vertical, 10)
                    .background(.thinMaterial, in: .capsule)
                    .padding(.bottom, 16)
                    .transition(reduceMotion ? .opacity : .move(edge: .bottom).combined(with: .opacity))
                    .accessibilityAddTraits(.isStaticText)
            }
        }
        // motion: toast — CSS `ease` (0.25, 0.1, 0.25, 1), 400ms
        .animation(.timingCurve(0.25, 0.1, 0.25, 1, duration: 0.4), value: message)
    }
}
```

Announce it for VoiceOver (`AccessibilityNotification.Announcement`) — motion is never the only signal.

## Accordion

`DisclosureGroup` first. Custom: SwiftUI animates the height change itself; keep it short —
this is layout work on every frame. Content fades in with the same curve.

```swift
import SwiftUI

struct ExpandableRow: View {
    let title: String
    let detail: String
    @State private var isExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button {
                isExpanded.toggle()
            } label: {
                HStack {
                    Text(title)
                    Spacer()
                    Image(systemName: "chevron.down")
                        .rotationEffect(.degrees(isExpanded ? 180 : 0))
                }
            }
            if isExpanded {
                Text(detail).transition(.opacity)
            }
        }
        .clipped()
        // motion: accordion — 200ms ease-out; opacity-only content, so no reduced variant needed
        .animation(.timingCurve(0.23, 1, 0.32, 1, duration: 0.2), value: isExpanded)
    }
}
```

## Stagger a group entrance

For a grid or list seen occasionally — not a list scrolled past all day. 50ms apart (30–80ms),
fade + 8pt rise, 300ms ease-out, capped at 8 items. Decorative: rows stay tappable while it
plays. Reduced motion keeps the fade and drops the rise.

```swift
import SwiftUI

struct StaggeredList: View {
    let items: [String]
    @State private var appeared = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(Array(items.enumerated()), id: \.element) { index, item in
                Text(item)
                    .opacity(appeared ? 1 : 0)
                    .offset(y: appeared || reduceMotion ? 0 : 8)
                    // motion: stagger — 50ms step, cap 8
                    .animation(
                        .timingCurve(0.23, 1, 0.32, 1, duration: 0.3).delay(Double(min(index, 8)) * 0.05),
                        value: appeared)
            }
        }
        .onAppear { appeared = true }
    }
}
```

## Hold to confirm

For destructive actions where a plain tap is too easy to fire. Press is slow and deliberate
(2s **linear** — the fill is a progress indicator, and progress shouldn't ease); release snaps
back in 200ms ease-out. The fill is a mask scaled from the leading edge (the SwiftUI form of
`clip-path: inset(0 100% 0 0)`); the button also takes the 0.97 press. On iOS, a
`confirmationDialog` or a swipe action is the more familiar pattern — use hold-to-confirm when
the product has chosen it.

```swift
import SwiftUI

struct HoldToDeleteButton: View {
    var onConfirm: () -> Void
    @State private var progress: CGFloat = 0
    @State private var isPressing = false
    @State private var confirmations = 0

    var body: some View {
        Text("Hold to delete")
            .padding(.horizontal, 20).padding(.vertical, 12)
            .background(Color.red.opacity(0.15))
            .overlay(alignment: .leading) {
                Color.red.opacity(0.35)
                    .scaleEffect(x: progress, anchor: .leading)
            }
            .clipShape(.capsule)
            .scaleEffect(isPressing ? 0.97 : 1)
            .onLongPressGesture(minimumDuration: 2) {
                confirmations += 1
                onConfirm()
            } onPressingChanged: { pressing in
                isPressing = pressing
                // motion: hold — 2s linear press, 200ms ease-out release
                withAnimation(pressing ? .linear(duration: 2) : .timingCurve(0.23, 1, 0.32, 1, duration: 0.2)) {
                    progress = pressing ? 1 : 0
                }
            }
            .sensoryFeedback(.success, trigger: confirmations)
            .accessibilityAddTraits(.isButton)
            .accessibilityAction(named: "Delete") { onConfirm() }
    }
}
```

Give VoiceOver a direct action (above) — a hold gesture alone isn't accessible.

## Tab indicator with a synced color change

Timing a pill's movement and each label's color separately never quite lines up. Draw the
tab row twice — normal and active styling — and mask the active copy with the moving pill, so
text and background change in the same frame. The pill moves on screen, so it's ease-in-out,
250ms. Use a system `Picker(.segmented)` if it fits the design.

```swift
import SwiftUI

struct SegmentedTabs: View {
    let tabs = ["Day", "Week", "Month"]
    @State private var selected = "Day"
    @Namespace private var pill

    private func row(active: Bool) -> some View {
        HStack(spacing: 0) {
            ForEach(tabs, id: \.self) { tab in
                Text(tab)
                    .padding(.horizontal, 16).padding(.vertical, 8)
                    .foregroundStyle(active ? Color.white : Color.primary)
                    .background { if !active { Color.clear.matchedGeometryEffect(id: tab, in: pill) } }
                    .contentShape(.rect)
                    .onTapGesture { selected = tab }
            }
        }
    }

    var body: some View {
        row(active: false)
            .overlay {
                row(active: true)
                    .background(Color.accentColor)
                    .mask {
                        Capsule().matchedGeometryEffect(id: selected, in: pill, isSource: false)
                    }
                    .allowsHitTesting(false)
            }
            // motion: tab-indicator — ease-in-out, 250ms
            .animation(.timingCurve(0.77, 0, 0.175, 1, duration: 0.25), value: selected)
            .accessibilityRepresentation {
                Picker("Range", selection: $selected) {
                    ForEach(tabs, id: \.self) { Text($0) }
                }
                .pickerStyle(.segmented)
            }
    }
}
```


## Scroll reveal

Marketing and onboarding surfaces only — never functional UI visited daily. Reveal once; don't
re-animate on every scroll-by. Clip from the bottom edge (the `inset(0 0 100% 0)` reveal),
600ms ease-in-out.

```swift
import SwiftUI

struct RevealOnce<Content: View>: View {
    @ViewBuilder var content: Content
    @State private var revealed = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        content
            .mask(alignment: .top) {
                Rectangle().scaleEffect(y: revealed || reduceMotion ? 1 : 0.0001, anchor: .top)
            }
            .opacity(revealed || !reduceMotion ? 1 : 0)
            .onScrollVisibilityChange(threshold: 0.2) { visible in
                guard visible, !revealed else { return }
                // motion: scroll-reveal — 600ms ease-in-out, once
                withAnimation(reduceMotion ? .easeOut(duration: 0.2) : .timingCurve(0.77, 0, 0.175, 1, duration: 0.6)) {
                    revealed = true
                }
            }
    }
}
```

For effects tied continuously to scroll position, use `.scrollTransition` — it runs in the
renderer without re-evaluating `body`.

## Masking a crossfade that won't settle

When two states visibly double-expose and no curve or duration fixes it, blur the seam.
`.blurReplace` is the built-in version; custom blur stays small (≈2pt, never near 20).
`[platform]` Under Reduce Motion, avoid animating into and out of blurs — fall back to
opacity.

```swift
import SwiftUI

struct StatusLabel: View {
    let isSaved: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private var swap: AnyTransition {
        reduceMotion ? .opacity : AnyTransition(.blurReplace)
    }

    var body: some View {
        ZStack {
            if isSaved {
                Label("Saved", systemImage: "checkmark").transition(swap)
            } else {
                Label("Save", systemImage: "square.and.arrow.down").transition(swap)
            }
        }
        // motion: state-swap — 200ms ease-out
        .animation(.timingCurve(0.23, 1, 0.32, 1, duration: 0.2), value: isSaved)
    }
}
```

## Numbers and text that change

Tickers, counters, prices: `.contentTransition(.numericText(value:))` with tabular digits so the
layout doesn't jitter. It's state-driven, so rapid updates retarget.

```swift
import SwiftUI

struct Counter: View {
    @State private var count = 0

    var body: some View {
        Button {
            count += 1
        } label: {
            Text(count, format: .number)
                .monospacedDigit()
                .contentTransition(.numericText(value: Double(count)))
        }
        // motion: numeric
        .animation(.spring(duration: 0.3, bounce: 0), value: count)
    }
}
```

## Predetermined sequences (the WAAPI equivalent)

`PhaseAnimator` / `KeyframeAnimator` give scripted multi-step motion without a library. They
restart from the first phase when triggered again — fine for a success flourish at the delight
tier, wrong for anything a user can fire repeatedly.

```swift
import SwiftUI

struct SuccessCheck: View {
    let trigger: Int
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        Image(systemName: "checkmark.circle.fill")
            .font(.largeTitle)
            .phaseAnimator([false, true], trigger: trigger) { view, phase in
                view.scaleEffect(phase && !reduceMotion ? 1.12 : 1)
            } animation: { _ in
                // motion: celebrate — delight tier only (rare / first-time)
                .spring(duration: 0.35, bounce: 0.2)
            }
            .sensoryFeedback(.success, trigger: trigger)
    }
}
```

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

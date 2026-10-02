<!-- ship-reference
id: motion-apple-design
kind: mixed
sources: emil-skills@d16ebe6 (skills/apple-design/SKILL.md §12, §13, §15–17); /Applications/Xcode.app/.../Resources/AdditionalDocumentation/SwiftUI-Implementing-Liquid-Glass-Design.md (Xcode 27.0, 2026-09-23) — pointed to, not copied; iPhoneSimulator27.0.sdk SwiftUI/SwiftUICore .swiftinterface (2026-09-23)
reviewed: 2026-09-23
-->

# Apple design — materials, multimodal feedback, type, foundations

The non-gesture half of the motion authority's Apple-design rules (license notice at the end), which
distils Apple's WWDC design talks. Gestures, springs, and interruption live in
`fluid-interfaces.md`; reduced motion / transparency / contrast in `reduced-motion.md`.
Upstream translates Apple's ideas *to the web*; on iOS use the native API named in each section.
**Authority:** this is an expert reading of Apple's talks (tier 5 in the knowledge skill's
precedence), not Apple's documentation. Resolve a conflict rule by rule with that order —
accessibility and platform requirements (Dynamic Type, text resizing, Reduce Motion) and API
availability first; then product decisions and the founder's taste; then Apple's HIG and API docs,
which outrank anything here; a Ship default (e.g. in the UX typography/layout references) yields to
this file. **Applicability:** the iOS lines are for native apps; the CSS lines are one way to bring
the idea to a website — neither is a requirement on the other platform.

## 12. Materials and depth — translucency conveys hierarchy

Translucent materials are a floating functional layer that brings structure without stealing
focus.
- **Nav bars, toolbars, sheets as translucent layers** with content scrolling underneath, not
  opaque strips. iOS: the system bars and Liquid Glass do this — use them (`.toolbar`,
  `.glassEffect()` on iOS 26+; Xcode 27's `SwiftUI-Implementing-Liquid-Glass-Design.md` is the
  primary source). Web: `backdrop-filter: blur()` + a semi-transparent background.
- **Material weight encodes hierarchy:** heavier/darker materials separate structural regions
  (sidebars); lighter ones draw attention to interactive elements. **Never stack a light
  translucent surface on another** — legibility collapses.
- **Bigger surfaces read as thicker:** stronger blur and a deeper shadow than small chips;
  heavier shadow over busy content, lighter over plain backgrounds.
- **Dim to focus, separate to keep flow.** A modal task gets a dimming scrim and pushes the
  background back; a parallel, non-blocking panel uses translucency and offset *without* a
  scrim. Stacked sheets progressively dim and push back each parent (iOS sheets do this).
- **Vibrancy keeps text legible** over changing backgrounds: higher contrast, slightly heavier
  weight, a small tracking bump — not flat gray. Put color on a solid layer, not the
  translucent foreground. iOS: hierarchical styles (`.secondary`) on materials are vibrant
  automatically.
- **Scroll edge effects, not hard dividers** — fade a small blur/gradient where content meets
  floating chrome, only where it actually overlaps (iOS 26 bars do this natively).
- **Materialize, don't just fade** — glass surfaces animate blur and scale together on enter and
  exit so they read as a material arriving. iOS 26: `glassEffectTransition(.materialize)` and
  `glassEffectID(_:in:)` inside a `GlassEffectContainer` for morphing between glass shapes.

```css
.toolbar {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.4); /* bright edge = light catching the material */
}
```

```swift
import SwiftUI

@available(iOS 26.0, *)
struct EditingTools: View {
    @State private var isExpanded = false
    @Namespace private var glass

    var body: some View {
        GlassEffectContainer(spacing: 16) {
            HStack(spacing: 16) {
                Button { isExpanded.toggle() } label: { Image(systemName: "pencil") }
                    .glassEffect()
                    .glassEffectID("pencil", in: glass)
                if isExpanded {
                    Button {} label: { Image(systemName: "eraser") }
                        .glassEffect()
                        .glassEffectID("eraser", in: glass)
                }
            }
        }
        // motion: glass-morph — critically damped; the system morph handles Reduce Motion/Transparency
        .animation(.spring(duration: 0.35, bounce: 0), value: isExpanded)
    }
}
```

## 13. Multimodal feedback — motion + sound + haptics

From *Designing Audio-Haptic Experiences*:
1. **Causality** — obvious what caused it. Fire on the causal event (the toggle flipping, the
   item snapping home) and match the feedback's character to the action's physicality.
2. **Harmony** — visual, sound, and haptic land on the **same frame**. Don't let an animation
   lag the haptic. SwiftUI: `.sensoryFeedback(_:trigger:)` fires on the same state change that
   drives the animation.
3. **Utility** — only where it earns its place: success, error, commit, snap. Over-feedback
   trains people to ignore all of it.

```swift
import SwiftUI

struct FavoriteToggle: View {
    @State private var isFavorite = false

    var body: some View {
        Button {
            isFavorite.toggle()
        } label: {
            Image(systemName: isFavorite ? "heart.fill" : "heart")
                .contentTransition(.symbolEffect(.replace))
        }
        // One state change drives the symbol swap and the haptic — same frame.
        .sensoryFeedback(.impact(weight: .light), trigger: isFavorite)
        .animation(.spring(duration: 0.3, bounce: 0), value: isFavorite)
    }
}
```

## 15. Typography — optical sizing, tracking, leading

From *The Details of UI Typography* (WWDC 2020):
- **Tracking is size-specific** — large display text wants negative tracking, small text slightly
  positive. One fixed `letter-spacing` is wrong somewhere. iOS: the system font's tracking
  tables apply automatically to text styles; don't add blanket `.tracking`.
- **Leading tracks size inversely** — tight on large headings, looser on body; more for scripts
  with tall ascenders/descenders, tighter for dense UI.
- **Hierarchy from weight + size + leading together**, not size alone; emphasize with weight.
- **Respect the text-size setting** (Dynamic Type) — scale layout with the text (web: `rem`/`em`
  spacing; iOS: text styles and `@ScaledMetric`).
- **System font first** — it ships optical sizing, tracking tables, and legibility tuning.
  Override only with a reason.

```css
:root { font: 100%/1.5 system-ui, sans-serif; }
.display {
  font-size: clamp(2rem, 1.4rem + 3vw, 4rem); /* keep a rem term: follows the user's text size */
  line-height: 1.05;       /* tight leading for large text */
  letter-spacing: -0.02em; /* negative tracking as it grows */
  font-optical-sizing: auto;
}
```

## 16. Design foundations — the eight principles

The motion and craft above serve Apple's eight principles (*Principles of Great Design*,
WWDC 2026):
1. **Purpose** — decide what *not* to build; every feature spends the user's time, attention,
   and trust.
2. **Agency** — keep people in control; easy undo for slips; confirmation only for genuinely
   destructive, irreversible actions (overuse trains click-through).
3. **Responsibility** — act in the user's interest: ask for data at the right moment and only
   what's needed; anticipate misuse and harm (especially with AI); cut features whose risk
   outweighs their value.
4. **Familiarity** — build on what people know; metaphors neither too literal nor too
   abstract; things that look the same behave the same and live in the same place. Break a
   pattern only when it's provably better — then test it.
5. **Flexibility** — design for contexts, devices, and the full range of abilities; let people
   personalize when no single layout fits.
6. **Simplicity, not minimalism** — strip the unnecessary so the core shines; concise, clear
   hierarchy; sometimes *adding* context simplifies; common path first, advanced one level down.
7. **Craft** — every spacing, timing, and alignment value is a deliberate, defensible choice;
   responsive animation that gives immediate, natural feedback; iterate as features and hardware
   change.
8. **Delight** — the result of the other seven, not confetti on top; decide the emotion
   (calm, confident, excited) and reinforce it everywhere.

Tactical rules that serve them: **feedback in four kinds** (status, completion, warning, error —
validate inline, not on submit); **wayfinding** (where am I, where can I go, what's there, how
do I get out — never trap the user); **grouping and mapping** (a control near what it affects,
arranged like what it changes — needing a label is a sign the mapping is weak); **direct,
specific labels** ("Progress", "Library") over safe generic ones ("Home").

## 17. Process

- **Prototype interactively** — a working demo is worth a million static designs and sets a
  concrete bar for the final build.
- **Design interaction and visuals together** — motion isn't a layer added after the pixels.
- **Test with real people in real context**, and review motion with fresh eyes, in slow motion
  and frame by frame.

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

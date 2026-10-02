---
name: ship-android
description: |
  Android platform skill. Routes Jetpack Compose, Material 3, and Kotlin questions to official
  Android sources; carries Ship's registry rules. Only loaded when Stack is android. (ship)
paths: "*.kt,*.kts,*.java,*.xml,build.gradle,build.gradle.kts,AndroidManifest.xml"
user-invocable: false
---

# Android platform skill

**What Ship supports on Android today:** its loop (plan, build, review, launch), the design
registry, and routing to official sources. **What it doesn't have yet:** Compose depth of its own,
verified code examples, or Android-specific review checklists beyond the signs below. Say so when
it matters; don't present Ship as an Android authority. Google's official docs are.

## Precedence

Platform requirements and accessibility (Android API behavior, Google Play policy, TalkBack, font
scale) > product decisions (`DECISIONS.md`, `design-model.yaml`, `design/components.yaml`) >
founder preferences > Material 3 guidance > expert skills > Ship defaults > your inference.
A line here that follows Google's docs is a platform fact, not a Ship default; for motion, the
motion skill outranks every other skill.

## Where each question goes

| Question | Go to |
|---|---|
| Compose basics, layouts, state, lists, theming | [Compose docs](https://developer.android.com/develop/ui/compose/documentation) |
| Material 3 components and theming in Compose | [Material 3 in Compose](https://developer.android.com/develop/ui/compose/designsystems/material3) · [m3.material.io](https://m3.material.io/) |
| Custom design systems in Compose | [Custom design systems](https://developer.android.com/develop/ui/compose/designsystems/custom) |
| Phones, tablets, foldables, desktop windows | [Adaptive layouts](https://developer.android.com/develop/ui/compose/layouts/adaptive) |
| Edge-to-edge, system bars, IME insets | [Edge-to-edge](https://developer.android.com/develop/ui/views/layout/edge-to-edge) |
| Navigation | [Navigation 3](https://developer.android.com/guide/navigation/navigation-3) |
| Accessibility (TalkBack, semantics) | [Compose accessibility](https://developer.android.com/develop/ui/compose/accessibility) |
| Performance, recomposition | [Compose performance](https://developer.android.com/develop/ui/compose/performance) |
| Animation API | [Compose animation](https://developer.android.com/develop/ui/compose/animation/introduction); values from `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/SKILL.md` |
| Coroutines, Flow | [Kotlin coroutines on Android](https://developer.android.com/kotlin/coroutines) |
| App architecture | [Guide to app architecture](https://developer.android.com/topic/architecture) |
| UI tests | [Testing Compose](https://developer.android.com/develop/ui/compose/testing) |
| Mobile design guidance | [Android design](https://developer.android.com/design/ui/mobile) |
| Play policy and launch | [Developer Program Policy](https://play.google.com/about/developer-content-policy/) · [Play Console help](https://support.google.com/googleplay/android-developer/answer/9859455) |

Ship doesn't suggest installing other skills; for anything it doesn't cover, read the official
docs above.

## Road signs (apply without being asked)

- **Registry first.** Colors, type, shapes, spacing, and motion come from `design-model.yaml`.
  The Compose emitter (`design_model.py emit compose`) writes `Theme.kt`: the colours for light
  and dark, text styles, shapes, spacing and motion, as plain Kotlin objects. It doesn't set up
  Material 3, so Material components would fall back to Material's own default colours. Hand it to
  Material once, in the app's own theme file (never the generated one): `MaterialTheme(colorScheme
  = …, typography = …, shapes = …)`, mapping the roles (action → primary, `on_action` → onPrimary
  when the model has it, background, surface, text → onBackground and onSurface, muted →
  onSurfaceVariant, hairline → outline) and the text styles to Material's type roles. Keep
  literals out of composables. Check `design/components.yaml` before building UI; register
  reusable components with their source `file:`.
- **Material 3 components before custom ones** (top app bars, navigation bar/rail, sheets,
  dialogs, snackbars, pull-to-refresh, search). A custom build of something M3 provides needs a
  product reason.
- **Edge-to-edge:** targeting SDK 35+ makes the app edge-to-edge on Android 15+ — handle insets
  (`enableEdgeToEdge` for older versions) rather than padding by guess.
- **Adaptive, not device checks:** decide with window size classes; test phone, foldable, tablet,
  and a resized desktop window.
- **Accessibility:** 48 × 48 dp minimum touch targets (Android + Material guidance); every icon-only control has a
  `contentDescription`; text in `sp` so font scaling works; check TalkBack order.
- **State:** hoist state; one source of truth; side effects in effect APIs, never in composition.
- **Performance claims need a measurement** (profiler, baseline profile, macrobenchmark);
  otherwise they're suggestions.

## By command

**/shipmate plan:** Material 3 navigation pattern per screen; adaptive layouts in scope; note every
Play policy that applies (payments, permissions, data safety).
**/shipmate build:** registry tokens, M3 components, edge-to-edge insets, previews at several font
scales and widths.
**/shipmate review:** Eye checks tokens, touch targets, contrast, TalkBack labels, insets, dark
theme; Crit checks state hoisting, side effects, measured performance.
**/shipmate qa:** font scale 200%, dark theme, TalkBack pass, foldable/tablet widths, gesture
navigation and 3-button navigation, Release build for performance.

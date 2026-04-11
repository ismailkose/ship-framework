---
name: ship-ios
description: |
  iOS/SwiftUI platform skill. Apple API enforcement, HIG compliance, SwiftUI patterns.
  Only loaded when Stack is ios. (ship)
paths: "*.swift,*.xib,*.storyboard,*.xcodeproj,*.plist,*.entitlements,Package.swift"
---

# iOS Platform Skill

This skill enforces Apple-first development practices, HIG compliance, and SwiftUI best patterns. Only loaded when `Stack: ios` is declared in CLAUDE.md.

**Reference files:**
- `.claude/skills/ship/ios/references/swiftui-core.md` — SwiftUI navigation, concurrency, Liquid Glass, animation, gestures, layout, architecture, No-Hack APIs
- `.claude/skills/ship/ios/references/hig-ios.md` — Human Interface Guidelines: navigation, color, components, lifecycle, design checklists
- `.claude/skills/ship/ios/references/swift-essentials.md` — Swift language features, Codable, Swift Testing
- `.claude/skills/ship/ios/references/frameworks/[name].md` — per-framework guides (HealthKit, StoreKit, CloudKit, etc.)

## Apple API First (Rule 19 enforcement)

Before building ANY custom component, check if Apple already provides it. This applies to:

- **UI effects** — blur (`Material`), gradients (`MeshGradient`), haptics (`sensoryFeedback`), symbol animations (`symbolEffect`)
- **Layout** — sizing (`containerRelativeFrame`), keyboard (`scrollDismissesKeyboard`), safe areas
- **Presentation** — sheets (`presentationDetents`), popovers, toolbars (`toolbarVisibility`)
- **Navigation** — `NavigationStack`, `NavigationSplitView`, deep links
- **Input** — `FocusState`, `onSubmit`, search with `searchable`
- **Accessibility** — built-in VoiceOver labels, Dynamic Type, reduce motion

See `.claude/skills/ship/ios/references/swiftui-core.md` Section 6.5 for the 9 most common violations where developers custom-build what Apple already provides.

**Eye rejects any PR that custom-builds something Apple provides natively.**

## For Planning (/ship-plan)

When Arc plans iOS features:

1. **Navigation architecture** — read `.claude/skills/ship/ios/references/swiftui-core.md` Section 1 for router pattern, NavigationStack vs NavigationSplitView, sheet routing, deep links.
2. **Framework check** — read `.claude/skills/ship/ios/references/frameworks/[relevant].md` for the feature being planned. E.g., building in-app purchases → read `.claude/skills/ship/ios/references/frameworks/storekit.md`.
3. **HIG compliance** — read `.claude/skills/ship/ios/references/hig-ios.md` Sections 1, 4, 7-8 for navigation patterns, color system, component choices, app lifecycle.

## For Building (/ship-build)

When Dev builds iOS features:

1. **SwiftUI patterns** — read `.claude/skills/ship/ios/references/swiftui-core.md` for navigation, concurrency (@concurrent, MainActor, Sendable), Liquid Glass, animation, gestures, layout, @Observable architecture, UIKit interop.
2. **Swift language** — read `.claude/skills/ship/ios/references/swift-essentials.md` for result builders, macros, typed throws, Codable patterns, Swift Testing.
3. **HIG implementation** — read `.claude/skills/ship/ios/references/hig-ios.md` Sections 2-6, 8-9 for safe areas, Dynamic Type, semantic colors, touch targets, spring animations, notifications, multitasking.
4. **Frameworks** — read `.claude/skills/ship/ios/references/frameworks/[relevant].md` matching the feature being built. Only the relevant framework file — not all of them.
5. **No-Hack APIs** — before any custom implementation, check `.claude/skills/ship/ios/references/swiftui-core.md` Section 6.5.

## For Review (/ship-review)

When Eye reviews iOS UI:

1. **HIG design checklist** — read `.claude/skills/ship/ios/references/hig-ios.md` Section 10 for navigation, typography, color, touch, materials, accessibility, lifecycle checklists.
2. **SwiftUI implementation checklist** — read `.claude/skills/ship/ios/references/swiftui-core.md` Section 9 for navigation code, concurrency, Liquid Glass, animation, architecture, No-Hack API enforcement.
3. **Framework review** — read review checklists in `.claude/skills/ship/ios/references/frameworks/` files when reviewing framework-specific code.
4. **Apple API violation scan** — flag any custom implementation that duplicates a native SwiftUI modifier or system framework capability.

## For QA (/ship-qa)

When Test verifies iOS builds:

1. **Dynamic Type** — test with all text sizes (accessibility sizes too).
2. **Dark Mode** — verify semantic colors adapt correctly.
3. **VoiceOver** — navigate the entire flow with VoiceOver enabled.
4. **Reduced Motion** — verify `accessibilityReduceMotion` is respected.
5. **Device matrix** — test on smallest supported device (iPhone SE) and largest (iPad Pro if universal).

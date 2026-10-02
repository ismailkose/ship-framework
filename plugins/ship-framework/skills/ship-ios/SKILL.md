---
name: ship-ios
description: |
  iOS/SwiftUI platform skill. Routes SwiftUI, Swift, HIG, and Apple-framework questions to the
  right source; enforces the design registry and platform-API-first. Only loaded when Stack is ios. (ship)
paths: "*.swift,*.xib,*.storyboard,*.xcodeproj,*.plist,*.entitlements,Package.swift"
user-invocable: false
---

# iOS platform skill

Ship carries its own working guides for building iOS apps — screens, Swift, data and sync,
purchases and accounts, notifications, media, system surfaces, devices, and on-device
intelligence — plus Ship's contracts and the facts the model can't know yet (iOS 27 / Xcode 27 /
Swift 6.4). Nothing extra is needed.

## Precedence (when sources disagree)

Platform facts and accessibility (SDK `@available`, App Review, VoiceOver, Reduce Motion)
> product decisions (`DECISIONS.md`, `design-model.yaml`, `design/components.yaml`)
> founder preferences > Apple HIG and API docs > expert skills (any the builder installed; the motion skill for motion)
> Ship defaults > your inference. If Apple's bundled Xcode text and the SDK disagree, the SDK wins.
Ship's guides tag each rule **Apple** (platform fact/requirement) or **Ship** (default): an installed
expert skill outranks a **Ship** default, never an **Apple** fact. For motion, the motion skill outranks
every other expert skill.

## Where each question goes

| Question | Go to (`${CLAUDE_PLUGIN_ROOT}/skills/ship-ios/references/`) |
|---|---|
| Tokens, components, "can I hard-code this?", architecture default, native API first | `swiftui-ship.md` |
| Building a screen: state, navigation, lists, forms, layout, sheets, gestures, charts, Liquid Glass, accessibility, localization, previews | `swiftui-building.md` |
| Concurrency (where code runs), networking / API clients, JSON, errors, Swift Testing | `swift-practice.md` (+ `ios-27.md` §2–3 for build settings) |
| Saving data, SwiftData/Core Data, iCloud sync, migrations, files | `data-sync.md` |
| Purchases, subscriptions, Apple Pay, sign-in, passkeys, Face ID, Keychain, logout, token migration, encryption | `commerce-identity.md` |
| Reminders, push, background work, Live Activities, alarms, VoIP | `notifications-background.md` |
| Photos, camera, audio, video, speech, PDFs, drawing, games/3D | `media.md` |
| Siri, Shortcuts, widgets, controls, deep/universal links, tips, web views, App Clips, SharePlay | `system-integration.md` |
| Location, maps, Health and workouts, calendar, contacts, motion, weather, music, FinanceKit, SensorKit, EnergyKit, PermissionKit | `device-data.md` |
| Bluetooth, accessory pairing, NFC, HomeKit/Matter, DockKit | `accessories.md` |
| Voice Control, Switch Control, Full Keyboard Access, VoiceOver per component, accessibility audits | `accessibility-ios.md` |
| Foundation Models, Core ML, Vision, language, translation | `intelligence.md` |
| Any other Apple framework (index + signs) | `frameworks.md` |
| New in iOS 27 / Xcode 27 / Swift 6.4, availability | `ios-27.md` + Xcode's bundled skills it lists |
| Screen structure, type, color, touch, icons, lifecycle, Eye's checklist | `hig-ios.md` |
| Slow, janky, hangs, leaks, logging, crashes | `swiftui-performance.md` |
| Chat / AI-assistant screens | `chat-ui-swiftui.md` |
| Motion values, springs, Reduce Motion behavior | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/SKILL.md` (never SwiftUI or expert-skill defaults) |
| App Review readiness | `frameworks.md` › Tooling and App Store · `commerce-identity.md` §1 |

Load only the row the change touches.

## Beyond these guides

Ship's guides above are the baseline (recipes and compiled examples for most capabilities, a few
still pointers), with Xcode 27's bundled guides (`ios-27.md` §1) and developer.apple.com. Ship doesn't
suggest installing other skills and never installs anything. A skill the builder installed on their
own shows up in the knowledge route with Ship's corrections, and a checked **Apple** line outranks it.

## Road signs (apply without being asked)

- **Registry first.** Colors, type, radius, spacing, motion come from the registry's `Theme.swift`
  (with Ship's generated header: never edit it; a hand-written theme is the project's own code),
  never inline a literal the model covers; check `design/components.yaml` before
  building UI and register new reusable primitives.
- **Platform API first (`${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` › Platform first).** Check `swiftui-ship.md` §3 before hand-building; use the
  native API when it gives the needed behavior at the deployment target. A custom build needs a
  stated reason (a capability the API lacks, or the target) — reviewers ask for it, not reject.
- **Availability is a fact, not a memory.** Above the deployment target → `if #available` with a
  real fallback. Unsure of a version → compile it or grep the SDK (`ios-27.md` §2).
- **Read the build settings before concurrency advice** — default isolation and Approachable
  Concurrency differ between new Xcode 27 app targets and packages (`ios-27.md` §3).
- **After an SDK bump,** `@State` and result-builder errors have documented fixes — read the Xcode
  reference before "fixing" by reordering code.
- **Liquid Glass** on custom surfaces only where a product decision says so; controls/navigation
  layer only.
- **Soft-deprecated APIs** found during feature work: flag, don't rewrite, unless asked.
- **Performance claims need a measurement**; otherwise they're suggestions.

## By command

**/shipmate plan (Arc):** `hig-ios.md` §1, §7, §8 for screen structure; the guide for each capability
the plan touches (the table above) — list its prerequisites (capabilities, entitlements, Info.plist
keys, server, accounts) and the deployment target any iOS-26/27-only API implies; architecture per
`swiftui-ship.md` §4 unless `DECISIONS.md` says otherwise.

**/shipmate build (Dev):** `swiftui-ship.md` §2–§3 before writing UI; `swiftui-building.md` /
`swift-practice.md` for the patterns; the capability's guide (table above) including its failure
and permission-denied paths; `ios-27.md` for any SDK 27 API; `swiftui-performance.md` §3 before
calling a list or live-updating screen done.

**/shipmate review (Eye, Crit):** Eye — `hig-ios.md` §9 and `swiftui-ship.md` §8. Crit —
`swiftui-ship.md` §5 (enforced rules), `swiftui-performance.md` §6, and the capability guide's rules
for framework code (purchases verified and finished, permissions denied handled, cancellation,
sync conflicts). Flag a hand-built native capability that has no stated reason.

**/shipmate qa (Test):** the capability guide's **Verify** table — run what the simulator can prove and
list the device/account/hardware cases as manual acceptance, never as passed; Dynamic Type through AX5; light and dark; Increase Contrast; Reduce Motion
and Reduce Transparency; VoiceOver through the whole flow; the smallest supported iPhone and a
resized iPad window; Release build for anything performance-related.

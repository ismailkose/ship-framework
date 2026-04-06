# iOS Muscle Plan — Absorbing swift-ios-skills into Ship Framework

> Source: [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) v3.1.0 (76 skills)
> Target: Ship Framework v2026.04.06
> Philosophy: Not 76 new files. Add muscle to existing bones.

---

## How Ship's Structure Absorbs This

Their repo has 76 standalone skills (one file per framework). Ship has 3 deep iOS core references + 47 framework references + 19 shared design references, all wired through persona routing.

The integration strategy:

| Their structure | Ship's structure | Action |
|---|---|---|
| 9 SwiftUI skills (patterns, navigation, performance, animation, gestures, layout, liquid-glass, uikit-interop, webkit) | `swiftui-core.md` (2,947 lines, 9 sections) | **Enrich** — add missing patterns, diagnostics, common mistakes |
| 6 Core Swift skills (concurrency, language, codable, testing, charts, swiftdata) | `swift-essentials.md` (1,878 lines) + framework refs | **Enrich** swift-essentials + deepen framework refs |
| 15 App Experience frameworks | 13 existing framework refs + 2 new | **Enrich** existing + **add** avkit.md, pdfkit.md |
| 8 Data & Service frameworks | 8 existing framework refs | **Enrich** with their deeper patterns |
| 5 AI/ML skills | 4 existing framework refs + 1 existing | **Enrich** existing refs |
| 11 Engineering skills | 8 existing framework refs | **Enrich** + **add** cryptokit.md |
| 8 Hardware skills | 5 existing + 3 new | **Enrich** + **add** accessorysetupkit.md, dockkit.md, sensorkit.md |
| 10 Platform Integration skills | 5 existing + 5 new | **Enrich** + **add** appmigrationkit.md, audioaccessorykit.md, browserenginekit.md, cryptotokenkit.md, relevancekit.md |
| 4 Gaming skills | 0 existing | **Add** gamekit.md, spritekit.md, scenekit.md, tabletopkit.md |

---

## Phase 1: Enrich swiftui-core.md (Biggest Impact)

Their 9 SwiftUI skills combined ≈ 5,000 words of patterns. Ship's swiftui-core.md is already 2,947 lines but their content surfaces gaps.

### Section 1: Navigation (existing)
**Add from their swiftui-navigation:**
- `NavigationSplitView` multi-column patterns (they cover 2-column and 3-column, Ship has basic coverage)
- Sheet presentation sizing options: `.presentationDetents`, `.presentationDragIndicator`, `.presentationCornerRadius` (iOS 16+)
- iOS 26 Tab API: search role, `sidebarAdaptable` style, `TabSection`
- Deep linking: Universal Links AASA file pattern, `NSUserActivity` handoff, custom URL scheme handling
- 8 common mistakes list (they have specific compilation/runtime failure modes)

### Section 3: Liquid Glass (existing)
**Add from their swiftui-liquid-glass:**
- `GlassEffectContainer` for grouped rendering
- Morphing modifiers: `glassEffectID`, `glassEffectUnion`, `glassEffectTransition`
- `.regular` vs `.identity` glass variant distinction
- Reduce Transparency / Reduce Motion accessibility handling
- Common mistakes (5 specific items)

### Section 4: Animation (existing)
**Add from their swiftui-animation:**
- PhaseAnimator discrete phase cycling pattern
- KeyframeAnimator multi-property timelines (4 keyframe types: Linear, Cubic, Spring, Move)
- `@Animatable` macro (iOS 26+ — boilerplate elimination)
- Navigation zoom transitions (iOS 18+)
- ContentTransition for in-place text/number changes
- Symbol effects for SF Symbol animations
- Spring type: 4 initialization forms (perceptual, physical, response, settling)
- 7 common mistakes with code examples

### Section 5: Gestures (existing)
**Add from their swiftui-gestures:**
- Gesture composition: `.simultaneously`, `.sequenced`, `.exclusively`
- `@GestureState` vs `@State` distinction (auto-reset behavior)
- `GestureMask` scope control
- Renamed APIs: `MagnificationGesture` → `MagnifyGesture`, `RotationGesture` → `RotateGesture`
- `minimumAngleDelta` for RotateGesture
- Gesture priority in view hierarchies
- Common mistakes + review checklist

### Section 6: Layout (existing)
**Add from their swiftui-layout-components:**
- `LazyVGrid` / `LazyHGrid` patterns (fixed, flexible, adaptive columns)
- `safeAreaBar` and `backgroundExtensionEffect` (iOS 26)
- `scrollEdgeEffectStyle` (iOS 26)
- Form and Controls patterns (TextField, SecureField, Picker, Toggle, Stepper, DatePicker, ColorPicker)
- Searchable modifier patterns (`.searchable`, suggestions, tokens, scopes)
- Common mistakes (array indices as ForEach IDs, GeometryReader in lazy containers)

### Section 7: Architecture (existing)
**Add from their swiftui-patterns:**
- MV pattern emphasis (lightweight, no unnecessary ViewModels)
- `@Observable` ownership rules (5 distinct cases)
- View ordering conventions (6 member categories)
- View composition strategies: subviews vs `@ViewBuilder` vs `ViewModifier`
- Async data loading `.task` patterns
- iOS 26+ new APIs
- Performance guidelines from patterns perspective

### Section 8: UIKit Interop (existing)
**Add from their swiftui-uikit-interop:**
- Coordinator pattern as delegate bridge (critical timing for delegate assignment)
- `UIHostingController` three-step sequence
- `sizingOptions` for `intrinsicContentSize` (iOS 16+)
- Closures vs `@Binding` decision guidance
- Bidirectional state updates via Coordinator references

### NEW Section 10: Performance Diagnostics
**Add from their swiftui-performance (this is the biggest gap):**
- Diagnostic workflow: code review → profile → diagnose → remediate → verify
- 7 common antipatterns to check in code review
- Instruments profiling: 3 SwiftUI-specific instruments + how to read them
- `Self._printChanges()` for debug builds
- Identity and lifetime: structural vs explicit vs AnyView
- Lazy loading decision tree
- State and observation optimization (granular tracking)
- 10 common mistakes with examples
- Review checklist (10 items)

### NEW: WebKit section addition
**Add from their swiftui-webkit:**
- Tool selection guide: `WebView` vs `SFSafariViewController` vs `ASWebAuthenticationSession`
- `WebPage` observable class with `NavigationDeciding` protocol
- JavaScript integration via `callJavaScript()`
- Critical warning: avoid `WKWebView` wrappers
- Resource handling configuration

**Estimated growth:** swiftui-core.md from ~2,947 lines to ~3,800-4,200 lines

---

## Phase 2: Enrich swift-essentials.md

### Section 1: Swift Language (existing)
**Add from their swift-language:**
- If/switch expressions (Swift 5.9+)
- Typed throws with specific error types
- `Never` type patterns
- Regex builders (Swift 5.7+)
- Modern collection APIs (`.first(where:)`, `.compactMap`, `.reduce(into:)`)
- `FormatStyle` API patterns
- Common mistakes + review checklist

### Section 2: Concurrency (existing — CRITICAL UPDATE)
**Add from their swift-concurrency:**
- **Swift 6.3 SE proposals:** SE-0466 (default MainActor isolation), SE-0461, SE-0472, SE-0475, SE-0493 (async defer), SE-0473 (clock epochs)
- 3-step triage workflow for concurrency errors
- Actor isolation: 3 core principles
- Sendable rules: value type vs actor vs class
- Synchronization primitives: `Mutex`, `OSAllocatedUnfairLock`, `Atomic`
- `Observations { }` pattern for `@Observable` types
- `nonisolated(unsafe)` guidance
- Common mistakes + review checklist

### Section 3: Codable (existing or new subsection)
**Add from their swift-codable:**
- Heterogeneous arrays with discriminator fields
- Lossy array decoding via wrapper types
- `nestedContainer` for flattening JSON
- `decodeIfPresent` with nil-coalescing for defaults
- `PropertyListEncoder`/`Decoder` alternatives
- Integration patterns: URLSession, SwiftData, UserDefaults
- Common mistakes

### Section 4: Testing (existing or new subsection)
**Add from their swift-testing:**
- `@Test` decorator, `#expect`/`#require` assertions
- `Confirmation` pattern (replacing `XCTestExpectation`)
- Test traits and organization
- Parameterized testing
- Tags and filtering (with CLI syntax caveat)
- Async testing with actor isolation
- Test attachments
- Exit testing
- Common mistakes + review checklist

**Estimated growth:** swift-essentials.md from ~1,878 lines to ~2,600-3,000 lines

---

## Phase 3: Enrich Existing Framework References

For each existing framework ref, add three things from their equivalent skill:
1. **Common Mistakes section** (5-8 anti-patterns)
2. **Review Checklist** (5-8 verification items for Crit/Eye)
3. **Any missing patterns** unique to their coverage

### High-priority enrichments (used in most apps):

| Ship file | Their skill | Key additions |
|---|---|---|
| `swiftdata.md` (280 lines → ~500) | swiftdata | `@ModelActor` cross-actor patterns, `PersistentIdentifier`, schema versioning, migration strategies, `#Predicate` type-safe queries, relationship inverse rules |
| `storekit.md` (existing) | storekit | Family Sharing considerations, subscription grace periods / billing retry states, `SubscriptionStoreView` (iOS 17+), `AppStore.sync()` restoration, `.finish()` requirement |
| `authentication.md` (existing) | authentication | Credential state checking on app launch, `.preferImmediatelyAvailableCredentials` vs interactive, identity token server-side validation, `credentialRevokedNotification` |
| `healthkit.md` (existing) | healthkit | `HKSampleQueryDescriptor` async/await, empty results on denial (not errors), `HKWorkoutSession` + `HKLiveWorkoutBuilder`, statistics options matching |
| `cloudkit.md` (existing) | cloudkit | `CKSyncEngine` (iOS 17+) as recommended sync, SwiftData integration, state persistence, iCloud account status checking |
| `coreml.md` (existing) | coreml | Async model loading (`MLModel.load()` iOS 16+), `MLTensor` (iOS 18+), `MLState` stateful prediction (iOS 18+), `CoreMLRequest` Vision integration, profiling tools |
| `debugging.md` (existing) | debugging-instruments | Memory Graph Debugger workflow, hang diagnostics (250ms vs 1s thresholds), `os_signpost`, Thread Checker, `xctrace` CLI, SPM dependency conflict resolution |
| `networking.md` (existing) | ios-networking | Token refresh pattern, exponential backoff, request middleware/interceptor, URLSession doesn't throw for 4xx/5xx, protocol-based clients for testability |
| `accessibility.md` (existing) | ios-accessibility | VoiceOver reading order, focus restoration with Task delay, custom rotors, Assistive Access (iOS 18+), `UIAccessibility` notifications, testing methods |
| `push-notifications.md` (existing) | push-notifications | Common mistakes + review checklist enrichment |
| `app-intents.md` (existing) | app-intents | 4-step triage workflow, `SnippetIntent` (iOS 26), `IntentValueQuery` (iOS 26), `AppEnum` with `LosslessStringConvertible`, non-optional parameter compilation failures |
| `widgetkit.md` (existing) | widgetkit | Interactive widgets with AppIntent, Control Center widgets (iOS 18+), Liquid Glass, `WidgetPushHandler`, CarPlay widgets (iOS 26), Lock Screen accessory families |
| `swift-charts.md` (existing) | swift-charts | Vectorized plots for 10,000+ data points, `SectorMark` pie/donut (iOS 17+), `foregroundStyle(by:)` data-driven encoding, scale domain with zero-baseline |

### Medium-priority enrichments:

| Ship file | Their skill | Key additions |
|---|---|---|
| `background-processing.md` | background-processing | `BGContinuedProcessingTask` (iOS 26+) with `ProgressReporting`, critical expiration handler pattern |
| `live-activities.md` | activitykit | Common mistakes + review checklist |
| `mapkit.md` | mapkit | Common mistakes + review checklist |
| `callkit.md` | callkit | Common mistakes + review checklist |
| `homekit.md` | homekit | Common mistakes + review checklist |
| `passkit.md` | passkit | Common mistakes + review checklist |
| `musickit.md` | musickit | Common mistakes + review checklist |
| `shareplay.md` | shareplay-activities | `prepareForActivation`/`activate` correction |
| `device-integrity.md` | device-integrity | Common mistakes + review checklist |
| `energykit.md` | energykit | Remove 'verify against Xcode 26 SDK' placeholders |
| `permissionkit.md` | permissionkit | Common mistakes + review checklist |
| `photos-camera.md` | photokit | Common mistakes + review checklist |
| `localization.md` | ios-localization | `.navigationTitle` correction + common mistakes |
| `metrickit.md` | metrickit | Call stacks, signposts, export patterns |
| `natural-language.md` | natural-language | Common mistakes + review checklist |
| `speech.md` | speech-recognition | Common mistakes + review checklist |
| `vision-framework.md` | vision-framework | Common mistakes + review checklist |
| `weatherkit.md` | weatherkit | Common mistakes + review checklist |
| `webkit.md` | swiftui-webkit | Tool selection guide, WebPage observable |
| `ios-security.md` | ios-security | Common mistakes + review checklist |
| `core-bluetooth.md` | core-bluetooth | Common mistakes + review checklist |
| `core-motion.md` | core-motion | Common mistakes + review checklist |
| `core-nfc.md` | core-nfc | Common mistakes + review checklist |
| `pencilkit.md` | pencilkit + paperkit | PaperKit unified markup, FeatureSet config, async serialization |
| `realitykit.md` | realitykit | Common mistakes + review checklist |
| `tipkit.md` | tipkit | Common mistakes + review checklist |
| `apple-on-device-ai.md` | apple-on-device-ai | Common mistakes + review checklist |
| `eventkit.md` | eventkit | Common mistakes + review checklist |
| `contacts.md` | contacts-framework | Common mistakes + review checklist |

---

## Phase 4: New Framework References (14 files)

These frameworks don't exist in Ship yet. Create new files in `references/ios/frameworks/`:

### Common frameworks (most apps could use):

| New file | Source skill | Lines est. | Content |
|---|---|---|---|
| `avkit.md` | avkit | ~300 | AVPlayerViewController, SwiftUI VideoPlayer, PiP, AirPlay, transport controls, subtitles |
| `pdfkit.md` | pdfkit | ~250 | PDFDocument/PDFPage/PDFView, text operations, annotations, SwiftUI integration |
| `cryptokit.md` | cryptokit | ~280 | Hashing, HMAC, symmetric encryption, public-key signing, key agreement, Secure Enclave |
| `financekit.md` | financekit | ~220 | Authorization, account types, balances/transactions, queries, UI pickers, Wallet Orders |

### Gaming bundle:

| New file | Source skill | Lines est. | Content |
|---|---|---|---|
| `gamekit.md` | gamekit | ~350 | Game Center auth, Access Point, leaderboards, achievements, real-time + turn-based MP |
| `spritekit.md` | spritekit | ~320 | Scene setup, nodes, actions, physics, touch handling, camera, particles, SwiftUI |
| `scenekit.md` | scenekit | ~300 | Nodes/geometry, materials, lighting, cameras, animation, physics, model loading + deprecation notice |
| `tabletopkit.md` | tabletopkit | ~150 | visionOS board games, spatial interactions, RealityKit integration |

### Niche/specialized:

| New file | Source skill | Lines est. | Content |
|---|---|---|---|
| `accessorysetupkit.md` | accessorysetupkit | ~180 | Privacy-preserving BLE/WiFi discovery, session management, picker UI |
| `dockkit.md` | dockkit | ~300 | Motorized gimbal tracking, ML subject detection, motor control |
| `sensorkit.md` | sensorkit | ~150 | Research-grade sensor data, delegate architecture, fetch requests |
| `browserenginekit.md` | browserenginekit | ~350 | Multi-process browser engine, XPC communication, sandboxing (EU/Japan) |
| `appmigrationkit.md` | appmigrationkit | ~220 | Android→iOS data transfer, extension-based export/import |
| `cryptotokenkit.md` | cryptotokenkit | ~250 | Smart card/security token, APDU communication, keychain integration |

### Skipping (too niche, <100 words of unique content):

- `audioaccessorykit.md` — ~500 words, very narrow (audio routing for accessories)
- `relevancekit.md` — watchOS Smart Stack only, ~650 words
- `adattributionkit.md` — ad attribution tracking, ~550 words

> These 3 can be added later if anyone asks. Not worth the routing complexity.

---

## Phase 5: Routing Updates

### ship-team.md — Add framework routing

```
### Gaming Stack (when project includes games)
22. **Dev reads `references/ios/frameworks/gamekit.md`** when building Game Center features.
23. **Dev reads `references/ios/frameworks/spritekit.md`** when building 2D game scenes.
24. **Dev reads `references/ios/frameworks/scenekit.md`** when building 3D scenes (note: maintenance mode, prefer RealityKit).
```

### ship-review.md — Leverage new review checklists

Every enriched framework ref now has a Review Checklist section. Update Crit and Eye to read these:

```
**Crit reads the Review Checklist in the relevant framework reference** when reviewing
framework-specific code — authentication flows, StoreKit purchases, HealthKit queries, etc.
```

### ship-build.md — Reference loading

Add a note: "When building with a specific framework, Dev reads the matching file in `references/ios/frameworks/`. Each file now includes Common Mistakes — read those BEFORE writing code, not after."

### hig-ios.md — No changes needed

HIG stays design-focused. The enrichments go into implementation refs.

---

## Phase 6: Overlap Quality Fixes

Cross-reference notes to add, preventing confusion between Ship's existing refs and the new enriched content:

1. **swiftui-core.md Section 10 (Performance)** → Add note: "For design-level performance decisions (perceived speed, skeleton screens, optimistic UI), see `ux-principles.md` Section 3. This section covers SwiftUI-specific profiling and code optimization."

2. **swift-essentials.md Section 2 (Concurrency)** → Add note: "For SwiftUI-specific concurrency patterns (@Observable, .task, MainActor views), see `swiftui-core.md` Section 7. This section covers Swift language-level concurrency."

3. **webkit.md (framework ref)** → Add note: "For SwiftUI WebView integration patterns, see `swiftui-core.md` WebKit section. This file covers WebKit framework APIs."

4. **accessibility.md (framework ref)** → Add note: "For design-level accessibility guidance (WCAG, contrast, touch targets), see `shared/ux-principles.md` Section 5. This file covers iOS-specific VoiceOver, Dynamic Type, and UIAccessibility APIs."

5. **debugging.md** → Add note: "For SwiftUI-specific performance profiling, see `swiftui-core.md` Section 10. This file covers general debugging, memory, and Instruments."

---

## Phase 7: setup.sh and ship-update.sh

### setup.sh
- Add new framework files to the `--add-framework` flag options
- Update the available frameworks list in help text

### ship-update.sh
- New framework files will sync automatically (they're in the template, not protected)
- No special migration needed — new files just appear

### VERSION
- Bump to `2026.04.07` or next appropriate date

### CHANGELOG.md
- Add entry for iOS Muscle update

### README.md
- Update framework count: 47 → 61 framework references
- Add Gaming category mention

### CHEATSHEET.md
- Add new framework categories to reference list

---

## Execution Order

| Phase | Files touched | Effort | Impact |
|---|---|---|---|
| **Phase 1** | swiftui-core.md | High (biggest file) | Highest — core SwiftUI patterns |
| **Phase 2** | swift-essentials.md | Medium | High — Swift 6.3 currency |
| **Phase 3** | 30+ framework refs | High (volume) | High — anti-patterns prevent bugs |
| **Phase 4** | 14 new files | Medium | Medium — coverage completeness |
| **Phase 5** | ship-team.md, ship-review.md, ship-build.md | Low | Medium — proper routing |
| **Phase 6** | 5 cross-reference notes | Low | Low — prevents confusion |
| **Phase 7** | setup.sh, ship-update.sh, README, CHANGELOG, CHEATSHEET | Low | Low — housekeeping |

**Total estimated new/changed lines:** ~4,000-5,000 across all phases
**New files:** 14 framework references
**Enriched files:** 2 core refs + ~30 framework refs + 3 command files

---

## What This Does NOT Do

- Does not create 76 separate skill files (Ship's structure is different)
- Does not copy their content verbatim (Ship enriches with its own patterns + persona routing)
- Does not add their `npx skills` installer (Ship uses `setup.sh` / `ship-update.sh`)
- Does not break existing routing (all changes are additive)
- Does not touch shared/ design references (those are Ship's unique moat)

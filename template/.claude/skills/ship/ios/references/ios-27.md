<!-- ship-reference
id: ios-27
kind: platform
sources: iPhoneOS27.0.sdk .swiftinterface + headers (Xcode 27.0 27A266a; Swift 6.4, swiftlang-6.4.0.34.1) — each fact in §3 is tagged by how it was checked (scripts/checks/ios.sh compiles or inspects the tagged ones); xcode-bundled-skills@27A266a (pointed to, never copied); https://developer.apple.com/documentation (2026-09-23); Xcode 27 project templates (App Base.xctemplate)
reviewed: 2026-09-23
-->
# iOS 27 / Xcode 27 / Swift 6.4 — what changed after the model's training

Read this before writing code that uses SDK 27 APIs, before answering "what's new", and whenever
a compile error appears right after moving to Xcode 27. Apple's own guidance ships inside Xcode;
this file points at it and records what Ship checked. It covers selected changes, not the whole
release — for the language itself use Swift's own docs (§2b).

## 1. Apple's bundled skills (read them, never copy them)

```bash
R="$(xcode-select -p)/../PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources"
ls "$R"/*.idechatprompttemplate "$R"/AdditionalDocumentation/   # what this Xcode ships
```

| Topic | Read |
|---|---|
| New SwiftUI APIs and breakages in SDK 27 | `swiftui-whats-new-27.idechatprompttemplate` + `swiftui-whats-new-27-ref-*.md.packaged` (state-macro, content-builder, reorderable, swipe-actions, async-image, item-binding, toolbar) |
| SwiftUI best practice (data flow, environment, `ForEach` identity, localization, soft deprecations, `@Animatable`) | `swiftui-specialist` + `swiftui-specialist-ref-*` |
| App Intents (26 + 27 additions; correctness) | `app-intents-whats-new-27`, `app-intents-specialist` (+ refs) |
| Document-based apps (`Document`, `DocumentGroup`) | `building-document-based-swiftui-applications` |
| UIKit modernization (scenes, `UIScreen.main`, orientation, safe areas) | `uikit-app-modernization` |
| Security build settings | `audit-xcode-security-settings` |
| Framework notes (iOS 26 generation) | `AdditionalDocumentation/`: FoundationModels, StoreKit, AlarmKit, MapKit GeoToolbox, SwiftData inheritance, WidgetKit / SwiftUI / UIKit Liquid Glass, Visual Intelligence, Assistive Access, Swift Charts 3D, WebKit, styled text editing, toolbar features, InlineArray/Span, Swift concurrency (6.2) |

Missing (older Xcode or Linux)? Use developer.apple.com. If Apple's bundled text and the SDK
disagree, **the SDK wins** — two such cases are in §3.

## 2. Check availability, don't remember it

```bash
SDK="$(xcrun --sdk iphoneos --show-sdk-path)"
grep -rn -B4 'func dismissalConfirmationDialog' "$SDK"/System/Library/Frameworks/SwiftUI*.framework/Modules/*/arm64e-apple-ios.swiftinterface | grep @available
# or compile the call at the deployment target — an "only available in iOS N" error is the answer:
xcrun -sdk iphonesimulator swiftc -typecheck -target arm64-apple-ios18.0-simulator Probe.swift
```

Anything above the deployment target: `if #available(iOS 27, *)` with a real fallback.

**Before advising on concurrency or language features, read the project's settings** (per target):

```bash
xcrun swiftc --version                                   # compiler (Xcode 27.0: Swift 6.4)
xcodebuild -showBuildSettings -scheme <Scheme> | grep -E '^\s*(SWIFT_VERSION|SWIFT_STRICT_CONCURRENCY|SWIFT_DEFAULT_ACTOR_ISOLATION|SWIFT_APPROACHABLE_CONCURRENCY|SWIFT_UPCOMING_FEATURE_[A-Z_]+|OTHER_SWIFT_FLAGS|IPHONEOS_DEPLOYMENT_TARGET) ='
```

A setting that isn't printed is at its default: language mode 6 means strict concurrency is
already complete; default isolation is nonisolated; upcoming features are off. Packages keep
these in `Package.swift` instead (`swift-tools-version`, `swiftLanguageModes`,
`.defaultIsolation(...)`, `.enableUpcomingFeature(...)`, `platforms`). App targets and packages in
one project often differ — check the target you're changing.

## 2b. Swift's own sources

- Release notes: [Swift 6.4 released](https://www.swift.org/blog/swift-6.4-released/) (swift.org blog);
  proposals and their status: [Swift Evolution](https://www.swift.org/swift-evolution/).
- Language: [The Swift Programming Language — Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/);
  standard library, e.g. [TaskGroup](https://docs.swift.org/latest/documentation/swift/taskgroup/).
- Migrating to Swift 6 mode: [Swift migration guide](https://www.swift.org/migration/documentation/migrationguide/).
- Xcode's bundled concurrency notes describe the Swift 6.2 generation — pair them with the
  release notes above for later changes.
Deployment target is a product decision (`DECISIONS.md`). Ship default when none is recorded:
keep the project's current target; for a new app, suggest one release back (iOS 26) and gate 27-only
APIs.

## 3. Checked facts (SDK 27.0, Swift 6.4)

Tags: **[compiled]** — `ios.sh` compiles it at the stated minimum and expects an availability
error below it · **[SDK]** — read from the SDK interface, a header, or an Xcode template (by
`ios.sh` where noted) · **[docs]** — from Apple's or Xcode's documentation, not compiled. Nothing
here is runtime-tested.

**SwiftUI**
- [docs] `@State` is now a macro. Views that compiled before can fail ("used before being initialized",
  "invalid redeclaration of synthesized property", "extraneous argument label"). Read Xcode's
  state-macro reference before fixing — reordering the init assignments is the wrong fix.
- [docs] Result builders are unified under `@ContentBuilder`; expect ambiguous `overlay`/`background`
  `ShapeStyle` overloads and slower type-checking in deeply branching Charts — content-builder ref.
- [compiled] iOS 27.0+: `.reorderable()` + `.reorderContainer(for:)`, `.swipeActionsContainer()`,
  `.dismissalConfirmationDialog(…)` (not 26), `AsyncImage(request:)`, `.asyncImageURLSession(_:)`,
  `ToolbarOverflowMenu`, `.visibilityPriority`, `.topBarPinnedTrailing`, `.contentMarginsRemoved`,
  `ToolbarPlacement.statusBar` (`.toolbarVisibility(.hidden, for: .statusBar)`); [SDK] the SwiftUI
  `Document` protocol.
- [compiled] **SDK ≠ Apple's reference, case 1:** `confirmationDialog(_:item:…)` and `alert(_:item:…)` are
  inlined into your binary, so with Xcode 27 they compile for **iOS 15+** — Xcode's item-binding
  reference says 27. No `#available` needed above iOS 15.
- [compiled] **SDK ≠ Apple's reference, case 2:** Xcode's toolbar reference spells it
  `toolbarMinimizeBehavior(_:for:)`, which doesn't exist. The SDK 27.0 names are
  `toolbarMinimizationBehavior(_:for:)` (`.automatic`, `.onScrollDown`, `.onScrollUp`, `.never`) and
  `toolbarMinimizationRestoration(_:for:)` (`.automatic`, `.atScrollEdge`), iOS 27+. Also real:
  `tabBarMinimizeBehavior` (26+) [compiled] and `toolbarMinimizationSafeAreaAdjustment` [SDK].
- [compiled] **SDK ≠ Apple's reference, case 3:** `ForEach(items.enumerated(), id: \.element.id)` needs an
  **iOS 26** deployment target: `enumerated()` became a collection in iOS 26, and at an iOS 18 target
  the compiler says the conformance is only available in iOS 26. Xcode's `ForEach` reference names
  Swift 6.1 and no OS limit. Below iOS 26, use `Array(items.enumerated())`.
- [compiled] `@Animatable` / `@AnimatableIgnored`: with the SDK 27 toolchain the macro back-deploys (declared
  iOS 13+; a multi-property `Shape` type-checks at an iOS 13 target). Its companion
  `AnimatableValues` type is iOS 26+. "iOS 26+" in other sources describes the SDK generation, not
  the deployment floor.

**Swift 6.4**
- [compiled] `await` inside `defer` works in async functions (SE-0493): `defer { await store.close() }`.
  There is no `async defer` syntax.
- [compiled] Default `MainActor` isolation (SE-0466) is **opt-in per module**. The compiler default is
  nonisolated; opt in with `-default-isolation MainActor`, SwiftPM
  `.defaultIsolation(MainActor.self)` (tools 6.2+), or Xcode `SWIFT_DEFAULT_ACTOR_ISOLATION`.
  [SDK] Xcode 27's new-app template sets it to `MainActor` and turns on Approachable Concurrency — so new
  app targets differ from packages and older targets. Read the build settings before advising.
- [docs] Approachable Concurrency (`SWIFT_APPROACHABLE_CONCURRENCY`) turns on `NonisolatedNonsendingByDefault`
  and `InferIsolatedConformances`; [SDK] both remain *upcoming* features (default only in Swift 7
  mode — `swiftc -print-supported-features`).
- [compiled] `Task.immediate` needs iOS 26; `Mutex` (Synchronization) iOS 18; `InlineArray` iOS 26;
  `Span` back-deploys (iOS 12.2).

**Frameworks**
- [compiled] MetricKit: iOS 27 adds `MetricManager` (async `metricReports` / `diagnosticReports` sequences,
  `logHandle(category:)`); [SDK] `MXMetricManager` is marked `API_TO_BE_DEPRECATED` ("Use MetricManager
  instead"). New code on 27+: `MetricManager`; keep `MXMetricManager` behind the fallback branch.
- [compiled] CryptoKit: `SHA3_256`, `SHA3_384`, `SHA3_512` are iOS 26+ (not 18).
- New frameworks in the iOS 27 SDK and everything else per framework: `frameworks.md`.

```swift
import MetricKit

@available(iOS 27.0, *)
func watchFieldMetrics() async {
    let manager = MetricManager()
    for await report in manager.metricReports {
        print(report)            // forward to your analytics pipeline instead
    }
}
```

## 4. Toolchain facts

- [SDK] Xcode 27.0 (27A266a) ships Swift 6.4 and Instruments 27; `xcrun xctrace list templates` includes
  **SwiftUI**, **Swift Concurrency**, **Animation Hitches**, **Foundation Models**, **Power Profiler**.
  Profiling workflow: `swiftui-performance.md`.
- Swift Testing ships in Xcode (`import Testing`); use it for new unit tests.

## 5. When this file goes stale

On the next Xcode: list `$R` again, diff against §1, and re-run `bash scripts/checks/ios.sh` in the
Ship repo — it compiles the [compiled] facts and inspects the [SDK] ones it names; [docs] facts
need a manual re-read of the source. A fact that stops verifying is fixed here first, then in the ledger (`maintainers/upstreams.yaml › decisions`).

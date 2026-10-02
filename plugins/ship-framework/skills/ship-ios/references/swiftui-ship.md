<!-- ship-reference
id: swiftui-ship
kind: ship-default
sources: iPhoneOS27.0.sdk SwiftUI/SwiftUICore .swiftinterface (Xcode 27.0 27A266a, availability machine-checked by scripts/checks/ios.sh); avdlee-swiftui@b24e68a (skills/swiftui-expert-skill — claims mapped, no text); avdlee-swift-concurrency@d577081 (skills/swift-concurrency — claims mapped, no text); https://developer.apple.com/documentation/swiftui (2026-09-23)
reviewed: 2026-09-24
-->
# SwiftUI — Ship's contracts

Ship's contracts for SwiftUI code: the design registry, platform-API-first, an architecture
default, and the rules Ship applies or overrides from the SwiftUI expert skills. The working patterns
(state, navigation, lists, forms, charts, accessibility, localization) are in
`swiftui-building.md`; Swift, concurrency, networking, and tests in `swift-practice.md`. Installed
Xcode 27's Apple guides add depth; `${CLAUDE_PLUGIN_ROOT}/skills/ship-ios/SKILL.md` routes.

## 1. Precedence when sources disagree

1. Platform facts and accessibility — the SDK's `@available`, App Review, Reduce Motion, VoiceOver.
2. Product decisions — `DECISIONS.md`, `design-model.yaml`, `design/components.yaml`.
3. Founder preferences (taste entries whose context matches).
4. Apple's HIG.
5. Expert skills: the installed SwiftUI and concurrency skills; the motion skill for motion.
6. Ship defaults (this file).
7. Your own inference — surface it, don't enforce it.

A skill update can change 4–6. It never rewrites 2–3.

## 2. The design registry in SwiftUI code

`Theme.swift` is generated from `design-model.yaml` (`design_model.py emit-swiftui`; the exact
command is in `PDC.md`). Default namespaces: `Theme.Colors`, `Theme.Typography`, `Theme.Radius`,
`Theme.Spacing`, `Theme.Motion` — a project may rename them in `emit.swiftui.namespaces`; use
whatever the generated file declares. Token names (e.g. `Spacing.md`) come from the project's model.

- **Never edit `Theme.swift`.** Change `design-model.yaml`, validate, re-emit.
- **No literals in views** for anything the model covers: no hex, no `Color(red:…)`, no raw point
  sizes for type, radius, or spacing. Missing token → add it to the model (tell the founder in one
  line), re-emit, then use it. Layout geometry that isn't a design choice (a 1pt hairline, 44pt hit
  area) is fine as a literal.
- **Apple's adaptive colors** are mapped in the model as `system.<name>`; they arrive through
  `Theme.Colors` like any token — don't bypass the theme to reach `Color(.label)`.
- **Components:** before building any UI element, read `design/components.yaml`.
  Hit → reuse that file (extend with a variant if needed). Miss → a reusable primitive gets its own
  file and a registry entry (`file:` must exist, `tokens:` semantic only). One-off → compose it
  locally in the screen. Third local copy of the same thing → ask once about promoting it.
- **Motion:** use `Theme.Motion.*`. Curves and springs are decided by the motion skill
  (`${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/SKILL.md`), not by SwiftUI defaults or an expert skill's examples.

```swift
// Registered primitive — every visual value comes from the generated theme.
struct StatCard: View {
    let title: LocalizedStringKey
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: Theme.Spacing.xs) {
            Text(title).font(Theme.Typography.caption).foregroundStyle(Theme.Colors.muted)
            Text(value).font(Theme.Typography.title).foregroundStyle(Theme.Colors.text)
        }
        .padding(Theme.Spacing.md)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.Colors.surface, in: .rect(cornerRadius: Theme.Radius.card))
    }
}
```

## 3. Platform API first (`${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` › Platform first)

Prefer the native API when it gives the behavior the product needs at the deployment target.
A custom build is fine with a stated reason — a required capability the API lacks, or a target
below its minimum — recorded in the PR or `DECISIONS.md`; reviewers ask for that reason instead of
rejecting on sight. Versions below are compile-probed against the iOS 27 SDK by
`scripts/checks/ios.sh`; anything above the deployment target needs `if #available` and a fallback.

| Instead of hand-rolling… | Try first | iOS |
|---|---|---|
| `UIImpactFeedbackGenerator` calls in views | `.sensoryFeedback(_:trigger:)` | 17 |
| `GeometryReader` just to size a fraction of the container | `.containerRelativeFrame` | 17 |
| Animated SF Symbols by hand | `.symbolEffect` | 17 |
| Keyboard dismissal gestures | `.scrollDismissesKeyboard` | 16 |
| Custom half-sheets | `.presentationDetents` · `.presentationSizing` | 16 · 18 |
| Keyboard focus juggling | `@FocusState` + `.focused` | 15 |
| Hiding bars by hand | `.toolbarVisibility` | 18 |
| Image-based gradients | `MeshGradient` | 18 |
| `UIVisualEffectView` blur | `Material` (content) · `.glassEffect` (controls, product decision) | 15 · 26 |
| Blank "no items" screens | `ContentUnavailableView` | 17 |
| Search fields | `.searchable` | 15 |
| `UIActivityViewController` wrappers for plain sharing | `ShareLink` | 16 |
| Photo picker wrappers | `PhotosPicker` | 16 |
| Custom paywall for a standard subscription offer | `SubscriptionStoreView` / `ProductView` | 17 |
| Pull-to-refresh gestures | `.refreshable` | 15 |
| Hand-drawn skeleton placeholders | `.redacted(reason: .placeholder)` | 14 |
| Offset-tracking scroll code | `ScrollPosition` · `.onScrollGeometryChange` · `.defaultScrollAnchor` | 18 · 18 · 17 |
| Hero transitions by hand | `.navigationTransition(.zoom(…))` + `.matchedTransitionSource` | 18 |
| Bottom bars floating over scroll content | `.safeAreaBar` | 26 |
| `WKWebView` wrappers | `WebView` (import WebKit) | 26 |
| Drag-to-reorder outside `List` | `.reorderable()` + `.reorderContainer` | 27 |
| Swipe actions outside `List` | `.swipeActionsContainer()` | 27 |
| "Discard changes?" alerts on sheet swipe | `.dismissalConfirmationDialog` | 27 |

Not equivalents — keep the custom path when you need these:
- `.redacted` masks content as a static skeleton; it doesn't animate. A shimmer is a separate
  motion decision (the motion skill), layered on top if the product wants one.
- `ShareLink` covers sharing items. `UIActivityViewController` is still the tool when you need
  excluded activity types, custom activities, or a completion handler.
- Store views cover standard offers; a paywall with product-specific flows or layout can stay custom.
- `.containerRelativeFrame` sizes against the nearest eligible container (scroll view, navigation
  stack, window…), not the immediate parent — use `GeometryReader`/`onGeometryChange` when you
  need the parent's size.

## 4. Architecture default — MV + Router

**Status:** Ship default recommendation (proposed as Q13, not founder-confirmed). A product
decision in `DECISIONS.md` overrides it; so does the architecture the codebase already uses —
detect it first (ViewModels, TCA stores, coordinators) and follow it. Don't mix patterns within
one feature. The SwiftUI expert skill is deliberately architecture-neutral, so this is Ship's call.

- Views own view state with `@State`; shared app state lives in `@Observable` models injected
  with `.environment`. No ViewModel per screen unless the screen's logic needs unit tests the
  model can't host.
- Business logic lives outside `body`, in models or services that tests can reach.
- One `Router` per navigation stack holds the path; views ask it to navigate.

```swift
enum Route: Hashable { case detail(id: UUID), settings }

@Observable @MainActor
final class Router {
    var path: [Route] = []
    func open(_ route: Route) { path.append(route) }
    func popToRoot() { path.removeAll() }
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            List { Button("Settings") { router.open(.settings) } }
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .detail(let id): Text(id.uuidString)
                    case .settings: Text("Settings")
                    }
                }
        }
        .environment(router)
    }
}
```

## 5. What Ship takes from the SwiftUI expert skills

The skills are a dependency, not a copy. Ship's side, per rule (full claim map in the Ship
repository's `maintainers/audit/`):

- **Enforced at a Ship decision point** (Eye/Crit review, `/shipmate build`): `@State` is `private`;
  `@Binding` only when the child writes; stable `ForEach` identity (no indices/offsets, no
  `UUID()` per render); `.animation(_:value:)` always has `value:`; version-specific APIs gated with
  `#available` + fallback; native API over UIKit bridging; hard-deprecated APIs replaced,
  soft-deprecated ones flagged not rewritten during feature work; performance findings are
  suggestions unless a trace backs them; Liquid Glass only when requested.
- **Override (Ship differs, on purpose):**
  - *Motion values* — the motion skill (the founder-designated authority) sets springs and curves;
    the expert skill's example springs (e.g. damping 0.7 on interactive elements) are not Ship's values.
  - *Visual values* — tokens come from the registry, never from examples in any skill.
  - *Architecture* — the expert skill is neutral; Ship recommends MV + Router (§4) as an overridable default.
  - *"Requested" for Liquid Glass* means recorded in `DECISIONS.md` / the design model, not a
    passing remark.
- **Ship's baseline, Apple's depth:** state and environment, view composition, lists, scroll,
  focus, layout, sheets/navigation, charts, localization, previews, and Swift Concurrency have a
  Ship baseline (`swiftui-building.md`, `swift-practice.md`); Xcode 27's bundled SwiftUI guides go
  deeper. A skill the builder installed on their own ranks above a **Ship** default, never above an
  **Apple** fact. Toolbars: Apple's toolbar guide (`SwiftUI-New-Toolbar-Features`, `ios-27.md` §1);
  traces: `swiftui-performance.md` §4.
- **Corrected (platform fact, runtime-verified 2026-09-23, Swift 6.4):** The concurrency
  expert skill (`d577081`, still upstream HEAD) says in its SKILL.md tool table that `withTaskGroup`
  "cancels children on scope exit". It doesn't: a group body that **returns normally waits for
  the remaining children and does not cancel them**; throwing out of the body cancels the rest,
  then waits. For a race or timeout, take the first result and call `group.cancelAll()`
  ([TaskGroup](https://docs.swift.org/latest/documentation/swift/taskgroup/)). The skill's own
  `references/tasks.md` agrees with this; only the table row is wrong. `async let` left unawaited
  *is* cancelled at scope exit — that claim is right.

If the skill isn't installed, the enforced rules above and Ship's guides still apply; Xcode 27's
Apple skills and Apple's docs cover the rest (`${CLAUDE_PLUGIN_ROOT}/skills/ship-ios/references/ios-27.md`).

## 6. Swift road signs

- Format with `FormatStyle` (`.formatted(…)`, `Text(date, format:)`); never build a `DateFormatter`
  in `body`.
- New async work uses structured concurrency; no new `DispatchQueue` code. Tie work to a view with
  `.task` / `.task(id:)` so it's cancelled with the view or when the id changes.
- Cancellation is a request, not a stop: work that ignores it — or a callback API behind a
  continuation — can still finish and write a stale result over a newer one. Keep `.task(id:)` for
  the lifecycle, **and** before committing a result check `Task.isCancelled` (or that the
  request/id still matches the current one). Wrap callback APIs with
  `withTaskCancellationHandler` so cancellation reaches them. Don't swallow `CancellationError`
  and then update state.
- Decode evolving server payloads defensively: `decodeIfPresent` with defaults for optional
  fields; don't let one bad element fail a whole feed.
- Typed `throws(…)` only for a closed error domain; plain `throws` otherwise.
- New tests use Swift Testing (`@Test`, `#expect`, `#require`, `confirmation`); keep XCTest where
  it already lives (UI tests, performance tests).
- Secrets go in the Keychain, never `UserDefaults` or the bundle.

## 7. UIKit bridging signs

- Bridge only what SwiftUI lacks; check §3 first.
- Delegates go through a `Coordinator`; `updateUIView` must be cheap and idempotent (compare before
  setting).
- Size bridged views with `sizeThatFits(_:uiView:context:)`, not frame guesses.
- Collection/table cells: `UIHostingConfiguration`.
- Modernizing an old UIKit app (scenes, `UIScreen.main`, orientation): Xcode 27 skill
  `uikit-app-modernization`.

```swift
import PDFKit

/// A UIKit view in SwiftUI: create once, update idempotently, delegate through the Coordinator.
struct PDFReader: UIViewRepresentable {
    let document: PDFDocument?
    @Binding var pageIndex: Int

    func makeUIView(context: Context) -> PDFView {
        let view = PDFView()
        view.autoScales = true
        NotificationCenter.default.addObserver(context.coordinator, selector: #selector(Coordinator.pageChanged(_:)),
                                               name: .PDFViewPageChanged, object: view)
        return view
    }

    func updateUIView(_ view: PDFView, context: Context) {
        context.coordinator.parent = self
        if view.document !== document { view.document = document }            // compare before setting
        if let page = document?.page(at: pageIndex), view.currentPage !== page { view.go(to: page) }
    }

    func makeCoordinator() -> Coordinator { Coordinator(parent: self) }

    final class Coordinator: NSObject {
        var parent: PDFReader
        init(parent: PDFReader) { self.parent = parent }
        @MainActor @objc func pageChanged(_ note: Notification) {
            guard let view = note.object as? PDFView, let page = view.currentPage,
                  let index = view.document?.index(for: page), index != parent.pageIndex else { return }
            parent.pageIndex = index                                           // UIKit → SwiftUI
        }
    }
}
```

## 8. Review checklist (Eye / Crit, iOS)

- [ ] Every color, font, radius, spacing, and animation value comes from the generated theme.
- [ ] `Theme.swift` unchanged by hand; `design-model.yaml` changed instead.
- [ ] New reusable UI is registered in `design/components.yaml` with an existing `file:`.
- [ ] Nothing in §3's left column was hand-built without a stated reason (a needed capability the
      API lacks, or the deployment target); ask for the reason before flagging it.
- [ ] Async results are committed only if the work wasn't cancelled / the request is still current.
- [ ] APIs newer than the deployment target are gated and have a fallback.
- [ ] Liquid Glass appears only where a product decision says so, on controls/navigation only.
- [ ] Architecture matches the project's existing pattern (or MV + Router for new code).
- [ ] The correctness items in §5 hold.

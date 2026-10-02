<!-- ship-reference
id: ios-swiftui-building
kind: mixed
sources: xcode-bundled-skills@27A266a swiftui-specialist-ref-environment (closures in custom environment keys; 2026-09-28); iPhoneOS27.0.sdk SwiftUI / SwiftUICore / Charts / XCTest interfaces (Xcode 27.0 27A266a — every example type-checks via scripts/checks/ios.sh at an iOS 18 target, Swift 6, both isolation defaults; the load-state and cancellation rule runs on the host via scripts/checks/ios_runtime); https://developer.apple.com/documentation/swiftui ; https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app ; https://developer.apple.com/documentation/swiftui/navigationstack ; https://developer.apple.com/documentation/charts ; https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views ; https://developer.apple.com/documentation/accessibility/supporting-voiceover-in-your-app ; https://developer.apple.com/documentation/xcode/localization ; https://developer.apple.com/documentation/xcode/previewing-your-apps-interface-in-xcode (all checked 2026-09-24). Written for Ship from Apple's docs and the SDK; no third-party text.
reviewed: 2026-09-24
-->
# Building SwiftUI screens — the working patterns

Ship's baseline for everyday SwiftUI work. `swiftui-ship.md` (registry, API-first, architecture)
applies on top. An installed `swiftui-expert-skill` adds depth and outranks the **Ship** defaults
here; **Apple** facts outrank both. It isn't required. Motion values: the motion skill. Tokens in
examples: `Theme.*`.

## 1. State and data flow

| The value | Owned by | Declared as |
|---|---|---|
| View-local UI state (toggle, draft text, selection) | the view | `@State private var` |
| A reference model the view creates and owns | the view | `@State private var model = Model()` (`@Observable` class) |
| A model passed in that the child edits | the parent | `@Bindable var model` (child) |
| A value a child must write back | the parent | `@Binding var value` — only if it writes |
| App-wide or subtree-wide services/models | the app/root | `.environment(model)` + `@Environment(Model.self)` |
| Custom environment values (plain values, never closures) | any ancestor | `@Entry var` in `extension EnvironmentValues`. For an action, a struct holding the data with a method or `callAsFunction`: closures can't be compared, so every view that reads one updates on any change |
| Tiny preferences | UserDefaults | `@AppStorage("key")` |
| Per-window UI state to restore after relaunch | the scene | `@SceneStorage("key")` |

- `@Observable` tracks per property read in `body`; read in the smallest view that shows it
  (`swiftui-performance.md` §3). Don't create an `@Observable` in `init` of a view without `@State`
  — it's recreated on every parent update.
- **Identity is lifetime:** a view's position in the tree (or `.id(_:)`) decides when `@State`
  resets. `if/else` branches are different views; changing `.id` on purpose resets state.
- **Load data with `.task(id:)`** and model it as states, not flags — one enum, one switch:

```swift
enum Loadable<Value> {
    case loading, empty, loaded(Value), failed(String)
}

@Observable @MainActor
final class TripsModel {
    private(set) var state: Loadable<[String]> = .loading
    func load(filter: String) async {
        state = .loading
        do {
            try await Task.sleep(for: .milliseconds(200))            // your fetch here
            let rows = ["Lisbon", "Kyoto"].filter { filter.isEmpty || $0.localizedStandardContains(filter) }
            if Task.isCancelled { return }                             // a newer filter replaced us
            state = rows.isEmpty ? .empty : .loaded(rows)
        } catch is CancellationError {
            return
        } catch {
            state = .failed("Couldn't load trips.")
        }
    }
}

struct TripsScreen: View {
    @State private var model = TripsModel()
    @State private var query = ""

    var body: some View {
        Group {
            switch model.state {
            case .loading: ProgressView()
            case .empty: ContentUnavailableView.search(text: query)
            case .loaded(let rows): List(rows, id: \.self) { Text($0) }
            case .failed(let message):
                ContentUnavailableView {
                    Label(message, systemImage: "wifi.exclamationmark")
                } actions: {
                    Button("Try Again") { Task { await model.load(filter: query) } }
                }
            }
        }
        .searchable(text: $query)
        .task(id: query) { await model.load(filter: query) }   // cancels the previous load per keystroke
    }
}
```

## 2. Navigation and presentation

- **Stacks:** typed path + one router per stack (`swiftui-ship.md` §4). `navigationDestination(for:)`
  sits on the stack's root content, once per type — not inside lazy rows.
- **iPad / wide windows:** `NavigationSplitView` with a selection binding (sidebar → content →
  detail); on iPhone it collapses to a stack automatically. Or `.tabViewStyle(.sidebarAdaptable)`.
- **Restore navigation:** encode the path (`[Route]` where `Route: Codable`, or
  `NavigationPath.codable`) into `@SceneStorage` and decode on launch; drop routes whose data no
  longer exists.
- **Sheets:** drive them with an optional item (`.sheet(item: $editing)`), not a Bool plus a
  separate value. One enum for all sheets on a screen avoids stacked-sheet bugs. Dismiss from
  inside with `@Environment(\.dismiss)`.
- **Unsaved edits:** `.interactiveDismissDisabled(hasChanges)` (15+); on 27, `.dismissalConfirmationDialog`
  (`swiftui-ship.md` §3).
- **Popovers** become sheets on iPhone; keep them as popovers with
  `.presentationCompactAdaptation(.popover)` only for small content. `.inspector` (17) for iPad
  side panels.
- **Alerts / dialogs:** item-binding forms (`.alert(_:item:)`, `.confirmationDialog(_:item:)`)
  compile from iOS 15 with Xcode 27 (`ios-27.md` §3). Destructive buttons use `role: .destructive`.

```swift
enum Sheet: Identifiable {
    case newTrip, editTrip(id: UUID)
    var id: String { switch self { case .newTrip: "new"; case .editTrip(let id): id.uuidString } }
}

struct TripsHome: View {
    @State private var sheet: Sheet?
    @SceneStorage("tripsPath") private var savedPath: Data?
    @State private var path: [UUID] = []

    var body: some View {
        NavigationStack(path: $path) {
            List { Button("New trip") { sheet = .newTrip } }
                .navigationDestination(for: UUID.self) { id in Text(id.uuidString) }
        }
        .sheet(item: $sheet) { sheet in
            switch sheet {
            case .newTrip: Text("New trip form")
            case .editTrip(let id): Text("Edit \(id.uuidString)")
            }
        }
        .onChange(of: path) { _, new in savedPath = try? JSONEncoder().encode(new) }
        .onAppear {
            if let data = savedPath, let restored = try? JSONDecoder().decode([UUID].self, from: data) { path = restored }
        }
    }
}
```

## 3. Lists, search, and long content

- `List` for rows (selection, swipe actions, edit mode, accessibility for free); `LazyVStack` in a
  `ScrollView` for card layouts. Both need stable ids (`swiftui-ship.md` §5).
- Row actions: `.swipeActions` (with a full-swipe default only for reversible actions),
  `.contextMenu` with the same actions, `.onDelete`/`.onMove` in edit mode.
- **Pagination:** load the next page when the last few rows appear (`.onAppear` on a row near the
  end, or a sentinel row), guard against duplicate loads, show a footer spinner / retry.
- **Search:** `.searchable(text:)` + `.task(id: query)` gives cancellation per keystroke for free
  (§1); add `.searchScopes` for categories and `.searchSuggestions` for completions. Debounce
  network search with `try await Task.sleep` at the top of the task.
- `.refreshable` awaits your async reload — the spinner stays until it returns.
- Programmatic scrolling: `ScrollPosition` (18) / `.scrollPosition(id:)` (17); `ScrollViewReader`
  below 17.

## 4. Forms and input

- `Form` + `Section` for settings and data entry; `LabeledContent` for read-only rows.
- Give every field the right keyboard and autofill: `.keyboardType`, `.textContentType`
  (`.emailAddress`, `.username`, `.password`, `.newPassword`, `.oneTimeCode`, `.postalCode`),
  `.textInputAutocapitalization`, `.autocorrectionDisabled()` for codes and emails.
- **Focus:** `@FocusState` over an enum of fields; `.onSubmit` moves to the next field;
  `.submitLabel(.next / .done)`. Focus the first field when a creation form opens.
- **Validation:** validate as the person leaves a field and on submit, not on every keystroke;
  show the message under the field, in words that say how to fix it; keep Save disabled until
  valid only when the reason is visible. Numeric input: `TextField(value:format:)`.
- Don't lose input: drafts survive rotation, backgrounding, and a failed save
  (`hardening-guide.md`).

```swift
struct SignUpForm: View {
    enum Field: Hashable { case email, password }
    @State private var email = ""
    @State private var password = ""
    @State private var touched: Set<Field> = []
    @FocusState private var focus: Field?

    static func emailProblem(_ s: String) -> String? {
        let t = s.trimmingCharacters(in: .whitespaces)
        if t.isEmpty { return "Enter your email." }
        return t.contains("@") && t.split(separator: "@").count == 2 ? nil : "Use an address like name@example.com."
    }
    static func passwordProblem(_ s: String) -> String? { s.count >= 8 ? nil : "Use at least 8 characters." }

    var body: some View {
        Form {
            Section {
                LabeledContent("Email") {   // a visible label; the prompt is only an example
                    TextField("Email", text: $email, prompt: Text("name@example.com"))
                        .textContentType(.emailAddress).keyboardType(.emailAddress)
                        .textInputAutocapitalization(.never).autocorrectionDisabled()
                        .focused($focus, equals: .email).submitLabel(.next)
                        .onSubmit { touched.insert(.email); focus = .password }
                }
                if touched.contains(.email), let problem = Self.emailProblem(email) {
                    Text(problem).font(Theme.Typography.caption).foregroundStyle(.red)
                }
                LabeledContent("Password") {
                    SecureField("Password", text: $password, prompt: Text("8 or more characters"))
                        .textContentType(.newPassword).focused($focus, equals: .password).submitLabel(.done)
                        .onSubmit { touched.insert(.password) }
                }
                if touched.contains(.password), let problem = Self.passwordProblem(password) {
                    Text(problem).font(Theme.Typography.caption).foregroundStyle(.red)
                }
            }
        }
        .onChange(of: focus) { old, _ in if let old { touched.insert(old) } }   // validate on leaving a field
        .onAppear { focus = .email }
    }
}
```

(`.red` stands in for the registry's error color — use `Theme.Colors.<error token>` in a project.)

## 5. Layout

- Stacks + `Spacer` + `.frame(maxWidth: .infinity, alignment:)` for most screens. `Grid` (16) for
  aligned rows and columns; `ViewThatFits` (16) to pick the first layout that fits (e.g. horizontal
  buttons that wrap to vertical); `AnyLayout` to switch layouts without losing state
  (`hig-ios.md` §3 example); the `Layout` protocol only for genuinely custom arrangements.
- Size decisions come from the container: `horizontalSizeClass`, `.containerRelativeFrame`,
  `.onGeometryChange` — not `UIScreen` or device checks.
- Pin things to edges with `.safeAreaInset(edge:)` (keeps scroll content clear) rather than a
  `ZStack` overlay; backgrounds extend with `.ignoresSafeArea` (decoration only).
- `layoutPriority` decides which sibling truncates first; `.fixedSize(horizontal: false, vertical: true)`
  for text that must wrap fully.

## 6. Gestures

- Prefer controls (`Button`, `Toggle`, `.swipeActions`, `.contextMenu`) — they carry
  accessibility and haptics. A custom gesture always has a visible alternative (`hig-ios.md` §5).
- `DragGesture` in a `ScrollView` fights the scroll: use `.simultaneousGesture` only when both
  should run; `.highPriorityGesture` to win; set `minimumDistance` so taps still work.
- `@GestureState` for in-flight values (resets automatically when the gesture ends or cancels);
  commit the final value in `.onEnded`. `MagnifyGesture` / `RotateGesture` (17) replace the old names.
- Springs and velocity hand-off: the motion skill (`fluid-interfaces`).

## 7. Charts

- **Ship:** one question per chart; the title says the answer ("Steps are up 12% this week").
  Colors from the registry; don't rely on color alone — label series or use symbols.
- Marks: `BarMark`, `LineMark`, `AreaMark`, `PointMark`, `RuleMark` (thresholds), `SectorMark` (17,
  pie/donut — only for a few parts of a whole). Series via `foregroundStyle(by:)`.
- Axes: `.chartYScale(domain:)` to start at zero for bars; format axis labels with `FormatStyle`.
- Interaction (17): `.chartXSelection(value:)` + a `RuleMark` annotation; long ranges scroll with
  `.chartScrollableAxes(.horizontal)` + `.chartXVisibleDomain(length:)`. Large data (18):
  vectorized `LinePlot`/`BarPlot`/`PointPlot`.
- Accessibility: Charts generates an audio graph and element descriptions; add
  `.accessibilityLabel`/`.accessibilityValue` on marks when the defaults read poorly.

```swift
import Charts

struct DailySteps: Identifiable { let id = UUID(); let day: Date; let steps: Int }

struct StepsChart: View {
    let data: [DailySteps]
    @State private var selected: Date?

    var body: some View {
        Chart(data) { point in
            BarMark(x: .value("Day", point.day, unit: .day), y: .value("Steps", point.steps))
                .accessibilityValue("\(point.steps) steps")
            if let selected, Calendar.current.isDate(selected, inSameDayAs: point.day) {
                RuleMark(x: .value("Selected", point.day, unit: .day))
                    .annotation(position: .top) { Text(point.steps, format: .number).font(Theme.Typography.caption) }
            }
        }
        .chartXSelection(value: $selected)
        .chartYScale(domain: 0...(max(10_000, data.map(\.steps).max() ?? 0)))
        .frame(height: 220)
    }
}
```

## 8. Liquid Glass on custom views (iOS 26)

- System bars, tab bars, toolbars, sheets, and standard controls adopt Liquid Glass automatically
  when built with the iOS 26+ SDK — check them before adding anything.
- Toolbar items in one `ToolbarItemGroup` share a glass capsule; `ToolbarSpacer(.fixed)` starts a new
  one. A count badge goes on the button inside the item (`.badge(n)`): `ToolbarItem` has no `badge`.
- Custom glass only where a product decision says so (`swiftui-ship.md` §5), on controls and
  navigation, never content: `.glassEffect(_:in:)` (`.regular`, `.clear`, `.interactive()`,
  `.tint(_:)`), buttons with `.buttonStyle(.glass)` / `.glassProminent`.
- Several glass shapes near each other go in one `GlassEffectContainer` (they blend and morph);
  `glassEffectID(_:in:)` with a namespace morphs a shape between states.
- Gate with `#available(iOS 26, *)` and fall back to a `Material`. Reduce Transparency and
  Increase Contrast adjust system glass automatically — check custom glass with both on.

```swift
struct MapControls: View {
    var body: some View {
        if #available(iOS 26.0, *) {
            GlassEffectContainer(spacing: Theme.Spacing.sm) {
                HStack(spacing: Theme.Spacing.sm) {
                    Button("Locate", systemImage: "location") { }.buttonStyle(.glass)
                    Button("Layers", systemImage: "square.3.layers.3d") { }.buttonStyle(.glass)
                }
            }
        } else {
            HStack(spacing: Theme.Spacing.sm) {
                Button("Locate", systemImage: "location") { }
                Button("Layers", systemImage: "square.3.layers.3d") { }
            }
            .padding(Theme.Spacing.sm)
            .background(.regularMaterial, in: .capsule)
        }
    }
}
```

## 9. Accessibility in code

- **Labels:** icon-only buttons use `Button("Label", systemImage:)` + `.labelStyle(.iconOnly)` so
  VoiceOver reads the label; images that carry meaning get `.accessibilityLabel`; decorative ones
  `Image(decorative:)` / `.accessibilityHidden(true)`.
- **Grouping:** `.accessibilityElement(children: .combine)` for a card read as one item;
  `.ignore` + your own label when the combined reading is clumsy. Headings: `.accessibilityAddTraits(.isHeader)`.
- **Custom controls:** `.accessibilityRepresentation { Slider(…) }` or
  `.accessibilityAdjustableAction` + `.accessibilityValue`; extra actions with `.accessibilityActions`
  (e.g. swipe actions reachable without swiping).
- **Focus and announcements:** `@AccessibilityFocusState` to move VoiceOver after an action;
  `AccessibilityNotification.Announcement(…).post()` (17) for results that don't move focus.
  Rotors (`.accessibilityRotor`) for long lists of headings/links.
- **Settings to honour:** Dynamic Type (`@ScaledMetric` for custom sizes), `accessibilityReduceMotion`
  (motion skill), `accessibilityReduceTransparency`, `colorSchemeContrast`, Bold Text, Differentiate
  Without Color. Assistive Access: Xcode 27 `AdditionalDocumentation/Implementing-Assistive-Access-in-iOS.md`.
- **Automated check (iOS 17):** `try app.performAccessibilityAudit()` in a UI test catches missing
  labels, small hit areas, contrast, and clipped Dynamic Type; VoiceOver on a device is still the
  real test.

## 10. Localization

- Use a **String Catalog** (`Localizable.xcstrings`); Xcode extracts `Text("…")`, `String(localized:)`,
  and `LocalizedStringResource` literals on build. Plurals and device variations live in the
  catalog ("Vary by Plural"), not in code.
- `Text("key")` localizes; `Text(verbatim:)` / `Text(someString)` from a variable does not. Pass
  `LocalizedStringResource` into code outside views (App Intents, widgets, notifications, models).
- Never concatenate sentences; interpolate (`Text("\(count) photos")` → catalog variations).
  Inflection: `^[\(count) photo](inflect: true)` in supported languages.
- Format with `FormatStyle` (dates, numbers, currency, measurements, lists, person names) — it
  follows the person's locale and calendar.
- Layout: leading/trailing, never left/right; directional SF Symbols flip automatically; test
  right-to-left and a double-length pseudolanguage (scheme › Options › App Language).
- Export for translators with Product › Export Localizations (XLIFF); review screenshots per
  language before release.

## 11. Previews

- `#Preview` for every screen state that matters: loading, empty, error, long text, a large
  Dynamic Type size (`.environment(\.dynamicTypeSize, .accessibility3)`), dark mode.
- `@Previewable @State` (Xcode 16+) for interactive previews without a wrapper view.
- SwiftData previews: an in-memory `ModelContainer` seeded with sample data
  (`data-sync.md` §7); network services get a fake conforming to the same protocol.
- Previews compile the app target — keep them free of real network calls and secrets.

```swift
#Preview("Reminder row — AX3 text, dark") {
    @Previewable @State var enabled = true
    Toggle("Daily reminder", isOn: $enabled)
        .padding(Theme.Spacing.md)
        .environment(\.dynamicTypeSize, .accessibility3)
        .preferredColorScheme(.dark)
}
```

## 12. Verify

| What | How | Level |
|---|---|---|
| Every load state renders (loading/empty/loaded/failed) | Previews + a UI test per state with a fake service | CI |
| Navigation restore | Background, kill from Xcode, relaunch — same screen | Simulator |
| Form: focus order, autofill, validation messages | UI test + manual pass with a password manager | Simulator + device |
| Search cancellation | Type fast; only the last query's results show | Simulator |
| Accessibility | `performAccessibilityAudit` in UI tests; VoiceOver pass; AX5 text | CI + **device** |
| Localization | Pseudolanguage + RTL run; screenshots per language | Simulator |
| Liquid Glass fallback | Run on iOS 18 and 26+ simulators; Reduce Transparency on | Simulator |

Apple: [SwiftUI](https://developer.apple.com/documentation/swiftui) ·
[Model data](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app) ·
[Charts](https://developer.apple.com/documentation/charts) ·
[Liquid Glass](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views) ·
[VoiceOver](https://developer.apple.com/documentation/accessibility/supporting-voiceover-in-your-app) ·
[Localization](https://developer.apple.com/documentation/xcode/localization) · Xcode 27:
`swiftui-specialist`, `AdditionalDocumentation/SwiftUI-Implementing-Liquid-Glass-Design.md`.
Deeper (optional): the installed `swiftui-expert-skill`.

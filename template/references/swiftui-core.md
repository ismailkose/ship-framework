# SwiftUI Core Implementation Reference

> **When to read:** Dev reads Sections 1-8 when building SwiftUI features.
> Arc reads Section 1 when planning navigation architecture.
> Eye reads Section 9 for SwiftUI review checklists.
>
> This covers implementation patterns every SwiftUI project needs — navigation,
> concurrency, Liquid Glass, animation, gestures, layout, architecture, and
> UIKit interop. For framework-specific APIs (HealthKit, StoreKit, etc.),
> see `references/frameworks/`.

---

## Triage

Pick the path that matches your task:

- **Building a new feature** → Read the relevant section(s), follow the code patterns
- **Fixing a bug** → Check Common Mistakes in the relevant section first
- **Reviewing code** → Use Section 9 (Review Checklists)

---

## Section 1: Navigation Implementation

### NavigationStack with NavigationPath

Use `NavigationStack` with a `NavigationPath` binding for programmatic, type-safe push navigation. Define routes as a `Hashable` enum and map them with `.navigationDestination(for:)`.

```swift
// Route enum — lightweight, Hashable
enum AppRoute: Hashable {
  case detail(Item)
  case settings
  case profile(User)
}

struct ContentView: View {
  @State private var path = NavigationPath()

  var body: some View {
    NavigationStack(path: $path) {
      List(items) { item in
        NavigationLink(value: AppRoute.detail(item)) {
          ItemRow(item: item)
        }
      }
      .navigationDestination(for: AppRoute.self) { route in
        switch route {
        case .detail(let item): DetailView(item: item)
        case .settings: SettingsView()
        case .profile(let user): ProfileView(user: user)
        }
      }
      .navigationTitle("Items")
    }
  }
}
```

**Programmatic navigation:**
```swift
path.append(AppRoute.detail(item))  // Push
path.removeLast()                    // Pop one
path = NavigationPath()              // Pop to root
```

### Router Pattern

For apps with complex navigation, use an `@Observable @MainActor` router that owns path + sheet state. Each tab gets its own router instance.

```swift
@Observable @MainActor
final class Router {
  var path = NavigationPath()
  var sheet: SheetDestination?

  func navigate(to route: AppRoute) {
    path.append(route)
  }

  func popToRoot() {
    path = NavigationPath()
  }

  func present(_ sheet: SheetDestination) {
    self.sheet = sheet
  }
}

// Inject per tab
TabView {
  Tab("Home", systemImage: "house", value: .home) {
    NavigationStack(path: $homeRouter.path) {
      HomeView()
        .withAppDestinations()
    }
    .environment(homeRouter)
  }
}
```

### NavigationSplitView (iPad Sidebar-Detail)

Falls back to stack navigation on iPhone automatically.

```swift
struct MasterDetailView: View {
  @State private var selectedItem: Item?

  var body: some View {
    NavigationSplitView {
      List(items, selection: $selectedItem) { item in
        NavigationLink(value: item) {
          ItemRow(item: item)
        }
      }
      .navigationTitle("Items")
    } detail: {
      if let item = selectedItem {
        ItemDetailView(item: item)
      } else {
        ContentUnavailableView("Select an Item",
          systemImage: "sidebar.leading")
      }
    }
  }
}
```

### Sheet Routing

Prefer `.sheet(item:)` over `.sheet(isPresented:)` when state represents a selected model.

```swift
// Correct: item-driven sheet
@State private var selectedItem: Item?

.sheet(item: $selectedItem) { item in
  EditItemSheet(item: item)
    .presentationSizing(.form)  // iOS 18+
}
```

**PresentationSizing values (iOS 18+):**
- `.automatic` — platform default
- `.page` — roughly paper size, informational content
- `.form` — narrower than page, form-style UI
- `.fitted` — sized by the content's ideal size

**Enum-driven sheet routing:**
```swift
enum SheetDestination: Identifiable {
  case edit(Item)
  case compose
  case settings

  var id: String {
    switch self {
    case .edit(let item): "edit-\(item.id)"
    case .compose: "compose"
    case .settings: "settings"
    }
  }
}
```

### Deep Links

```swift
@main
struct MyApp: App {
  @State private var router = Router()

  var body: some Scene {
    WindowGroup {
      ContentView()
        .environment(router)
        .onOpenURL { url in
          router.handle(url: url)
        }
        .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
          guard let url = activity.webpageURL else { return }
          router.handle(url: url)
        }
    }
  }
}
```

Universal links require an Apple App Site Association (AASA) file at `/.well-known/apple-app-site-association` and an Associated Domains entitlement (`applinks:example.com`).

**Common Mistakes — Navigation:**
```swift
// WRONG: Using deprecated NavigationView
NavigationView { content }

// CORRECT: NavigationStack or NavigationSplitView
NavigationStack { content }
```

```swift
// WRONG: Sharing one NavigationPath across tabs
@State var sharedPath = NavigationPath()
TabView {
  Tab("A") { NavigationStack(path: $sharedPath) { ViewA() } }
  Tab("B") { NavigationStack(path: $sharedPath) { ViewB() } }
}

// CORRECT: Each tab owns its path
@State var pathA = NavigationPath()
@State var pathB = NavigationPath()
```

```swift
// WRONG: .sheet(isPresented:) when you have a model
@State var showEdit = false
@State var selectedItem: Item?
.sheet(isPresented: $showEdit) { EditView(item: selectedItem!) }

// CORRECT: .sheet(item:) — binding handles both state
.sheet(item: $selectedItem) { item in EditView(item: item) }
```

---

## Section 2: Swift 6.2 Concurrency

### Default MainActor Isolation (SE-0466)

With the Xcode 26 "Approachable Concurrency" build setting (or `-default-isolation MainActor`), all code in a module runs on `@MainActor` by default unless explicitly opted out.

```swift
// With default MainActor isolation, these are implicitly @MainActor:
final class StickerLibrary {
  static let shared = StickerLibrary()  // safe — on MainActor
  var stickers: [Sticker] = []
}

// Conformances are also implicitly isolated:
extension StickerModel: Exportable {
  func export() { photoProcessor.exportAsPNG() }
}
```

**When to use:** Recommended for apps and scripts where most code is UI-bound.
**Not recommended:** For library targets that should remain actor-agnostic.

### @concurrent for Background Work

`@concurrent` ensures a function always runs on the concurrent thread pool, freeing the calling actor.

```swift
class PhotoProcessor {
  // Heavy work — explicitly runs off MainActor
  @concurrent
  static func extractSubject(from data: Data) async -> Sticker {
    // Expensive image processing on background thread pool
  }
}

// To move a function to background:
// 1. Ensure the containing type is nonisolated (or the function itself)
// 2. Add @concurrent
// 3. Add async if not already
// 4. Add await at call sites
nonisolated struct PhotoProcessor {
  @concurrent func process(data: Data) async -> ProcessedPhoto? { /* ... */ }
}
```

### nonisolated(nonsending) — Swift 6.2 Default

Nonisolated async functions now stay on the caller's actor by default instead of hopping to the global concurrent executor.

```swift
class PhotoProcessor {
  func extractSticker(data: Data) async -> Sticker? {
    // In Swift 6.2, this runs on the caller's actor (e.g., MainActor)
    // instead of hopping to a background thread
  }
}
```

### Task.immediate (SE-0472)

Starts executing synchronously on the current actor before any suspension point.

```swift
Task.immediate {
  await handleUserInput()  // begins without delay
}
```

### Isolated Conformances

```swift
// Conformance only usable on MainActor
extension StickerModel: @MainActor Exportable {
  func export() { photoProcessor.exportAsPNG() }
}
```

### Actor Isolation Rules

- All mutable shared state MUST be protected by an actor or global actor
- `@MainActor` for all UI-touching code — no exceptions
- Use `nonisolated` only for methods accessing immutable (`let`) properties or pure computations
- Use `@concurrent` to explicitly move work off the caller's actor
- Never use `nonisolated(unsafe)` unless you've proven internal synchronization and exhausted all other options
- Never add manual locks (`NSLock`, `DispatchSemaphore`) inside actors

### Sendable Rules

- Value types (structs, enums) are automatically `Sendable` when all stored properties are `Sendable`
- Actors are implicitly `Sendable`. `@MainActor` classes are implicitly `Sendable`
- Don't add redundant `Sendable` conformance
- Non-actor classes: must be `final` with all stored properties `let` and `Sendable`
- `@unchecked Sendable` is a last resort — document why the compiler cannot prove safety
- Use `@preconcurrency import` only for third-party libraries you cannot modify — plan to remove it

### Structured Concurrency Patterns

```swift
// async let — fixed number of concurrent operations
async let a = fetchA()
async let b = fetchB()
let result = try await (a, b)

// TaskGroup — dynamic number of concurrent operations
try await withThrowingTaskGroup(of: Item.self) { group in
  for id in ids {
    group.addTask { try await fetch(id) }
  }
  for try await item in group {
    process(item)
  }
}

// Task.immediate — latency-sensitive, starts synchronously
Task.immediate { await handleUserInput() }
```

### Synchronization Primitives

When actors don't fit (synchronous access, performance-critical, bridging C/ObjC):

- `Mutex<Value>` (iOS 18+, Synchronization module) — preferred lock for new code
- `OSAllocatedUnfairLock` (iOS 16+, os module) — for older iOS targets
- `Atomic<Value>` (iOS 18+, Synchronization module) — lock-free for simple counters/flags

**Key rule:** Never put locks inside actors (double synchronization). Never hold a lock across `await` (deadlock risk).

### Actor Reentrancy

Actors are reentrant — state can change across suspension points.

```swift
// WRONG: State may change during await
actor Counter {
  var count = 0
  func increment() async {
    let current = count
    await someWork()
    count = current + 1  // BUG: count may have changed
  }
}

// CORRECT: Mutate synchronously, no reentrancy risk
actor Counter {
  var count = 0
  func increment() { count += 1 }
}
```

**Common Mistakes — Concurrency:**

```swift
// WRONG: Blocking MainActor with heavy computation
@MainActor func processImage(_ data: Data) -> UIImage {
  // CPU-heavy work freezes UI
}

// CORRECT: Move to @concurrent
@concurrent static func processImage(_ data: Data) async -> UIImage {
  // Runs on background thread pool
}
```

```swift
// WRONG: Using GCD APIs — no data-race safety
DispatchQueue.global().async { doWork() }

// CORRECT: Use structured concurrency
Task { await doWork() }
```

```swift
// WRONG: DispatchSemaphore in async context — deadlock
let sem = DispatchSemaphore(value: 0)
Task { sem.signal() }
sem.wait()  // DEADLOCK

// CORRECT: Use async/await
let result = await doWork()
```

---

## Section 3: Liquid Glass Implementation (iOS 26+)

### Core API

```swift
// Basic glass effect with availability gate
if #available(iOS 26, *) {
  Text("Status")
    .padding()
    .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 16))
} else {
  Text("Status")
    .padding()
    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
}
```

**Glass struct:**
| Property | Purpose |
|----------|---------|
| `.regular` | Standard glass material |
| `.clear` | Clear variant (minimal tint) |
| `.identity` | No visual effect (pass-through) |
| `.tint(_:)` | Add a color tint for prominence |
| `.interactive(_:)` | React to touch and pointer interactions |

Chain them: `.regular.tint(.blue).interactive()`

### GlassEffectContainer

Wraps multiple glass views for shared rendering, blending, and morphing.

```swift
GlassEffectContainer(spacing: 24) {
  HStack(spacing: 24) {
    ForEach(tools) { tool in
      Image(systemName: tool.icon)
        .frame(width: 56, height: 56)
        .glassEffect(.regular.interactive())
    }
  }
}
```

The `spacing` controls when nearby glass shapes begin to blend. Match or exceed the interior layout spacing so shapes merge during animated transitions but remain separate at rest.

### Morphing Transitions

```swift
@State private var isExpanded = false
@Namespace private var ns

GlassEffectContainer(spacing: 40) {
  HStack(spacing: 40) {
    Image(systemName: "pencil")
      .frame(width: 80, height: 80)
      .glassEffect()
      .glassEffectID("pencil", in: ns)

    if isExpanded {
      Image(systemName: "eraser.fill")
        .frame(width: 80, height: 80)
        .glassEffect()
        .glassEffectID("eraser", in: ns)
    }
  }
}

Button("Toggle") {
  withAnimation { isExpanded.toggle() }
}
.buttonStyle(.glass)
```

**Transition types:**
- `.matchedGeometry` — default when within spacing
- `.materialize` — fade content + animate glass in/out
- `.identity` — no transition

### Glass Union

Merge multiple views into one glass shape:

```swift
@Namespace private var ns

GlassEffectContainer(spacing: 20) {
  HStack(spacing: 20) {
    ForEach(items.indices, id: \.self) { i in
      Image(systemName: items[i])
        .frame(width: 80, height: 80)
        .glassEffect()
        .glassEffectUnion(id: i < 2 ? "group1" : "group2", namespace: ns)
    }
  }
}
```

### Button Styles

```swift
Button("Action") { }
  .buttonStyle(.glass)           // standard

Button("Primary") { }
  .buttonStyle(.glassProminent)  // prominent
```

### Scroll Edge Effects & Background Extension

```swift
ScrollView { content }
  .scrollEdgeEffectStyle(.soft, for: .top)

content
  .backgroundExtensionEffect()  // extend behind sidebars/inspectors

.toolbar {
  ToolbarItem { Button("Edit") { } }
  ToolbarSpacer(.fixed)
  ToolbarItem { Button("Share") { } }
}
```

**Common Mistakes — Liquid Glass:**

```swift
// WRONG: Glass applied before layout modifiers (incorrect bounds)
Text("Label").glassEffect().padding()

// CORRECT: Glass after layout
Text("Label").padding().glassEffect()
```

```swift
// WRONG: Nested GlassEffectContainer (undefined rendering)
GlassEffectContainer {
  GlassEffectContainer { content.glassEffect() }
}

// CORRECT: Single container
GlassEffectContainer { content.glassEffect() }
```

```swift
// WRONG: Glass on everything
VStack {
  Text("Title").glassEffect()
  Text("Subtitle").glassEffect()
  Text("Body").glassEffect()
}

// CORRECT: Glass on primary interactive elements only
VStack {
  Text("Title").font(.title)
  Text("Subtitle").font(.subheadline)
  Text("Body")
}
.padding()
.glassEffect()
```

- `.interactive()` only on tappable/focusable elements — not decorative glass
- Always test with Reduce Transparency and Reduce Motion enabled
- Always gate with `if #available(iOS 26, *)`

---

## Section 4: SwiftUI Animation

### Spring Animations (Preferred)

SwiftUI defaults to spring animations. Use them unless you have a reason not to.

```swift
withAnimation(.spring(duration: 0.35, bounce: 0.2)) {
  isExpanded.toggle()
}

// Presets
.spring()                          // default
.spring(duration: 0.5, bounce: 0)  // critically damped (no overshoot)
.bouncy                            // playful
.snappy                            // quick, minimal bounce
.smooth                            // no bounce
```

### Transition Animations

```swift
if showDetail {
  DetailView()
    .transition(.move(edge: .trailing).combined(with: .opacity))
}
```

### matchedGeometryEffect

```swift
@Namespace private var animation

// Source
Image(systemName: "star")
  .matchedGeometryEffect(id: "star", in: animation)

// Destination (shown conditionally)
Image(systemName: "star.fill")
  .matchedGeometryEffect(id: "star", in: animation)
```

### Phase Animations (iOS 17+)

```swift
PhaseAnimator([false, true]) { phase in
  Image(systemName: "star")
    .scaleEffect(phase ? 1.2 : 1.0)
    .opacity(phase ? 1.0 : 0.7)
}
```

### Keyframe Animations (iOS 17+)

```swift
KeyframeAnimator(initialValue: AnimationValues()) { values in
  Image(systemName: "heart.fill")
    .scaleEffect(values.scale)
    .rotationEffect(values.rotation)
} keyframes: { _ in
  KeyframeTrack(\.scale) {
    SpringKeyframe(1.5, duration: 0.2)
    SpringKeyframe(1.0, duration: 0.3)
  }
  KeyframeTrack(\.rotation) {
    LinearKeyframe(.degrees(10), duration: 0.1)
    LinearKeyframe(.degrees(-10), duration: 0.1)
    LinearKeyframe(.zero, duration: 0.2)
  }
}
```

### Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

withAnimation(reduceMotion ? .none : .spring()) {
  // state change
}
```

**Rules:**
- Spring animations for all interactive transitions
- Match animation duration to the significance of the change (subtle = fast, major = slower)
- Always provide `.none` animation path for Reduce Motion
- Don't animate layout changes that cause content reflow
- Use `.animation(.default, value: property)` for implicit — prefer explicit `withAnimation`

---

## Section 5: Gestures

### Basic Gestures

```swift
// Tap
Image(systemName: "star")
  .onTapGesture { toggleFavorite() }

// Long press
Text("Hold me")
  .onLongPressGesture(minimumDuration: 0.5) { showMenu() }

// Drag
@GestureState private var dragOffset = CGSize.zero

Image("card")
  .offset(dragOffset)
  .gesture(
    DragGesture()
      .updating($dragOffset) { value, state, _ in
        state = value.translation
      }
      .onEnded { value in
        handleSwipe(value.translation)
      }
  )
```

### Gesture Composition

```swift
// Simultaneous — both active at once
let combined = rotateGesture.simultaneously(with: magnifyGesture)

// Sequenced — first then second
let longPressThenDrag = LongPressGesture()
  .sequenced(before: DragGesture())

// Exclusive — first match wins
let tapOrLongPress = tapGesture.exclusively(before: longPressGesture)
```

### MagnifyGesture (iOS 17+)

```swift
@State private var scale: CGFloat = 1.0

Image("photo")
  .scaleEffect(scale)
  .gesture(
    MagnifyGesture()
      .onChanged { value in scale = value.magnification }
      .onEnded { _ in
        withAnimation { scale = max(1.0, min(scale, 3.0)) }
      }
  )
```

### RotateGesture

```swift
@State private var angle: Angle = .zero

Image("dial")
  .rotationEffect(angle)
  .gesture(
    RotateGesture()
      .onChanged { value in angle = value.rotation }
  )
```

**Rules:**
- Always provide visual feedback during gesture (offset, scale, opacity change)
- Use `@GestureState` for transient gesture state — resets automatically on end
- Minimum 44pt touch target for gesture-interactive elements
- Don't override system gestures (edge swipes, bottom bar)
- Add haptic feedback at meaningful thresholds during continuous gestures

---

## Section 6: Layout & Components

### Layout Priority

```swift
HStack {
  Text("Title")
    .layoutPriority(1)  // gets space first
  Text("Long description that can be truncated...")
}
```

### ViewThatFits (iOS 16+)

```swift
ViewThatFits {
  HStack { label; description }  // try horizontal first
  VStack { label; description }  // fall back to vertical
}
```

### Grid (iOS 16+)

```swift
Grid(alignment: .leading) {
  GridRow {
    Text("Name")
    TextField("Enter name", text: $name)
  }
  GridRow {
    Text("Email")
    TextField("Enter email", text: $email)
  }
}
```

### Custom Layout (iOS 16+)

```swift
struct FlowLayout: Layout {
  var spacing: CGFloat = 8

  func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
    // Calculate total size
  }

  func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
    // Place each subview, wrapping to next line when needed
  }
}
```

### ContentUnavailableView (iOS 17+)

```swift
if items.isEmpty {
  ContentUnavailableView("No Results",
    systemImage: "magnifyingglass",
    description: Text("Try a different search term."))
}

// Search-specific
ContentUnavailableView.search(text: searchText)
```

### ScrollView Enhancements

```swift
// Scroll position (iOS 17+)
@State private var scrollPosition: ScrollPosition = .init()

ScrollView {
  LazyVStack { /* content */ }
}
.scrollPosition($scrollPosition)

// Scroll transitions (iOS 17+)
ScrollView(.horizontal) {
  LazyHStack {
    ForEach(items) { item in
      ItemCard(item: item)
        .scrollTransition { content, phase in
          content
            .opacity(phase.isIdentity ? 1 : 0.5)
            .scaleEffect(phase.isIdentity ? 1 : 0.8)
        }
    }
  }
}
```

---

## Section 7: Architecture Patterns

### @Observable (iOS 17+)

```swift
@Observable @MainActor
final class ViewModel {
  var items: [Item] = []
  var isLoading = false
  var errorMessage: String?

  func loadItems() async {
    isLoading = true
    defer { isLoading = false }
    do {
      items = try await ItemService.fetch()
    } catch {
      errorMessage = error.localizedDescription
    }
  }
}

// In view — use @State for ownership
struct ItemListView: View {
  @State private var viewModel = ViewModel()

  var body: some View {
    List(viewModel.items) { item in
      ItemRow(item: item)
    }
    .task { await viewModel.loadItems() }
  }
}
```

### Environment for Dependency Injection

```swift
@Observable @MainActor
final class AuthService {
  var currentUser: User?
  func signIn() async throws { /* ... */ }
}

extension EnvironmentValues {
  @Entry var authService = AuthService()
}

// Inject at root
ContentView()
  .environment(\.authService, authService)

// Consume in any descendant
@Environment(\.authService) private var auth
```

### Async Observation (SE-0475, Swift 6.2)

```swift
for await _ in Observations { model.count } {
  print("Count changed to \(model.count)")
}
```

---

## Section 8: UIKit Interop

### UIViewRepresentable

```swift
struct MapView: UIViewRepresentable {
  @Binding var region: MKCoordinateRegion

  func makeUIView(context: Context) -> MKMapView {
    let map = MKMapView()
    map.delegate = context.coordinator
    return map
  }

  func updateUIView(_ map: MKMapView, context: Context) {
    map.setRegion(region, animated: true)
  }

  func makeCoordinator() -> Coordinator { Coordinator(self) }

  class Coordinator: NSObject, MKMapViewDelegate {
    var parent: MapView
    init(_ parent: MapView) { self.parent = parent }
  }
}
```

### UIViewControllerRepresentable

```swift
struct ImagePicker: UIViewControllerRepresentable {
  @Binding var image: UIImage?
  @Environment(\.dismiss) private var dismiss

  func makeUIViewController(context: Context) -> UIImagePickerController {
    let picker = UIImagePickerController()
    picker.delegate = context.coordinator
    return picker
  }

  func updateUIViewController(_ controller: UIImagePickerController, context: Context) {}

  func makeCoordinator() -> Coordinator { Coordinator(self) }

  class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
    let parent: ImagePicker
    init(_ parent: ImagePicker) { self.parent = parent }

    func imagePickerController(_ picker: UIImagePickerController,
                               didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
      parent.image = info[.originalImage] as? UIImage
      parent.dismiss()
    }
  }
}
```

### Hosting SwiftUI in UIKit

```swift
let hostingController = UIHostingController(rootView: SwiftUIView())
addChild(hostingController)
view.addSubview(hostingController.view)
hostingController.view.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
  hostingController.view.topAnchor.constraint(equalTo: view.topAnchor),
  hostingController.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
  hostingController.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
  hostingController.view.trailingAnchor.constraint(equalTo: view.trailingAnchor),
])
hostingController.didMove(toParent: self)
```

**Rules:**
- Use `makeCoordinator()` for delegates — never store UIKit delegates in SwiftUI `@State`
- Update UIKit view in `updateUIView` based on binding changes — don't bypass the SwiftUI lifecycle
- Use `@Environment(\.dismiss)` in representables, not `presentingViewController?.dismiss`

---

## Section 9: Review Checklists

### Navigation
- [ ] `NavigationStack` used (not `NavigationView`)
- [ ] Each tab has its own `NavigationStack` with independent path
- [ ] Route enum is `Hashable` with stable identifiers
- [ ] `.navigationDestination(for:)` maps all route types
- [ ] `.sheet(item:)` preferred over `.sheet(isPresented:)`
- [ ] Sheets own their dismiss logic internally
- [ ] Router object is `@MainActor` and `@Observable`
- [ ] Deep link URLs parsed and validated before navigation
- [ ] Tab selection uses `Tab(value:)` with binding

### Concurrency
- [ ] All mutable shared state is actor-isolated
- [ ] No data races (no unprotected cross-isolation access)
- [ ] Tasks are cancelled when no longer needed
- [ ] No blocking calls on `@MainActor`
- [ ] No manual locks inside actors
- [ ] `Sendable` conformance is correct (no unjustified `@unchecked`)
- [ ] Actor reentrancy is handled (no state assumptions across awaits)
- [ ] `@preconcurrency` imports documented with removal plan
- [ ] Heavy work uses `@concurrent`, not `@MainActor`
- [ ] `.task` modifier used in SwiftUI instead of manual `Task` management
- [ ] No GCD APIs (`DispatchQueue`, `DispatchGroup`, `DispatchSemaphore`)

### Liquid Glass
- [ ] `if #available(iOS 26, *)` present with fallback UI
- [ ] Multiple glass views wrapped in `GlassEffectContainer`
- [ ] `.glassEffect()` applied after layout/appearance modifiers
- [ ] `.interactive()` used only where user interaction exists
- [ ] `glassEffectID` used with `@Namespace` for morphing
- [ ] Shapes, tints, and spacing uniform across related elements
- [ ] Glass effects limited in number; container used for grouping
- [ ] Tested with Reduce Transparency and Reduce Motion
- [ ] Standard `.glass` / `.glassProminent` used for buttons

### Animation
- [ ] Spring animations used for interactive transitions
- [ ] `@Environment(\.accessibilityReduceMotion)` checked
- [ ] Alternative `.none` animation provided for Reduce Motion
- [ ] No layout reflow during animation
- [ ] `withAnimation` used explicitly (not implicit `.animation`)

### Architecture
- [ ] `@Observable` used (not `ObservableObject` / `@Published`)
- [ ] `@State` owns `@Observable` instances (not `@StateObject`)
- [ ] View models are `@MainActor`
- [ ] `.task` used for async work on appear
- [ ] Environment used for dependency injection

---

_Source: SwiftUI documentation, Swift Evolution proposals, WWDC sessions · Condensed for Ship Framework agent reference_

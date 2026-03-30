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

**Sheet presentation shortcuts:**
- When `sheet(item:)` presents a view that takes the item as its only init parameter, use the shorthand: `.sheet(item: $selectedItem, content: EditItemSheet.init)` instead of a closure.
- Alert with a single dismiss-only OK button can omit the actions closure entirely: `.alert("Title", isPresented: $showAlert) { }`

**Navigation rules:**
- `navigationDestination(for:)` must be registered exactly once per data type in the navigation hierarchy. Duplicates cause undefined behavior — flag them.
- Never mix `navigationDestination(for:)` and the old `NavigationLink(destination:)` pattern in the same `NavigationStack`. This causes significant navigation bugs.

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

### iOS 26 Tab APIs

**Tab roles for specialized behavior:**

```swift
// Search tab — replaces tab bar with search field when active
Tab(role: .search) {
  SearchView()
}

// Regular tab with data
Tab("Feed", systemImage: "house", value: .home) {
  FeedView()
}
```

**Tab bar minimization (iPhone only):**

```swift
TabView(selection: $selectedTab) {
  // tabs
}
.tabBarMinimizeBehavior(.onScrollDown)  // minimize when scrolling down
```

`TabBarMinimizeBehavior` values: `.automatic`, `.onScrollDown`, `.onScrollUp`, `.never`

**Sidebar customization:**

```swift
TabView {
  TabSection("Main") {
    Tab("Home") { HomeView() }
    Tab("Search") { SearchView() }
  }
  .tabPlacement(.sidebarOnly)
}
.tabViewSidebarHeader { SidebarHeaderView() }
.tabViewSidebarFooter { SidebarFooterView() }
.tabViewBottomAccessory { NowPlayingBar() }
```

**`TabSection`** groups related tabs under a sidebar header.

**Tab selection binding:** When using `TabView(selection:)`, bind to an enum property, not an integer or string. Example: `Tab("Home", systemImage: "house", value: .home)`.

### PresentationSizing Fine-Tuning (iOS 18+)

```swift
.sheet(item: $selectedItem) { item in
  EditItemSheet(item: item)
    .presentationSizing(.fitted(horizontal: .flexible, vertical: .flexible))
}

// or sticky (grow but don't shrink)
.presentationSizing(.sticky(horizontal: .flexible, vertical: .flexible))
```

### Dismissal Confirmation (iOS 26+)

```swift
.sheet(item: $selectedItem) { item in
  EditItemSheet(item: item)
    .dismissalConfirmationDialog(
      "Discard changes?",
      shouldPresent: hasUnsavedChanges
    ) {
      Button("Discard", role: .destructive) { discardChanges() }
    }
}
```

**confirmationDialog placement:** Always attach `.confirmationDialog()` to the specific UI element that triggers it. On iOS 26, Liquid Glass animations morph from the source element — attaching to the wrong view breaks the transition animation.

**Common Mistakes — Navigation:**
```swift
// WRONG: Using deprecated NavigationView
NavigationView { content }

// CORRECT: NavigationStack or NavigationSplitView
NavigationStack { content }
```

```swift
// WRONG: Storing view instances in NavigationPath
@State var path = NavigationPath()
path.append(DetailView(item: item))  // WRONG: views aren't Hashable

// CORRECT: Store lightweight routes
enum Route: Hashable { case detail(Item) }
path.append(Route.detail(item))
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

```swift
// WRONG: Nesting @Observable routers or storing multiple routers
@Observable final class AppRouter {
  var homeRouter = RouterPath()  // WRONG: nested @Observable
}

// CORRECT: One router owns navigation for all features
@Observable final class AppRouter {
  var path = NavigationPath()
  var presentedSheet: SheetDestination?
}
// Inject once at app root, never nest
```

```swift
// WRONG: Using deprecated .tabItem { }
TabView {
  Text("Home").tabItem { Label("Home", systemImage: "house") }
}

// CORRECT: Use Tab(value:) with selection
@State var selectedTab: AppTab = .home
TabView(selection: $selectedTab) {
  Tab("Home", systemImage: "house", value: .home) { HomeView() }
}
```

```swift
// WRONG: Hard-coding sheet dimensions
.sheet(item: $selectedItem) { item in
  EditView(item: item)
    .frame(height: 400)  // brittle across devices
}

// CORRECT: Use presentationSizing(.form) or .fitted
.sheet(item: $selectedItem) { item in
  EditView(item: item)
    .presentationSizing(.form)
}
```

```swift
// WRONG: Scattered deep link handling across views
struct HomeView {
  .onOpenURL { url in router.handle(url) }
}
struct SettingsView {
  .onOpenURL { url in router.handle(url) }
}

// CORRECT: Handle deep links once at app root
@main struct MyApp: App {
  @State var router = Router()
  var body: some Scene {
    WindowGroup {
      ContentView()
        .environment(router)
        .onOpenURL { url in router.handle(url: url) }
    }
  }
}
```

```swift
// WRONG: Router not marked @MainActor
@Observable class Router { var path = NavigationPath() }

// CORRECT: Navigation always on MainActor
@Observable @MainActor final class Router {
  var path = NavigationPath()
  func navigate(to route: AppRoute) { path.append(route) }
}
```

### Toolbar Enhancements (iOS 26+)

- `toolbar(id:)` — creates a user-customizable toolbar with drag-to-reorder.
- `searchToolbarBehavior(.minimize)` — search appears as a button that expands on tap.
- `matchedTransitionSource(id:in:)` — smooth zoom transitions from toolbar items to destination views.
- `.largeSubtitle` placement — subtitle under large navigation title.
- `sharedBackgroundVisibility(.hidden)` — hides the shared glass background behind toolbar items.

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

### Scroll Edge Effects (Progressive Blur) & Background Extension

The scroll edge effect is the **progressive blur** that fades content as it scrolls
behind a bar or edge. This is a system-provided effect — do NOT build it manually.

```swift
// WRONG — don't hand-roll progressive blur
.overlay(alignment: .top) {
  LinearGradient(...)
    .blur(radius: 10)
    .frame(height: 40)
}

// WRONG — don't wrap UIVisualEffectView with gradient mask
UIViewRepresentable { UIVisualEffectView(effect: UIBlurEffect(...)) }

// CORRECT — one line, system progressive blur (iOS 26+)
ScrollView { content }
  .scrollEdgeEffectStyle(.soft, for: .top)
```

**Styles:**

| Style | Effect | When to use |
|-------|--------|-------------|
| `.automatic` | System decides (default) | Most scroll views — let the system handle it |
| `.soft` | Progressive blur fade | Chat UIs, feeds, any content scrolling behind a bar |
| `.hard` | Sharp cutoff with divider line | Settings lists, sidebars, structured content |

```swift
// Apply to specific edges
ScrollView { content }
  .scrollEdgeEffectStyle(.soft, for: .top)
  .scrollEdgeEffectStyle(.hard, for: .bottom)

// Hide edge effect entirely
ScrollView { content }
  .scrollEdgeEffectHidden(true, for: .bottom)

// Apply to all edges at once
ScrollView { content }
  .scrollEdgeEffectStyle(.hard, for: .all)
```

**UIKit equivalent** (for `UIViewRepresentable` or pure UIKit):

```swift
scrollView.topEdgeEffect.style = .soft      // progressive blur
scrollView.bottomEdgeEffect.style = .hard   // sharp divider
scrollView.leftEdgeEffect.isHidden = true   // disable for edge
```

**safeAreaBar** (iOS 26+) — custom bar that automatically extends scroll edge effects:

```swift
// WRONG — safeAreaInset doesn't extend the edge effect into the bar
ScrollView { content }
  .safeAreaInset(edge: .bottom) { MyToolbar() }

// CORRECT — safeAreaBar extends the progressive blur behind the bar
ScrollView { content }
  .safeAreaBar(edge: .bottom) { MyToolbar() }
```

**backgroundExtensionEffect** — extend content behind sidebars/inspectors:

```swift
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

### Symbol Effects (All 10 Types)

**Discrete effects — trigger with `value:`:**

```swift
// Bounce — scale pulse at discrete moment
Image(systemName: "bell.fill")
  .symbolEffect(.bounce, value: notificationCount)

// Wiggle — directional shake
Image(systemName: "arrow.left.arrow.right")
  .symbolEffect(.wiggle.left, value: swapCount)
```

**Indefinite effects — toggle with `isActive:`:**

```swift
// Pulse — steady opacity pulse
Image(systemName: "wifi")
  .symbolEffect(.pulse.byLayer, isActive: isConnecting)

// VariableColor — color cycling with options
Image(systemName: "speaker.wave.3.fill")
  .symbolEffect(
    .variableColor.cumulative.nonReversing.dimInactiveLayers,
    options: .repeating,
    isActive: isPlaying
  )

// Scale — grow/shrink effect
Image(systemName: "magnifyingglass")
  .symbolEffect(.scale.up, isActive: isHighlighted)

// Breathe — breathing animation
Image(systemName: "heart.fill")
  .symbolEffect(.breathe, isActive: isFavorite)

// Rotate — spinning animation
Image(systemName: "gear")
  .symbolEffect(.rotate.clockwise, isActive: isProcessing)

// Appear/Disappear — entry/exit effects
Image(systemName: "checkmark.circle.fill")
  .symbolEffect(.appear, isActive: showCheck)
```

**Content transitions:**

```swift
// Replace symbol with transition
Image(systemName: isMuted ? "speaker.slash" : "speaker.wave.3")
  .contentTransition(.symbolEffect(.replace.downUp))

// Magic replace (morphs between symbols)
Image(systemName: isPlaying ? "pause.fill" : "play.fill")
  .contentTransition(.symbolEffect(.replace.magic(fallback: .downUp)))
```

**Key options:**
- `.byLayer` vs `.wholeSymbol` — render scope
- `.repeating` vs `.nonRepeating` — repeat behavior
- `.speed(2.0)` — speed multiplier
- `.cumulative`, `.iterative` — variableColor chaining modes

### @Animatable Macro and @AnimatableIgnored (iOS 18+)

Auto-conform types to `VectorArithmetic` for smooth animations:

```swift
@Animatable
struct AnimatedValues {
  var scale: Double = 1.0
  var offset: CGSize = .zero

  @AnimatableIgnored
  var id: String  // ignored during animation
}
```

### withAnimation Completion Callbacks

```swift
// Detect when animation finishes
withAnimation(.spring(duration: 0.3)) {
  isExpanded.toggle()
} completion: {
  handleAnimationComplete()
}
```

### ContentTransition Types

```swift
// Numeric text animation
Text("\(count)")
  .contentTransition(.numericText())

// Symbol effect transition (already shown above)
.contentTransition(.symbolEffect(.replace.downUp))
```

### Navigation Zoom Transition (iOS 18+)

```swift
// On source view
Image("item")
  .matchedTransitionSource(id: "item", in: itemNamespace)

// On destination view
DetailView()
  .navigationTransition(.zoom(sourceID: "item", in: itemNamespace))
```

### PhaseAnimator with Custom Animation Curves

```swift
PhaseAnimator(phases) { phase in
  Image(systemName: "heart")
    .scaleEffect(phase.scale)
} animation: { phase in
  switch phase {
  case .loading: .easeIn(duration: 0.15)
  case .spinning: .linear(duration: 0.6)
  case .complete: .spring(duration: 0.3, bounce: 0.4)
  }
}
```

**Common Mistakes — Animation:**

```swift
// WRONG: withAnimation doesn't return value
let result = withAnimation { doSomething() }

// CORRECT: Use completion handler (iOS 18+)
withAnimation { doSomething() } completion: { print("done") }
```

```swift
// WRONG: Symbol effects without reduce motion
Image("icon").symbolEffect(.pulse, isActive: isLoading)

// CORRECT: Respect accessibility
Image("icon")
  .symbolEffect(.pulse, isActive: isLoading)
  .symbolEffectsRemoved(reduceMotion)
```

```swift
// WRONG: Animating core layout properties
withAnimation(.spring) {
  isExpanded.toggle()
  // if this changes the view tree, animation stutters
}

// CORRECT: Only animate visual properties
@State var scale = 1.0
withAnimation(.spring) {
  scale = isExpanded ? 1.2 : 1.0
}
```

```swift
// WRONG: Using @Animatable without understanding vector arithmetic
struct BadValues {
  @Animatable var color: Color  // NOT VectorArithmetic
}

// CORRECT: Only use @Animatable for numeric/geometric types
@Animatable
struct GoodValues {
  var scale: Double = 1.0
  var offset: CGSize = .zero
}
```

```swift
// WRONG: PhaseAnimator for one-time animations
@State var trigger = false
PhaseAnimator([0, 1]) { phase in
  Circle().scaleEffect(phase)
}

// CORRECT: Use keyframeAnimator for one-time, or add trigger
PhaseAnimator([0, 1], trigger: trigger) { phase in
  Circle().scaleEffect(phase)
}
.onTapGesture { trigger.toggle() }
```

```swift
// WRONG: Hard-coding animation duration
withAnimation(.spring(duration: 0.5)) { /* ... */ }

// CORRECT: Use presets (or scale appropriately)
withAnimation(.snappy) { /* ... */ }
```

```swift
// WRONG: Nested contentTransition modifiers
Text("Hi")
  .contentTransition(.numericText())
  .contentTransition(.symbolEffect(.bounce))  // second overwrites first

// CORRECT: Only one contentTransition at a time
Text("Hi").contentTransition(.numericText())
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

### RotateGesture (iOS 17+)

```swift
@State private var angle: Angle = .zero

Image("dial")
  .rotationEffect(angle)
  .gesture(
    RotateGesture()
      .onChanged { value in angle = value.rotation }
      .onEnded { value in
        withAnimation(.spring) { angle += value.rotation }
      }
  )
```

### @GestureState Auto-Reset Behavior

`@GestureState` automatically resets to its initial value when the gesture ends:

```swift
@GestureState private var dragOffset = CGSize.zero
@State private var accumulatedOffset = CGSize.zero

Image("card")
  .offset(dragOffset)
  .gesture(
    DragGesture()
      .updating($dragOffset) { value, state, _ in
        state = value.translation
      }
      .onEnded { value in
        accumulatedOffset.width += value.translation.width
        accumulatedOffset.height += value.translation.height
        // dragOffset auto-resets here
      }
  )
```

**Custom reset with `resetTransaction` (iOS 18+):**

```swift
@GestureState private var scale = 1.0

Image("photo")
  .scaleEffect(scale)
  .gesture(
    MagnifyGesture()
      .updating($scale) { value, state, _ in
        state = value.magnification
      }
      .onEnded { _ in
        // spring animation applies to reset
      }
  )
```

### Gesture Composition Details

**Simultaneous gestures — both respond:**

```swift
let combined = DragGesture()
  .simultaneously(with: MagnifyGesture())
  .onChanged { value in
    // both active at same time
  }
```

**Sequenced gestures — first then second:**

```swift
let sequence = LongPressGesture(minimumDuration: 0.5)
  .sequenced(before: DragGesture())
  .onChanged { value in
    switch value {
    case .first(true):  // long press recognized
      print("Can now drag")
    case .second(true, let drag):  // dragging
      print("Dragging: \(drag?.translation ?? .zero)")
    default:
      break
    }
  }
```

**Exclusively — first match wins, cancels others:**

```swift
let exclusive = TapGesture()
  .exclusively(before: LongPressGesture(minimumDuration: 0.5))
  // Quick tap fires immediately, cancels long press
  // If long press completes first, tap never fires
```

### GestureMask Control

Control which gesture responders are active:

```swift
View()
  .gesture(parentGesture, mask: .subviews)  // children only
  .gesture(childGesture, mask: .gesture)    // parent only
  .gesture(combinedGesture, mask: .all)     // both
```

### Conflicting Parent/Child Gestures

Resolve conflicts with composition order:

```swift
// WRONG: Ambiguous gesture priority
VStack {
  Button("Tap me") { }
    .gesture(DragGesture())  // conflicts with button's tap
}
.gesture(DragGesture())

// CORRECT: Use simultaneousGesture on parent
VStack {
  Button("Tap me") { buttonAction() }
}
.simultaneousGesture(DragGesture())  // both can fire
```

**Common Mistakes — Gestures:**

```swift
// WRONG: Storing gesture in @State (gestures are value types)
@State var myGesture = DragGesture()

// CORRECT: Define as computed property or local variable
var dragGesture: some Gesture {
  DragGesture()
    .updating($offset) { value, state, _ in
      state = value.translation
    }
}
```

```swift
// WRONG: Not resetting gesture state on dismissal
@GestureState var offset = CGSize.zero
// if parent dismisses view, gesture state may linger

// CORRECT: @GestureState auto-resets, but verify with onEnded
.gesture(DragGesture()
  .updating($offset) { /* ... */ }
  .onEnded { _ in
    // guaranteed reset here
  }
)
```

```swift
// WRONG: @GestureState variable loses state across gesture cycles
@GestureState var count = 0
.gesture(DragGesture()
  .onEnded { _ in count += 1 }  // count won't persist!
)

// CORRECT: Use @State for persistent values
@State var count = 0
@GestureState var dragOffset = CGSize.zero
```

```swift
// WRONG: Sequenced gesture without checking phase
LongPressGesture()
  .sequenced(before: DragGesture())
  .onChanged { value in
    let drag = value.second?.second  // force-unwrap crashes
  }

// CORRECT: Use pattern matching
.onChanged { value in
  switch value {
  case .second(true, let drag?):
    print("Safe: \(drag.translation)")
  default:
    break
  }
}
```

```swift
// WRONG: High minimumDuration delays gesture recognition
Text("Press me")
  .onLongPressGesture(minimumDuration: 3.0) { /* ... */ }

// CORRECT: Use 0.3-0.7 seconds (feels responsive)
Text("Press me")
  .onLongPressGesture(minimumDuration: 0.5) { /* ... */ }
```

```swift
// WRONG: Not providing visual feedback during gesture
.gesture(DragGesture()
  .updating($offset) { value, state, _ in
    state = value.translation
  }
)

// CORRECT: Feedback at each phase
.offset(offset)
.opacity(offset == .zero ? 1.0 : 0.8)  // visual cue
.gesture(DragGesture()
  .updating($offset) { /* ... */ }
)
```

**Rules:**
- Always provide visual feedback during gesture (offset, scale, opacity change)
- Use `@GestureState` for transient gesture state — resets automatically on end
- Minimum 44pt touch target for gesture-interactive elements
- Don't override system gestures (edge swipes, bottom bar)
- Add haptic feedback at meaningful thresholds during continuous gestures
- Use simultaneous/sequenced composition to prevent gesture conflicts
- Test `@GestureState` reset behavior across different scenarios

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

**Shortcut:** `ContentUnavailableView.search` auto-includes the search term — no need for `.search(text: searchText)`.

### Design Rules

**Tap targets:** Apple's minimum is 44×44pt. Use `.contentShape(.rect)` or `.frame(minWidth: 44, minHeight: 44)` to expand small elements.

**Typography:**
- Use `bold()` instead of `fontWeight(.bold)` — `bold()` lets the system choose the correct weight for context.
- Avoid `.caption2` (extremely small). Use `.caption` carefully.
- Limit to 4-5 font sizes across the app. Differentiate with weight, not size sprawl.

**Semantic styling:**
- Prefer system hierarchical styles (`.secondary`, `.tertiary`) over manual `opacity()` — they adapt to context automatically.
- Use semantic colors (`Color.primary`, `.secondary`, `.accentColor`) over hardcoded colors. Limit opacity values to 2-3 at most.
- `RoundedRectangle` default corner style is `.continuous` — no need to specify it.

**Component preferences:**
- Use `Label("Settings", systemImage: "gear")` over `HStack { Image(); Text() }` for icon+text — it's semantic and adapts to context (sidebar, list, etc.).
- Wrap `Slider`, `Stepper`, and other controls in `LabeledContent` inside `Form` for correct layout.
- Prefer `TextField(axis: .vertical)` over `TextEditor` — it supports placeholder text. Use `lineLimit(5...)` for minimum height.
- Use `Button("Add", systemImage: "plus", action: addUser)` when action can be passed directly — cleaner than trailing closure.

**Spacing discipline:**
- Prefer a consistent spacing grid: 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48. No arbitrary values.
- Create a shared design constants enum for fonts, sizes, colors, spacing, padding, rounding, and animation timings.

### LazyVStack and LazyHStack

Defer view creation until items become visible:

```swift
ScrollView {
  LazyVStack(spacing: 8) {
    ForEach(largeArray) { item in
      ItemRow(item: item)  // created on-demand
    }
  }
}
```

**Warning:** Never nest `GeometryReader` inside lazy containers — it defeats lazy evaluation.

```swift
// WRONG: GeometryReader inside LazyVStack
LazyVStack {
  ForEach(items) { item in
    GeometryReader { geo in
      // Breaks lazy loading
    }
  }
}

// CORRECT: Use outer GeometryReader if needed
GeometryReader { geo in
  LazyVStack {
    ForEach(items) { item in
      ItemView(item: item, width: geo.size.width)
    }
  }
}
```

### ScrollView Background & Custom Styling

```swift
// Hide default background
ScrollView {
  LazyVStack { content }
    .scrollContentBackground(.hidden)
}
.background(LinearGradient(...))
```

### ScrollViewReader for Scroll-to-Top

Combine with `.onChange(of:)` for scroll-to-top patterns:

```swift
@State private var scrollProxy: ScrollViewProxy?

ScrollViewReader { proxy in
  ScrollView {
    LazyVStack {
      ForEach(messages, id: \.id) { message in
        MessageRow(message: message)
      }
      Color.clear.frame(height: 1).id("bottom")
    }
  }
  .onAppear {
    scrollProxy = proxy
    proxy.scrollTo("bottom", anchor: .bottom)
  }
  .onChange(of: messages.count) {
    scrollProxy?.scrollTo("bottom", anchor: .bottom)
  }
}
```

### .searchable with Scopes and Debouncing

```swift
@State private var searchText = ""
@State private var scope: SearchScope = .all

var body: some View {
  NavigationStack {
    List(results) { item in
      ItemRow(item: item)
    }
    .searchable(
      text: $searchText,
      scope: $scope,
      prompt: "Search items"
    ) {
      ForEach(SearchScope.allCases) { s in
        Text(s.label).tag(s)
      }
    }
    .task(id: searchText) {
      guard !searchText.isEmpty else { return }
      await performSearch(query: searchText)
    }
  }
}
```

### safeAreaInset for Keyboard-Aware Pins

```swift
NavigationStack {
  ScrollView {
    content
  }
  .safeAreaInset(edge: .bottom) {
    MessageInputBar()
      .background(.ultraThinMaterial)
  }
}
```

The input bar stays above the keyboard automatically.

### Custom Multi-Column HStack with horizontalSizeClass

Adaptive layouts for compact/regular widths:

```swift
@Environment(\.horizontalSizeClass) var sizeClass

var body: some View {
  if sizeClass == .compact {
    VStack { columnA; columnB; columnC }
  } else {
    HStack { columnA; columnB; columnC }
  }
}
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

## Section 6.5: Use the Real API — Don't Hack These

> **Rule 19: Apple API first — no custom builds when a system API exists.**
>
> Before building ANY custom component, check Apple's documentation first. If Apple
> provides it as a native SwiftUI modifier, UIKit API, or system framework — use it.
> No custom implementations when a system equivalent exists. Eye rejects any code that
> custom-builds something Apple already provides natively.
>
> The items below are the 18 most common violations. Every one has a clean SwiftUI API
> that replaces 50-200 lines of hacky workaround code. If you find yourself writing
> UIKit bridge code, wrapping `UIViewRepresentable`, or importing `UIKit` for any of
> these — stop and use the SwiftUI modifier instead.

### Haptic Feedback — sensoryFeedback (iOS 17+)

```swift
// WRONG — UIKit bridge for haptics
import UIKit
UIImpactFeedbackGenerator(style: .medium).impactOccurred()
UINotificationFeedbackGenerator().notificationOccurred(.success)

// CORRECT — pure SwiftUI, semantic haptics
@State private var taskCompleted = false

Button("Complete") { taskCompleted = true }
  .sensoryFeedback(.success, trigger: taskCompleted)
```

**Available feedback types:**

| Type | When to use |
|------|-------------|
| `.success` | Task completed successfully |
| `.warning` | Something needs attention |
| `.error` | Something failed |
| `.selection` | Picker or value changed |
| `.increase` / `.decrease` | Value crossed a threshold |
| `.impact` | Physical metaphor (tap, drop) |
| `.impact(weight: .heavy, intensity: 0.8)` | Custom weight + intensity |
| `.start` / `.stop` | Activity began or ended |
| `.levelChange` | Discrete pressure levels |
| `.alignment` | Dragged item snapped to guide |

```swift
// Conditional feedback
.sensoryFeedback(trigger: sliderValue) { oldVal, newVal in
  newVal > threshold ? .impact(weight: .heavy) : nil
}

// During continuous gesture (e.g., drag snapping to grid)
.sensoryFeedback(.alignment, trigger: snappedToGrid)
```

### containerRelativeFrame — No More GeometryReader Hacks (iOS 17+)

```swift
// WRONG — GeometryReader for percentage-based sizing
GeometryReader { geo in
  Image("hero")
    .resizable()
    .frame(width: geo.size.width * 0.9, height: geo.size.height * 0.4)
}

// CORRECT — containerRelativeFrame (doesn't break layout or lazy loading)
Image("hero")
  .resizable()
  .containerRelativeFrame(.horizontal) { length, _ in length * 0.9 }
  .containerRelativeFrame(.vertical) { length, _ in length * 0.4 }
```

```swift
// Carousel cards that are 85% of scroll view width
ScrollView(.horizontal) {
  LazyHStack(spacing: 16) {
    ForEach(items) { item in
      CardView(item: item)
        .containerRelativeFrame(.horizontal, count: 1, span: 1, spacing: 16)
    }
  }
  .scrollTargetLayout()
}
.scrollTargetBehavior(.viewAligned)
```

**Rule:** `GeometryReader` is a last resort — it breaks `LazyVStack`/`LazyHStack`
performance, forces eager evaluation, and causes layout ambiguity. Use
`containerRelativeFrame` for percentage sizing, `ViewThatFits` for adaptive
layout, and `Layout` protocol for custom arrangements.

### symbolEffect — Animated SF Symbols (iOS 17+)

```swift
// WRONG — manual animation on SF Symbol
Image(systemName: "checkmark.circle")
  .rotationEffect(.degrees(isLoading ? 360 : 0))
  .animation(.linear(duration: 1).repeatForever(), value: isLoading)

// CORRECT — built-in symbol animations
Image(systemName: "checkmark.circle")
  .symbolEffect(.bounce, value: taskComplete)       // bounce on trigger

Image(systemName: "wifi")
  .symbolEffect(.variableColor.iterative)            // animated signal bars

Image(systemName: "arrow.down.circle")
  .symbolEffect(.pulse, isActive: isDownloading)     // pulse while active

// Replace one symbol with another (animated transition)
Image(systemName: isPlaying ? "pause.fill" : "play.fill")
  .contentTransition(.symbolEffect(.replace))
```

**Available effects:** `.bounce`, `.pulse`, `.variableColor`, `.scale`,
`.appear`, `.disappear`, `.replace`, `.wiggle`, `.breathe`, `.rotate`

### scrollDismissesKeyboard (iOS 16+)

```swift
// WRONG — tap gesture to dismiss keyboard
.onTapGesture {
  UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder),
    to: nil, from: nil, for: nil)
}

// WRONG — custom ViewModifier wrapping UIKit
struct DismissKeyboardOnScroll: ViewModifier { ... }

// CORRECT — one modifier on the ScrollView
ScrollView {
  LazyVStack { /* messages */ }
}
.scrollDismissesKeyboard(.interactively)  // dismiss as you scroll
```

**Modes:**

| Mode | Behavior |
|------|----------|
| `.automatic` | System decides based on context |
| `.immediately` | Keyboard hides as soon as scroll starts |
| `.interactively` | Keyboard tracks finger — drag down to dismiss |
| `.never` | Keyboard stays open during scroll |

### presentationDetents + Sheet Customization (iOS 16+)

```swift
// WRONG — custom bottom sheet with DragGesture + offset + dimming
struct CustomBottomSheet: View {
  @State private var offset: CGFloat = 0
  @GestureState private var dragOffset: CGFloat = 0
  // ... 100+ lines of gesture math and animation

// CORRECT — native sheet detents
.sheet(item: $selectedItem) { item in
  DetailView(item: item)
    .presentationDetents([.medium, .large])              // snap points
    .presentationDetents([.fraction(0.3), .height(200)]) // custom sizes
    .presentationDragIndicator(.visible)                  // grabber
    .presentationBackground(.ultraThinMaterial)            // blur background
    .presentationCornerRadius(24)                          // corner radius
    .presentationBackgroundInteraction(.enabled(upThrough: .medium))  // interact behind
    .interactiveDismissDisabled(hasUnsavedChanges)        // prevent accidental dismiss
}
```

### FocusState — Keyboard Management (iOS 15+)

```swift
// WRONG — UITextField wrapper just for keyboard control
struct FocusableTextField: UIViewRepresentable {
  func makeUIView(context: Context) -> UITextField { ... }
  // ... 50 lines of coordinator code

// CORRECT — native focus management
@FocusState private var focusedField: Field?

enum Field { case username, password }

VStack {
  TextField("Username", text: $username)
    .focused($focusedField, equals: .username)
    .submitLabel(.next)
    .onSubmit { focusedField = .password }

  SecureField("Password", text: $password)
    .focused($focusedField, equals: .password)
    .submitLabel(.go)
    .onSubmit { login() }
}
.toolbar {
  ToolbarItemGroup(placement: .keyboard) {
    Spacer()
    Button("Done") { focusedField = nil }  // dismiss keyboard
  }
}
.onAppear { focusedField = .username }  // auto-focus on appear
```

**Key points:**
- `@FocusState` is `nil` when nothing is focused — set to `nil` to dismiss keyboard
- `.submitLabel()` changes the return key: `.done`, `.go`, `.send`, `.next`, `.search`
- `.onSubmit` fires when user taps return — chain focus between fields
- `ToolbarItemGroup(placement: .keyboard)` adds buttons above the keyboard

### toolbarVisibility — Hide/Show Bars (iOS 16+)

```swift
// WRONG — global side effects
UINavigationBar.appearance().isHidden = true

// WRONG — deprecated modifier
.navigationBarHidden(true)

// CORRECT — scoped, per-view, no side effects
.toolbarVisibility(.hidden, for: .navigationBar)
.toolbarVisibility(.hidden, for: .tabBar)
.toolbarVisibility(.visible, for: .bottomBar)
```

**Bars you can control:** `.navigationBar`, `.tabBar`, `.bottomBar`,
`.windowToolbar` (macOS)

**Visibility values:** `.automatic` (system decides), `.visible`, `.hidden`

### MeshGradient (iOS 18+)

```swift
// WRONG — stacking multiple LinearGradients with blend modes
ZStack {
  LinearGradient(colors: [.blue, .purple], ...)
  RadialGradient(colors: [.pink, .clear], ...)
    .blendMode(.overlay)
}

// CORRECT — native mesh gradient with control points
MeshGradient(
  width: 3, height: 3,
  points: [
    .init(0, 0), .init(0.5, 0), .init(1, 0),
    .init(0, 0.5), .init(0.5, 0.5), .init(1, 0.5),
    .init(0, 1), .init(0.5, 1), .init(1, 1)
  ],
  colors: [
    .red, .purple, .indigo,
    .orange, .cyan, .blue,
    .yellow, .green, .mint
  ]
)
.ignoresSafeArea()
```

Animate by changing point positions or colors with `withAnimation`.

### Background + Keyboard Corners — ignoresSafeArea (iOS 26+)

```swift
// WRONG — background doesn't extend behind keyboard
// White square artifact visible behind keyboard's rounded corners (Liquid Glass)
VStack {
  List { /* content */ }
  TextField("Search...", text: $query)
}
.background(Color(.systemGroupedBackground))  // BUG: white corners behind keyboard

// CORRECT — ignoresSafeArea() extends background behind keyboard area
VStack {
  List { /* content */ }
  TextField("Search...", text: $query)
}
.background(Color(.systemGroupedBackground).ignoresSafeArea())
```

**Why this happens:** In iOS 26, the keyboard has rounded corners (Liquid Glass). If your
view's background doesn't extend into the safe area behind the keyboard, the default white
background bleeds through at those corners, creating a visible square artifact.

**Key details:**
- Only visible on real devices by default — toggle CMD+K in simulator to reproduce
- Add `.keyboard` scope if you only want to ignore the keyboard safe area:
  `.ignoresSafeArea(.keyboard)`
- Applies to any view with a custom background behind a keyboard — not just `List`

### overlay() — Use Trailing Closure Form

```swift
// WRONG — deprecated overlay form
Text("Hello")
  .overlay(Circle().fill(.red), alignment: .topTrailing)

// CORRECT — modern trailing closure form (iOS 15+)
Text("Hello")
  .overlay(alignment: .topTrailing) {
    Circle().fill(.red)
  }
```

### Toolbar Placement — topBarLeading / topBarTrailing

```swift
// WRONG — deprecated placement names
.toolbar {
  ToolbarItem(placement: .navigationBarLeading) { BackButton() }
  ToolbarItem(placement: .navigationBarTrailing) { SaveButton() }
}

// CORRECT — modern placement names
.toolbar {
  ToolbarItem(placement: .topBarLeading) { BackButton() }
  ToolbarItem(placement: .topBarTrailing) { SaveButton() }
}
```

### scrollIndicators — Hide Scroll Bars

```swift
// WRONG — old initializer parameter
ScrollView(showsIndicators: false) { content }

// CORRECT — modern modifier (iOS 16+)
ScrollView { content }
  .scrollIndicators(.hidden)
```

### @Entry Macro — Custom Environment Keys (iOS 17+)

```swift
// WRONG — verbose legacy pattern
struct ThemeKey: EnvironmentKey {
  static let defaultValue = Theme.standard
}
extension EnvironmentValues {
  var theme: Theme {
    get { self[ThemeKey.self] }
    set { self[ThemeKey.self] = newValue }
  }
}

// CORRECT — @Entry macro replaces all boilerplate
extension EnvironmentValues {
  @Entry var theme = Theme.standard
}
// Works for EnvironmentValues, FocusValues, Transaction, ContainerValues
```

### Fill + Stroke — No Overlay Needed (iOS 17+)

```swift
// WRONG — old overlay pattern for fill+stroke
Circle()
  .fill(.blue)
  .overlay(Circle().stroke(.white, lineWidth: 2))

// CORRECT — chain directly (iOS 17+)
Circle()
  .fill(.blue)
  .stroke(.white, lineWidth: 2)
```

**Rendering views to images:** Prefer `ImageRenderer` over `UIGraphicsImageRenderer` for rendering SwiftUI views to images.

### Text Interpolation — No + Concatenation

```swift
// WRONG — deprecated Text concatenation
Text("Hello ").foregroundStyle(.red)
+
Text("World").foregroundStyle(.blue)

// CORRECT — text interpolation
let red = Text("Hello ").foregroundStyle(.red)
let blue = Text("World").foregroundStyle(.blue)
Text("\(red)\(blue)")
```

### Grammar Agreement — Auto-Pluralization

```swift
// WRONG — manual pluralization
Text(count == 1 ? "1 item" : "\(count) items")

// CORRECT — automatic grammar agreement (en, fr, de, pt, es, it)
Text("^[\(count) item](inflect: true)")
```

### ForEach over enumerated() — No Array Conversion

```swift
// WRONG — unnecessary Array allocation
ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
  Text("\(index): \(item.name)")
}

// CORRECT — use enumerated directly
ForEach(items.enumerated(), id: \.element.id) { index, item in
  Text("\(index): \(item.name)")
}
```

---

## Section 6.7: Accessibility Quick Reference

### Dynamic Type

- Never force specific font sizes. Prefer Dynamic Type: `.font(.body)`, `.font(.headline)`.
- For custom font sizes: use `@ScaledMetric` (iOS 14+) or `.font(.body.scaled(by:))` (iOS 26+).
- Avoid `.caption2` (extremely small). Use `.caption` carefully.

### VoiceOver

- **Buttons with image labels must always include text**, even if invisible: `Button("Add User", systemImage: "plus", action: addUser)`. Flag icon-only buttons as VoiceOver-invisible.
- **Menu must include text label** like Button: `Menu("Options", systemImage: "ellipsis.circle") { }` — not just an image.
- `onTapGesture()` should only be used when you need tap location or tap count. All other tappable elements should be `Button`.
- If `onTapGesture()` must be used, add `.accessibilityAddTraits(.isButton)` for VoiceOver.
- Use `accessibilityInputLabels()` for buttons with complex/changing labels (e.g. live stock price button — add input label "Apple" for Voice Control).

### Color & Motion

- Respect `accessibilityDifferentiateWithoutColor` — when color differentiates items, also add icons, patterns, or strokes.
- Respect `accessibilityReduceMotion` — replace large animations with crossfade/opacity.
- Use `bold()` over `fontWeight(.bold)` — `bold()` lets the system pick the correct weight for context.

### Tap Targets

- Apple's minimum acceptable tap area is **44×44pt**. Enforce strictly for all interactive elements.
- Use `.contentShape(.rect)` to expand small visual elements to meet the 44pt minimum.

### Design for All Input Methods

- Support Voice Control: ensure all interactive elements have discoverable labels.
- Support Full Keyboard Access: test `Tab` navigation order, ensure focus rings are visible.
- Support Switch Control: all actions reachable without gestures.

---

**Previews:** Always use `#Preview { }` — never the legacy `PreviewProvider` protocol.

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

### Data Flow Rules

**@State ownership:**
- `@State` should always be `private` — only the view that creates it should own it.
- `@State` can cache expensive non-observable objects (e.g. `CIContext`) — SwiftUI persists it without change tracking.

**@AppStorage traps:**
- Never use `@AppStorage` inside an `@Observable` class, even with `@ObservationIgnored` — it will NOT trigger view updates when the stored value changes.
- `@AppStorage` must never store sensitive data (passwords, tokens, API keys). Use Keychain instead.

**Bindings:**
- Never use `Binding(get:set:)` in view body code — use `@State`/`@Binding` with `.onChange()` instead.
- For numeric `TextField`: `TextField("Score", value: $score, format: .number)` + `.keyboardType(.numberPad)`.

**onChange:**
- Never use the 1-parameter `onChange()` variant — it's deprecated. Use the 0-parameter or 2-parameter variant.

**ObservableObject:**
- If `ObservableObject` is absolutely required (e.g. Combine debouncer), you must add `import Combine` explicitly — SwiftUI no longer provides it.

**SwiftData + CloudKit constraints:**
- Never use `@Attribute(.unique)` or `#Unique` with CloudKit sync.
- All model properties must have default values or be optional.
- All relationships must be optional.

**MV-first default:**
- When `@State` + `.task` + `@Environment` suffices, don't introduce a view model. Only extract to `@Observable` class when logic grows complex enough to need independent testing.

**When to justify a view model (exceptions to MV-first):**
- User explicitly requests MVVM pattern
- Codebase has established MVVM convention (stay consistent)
- Long-lived reference model shared across multiple views
- Bridging non-SwiftUI API that requires reference semantics
- Shared presentation state (e.g., multi-step form wizard)

If none of these apply, MV-first wins. Split UI before inventing abstraction layers.

### Architecture Routing

Before writing any architecture code, **detect** what the project already uses. Never assume.

**Detection — read the codebase first:**

| Signal in Code | Pattern |
|---|---|
| `@State` + `.task` + `@Environment` + services, no ViewModel classes | **MV** (Model-View) |
| `@Observable class *ViewModel` or `ObservableObject` + `@Published` | **MVVM** |
| `Store<State, Action>`, `Reducer`, `@Dependency` | **TCA** (Composable Architecture) |
| `protocol *Router`, `Coordinator` class, `path` management | **Coordinator** |
| `Intent`/`Action` enum → `reduce()` → `Effect` | **MVI** (Unidirectional) |
| `protocol *Interactor`, `*Presenter`, `*Router` per module | **VIPER** |
| `protocol *UseCase`, `*Repository`, strict layer folders | **Clean Architecture** |
| Combine `Publisher` chains, `sink`, `switchToLatest` | **Reactive** |

**After detection — isolation rules (never mix):**

| If Pattern Is... | NEVER Do This |
|---|---|
| **MV** | Create ViewModel classes. If you need shared state, use `@Environment` services. |
| **MVVM** | Use `@Dependency` macro (that's TCA). Use `@Environment` for DI, not `@Dependency`. |
| **TCA** | Create ViewModel classes or use `@Environment` for DI. TCA uses `@Dependency` and `Store`. |
| **Coordinator** | Push/present from inside views. Views call coordinator methods or set state. |
| **MVI** | Put side effects in the reducer. Reducer is pure. Effects run separately. |
| **VIPER** | Let views call services directly. Views talk only to Presenter. |
| **Clean** | Import inner layers from outer layers. Dependencies point inward only. |
| **Reactive** | Break publisher chains with random `Task {}` blocks. Stay in the reactive pipeline. |

**Intentional simplification is OK:** A simpler pattern can exist inside a more complex architecture (e.g., a plain MV settings screen inside a TCA app). But never the reverse — don't introduce TCA into one screen of an MV app.

**Architecture decision tree (new projects or architecture reviews):**

```
START → Is it a simple app (≤5 screens, minimal shared state)?
  YES → MV pattern (State + Environment + services)
  NO ↓
Does the project need composable features at scale with deterministic testing?
  YES → TCA
  NO ↓
Is navigation complex (deep links, auth gates, multi-step flows)?
  YES → Coordinator pattern (pair with MVVM or MV for screens)
  NO ↓
Is it stream-heavy (live search, real-time feeds, reactive chains)?
  YES → Reactive (Combine / AsyncSequence)
  NO ↓
Do multiple views share complex presentation state?
  YES → MVVM
  NO → MV pattern (default)
```

**For architecture reviews:** Run the same decision tree against the current project. If the current pattern doesn't match the project's actual complexity, flag it:
- **Over-engineered:** Full TCA for a 3-screen app with no shared state → recommend MV
- **Under-engineered:** Bare MV with 15+ screens sharing complex state → recommend MVVM or Coordinator
- **Good fit:** Pattern matches complexity → enforce its isolation rules

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

### UIViewRepresentable Lifecycle

The representable calls methods in this order:

1. **`makeCoordinator()`** — create the coordinator (once)
2. **`makeUIView(context:)`** — create and configure the UIView
3. **`updateUIView(_:context:)`** — sync SwiftUI state to UIView (called whenever bindings change)
4. **`dismantleUIView(_:coordinator:)`** (optional) — cleanup before removal
5. **`sizeThatFits(_:uiView:context:)`** (iOS 16+, optional) — custom sizing

### Guard-Against-Redundancy Pattern

Avoid update loops by checking before mutating:

```swift
func updateUIView(_ uiView: UITextView, context: Context) {
  // Check before updating to avoid triggering delegate callbacks
  if uiView.text != text {
    uiView.text = text
  }

  if uiView.mapType != mapType {
    uiView.mapType = mapType
  }
}
```

This prevents the UIView's delegate from triggering a state change that loops back.

### .sizeThatFits() for Custom Sizing (iOS 16+)

```swift
struct CustomTextEditor: UIViewRepresentable {
  @Binding var text: String

  func makeUIView(context: Context) -> UITextView {
    let textView = UITextView()
    textView.delegate = context.coordinator
    return textView
  }

  func updateUIView(_ uiView: UITextView, context: Context) {
    if uiView.text != text {
      uiView.text = text
    }
  }

  @available(iOS 16.0, *)
  func sizeThatFits(
    _ proposal: ProposedViewSize,
    uiView: UITextView,
    context: Context
  ) -> CGSize? {
    let width = proposal.width ?? UIView.layoutFittingExpandedSize.width
    let size = uiView.sizeThatFits(CGSize(width: width, height: .greatestFiniteMagnitude))
    return CGSize(width: width, height: max(size.height, 44))
  }
}
```

### UIHostingConfiguration for Collection/Table Views (iOS 16+)

Host SwiftUI content inside UITableViewCell or UICollectionViewCell:

```swift
var listConfiguration: UICollectionView.CellRegistration<UICollectionViewListCell, Item> {
  UICollectionView.CellRegistration { cell, indexPath, item in
    var config = cell.defaultContentConfiguration()
    config.imageProperties.maximumWidth = 60

    let swiftUIView = ItemDetailView(item: item)
    cell.contentConfiguration = UIHostingConfiguration {
      swiftUIView
    }
  }
}
```

### UIHostingController.sizingOptions (iOS 16+)

Control how UIHostingController sizes its view:

```swift
let hostingController = UIHostingController(rootView: SwiftUIView())
hostingController.sizingOptions = [.intrinsicContentSize]
// now respects SwiftUI view's ideal size
```

Options: `.intrinsicContentSize` (use ideal size), `.preferredContentSize` (use size class), default (fill container).

**Common Mistakes — UIKit Interop:**

```swift
// WRONG: Storing UIKit delegates in @State
@State var delegate: MapDelegate?

func makeUIView(context: Context) -> MKMapView {
  let map = MKMapView()
  map.delegate = delegate  // WRONG: delegate released unexpectedly
  return map
}

// CORRECT: Use makeCoordinator()
func makeCoordinator() -> Coordinator { Coordinator(self) }

func makeUIView(context: Context) -> MKMapView {
  let map = MKMapView()
  map.delegate = context.coordinator  // survives representable lifetime
  return map
}
```

```swift
// WRONG: Updating UIView without checking state
func updateUIView(_ uiView: UITextView, context: Context) {
  uiView.text = text  // even if unchanged, triggers delegate
}

// CORRECT: Guard against redundancy
func updateUIView(_ uiView: UITextView, context: Context) {
  if uiView.text != text {
    uiView.text = text
  }
}
```

```swift
// WRONG: Dismissing with UIKit API
func imagePickerController(...) {
  presentingViewController?.dismiss(animated: true)
}

// CORRECT: Use SwiftUI @Environment(\.dismiss)
class Coordinator: NSObject, UIImagePickerControllerDelegate {
  @Environment(\.dismiss) private var dismiss

  func imagePickerController(...) {
    dismiss()  // SwiftUI handles it
  }
}
```

```swift
// WRONG: No coordinator for state synchronization
func makeUIView(context: Context) -> UIView {
  let view = UIView()
  // Can't communicate back to parent SwiftUI view
  return view
}

// CORRECT: Use coordinator to bridge UIKit callbacks to bindings
class Coordinator: NSObject, UITextViewDelegate {
  var parent: TextViewRepresentable

  func textViewDidChange(_ textView: UITextView) {
    parent.text = textView.text
  }
}
```

```swift
// WRONG: Hard-coding auto-layout constraints
hostingController.view.frame = CGRect(x: 0, y: 0, width: 320, height: 480)

// CORRECT: Use autolayout and constraints for adaptability
hostingController.view.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
  hostingController.view.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
  hostingController.view.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
  // ... etc
])
```

**Rules:**
- Use `makeCoordinator()` for delegates — never store UIKit delegates in SwiftUI `@State`
- Update UIKit view in `updateUIView` based on binding changes — don't bypass the SwiftUI lifecycle
- Use `@Environment(\.dismiss)` in representables, not `presentingViewController?.dismiss`
- Always check before mutating UIView state to avoid feedback loops
- Use `.sizeThatFits()` for proper intrinsic sizing in iOS 16+
- Use `UIHostingConfiguration` to embed SwiftUI in collection/table cells
- Set `sizingOptions = [.intrinsicContentSize]` on UIHostingController for proper sizing

---

## Section 8.5: Performance Profiling & Optimization

### Instruments + SwiftUI Instrument

Profile with the dedicated SwiftUI instrument (Instruments 26+):

```bash
# Record in Release mode with SwiftUI template
# Xcode → Product → Profile
```

Open the SwiftUI instrument lane to see:
- **Long View Body Updates** — views that take too long to evaluate
- **Other Long Updates** — state changes, notifications, updates
- **View body evaluation counts** — how many times each view's body runs

### Self._printChanges() Debug API

Print view update reasons during development:

```swift
var body: some View {
  VStack {
    // ...
  }
  ._printChanges()  // logs why this view updated
}
```

Example output:
```
Body.View(source: "/App.swift:20", state changed, <timestamp>)
```

Use to catch unexpected updates or large state change cascades.

### Lazy Loading Decision Tree

Use this heuristic:

- **< 50 items** → eager stacks (VStack, HStack, List)
- **50-100 items** → consider Lazy* containers
- **> 100 items** → always use Lazy* (LazyVStack, LazyHStack, LazyVGrid)

### Observation Scope Pollution

Problem: Large @Observable objects trigger all children to update when any field changes.

Solution: Push reads into child views — decompose @Observable objects.

```swift
// WRONG: Single massive @Observable
@Observable final class AppState {
  var user: User
  var posts: [Post]
  var notifications: [Notification]
  var settings: Settings
}

// Every property change updates entire tree

// CORRECT: Decompose into scoped services
@Observable final class UserService {
  var user: User
}

@Observable final class PostService {
  var posts: [Post]
}

// Each service used where needed; only affected children update
```

### Performance Triage Order

When a view has multiple performance issues, fix them in this priority order:

1. **Invalidation storms** — Broad `@Observable` reads triggering cascading updates across the view tree. Fix: narrow observation scope, decompose into smaller observable objects.
2. **Identity churn** — Unstable `ForEach` identity (`id: \.self` on mutable collections, inline filtering, root-level `if/else` swapping entire view trees). Fix: stable identifiers, ternary for toggling.
3. **Main-thread work** — Heavy compute, sorting, filtering, or formatter creation in `body`. Fix: precompute in `@State`, move to `.task()`, use `@concurrent`.
4. **Image cost** — Decoding/resizing full-resolution images on main thread. Fix: `preparingThumbnail(of:)`, `AsyncImage`, downsample before display.
5. **Layout thrash** — Deep nesting, `GeometryReader` abuse, preference key chains. Fix: simplify hierarchy, use `ViewThatFits`, `Layout` protocol.

### Formatter Anti-Pattern

DateFormatter and NumberFormatter are expensive to create. Never instantiate in `body` — they re-create every render cycle.

```swift
// WRONG — new formatter on every body evaluation
var body: some View {
  let formatter = DateFormatter()
  formatter.dateStyle = .medium
  Text(formatter.string(from: date))
}

// CORRECT — static cached singleton
private static let dateFormatter: DateFormatter = {
  let f = DateFormatter()
  f.dateStyle = .medium
  return f
}()

// BEST — use FormatStyle (no formatter needed)
Text(date, format: .dateTime.month().day().year())
```

### Common Performance Mistakes

```swift
// WRONG: Heavy computation in view body
var body: some View {
  let expensiveSort = items.sorted { expensiveComparison($0, $1) }
  return List(expensiveSort) { item in
    ItemRow(item: item)
  }
}

// CORRECT: Precompute in @State or service
@State private var sortedItems: [Item] = []
@State private var items: [Item] = []

var body: some View {
  List(sortedItems) { item in
    ItemRow(item: item)
  }
  .onChange(of: items) { oldItems, newItems in
    sortedItems = newItems.sorted { expensiveComparison($0, $1) }
  }
}
```

```swift
// WRONG: Fast-changing environment values
@Environment(\.geometry) var geometry  // 60 fps updates break layout optimization

// CORRECT: Use @Binding or @State for changing values
@State private var geometry: CGSize
```

```swift
// WRONG: No memoization of expensive closures
List(items) { item in
  ItemRow(item: item)
    .onTapGesture {
      Task { await expensiveOperation(item) }  // recreated every frame
    }
}

// CORRECT: Memoize tap handler or use @Bindable
List(items) { item in
  ItemRow(item: item)
    .onTapGesture {
      handleTap(item)
    }
}

private func handleTap(_ item: Item) {
  Task { await expensiveOperation(item) }
}
```

### Ternary vs if/else for Modifier Toggling

When toggling modifier values (not switching between different view types), prefer ternary expressions. `if/else` creates `_ConditionalContent` which destroys structural identity and recreates underlying platform views.

```swift
// WRONG — if/else creates _ConditionalContent, destroys structural identity
var body: some View {
  if isHighlighted {
    Text(title).foregroundStyle(.yellow).bold()
  } else {
    Text(title).foregroundStyle(.primary)
  }
}

// CORRECT — ternary preserves structural identity, just updates properties
Text(title)
  .foregroundStyle(isHighlighted ? .yellow : .primary)
  .bold(isHighlighted)
```

### View Initializers Must Be Minimal

Never do non-trivial work in a view's `init`. View structs are created frequently — heavy init work (network calls, file I/O, complex computation) runs every time. Move work to `.task()`.

```swift
// WRONG — heavy work in init
struct ProfileView: View {
  let profile: Profile
  init(userID: String) {
    self.profile = Database.shared.fetchProfile(userID)  // blocking I/O in init!
  }
}

// CORRECT — defer to task
struct ProfileView: View {
  let userID: String
  @State private var profile: Profile?
  var body: some View {
    Group { /* display profile */ }
      .task { profile = try? await fetchProfile(userID) }
  }
}
```

### ScrollView Performance: scrollContentBackground

For ScrollViews with opaque, static, solid backgrounds, use `.scrollContentBackground(.visible)` to improve scroll-edge rendering efficiency.

### @ViewBuilder Closure Storage Anti-Pattern

Store built view results, not escaping closures:

```swift
// WRONG — stores escaping closure, re-invoked each body eval
struct CardView<Content: View>: View {
  let content: () -> Content
  var body: some View {
    VStack { content() }.padding().background(.ultraThinMaterial)
  }
}

// CORRECT — store the built view value
struct CardView<Content: View>: View {
  @ViewBuilder let content: Content
  var body: some View {
    VStack { content }.padding().background(.ultraThinMaterial)
  }
}
```

### Avoid Inline Transforms in List/ForEach

Expensive transforms (`.filter`, `.sorted`, `.map`) in `List`/`ForEach` initializers re-run on every body evaluation. Derive data outside body or cache with `@State` (but add invalidation logic to avoid stale UI).

---

## Section 8.6: Architecture Patterns

### @Observable Ownership Rules

- **`@State` owns** — creates and mutates the instance
- **`let` reads** — access without binding
- **`@Bindable` writes** — mutate individual fields

```swift
@State private var userService = UserService()

var body: some View {
  @Bindable var user = userService  // can bind individual fields

  VStack {
    TextField("Name", text: $user.name)
    // modifies userService.name
  }
  .environment(userService)  // child views read
}
```

### View Composition: Extract Subviews

Keep view bodies under 200 lines. **Strongly prefer extracting into separate `View` structs** over computed properties or `@ViewBuilder` methods. Separate structs get their own identity in SwiftUI's diffing system, reducing unnecessary re-evaluations.

```swift
// WRONG: Computed properties — no separate identity, re-evaluated with parent
var body: some View {
  VStack {
    headerView    // computed property — re-evaluated every time parent updates
    contentView
    footerView
  }
}

private var headerView: some View {
  Text("Title").font(.title)
}

// CORRECT: Separate View structs — own identity, own diffing scope
var body: some View {
  VStack {
    HeaderView(title: "Title")
    ContentView(items: items)
    FooterView(onSave: save)
  }
}

// Each in its own Swift file
struct HeaderView: View {
  let title: String
  var body: some View {
    Text(title).font(.title)
  }
}
```

**View file ordering convention:**
1. Environment properties
2. `private`/`public let` and `@Binding` parameters
3. `@State` private properties
4. Computed properties
5. `init` (if custom)
6. `body`
7. Private helper methods

**Rules:**
- Each type (struct, class, enum) should be in its own Swift file. Flag files with multiple type definitions.
- Button actions should be extracted into separate methods — don't mix layout and logic in `body`.
- Business logic should not live inline in `.task()`, `.onAppear()`, or closures in `body`.
- When `@State` suffices (with `.task` for async and `@Environment` for dependencies), don't introduce a view model. Only extract to `@Observable` view model when logic grows complex enough to need testing.

### @ViewBuilder for Conditional Logic

Use `@ViewBuilder` functions instead of ternaries in bodies:

```swift
// WRONG: Ternary in body (forces two branches to be the same type)
var body: some View {
  isLoading ? AnyView(ProgressView()) : AnyView(ContentView())
}

// CORRECT: @ViewBuilder function
var body: some View {
  loadingState()
}

@ViewBuilder
private func loadingState() -> some View {
  if isLoading {
    ProgressView()
  } else {
    ContentView()
  }
}
```

### Custom ViewModifier and Extensions

Create reusable modifiers for repeated style patterns:

```swift
struct GlassCardModifier: ViewModifier {
  func body(content: Content) -> some View {
    content
      .padding()
      .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
      .shadow(radius: 8)
  }
}

extension View {
  func glassCard() -> some View {
    modifier(GlassCardModifier())
  }
}

// Usage
VStack { /* content */ }
  .glassCard()
```

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

### Accessibility
- [ ] No forced font sizes — Dynamic Type used (`.body`, `.headline`, etc.)
- [ ] Buttons with images include text labels (VoiceOver)
- [ ] Menu includes text label, not just image
- [ ] No `onTapGesture` where `Button` works — only for tap location/count
- [ ] 44×44pt minimum tap targets enforced
- [ ] Color differences supplemented with icons/patterns (`differentiateWithoutColor`)
- [ ] `accessibilityReduceMotion` respected — animations replaced with opacity
- [ ] `@ScaledMetric` used for custom sizes

### Architecture
- [ ] `@Observable` used (not `ObservableObject` / `@Published`)
- [ ] `@State` owns `@Observable` instances (not `@StateObject`)
- [ ] View models are `@MainActor`
- [ ] `.task` used for async work on appear
- [ ] Environment used for dependency injection

### No-Hack APIs (Section 6.5)
- [ ] No `GeometryReader` for percentage sizing — use `containerRelativeFrame`
- [ ] No `UIImpactFeedbackGenerator` — use `.sensoryFeedback()` modifier
- [ ] No manual keyboard dismiss gesture — use `.scrollDismissesKeyboard()`
- [ ] No custom bottom sheet with `DragGesture` — use `.presentationDetents()`
- [ ] No `UITextField` wrapper for focus — use `@FocusState` + `.focused()`
- [ ] No `UINavigationBar.appearance()` — use `.toolbarVisibility()`
- [ ] No manual blur overlay on scroll edges — use `.scrollEdgeEffectStyle(.soft)`
- [ ] No stacked `LinearGradient` hacks — use `MeshGradient` (iOS 18+)
- [ ] SF Symbol animations use `.symbolEffect()`, not manual rotation/opacity
- [ ] `.safeAreaBar()` used instead of `.safeAreaInset()` when edge effects needed (iOS 26+)
- [ ] No deprecated `overlay(_:alignment:)` — use trailing closure `.overlay { }`
- [ ] No `.navigationBarLeading/.Trailing` — use `.topBarLeading/.topBarTrailing`
- [ ] No `showsIndicators: false` — use `.scrollIndicators(.hidden)`
- [ ] `@Entry` macro used for custom environment keys (not manual `EnvironmentKey`)
- [ ] No overlay for fill+stroke — chain `.fill().stroke()` directly (iOS 17+)
- [ ] No `Text` concatenation with `+` — use text interpolation
- [ ] Grammar agreement uses `inflect: true` for pluralization
- [ ] `sheet(item:)` preferred over `sheet(isPresented:)` for data-driven sheets

---

_Source: SwiftUI documentation, Swift Evolution proposals, WWDC sessions · Condensed for Ship Framework agent reference_

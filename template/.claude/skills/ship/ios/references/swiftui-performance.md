# SwiftUI Performance Audit

> **When to read:** Dev reads during `/ship-build` when optimizing performance.
> Crit reads during `/ship-review` to flag perf anti-patterns in iOS diffs.
> For basic performance patterns (triage order, formatter anti-patterns, identity),
> see `swiftui-core.md` Section 10. This file is the deep diagnostic reference.

---

## Section 1: Symptom Classification

Before diagnosing, classify the symptom:

| Symptom | Likely category | First check |
|---------|----------------|-------------|
| Janky scrolling / dropped frames | Identity churn, layout thrash, main-thread image decode | ForEach identity, GeometryReader in lazy containers |
| High CPU in background | Invalidation storms, broad observation | @Observable fan-out, environment reads |
| Slow first load | Main-thread work in body, image decode | .task vs inline computation, image sizing |
| Memory growth over time | Leaked tasks, retained closures, image caching | Task cancellation, closure captures, image pipeline |
| Hangs / unresponsiveness | Main-thread blocking, synchronous network | await on MainActor, URLSession.shared usage |
| Excessive view updates | Broad @Observable, unstable identity | Self._printChanges(), observation scope |

---

## Section 2: Code Smell Catalog

### Smell 1: Invalidation Storms

Broad observation triggers cascading updates across the view tree.

```swift
// SMELL: View reads entire model but only uses one property
struct ProfileHeader: View {
  var model: UserModel  // @Observable with 15 properties
  var body: some View {
    Text(model.displayName)  // updates when ANY of 15 properties change
  }
}

// FIX: Granular access — only track what you read
struct ProfileHeader: View {
  var model: UserModel
  var body: some View {
    let name = model.displayName  // only this property tracked
    Text(name)
  }
}
```

```swift
// SMELL: One massive @Observable for entire app state
@Observable class AppState {
  var user: User
  var posts: [Post]
  var settings: Settings
  var notifications: [Notification]
  // 20 more properties...
}

// FIX: Decompose into focused observable objects
@Observable class UserService { var user: User }
@Observable class PostService { var posts: [Post] }
@Observable class SettingsService { var settings: Settings }
```

**Detection:** Use `Self._printChanges()` — if a view re-evaluates when unrelated properties change, observation is too broad.

### Smell 2: Unstable ForEach Identity

```swift
// SMELL: id: \.self on mutable collection — identity changes on mutation
ForEach(items, id: \.self) { item in ItemRow(item: item) }

// SMELL: UUID() in .id() — forces recreation every update
ForEach(items) { item in
  ItemRow(item: item).id(UUID())
}

// SMELL: Inline filtering changes identity set
ForEach(items.filter { $0.isActive }) { item in ItemRow(item: item) }

// FIX: Stable identifiers, derive filtered data outside body
ForEach(items) { item in  // Item conforms to Identifiable with stable id
  ItemRow(item: item)
}

// For filtering — precompute
@State private var activeItems: [Item] = []
// update in .onChange(of: items)
```

### Smell 3: Heavy Work in body

```swift
// SMELL: Sorting in body — runs on every re-evaluation
var body: some View {
  let sorted = items.sorted { $0.date > $1.date }  // O(n log n) every render
  List(sorted) { item in ItemRow(item: item) }
}

// FIX: Precompute in @State, update on change
@State private var sortedItems: [Item] = []

var body: some View {
  List(sortedItems) { item in ItemRow(item: item) }
  .onChange(of: items) { _, new in
    sortedItems = new.sorted { $0.date > $1.date }
  }
}
```

```swift
// SMELL: DateFormatter created in body — expensive, recreated every frame
var body: some View {
  let fmt = DateFormatter()
  fmt.dateStyle = .medium
  Text(fmt.string(from: date))
}

// FIX: Use FormatStyle (no formatter needed)
Text(date, format: .dateTime.month().day().year())
```

### Smell 4: Image Cost on Main Thread

```swift
// SMELL: Full-resolution image loaded and displayed directly
Image(uiImage: UIImage(contentsOfFile: path)!)
  .resizable()

// FIX: Downsample before rendering
let thumbnail = await UIImage(contentsOfFile: path)?
  .preparingThumbnail(of: CGSize(width: 200, height: 200))

// Or use AsyncImage for remote
AsyncImage(url: imageURL) { image in
  image.resizable().aspectRatio(contentMode: .fill)
} placeholder: {
  ProgressView()
}
```

### Smell 5: Layout Thrash

```swift
// SMELL: GeometryReader inside LazyVStack — defeats lazy loading
LazyVStack {
  ForEach(items) { item in
    GeometryReader { geo in
      ItemRow(item: item, width: geo.size.width)
    }
  }
}

// FIX: Use containerRelativeFrame (iOS 17+)
LazyVStack {
  ForEach(items) { item in
    ItemRow(item: item)
      .containerRelativeFrame(.horizontal)
  }
}
```

```swift
// SMELL: Deeply nested preference key chains
// Multiple PreferenceKey reads triggering layout passes

// FIX: Simplify hierarchy, use ViewThatFits, Layout protocol
ViewThatFits {
  HorizontalLayout()
  VerticalLayout()
}
```

### Smell 6: Animation Cost

```swift
// SMELL: .animation() on container — animates everything including layout
VStack { /* complex content */ }
  .animation(.default, value: isLoading)

// FIX: Explicit withAnimation on specific state change
Button("Load") {
  withAnimation(.spring(duration: 0.3)) {
    isLoading.toggle()
  }
}
```

---

## Section 3: Diagnostic Workflow

### Step 1: Code-First Review

Before touching Instruments, check for the 6 smells above in the diff. Most SwiftUI performance issues are visible in the code.

Quick scan checklist:
- [ ] Any `UUID()` or random values in `.id()` modifiers?
- [ ] Any `@Observable` with 5+ properties and views reading the whole object?
- [ ] Any computation (sort, filter, map, formatter creation) inside `body`?
- [ ] Any full-resolution image loading without downsampling?
- [ ] Any `GeometryReader` inside lazy containers?
- [ ] Any `.animation()` on containers instead of explicit `withAnimation`?
- [ ] Any `AnyView` type erasure in lists?

### Step 2: Runtime Profiling (guide the user)

If code review is inconclusive, guide the user through Instruments:

**What to collect:**
1. SwiftUI View Body instrument — which bodies re-evaluate and how often
2. Time Profiler — heaviest call stacks during interaction
3. Core Animation Commits — actual rendering time per frame

**Ask the user for:**
- Target view code and data flow (@State, @Binding, @Observable dependencies)
- Exact reproduction steps (scroll, tap, navigate — be specific)
- Device and build config (Debug vs Release — Debug is 10x slower in SwiftUI)
- Screenshots of Instruments timeline during the problematic interaction

**Important:** Always profile in Release mode. Debug builds include SwiftUI instrumentation that adds significant overhead — performance measured in Debug is not representative.

### Step 3: Diagnose

Map evidence to categories:
- **Invalidation** — view body called more than expected per interaction
- **Identity churn** — view state resets, animations restart unexpectedly
- **Layout thrash** — Core Animation Commits show layout passes > 16ms
- **Main-thread work** — Time Profiler shows heavy stacks on main thread
- **Image cost** — memory spikes during scroll, thumbnail generation on main thread
- **Animation cost** — dropped frames during transitions

Prioritize by user impact, not ease of fix.

### Step 4: Remediate

Apply targeted fixes from the Code Smell Catalog (Section 2). One fix at a time — verify before stacking changes.

Priority order:
1. Narrow observation scope (biggest wins, lowest risk)
2. Stabilize ForEach identities
3. Move computation out of body
4. Downsample images
5. Simplify layout hierarchy
6. Scope animations

### Step 5: Verify

- Re-run the same interaction with Instruments
- Compare frame rate, CPU, memory against baseline
- `Self._printChanges()` should show fewer re-evaluations
- Confirm no regressions in other views

---

## Section 4: Review Integration

### For Crit (during /ship-review of iOS projects)

Quick perf scan — check the diff for these 5 red flags:

1. **Broad @Observable reads** — view accesses model with 5+ properties but only uses 1-2
2. **Unstable ForEach identity** — `id: \.self` on mutable collections, `UUID()` in `.id()`
3. **Computation in body** — sorting, filtering, formatting, or network calls inline
4. **Full-res images without downsampling** — `UIImage(contentsOfFile:)` displayed directly
5. **GeometryReader in lazy containers** — kills lazy loading

Flag as: `PERF: [description]` with confidence score. These are "Should fix" severity unless the view is in a hot path (list items, frequently-updated views), then "Must fix."

### For Dev (during /ship-build)

Before claiming a feature is done, run the quick scan checklist from Step 1. If building list views, scrollable content, or frequently-updated views, profile in Instruments before committing.

---

## Common Mistakes

```swift
// WRONG: Debug-mode profiling
// "It's slow in the simulator" — simulator + Debug build = 10x overhead
// Always profile on device in Release mode

// WRONG: Premature optimization
// Don't optimize views that render once (settings, about screens)
// Focus on hot paths: list items, scroll views, real-time updates

// WRONG: equatable() everywhere
// .equatable() adds equality checking overhead
// Only use when equality check is cheaper than subtree recomputation
// AND inputs are value-semantic

// WRONG: Task.detached for everything
// Task.detached breaks actor inheritance — use @concurrent instead
// Reserve Task.detached for truly independent work with no actor context
```

# Apple Human Interface Guidelines — iOS/SwiftUI Reference

> **When to read:** Arc reads Sections 1, 4, 7 when planning screen maps for iOS/SwiftUI projects.
> Dev reads Sections 2-6 when building iOS UI. Eye reads Section 7 when reviewing.
>
> This is not a replacement for Apple's full HIG — it's the concrete specs and rules
> that prevent common mistakes and App Store rejections. For the full guide:
> https://developer.apple.com/design/human-interface-guidelines

---

## Section 1: Navigation Patterns

Three navigation models. Pick the right one — don't mix them at the same level.

### Tab Bar (parallel sections)
- Max 5 tabs. If you need more, use "More" tab with a list
- 49pt height + home indicator (34pt)
- Don't hide on scroll — users expect persistent access
- Each tab has its own independent `NavigationStack`
- Use SF Symbols for tab icons, label below

```swift
TabView {
  HomeView()
    .tabItem { Label("Home", systemImage: "house") }
  SearchView()
    .tabItem { Label("Search", systemImage: "magnifyingglass") }
  ProfileView()
    .tabItem { Label("Profile", systemImage: "person") }
}
```

### NavigationStack (hierarchical drill-down)
- Push/pop. Always show back button — never remove it
- Large title collapses on scroll (`.navigationBarTitleDisplayMode(.large)`)
- Use for: list → detail → sub-detail flows

```swift
NavigationStack {
  List(items) { item in
    NavigationLink(value: item) {
      ItemRow(item: item)
    }
  }
  .navigationTitle("Items")
  .navigationDestination(for: Item.self) { item in
    ItemDetail(item: item)
  }
}
```

### Modal Sheets (interrupting tasks)
- For self-contained tasks: compose, filter, settings, edit
- Three detent sizes: `.medium` (half), `.large` (full), custom
- Dismiss with swipe-down or explicit button
- Always provide a cancel/close action

```swift
.sheet(isPresented: $showCompose) {
  ComposeView()
    .presentationDetents([.medium, .large])
}
```

### When to use which

| Need | Use | Not |
|------|-----|-----|
| 2-5 parallel top-level sections | Tab bar | Hamburger menu |
| Master → detail hierarchy | NavigationStack | Custom navigation |
| Interrupting task (compose, edit) | `.sheet()` | Full-screen push |
| Destructive confirmation | `.alert()` | Custom dialog |
| Picking from options (iPad) | `.popover()` | Sheet |
| Picking from options (iPhone) | `.sheet()` or `.confirmationDialog()` | Popover |

---

## Section 2: Layout & Safe Areas

### Device dimensions

| Element | Height | Notes |
|---------|--------|-------|
| Status bar (Dynamic Island) | 59pt | iPhone 14 Pro+ |
| Status bar (notch) | 54pt | iPhone X–14 |
| Status bar (classic) | 20pt | iPhone SE |
| Navigation bar (standard) | 44pt | Below status bar |
| Navigation bar (large title) | 96pt | Collapses on scroll |
| Tab bar | 49pt | Above home indicator |
| Home indicator | 34pt | Bottom safe area |

### Safe area rules
- **Always** respect `.safeAreaInset` — never place interactive content behind system UI
- Use `ignoresSafeArea` only for decorative backgrounds, never for buttons or text
- Standard margins: 16pt on iPhone, 20pt on larger models (Pro Max)
- List row minimum height: 44pt

### Layout rules
- Use `GeometryReader` sparingly — prefer `frame`, `padding`, `Spacer`
- Support both portrait and landscape
- iPad: use `NavigationSplitView` (sidebar + detail), not tab bar
- Don't place content that competes with Dynamic Island / Live Activities

```swift
// Good: respects safe areas, uses standard spacing
VStack(spacing: 16) {
  HeaderView()
  ContentView()
  Spacer()
}
.padding(.horizontal, 16)

// Bad: ignores safe areas for interactive content
Button("Submit")
  .ignoresSafeArea()
```

---

## Section 3: Typography — Dynamic Type

SF Pro scale with default sizes. **Always use semantic styles, never hardcode sizes.**

| Style | Size | Weight | Use for |
|-------|------|--------|---------|
| `.largeTitle` | 34pt | Regular | Screen headers (first screen only) |
| `.title` | 28pt | Regular | Section headers |
| `.title2` | 22pt | Regular | Sub-section headers |
| `.title3` | 20pt | Regular | Tertiary headers |
| `.headline` | 17pt | Semibold | List row titles, emphasized body |
| `.body` | 17pt | Regular | Primary readable text |
| `.callout` | 16pt | Regular | Secondary descriptive text |
| `.subheadline` | 15pt | Regular | Metadata, tertiary text |
| `.footnote` | 13pt | Regular | Timestamps, captions |
| `.caption` | 12pt | Regular | Labels, annotations |
| `.caption2` | 11pt | Regular | Smallest readable text |

### Rules
- Use `.font(.body)`, `.font(.headline)` — never `.font(.system(size: 17))`
- Test with largest and smallest accessibility sizes (Settings → Accessibility → Larger Text)
- Max 2 font families (SF Pro + one brand font)
- Minimum readable size: 11pt
- Don't override system line spacing unless you have a specific reason

```swift
// Good: scales with Dynamic Type
Text("Welcome back")
  .font(.largeTitle)
Text("Your tasks for today")
  .font(.subheadline)
  .foregroundStyle(.secondary)

// Bad: hardcoded size, won't scale
Text("Welcome back")
  .font(.system(size: 34))
```

---

## Section 4: Color System

Semantic colors that auto-adapt to dark mode. **Always use these instead of hardcoded hex.**

### System backgrounds

| Color | Light | Dark | Use for |
|-------|-------|------|---------|
| `.background` | White | Black | Primary background |
| `.secondarySystemBackground` | #F2F2F7 | #1C1C1E | Grouped content background |
| `.tertiarySystemBackground` | White | #2C2C2E | Elevated cards, nested groups |

### System labels

| Color | Light | Dark | Use for |
|-------|-------|------|---------|
| `.primary` | Black | White | Primary text |
| `.secondary` | 60% gray | 60% light gray | Secondary text |
| `.tertiary` | 30% gray | 30% light gray | Placeholders, disabled |
| `.quaternary` | 18% gray | 18% light gray | Subtle fills |

### System accents
`.blue`, `.green`, `.red`, `.orange`, `.yellow`, `.pink`, `.purple`, `.teal`, `.indigo`, `.mint`, `.cyan`, `.brown`

### Rules
- Pick **one** accent color for interactive elements across the app (`.tint()`)
- 4.5:1 contrast ratio minimum for body text (WCAG AA)
- 3:1 contrast ratio for large text and interactive elements
- Dark mode: use elevated surfaces (lighter grays) for depth, don't just invert
- Never hardcode hex for system elements — use semantic colors

```swift
// Good: semantic, dark mode free
Text("Title")
  .foregroundStyle(.primary)
Text("Subtitle")
  .foregroundStyle(.secondary)
VStack { }
  .background(Color(.secondarySystemBackground))

// Bad: hardcoded, breaks in dark mode
Text("Title")
  .foregroundColor(Color(hex: "#000000"))
```

---

## Section 5: Touch & Interaction

### Tap targets
- **Minimum: 44×44pt** — apps get rejected for smaller targets
- Spacing between targets: at least 8pt
- Navigation bar buttons: 44pt touch area even if visually smaller
- Use `.contentShape(Rectangle())` to extend hit areas when needed

### Standard gestures — never override these

| Gesture | System behavior | Don't |
|---------|----------------|-------|
| Tap | Primary action | — |
| Long press | Context menu | Use for primary actions |
| Swipe left edge | Back navigation | Disable this |
| Swipe on list row | Quick actions (delete, pin) | Use for navigation |
| Pull down | Refresh | Use for other things |
| Pinch | Zoom (maps, photos) | Use for non-zoom |

### Haptic feedback

```swift
// Button tap, toggle
UIImpactFeedbackGenerator(style: .light).impactOccurred()

// Snapping, selection change
UIImpactFeedbackGenerator(style: .medium).impactOccurred()

// Task completed
UINotificationFeedbackGenerator().notificationOccurred(.success)

// Error
UINotificationFeedbackGenerator().notificationOccurred(.error)

// Scrolling through picker values
UISelectionFeedbackGenerator().selectionChanged()
```

### Rules
- Always provide visual feedback on tap (opacity, scale, or highlight)
- Don't create custom gestures for things system gestures already handle
- Avoid gesture conflicts — scrolling view + horizontal swipe = frustration
- `.contextMenu` for long press menus, `.swipeActions` for list row actions

```swift
// Swipe actions on list rows
List {
  ForEach(items) { item in
    ItemRow(item: item)
      .swipeActions(edge: .trailing) {
        Button(role: .destructive) { delete(item) } label: {
          Label("Delete", systemImage: "trash")
        }
      }
      .swipeActions(edge: .leading) {
        Button { pin(item) } label: {
          Label("Pin", systemImage: "pin")
        }
        .tint(.orange)
      }
  }
}
```

---

## Section 6: Motion & Animation

iOS uses **spring physics**, not CSS easing. Springs feel natural — linear and ease-in-out feel mechanical.

### Standard springs

```swift
// Default — use for most UI animations
withAnimation(.spring(response: 0.35, dampingFraction: 0.85)) {
  showDetail = true
}

// Quick feedback — toggles, button states
withAnimation(.spring(response: 0.25, dampingFraction: 0.9)) {
  isSelected.toggle()
}

// Dramatic entrance — onboarding, celebrations
withAnimation(.spring(response: 0.5, dampingFraction: 0.7)) {
  showWelcome = true
}

// Subtle — opacity, color changes
withAnimation(.easeOut(duration: 0.2)) {
  opacity = 1
}
```

### System transitions (don't recreate these)

| Transition | Behavior | Duration |
|-----------|----------|----------|
| Navigation push | Slide from right | 0.35s (system) |
| Navigation pop | Slide to right | 0.35s (system) |
| Sheet present | Slide up with spring | ~0.4s (system) |
| Sheet dismiss | Slide down | ~0.3s (system) |
| Alert | Fade + slight scale | ~0.2s (system) |
| Tab switch | Cross-fade (instant) | No animation |

### Shared element transitions

```swift
@Namespace var heroAnimation

// Source view (e.g., thumbnail in list)
Image("photo")
  .matchedGeometryEffect(id: "hero", in: heroAnimation)

// Destination view (e.g., full-screen detail)
Image("photo")
  .matchedGeometryEffect(id: "hero", in: heroAnimation)
```

### Rules
- Keep animations under 0.4s — longer feels sluggish
- Use `withAnimation` for state-driven animations
- Use `.animation(.spring(), value: someValue)` for view-specific animations
- Don't animate layout changes that cause content to jump
- Loading states: `.redacted(reason: .placeholder)` for skeleton screens
- Progress: `ProgressView()` for indeterminate, `ProgressView(value: 0.5)` for determinate
- Never use `.linear` for UI animation — it feels robotic

```swift
// Skeleton loading state
VStack {
  Text("Loading title")
  Text("Loading description that is longer")
}
.redacted(reason: .placeholder)
```

---

## Section 7: Components & Common Patterns

### Always use system components when possible
They get Dark Mode, Dynamic Type, and accessibility for free.

| Need | Use | Not |
|------|-----|-----|
| Scrollable list | `List` | `ScrollView` + `VStack` |
| Form / settings | `Form` | Custom layout |
| Navigation hierarchy | `NavigationStack` | Custom navigation |
| Tab switching | `TabView` | Custom tab bar |
| Modal task | `.sheet()` | Custom overlay |
| Confirmation | `.alert()` | Custom dialog |
| Quick actions | `.contextMenu` | Custom long-press |
| Pull to refresh | `.refreshable` | Custom gesture |
| Search | `.searchable` | Custom text field |
| Share | `ShareLink` | Custom share sheet |
| Date/time input | `DatePicker` | Custom picker |
| Toggle on/off | `Toggle` | Custom switch |
| Pick one from list | `Picker` | Custom radio buttons |

### SF Symbols
- 5000+ icons built into iOS — use these before custom assets
- Auto-scale with Dynamic Type
- Match symbol weight to nearby text weight
- Four rendering modes: `.monochrome`, `.hierarchical`, `.palette`, `.multicolor`

```swift
// Basic usage
Image(systemName: "heart.fill")
  .symbolRenderingMode(.hierarchical)
  .foregroundStyle(.red)

// In a label (icon + text, properly aligned)
Label("Favorites", systemImage: "heart.fill")
```

### Empty states
Every list and content area needs an empty state — don't show a blank screen.

```swift
if items.isEmpty {
  ContentUnavailableView(
    "No Items",
    systemImage: "tray",
    description: Text("Items you add will appear here.")
  )
}
```

### App Store rejection — common causes
1. Tap targets under 44pt
2. No Dynamic Type support
3. Custom back button that breaks swipe-back gesture
4. Missing dark mode support (hardcoded colors)
5. Loading spinners instead of skeleton/placeholder content
6. Using alerts for non-destructive choices (should be sheet or action sheet)
7. Horizontal scrolling that conflicts with edge-swipe back
8. No empty states — blank screens with no guidance
9. Ignoring safe areas — content behind notch or home indicator

---

_Source: [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines) · Condensed for Ship Framework agent reference_

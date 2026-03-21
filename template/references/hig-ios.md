# Apple Human Interface Guidelines — iOS/SwiftUI Reference

> **When to read:** Arc reads Sections 1, 4, 7-8 when planning screen maps for iOS/SwiftUI projects.
> Dev reads Sections 2-6, 8-9 when building iOS UI. Eye reads Sections 7 + 10 when reviewing.
> Section 9 deepens Sections 2-4 with extended typography, color, dark mode, materials, images, and layout specs.
> Section 10 has design review checklists for Eye agent.
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

## Section 8: App Lifecycle & Patterns

iOS-specific patterns for onboarding, accounts, notifications, multitasking,
settings, help, and haptics best practices.

### Onboarding

- Delay sign-in until the user has seen value — don't gate the first screen
- Request permissions only at the moment they're needed, with context explaining why
- Teach through interactivity, not instruction carousels — let users try features
- Use `TipKit` for contextual feature discovery (popover, annotation, or hint style)
- Tips should be 1-2 sentences max, action-oriented, with display frequency rules
- If a feature needs more than 3 steps to explain, it's too complex for a tip

```swift
// TipKit: contextual tip for a feature
struct FavoritesTip: Tip {
  var title: Text { Text("Save Favorites") }
  var message: Text? { Text("Tap the heart to save items you love.") }
  var image: Image? { Image(systemName: "heart.fill") }
}
```

### Managing Accounts

- Support Sign in with Apple and passkeys — always offer these first
- Delay account creation until a feature requires it
- Prefill from system data: name, email from Apple ID when authorized
- Verify email addresses by sending a code — don't make users retype
- Provide clear sign-out and account deletion options (App Store requirement)

### Notifications

Four interruption levels — use the right one:

| Level | Behavior | Use for |
|-------|----------|---------|
| **Passive** | Silently added to list | Background updates, recommendations |
| **Active** (default) | Appears on lock screen, respects Focus | Most notifications |
| **Time Sensitive** | Breaks through Focus for 1 hour | Delivery arriving, account security |
| **Critical** | Always plays sound, bypasses all | Health alerts, safety warnings (requires entitlement) |

**Rules:**
- Never use Time Sensitive for marketing or non-urgent content
- Always send an initial notification before requesting push permission
- Let users customize which notification types they receive in-app
- Update badge counts to reflect actionable items, not total unread
- Group related notifications with `threadIdentifier`

### Multitasking

- Save and restore state — users expect to return exactly where they left off
- Pause attention-requiring activities (games, video) when user switches away
- Resume seamlessly on return — don't show splash screens or reload from scratch
- Finish user-initiated background tasks (downloads, uploads, processing)
- Handle audio interruptions: pause for primary (calls), duck for secondary (GPS)
- Use notifications sparingly for background task completion — only for important/time-sensitive tasks

```swift
// Save state on background
func sceneDidEnterBackground(_ scene: UIScene) {
  saveCurrentState()
}

// Restore state on foreground
func sceneWillEnterForeground(_ scene: UIScene) {
  restoreLastState()
}
```

### Settings

- Aim for zero settings — smart defaults that work for most users
- Put rarely changed options in a settings screen (appearance, account, notifications)
- Put task-specific options in context — sort, filter, and view toggles belong in the screen they affect
- Support `Command-Comma (⌘,)` keyboard shortcut for settings when a keyboard is connected
- Respect systemwide settings — don't duplicate system toggles (Dark Mode, text size, etc.)
- Auto-detect what you can: connected peripherals, current appearance, device capabilities

### Haptics — Extended Patterns

Expanding on Section 5's basics — use the right pattern for the right meaning:

| Pattern | Weight | Use for |
|---------|--------|---------|
| **Impact Light** | Subtle | Small UI collisions, toggles |
| **Impact Medium** | Moderate | Snapping into place, selection |
| **Impact Heavy** | Strong | Large collisions, significant state changes |
| **Impact Rigid** | Sharp | Hard surface collisions |
| **Impact Soft** | Gentle | Flexible/organic collisions |
| **Notification Success** | Double pulse | Task completed, check deposited |
| **Notification Warning** | Attention | Approaching limit, unusual activity |
| **Notification Error** | Triple pulse | Action failed, invalid input |
| **Selection Changed** | Tick | Scrolling picker, segment change |

**Rules:**
- Use standard haptic patterns for their documented meanings — don't repurpose
- Synchronize haptics with animations — the tactile and visual must match
- Avoid overusing haptics — occasional and meaningful beats constant buzzing
- Always make haptics optional (users can disable in system settings)
- Short, discrete haptics for apps; continuous haptics only for games

### Charting Data — Swift Charts

Use Apple's `Charts` framework (iOS 16+) instead of building custom chart views.

```swift
import Charts

// Basic bar chart
Chart(salesData) { item in
  BarMark(
    x: .value("Month", item.month),
    y: .value("Revenue", item.revenue)
  )
  .foregroundStyle(by: .value("Category", item.category))
}
.chartXAxisLabel("Month")
.chartYAxisLabel("Revenue ($)")
```

**Mark types:** `BarMark`, `LineMark`, `PointMark`, `AreaMark`, `RuleMark`, `RectangleMark`

**Rules:**
- One insight per chart — don't pack multiple stories into one visualization
- Use `foregroundStyle(by:)` for category differentiation — uses system colors automatically
- Add `.chartXAxisLabel` / `.chartYAxisLabel` for context
- Provide accessibility labels: `.accessibilityLabel()` on each mark or use `AXChartDescriptor`
- Keep consistent chart types across your app — don't use bar in one view and line in another for the same data
- Let users reveal detail on demand with `.chartOverlay` for interactive inspection
- Small charts (widgets, glanceable) → remove axes, show only the shape + a summary label
- Full charts → include axes, labels, annotations, and support Dynamic Type in all text

```swift
// Accessible chart with interactive overlay
Chart(data) { item in
  LineMark(
    x: .value("Date", item.date),
    y: .value("Steps", item.steps)
  )
  .accessibilityLabel("\(item.date.formatted()): \(item.steps) steps")
}
.chartOverlay { proxy in
  // tap/drag to inspect individual data points
}
```

---

## Section 9: Foundations

Deep iOS-specific specs from Apple's HIG foundation pages. Supplements
Sections 3-4 (typography, color) with additional rules and fills gaps
on dark mode, materials, images, and layout.

### Typography — Extended Rules

Builds on Section 3's Dynamic Type scale.

**Minimum sizes per platform:**

| Platform | Default size | Minimum size |
|----------|-------------|-------------|
| iOS/iPadOS | 17pt | 11pt |
| macOS | 13pt | 10pt |
| watchOS | 16pt | 12pt |

**Rules:**
- Avoid light, ultralight, and thin font weights — prefer Regular, Medium, Semibold, Bold
- Max 2 font families (SF Pro + one brand font). More than 2 obscures hierarchy
- Emphasized variants: use `.bold()` modifier, not a heavier font — system maps to correct emphasized weight per style
- Use loose leading for wide columns/long passages, tight leading for constrained height — but never tight leading for 3+ lines
- Custom fonts must implement Dynamic Type: use `UIFontMetrics` to scale custom sizes
- Test with largest accessibility size (AX5) and smallest (xSmall) — verify no truncation in scrollable areas
- At large font sizes, switch horizontal layouts to stacked (vertical) to avoid truncation
- Use `Font.Design.default` for SF Pro, `Font.Design.serif` for New York — never embed system fonts in your app bundle

```swift
// Scale custom font with Dynamic Type
let customFont = UIFont(name: "BrandFont-Regular", size: 17)!
let scaledFont = UIFontMetrics(forTextStyle: .body).scaledFont(for: customFont)
label.font = scaledFont
label.adjustsFontForContentSizeCategory = true
```

### Color — Extended Rules

Builds on Section 4's semantic colors.

**iOS background hierarchy (system vs grouped):**

| Set | Use for | Primary | Secondary | Tertiary |
|-----|---------|---------|-----------|----------|
| **System** | Flat lists, content views | `systemBackground` | `secondarySystemBackground` | `tertiarySystemBackground` |
| **Grouped** | Grouped tables, forms | `systemGroupedBackground` | `secondarySystemGroupedBackground` | `tertiarySystemGroupedBackground` |

Use grouped backgrounds with `Form` and grouped `List` styles. Use system backgrounds for flat content.

**Foreground colors:**

| Color | Use for |
|-------|---------|
| `.label` | Primary content text |
| `.secondaryLabel` | Subtitles, metadata |
| `.tertiaryLabel` | Placeholders, disabled |
| `.quaternaryLabel` | Subtle fills |
| `.link` | Tappable text links |
| `.separator` | Translucent dividers |
| `.opaqueSeparator` | Opaque dividers |

**Liquid Glass color (iOS 26+):**
- Liquid Glass has no inherent color — it picks up from content behind it
- Apply color sparingly: reserve for primary actions (like Done button)
- System applies accent color to prominent button backgrounds — don't color multiple controls
- Symbols/text on Liquid Glass: prefer monochromatic, colored only for status indicators
- Colorful app backgrounds: prefer monochromatic toolbar/tab bar appearance

**Contrast rules:**
- 4.5:1 minimum for body text (WCAG AA)
- 3:1 minimum for 18pt+ text or bold text
- 7:1 ideal for custom foreground/background pairs
- Always supply increased-contrast variants for custom colors
- Test with Increase Contrast setting on, in both light and dark modes

### Dark Mode — Rules

**Core rules:**
- Never offer an app-specific dark mode toggle — respect the system setting
- iOS uses two background sets: **base** (dimmer, background) and **elevated** (brighter, foreground like sheets/popovers)
- System automatically switches base → elevated for foreground interfaces (sheets, multitasking)
- Use system background colors to get this behavior for free — custom backgrounds lose it
- Test with both Increase Contrast and Reduce Transparency turned on (separately and together)
- Soften white backgrounds in images to prevent glowing against dark surroundings
- Dark mode colors are not simple inversions — some colors stay the same, some shift

```swift
// Good: system background auto-adapts to base/elevated
VStack { content }
  .background(Color(.systemBackground))

// Bad: custom color doesn't adapt to elevation context
VStack { content }
  .background(Color(hex: "#000000"))
```

### Materials (iOS)

**Liquid Glass (iOS 26+):**
- Forms a distinct layer for controls/navigation above the content layer
- Content scrolls and peeks through — provides depth and dynamism
- Don't use Liquid Glass in the content layer — only for controls and navigation
- Standard components pick it up automatically — apply to custom controls sparingly
- Two variants: **regular** (blurred, for text-heavy elements like alerts/sidebars) and **clear** (translucent, for media backgrounds)
- Clear variant over bright content: add dark dimming layer at 35% opacity

**Standard materials (content layer):**

| Material | Opacity | Use for |
|----------|---------|---------|
| Ultra-thin | Most translucent | Background with visible content behind |
| Thin | — | Light overlay |
| Regular (default) | — | Standard overlay |
| Thick | Most opaque | High contrast needed |

- Use vibrant colors on top of materials for legibility
- Don't pick material by its apparent color — use semantic purpose

### Images — Asset Rules

**Scale factors:**

| Platform | Required |
|----------|----------|
| iOS | @2x and @3x |
| iPadOS | @2x |
| watchOS | @2x |
| macOS | @1x and @2x |

**Rules:**
- Provide high-resolution assets for all bitmap images — missing @3x looks blurry on Pro/Max iPhones
- Design at lowest resolution, scale up — control points at whole values for clean @1x alignment
- Include color profiles with every image (sRGB for standard, Display P3 for wide gamut)
- Use SVG or PDF for flat icons and interface graphics — they scale without artifacts
- Use PNG for bitmap/raster work, JPEG/HEIC for photos
- Test images on actual devices — Simulator doesn't show resolution issues accurately
- SF Symbols preferred over custom icon assets (5000+ icons, auto-scale with Dynamic Type)

### Layout — Extended Rules

Builds on Section 2's safe areas and device dimensions.

**Size classes (determines layout adaptation):**

| Device | Portrait | Landscape |
|--------|----------|-----------|
| iPhone (standard) | Compact width, Regular height | Compact width, Compact height |
| iPhone (Plus/Max) | Compact width, Regular height | Regular width, Compact height |
| iPad (all) | Regular width, Regular height | Regular width, Regular height |

**Rules:**
- Design for compact width first, adapt up to regular width
- Use `@Environment(\.horizontalSizeClass)` to switch layouts
- iPad: use `NavigationSplitView`, support resizable windows — defer switching to compact view as long as possible
- iPad convertible tab bar: adopts sidebar appearance when space allows (`sidebarAdaptable` style)
- Full-bleed: backgrounds and artwork extend to screen edges — content scrolls under bars
- Avoid full-width buttons on iPhone — inset from edges, respect system margins and corner radius
- Hide status bar only when it adds value (games, media playback) — keep visible otherwise
- Support both portrait and landscape — if only one orientation, support both rotation directions
- Use `backgroundExtensionEffect()` to extend content behind sidebars/inspectors (iOS 26+)

```swift
// Adapt layout based on size class
@Environment(\.horizontalSizeClass) var sizeClass

var body: some View {
  if sizeClass == .compact {
    TabView { /* phone layout */ }
  } else {
    NavigationSplitView { /* iPad sidebar layout */ }
  }
}
```

---

## Section 10: Design Review Checklists

Consolidated HIG-level checklists for Eye agent during `/review`. These check design
compliance — for code-level implementation checklists, see `swiftui-core.md` Section 9.

### Navigation
- [ ] Correct navigation model chosen (Tab Bar, Stack, or Flat) — not mixed at same level
- [ ] Tab bar has max 5 tabs, each with SF Symbol icon + label
- [ ] Back button always visible in push navigation
- [ ] Large title collapses on scroll where appropriate
- [ ] NavigationSplitView used for iPad sidebar layouts
- [ ] Deep links handled with `.onOpenURL`

### Typography
- [ ] Dynamic Type supported — all text scales with system setting
- [ ] No text smaller than 11pt on iOS
- [ ] Max 2 font families (SF Pro + one brand font)
- [ ] Custom fonts scale via `UIFontMetrics`
- [ ] Tested with largest accessibility size (AX5) and smallest (xSmall)
- [ ] At large font sizes, horizontal layouts switch to stacked vertical

### Color
- [ ] Semantic colors used (`Color(.label)`, `Color(.systemBackground)`, etc.)
- [ ] System backgrounds match style: grouped for forms/lists, system for flat content
- [ ] 4.5:1 contrast ratio for body text, 3:1 for 18pt+ or bold
- [ ] Increased-contrast variants provided for custom colors
- [ ] Liquid Glass color applied sparingly — reserve for primary actions
- [ ] Tested in both light and dark modes with Increase Contrast on

### Touch & Interaction
- [ ] All tap targets minimum 44×44pt
- [ ] Primary actions in thumb zone (bottom half of screen)
- [ ] Destructive actions require confirmation
- [ ] Swipe actions discoverable and reversible
- [ ] Haptics match their documented meanings — not repurposed

### Materials & Liquid Glass
- [ ] Liquid Glass used only for controls/navigation, not content layer
- [ ] Standard components (tab bar, toolbar, nav bar) use automatic glass
- [ ] Custom glass applied sparingly — not on every surface
- [ ] `if #available(iOS 26, *)` with fallback UI
- [ ] Tested with Reduce Transparency enabled

### Accessibility
- [ ] VoiceOver labels on all interactive elements
- [ ] Meaningful accessibility hints for non-obvious controls
- [ ] Images have accessibility labels or are marked decorative
- [ ] Reduce Motion respected — alternative animations provided
- [ ] Reduce Transparency respected — content remains readable
- [ ] Keyboard navigation works for all flows (iPad + external keyboard)

### App Lifecycle
- [ ] State saved on background, restored on foreground
- [ ] Permissions requested in context with explanation — not on first launch
- [ ] Notifications use correct interruption level (not Time Sensitive for marketing)
- [ ] Sign in with Apple offered first when auth is needed
- [ ] Account deletion option available (App Store requirement)

---

_Source: [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines) · Condensed for Ship Framework agent reference_

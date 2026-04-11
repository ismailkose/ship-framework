# TipKit — iOS Reference

> **When to read:** Dev reads this when adding feature discovery tooltips, onboarding flows, contextual tips, first-run experiences, coach marks, or working with Tip protocol, TipView, popoverTip, tip rules, tip events, or feature education UI.

---

## Triage
- **Implement new feature** → Read Setup + Defining Tips + Displaying Tips
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `Tip` protocol | Define a feature discovery tip | Requires `title`; optional `message`, `image`, `actions`, `rules`, `options` |
| `TipView` | Inline tip display | Renders as rounded card; appears with animation |
| `popoverTip()` | Popover tip modifier | Anchored to view with arrow; optional `arrowEdge` control |
| `@Parameter` | Parameter-based rule | Track app state; rule fires when value satisfies condition |
| `Tips.Event` | Event-based rule | Track user actions; rule fires when donation count/timing met |
| `TipGroup` | Coordinate multiple tips | Ensures only one tip displays at a time; priority ordering |
| `Tips.configure()` | Initialize TipKit | Must be called in `App.init` before views render |
| `LanguageAvailability` | Check language support | Returns `.installed`, `.supported`, or `.unsupported` |
| `TipViewStyle` | Custom tip appearance | Conform and implement `makeBody(configuration:)` |

## Code Examples

### 1. Basic Tip Definition

```swift
import TipKit

struct FavoriteTip: Tip {
    var title: Text { Text("Pin Your Favorites") }
    var message: Text? { Text("Tap the heart icon to save items for quick access.") }
    var image: Image? { Image(systemName: "heart") }
}
```

### 2. Configure TipKit in App.init

```swift
@main
struct MyApp: App {
    init() {
        try? Tips.configure([
            .datastoreLocation(.applicationDefault)
        ])
    }

    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

### 3. Display Inline Tip with TipView

```swift
let favoriteTip = FavoriteTip()

var body: some View {
    VStack {
        TipView(favoriteTip)
        ItemListView()
    }
}
```

### 4. Display Popover Tip

```swift
Button { toggleFavorite() } label: { Image(systemName: "heart") }
    .popoverTip(favoriteTip)

// Control arrow direction
.popoverTip(favoriteTip, arrowEdge: .bottom)
```

### 5. Parameter-Based Rule

```swift
struct FavoriteTip: Tip {
    @Parameter
    static var hasSeenList: Bool = false

    var title: Text { Text("Pin Your Favorites") }

    var rules: [Rule] {
        #Rule(Self.$hasSeenList) { $0 == true }
    }
}

// Set the parameter when the user reaches the list
FavoriteTip.hasSeenList = true
```

### 6. Event-Based Rule

```swift
struct ShortcutTip: Tip {
    static let appOpenedEvent = Tips.Event(id: "appOpened")

    var title: Text { Text("Try the Quick Action") }

    var rules: [Rule] {
        #Rule(Self.appOpenedEvent) { $0.donations.count >= 3 }
    }
}

// Donate each time the app opens
ShortcutTip.appOpenedEvent.donate()
```

### 7. Multiple Rules (Logical AND)

```swift
struct AdvancedTip: Tip {
    @Parameter
    static var isLoggedIn: Bool = false

    static let featureUsedEvent = Tips.Event(id: "featureUsed")

    var title: Text { Text("Unlock Advanced Mode") }

    var rules: [Rule] {
        #Rule(Self.$isLoggedIn) { $0 == true }
        #Rule(Self.featureUsedEvent) { $0.donations.count >= 5 }
    }
}
```

### 8. Display Frequency Options

```swift
struct DailyTip: Tip {
    var title: Text { Text("Daily Reminder") }

    var options: [TipOption] {
        MaxDisplayCount(3)
        IgnoresDisplayFrequency(true)
    }
}
```

### 9. Configure Global Display Frequency

```swift
try? Tips.configure([
    .displayFrequency(.daily)  // .immediate, .hourly, .daily, .weekly, .monthly
])
```

### 10. Tip Actions

```swift
struct FeatureTip: Tip {
    var title: Text { Text("Try the New Editor") }
    var message: Text? { Text("We added a powerful new editing mode.") }

    var actions: [Action] {
        Action(id: "open-editor", title: "Open Editor")
        Action(id: "learn-more", title: "Learn More")
    }
}

// Handle actions
TipView(featureTip) { action in
    switch action.id {
    case "open-editor":
        navigateToEditor()
        featureTip.invalidate(reason: .actionPerformed)
    case "learn-more":
        showHelpSheet = true
    default:
        break
    }
}
```

### 11. Custom TipViewStyle

```swift
struct CustomTipStyle: TipViewStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack(spacing: 12) {
            configuration.image?
                .font(.title2)
                .foregroundStyle(.tint)

            VStack(alignment: .leading, spacing: 4) {
                configuration.title
                    .font(.headline)
                configuration.message?
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
    }
}

// Apply globally
TipView(favoriteTip)
    .tipViewStyle(CustomTipStyle())
```

### 12. TipGroup for Sequential Tips

```swift
struct OnboardingView: View {
    let tipGroup = TipGroup(.ordered) {
        WelcomeTip()
        NavigationTip()
        ProfileTip()
    }

    var body: some View {
        VStack {
            if let currentTip = tipGroup.currentTip {
                TipView(currentTip)
            }

            Button("Next") {
                tipGroup.currentTip?.invalidate(reason: .actionPerformed)
            }
        }
    }
}
```

### 13. Invalidate Tips Programmatically

```swift
let tip = FavoriteTip()
tip.invalidate(reason: .actionPerformed)
// Other reasons: .displayCountExceeded, .tipClosed
```

### 14. Testing: Show All Tips

```swift
#if DEBUG
Tips.showAllTipsForTesting()
#endif
```

### 15. Testing: Show Specific Tips

```swift
#if DEBUG
Tips.showTipsForTesting([FavoriteTip.self, ShortcutTip.self])
#endif
```

### 16. Testing: Hide All Tips

```swift
#if DEBUG
Tips.hideAllTipsForTesting()
#endif
```

### 17. Testing: Reset Datastore

```swift
#if DEBUG
try? Tips.resetDatastore()
#endif
```

### 18. Testing: ProcessInfo Launch Arguments

```swift
if ProcessInfo.processInfo.arguments.contains("--show-all-tips") {
    Tips.showAllTipsForTesting()
}
```

### 19. CloudKit Sync Configuration

```swift
try? Tips.configure([
    .datastoreLocation(.applicationDefault),
    .cloudKitContainer(.named("iCloud.com.example.app"))
])
```

### 20. Datastore Location Options

```swift
try? Tips.configure([
    .datastoreLocation(.applicationDefault)           // App sandbox
    .datastoreLocation(.groupContainer(identifier: "group.com.example"))  // Shared
    .datastoreLocation(.url(customPath))              // Custom URL
])
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Call `Tips.configure()` in view's `onAppear` | Always call in `App.init` before views render |
| Show multiple tips simultaneously | Use `TipGroup` to sequence tips; show one at a time |
| Forget to invalidate tip after user performs action | Call `invalidate(reason: .actionPerformed)` when action happens |
| Leave testing utilities enabled in production | Gate behind `#if DEBUG` — `showAllTipsForTesting()` bypasses rules |
| Make tip titles too long | Keep titles under ~40 characters; use message for details |
| Use tips for critical information | Tips are dismissible; use alerts for safety-critical info |
| Concurrent requests on one session | Check `session.isResponding` or serialize access |

## Review Checklist

- [ ] `Tips.configure()` called in `App.init`, before any views render
- [ ] Each tip has a clear, concise title (action-oriented, under ~40 characters)
- [ ] Tips invalidated when the user performs the discovered action
- [ ] Rules set so tips appear at the right time (not immediately on first launch for all tips)
- [ ] `TipGroup` used when multiple tips exist in one view
- [ ] Testing utilities (`showAllTipsForTesting`, `resetDatastore`) gated behind `#if DEBUG`
- [ ] CloudKit sync configured if the app supports multiple devices
- [ ] Display frequency set appropriately (`.daily` or `.weekly` for most apps)
- [ ] Tips used for feature discovery only, not for critical information
- [ ] Custom `TipViewStyle` applied consistently if the default style does not match the app design
- [ ] Tip actions handled and tip invalidated in the action handler
- [ ] Event donations placed at the correct user action points
- [ ] Ensure custom Tip types are Sendable; configure Tips on @MainActor

---

_Source: swift-ios-skills · Adapted for Ship Framework agent reference_

# App Intents — iOS Reference

> **When to read:** Dev reads this when building Siri shortcuts, Spotlight suggestions, or app action integrations.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `AppIntent` | Protocol for executable app actions | Implement `perform() async throws` |
| `@Parameter` | Input property for intent | Optional/default, supports validation |
| `IntentResult` | Success or failure outcome | Returns data or error message |
| `AppEntity` | Shadow model for intent data | Never conform core models directly |
| `EntityQuery` | Resolve entities by ID | Base variant for custom resolution |
| `EntityStringQuery` | Free-text search entities | Full-text search support |
| `EnumerableEntityQuery` | Finite entity set | Query all items (e.g., all songs) |
| `UniqueAppEntityQuery` (iOS 18+) | Singleton entity | Single-instance (e.g., app settings) |
| `EntityPropertyQuery` (iOS 18+) | Filter/sort entities | Advanced queries with predicates |
| `AppEnum` | Fixed value choices | Must use `String` raw value |
| `AppShortcut` | Declares available shortcuts | Defines phrases for Siri |
| `AppShortcutsProvider` | Registers shortcuts | Shortcut phrase & intent mapping |
| `ControlConfigurationIntent` (iOS 18+) | Control Center config | Setup for ControlWidget |
| `WidgetConfigurationIntent` (iOS 17+) | Widget configuration | Widget settings intent |
| `IndexedEntity` (iOS 18+) | Spotlight searchable | With `@Property(indexingKey:)` (iOS 26+) |
| `SnippetIntent` (iOS 26+) | Interactive snippets | Display UI inline in system |
| `IntentValueQuery` (iOS 26+) | Visual Intelligence | Query entities from visual context |

## Code Examples

```swift
// 1. Simple AppIntent with parameters
import AppIntents

struct CreateReminderIntent: AppIntent {
    static var title: LocalizedStringResource = "Create Reminder"
    static var description: LocalizedStringResource = "Add a new reminder to your list"
    static var openAppWhenRun = true

    @Parameter(title: "Reminder Text", description: "What should the reminder say?")
    var reminderText: String

    @Parameter(title: "Priority", description: "How important is this?")
    var priority: Priority = .normal

    enum Priority: String, AppEnum {
        case low = "Low"
        case normal = "Normal"
        case high = "High"

        static var typeDisplayRepresentation: TypeDisplayRepresentation = "Priority"
        static var caseDisplayRepresentations: [Priority: DisplayRepresentation] = [
            .low: "Low",
            .normal: "Normal",
            .high: "High"
        ]
    }

    func perform() async throws -> some IntentResult {
        // Implement reminder creation logic
        let reminder = Reminder(text: reminderText, priority: priority)
        try await ReminderStore.shared.add(reminder)

        return .result(
            value: reminder,
            view: ReminderResultView(reminder: reminder)
        )
    }
}

// 2. Define AppShortcuts for Siri
struct MyAppShortcuts: AppShortcutsProvider {
    static var shortcutTileDisplayRepresentation: ShortcutTileDisplayRepresentation {
        ShortcutTileDisplayRepresentation(title: "My App Shortcuts")
    }

    static var shortcuts: [AppShortcut] {
        AppShortcut(
            intent: CreateReminderIntent(),
            phrases: [
                "Create a reminder in <app-name>",
                "Add a <#reminder text#> reminder in <app-name>"
            ]
        )
        AppShortcut(
            intent: ListRemindersIntent(),
            phrases: [
                "Show my reminders in <app-name>"
            ]
        )
    }
}

// 3. Query intent with result selection
struct ListRemindersIntent: AppIntent {
    static var title: LocalizedStringResource = "List Reminders"
    static var openAppWhenRun = false

    @Parameter(title: "Filter by Priority")
    var priority: CreateReminderIntent.Priority?

    func perform() async throws -> some IntentResult & ReturnsValue<[Reminder]> {
        let reminders = try await ReminderStore.shared.fetchAll()
        let filtered = priority.map { p in
            reminders.filter { $0.priority.rawValue == p.rawValue }
        } ?? reminders

        return .result(value: filtered)
    }
}

// 4. Implement Spotlight searchable item
struct SearchableReminderItem: AppIntentSearchableItem {
    let reminder: Reminder

    var id: String { reminder.id.uuidString }
    var displayString: String { reminder.text }
    var displayImage: Image? { Image(systemName: "checkmark.circle") }

    static var defaultQuery: SearchableItemQuery<SearchableReminderItem> {
        SearchableItemQuery(
            matching: { item, string in
                item.reminder.text.localizedCaseInsensitiveContains(string)
            },
            sortBy: { [$0.reminder.createdDate < $1.reminder.createdDate] }
        )
    }

    var attributes: AppIntentSearchableItemAttributeScopes {
        AppIntentSearchableItemAttributeScopes(
            text: .init(content: reminder.text),
            keywords: ["reminder", "task", "todo"]
        )
    }

    func perform() async throws -> some IntentResult {
        return .result(
            value: reminder,
            view: ReminderDetailView(reminder: reminder)
        )
    }
}

// 5. Register searchable items in app
class AppSearchDelegate: NSObject, AppIntentSearchableItemsProvider {
    func searchableItems() async throws -> [AppIntentSearchableItem] {
        let reminders = try await ReminderStore.shared.fetchAll()
        return reminders.map { SearchableReminderItem(reminder: $0) }
    }
}

// 6. UniqueAppEntityQuery for singleton (iOS 18+)
struct AppSettingsEntity: UniqueAppEntity {
    static let defaultQuery = AppSettingsQuery()
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Settings"
    var displayRepresentation: DisplayRepresentation { "App Settings" }
    var id: String { "app-settings" }
}

struct AppSettingsQuery: UniqueAppEntityQuery {
    func entity() async throws -> AppSettingsEntity {
        AppSettingsEntity()
    }
}

// 7. IndexedEntity with property indexing (iOS 26+)
struct RecipeEntity: IndexedEntity {
    static let defaultQuery = RecipeQuery()
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Recipe"
    var id: String

    @Property(title: "Name", indexingKey: .title) var name: String       // iOS 26+
    @ComputedProperty(indexingKey: .description)                         // iOS 26+
    var summary: String { "\(name) -- delicious" }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)")
    }
}

// 8. SnippetIntent (iOS 26+)
struct OrderStatusSnippet: SnippetIntent {
    static var title: LocalizedStringResource = "Order Status"
    func perform() async throws -> some IntentResult & ShowsSnippetView {
        let status = await OrderTracker.currentStatus()
        return .result(view: OrderStatusSnippetView(status: status))
    }
    static func reload() { /* notify system to refresh */ }
}

// 9. IntentValueQuery for Visual Intelligence (iOS 26+)
struct ProductValueQuery: IntentValueQuery {
    typealias Input = String
    typealias Result = ProductEntity
    func values(for input: String) async throws -> [ProductEntity] {
        ProductStore.shared.search(input).map { ProductEntity(from: $0) }
    }
}

// 10. ControlConfigurationIntent (iOS 18+)
struct LightControlConfig: ControlConfigurationIntent {
    static var title: LocalizedStringResource = "Light Control"
    @Parameter(title: "Light", default: .livingRoom) var light: LightEntity
}

struct ToggleLightIntent: AppIntent {
    static var title: LocalizedStringResource = "Toggle Light"
    @Parameter(title: "Light") var light: LightEntity
    func perform() async throws -> some IntentResult {
        try await LightService.shared.toggle(light.id)
        return .result()
    }
}

// 11. Result view for intent completion
struct ReminderResultView: View {
    let reminder: Reminder

    var body: some View {
        VStack(alignment: .leading) {
            Text("Reminder Created")
                .font(.headline)
            Text(reminder.text)
                .font(.body)
                .foregroundColor(.secondary)
            HStack {
                Label("Priority", systemImage: "star.fill")
                Text(reminder.priority.rawValue)
            }
            .font(.caption)
        }
        .padding()
    }
}
```

### @Parameter UI Customization

```swift
// Numeric slider
@Parameter(title: "Volume", controlStyle: .slider, inclusiveRange: (0, 100))
var volume: Int

// Options provider (dynamic list)
@Parameter(title: "Category", optionsProvider: CategoryOptionsProvider())
var category: Category

// File with content types
@Parameter(title: "Document", supportedContentTypes: [.pdf, .plainText])
var document: IntentFile

// Measurement with unit
@Parameter(title: "Distance", defaultUnit: .miles, supportsNegativeNumbers: false)
var distance: Measurement<UnitLength>
```

### EntityPropertyQuery (iOS 18+) — Advanced Filtering & Sorting

```swift
struct RecipePropertyQuery: EntityPropertyQuery {
    func results(for ids: [String]) async throws -> [RecipeEntity] {
        RecipeStore.shared.recipes.filter { ids.contains($0.id) }.map { RecipeEntity(from: $0) }
    }

    @Property(title: "Name") var name: String
    @Property(title: "Cuisine") var cuisine: String
    @Property(title: "Rating") var rating: Double

    // System can now filter by cuisine and sort by rating
}
```

### Deprecated Macro Warnings

```swift
// DEPRECATED: Use @AppEntity(schema:) instead
@AssistantEntity(schema: .suggestions) // ❌ Avoid
struct OldEntity { }

// CORRECT (iOS 18+): Use @AppEntity with schema parameter
@AppEntity(schema: .suggestions) // ✅ Correct
struct NewEntity: AppEntity { }

// NOTE: @AssistantIntent(schema:) is STILL ACTIVE (iOS 18+)
@AssistantIntent(schema: .suggestions) // ✅ Still in use
struct MyIntent: AppIntent { }
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Forgetting `async` in `perform()` method | Always declare `func perform() async throws` — enables async/await operations |
| Not implementing `@Parameter` properties correctly | Use `@Parameter(title:description:)` with AppEnum for enum constraints |
| Returning no result; forgetting `.result()` | Return `.result(value:)` or `.result(value:view:)` for UI |
| Not declaring `openAppWhenRun` when launching UI | Set `openAppWhenRun = true` if intent needs to show app interface |
| Hardcoding Siri phrases without localization | Use `LocalizedStringResource` for all user-facing text |
| Using deprecated `@AssistantEntity` / `@AssistantEnum` | Use `@AppEntity(schema:)` and `@AppEnum(schema:)` instead (Note: `@AssistantIntent` is still active) |
| Missing `@Property(indexingKey:)` on IndexedEntity (iOS 26+) | Mark properties with indexing keys for Spotlight metadata |
| Not using `EntityPropertyQuery` for filter/sort | Use for advanced entity queries instead of basic `EntityQuery` (iOS 18+) |

## Review Checklist

- [ ] AppIntent implements `perform() async throws`
- [ ] `@Parameter` properties have title and description
- [ ] Enum parameters conform to AppEnum
- [ ] `openAppWhenRun` set correctly based on UX needs
- [ ] Result values typed correctly (`.result(value:)`)
- [ ] Optional parameters have sensible defaults
- [ ] AppShortcuts registered in AppShortcutsProvider
- [ ] Siri phrases localized (LocalizedStringResource)
- [ ] Spotlight integration: AppIntentSearchableItem conforms
- [ ] Search attributes indexed for discoverability
- [ ] Error handling: intents throw meaningful errors
- [ ] Result views SwiftUI-native, no complexity
- [ ] `UniqueAppEntityQuery` used for singletons (iOS 18+)
- [ ] `EntityPropertyQuery` applied for filter/sort support (iOS 18+)
- [ ] `IndexedEntity` properties use `@Property(indexingKey:)` (iOS 26+)
- [ ] `SnippetIntent` returns `ShowsSnippetView` (iOS 26+)
- [ ] `IntentValueQuery` implemented for Visual Intelligence (iOS 26+)
- [ ] `ControlConfigurationIntent` used for Control Center (iOS 18+)
- [ ] `@Parameter` UI customization applied (sliders, file types, measurements)
- [ ] No deprecated `@AssistantEntity` / `@AssistantEnum` used (use `@AppEntity(schema:)` instead)
- [ ] `@AssistantIntent(schema:)` still in use where appropriate (iOS 18+)
- [ ] All intent types are `Sendable`; runs in correct isolation context

## iOS 26+ AppIntents Updates

- **IntentModes** — `[.background, .foreground(.dynamic)]` for flexible execution context.
- **`continueInForeground(alwaysConfirm:)`** — request app launch mid-intent execution.
- **`requestChoice(between:dialog:)`** — get user input during intent.
- **`@ComputedProperty`** macro — live access to data source in intent parameters.
- **`@DeferredProperty`** macro — lazy load expensive properties.
- **`IndexedEntity`** + `searchableAttributes` — Spotlight indexing for app entities.
- **Swift Package support** — AppIntents can now be defined in Swift packages.

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

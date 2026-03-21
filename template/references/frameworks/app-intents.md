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
| `AppIntent` | Protocol for executable app actions | Implement `perform()` async method |
| `@Parameter` | Input property for intent | Supports validation, enum constraints |
| `IntentResult` | Success or failure outcome | Returns data or error message |
| `AppShortcut` | Declares available shortcuts | Defines phrases for Siri |
| `AppShortcutsProvider` | Registers shortcuts | Shortcut phrase & intent mapping |
| `IntentFile` | Spotlight-searchable item | File path with metadata |
| `AppIntentSearchableItemAttributeScopes` | Search attributes | Indexes app data for Spotlight |
| `AppIntentSearchableItems` | Dynamic Spotlight results | Generated from app state |

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

// 6. Result view for intent completion
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

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Forgetting `async` in `perform()` method | Always declare `func perform() async throws` — enables async/await operations |
| Not implementing `@Parameter` properties correctly | Use `@Parameter(title:description:)` with AppEnum for enum constraints |
| Returning no result; forgetting `.result()` | Return `.result(value:)` or `.result(value:view:)` for UI |
| Not declaring `openAppWhenRun` when launching UI | Set `openAppWhenRun = true` if intent needs to show app interface |
| Hardcoding Siri phrases without localization | Use `LocalizedStringResource` for all user-facing text |

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

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

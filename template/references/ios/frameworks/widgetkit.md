# WidgetKit — iOS Reference

> **When to read:** Dev reads this when building home screen widgets or lock screen widgets.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `Widget` | Main protocol for widget definition | Conform to implement body |
| `WidgetConfiguration` | Static or intent-driven config | `.systemSmall`, `.systemMedium`, `.systemLarge` |
| `TimelineProvider` | Supplies timeline entries over time | `placeholder()`, `getSnapshot()`, `getTimeline()` |
| `TimelineEntry` | Single point-in-time state | Includes date for refresh scheduling |
| `WidgetFamily` | Enum of widget sizes | Constraint layout per size |
| `.containerBackground()` | Widget background styling | Material, transparency support |
| `AppIntentConfiguration` | Intent-driven widget options | User-configurable via long-press |
| `@Environment` | Access system settings | `.colorScheme`, `.showsWidgetContainerBackground` |
| `widgetLabel()` | Lock screen widget label | Small text above/below widget |

## Code Examples

```swift
// 1. Define TimelineEntry
import WidgetKit
import SwiftUI

struct QuotesTimelineEntry: TimelineEntry {
    let date: Date
    let quote: String
    let author: String
}

// 2. Implement TimelineProvider
struct QuotesProvider: TimelineProvider {
    func placeholder(in context: Context) -> QuotesTimelineEntry {
        QuotesTimelineEntry(
            date: Date(),
            quote: "Loading...",
            author: "Unknown"
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (QuotesTimelineEntry) -> Void) {
        // Quick snapshot for widget gallery preview
        let entry = QuotesTimelineEntry(
            date: Date(),
            quote: "The only way to do great work is to love what you do.",
            author: "Steve Jobs"
        )
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<QuotesTimelineEntry>) -> Void) {
        // Generate timeline: typically 1-2 entries plus reload date
        var entries: [QuotesTimelineEntry] = []

        let now = Date()
        let calendar = Calendar.current

        // Add entry for now
        entries.append(QuotesTimelineEntry(
            date: now,
            quote: "The best time to plant a tree was 20 years ago.",
            author: "Chinese Proverb"
        ))

        // Add entry for 4 hours later (next refresh time)
        if let nextRefresh = calendar.date(byAdding: .hour, value: 4, to: now) {
            entries.append(QuotesTimelineEntry(
                date: nextRefresh,
                quote: "Innovation distinguishes between a leader and a follower.",
                author: "Steve Jobs"
            ))
        }

        let timeline = Timeline(entries: entries, policy: .atEnd)
        completion(timeline)
    }
}

// 3. Widget view hierarchy
struct QuotesWidgetEntryView: View {
    var entry: QuotesProvider.Entry
    @Environment(\.widgetRenderingMode) var renderingMode
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("\"\(entry.quote)\"")
                .font(.system(.body, design: .rounded))
                .fontWeight(.semibold)
                .lineLimit(3)

            Spacer()

            Text("— \(entry.author)")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .containerBackground(.blue.gradient, for: .widget)
    }
}

// 4. Main Widget definition
@main
struct QuotesWidget: Widget {
    let kind: String = "com.myapp.quotes"

    var body: some WidgetConfiguration {
        StaticConfiguration(
            kind: kind,
            provider: QuotesProvider()
        ) { entry in
            QuotesWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Daily Quote")
        .description("Get inspired with a daily quote")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
    }
}

// 5. Intent-driven widget with user configuration
struct TasksWidgetIntent: WidgetConfigurationIntent {
    @Parameter(title: "Category", default: "All")
    var category: String
}

struct TasksTimelineEntry: TimelineEntry {
    let date: Date
    let tasks: [String]
    let category: String
}

struct TasksProvider: AppIntentTimelineProvider {
    func placeholder(in context: Context) -> TasksTimelineEntry {
        TasksTimelineEntry(
            date: Date(),
            tasks: ["Task 1", "Task 2"],
            category: "All"
        )
    }

    func snapshot(for configuration: TasksWidgetIntent, in context: Context) async -> TasksTimelineEntry {
        return TasksTimelineEntry(
            date: Date(),
            tasks: ["Sample Task"],
            category: configuration.category
        )
    }

    func timeline(for configuration: TasksWidgetIntent, in context: Context) async -> Timeline<TasksTimelineEntry> {
        let tasks = await fetchTasks(for: configuration.category)
        let entry = TasksTimelineEntry(
            date: Date(),
            tasks: tasks,
            category: configuration.category
        )
        return Timeline(entries: [entry], policy: .atEnd)
    }

    private func fetchTasks(for category: String) async -> [String] {
        // Fetch from app or shared storage
        return ["Task 1", "Task 2"]
    }
}

@main
struct TasksWidget: Widget {
    let kind: String = "com.myapp.tasks"

    var body: some WidgetConfiguration {
        AppIntentConfiguration(
            kind: kind,
            intent: TasksWidgetIntent.self,
            provider: TasksProvider()
        ) { entry in
            TasksWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("My Tasks")
        .description("View your tasks by category")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

// 6. Lock screen widget with label
struct LockScreenWidgetView: View {
    var entry: QuotesTimelineEntry

    var body: some View {
        VStack(alignment: .leading) {
            Text(entry.quote)
                .font(.caption)
                .lineLimit(2)
        }
        .widgetLabel {
            Label(entry.author, systemImage: "quote.opening")
                .font(.caption2)
        }
    }
}

// 7. Handle shared data (SwiftData integration)
struct SharedDataWidget: Widget {
    let kind: String = "com.myapp.shared"

    var body: some WidgetConfiguration {
        StaticConfiguration(
            kind: kind,
            provider: SharedDataProvider()
        ) { entry in
            SharedDataView(entry: entry)
        }
        .supportedFamilies([.systemSmall])
    }
}

struct SharedDataProvider: TimelineProvider {
    func getTimeline(in context: Context, completion: @escaping (Timeline<QuotesTimelineEntry>) -> Void) {
        // Access shared app group data
        if let sharedDefaults = UserDefaults(suiteName: "group.com.myapp.shared") {
            let savedQuote = sharedDefaults.string(forKey: "lastQuote") ?? "Default"
            let entry = QuotesTimelineEntry(
                date: Date(),
                quote: savedQuote,
                author: "App"
            )
            completion(Timeline(entries: [entry], policy: .atEnd))
        }
    }
}
```

## iOS 26 Additions

### AppIntentTimelineProvider with async/await

Modern configurable widgets use `AppIntentTimelineProvider` with full async/await support, unlike the deprecated `IntentTimelineProvider`:

```swift
struct CategoryProvider: AppIntentTimelineProvider {
    typealias Entry = CategoryEntry
    typealias Intent = SelectCategoryIntent

    func placeholder(in context: Context) -> CategoryEntry {
        CategoryEntry(date: .now, categoryName: "Sample", items: [])
    }

    func snapshot(for config: SelectCategoryIntent, in context: Context) async -> CategoryEntry {
        let items = await DataStore.shared.items(for: config.category)
        return CategoryEntry(date: .now, categoryName: config.category.name, items: items)
    }

    func timeline(for config: SelectCategoryIntent, in context: Context) async -> Timeline<CategoryEntry> {
        let items = await DataStore.shared.items(for: config.category)
        let entry = CategoryEntry(date: .now, categoryName: config.category.name, items: items)
        return Timeline(entries: [entry], policy: .atEnd)
    }
}
```

### Liquid Glass Support

Adapt widgets to Liquid Glass visual style with `WidgetAccentedRenderingMode`:

| Mode | Use Case |
|------|----------|
| `.accented` | Emphasized content for Liquid Glass |
| `.accentedDesaturated` | Accented with reduced saturation |
| `.desaturated` | Fully desaturated appearance |
| `.fullColor` | Standard full-color rendering |

### WidgetPushHandler

Enable push-based timeline reloads without polling:

```swift
struct MyWidgetPushHandler: WidgetPushHandler {
    func pushTokenDidChange(_ pushInfo: WidgetPushInfo, widgets: [WidgetInfo]) {
        let tokenString = pushInfo.token.map { String(format: "%02x", $0) }.joined()
        // Send tokenString to your server for push updates
    }
}
```

### CarPlay Widgets (iOS 26+)

`.systemSmall` widgets render in CarPlay. Ensure layouts are glanceable and driver-safe—minimize text, use clear icons, avoid rapid animations.

## Common Mistakes

1. **Using IntentTimelineProvider instead of AppIntentTimelineProvider.**
   `IntentTimelineProvider` is deprecated. Always use `AppIntentTimelineProvider` with async/await.

2. **Exceeding the refresh budget.**
   Widgets have a daily refresh limit. Do not call `WidgetCenter.shared.reloadTimelines(ofKind:)` on every minor data change. Batch updates and use appropriate `TimelineReloadPolicy` values.

3. **Forgetting App Groups for shared data.**
   The widget extension runs in a separate process. Use `UserDefaults(suiteName:)` or a shared App Group container for data the widget reads.

4. **Performing network calls in placeholder().**
   `placeholder(in:)` must return synchronously with sample data. Use `getTimeline` or `timeline(for:in:)` for async work.

5. **Missing NSSupportsLiveActivities Info.plist key.**
   Live Activities will not start without `NSSupportsLiveActivities = YES` in the host app's Info.plist.

6. **Using the deprecated contentState API.**
   Use `ActivityContent` for all `Activity.request`, `update`, and `end` calls. The `contentState`-based methods are deprecated.

7. **Not handling the stale state.**
   Check `context.isStale` in Live Activity views and show a fallback (e.g., "Updating...") when content is outdated.

8. **Putting heavy logic in the widget view.**
   Widget views are rendered in a size-limited process. Pre-compute data in the timeline provider and pass display-ready values through the entry.

9. **Ignoring accessory rendering modes.**
   Lock Screen widgets render in `.vibrant` or `.accented` mode, not `.fullColor`. Test with `@Environment(\.widgetRenderingMode)` and avoid relying on color alone.

10. **Not testing on device.**
    Dynamic Island and StandBy behavior differ significantly from Simulator. Always verify on physical hardware.

11. **Ignoring WidgetAccentedRenderingMode for Liquid Glass.**
    iOS 26 Liquid Glass requires explicit rendering mode adaptation. Test in Simulator with Liquid Glass theme.

12. **Forgetting WidgetPushHandler registration.**
    If using push-based updates, register the push handler in `WidgetBundle` and handle token changes.

## Review Checklist

- [ ] TimelineEntry conforms to Codable (for state restoration)
- [ ] `getTimeline()` avoids network calls; uses cached data
- [ ] Timeline policy set appropriately (`.atEnd`, `.after()`, `.never`)
- [ ] Widget sizes supported declared in `supportedFamilies`
- [ ] Placeholder view renders quickly
- [ ] Snapshot view matches gallery preview
- [ ] Lock screen widgets use `widgetLabel()` correctly
- [ ] Intent-driven widgets use `AppIntentConfiguration`
- [ ] Colors respect `.colorScheme` (light/dark modes)
- [ ] `.containerBackground()` used for proper styling
- [ ] Shared data uses App Groups `UserDefaults`
- [ ] Widget refresh time not < 15 minutes (system limit)

## visionOS Widgets

- Mounting styles: `.elevated` (floating on surface), `.recessed` (embedded in wall/surface).
- Textures: `.glass` (default), `.paper`.
- `@Environment(\.levelOfDetail)` — `.default` vs `.simplified` based on user proximity.
- Widget families include `.systemExtraLarge` and `.systemExtraLargePortrait`.

## Widget Performance

- **Memory budget:** Widgets have a strict `EXC_RESOURCE` hard limit. Use `Canvas` for dense visuals (dot grids etc.), not hundreds of nested views.
- **Timeline refresh:** Match data granularity — midnight for day-level data, 15-minute periodic for time-of-day, never minute-level for static data.

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

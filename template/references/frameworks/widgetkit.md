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

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Slow `getTimeline()` blocking widget refresh | Use `.atEnd` policy; preload next entries; avoid blocking I/O |
| Fetching live network data in timeline | Use snapshot for quick preview; timeline for cached/static data only |
| Not specifying `supportedFamilies`; crashes on unsupported size | Always declare supported families: `.systemSmall`, `.systemMedium`, `.systemLarge` |
| Hardcoding colors; ignoring dark mode | Use `.containerBackground()` with environment colors; respect `.colorScheme` |
| Not sharing data with main app (UserDefaults vs. App Groups) | Use `UserDefaults(suiteName: "group.com.bundle")` for shared data |

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

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

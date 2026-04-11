# EventKit — iOS Reference

> **When to read:** Dev reads this when building features with calendar events, reminders, or calendar access.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `EKEventStore` | Main API; manages calendar, event, reminder access |
| `EKEvent` | Immutable event object; properties for time, location, attendees |
| `EKMutableEvent` | Editable event; set title, description, date/time, recurrence |
| `EKReminder` | Task/reminder; similar to event but no time-based |
| `EKCalendar` | Calendar container; local or cloud-synced |
| `EKEventViewController` | Read-only event detail UI |
| `EKEventEditViewController` | Native event editor; minimal code integration |
| `EKRecurrenceRule` | Daily, weekly, monthly, yearly patterns |
| `EKRecurrenceEnd` | Limit recurrence: by date or occurrence count |
| `EKAlarm` | Notification trigger: relative time or absolute |
| `EKAuthorizationStatus` | `.authorized`, `.denied`, `.restricted`, `.notDetermined` |
| `EKEventAvailability` | Event type: `.busy`, `.free`, `.tentative`, `.unavailable` |

---

## Code Examples

### Example 1: Create and save an event
```swift
import EventKit

func createEvent(title: String, startDate: Date, endDate: Date, calendarTitle: String? = nil) throws {
    let eventStore = EKEventStore()

    // Request authorization
    if #available(iOS 17, *) {
        try eventStore.requestFullAccessToEvents()
    } else {
        let status = EKEventStore.authorizationStatus(for: .event)
        if status == .notDetermined {
            try await eventStore.requestAccess(to: .event)
        } else if status != .authorized {
            throw NSError(domain: "EventKitError", code: 1, userInfo: [NSLocalizedDescriptionKey: "No access"])
        }
    }

    let event = EKMutableEvent()
    event.title = title
    event.startDate = startDate
    event.endDate = endDate
    event.calendar = calendarTitle != nil ? fetchCalendar(named: calendarTitle!) : eventStore.defaultCalendarForNewEvents

    let alarm = EKAlarm(relativeOffset: -15 * 60) // 15 minutes before
    event.addAlarm(alarm)

    try eventStore.save(event, span: .thisEvent)
    print("Event saved: \(event.eventIdentifier)")
}

func fetchCalendar(named name: String) -> EKCalendar? {
    let eventStore = EKEventStore()
    return eventStore.calendars(for: .event).first { $0.title == name }
}
```

### Example 1b: Write-only access to events (iOS 17+)
```swift
func requestWriteOnlyAccess() async throws -> Bool {
    let granted = try await eventStore.requestWriteOnlyAccessToEvents()
    return granted
}
```

### Example 1c: Add structured location with geo-location
```swift
let location = EKStructuredLocation(title: "Apple Park")
location.geoLocation = CLLocation(latitude: 37.3349, longitude: -122.0090)
event.structuredLocation = location
```

### Example 1d: Fetch reminders with async continuation
```swift
func fetchIncompleteReminders() async -> [EKReminder] {
    let predicate = eventStore.predicateForIncompleteReminders(
        withDueDateStarting: nil,
        ending: nil,
        calendars: nil
    )

    return await withCheckedContinuation { continuation in
        eventStore.fetchReminders(matching: predicate) { reminders in
            continuation.resume(returning: reminders ?? [])
        }
    }
}
```

### Example 1e: Handling timezone for events
```swift
event.timeZone = TimeZone(identifier: "America/New_York")
event.startDate = startDate
event.endDate = endDate
```

### Example 2: Fetch events in date range
```swift
import EventKit

func fetchEvents(from startDate: Date, to endDate: Date) -> [EKEvent] {
    let eventStore = EKEventStore()

    guard EKEventStore.authorizationStatus(for: .event) == .authorized else {
        print("Calendar access not authorized")
        return []
    }

    let predicate = eventStore.predicateForEvents(
        withStart: startDate,
        end: endDate,
        calendars: eventStore.calendars(for: .event)
    )

    return eventStore.events(matching: predicate)
}

// Usage
let today = Date()
let tomorrow = Calendar.current.date(byAdding: .day, value: 1, to: today)!
let events = fetchEvents(from: today, to: tomorrow)
events.forEach { print("Event: \($0.title) at \($0.startDate)") }
```

### Example 3: Create a recurring event
```swift
import EventKit

func createRecurringEvent(title: String, startDate: Date, endDate: Date) throws {
    let eventStore = EKEventStore()

    guard EKEventStore.authorizationStatus(for: .event) == .authorized else {
        throw NSError(domain: "", code: 1)
    }

    let event = EKMutableEvent()
    event.title = title
    event.startDate = startDate
    event.endDate = endDate

    // Repeat weekly on same day of week, 10 occurrences
    let recurrenceRule = EKRecurrenceRule(
        recurrenceWith: .weekly,
        interval: 1,
        daysOfTheWeek: [EKRecurrenceDayOfWeek(EKWeekday.monday)],
        daysOfTheMonth: nil,
        monthsOfTheYear: nil,
        weeksOfTheYear: nil,
        daysOfTheYear: nil,
        setPositions: nil,
        end: EKRecurrenceEnd(occurrenceCount: 10)
    )
    event.recurrenceRules = [recurrenceRule]

    event.calendar = eventStore.defaultCalendarForNewEvents

    try eventStore.save(event, span: .futureEvents)
    print("Recurring event saved")
}
```

### Example 4: Add reminder (task)
```swift
import EventKit

func createReminder(title: String, dueDate: Date?) throws {
    let eventStore = EKEventStore()

    if #available(iOS 17, *) {
        try eventStore.requestFullAccessToReminders()
    } else {
        let status = EKEventStore.authorizationStatus(for: .reminder)
        if status != .authorized {
            throw NSError(domain: "", code: 1)
        }
    }

    let reminder = EKMutableReminder()
    reminder.title = title
    reminder.dueDate = dueDate
    reminder.calendar = eventStore.defaultCalendarForNewReminders()

    // Add alarm
    let alarm = EKAlarm(relativeOffset: -1 * 60 * 60) // 1 hour before
    reminder.addAlarm(alarm)

    try eventStore.save(reminder, commit: true)
    print("Reminder saved")
}
```

### Example 5: Edit event with native UI
```swift
import EventKit
import EventKitUI

class EventEditorViewController: UIViewController, EKEventEditViewDelegate {
    func openEventEditor(for event: EKEvent) {
        let eventStore = EKEventStore()
        let eventEditViewController = EKEventEditViewController()
        eventEditViewController.event = event
        eventEditViewController.eventStore = eventStore
        eventEditViewController.editViewDelegate = self

        present(eventEditViewController, animated: true)
    }

    // MARK: - EKEventEditViewDelegate
    func eventEditViewController(_ controller: EKEventEditViewController, didCompleteWith action: EKEventEditViewAction) {
        dismiss(animated: true)

        switch action {
        case .saved:
            print("Event saved")
        case .deleted:
            print("Event deleted")
        case .cancelled:
            print("Cancelled")
        @unknown default:
            break
        }
    }
}
```

---

## Common Mistakes

### ❌ Not requesting authorization before accessing events
```swift
// Bad: Silent failure if not authorized
let predicate = eventStore.predicateForEvents(withStart: today, end: tomorrow, calendars: nil)
let events = eventStore.events(matching: predicate) // Empty array
```
✅ **Fix:** Check authorization status first
```swift
if EKEventStore.authorizationStatus(for: .event) == .authorized {
    let predicate = eventStore.predicateForEvents(withStart: today, end: tomorrow, calendars: nil)
    let events = eventStore.events(matching: predicate)
} else {
    EKEventStore().requestAccess(to: .event) { granted, _ in ... }
}
```

### ❌ Ignoring span parameter when saving recurring events
```swift
// Bad: Only saves one occurrence
event.recurrenceRules = [rule]
try eventStore.save(event, span: .thisEvent) // Should be .futureEvents
```
✅ **Fix:** Specify correct span
```swift
event.recurrenceRules = [rule]
try eventStore.save(event, span: .futureEvents)
```

### ❌ Modifying immutable EKEvent directly
```swift
// Bad: EKEvent is immutable
let event = eventStore.event(withIdentifier: id)
event.title = "New Title" // No effect
```
✅ **Fix:** Create mutable copy, modify, save
```swift
let event = eventStore.event(withIdentifier: id)!
let mutableEvent = event.copy() as! EKMutableEvent
mutableEvent.title = "New Title"
try eventStore.save(mutableEvent, span: .thisEvent)
```

### ❌ Not handling iOS 17+ authorization changes
```swift
// Bad: iOS 17+ requires fullAccess or writeOnly explicitly
let status = EKEventStore.authorizationStatus(for: .event)
```
✅ **Fix:** Use requestFullAccessToEvents for iOS 17+
```swift
if #available(iOS 17, *) {
    do {
        try eventStore.requestFullAccessToEvents()
    } catch {
        print("Authorization failed: \(error)")
    }
} else {
    eventStore.requestAccess(to: .event) { granted, _ in ... }
}
```

### ❌ Querying events with nil calendars
```swift
// Bad: Searches all calendars including disabled ones
let predicate = eventStore.predicateForEvents(
    withStart: start,
    end: end,
    calendars: nil // Searches all
)
```
✅ **Fix:** Specify calendars explicitly
```swift
let calendars = eventStore.calendars(for: .event).filter { $0.isSubscribed }
let predicate = eventStore.predicateForEvents(
    withStart: start,
    end: end,
    calendars: calendars
)
```

---

## Review Checklist

- [ ] Authorization status checked for `.event` or `.reminder` before access
- [ ] `requestFullAccessToEvents()` used on iOS 17+; `requestAccess(to:)` on earlier versions
- [ ] Immutable events never modified directly; use `copy()` and create `EKMutableEvent`
- [ ] `span` parameter correct when saving recurring events (`.thisEvent` vs `.futureEvents`)
- [ ] Alarms added with relative offset or absolute time as needed
- [ ] Recurrence rules properly constructed with valid end condition (date or count)
- [ ] Calendar specified for new events (not default if user prefers specific calendar)
- [ ] Event fetch includes timezone conversion if needed
- [ ] Memory: event store retained (not local variable) to avoid early deallocation
- [ ] Error handling for authorization denial, calendar unavailability
- [ ] Privacy: `NSCalendarsUsageDescription` and `NSRemindersUsageDescription` in Info.plist
- [ ] Tests use EKEventStore mock or in-memory store to avoid modifying real calendar

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

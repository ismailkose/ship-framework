<!-- ship-reference
id: ios-device-data
kind: mixed
sources: iPhoneOS27.0.sdk CoreLocation / MapKit / HealthKit / EventKit (headers) / Contacts / ContactsUI / CoreMotion / CoreBluetooth / AccessorySetupKit / CoreNFC / WeatherKit / MusicKit interfaces and headers (Xcode 27.0 27A266a — examples type-check via scripts/checks/ios.sh); https://developer.apple.com/documentation/corelocation ; https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui ; https://developer.apple.com/documentation/healthkit/protecting-user-privacy ; https://developer.apple.com/documentation/eventkit/accessing-the-event-store ; https://developer.apple.com/documentation/contacts ; https://developer.apple.com/documentation/corebluetooth ; https://developer.apple.com/documentation/accessorysetupkit ; https://developer.apple.com/documentation/corenfc ; https://developer.apple.com/documentation/weatherkit ; https://developer.apple.com/documentation/musickit ; https://developer.apple.com/documentation/healthkit/hkworkoutsession ; https://developer.apple.com/documentation/financekit ; https://developer.apple.com/documentation/sensorkit ; https://developer.apple.com/documentation/energykit ; https://developer.apple.com/documentation/permissionkit ; https://developer.apple.com/documentation/declaredagerange (checked 2026-09-24/25). Written for Ship from Apple's docs and the SDK; no third-party text.
reviewed: 2026-09-25
-->
# Location, Health, calendar, contacts, and data services

**When to read:** "where am I", maps and directions, "track my runs", workouts, Health data, "add
to my calendar", "create a reminder in Reminders", contacts, step counts and motion, weather, Apple
Music, Apple Card data (FinanceKit), research sensors (SensorKit), home energy (EnergyKit), child
accounts (PermissionKit, Declared Age Range). Accessories and Bluetooth: `accessories.md`. **Apple** = platform
requirement; **Ship** = default.

## 1. Permission rules that apply to all of them

- **Ask in context**, when the person uses the feature — never a wall of prompts at launch. Before
  the system prompt, the screen should already make clear why (the purpose string repeats it).
- **Ask for the least:** when-in-use before always; write-only calendar access before full;
  a picker (photos, contacts, accessories) before library-wide access.
- **Denied is a normal state:** keep the feature's screen useful (manual entry, search instead of
  "near me") and offer Settings. You can't re-prompt.
- **HealthKit is different:** the app can't tell read-denied from "no data" (§3).

| Data / hardware | Info.plist key(s) | Capability / entitlement |
|---|---|---|
| Location | `NSLocationWhenInUseUsageDescription` (+ `…AlwaysAndWhenInUse…` for always) | Background Modes › Location updates for continuous background tracking |
| HealthKit | `NSHealthShareUsageDescription`, `NSHealthUpdateUsageDescription` | HealthKit (+ Background Delivery if used) |
| Calendar | `NSCalendarsWriteOnlyAccessUsageDescription` or `NSCalendarsFullAccessUsageDescription` | — |
| Reminders | `NSRemindersFullAccessUsageDescription` | — |
| Contacts | `NSContactsUsageDescription` | — |
| Motion & fitness | `NSMotionUsageDescription` | — |
| Bluetooth | `NSBluetoothAlwaysUsageDescription` | Background Modes › Uses Bluetooth LE accessories (if needed) |
| NFC | `NFCReaderUsageDescription` | Near Field Communication Tag Reading |
| WeatherKit | — | WeatherKit (capability + App Services) |
| Apple Music | `NSAppleMusicUsageDescription` | MusicKit App Service |

## 2. Location and maps

- **Ship:** "near me" features need when-in-use only. Use approximate location when precision
  isn't needed; request temporary full accuracy only for the moment it matters.
- iOS 17+: `CLLocationUpdate.liveUpdates()` — an async sequence; iterate it in a task you cancel
  when the screen goes away. iOS 18+: hold a `CLServiceSession(authorization: .whenInUse)` while
  the feature is active; it also handles the authorization prompt. Regions/geofences:
  `CLMonitor` (iOS 17).
- Continuous background tracking (a run, a delivery route) needs the background mode and a visible
  reason; the system shows the location indicator. Anything else stays foreground.
- **Maps:** SwiftUI `Map` (iOS 17) with `Marker`/`Annotation`, `MapCameraPosition`
  (`.userLocation(fallback:)`, `.region`), `UserAnnotation()`, `MapUserLocationButton`; search with
  `MKLocalSearch`, routes with `MKDirections`. Debounce search-as-you-type with `.task(id: query)`.
- **Test:** simulator Features › Location (custom location, City Run) and a GPX file in the scheme;
  accuracy, background tracking, and battery need a **device** outdoors.

```swift
import CoreLocation

@MainActor @Observable
final class NearbyLocation {
    private(set) var last: CLLocation?
    private(set) var denied = false

    /// Run from `.task` on the screen that needs location; cancelling the task stops updates.
    @available(iOS 18.0, *)
    func follow() async {
        let session = CLServiceSession(authorization: .whenInUse)   // keep alive while updates run
        defer { withExtendedLifetime(session) {} }
        do {
            for try await update in CLLocationUpdate.liveUpdates() {
                if update.authorizationDenied { denied = true; return }
                if let location = update.location { last = location }
            }
        } catch {
            // updates end on error; the view shows the last known location or manual entry
        }
    }
}
```

## 3. Health data (HealthKit)

- **Prerequisites (Apple):** HealthKit capability; both usage strings; check
  `HKHealthStore.isHealthDataAvailable()`. App Review: health data isn't for advertising, and the
  app must have a clear health purpose.
- Request only the types the current feature uses, when it first needs them. **Reads can't be
  checked:** a denied read returns no samples, like "no data yet". Design the empty state as
  "No data — check Health permissions" with a Settings path; never infer consent.
- Queries: the async descriptors — `HKSampleQueryDescriptor` for samples,
  `HKStatisticsCollectionQueryDescriptor` for daily totals (steps, energy) with the right
  `HKUnit`, `HKAnchoredObjectQueryDescriptor` to sync only what changed.
- Writing: save samples with correct units and dates; the person can delete them in Health —
  don't assume your writes stay.
- **Test:** the simulator has the Health app — add sample data there; background delivery and
  Watch data need a **device**.

```swift
import HealthKit

nonisolated func stepsPerDay(store: HKHealthStore, days: Int) async throws -> [(Date, Double)] {
    let stepType = HKQuantityType(.stepCount)
    try await store.requestAuthorization(toShare: [], read: [stepType])   // shows the sheet once
    let calendar = Calendar.current
    let end = calendar.startOfDay(for: .now).addingTimeInterval(86_400)
    let start = calendar.date(byAdding: .day, value: -days, to: end)!
    let query = HKStatisticsCollectionQueryDescriptor(
        predicate: .quantitySample(type: stepType, predicate: HKQuery.predicateForSamples(withStart: start, end: end)),
        options: .cumulativeSum, anchorDate: start, intervalComponents: DateComponents(day: 1))
    let collection = try await query.result(for: store)
    var rows: [(Date, Double)] = []
    collection.enumerateStatistics(from: start, to: end) { stats, _ in
        rows.append((stats.startDate, stats.sumQuantity()?.doubleValue(for: .count()) ?? 0))
    }
    return rows      // zeros can mean "no steps" OR "read denied" — say so in the UI
}
```

**Workouts on iPhone (iOS 26) — session lifecycle and recovery:**
- Request share permission for `HKObjectType.workoutType()` (plus the samples you'll save) and
  read permission for what you display.
- Start: `HKWorkoutSession(healthStore:configuration:)` → `associatedWorkoutBuilder()` → set an
  `HKLiveWorkoutDataSource` → `startActivity(with:)` → `beginCollection(at:)`.
- Pause/resume with `session.pause()` / `resume()`; end with `session.end()` →
  `endCollection(at:)` → `finishWorkout()` (that's the save).
- **If the app is killed mid-workout**, call `recoverActiveWorkoutSession()` at launch and resume
  showing it — don't start a second one. Handle `session` state changes and errors through its
  delegate (`workoutSession(_:didChangeTo:from:date:)`, `didFailWithError`).
- Background: a running workout session keeps the app running in the background; test with the
  screen locked.

**Keeping your own copy in sync — anchored changes:** `HKAnchoredObjectQueryDescriptor` returns
what was **added and deleted** since an anchor; persist the new anchor
(`NSKeyedArchiver`, secure coding) after applying the batch, and start from `nil` on first run.
Deleted samples come back as `deletedObjects` — remove them from your store too.

**Background delivery:** HealthKit Background Delivery entitlement →
`enableBackgroundDelivery(for:frequency:)` → a long-lived `HKObserverQuery` registered at every
launch. The observer only says *something changed*: run the anchored query, then **call the
observer's completion handler** — HealthKit backs off an app that doesn't.

```swift
import HealthKit

@available(iOS 26.0, *)
@MainActor
final class WorkoutRecorder {
    private let store = HKHealthStore()
    private var session: HKWorkoutSession?

    /// Picks up a workout the system kept running while the app was gone; call at launch.
    func recover() async -> Bool {
        session = try? await store.recoverActiveWorkoutSession()
        return session != nil
    }

    func start(_ activity: HKWorkoutActivityType) async throws {
        guard session == nil else { return }                        // one workout at a time
        let config = HKWorkoutConfiguration()
        config.activityType = activity
        config.locationType = .outdoor
        let session = try HKWorkoutSession(healthStore: store, configuration: config)
        let builder = session.associatedWorkoutBuilder()
        builder.dataSource = HKLiveWorkoutDataSource(healthStore: store, workoutConfiguration: config)
        session.startActivity(with: .now)
        try await builder.beginCollection(at: .now)
        self.session = session
    }

    /// Ends and saves; returns nil if nothing was running.
    func finish() async throws -> HKWorkout? {
        guard let session else { return nil }
        session.end()
        let builder = session.associatedWorkoutBuilder()
        try await builder.endCollection(at: .now)
        let workout = try await builder.finishWorkout()
        self.session = nil
        return workout
    }
}
```

**Not shown:** the session delegate (state changes, failures), live statistics display, and
pausing. Compiles; not run — workouts, recovery, and background delivery need a **device**.

## 4. Calendar, reminders, contacts

- **Adding one event:** `EKEventEditViewController` (EventKitUI) runs out of process — on iOS 17+ it
  needs **no** calendar permission. Only ask for access to read or manage events.
- Write-only calendar access (iOS 17) when the app only adds events; full access to read them.
  Reminders only have full access (`requestFullAccessToReminders`).
- Recurring events: saving or deleting needs a span (`.thisEvent` / `.futureEvents`) — ask the
  person which, like Calendar does. Store the `eventIdentifier`/`calendarItemIdentifier` to find the
  item later, and handle it having been deleted. Observe `.EKEventStoreChanged` to refresh.
- **Contacts:** one contact → `CNContactPickerViewController` (no permission). iOS 18 limited
  access: the person may share only some contacts; `ContactAccessButton` lets them add more in
  context. Fetch only the keys you display (`keysToFetch`).

```swift
import EventKit

/// Creates a reminder in the person's default Reminders list. Returns nil if access is denied.
nonisolated func addReminder(title: String, due: Date, store: EKEventStore = EKEventStore()) async throws -> String? {
    guard try await store.requestFullAccessToReminders(),
          let list = store.defaultCalendarForNewReminders() else { return nil }
    let reminder = EKReminder(eventStore: store)
    reminder.title = title
    reminder.calendar = list
    reminder.dueDateComponents = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: due)
    reminder.addAlarm(EKAlarm(absoluteDate: due))
    try store.save(reminder, commit: true)
    return reminder.calendarItemIdentifier       // keep it to edit or delete later
}
```

(A reminder *inside your app* is a local notification — `notifications-background.md` §2. Use
EventKit only when the person wants it in Apple's Reminders or Calendar.)

## 5. Motion, weather, music, and special-purpose data

Each of these has its own prerequisites; a plan names them before any code.

**Core Motion** — steps, activity, raw sensors.
- `CMPedometer` (check `isStepCountingAvailable()`), `CMMotionActivityManager` (walking/running/
  driving), `CMMotionManager` for raw sensors — one instance per app, the lowest update interval that
  works, stop updates when the screen goes away. `NSMotionUsageDescription`.
- Denied or unavailable → hide the feature or fall back to manual entry. Simulator has no motion
  data — **device**.

**WeatherKit** — forecasts.
- Capability + the WeatherKit App Service on the App ID; `WeatherService.shared.weather(for:)`.
- **Apple requires attribution** (the Apple Weather mark and legal link, from
  `WeatherService.shared.attribution`) wherever the data appears.
- Cache by location and time; there's a monthly call allowance per developer account. Network
  errors → show the cached forecast with its age.

**MusicKit** — Apple Music.
- MusicKit App Service; `MusicAuthorization.request()`; catalog search works without a
  subscription, playback needs one (`MusicSubscription.current`, `.musicSubscriptionOffer`).
- `ApplicationMusicPlayer` for in-app queues, `SystemMusicPlayer` to drive the Music app.

**FinanceKit** — Apple Card, Apple Cash, and Wallet order data (iOS 17.4+).
- **Prerequisites:** an Apple-granted FinanceKit entitlement (apply first — without it nothing
  works), `NSFinancialDataUsageDescription`, and a device region where the data exists.
- Check `FinanceStore.isDataAvailable(.financialData)` before showing the feature; then
  `requestAuthorization()` (the person picks which accounts to share); `.denied` → explain, no retry.
- Read with `transactions(query:)` / `accounts(query:)`; keep up to date with
  `transactionHistory(forAccountID:since:)` and persist the history token.
- **Acceptance:** entitlement granted, a device with Apple Card/Cash data, sharing then revoking
  access in Settings.

**SensorKit** — research-study sensor data (ambient light, visits, device usage, keyboard metrics…).
- **Only for approved research studies:** Apple reviews and grants the entitlement per study; the
  app needs a study consent flow and per-sensor usage strings.
- iOS 27: the Swift `SRReader<Sensor>` — `requestAuthorization(for:)`, `startRecording()`, then
  `samples(matching:)`; data arrives after a system holding period, not live. Earlier releases:
  `SRSensorReader` with a delegate.
- **Acceptance:** entitlement, consented participant device, data appearing after the holding period.

**EnergyKit** — cleaner/cheaper electricity guidance and usage insights (iOS 26).
- **Prerequisites:** EnergyKit entitlement; the person has set up a home (energy venue) in the Home
  app in a supported region. `EnergyVenue.venues()` (iOS 26.1) empty → hide the feature.
- Guidance: `ElectricityGuidance.sharedService.guidance(using: .init(suggestedAction: .shift), at:
  venueID)` is a stream of time windows with ratings — schedule flexible work (EV charging) into the
  windows the guidance favours; report what you did with load events (`submitEvents`) if you control
  a device.
- **Acceptance:** device with a configured home; guidance updates over a day.

**PermissionKit and Declared Age Range** — child accounts (iOS 26).
- **PermissionKit:** a child asks a parent through Messages to allow something (contacting a person,
  a significant app update). SwiftUI `PermissionButton(question:)` / UIKit `AskCenter.ask(_:in:)`;
  listen to `AskCenter.shared.responses(for:)` and apply the answer when it arrives — it can take
  hours. Until then, keep the request pending, not denied.
- **Declared Age Range:** `DeclaredAgeRangeAction` / `AgeRangeService.requestAgeRange(ageGates:)`
  returns `.sharing(range:)` or `.declinedSharing`; adapt the experience to the range and treat
  "declined" as a normal answer. It's a signal, not identity verification.
- **Acceptance:** Family Sharing with a child account on a device; the parent approving and
  declining.

```swift
import FinanceKit
import EnergyKit

/// FinanceKit: this month's transactions, or nil when the feature can't run here.
@available(iOS 17.4, *)
nonisolated func recentTransactions(limit: Int = 50) async throws -> [FinanceKit.Transaction]? {
    guard FinanceStore.isDataAvailable(.financialData) else { return nil }    // region/device
    guard try await FinanceStore.shared.requestAuthorization() == .authorized else { return nil }
    let query = TransactionQuery(sortDescriptors: [SortDescriptor(\.transactionDate, order: .reverse)], limit: limit)
    return try await FinanceStore.shared.transactions(query: query)
}

/// EnergyKit: the upcoming guidance windows for the person's home, or nil when none is set up.
/// Returns windows with their ratings; how to rank them is a product decision (see the note below).
@available(iOS 26.1, *)
nonisolated func upcomingShiftGuidance() async throws -> [(interval: DateInterval, rating: Double)]? {
    guard let venue = try await EnergyVenue.venues().first else { return nil }   // no home in Home → hide
    for try await guidance in ElectricityGuidance.sharedService.guidance(using: .init(suggestedAction: .shift), at: venue.id) {
        return guidance.values.filter { $0.interval.end > .now }.map { ($0.interval, $0.rating) }
    }
    return nil
}
```

**Open question, not guessed:** Apple's EnergyKit pages (checked 2026-09-25) don't state which
direction of `rating` means cleaner or cheaper, so the example doesn't pick a "best" window. Confirm
it from Apple's documentation or sample code, or a device run against known grid conditions, before
ranking windows. `EnergyVenue.venues()` needs iOS 26.1.

## 6. Accessories

Bluetooth, AccessorySetupKit, NFC, HomeKit/Matter, DockKit, and Wi-Fi Aware: `accessories.md`.

## 7. Verify

| What | How | Level |
|---|---|---|
| Every permission: allow, deny, limited, later change in Settings | Simulator — reset with `xcrun simctl privacy booted reset all <bundle-id>` | Simulator |
| Location live updates, maps, search | Simulated locations + GPX | Simulator |
| Background location, accuracy, battery | Outdoors, screen locked | **Device** |
| Health reads/writes and the "no data vs denied" state | Simulator Health app with sample data | Simulator |
| Workout start → finish saves; kill mid-workout → recovered, not duplicated | **Device** (iOS 26), screen locked | Manual |
| Anchored sync applies adds and deletions; background delivery calls completion | Device over a day with real samples | Manual |
| Calendar/reminder add, recurring edit spans | Simulator Calendar/Reminders | Simulator |
| Motion | Device walking | **Device** |
| WeatherKit attribution and quota | Simulator for UI; App Services enabled | Simulator + account |
| FinanceKit / SensorKit / EnergyKit | Granted entitlement + eligible device/region/participant (see each recipe) | **Manual, entitlement + device** |
| PermissionKit / Declared Age Range | Family Sharing child account; parent approves and declines | **Manual, family accounts** |

Apple: [Core Location](https://developer.apple.com/documentation/corelocation) ·
[MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui) ·
[HealthKit privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy) ·
[EventKit access](https://developer.apple.com/documentation/eventkit/accessing-the-event-store) ·
Xcode 27: `AdditionalDocumentation/MapKit-GeoToolbox-PlaceDescriptors.md`.

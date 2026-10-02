<!-- ship-reference
id: ios-notifications-background
kind: mixed
sources: iPhoneOS27.0.sdk UserNotifications / BackgroundTasks (headers) / ActivityKit / AlarmKit / PushKit / CallKit / UIKit interfaces (Xcode 27.0 27A266a — examples type-check via scripts/checks/ios.sh; the reminder date rule runs on the host via scripts/checks/ios_runtime); https://developer.apple.com/documentation/usernotifications ; https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns ; https://developer.apple.com/documentation/uikit/uiapplication/registerforremotenotifications() (registration doesn't need alert permission; 2026-09-28) ; https://developer.apple.com/documentation/backgroundtasks ; https://developer.apple.com/documentation/activitykit ; https://developer.apple.com/documentation/alarmkit ; https://developer.apple.com/documentation/pushkit ; https://developer.apple.com/design/human-interface-guidelines/managing-notifications (all checked 2026-09-24). Written for Ship from Apple's docs and the SDK; no third-party text.
reviewed: 2026-10-01
-->
# Notifications, background work, and live updates

**When to read:** "remind me", "schedule a reminder", push notifications, "notify when…", a tap on a
notification should open a screen, "refresh in the background", "keep uploading after I leave the
app", Live Activities / Dynamic Island, alarms and timers, VoIP calls. **Apple** = platform
behaviour or requirement; **Ship** = default. Wording and interruption levels: `hig-ios.md` §8.

## 1. Pick the mechanism

| Need | Use | Needs |
|---|---|---|
| A reminder at a time or place the person chose | Local notification (`UNCalendarNotificationTrigger` / `UNLocationNotificationTrigger`) | Permission only |
| Tell the person about something that happened on the server | Remote push (APNs) | Push capability + a server |
| Fresh content next time the app opens | `BGAppRefreshTask` (or a silent push) | Background Modes › Background fetch |
| Heavy work that can wait for charging/Wi-Fi | `BGProcessingTask` | Background Modes › Background processing |
| A job the person started that must finish after they leave (export, upload) | `BGContinuedProcessingTask` (iOS 26), with visible progress; or a background `URLSession` for transfers | Info.plist identifier |
| Live progress of something the person started (delivery, timer, score) | Live Activity (ActivityKit, iOS 16.1+) | Widget extension |
| An alarm or countdown that must break through Silent / Focus | AlarmKit (iOS 26) | Permission + usage string |
| Incoming VoIP calls | PushKit VoIP push + CallKit | Must report a call for every VoIP push |

**Apple:** the system decides when background tasks run — minutes to hours, less on Low Power Mode
and for apps the person rarely opens, never after they force-quit the app. **Ship:** never promise
background timing in UI copy.

## 2. Local notifications and reminders

- **Ask in context**, right after the person sets their first reminder — not at launch.
  `.provisional` delivers quietly to Notification Center without a prompt (good for "try it" flows).
- Always read `notificationSettings()` before scheduling; if `.denied`, show the in-app state and a
  button to Settings (`UIApplication.openNotificationSettingsURLString`), don't re-prompt.
- **Identifiers are the update mechanism:** adding a request with an existing identifier replaces
  it. Use the reminder's own id, remove it when the reminder is deleted.
- **Apple limit:** 64 pending local notifications per app — the soonest 64 are kept. For long
  schedules, schedule the next batch when the app runs.
- Calendar triggers match the date components you give, in the device's time zone at fire time:
  "every day at 8:00" = hour + minute only; a one-off = full date. A reminder stored in UTC must be
  converted with the person's calendar before building components. Triggers match to the minute.
- **Reject past one-offs yourself.** For a full date two days in the past, `UNCalendarNotificationTrigger`
  reported a next fire date a week later on an earlier 27 build, and reports none on macOS 27.0
  (26A428, Ship's host test, 2026-10-01), so the reminder silently never fires. Either way, never pass
  a past date: validate in the model and tell the person.
- Interruption level (`hig-ios.md` §8): `.timeSensitive` needs the Time Sensitive capability and a
  real reason; `.critical` needs an Apple-granted entitlement.
- Actions: register `UNNotificationCategory`s with `UNNotificationAction`s at launch; set
  `categoryIdentifier` on the content.

```swift
import UserNotifications

/// Date components for a reminder: daily reminders match hour + minute; one-offs match the full date.
/// Nil for a one-off in the past: the system either reports a later date or none, and says nothing (§2).
nonisolated func reminderComponents(for date: Date, repeatsDaily: Bool, now: Date = .now,
                                    calendar: Calendar = .current) -> DateComponents? {
    if repeatsDaily { return calendar.dateComponents([.hour, .minute], from: date) }
    guard date > now else { return nil }
    return calendar.dateComponents([.year, .month, .day, .hour, .minute], from: date)
}

struct ReminderScheduler {
    let center = UNUserNotificationCenter.current()

    /// Returns false when the person has said no (the caller shows the Settings path) or the date has passed.
    func schedule(id: String, title: String, at date: Date, repeatsDaily: Bool) async throws -> Bool {
        let settings = await center.notificationSettings()
        switch settings.authorizationStatus {
        case .notDetermined:
            guard try await center.requestAuthorization(options: [.alert, .sound, .badge]) else { return false }
        case .denied:
            return false
        default:
            break
        }
        let content = UNMutableNotificationContent()
        content.title = title
        content.sound = .default
        content.userInfo = ["route": "reminder/\(id)"]      // read by the tap handler (§3)
        guard let components = reminderComponents(for: date, repeatsDaily: repeatsDaily) else { return false }
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: repeatsDaily)
        try await center.add(UNNotificationRequest(identifier: id, content: content, trigger: trigger))
        return true
    }

    func cancel(id: String) {
        center.removePendingNotificationRequests(withIdentifiers: [id])
        center.removeDeliveredNotifications(withIdentifiers: [id])
    }
}
```

## 3. Handling taps and foreground delivery

- Set `UNUserNotificationCenter.current().delegate` **before launch finishes** (an app delegate via
  `@UIApplicationDelegateAdaptor`), or the tap that launched the app is lost.
- The tap handler resolves `userInfo` to a **route** and hands it to the app's router
  (`swiftui-ship.md` §4) — never builds a view itself. Validate ids: the item may have been deleted.
- Foreground: return presentation options from `willPresent` (e.g. `[.banner, .sound]`) or the
  notification is silent while the app is open.

```swift
import UIKit
import UserNotifications

@MainActor @Observable final class PendingRoute { var value: String? }

final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    let pending = PendingRoute()

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        UNUserNotificationCenter.current().delegate = self
        return true
    }

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter,
                                            didReceive response: UNNotificationResponse) async {
        let route = response.notification.request.content.userInfo["route"] as? String
        await MainActor.run { pending.value = route }       // the root view observes this and navigates
    }

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter,
                                            willPresent notification: UNNotification) async -> UNNotificationPresentationOptions {
        [.banner, .sound]
    }
}
```

Wire it with `@UIApplicationDelegateAdaptor(AppDelegate.self) var delegate` in the `App`, inject
`delegate.pending` with `.environment`, and navigate when `value` changes.

## 4. Remote push

- **Prerequisites (Apple):** Push Notifications capability; an APNs auth key (.p8) on your server;
  `registerForRemoteNotifications()` at every launch, whether or not the person allowed alerts
  (without permission, pushes arrive silently); send the token from
  `didRegisterForRemoteNotificationsWithDeviceToken` to your server **every launch** — tokens change
  (restore, reinstall, new device). Development and production APNs environments have different
  tokens.
- Payload basics: `aps.alert` (title/body), `sound`, `badge`, `thread-id`, `interruption-level`,
  `relevance-score`; keep custom routing data outside `aps`.
- Modify or decrypt before display (images, end-to-end encrypted text): a **Notification Service
  Extension** with `"mutable-content": 1`; it gets about 30 seconds and must call the handler with
  something even on failure.
- **Silent push** (`"content-available": 1`, no alert) wakes the app to fetch — best effort,
  throttled; not a delivery guarantee. Needs Background Modes › Remote notifications.
- **Test:** push to a simulator by dragging an `.apns` file onto it or `xcrun simctl push`; real
  delivery, tokens, and the service extension need a **device** and your server.

## 5. Background tasks

- Register every task identifier in Info.plist `BGTaskSchedulerPermittedIdentifiers` and handle it:
  SwiftUI `.backgroundTask(.appRefresh("id"))` (iOS 16) or `BGTaskScheduler.shared.register`
  before launch finishes.
- Schedule the **next** refresh inside the handler; a refresh request runs at most once.
- Work must be short, cancellable, and idempotent. In the SwiftUI handler, the task is cancelled
  when time runs out — check `Task.isCancelled` between steps (`swift-practice.md` §2). The handler
  isn't on the main actor: helpers it calls must be `nonisolated` (or hop with `await`).
- Long transfers: background `URLSessionConfiguration.background(withIdentifier:)` hands the upload
  or download to the system; it continues after the app is suspended, and the app is relaunched
  to handle completion.
- **iOS 26 continued processing:** `BGContinuedProcessingTaskRequest(identifier:title:subtitle:)`
  for work the person started (exports); the system shows its progress and the person can cancel
  it. It must report progress; GPU work needs an extra entitlement.
- **Test:** pause in the debugger and run
  `e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"<id>"]`
  (debug only). Real scheduling behaviour needs a device used for days — don't claim it from a run.

```swift
import BackgroundTasks

enum Refresh {
    nonisolated static let id = "com.example.app.refresh"      // also listed in BGTaskSchedulerPermittedIdentifiers

    nonisolated static func scheduleNext() {   // the handler runs off the main actor
        let request = BGAppRefreshTaskRequest(identifier: id)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60)   // a floor, not a promise
        try? BGTaskScheduler.shared.submit(request)
    }
}

struct RefreshingScene: Scene {
    var body: some Scene {
        WindowGroup { Text("Feed") }
            .backgroundTask(.appRefresh(Refresh.id)) {
                Refresh.scheduleNext()
                // fetch, check Task.isCancelled between steps, save
            }
    }
}
```

## 6. Live Activities

- **When (HIG/Ship):** a task the person started, with a clear end, that changes over minutes to
  hours (delivery, ride, workout, match). Not ads, not a static reminder.
- **Setup:** a widget extension with `ActivityConfiguration` (Lock Screen + Dynamic Island compact,
  minimal, expanded); `NSSupportsLiveActivities = YES` in the app's Info.plist.
- Check `ActivityAuthorizationInfo().areActivitiesEnabled` — the person can turn them off.
- Updates: locally with `activity.update(_:)`, or by push (`pushType: .token`, send
  `pushTokenUpdates` to your server). Push-to-start: `Activity<…>.pushToStartTokenUpdates` (17.2).
  Broadcast channels for many viewers of one event (iOS 18). Set `staleDate` so old data looks old.
- **Apple limits:** content state stays small (4 KB); an activity lasts up to 8 hours active, then
  up to 4 more on the Lock Screen; frequent push updates are budgeted.
- End it when the task ends: `end(_:dismissalPolicy:)` with the final state.

```swift
import ActivityKit

struct DeliveryAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable { var minutesAway: Int }
    var orderNumber: String
}

@available(iOS 16.2, *)
func startDeliveryActivity(order: String) throws -> Activity<DeliveryAttributes>? {
    guard ActivityAuthorizationInfo().areActivitiesEnabled else { return nil }
    let content = ActivityContent(state: DeliveryAttributes.ContentState(minutesAway: 25),
                                  staleDate: Date(timeIntervalSinceNow: 15 * 60))
    return try Activity.request(attributes: DeliveryAttributes(orderNumber: order), content: content)
}
```

## 7. Alarms and calls

- **AlarmKit (iOS 26)** — alarms and countdown timers that sound through Silent and Focus, with a
  system alert, Lock Screen, and Dynamic Island UI. Only for alarms/timers the person set; a reminder
  that can wait is a notification (§2).
  - **Alarm vs timer:** an **alarm** fires at a time of day (`Alarm.Schedule.relative` with
    hour/minute and weekly repeats, or `.fixed(date)`); a **timer** counts down a duration
    (`AlarmConfiguration.timer(duration:…)`) and can pause/resume.
  - **Prerequisites:** `NSAlarmKitUsageDescription`; `AlarmManager.shared.requestAuthorization()` —
    `.denied` means no alarms: say so and keep the feature's other parts working.
  - **State:** `.scheduled` → `.countdown` → `.alerting` (and `.paused` for timers). Observe
    `alarmUpdates` and reconcile it with your model at launch: the system is the source of truth —
    an alarm the person stopped or dismissed from the Lock Screen is gone from `alarms`.
  - **Change or cancel:** `cancel(id:)` removes it; to change the time, cancel and schedule again
    with a new id, and store the id in your model. `stop(id:)` ends one that's alerting;
    `pause`/`resume`/`countdown` for timers. Every call can throw (not authorized, unknown id) —
    show the failure, don't show it as set.
  - Buttons: the alert's stop button and an optional secondary button (snooze-style countdown or
    open the app via an App Intent).

```swift
import AlarmKit
import SwiftUI

struct WakeMetadata: AlarmMetadata {}

@available(iOS 26.0, *)
@MainActor @Observable
final class WakeAlarms {
    private(set) var scheduled: [Alarm] = []
    private(set) var problem: String?

    /// Keep the model in step with the system (alarms stopped on the Lock Screen disappear here).
    func watch() async {
        for await alarms in AlarmManager.shared.alarmUpdates { scheduled = alarms }
    }

    func scheduleWeekday(hour: Int, minute: Int) async -> Alarm.ID? {
        do {
            let state = AlarmManager.shared.authorizationState == .notDetermined
                ? try await AlarmManager.shared.requestAuthorization()
                : AlarmManager.shared.authorizationState
            guard state == .authorized else { problem = "Alarms are off for this app in Settings."; return nil }
            let alert = AlarmPresentation.Alert(title: "Wake up",
                                                stopButton: AlarmButton(text: "Stop", textColor: .white, systemImageName: "stop.fill"))
            let attributes = AlarmAttributes<WakeMetadata>(presentation: AlarmPresentation(alert: alert), tintColor: .orange)
            let schedule = Alarm.Schedule.relative(.init(time: .init(hour: hour, minute: minute),
                                                         repeats: .weekly([.monday, .tuesday, .wednesday, .thursday, .friday])))
            let id = UUID()
            _ = try await AlarmManager.shared.schedule(id: id, configuration: .alarm(schedule: schedule, attributes: attributes))
            problem = nil
            return id                                      // store it with the person's alarm in your model
        } catch {
            problem = "Couldn't set the alarm. Try again."
            return nil
        }
    }

    func remove(_ id: Alarm.ID) {
        do { try AlarmManager.shared.cancel(id: id) } catch { problem = "Couldn't remove the alarm." }
    }
}
```

  (`.orange` stands in for a registry color; the tint colors the system's alarm UI.) Compiles;
  **not run** — alarms sounding through Silent/Focus, Lock Screen stop, and repeats need a device.
- **VoIP (PushKit + CallKit):** **Apple:** every VoIP push must be reported to CallKit as an
  incoming call (`reportNewIncomingCall`) before the handler returns, or the app is terminated and
  eventually stops receiving VoIP pushes. Configure the audio session in CallKit's `didActivate`.
  Not for messaging — use regular push. CallKit is unavailable in some regions (App Store rules).

## 8. Verify

| What | How | Level |
|---|---|---|
| Permission flows (first ask, denied, provisional) | Reset the simulator or delete the app; deny, then check the Settings path | Simulator |
| Reminder fires at the right local time, repeats, DST | Unit-test the components; schedule a 1-minute reminder; change time zone in Settings | Simulator + host test |
| Tap opens the right screen (cold and warm launch) | `xcrun simctl push` with a `route`; kill the app first for cold launch | Simulator |
| Remote push end-to-end, service extension | Your server → APNs sandbox → **device** | **Manual, device + server** |
| Background refresh | LLDB simulate launch (§5); then days of real use | Simulator (handler) / **device** (scheduling) |
| Live Activity UI, updates, end | Simulator for layout; push updates on a **device** | Simulator + device |
| AlarmKit: alarm through Silent/Focus; stop from Lock Screen → gone from `alarmUpdates`; cancel; denied state | **Device** | Manual |
| VoIP push reported as a call | **Device** + server | Manual |

Apple: [User Notifications](https://developer.apple.com/documentation/usernotifications) ·
[Registering with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns) ·
[Background Tasks](https://developer.apple.com/documentation/backgroundtasks) ·
[ActivityKit](https://developer.apple.com/documentation/activitykit) ·
[AlarmKit](https://developer.apple.com/documentation/alarmkit) · Xcode 27: `AdditionalDocumentation/SwiftUI-AlarmKit-Integration.md`.

# Push Notifications — iOS Reference

> **When to read:** Dev reads this when requesting notification permissions, handling remote/local notifications, or designing notification content.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `UNUserNotificationCenter` | Central hub for all notifications | Request auth, register categories, handle delegates |
| `UNAuthorizationOptions` | Permission types | `.alert`, `.sound`, `.badge`, `.provisional`, `.criticalAlert` |
| `UNNotificationRequest` | Local notification spec | Includes trigger (time, calendar, location) |
| `UNNotificationContent` | Notification body & metadata | Title, subtitle, body, badge, sound, attachments |
| `UNTimeIntervalNotificationTrigger` | Time-based trigger | Fires after N seconds |
| `UNNotificationServiceExtension` | Rich notification processing | Modify content before display (large media) |
| `UNNotificationPresentationOptions` | How to present in foreground | `.banner`, `.sound`, `.badge` |
| `UNInterruptionLevel` | Notification importance | `.timeSensitive`, `.passive` (iOS 15+) |

## Code Examples

```swift
// 1. Request authorization & register notification settings
import UserNotifications

func requestNotificationPermission() {
    UNUserNotificationCenter.current().requestAuthorization(
        options: [.alert, .sound, .badge, .provisional]
    ) { granted, error in
        if granted {
            DispatchQueue.main.async {
                UIApplication.shared.registerForRemoteNotifications()
            }
        } else if let error = error {
            print("Permission denied: \(error.localizedDescription)")
        }
    }
}

// 2. Schedule a local notification with custom trigger
func scheduleLocalNotification() {
    let content = UNMutableNotificationContent()
    content.title = "Workout Reminder"
    content.subtitle = "Time for your evening run"
    content.body = "You've been sitting for 2 hours. Get moving!"
    content.sound = .default
    content.badge = NSNumber(value: UIApplication.shared.applicationIconBadgeNumber + 1)
    content.userInfo = ["workoutId": "12345"]

    // Interrupt level controls how aggressively notification interrupts user
    if #available(iOS 15.0, *) {
        content.interruptionLevel = .timeSensitive
    }

    // Fire after 10 seconds
    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 10, repeats: false)
    let request = UNNotificationRequest(identifier: "workout-reminder", content: content, trigger: trigger)

    UNUserNotificationCenter.current().add(request) { error in
        if let error = error {
            print("Failed to schedule: \(error.localizedDescription)")
        }
    }
}

// 3. Handle notification interaction in AppDelegate
func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    didReceive response: UNNotificationResponse,
    withCompletionHandler completionHandler: @escaping () -> Void
) {
    let userInfo = response.notification.request.content.userInfo
    let actionId = response.actionIdentifier

    if let workoutId = userInfo["workoutId"] as? String {
        if actionId == UNNotificationDefaultActionIdentifier {
            // User tapped notification
            navigateToWorkout(workoutId)
        }
    }
    completionHandler()
}

// 4. Handle notification in foreground
func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    willPresent notification: UNNotification,
    withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
) {
    let userInfo = notification.request.content.userInfo

    // Even if app is in foreground, show banner & play sound
    if #available(iOS 14.0, *) {
        completionHandler([.banner, .sound, .badge])
    } else {
        completionHandler([.alert, .sound, .badge])
    }
}
```

## Modernized Delegate Methods

iOS 16+ allows async/await in notification delegates instead of completion handlers:

```swift
@MainActor
final class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    static let shared = NotificationDelegate()

    // Modern async/await foreground presentation
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification
    ) async -> UNNotificationPresentationOptions {
        // Return which presentation elements to show
        return [.banner, .sound, .badge]
    }

    // Modern async/await tap handling
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        let userInfo = response.notification.request.content.userInfo
        let actionIdentifier = response.actionIdentifier
        // Handle tap or action
    }
}
```

## Deep-Linking with @Observable Router

Use a shared `@Observable` router to handle notification deep links:

```swift
@Observable @MainActor
final class DeepLinkRouter {
    var pendingDestination: AppDestination?
}

// In NotificationDelegate:
func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    didReceive response: UNNotificationResponse
) async {
    guard let id = response.notification.request.content.userInfo["messageId"] as? String else { return }
    DeepLinkRouter.shared.pendingDestination = .chat(id: id)
}

// In SwiftUI view:
.onChange(of: router.pendingDestination) { _, destination in
    if let destination {
        path.append(destination)
        router.pendingDestination = nil
    }
}
```

## Provisional and Critical Alerts

### Provisional Notifications

Request provisional authorization to deliver silently to Notification Center without interrupting the user:

```swift
try await center.requestAuthorization(
    options: [.alert, .sound, .badge, .provisional]
)
```

The user can then choose to promote them to full notifications.

### Critical Alerts

Critical alerts bypass Do Not Disturb and require special entitlement (request from Apple Developer account). Use only for health, safety, or security:

```swift
try await center.requestAuthorization(
    options: [.alert, .sound, .badge, .criticalAlert]
)
```

## Silent Push with UIBackgroundFetchResult

For background fetches triggered by silent push (`content-available: 1`), use async/await with `UIBackgroundFetchResult`:

```swift
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any]
) async -> UIBackgroundFetchResult {
    guard let updateType = userInfo["updateType"] as? String else {
        return .noData
    }
    do {
        try await DataSyncService.shared.sync(trigger: updateType)
        return .newData
    } catch {
        return .failed
    }
}
```

## Common Mistakes

1. **Register for remote notifications before requesting authorization.**
   Call `requestAuthorization` first, then `registerForRemoteNotifications()`.

2. **Convert device token with `String(data:encoding:)`.**
   Use hex: `deviceToken.map { String(format: "%02x", $0) }.joined()`.

3. **Assume notifications always arrive.**
   APNs is best-effort. Design features that degrade gracefully; use background refresh as fallback.

4. **Put sensitive data directly in the notification payload.**
   Use `mutable-content: 1` with a Notification Service Extension to modify content before display.

5. **Forget foreground handling.**
   Without `willPresent`, notifications are silently suppressed. Implement and return `.banner`, `.sound`, `.badge`.

6. **Set delegate too late or use SwiftUI without AppDelegate adaptor.**
   Set delegate in `App.init`; use `UIApplicationDelegateAdaptor` for APNs token callbacks.

7. **Send device token only once.**
   Device tokens change. Re-send on every callback, not just the first time.

8. **Ignore async/await modernization.**
   Delegate methods are now `async` and return directly instead of using completion handlers.

9. **Forget to handle provisional and critical alert options.**
   Always check and respect the authorization status; provisional may require user upgrades.

10. **Use deprecated completion handler patterns.**
    Use async/await instead of closure-based `willPresent` and `didReceive` callbacks.

## Deep-Linking from Notifications with @Observable Router

Route notification taps to the correct screen using a shared `@Observable` router:

```swift
@Observable @MainActor
final class DeepLinkRouter {
    var pendingDestination: AppDestination?
}

// In NotificationDelegate:
func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    didReceive response: UNNotificationResponse
) async {
    guard let id = response.notification.request.content.userInfo["messageId"] as? String else { return }
    DeepLinkRouter.shared.pendingDestination = .chat(id: id)
}

// In SwiftUI view:
.onChange(of: router.pendingDestination) { _, destination in
    if let destination {
        path.append(destination)
        router.pendingDestination = nil
    }
}
```

## Provisional & Critical Alerts

**Provisional Notifications:** Deliver silently to Notification Center without interrupting the user; user can later promote to full notifications:

```swift
try await center.requestAuthorization(options: [.alert, .sound, .badge, .provisional])
```

**Critical Alerts:** Bypass Do Not Disturb and require special Apple entitlement. Use only for health/safety/security:

```swift
try await center.requestAuthorization(options: [.alert, .sound, .badge, .criticalAlert])
```

## Silent Push with UIBackgroundFetchResult

For background fetches triggered by silent push (`content-available: 1`), use async/await with `UIBackgroundFetchResult`:

```swift
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any]
) async -> UIBackgroundFetchResult {
    guard let updateType = userInfo["updateType"] as? String else {
        return .noData
    }
    do {
        try await DataSyncService.shared.sync(trigger: updateType)
        return .newData
    } catch {
        return .failed
    }
}
```

## Review Checklist

- [ ] `requestAuthorization()` called at app startup or first relevant screen
- [ ] Check granted status before calling `registerForRemoteNotifications()`
- [ ] `UNUserNotificationCenterDelegate` set on `UNUserNotificationCenter.current()`
- [ ] Both `willPresent()` and `didReceive()` implemented
- [ ] Foreground presentation options appropriate (banner/sound/badge)
- [ ] `interruptionLevel` set correctly for notification urgency
- [ ] Custom actions (buttons) registered with UNNotificationCategory
- [ ] Provisional auth used only for less critical notifications
- [ ] Badge count managed (incremented/cleared appropriately)
- [ ] userInfo dictionary safe (check key existence before casting)
- [ ] Deep links in notification payload validated before navigation
- [ ] Notification sounds < 30 seconds; included in app bundle or downloaded

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

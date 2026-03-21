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

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Requesting notifications without checking `requestAuthorization()` result | Always check granted boolean; only register for remote notifications if approved |
| Calling `registerForRemoteNotifications()` on background thread | Dispatch to main thread: `DispatchQueue.main.async { ... }` |
| Not implementing `willPresent()` delegate; missing foreground notifications | Implement both `willPresent()` and `didReceive()` in UNUserNotificationCenterDelegate |
| Provisional auth without clear explanation | Use `.provisional` carefully; only for non-critical notifications |
| Ignoring `interruptionLevel`; all notifications equally disruptive | Use `.timeSensitive` only for urgent alerts (calls, alarms); `.passive` for background info |

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

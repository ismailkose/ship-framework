# AlarmKit — iOS Reference

> **When to read:** Dev reads this when scheduling alarms, customizing alarm UI, managing recurring alarms, or integrating with system alarm features (iOS 18+).

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `AlarmAttributes` | SwiftUI dynamic island metadata for alarm (time, label, sound) |
| `ActivityKit` | Framework for managing live activities and alarm status |
| `AlarmScheduler` | Schedule and manage alarms in system |
| `AlarmNotification` | Customizable alarm notification with sound, haptics, UI |
| `AlarmCharacteristics` | Defines alarm behavior (snooze, repeat, vibration pattern) |

**Key Types:**
- `AlarmAttributes` — Live activity content (time, label, sound choice)
- `AlertConfiguration` — Sound, haptic feedback, notification sound
- `RecurrencePattern` — Daily, weekly, custom patterns

---

## Code Examples

**Example 1: Define AlarmAttributes and schedule alarm**
```swift
import ActivityKit
import SwiftUI

// Define alarm metadata (shown in Dynamic Island)
struct AlarmAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var time: Date
        var label: String
        var soundName: String
        var isActive: Bool
    }

    var alarmID: UUID
}

class AlarmManager: NSObject {
    func scheduleAlarm(at time: Date, label: String, soundName: String) async {
        do {
            let alarmID = UUID()

            // Create live activity for Dynamic Island
            let initialState = AlarmAttributes.ContentState(
                time: time,
                label: label,
                soundName: soundName,
                isActive: true
            )

            let attributes = AlarmAttributes(alarmID: alarmID)

            let activity = try Activity<AlarmAttributes>.request(
                attributes: attributes,
                contentState: initialState,
                options: .init(dismissalPolicy: .default)
            )

            print("Alarm scheduled: \(label) at \(time)")

            // Store alarm in UserDefaults
            let defaults = UserDefaults.standard
            var alarms = defaults.array(forKey: "alarms") as? [String] ?? []
            alarms.append(alarmID.uuidString)
            defaults.set(alarms, forKey: "alarms")

            // Schedule local notification
            scheduleNotification(alarmID: alarmID, time: time, label: label)
        } catch {
            print("Failed to schedule alarm: \(error)")
        }
    }

    func scheduleNotification(alarmID: UUID, time: Date, label: String) {
        let content = UNMutableNotificationContent()
        content.title = label
        content.body = "Alarm"
        content.sound = UNNotificationSound(named: UNNotificationSoundName(rawValue: "alarm_sound.caf"))
        content.badge = NSNumber(value: 1)

        // Add vibration pattern via userInfo
        content.userInfo["alarmID"] = alarmID.uuidString

        let components = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: time)
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: false)
        let request = UNNotificationRequest(identifier: alarmID.uuidString, content: content, trigger: trigger)

        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("Notification schedule failed: \(error)")
            }
        }
    }
}
```

**Example 2: Customize alarm UI and sound selection**
```swift
import SwiftUI

struct AlarmView: View {
    @State var alarmTime = Date()
    @State var alarmLabel = "Wake up"
    @State var selectedSound = "Alarm Tone 1"
    @State var repeatDaily = false
    @State var isPresented = false

    let sounds = ["Alarm Tone 1", "Alarm Tone 2", "Bells", "Digital", "Gentle", "Radar"]

    var body: some View {
        Form {
            Section("Alarm Time") {
                DatePicker("Time", selection: $alarmTime, displayedComponents: .hourAndMinute)
                    .datePickerStyle(.wheel)
            }

            Section("Label") {
                TextField("Alarm label (optional)", text: $alarmLabel)
            }

            Section("Sound") {
                Picker("Select Sound", selection: $selectedSound) {
                    ForEach(sounds, id: \.self) { sound in
                        Text(sound).tag(sound)
                    }
                }

                // Play preview
                Button("Play Preview") {
                    playPreviewSound(selectedSound)
                }
            }

            Section("Repeat") {
                Toggle("Every Day", isOn: $repeatDaily)
            }

            Button("Save Alarm") {
                saveAlarm()
            }
        }
    }

    func playPreviewSound(_ soundName: String) {
        let soundFile = "\(soundName.lowercased().replacingOccurrences(of: " ", with: "_")).caf"
        if let url = Bundle.main.url(forResource: soundFile, withExtension: nil) {
            try? AVAudioPlayer(contentsOf: url).play()
        }
    }

    func saveAlarm() {
        Task {
            let alarmManager = AlarmManager()
            await alarmManager.scheduleAlarm(at: alarmTime, label: alarmLabel, soundName: selectedSound)
            isPresented = false
        }
    }
}
```

**Example 3: Manage recurring alarms and snooze**
```swift
import UserNotifications

class RecurringAlarmManager {
    func scheduleRecurringAlarm(
        at time: Date,
        label: String,
        pattern: RecurrencePattern,
        soundName: String
    ) async {
        let alarmID = UUID()

        switch pattern {
        case .daily:
            // Schedule for 365 days
            for day in 0..<365 {
                var dateComponents = Calendar.current.dateComponents([.hour, .minute], from: time)
                dateComponents.day = Calendar.current.component(.day, from: Date()) + day
                dateComponents.month = Calendar.current.component(.month, from: Date())
                dateComponents.year = Calendar.current.component(.year, from: Date())

                let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)

                let content = UNMutableNotificationContent()
                content.title = label
                content.sound = UNNotificationSound(named: UNNotificationSoundName(rawValue: soundName))
                content.badge = NSNumber(value: 1)

                let request = UNNotificationRequest(
                    identifier: "\(alarmID)-\(day)",
                    content: content,
                    trigger: trigger
                )

                try? await UNUserNotificationCenter.current().add(request)
            }

        case .weekdays:
            let weekdays: [Int] = [2, 3, 4, 5, 6]  // Mon-Fri
            for weekday in weekdays {
                var dateComponents = Calendar.current.dateComponents([.hour, .minute], from: time)
                dateComponents.weekday = weekday

                let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)

                let content = UNMutableNotificationContent()
                content.title = label
                content.sound = UNNotificationSound(named: UNNotificationSoundName(rawValue: soundName))

                let request = UNNotificationRequest(
                    identifier: "\(alarmID)-weekday-\(weekday)",
                    content: content,
                    trigger: trigger
                )

                try? await UNUserNotificationCenter.current().add(request)
            }
        }
    }

    func snoozeAlarm(alarmID: UUID, minutes: Int = 9) {
        // Snooze = cancel current notification, reschedule for 9 minutes later
        UNUserNotificationCenter.current().removePendingNotificationRequests(
            withIdentifiers: [alarmID.uuidString]
        )

        let content = UNMutableNotificationContent()
        content.title = "Alarm Snoozed"
        content.body = "Alarm in \(minutes) minutes"

        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: TimeInterval(minutes * 60),
            repeats: false
        )

        let request = UNNotificationRequest(
            identifier: "\(alarmID)-snooze",
            content: content,
            trigger: trigger
        )

        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("Snooze failed: \(error)")
            } else {
                print("Alarm snoozed for \(minutes) minutes")
            }
        }
    }
}

enum RecurrencePattern {
    case daily
    case weekdays
    case custom([Int])  // Array of weekday indices
}
```

---

## Common Mistakes

**Mistake 1: Not checking iOS 18+ availability**
```swift
// ❌ WRONG: AlarmKit only available on iOS 18+
let alarmManager = AlarmManager()
await alarmManager.scheduleAlarm(at: time, label: "Wake Up", soundName: "Tone")

// ✅ CORRECT: Check availability
if #available(iOS 18, *) {
    let alarmManager = AlarmManager()
    await alarmManager.scheduleAlarm(at: time, label: "Wake Up", soundName: "Tone")
}
```

**Mistake 2: Not requesting user notification permission**
```swift
// ❌ WRONG: Scheduling without permission; notifications silently fail
scheduleNotification(...)

// ✅ CORRECT: Request permission first
func requestNotificationPermission() {
    UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
        if granted {
            print("Notification permission granted")
        } else {
            print("Permission denied or error: \(error?.localizedDescription ?? "")")
        }
    }
}
```

**Mistake 3: Not including sound file in bundle**
```swift
// ❌ WRONG: Sound file not in project
let sound = UNNotificationSound(named: UNNotificationSoundName(rawValue: "alarm.caf"))

// ✅ CORRECT: Verify sound is in Xcode project
// 1. Add .caf or .m4a file to project
// 2. Ensure it's in target's Build Phases > Copy Bundle Resources
// 3. Reference correctly
let sound = UNNotificationSound(named: UNNotificationSoundName(rawValue: "alarm.caf"))
```

**Mistake 4: Not canceling alarms when user deletes**
```swift
// ❌ WRONG: Notification remains scheduled
func deleteAlarm(_ alarmID: UUID) {
    // Delete from database but notification still fires
}

// ✅ CORRECT: Cancel notification and activity
func deleteAlarm(_ alarmID: UUID) {
    // Remove scheduled notification
    UNUserNotificationCenter.current().removePendingNotificationRequests(
        withIdentifiers: [alarmID.uuidString]
    )

    // Remove dynamic island activity
    Task {
        for activity in Activity<AlarmAttributes>.activities {
            if activity.attributes.alarmID == alarmID {
                await activity.end(dismissalPolicy: .immediate)
            }
        }
    }
}
```

**Mistake 5: Recurring alarm conflicts (duplicate schedules)**
```swift
// ❌ WRONG: Schedules both daily and specific day
scheduleRecurringAlarm(pattern: .daily)
scheduleRecurringAlarm(pattern: .weekdays)
// User gets multiple notifications per day

// ✅ CORRECT: Choose one pattern or cancel before rescheduling
func updateAlarm(_ alarmID: UUID, pattern: RecurrencePattern) {
    // First cancel all existing notifications for this alarm
    UNUserNotificationCenter.current().removePendingNotificationRequests(
        withIdentifiers: [alarmID.uuidString]
    )

    // Then schedule new pattern
    Task {
        await scheduleRecurringAlarm(at: time, label: label, pattern: pattern, soundName: sound)
    }
}
```

---

## Review Checklist

- [ ] iOS 18+ availability check (`#available(iOS 18, *)`)
- [ ] User notification permission requested via `UNUserNotificationCenter.requestAuthorization()`
- [ ] `AlarmAttributes` defined with `ContentState` struct
- [ ] Alarm sound files (.caf, .m4a) added to Xcode project
- [ ] Sound files verified in Build Phases > Copy Bundle Resources
- [ ] `Activity<AlarmAttributes>.request()` called to show in Dynamic Island
- [ ] UNNotificationRequest created with proper date components
- [ ] Recurring alarms managed: no duplicate notifications
- [ ] Snooze functionality cancels and reschedules notification
- [ ] Delete alarm removes both notification and activity
- [ ] Alarm label/time updated via activity state mutations
- [ ] Haptic feedback considered (AudioServicesPlaySystemSound for vibration)
- [ ] Alarm sound plays even when device is silent (use critical alert if needed)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

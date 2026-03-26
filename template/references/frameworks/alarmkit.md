# AlarmKit — iOS Reference

> **When to read:** Dev reads this when scheduling alarms, customizing alarm UI with Lock Screen and Dynamic Island, managing recurring alarms, implementing countdown timers, handling snooze/stop actions, or integrating system alarm features (iOS 26+).

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose | Key Methods |
|------|---------|--------------|
| `AlarmManager` | Central API for scheduling, pausing, resuming, stopping alarms | `requestAuthorization()`, `schedule(id:configuration:)`, `alarmUpdates`, `pause(id:)`, `resume(id:)`, `stop(id:)`, `countdown(id:)`, `cancel(id:)` |
| `AlarmManager.AlarmConfiguration` | Configuration enum (alarm or timer) with schedule, attributes, intents, sound | `.alarm(schedule:...)` or `.timer(duration:...)` |
| `Alarm.Schedule` | When the alarm fires (fixed date or relative time) | `.fixed(Date)`, `.relative(RelativeSchedule)` |
| `Alarm.Schedule.RelativeSchedule` | Time of day and recurrence pattern | `.never`, `.weekly([.monday, ...])`, `time: TimeComponents` |
| `Alarm.CountdownDuration` | Pre-alert and post-alert countdown phases | `preAlert`, `postAlert` seconds |
| `AlarmAttributes` | Live Activity attributes with presentation, metadata, tint color | `presentation`, `metadata`, `tintColor` |
| `AlarmPresentation` | UI content for alert, countdown, and paused states | `.alert(Alert)`, `.countdown(Countdown)`, `.paused(Paused)` |
| `AlarmPresentationState` | System-managed content state with mode (alert/countdown/paused) | `mode`, `alarmID` |
| `AlarmButton` | Action button appearance (text, color, icon) | `text`, `textColor`, `systemImageName` |
| `ActivityKit` | Framework for managing live activities and alarm status | `Activity<AlarmAttributes>` |

**Key Concepts:**
- `AlarmManager.authorizationUpdates` — AsyncSequence for authorization state changes
- `AlarmManager.alarmUpdates` — AsyncSequence for alarm state transitions
- `AlarmButton` behavior enum — `.countdown` (snooze) or `.custom` (open app)
- Widget extension **required** for non-alerting countdown/paused Live Activity UI

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

**Example 3: Alarm Schedule types**
```swift
import AlarmKit

// Fixed: fire at an exact Date (one-time)
let fixed: Alarm.Schedule = .fixed(Date())

// Relative one-time: fire at 7:30 AM, no repeat
let oneTime: Alarm.Schedule = .relative(.init(
    time: .init(hour: 7, minute: 30),
    repeats: .never
))

// Recurring weekdays: fire at 6:00 AM Mon-Fri
let weekday: Alarm.Schedule = .relative(.init(
    time: .init(hour: 6, minute: 0),
    repeats: .weekly([.monday, .tuesday, .wednesday, .thursday, .friday])
))
```

**Example 4: Countdown duration for timers with snooze**
```swift
import AlarmKit

// 10-minute countdown before alert, 5-minute snooze countdown
let countdown = Alarm.CountdownDuration(
    preAlert: 600,   // 10 minutes
    postAlert: 300   // 5 minutes snooze
)

let config = AlarmManager.AlarmConfiguration.timer(
    duration: 300,  // 5 minute timer
    attributes: attributes,
    stopIntent: StopTimerIntent(timerID: id.uuidString),
    sound: .default,
    countdownDuration: countdown
)
```

**Example 5: Alarm state machine observation**
```swift
import AlarmKit

let manager = AlarmManager.shared

// Observe state transitions
for await updatedAlarms in manager.alarmUpdates {
    for alarm in updatedAlarms {
        switch alarm.state {
        case .scheduled:  print("Waiting to fire")
        case .countdown:  print("Counting down")
        case .paused:     print("Paused by user")
        case .alerting:   print("Alarm firing!")
        @unknown default: break
        }
    }
}
```

**Example 6: Snooze action with countdown behavior**
```swift
import AlarmKit

let snoozeButton = AlarmButton(
    text: "Snooze",
    textColor: .white,
    systemImageName: "bell.slash"
)

let alert = AlarmPresentation.Alert(
    title: "Wake Up",
    secondaryButton: snoozeButton,
    secondaryButtonBehavior: .countdown  // Snooze restarts countdown
)
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

- [ ] `NSAlarmKitUsageDescription` added to Info.plist with descriptive text
- [ ] iOS 26+ availability check (AlarmKit requires iOS 26+)
- [ ] `AlarmManager.requestAuthorization()` called; `.denied` state handled
- [ ] `AlarmPresentation` covers all relevant states (alert, countdown, paused)
- [ ] Widget extension target added for countdown/paused Live Activity UI
- [ ] `AlarmAttributes` metadata type conforms to `AlarmMetadata` protocol
- [ ] Alarm ID stored for later pause/resume/stop/cancel operations
- [ ] `alarmManager.alarmUpdates` async sequence observed for state tracking
- [ ] `stopIntent` and `secondaryIntent` are valid `LiveActivityIntent` implementations
- [ ] `Alarm.Schedule` uses `.fixed()` or `.relative()` with proper recurrence pattern
- [ ] `Alarm.CountdownDuration` preAlert/postAlert set for timer snooze behavior
- [ ] `AlarmButton` behavior set to `.countdown` for snooze, `.custom` for app launch
- [ ] Tint color set on `AlarmAttributes` to differentiate from other apps
- [ ] Error handling for `AlarmManager.AlarmError.maximumLimitReached`
- [ ] `authorizationUpdates` observed if authorization can change during runtime
- [ ] Tested on device (alarm sound/vibration differs in Simulator)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

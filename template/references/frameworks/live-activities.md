# Live Activities — iOS Reference

> **When to read:** Dev reads this when displaying real-time status on lock screen or Dynamic Island.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `ActivityKit` | Framework for live activities | Import for .activity modifier |
| `ActivityAttributes` | Data shared across views | Published updates + state |
| `@State var activity` | Holds active activity reference | Used to update/end live activity |
| `Activity<T>` | Generic activity container | Has attributes, contentState, id |
| `ActivityState` | Activity lifecycle enum | `.active`, `.ended`, `.dismissed` |
| `.dynamicIsland()` | Dynamic Island presentation | Compact, expanded, minimal regions |
| `PushToken` | Remote notification token | From activity.pushTokenUpdates |
| `WidgetKit` view support | Lock screen + Dynamic Island rendering | Uses SwiftUI structures |

## Code Examples

```swift
// 1. Define ActivityAttributes and ContentState
import ActivityKit

struct DeliveryAttributes: ActivityAttributes {
    typealias Status = DeliveryStatus

    struct ContentState: Codable, Hashable {
        var eta: TimeInterval
        var driverName: String
        var distance: Double
    }

    var orderId: String
    var driverPhone: String
}

enum DeliveryStatus {
    case active
    case completed
}

// 2. Request live activity permission and start
func requestLiveActivityPermission() async {
    do {
        try await ActivityAuthorizationInfo.current.requestPermission(for: .default)
        print("Live Activity permission granted")
    } catch {
        print("Live Activity permission denied: \(error)")
    }
}

func startDeliveryActivity() async {
    let attributes = DeliveryAttributes(
        orderId: "ORD-12345",
        driverPhone: "+1234567890"
    )
    let initialState = DeliveryAttributes.ContentState(
        eta: 600,
        driverName: "Alex",
        distance: 2.5
    )

    do {
        let activity = try Activity<DeliveryAttributes>.request(
            attributes: attributes,
            contentState: initialState,
            pushType: .token
        )

        // Listen for push token updates
        for await token in activity.pushTokenUpdates {
            let tokenString = token.map { String(format: "%02x", $0) }.joined()
            print("Activity token: \(tokenString)")
            // Send token to backend for push updates
        }
    } catch {
        print("Failed to start activity: \(error)")
    }
}

// 3. Update live activity with new state
func updateDeliveryStatus(activity: Activity<DeliveryAttributes>, eta: TimeInterval) async {
    let updatedState = DeliveryAttributes.ContentState(
        eta: eta,
        driverName: "Alex",
        distance: 1.2
    )

    await activity.update(using: updatedState)
}

// 4. End live activity
func completeDelivery(activity: Activity<DeliveryAttributes>) async {
    let finalState = DeliveryAttributes.ContentState(
        eta: 0,
        driverName: "Alex",
        distance: 0
    )

    await activity.end(using: finalState, dismissalPolicy: .immediate)
}

// 5. Lock screen + Dynamic Island view
struct DeliveryLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: DeliveryAttributes.self) { context in
            // Lock screen view
            VStack(alignment: .leading) {
                HStack {
                    VStack(alignment: .leading) {
                        Text("Delivery in progress")
                            .font(.headline)
                        Text("\(Int(context.state.distance)) km away")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                    Text("\(Int(context.state.eta / 60))m")
                        .font(.title2)
                        .fontWeight(.bold)
                }
                ProgressView(value: 1 - (context.state.distance / 5))
            }
            .padding()
            .activitySystemActionForegroundColor(.blue)
            .activityBackgroundTint(.white)
        } dynamicIsland: { context in
            // Dynamic Island presentation
            DynamicIsland {
                // Expanded view
                DynamicIslandExpandedRegion(.leading) {
                    Label("\(context.attributes.orderId)", systemImage: "box.truck.badge.clock")
                        .font(.caption)
                }

                DynamicIslandExpandedRegion(.trailing) {
                    HStack {
                        Image(systemName: "mappin.circle.fill")
                        Text("\(Int(context.state.distance))km")
                    }
                    .font(.caption)
                }

                DynamicIslandExpandedRegion(.bottom) {
                    VStack {
                        ProgressView(value: 1 - (context.state.distance / 5))
                        Text("Driver: \(context.state.driverName)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(.horizontal)
                }
            } compactLeading: {
                // Compact leading view
                Image(systemName: "box.truck")
            } compactTrailing: {
                // Compact trailing view
                Text("\(Int(context.state.eta / 60))m")
                    .fontWeight(.bold)
            } minimal: {
                // Minimal view (when space is very limited)
                Image(systemName: "box.truck")
            }
            .keylineTint(.blue)
        }
    }
}

// 6. SwiftUI view that manages activity lifecycle
@main
struct DeliveryApp: App {
    @State private var activity: Activity<DeliveryAttributes>?

    var body: some Scene {
        WindowGroup {
            ZStack {
                if let activity = activity {
                    VStack {
                        Text("Delivery Active")
                        Button("End Delivery") {
                            Task {
                                await activity.end(
                                    using: DeliveryAttributes.ContentState(
                                        eta: 0, driverName: "", distance: 0
                                    ),
                                    dismissalPolicy: .immediate
                                )
                                self.activity = nil
                            }
                        }
                    }
                } else {
                    VStack {
                        Text("No Active Delivery")
                        Button("Start Delivery") {
                            Task {
                                await startDeliveryActivity()
                            }
                        }
                    }
                }
            }
        }
    }
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Not requesting ActivityKit permission | Call `ActivityAuthorizationInfo.current.requestPermission()` at app launch |
| Not listening for push token updates | Iterate `activity.pushTokenUpdates` async sequence; send tokens to backend |
| Updating with nil values causing crashes | Always provide complete ContentState; don't omit fields |
| Not dismissing activity after completion | Call `activity.end(dismissalPolicy: .immediate)` when done |
| Over-updating frequency; excessive state changes | Throttle updates; rapid updates drain battery and stress system |

## Review Checklist

- [ ] ActivityAttributes defined with proper Codable conformance
- [ ] ContentState includes all displayed data
- [ ] Permission requested via `ActivityAuthorizationInfo.requestPermission()`
- [ ] Activity request wrapped in try/catch
- [ ] Push token updates forwarded to backend
- [ ] State updates use complete ContentState (no partial updates)
- [ ] Activity ended with final state & dismissal policy
- [ ] Dynamic Island views implemented (expanded, compact, minimal)
- [ ] Lock screen view renders correctly for all screen sizes
- [ ] No UI blocking; all activity ops async
- [ ] Update frequency throttled (not > every 15 seconds)
- [ ] Activity removed from active set after dismissal

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

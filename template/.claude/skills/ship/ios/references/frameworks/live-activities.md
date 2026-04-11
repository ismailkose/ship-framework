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
| `ActivityStyle` | Activity persistence mode | `.standard` (persists) vs `.transient` (auto-dismiss) — iOS 26+ |
| `ClServiceSession` (iOS 18+) | Manages authorization | Manages location access for Live Activities |
| Scheduled Live Activities (iOS 26+) | Start at future time | System-initiated without app |
| Channel-based push (iOS 18+) | Broadcast updates | Send to multiple activities via channel name |
| `NSSupportsLiveActivitiesFrequentUpdates` | Increase push budget | For updates > 1/minute (sports, tracking) |
| `.keylineTint()` | Dynamic Island border tint | Apply subtle color to DI border |

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

### APNs Payload Format

Send HTTP/2 POST to APNs with headers and JSON body:

**Headers:**
- `apns-push-type: liveactivity`
- `apns-topic: <bundle-id>.push-type.liveactivity`
- `apns-priority: 5` (low) or `10` (high, shows alert)

**Update Payload:**

```json
{
    "aps": {
        "timestamp": 1700000000,
        "event": "update",
        "content-state": {
            "driverName": "Alex",
            "estimatedDeliveryTime": {
                "lowerBound": 1700000000,
                "upperBound": 1700001800
            },
            "currentStep": "delivering"
        },
        "stale-date": 1700000300,
        "alert": {
            "title": "Delivery Update",
            "body": "Your driver is nearby!"
        }
    }
}
```

**End Payload:** Same structure with `"event": "end"` and optional `"dismissal-date"`.

### Push-to-Start (iOS 17.2+)

```swift
Task {
    for await token in Activity<DeliveryAttributes>.pushToStartTokenUpdates {
        let tokenString = token.map { String(format: "%02x", $0) }.joined()
        try await ServerAPI.shared.registerPushToStartToken(tokenString)
    }
}
```

### Scheduled Live Activities (iOS 26+)

```swift
let scheduledDate = Calendar.current.date(
    from: DateComponents(year: 2026, month: 3, day: 15, hour: 19, minute: 0)
)!

let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token,
    start: scheduledDate
)
```

### ActivityStyle (iOS 26+)

```swift
// Standard: persists until explicitly ended (default)
let activity = try Activity.request(
    attributes: attributes, content: content,
    pushType: .token, style: .standard
)

// Transient: system may dismiss automatically (for short-lived updates)
let activity = try Activity.request(
    attributes: attributes, content: content,
    pushType: .token, style: .transient
)
```

### Channel-Based Push (iOS 18+)

```swift
let activity = try Activity.request(
    attributes: attributes, content: content,
    pushType: .channel("delivery-updates")
)
```

### Lock Screen Sizing Details

```swift
ActivityConfiguration(for: DeliveryAttributes.self) { context in
    // Lock Screen content -- keep under ~160 points height
    VStack(alignment: .leading, spacing: 8) {
        Text("Order #\(context.attributes.orderNumber)").font(.headline)
        Text(context.state.driverName).font(.subheadline)
    }.padding()
} dynamicIsland: { context in
    DynamicIsland { /* ... */ }
}
.supplementalActivityFamilies([.small, .medium])  // Opt into compact sizing
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Not requesting ActivityKit permission | Call `ActivityAuthorizationInfo.current.requestPermission()` at app launch |
| Not listening for push token updates | Iterate `activity.pushTokenUpdates` async sequence; send tokens to backend |
| Updating with nil values causing crashes | Always provide complete ContentState; don't omit fields |
| Not dismissing activity after completion | Call `activity.end(dismissalPolicy: .immediate)` when done |
| Over-updating frequency; excessive state changes | Throttle updates; rapid updates drain battery and stress system |
| Missing `NSSupportsLiveActivities` in Info.plist | Add `NSSupportsLiveActivities = YES` to host app's Info.plist (not extension) |
| Frequent updates without budget declaration | Add `NSSupportsLiveActivitiesFrequentUpdates = YES` for > 1/minute updates |
| Forgetting to set `NSSupportsLiveActivitiesFrequentUpdates` | Required for sports, ride tracking, live scores |

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
- [ ] APNs payload format correct (headers + JSON structure)
- [ ] Push-to-start tokens registered (iOS 17.2+)
- [ ] Scheduled Live Activities use `start:` parameter (iOS 26+)
- [ ] `ActivityStyle` set appropriately (`.standard` vs `.transient`)
- [ ] Channel-based push used for broadcasts (iOS 18+)
- [ ] `NSSupportsLiveActivitiesFrequentUpdates` declared if > 1/minute updates
- [ ] `.keylineTint()` applied to Dynamic Island for branding
- [ ] Lock Screen layout under ~160 points height
- [ ] `.supplementalActivityFamilies([.small, .medium])` configured

## Enriched Common Mistakes

- ❌ Not requesting ActivityKit permission — call `ActivityAuthorizationInfo.current.requestPermission()` at app launch
- ❌ Not listening for push token updates — iterate `activity.pushTokenUpdates` and send to backend
- ❌ Updating with incomplete ContentState — always provide complete state, no partial fields
- ❌ Over-updating frequency — throttle to prevent battery drain and system stress
- ❌ Forgetting `NSSupportsLiveActivities` in Info.plist — add to host app, not extension

## Enriched Review Checklist

- [ ] ActivityKit permission requested at launch
- [ ] Push token updates streamed to backend server
- [ ] Complete ContentState provided on every update
- [ ] Update frequency throttled appropriately
- [ ] `NSSupportsLiveActivities = YES` in host app Info.plist
- [ ] Activity lifecycle properly managed (start/update/end)
- [ ] Push updates handle errors gracefully

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

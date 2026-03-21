# SharePlay — iOS Reference

> **When to read:** Dev reads this when building shared experiences, group activities, coordinated media playback, or multi-user synchronization.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `GroupActivity` | Protocol defining shared activity (what's being coordinated) |
| `GroupSession` | Active session between participants; handles message passing |
| `GroupStateObserver` | Monitors session state (active, inactive, joined, left) |
| `Shareable` | Protocol for objects that can sync state across session |
| `SharedImmutableReference` | Reference to immutable data synced in group |
| `SharedMutableReference` | Mutable state binding (SwiftUI) synced across group |
| `AVPlayer` | Extended to support synchronized playback in group sessions |
| `GroupActivitySharingController` | UI for inviting others to activity |

**Key Protocols:**
- `GroupActivity` — Codable, defines session ID and metadata
- `Shareable` — Encode/decode for transmission between participants

---

## Code Examples

**Example 1: Define a group activity (game/quiz session)**
```swift
import GroupActivities
import Codable

struct QuizActivity: GroupActivity, Codable {
    var metadata: GroupActivityMetadata {
        var metadata = GroupActivityMetadata()
        metadata.title = "Quiz Battle"
        metadata.description = "Compete in live quiz with friends"
        metadata.type = .generic
        return metadata
    }

    let quizID: UUID
    let topic: String
}

// In your quiz view controller
@main
struct QuizApp: App {
    var body: some Scene {
        WindowGroup {
            QuizView()
                .task {
                    await prepareGroupActivity()
                }
        }
    }

    func prepareGroupActivity() async {
        do {
            let activity = QuizActivity(quizID: UUID(), topic: "Science")
            try await activity.activate()
        } catch {
            print("Could not activate activity: \(error)")
        }
    }
}
```

**Example 2: Join and monitor a group session**
```swift
import GroupActivities

struct QuizView: View {
    @State var groupSession: GroupSession<QuizActivity>?
    @State var messagesTask: Task<Void, Never>?

    var body: some View {
        VStack {
            Text("Quiz Battle")
            Button("Invite Friends") {
                Task {
                    await inviteFriends()
                }
            }
        }
        .task {
            for await session in QuizActivity.sessions() {
                groupSession = session
                messagesTask = Task {
                    await handleSessionMessages(session)
                }
            }
        }
        .onChange(of: groupSession) { _, newSession in
            if newSession == nil {
                messagesTask?.cancel()
            }
        }
    }

    func inviteFriends() async {
        guard let session = groupSession else {
            print("No active session")
            return
        }

        do {
            try await session.activity.activate()
        } catch {
            print("Cannot invite: \(error)")
        }
    }

    func handleSessionMessages(_ session: GroupSession<QuizActivity>) async {
        for await message in session.messages(of: QuizMessage.self) {
            print("Message from \(message.source.displayName): \(message.content.text)")
            // Update quiz state based on message
        }
    }
}

// Message type sent between participants
struct QuizMessage: Codable {
    let playerID: UUID
    let text: String
    let score: Int
}
```

**Example 3: Synchronized AVPlayer playback**
```swift
import AVKit
import GroupActivities

struct WatchPartyActivity: GroupActivity, Codable {
    var metadata: GroupActivityMetadata {
        var metadata = GroupActivityMetadata()
        metadata.title = "Watch Party"
        metadata.description = "Watch video together"
        metadata.type = .watchTogether
        return metadata
    }

    let videoURL: URL
}

class WatchPartyViewController: AVPlayerViewController {
    var groupSession: GroupSession<WatchPartyActivity>?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Setup player
        let playerItem = AVPlayerItem(url: URL(fileURLWithPath: "video.mp4"))
        player = AVPlayer(playerItem: playerItem)

        // Listen for group sessions
        Task {
            for await session in WatchPartyActivity.sessions() {
                groupSession = session

                // Sync playback with session
                try? await configureGroupPlayback(for: session)

                // Monitor participant status
                Task {
                    for await state in session.states(of: GroupStateObserver.self) {
                        if state.isActive {
                            print("Session active with \(state.localParticipant.displayName)")
                        }
                    }
                }
            }
        }
    }

    func configureGroupPlayback(for session: GroupSession<WatchPartyActivity>) async throws {
        // Use GroupPlaybackCoordinator to sync playback
        let coordinator = try await GroupPlaybackCoordinator(session: session)

        // Player will sync across participants
        // When initiator plays, others play
        // When initiator seeks, others seek
    }
}
```

---

## Common Mistakes

**Mistake 1: Not activating activity before using group session**
```swift
// ❌ WRONG: Activity never activated, no session available
for await session in QuizActivity.sessions() {
    // This never fires because activity not activated
}

// ✅ CORRECT: Activate activity first
let activity = QuizActivity(quizID: UUID(), topic: "Science")
try await activity.activate()

for await session in QuizActivity.sessions() {
    // Now this fires
}
```

**Mistake 2: Not checking for `nil` session before using**
```swift
// ❌ WRONG: Crash if session deallocated
groupSession?.send(message)

// ✅ CORRECT: Validate session is still active
guard let session = groupSession else {
    print("Session ended")
    return
}
try? await session.send(message)
```

**Mistake 3: Not handling GroupActivity decoding errors**
```swift
// ❌ WRONG: No error handling for malformed activity
struct QuizActivity: GroupActivity, Codable {}  // No metadata defined

// ✅ CORRECT: Ensure Codable conformance and metadata
struct QuizActivity: GroupActivity, Codable {
    var metadata: GroupActivityMetadata {
        var meta = GroupActivityMetadata()
        meta.title = "Quiz"
        return meta
    }

    let quizID: UUID
    // All properties must be Codable
}
```

**Mistake 4: Sending non-Codable messages**
```swift
// ❌ WRONG: Message doesn't conform to Codable
let message = UIImage()  // Not Codable
try? await groupSession?.send(message)

// ✅ CORRECT: Wrap in Codable struct
struct ImageMessage: Codable {
    let imageData: Data  // UIImage -> Data
    let timestamp: Date
}
```

**Mistake 5: Not canceling observer tasks when session ends**
```swift
// ❌ WRONG: Task continues observing after session ends (memory leak)
@State var messagesTask: Task<Void, Never>?

func handleSession(_ session: GroupSession<Activity>) {
    messagesTask = Task {
        for await message in session.messages(of: String.self) {
            // Observer never stops
        }
    }
}

// ✅ CORRECT: Cancel task when session ends
.onChange(of: groupSession) { _, newSession in
    if newSession == nil {
        messagesTask?.cancel()  // Cleanup
    }
}
```

---

## Review Checklist

- [ ] `GroupActivity` protocol adopted with `metadata` property implemented
- [ ] Activity is `Codable` with all properties serializable
- [ ] `activity.activate()` called before using sessions
- [ ] `GroupSession.sessions()` async sequence properly iterated
- [ ] Optional `groupSession` property validated before use
- [ ] Message types conform to `Codable` (no UIImage, UIView, etc.)
- [ ] Observer tasks canceled in `deinit` or `onChange` when session ends
- [ ] `GroupStateObserver` monitored for participant join/leave events
- [ ] Participant display names shown in UI (from `participant.displayName`)
- [ ] For AVPlayer: `GroupPlaybackCoordinator` configured (not manual sync)
- [ ] Error messages from `activate()` handled gracefully
- [ ] Session messages sent with `try? await session.send(message)`
- [ ] SharePlay entitlement enabled in Xcode capabilities

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

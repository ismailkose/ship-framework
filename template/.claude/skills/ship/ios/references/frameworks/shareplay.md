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
| `GroupSessionMessenger` | Message transport with delivery modes (reliable vs. unreliable) |
| `GroupSessionJournal` | File/data transfer system for large payloads |
| `GroupActivityMetadata` | Activity metadata with type enumeration |
| `Shareable` | Protocol for objects that can sync state across session |
| `SharedImmutableReference` | Reference to immutable data synced in group |
| `SharedMutableReference` | Mutable state binding (SwiftUI) synced across group |
| `AVPlayer` | Extended to support synchronized playback in group sessions |
| `AVPlaybackCoordinator` | Coordinates media playback across participants |
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

**Example 3: Synchronized AVPlayer playback with AVPlaybackCoordinator**
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

                // Sync playback with session using AVPlaybackCoordinator
                configureGroupPlayback(for: session)

                // Monitor participant status
                Task {
                    for await participants in session.$activeParticipants.values {
                        print("Active participants: \(participants.count)")
                    }
                }
            }
        }
    }

    func configureGroupPlayback(for session: GroupSession<WatchPartyActivity>) {
        // Connect player's coordinator to the session
        let coordinator = player.playbackCoordinator
        coordinator.coordinateWithSession(session)

        // Player will automatically sync across participants
        // When initiator plays, others play
        // When initiator seeks, others seek
    }
}
```

**Example 3b: GroupSessionMessenger with delivery modes**
```swift
// Reliable (default) -- guaranteed delivery, ordered
let reliableMessenger = GroupSessionMessenger(
    session: session,
    deliveryMode: .reliable
)

// Unreliable -- faster, no guarantees (good for frequent position updates)
let unreliableMessenger = GroupSessionMessenger(
    session: session,
    deliveryMode: .unreliable
)

// Use .reliable for state-changing actions (play/pause, selections)
// Use .unreliable for high-frequency ephemeral data (cursor positions, drawing strokes)
```

**Example 3c: GroupSessionJournal for file transfer**
```swift
let journal = GroupSessionJournal(session: session)

// Upload a file
let attachment = try await journal.add(imageData)

// Observe incoming attachments
Task {
    for await attachments in journal.attachments {
        for attachment in attachments {
            let data = try await attachment.load(Data.self)
            handleReceivedFile(data)
        }
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

**Mistake 6: Not handling late-joiner state**
```swift
// ❌ WRONG: Broadcasting state without handling late joiners
func onJoin() {
    // New participant has no idea what the current state is
}

// ✅ CORRECT: Send full state to new participants
func handleParticipants(_ participants: Set<Participant>) {
    let newParticipants = participants.subtracting(knownParticipants)
    for participant in newParticipants {
        Task {
            try await messenger?.send(currentState, to: .only(participant))
        }
    }
    knownParticipants = participants
}
```

**Mistake 7: Using GroupSessionMessenger for large data**
```swift
// ❌ WRONG: Messenger has a per-message size limit
let largeImage = try Data(contentsOf: imageURL)  // 5 MB
try await messenger.send(largeImage, to: .all)    // May fail

// ✅ CORRECT: Use GroupSessionJournal for files
let journal = GroupSessionJournal(session: session)
try await journal.add(largeImage)
```

---

## Review Checklist

- [ ] `GroupActivity` protocol adopted with `metadata` property implemented
- [ ] `GroupActivityMetadata.type` set correctly (watchTogether, listenTogether, createTogether, etc.)
- [ ] Activity is `Codable` with all properties serializable
- [ ] `activity.activate()` called before using sessions
- [ ] `GroupSession.sessions()` async sequence properly iterated
- [ ] Optional `groupSession` property validated before use
- [ ] Message types conform to `Codable` (no UIImage, UIView, etc.)
- [ ] `GroupSessionMessenger` created with appropriate `deliveryMode` (.reliable vs .unreliable)
- [ ] Late-joining participants receive current state on connection
- [ ] Observer tasks canceled in `deinit` or `onChange` when session ends
- [ ] `GroupStateObserver` monitored for participant join/leave events
- [ ] Participant display names shown in UI (from `participant.displayName`)
- [ ] For AVPlayer: `AVPlaybackCoordinator` configured (not manual sync)
- [ ] `GroupSessionJournal` used for large file transfers instead of messenger
- [ ] Error messages from `activate()` handled gracefully
- [ ] Session messages sent with `try? await session.send(message)`
- [ ] SharePlay entitlement enabled in Xcode capabilities

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

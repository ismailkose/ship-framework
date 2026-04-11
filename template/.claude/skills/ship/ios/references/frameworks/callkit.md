# CallKit — iOS Reference

> **When to read:** Dev reads this when building VoIP calling, integrating with system call UI, reporting incoming/outgoing calls, or handling call events.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `CXProvider` | Manages system call UI and call state; delegates to app |
| `CXProviderConfiguration` | Configuration for provider: name, icon, supported call types |
| `CXCallController` | Initiates calls and call actions (answer, hang up, mute, etc.) |
| `CXCallObserver` | Monitors current calls in system (incoming, outgoing) |
| `CXCall` | Call state object (UUID, isOutgoing, isOnHold, hasEnded) |
| `CXAction` | Base class for call actions (start/end call, answer, hold, etc.) |
| `CXStartCallAction` | Initiate outgoing call |
| `CXAnswerCallAction` | Answer incoming call |
| `CXEndCallAction` | End call |
| `CXSetMutedCallAction` | Mute/unmute audio |
| `CXSetHeldCallAction` | Hold/resume call |
| `CXTransaction` | Groups multiple call actions |
| `CXProviderDelegate` | Responds to call events and actions |
| `CXCallUpdate` | Describes call metadata (caller name, video, handle) |
| `CXHandle` | Call endpoint (phone number, email, generic) |
| `CXCallDirectoryProvider` | Extension for caller ID and call blocking |
| `CXCallDirectoryPhoneNumber` | E.164 formatted phone number (Int64) |
| `PKPushRegistry` | Registers for and receives VoIP push notifications |
| `PKPushRegistryDelegate` | Handles VoIP push token updates and push receipt |

---

## Code Examples

**Example 1: Setup CallKit provider and report incoming call**
```swift
import CallKit

/// CXProvider dispatches all delegate calls to the queue passed to `setDelegate(_:queue:)`.
/// The `let` properties are initialized once and never mutated, making this type
/// safe to share across concurrency domains despite @unchecked Sendable.
final class CallManager: NSObject, @unchecked Sendable {
    static let shared = CallManager()

    let provider: CXProvider
    let callController = CXCallController()

    private override init() {
        let config = CXProviderConfiguration()
        config.localizedName = "My VoIP App"
        config.supportsVideo = true
        config.maximumCallsPerCallGroup = 1
        config.maximumCallGroups = 2
        config.supportedHandleTypes = [.phoneNumber, .emailAddress]
        config.includesCallsInRecents = true

        provider = CXProvider(configuration: config)
        super.init()
        provider.setDelegate(self, queue: nil)
    }
}
```

**Example 1b: Report incoming call with async/await**
```swift
func reportIncomingCall(
    uuid: UUID,
    handle: String,
    hasVideo: Bool
) async throws {
    let update = CXCallUpdate()
    update.remoteHandle = CXHandle(type: .phoneNumber, value: handle)
    update.hasVideo = hasVideo
    update.localizedCallerName = "Jane Doe"

    try await withCheckedThrowingContinuation {
        (continuation: CheckedContinuation<Void, Error>) in
        provider.reportNewIncomingCall(
            with: uuid,
            update: update
        ) { error in
            if let error {
                continuation.resume(throwing: error)
            } else {
                continuation.resume()
            }
        }
    }
}
```

**Legacy Example 1c: UIKit-based call reporting**
```swift
class VoIPCallManager: NSObject, CXProviderDelegate {
    let provider: CXProvider
    let callController = CXCallController()
    var calls: [UUID: Call] = [:]

    override init() {
        let config = CXProviderConfiguration(localizedName: "My VoIP App")
        config.supportsVideo = true
        config.maximumCallsPerCallGroup = 1
        config.supportedHandleTypes = [.phoneNumber, .generic]

        provider = CXProvider(configuration: config)
        super.init()
        provider.setDelegate(self, queue: .main)
    }

    // Report incoming call to system
    func reportIncomingCall(uuid: UUID, from phoneNumber: String) {
        let handle = CXHandle(type: .phoneNumber, value: phoneNumber)
        let update = CXCallUpdate()
        update.remoteHandle = handle
        update.hasVideo = false
        update.supportsHolding = true

        provider.reportNewIncomingCall(with: uuid, update: update) { error in
            if let error = error {
                print("Incoming call report failed: \(error)")
            } else {
                self.calls[uuid] = Call(uuid: uuid, phoneNumber: phoneNumber)
            }
        }
    }

    // MARK: - CXProviderDelegate

    func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
        // User answered the call
        if let call = calls[action.callUUID] {
            print("Answered call: \(call.phoneNumber)")
            // Start audio/video
        }
        action.fulfill()
    }

    func provider(_ provider: CXProvider, perform action: CXEndCallAction) {
        // User ended the call
        if let call = calls[action.callUUID] {
            print("Ended call: \(call.phoneNumber)")
            calls.removeValue(forKey: action.callUUID)
        }
        action.fulfill()
    }

    func provider(_ provider: CXProvider, perform action: CXSetMutedCallAction) {
        // User muted/unmuted
        print("Mute: \(action.isMuted)")
        action.fulfill()
    }

    func providerDidReset(_ provider: CXProvider) {
        // Provider reset; stop all calls
        calls.removeAll()
    }
}

struct Call {
    let uuid: UUID
    let phoneNumber: String
}
```

**Example 2: Outgoing call with state reporting**
```swift
import CallKit

func startOutgoingCall(handle: String, hasVideo: Bool) {
    let uuid = UUID()
    let handle = CXHandle(type: .phoneNumber, value: handle)
    let startAction = CXStartCallAction(call: uuid, handle: handle)
    startAction.isVideo = hasVideo

    let transaction = CXTransaction(action: startAction)
    callController.request(transaction) { error in
        if let error {
            print("Failed to start call: \(error)")
        }
    }
}

extension CallManager: CXProviderDelegate {
    func provider(_ provider: CXProvider, perform action: CXStartCallAction) {
        configureAudioSession()
        // Begin connecting to server
        provider.reportOutgoingCall(
            with: action.callUUID,
            startedConnectingAt: Date()
        )

        connectToServer(callUUID: action.callUUID) {
            provider.reportOutgoingCall(
                with: action.callUUID,
                connectedAt: Date()
            )
        }
        action.fulfill()
    }
}
```

**Legacy Example 2b: Callback-based outgoing call**
```swift
func startOutgoingCall(to phoneNumber: String) {
    let uuid = UUID()
    let handle = CXHandle(type: .phoneNumber, value: phoneNumber)
    let startCallAction = CXStartCallAction(call: uuid, handle: handle)

    let transaction = CXTransaction(action: startCallAction)

    callController.request(transaction) { error in
        if let error = error {
            print("Start call failed: \(error)")
        } else {
            print("Start call action requested")
            // System will call provider(_:perform:CXStartCallAction)
        }
    }
}

func provider(_ provider: CXProvider, perform action: CXStartCallAction) {
    // Actually start the call (connect VoIP, etc.)
    print("Starting outgoing call to \(action.handle.value)")
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
        action.fulfill()  // Complete action
    }
}
```

**Example 3: Call Directory with E.164 formatting**
```swift
import CallKit

final class CallDirectoryHandler: CXCallDirectoryProvider {
    override func beginRequest(
        with context: CXCallDirectoryExtensionContext
    ) {
        if context.isIncremental {
            addOrRemoveIncrementalEntries(to: context)
        } else {
            addAllEntries(to: context)
        }
        context.completeRequest()
    }

    private func addAllEntries(
        to context: CXCallDirectoryExtensionContext
    ) {
        // Phone numbers must be in ascending order (E.164 format as Int64)
        let blockedNumbers: [CXCallDirectoryPhoneNumber] = [
            18005551234, 18005555678
        ]
        for number in blockedNumbers {
            context.addBlockingEntry(
                withNextSequentialPhoneNumber: number
            )
        }

        let identifiedNumbers: [(CXCallDirectoryPhoneNumber, String)] = [
            (18005551111, "Local Pizza"),
            (18005552222, "Dentist Office")
        ]
        for (number, label) in identifiedNumbers {
            context.addIdentificationEntry(
                withNextSequentialPhoneNumber: number,
                label: label
            )
        }
    }
}
```

**Example 4: Monitor active calls and handle VoIP push notifications**
```swift
import CallKit
import PushKit

class CallMonitor: NSObject, CXCallObserverDelegate {
    let callObserver = CXCallObserver()

    override init() {
        super.init()
        callObserver.setDelegate(self, queue: .main)

        // Also request VoIP push notifications
        let pushRegistry = PKPushRegistry(queue: .main)
        pushRegistry.desiredPushTypes = [.voIP]
        pushRegistry.delegate = self
    }

    func callObserver(_ callObserver: CXCallObserver, callChanged call: CXCall) {
        if call.hasEnded {
            print("Call ended")
        } else if call.isOutgoing && !call.hasConnected {
            print("Outgoing call connecting...")
        } else if call.hasConnected {
            print("Call connected; audio/video should start")
        }
    }
}

// MARK: - PKPushRegistryDelegate (for VoIP push)
extension CallMonitor: PKPushRegistryDelegate {
    func pushRegistry(
        _ registry: PKPushRegistry,
        didUpdate pushCredentials: PKPushCredentials,
        for type: PKPushType
    ) {
        let token = pushCredentials.token.map { String(format: "%02x", $0) }.joined()
        print("VoIP push token: \(token)")
        // Send token to server
    }

    func pushRegistry(
        _ registry: PKPushRegistry,
        didReceiveIncomingPushWith payload: PKPushPayload,
        for type: PKPushType
    ) {
        // VoIP push received; app wakes up in background
        let uuid = UUID()
        let phoneNumber = payload.dictionaryPayload["caller"] as? String ?? "Unknown"
        callManager.reportIncomingCall(uuid: uuid, from: phoneNumber)
    }
}
```

---

## Common Mistakes

**Mistake 1: Not setting CXProvider delegate**
```swift
// ❌ WRONG: Provider created but delegate not set
let provider = CXProvider(configuration: config)

// ✅ CORRECT: Set delegate on main queue
provider.setDelegate(self, queue: .main)
```

**Mistake 2: VoIP push not reported before completion handler returns**
```swift
// ❌ WRONG: No call reported on VoIP push receipt
func pushRegistry(
    _ registry: PKPushRegistry,
    didReceiveIncomingPushWith payload: PKPushPayload,
    for type: PKPushType,
    completion: @escaping () -> Void
) {
    // Just process data, no call reported
    processPayload(payload)
    completion()
}

// ✅ CORRECT: Always report a call before completion
func pushRegistry(
    _ registry: PKPushRegistry,
    didReceiveIncomingPushWith payload: PKPushPayload,
    for type: PKPushType,
    completion: @escaping () -> Void
) {
    let uuid = UUID()
    provider.reportNewIncomingCall(
        with: uuid, update: makeUpdate(from: payload)
    ) { _ in completion() }
}
```

**Mistake 2b: Reporting incoming call without handling delegate action**
```swift
// ❌ WRONG: Report call but provider(_ perform:) not implemented
reportIncomingCall(uuid: uuid, from: phoneNumber)
// User taps "Answer" but nothing happens

// ✅ CORRECT: Implement CXProviderDelegate method
func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
    configureAudioSession()
    connectToCallServer(callUUID: action.callUUID)
    action.fulfill()  // Must call to complete
}
```

**Mistake 3: Forgetting to fulfill actions**
```swift
// ❌ WRONG: Action never marked complete; UI hangs
func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
    print("Answering call...")
    // Missing action.fulfill()
}

// ✅ CORRECT: Always call fulfill() or fail()
func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
    if connectCall() {
        action.fulfill()
    } else {
        action.fail()
    }
}
```

**Mistake 4: Not requesting CallKit capability in Info.plist**
```swift
// ❌ WRONG: Missing entitlements
provider.reportNewIncomingCall(with: uuid, update: update)

// ✅ CORRECT: Add to Info.plist
// <key>NSVoIPAppsRequireLocalNetwork</key>
// <true/>
// And enable in Xcode: Signing & Capabilities > CallKit
```

**Mistake 5: Creating multiple CXProvider instances**
```swift
// ❌ WRONG: Each call creates new provider; conflicts
func reportIncomingCall() {
    let provider = CXProvider(configuration: config)  // New instance each time
    provider.reportNewIncomingCall(...)
}

// ✅ CORRECT: Singleton or persistent property
class VoIPManager {
    let provider: CXProvider  // Single instance
}
```

---

## Review Checklist

- [ ] `CXProvider` marked with `@unchecked Sendable` since it dispatches to dedicated queue
- [ ] `CXProvider` initialized with `CXProviderConfiguration`
- [ ] Provider delegate set via `setDelegate(_:queue:)` (usually nil for main queue dispatch)
- [ ] `CXProviderConfiguration.localizedName` set to app name
- [ ] `CXProviderConfiguration.supportsVideo` set correctly for app capability
- [ ] `maximumCallsPerCallGroup` and `maximumCallGroups` set appropriately
- [ ] Incoming call reported via `reportNewIncomingCall(with:update:)` with async/await or completion
- [ ] `reportIncomingCall()` uses `withCheckedThrowingContinuation` for async/await pattern
- [ ] All `CXProviderDelegate` methods implemented (answer, end, mute, hold, reset)
- [ ] Every delegate action calls either `fulfill()` or `fail()`
- [ ] Outgoing call state reported via `reportOutgoingCall(with:startedConnectingAt:)` then `connectedAt:`
- [ ] CallKit entitlement added in Xcode capabilities
- [ ] VoIP background mode enabled in Signing & Capabilities
- [ ] VoIP push notifications registered via `PKPushRegistry` at every app launch
- [ ] VoIP push token sent to server on every `didUpdate pushCredentials` callback
- [ ] VoIP push always results in `reportNewIncomingCall` before completion handler returns
- [ ] Outgoing calls initiated via `CXStartCallAction` in `CXCallController`
- [ ] AVAudioSession configured for VoIP (category: `.playAndRecord`, mode: `.voiceChat`)
- [ ] Call Directory phone numbers in ascending E.164 order (Int64 format)
- [ ] Call Directory loader handles both incremental and full refresh contexts

## Enriched Common Mistakes

- ❌ Not calling action.fulfill() or action.fail() — UI hangs, user perceives frozen app
- ❌ Reporting incoming call without implementing CXProviderDelegate — call never connects
- ❌ Not calling reportNewIncomingCall before VoIP push completion handler returns — call dismissed
- ❌ Creating multiple CXProvider instances — causes conflicts and crashes
- ❌ Missing CallKit entitlement or VoIP background mode — system won't wake app

## Enriched Review Checklist

- [ ] Every CXProviderDelegate action fulfills or fails immediately
- [ ] CXProviderDelegate methods fully implemented
- [ ] VoIP push completion called after reportNewIncomingCall
- [ ] Single CXProvider singleton instance
- [ ] CallKit capability and VoIP background mode enabled
- [ ] AVAudioSession properly configured for VoIP
- [ ] Phone numbers in E.164 format for Call Directory

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

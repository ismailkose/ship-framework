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

---

## Code Examples

**Example 1: Setup CallKit provider and report incoming call**
```swift
import CallKit

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

**Example 2: Initiate outgoing call**
```swift
import CallKit

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

**Example 3: Monitor active calls and handle push notifications**
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
        let token = pushCredentials.token.map { String(format: "%02.2hhx", $0) }.joined()
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

**Mistake 2: Reporting incoming call without handling delegate action**
```swift
// ❌ WRONG: Report call but provider(_ perform:) not implemented
reportIncomingCall(uuid: uuid, from: phoneNumber)
// User taps "Answer" but nothing happens

// ✅ CORRECT: Implement CXProviderDelegate method
func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
    startAudioSession()
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

- [ ] `CXProvider` initialized with `CXProviderConfiguration`
- [ ] Provider delegate set via `setDelegate(_:queue:)` on main queue
- [ ] `CXProviderConfiguration.localizedName` set to app name
- [ ] `CXProviderConfiguration.supportsVideo` set correctly for app capability
- [ ] `maximumCallsPerCallGroup` set (typically 1 for VoIP apps)
- [ ] Incoming call reported via `reportNewIncomingCall(with:update:)`
- [ ] All `CXProviderDelegate` methods implemented (answer, end, mute, hold, reset)
- [ ] Every delegate action calls either `fulfill()` or `fail()`
- [ ] CallKit entitlement added in Xcode capabilities
- [ ] VoIP push notifications registered via `PKPushRegistry` and `PKPushRegistryDelegate`
- [ ] VoIP push token sent to server for remote push delivery
- [ ] Outgoing calls initiated via `CXStartCallAction` in `CXCallController`
- [ ] AVAudioSession configured for VoIP (category: `.voiceChat`, options: `.duckOthers`)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

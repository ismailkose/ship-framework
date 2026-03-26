# Core NFC — iOS Reference

> **When to read:** Dev reads this when building NFC tag reading/writing, NDEF message handling, or background tag detection features.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `NFCNDEFReaderSession` | Read NDEF messages from NFC Forum Type 2/3/4/5 tags |
| `NFCTagReaderSession` | Low-level raw tag reading (ISO7816, ISO15693, Felica, NFCA/B) |
| `NFCNDEFMessage` | Container for NDEF records |
| `NFCNDEFPayload` | Single NDEF record (text, URL, custom) |
| `NFCNDEFReaderSessionDelegate` | Delegate for tag detection callbacks |
| `NFCTagReaderSessionDelegate` | Delegate for raw tag operations |
| `HCESessionManager` | Host Card Emulation (HCE) — iOS 13.6+ for Apple Pay only |

**Key Enum Values:**
- `NFCTypeNameFormat` — TNF type: empty, NFC well-known (U, T, SP), media type, absolute URI, external
- `NFCNDEFRecordTypeNameFormat` — Record type interpretation (URI, text, smart poster, etc.)

---

## Code Examples

**Example 1: Read NDEF messages from NFC tag**
```swift
import CoreNFC

class NFCReaderViewController: UIViewController, NFCNDEFReaderSessionDelegate {
    var nfcSession: NFCNDEFReaderSession?

    func beginNFCReading() {
        nfcSession = NFCNDEFReaderSession(
            delegate: self,
            queue: .main,
            invalidateAfterFirstRead: false
        )
        nfcSession?.alertMessage = "Hold your NFC tag near your device"
        nfcSession?.begin()
    }

    // Delegate: tag(s) detected
    func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetectNDEFs messages: [NFCNDEFMessage]
    ) {
        DispatchQueue.main.async {
            self.processNDEFMessages(messages)
        }
    }

    func processNDEFMessages(_ messages: [NFCNDEFMessage]) {
        for message in messages {
            for record in message.records {
                if record.typeNameFormat == .nfcWellKnownType {
                    let payloadString = String(data: record.payload, encoding: .utf8) ?? ""
                    print("Payload: \(payloadString)")
                }
            }
        }
    }

    func readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        print("NFC session ended: \(error.localizedDescription)")
    }

    func readerSessionDidBecomeActive(_ session: NFCNDEFReaderSession) {
        print("Ready to scan")
    }
}
```

**Example 1b: Tag connection with queryNDEFStatus**
```swift
session.connect(to: tag) { error in
    if let error {
        session.invalidate(errorMessage: "Connection failed: \(error)")
        return
    }

    tag.queryNDEFStatus { status, capacity, error in
        guard error == nil else {
            session.invalidate(errorMessage: "Query failed.")
            return
        }

        switch status {
        case .notSupported:
            session.invalidate(errorMessage: "Tag is not NDEF compliant.")
        case .readOnly:
            tag.readNDEF { message, error in
                if let message {
                    self.processMessage(message)
                }
                session.invalidate()
            }
        case .readWrite:
            // Can read or write
            tag.readNDEF { message, error in
                if let message {
                    self.processMessage(message)
                }
                session.invalidate()
            }
        @unknown default:
            session.invalidate()
        }
    }
}
```

**Example 2: Tag type switch pattern with NFCTagReaderSession**
```swift
func readerSession(
    _ session: NFCTagReaderSession,
    didDetect tags: [NFCTag]
) {
    guard let tag = tags.first else { return }

    session.connect(to: tag) { error in
        guard error == nil else {
            session.invalidate(errorMessage: "Connection failed.")
            return
        }

        switch tag {
        case .iso7816(let iso7816Tag):
            self.readISO7816(tag: iso7816Tag, session: session)
        case .miFare(let miFareTag):
            self.readMiFare(tag: miFareTag, session: session)
        case .iso15693(let iso15693Tag):
            self.readISO15693(tag: iso15693Tag, session: session)
        case .feliCa(let feliCaTag):
            self.readFeliCa(tag: feliCaTag, session: session)
        @unknown default:
            session.invalidate(errorMessage: "Unsupported tag type.")
        }
    }
}
```

**Example 3: Session invalidation error filtering**
```swift
func readerSession(
    _ session: NFCNDEFReaderSession,
    didInvalidateWithError error: Error
) {
    let nfcError = error as? NFCReaderError
    switch nfcError?.code {
    case .readerSessionInvalidationErrorUserCanceled,
         .readerSessionInvalidationErrorFirstNDEFTagRead,
         .readerSessionInvalidationErrorSessionTimeout:
        break  // Normal termination or timeout
    default:
        showAlert("NFC Error: \(error.localizedDescription)")
    }
    self.session = nil
}
```

**Example 4: Write NDEF message to tag (NFCTagReaderSession)**
```swift
import CoreNFC

func writeNDEFToTag() {
    let tagSession = NFCTagReaderSession(
        pollingOption: [.iso14443],
        delegate: self
    )
    tagSession?.alertMessage = "Hold NFC tag to write data"
    tagSession?.begin()
}

func readerSession(
    _ session: NFCTagReaderSession,
    didDetect tags: [NFCTag]
) {
    guard let tag = tags.first else { return }

    session.connect(to: tag) { error in
        if error != nil { return }

        guard case .ndef(let ndefTag) = tag else { return }

        // Create NDEF message
        let textRecord = NFCNDEFPayload(
            format: .nfcWellKnownType,
            type: "T".data(using: .utf8)!,
            identifier: Data(),
            payload: "Hello NFC".data(using: .utf8)!
        )
        let message = NFCNDEFMessage(records: [textRecord])

        // Write to tag
        ndefTag.writeNDEF(message) { error in
            if let error = error {
                print("Write failed: \(error)")
            } else {
                print("Write succeeded")
            }
            session.invalidate()
        }
    }
}
```

**Example 3: Background tag reading (iOS 13+)**
```swift
import CoreNFC

// In AppDelegate or SceneDelegate
func scene(
    _ scene: UIScene,
    continue userActivity: NSUserActivity
) {
    if userActivity.activityType == NFCNDEFReaderSession.ndefReaderSessionDidCloseNotification {
        // Tag scanned in background; process it
        if let ndefMessage = userActivity.ndefMessagePayload {
            print("Background NDEF detected: \(ndefMessage.records)")
        }
    }
}

// In Info.plist:
// - com.apple.developer.nfc.readersession.formats: [NDEF]
// - NFCReaderUsageDescription: "We need NFC to read tags"
```

---

## Common Mistakes

**Mistake 1: Not checking NFC availability at launch**
```swift
// ❌ WRONG: Crashes on non-NFC devices
let session = NFCNDEFReaderSession(delegate: self, queue: .main, invalidateAfterFirstRead: false)

// ✅ CORRECT: Check availability first
if NFCNDEFReaderSession.readingAvailable {
    let session = NFCNDEFReaderSession(delegate: self, queue: .main, invalidateAfterFirstRead: false)
}
```

**Mistake 2: Starting NFC session on main thread but processing on background**
```swift
// ❌ WRONG: Callback happens on .main, but delegate method runs on background
func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
    // This already runs on main thread; UI updates are safe
    processMessages(messages)
}

// ✅ CORRECT: Explicitly dispatch to main if async work needed
func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
    DispatchQueue.main.async {
        self.updateUI(with: messages)
    }
}
```

**Mistake 3: Forgetting NFCReaderUsageDescription in Info.plist**
```swift
// ❌ WRONG: No description = runtime crash
let session = NFCNDEFReaderSession(...)

// ✅ CORRECT: Add to Info.plist
// <key>NFCReaderUsageDescription</key>
// <string>We scan NFC tags to unlock special content</string>
```

**Mistake 4: Not invalidating session after use**
```swift
// ❌ WRONG: Session stays open, user confused
var nfcSession: NFCNDEFReaderSession?
nfcSession?.begin()  // Session never invalidated = stuck UI

// ✅ CORRECT: Invalidate after processing
func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
    processMessages(messages)
    session.invalidate()  // Close session
}
```

**Mistake 5: Assuming NDEF record type without checking**
```swift
// ❌ WRONG: crashes if payload doesn't decode
let payload = String(data: record.payload, encoding: .utf8)!  // Force unwrap

// ✅ CORRECT: Optional binding
if let payload = String(data: record.payload, encoding: .utf8) {
    print("Payload: \(payload)")
}
```

---

## Review Checklist

- [ ] `NFCNDEFReaderSession.readingAvailable` checked before creating session
- [ ] Info.plist includes `NFCReaderUsageDescription` with user-facing description
- [ ] Entitlements file includes `com.apple.developer.nfc.readersession.formats`
- [ ] NFC session initialized with appropriate delegate and queue
- [ ] `invalidateAfterFirstRead` set correctly (true for one-time scans, false for continuous)
- [ ] Delegate methods (`didDetectNDEFs`, `didInvalidateWithError`) implemented
- [ ] UI update code runs on main thread (use `DispatchQueue.main.async`)
- [ ] Error handling in `didInvalidateWithError()` provides user feedback
- [ ] Session invalidated after processing (avoid memory leaks)
- [ ] Tag type checked before calling type-specific methods (`case .ndef`)
- [ ] NDEF payload encoding verified (UTF-8, ASCII, etc.)
- [ ] Tested on actual NFC-capable device (simulator has no NFC support)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

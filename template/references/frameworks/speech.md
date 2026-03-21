# Speech Recognition — iOS Reference

> **When to read:** Dev reads this when building features with voice input, real-time transcription, or speech-to-text.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `SFSpeechRecognizer` | Main API; handles recognition requests; language/locale aware |
| `SFSpeechAudioBufferRecognitionRequest` | Real-time streaming; feed audio buffers via `append(_:)` |
| `SFSpeechURLRecognitionRequest` | File-based recognition; pass pre-recorded audio file URL |
| `SFSpeechRecognitionResult` | Contains best transcript + alternatives |
| `SFSpeechRecognitionTaskHint` | `.unspecified`, `.dictation`, `.search`, `.confirmation` |
| `AVAudioSession` | Required; set category/mode before capturing audio |
| `AVAudioEngine` | Builds audio graph; connects microphone to recognition |
| `AVAudioFormat` | Specifies sample rate, channels, bit depth |
| `SFSpeechRecognizerAuthorizationStatus` | `.authorized`, `.denied`, `.restricted`, `.notDetermined` |

---

## Code Examples

### Example 1: Real-time transcription with microphone
```swift
import Speech
import AVFoundation

class SpeechRecognizer {
    let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    let audioEngine = AVAudioEngine()

    func startListening() throws {
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)

        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else { return }

        recognitionRequest.shouldReportPartialResults = true
        recognitionRequest.taskHint = .dictation

        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)!

        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }

        audioEngine.prepare()
        try audioEngine.start()

        let recognitionTask = recognizer.recognitionTask(
            with: recognitionRequest,
            resultHandler: { result, error in
                if let result = result {
                    print("Transcript: \(result.bestTranscription.formattedString)")
                    if result.isFinal { print("Final result") }
                }
            }
        )
    }

    func stopListening() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
    }
}
```

### Example 2: File-based recognition (pre-recorded audio)
```swift
import Speech
import AVFoundation

func recognizeFromFile(url: URL) throws {
    let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))!
    let request = SFSpeechURLRecognitionRequest(url: url)

    recognizer.recognitionTask(with: request) { result, error in
        guard let result = result else {
            print("Error: \(error?.localizedDescription ?? "unknown")")
            return
        }
        print("Transcript: \(result.bestTranscription.formattedString)")
        result.bestTranscription.segments.forEach { segment in
            print("  [\(segment.timestamp)] \(segment.substring)")
        }
    }
}
```

### Example 3: Check authorization + request if needed
```swift
import Speech

func requestSpeechAuthorization(completion: @escaping (Bool) -> Void) {
    SFSpeechRecognizer.requestAuthorization { status in
        DispatchQueue.main.async {
            switch status {
            case .authorized:
                completion(true)
            case .denied:
                print("User denied speech recognition")
                completion(false)
            case .restricted, .notDetermined:
                completion(false)
            @unknown default:
                completion(false)
            }
        }
    }
}
```

---

## Common Mistakes

### ❌ Missing AVAudioSession setup
```swift
// Bad: Audio engine won't capture without session config
let recognizer = SFSpeechRecognizer()
recognizer.recognitionTask(with: request) { ... }
```
✅ **Fix:** Configure audio session before recognition
```swift
let audioSession = AVAudioSession.sharedInstance()
try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
try audioSession.setActive(true, options: .notifyOthersOnDeactivation)

let recognizer = SFSpeechRecognizer()
recognizer.recognitionTask(with: request) { ... }
```

### ❌ Not handling partial results properly
```swift
// Bad: Only processes final result; misses real-time feedback
let request = SFSpeechAudioBufferRecognitionRequest()
// (shouldReportPartialResults defaults to false)
```
✅ **Fix:** Enable partial results for responsive UI
```swift
let request = SFSpeechAudioBufferRecognitionRequest()
request.shouldReportPartialResults = true

recognizer.recognitionTask(with: request) { result, error in
    if let result = result {
        let transcript = result.bestTranscription.formattedString
        let isFinal = result.isFinal
        updateUI(transcript: transcript, isFinal: isFinal)
    }
}
```

### ❌ Retaining recognition task without strong reference
```swift
// Bad: Task deallocates immediately; no recognition happens
func startRecognition() {
    let request = SFSpeechAudioBufferRecognitionRequest()
    recognizer.recognitionTask(with: request) { ... } // Not stored
}
```
✅ **Fix:** Keep task alive as property
```swift
var recognitionTask: SFSpeechRecognitionTask?

func startRecognition() {
    let request = SFSpeechAudioBufferRecognitionRequest()
    recognitionTask = recognizer.recognitionTask(with: request) { ... }
}
```

### ❌ Ignoring authorization status before starting
```swift
// Bad: Crashes if authorization denied
let recognizer = SFSpeechRecognizer()!
recognizer.recognitionTask(with: request) { ... }
```
✅ **Fix:** Check status and request if needed
```swift
if SFSpeechRecognizer.authorizationStatus() != .authorized {
    SFSpeechRecognizer.requestAuthorization { _ in }
    return
}
let recognizer = SFSpeechRecognizer()!
```

### ❌ Not stopping audio engine or releasing resources
```swift
// Bad: Memory leak; audio tap never removed
let inputNode = audioEngine.inputNode
inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in ... }
```
✅ **Fix:** Clean up on dealloc or stop
```swift
func stopListening() {
    audioEngine.stop()
    audioEngine.inputNode.removeTap(onBus: 0)
    recognitionRequest?.endAudio()
}
```

---

## Review Checklist

- [ ] `AVAudioSession` configured with appropriate category/mode before recognition
- [ ] Authorization status checked; `requestAuthorization` called if `.notDetermined`
- [ ] `SpeechRecognitionTask` retained as property (not inline); stored for lifetime
- [ ] `shouldReportPartialResults = true` for real-time UI updates
- [ ] Audio engine input tap **removed** in cleanup/deinit
- [ ] `recognitionRequest.endAudio()` called when stopping
- [ ] Error handling covers authorization denial, audio capture failures
- [ ] Supported languages checked (not all locales available on all devices)
- [ ] `taskHint` set appropriately (dictation, search, etc.)
- [ ] Alternatives considered: check `result.bestTranscription.segments` for timestamps
- [ ] Tests mock SFSpeechRecognizer for offline testing
- [ ] Privacy: Speech Recognition usage description in Info.plist

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

# Speech Recognition — iOS Reference

> **When to read:** Dev reads this when building features with voice input, real-time transcription, speech-to-text, or adopting the modern SpeechAnalyzer API (iOS 26+).

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose | Availability |
|------|---------|---------------|
| `SFSpeechRecognizer` | Main API; handles recognition requests; language/locale aware | iOS 10+ |
| `SFSpeechAudioBufferRecognitionRequest` | Real-time streaming; feed audio buffers via `append(_:)` | iOS 10+ |
| `SFSpeechURLRecognitionRequest` | File-based recognition; pass pre-recorded audio file URL | iOS 10+ |
| `SFSpeechRecognitionResult` | Contains best transcript + alternatives | iOS 10+ |
| `SFSpeechRecognitionTaskHint` | `.unspecified`, `.dictation`, `.search`, `.confirmation` | iOS 10+ |
| `AVAudioSession` | Required; set category/mode before capturing audio | iOS 8+ |
| `AVAudioEngine` | Builds audio graph; connects microphone to recognition | iOS 8+ |
| `AVAudioFormat` | Specifies sample rate, channels, bit depth | iOS 8+ |
| `SFSpeechRecognizerAuthorizationStatus` | `.authorized`, `.denied`, `.restricted`, `.notDetermined` | iOS 10+ |
| `SpeechAnalyzer` | Modern async/await API (actor-based); iOS 26+ preferred for new code | iOS 26+ |
| `SpeechTranscriber` | Modular transcription analyzer; works with `SpeechAnalyzer` | iOS 26+ |
| `AssetInventory` | Manages on-device speech assets for `SpeechAnalyzer` | iOS 26+ |

---

## SpeechAnalyzer (iOS 26+) — Modern Async/Await API

For new iOS 26+ projects, use `SpeechAnalyzer` instead of `SFSpeechRecognizer`. It provides native async/await, actor-based concurrency, and modular analysis via `SpeechTranscriber`.

### Example 0: SpeechAnalyzer quick start

```swift
import Speech

// 1. Create transcriber with supported locale
guard let locale = SpeechTranscriber.supportedLocale(
    equivalentTo: Locale.current
) else { return }
let transcriber = SpeechTranscriber(locale: locale, preset: .offlineTranscription)

// 2. Ensure assets are installed
if let request = try await AssetInventory.assetInstallationRequest(
    supporting: [transcriber]
) {
    try await request.downloadAndInstall()
}

// 3. Create input stream and analyzer
let (inputSequence, inputBuilder) = AsyncStream.makeStream(of: AnalyzerInput.self)
let analyzer = SpeechAnalyzer(modules: [transcriber])

// 4. Feed audio buffers and get results
Task {
    for try await result in transcriber.results {
        let text = String(result.text.characters)
        print("Transcribed: \(text)")
    }
}

// 5. Run analysis
let lastSampleTime = try await analyzer.analyzeSequence(inputSequence)
if let lastSampleTime {
    try await analyzer.finalizeAndFinish(through: lastSampleTime)
}
```

### Key differences: SFSpeechRecognizer vs SpeechAnalyzer

| Feature | SFSpeechRecognizer | SpeechAnalyzer |
|---|---|---|
| Concurrency model | Callbacks/delegates | async/await + `AsyncSequence` |
| Type | `class` | `actor` |
| Architecture | Monolithic | Composable (modular) |
| Audio input | `append(_:)` on request | `AsyncStream<AnalyzerInput>` |
| Language support | String identifiers | `SpeechTranscriber.supportedLocale(equivalentTo:)` |
| On-device mode | `requiresOnDeviceRecognition` flag | Asset-based via `AssetInventory` |
| Availability | iOS 10+ | iOS 26+ |

For iOS 25 and below, continue using `SFSpeechRecognizer`.

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
- [ ] For iOS 26+: Prefer `SpeechAnalyzer` (actor-based) over `SFSpeechRecognizer` for new code
- [ ] For iOS 26+: `SpeechTranscriber.supportedLocale(equivalentTo:)` validated before creating transcriber
- [ ] For iOS 26+: `AssetInventory.assetInstallationRequest()` called and assets downloaded before analysis
- [ ] For iOS 26+: `AsyncStream<AnalyzerInput>` properly closed with `finish()` after audio feed completes

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

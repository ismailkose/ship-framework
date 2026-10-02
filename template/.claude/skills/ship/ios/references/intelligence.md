<!-- ship-reference
id: ios-intelligence
kind: mixed
sources: iPhoneOS27.0.sdk FoundationModels / CoreML / Vision / NaturalLanguage / Translation / ImagePlayground interfaces (Xcode 27.0 27A266a — examples type-check via scripts/checks/ios.sh; language detection runs on the host via scripts/checks/ios_runtime; iOS 27 FoundationModels changes read from the SDK: LanguageModelError replaces the deprecated GenerationError, PrivateCloudComputeLanguageModel, contextSize/tokenCount); https://developer.apple.com/documentation/foundationmodels ; https://developer.apple.com/documentation/coreml ; https://developer.apple.com/documentation/vision ; https://developer.apple.com/documentation/naturallanguage ; https://developer.apple.com/documentation/translation (all checked 2026-09-24); xcode-bundled-skills@27A266a AdditionalDocumentation/FoundationModels-Using-on-device-LLM-in-your-app.md (pointed to). Written for Ship from Apple's docs and the SDK; no third-party text.
reviewed: 2026-09-24
-->
# On-device intelligence — Foundation Models, Core ML, Vision, language

**When to read:** "summarize", "suggest tags", "generate", an AI assistant or chat (UI: `chat-ui-swiftui.md`),
"read the text in this photo", "scan a barcode", "detect the language", "translate", running your
own model. **Apple** = platform requirement; **Ship** = default.

## 1. Pick the tool

| Task | Use | iOS |
|---|---|---|
| Generate/summarize/extract text, structured output, simple agents | **Foundation Models** (on-device LLM) | 26 |
| Larger requests on Apple's servers with the same privacy model | `PrivateCloudComputeLanguageModel` — read Apple's 27 docs first; availability and quota apply | 27 |
| Text in images, barcodes, faces, body/hand pose, document structure | **Vision** (Swift API `RecognizeTextRequest`, `DetectBarcodesRequest`, … on 18+) | 11 / 18 |
| Language ID, tokenizing, lemmas, named entities, sentiment | **Natural Language** | 12 |
| Translate text | **Translation** (system sheet 17.4; `TranslationSession` 18) | 17.4 / 18 |
| Your own trained model (classifier, regressor, custom vision) | **Core ML** (convert with coremltools; Create ML for simple ones) | 11 |
| Let people create images in the system style | **Image Playground** sheet | 18.1 |
| Appear in visual search results | Visual Intelligence (App Intents) | 26 |

**Ship:** don't send personal data to a third-party model when an on-device API does the job.
Any server model is a product decision (privacy label, cost, consent) in `DECISIONS.md`.

## 2. Foundation Models

**Availability is part of the design (Apple):** the model exists only on Apple Intelligence
devices, with Apple Intelligence on, and after the model has downloaded. Check
`SystemLanguageModel.default.availability`; each `.unavailable(reason)` gets its own UI:
`.deviceNotEligible` → hide the feature; `.appleIntelligenceNotEnabled` → explain and link to
Settings; `.modelNotReady` → "getting ready", try later. The simulator uses the Mac's model only
on a Mac that supports Apple Intelligence.

- **Sessions:** a `LanguageModelSession` keeps a transcript (the context). One session per
  conversation or task; `instructions` set role and rules (not user data). Only one request at a
  time — check `isResponding` or disable the button.
- **Structured output:** `@Generable` types with `@Guide` constraints (`.range`, `.count`,
  `.anyOf`, descriptions) instead of parsing text. Order properties the way the model should think
  (fields it needs first).
- **Streaming:** `streamResponse(to:)` yields snapshots of the partial result — update one message
  model per snapshot (`chat-ui-swiftui.md` §4).
- **Tools:** conform to `Tool` (`name`, `description`, `@Generable` `Arguments`, `call(arguments:)`)
  when the model needs app data. `call` is `@concurrent` (runs off the main actor) — read app
  state through an actor or `await MainActor.run`, keep it fast, and make repeated calls safe.
- **Limits:** the context window is small. Measure it: `contextSize` (on-device model: iOS 26, reports
  4096 before iOS 27; the Private Cloud Compute model's is iOS 27) and `tokenCount(for:)` (iOS 26.4).
  Summarize or start a new session when it fills up.
- **Errors (iOS 27 SDK):** `LanguageModelError` — `.contextSizeExceeded`, `.guardrailViolation`,
  `.refusal`, `.unsupportedLanguageOrLocale`, `.rateLimited`, `.timeout`, … On iOS 26, catch
  `LanguageModelSession.GenerationError` (deprecated in 27; its cases differ — handle both behind
  `#available`). Every case needs a human message, not a raw error.
- `prewarm()` when you know a request is coming (the person opened the compose screen).
- **Quality isn't guaranteed:** it's a small model. Keep tasks narrow (summarize, classify,
  extract); validate generated values before saving; never present output as fact without a way
  to edit it. Test prompts with Xcode's Foundation Models Instruments template and a fixed set of
  inputs.

```swift
import FoundationModels

@available(iOS 26.0, *)
@Generable
struct TripSuggestion {
    @Guide(description: "A short, specific title")
    var title: String
    @Guide(description: "Three activities for the trip", .count(3))
    var activities: [String]
}

@available(iOS 26.0, *)
@MainActor @Observable
final class TripIdeas {
    enum State { case unavailable(String), idle, working, done(TripSuggestion), failed(String) }
    private(set) var state: State = .idle
    private let session = LanguageModelSession(instructions: "You suggest short weekend trips. Be concrete.")

    func checkAvailability() {
        switch SystemLanguageModel.default.availability {
        case .available: state = .idle
        case .unavailable(.deviceNotEligible): state = .unavailable("Not available on this device.")
        case .unavailable(.appleIntelligenceNotEnabled): state = .unavailable("Turn on Apple Intelligence in Settings to use this.")
        case .unavailable(_): state = .unavailable("Getting ready — try again in a little while.")
        }
    }

    func suggest(for city: String) async {
        guard !session.isResponding else { return }
        state = .working
        do {
            let response = try await session.respond(to: "A weekend in \(city)", generating: TripSuggestion.self)
            state = .done(response.content)
        } catch {
            state = .failed("Couldn't make a suggestion. Try a different city.")   // map error cases in real code
        }
    }
}
```

**Not shown:** streaming, tools, and the per-case error messages — build them from the list above.
Compiles; not run (needs an Apple Intelligence device).

## 3. Vision — text, barcodes, and images

- iOS 18+: the Swift API (`RecognizeTextRequest`, `DetectBarcodesRequest`, …) — `try await
  request.perform(on: cgImage)`; below 18 the `VN…Request` classes with a request handler.
- Run on a downsampled image off the main actor (`media.md` §2); pass orientation.
- Vision's normalized coordinates have a **bottom-left origin** — convert before drawing boxes
  in SwiftUI (top-left).
- Live camera scanning of text/codes: VisionKit's `DataScannerViewController` (wrapped) before a
  custom capture + Vision pipeline; check `isSupported` and `isAvailable` (device only).

```swift
import Vision

/// Lines of text Vision is reasonably sure about, top to bottom, for the person's languages.
@available(iOS 18.0, *)
nonisolated func readableLines(in image: CGImage, languages: [Locale.Language],
                               minimumConfidence: Float = 0.5) async throws -> [String] {
    var ocr = RecognizeTextRequest()
    ocr.recognitionLanguages = languages            // e.g. the app's preferred localizations
    let found = try await ocr.perform(on: image)
    return found
        .sorted { $0.boundingBox.origin.y > $1.boundingBox.origin.y }   // Vision's origin is bottom-left
        .compactMap { $0.topCandidates(1).first }
        .filter { $0.confidence >= minimumConfidence }                   // drop guesses; let the person fix the rest
        .map(\.string)
}
```

## 4. Language and translation

- `NLLanguageRecognizer` for the language of user text (set `languageHints`/`languageConstraints`
  when you know the candidates); `NLTagger` for tokens, lemmas, names, parts of speech;
  `NLEmbedding` for word/sentence similarity where available for the language.
- Short strings are ambiguous — below ~20 characters, treat the result as a guess.
- **Ship:** the system translation sheet (`.translationPresentation`, 17.4) for "translate this";
  `TranslationSession` via `.translationTask` (18) for in-app translation. Language packs may need
  a download the system prompts for; handle unsupported pairs.

```swift
import NaturalLanguage

/// Dominant language of user text, or nil when the text is too short to tell.
nonisolated func detectLanguage(_ text: String) -> NLLanguage? {
    guard text.count >= 20 else { return nil }
    let recognizer = NLLanguageRecognizer()
    recognizer.processString(text)
    return recognizer.dominantLanguage
}
```

## 5. Core ML — your own model

- Add the `.mlmodel`/`.mlpackage` to the target; Xcode generates a typed class. Load once
  (`MLModel.load(contentsOf:configuration:)` is async) and reuse — loading is expensive; never
  load per prediction or on the main actor.
- `MLModelConfiguration.computeUnits`: leave `.all` unless measured otherwise; `.cpuOnly` for
  determinism in tests.
- Large models: download after install (Background Assets or your server), compile on device
  with `MLModel.compileModel(at:)`, store the compiled model in Application Support.
- Measure with Xcode's Core ML performance report and Instruments (Core ML template) on the
  oldest supported device.

## 6. Verify

| What | How | Level |
|---|---|---|
| Unavailable states (device, setting off, not ready) | Force each state in UI tests with a fake availability provider | CI |
| Generation quality | A fixed set of 20–50 inputs with expected properties; review the outputs; rerun after model/OS updates | **Device with Apple Intelligence**; manual review |
| Guardrail / refusal / context-limit handling | Inputs that trigger them; each shows a human message | Device |
| Vision text/barcodes | Fixture images in unit tests (host or simulator); live scanning on device | CI + device |
| Language detection | Host unit tests with known strings | CI |
| Core ML accuracy and latency | Holdout set in tests; Instruments on the oldest device | CI + device |

Apple: [Foundation Models](https://developer.apple.com/documentation/foundationmodels) ·
[Vision](https://developer.apple.com/documentation/vision) ·
[Natural Language](https://developer.apple.com/documentation/naturallanguage) ·
[Translation](https://developer.apple.com/documentation/translation) ·
[Core ML](https://developer.apple.com/documentation/coreml) ·
Xcode 27: `AdditionalDocumentation/FoundationModels-Using-on-device-LLM-in-your-app.md`,
`AdditionalDocumentation/Implementing-Visual-Intelligence-in-iOS.md`.

# On-Device AI for Apple Platforms — iOS Reference

> **When to read:** Dev reads this when building tool-calling AI features, working with guided generation schemas, converting models, or running on-device inference using Foundation Models, Core ML, MLX Swift, or llama.cpp.

---

## Triage
- **Implement new feature** → Read Framework Selection Router + Core API
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `LanguageModelSession` | On-device language generation | Stateful; one request at a time; check `isResponding` |
| `@Generable` + `@Guide` | Type-safe structured output | Compile-time schema generation; supports constraints |
| `Tool` protocol | Tool-augmented generation | Model invokes autonomously; returns String result |
| `SystemLanguageModel` | Access on-device Foundation Model | Check `availability` before use |
| `GenerationOptions` | Control sampling and tokens | `temperature`, `sampling`, `maximumResponseTokens` |
| `HKHealthStore` | Core ML model deployment | `.mlpackage` format; Neural Engine optimization |
| `NLTensor` | MLX tensor operations (iOS 18+) | Multidimensional arrays; `reshaped()`, `softmax()` |
| `LLMModelFactory` | MLX Swift model loading | Load quantized LLMs from mlx-community |

## Code Examples

### 1. Foundation Models: Availability Check & Basic Generation

```swift
import FoundationModels

switch SystemLanguageModel.default.availability {
case .available:
    // Proceed with model usage
case .unavailable(.appleIntelligenceNotEnabled):
    // Guide user to enable Apple Intelligence in Settings
case .unavailable(.modelNotReady):
    // Model is downloading; show loading state
case .unavailable(.deviceNotEligible):
    // Device cannot run Apple Intelligence; use fallback
default:
    break
}

// Basic session
let session = LanguageModelSession()
do {
    let response = try await session.respond(to: "Explain quantum computing")
    print(response.content)
} catch let error as LanguageModelSession.GenerationError {
    switch error {
    case .guardrailViolation(let context):
        print("Content triggered safety filters")
    case .exceededContextWindowSize(let context):
        print("Too many tokens; summarize and retry")
    case .concurrentRequests(let context):
        print("Another request is in progress")
    default:
        break
    }
}
```

### 2. Structured Output with @Generable

```swift
@Generable
struct Recipe {
    @Guide(description: "The recipe name")
    var name: String

    @Guide(description: "Cooking steps", .count(3))
    var steps: [String]

    @Guide(description: "Prep time in minutes", .range(1...120))
    var prepTime: Int
}

let session = LanguageModelSession {
    "You are a helpful cooking assistant."
}

let response = try await session.respond(
    to: "Suggest a quick pasta recipe",
    generating: Recipe.self
)
print(response.content.name)
print(response.content.steps)
print(response.content.prepTime)
```

### 3. Tool Calling

```swift
struct WeatherTool: Tool {
    let name = "weather"
    let description = "Get current weather for a city."

    @Generable
    struct Arguments {
        @Guide(description: "The city name")
        var city: String
    }

    func call(arguments: Arguments) async throws -> String {
        let weather = try await fetchWeather(arguments.city)
        return weather.description
    }
}

let session = LanguageModelSession(
    tools: [WeatherTool()]
) {
    "You are a helpful assistant with access to weather data."
}

let response = try await session.respond(
    to: "What's the weather in San Francisco?"
)
```

### 4. Core ML: Model Loading and Prediction

```swift
import CoreML

let config = MLModelConfiguration()
config.computeUnits = .all
let model = try MLModel(contentsOf: modelURL, configuration: config)

// Async prediction (iOS 17+)
let output = try await model.prediction(from: input)
```

### 5. Core ML: PyTorch Conversion with coremltools

```python
import coremltools as ct
import torch

model.eval()  # CRITICAL: always call eval() before tracing
traced = torch.jit.trace(model, example_input)
mlmodel = ct.convert(
    traced,
    inputs=[ct.TensorType(shape=(1, 3, 224, 224), name="image")],
    minimum_deployment_target=ct.target.iOS18,
    convert_to='mlprogram',
)
mlmodel.save("Model.mlpackage")
```

### 6. MLX Swift: Loading and Running LLMs

```swift
import MLX
import MLXLLM

let config = ModelConfiguration(id: "mlx-community/Mistral-7B-Instruct-v0.3-4bit")
let model = try await LLMModelFactory.shared.loadContainer(configuration: config)

try await model.perform { context in
    let input = try await context.processor.prepare(
        input: UserInput(prompt: "Hello")
    )
    let stream = try generate(
        input: input,
        parameters: GenerateParameters(temperature: 0.0),
        context: context
    )
    for await part in stream {
        print(part.chunk ?? "", terminator: "")
    }
}
```

### 7. MLX Swift: Memory Management

```swift
// Set GPU cache limits
MLX.GPU.set(cacheLimit: 512 * 1024 * 1024)

// Unload models on background
.onChange(of: scenePhase) { _, newPhase in
    if newPhase == .background {
        try? await model.unload()
    }
}
```

### 8. Multi-Backend Architecture

```swift
func respond(to prompt: String) async throws -> String {
    if SystemLanguageModel.default.isAvailable {
        return try await foundationModelsRespond(prompt)
    } else if canLoadMLXModel() {
        return try await mlxRespond(prompt)
    } else {
        throw AIError.noBackendAvailable
    }
}

// Serialize all model access through a coordinator actor
actor ModelCoordinator {
    func withExclusiveAccess<T>(_ work: () async throws -> T) async rethrows -> T {
        try await work()
    }
}
```

### 9. Generation Options & Sampling

```swift
let options = GenerationOptions(
    sampling: .random(top: 40),
    temperature: 0.7,
    maximumResponseTokens: 512
)
let response = try await session.respond(to: prompt, options: options)

// Sampling modes: .greedy, .random(top:seed:), .random(probabilityThreshold:seed:)
```

### 10. Streaming Structured Output

```swift
let stream = session.streamResponse(
    to: "Suggest a recipe",
    generating: Recipe.self
)
for try await snapshot in stream {
    // snapshot.content is Recipe.PartiallyGenerated (all properties optional)
    if let name = snapshot.content.name { updateNameLabel(name) }
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| No availability check before calling `LanguageModelSession()` | Always check `SystemLanguageModel.default.availability` first |
| Concurrent requests on one session | Check `session.isResponding` or serialize access |
| Context window exceeded silently | Monitor with `tokenCount(for:)` and summarize when needed |
| Untrusted user content in instructions | Keep user content in prompt; instructions are privileged |
| Forgetting `model.eval()` before PyTorch tracing | Always call `eval()` — training-mode artifacts corrupt output |
| Using `neuralnetwork` format for Core ML | Always use `mlprogram` (.mlpackage) for iOS 15+ |
| Exceeding 60% RAM on iOS with MLX | Large models cause OOM kills; check device RAM constraints |
| Running MLX in simulator | MLX requires Metal GPU — use physical devices only |
| Not unloading models on app backgrounding | Unload in `scenePhase == .background` |
| Testing tools enabled in production | Gate test utilities behind `#if DEBUG` |

## Review Checklist

- [ ] Foundation Models: availability checked before every API call
- [ ] Foundation Models: graceful fallback when model unavailable
- [ ] Foundation Models: session prewarm called before user interaction
- [ ] Foundation Models: @Generable properties in logical generation order
- [ ] Foundation Models: token budget accounted for (check `contextSize`)
- [ ] Core ML: model format is mlprogram (.mlpackage) for iOS 15+
- [ ] Core ML: model.eval() called before tracing/exporting PyTorch models
- [ ] Core ML: minimum_deployment_target set explicitly
- [ ] Core ML: model accuracy validated after compression
- [ ] MLX Swift: model size appropriate for target device RAM
- [ ] MLX Swift: GPU cache limits set, models unloaded on backgrounding
- [ ] All model access serialized through coordinator actor
- [ ] Concurrency: model types and tool implementations are `Sendable`-conformant or `@MainActor`-isolated
- [ ] Physical device testing performed (not simulator)
- [ ] No untrusted content in instructions parameter

---

_Source: swift-ios-skills · Adapted for Ship Framework agent reference_

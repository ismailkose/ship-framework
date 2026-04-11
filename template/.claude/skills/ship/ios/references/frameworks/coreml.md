# CoreML — iOS Reference

> **When to read:** Dev reads this when building features that use on-device ML models, Apple Intelligence integration, or predictive features.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `MLModel` | Compiled ML model; load via `MLModel(contentsOf:)` |
| `MLFeatureProvider` | Input/output container for predictions |
| `MLModelConfiguration` | Runtime config: compute units, neuralEnginePreference |
| `MLComputeUnits` | `.all` \| `.cpuOnly` \| `.cpuAndNeuralEngine` \| `.cpuAndGPU` \| `.cpuAndNeuralEngine` |
| `MLDictionaryFeatureProvider` | Simple dict-based input provider |
| `MLArrayBatchProvider` | Batch predictions from array of inputs |
| `MLTensor` | Swift-native multidimensional array (iOS 18+); zero-copy with `.shapedArray(of:)` |
| `MLState` | Stateful prediction state for sequence/LSTM models (iOS 18+) |
| `MLComputePlan` | Inspect compute device dispatch per operation (iOS 17.4+) |
| `CoreMLRequest` | Vision API for Core ML inference (iOS 18+) |
| `VNCoreMLRequest` | Legacy Vision integration; still supported |
| `NSBundleResourceRequest` | On-demand resource loading for large models |
| `MLModel.compileModel(at:)` | Compile .mlpackage to .mlmodelc at runtime |
| `CreateML` | Xcode tool; not code—generates .mlmodel files |
| `MLPredictionOptions` | Async config: usesCPUOnly, completionHandler |

---

## Code Examples

### Example 1: Load & predict synchronously
```swift
import CoreML

let model = try MLModel(contentsOf: modelURL)
let input = MyModelInput(image: cgImage)
let output = try model.prediction(input: input)

print("Class: \(output.classLabel), Confidence: \(output.classLabelProbs)")
```

### Example 2: Async prediction with progress
```swift
import CoreML

let model = try MLModel(contentsOf: modelURL)
let config = MLModelConfiguration()
config.computeUnits = .cpuAndNeuralEngine

let asyncModel = try model.modelWithConfiguration(config)
let input = MyModelInput(...)

let options = MLPredictionOptions()
asyncModel.predictionAsync(from: input, options: options) { output, error in
    if let output = output as? MyModelOutput {
        print("Result: \(output.prediction)")
    }
}
```

### Example 3: Vision framework integration (modern CoreMLRequest, iOS 18+)
```swift
import Vision
import CoreML

let model = try MLModel(contentsOf: modelURL)
let request = CoreMLRequest(model: .init(model))
let results = try await request.perform(on: cgImage)

if let classification = results.first as? ClassificationObservation {
    print("\(classification.identifier): \(classification.confidence)")
}
```

### Example 4: Vision framework integration (legacy VNCoreMLRequest)
```swift
import Vision
import CoreML

let model = try MLModel(contentsOf: modelURL)
let visionModel = try VNCoreMLModel(for: model)
let request = VNCoreMLRequest(model: visionModel) { request, error in
    if let result = request.results as? [VNClassificationObservation] {
        result.forEach { print("\($0.identifier): \($0.confidence)") }
    }
}

let handler = VNImageRequestHandler(cgImage: image, options: [:])
try handler.perform([request])
```

### Example 5: Stateful predictions (iOS 18+, for LLMs/RNNs)
```swift
import CoreML

let state = model.makeState()

for frame in audioFrames {
    let input = try MLDictionaryFeatureProvider(dictionary: [
        "audio_features": MLFeatureValue(multiArray: frame)
    ])
    let output = try await model.prediction(from: input, using: state)
    let label = output.featureValue(for: "classification")?.stringValue
    print("Frame classification: \(label ?? "unknown")")
}
```

### Example 6: MLTensor (iOS 18+)
```swift
import CoreML

// Creation and operations
let tensor = MLTensor([1.0, 2.0, 3.0, 4.0])
let reshaped = tensor.reshaped(to: [2, 2])
let softmaxed = tensor.softmax()

// Materialization
let array = try tensor.shapedArray(of: Float.self)
```

### Example 7: Batch prediction
```swift
let batchInputs = try MLArrayBatchProvider(array: inputs.map { input in
    try MLDictionaryFeatureProvider(dictionary: ["image": MLFeatureValue(pixelBuffer: input)])
})
let batchOutput = try model.predictions(from: batchInputs)
for i in 0..<batchOutput.count {
    let result = batchOutput.features(at: i)
    print(result.featureValue(for: "classLabel")?.stringValue ?? "unknown")
}
```

---

## Common Mistakes

### ❌ Loading model on main thread every time
```swift
// Bad: Blocks UI
let model = try MLModel(contentsOf: modelURL)
let output = try model.prediction(input: input)
```
✅ **Fix:** Cache the model; load once in init
```swift
class Predictor {
    let model: MLModel
    init(modelURL: URL) throws {
        self.model = try MLModel(contentsOf: modelURL)
    }
    func predict(_ input: MyInput) throws -> MyOutput {
        try model.prediction(input: input) as! MyOutput
    }
}
```

### ❌ Ignoring compute units; forcing CPU
```swift
// Bad: Slow; neural engine unused
let config = MLModelConfiguration()
config.computeUnits = .cpuOnly
```
✅ **Fix:** Let model choose intelligently
```swift
let config = MLModelConfiguration()
config.computeUnits = .cpuAndNeuralEngine // Default is best
```

### ❌ Not handling feature type mismatches
```swift
// Bad: Runtime crash if input shape wrong
let input = try MLDictionaryFeatureProvider(dictionary: ["image": cgImage])
```
✅ **Fix:** Validate or use generated input types
```swift
let input = MyModelInput(image: resizedCGImage) // Type-safe
let output = try model.prediction(input: input)
```

### ❌ Blocking async predictions
```swift
// Bad: Defeats purpose of async
asyncModel.predictionAsync(from: input, options: opts) { output, _ in
    Thread.sleep(forTimeInterval: 1) // ???
}
```
✅ **Fix:** Use callbacks or async/await properly
```swift
if #available(iOS 17, *) {
    let output = try await model.asyncPrediction(from: input)
} else {
    asyncModel.predictionAsync(from: input, options: opts) { output, _ in
        DispatchQueue.main.async { updateUI(with: output) }
    }
}
```

### ❌ No error handling for unsupported models
```swift
// Bad: Crashes if model incompatible with device
let model = try MLModel(contentsOf: url)
```
✅ **Fix:** Check availability gracefully
```swift
do {
    let config = MLModelConfiguration()
    let model = try MLModel(contentsOf: url, configuration: config)
    // proceed
} catch {
    fallbackToCoreImageOrNet()
}
```

## MLComputePlan (iOS 17.4+)

Inspect compute device dispatch before running predictions:

```swift
let computePlan = try await MLComputePlan.load(
    contentsOf: modelURL, configuration: config
)
guard case let .program(program) = computePlan.modelStructure else { return }
guard let mainFunction = program.functions["main"] else { return }

for operation in mainFunction.block.operations {
    let device = computePlan.deviceUsage(for: operation)
    let cost = computePlan.estimatedCost(of: operation)
    print("\(operation.operatorName): \(device?.preferredComputeDevice ?? "unknown")")
}
```

## Model Loading and Async Patterns

### Async Loading (iOS 16+)

```swift
let model = try await MLModel.load(
    contentsOf: modelURL,
    configuration: config
)
```

### Compile at Runtime

```swift
let compiledURL = try await MLModel.compileModel(at: packageURL)
// Cache compiledURL persistently to avoid recompilation
let model = try MLModel(contentsOf: compiledURL, configuration: config)
```

### On-Demand Resource Loading

```swift
let request = NSBundleResourceRequest(tags: ["ml-model-v2"])
try await request.beginAccessingResources()
let modelURL = Bundle.main.url(forResource: "LargeModel", withExtension: "mlmodelc")!
let model = try await MLModel.load(contentsOf: modelURL, configuration: config)
// Call request.endAccessingResources() when done
```

### Actor-Based Caching

```swift
actor ModelManager {
    static let shared = ModelManager()
    private var cachedModel: MLModel?
    private let config = MLModelConfiguration()

    func getModel() async throws -> MLModel {
        if let cached = cachedModel { return cached }
        let model = try await MLModel.load(contentsOf: modelURL, configuration: config)
        cachedModel = model
        return model
    }
}

// Usage
let model = try await ModelManager.shared.getModel()
let output = try await model.prediction(from: input)
```

---

## Review Checklist

- [ ] Model is loaded **once**, cached as property (not per-prediction)
- [ ] Async loading used for large models; not blocking main thread
- [ ] Compiled `.mlmodelc` URL cached persistently if compiled at runtime
- [ ] Inputs are **resized/normalized** to model's expected dimensions
- [ ] Compute units set to `.cpuAndNeuralEngine` or `.all` (not forced to `.cpuOnly`)
- [ ] Async predictions run **off main thread**; UI updates queued to main
- [ ] Feature provider types match model's input schema
- [ ] Error handling covers unsupported/corrupted model files
- [ ] Model file **included in bundle** (Copy Bundle Resources build phase)
- [ ] MLComputePlan used to verify device dispatch (iOS 17.4+)
- [ ] Batch predictions used when processing multiple inputs
- [ ] Stateful predictions (MLState) only used for sequence/LSTM models
- [ ] Vision integration uses CoreMLRequest (iOS 18+) or VNCoreMLRequest
- [ ] MLTensor operations used for pre/post-processing (iOS 18+)
- [ ] Prediction latency measured; acceptable for feature's UX (e.g., <100ms for real-time)
- [ ] Tests mock MLModel or use small quantized model for speed
- [ ] No memory leaks from retained model references in closures
- [ ] Memory tested on target devices (especially older devices with less RAM)
- [ ] Fallback strategy documented if model unavailable

## Enriched Common Mistakes

- ❌ Loading models synchronously on main thread — use `MLModel.load()` async (iOS 16+)
- ❌ Wrong compute unit selection — `.all` lets Core ML choose, don't force `.cpuAndGPU` unless profiled
- ❌ Not handling model loading failures — model file may be corrupt or missing
- ❌ Creating new model instance for every prediction — cache and reuse
- ❌ Ignoring `MLTensor` (iOS 18+) — lazy evaluation is more memory-efficient for large data

## Enriched Review Checklist

- [ ] Models loaded asynchronously (not blocking main thread)
- [ ] Compute units set appropriately (`.all` unless profiled)
- [ ] Model instances cached and reused
- [ ] Prediction errors handled gracefully
- [ ] Memory profiled for large models
- [ ] Batch prediction used when processing multiple inputs

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

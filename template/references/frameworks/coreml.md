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
| `MLComputeUnits` | `.all` \| `.cpuOnly` \| `.cpuAndNeuralEngine` |
| `MLDictionaryFeatureProvider` | Simple dict-based input provider |
| `MLSequenceConstraint` | Validates sequence inputs for LSTM/RNN models |
| `CreateML` | Xcode tool; not code—generates .mlmodel files |
| `Vision + CoreML` | Use `VNCoreMLRequest` for image classification |
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

### Example 3: Vision framework integration
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

---

## Review Checklist

- [ ] Model is loaded **once**, cached as property (not per-prediction)
- [ ] Inputs are **resized/normalized** to model's expected dimensions
- [ ] Compute units set to `.cpuAndNeuralEngine` (not forced to CPU)
- [ ] Async predictions run **off main thread**; UI updates queued to main
- [ ] Feature provider types match model's input schema
- [ ] Error handling covers unsupported/corrupted model files
- [ ] Model file **included in bundle** (Copy Bundle Resources build phase)
- [ ] Prediction latency measured; acceptable for feature's UX (e.g., <100ms for real-time)
- [ ] Tests mock MLModel or use small quantized model for speed
- [ ] No memory leaks from retained model references in closures
- [ ] Apple Intelligence integration points noted if applicable (e.g., on-device alternatives)
- [ ] Fallback strategy documented if model unavailable

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

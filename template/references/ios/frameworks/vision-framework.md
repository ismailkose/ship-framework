# Vision Framework — iOS Reference

> **When to read:** Dev reads this when building features with image analysis: face detection, text recognition, barcode scanning, document scanning, image segmentation, body/hand pose detection, object tracking, or implementing Core ML inference (iOS 18+ preferred for modern async API).

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API — Legacy (Pre-iOS 18)

| Type | Purpose | Pattern |
|------|---------|---------|
| `VNImageRequestHandler` | Synchronous request processor; init with CGImage, CIImage, or Data | Completion handler or synchronous `perform` |
| `VNSequenceRequestHandler` | Processes video frames; maintains tracking state across frames | Completion handler |
| `VNRequest` | Abstract base; subclass or use concrete types | ObjC classes (VNDetect*, VNRecognize*, VNGenerate*) |
| `VNDetectFaceRectanglesRequest` | Detects face bounds; returns VNFaceObservation | Completion handler |
| `VNRecognizeTextRequest` | Live Text; OCR for any language; VNRecognizedTextObservation | Completion handler |
| `VNDetectBarcodesRequest` | QR, UPC, Code128, etc.; VNBarcodeObservation with payload | Completion handler |

## Core API — Modern (iOS 18+)

| Type | Purpose | Pattern |
|------|---------|---------|
| `ImageProcessingRequest` | Protocol for modern requests; `perform(on:orientation:)` async | Swift structs, async/await |
| `RecognizeTextRequest` | Modern OCR with custom words, language hints | Struct; `perform(on:)` returns `[RecognizedTextObservation]` |
| `RecognizeDocumentsRequest` | Structured document reading (paragraphs, tables, lists) | Struct; `perform(on:)` returns `[DocumentObservation]` |
| `DetectFaceRectanglesRequest` | Modern face detection | Struct; `perform(on:)` returns `[FaceObservation]` |
| `DetectFaceLandmarksRequest` | Modern face landmarks (eyes, nose, mouth) | Struct; `perform(on:)` returns `[FaceLandmarkObservation]` |
| `DetectBarcodesRequest` | Modern barcode detection | Struct; `perform(on:)` returns `[BarcodeObservation]` |
| `GeneratePersonSegmentationRequest` | Person silhouette mask | Struct; `perform(on:)` returns `PersonSegmentationObservation` |
| `GeneratePersonInstanceMaskRequest` | Per-person instance masks | Struct; `perform(on:)` returns `PersonInstanceMaskObservation` |
| `TrackObjectRequest` | Stateful object tracking across frames | Final class (stateful); `perform(on:)` tracks object |
| `DetectHumanBodyPoseRequest` | Body joint detection | Struct; `perform(on:)` returns `[HumanBodyPoseObservation]` |
| `DetectHumanHandPoseRequest` | Hand joint and finger detection | Struct; `perform(on:)` returns `[HumanHandPoseObservation]` |
| `DetectAnimalBodyPoseRequest` | Animal body pose estimation | Struct; `perform(on:)` returns `[AnimalBodyPoseObservation]` |
| `CoreMLRequest` | Custom Core ML model inference | Struct; `perform(on:)` returns typed observations |

---

## Code Examples

### Example 1: Face detection
```swift
import Vision

let request = VNDetectFaceRectanglesRequest { request, error in
    guard let observations = request.results as? [VNFaceObservation] else { return }
    observations.forEach { face in
        print("Face at: \(face.boundingBox)")
        // Convert normalized coords to image space
        let rect = VNImageRectForNormalizedRect(face.boundingBox, imageWidth, imageHeight)
    }
}

let handler = VNImageRequestHandler(cgImage: image, options: [:])
try handler.perform([request])
```

### Example 2: Live Text (OCR)
```swift
import Vision

let textRequest = VNRecognizeTextRequest { request, error in
    guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
    let fullText = observations
        .compactMap { $0.topCandidates(1).first?.string }
        .joined(separator: "\n")
    print("Recognized: \(fullText)")
}
textRequest.recognitionLanguages = ["en-US", "es-ES"]

let handler = VNImageRequestHandler(cgImage: image, options: [:])
try handler.perform([textRequest])
```

### Example 3: Barcode detection + streaming video
```swift
import Vision
import AVFoundation

class BarcodeScanner: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    let sequenceHandler = VNSequenceRequestHandler()

    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        let barcodeRequest = VNDetectBarcodesRequest { request, error in
            guard let barcodes = request.results as? [VNBarcodeObservation] else { return }
            barcodes.forEach { barcode in
                print("Barcode: \(barcode.payloadStringValue ?? "")")
            }
        }

        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        try? sequenceHandler.perform([barcodeRequest], on: pixelBuffer)
    }
}
```

### Example 4: Modern API (iOS 18+) — Text recognition with custom words
```swift
import Vision

func recognizeText(in image: CGImage) async throws -> [String] {
    var request = RecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = [Locale.Language(identifier: "en-US")]
    request.customWords = ["SwiftUI", "Xcode", "API"]  // Domain-specific hints
    request.usesLanguageCorrection = true

    let observations = try await request.perform(on: image)
    return observations.compactMap { observation in
        observation.topCandidates(1).first?.string
    }
}
```

### Example 5: Document recognition (iOS 18+)
```swift
import Vision

func recognizeDocument(in image: CGImage) async throws {
    var request = RecognizeDocumentsRequest()
    let documents = try await request.perform(on: image)

    for observation in documents {
        let fullText = observation.document.text

        // Access structured elements
        for paragraph in observation.document.paragraphs {
            print("Paragraph: \(paragraph.text)")
        }

        for table in observation.document.tables {
            // Process table structure
        }

        for list in observation.document.lists {
            // Process list items
        }
    }
}
```

### Example 6: Person instance segmentation (iOS 18+)
```swift
import Vision

func segmentPersonInstances(in image: CGImage) async throws {
    let request = GeneratePersonInstanceMaskRequest()
    let observation = try await request.perform(on: image)

    // Get all person instances in the image
    let indices = observation.allInstances

    for index in indices {
        // Generate mask for this person only
        let mask = try observation.generateMask(forInstances: IndexSet(integer: index))
        // mask is a CVPixelBuffer with only this person visible
    }
}
```

### Example 7: Human hand pose detection (iOS 18+)
```swift
import Vision

func detectHandPose(in image: CGImage) async throws {
    let request = DetectHumanHandPoseRequest()
    let observations = try await request.perform(on: image)

    for observation in observations {
        // observation contains all hand joints (wrist, fingers, etc.)
        for joint in observation.recognizedPoints {
            let confidence = joint.confidence
            let location = joint.location  // normalized coordinates
        }
    }
}
```

### Example 8: Object tracking across video frames (iOS 18+)
```swift
import Vision

class ObjectTracker {
    var trackRequest: TrackObjectRequest?

    func startTracking(with initialBox: CGRect) {
        let observation = DetectedObjectObservation(boundingBox: initialBox)
        trackRequest = TrackObjectRequest(observation: observation)
        trackRequest?.trackingLevel = .accurate
    }

    func trackInFrame(_ pixelBuffer: CVPixelBuffer) async throws {
        guard let request = trackRequest else { return }

        let results = try await request.perform(on: pixelBuffer)
        if let tracked = results.first {
            print("Object at: \(tracked.boundingBox)")
            // Update for next frame
            trackRequest?.inputObservation = tracked
        }
    }
}
```

### Example 9: Coordinate system conversion (Vision uses bottom-left origin)
```swift
import Vision

func convertToUIKit(_ rect: CGRect, imageHeight: CGFloat) -> CGRect {
    // Vision: bottom-left origin, normalized [0...1]
    // UIKit: top-left origin, points
    CGRect(
        x: rect.origin.x * imageWidth,
        y: (1.0 - rect.origin.y - rect.height) * imageHeight,
        width: rect.width * imageWidth,
        height: rect.height * imageHeight
    )
}
```

---

## Common Mistakes

### ❌ Using non-normalized coordinates directly
```swift
// Bad: Results are in normalized space [0, 1]
let faceRect = CGRect(x: face.boundingBox.minX, y: face.boundingBox.minY, ...)
```
✅ **Fix:** Convert to image space
```swift
let faceRect = VNImageRectForNormalizedRect(
    face.boundingBox,
    Int(image.width),
    Int(image.height)
)
```

### ❌ Running requests on main thread without async
```swift
// Bad: Blocks UI for 100-500ms per image
try handler.perform([request]) // Synchronous
```
✅ **Fix:** Dispatch to background
```swift
DispatchQueue.global(qos: .userInitiated).async {
    try? handler.perform([request])
    DispatchQueue.main.async { updateUI() }
}
```

### ❌ Creating new handler for each frame in video
```swift
// Bad: Allocates handler repeatedly
func processFrame(_ buffer: CVPixelBuffer) {
    let handler = VNImageRequestHandler(cvPixelBuffer: buffer, options: [:])
    try? handler.perform([request])
}
```
✅ **Fix:** Use VNSequenceRequestHandler for streaming
```swift
class VideoProcessor {
    let sequenceHandler = VNSequenceRequestHandler()

    func processFrame(_ buffer: CVPixelBuffer) {
        try? sequenceHandler.perform([request], on: buffer)
    }
}
```

### ❌ Ignoring text recognition orientation
```swift
// Bad: Image rotated; text upside down
let request = VNRecognizeTextRequest { ... }
let handler = VNImageRequestHandler(cgImage: rotatedImage, options: [:])
```
✅ **Fix:** Specify image orientation
```swift
let handler = VNImageRequestHandler(
    cgImage: rotatedImage,
    orientation: .rightMirrored // Match actual orientation
)
```

### ❌ Not cleaning up landmark dependencies
```swift
// Bad: Face landmark request runs without face detection
let landmarkRequest = VNDetectFaceLandmarksRequest()
try handler.perform([landmarkRequest])
```
✅ **Fix:** Run face detection first, then landmarks
```swift
let faceRequest = VNDetectFaceRectanglesRequest { ... }
let landmarkRequest = VNDetectFaceLandmarksRequest()
try handler.perform([faceRequest, landmarkRequest])
```

---

## Review Checklist

- [ ] Modern API preferred (iOS 18+): struct-based requests with `perform(on:)` and async/await
- [ ] Results converted from **normalized to image space** (use coordinate conversion functions)
- [ ] Requests run **off main thread** (background queue or detached async task)
- [ ] UI updates queued back to main thread
- [ ] For video/streaming: use `VNSequenceRequestHandler` (legacy) or modern stateful requests
- [ ] Image orientation specified if known (`.up`, `.rightMirrored`, etc.)
- [ ] Error handling present; gracefully handles no detections
- [ ] Dependencies honored: face landmarks require face detection first
- [ ] Performance profiled; acceptable latency for use case (real-time <33ms per frame)
- [ ] Live Text authorization checked if using text recognition
- [ ] Memory: no retained references to CGImage/CVPixelBuffer in closures
- [ ] Barcode symbologies specified if known (reduce false positives)
- [ ] Tests use sample images at expected resolutions
- [ ] For iOS 18+: `RecognizeTextRequest.customWords` set for domain-specific terms
- [ ] For iOS 18+: `RecognizeDocumentsRequest` used for structured document layout (paragraphs, tables)
- [ ] For iOS 18+: `GeneratePersonInstanceMaskRequest` used for per-person segmentation
- [ ] For iOS 18+: `DetectHumanHandPoseRequest` and `DetectAnimalBodyPoseRequest` confidence threshold applied
- [ ] For iOS 18+: Stateful `TrackObjectRequest` retained and updated across frames
- [ ] Confidence threshold applied to filter low-quality observations
- [ ] Recognition level matches use case (`.fast` for video, `.accurate` for stills)

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

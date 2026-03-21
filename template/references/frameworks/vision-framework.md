# Vision Framework — iOS Reference

> **When to read:** Dev reads this when building features with image analysis: face detection, text recognition, barcode scanning, image classification, or Live Text.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `VNImageRequestHandler` | Synchronous request processor; init with CGImage, CIImage, or Data |
| `VNSequenceRequestHandler` | Processes video frames; maintains tracking state across frames |
| `VNRequest` | Abstract base; subclass or use concrete types |
| `VNDetectFaceRectanglesRequest` | Detects face bounds; returns VNFaceObservation |
| `VNDetectFaceLandmarksRequest` | Eyes, nose, mouth, jaw points; requires face detection first |
| `VNRecognizeTextRequest` | Live Text; OCR for any language; VNRecognizedTextObservation |
| `VNBarcodeDetectionRequest` | QR, UPC, Code128, etc.; VNBarcodeObservation with payload |
| `VNImageBasedRequest` | Superclass; defines image input requirements |
| `VNObservation` | Result container; subclassed for each request type |
| `VNImageCropAndScaleOption` | `.scaleFill` \| `.scaleFit` \| `.centerCrop` |
| `VNTrackingRequest` | Tracks objects across video frames; VNTrajectoryObservation |

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

- [ ] Results converted from **normalized to image space** (use `VNImageRectForNormalizedRect`)
- [ ] Requests run **off main thread** (DispatchQueue.global)
- [ ] UI updates queued back to main thread
- [ ] For video/streaming: use `VNSequenceRequestHandler`, not new handler per frame
- [ ] Image orientation specified if known (`.up`, `.rightMirrored`, etc.)
- [ ] Error handling present; gracefully handles no detections
- [ ] Dependencies honored: face landmarks require face detection first
- [ ] Performance profiled; acceptable latency for use case (real-time <33ms per frame)
- [ ] Live Text authorization checked if using `VNRecognizeTextRequest`
- [ ] Memory: no retained references to CGImage/CVPixelBuffer in closures
- [ ] Barcode symbologies specified if known (avoid scanning all types)
- [ ] Tests use sample images at expected resolutions

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

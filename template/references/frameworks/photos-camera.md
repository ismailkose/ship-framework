# Photos & Camera — iOS Reference

> **When to read:** Dev reads this when building features with photo picking, camera capture, or saving to photo library.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `PhotosPicker` | SwiftUI view; opens native picker; iOS 16+ recommended |
| `PHPickerViewController` | UIKit picker; fine-grained control over selection |
| `PHPickerConfiguration` | Filter by media type (`.images`, `.videos`, `.livePhotos`) |
| `PHPhotoLibrary` | Access to user's photo library; requires authorization |
| `PHAsset` | Represents a photo/video; immutable reference |
| `PHAssetCollection` | Album/folder of PHAssets |
| `PHImageManager` | Fetch image data from PHAsset; with caching |
| `AVCaptureSession` | Manages camera input/output graph |
| `AVCaptureDevice` | Camera/microphone; position, format, zoom, focus |
| `AVCaptureVideoPreviewLayer` | Preview layer for camera |
| `PHAssetChangeRequest` | Request to modify/delete assets |
| `PHAssetCreationRequest` | Add new photos to library |
| `PHPhotoLibraryChangeObserver` | Listen for library changes |

---

## Code Examples

### Example 1: PhotosPicker (SwiftUI) — iOS 16+
```swift
import SwiftUI
import PhotosUI

struct PhotoPickerView: View {
    @State var selectedPhotos: [PhotosPickerItem] = []
    @State var selectedImages: [Image] = []

    var body: some View {
        VStack {
            PhotosPicker(
                selection: $selectedPhotos,
                maxSelectionCount: 3,
                matching: .images,
                label: { Text("Pick Photos") }
            )
            .onChange(of: selectedPhotos) { oldValue, newValue in
                Task {
                    for item in newValue {
                        if let data = try? await item.loadTransferable(type: Data.self),
                           let uiImage = UIImage(data: data) {
                            selectedImages.append(Image(uiImage: uiImage))
                        }
                    }
                }
            }

            ForEach(selectedImages, id: \.self) { image in
                image.resizable().scaledToFit()
            }
        }
    }
}
```

### Example 2: PHPickerViewController (UIKit)
```swift
import UIKit
import PhotosUI

class ViewController: UIViewController, PHPickerViewControllerDelegate {
    func openPhotoPicker() {
        var config = PHPickerConfiguration()
        config.filter = .images
        config.selectionLimit = 5

        let picker = PHPickerViewController(configuration: config)
        picker.delegate = self
        present(picker, animated: true)
    }

    func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
        dismiss(animated: true)

        results.forEach { result in
            result.itemProvider.loadObject(ofClass: UIImage.self) { image, error in
                if let image = image as? UIImage {
                    DispatchQueue.main.async { self.processImage(image) }
                }
            }
        }
    }

    func processImage(_ image: UIImage) {
        // Use image
    }
}
```

### Example 3: Save image to photo library
```swift
import Photos

func saveImageToLibrary(_ image: UIImage) {
    PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
        guard status == .authorized else {
            print("Photo library access denied")
            return
        }

        PHPhotoLibrary.shared().performChanges {
            let creationRequest = PHAssetCreationRequest.creationRequestForAsset(from: image)
            creationRequest.creationDate = Date()
        } completionHandler: { success, error in
            if success {
                print("Saved to library")
            } else if let error = error {
                print("Error: \(error)")
            }
        }
    }
}
```

### Example 4: Camera capture with AVCaptureSession
```swift
import AVFoundation
import UIKit

class CameraViewController: UIViewController {
    let captureSession = AVCaptureSession()
    let videoOutput = AVCaptureVideoDataOutput()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
    }

    func setupCamera() {
        guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) else {
            print("No camera available")
            return
        }

        do {
            let input = try AVCaptureDeviceInput(device: camera)
            captureSession.addInput(input)
            captureSession.addOutput(videoOutput)

            let previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
            previewLayer.videoGravity = .resizeAspectFill
            previewLayer.frame = view.bounds
            view.layer.insertSublayer(previewLayer, at: 0)

            captureSession.startRunning()
        } catch {
            print("Camera setup error: \(error)")
        }
    }

    func capturePhoto() {
        let photoOutput = AVCapturePhotoOutput()
        captureSession.addOutput(photoOutput)

        let photoSettings = AVCapturePhotoSettings()
        photoSettings.flashMode = .auto

        photoOutput.capturePhoto(with: photoSettings, delegate: self)
    }
}

extension CameraViewController: AVCapturePhotoCaptureDelegate {
    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        guard let imageData = photo.fileDataRepresentation(),
              let image = UIImage(data: imageData) else { return }
        saveImageToLibrary(image)
    }
}
```

---

## Common Mistakes

### ❌ Not requesting photo library authorization
```swift
// Bad: Picker appears empty; user confused
var selectedPhotos: [PhotosPickerItem] = []
```
✅ **Fix:** Request authorization in Info.plist + code
```swift
// Info.plist: NSPhotoLibraryUsageDescription
PhotosPicker(selection: $selectedPhotos, matching: .images) { ... }
// iOS will prompt on first access
```

### ❌ Loading full-resolution image for thumbnail
```swift
// Bad: Memory spike; slow UI
result.itemProvider.loadObject(ofClass: UIImage.self) { image, _ in
    // Image is full resolution; massive for thumbnail
}
```
✅ **Fix:** Use PHImageManager with target size
```swift
let options = PHImageRequestOptions()
options.deliveryMode = .fastFormat
options.resizeMode = .fast

PHImageManager.default().requestImage(
    for: asset,
    targetSize: CGSize(width: 100, height: 100),
    contentMode: .aspectFill,
    options: options
) { image, _ in ... }
```

### ❌ Saving to library without checking authorization first
```swift
// Bad: Silent failure
PHPhotoLibrary.shared().performChanges { ... }
```
✅ **Fix:** Request authorization and check status
```swift
PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
    guard status == .authorized else { return }
    PHPhotoLibrary.shared().performChanges { ... }
}
```

### ❌ Keeping camera session running in background
```swift
// Bad: Battery drain; background audio/video restrictions
override func viewDidLoad() {
    captureSession.startRunning()
}
// No cleanup; runs forever
```
✅ **Fix:** Manage session lifecycle
```swift
override func viewWillAppear(_ animated: Bool) {
    super.viewWillAppear(animated)
    if !captureSession.isRunning {
        captureSession.startRunning()
    }
}

override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    if captureSession.isRunning {
        captureSession.stopRunning()
    }
}
```

### ❌ Not handling multi-selection properly
```swift
// Bad: User picks 10 images; UI hangs loading all
for item in selectedPhotos {
    let image = await item.loadTransferable(type: Data.self)
    // Load sequentially; blocks
}
```
✅ **Fix:** Load concurrently with task group
```swift
Task {
    await withTaskGroup(of: Image?.self) { group in
        for item in selectedPhotos {
            group.addTask {
                if let data = try? await item.loadTransferable(type: Data.self),
                   let uiImage = UIImage(data: data) {
                    return Image(uiImage: uiImage)
                }
                return nil
            }
        }

        for await image in group {
            if let image = image {
                selectedImages.append(image)
            }
        }
    }
}
```

---

## Review Checklist

- [ ] Photo library access permissions in Info.plist (`NSPhotoLibraryUsageDescription`, `NSCameraUsageDescription`)
- [ ] Authorization status checked/requested before accessing library
- [ ] `PHPickerViewController` used instead of deprecated `UIImagePickerController`
- [ ] Images resized/optimized before display (avoid full resolution for thumbnails)
- [ ] Camera session **started in viewWillAppear, stopped in viewWillDisappear** (battery/background safety)
- [ ] AVCaptureSession teardown complete (inputs/outputs removed)
- [ ] Multi-selection loads concurrently (Task.group) not sequentially
- [ ] Photo library changes observed if displaying persistent asset list
- [ ] `performChanges` wrapped with error handling for library modifications
- [ ] Privacy: Camera usage in Info.plist if capturing (not just picking)
- [ ] Tests mock PHPhotoLibrary/AVCaptureDevice for unit tests
- [ ] Video capture: check device formats/frame rates before setting

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

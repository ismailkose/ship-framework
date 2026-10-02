<!-- ship-reference
id: ios-media
kind: mixed
sources: iPhoneOS27.0.sdk PhotosUI / Photos / AVFoundation / AVFAudio (headers) / AVKit / MediaPlayer / Speech / ImageIO / PDFKit / PencilKit / SpriteKit / RealityKit / GameKit interfaces (Xcode 27.0 27A266a — examples type-check via scripts/checks/ios.sh; the downsampling function runs on the host via scripts/checks/ios_runtime); https://developer.apple.com/documentation/photokit ; https://developer.apple.com/documentation/avfoundation/capture-setup ; https://developer.apple.com/documentation/avfaudio/avaudiosession ; https://developer.apple.com/documentation/speech ; https://developer.apple.com/documentation/avkit ; https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app ; https://developer.apple.com/documentation/gamekit (all checked 2026-09-24). Written for Ship from Apple's docs and the SDK; no third-party text.
reviewed: 2026-09-25
-->
# Photos, camera, audio, video, speech — and a little 3D

**When to read:** "import photos", "attach an image", "take a photo", "scan", "record audio / a voice
memo", "play a podcast in the background", video playback, transcription / dictation, PDFs,
drawing, a game or 3D scene. **Apple** = platform requirement; **Ship** = default.

## 1. Permissions at a glance (Apple)

| Feature | Info.plist key | Ask for |
|---|---|---|
| Pick photos (`PhotosPicker`) | none | nothing — runs out of process |
| Save photos to the library | `NSPhotoLibraryAddUsageDescription` | `.addOnly` access |
| Read/manage the library | `NSPhotoLibraryUsageDescription` | `.readWrite`; the person may grant **Limited** |
| Camera | `NSCameraUsageDescription` | `AVCaptureDevice.requestAccess(for: .video)` |
| Microphone | `NSMicrophoneUsageDescription` | `AVAudioApplication.requestRecordPermission()` (iOS 17) |
| Speech recognition | `NSSpeechRecognitionUsageDescription` | `SFSpeechRecognizer.requestAuthorization` |

A missing key crashes on first use. Purpose strings say what and why in the person's terms
(App Review 5.1.1). Denied → explain in place and link to Settings; don't loop the prompt.

## 2. Importing photos and video

- **Ship:** `PhotosPicker` first — no permission prompt, supports multi-select, filters
  (`.images`, `.videos`, `.any(of:)`), and respects the person's privacy. Use PhotoKit only when
  the app manages the library (albums, edits in place, "all my photos" views).
- Load with `loadTransferable(type:)`. It's async and can fail or return nil (iCloud-only asset
  offline, unsupported type) — show per-item progress and errors, and keep the rest.
- **Never decode the original for display.** A 48 MP photo is ~200 MB decoded. Downsample to the
  displayed size × scale with ImageIO (below) or `byPreparingThumbnail(ofSize:)`; keep the
  original bytes only if you upload or store them.
- **Remote images:** on iOS 27, `AsyncImage(request:)` with `.asyncImageURLSession(_:)` loads through a
  session you configure, so its `URLCache` and the server's cache headers decide what's reused
  (`ios-27.md` §3). Below 27, `AsyncImage(url:)` has only the shared cache: long lists get a small
  loader that downsamples as above and keeps decoded images in `NSCache`.
- **Decode off the main actor.** A view's `.task` runs on the main actor, and a synchronous helper
  runs wherever it's called — so call the decoder through a `@concurrent` async function
  (`swift-practice.md` §1). Ship's host test checks the example below does its decoding off the main
  thread when called from the main actor.
- Video and large files: use a `Transferable` type with a `FileRepresentation` and copy the
  received file into your container — the provided URL is temporary.
- Saving: `PHPhotoLibrary.shared().performChanges` with add-only permission.
- Limited library access: the app sees only the chosen items; offer "Select more photos"
  (`PHPhotoLibrary.shared().presentLimitedLibraryPicker`) where a grid would look empty.

```swift
import PhotosUI
import ImageIO

/// Decodes a thumbnail no larger than `maxPixel` on its longest side — no full-size decode.
nonisolated func downsample(_ data: Data, maxPixel: Int) -> CGImage? {
    let sourceOptions = [kCGImageSourceShouldCache: false] as CFDictionary
    guard let source = CGImageSourceCreateWithData(data as CFData, sourceOptions) else { return nil }
    let options = [kCGImageSourceCreateThumbnailFromImageAlways: true,
                   kCGImageSourceCreateThumbnailWithTransform: true,   // honour EXIF orientation
                   kCGImageSourceShouldCacheImmediately: true,
                   kCGImageSourceThumbnailMaxPixelSize: maxPixel] as CFDictionary
    return CGImageSourceCreateThumbnailAtIndex(source, 0, options)
}

/// The decode runs off the main actor even when awaited from a view's `.task`.
@concurrent nonisolated func thumbnail(from data: Data, maxPixel: Int) async -> CGImage? {
    downsample(data, maxPixel: maxPixel)
}

struct AttachPhotos: View {
    @State private var selection: [PhotosPickerItem] = []
    @State private var thumbnails: [Image] = []
    @Environment(\.displayScale) private var scale

    var body: some View {
        PhotosPicker("Add photos", selection: $selection, maxSelectionCount: 10, matching: .images)
            .task(id: selection) {
                var loaded: [Image] = []
                for item in selection {
                    guard let data = try? await item.loadTransferable(type: Data.self),
                          let cg = await thumbnail(from: data, maxPixel: Int(120 * scale)) else { continue }
                    if Task.isCancelled { return }           // selection changed — drop stale work
                    loaded.append(Image(decorative: cg, scale: scale))
                }
                thumbnails = loaded
            }
    }
}
```

## 3. Camera capture

- **Ship:** for "take a photo to attach", the system camera UI (`UIImagePickerController` with
  `.camera`, wrapped) or a document scanner (VisionKit `VNDocumentCameraViewController`) is less
  code and fewer bugs than a custom session. Build a custom `AVCaptureSession` only for a custom
  camera experience (scanning overlays, filters, live analysis).
- Custom session rules (Apple): configure between `beginConfiguration()`/`commitConfiguration()`;
  `startRunning()` blocks — never on the main thread; stop when the view disappears or the app
  backgrounds; handle `AVCaptureSession.wasInterruptedNotification` (a call, Split View, another
  app using the camera). Orientation: `AVCaptureDevice.RotationCoordinator` (iOS 17), not the
  deprecated video-orientation property.
- Isolation: put the session in an actor whose executor is a serial dispatch queue — capture APIs
  expect one, and this is the one place Ship code touches a `DispatchQueue` (as an executor only).
- **Test:** the simulator has no camera. Capture needs a **device**; test permission denied,
  interruption (incoming call), backgrounding, and rotation.

```swift
import AVFoundation

actor CaptureService {
    private let queue = DispatchSerialQueue(label: "capture.session")
    nonisolated var unownedExecutor: UnownedSerialExecutor { queue.asUnownedSerialExecutor() }

    private let session = AVCaptureSession()
    private let photoOutput = AVCapturePhotoOutput()

    /// Returns false if permission is missing or the device has no suitable camera.
    func start() async -> Bool {
        guard await AVCaptureDevice.requestAccess(for: .video),
              let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: camera) else { return false }
        session.beginConfiguration()
        session.sessionPreset = .photo
        if session.canAddInput(input) { session.addInput(input) }
        if session.canAddOutput(photoOutput) { session.addOutput(photoOutput) }
        session.commitConfiguration()
        session.startRunning()                 // blocks — fine here, we're on the session queue
        return session.isRunning
    }

    func stop() { session.stopRunning() }
}
```

## 4. Audio: session, recording, playback

- **Session category is the contract with the system** (Apple): `.playback` for media the person
  listens to (keeps playing with the Silent switch; background playback also needs Background
  Modes › Audio); `.playAndRecord` for recording or calls; `.ambient` for sounds that mix with
  other audio and obey Silent. Activate right before use; deactivate with
  `.notifyOthersOnDeactivation` when done so the person's music resumes.
- **Interruptions:** observe `AVAudioSession.interruptionNotification`; on `.began` pause and update
  UI; on `.ended` resume only if the options include `.shouldResume`.
- **Route changes:** on `.oldDeviceUnavailable` (headphones unplugged) pause playback — Apple's
  expected behaviour.
- **Recording:** request microphone permission in context; record to a file in your container
  (`AVAudioRecorder` for simple memos, `AVAudioEngine` for live processing/levels); show a
  clear recording indicator; handle a full disk.
- **Now Playing:** long-form audio sets `MPNowPlayingInfoCenter.default().nowPlayingInfo` and
  handles `MPRemoteCommandCenter` play/pause/skip so Lock Screen and Control Center work.

```swift
import AVFoundation

@MainActor @Observable
final class VoiceMemoRecorder {
    private(set) var isRecording = false
    private var recorder: AVAudioRecorder?

    func start(to url: URL) async throws -> Bool {
        guard await AVAudioApplication.requestRecordPermission() else { return false }
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker])
        try session.setActive(true)
        let settings: [String: Any] = [AVFormatIDKey: kAudioFormatMPEG4AAC,
                                       AVSampleRateKey: 44_100, AVNumberOfChannelsKey: 1]
        let recorder = try AVAudioRecorder(url: url, settings: settings)
        isRecording = recorder.record()
        self.recorder = recorder
        return isRecording
    }

    func stop() {
        recorder?.stop()
        isRecording = false
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }
}
```

**Not shown (add before shipping):** interruption and route-change observers, a level meter, and
what happens when recording is interrupted by a call — test those on a **device**.

## 5. Video playback

- **Ship:** `VideoPlayer` (AVKit) for inline playback; `AVPlayerViewController` (wrapped) when you
  need the full system player, Picture in Picture, or AirPlay controls. Custom players need a
  reason (captions, PiP, and accessibility come free with the system player).
- PiP needs Background Modes › Audio and an `.playback` session. Captions: provide
  `AVMediaSelectionGroup` subtitle tracks or HLS subtitles; the system player shows them.
- Keep one `AVPlayer` per screen; pause and release it when the view disappears.

## 6. Speech to text

- **iOS 26+:** `SpeechAnalyzer` with a `SpeechTranscriber` module — on-device, async sequences of
  results, long-form friendly. Models download per locale: check
  `SpeechTranscriber.supportedLocale(equivalentTo:)` and install assets with
  `AssetInventory.assetInstallationRequest(supporting:)` before starting.
- **Below 26:** `SFSpeechRecognizer` (set `requiresOnDeviceRecognition` when privacy matters and
  `supportsOnDeviceRecognition` is true; server recognition has usage limits).
- Show partial ("volatile") results differently from final ones; let the person edit the text.

```swift
import Speech
import AVFoundation

@available(iOS 26.0, *)
func transcribe(fileAt url: URL, locale: Locale) async throws -> String {
    guard let supported = await SpeechTranscriber.supportedLocale(equivalentTo: locale) else { return "" }
    let transcriber = SpeechTranscriber(locale: supported, preset: .transcription)
    if let install = try await AssetInventory.assetInstallationRequest(supporting: [transcriber]) {
        try await install.downloadAndInstall()          // first use per locale needs a download
    }
    let analyzer = SpeechAnalyzer(modules: [transcriber])
    async let text = transcriber.results.reduce(into: "") { partial, result in
        partial += String(result.text.characters)
    }
    if let end = try await analyzer.analyzeSequence(from: AVAudioFile(forReading: url)) {
        try await analyzer.finalizeAndFinish(through: end)
    } else {
        await analyzer.cancelAndFinishNow()
    }
    return try await text
}
```

## 7. Documents and drawing

**Show and search a PDF:** `PDFView` (wrap in `UIViewRepresentable`, `swiftui-ship.md` §7 has a
reader). `PDFDocument(url:)` returns nil for unreadable files — show an error, not a blank view;
`document.isLocked` → ask for the password and `unlock(withPassword:)`. Create PDFs to share with
`ImageRenderer.render` or `UIGraphicsPDFRenderer`.

**Drawing on PDF pages (PencilKit on PDFKit):**
- Put a `PKCanvasView` over each page with `PDFPageOverlayViewProvider` (iOS 16): PDFKit asks for an
  overlay per visible page and **discards it when the page scrolls away**. So the drawing's owner is
  your model, keyed by **page index** — save in `pdfView(_:willEndDisplayingOverlayView:for:)`,
  restore in `pdfView(_:overlayViewFor:)`. A drawing kept only in the canvas is lost on scroll.
- The overlay moves and zooms with its page, so strokes stay in page space. Converting a point from
  the `PDFView` into page coordinates: `pdfView.convert(point, to: page)` (and back with
  `convert(_:from:)`); PDF page space has its origin at the bottom-left.
- Saving: store each page's `PKDrawing.dataRepresentation()` next to the document (the original
  PDF stays untouched), or **flatten** on export — render the drawing to an image and add it as a
  `PDFAnnotation` in the page's bounds, then `document.write(to:)`.
- Tools: `PKToolPicker` shown for the focused canvas; `drawingPolicy = .anyInput` if finger drawing
  is allowed (else Apple Pencil only). **PaperKit (iOS 26)** gives Apple's full markup UI (shapes,
  text, signatures) when you don't need custom behaviour.
- Collaborative drawing during FaceTime: SharePlay (`system-integration.md` §7) carrying
  `PKDrawing` data or stroke deltas per page.

```swift
import PDFKit
import PencilKit

/// Owns the drawings; PDFKit owns (and recycles) the overlay views.
@MainActor
final class PDFMarkup: NSObject, @preconcurrency PDFPageOverlayViewProvider {
    private(set) var drawings: [Int: PKDrawing] = [:]            // page index → drawing
    private let document: PDFDocument

    init(document: PDFDocument, saved: [Int: Data] = [:]) {
        self.document = document
        self.drawings = saved.compactMapValues { try? PKDrawing(data: $0) }
    }

    func pdfView(_ view: PDFView, overlayViewFor page: PDFPage) -> UIView? {
        let canvas = PKCanvasView()
        canvas.backgroundColor = .clear
        canvas.isOpaque = false
        canvas.drawingPolicy = .pencilOnly                        // product decision: .anyInput allows fingers
        canvas.drawing = drawings[document.index(for: page)] ?? PKDrawing()
        return canvas
    }

    func pdfView(_ pdfView: PDFView, willEndDisplayingOverlayView overlayView: UIView, for page: PDFPage) {
        guard let canvas = overlayView as? PKCanvasView else { return }
        drawings[document.index(for: page)] = canvas.drawing     // save before PDFKit discards the view
    }

    /// What to persist next to the PDF (the original file stays untouched).
    func archive() -> [Int: Data] { drawings.mapValues { $0.dataRepresentation() } }

    /// Export with the drawings flattened into the pages as image annotations.
    func flattened(scale: CGFloat = 2) -> PDFDocument? {
        guard let data = document.dataRepresentation(), let copy = PDFDocument(data: data) else { return nil }
        for (index, drawing) in drawings where !drawing.strokes.isEmpty {
            guard let page = copy.page(at: index) else { continue }
            let bounds = page.bounds(for: .mediaBox)
            let image = drawing.image(from: bounds, scale: scale)
            page.addAnnotation(ImageStamp(bounds: bounds, image: image))
        }
        return copy
    }
}

/// A stamp annotation that draws an image in its bounds.
nonisolated final class ImageStamp: PDFAnnotation {    // PDFKit draws annotations off the main actor
    private let image: UIImage
    init(bounds: CGRect, image: UIImage) {
        self.image = image
        super.init(bounds: bounds, forType: .stamp, withProperties: nil)
    }
    required init?(coder: NSCoder) { nil }
    override func draw(with box: PDFDisplayBox, in context: CGContext) {
        guard let cg = image.cgImage else { return }
        context.draw(cg, in: bounds)
    }
}
```

Set `pdfView.pageOverlayViewProvider = markup` and `pdfView.isInMarkupMode = true` while drawing.
**Not shown:** the tool picker, undo, and page rotation. Compiles; **not run** — scrolling pages
away and back, zoom, and Pencil input need an iPad with an Apple Pencil; check that strokes survive
scrolling and a relaunch, and that the flattened export matches on-screen strokes.

## 8. Games and 3D (brief)

- 2D: `SpriteView` (SpriteKit) hosts a scene in SwiftUI. 3D and AR: `RealityView` (RealityKit;
  iOS 18 on iPhone). SceneKit keeps working for existing scenes; **Ship:** start new 3D in
  RealityKit (Apple's current direction).
- Game Center: authenticate at launch (`GKLocalPlayer.local.authenticateHandler`), then
  leaderboards, achievements, and `GKAccessPoint`; needs the Game Center capability and App Store
  Connect setup. Test with a sandbox Game Center account on a device.
- Engine depth (physics tuning, shaders, multiplayer netcode) is outside Ship — use Apple's docs
  and sample code.

## 9. Verify

| What | How | Level |
|---|---|---|
| Picker import, multi-select, iCloud-only photo offline | Simulator (add photos by dragging) + device with iCloud Photos | Simulator + device |
| Memory on large photos | Import 20 full-size photos; Allocations stays flat | Device (Instruments) |
| Camera, rotation, interruption | **Device only** | Manual |
| Recording + call interruption + headphones unplugged | **Device** | Manual |
| Background audio + Lock Screen controls | Device, screen locked | Manual |
| Transcription | Device or simulator with the locale's assets; compare with a known recording | Simulator + device |
| Denied permissions | Settings › Privacy per feature; the app explains and links to Settings | Simulator |

Apple: [PhotosUI](https://developer.apple.com/documentation/photosui) ·
[Capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup) ·
[AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession) ·
[Speech](https://developer.apple.com/documentation/speech) ·
[Now Playing](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app).

# RealityKit — iOS Reference

> **When to read:** Dev reads this when building AR features with SwiftUI, working with 3D models, anchors, scene understanding, or AR gestures.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `RealityView` | SwiftUI container for RealityKit content; SwiftUI-first pattern on iOS/visionOS |
| `RealityViewCameraContent` | iOS 18+ content that renders through device camera for AR |
| `Entity` | Base class for all 3D objects in RealityKit scene |
| `ModelEntity` | Entity that renders a 3D mesh with material |
| `AnchorEntity` | Entity anchored to world, face, image, body, or plane |
| `ARSession` | Manages device tracking and scene understanding |
| `ARWorldTrackingConfiguration` | Configuration for world tracking and features (planes, images) |
| `ModelComponent` | Defines mesh and material for rendering |
| `Transform` | Position, rotation, scale of entity |
| `Gesture` | Protocol for AR gestures (drag, rotate, scale) |
| `SceneUnderstanding` | Detects planes, frames, meshes from ARSession |
| `SpatialTapGesture` | Gesture for tapping entities; use `.targetedToAnyEntity()` |
| `DragGesture` | Gesture for dragging entities; use `.targetedToAnyEntity()` |
| `SceneEvents.Update` | Per-frame update subscription for continuous processing |

**Key Enums:**
- `AnchorEntity.AnchorType` — world, plane, image, body, face
- `PlaneDetectionConfiguration` — horizontal, vertical, or both

---

## Code Examples

**Example 1: RealityView SwiftUI-first pattern (iOS 18+)**
```swift
import SwiftUI
import RealityKit

struct ARExperienceView: View {
    var body: some View {
        RealityView { content in
            // content is RealityViewCameraContent on iOS
            let sphere = ModelEntity(
                mesh: .generateSphere(radius: 0.05),
                materials: [SimpleMaterial(color: .blue, isMetallic: true)]
            )
            sphere.position = [0, 0, -0.5]  // 50cm in front of camera
            content.add(sphere)
        }
    }
}
```

**Example 1b: Legacy UIKit-based ARView (pre-iOS 18 pattern)**
```swift
import SwiftUI
import RealityKit
import ARKit

struct ARViewContainer: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> ARViewViewController {
        return ARViewViewController()
    }

    func updateUIViewController(_ uiViewController: ARViewViewController, context: Context) {}
}

class ARViewViewController: UIViewController, ARViewDelegate {
    var arView: ARView?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Create AR view
        arView = ARView(frame: view.bounds)
        view.addSubview(arView!)

        // Configure AR session
        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        configuration.frameSemantics.insert(.personSegmentationWithDepth)

        arView?.session.run(configuration)

        // Add a model to the scene
        let anchor = try? Experience.loadBox()  // Example: prebuilt model
        if let anchor = anchor {
            arView?.scene.addAnchor(anchor)
        }
    }
}
```

**Example 2: Programmatic 3D model creation**
```swift
import RealityKit

func createSphere() -> ModelEntity {
    // Create a sphere mesh
    var mesh = try! MeshResource.generateSphere(radius: 0.1)

    // Create material
    var material = SimpleMaterial(
        color: .init(tint: .blue),
        isMetallic: true
    )

    // Create entity
    let sphere = ModelEntity(mesh: mesh, materials: [material])

    // Position in world
    var transform = sphere.transform
    transform.translation = [0, 0, -0.5]  // 0.5m in front of camera
    sphere.move(to: transform, relativeTo: sphere, duration: 0.3, timingFunction: .linear)

    return sphere
}

// Add to scene
let sphere = createSphere()
arView.scene.addAnchor(AnchorEntity(world: [0, 0, -0.5]))
```

**Example 3: Tap gesture to place objects (RealityView)**
```swift
import RealityKit

struct TapToPlaceView: View {
    var body: some View {
        RealityView { content in
            let box = ModelEntity(
                mesh: .generateBox(size: 0.1),
                materials: [SimpleMaterial(color: .red, isMetallic: false)]
            )
            box.position = [0, 0, -0.5]
            box.name = "tapTarget"
            content.add(box)
        }
        .gesture(
            SpatialTapGesture()
                .targetedToAnyEntity()
                .onEnded { value in
                    let tappedEntity = value.entity
                    print("Tapped: \(tappedEntity.name)")
                    highlightEntity(tappedEntity)
                }
        )
    }
}
```

**Example 3b: Legacy UIKit tap-to-place**
```swift
import RealityKit

class ARViewController: UIViewController {
    var arView: ARView?

    override func viewDidLoad() {
        super.viewDidLoad()
        arView = ARView(frame: view.bounds)
        view.addSubview(arView!)

        // Add tap gesture
        let tap = UITapGestureRecognizer(target: self, action: #selector(handleTap))
        arView!.addGestureRecognizer(tap)
    }

    @objc func handleTap(gesture: UITapGestureRecognizer) {
        let location = gesture.location(in: arView!)

        // Ray cast to find surface
        if let result = arView?.raycast(from: location, allowing: .estimatedPlane, alignment: .any).first {
            let anchor = AnchorEntity(world: result.worldTransform)
            let sphere = createSphere()
            anchor.addChild(sphere)
            arView?.scene.addAnchor(anchor)
        }
    }
}
```

---

## Common Mistakes

**Mistake 1: Not checking ARKit availability**
```swift
// ❌ WRONG: Crashes on non-ARKit devices
let configuration = ARWorldTrackingConfiguration()
arView.session.run(configuration)

// ✅ CORRECT: Check availability
if ARWorldTrackingConfiguration.isSupported {
    let configuration = ARWorldTrackingConfiguration()
    arView.session.run(configuration)
}
```

**Mistake 2: Forgetting to run session with configuration**
```swift
// ❌ WRONG: ARSession runs but with default config; no plane detection
arView.session.run(ARWorldTrackingConfiguration())

// ✅ CORRECT: Configure before running
let config = ARWorldTrackingConfiguration()
config.planeDetection = [.horizontal]
arView.session.run(config)
```

**Mistake 3: Modifying transform without reference frame**
```swift
// ❌ WRONG: Position is relative to entity's parent, confusing
entity.position = [0, 0, -0.5]

// ✅ CORRECT: Specify coordinate system
var transform = entity.transform
transform.translation = [0, 0, -0.5]
entity.move(to: transform, relativeTo: arView.scene)
```

**Mistake 4: Not pausing session when app backgrounded**
```swift
// ❌ WRONG: Session continues consuming battery in background
// No pause logic

// ✅ CORRECT: Pause in AppDelegate or SceneDelegate
func sceneWillResignActive(_ scene: UIScene) {
    arView?.session.pause()
}

func sceneDidBecomeActive(_ scene: UIScene) {
    arView?.session.run(configuration)
}
```

**Mistake 5: Raycast result transformation misuse**
```swift
// ❌ WRONG: Using result position without understanding coordinate system
let anchor = AnchorEntity(world: result.worldTransform)  // ✓ Correct, but...
entity.setPosition(result.worldTransform.translation, relativeTo: anchor)  // ✗ Double-anchoring

// ✅ CORRECT: Use world position directly
let anchor = AnchorEntity(world: result.worldTransform)
arView.scene.addAnchor(anchor)
```

**Mistake 6: Not using entity names for lookup in RealityView update closure**
```swift
// ❌ WRONG: Cannot find entity by reference in update closure
RealityView { content in
    let sphere = ModelEntity(mesh: .generateSphere(radius: 0.05))
    content.add(sphere)
} update: { content in
    // sphere is out of scope; no way to find it
    sphere.position.y = 0.1
}

// ✅ CORRECT: Set name for lookup
RealityView { content in
    let sphere = ModelEntity(mesh: .generateSphere(radius: 0.05))
    sphere.name = "mySphere"
    content.add(sphere)
} update: { content in
    if let sphere = content.entities.first(where: { $0.name == "mySphere" }) as? ModelEntity {
        sphere.position.y = 0.1
    }
}
```

**Mistake 7: Ignoring iOS vs. visionOS ARKit differences**
```swift
// ❌ WRONG: Using visionOS-only ARKit APIs on iOS
let arKitSession = ARKitSession()  // Not available on iOS
let worldTrackingProvider = WorldTrackingProvider()  // visionOS only

// ✅ CORRECT: Use RealityViewCameraContent on iOS
RealityView { content in
    // content is RealityViewCameraContent on iOS
    // ARKit tracking handled automatically
    let entity = ModelEntity(mesh: .generateBox(size: 0.1))
    content.add(entity)
}

// For visionOS, use ARKitSession separately; iOS uses RealityView's built-in tracking
```

---

## Review Checklist

- [ ] `ARWorldTrackingConfiguration.isSupported` checked before creating configuration
- [ ] ARSession configuration set before calling `session.run(config)` (or implicit in RealityView)
- [ ] `planeDetection` enabled if planes needed (horizontal, vertical, or both)
- [ ] Scene semantics enabled if required (person segmentation, motion capture, etc.)
- [ ] Camera usage description in Info.plist for camera permission
- [ ] AR content position uses correct coordinate system (world vs. relative)
- [ ] Entity transform modifications use `move(to:relativeTo:)` for clarity
- [ ] Tap/gesture handlers check raycast results are non-nil before use
- [ ] Session paused in `sceneWillResignActive()` (battery critical)
- [ ] Session resumed in `sceneDidBecomeActive()`
- [ ] No direct mutation of entity children during scene updates (use anchors)
- [ ] Texture/material loading handles errors (missing files, formats)
- [ ] RealityView uses SwiftUI-first pattern with `make` and `update` closures
- [ ] `SpatialTapGesture.targetedToAnyEntity()` used for tap interactions
- [ ] `DragGesture.targetedToAnyEntity()` used for drag interactions
- [ ] `SceneEvents.Update` subscription used for per-frame logic (not SwiftUI timers)
- [ ] Entity names set for lookup in update closure
- [ ] iOS vs visionOS differences acknowledged (RealityViewCameraContent on iOS)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

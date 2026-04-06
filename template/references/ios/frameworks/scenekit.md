# SceneKit Reference

> **When to read:** Dev reads when building 3D scenes or visualizations.
> **Note:** SceneKit is in maintenance mode post-WWDC 2025. Prefer RealityKit for new projects.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Scene Setup

```swift
import SceneKit

let sceneView = SCNView()
sceneView.scene = SCNScene()
sceneView.allowsCameraControl = true  // orbit, pan, zoom
sceneView.autoenablesDefaultLighting = true

// SwiftUI
struct SceneView3D: View {
  var body: some View {
    SceneView(scene: scene, options: [.allowsCameraControl, .autoenablesDefaultLighting])
  }
}
```

## Nodes and Geometry

```swift
// Box
let box = SCNBox(width: 1, height: 1, length: 1, chamferRadius: 0.05)
let boxNode = SCNNode(geometry: box)
boxNode.position = SCNVector3(0, 0, 0)
scene.rootNode.addChildNode(boxNode)

// Sphere
let sphere = SCNSphere(radius: 0.5)
let sphereNode = SCNNode(geometry: sphere)

// Built-in geometries: SCNBox, SCNSphere, SCNCylinder, SCNCone, SCNTorus, SCNPlane, SCNFloor, SCNText, SCNShape
```

## Materials

```swift
let material = SCNMaterial()
material.diffuse.contents = UIColor.blue          // base color
material.metalness.contents = 0.8                  // metallic look
material.roughness.contents = 0.2                  // surface smoothness
material.normal.contents = UIImage(named: "normal_map")  // surface detail
box.materials = [material]
```

## Lighting

```swift
let light = SCNLight()
light.type = .directional  // .omni, .spot, .ambient, .area
light.intensity = 1000
light.castsShadow = true

let lightNode = SCNNode()
lightNode.light = light
lightNode.eulerAngles = SCNVector3(-Float.pi / 4, 0, 0)
scene.rootNode.addChildNode(lightNode)
```

## Camera

```swift
let camera = SCNCamera()
camera.fieldOfView = 60
camera.zNear = 0.1
camera.zFar = 100

let cameraNode = SCNNode()
cameraNode.camera = camera
cameraNode.position = SCNVector3(0, 2, 5)
cameraNode.look(at: SCNVector3Zero)
scene.rootNode.addChildNode(cameraNode)
```

## Animation

```swift
// Basic animation
SCNTransaction.begin()
SCNTransaction.animationDuration = 1.0
boxNode.position = SCNVector3(2, 0, 0)
SCNTransaction.commit()

// Action-based (like SpriteKit)
let rotate = SCNAction.rotateBy(x: 0, y: .pi * 2, z: 0, duration: 2)
boxNode.runAction(.repeatForever(rotate))

// Core Animation
let animation = CABasicAnimation(keyPath: "eulerAngles.y")
animation.fromValue = 0
animation.toValue = Float.pi * 2
animation.duration = 3
animation.repeatCount = .infinity
boxNode.addAnimation(animation, forKey: "spin")
```

## Loading 3D Models

```swift
// From .scn or .usdz file
let scene = try SCNScene(url: modelURL)

// From .dae (Collada)
let scene = SCNScene(named: "model.dae")

// Access nodes
if let character = scene.rootNode.childNode(withName: "character", recursively: true) {
  // manipulate character node
}
```

## Common Mistakes
- ❌ Forgetting to add camera and light — scene renders black
- ❌ Using exact floating-point geometry dimensions for hit testing — use tolerance
- ❌ Modifying `transform` directly on physics-enabled nodes — use forces/impulses
- ❌ Too many dynamic lights (>4) — severe performance hit
- ❌ Starting new projects with SceneKit — use RealityKit instead (SceneKit is maintenance mode)

## Review Checklist
- [ ] Scene has camera and at least one light source
- [ ] Materials configured for target aesthetic (PBR or legacy)
- [ ] Physics bodies use simplified shapes (not exact mesh)
- [ ] 3D models loaded asynchronously for large files
- [ ] Memory profiled for complex scenes
- [ ] SceneKit deprecation considered — evaluate RealityKit migration path
- [ ] `allowsCameraControl` disabled in production if custom camera logic exists

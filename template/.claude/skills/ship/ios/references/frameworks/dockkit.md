# DockKit Reference

> **When to read:** Dev reads when building apps for motorized camera docks/gimbals.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Overview

DockKit controls motorized accessories (gimbals, docks) that physically track subjects. Uses ML-based subject detection and motor commands.

## Accessory Discovery

```swift
import DockKit

// Observe connected docks
for await event in try DockAccessoryManager.shared.accessoryStateChanges {
  switch event {
  case .dockAccessoryAdded(let accessory):
    currentDock = accessory
  case .dockAccessoryRemoved(let accessory):
    if accessory == currentDock { currentDock = nil }
  @unknown default: break
  }
}
```

## Tracking Modes

```swift
// System tracking — DockKit handles everything
try await dock.setSystemTrackingEnabled(true)

// Manual tracking — you control the target
let observation = DockObservation(
  identifier: subjectID,
  rect: boundingBox,     // normalized CGRect in camera coordinates
  type: .person
)
try await dock.track([observation], cameraInformation: cameraInfo)
```

## Motor Control

```swift
// Set motor speed
let velocity = DockMotion(
  rotationRate: simd_double3(x: 0, y: 0.5, z: 0)  // radians/sec
)
try await dock.setMotorVelocity(velocity)

// Move to specific angle
let target = DockMotion(
  orientation: simd_quatd(angle: .pi / 4, axis: simd_double3(0, 1, 0))
)
try await dock.setMotorPosition(target)
```

## Camera Integration

```swift
let cameraInfo = DockCameraInformation(
  captureDevice: captureDevice,
  cameraOrientation: .portrait,
  cameraPosition: .front
)
```

## Common Mistakes
- ❌ Not observing `accessoryStateChanges` — dock can disconnect at any time
- ❌ Sending motor commands without checking dock capabilities
- ❌ Ignoring camera orientation in tracking — causes inverted movement
- ❌ Not handling the case where system tracking overrides manual tracking

## Review Checklist
- [ ] Accessory connection/disconnection handled
- [ ] Tracking mode appropriate for use case (system vs manual)
- [ ] Motor commands within accessory's physical limits
- [ ] Camera information matches actual capture session
- [ ] Graceful degradation when no dock is connected

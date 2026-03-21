# Core Motion — iOS Reference

> **When to read:** Dev reads this when building features that track device motion, step counting, activity recognition, or use accelerometer/gyroscope/magnetometer data.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `CMMotionManager` | Central manager for device motion, accelerometer, gyroscope, magnetometer data |
| `CMDeviceMotion` | Structured object containing acceleration, rotation, magnetometer readings |
| `CMAccelerometerData` | Raw accelerometer values (x, y, z) |
| `CMGyroData` | Raw gyroscope rotation rates (x, y, z) |
| `CMMagnetometerData` | Magnetometer readings; requires heading calibration |
| `CMPedometer` | Step counting and distance/pace tracking; not tied to CMMotionManager |
| `CMMotionActivityManager` | Classifies user activity: walking, running, cycling, stationary, etc. |
| `CMAcceleration` | Acceleration struct (x, y, z) in G forces |
| `CMRotationRate` | Rotation struct (x, y, z) in rad/s |
| `CMMagneticField` | Magnetometer struct (x, y, z) in microTesla |

**Key Constants:**
- `CMMotionManager.deviceMotionUpdateInterval` — Set update rate (e.g., 0.1 for 100ms)
- `CMMotionManager.accelerometerUpdateInterval` — Separate interval for accelerometer-only
- `CMPedometer.isStepCountingAvailable` — Check hardware support before starting

---

## Code Examples

**Example 1: Start monitoring device motion**
```swift
import CoreMotion

let motionManager = CMMotionManager()

// Check availability and start updates
if motionManager.isDeviceMotionAvailable {
    motionManager.deviceMotionUpdateInterval = 0.1  // 100ms updates
    motionManager.startDeviceMotionUpdates(to: .main) { motion, error in
        guard let motion = motion else { return }

        let accel = motion.userAcceleration
        let attitude = motion.attitude

        print("Pitch: \(attitude.pitch), Roll: \(attitude.roll), Yaw: \(attitude.yaw)")
        print("Accel: (\(accel.x), \(accel.y), \(accel.z))")
    }
}
```

**Example 2: Pedometer for step counting**
```swift
import CoreMotion

let pedometer = CMPedometer()

if CMPedometer.isStepCountingAvailable {
    let startDate = Date().addingTimeInterval(-3600)  // Last hour
    pedometer.queryPedometerData(from: startDate, to: Date()) { data, error in
        if let data = data {
            print("Steps: \(data.numberOfSteps)")
            print("Distance: \(data.distance ?? 0) meters")
            print("Pace: \(data.pace ?? 0) sec/m")
        }
    }
}
```

**Example 3: Activity classification with CMMotionActivityManager**
```swift
import CoreMotion

let activityManager = CMMotionActivityManager()

activityManager.queryActivityStarting(from: Date().addingTimeInterval(-3600), to: Date()) { activities, error in
    activities?.forEach { activity in
        if activity.walking { print("User was walking") }
        if activity.running { print("User was running") }
        if activity.cycling { print("User was cycling") }
        if activity.stationary { print("User was stationary") }
    }
}
```

---

## Common Mistakes

**Mistake 1: Not checking availability before starting motion updates**
```swift
// ❌ WRONG: Crashes if device motion unavailable
motionManager.startDeviceMotionUpdates()

// ✅ CORRECT: Check first
if motionManager.isDeviceMotionAvailable {
    motionManager.startDeviceMotionUpdates()
}
```

**Mistake 2: Keeping CMMotionManager alive indefinitely**
```swift
// ❌ WRONG: Local variable deallocates, updates stop immediately
func setupMotion() {
    let manager = CMMotionManager()  // Lost after function returns
    manager.startDeviceMotionUpdates()
}

// ✅ CORRECT: Keep strong reference
class MotionViewModel: NSObject {
    let motionManager = CMMotionManager()
}
```

**Mistake 3: Not stopping updates when app enters background**
```swift
// ❌ WRONG: Drains battery continuously
// Updates continue even when app backgrounded

// ✅ CORRECT: Stop in viewWillDisappear or lifecycle
override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    motionManager.stopDeviceMotionUpdates()
}
```

**Mistake 4: Ignoring update interval in battery-critical apps**
```swift
// ❌ WRONG: Too frequent updates
motionManager.deviceMotionUpdateInterval = 0.01  // 10ms = high battery drain

// ✅ CORRECT: Balance accuracy vs. power
motionManager.deviceMotionUpdateInterval = 0.2  // 200ms for most use cases
```

**Mistake 5: Not requesting location permission for magnetometer accuracy**
```swift
// ❌ WRONG: Magnetometer is noisy without heading calibration
let motion = motionManager.deviceMotion
let magField = motion.magneticField  // Uncalibrated

// ✅ CORRECT: Use heading calibration or request location permission
let heading = motionManager.deviceMotion.heading
```

---

## Review Checklist

- [ ] `CMMotionManager` instance is stored as a property (not local variable)
- [ ] Availability check performed before starting any updates (`isDeviceMotionAvailable`, `isAccelerometerAvailable`, etc.)
- [ ] Update interval set appropriately for use case (0.05–0.5s typical range)
- [ ] `stopDeviceMotionUpdates()` called in `viewWillDisappear()` or appropriate lifecycle method
- [ ] Pedometer queries use time ranges; no infinite polling via `startPedometerUpdates()`
- [ ] Activity manager queries run on background thread to avoid blocking UI
- [ ] Error handling in completion blocks (check `error` parameter)
- [ ] CMMotionActivityManager requires Info.plist key: `NSMotionUsageDescription`
- [ ] Test on device (simulator motion data is limited/artificial)
- [ ] Memory: ensure strong reference to motion manager or updates will stop
- [ ] Battery impact measured: excessive update intervals can drain 5–15% per hour
- [ ] No logging raw sensor data at high frequency in production (use periodic sampling)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

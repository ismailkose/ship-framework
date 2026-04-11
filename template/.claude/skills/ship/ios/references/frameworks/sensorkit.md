# SensorKit Reference

> **When to read:** Dev reads when building research apps that collect sensor data.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Overview

SensorKit provides research-grade sensor data collection (ambient light, accelerometer, keyboard usage, phone usage, etc.). Requires Apple Research approval.

## Authorization

```swift
import SensorKit

let reader = SRSensorReader(sensor: .ambientLightSensor)

reader.requestAuthorization { error in
  if let error {
    print("Authorization failed: \(error)")
  }
}
```

## Available Sensors

- `.ambientLightSensor` — lux levels
- `.accelerometer` — motion data
- `.rotationRate` — gyroscope
- `.keyboardMetrics` — typing patterns (aggregated, privacy-preserving)
- `.phoneUsageReport` — screen time, app usage
- `.messagesUsageReport` — messaging patterns
- `.mediaEvents` — music/podcast listening
- `.wristDetection` — Apple Watch wear state

## Data Collection

```swift
let reader = SRSensorReader(sensor: .ambientLightSensor)
reader.delegate = self

let request = SRFetchRequest()
request.from = SRAbsoluteTime(Date().addingTimeInterval(-86400))  // last 24h
request.to = SRAbsoluteTime(Date())
reader.fetch(request)

// Delegate
extension SensorManager: SRSensorReaderDelegate {
  func sensorReader(_ reader: SRSensorReader, didFetch devices: [SRDevice]) {
    for device in devices {
      // Process sensor data
    }
  }
}
```

## Common Mistakes
- ❌ Expecting immediate data — sensor data has a recording delay
- ❌ Not handling authorization denial — provide clear explanation
- ❌ Requesting too many sensors — each requires separate authorization

## Review Checklist
- [ ] Apple Research approval obtained
- [ ] Each sensor authorized individually
- [ ] Data fetch time ranges are reasonable
- [ ] Delegate handles empty results gracefully
- [ ] User informed about what data is collected

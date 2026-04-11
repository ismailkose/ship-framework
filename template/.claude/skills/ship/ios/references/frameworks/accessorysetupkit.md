# AccessorySetupKit Reference

> **When to read:** Dev reads when building Bluetooth/Wi-Fi accessory discovery.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Overview

AccessorySetupKit replaces manual Bluetooth/Wi-Fi pairing with a privacy-preserving system picker (iOS 18+). Users select accessories from a system UI — no location permission needed.

## Setup

```swift
import AccessorySetupKit

let session = ASAccessorySession()

// Define what to discover
let descriptor = ASDiscoveryDescriptor()
descriptor.bluetoothServiceUUID = CBUUID(string: "YOUR-SERVICE-UUID")
// Or Wi-Fi:
// descriptor.ssidPrefix = "MyDevice"
```

## Discovery

```swift
// Show system picker
session.activate(on: DispatchQueue.main, eventHandler: handleEvent)

func showPicker() {
  session.showPicker(for: [descriptor]) { error in
    if let error {
      print("Picker failed: \(error)")
    }
  }
}

func handleEvent(_ event: ASAccessoryEvent) {
  switch event.eventType {
  case .activated:
    // Session ready
  case .accessoryAdded:
    if let accessory = event.accessory {
      // User selected this accessory — now connect via CoreBluetooth/Network framework
      connectToAccessory(accessory)
    }
  case .accessoryRemoved:
    // User removed accessory from settings
  case .accessoryChanged:
    // Accessory properties updated
  @unknown default: break
  }
}
```

## Common Mistakes
- ❌ Using CoreBluetooth scanning directly when AccessorySetupKit is available — use the system picker
- ❌ Not handling `.accessoryRemoved` events — user can unpair from Settings
- ❌ Forgetting to activate the session before showing the picker

## Review Checklist
- [ ] Session activated before picker is shown
- [ ] All event types handled (added, removed, changed)
- [ ] Graceful fallback for iOS < 18
- [ ] Bluetooth/Wi-Fi descriptor matches actual accessory advertisement

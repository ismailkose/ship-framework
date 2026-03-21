# HomeKit — iOS Reference

> **When to read:** Dev reads this when building smart home control, configuring accessories/rooms, handling Matter support, or managing home automation.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `HMHomeManager` | Central manager for homes and accessories |
| `HMHome` | Container for rooms, zones, accessories, scenes, automation |
| `HMAccessory` | Physical smart home device (light, door lock, thermostat) |
| `HMService` | Capability of accessory (brightness, lock status, temperature) |
| `HMCharacteristic` | Actual property/value of service (on/off, 0–100%, etc.) |
| `HMRoom` | Logical grouping of accessories (e.g., living room) |
| `HMZone` | Collection of rooms (e.g., downstairs) |
| `HMScene` | Predefined set of characteristic values (e.g., "movie time") |
| `HMServiceGroup` | Groups related services across accessories |
| `HMUserActivity` | Siri intent for automation/voice control |
| `HMMatterSupport` | Matter protocol interoperability (iOS 18+) |

**Common Service Types:**
- `HMServiceTypeLightbulb` — Light with on/off and brightness
- `HMServiceTypeOutlet` — Smart plug with on/off
- `HMServiceTypeLock` — Smart lock with lock/unlock
- `HMServiceTypeThermostat` — Climate control
- `HMServiceTypeTemperatureSensor` — Temperature reading

---

## Code Examples

**Example 1: List all homes, rooms, and accessories**
```swift
import HomeKit

class HomeKitManager: NSObject, HMHomeManagerDelegate {
    let homeManager = HMHomeManager()

    override init() {
        super.init()
        homeManager.delegate = self
    }

    func listAllAccessories() {
        guard let homes = homeManager.homes else {
            print("HomeKit not accessible")
            return
        }

        for home in homes {
            print("Home: \(home.name)")

            // List rooms
            for room in home.rooms {
                print("  Room: \(room.name)")

                // List accessories in room
                for accessory in room.accessories {
                    print("    Accessory: \(accessory.name ?? "Unknown")")
                    print("      Manufacturer: \(accessory.manufacturer ?? "Unknown")")

                    // List services
                    for service in accessory.services {
                        print("      Service: \(service.serviceType)")

                        // List characteristics
                        for characteristic in service.characteristics {
                            print("        \(characteristic.localizedName ?? "Unknown"): \(characteristic.value ?? "N/A")")
                        }
                    }
                }
            }

            // List zones
            for zone in home.zones {
                print("  Zone: \(zone.name)")
                for room in zone.rooms {
                    print("    - \(room.name)")
                }
            }
        }
    }

    // MARK: - HMHomeManagerDelegate

    func homeManagerDidUpdateHomes(_ manager: HMHomeManager) {
        print("Homes updated")
        listAllAccessories()
    }
}
```

**Example 2: Control an accessory (turn light on/off)**
```swift
import HomeKit

func controlLightbulb(_ accessory: HMAccessory, on: Bool) {
    // Find lightbulb service
    guard let service = accessory.services.first(where: { $0.serviceType == HMServiceTypeLightbulb }) else {
        print("No lightbulb service found")
        return
    }

    // Find power characteristic
    guard let powerCharacteristic = service.characteristics.first(where: {
        $0.characteristicType == HMCharacteristicTypePowerState
    }) else {
        print("No power characteristic found")
        return
    }

    // Write new value
    powerCharacteristic.writeValue(on) { error in
        if let error = error {
            print("Control failed: \(error)")
        } else {
            print("Light turned \(on ? "on" : "off")")
        }
    }
}

func adjustBrightness(_ accessory: HMAccessory, percentage: Int) {
    guard let service = accessory.services.first(where: { $0.serviceType == HMServiceTypeLightbulb }) else { return }
    guard let brightCharacteristic = service.characteristics.first(where: {
        $0.characteristicType == HMCharacteristicTypeBrightness
    }) else { return }

    brightCharacteristic.writeValue(percentage) { error in
        if error == nil {
            print("Brightness set to \(percentage)%")
        }
    }
}
```

**Example 3: Execute scene and handle Matter accessories**
```swift
import HomeKit

func activateScene(_ scene: HMScene) {
    scene.execute { error in
        if let error = error {
            print("Scene activation failed: \(error)")
        } else {
            print("Scene '\(scene.name)' activated")
        }
    }
}

// iOS 18+: Check Matter support
func checkMatterSupport(_ home: HMHome) {
    if #available(iOS 18, *) {
        let matterAccessories = home.accessories.filter { accessory in
            accessory.isMatterDevice
        }

        print("Matter accessories in home: \(matterAccessories.count)")

        for accessory in matterAccessories {
            print("Matter device: \(accessory.name ?? "Unknown")")
            // Matter devices have unified homekit/Matter interface
        }
    }
}

// Create/manage scene
func createMovieTimeScene(_ home: HMHome) {
    let scene = HMScene(home: home)
    scene.name = "Movie Time"

    // Dim lights
    for accessory in home.accessories {
        guard let service = accessory.services.first(where: { $0.serviceType == HMServiceTypeLightbulb }) else { continue }
        guard let brightCharacteristic = service.characteristics.first(where: {
            $0.characteristicType == HMCharacteristicTypeBrightness
        }) else { continue }

        // Add to scene: 20% brightness
        scene.addCharacteristicAction(HMCharacteristicWriteAction(
            characteristic: brightCharacteristic,
            targetValue: 20
        ))
    }

    // Save scene
    home.addScene(scene) { error in
        if error == nil {
            print("Scene created: Movie Time")
        }
    }
}
```

---

## Common Mistakes

**Mistake 1: Not checking homeManager availability**
```swift
// ❌ WRONG: homes could be nil while HomeKit is syncing
let homes = homeManager.homes!  // Force unwrap crashes

// ✅ CORRECT: Optional binding
guard let homes = homeManager.homes else {
    print("HomeKit not yet available")
    return
}
```

**Mistake 2: Blocking UI with characteristic reads**
```swift
// ❌ WRONG: Main thread block
let value = characteristic.value  // Synchronous, but may take time to read

// ✅ CORRECT: Use async write/read
characteristic.readValue { error in
    if let value = characteristic.value {
        DispatchQueue.main.async {
            self.updateUI(value)
        }
    }
}
```

**Mistake 3: Not verifying characteristic type before reading**
```swift
// ❌ WRONG: Crashes if service doesn't have expected characteristic
let brightness = service.characteristics[0].value as! Int

// ✅ CORRECT: Find and verify type
guard let brightCharacteristic = service.characteristics.first(where: {
    $0.characteristicType == HMCharacteristicTypeBrightness
}) else {
    print("Brightness not available")
    return
}
let brightness = brightCharacteristic.value as? Int ?? 0
```

**Mistake 4: Not handling "Home Not Invited" scenario**
```swift
// ❌ WRONG: App crashes if user removed from home
let home = homeManager.homes?.first!

// ✅ CORRECT: Gracefully handle no homes
guard let home = homeManager.homes?.first else {
    print("Not invited to any homes")
    showSetupUI()
    return
}
```

**Mistake 5: Modifying characteristic without permission check**
```swift
// ❌ WRONG: User may not have write permission
characteristic.writeValue(true) { error in
    print("Changed")
}

// ✅ CORRECT: Check permission metadata
if characteristic.metadata?.writableWhenNotificationEnabled == false {
    print("Characteristic is read-only")
}
```

---

## Review Checklist

- [ ] `HMHomeManager` delegate set in `init()`
- [ ] `homeManager.homes` optional check before access
- [ ] `homeManagerDidUpdateHomes(_:)` implemented to refresh UI
- [ ] Characteristic reads wrapped in error handlers
- [ ] Characteristic writes wrapped in error handlers
- [ ] `characteristic.writeValue()` used instead of direct assignment
- [ ] Service type verified before accessing characteristics
- [ ] Characteristic type verified using `characteristicType` enum
- [ ] Scene execution wrapped in error handler
- [ ] Room/zone hierarchy understood (room -> zone -> home)
- [ ] HomeKit permission in Info.plist: `NSHomeKitUsageDescription`
- [ ] Matter device support checked with `#available(iOS 18, *)` if app targets iOS 18+
- [ ] UI updates run on main thread (from background completion handlers)
- [ ] Automatic reconnection handled via delegate (no manual retry loops)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

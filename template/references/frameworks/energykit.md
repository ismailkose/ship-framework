# EnergyKit — iOS Reference

> **When to read:** Dev reads this when monitoring home energy usage, building smart energy dashboards, or integrating with grid services (iOS 18+).

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `EnergyManager` | Central manager for accessing energy data and services |
| `HomeEnergyStatus` | Current home energy usage and solar production |
| `Device` | Connected smart device with energy consumption data |
| `EnergyEvent` | Time-stamped energy or device event |
| `EnergyDeviceCategory` | Enum: water heater, HVAC, EV charger, battery, etc. |
| `HomeEnergyManager` | Monitors whole-home energy and environmental data |
| `GridInteraction` | Time-of-use rates, demand response, grid signals |

**Key Properties:**
- `HomeEnergyStatus.devices` — Array of connected devices
- `Device.powerWatts` — Current power consumption (watts)
- `Device.category` — Device type (e.g., `.evCharger`, `.waterHeater`)
- `HomeEnergyStatus.timeOfUseRate` — Current grid rate or `nil` if unavailable

---

## Code Examples

**Example 1: Monitor whole-home energy usage**
```swift
import EnergyKit

class EnergyDashboard {
    let energyManager = EnergyManager()

    func monitorHomeEnergy() {
        Task {
            do {
                // Get current home energy status
                let status = try await energyManager.homeEnergyStatus()

                print("Total power: \(status.powerWatts) W")
                print("Solar production: \(status.solarPowerWatts) W")
                print("Battery: \(status.batteryPercentageRemaining) %")

                // List all devices
                for device in status.devices {
                    print("Device: \(device.name ?? "Unknown")")
                    print("  Power: \(device.powerWatts) W")
                    print("  Category: \(device.category)")
                }

                // Subscribe to updates
                for await update in energyManager.homeEnergyStatusUpdates() {
                    print("Energy update: \(update.powerWatts) W")
                    updateUI(with: update)
                }
            } catch {
                print("Energy data unavailable: \(error)")
            }
        }
    }

    func updateUI(with status: HomeEnergyStatus) {
        // Update dashboard UI
    }
}
```

**Example 2: Track device-level consumption**
```swift
import EnergyKit

func monitorDeviceConsumption() {
    Task {
        do {
            let energyManager = EnergyManager()
            let status = try await energyManager.homeEnergyStatus()

            // Find EV charger
            if let evCharger = status.devices.first(where: { $0.category == .evCharger }) {
                print("EV Charger consuming: \(evCharger.powerWatts) W")

                // Query historical data
                let history = try await evCharger.energyHistory(
                    from: Date().addingTimeInterval(-3600),  // Last hour
                    to: Date()
                )

                var totalEnergy = 0.0
                for event in history {
                    totalEnergy += event.energyWattHours
                }
                print("EV charger used: \(totalEnergy / 1000) kWh")
            }
        } catch {
            print("Device monitoring failed: \(error)")
        }
    }
}
```

**Example 3: Respond to grid signals and time-of-use rates**
```swift
import EnergyKit

class GridAwareEnergyController {
    let energyManager = EnergyManager()

    func respondToGridEvents() {
        Task {
            do {
                let status = try await energyManager.homeEnergyStatus()

                // Check time-of-use rate
                if let rate = status.timeOfUseRate {
                    print("Current rate: \(rate.ratePerKilowattHour) $/kWh")

                    // Shift load if rate is high
                    if rate.ratePerKilowattHour > 0.25 {
                        defer_non_critical_loads()
                    }
                }

                // Monitor grid interaction events
                for await gridEvent in energyManager.gridInteractionUpdates() {
                    print("Grid event: \(gridEvent.type)")
                    // gridEvent.type: demand response, price signal, outage, etc.
                    handle_grid_event(gridEvent)
                }
            } catch {
                print("Grid monitoring failed: \(error)")
            }
        }
    }

    func defer_non_critical_loads() {
        // Delay EV charging, water heating, pool pump, etc.
        print("Deferring non-critical loads due to high rate")
    }

    func handle_grid_event(_ event: GridInteraction) {
        // Respond to demand response, price signals, etc.
    }
}
```

---

## Common Mistakes

**Mistake 1: Not checking availability on iOS versions < 18**
```swift
// ❌ WRONG: Crashes on iOS 17 and earlier
let energyManager = EnergyManager()
let status = await energyManager.homeEnergyStatus()

// ✅ CORRECT: Check OS availability
if #available(iOS 18, *) {
    let energyManager = EnergyManager()
    let status = try await energyManager.homeEnergyStatus()
}
```

**Mistake 2: Blocking UI with synchronous energy queries**
```swift
// ❌ WRONG: Main thread blocked
let status = try await energyManager.homeEnergyStatus()  // On main thread!
print(status.powerWatts)

// ✅ CORRECT: Fetch on background thread
Task {
    let status = try await energyManager.homeEnergyStatus()
    DispatchQueue.main.async {
        updateUI(status)
    }
}
```

**Mistake 3: Not handling permission errors**
```swift
// ❌ WRONG: User denied HomeKit access, error not handled
let status = try! energyManager.homeEnergyStatus()

// ✅ CORRECT: Handle permission errors
do {
    let status = try await energyManager.homeEnergyStatus()
} catch {
    if error.code == NSError.HKErrorDomain {
        print("HomeKit access denied")
        // Prompt user to grant permission in Settings
    }
}
```

**Mistake 4: Over-querying energy data (performance drain)**
```swift
// ❌ WRONG: Query energy every 100ms
for i in 0..<1000 {
    let status = try await energyManager.homeEnergyStatus()
    print(status.powerWatts)
}

// ✅ CORRECT: Use async stream updates
for await status in energyManager.homeEnergyStatusUpdates() {
    print(status.powerWatts)
    // Receives updates at reasonable intervals
}
```

**Mistake 5: Not respecting HomeKit/Home app configuration**
```swift
// ❌ WRONG: Assuming devices exist without HomeKit setup
let devices = status.devices  // May be empty if HomeKit not configured

// ✅ CORRECT: Handle empty device list gracefully
if status.devices.isEmpty {
    print("No devices configured in Home app")
    // Show onboarding or prompt
} else {
    for device in status.devices {
        // Process device
    }
}
```

---

## Review Checklist

- [ ] iOS 18+ availability check before using EnergyKit (`#available(iOS 18, *)`)
- [ ] HomeKit framework linked in project (dependency of EnergyKit)
- [ ] User has enabled HomeKit in Home app (graceful fallback if not)
- [ ] HomeKit permission granted via Info.plist: `NSHomeKitUsageDescription`
- [ ] Energy queries run on background thread (not main thread)
- [ ] Error handling for permission denied (NSError.HKErrorDomain)
- [ ] Async/await used for all energy operations (not deprecated block APIs)
- [ ] Energy updates subscribed via `homeEnergyStatusUpdates()` stream (not polling)
- [ ] Device history queries specify time range (from/to parameters)
- [ ] Grid interaction events handled if app supports demand response
- [ ] Time-of-use rates checked before deferring loads
- [ ] Device categories validated before calling category-specific methods

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

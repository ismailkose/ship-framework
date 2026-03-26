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
| `ElectricityGuidance` | Forecast data with weighted time intervals |
| `ElectricityGuidance.Service` | Interface for obtaining guidance data |
| `ElectricityGuidance.Query` | Query specifying `.shift` or `.reduce` action |
| `ElectricityGuidance.Value` | Time interval with rating (0.0-1.0) |
| `EnergyVenue` | Physical location registered for energy management |
| `ElectricVehicleLoadEvent` | Load event for EV charger telemetry |
| `ElectricHVACLoadEvent` | Load event for HVAC system telemetry |
| `ElectricalMeasurement` | Power and energy measurement data |
| `ElectricityInsightService` | Service for querying energy/runtime insights |
| `ElectricityInsightQuery` | Query for historical insight data |
| `ElectricityInsightRecord` | Historical energy data by cleanliness/tariff |
| `EnergyKitError` | Error enum with unsupportedRegion, guidanceUnavailable, etc. |

**Key Properties:**
- `HomeEnergyStatus.devices` — Array of connected devices
- `Device.powerWatts` — Current power consumption (watts)
- `Device.category` — Device type (e.g., `.evCharger`, `.waterHeater`)
- `HomeEnergyStatus.timeOfUseRate` — Current grid rate or `nil` if unavailable

---

## Code Examples

**Example 1: Query electricity guidance with shift/reduce actions**
```swift
import EnergyKit

func observeGuidance(venueID: UUID) async throws {
    let query = ElectricityGuidance.Query(suggestedAction: .shift)
    let service = ElectricityGuidance.sharedService

    let guidanceStream = service.guidance(using: query, at: venueID)

    for try await guidance in guidanceStream {
        print("Guidance token: \(guidance.guidanceToken)")
        print("Interval: \(guidance.interval)")
        print("Venue: \(guidance.energyVenueID)")

        // Check guidance options
        if guidance.options.contains(.guidanceIncorporatesRatePlan) {
            print("Rate plan data incorporated")
        }
        if guidance.options.contains(.locationHasRatePlan) {
            print("Location has a rate plan")
        }

        processGuidanceValues(guidance.values)
    }
}
```

**Example 1b: Legacy home energy monitoring**
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

**Example 2: Working with guidance values and electricity measurements**
```swift
import EnergyKit

func processGuidanceValues(_ values: [ElectricityGuidance.Value]) {
    for value in values {
        let interval = value.interval
        let rating = value.rating  // 0.0 (best) to 1.0 (worst)

        print("From \(interval.start) to \(interval.end): rating \(rating)")
    }
}

// Find the best time to charge
func bestChargingWindow(
    in values: [ElectricityGuidance.Value]
) -> ElectricityGuidance.Value? {
    values.min(by: { $0.rating < $1.rating })
}

// Submit EV charging load event with ElectricalMeasurement
func submitEVChargingEvent(
    at venue: EnergyVenue,
    guidanceToken: UUID,
    deviceID: String
) async throws {
    let session = ElectricVehicleLoadEvent.Session(
        id: UUID(),
        state: .begin,
        guidanceState: ElectricVehicleLoadEvent.Session.GuidanceState(
            wasFollowingGuidance: true,
            guidanceToken: guidanceToken
        )
    )

    let measurement = ElectricVehicleLoadEvent.ElectricalMeasurement(
        stateOfCharge: 45,
        direction: .imported,
        power: Measurement(value: 7.2, unit: .kilowatts),
        energy: Measurement(value: 0, unit: .kilowattHours)
    )

    let event = ElectricVehicleLoadEvent(
        timestamp: Date(),
        measurement: measurement,
        session: session,
        deviceID: deviceID
    )

    try await venue.submitEvents([event])
}
```

**Example 2b: Track device-level consumption (legacy)**
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

**Example 3: Query electricity insights with granularity**
```swift
import EnergyKit

func queryEnergyInsights(deviceID: String, venueID: UUID) async throws {
    let query = ElectricityInsightQuery(
        options: [.cleanliness, .tariff],
        range: DateInterval(
            start: Calendar.current.date(byAdding: .day, value: -7, to: Date())!,
            end: Date()
        ),
        granularity: .daily,
        flowDirection: .imported
    )

    let service = ElectricityInsightService.shared
    let stream = try await service.energyInsights(
        forDeviceID: deviceID, using: query, atVenue: venueID
    )

    for await record in stream {
        if let total = record.totalEnergy { print("Total: \(total)") }
        if let cleaner = record.dataByGridCleanliness?.cleaner {
            print("Cleaner: \(cleaner)")
        }
    }
}

// For runtime data instead of energy
func queryRuntimeInsights(deviceID: String, venueID: UUID) async throws {
    let query = ElectricityInsightQuery(
        options: [.cleanliness],
        range: DateInterval(start: Date().addingTimeInterval(-86400), end: Date()),
        granularity: .hourly,
        flowDirection: .imported
    )

    let service = ElectricityInsightService.shared
    let stream = try await service.runtimeInsights(
        forDeviceID: deviceID, using: query, atVenue: venueID
    )

    for await record in stream {
        print("Runtime record: \(record)")
    }
}
```

**Example 3b: Legacy grid signal monitoring**
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

**Mistake 3: Not handling EnergyKitError cases**
```swift
// ❌ WRONG: Assume guidance always available
for try await guidance in service.guidance(using: query, at: venueID) {
    updateUI(guidance)
}

// ✅ CORRECT: Handle region-specific errors
do {
    for try await guidance in service.guidance(using: query, at: venueID) {
        updateUI(guidance)
    }
} catch let error as EnergyKitError {
    switch error {
    case .unsupportedRegion:
        showUnsupportedRegionMessage()
    case .guidanceUnavailable:
        showGuidanceUnavailableMessage()
    case .venueUnavailable:
        showNoVenueMessage()
    case .permissionDenied:
        showPermissionDeniedMessage()
    case .serviceUnavailable:
        retryLater()
    case .rateLimitExceeded:
        backOff()
    default:
        break
    }
}
```

**Mistake 4: Discarding the guidance token**
```swift
// ❌ WRONG: Ignore the guidance token
for try await guidance in guidanceStream {
    startCharging()
}

// ✅ CORRECT: Store the token for load events
for try await guidance in guidanceStream {
    let token = guidance.guidanceToken
    startCharging(followingGuidanceToken: token)
}
```

**Mistake 5: Submitting load events without session lifecycle**
```swift
// ❌ WRONG: Only submit one event
let event = ElectricVehicleLoadEvent(/* state: .active */)
try await venue.submitEvents([event])

// ✅ CORRECT: Full session lifecycle (.begin -> .active -> .end)
try await venue.submitEvents([beginEvent])
// ... periodic active events ...
try await venue.submitEvents([activeEvent])
// ... when done ...
try await venue.submitEvents([endEvent])
```

**Mistake 6: Querying guidance without a venue**
```swift
// ❌ WRONG: Use a hardcoded UUID
let fakeID = UUID()
service.guidance(using: query, at: fakeID)  // Will fail

// ✅ CORRECT: Discover venues first
let venues = try await EnergyVenue.venues()
guard let venue = venues.first else {
    showNoVenueSetup()
    return
}
let guidanceStream = service.guidance(using: query, at: venue.id)
```

---

## Review Checklist

- [ ] `com.apple.developer.energykit` entitlement added to the project
- [ ] `EnergyKitError.unsupportedRegion` handled with user-facing message
- [ ] `EnergyKitError.permissionDenied` handled gracefully
- [ ] `ElectricityGuidance.Query` specifies `.shift` or `.reduce` action appropriately
- [ ] Guidance options checked for `.guidanceIncorporatesRatePlan` and `.locationHasRatePlan`
- [ ] Venues discovered via `EnergyVenue.venues()` before querying guidance
- [ ] Guidance token stored and passed to load event submissions
- [ ] Load event sessions follow `.begin` -> `.active` -> `.end` lifecycle
- [ ] `ElectricalMeasurement` populated with power/energy values for load events
- [ ] `ElectricityInsightQuery` uses appropriate granularity for time range (.hourly, .daily, etc.)
- [ ] `ElectricityInsightRecord` parsed for cleanliness/tariff data
- [ ] Rate limiting handled via `EnergyKitError.rateLimitExceeded`
- [ ] Service unavailability handled with retry logic
- [ ] iOS 18+ availability check before using EnergyKit (`#available(iOS 18, *)`)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

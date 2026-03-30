# HealthKit — iOS Reference

> **When to read:** Dev reads this when reading/writing health data, requesting permissions, or syncing workout data.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `HKHealthStore` | Central data access | Singleton; checks availability with `isHealthDataAvailable()` |
| `HKObjectType` | Type of health data | `.workoutType()`, `.quantityType()`, `.categoryType()` |
| `HKSampleQueryDescriptor` | Async/await query for samples (modern) | Preferred over `HKSampleQuery`; use `.result(for:)` for one-shot or `.results(for:)` for AsyncSequence |
| `HKStatisticsQueryDescriptor` | Async/await aggregation (modern) | Preferred over `HKStatisticsQuery`; sum, average, min, max |
| `HKStatisticsCollectionQueryDescriptor` | Time-series data grouped into intervals | Ideal for charts; `.results(for:)` for streaming updates |
| `HKSampleQuery` | Callback-based sample fetch (legacy) | Older; prefer descriptors |
| `HKStatisticsQuery` | Callback-based aggregation (legacy) | Older; prefer descriptors |
| `HKWorkoutSession` | Track active workout | Built-in pause/resume/end; iOS 17+ |
| `HKLiveWorkoutBuilder` | Stream samples during session | Preferred over `HKWorkoutBuilder` for live tracking |
| `HKWorkoutBuilder` | Construct workout (legacy) | Older; prefer `HKLiveWorkoutBuilder` |
| `HKWorkoutRoute` | GPS path data | Attached to workout |
| `HKUpdateFrequency` | Background sync rate | `.immediate`, `.hourly`, `.daily`, `.weekly` |
| `HKQuantityType(.shorthand)` | Shorthand constructor | `HKQuantityType(.stepCount)` instead of `HKQuantityType.quantityType(forIdentifier:)` |

## Code Examples

```swift
// 1. Request HealthKit authorization
import HealthKit

func requestHealthKitPermissions() {
    guard HKHealthStore.isHealthDataAvailable() else {
        print("HealthKit not available on this device")
        return
    }

    let store = HKHealthStore()
    let typesToRead: Set<HKObjectType> = [
        .workoutType(),
        HKQuantityType.quantityType(
            forIdentifier: .stepCount
        )!,
        HKQuantityType.quantityType(
            forIdentifier: .heartRate
        )!
    ]
    let typesToWrite: Set<HKSampleType> = [
        .workoutType(),
        HKQuantityType.quantityType(
            forIdentifier: .activeEnergyBurned
        )!
    ]

    store.requestAuthorization(
        toShare: typesToWrite,
        read: typesToRead
    ) { success, error in
        if success {
            print("HealthKit authorization granted")
        } else if let error = error {
            print("Authorization failed: \(error.localizedDescription)")
        }
    }
}

// 2. Query step count for past week
func queryStepCount(completion: @escaping (Double) -> Void) {
    let store = HKHealthStore()
    let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount)!

    let calendar = Calendar.current
    let endDate = Date()
    let startDate = calendar.date(byAdding: .day, value: -7, to: endDate)!

    let predicate = HKQuery.predicateForSamples(
        withStart: startDate,
        end: endDate,
        options: .strictStartDate
    )

    let query = HKStatisticsQuery(
        quantityType: stepType,
        quantitySamplePredicate: predicate,
        options: .cumulativeSum
    ) { _, result, error in
        guard let result = result, error == nil else {
            print("Query error: \(error?.localizedDescription ?? "")")
            return
        }
        let steps = result.sumQuantity()?.doubleValue(for: HKUnit.count()) ?? 0
        DispatchQueue.main.async {
            completion(steps)
        }
    }
    store.execute(query)
}

// 3. Record a workout session
func startWorkout() async {
    let store = HKHealthStore()
    let workoutType = HKWorkoutType.workoutType()

    let config = HKWorkoutConfiguration()
    config.activityType = .running
    config.locationType = .outdoor

    do {
        let session = try HKWorkoutSession(healthStore: store, configuration: config)
        let builder = HKWorkoutBuilder(healthStore: store, configuration: config, device: .local())

        session.delegate = self
        builder.delegate = self

        try session.startActivity(with: Date())
        try await builder.beginCollection(at: Date())

        // Collect samples during workout
        let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate)!
        let heartRateSample = HKQuantitySample(
            type: heartRateType,
            quantity: HKQuantity(unit: HKUnit(from: "count/min"), doubleValue: 120),
            start: Date(),
            end: Date()
        )
        try await builder.addSample(heartRateSample)

        // End workout
        session.end()
        let workout = try await builder.finishWorkout()
        print("Workout saved: \(workout.totalEnergy ?? HKQuantity(unit: .kilocalorie(), doubleValue: 0))")
    } catch {
        print("Workout error: \(error.localizedDescription)")
    }
}

// 4. Query recent workouts
func queryWorkouts(completion: @escaping ([HKWorkout]) -> Void) {
    let store = HKHealthStore()
    let workoutType = HKWorkoutType.workoutType()

    let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)
    let query = HKSampleQuery(
        sampleType: workoutType,
        predicate: nil,
        limit: 10,
        sortDescriptors: [sortDescriptor]
    ) { _, samples, error in
        let workouts = samples as? [HKWorkout] ?? []
        DispatchQueue.main.async {
            completion(workouts)
        }
    }
    store.execute(query)
}

// 5. Set up background delivery for heart rate
func setupBackgroundHeartRateNotification() {
    let store = HKHealthStore()
    let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate)!

    store.enableBackgroundDelivery(
        for: heartRateType,
        frequency: .immediate
    ) { success, error in
        if success {
            print("Background delivery enabled")
        } else if let error = error {
            print("Background delivery failed: \(error.localizedDescription)")
        }
    }
}
```

### Modern Async/Await API Examples

```swift
// Query with HKSampleQueryDescriptor (async/await)
func fetchRecentHeartRates() async throws -> [HKQuantitySample] {
    let store = HKHealthStore()
    let heartRateType = HKQuantityType(.heartRate)

    let descriptor = HKSampleQueryDescriptor(
        predicates: [.quantitySample(type: heartRateType)],
        sortDescriptors: [SortDescriptor(\.endDate, order: .reverse)],
        limit: 20
    )

    return try await descriptor.result(for: store)
}

// Statistics query for aggregated data
func fetchTodayStepCount() async throws -> Double {
    let store = HKHealthStore()
    let calendar = Calendar.current
    let startOfDay = calendar.startOfDay(for: Date())
    let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!

    let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: endOfDay)
    let stepType = HKQuantityType(.stepCount)
    let samplePredicate = HKSamplePredicate.quantitySample(type: stepType, predicate: predicate)

    let query = HKStatisticsQueryDescriptor(
        predicate: samplePredicate,
        options: .cumulativeSum
    )

    let result = try await query.result(for: store)
    return result?.sumQuantity()?.doubleValue(for: .count()) ?? 0
}

// Time-series data for charts
func fetchDailySteps(forLast days: Int) async throws -> [(date: Date, steps: Double)] {
    let store = HKHealthStore()
    let calendar = Calendar.current
    let endDate = calendar.startOfDay(for: calendar.date(byAdding: .day, value: 1, to: Date())!)
    let startDate = calendar.date(byAdding: .day, value: -days, to: endDate)!

    let predicate = HKQuery.predicateForSamples(withStart: startDate, end: endDate)
    let stepType = HKQuantityType(.stepCount)
    let samplePredicate = HKSamplePredicate.quantitySample(type: stepType, predicate: predicate)

    let query = HKStatisticsCollectionQueryDescriptor(
        predicate: samplePredicate,
        options: .cumulativeSum,
        anchorDate: endDate,
        intervalComponents: DateComponents(day: 1)
    )

    let collection = try await query.result(for: store)
    var dailySteps: [(date: Date, steps: Double)] = []

    collection.statisticsCollection.enumerateStatistics(from: startDate, to: endDate) { statistics, _ in
        let steps = statistics.sumQuantity()?.doubleValue(for: .count()) ?? 0
        dailySteps.append((date: statistics.startDate, steps: steps))
    }
    return dailySteps
}

// AsyncSequence for streaming updates
func streamCollectionUpdates() async throws {
    let store = HKHealthStore()
    let calendar = Calendar.current
    let endDate = calendar.startOfDay(for: calendar.date(byAdding: .day, value: 1, to: Date())!)
    let startDate = calendar.date(byAdding: .day, value: -7, to: endDate)!

    let predicate = HKQuery.predicateForSamples(withStart: startDate, end: endDate)
    let stepType = HKQuantityType(.stepCount)
    let samplePredicate = HKSamplePredicate.quantitySample(type: stepType, predicate: predicate)

    let query = HKStatisticsCollectionQueryDescriptor(
        predicate: samplePredicate,
        options: .cumulativeSum,
        anchorDate: endDate,
        intervalComponents: DateComponents(day: 1)
    )

    let updateStream = query.results(for: store)
    for try await result in updateStream {
        // result.statisticsCollection contains updated data
    }
}
```

## Common Mistakes

### Legacy Mistakes (still relevant)

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Assuming HealthKit available on all devices | Always call `HKHealthStore.isHealthDataAvailable()` first |
| Requesting authorization without privacy strings in Info.plist | Add `NSHealthShareUsageDescription` & `NSHealthUpdateUsageDescription` |
| Querying without predicate; fetching all data | Use `HKQuery.predicateForSamples(withStart:end:)` to limit scope |
| Not checking workout authorization before recording | Verify read/write permissions granted; handle denied state |
| Blocking main thread with synchronous queries | Use async handlers or `async/await`; never call on main thread |

### Additional Common Mistakes

**1. Using callback-based queries instead of async/await descriptors**

DON'T -- old `HKSampleQuery` API:
```swift
let query = HKSampleQuery(sampleType: type, predicate: nil, limit: 100, sortDescriptors: []) { _, samples, _ in
    // Callback-based, error-prone
}
store.execute(query)
```

DO -- modern descriptors:
```swift
let descriptor = HKSampleQueryDescriptor(predicates: [.quantitySample(type: type)], limit: 100)
let results = try await descriptor.result(for: store)
```

**2. Not using HKQuantityType shorthand**

DON'T:
```swift
let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount)!
```

DO:
```swift
let stepType = HKQuantityType(.stepCount)
```

**3. Ignoring privacy-by-silence design**

HealthKit doesn't throw errors when authorization is denied—it silently returns empty results. This is intentional privacy design.

DON'T -- assuming data will be returned:
```swift
let results = try await query.result(for: store)
let firstResult = results!.first // Crashes if denied
```

DO -- handle nil/empty gracefully:
```swift
let results = try await query.result(for: store)
guard let first = results?.first else { return }
```

**4. Creating multiple HKHealthStore instances**

DON'T:
```swift
func getData() {
    let store = HKHealthStore() // Creating new instance each time
    // ...
}
```

DO:
```swift
class HealthManager {
    let store = HKHealthStore()
}
```

**5. Not pairing HKObserverQuery with completion handler**

DON'T -- forgotten completion handler:
```swift
let query = HKObserverQuery(sampleType: type, predicate: nil) { _, handler, _ in
    processData()
    // Forgot to call handler()
}
```

DO:
```swift
let query = HKObserverQuery(sampleType: type, predicate: nil) { _, handler, _ in
    defer { handler() }
    processData()
}
```

**6. Mismatched statistics options for data type**

DON'T -- cumulative sum on discrete data:
```swift
let query = HKStatisticsQueryDescriptor(
    predicate: heartRatePredicate,
    options: .cumulativeSum  // Wrong for heart rate!
)
```

DO -- match to data type:
```swift
let query = HKStatisticsQueryDescriptor(
    predicate: heartRatePredicate,
    options: .discreteAverage  // Correct for discrete types
)
```

**7. Over-requesting data types in authorization**

DON'T -- requesting types app never uses:
```swift
let allTypes: Set<HKObjectType> = [
    HKQuantityType(.stepCount),
    HKQuantityType(.heartRate),
    HKQuantityType(.bloodGlucose),
    HKQuantityType(.bodyMass),
    // ...20 more types
]
try await store.requestAuthorization(toShare: allTypes, read: allTypes)
```

DO -- request only what's needed:
```swift
let neededTypes: Set<HKObjectType> = [
    HKQuantityType(.stepCount),
    HKQuantityType(.activeEnergyBurned)
]
try await store.requestAuthorization(toShare: neededTypes, read: neededTypes)
```

**8. Forgetting the availability check**

DON'T:
```swift
let store = HKHealthStore() // Crashes on iPad!
```

DO:
```swift
guard HKHealthStore.isHealthDataAvailable() else { return }
```

**9. Running queries on the main thread**

DON'T -- even though async/await handles it better, be explicit:
```swift
@MainActor func loadData() async {
    let results = try await query.result(for: store)
}
```

DO -- background task for heavy work:
```swift
Task(priority: .background) {
    let results = try await query.result(for: store)
    await MainActor.run {
        updateUI(with: results)
    }
}
```

**10. Not handling unit conversions for custom queries**

DON'T -- assuming default units:
```swift
let bpm = sample.quantity.doubleValue(for: HKUnit.count())
```

DO -- explicit unit:
```swift
let bpm = sample.quantity.doubleValue(
    for: HKUnit.count().unitDivided(by: .minute())
)
```

**11. Assuming .results(for:) works for all query types**

`.results(for:)` returns an `AsyncSequence` and is only for collection queries. For single-result queries use `.result(for:)`.

DON'T:
```swift
let descriptor = HKSampleQueryDescriptor(...)
for try await result in descriptor.results(for: store) { } // Wrong!
```

DO:
```swift
let descriptor = HKSampleQueryDescriptor(...)
let results = try await descriptor.result(for: store)
```

## HKUnit Reference

Common units for HealthKit data:

```swift
// Basic units
HKUnit.count()                              // Steps, counts
HKUnit.meter()                              // Distance
HKUnit.mile()                               // Distance (imperial)
HKUnit.kilocalorie()                        // Energy
HKUnit.joule(with: .kilo)                   // Energy (SI)
HKUnit.gramUnit(with: .kilo)                // Mass (kg)
HKUnit.pound()                              // Mass (imperial)
HKUnit.percent()                            // Percentage
HKUnit.degreeCelsius()                      // Temperature
HKUnit.degreeFahrenheit()                   // Temperature
HKUnit.millimeterOfMercury()                // Blood pressure

// Compound units
HKUnit.count().unitDivided(by: .minute())   // Heart rate (bpm)
HKUnit.meter().unitDivided(by: .second())   // Speed (m/s)
HKUnit.gramUnit(with: .milli).unitDivided(by: .literUnit(with: .deci))  // Blood glucose (mg/dL)

// Prefixed units
HKUnit.gramUnit(with: .milli)               // Milligrams
HKUnit.literUnit(with: .deci)               // Deciliters
HKUnit.literUnit(with: .milli)              // Milliliters
HKUnit.second()                             // Duration
HKUnit.minute()                             // Duration
```

## Common Data Types (Extended Reference)

### HKQuantityTypeIdentifier (Extended)

| Identifier | Category | Unit |
|---|---|---|
| `.stepCount` | Fitness | `.count()` |
| `.distanceWalkingRunning` | Fitness | `.meter()` |
| `.distanceCycling` | Fitness | `.meter()` |
| `.distanceSwimming` | Fitness | `.meter()` |
| `.activeEnergyBurned` | Fitness | `.kilocalorie()` |
| `.basalEnergyBurned` | Fitness | `.kilocalorie()` |
| `.pushCount` | Fitness | `.count()` |
| `.swimmingStrokeCount` | Fitness | `.count()` |
| `.heartRate` | Vitals | `.count().unitDivided(by: .minute())` |
| `.restingHeartRate` | Vitals | `.count().unitDivided(by: .minute())` |
| `.walkingHeartRateAverage` | Vitals | `.count().unitDivided(by: .minute())` |
| `.oxygenSaturation` | Vitals | `.percent()` |
| `.bloodPressureSystolic` | Vitals | `.millimeterOfMercury()` |
| `.bloodPressureDiastolic` | Vitals | `.millimeterOfMercury()` |
| `.temperature` | Vitals | `.degreeCelsius()` or `.degreeFahrenheit()` |
| `.respiratoryRate` | Vitals | `.count().unitDivided(by: .minute())` |
| `.bodyMass` | Body | `.gramUnit(with: .kilo)` |
| `.bodyMassIndex` | Body | `.count()` |
| `.height` | Body | `.meter()` |
| `.bodyFatPercentage` | Body | `.percent()` |
| `.bloodGlucose` | Lab | `.gramUnit(with: .milli).unitDivided(by: .literUnit(with: .deci))` |
| `.dietaryEnergyConsumed` | Nutrition | `.kilocalorie()` |
| `.fluidIntake` | Nutrition | `.liter()` |

## Review Checklist

- [ ] `HKHealthStore.isHealthDataAvailable()` checked at startup
- [ ] Privacy strings (NSHealthShareUsageDescription, NSHealthUpdateUsageDescription) in Info.plist
- [ ] `requestAuthorization()` called before any queries
- [ ] Read/write types correctly specified for requested data
- [ ] Queries use predicates with date ranges (not open-ended)
- [ ] Completion handlers dispatch to main thread for UI updates
- [ ] Workout sessions properly start/end (not orphaned)
- [ ] Background delivery frequency appropriate (avoid `.immediate` for non-critical)
- [ ] HKWorkoutBuilder used for recording, not manual samples
- [ ] Quantity units correct for type (steps: count, heart rate: count/min, etc.)
- [ ] Error handling for denied authorization
- [ ] Sample metadata (device, location, metadata dict) populated correctly

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

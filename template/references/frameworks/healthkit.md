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
| `HKSampleQuery` | Fetch existing samples | Can sort, limit, filter with predicates |
| `HKStatisticsQuery` | Aggregate data (sum, avg, min, max) | Over time intervals |
| `HKWorkoutSession` | Track active workout | Built-in pause/resume/end |
| `HKWorkoutBuilder` | Construct workout | Add samples during session |
| `HKWorkoutRoute` | GPS path data | Attached to workout |
| `HKUpdateFrequency` | Background sync rate | `.immediate`, `.hourly`, `.daily`, `.weekly` |

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

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Assuming HealthKit available on all devices | Always call `HKHealthStore.isHealthDataAvailable()` first |
| Requesting authorization without privacy strings in Info.plist | Add `NSHealthShareUsageDescription` & `NSHealthUpdateUsageDescription` |
| Querying without predicate; fetching all data | Use `HKQuery.predicateForSamples(withStart:end:)` to limit scope |
| Not checking workout authorization before recording | Verify read/write permissions granted; handle denied state |
| Blocking main thread with synchronous queries | Use async handlers or `async/await`; never call on main thread |

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

# Background Processing — iOS Reference

> **When to read:** Dev reads this when implementing scheduled tasks, background sync, or background push notifications that persist while the app is suspended.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Methods/Types |
|---------|---------|-------------------|
| **BGTaskScheduler** | Schedule background tasks | `.shared.submit(_:)`, `.shared.cancel(taskRequest:)` |
| **BGAppRefreshTask** | Periodic app refresh | `BGAppRefreshTaskRequest(identifier:)` |
| **BGProcessingTask** | Long-running task | `BGProcessingTaskRequest(identifier:)` |
| **Background URL Sessions** | Network after suspend | `URLSessionConfiguration.background(withIdentifier:)` |
| **Background Push** | Silent notifications | `remote-notification` in content, no alert |
| **beginBackgroundTask** | Short-lived grace period | `UIApplication.shared.beginBackgroundTask()` |
| **WKExtendedRuntimeSession** | Workout/navigation | iOS 16+, extended time for specific scenarios |
| **Task Scheduling** | Request management | Minimum 15 min intervals, high-priority on plugged |
| **Entitlements** | Required for background | `com.apple.developer.backgroundtasks` |

---

## Code Examples

**Example 1: BGAppRefreshTask for periodic sync**
```swift
import BackgroundTasks

class SyncManager {
    static let refreshTaskID = "com.app.sync"

    static func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: Self.refreshTaskID)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // 15 min

        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Failed to schedule refresh: \(error)")
        }
    }

    static func registerHandlers() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.refreshTaskID,
            using: nil
        ) { task in
            handleAppRefresh(task as! BGAppRefreshTask)
        }
    }

    static func handleAppRefresh(_ task: BGAppRefreshTask) {
        scheduleAppRefresh() // Reschedule for next interval

        let queue = OperationQueue()
        queue.maxConcurrentOperationCount = 1

        Task {
            do {
                try await fetchLatestData()
                task.setTaskCompletedWithSuccess(true)
            } catch {
                task.setTaskCompletedWithSuccess(false)
            }
        }
    }

    static func fetchLatestData() async throws {
        // Network request with timeout
        let (data, _) = try await URLSession.shared.data(from: apiURL)
        // Process data
    }
}

// In AppDelegate or SceneDelegate:
// SyncManager.registerHandlers()
// SyncManager.scheduleAppRefresh()
```

**Example 2: BGProcessingTask for long background work**
```swift
class DataProcessingManager {
    static let processingTaskID = "com.app.processing"

    static func scheduleProcessing() {
        let request = BGProcessingTaskRequest(identifier: Self.processingTaskID)
        request.requiresNetworkConnectivity = true
        request.requiresExternalPower = true // Only when plugged in

        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Failed to schedule processing: \(error)")
        }
    }

    static func registerHandlers() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.processingTaskID,
            using: nil
        ) { task in
            handleProcessing(task as! BGProcessingTask)
        }
    }

    static func handleProcessing(_ task: BGProcessingTask) {
        scheduleProcessing() // Reschedule

        Task {
            defer { task.setTaskCompletedWithSuccess(true) }

            do {
                // Long-running work (up to 10 minutes when plugged in)
                try await processLargeDataset()
            } catch {
                task.setTaskCompletedWithSuccess(false)
            }
        }

        task.expirationHandler = {
            // Called when OS needs resources back
            print("Background task expiring")
            task.setTaskCompletedWithSuccess(false)
        }
    }
}
```

**Example 3: Background URL session with delegate**
```swift
class BackgroundDownloadManager: NSObject, URLSessionDownloadDelegate {
    static let backgroundSessionID = "com.app.background-download"

    static let shared = BackgroundDownloadManager()

    lazy var backgroundSession: URLSession = {
        let config = URLSessionConfiguration.background(withIdentifier: Self.backgroundSessionID)
        return URLSession(configuration: config, delegate: self, delegateQueue: nil)
    }()

    func downloadFile(from url: URL) {
        let task = backgroundSession.downloadTask(with: url)
        task.resume()
    }

    // Delegate methods
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didFinishDownloadingTo location: URL) {
        // Move file from temp location to Documents
        let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let destinationURL = documentsURL.appendingPathComponent(downloadTask.originalRequest?.url?.lastPathComponent ?? "file")

        do {
            try FileManager.default.moveItem(at: location, to: destinationURL)
        } catch {
            print("Download failed: \(error)")
        }
    }

    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        if let error = error {
            print("Task error: \(error)")
        }
    }
}
```

---

## BGContinuedProcessingTask (iOS 26+)

A task initiated in the foreground that continues running in the background with system support for resource management and Live Activity progress display.

```swift
func startExport() {
    let request = BGContinuedProcessingTaskRequest(
        identifier: "com.example.app.export",
        title: "Exporting Photos",
        subtitle: "Processing 247 items"
    )
    // .queue: begin ASAP if unable to run immediately
    // .fail: fail submission if unable to run immediately
    request.strategy = .queue

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        print("Could not submit: \(error)")
    }
}

func performExport(task: BGContinuedProcessingTask) async {
    let items = await PhotoLibrary.shared.itemsToExport()
    let progress = task.progress
    progress.totalUnitCount = Int64(items.count)

    for (index, item) in items.enumerated() {
        if Task.isCancelled { break }

        await PhotoExporter.shared.export(item)
        progress.completedUnitCount = Int64(index + 1)

        task.updateTitle(
            "Exporting Photos",
            subtitle: "\(index + 1) of \(items.count) complete"
        )
    }

    task.setTaskCompleted(success: !Task.isCancelled)
}
```

### BGTaskScheduler.supportedResources

Check resource availability before requesting them:

```swift
let supported = BGTaskScheduler.shared.supportedResources
if supported.contains(.gpu) {
    request.requiredResources = .gpu
}
if supported.contains(.neural) {
    request.requiredResources.insert(.neural)
}
```

## Swift 6 Concurrency Patterns

Use modern structured concurrency for background tasks:

```swift
func handleAppRefresh(task: BGAppRefreshTask) {
    scheduleAppRefresh()

    let work = Task {
        do {
            let data = try await APIClient.shared.fetchLatestFeed()
            await FeedStore.shared.update(with: data)
            task.setTaskCompleted(success: true)
        } catch {
            task.setTaskCompleted(success: false)
        }
    }

    task.expirationHandler = {
        work.cancel()
        task.setTaskCompleted(success: false)
    }
}
```

## Common Mistakes

**Mistake 1: Not registering task handlers in app startup**
```swift
// ❌ WRONG — Handlers only registered when user taps button
@IBAction func syncButtonTapped() {
    BGTaskScheduler.shared.register(forTaskWithIdentifier: "sync") { task in
        // Handle task
    }
}

// ✅ CORRECT — Register in AppDelegate.application(_:didFinishLaunchingWithOptions:)
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    SyncManager.registerHandlers()
    return true
}
```

**Mistake 2: No expirationHandler in background task**
```swift
// ❌ WRONG — Task hangs, doesn't return gracefully
BGTaskScheduler.shared.register(forTaskWithIdentifier: "work") { task in
    Task {
        await doLongWork()
        task.setTaskCompletedWithSuccess(true)
    }
}

// ✅ CORRECT — Always set expirationHandler
BGTaskScheduler.shared.register(forTaskWithIdentifier: "work") { task in
    let bgTask = task as! BGProcessingTask
    bgTask.expirationHandler = {
        // Stop current work, return resources
        bgTask.setTaskCompletedWithSuccess(false)
    }

    Task {
        await doLongWork()
        bgTask.setTaskCompletedWithSuccess(true)
    }
}
```

**Mistake 3: Too-frequent task scheduling**
```swift
// ❌ WRONG — 5-minute intervals (system ignores, wastes battery)
let request = BGAppRefreshTaskRequest(identifier: "sync")
request.earliestBeginDate = Date(timeIntervalSinceNow: 5 * 60)

// ✅ CORRECT — Minimum 15 minutes recommended
let request = BGAppRefreshTaskRequest(identifier: "sync")
request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
```

**Mistake 4: Blocking main thread in background task**
```swift
// ❌ WRONG — Synchronous file I/O blocks background task
BGTaskScheduler.shared.register(forTaskWithIdentifier: "process") { task in
    let data = try! Data(contentsOf: largeFile) // Blocks!
    process(data)
}

// ✅ CORRECT — Use async I/O
BGTaskScheduler.shared.register(forTaskWithIdentifier: "process") { task in
    Task {
        let data = try await URLSession.shared.data(from: url).0
        process(data)
    }
}
```

**Mistake 5: No entitlement for background tasks**
```swift
// ❌ WRONG — Entitlement missing, task never runs
// Signing & Capabilities: Background Tasks NOT checked

// ✅ CORRECT — Enable in Xcode
// Target Settings → Signing & Capabilities → Background Tasks
// Add specific task identifiers
```

---

## Review Checklist

- [ ] Background task handlers registered in `AppDelegate` or `SceneDelegate`?
- [ ] All BGTasks have `expirationHandler` that stops work gracefully?
- [ ] Task identifiers match between registration and entitlements?
- [ ] Minimum 15-minute intervals between scheduled tasks?
- [ ] Tasks reschedule themselves for next iteration?
- [ ] Background URL session has stable identifier?
- [ ] Background session delegate methods implemented?
- [ ] No main thread blocking (use async/await)?
- [ ] Background Tasks entitlement enabled in Xcode?
- [ ] Tasks clean up resources when expirationHandler fires?
- [ ] Tested in simulator with scheme arguments `com.apple.CoreData.ConcurrencyDebug`?
- [ ] Database or file writes are atomic (no corruption on interrupt)?

## Enriched Common Mistakes

- ❌ Missing expirationHandler — task hangs without graceful cleanup
- ❌ Registering handlers on demand instead of app startup — handlers won't be available when task fires
- ❌ Scheduling tasks too frequently — system ignores requests < 15 minutes apart
- ❌ Blocking main thread in background task — defeats purpose of background processing
- ❌ Forgetting Background Tasks entitlement — enabled task never runs

## Enriched Review Checklist

- [ ] ExpirationHandler set on all background tasks
- [ ] Task handlers registered in app startup (AppDelegate/SceneDelegate)
- [ ] Task reschedule logic prevents scheduling dead-mans-switch
- [ ] Minimum 15-minute scheduling intervals respected
- [ ] No synchronous I/O (use async/await)
- [ ] Background Tasks capability enabled in Xcode

## BGContinuedProcessingTask (iOS 26+)

Extended background runtime for long-running operations:

```swift
let request = BGContinuedProcessingTaskRequest(identifier: "com.app.extended")
request.estimatedDuration = 60 // Estimate runtime in seconds
try BGTaskScheduler.shared.submit(request)
```

---

_Source: Apple Developer Documentation · BackgroundTasks, URLSession, WKExtendedRuntimeSession · Condensed for Ship Framework agent reference_

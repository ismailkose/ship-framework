# MetricKit — iOS Reference

> **When to read:** Dev reads this when collecting diagnostic data, crash reports, hang detection, or performance metrics from user devices.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Types/Methods |
|---------|---------|-------------------|
| **MXMetricManager** | Central metrics collection | `.shared.add(_:)`, `.shared.pauseMetricsCollection()` |
| **MXMetricPayload** | Aggregated metrics | `.signpost`, `.applicationLaunchMetrics`, `.memoryMetrics` |
| **MXDiagnosticPayload** | Detailed diagnostics | `.crashDiagnostics`, `.hangDiagnostics`, `.diskWriteExceptionDiagnostics` |
| **Crash Reports** | Exception/signal crashes | `MXCrashDiagnostic.callStackTree` |
| **Hang Rate** | Main thread hangs | Detected > 250ms blocks |
| **Memory Metrics** | Peak/avg memory | `peakMemoryUsage`, `averageMemoryUsage` |
| **CPU Metrics** | Processing activity | `cumulativeCPUTime` |
| **Disk Writes** | I/O tracking | `cumulativeLogicalWrites` |
| **Custom Signposts** | App-defined metrics | `os_signpost()` with metrics category |
| **Data Privacy** | Metric anonymization | No PII, sample before sending |

---

## Code Examples

**Example 1: Basic MetricKit subscriber setup**
```swift
import MetricKit

class MetricsSubscriber: NSObject, MXMetricManagerSubscriber {
    static let shared = MetricsSubscriber()

    override init() {
        super.init()
        MXMetricManager.shared.add(self)
    }

    // Called daily or when app is backgrounded
    func didReceive(_ payload: MXMetricPayload) {
        print("Received metrics payload")

        // App launch metrics
        if let launchMetrics = payload.applicationLaunchMetrics {
            let duration = launchMetrics.duration.value
            print("App launch duration: \(duration)ms")
        }

        // Memory metrics
        if let memoryMetrics = payload.memoryMetrics {
            let peakMemory = memoryMetrics.peakMemoryUsage
            print("Peak memory: \(peakMemory / 1_000_000)MB")
        }

        // Disk write metrics
        if let diskMetrics = payload.diskMetrics {
            let writes = diskMetrics.cumulativeLogicalWrites.value
            print("Disk writes: \(writes)MB")
        }

        // Custom signposts (from os_signpost)
        if let signpostMetrics = payload.signpostMetrics {
            for signpost in signpostMetrics {
                print("Signpost: \(signpost.signpostName), duration: \(signpost.duration)")
            }
        }

        // Send to analytics backend
        Task {
            await sendMetricsToServer(payload)
        }
    }

    func didReceive(_ payload: MXDiagnosticPayload) {
        print("Received diagnostic payload")

        // Crash diagnostics
        if let crashes = payload.crashDiagnostics {
            for crash in crashes {
                print("Crash: \(crash.exceptionCode ?? "unknown")")
                print("Call stack: \(crash.callStackTree?.description ?? "none")")
            }
        }

        // Hang diagnostics
        if let hangs = payload.hangDiagnostics {
            print("Detected \(hangs.count) main thread hangs")
        }

        // Disk write exceptions
        if let diskExceptions = payload.diskWriteExceptionDiagnostics {
            print("Disk write exceptions: \(diskExceptions.count)")
        }

        // Send diagnostics to backend
        Task {
            await sendDiagnosticsToServer(payload)
        }
    }

    private func sendMetricsToServer(_ payload: MXMetricPayload) async {
        let jsonData = try JSONEncoder().encode(payload)
        // POST to analytics endpoint
    }

    private func sendDiagnosticsToServer(_ payload: MXDiagnosticPayload) async {
        // Encode and send to crash reporting service
    }
}

// In AppDelegate or app init:
// _ = MetricsSubscriber.shared
```

**Example 2: Custom signposts for app-specific metrics**
```swift
import os

let metricsLog = OSLog(subsystem: "com.app.metrics", category: .metrics)

struct DataProcessingMetrics {
    static func trackProcessing(items: Int) async {
        let signpostID = OSSignpostID(log: metricsLog)

        os_signpost(.begin, log: metricsLog, name: "DataProcessing", signpostID: signpostID,
                    "Processing %d items", items)

        defer {
            os_signpost(.end, log: metricsLog, name: "DataProcessing", signpostID: signpostID)
        }

        // Simulate processing
        for i in 0..<items {
            try? await Task.sleep(nanoseconds: 100_000) // 0.1ms per item
        }
    }

    static func trackNetwork(requestSize: Int, responseSize: Int) async {
        let signpostID = OSSignpostID(log: metricsLog)

        os_signpost(.begin, log: metricsLog, name: "NetworkRequest", signpostID: signpostID)

        defer {
            os_signpost(.end, log: metricsLog, name: "NetworkRequest", signpostID: signpostID,
                        "Request: %d bytes, Response: %d bytes", requestSize, responseSize)
        }

        // Network operation
    }
}

// MetricKit will aggregate these signposts and report in MXMetricPayload.signpostMetrics
```

**Example 3: Filtered metrics collection (reduce privacy concerns)**
```swift
class PrivacyAwareMetricsCollector: MXMetricManagerSubscriber {
    func didReceive(_ payload: MXMetricPayload) {
        // Only collect on WiFi and plugged in (less sensitive)
        guard shouldCollectMetrics() else { return }

        // Sample data (e.g., 10% of payloads)
        guard Int.random(in: 0..<100) < 10 else { return }

        // Remove or anonymize sensitive fields
        let sanitizedPayload = sanitize(payload)

        Task {
            await sendMetricsToServer(sanitizedPayload)
        }
    }

    func didReceive(_ payload: MXDiagnosticPayload) {
        // Only send crashes/hangs, not routine diagnostics
        guard payload.crashDiagnostics?.isEmpty == false ||
              payload.hangDiagnostics?.isEmpty == false else {
            return
        }

        Task {
            await sendDiagnosticsToServer(payload)
        }
    }

    private func shouldCollectMetrics() -> Bool {
        // Check connectivity, power state
        return true
    }

    private func sanitize(_ payload: MXMetricPayload) -> MXMetricPayload {
        // Remove identifiable information
        return payload
    }
}
```

---

## Common Mistakes

**Mistake 1: Not adding subscriber before app finishes launching**
```swift
// ❌ WRONG — Subscriber added too late, misses first launch metrics
func viewDidLoad() {
    MXMetricManager.shared.add(MetricsSubscriber.shared)
}

// ✅ CORRECT — Add in AppDelegate.didFinishLaunching
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    _ = MetricsSubscriber.shared // Initializes and adds subscriber
    return true
}
```

**Mistake 2: Sending all metrics to server without sampling**
```swift
// ❌ WRONG — Every device sends data daily, privacy/server load issues
func didReceive(_ payload: MXMetricPayload) {
    Task {
        await sendMetricsToServer(payload) // Always sends
    }
}

// ✅ CORRECT — Sample data, only on WiFi
func didReceive(_ payload: MXMetricPayload) {
    guard Int.random(in: 0..<100) < 5 else { return } // 5% sample
    guard isOnWiFi() else { return }

    Task {
        await sendMetricsToServer(payload)
    }
}
```

**Mistake 3: Logging PII in crash diagnostics**
```swift
// ❌ WRONG — User account info in crash stack trace
os_log("Processing user: %{public}@", user.email)
// Crash occurs, MetricKit reports email in diagnostics

// ✅ CORRECT — Redact identifiers
os_log("Processing user", log: .default, type: .info)
// No identifiable info in crash stack
```

**Mistake 4: Not handling parse failures gracefully**
```swift
// ❌ WRONG — JSONEncoder throws, metrics lost
func didReceive(_ payload: MXMetricPayload) {
    let jsonData = try JSONEncoder().encode(payload) // May throw
    // If throws, crash or data lost
}

// ✅ CORRECT — Handle encoding errors
func didReceive(_ payload: MXMetricPayload) {
    do {
        let jsonData = try JSONEncoder().encode(payload)
        Task { await sendMetricsToServer(jsonData) }
    } catch {
        print("Failed to encode metrics: \(error)")
        // Silently fail, don't crash
    }
}
```

**Mistake 5: Not pausing collection during sensitive operations**
```swift
// ❌ WRONG — Metrics collected during authentication, leaks timing data
func authenticateUser() async {
    let start = Date()
    let result = try await performAuthentication()
    let duration = Date().timeIntervalSince(start)
    // MetricKit may report timing, brute-force detection risk
}

// ✅ CORRECT — Pause metrics during sensitive operations
func authenticateUser() async {
    MXMetricManager.shared.pauseMetricsCollection()
    defer { MXMetricManager.shared.resumeMetricsCollection() }

    let result = try await performAuthentication()
}
```

---

## Review Checklist

- [ ] MetricsSubscriber added in app startup (`AppDelegate` or app init)?
- [ ] Both `didReceive(_: MXMetricPayload)` and `didReceive(_: MXDiagnosticPayload)` implemented?
- [ ] Metrics sampled before sending (not 100% of events)?
- [ ] Only collected on WiFi or when explicitly enabled?
- [ ] No PII in logs or custom signposts?
- [ ] Crash/hang diagnostics sent to backend for analysis?
- [ ] Custom signposts added for app-specific features?
- [ ] App launch time tracked and monitored?
- [ ] Memory peaks flagged when exceeding threshold?
- [ ] Main thread hangs analyzed for UI blocking?
- [ ] Metrics paused during sensitive operations?
- [ ] User consent obtained before collecting metrics?

---

_Source: Apple Developer Documentation · MetricKit, os_signpost · Condensed for Ship Framework agent reference_

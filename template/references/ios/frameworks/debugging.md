# Debugging & Profiling — iOS Reference

> **When to read:** Dev reads this when profiling performance, debugging memory leaks, tracking network requests, or investigating SwiftUI rendering issues.

> **Cross-reference:** For SwiftUI-specific performance profiling, see `swiftui-core.md` Section 10. This file covers general debugging, memory, and Instruments.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Tools/Methods |
|---------|---------|-------------------|
| **Time Profiler** | CPU usage per function | Instruments app, time per call |
| **Allocations** | Memory growth tracking | Heap snapshots, allocation history |
| **Leaks** | Detect unreleased memory | Automatic leak detection & stack traces |
| **Network** | HTTP request inspection | Request/response headers, body, timing |
| **Core Data** | Query performance | Fetch request analysis, fault patterns |
| **SwiftUI** | View body tracking | `.debugPrint()`, `.onReceive()` debug hooks |
| **os_log/Logger** | Structured logging | `Logger(subsystem:category:)`, log levels |
| **os_signpost** | Performance markers | `os_signpost()`, interval tracking in Instruments |
| **MetricKit** | Diagnostic payloads | `MXMetricManager`, crash reports, hang rate |
| **Xcode Debugger** | Breakpoints & LLDB | `po`, `p`, conditional breakpoints |

---

## Code Examples

**Example 1: Structured logging with Logger**
```swift
import os

let logger = Logger(subsystem: "com.app.networking", category: "URLSession")

func fetchUser(_ id: Int) async throws -> User {
    logger.debug("Starting user fetch for ID: \(id, privacy: .public)")

    do {
        let url = URL(string: "https://api.example.com/users/\(id)")!
        let (data, response) = try await URLSession.shared.data(from: url)

        logger.debug("Received response: \(response.description, privacy: .public)")

        let user = try JSONDecoder().decode(User.self, from: data)
        logger.info("User fetched successfully: \(user.name, privacy: .private)")
        return user
    } catch {
        logger.error("Failed to fetch user: \(error.localizedDescription, privacy: .public)")
        throw error
    }
}

// View in Console.app, filter by "com.app.networking"
```

**Example 2: SwiftUI view performance debugging**
```swift
struct ContentView: View {
    @State var items: [Item] = []
    @State var filterText = ""

    var filteredItems: [Item] {
        items.filter { item in
            filterText.isEmpty || item.name.contains(filterText)
        }
    }

    var body: some View {
        VStack {
            TextField("Search", text: $filterText)

            List(filteredItems) { item in
                ItemRow(item: item)
                    .id(item.id) // Helps SwiftUI track identity
            }
            .onReceive(Timer.publish(every: 1, on: .main, in: .common).autoconnect()) { _ in
                // Track render counts
                logger.debug("ContentView rendered")
            }
        }
    }
}

// Debug view hierarchy:
struct ItemRow: View {
    let item: Item

    var body: some View {
        HStack {
            Text(item.name)
                .redacted(reason: .placeholder) // Highlight expensive views
        }
    }
}
```

**Example 3: os_signpost for performance intervals**
```swift
import os

let pointsOfInterest = OSLog(subsystem: "com.app", category: .pointsOfInterest)

func processDatabaseQuery() async {
    let signpostID = OSSignpostID(log: pointsOfInterest)

    // Mark start of interval
    os_signpost(.begin, log: pointsOfInterest, name: "Database Query", signpostID: signpostID,
                "Processing %d items", items.count)

    defer {
        // Mark end of interval
        os_signpost(.end, log: pointsOfInterest, name: "Database Query", signpostID: signpostID)
    }

    // Simulate work
    try? await Task.sleep(nanoseconds: 1_000_000_000) // 1 second

    // View in Instruments > Points of Interest
}
```

### Custom Metrics with mxSignpost and OSSignposter

For production telemetry integrated with MetricKit, use `mxSignpost()` with `MXSignpostIntervalData`.
Create an `OSSignposter` actor for thread-safe custom metric emission:

```swift
import os

// Create a MetricKit log handle for custom metrics
let metricLog = MXMetricManager.makeLogHandle(category: "Networking")

// Actor pattern for thread-safe signpost emission
actor NetworkMetricsRecorder {
    func recordRequest(duration: TimeInterval, bytes: Int) {
        let signpostID = MXSignpostIntervalData.makeSignpostID(log: metricLog)

        mxSignpost(.begin, log: metricLog, name: "APIRequest", signpostID: signpostID)
        defer {
            mxSignpost(.end, log: metricLog, name: "APIRequest", signpostID: signpostID,
                      "Duration: %.2fs, Bytes: %d", duration, bytes)
        }

        // Recording happens within the signpost interval
    }
}

// Or use OSSignposter for standard (non-MetricKit) signposts
let paster = OSSignposter(subsystem: "com.example.app", category: "DataLoad")

func loadData() async {
    let state = paster.beginInterval("loadData")
    defer { paster.endInterval("loadData", state) }

    let result = await fetchFromNetwork()
    process(result)
}
```

**Note:** Limit custom metrics to critical code paths. The system caps the number
of unique signpost names per log handle to reduce on-device overhead. Custom
metrics appear in `MXMetricPayload.signpostMetrics` for analysis.

---

## Common Mistakes

**Mistake 1: No logging in production code**
```swift
// ❌ WRONG — Silent failures, no diagnostics
func syncData() async throws {
    let data = try await fetchFromServer()
    try await saveToDatabase(data)
}

// ✅ CORRECT — Log at appropriate levels
func syncData() async throws {
    logger.info("Starting data sync")
    let data = try await fetchFromServer()
    logger.debug("Fetched \(data.count) items")

    try await saveToDatabase(data)
    logger.info("Sync completed successfully")
}
```

**Mistake 2: Excessive logging of sensitive data**
```swift
// ❌ WRONG — API keys, tokens in logs
logger.debug("API Key: \(apiKey)")
logger.debug("Token: \(authToken)")

// ✅ CORRECT — Use privacy levels
logger.debug("Making request to API", privateMetadata: "\(apiKey)")
logger.debug("Auth token length: \(authToken.count, privacy: .public)")
```

**Mistake 3: Not profiling before optimizing**
```swift
// ❌ WRONG — Assume loop is slow without measurement
func updateUI() {
    for i in 0..<10000 {
        updateLabel(i) // Assumed slow
    }
}

// ✅ CORRECT — Measure first with Time Profiler
// Run Xcode Instruments > Time Profiler
// Identify actual bottleneck (usually network, not loops)
// Then optimize the real issue
```

**Mistake 4: SwiftUI view recomputation without identity**
```swift
// ❌ WRONG — List recreates all rows on state change
List(items) { item in
    ItemRow(item: item) // Row recreates even if item unchanged
}

// ✅ CORRECT — Add .id() for stable identity
List(items) { item in
    ItemRow(item: item)
        .id(item.id) // Prevents unnecessary recomputation
}
```

**Mistake 5: Memory leak from closure capture**
```swift
// ❌ WRONG — Strong reference cycle
class DataFetcher {
    func fetchWithTimer() {
        var timer: Timer?
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            self.fetch() // Captures self strongly, timer holds closure, prevents deallocation
        }
    }
}

// ✅ CORRECT — Weak self in timer closure
class DataFetcher {
    var timer: Timer?

    func fetchWithTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            self?.fetch()
        }
    }

    deinit {
        timer?.invalidate() // Explicitly stop timer
    }
}
```

**Mistake 6: Ignoring Thread Sanitizer warnings**
```swift
// ❌ WRONG — Concurrent access from multiple threads
var cache: [String: Data] = [:]

func getCached(_ key: String) -> Data? {
    return cache[key]  // Main thread
}

func updateCache(_ key: String, _ value: Data) {
    DispatchQueue.global().async {
        self.cache[key] = value  // Background thread — data race!
    }
}

// ✅ CORRECT — Protect shared mutable state with an actor
actor CacheActor {
    var cache: [String: Data] = [:]

    func getCached(_ key: String) -> Data? {
        cache[key]
    }

    func updateCache(_ key: String, _ value: Data) {
        cache[key] = value
    }
}

// Usage enforces synchronization
await cacheActor.updateCache("key", data)
let result = await cacheActor.getCached("key")
```

Enable Thread Sanitizer in Scheme > Run > Diagnostics > Thread Sanitizer.
Note: TSan cannot run simultaneously with Address Sanitizer.

### mxSignpost() with OSSignpostID and OSSignposter

For production telemetry integrated with MetricKit, use `mxSignpost()` with `MXSignpostIntervalData`.
Create an `OSSignposter` actor for thread-safe custom metric emission:

```swift
import os

// Create a MetricKit log handle for custom metrics
let metricLog = MXMetricManager.makeLogHandle(category: "Networking")

// Actor pattern for thread-safe signpost emission
actor NetworkMetricsRecorder {
    func recordRequest(duration: TimeInterval, bytes: Int) {
        let signpostID = MXSignpostIntervalData.makeSignpostID(log: metricLog)

        mxSignpost(.begin, log: metricLog, name: "APIRequest", signpostID: signpostID)
        defer {
            mxSignpost(.end, log: metricLog, name: "APIRequest", signpostID: signpostID,
                      "Duration: %.2fs, Bytes: %d", duration, bytes)
        }

        // Recording happens within the signpost interval
    }
}

// Or use OSSignposter for standard (non-MetricKit) signposts
let paster = OSSignposter(subsystem: "com.example.app", category: "DataLoad")

func loadData() async {
    let state = paster.beginInterval("loadData")
    defer { paster.endInterval("loadData", state) }

    let result = await fetchFromNetwork()
    process(result)
}
```

### xctrace CLI for CI Profiling

Profile app performance in continuous integration pipelines without the GUI:

```bash
# Record Time Profiler trace from CLI
xcrun xctrace record --device "My iPhone" \
    --template "Time Profiler" \
    --output profile.trace \
    --launch MyApp.app

# Export trace data as XML for automated analysis
xcrun xctrace export --input profile.trace --xpath '/trace-toc/run/data/table'

# List available templates
xcrun xctrace list templates

# List connected devices
xcrun xctrace list devices
```

Use `xctrace` in CI pipelines to catch performance regressions automatically.
Parse exported metrics programmatically to set pass/fail thresholds.

### Thread Sanitizer Data Race Patterns

Enable Thread Sanitizer in Scheme > Run > Diagnostics > Thread Sanitizer.
Protect shared mutable state with actors:

```swift
// ❌ WRONG — Concurrent access from multiple threads
var cache: [String: Data] = [:]

func getCached(_ key: String) -> Data? {
    return cache[key]  // Main thread
}

func updateCache(_ key: String, _ value: Data) {
    DispatchQueue.global().async {
        self.cache[key] = value  // Background thread — data race!
    }
}

// ✅ CORRECT — Protect shared mutable state with an actor
actor CacheActor {
    var cache: [String: Data] = [:]

    func getCached(_ key: String) -> Data? {
        cache[key]
    }

    func updateCache(_ key: String, _ value: Data) {
        cache[key] = value
    }
}

// Usage enforces synchronization
await cacheActor.updateCache("key", data)
let result = await cacheActor.getCached("key")
```

**Note:** TSan cannot run simultaneously with Address Sanitizer.

---

## Review Checklist

- [ ] Logging uses `Logger` with subsystem & category?
- [ ] Sensitive data redacted (`.private` annotation)?
- [ ] No printing debug info in production code?
- [ ] Profile with Time Profiler before micro-optimizing?
- [ ] Memory footprint checked with Allocations tool?
- [ ] No obvious memory leaks detected by Leaks instrument?
- [ ] Network requests logged with request/response size?
- [ ] SwiftUI views have `.id()` for stable identity?
- [ ] No strong reference cycles in closures (use `[weak self]`)?
- [ ] os_signpost markers added for long operations?
- [ ] Database queries profiled for N+1 problems?
- [ ] Breakpoints and conditional breakpoints used for debugging?

## Enriched Common Mistakes

- ❌ Profiling Debug builds — always profile Release builds (Debug has optimizations disabled)
- ❌ Using `print()` for production logging — use `os.Logger` with proper subsystem/category
- ❌ Ignoring Memory Graph Debugger — it catches retain cycles Instruments misses
- ❌ Not checking Thread Checker — data races in Swift Concurrency are silent until crash
- ❌ Treating 250ms hangs as acceptable — the main thread hang threshold is 250ms in MetricKit

## Enriched Review Checklist

- [ ] Profiling done on Release builds, not Debug
- [ ] `os.Logger` used instead of `print()` for production logging
- [ ] Memory Graph Debugger run to check for retain cycles
- [ ] Thread Checker enabled during development
- [ ] No main thread hangs > 250ms
- [ ] `xctrace` CLI available for automated performance testing

---

_Source: Apple Developer Documentation · Instruments, os_log, MetricKit, SwiftUI Debugging · Condensed for Ship Framework agent reference_

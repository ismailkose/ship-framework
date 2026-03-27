# Swift Essentials Reference

> **When to read:** Dev reads all sections when writing Swift code.
> Eye reads review checklists when reviewing Swift code quality.

---

## Section 1: Swift Language (Swift 6.2)

Swift 6.2 brings powerful tools for building robust iOS apps. These language features are critical for modern iOS development.

### Result Builders

Result builders enable DSL-like syntax for constructing values. They're used in SwiftUI and can be applied to custom types.

**Correct pattern:**
```swift
@resultBuilder
struct ViewBuilder {
    static func buildBlock(_ components: View...) -> View {
        return VStack(views: components)
    }
}

@ViewBuilder
func createLayout() -> View {
    Text("Hello")
    Text("World")
}
```

**Common Mistakes:**
- ❌ Forgetting to implement `buildBlock` and other required methods
- ❌ Not understanding that result builders transform the closure into method calls
- ✅ Always implement `buildBlock(_:)` as the minimal requirement
- ✅ Use `buildEither(first:)` and `buildEither(second:)` for if-else support

### Property Wrappers

Property wrappers reduce boilerplate by encapsulating property behaviors.

**Correct pattern:**
```swift
@propertyWrapper
struct Validated<Value> {
    private var value: Value

    var wrappedValue: Value {
        get { value }
        set { value = newValue } // Add validation here
    }

    var projectedValue: Validated<Value> {
        return self
    }

    init(wrappedValue: Value) {
        self.value = wrappedValue
    }
}

struct User {
    @Validated var email: String

    func checkEmail() {
        let validator = _email // Access via projectedValue
    }
}
```

**Common Mistakes:**
- ❌ Missing `init(wrappedValue:)` — wrapper won't initialize
- ❌ Forgetting `projectedValue` when you need to access the wrapper itself
- ✅ Provide meaningful `wrappedValue` and `projectedValue` semantics
- ✅ Keep wrapper logic simple; move complex logic to separate types

### Macros & Opaque Types

Macros (new in Swift 5.9+) generate code at compile time. Opaque types (`some`, `any`) abstract over concrete types.

**Correct pattern:**
```swift
// Opaque return type - return type is concrete but hidden from caller
func makeView() -> some View {
    Text("Hello")
}

// Existential type - accepts any type conforming to protocol
func processValue(_ value: any Equatable) {
    // Can store different types in same collection
}

// Using @Codable macro (Swift 6.2)
@Codable
struct Person {
    let name: String
    let age: Int
}
```

**Common Mistakes:**
- ❌ Using `any` when `some` would work (performance cost)
- ❌ Mixing `some` and `any` inconsistently across similar functions
- ✅ Use `some` for return types (concrete, single type)
- ✅ Use `any` for parameters when accepting multiple types

### Pattern Matching & Enums

Pattern matching makes complex conditional logic readable.

**Correct pattern:**
```swift
enum LoadState {
    case idle
    case loading
    case success(Data)
    case failure(Error)
}

// Pattern matching with associated values
let state = LoadState.success(data)
switch state {
case .success(let data):
    print("Got data: \(data)")
case .failure(let error):
    print("Error: \(error)")
case .loading:
    print("Loading...")
case .idle:
    print("Idle")
}

// Guard pattern
if case .success(let data) = state {
    processData(data)
}

// Enum with RawValue for networking
enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
}
```

**Common Mistakes:**
- ❌ Not exhaustively matching all enum cases
- ❌ Using `if let` for enum matching when `if case` is more idiomatic
- ✅ Always handle all cases in switch statements (or use `@unknown default`)
- ✅ Use associated values instead of separate properties

### Error Handling (Typed Throws)

Swift 6.2 supports typed throws for precise error handling.

**Correct pattern:**
```swift
enum NetworkError: Error {
    case invalidURL
    case serverError(Int)
    case decodingFailed
}

// Typed throws - caller knows exactly what errors can be thrown
func fetchUser(id: String) throws(NetworkError) -> User {
    guard let url = URL(string: "https://api.example.com/users/\(id)") else {
        throw .invalidURL
    }

    let (data, response) = try await URLSession.shared.data(from: url)
    guard let httpResponse = response as? HTTPURLResponse,
          (200...299).contains(httpResponse.statusCode) else {
        if let httpResponse = response as? HTTPURLResponse {
            throw .serverError(httpResponse.statusCode)
        }
        throw .decodingFailed
    }

    return try JSONDecoder().decode(User.self, from: data)
}

// Caller benefits from type information
do {
    let user = try fetchUser(id: "123")
} catch .invalidURL {
    print("Invalid URL")
} catch .serverError(let code) {
    print("Server error: \(code)")
} catch .decodingFailed {
    print("Failed to decode response")
}
```

**Common Mistakes:**
- ❌ Throwing generic `Error` when specific error types are better
- ❌ Not providing sufficient context in error cases
- ✅ Create specific error enums for each failure mode
- ✅ Include associated values for error context

### If/Switch Expressions

Swift 5.9+ allows `if` and `switch` to be used as expressions returning values.

**Correct pattern:**
```swift
// Assign from if expression
let icon = if isComplete { "checkmark.circle.fill" } else { "circle" }

// Assign from switch expression (must be exhaustive)
let label = switch status {
case .draft: "Draft"
case .published: "Published"
case .archived: "Archived"
}

// Return directly
func buttonColor(for priority: Priority) -> Color {
    switch priority {
    case .high: .red
    case .medium: .orange
    case .low: .green
    }
}
```

**Rules:**
- ✅ Every branch must produce the same type
- ✅ Each branch is a single expression (no statements)
- ✅ Wrap in parentheses when used as function argument
- ❌ Don't use multi-statement branches

### Modern Collection APIs

Use these APIs instead of manual loops:

**Correct pattern:**
```swift
let numbers = [1, 2, 3, 4, 5, 6, 7, 8]

// count(where:) - more efficient than .filter { }.count
let evenCount = numbers.count(where: { $0.isMultiple(of: 2) })

// contains(where:) - short-circuits on first match
let hasNegative = numbers.contains(where: { $0 < 0 })

// String.replacing() - returns new string (Swift 5.7+)
let cleaned = text.replacing(/\s+/, with: " ")
let snakeCase = name.replacing("_", with: " ")

// Dictionary(grouping:by:) - group items by key
let byCategory = items.grouping(by: \.category)
let byPriority = Dictionary(grouping: tasks, by: \.priority)

// first(where:), last(where:) - find first/last matching condition
let firstEven = numbers.first(where: { $0.isMultiple(of: 2) })

// compactMap - filter and transform in one step
let ids = strings.compactMap { Int($0) }
```

**Common Mistakes:**
- ❌ Using `.filter { }.count` instead of `count(where:)`
- ❌ Using `.contains()` for complex conditions instead of `contains(where:)`
- ✅ Use `count(where:)` for counting with predicate
- ✅ Use `contains(where:)` when you only need a boolean
- ✅ Use `.replacing()` for string modifications

### FormatStyle (Replacing DateFormatter/NumberFormatter)

Use `.formatted()` for type-safe, localized formatting:

**Correct pattern:**
```swift
// Dates - no more DateFormatter boilerplate
let now = Date.now
now.formatted()                                    // "3/15/2024, 2:30 PM"
now.formatted(date: .abbreviated, time: .shortened) // "Mar 15, 2024, 2:30 PM"
now.formatted(.dateTime.year().month().day())      // "Mar 15, 2024"

// Numbers - automatic localization
let price = 42.5
price.formatted(.currency(code: "USD"))           // "$42.50"
(1_000_000).formatted(.number.notation(.compactName)) // "1M"

// Durations
let duration = Duration.seconds(3661)
duration.formatted(.time(pattern: .hourMinuteSecond)) // "1:01:01"
```

**Common Mistakes:**
- ❌ Creating `DateFormatter` instances repeatedly (expensive)
- ❌ Forgetting to set locale on formatter
- ✅ Use `.formatted()` method directly on values
- ✅ Leverage automatic localization

### String Interpolation Extensions

Extend `DefaultStringInterpolation` for domain-specific formatting:

**Correct pattern:**
```swift
extension DefaultStringInterpolation {
    mutating func appendInterpolation(_ value: Int, as style: IntFormat) {
        switch style {
        case .hex: appendLiteral(String(value, radix: 16))
        case .binary: appendLiteral(String(value, radix: 2))
        case .currency: appendLiteral("$\(value)")
        }
    }
}

enum IntFormat { case hex, binary, currency }

let num = 255
print("Hex: \(num, as: .hex)") // "Hex: ff"
```

### Key Protocols

These protocols unlock capabilities in Swift's ecosystem:

**Hashable** - Required for use in Set/Dictionary keys
```swift
struct User: Hashable {
    let id: UUID
    let name: String

    func hash(into hasher: inout Hasher) {
        hasher.combine(id) // Only hash the unique identifier
    }
}
```

**Identifiable** - Required for List/ForEach in SwiftUI
```swift
struct Article: Identifiable {
    let id = UUID()
    let title: String
    let content: String
}
```

**Codable** - See Section 2 for detailed coverage

**Sendable** - Thread-safe types (required in Swift 6.2 strict mode)
```swift
@Sendable
struct Config: Codable {
    let apiKey: String
    let timeout: TimeInterval
}
```

### Modern Swift Idioms

**Prefer Swift-native APIs over Foundation equivalents:**
- `"hello".replacing("l", with: "r")` — not `replacingOccurrences(of:with:)`
- `URL.documentsDirectory` — not `FileManager.default.urls(for:in:)`
- `URL.documentsDirectory.appending(path: "file.txt")` — not `appendingPathComponent()`
- `Date.now` — not `Date()`
- `Date(myString, strategy: .iso8601)` — not manual `DateFormatter` for ISO 8601

**Number and text formatting:**
- Never use `String(format: "%.2f", value)`. Use `Text(value, format: .number.precision(.fractionLength(2)))` or `FormatStyle` APIs.
- Prefer `.formatted()` for display: `date.formatted(.dateTime.day().month().year())`
- For date formatting with year: use `"y"` not `"yyyy"` — `"y"` is correct in all localizations.
- Use `PersonNameComponents` with modern formatting for people's names — not `"\(firstName) \(lastName)"`.

**Collection idioms:**
- `count(where:)` over `filter().count` — avoids intermediate allocation.
- When a type is repeatedly sorted by the same property, make it `Comparable` instead.
- `localizedStandardContains()` for user-input text filtering — not `contains()` or `localizedCaseInsensitiveContains()`.

**Type idioms:**
- Prefer `Double` over `CGFloat` except in optionals or `inout` parameters — Swift bridges them freely.
- Prefer static member lookup: `.circle` over `Circle()`, `.borderedProminent` over `BorderedProminentButtonStyle()`.
- `import SwiftUI` already provides access to UIKit/AppKit types — no separate `import UIKit` needed for `UIImage` etc.

**Control flow:**
- Use `if let value {` shorthand — not `if let value = value {`.
- `if` and `switch` can be used as expressions — omit `return` for single-expression functions.
- Flag silently swallowed errors: `print(error.localizedDescription)` should be an alert, not just a print.

```swift
// WRONG
var tileColor: Color {
  if isCorrect {
    return .green
  } else {
    return .red
  }
}

// CORRECT — if/switch as expression
var tileColor: Color {
  if isCorrect { .green } else { .red }
}
```

**Asset references:**
- Use generated asset symbols: `Image(.avatar)` over `Image("avatar")` — type-safe, catches missing assets at compile time.
- Use `#Preview { }` — never the legacy `PreviewProvider` protocol.

### Review Checklist
- [ ] All enum cases handled in switch statements
- [ ] Error types are specific, not generic `Error`
- [ ] Property wrappers have `wrappedValue` and `projectedValue`
- [ ] Opaque types (`some`) used for returns, `any` for parameters
- [ ] Protocols conform to Hashable/Identifiable/Sendable where appropriate
- [ ] If/switch expressions used for conditional assignment
- [ ] Collection APIs (`count(where:)`, `contains(where:)`, `.replacing()`) used instead of manual loops
- [ ] `.formatted()` used instead of DateFormatter/NumberFormatter
- [ ] Dictionary(grouping:by:) used for grouping operations

---

## Section 2: Concurrency (Swift 6.2)

Swift 6.2 brings comprehensive tools for safe concurrent code. Master the triage workflow and synchronization primitives.

### Triage Workflow for Concurrency Errors

When facing a compiler diagnostic, follow this sequence:

**Step 1: Capture context**
- Copy the exact error message and symbol
- Identify isolation context: `@MainActor`, actor, or `nonisolated`?
- Is the code UI-bound or background work?
- Is approachable concurrency mode enabled?

**Step 2: Apply the smallest safe fix**
| Situation | Fix |
|---|---|
| UI-bound type/method | Add `@MainActor` annotation |
| Protocol conformance on MainActor type | Use isolated conformance: `extension Foo: @MainActor Proto` |
| Mutable shared state | Move into an actor or protect with lock |
| Background work needed | Use `@concurrent async` function |
| Sendable error | Use immutable value types, add `Sendable` only when proven safe |

**Step 3: Verify**
- Rebuild and confirm error is resolved
- Check for new warnings introduced
- Ensure no unjustified `@unchecked Sendable`

**Example workflow:**
```swift
// WRONG - shared mutable state on multiple actors
class DataCache {
    var items: [Item] = []  // error: property not isolated
}

// FIX 1 - isolate to MainActor
@MainActor
class DataCache {
    var items: [Item] = []
}

// FIX 2 - use an actor instead
actor DataCache {
    private var items: [Item] = []
    func getItems() -> [Item] { items }
}
```

### AsyncSequence and AsyncStream

Bridge callback/delegate patterns to async/await:

**Correct pattern:**
```swift
// Convert delegate callbacks to AsyncStream
let locationStream = AsyncStream<Location> { continuation in
    let delegate = LocationDelegate { location in
        continuation.yield(location)
    }
    continuation.onTermination = { _ in delegate.stop() }
    delegate.start()
}

// Consume the stream
for await location in locationStream {
    updateMapView(with: location)
}

// Single-value callbacks with checked continuation
func fetchUserAsync(id: String) async throws -> User {
    return try await withCheckedThrowingContinuation { continuation in
        fetchUser(id: id) { result in
            continuation.resume(with: result)  // Resume exactly once
        }
    }
}
```

**Rules:**
- ✅ Resume continuation exactly once (crash if more than once)
- ✅ Use `onTermination` to clean up resources
- ✅ Use `withCheckedContinuation` for single-value callbacks
- ❌ Never resume after `onTermination` fires

### Synchronization Primitives: Mutex vs OSAllocatedUnfairLock vs Atomic

When actors are not the right fit (synchronous access, perf-critical paths, C/ObjC bridging):

**Decision guide with code examples:**

```swift
// MUTEX<VALUE> (iOS 18+) - Preferred for new code
import Synchronization

// Stores protected value inside lock
@MainActor
class Cache {
    private let cache = Mutex<[String: String]>([:])

    func getValue(_ key: String) -> String? {
        cache.withLock { $0[key] }
    }

    func setValue(_ value: String, for key: String) {
        cache.withLock { $0[key] = value }
    }
}

// OSALLOCATEDUNFAIRLOCK (iOS 16+) - Use for older targets
import os

class ReferenceCache {
    private let lock = os.unfair_lock()
    private var _items: [String] = []

    var items: [String] {
        get {
            lock.lock()
            defer { lock.unlock() }
            return _items
        }
        set {
            lock.lock()
            defer { lock.unlock() }
            _items = newValue
        }
    }
}

// ATOMIC<VALUE> (iOS 18+) - Lock-free for simple counters/flags
import Synchronization

class OperationTracker {
    private let completedCount = Atomic<Int>(0)

    func increment() {
        completedCount.wrappingIncrementThenLoad(ordering: .sequentiallyConsistent)
    }

    func getCount() -> Int {
        completedCount.load(ordering: .sequentiallyConsistent)
    }
}

// AVOID - Never use locks inside actors (double synchronization)
actor BadCache {
    private let lock = os.unfair_lock()  // ❌ WRONG
    private var items: [String] = []
}
```

**When to use each:**
- **Mutex**: Default choice for iOS 18+, stores value inside lock, clean API
- **OSAllocatedUnfairLock**: Supporting iOS 16-17, lower overhead
- **Atomic**: Lock-free atomics for simple integers/flags, requires memory ordering knowledge
- **Actors**: When entire type manages state, inheritance needed, or no synchronous access required

### Explicit GCD Prohibition

**CRITICAL:** Never use Grand Central Dispatch APIs. GCD has no data-race safety guarantees.

**Prohibited APIs:**
```swift
// ❌ NEVER use these
DispatchQueue.main.async { }
DispatchQueue.global().sync { }
DispatchGroup()
DispatchSemaphore()
DispatchWorkItem()
```

**Replacements:**
```swift
// WRONG - using GCD
DispatchQueue.main.async { updateUI() }

// RIGHT - use Task on MainActor
Task { @MainActor in updateUI() }

// WRONG - using semaphore
let sem = DispatchSemaphore(value: 0)
background { sem.signal() }
sem.wait()

// RIGHT - use async/await
let result = await backgroundWork()

// WRONG - using DispatchGroup
let group = DispatchGroup()
group.enter()
api.fetch { group.leave() }
group.wait()

// RIGHT - use TaskGroup
try await withThrowingTaskGroup(of: Data.self) { group in
    for url in urls {
        group.addTask { try await api.fetch(url) }
    }
}
```

### Common Concurrency Mistakes (8 Additional)

Beyond blocking, unnecessary `@MainActor`, and semaphores:

1. **Using GCD APIs (DispatchQueue, DispatchGroup, DispatchSemaphore).** These have no data-race safety. Use Task, TaskGroup, and async/await instead.

2. **Blocking the main actor with sync computation.** Even non-UI work on `@MainActor` blocks UI. Move heavy computation to `@concurrent` functions.

3. **Forgetting to cancel stored Task references.** Store `Task` handles and cancel in `deinit` or use `.task` view modifier in SwiftUI.

4. **Task.detached without good reason.** Detached tasks lose priority inheritance, task-local values, and cancellation propagation. Use only when explicitly breaking isolation.

5. **Retain cycles in long-lived tasks.** Capture `[weak self]` in tasks that live longer than their closure (e.g., stored properties).

6. **Mixing actor and non-actor state in one type.** Don't have both `@MainActor` properties and `nonisolated` properties in the same class—isolate the entire type.

7. **Assuming actor reentrancy.** State can change across `await` points. Never read, then await, then use (state may have changed). Mutate synchronously.

8. **Using `@preconcurrency` without a removal plan.** Document why the import is needed and when it can be removed.

### Actor Reentrancy — The #1 LLM Bug

After every `await` inside an actor, ALL state assumptions are invalidated. Other calls may have executed during the suspension. This is the most common concurrency bug that AI generates.

```swift
// WRONG — check-then-act across await (stale state)
actor ImageCache {
  var cache: [URL: Image] = [:]

  func image(for url: URL) async -> Image {
    if let cached = cache[url] { return cached }
    let downloaded = await download(url)  // ⚠️ another caller may have set cache[url] during this await
    cache[url] = downloaded  // may overwrite a newer version
    return downloaded
  }
}

// CORRECT — capture result locally, then assign
actor ImageCache {
  var cache: [URL: Image] = [:]
  private var inFlight: [URL: Task<Image, Error>] = [:]

  func image(for url: URL) async throws -> Image {
    if let cached = cache[url] { return cached }
    if let existing = inFlight[url] { return try await existing.value }

    let task = Task { try await download(url) }
    inFlight[url] = task
    let result = try await task.value
    cache[url] = result
    inFlight[url] = nil
    return result
  }
}
```

**Key rule:** Never force-unwrap after `await` in actors — if another caller set a value to `nil` during suspension, you crash.

### Bug Patterns: 10 Common Concurrency Failures

1. **Check-then-act across await** — State assumed valid after suspension. Fix: capture result locally first.
2. **Continuation resumed 0 times** — Causes permanent hang. Audit every code path in `withCheckedContinuation` to ensure exactly one resume.
3. **Continuation resumed 2+ times** — Runtime crash. Guard with Bool flag or use actor to serialize.
4. **Unstructured tasks in loops** — `for item in items { Task { } }` has no cancellation propagation, no error collection. Use `withTaskGroup` instead.
5. **Swallowed errors in Task** — Errors silently lost inside `Task { }`. Handle errors inside the closure or use `Task<Void, Error>`.
6. **Blocking MainActor with CPU work** — Freezes UI. Use `@concurrent` or move to task group.
7. **Unbounded AsyncStream buffer** — Memory grows without limit. Always specify `.bufferingNewest(n)` or `.bufferingOldest(n)`.
8. **Ignoring CancellationError** — Retries on normal lifecycle events. Filter `CancellationError` before retry logic.
9. **@unchecked Sendable hiding races** — Silences compiler but data race still exists at runtime. Restructure with value types or actors.
10. **Force unwrap after await in actor** — Can crash if another caller set value to nil during suspension.

### Structured Concurrency Patterns

**async let vs Task Groups:**
- `async let` — fixed number of different-type operations
- `withTaskGroup` — dynamic number of same-type operations
- `withDiscardingTaskGroup` — fire-and-forget child tasks (Swift 5.9+)

```swift
// async let — fixed, different types
async let profile = fetchProfile(id)
async let posts = fetchPosts(for: id)
let (p, ps) = try await (profile, posts)

// Task group — dynamic, same type
let images = try await withThrowingTaskGroup(of: UIImage.self) { group in
  for url in urls {
    group.addTask { try await downloadImage(url) }
  }
  return try await group.reduce(into: []) { $0.append($1) }
}
```

**Limiting concurrency in task groups:**
```swift
await withTaskGroup(of: Void.self) { group in
  var iterator = urls.makeIterator()
  // Start initial batch
  for _ in 0..<maxConcurrent {
    guard let url = iterator.next() else { break }
    group.addTask { await process(url) }
  }
  // As each finishes, start next
  for await _ in group {
    if let url = iterator.next() {
      group.addTask { await process(url) }
    }
  }
}
```

### AsyncStream Patterns

```swift
// Modern factory (preferred)
let (stream, continuation) = AsyncStream.makeStream(of: Event.self)

// Always specify buffer policy for high-throughput streams
let (stream, continuation) = AsyncStream.makeStream(
  of: Event.self,
  bufferingPolicy: .bufferingNewest(100)
)

// Cleanup on consumer stop
continuation.onTermination = { _ in
  sensor.stopMonitoring()
}

// Finish exactly once
continuation.finish()
```

### Request ID Gating — Preventing Stale Response Overwrites

Task cancellation stops in-flight work, but **doesn't prevent out-of-order responses**. When a user triggers rapid sequential requests (typing in search, pull-to-refresh while loading), a slower first response can overwrite a newer second response. This is distinct from cancellation — both patterns are needed.

```swift
// WRONG — stale overwrite: slow Response 1 arrives after fast Response 2
func search(_ query: String) async {
  let results = try? await api.search(query)
  self.results = results  // overwrites newer results!
}

// CORRECT — request ID gating + cancellation
@Observable @MainActor
final class SearchViewModel {
  var results: [Item] = []
  private var currentRequestID = UUID()
  private var searchTask: Task<Void, Never>?

  func search(_ query: String) {
    searchTask?.cancel()  // cancel previous work
    let requestID = UUID()
    currentRequestID = requestID  // stamp this request

    searchTask = Task {
      try? await Task.sleep(for: .milliseconds(300))  // debounce
      guard !Task.isCancelled else { return }
      let fetched = try? await api.search(query)
      guard currentRequestID == requestID else { return }  // stale guard
      results = fetched ?? []
    }
  }
}
```

**Key distinction:** `Task.cancel()` stops work that hasn't finished. Request ID gating rejects results that arrive after a newer request was issued. Use both.

### Cancellation-First Checklist

Every async entry point in your code should have explicit cancellation handling:
- `.task {}` — handled automatically by SwiftUI (cancels on disappear)
- Stored `Task` property — cancel in `deinit`, or before starting new work
- `TaskGroup` children — cancelled when parent is cancelled
- `AsyncStream` — set `onTermination` handler for cleanup
- `withCheckedContinuation` — must resume exactly once, even on cancellation

### Cancellation Patterns

- **Structured tasks:** parent cancels all children automatically.
- **Unstructured tasks:** you must cancel explicitly — store the `Task` handle.
- **SwiftUI `.task()`:** auto-cancels when view disappears.
- Use `Task.checkCancellation()` (throws) in loops, or `Task.isCancelled` (returns Bool).
- `withTaskCancellationHandler` bridges Swift cancellation to APIs with their own cancel mechanism.
- **Never catch and ignore `CancellationError`** — it's a normal lifecycle signal.

### Bridging Legacy Code

| Legacy Pattern | Modern Replacement |
|---|---|
| Completion handler | `withCheckedThrowingContinuation` (resume exactly once!) |
| Delegate callbacks | `AsyncStream` with `onTermination` cleanup |
| `DispatchQueue.main.async` | `@MainActor` |
| `DispatchQueue.global().async` | `@concurrent` or task group |
| Serial `DispatchQueue` | `actor` |
| Combine publisher | `AsyncSequence` |

### Concurrency Diagnostics Quick Reference

| Compiler Error | Fix (in priority order) |
|---|---|
| "cannot be sent to non-isolated context" | 1. Make type `Sendable` (value type or immutable) 2. Use actor isolation 3. Last resort: `@unchecked Sendable` with internal locking |
| "actor-isolated property cannot be referenced from non-isolated context" | 1. Mark caller `@MainActor` 2. Use `await` 3. Mark property `nonisolated` if safe |
| "capture of mutable var in Sendable closure" | 1. Copy to `let` before capture 2. Use actor |
| "call to MainActor-isolated function in non-isolated context" | 1. Mark caller `@MainActor` 2. Use `await` |

### Swift 6.3 Updates

Swift 6.3 (Xcode 26.4, March 2026) adds:
- **`@c` attribute** — expose Swift functions/enums to C code (embedded/systems programming).
- **`@specialize`** — provide pre-specialized implementations of generic APIs for common types.
- **`@inline(always)`** — guarantee function inlining for direct calls.
- **Android SDK** — first stable Swift SDK for Android development.

These are primarily library-author and cross-platform features. No changes to concurrency model or actor isolation rules from Swift 6.2.

---

## Section 2b: Codable

Codable is Swift's standard for serialization. Master it to avoid runtime crashes and data corruption.

### JSONDecoder/JSONEncoder Setup

Configuration at initialization prevents subtle bugs.

**Correct pattern:**
```swift
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase  // api_key → apiKey
decoder.dateDecodingStrategy = .iso8601              // 2026-03-21T10:00:00Z
decoder.userInfo[CodingUserInfoKey.context] = managedObjectContext

let encoder = JSONEncoder()
encoder.keyEncodingStrategy = .convertToSnakeCase
encoder.dateEncodingStrategy = .iso8601
encoder.outputFormatting = .prettyPrinted            // For debugging

do {
    let data = try encoder.encode(user)
    let decoded = try decoder.decode(User.self, from: data)
} catch {
    print("Coding error: \(error)")
}
```

**Common Mistakes:**
- ❌ Not setting `keyDecodingStrategy` when API uses snake_case
- ❌ Using default date strategy for ISO8601 timestamps (will crash)
- ✅ Always configure decoder/encoder at point of use
- ✅ Document which strategy to use in type comments

### Custom CodingKeys

CodingKeys map JSON keys to property names, essential when API and Swift naming differ.

**Correct pattern:**
```swift
struct APIResponse: Codable {
    let userId: String
    let userName: String
    let createdAt: Date
    let isActive: Bool

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case userName = "user_name"
        case createdAt = "created_at"
        case isActive = "is_active"
    }
}

// Decodes: { "user_id": "123", "user_name": "Alice", ... }
```

**Common Mistakes:**
- ❌ Adding one property to CodingKeys but not all (other properties won't decode)
- ❌ Typos in key names — decoding silently fails with default values
- ✅ Include ALL properties that need custom key mapping
- ✅ Use `rawValue` parameter only when JSON key differs from Swift name

### Custom init(from:) and encode(to:)

For complex transformations or conditional logic.

**Correct pattern:**
```swift
struct User: Codable {
    let id: UUID
    let email: String
    let role: UserRole

    init(from decoder: any Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        // Decode UUID from string
        let idString = try container.decode(String.self, forKey: .id)
        guard let id = UUID(uuidString: idString) else {
            throw DecodingError.dataCorrupted(
                DecodingError.Context(
                    codingPath: [CodingKeys.id],
                    debugDescription: "Invalid UUID format"
                )
            )
        }

        self.id = id
        self.email = try container.decode(String.self, forKey: .email)

        // Default to .user if role missing
        let roleString = try container.decodeIfPresent(String.self, forKey: .role) ?? "user"
        self.role = UserRole(rawValue: roleString) ?? .user
    }

    func encode(to encoder: any Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id.uuidString, forKey: .id)
        try container.encode(email, forKey: .email)
        try container.encode(role.rawValue, forKey: .role)
    }

    enum CodingKeys: String, CodingKey {
        case id, email, role
    }
}
```

**Common Mistakes:**
- ❌ Throwing generic errors instead of `DecodingError`
- ❌ Forgetting to handle all properties in init(from:)
- ✅ Provide meaningful error context with `debugDescription`
- ✅ Mirror encode/decode logic (they should handle the same data)

### Nested Containers & Optional/Null Handling

Real APIs often have nested objects and nullable fields.

**Correct pattern:**
```swift
struct Profile: Codable {
    let user: UserInfo
    let settings: [String: Bool]?
    let metadata: Metadata?

    struct UserInfo: Codable {
        let id: String
        let email: String
    }
}

struct APIResponse: Codable {
    let profile: Profile

    init(from decoder: any Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        // Nested object
        let userContainer = try container.nestedContainer(
            keyedBy: UserInfoKeys.self,
            forKey: .user
        )
        let id = try userContainer.decode(String.self, forKey: .id)
        let email = try userContainer.decode(String.self, forKey: .email)
        let userInfo = Profile.UserInfo(id: id, email: email)

        // Optional nested
        let settings = try container.decodeIfPresent([String: Bool].self, forKey: .settings)
        let metadata = try container.decodeIfPresent(Metadata.self, forKey: .metadata)

        self.profile = Profile(user: userInfo, settings: settings, metadata: metadata)
    }

    enum CodingKeys: String, CodingKey {
        case user, settings, metadata
    }

    enum UserInfoKeys: String, CodingKey {
        case id, email
    }
}
```

**Common Mistakes:**
- ❌ Using `decode(_:forKey:)` for optional fields (will crash if null)
- ❌ Not using `nestedContainer(keyedBy:forKey:)` for nested objects
- ✅ Use `decodeIfPresent` for optional fields
- ✅ Always nest containers for complex JSON structures

### Lossy Array Decoding

By default, one invalid array element fails the entire decode. Use a wrapper to skip invalid elements:

**Correct pattern:**
```swift
// Wrapper that skips invalid elements
struct LossyArray<Element: Decodable>: Decodable {
    let elements: [Element]

    init(from decoder: Decoder) throws {
        var container = try decoder.unkeyedContainer()
        var elements: [Element] = []

        while !container.isAtEnd {
            if let element = try? container.decode(Element.self) {
                elements.append(element)
            } else {
                // Advance past bad element
                _ = try? container.decode(AnyCodableValue.self)
            }
        }
        self.elements = elements
    }
}

private struct AnyCodableValue: Decodable {}

// Usage: API sends array with invalid items mixed in
struct APIResponse: Decodable {
    let items: [Item]  // If one item is corrupt, entire decode fails
    let tags: LossyArray<String>  // Invalid tags are skipped
}

let response = try decoder.decode(APIResponse.self, from: data)
let validTags = response.tags.elements
```

**Common Mistakes:**
- ❌ Failing entire array when one element is invalid
- ✅ Use `LossyArray` wrapper for arrays that may contain invalid items
- ✅ Only apply to data sources you don't fully control

### Single Value Containers

Wrap primitives for type safety using `singleValueContainer()`:

**Correct pattern:**
```swift
// Create a strongly-typed wrapper
struct UserID: Codable, Hashable {
    let rawValue: String

    init(_ rawValue: String) { self.rawValue = rawValue }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        rawValue = try container.decode(String.self)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(rawValue)
    }
}

// Usage
let json = #"{ "id": "usr_abc123", "name": "Alice" }"#
let data = json.data(using: .utf8)!
let user = try JSONDecoder().decode(User.self, from: data)
// user.id is UserID, type-safe and encoded directly as "usr_abc123"
```

**Common Mistakes:**
- ❌ Using `String` directly instead of wrapper types for IDs
- ✅ Use single value containers for wrapper types
- ✅ Provides type safety without extra JSON structure

### Default Values with decodeIfPresent

Use `decodeIfPresent` with nil-coalescing to provide defaults:

**Correct pattern:**
```swift
struct Settings: Decodable {
    let theme: String
    let fontSize: Int
    let notificationsEnabled: Bool

    enum CodingKeys: String, CodingKey {
        case theme, fontSize = "font_size"
        case notificationsEnabled = "notifications_enabled"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        // Use default if key is missing
        theme = try container.decodeIfPresent(String.self, forKey: .theme) ?? "system"
        fontSize = try container.decodeIfPresent(Int.self, forKey: .fontSize) ?? 16
        notificationsEnabled = try container.decodeIfPresent(
            Bool.self, forKey: .notificationsEnabled) ?? true
    }
}

// JSON: { "theme": "dark" }
// fontSize and notificationsEnabled use defaults
```

**Common Mistakes:**
- ❌ Using `decode(_:forKey:)` for optional fields (crashes if missing)
- ✅ Always use `decodeIfPresent` with nil-coalescing for defaults
- ✅ Document default values in type comments

### Codable with SwiftData (iOS 18+)

In iOS 18+, SwiftData natively supports `Codable` structs as composite attributes without explicit transformation:

**Correct pattern:**
```swift
// Codable value type
struct Address: Codable {
    var street: String
    var city: String
    var zipCode: String
    var country: String = "USA"  // Optional default
}

// SwiftData model uses Codable struct directly
@Model final class Contact {
    var name: String
    var address: Address?  // Automatically stored as composite attribute
    var alternateAddresses: [Address] = []  // Even arrays of Codable types work

    init(name: String, address: Address? = nil) {
        self.name = name
        self.address = address
    }
}

// No extra annotation needed in iOS 18+
// In iOS 17 and earlier, use @Attribute(.transformable)
```

**Benefits:**
- ✅ No boilerplate `@Attribute(.transformable)` in iOS 18+
- ✅ Arrays of Codable types are supported
- ✅ Optional Codable properties work seamlessly
- ❌ Pre-iOS 18, must use `@Attribute(.transformable)` annotation

### keyDecodingStrategy Trade-off: convertFromSnakeCase vs Manual CodingKeys

When APIs use snake_case, decide between automatic conversion and explicit control:

**Automatic conversion (simple APIs):**
```swift
struct User: Decodable {
    let id: Int
    let firstName: String
    let lastName: String
    let createdAt: Date
    // No CodingKeys needed
}

let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase  // snake_case → camelCase
decoder.dateDecodingStrategy = .iso8601
// JSON: { "id": 1, "first_name": "Alice", "last_name": "Smith", "created_at": "2024-03-15T..." }
```

**Manual CodingKeys (complex APIs, overrides, validation):**
```swift
struct User: Decodable {
    let id: Int
    let firstName: String
    let email: String  // Email has special validation
    let timestamp: Date

    enum CodingKeys: String, CodingKey {
        case id
        case firstName = "first_name"
        case email
        case timestamp = "created_at"  // API key differs from snake_case
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        firstName = try container.decode(String.self, forKey: .firstName)

        // Custom validation on email
        let rawEmail = try container.decode(String.self, forKey: .email)
        guard rawEmail.contains("@") else {
            throw DecodingError.dataCorruptedError(forKey: .email, in: container,
                debugDescription: "Invalid email format")
        }
        email = rawEmail

        timestamp = try container.decode(Date.self, forKey: .timestamp)
    }
}
```

**Trade-off decision:**
| Scenario | Use |
|---|---|
| All fields are snake_case, no validation | `keyDecodingStrategy = .convertFromSnakeCase` |
| Mixed naming or special fields | Manual `CodingKeys` |
| Need custom validation or transformation | Manual `init(from:)` with `CodingKeys` |
| API is inconsistent (e.g., some camelCase) | Manual `CodingKeys` for clarity |

**Common Mistakes:**
- ❌ Over-using `keyDecodingStrategy` when few fields differ
- ❌ Using strategy but forgetting to apply it to decoder
- ✅ Use strategy for consistent APIs, manual keys for complex ones
- ✅ Document which strategy is in use

### Review Checklist
- [ ] All CodingKeys entries match JSON response
- [ ] Date strategy configured (ISO8601 or custom)
- [ ] All required fields use `decode`, optional fields use `decodeIfPresent`
- [ ] Custom init/encode mirrors each other
- [ ] Error messages in DecodingError include field name
- [ ] Lossy arrays use `LossyArray<T>` wrapper for unreliable data
- [ ] Single value containers used for wrapper types (UserID, etc.)
- [ ] `decodeIfPresent` with nil-coalescing used for defaults
- [ ] Codable structs used as composite attributes in SwiftData (iOS 18+)
- [ ] `keyDecodingStrategy = .convertFromSnakeCase` used vs manual CodingKeys trade-off decided

---

## Section 3: Swift Testing (iOS 18+)

Swift Testing replaces XCTest with a modern, async-first approach.

### @Test Macro & Basic Assertions

Swift Testing uses the `@Test` macro and `#expect`/`#require` for assertions.

**Correct pattern:**
```swift
import Testing

struct LoginTests {
    @Test
    func validCredentialsLogin() async throws {
        let user = try await login(email: "test@example.com", password: "secure123")
        #expect(user.email == "test@example.com")
    }

    @Test
    func invalidEmailThrows() async throws {
        try #require(throws: LoginError.invalidEmail) {
            _ = try await login(email: "invalid", password: "pass")
        }
    }

    @Test
    func networkTimeout() async throws {
        let result = try await loginWithTimeout(seconds: 0.1)
        #expect(result == .timedOut)
    }
}
```

**#expect vs #require:**
- `#expect` - Assertion continues on failure, records error
- `#require` - Assertion stops test on failure, for critical conditions

**Common Mistakes:**
- ❌ Using XCTest assertions like `XCTAssertEqual` (incompatible with Swift Testing)
- ❌ Not marking async tests with `async`
- ✅ Use `#expect(condition)` for soft assertions
- ✅ Use `#require(condition)` for conditions that must hold

### @Suite & Test Organization

Suites group related tests with shared setup/teardown.

**Correct pattern:**
```swift
@Suite("User Model Tests")
struct UserModelTests {
    var testUser: User!

    init() {
        testUser = User(id: "1", name: "Alice")
    }

    @Test
    func userIdNotEmpty() {
        #expect(!testUser.id.isEmpty)
    }

    @Test
    func userNameCapitalized() {
        #expect(testUser.name.first?.isUppercase ?? false)
    }
}

// Nested suites
@Suite
struct ValidationTests {
    @Suite
    struct EmailValidationTests {
        @Test
        func validEmail() {
            #expect(isValidEmail("test@example.com"))
        }
    }
}
```

**Common Mistakes:**
- ❌ Mixing test logic in suite initializer (should only set up state)
- ❌ Sharing mutable state between test methods (use separate instances)
- ✅ Use suite names to describe test category
- ✅ Reset shared state in init for each test

### Parameterized Tests with Cartesian Products

Run the same test with multiple input values. Two argument collections create a cartesian product (every combination):

**Correct pattern:**
```swift
@Test("Validate email formats", arguments: [
    ("valid@example.com", true),
    ("invalid.email", false),
    ("test@domain.co.uk", true),
    ("@example.com", false),
])
func validateEmails(email: String, expected: Bool) {
    let result = isValidEmail(email)
    #expect(result == expected)
}

// With custom types
struct TestCase: Sendable {
    let input: String
    let expected: Int
}

@Test("Parse numbers", arguments: [
    TestCase(input: "123", expected: 123),
    TestCase(input: "-456", expected: -456),
])
func parseNumbers(testCase: TestCase) {
    let result = Int(testCase.input)
    #expect(result == testCase.expected)
}

// Cartesian product: every combination
@Test("Snapshot rendering", arguments: ["light", "dark"], ["iPhone", "iPad"])
func renderSnapshot(colorScheme: String, device: String) {
    // Runs 4 combinations: light+iPhone, light+iPad, dark+iPhone, dark+iPad
    let config = SnapshotConfig(scheme: colorScheme, device: device)
    #expect(config.isValid)
}

// 1:1 pairing with zip (avoid cartesian product)
@Test("HTTP status codes", arguments: zip([200, 201, 204], ["OK", "Created", "No Content"]))
func httpStatus(code: Int, description: String) {
    // Runs 3 cases: (200, "OK"), (201, "Created"), (204, "No Content")
    #expect(HTTPStatus(code).description == description)
}
```

**Common Mistakes:**
- ❌ Creating parameterized tests with only 1-2 cases (use simple tests instead)
- ❌ Two argument collections create cartesian product (4 tests, not 2)
- ✅ Use `zip()` for 1:1 pairing when you don't want all combinations
- ✅ Use cartesian product when testing all combinations matters

### Traits

Traits customize test behavior.

**Correct pattern:**
```swift
@Test(.disabled("Waiting for backend API"))
func futureFeatureTest() {
    // Test code won't run
}

@Test(.bug("https://github.com/issue/123"))
func knownFailingTest() {
    // Marked as known bug, failure expected
    #expect(false)
}

@Test(.timeLimit(.seconds(2)))
func performanceTest() {
    let start = Date()
    expensiveOperation()
    let elapsed = Date().timeIntervalSince(start)
    #expect(elapsed < 2)
}

@Test(.enabled(if: ProcessInfo.processInfo.environment["CI"] == "true"))
func onlyCITest() {
    // Only runs in CI environment
}
```

**Common Traits:**
- `.disabled(String)` - Skip test with reason
- `.bug(String)` - Mark as known issue
- `.timeLimit(Duration)` - Enforce time constraint
- `.enabled(if: Bool)` - Conditional execution
- `.serialized` - Run test sequentially (default is parallel)

### Async Test Support

Swift Testing is async-first.

**Correct pattern:**
```swift
@Test
func fetchUserAsync() async throws {
    let user = try await fetchUser(id: "123")
    #expect(user.name == "Alice")
}

@Test
func multipleAsyncOperations() async throws {
    async let user = fetchUser(id: "1")
    async let posts = fetchPosts(userId: "1")

    let (userData, postData) = try await (user, posts)
    #expect(userData.id == "1")
    #expect(!postData.isEmpty)
}

@Test
func withAsyncSequence() async throws {
    var count = 0
    for try await item in fetchItems() {
        count += 1
    }
    #expect(count > 0)
}
```

**Common Mistakes:**
- ❌ Not marking async tests with `async`
- ❌ Blocking async code with `wait()` instead of `await`
- ✅ Always use `await` for async calls
- ✅ Use `async let` for concurrent operations

### Confirmation Pattern (Replacing XCTestExpectation)

Use `confirmation()` to verify callbacks/delegates are called the expected number of times:

**Correct pattern:**
```swift
@Test("Notification fires on login")
func notificationPosted() async throws {
    try await confirmation("UserDidLogin notification", expectedCount: 1) { confirm in
        let center = NotificationCenter.default
        let observer = center.addObserver(
            forName: .userDidLogin, object: nil, queue: .main
        ) { _ in
            confirm()  // Called when notification is posted
        }

        await loginService.login(user: "test", password: "pass")
        center.removeObserver(observer)
    }
}

@Test("Batch processor calls delegate for each item")
func batchProcessing() async throws {
    try await confirmation("Items processed", expectedCount: 3) { confirm in
        let processor = BatchProcessor()
        processor.onItemComplete = { _ in confirm() }

        await processor.process(items: [item1, item2, item3])
    }
}

// Default expectedCount is 1
@Test("Single callback")
func singleCallback() async throws {
    try await confirmation("Callback fired") { confirm in
        someAsyncAPI { _ in confirm() }
    }
}
```

**Common Mistakes:**
- ❌ Using `Task.sleep()` to wait for callbacks
- ❌ Not specifying `expectedCount` when expecting multiple calls
- ✅ Use `confirmation()` with expected count instead of sleep
- ✅ Confirmation fails if count doesn't match (test fails safely)

### Custom Test Argument Generators

Create parameterized test arguments with `CustomTestArgumentProviding`:

**Correct pattern:**
```swift
struct APIEndpoint: Sendable {
    let path: String
    let method: String
    let expectedStatus: Int

    // Static test cases property
    static let testCases: [APIEndpoint] = [
        .init(path: "/users", method: "GET", expectedStatus: 200),
        .init(path: "/users", method: "POST", expectedStatus: 201),
        .init(path: "/missing", method: "GET", expectedStatus: 404),
    ]
}

@Test("API returns expected status", arguments: APIEndpoint.testCases)
func apiStatus(endpoint: APIEndpoint) async throws {
    let response = try await client.request(endpoint.method, to: endpoint.path)
    #expect(response.statusCode == endpoint.expectedStatus)
}

// With custom ArgumentProvider conformance
struct ValidationScenario: CustomTestArgumentProviding, Sendable {
    let input: String
    let shouldPass: Bool

    static var testArguments: [ValidationScenario] {
        [
            .init(input: "valid@example.com", shouldPass: true),
            .init(input: "invalid.email", shouldPass: false),
            .init(input: "", shouldPass: false),
        ]
    }
}

@Test("Email validation", arguments: ValidationScenario.testArguments)
func validateEmail(scenario: ValidationScenario) {
    let result = isValidEmail(scenario.input)
    #expect(result == scenario.shouldPass)
}
```

**Common Mistakes:**
- ❌ Hard-coding test cases inline instead of creating reusable data
- ✅ Use static properties on custom types for test data
- ✅ Make argument types Sendable for concurrency

### Custom Traits with TestScoping

Create reusable traits for common test setup/teardown patterns:

**Correct pattern:**
```swift
struct DatabaseTrait: TestTrait, SuiteTrait, TestScoping {
    func provideScope(
        for test: Test,
        testCase: Test.Case?,
        performing function: @Sendable () async throws -> Void
    ) async throws {
        let db = try await TestDatabase.setUp()
        defer { Task { await db.tearDown() } }
        try await function()
    }
}

// Register extension for easy use
extension Trait where Self == DatabaseTrait {
    static var database: Self { .init() }
}

// Usage: tests get fresh database automatically
@Test(.database)
func insertUser() async throws { ... }

@Suite(.database)
struct DatabaseTests {
    @Test func create() async throws { ... }
    @Test func delete() async throws { ... }
}
```

**Benefits:**
- ✅ Consolidate setup/teardown logic in one place
- ✅ Reuse across multiple tests
- ✅ Async setup and cleanup
- ❌ Don't repeat setup code in each test

### withKnownIssue for Expected Failures

Mark expected failures (including intermittent ones) so they don't cause test failure:

**Correct pattern:**
```swift
@Test
func networkTimeout() async throws {
    withKnownIssue("Server occasionally drops connections") {
        #expect(service.isReachable)
    }
}

// Intermittent / flaky failures
@Test
func flakyAsyncOperation() async throws {
    withKnownIssue(isIntermittent: true) {
        let result = try await flakeyAPI.fetch()
        #expect(!result.isEmpty)
    }
}

// Conditional known issue
@Test
func propaneTest() async {
    withKnownIssue {
        #expect(truck.grill.isHeating)
    } when: {
        !hasPropane
    }
}
```

**Important:**
- ✅ Mark expected failures so test suite still passes
- ✅ Record distinct issue when known issue is actually fixed
- ❌ Don't use to hide real bugs; fix them

### Exit Testing

Test code paths that call `exit()`, `fatalError()`, or `preconditionFailure()`:

**Correct pattern:**
```swift
@Test func invalidInputCausesExit() async {
    await #expect(processExitsWith: .failure) {
        processInvalidInput()  // calls fatalError() internally
    }
}

@Test func successfulExit() async {
    await #expect(processExitsWith: .success) {
        runSuccessfulProcess()  // calls exit(0)
    }
}

@Test func preconditionFailure() async {
    await #expect(processExitsWith: .failure) {
        validatePrecondition()  // calls preconditionFailure()
    }
}
```

**Common Mistakes:**
- ❌ Not testing fatal error paths
- ✅ Use `processExitsWith` to verify exit codes
- ✅ Test both success (exit 0) and failure paths

### Migration from XCTest

Swift Testing is backward compatible but has different patterns.

**XCTest → Swift Testing:**
```swift
// Old XCTest
func testLogin() {
    let expectation = expectation(description: "Login completes")
    loginAsync { result in
        XCTAssertNotNil(result)
        expectation.fulfill()
    }
    waitForExpectations(timeout: 5)
}

// New Swift Testing
@Test
func login() async throws {
    let result = try await loginAsync()
    #expect(result != nil)
}
```

Use `import Testing` (not `XCTest`) in new tests. Gradually migrate old tests to new syntax.

**Common Mistakes:**
- ❌ Mixing Swift Testing and XCTest assertions in same file
- ❌ Using `XCTAssertEqual` instead of `#expect`
- ✅ Create new tests with `@Test` macro
- ✅ Migrate critical test files first, non-critical later

### Testing Gotchas — Common Agent Mistakes

**.serialized only works on parameterized tests:**
```swift
// WRONG — .serialized on a suite does NOT serialize regular tests
@Suite(.serialized)
struct MyTests {
  @Test func testA() { }  // Still runs in parallel with testB!
  @Test func testB() { }
}

// CORRECT — .serialized on parameterized test
@Suite(.serialized)
struct MyTests {
  @Test(arguments: [1, 2, 3])
  func testValues(value: Int) { }  // These run serially
}
```

**confirmation() must complete before returning:**
```swift
// WRONG — fire-and-forget, confirmation may not trigger
await confirmation { confirm in
  service.onComplete = { confirm() }
  service.start()
  // returns immediately, service hasn't finished
}

// CORRECT — await the work inside the closure
await confirmation { confirm in
  service.onComplete = { confirm() }
  await service.startAndWait()  // wait for completion
}
```

**Time limits use .minutes(), not .seconds():**
```swift
@Test(.timeLimit(.minutes(1)))  // ✓
@Test(.timeLimit(.seconds(30)))  // ✗ Does not compile
```

**Don't negate Booleans with ! in #expect:**
```swift
// WRONG — defeats macro expansion, poor diagnostics
#expect(!array.isEmpty)

// CORRECT — clear diagnostics on failure
#expect(array.isEmpty == false)
```

**Tests without expectations pass silently** — if no `#expect`/`#require` is hit, the test passes. Ensure every test has at least one assertion.

**No float tolerance built-in** — use Swift Numerics: `#expect(value.isApproximatelyEqual(to: expected, absoluteTolerance: 0.001))`

### Testing Best Practices

**Parallel-safe by default:**
- Assume all tests run in parallel. Each must be independent.
- Fix shared state before reaching for `.serialized`.
- Use `init()` for per-test setup (structs preferred over classes for test suites).

**#expect vs #require:**
- `#expect` — assertion, test continues on failure.
- `#require` — precondition, test stops on failure. Use for setup steps.

```swift
@Test func userCanUpdateProfile() throws {
  let user = try #require(await fetchUser(id: 1))  // stops if nil
  user.name = "New Name"
  try await user.save()
  #expect(user.name == "New Name")  // continues on failure
}
```

**Traits over naming conventions:**
- Use `@available` on individual `@Test` functions, not runtime `#available` inside tests.
- Use `.enabled(if:)`, `.disabled()`, `.timeLimit()`, `.bug(id:)` traits for metadata.
- Define custom tags: `extension Tag { @Tag static var networking: Self }` for cross-suite filtering.

**XCTest carve-outs** (keep XCTest for these):
- UI automation (`XCUIApplication`)
- Performance metrics (`XCTMetric`)
- Objective-C-only test code

**Never use Task.sleep() as a test wait mechanism** — await the actual operation instead.

**Test @Observable view models directly** — no need for protocols or mocks. Test the class, not the view.

**Deterministic async testing — no sleeps, no flakiness:**

Use `CheckedContinuation` to control when async work completes in tests:

```swift
// Test a ViewModel without real network calls or sleeps
@Test func loadItemsShowsResults() async {
  var continuation: CheckedContinuation<[Item], Error>!
  let mockService = MockService { resolve in
    continuation = resolve  // capture so test controls timing
  }
  let vm = ItemViewModel(service: mockService)

  await vm.load()  // starts the async work
  continuation.resume(returning: [Item.sample])  // test decides when it completes
  #expect(vm.items.count == 1)
}
```

For TCA: use `TestClock` to advance simulated time instead of real delays:
```swift
let clock = TestClock()
let store = TestStore(initialState: .init()) { Feature() } withDependencies: {
  $0.continuousClock = clock
}
await store.send(.startTimer)
await clock.advance(by: .seconds(1))
await store.receive(.timerTicked)
```

**Architecture-specific test targets:**

| Pattern | What to Test | What NOT to Test |
|---|---|---|
| **MV** | Services, model transforms, business logic | Views directly |
| **MVVM** | ViewModel methods, state transitions | View bindings |
| **TCA** | Reducer (actions → state), Effects | Store internals |
| **MVP** | Presenter logic, view method calls | UIKit view layout |
| **MVI** | Pure reducer, effect execution | View rendering |
| **Clean** | UseCases, Repository implementations, Mappers | Framework layer |

### Range-based Confirmations (Swift 6.2+)

```swift
// Expect exactly 3 calls
await confirmation(expectedCount: 3) { confirm in
  for item in items { process(item) { confirm() } }
}

// Expect 5-10 calls
await confirmation(expectedCount: 5...10) { confirm in
  /* ... */
}
```

### Exit Testing

Test `fatalError` and precondition failures:

```swift
@Test func invalidInputCrashes() async {
  await #expect(processExitsWith: .failure) {
    _ = UnsafeBuffer(count: -1)  // should trigger fatalError
  }
}
```

### Review Checklist
- [ ] All tests marked with `@Test` macro
- [ ] Async tests marked with `async` keyword
- [ ] Using `#expect` and `#require`, not XCTest assertions
- [ ] Parameterized tests have 5+ cases, or use cartesian products intentionally
- [ ] Known failing tests marked with `.bug()` or wrapped in `withKnownIssue()`
- [ ] No test interdependencies (each test is independent)
- [ ] Test names describe what's being tested and expected outcome
- [ ] `confirmation()` used instead of `Task.sleep()` for callback verification
- [ ] Custom traits with `TestScoping` used for setup/teardown consolidation
- [ ] Cartesian products intended (or `zip()` used for 1:1 pairing)
- [ ] Exit paths tested with `processExitsWith` for fatal errors
- [ ] Intermittent failures wrapped in `withKnownIssue(isIntermittent: true)`

### Swift 6.3 Testing Updates

- **Warning issues:** `Issue.record` now accepts a severity parameter — warnings don't fail the test.
- **Test cancellation:** `try Test.cancel()` cancels a test and its task hierarchy mid-execution. Useful for skipping individual arguments of parameterized tests.
- **Image attachments:** `Attachment.record()` can attach images during tests via cross-import overlays with UIKit (iOS) and AppKit (macOS). Swift 6.2+ feature, fully stable in 6.3.

---

## Cross-Section Quick Reference

| Concept | Section | Key Point |
|---------|---------|-----------|
| Async/await error types | 1 | Use typed throws in Swift 6.2 |
| Enum pattern matching | 1 | Always handle all cases exhaustively |
| Custom Codable init | 2 | Use `DecodingError` with context |
| JSONDecoder setup | 2 | Configure strategies before decoding |
| Async test support | 3 | Mark tests with `async`, use `await` |


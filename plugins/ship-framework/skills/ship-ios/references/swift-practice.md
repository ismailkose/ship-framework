<!-- ship-reference
id: ios-swift-practice
kind: mixed
sources: Swift 6.4 toolchain (swiftlang-6.4.0.34.1) and iPhoneOS27.0.sdk Foundation / Network / Synchronization / Testing interfaces (Xcode 27.0 27A266a — every example type-checks via scripts/checks/ios.sh; the decoding, retry (against a stubbed URLProtocol), and single-flight rules run on the host via scripts/checks/ios_runtime); https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/ ; https://www.swift.org/migration/documentation/migrationguide/ ; https://developer.apple.com/documentation/foundation/urlsession ; https://developer.apple.com/documentation/network/nwpathmonitor ; https://developer.apple.com/documentation/foundation/jsondecoder ; https://developer.apple.com/documentation/testing (all checked 2026-09-24); Swift Evolution SE-0461/0466/0470/0472/0493 (proposal texts). Written for Ship from Swift's and Apple's docs and the toolchain; no third-party text. Ideas credited (MIT, each compiled or probed before use): twostraws/Swift-Concurrency-Agent-Skill@bee3f69, twostraws/Swift-Testing-Agent-Skill@2d6bba1.
reviewed: 2026-09-24
-->
# Swift in practice — concurrency, networking, data, errors, tests

Ship's baseline for the Swift underneath the screens. It builds on the road signs in
`swiftui-ship.md` §5–§6 (those stay: cancellation-before-commit, the task-group correction,
structured concurrency) and the build-setting facts in `ios-27.md` §2–§3 — **read the target's
concurrency settings before advising**. An installed `swift-concurrency` skill adds depth; it
isn't required.

## 1. Where code runs

Read the target's settings first (`ios-27.md` §2): whether `NonisolatedNonsendingByDefault` is on
(Approachable Concurrency — Xcode 27's new-app template turns it on) changes the answer. Measured
by Ship's host test (`ios_runtime/isolation_*`, Swift 6.4), calling from the main actor:

| What you call | Default settings | `NonisolatedNonsendingByDefault` on |
|---|---|---|
| A **synchronous** function — `nonisolated` or not | caller's thread (main) | caller's thread (main) |
| A `nonisolated` **async** function | off the main actor | **on the caller's actor (main)** |
| A `@concurrent` async function (Swift 6.2+) | off the main actor | off the main actor |
| `Task { … }` started on the main actor | main (it inherits the actor) | main |
| `Task.detached { … }` | off the main actor | off the main actor |

- **CPU-heavy work** (parsing a big file, decoding images, hashing): put it behind a `@concurrent`
  async function and `await` it. That's the one form that leaves the main actor under both
  settings. `nonisolated` alone never moves synchronous work, and wrapping it in `Task { }` from a
  view doesn't either.
- `Task.detached` also leaves, but drops priority and task-locals and isn't cancelled when the
  calling task is — don't use it just to get off the main actor.
- UI models and anything a view reads: `@MainActor` (explicit, or the target's default isolation).
- Shared mutable state across tasks: an `actor`, or `Mutex` (iOS 18) for a small synchronous
  critical section. `@unchecked Sendable` only with a comment saying what makes it safe.
- Hopping off the main actor doesn't make work cancellable: check `Task.isCancelled` /
  `checkCancellation()` in long loops, and drop results the caller no longer wants (§2).
- `Task.immediate` (iOS 26) starts synchronously on the caller.

## 2. Cancellation and structure

- Tie work to lifetimes: `.task` / `.task(id:)` in views; a stored `Task` you cancel in a model
  (`deinit` or an explicit `stop()`).
- **Cooperative:** long loops call `try Task.checkCancellation()`; before writing a result, check
  it still applies (`swiftui-ship.md` §6).
- `async let` for a fixed number of parallel calls; `withThrowingTaskGroup` for a dynamic number.
  A group body that returns normally **waits** for the remaining children; for "first result wins"
  or timeouts, take the result and `cancelAll()`.
- Callback APIs → `withCheckedThrowingContinuation`; resume **exactly once** on every path
  (including errors and cancellation); pair with `withTaskCancellationHandler` so cancelling the
  task cancels the underlying request.
- `AsyncStream` from delegate/callback sources: create it with `AsyncStream.makeStream(of:)`
  (stream + continuation, no escaping closure), stop the source in `onTermination`, call
  `finish()` on every exit path, and choose a buffering policy (`.bufferingNewest(1)` for "latest
  value" streams like location).
- `Task { }` created in a loop is usually a task group in disguise — use `withTaskGroup` so the
  work is cancelled and awaited together.

## 3. Actor reentrancy

Every `await` inside an actor is a point where other callers run. State you read before the
`await` may be different after it. Two consequences:
- Re-check invariants after an `await` before writing. A force-unwrap of actor state after an
  `await` is a latent crash: another caller may have cleared it during the suspension.
- For "do this once even if many callers ask" (token refresh, loading a shared resource), store
  the in-flight `Task` and let later callers await it — **single-flight**:

```swift
actor TokenStore {
    private var token: String?
    private var refreshing: Task<String, any Error>?
    private let refresh: @Sendable () async throws -> String   // calls your auth server

    init(refresh: @escaping @Sendable () async throws -> String) { self.refresh = refresh }

    /// Many concurrent callers → one refresh; everyone gets its result.
    func validToken(forceRefresh: Bool = false) async throws -> String {
        if let token, !forceRefresh { return token }
        if let refreshing { return try await refreshing.value }
        let task = Task { try await refresh() }
        refreshing = task
        defer { refreshing = nil }
        let fresh = try await task.value
        token = fresh
        return fresh
    }
}
```

## 4. Networking

- `URLSession` async APIs (`data(for:)`, `upload`, `download`, `bytes`); one configured session per
  API, not `URLSession.shared` for authenticated calls. HTTPS only (App Transport Security);
  exceptions need a reason in Info.plist and App Review.
- **Map responses deliberately:** 2xx → decode; 401 → refresh once (§3) then sign-in; 4xx → a
  message the person can act on; 5xx / timeouts / connection lost → retry if idempotent.
- **Retry only idempotent requests** (GET, PUT with the same body, requests with an idempotency
  key) on transient errors, with exponential backoff + jitter and a cap; respect `Retry-After`.
- **Offline:** `NWPathMonitor` for a connectivity banner; `URLSessionConfiguration.waitsForConnectivity`
  so requests wait instead of failing instantly; queue writes locally and send when back
  (`data-sync.md`). Never block the UI on "are we online".
- Cancel with the view (`.task`); a cancelled request throws `URLError(.cancelled)` or
  `CancellationError` — neither is a user-facing error.
- Big transfers that must survive the app leaving: background sessions
  (`notifications-background.md` §5). WebSockets: `URLSessionWebSocketTask`, with a ping and
  reconnect-with-backoff.

```swift
enum APIError: Error, Equatable { case unauthorized, client(Int), server(Int), transport(URLError.Code) }

/// Whether a failure is worth retrying (idempotent requests only).
nonisolated func isTransient(_ error: APIError) -> Bool {
    switch error {
    case .server(let code): return code == 502 || code == 503 || code == 504
    case .transport(let code): return [.timedOut, .networkConnectionLost, .notConnectedToInternet, .cannotConnectToHost].contains(code)
    default: return false
    }
}

/// Exponential backoff with full jitter, capped: attempt 0 → up to 0.5 s, 1 → 1 s, 2 → 2 s … max 8 s.
nonisolated func backoff(attempt: Int, random: (ClosedRange<Double>) -> Double = { .random(in: $0) }) -> Duration {
    let ceiling = min(8.0, 0.5 * pow(2.0, Double(attempt)))
    return .milliseconds(Int(random(0...ceiling) * 1000))
}

struct APIClient: Sendable {
    let base: URL
    let session: URLSession
    var decoder = JSONDecoder()            // pass the configured one from §5 (`.api`)

    func get<T: Decodable & Sendable>(_ path: String, as: T.Type, maxAttempts: Int = 3) async throws -> T {
        var attempt = 0
        while true {
            do {
                let (data, response) = try await session.data(from: base.appending(path: path))
                let status = (response as? HTTPURLResponse)?.statusCode ?? 0
                switch status {
                case 200..<300: return try decoder.decode(T.self, from: data)
                case 401: throw APIError.unauthorized
                case 400..<500: throw APIError.client(status)
                default: throw APIError.server(status)
                }
            } catch let error as URLError where error.code != .cancelled {
                try await retryOrThrow(APIError.transport(error.code), attempt: &attempt, max: maxAttempts)
            } catch let error as APIError {
                try await retryOrThrow(error, attempt: &attempt, max: maxAttempts)
            }
        }
    }

    private func retryOrThrow(_ error: APIError, attempt: inout Int, max: Int) async throws {
        attempt += 1
        guard isTransient(error), attempt < max else { throw error }
        try await Task.sleep(for: backoff(attempt: attempt - 1))   // throws if cancelled — stops retrying
    }
}
```

## 5. Codable at the edges

- One configured decoder per API (dates, keys) — not a new `JSONDecoder()` with different settings
  at every call site.
- Dates: `.iso8601` rejects fractional seconds; servers often send them. Use a custom strategy
  with `Date.ISO8601FormatStyle(includingFractionalSeconds: true)` and fall back to the plain form.
- Keys: `convertFromSnakeCase` is fine for consistent APIs; explicit `CodingKeys` when names are
  irregular or you need to rename. Don't mix both on one type.
- **Be lenient with what you receive:** optional fields with `decodeIfPresent` + defaults; enums
  with an `unknown` case so a new server value doesn't fail the whole payload; one bad element in a
  list is skipped, not fatal (below). Be strict with what you send.

```swift
extension JSONDecoder {
    nonisolated static var api: JSONDecoder {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .custom { decoder in
            let text = try decoder.singleValueContainer().decode(String.self)
            if let date = try? Date(text, strategy: Date.ISO8601FormatStyle(includingFractionalSeconds: true)) { return date }
            if let date = try? Date(text, strategy: .iso8601) { return date }
            throw DecodingError.dataCorrupted(.init(codingPath: decoder.codingPath, debugDescription: "Bad date: \(text)"))
        }
        return decoder
    }
}

/// Decodes the elements that decode and skips the ones that don't.
struct LossyArray<Element: Decodable>: Decodable {
    var elements: [Element]
    private struct Skip: Decodable {}
    init(from decoder: any Decoder) throws {
        var container = try decoder.unkeyedContainer()
        var items: [Element] = []
        while !container.isAtEnd {
            if let item = try? container.decode(Element.self) { items.append(item) }
            else { _ = try? container.decode(Skip.self) }       // advance past the bad element
        }
        elements = items
    }
}

enum TripStatus: String, Decodable {
    case planned, active, finished, unknown
    init(from decoder: any Decoder) throws {
        self = TripStatus(rawValue: try decoder.singleValueContainer().decode(String.self)) ?? .unknown
    }
}
```

## 6. Errors people see

- Model failures as a small enum per domain (`APIError`, `SyncError`); map each to a message that
  says what happened and what to do, at the UI boundary (`LocalizedError` or a function).
- Never show `error.localizedDescription` of a system error raw; never show nothing. Log the
  underlying error with `Logger` (`swiftui-performance.md` §7).
- Typed throws (`throws(APIError)`) only for a closed domain; plain `throws` elsewhere.

## 7. Tests with Swift Testing

- New unit tests: `import Testing`, `@Test`, `#expect` (keeps going), `#require` (stops and unwraps).
  A struct with `@Test` methods is a suite already — add `@Suite` only to name it or attach traits.
  Setup in `init` (it can be `async throws`); a class suite can tear down in `deinit`.
- **Write `#expect(x == false)`, not `#expect(!x)`.** Ship's probe (Swift 6.4): a failing
  `#expect(!isLoggedIn())` reported the inner call's value inverted, while `== false` reported it
  correctly. A test that reaches no `#expect`/`#require` passes — make sure each path asserts.
- `@available` goes on each `@Test`, not on the suite type — the compiler rejects `@Test` inside a
  suite marked `@available` (checked with Swift 6.4).
- **Parameterize** instead of copy-paste: `@Test(arguments: [...])` — each argument is its own
  result. Two argument collections run all combinations; use `zip` for pairs.
- Async tests just `await`. Callback/event code: `await confirmation("…", expectedCount: n) { confirm in … }`
  (ranges like `1...` are Swift 6.2+). Known bugs: `withKnownIssue { }` (fails the test if the
  issue *stops* happening — you'll notice the fix); `isIntermittent: true` for flaky ones.
- Traits: `.tags(...)`, `.disabled("reason")`, `.timeLimit(.minutes(1))`, `.serialized` for tests
  that share state. Tests run in parallel by default — no shared mutable globals.
- Keep XCTest for UI tests (`XCUIApplication`), performance tests (`measure`), and
  `performAccessibilityAudit`. Exit tests (`#expect(processExitsWith:)`) don't run on iOS.
- Test the logic, not the framework: inject protocols for network/clock/storage; use in-memory
  stores (`data-sync.md` §7) and fixed dates.

```swift
import Testing

@Suite("Retry policy")
struct RetryPolicyTests {
    @Test(arguments: [APIError.server(503), .transport(.timedOut), .transport(.networkConnectionLost)])
    func transientErrorsRetry(_ error: APIError) {
        #expect(isTransient(error))
    }

    @Test(arguments: [APIError.unauthorized, .client(404), .server(500)])
    func permanentErrorsDont(_ error: APIError) {
        #expect(isTransient(error) == false)
    }

    @Test func backoffIsCapped() {
        #expect(backoff(attempt: 10, random: { $0.upperBound }) == .milliseconds(8000))
    }
}

enum APIError: Error, Equatable { case unauthorized, client(Int), server(Int), transport(URLError.Code) }
func isTransient(_ error: APIError) -> Bool {
    switch error {
    case .server(let code): [502, 503, 504].contains(code)
    case .transport(let code): [.timedOut, .networkConnectionLost, .notConnectedToInternet, .cannotConnectToHost].contains(code)
    default: false
    }
}
func backoff(attempt: Int, random: (ClosedRange<Double>) -> Double) -> Duration {
    .milliseconds(Int(random(0...min(8.0, 0.5 * pow(2.0, Double(attempt)))) * 1000))
}
```

(The test repeats §4's two functions so it compiles on its own; in a project it imports them.)

## 8. Concurrency compile errors — first moves

| Error says | Usually means | First move |
|---|---|---|
| "…main actor-isolated … cannot be called from outside of the actor" | Calling UI-isolated code from a background context | `await` it, or make the callee `nonisolated` if it touches no UI state |
| "Sending '…' risks causing data races" | A non-Sendable value crosses actors | Make it a value type / `Sendable`, or keep it on one actor |
| "Capture of '…' with non-Sendable type in a `@Sendable` closure" | Closure runs elsewhere with a reference type | Capture a Sendable copy or an id; move the work to the owning actor |
| "Main actor-isolated conformance … cannot be used in nonisolated context" | A `@MainActor` type conforms to a delegate protocol the SDK calls elsewhere | `@preconcurrency` conformance if the SDK calls on main; else `nonisolated` methods that hop |
| "Static property '…' is not concurrency-safe" | Mutable global/static | `let`, `@MainActor`, or `Mutex` |

Settings drive which of these appear — read them first (`ios-27.md` §2). Migrating a module to
Swift 6 mode: one module at a time, fix warnings with strict checking on first
([migration guide](https://www.swift.org/migration/documentation/migrationguide/)).

## 9. Verify

| What | How | Level |
|---|---|---|
| Parsing, retry, single-flight, validation | Swift Testing unit tests (like §7) | CI |
| Cancellation doesn't commit stale results | Test that cancels mid-flight and asserts state unchanged | CI |
| Data races | Swift 6 language mode compiles clean; Thread Sanitizer on the test scheme | CI |
| Offline and flaky network | Network Link Conditioner (device) / airplane mode; `waitsForConnectivity` behaviour | **Device** |
| Token refresh under load | Fire 10 requests with an expired token; exactly one refresh (server log or test double) | CI + staging |

Swift: [Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/) ·
[Migration guide](https://www.swift.org/migration/documentation/migrationguide/) ·
[Swift Testing](https://developer.apple.com/documentation/testing) ·
[URLSession](https://developer.apple.com/documentation/foundation/urlsession).

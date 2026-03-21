# URLSession — iOS Reference

> **When to read:** Dev reads this when building features that use URLSession for data fetching, uploads, downloads, or background network operations.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Methods/Properties |
|---------|---------|------------------------|
| **URLSessionTask** | Represents a single request | `resume()`, `suspend()`, `cancel()`, `state`, `progress` |
| **URLSession** | Shared configuration for tasks | `.shared`, custom init with `URLSessionConfiguration` |
| **URLSessionConfiguration** | Request behavior & defaults | `.default`, `.ephemeral`, `.background(withIdentifier:)` |
| **URLRequest** | HTTP request builder | `url`, `httpMethod`, `timeoutInterval`, `allHTTPHeaderFields` |
| **URLResponse/HTTPURLResponse** | Response metadata | `statusCode`, `headerFields`, `mimeType` |
| **URLCache** | Disk/memory caching | `cachedResponse(for:)`, `storeCachedResponse:forRequest:` |
| **async/await API** | Modern data fetching | `data(from:)`, `data(for:)`, `download(from:)`, `upload(for:data:)` |
| **Codable Integration** | Type-safe JSON | `JSONDecoder()` with `data(from:)` result |
| **Background Sessions** | Network after app suspend | `.background(withIdentifier:)` + delegate |
| **Certificate Pinning** | Security validation | `urlSession(_:didReceive:completionHandler:)` in delegate |

---

## Code Examples

**Example 1: Async/await data fetch with Codable**
```swift
struct User: Codable {
    let id: Int
    let name: String
}

func fetchUser(id: Int) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Call: let user = try await fetchUser(id: 42)
```

**Example 2: Custom URLSessionConfiguration with timeout & cache**
```swift
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 30
config.waitsForConnectivity = true
config.urlCache = URLCache(memoryCapacity: 10_000_000, diskCapacity: 100_000_000)
config.requestCachePolicy = .returnCacheDataElseLoad

let session = URLSession(configuration: config)
let (data, _) = try await session.data(from: url)
```

**Example 3: File upload with progress tracking**
```swift
func uploadFile(at fileURL: URL, to endpoint: URL) async throws {
    var request = URLRequest(url: endpoint)
    request.httpMethod = "POST"

    let (data, response) = try await URLSession.shared.upload(for: request, fromFile: fileURL)
    guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
        throw NetworkError.invalidResponse
    }
}
```

---

## Common Mistakes

**Mistake 1: Forgetting `resume()` on dataTask**
```swift
// ❌ WRONG — task never executes
let task = URLSession.shared.dataTask(with: url) { data, _, error in
    // This closure is never called
}
// No resume() call

// ✅ CORRECT
let task = URLSession.shared.dataTask(with: url) { data, _, error in
    print(data ?? "no data")
}
task.resume()
// OR use async/await (no resume needed)
let (data, _) = try await URLSession.shared.data(from: url)
```

**Mistake 2: Not handling HTTPURLResponse status codes**
```swift
// ❌ WRONG — treats 404/500 as success
let (data, response) = try await URLSession.shared.data(from: url)
let model = try JSONDecoder().decode(Model.self, from: data) // May fail

// ✅ CORRECT
let (data, response) = try await URLSession.shared.data(from: url)
guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
    throw NetworkError.badStatusCode(http?.statusCode ?? -1)
}
let model = try JSONDecoder().decode(Model.self, from: data)
```

**Mistake 3: Not configuring background session properly**
```swift
// ❌ WRONG — background identifier changes each launch
let config = URLSessionConfiguration.background(withIdentifier: "com.app.bg.\(UUID())")
let session = URLSession(configuration: config, delegate: self, delegateQueue: nil)

// ✅ CORRECT — stable identifier, delegate on queue
let config = URLSessionConfiguration.background(withIdentifier: "com.app.network")
let queue = OperationQueue()
let session = URLSession(configuration: config, delegate: self, delegateQueue: queue)
```

**Mistake 4: Holding strong reference to URLSession unnecessarily**
```swift
// ❌ WRONG — session retained longer than needed
class DataFetcher {
    let session = URLSession(configuration: .default)
}

// ✅ CORRECT — use .shared or pass session as parameter
class DataFetcher {
    func fetch() async throws -> Data {
        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }
}
```

**Mistake 5: No timeout handling with waitsForConnectivity**
```swift
// ❌ WRONG — request hangs indefinitely waiting for connection
let config = URLSessionConfiguration.default
config.waitsForConnectivity = true
// Missing timeout or max wait time

// ✅ CORRECT — set explicit timeout
let config = URLSessionConfiguration.default
config.waitsForConnectivity = true
config.timeoutIntervalForRequest = 60 // Fallback timeout
```

---

## Review Checklist

- [ ] All network responses check `HTTPURLResponse` status code (200-299)?
- [ ] Errors from `URLSession` are properly caught and handled?
- [ ] URLSession instance is `.shared` or properly retained?
- [ ] Timeout intervals are set for network requests?
- [ ] Cache policy matches use case (`.useProtocolCachePolicy` for APIs)?
- [ ] Background session has stable identifier & delegate implementation?
- [ ] JSONDecoder errors don't expose raw JSON in UI?
- [ ] Large downloads use `download(from:)` instead of `data(from:)`?
- [ ] Certificate pinning implemented if handling sensitive data?
- [ ] No network requests on main thread (async/await handles this)?
- [ ] User-facing errors are localized, not raw HTTP codes?
- [ ] Rate limiting or retry logic considered for failed requests?

---

_Source: Apple Developer Documentation · URLSession & URLSessionConfiguration · Condensed for Ship Framework agent reference_

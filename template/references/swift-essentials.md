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

### Review Checklist
- [ ] All enum cases handled in switch statements
- [ ] Error types are specific, not generic `Error`
- [ ] Property wrappers have `wrappedValue` and `projectedValue`
- [ ] Opaque types (`some`) used for returns, `any` for parameters
- [ ] Protocols conform to Hashable/Identifiable/Sendable where appropriate

---

## Section 2: Codable

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

### Review Checklist
- [ ] All CodingKeys entries match JSON response
- [ ] Date strategy configured (ISO8601 or custom)
- [ ] All required fields use `decode`, optional fields use `decodeIfPresent`
- [ ] Custom init/encode mirrors each other
- [ ] Error messages in DecodingError include field name

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

### Parameterized Tests

Run the same test with multiple input values.

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
struct TestCase {
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
```

**Common Mistakes:**
- ❌ Creating parameterized tests with only 1-2 cases (use simple tests instead)
- ❌ Not using descriptive test names with data context
- ✅ Use for validation/edge cases with 5+ test cases
- ✅ Name tests to include the parameter description

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

### Review Checklist
- [ ] All tests marked with `@Test` macro
- [ ] Async tests marked with `async` keyword
- [ ] Using `#expect` and `#require`, not XCTest assertions
- [ ] Parameterized tests have 5+ cases
- [ ] Known failing tests marked with `.bug()`
- [ ] No test interdependencies (each test is independent)
- [ ] Test names describe what's being tested and expected outcome

---

## Cross-Section Quick Reference

| Concept | Section | Key Point |
|---------|---------|-----------|
| Async/await error types | 1 | Use typed throws in Swift 6.2 |
| Enum pattern matching | 1 | Always handle all cases exhaustively |
| Custom Codable init | 2 | Use `DecodingError` with context |
| JSONDecoder setup | 2 | Configure strategies before decoding |
| Async test support | 3 | Mark tests with `async`, use `await` |


# Device Integrity — iOS Reference

> **When to read:** Dev reads this when implementing fraud detection, app integrity checks, or securing high-value transactions with DeviceCheck and App Attest.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Types/Methods |
|---------|---------|-------------------|
| **DCDevice** | Shared device identifier | `DCDevice.current`, unique per app |
| **DCAppAttestService** | App integrity verification | `generateAssertion()`, hardware-backed signing |
| **App Attest Assertion** | Cryptographic proof | Challenge-response, server validation |
| **Server-side Verification** | Apple validation service | POST to Apple's verification endpoint |
| **Device Token** | Per-app identifier | `currentDeviceIdentifier()` (deprecated) |
| **Nonce/Challenge** | Prevents replay attacks | Client gets from server, includes in assertion |
| **Attestation Object** | Binary assertion format | Signed by Secure Enclave |
| **Key ID** | Attestation key reference | Rotate periodically |

---

## Code Examples

**Example 1: Basic App Attest assertion generation**
```swift
import DeviceCheck

class AppAttestManager {
    static let shared = AppAttestManager()

    func generateAssertion(challenge: Data) async throws -> Data {
        let service = DCAppAttestService.shared

        // Check availability (iOS 14+)
        guard service.isSupported else {
            throw AttestError.notSupported
        }

        do {
            // Generate assertion (challenge from server)
            let assertion = try await service.generateAssertion(
                forPayload: challenge,
                clientInput: Data() // Can include additional client data
            )
            return assertion
        } catch {
            throw AttestError.generationFailed(error)
        }
    }
}

enum AttestError: Error {
    case notSupported
    case generationFailed(Error)
    case verificationFailed
}
```

**Example 2: Attest flow with server challenge**
```swift
class IntegrityVerificationFlow {
    let apiURL = URL(string: "https://api.example.com/verify-device")!
    let attestManager = AppAttestManager.shared

    func verifyDeviceIntegrity() async throws {
        // Step 1: Request challenge from server
        let challengeResponse = try await requestChallenge()
        let challenge = challengeResponse.challenge

        // Step 2: Generate assertion with challenge
        let assertion = try await attestManager.generateAssertion(challenge: challenge)

        // Step 3: Send assertion back to server for verification
        let verifyResponse = try await verifyAssertionWithServer(
            assertion: assertion,
            requestID: challengeResponse.requestID
        )

        guard verifyResponse.isValid else {
            throw AttestError.verificationFailed
        }

        // Device verified, allow high-value transaction
        print("Device integrity confirmed")
    }

    func requestChallenge() async throws -> ChallengeResponse {
        var request = URLRequest(url: apiURL)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw AttestError.verificationFailed
        }

        return try JSONDecoder().decode(ChallengeResponse.self, from: data)
    }

    func verifyAssertionWithServer(assertion: Data, requestID: String) async throws -> VerifyResponse {
        var request = URLRequest(url: apiURL.appendingPathComponent("verify"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = VerifyRequest(
            assertion: assertion.base64EncodedString(),
            requestID: requestID
        )
        request.httpBody = try JSONEncoder().encode(body)

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw AttestError.verificationFailed
        }

        return try JSONDecoder().decode(VerifyResponse.self, from: data)
    }
}

struct ChallengeResponse: Codable {
    let challenge: Data
    let requestID: String
}

struct VerifyRequest: Codable {
    let assertion: String
    let requestID: String

    enum CodingKeys: String, CodingKey {
        case assertion
        case requestID = "request_id"
    }
}

struct VerifyResponse: Codable {
    let isValid: Bool

    enum CodingKeys: String, CodingKey {
        case isValid = "is_valid"
    }
}
```

**Example 3: Server-side verification with Apple API (pseudo-code)**
```swift
// This runs on your backend, NOT on the device

import Foundation
import CryptoKit

class AppleAttestVerifier {
    let bundleID = "com.example.app"
    let teamID = "ABCD123456"
    let appleEndpoint = URL(string: "https://appattest.apple.com/verify")!

    func verifyAssertion(_ assertionB64: String) async throws -> Bool {
        // Step 1: Decode assertion
        guard let assertionData = Data(base64Encoded: assertionB64) else {
            return false
        }

        // Step 2: Parse attestation object (CBOR format)
        // In real code, use CBOR decoder
        // Extract: credentialID, credentialPublicKey, counter

        // Step 3: Send to Apple for verification
        var request = URLRequest(url: appleEndpoint)
        request.httpMethod = "POST"
        request.setValue("application/octet-stream", forHTTPHeaderField: "Content-Type")
        request.httpBody = assertionData

        let (response, httpResponse) = try await URLSession.shared.data(for: request)

        guard let http = httpResponse as? HTTPURLResponse, http.statusCode == 200 else {
            return false
        }

        // Parse Apple's response
        // Returns: isValid (boolean)
        return true // Simplified
    }
}
```

---

## Common Mistakes

**Mistake 1: No challenge from server (replay attack vulnerability)**
```swift
// ❌ WRONG — No challenge, assertion always same
let assertion = try await service.generateAssertion(
    forPayload: Data(),
    clientInput: Data()
)

// ✅ CORRECT — Use server-provided challenge
let challenge = try await fetchChallengeFromServer()
let assertion = try await service.generateAssertion(
    forPayload: challenge,
    clientInput: Data()
)
```

**Mistake 2: Not handling unsupported devices**
```swift
// ❌ WRONG — Crashes on older iOS
let service = DCAppAttestService.shared
let assertion = try await service.generateAssertion(forPayload: challenge, clientInput: Data())

// ✅ CORRECT — Check availability first
guard DCAppAttestService.shared.isSupported else {
    // Fallback: require re-authentication, limit features
    print("App Attest not available on this device")
    return
}
let assertion = try await service.generateAssertion(forPayload: challenge, clientInput: Data())
```

**Mistake 3: Trusting assertion without server verification**
```swift
// ❌ WRONG — Client-side verification only
let assertion = try await attestManager.generateAssertion(challenge: challenge)
// Just check assertion is not nil, proceed

// ✅ CORRECT — Always verify on server
let assertion = try await attestManager.generateAssertion(challenge: challenge)
let isValid = try await verifyAssertionWithServer(assertion: assertion)
guard isValid else {
    throw AttestError.verificationFailed
}
```

**Mistake 4: Hardcoding challenge, allowing reuse**
```swift
// ❌ WRONG — Same challenge for all requests
let staticChallenge = Data("my-challenge".utf8)
let assertion = try await service.generateAssertion(forPayload: staticChallenge)

// ✅ CORRECT — Generate unique challenge per request
let challenge = Data(randomBytes: 32) // Server generates this
let assertion = try await service.generateAssertion(forPayload: challenge)
```

**Mistake 5: Not rotating keys periodically**
```swift
// ❌ WRONG — Use same key for months
let keyID = "primary-key"
let assertion = try await service.generateAssertion(...)

// ✅ CORRECT — Rotate keys monthly or on compromise
let keyID = "key-\(Date().formatted(.iso8601))" // Include timestamp
let assertion = try await service.generateAssertion(...)
// Server validates latest key rotation
```

---

## Review Checklist

- [ ] App Attest availability checked (`isSupported`)?
- [ ] Challenge generated on server, never hardcoded?
- [ ] Assertion sent to server for verification (not trusted client-side)?
- [ ] Server verification uses Apple's attestation endpoint?
- [ ] Replay attacks prevented (unique challenge per request)?
- [ ] Graceful fallback for devices without App Attest?
- [ ] Sensitive transactions protected (payments, account changes)?
- [ ] No assertion reuse across requests?
- [ ] Keys rotated periodically (at least monthly)?
- [ ] Server validates credentialID and counter?
- [ ] Challenge-assertion pair verified before allowing action?
- [ ] Errors don't leak app state to attacker?

---

_Source: Apple Developer Documentation · DeviceCheck, App Attest · Condensed for Ship Framework agent reference_

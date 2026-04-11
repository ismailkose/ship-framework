# CryptoTokenKit Reference

> **When to read:** Dev reads when integrating smart cards or security tokens.
> Crit reads Common Mistakes during security review.

---

## Overview

CryptoTokenKit provides access to smart cards, security tokens, and hardware security modules via APDU (Application Protocol Data Unit) commands. Integrates with Keychain for certificate-based authentication.

## Token Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Your App   │ →  │  Token       │ →  │  Smart Card │
│             │    │  Extension   │    │  / HSM      │
└─────────────┘    └──────────────┘    └─────────────┘
```

The Token Extension mediates between your app and the physical token.

## Token Extension

```swift
import CryptoTokenKit

class TokenDriver: TKTokenDriver {
  override func createToken(for configuration: TKToken.Configuration) throws -> TKToken {
    return MyToken(tokenDriver: self, configuration: configuration)
  }
}

class MyToken: TKToken {
  override func createSession() throws -> TKTokenSession {
    return MyTokenSession(token: self)
  }
}
```

## Session and APDU Communication

```swift
class MyTokenSession: TKTokenSession {
  func sendAPDU(_ command: Data) async throws -> Data {
    // SELECT command
    let selectAPDU = Data([0x00, 0xA4, 0x04, 0x00])  // CLA INS P1 P2
    + Data([UInt8(aid.count)])  // Lc
    + aid                        // AID data

    let response = try await smartCard.transmit(selectAPDU)

    // Check status word (last 2 bytes)
    let sw1 = response[response.count - 2]
    let sw2 = response[response.count - 1]
    guard sw1 == 0x90, sw2 == 0x00 else {
      throw TokenError.commandFailed(sw1: sw1, sw2: sw2)
    }

    return response.dropLast(2)  // response data without status
  }
}
```

## Keychain Integration

```swift
// Import certificate from token into Keychain
let certificate = try await tokenSession.readCertificate()
let addQuery: [String: Any] = [
  kSecClass as String: kSecClassCertificate,
  kSecValueRef as String: certificate,
  kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
]
SecItemAdd(addQuery as CFDictionary, nil)
```

## Common Mistakes
- ❌ Sending APDU commands without SELECT first — card won't respond correctly
- ❌ Not checking status words (SW1/SW2) — silent failures
- ❌ Storing token PINs in app memory — use secure input and clear immediately
- ❌ Not handling card removal during operation — causes crashes
- ❌ Ignoring TKTokenSession lifecycle — sessions can be invalidated

## Review Checklist
- [ ] Token extension sandboxed correctly
- [ ] APDU command sequences follow card specification
- [ ] Status words checked after every command
- [ ] PIN handling follows security best practices
- [ ] Card insertion/removal handled gracefully
- [ ] Certificates stored with appropriate Keychain protection level

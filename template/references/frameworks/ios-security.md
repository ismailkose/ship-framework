# iOS Security Reference

> **When to read:** Dev reads when implementing authentication, credential storage,
> encryption, or any security-sensitive feature. Eye reads for security review.
>
> Informed by Swift Security Expert skill (ivan-magda) and OWASP MASVS/MASTG.

---

## Keychain Fundamentals

### Add-or-Update Pattern (Required)

Never delete-and-retry. Always attempt add first, fall back to update on duplicate:

```swift
actor KeychainService {
  func save(data: Data, service: String, account: String) throws {
    let query: [String: Any] = [
      kSecClass as String: kSecClassGenericPassword,
      kSecAttrService as String: service,
      kSecAttrAccount as String: account,
    ]
    let attributes: [String: Any] = [kSecValueData as String: data]

    // Attempt add
    var status = SecItemAdd(query.merging(attributes) { _, new in new } as CFDictionary, nil)

    if status == errSecDuplicateItem {
      // Fall back to update (update dict must NOT contain kSecClass)
      status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
    }

    guard status == errSecSuccess else {
      throw KeychainError.from(status)
    }
  }
}
```

### OSStatus Error Handling

Map ALL non-zero OSStatus to a domain-specific Swift error:

| Status Code | Meaning | Action |
|---|---|---|
| `errSecSuccess` (0) | Success | Proceed |
| `errSecDuplicateItem` (-25299) | Already exists | Update instead of add |
| `errSecItemNotFound` (-25300) | Not found | Not an error on delete |
| `errSecInteractionNotAllowed` (-25308) | Device locked | Retry later, never delete |
| `errSecUserCanceled` (-25293) | User cancelled biometric | Handle gracefully |
| `errSecParam` (-50) | Invalid parameter | Check dictionary keys |

### Critical Rules

- **NEVER execute SecItem* on @MainActor** — IPC to `securityd` blocks the main thread. Use a dedicated `actor`.
- **Always set `kSecMatchLimit` explicitly** on update/delete — default is `kSecMatchLimitAll` which affects ALL matching items.
- **Always set `kSecAttrAccessible` explicitly** — default `WhenUnlocked` breaks all background operations.
- **Update dict must NOT contain `kSecClass`** — produces `errSecParam`.
- **macOS: always set `kSecUseDataProtectionKeychain: true`** — otherwise access control flags are silently ignored.

### Accessibility Tiers

| Tier | When Available | Use For |
|---|---|---|
| `WhenPasscodeSetThisDeviceOnly` | Passcode set + unlocked | Highest security, deleted on passcode removal |
| `WhenUnlockedThisDeviceOnly` | Unlocked, device-bound | Standard credentials, no backup migration |
| `WhenUnlocked` (default) | Unlocked | Credentials that migrate with backups |
| `AfterFirstUnlockThisDeviceOnly` | After first unlock | Background tokens, widgets, extensions |
| `AfterFirstUnlock` | After first unlock | Background + backup migration |

---

## Biometric Authentication

### The Boolean Gate Vulnerability (CRITICAL)

`LAContext.evaluatePolicy()` alone is TRIVIALLY BYPASSABLE via Frida/objection. Attackers hook the callback to force `success = true`. OWASP MASTG explicitly fails apps relying solely on `evaluatePolicy`.

```swift
// WRONG — bypassable boolean gate (CWE-288)
let context = LAContext()
context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: "Auth") { success, error in
  if success { grantAccess() }  // Frida hooks this to always return true
}

// CORRECT — hardware-bound secret via Secure Enclave
// Secret physically cannot be read without valid biometric
let accessControl = SecAccessControlCreateWithFlags(
  nil,
  kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
  [.privateKeyUsage, .biometryCurrentSet],
  nil
)!

// Store credential with biometric protection
let query: [String: Any] = [
  kSecClass as String: kSecClassGenericPassword,
  kSecAttrService as String: "com.app.auth",
  kSecAttrAccount as String: "token",
  kSecValueData as String: tokenData,
  kSecAttrAccessControl as String: accessControl,
]
SecItemAdd(query as CFDictionary, nil)

// Reading triggers Secure Enclave biometric verification
// No boolean to hook — data is hardware-encrypted
```

### Access Control Flags

- `.userPresence` — biometry OR passcode (safe fallback if no biometry)
- `.biometryAny` — requires biometry, survives re-enrollment
- `.biometryCurrentSet` — requires biometry, invalidated on enrollment change (most secure)
- `.privateKeyUsage` — required for Secure Enclave key operations

**Rules:**
- Never set both `kSecAttrAccessible` AND `kSecAttrAccessControl` in the same query — causes `errSecParam`.
- `.or`/`.and` is MANDATORY between multiple flags — omitting causes nil return.
- Biometric flags CANNOT work in background (no UI context).

---

## Common Anti-Patterns (Agent-Generated)

1. **Tokens in UserDefaults** — plaintext XML plist, readable from backups. Use Keychain.
2. **Hardcoded API keys** — extractable via `strings` on binary. Fetch from server at runtime.
3. **Production secrets in .xcconfig** — compiled into Info.plist. Use server-side configuration.
4. **Missing `kSecAttrAccessible`** — defaults to `WhenUnlocked`, breaks background operations.
5. **Non-atomic token refresh** — crash between delete/add leaves inconsistent state. Use add-or-update.
6. **Incomplete logout cleanup** — leaves refresh token behind. Delete ALL credential artifacts.
7. **@AppStorage for sensitive data** — plaintext in UserDefaults. Always use Keychain.

---

## CryptoKit Essentials

### Symmetric Encryption

```swift
import CryptoKit

// Generate key (store in Keychain, not source code)
let key = SymmetricKey(size: .bits256)

// Encrypt (nonce auto-generated)
let sealed = try AES.GCM.seal(plaintext, using: key)
let ciphertext = sealed.combined!  // nonce + ciphertext + tag

// Decrypt
let box = try AES.GCM.SealedBox(combined: ciphertext)
let decrypted = try AES.GCM.open(box, using: key)
```

**Rules:**
- Never reuse a nonce under the same key — breaks confidentiality.
- Use `AES.GCM` or `ChaChaPoly` — both provide encryption + authentication.
- Never use `Insecure.MD5` or `Insecure.SHA1` for security purposes.
- `SHA3_256/384/512` require iOS 18+.

### Public Key (Signing & Key Agreement)

- P-256 — only curve supported by Secure Enclave. Required for hardware-backed keys.
- Curve25519 — preferred for software-only keys.
- **Type separation enforced:** `P256.Signing.PrivateKey` cannot do key agreement, and vice versa.
- After ECDH: ALWAYS derive via HKDF — never use `SharedSecret` directly.

### Post-Quantum Cryptography (iOS 26+)

- **ML-KEM-768/1024** — lattice-based key encapsulation (AES-128/192 equivalent)
- **ML-DSA-65/87** — lattice-based digital signatures
- **X-Wing** — hybrid ML-KEM-768 + X25519 (recommended migration path)
- All support Secure Enclave on iOS 26+.

---

## Secure Enclave

- Separate hardware security coprocessor — private keys NEVER leave the chip.
- P-256 ONLY for classical EC. No P-384, P-521, Curve25519.
- No key export (returns opaque encrypted blob).
- `SecureEnclave.isAvailable` can return `true` on Simulator with M-series Mac — unreliable. Always add `#if targetEnvironment(simulator)` guard.
- Performance overhead per round-trip — not suitable for thousands of operations/second.

---

## Keychain Lifecycle

- **Items persist after app uninstall** — use `UserDefaults` flag to detect fresh installs and clean stale items.
- **Extension targets need INDEPENDENT Keychain Sharing capability** — they don't inherit from main app.
- **iCloud Keychain sync is opt-in per item** — `kSecAttrSynchronizable` defaults to `false`.
- **`ThisDeviceOnly` + sync = errSecParam** — contradictory, will error.

---

## Testing Security Code

- Define `KeychainServiceProtocol` — mock with in-memory dictionary for unit tests.
- CryptoKit: test encrypt/decrypt round-trips, nonce uniqueness, invalid tag detection.
- Secure Enclave tests: skip on Simulator, require physical device.
- Cannot mock biometric prompts — use protocol abstraction for `LAContext`.

---

_Source: Swift Security Expert skill (ivan-magda), OWASP MASVS 2024, Apple Security documentation · Condensed for Ship Framework agent reference_

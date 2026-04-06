# CryptoKit Reference

> **When to read:** Dev reads when implementing encryption, hashing, or signing.
> Crit reads Common Mistakes during security review.

---

## Hashing

```swift
import CryptoKit

let data = "Hello, World!".data(using: .utf8)!

// SHA-256 (most common)
let hash = SHA256.hash(data: data)
let hashString = hash.compactMap { String(format: "%02x", $0) }.joined()

// SHA-384
let hash384 = SHA384.hash(data: data)

// SHA-512
let hash512 = SHA512.hash(data: data)
```

**Use hashing for:** file integrity checks, content deduplication, password storage (with salt).

## HMAC (Hash-based Message Authentication)

```swift
let key = SymmetricKey(size: .bits256)
let signature = HMAC<SHA256>.authenticationCode(for: data, using: key)

// Verify — ALWAYS use constant-time comparison
let isValid = HMAC<SHA256>.isValidAuthenticationCode(signature, authenticating: data, using: key)
```

## Symmetric Encryption (AES-GCM)

```swift
// Encrypt
let key = SymmetricKey(size: .bits256)
let sealedBox = try AES.GCM.seal(plaintext, using: key)
let ciphertext = sealedBox.combined!  // nonce + ciphertext + tag

// Decrypt
let box = try AES.GCM.SealedBox(combined: ciphertext)
let decrypted = try AES.GCM.open(box, using: key)
```

ChaChaPoly alternative (faster on devices without AES hardware):
```swift
let sealedBox = try ChaChaPoly.seal(plaintext, using: key)
let decrypted = try ChaChaPoly.open(sealedBox, using: key)
```

## Public-Key Signing

```swift
// Generate key pair
let privateKey = P256.Signing.PrivateKey()
let publicKey = privateKey.publicKey

// Sign
let signature = try privateKey.signature(for: data)

// Verify
let isValid = publicKey.isValidSignature(signature, for: data)

// Export public key for sharing
let publicKeyData = publicKey.compactRepresentation!
```

Supported curves: `P256`, `P384`, `P521`, `Curve25519`.

## Key Agreement (Diffie-Hellman)

```swift
let alicePrivate = P256.KeyAgreement.PrivateKey()
let bobPrivate = P256.KeyAgreement.PrivateKey()

// Alice derives shared secret using Bob's public key
let sharedSecret = try alicePrivate.sharedSecretFromKeyAgreement(with: bobPrivate.publicKey)

// Derive symmetric key from shared secret
let symmetricKey = sharedSecret.hkdfDerivedSymmetricKey(
  using: SHA256.self,
  salt: "my-app-salt".data(using: .utf8)!,
  sharedInfo: Data(),
  outputByteCount: 32
)
```

## Secure Enclave

Hardware-backed key storage (keys never leave the chip):

```swift
let privateKey = try SecureEnclave.P256.Signing.PrivateKey()

// Sign with hardware protection
let signature = try privateKey.signature(for: data)

// Store key reference in Keychain
let keyData = privateKey.dataRepresentation
```

Requirements:
- Device must have Secure Enclave (all modern iPhones/iPads)
- Only P256 curve supported in Secure Enclave
- Keys cannot be exported — only used on-device

## Common Mistakes
- ❌ Reusing nonces — catastrophic for AES-GCM security. Let CryptoKit generate nonces automatically
- ❌ Using SHA-256 for password hashing — use `bcrypt` or `scrypt` instead (CryptoKit hashes are too fast)
- ❌ Comparing authentication codes with `==` — use `isValidAuthenticationCode` (constant-time)
- ❌ Storing `SymmetricKey` in `UserDefaults` — use Keychain
- ❌ Ignoring the authentication tag in AES-GCM — it proves data wasn't tampered with
- ❌ Hardcoding encryption keys in source code — derive from Keychain or Secure Enclave

## Review Checklist
- [ ] Nonces are never reused (let CryptoKit manage them)
- [ ] Symmetric keys stored in Keychain, not UserDefaults or files
- [ ] HMAC verification uses `isValidAuthenticationCode` (constant-time)
- [ ] Secure Enclave used for signing keys when hardware is available
- [ ] Error handling covers key generation failures gracefully
- [ ] Public keys exported in standard format for server communication

# Security Frameworks — iOS Reference

> **When to read:** Dev reads this when implementing Keychain storage, encryption, signing, App Transport Security (ATS), or data protection.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Methods/Types |
|---------|---------|-------------------|
| **Keychain Services** | Secure credential storage | `SecureEnclave`, `Keychain`, password/certificate/key storage |
| **CryptoKit** | Modern cryptography | `SymmetricKey`, `ChaChaPoly`, `AES`, `SHA256`, `P256` |
| **Hashing** | One-way data digest | `Insecure.SHA1`, `SHA256`, `SHA384`, `SHA512` |
| **Signing** | Cryptographic signatures | `CryptoKit.Signing`, `P256.Signing.PrivateKey` |
| **Encryption** | AES-GCM symmetry | `ChaChaPoly.seal()`, `AES.GCM.seal()` |
| **App Transport Security** | HTTPS enforcement | Info.plist `NSAppTransportSecurity` dictionary |
| **Data Protection** | File encryption classes | `NSFileProtectionKey`: `complete`, `completeUnlessOpen`, `none` |
| **Secure Enclave** | Tamper-proof storage | Hardware-backed key generation & signing |
| **Certificate Pinning** | Validate server certs | URLSession delegate + `SecTrust` evaluation |

---

## Code Examples

**Example 1: Keychain password storage (modern wrapper)**
```swift
import Foundation

class KeychainManager {
    static let shared = KeychainManager()

    func store(password: String, for account: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecValueData as String: password.data(using: .utf8)!
        ]
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.storeFailed }
    }

    func retrieve(for account: String) throws -> String {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data else {
            throw KeychainError.retrieveFailed
        }
        return String(data: data, encoding: .utf8) ?? ""
    }
}
```

**Example 2: AES-GCM encryption with CryptoKit**
```swift
import CryptoKit

func encryptMessage(_ message: String) throws -> (ciphertext: Data, nonce: Data) {
    let key = SymmetricKey(size: .bits256)
    let messageData = message.data(using: .utf8)!
    let sealedBox = try AES.GCM.seal(messageData, using: key)

    // Store key securely in Keychain, return ciphertext & nonce
    return (sealedBox.ciphertext, sealedBox.nonce.withUnsafeBytes { Data($0) })
}

func decryptMessage(ciphertext: Data, nonce: Data, key: SymmetricKey) throws -> String {
    let nonce = try AES.GCM.Nonce(data: nonce)
    let sealedBox = try AES.GCM.SealedBox(nonce: nonce, ciphertext: ciphertext)
    let decrypted = try AES.GCM.open(sealedBox, using: key)
    return String(data: decrypted, encoding: .utf8) ?? ""
}
```

**Example 3: Data signing with P256 private key**
```swift
import CryptoKit

func signData(_ data: Data) throws -> Data {
    let privateKey = P256.Signing.PrivateKey()
    let signature = try privateKey.signature(for: data)
    return Data(signature.rawRepresentation)
}

func verifySignature(_ data: Data, signature: Data, publicKey: P256.Signing.PublicKey) throws -> Bool {
    let sig = try P256.Signing.ECDSASignature(rawRepresentation: signature)
    return publicKey.isValidSignature(sig, for: data)
}
```

---

## Common Mistakes

**Mistake 1: Storing credentials in UserDefaults**
```swift
// ❌ WRONG — UserDefaults is NOT encrypted
UserDefaults.standard.set(password, forKey: "userPassword")

// ✅ CORRECT — Use Keychain
try KeychainManager.shared.store(password: password, for: account)
```

**Mistake 2: Ignoring ATS and allowing cleartext HTTP**
```swift
// ❌ WRONG — Info.plist with NSExceptionDomains for non-https
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>example.com</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>

// ✅ CORRECT — HTTPS only, or justified exception with approval
// Remove NSTemporaryExceptionAllowsInsecureHTTPLoads
// Document why HTTP is needed in code comments
```

**Mistake 3: Using weak encryption or hashing for passwords**
```swift
// ❌ WRONG — SHA256 is not suitable for password hashing
import Crypto
let hash = SHA256.hash(data: password.data(using: .utf8)!)

// ✅ CORRECT — Use Keychain for passwords, bcrypt for server-side
try KeychainManager.shared.store(password: password, for: account)
// Server uses bcrypt, scrypt, or Argon2
```

**Mistake 4: Not protecting sensitive files with data protection**
```swift
// ❌ WRONG — No file protection
let sensitiveFile = documentsURL.appendingPathComponent("token.txt")
try token.write(toFile: sensitiveFile.path, atomically: true, encoding: .utf8)

// ✅ CORRECT — Set NSFileProtectionKey on file
try token.write(to: sensitiveFile, atomically: true, encoding: .utf8)
try FileManager.default.setAttributes(
    [.protectionKey: FileProtectionType.complete],
    ofItemAtPath: sensitiveFile.path
)
```

**Mistake 5: Logging or printing sensitive data**
```swift
// ❌ WRONG — API keys/tokens visible in console
print("API Key: \(apiKey)")
os_log("Token: %{public}@", token) // public means visible

// ✅ CORRECT — Redact or use private logging
os_log("Token stored", log: .default, type: .info) // No sensitive data
print("API Key: ***\(apiKey.suffix(4))") // Show only last 4 chars
```

---

## Review Checklist

- [ ] No passwords/tokens stored in UserDefaults?
- [ ] Keychain used for persistent credential storage?
- [ ] All network endpoints use HTTPS?
- [ ] No ATS exceptions or exceptions are documented & approved?
- [ ] Sensitive files have `NSFileProtectionKey: .complete`?
- [ ] CryptoKit used for encryption (not CommonCrypto)?
- [ ] Encryption keys stored in Keychain, not hardcoded?
- [ ] Sensitive data not logged to console or analytics?
- [ ] Certificate pinning implemented for API servers?
- [ ] Private keys never exported or transmitted?
- [ ] Nonces/IVs never reused for GCM encryption?
- [ ] Signing keys regularly rotated?

---

_Source: Apple Developer Documentation · Security, CryptoKit, Keychain Services · Condensed for Ship Framework agent reference_

# Authentication — iOS Reference

> **When to read:** Dev reads this when implementing login, biometric auth, or securing credentials.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `ASAuthorizationController` | Orchestrates Sign in with Apple flow | Handles UI presentation & callbacks |
| `ASAuthorizationAppleIDProvider` | Creates Apple ID request | Returns user, identity token, authorization code |
| `ASAuthorizationPasswordProvider` | AutoFill password flow | Integrates with iCloud Keychain |
| `ASWebAuthenticationSession` | OAuth/OIDC web login | Secure browser modal; dismisses after completion |
| `LAContext` | Biometric authentication | `canEvaluatePolicy()` + `evaluatePolicy()` |
| `LABiometryType` | Enum: faceID, touchID, none | Determines which biometric is available |
| `SecItemAdd/Update/CopyMatching` | Keychain CRUD | Store tokens, passwords, secrets |
| `kSecClass`, `kSecAttrAccount` | Keychain query attributes | Common: password, certificate, identity |

## Code Examples

```swift
// 1. Sign in with Apple (ASAuthorizationController)
import AuthenticationServices

func signInWithApple() {
    let request = ASAuthorizationAppleIDProvider().createRequest()
    request.requestedScopes = [.fullName, .email]

    let controller = ASAuthorizationController(authorizationRequests: [request])
    controller.delegate = self
    controller.presentationContextProvider = self
    controller.performRequests()
}

extension AppDelegate: ASAuthorizationControllerDelegate {
    func authorizationController(
        _ controller: ASAuthorizationController,
        didCompleteWithAuthorization authorization: ASAuthorization
    ) {
        if let credential = authorization.credential as? ASAuthorizationAppleIDCredential {
            let userId = credential.user
            let identityToken = credential.identityToken
            // Verify token on backend; store userId securely
        }
    }
}

// 2. Biometric authentication (Face ID / Touch ID)
import LocalAuthentication

func authenticateWithBiometrics() {
    let context = LAContext()
    var error: NSError?

    guard context.canEvaluatePolicy(
        .deviceOwnerAuthenticationWithBiometrics,
        error: &error
    ) else {
        print("Biometrics unavailable: \(error?.localizedDescription ?? "")")
        return
    }

    context.evaluatePolicy(
        .deviceOwnerAuthenticationWithBiometrics,
        localizedReason: "Unlock your account"
    ) { success, error in
        if success {
            DispatchQueue.main.async {
                self.unlockApp()
            }
        } else {
            print("Auth failed: \(error?.localizedDescription ?? "")")
        }
    }
}

// 3. Web-based OAuth (ASWebAuthenticationSession)
func signInWithGoogle() {
    guard let authURL = URL(string: "https://accounts.google.com/o/oauth2/v2/auth?client_id=...") else { return }

    let session = ASWebAuthenticationSession(
        url: authURL,
        callbackURLScheme: "com.myapp"
    ) { callbackURL, error in
        guard let callbackURL = callbackURL else {
            print("Auth cancelled: \(error?.localizedDescription ?? "")")
            return
        }
        let code = URLComponents(url: callbackURL, resolvingAgainstBaseURL: true)?
            .queryItems?.first(where: { $0.name == "code" })?.value
        // Exchange code for token on backend
    }
    session.presentationContextProvider = self
    session.start()
}

// 4. Keychain: Store access token securely
func storeTokenInKeychain(_ token: String) {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: "authToken",
        kSecValueData as String: token.data(using: .utf8)!,
        kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
    ]
    SecItemDelete(query as CFDictionary)
    SecItemAdd(query as CFDictionary, nil)
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Storing tokens in `UserDefaults` | Use Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` for app-only access |
| Not checking `canEvaluatePolicy()` before calling biometrics | Always guard against unavailable hardware; provide fallback |
| Ignoring `identity token` verification | Verify JWT signature on backend; don't trust client alone |
| Not setting `presentationContextProvider` on ASAuthorizationController | Must set delegate & context provider; controller won't display |
| Storing identity token in memory indefinitely | Refresh tokens periodically; revoke on logout |

## Review Checklist

- [ ] Sign in with Apple verified on backend (token signature, nonce)
- [ ] Biometric fallback available if LAContext unavailable
- [ ] Access tokens stored in Keychain, not UserDefaults
- [ ] Refresh tokens implemented; tokens expire & rotate
- [ ] ASWebAuthenticationSession uses correct callbackURLScheme
- [ ] presentationContextProvider set for AuthenticationServices
- [ ] Logout clears Keychain & invalidates tokens
- [ ] Biometric privacy strings (NSFaceIDUsageDescription) in Info.plist
- [ ] Handle authorization state changes (e.g., user revokes)
- [ ] No plaintext passwords logged or stored
- [ ] HTTPS enforced for all auth requests
- [ ] Error messages don't expose user email/account status

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

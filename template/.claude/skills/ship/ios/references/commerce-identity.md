<!-- ship-reference
id: ios-commerce-identity
kind: mixed
sources: iPhoneOS27.0.sdk StoreKit / _StoreKit_SwiftUI / PassKit / AuthenticationServices / LocalAuthentication / Security / CryptoKit / DeviceCheck interfaces and headers (Xcode 27.0 27A266a — every example type-checks via scripts/checks/ios.sh; the CryptoKit round trip runs on the host via scripts/checks/ios_runtime); https://developer.apple.com/documentation/storekit ; https://developer.apple.com/documentation/storekit/testing-in-app-purchases-in-xcode ; https://developer.apple.com/documentation/passkit/apple-pay ; https://developer.apple.com/documentation/authenticationservices ; https://developer.apple.com/documentation/localauthentication ; https://developer.apple.com/documentation/security/keychain-services ; https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility ; https://developer.apple.com/documentation/security/sharing-access-to-keychain-items-among-a-collection-of-apps ; https://developer.apple.com/documentation/devicecheck ; https://developer.apple.com/app-store/review/guidelines/ (June 8, 2026 revision) ; https://developer.apple.com/app-store/subscriptions/ (Terms of Use and privacy policy links; 2026-09-28) (all checked 2026-09-24). Written for Ship from Apple's docs and the SDK; no third-party text. Capability inventory for §5b credited: ivan-magda/swift-security-skill@bda2e0c (MIT) — text written from Apple's Keychain documentation.
reviewed: 2026-09-25
-->
# Accounts, purchases, and trust

**When to read:** a paywall, "restore purchases", subscriptions, a tip jar, Apple Pay, Wallet
passes, sign-in / sign-up / account deletion / logout, "remember me", Face ID, storing a token,
moving tokens out of `UserDefaults`, sharing credentials with an extension, encrypting data, fraud
or "is this a real device?". **Apple** = platform requirement or App Review rule;
**Ship** = Ship default (overridable by `DECISIONS.md`).

## 1. Which payment path (App Review 3.1)

| Selling | Path |
|---|---|
| Digital content, features, subscriptions used in the app | **In-App Purchase** (StoreKit) — Apple, 3.1.1 |
| Physical goods or services used outside the app | Apple Pay or another processor — **not** IAP (3.1.3(e)) |
| Fundraising | Approved nonprofits: in the app with Apple Pay (3.2.1(vi)); otherwise collect outside the app (3.2.2) |

**Apple:** restorable purchases (non-consumables, subscriptions) need a way to restore (3.1.1).
Subscriptions must say what the person gets, for how long, and the price before purchase (3.1.2).
Rules change — read the current guideline text before launch (`frameworks.md` › App Review checks).

## 2. In-App Purchase with StoreKit 2

**Prerequisites:** paid developer account with the Paid Apps agreement; products created in App
Store Connect; a local **StoreKit configuration file** (File › New › StoreKit Configuration, sync
it from App Store Connect) selected in the scheme for development. No server is required for a
simple app; a server that grants access elsewhere uses the App Store Server API.

**The rules that prevent lost or free purchases:**
1. **Start listening at launch.** Iterate `Transaction.updates` from app start for the whole app
   lifetime. Renewals, Ask to Buy approvals, refunds, and purchases on other devices arrive only
   there.
2. **Entitlement = current transactions, not a saved flag.** Recompute access from
   `Transaction.currentEntitlements` at launch, after every update, and when the app becomes active
   again: a subscription that simply runs out creates no transaction, so `Transaction.updates` never
   reports the lapse (`Product.SubscriptionInfo.Status.updates`, iOS 15, reports status changes).
   Skip `revocationDate != nil`. A `UserDefaults` "isPro" is a cache at best.
3. **Only trust `.verified`.** `VerificationResult.unverified` means the JWS didn't check out —
   don't grant, and tell the person the purchase couldn't be confirmed rather than returning silently.
4. **Finish after granting.** Call `transaction.finish()` once access is recorded; unfinished
   transactions are re-delivered.
5. **Handle every purchase outcome:** `.success`, `.pending` (Ask to Buy / SCA — say "waiting for
   approval", don't grant), `.userCancelled` (silence), thrown errors (show a retry).
6. **Restore** = `AppStore.sync()`, only from an explicit button (it can prompt for the Apple
   Account password). The system store views can show it for you (`.storeButton(.visible, for: .restorePurchases)`).
7. Link purchases to your own account system with `.appAccountToken(uuid)` if you have one.

**Ship:** use `SubscriptionStoreView` / `ProductView` / `StoreView` (iOS 17) for standard offers
(`swiftui-ship.md` §3); a custom paywall needs a stated reason.

```swift
import StoreKit

@Observable @MainActor
final class Entitlements {
    private(set) var unlocked: Set<String> = []     // product IDs the person owns right now
    private var updates: Task<Void, Never>?

    func start() {
        updates = Task { [weak self] in
            for await result in StoreKit.Transaction.updates {
                await self?.handle(result)
            }
        }
        Task { await refresh() }
    }

    func refresh() async {
        var owned: Set<String> = []
        for await result in StoreKit.Transaction.currentEntitlements {
            if case .verified(let transaction) = result, transaction.revocationDate == nil {
                owned.insert(transaction.productID)
            }
        }
        unlocked = owned
    }

    func handle(_ result: VerificationResult<StoreKit.Transaction>) async {
        guard case .verified(let transaction) = result else { return }   // never grant unverified
        await refresh()
        await transaction.finish()
    }
}

struct ProPaywall: View {
    @Environment(Entitlements.self) private var entitlements
    let groupID: String            // subscription group ID from App Store Connect
    let termsURL: URL              // your Terms of Use (or Apple's standard EULA)
    let privacyURL: URL            // your privacy policy

    var body: some View {
        SubscriptionStoreView(groupID: groupID)
            .storeButton(.visible, for: .restorePurchases, .policies)
            .subscriptionStorePolicyDestination(url: termsURL, for: .termsOfService)
            .subscriptionStorePolicyDestination(url: privacyURL, for: .privacyPolicy)
            .onInAppPurchaseCompletion { _, result in
                if case .success(.success(let verification)) = result {
                    await entitlements.handle(verification)
                }
            }
    }
}
```

A subscription screen needs working Terms of Use and privacy policy links (Apple: the app and its App
Store metadata must link both); `.policies` shows them. In a file that also imports SwiftUI, write `StoreKit.Transaction` — SwiftUI has its own
`Transaction` and the bare name doesn't compile. Call `entitlements.start()` once from the `App`
(e.g. the root view's `.task`) and inject it with `.environment`. Subscription state for UI ("renews on…", billing retry,
grace period): `.subscriptionStatusTask(for: groupID)`; "Manage subscription":
`.manageSubscriptionsSheet(isPresented:)`; offer codes: `.offerCodeRedemption(isPresented:)`;
refunds: `.refundRequestSheet(for:isPresented:)`.

**Test (in this order):**
1. Xcode + StoreKit configuration: buy, cancel, fail, Ask to Buy (`.pending`), refund, and
   subscription renewal / expiry at accelerated time — Debug › StoreKit › Manage Transactions.
2. Unit tests with `StoreKitTest` (`SKTestSession`) in an **app-hosted** test target for the
   entitlement logic.
3. Sandbox account on a device, then TestFlight — real receipts, real Apple Account prompts.
Simulator runs of step 1 don't prove App Store Connect product setup; step 3 does.

## 3. Apple Pay and Wallet

- **Prerequisites (Apple):** a merchant ID, the Apple Pay capability, a payment processing
  certificate from your payment provider; your server (or provider SDK) charges the token — the
  app never "completes" a payment by itself.
- Show `PayWithApplePayButton` only when `PKPaymentAuthorizationController.canMakePayments()` is
  true; otherwise offer your other checkout. Summary items end with your business name as the total.
- Wallet passes are signed `.pkpass` files made by your server; add them with
  `AddPassToWalletButton` (iOS 16) and keep them updated via the pass web service.
- **Test:** sandbox tester account with Apple's test cards on a device; the simulator shows the
  sheet but proves nothing about your processor.

## 4. Sign-in, passkeys, and account deletion

- **Ship:** ask for an account only when a feature needs it (`hig-ios.md` §8).
- **Apple 4.8:** offering a third-party or social login as the primary option requires an
  equivalent private login option (Sign in with Apple qualifies).
- **Sign in with Apple:** add the capability; `SignInWithAppleButton` (AuthenticationServices).
  Name and email arrive **only on the first authorization** — save them then. At launch check
  `ASAuthorizationAppleIDProvider().credentialState(forUserID:)`; `.revoked`/`.notFound` → sign out
  locally. Verify the identity token on your server.
- **Passkeys:** Associated Domains `webcredentials:<your-domain>` + `apple-app-site-association`
  on the server; `ASAuthorizationPlatformPublicKeyCredentialProvider(relyingPartyIdentifier:)`;
  the server issues the challenge and verifies the result. In SwiftUI, perform requests with
  `@Environment(\.authorizationController)`.
- **Apple 5.1.1(v):** an app that lets people create an account must let them delete it in the
  app — delete server data, revoke Sign in with Apple tokens (REST `revoke`), sign out locally.
- **Session expiry:** a 401 means "sign in again" with the person's in-progress work kept
  (`hardening-guide.md`).

```swift
import AuthenticationServices

struct SignInScreen: View {
    let onSignedIn: (String) -> Void          // Apple user ID → your session layer

    var body: some View {
        SignInWithAppleButton(.signIn) { request in
            request.requestedScopes = [.fullName, .email]
        } onCompletion: { result in
            guard case .success(let auth) = result,
                  let credential = auth.credential as? ASAuthorizationAppleIDCredential else { return }
            // First sign-in only: credential.fullName / credential.email — persist them now.
            onSignedIn(credential.user)       // send credential.identityToken to your server to verify
        }
        .signInWithAppleButtonStyle(.black)
        .frame(height: 50)
    }
}
```

## 5. Keychain — tokens and secrets

- Secrets (tokens, API keys the person entered, encryption keys) live in the Keychain, never in
  `UserDefaults`, files, or the bundle. Ship-owned API keys don't belong in the app at all — proxy
  through your server.
- **Add or update:** `SecItemAdd` fails with `errSecDuplicateItem` if the item exists — update it
  instead. Always check the `OSStatus`.
- **Accessibility class** decides when the item is readable: `…AfterFirstUnlockThisDeviceOnly` for
  tokens a background refresh needs; `…WhenUnlockedThisDeviceOnly` otherwise. `ThisDeviceOnly`
  keeps it out of backups and other devices.
- **Every helper takes a `KeychainScope`** (service + access group) — see §5b for why the group
  must be explicit once the app shares Keychain items. Items **survive app deletion** — if a fresh
  install must start signed out, clear on first launch (flag in `UserDefaults`).

```swift
import Security

enum KeychainError: Error { case status(OSStatus) }

/// Which items a helper may touch: one service in one access group. Add, read, update, and delete
/// all build their query here, so an operation in one scope can't reach another group's items.
nonisolated struct KeychainScope: Sendable {
    var service: String
    /// Written out in full (`<TeamID>.com.example.shared`). `nil` = no group in the query: adds go
    /// to the app's first access group, but reads, updates, and deletes search *all* its groups —
    /// only safe while the app has no Keychain Sharing or App Group entitlement.
    var accessGroup: String?

    func query(account: String?) -> [String: Any] {
        var query: [String: Any] = [kSecClass as String: kSecClassGenericPassword,
                                    kSecAttrService as String: service]
        if let account { query[kSecAttrAccount as String] = account }
        if let accessGroup { query[kSecAttrAccessGroup as String] = accessGroup }
        return query
    }

    /// The app's own session tokens. Name the group here as soon as the app shares Keychain items.
    static let session = KeychainScope(service: "app.session", accessGroup: nil)
}

nonisolated func saveSecret(_ data: Data, account: String, in scope: KeychainScope) throws {
    let item = scope.query(account: account)
    let attributes: [String: Any] = [kSecValueData as String: data,
                                     kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly]
    var status = SecItemUpdate(item as CFDictionary, attributes as CFDictionary)
    if status == errSecItemNotFound {
        status = SecItemAdd(item.merging(attributes) { $1 } as CFDictionary, nil)
    }
    guard status == errSecSuccess else { throw KeychainError.status(status) }
}

nonisolated func readSecret(account: String, in scope: KeychainScope) throws -> Data? {
    var query = scope.query(account: account)
    query[kSecReturnData as String] = true
    query[kSecMatchLimit as String] = kSecMatchLimitOne
    var item: CFTypeRef?
    let status = SecItemCopyMatching(query as CFDictionary, &item)
    if status == errSecItemNotFound { return nil }
    guard status == errSecSuccess else { throw KeychainError.status(status) }
    return item as? Data
}

/// `account: nil` deletes every account's item in the scope (sign-out).
nonisolated func deleteSecrets(account: String?, in scope: KeychainScope) throws {
    let status = SecItemDelete(scope.query(account: account) as CFDictionary)
    guard status == errSecSuccess || status == errSecItemNotFound else { throw KeychainError.status(status) }
}
```

### 5b. Credential lifecycle — choose, share, refresh, sign out, migrate

**Pick the accessibility class by who reads the item and when** (a Keychain item without
`kSecAttrAccessible` gets a default you didn't choose — always set it):

| Item | Class | Why |
|---|---|---|
| Access/refresh tokens the app uses in the foreground | `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | Readable only while unlocked; never leaves this device |
| Tokens a background task, notification service extension, or widget needs | `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` | Readable after the first unlock since boot, including while locked |
| Keys that must disappear if the passcode is removed | `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | Deleted with the passcode |
| Credentials that should follow the person to a new device | a non-`ThisDeviceOnly` class (+ `kSecAttrSynchronizable` for iCloud Keychain) | Only when that's a product decision |

- `ThisDeviceOnly` items **don't migrate** to a new device (restore from backup or Quick Start):
  expect a signed-out first launch there and make sign-in painless.
- **Locked device:** reading a `WhenUnlocked` item while locked (a background refresh) fails with
  `errSecInteractionNotAllowed`. That's "try later", **not** "signed out" — never clear the session
  on it; retry after `UIApplication.protectedDataDidBecomeAvailableNotification`.
- **Access groups (Apple's `kSecAttrAccessGroup` docs):** an add without a group lands in the
  app's *first* access group; a read, update, or delete without one searches *all* the app's
  groups — so a group-less update or sign-out delete can change another group's item. Once the app
  has Keychain Sharing or App Groups, give **every** scope its group, the app-private one included.
  To share with an extension, add the group to both targets' Keychain Sharing capability and use
  that scope in both; an extension that can't see the item is missing the entitlement or wrote it
  with a different scope.
- **Refresh rotation:** one refresh at a time (`swift-practice.md` §3 single-flight); write the new
  access **and** refresh token together before discarding the old ones; a refresh that returns
  401/`invalid_grant` means the session is gone — sign out (below), keep the person's unsaved work.
- **Sign out** removes everything tied to the account, not just one token:
  1. revoke the refresh token on the server (best effort; sign out locally even if offline);
  2. `deleteSecrets(account: nil, in:)` for **each** scope the app writes (service + group, no
     account, removes every account's item in that group — and only that group);
  3. clear cookies (`HTTPCookieStorage`), `URLCache`, per-account files and database rows, App Group
     caches the widget reads (then reload widgets), and the push token registration on the server;
  4. cancel in-flight tasks and reset in-memory models, then show signed-out UI.
- **Moving tokens out of `UserDefaults`:** read the old value → write it to the Keychain → read it
  back → only then delete the old key and record that migration ran. If the Keychain write fails
  (for example, device locked), keep the old value and try again next launch — a migration must
  never sign the person out. Run it before the first network call.

```swift
// continues: #2 — uses KeychainScope and the helpers from §5
import Foundation

protocol SecretStore {
    func read(_ account: String) throws -> Data?
    func write(_ data: Data, _ account: String) throws
    func delete(_ account: String) throws
}

/// Keychain-backed store: every call stays inside one scope.
struct KeychainSecretStore: SecretStore {
    var scope: KeychainScope = .session
    func read(_ account: String) throws -> Data? { try readSecret(account: account, in: scope) }
    func write(_ data: Data, _ account: String) throws { try saveSecret(data, account: account, in: scope) }
    func delete(_ account: String) throws { try deleteSecrets(account: account, in: scope) }
}

enum MigrationOutcome: Equatable { case nothingToMove, moved, alreadyDone, retryLater }

/// Moves a token from UserDefaults to the secret store without ever losing it. Idempotent.
/// Runs once at launch, before the first network call (fast enough for the main actor).
func migrateToken(defaultsKey: String, account: String,
                              defaults: UserDefaults, store: some SecretStore) -> MigrationOutcome {
    let doneKey = "migrated.\(defaultsKey).v1"
    if defaults.bool(forKey: doneKey) { return .alreadyDone }
    guard let legacy = defaults.string(forKey: defaultsKey), let data = legacy.data(using: .utf8) else {
        defaults.set(true, forKey: doneKey)
        return .nothingToMove
    }
    do {
        try store.write(data, account)
        guard try store.read(account) == data else { return .retryLater }   // verify before deleting
    } catch {
        return .retryLater                                                  // keep the old copy; try next launch
    }
    defaults.removeObject(forKey: defaultsKey)
    defaults.set(true, forKey: doneKey)
    return .moved
}
```

The migration function runs in Ship's host tests against an in-memory store, including a failing
write (`ios_runtime/credential_migration`). `ios_runtime/keychain_scope` records the queries the
helpers above send to a stand-in for `SecItem*` that follows Apple's documented group rules — each
scope's add, read, update, and delete carries its group and leaves the other group's items alone.
The real Keychain isn't touched by either: check entitlements, sharing with the extension, and
locked-device reads on a device.

## 6. Face ID / Touch ID

- **Apple:** `NSFaceIDUsageDescription` in Info.plist, or Face ID fails.
- A `Bool` from `evaluatePolicy` is a UI gate, not protection: on a compromised device it can be
  forced to `true`. When biometrics protect **data**, store the data in the Keychain with a
  `SecAccessControl` that requires biometry (`.biometryCurrentSet`, or `.userPresence` to allow
  the passcode) — then the Keychain itself refuses to return it without a match.
- `.deviceOwnerAuthentication` (biometry or passcode) for "confirm it's you";
  `.deviceOwnerAuthenticationWithBiometrics` only when the passcode must not be accepted.
- Handle `LAError`: `.userCancel`/`.appCancel` (silent), `.biometryNotEnrolled`/`.biometryNotAvailable`
  (offer the passcode or your sign-in), `.biometryLockout` (passcode unlocks it).
- **Test:** simulator Features › Face ID › Enrolled / Matching / Non-matching for the flows;
  a physical device for Keychain access control.

```swift
import LocalAuthentication

nonisolated func confirmOwner(reason: String) async -> Bool {
    let context = LAContext()
    var error: NSError?
    guard context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error) else { return false }
    do { return try await context.evaluatePolicy(.deviceOwnerAuthentication, localizedReason: reason) }
    catch { return false }        // LAError.userCancel etc. — let the caller keep the current screen
}

/// Keychain item that only comes back after a biometric match (the real protection).
nonisolated func biometryProtectedQuery(account: String, secret: Data) -> [String: Any]? {
    guard let access = SecAccessControlCreateWithFlags(nil, kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
                                                      .biometryCurrentSet, nil) else { return nil }
    return [kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecAttrAccessControl as String: access,
            kSecValueData as String: secret]
}
```

## 7. Encryption and device trust

- **CryptoKit** for app-level crypto: `AES.GCM` / `ChaChaPoly` to encrypt, `HKDF` to derive keys,
  `P256`/`Curve25519` to sign and agree keys, `SHA256` (SHA-3 is iOS 26+). Post-quantum:
  `MLKEM768`/`MLKEM1024` and `XWingMLKEM768X25519` are iOS 26+. Never invent a scheme; keep keys
  in the Keychain or the Secure Enclave.
- **Secure Enclave** keys (`SecureEnclave.P256.Signing.PrivateKey`) never leave the chip; check
  `SecureEnclave.isAvailable` (false on the simulator) and persist the key's
  `dataRepresentation` (an encrypted handle) in the Keychain.
- **App Attest** (`DCAppAttestService`) proves requests come from your genuine app on a real
  device: generate a key, attest it against a **server challenge**, then sign requests with
  assertions; the server verifies everything. `isSupported` is false on the simulator and some
  devices — design a fallback (rate limits, risk scoring), not a hard block.

```swift
import CryptoKit

nonisolated func seal(_ plaintext: Data, key: SymmetricKey) throws -> Data {
    try AES.GCM.seal(plaintext, using: key).combined!   // combined is non-nil with the default 12-byte nonce
}

nonisolated func open(_ sealed: Data, key: SymmetricKey) throws -> Data {
    try AES.GCM.open(AES.GCM.SealedBox(combined: sealed), using: key)
}
```

## 8. Verify

| What | How | Level |
|---|---|---|
| Purchase outcomes, renewals, refunds, Ask to Buy | Xcode StoreKit configuration + Transaction Manager | Simulator/device, local |
| Entitlement logic | `StoreKitTest` in an app-hosted test | CI |
| Real products, prices, restore | Sandbox account on device; TestFlight | **Manual, device + App Store Connect** |
| Apple Pay | Sandbox tester cards on device, your processor's test mode | **Manual, device + server** |
| Sign in with Apple / passkeys | Device with an Apple Account; revoke in Settings › Apple Account › Sign-In & Security and relaunch | **Manual, device + server** |
| Account deletion | Delete in app → server data gone, SIWA token revoked, signed out | Manual + server log |
| Keychain | Save/read/update/delete; reinstall behaviour; background refresh while locked (expect `errSecInteractionNotAllowed`, not sign-out) | Device (Keychain classes differ from the simulator's) |
| Migration from `UserDefaults` | Host test with a failing store; then upgrade a build that stored the token in defaults, on a device | CI + **device** |
| Sign out | After logout: no Keychain items for the service, no cookies, widget shows signed-out, server token revoked | Manual + server log |
| Extension access | Notification service extension / widget reads the token with the shared access group, device locked | **Device** |
| Biometry | Simulator enrolled/matching/non-matching; device for access control | Simulator + **device** |
| App Attest | Device only; server verification logs | **Manual, device + server** |

Apple: [StoreKit](https://developer.apple.com/documentation/storekit) ·
[Testing in Xcode](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-in-xcode) ·
[Apple Pay](https://developer.apple.com/documentation/passkit/apple-pay) ·
[Passkeys](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication) ·
[Keychain services](https://developer.apple.com/documentation/security/keychain-services) ·
[App Attest](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity) ·
Xcode 27: `AdditionalDocumentation/StoreKit-Updates.md`, `audit-xcode-security-settings`.

# StoreKit 2 — iOS Reference

> **When to read:** Dev reads this when implementing in-app purchases, subscriptions, or receipt validation.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `StoreKit.Product` | Represents purchasable item | Fetched via `Product.products(for:)` |
| `StoreKit.Transaction` | Completed purchase record | Includes bundle ID, user, expiration, revocation status |
| `StoreKit.AppTransaction` | App-level receipt data | Signed; verify on backend |
| `SubscriptionInfo` | Active subscriptions for user | Grouped by subscription group |
| `VerificationResult<T>` | Validates JWS-signed data | Unwrap with `.unsafePayload` or `try checkVerified()` |
| `StoreKit.purchaseState` | Current subscription status | `.subscribed`, `.expired`, `.revoked` |
| `.subscriptionStoreView()` | SwiftUI view | Renders in-app subscription UI; handles purchase flow |
| `.productView()` | SwiftUI view | Merchandise individual products |
| `.storeView()` | SwiftUI view | Multiple products with localized prices |
| `Transaction.updates` | AsyncSequence of transactions | Listen for purchase completion, refunds, renewals |
| `AppStore.sync()` | Sync transactions | Manual restore purchases; auto-called by system |
| `.currentEntitlementTask(for:)` | SwiftUI modifier | Check if user has entitlement; returns AsyncSequence |
| `.storeButton(.visible, for:)` | SwiftUI modifier | Show restore/redeem buttons on store views |

## Code Examples

```swift
// 1. Fetch products and display
import StoreKit

@Observable
class PremiumStore {
    var products: [Product] = []
    var userID: UUID { UUID() } // Your user ID for server reconciliation

    func loadProducts() async {
        do {
            self.products = try await Product.products(for: ["com.myapp.pro.monthly"])
        } catch {
            print("Failed to load products: \(error)")
        }
    }

    func purchaseProduct(_ product: Product) async -> Bool {
        do {
            let result = try await product.purchase(options: [
                .appAccountToken(userID)  // For server-side reconciliation
            ])
            switch result {
            case .success(let verification):
                let transaction = try checkVerified(verification)
                await transaction.finish()
                return true
            case .userCancelled:
                return false
            case .pending:
                print("Purchase pending approval (Ask to Buy)")
                return false
            @unknown default:
                return false
            }
        } catch {
            print("Purchase failed: \(error)")
            return false
        }
    }

    func restorePurchases() async {
        do {
            try await AppStore.sync()
            // After sync, Transaction.currentEntitlements will reflect restored purchases
        } catch {
            print("Restore failed: \(error)")
        }
    }
}

// 2. Use subscriptionStoreView and store buttons
struct PremiumView: View {
    var body: some View {
        SubscriptionStoreView(groupID: "group1")
            .subscriptionStoreButtonLabel(.multiline)
            .subscriptionStorePickerItemBackground(.white)
            .storeButton(.visible, for: .restorePurchases)
            .storeButton(.visible, for: .redeemCode)
            .subscriptionStorePolicyDestination(
                url: URL(string: "https://example.com/terms")!,
                for: .termsOfService
            )
            .subscriptionStorePolicyDestination(
                url: URL(string: "https://example.com/privacy")!,
                for: .privacyPolicy
            )
    }
}

// 3. Use StoreView for multiple products
struct StoreView: View {
    var body: some View {
        StoreView(ids: ["com.app.gems100", "com.app.premium"], prefersPromotionalIcon: true)
            .storeButton(.visible, for: .restorePurchases)
            .onInAppPurchaseCompletion { _, result in
                if case .success(.verified(let transaction)) = result {
                    Task { await transaction.finish() }
                }
            }
    }
}

// 3. Listen for transaction updates
func listenForTransactions() async {
    for await update in Transaction.updates {
        do {
            let transaction = try checkVerified(update)

            switch transaction.productType {
            case .autoRenewable:
                handleSubscription(transaction)
            case .nonConsumable:
                handleNonConsumable(transaction)
            case .consumable:
                handleConsumable(transaction)
            @unknown default:
                break
            }

            await transaction.finish()
        } catch {
            print("Transaction verification failed: \(error)")
        }
    }
}

// 4. Check subscription status
func checkSubscriptionStatus() async {
    do {
        var activeSubscription: SubscriptionInfo?

        for await result in Transaction.currentEntitlements {
            let transaction = try checkVerified(result)
            if transaction.productType == .autoRenewable {
                activeSubscription = transaction.subscription
            }
        }

        if let subscription = activeSubscription {
            print("Active subscription: \(subscription.subscriptionGroupID)")
            print("Expires: \(subscription.expirationDate ?? Date())")
        } else {
            print("No active subscription")
        }
    } catch {
        print("Failed to check entitlements: \(error)")
    }
}

// 5. Check subscription renewal state (detailed)
func checkSubscriptionState() async {
    do {
        let statuses = try await Product.SubscriptionInfo.Status.status(for: "group_id")
        for status in statuses {
            guard case .verified = status.renewalInfo,
                  case .verified = status.transaction else { continue }

            switch status.state {
            case .subscribed:
                print("Active subscription")
            case .inBillingRetryPeriod:
                print("Payment failed; Apple is retrying (user retains access)")
            case .inGracePeriod:
                print("Billing retry exhausted; grace period active (user retains access)")
            case .revoked:
                print("Subscription revoked")
            case .expired:
                print("Subscription expired")
            @unknown default:
                break
            }
        }
    } catch {
        print("Failed: \(error)")
    }
}

// 6. Purchase with options
func purchaseWithOptions(_ product: Product, userID: UUID) async throws {
    let result = try await product.purchase(options: [
        .appAccountToken(userID),           // Server-side reconciliation
        .quantity(1),                       // Consumable quantity (if applicable)
        .simulatesAskToBuyInSandbox(true)   // Test Ask to Buy in sandbox
    ])
    switch result {
    case .success(let verification):
        let transaction = try checkVerified(verification)
        await transaction.finish()
    case .userCancelled, .pending:
        break
    @unknown default:
        break
    }
}

// 7. Backend receipt validation
func validateReceiptOnBackend(appTransaction: AppTransaction) async {
    let jws = appTransaction.signedJWT
    // Send jws to backend; backend verifies signature using Apple's public key
    // Backend confirms: app ID, user, purchase date, subscription expiry
}
```

## Subscription Renewal States

| State | Meaning | User Access | Action |
|---|---|---|---|
| `.subscribed` | Actively subscribed | Full access | Normal billing |
| `.inBillingRetryPeriod` | Payment failed | **Retain access** | Apple retrying; user should update payment |
| `.inGracePeriod` | Billing retry exhausted | **Retain access** | Fallback for failed renewal; user must fix payment |
| `.revoked` | Subscription canceled/refunded | No access | Check `revocationDate` |
| `.expired` | Subscription term ended | No access | Renew if user wants to re-subscribe |

## Purchase Options Reference

```swift
// App account token for server-side reconciliation
try await product.purchase(options: [
    .appAccountToken(UUID())
])

// Consumable quantity (gems, credits, etc.)
try await product.purchase(options: [
    .quantity(5)  // Purchase 5 units
])

// Simulate Ask to Buy in sandbox testing
try await product.purchase(options: [
    .simulatesAskToBuyInSandbox(true)
])

// Combine multiple options
try await product.purchase(options: [
    .appAccountToken(userID),
    .quantity(1),
    .simulatesAskToBuyInSandbox(false)
])
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Forgetting to call `transaction.finish()` after purchase | Always finish transactions; required for reporting to App Store |
| Using `.unsafePayload` without verifying signature | Use `try checkVerified(verification)` to validate JWS signature |
| Not listening to `Transaction.updates` for background renewals | Implement async loop for `Transaction.updates` to handle renewals/refunds |
| Hardcoding product IDs without fetching via `Product.products()` | Always fetch live product metadata; enables server-side pricing changes |
| Testing real purchases in production app | Use App Store sandbox testing; separate test accounts for IAP |
| Not calling `AppStore.sync()` for restore purchases | Always call `AppStore.sync()` before checking `Transaction.currentEntitlements` |
| Ignoring billing retry and grace period states | Subscriptions in `.inBillingRetryPeriod` or `.inGracePeriod` should retain access |
| Not using `ProductView` or `StoreView` for UI | Use native views; manual pricing display often has bugs or is outdated |
| Ignoring `.currentEntitlementTask(for:)` modifier | Use it for clean, reactive entitlement checking in SwiftUI |
| Not handling store view callbacks | Always use `.onInAppPurchaseCompletion` to finish transactions on store views |

### Additional Common Mistakes (Extended)

**AppStore.sync() not called**

DON'T:
```swift
// User taps Restore, nothing happens
print("No purchases to restore")
```

DO:
```swift
func restorePurchases() async {
    try await AppStore.sync()
    await updateEntitlements()
}
```

**Not checking inBillingRetryPeriod or inGracePeriod**

DON'T:
```swift
if status.state == .subscribed {
    unlockFeature()
}
```

DO:
```swift
if status.state == .subscribed ||
   status.state == .inBillingRetryPeriod ||
   status.state == .inGracePeriod {
    unlockFeature()  // User retains access
}
```

**Not using .currentEntitlementTask modifier**

DO:
```swift
.currentEntitlementTask(for: ProductID.premium) { state in
    self.entitlementState = state
}
```

## Review Checklist

- [ ] Products fetched via `Product.products(for:)` (not hardcoded)
- [ ] Transaction verification using `checkVerified()` before processing
- [ ] `transaction.finish()` called after all handling
- [ ] `Transaction.updates` async loop active (not one-time check)
- [ ] Subscription group ID matches App Store configuration
- [ ] Backend validates `AppTransaction.signedJWT` on key operations
- [ ] `.subscriptionStoreView()` used for native subscription UI
- [ ] Consumable products tracked in app state (not assumed via receipt)
- [ ] Refund/revocation handling in place (check `isUpgraded`, `revocationDate`)
- [ ] Sandbox testing account configured in App Store Connect
- [ ] Receipts refreshed if missing (manual `AppStore.sync()` call)
- [ ] Error handling for network, verification, and purchase failures

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

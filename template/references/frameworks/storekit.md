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
| `.subscriptionStoreView()` | SwiftUI modifier | Renders in-app subscription UI; handles purchase flow |
| `Transaction.updates` | AsyncSequence of transactions | Listen for purchase completion, refunds, renewals |

## Code Examples

```swift
// 1. Fetch products and display
import StoreKit

@Observable
class PremiumStore {
    var products: [Product] = []

    func loadProducts() async {
        do {
            self.products = try await Product.products(for: ["com.myapp.pro.monthly"])
        } catch {
            print("Failed to load products: \(error)")
        }
    }

    func purchaseProduct(_ product: Product) async -> Bool {
        do {
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                let transaction = try checkVerified(verification)
                await transaction.finish()
                return true
            case .userCancelled:
                return false
            case .pending:
                print("Purchase pending approval")
                return false
            @unknown default:
                return false
            }
        } catch {
            print("Purchase failed: \(error)")
            return false
        }
    }
}

// 2. Use subscriptionStoreView modifier in SwiftUI
struct PremiumView: View {
    var body: some View {
        SubscriptionStoreView(groupID: "group1")
            .subscriptionStoreButtonLabel(.multiline)
            .subscriptionStorePickerItemBackground(.white)
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

// 5. Backend receipt validation
func validateReceiptOnBackend(appTransaction: AppTransaction) async {
    let jws = appTransaction.signedJWT
    // Send jws to backend; backend verifies signature using Apple's public key
    // Backend confirms: app ID, user, purchase date, subscription expiry
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Forgetting to call `transaction.finish()` after purchase | Always finish transactions; required for reporting to App Store |
| Using `.unsafePayload` without verifying signature | Use `try checkVerified(verification)` to validate JWS signature |
| Not listening to `Transaction.updates` for background renewals | Implement async loop for `Transaction.updates` to handle renewals/refunds |
| Hardcoding product IDs without fetching via `Product.products()` | Always fetch live product metadata; enables server-side pricing changes |
| Testing real purchases in production app | Use App Store sandbox testing; separate test accounts for IAP |

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

# PassKit & Apple Pay — iOS Reference

> **When to read:** Dev reads this when building features with Apple Pay, digital passes, wallet integration, or payment authorization.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `PKPaymentAuthorizationViewController` | Presents Apple Pay sheet; UIKit |
| `PKPaymentAuthorizationResult` | Response from payment request; success/failure |
| `PKPaymentRequest` | Defines payment amount, merchant, supported methods |
| `PKPaymentMethod` | Payment card/wallet method; `.card`, `.applePay` |
| `PKPaymentSummaryItem` | Line item: label + amount (regular, pending, final) |
| `PKShippingMethod` | Shipping option; identifier, label, cost |
| `PKContact` | Billing/shipping contact; name, address, email, phone |
| `PKPass` | Digital pass; loaded from .pkpass file |
| `PKPassLibrary` | Manages wallet passes; add, remove, update |
| `PKPaymentToken` | Encrypted payment data from successful transaction |
| `PKPaymentNetwork` | Supported networks: `.visa`, `.masterCard`, `.amex`, `.discover` |
| `PKMerchantCapability` | Capabilities: `supports3DS`, `supportsEMV`, `supportsCredit`, `supportsDebit` |

---

## Code Examples

### Example 1: Apple Pay payment request (UIKit)
```swift
import PassKit

class PaymentViewController: UIViewController, PKPaymentAuthorizationViewControllerDelegate {
    let merchantIdentifier = "merchant.com.example.app"

    func initiateApplePayPayment(amount: NSDecimalNumber) {
        guard PKPaymentAuthorizationViewController.canMakePayments() else {
            print("Apple Pay not available")
            return
        }

        let paymentRequest = PKPaymentRequest()
        paymentRequest.merchantIdentifier = merchantIdentifier
        paymentRequest.countryCode = "US"
        paymentRequest.currencyCode = "USD"

        // Define supported networks
        paymentRequest.supportedNetworks = [.visa, .masterCard, .amex]

        // Capabilities: what payment methods device supports
        paymentRequest.merchantCapabilities = [.capability3DS, .supportsEMV]

        // Payment summary items
        let item = PKPaymentSummaryItem(label: "Widget", amount: amount, type: .final)
        paymentRequest.paymentSummaryItems = [item]

        // Optional: request shipping/billing contact
        paymentRequest.requiredShippingContactFields = [.postalAddress, .email]

        guard let paymentVC = PKPaymentAuthorizationViewController(paymentRequest: paymentRequest) else {
            return
        }

        paymentVC.delegate = self
        present(paymentVC, animated: true)
    }

    // MARK: - PKPaymentAuthorizationViewControllerDelegate
    func paymentAuthorizationViewController(
        _ controller: PKPaymentAuthorizationViewController,
        didAuthorizePayment payment: PKPayment,
        handler completion: @escaping (PKPaymentAuthorizationResult) -> Void
    ) {
        // Validate and process payment token
        let token = payment.token
        let encryptedData = String(data: token.paymentData, encoding: .utf8) ?? ""
        print("Payment token: \(encryptedData)")

        // Send to server for validation/processing
        processPaymentOnServer(token: token) { success in
            let result = PKPaymentAuthorizationResult(
                status: success ? .success : .failure,
                errors: []
            )
            completion(result)
        }
    }

    func paymentAuthorizationViewControllerDidFinish(_ controller: PKPaymentAuthorizationViewController) {
        dismiss(animated: true)
    }

    func processPaymentOnServer(token: PKPaymentToken, completion: @escaping (Bool) -> Void) {
        // Encrypt and send token.paymentData to backend
        // Backend validates with Apple's payment processor
        completion(true)
    }
}
```

### Example 2: SwiftUI Apple Pay (iOS 16+)
```swift
import SwiftUI
import PassKit

struct ApplePayView: View {
    @State var showPaymentSheet = false

    var body: some View {
        Button(action: { showPaymentSheet = true }) {
            Image(systemName: "apple.logo")
            Text("Pay with Apple Pay")
        }
        .paymentSheet(isPresented: $showPaymentSheet) {
            let paymentRequest = buildPaymentRequest()
            // SwiftUI payment handling
        }
    }

    func buildPaymentRequest() -> PKPaymentRequest {
        let request = PKPaymentRequest()
        request.merchantIdentifier = "merchant.com.example.app"
        request.countryCode = "US"
        request.currencyCode = "USD"
        request.supportedNetworks = [.visa, .masterCard]
        request.merchantCapabilities = [.capability3DS]

        let summary = PKPaymentSummaryItem(label: "Total", amount: NSDecimalNumber(string: "19.99"), type: .final)
        request.paymentSummaryItems = [summary]

        return request
    }
}
```

### Example 3: Add pass to Wallet
```swift
import PassKit

func addPassToWallet(passURL: URL) {
    guard PKPassLibrary.isPassLibraryAvailable() else {
        print("Wallet not available")
        return
    }

    do {
        let passData = try Data(contentsOf: passURL)
        guard let pass = PKPass(data: passData, error: ()) else {
            print("Invalid pass file")
            return
        }

        let passLibrary = PKPassLibrary()
        if passLibrary.containsPass(pass) {
            print("Pass already in wallet")
        } else {
            passLibrary.addPasses([pass], withCompletionHandler: { success in
                print(success ? "Pass added" : "Failed to add pass")
            })
        }
    } catch {
        print("Error loading pass: \(error)")
    }
}
```

### Example 4: List and remove passes
```swift
import PassKit

func listWalletPasses() {
    guard PKPassLibrary.isPassLibraryAvailable() else { return }

    let passLibrary = PKPassLibrary()
    let allPasses = passLibrary.passes()

    allPasses.forEach { pass in
        print("Pass: \(pass.name) (\(pass.passType))")
    }
}

func removePassFromWallet(pass: PKPass) {
    let passLibrary = PKPassLibrary()
    passLibrary.removePass(pass)
    print("Pass removed")
}
```

---

## Common Mistakes

### ❌ Not checking Apple Pay availability
```swift
// Bad: Crashes on devices without Apple Pay
let paymentVC = PKPaymentAuthorizationViewController(paymentRequest: request)
present(paymentVC, animated: true)
```
✅ **Fix:** Check availability first
```swift
if PKPaymentAuthorizationViewController.canMakePayments() {
    let paymentVC = PKPaymentAuthorizationViewController(paymentRequest: request)
    present(paymentVC, animated: true)
} else {
    showAlternativePaymentMethod()
}
```

### ❌ Missing merchant capabilities
```swift
// Bad: Merchant capabilities not specified; request may fail
let paymentRequest = PKPaymentRequest()
paymentRequest.supportedNetworks = [.visa, .masterCard]
// No merchantCapabilities set
```
✅ **Fix:** Set appropriate capabilities and use centralized configuration
```swift
enum PaymentConfig {
    static let merchantIdentifier = "merchant.com.example.app"
    static let countryCode = "US"
    static let currencyCode = "USD"
    static let supportedNetworks: [PKPaymentNetwork] = [.visa, .masterCard, .amex]
}

paymentRequest.merchantIdentifier = PaymentConfig.merchantIdentifier
paymentRequest.supportedNetworks = PaymentConfig.supportedNetworks
paymentRequest.merchantCapabilities = [.capability3DS, .supportsEMV]
```

### ❌ Not validating payment on server
```swift
// Bad: Accept any payment without verification
func paymentAuthorizationViewController(...) {
    completion(PKPaymentAuthorizationResult(status: .success, errors: []))
}
```
✅ **Fix:** Send token to server; verify with Apple
```swift
func paymentAuthorizationViewController(...) {
    let success = verifyPaymentWithServer(payment.token)
    let result = PKPaymentAuthorizationResult(
        status: success ? .success : .failure,
        errors: success ? [] : [PKError(.unknownError)]
    )
    completion(result)
}
```

### ❌ Ignoring payment contact fields
```swift
// Bad: Required fields not requested; user skips billing
let paymentRequest = PKPaymentRequest()
// No requiredBillingContactFields
```
✅ **Fix:** Request necessary contact fields and handle shipping updates
```swift
paymentRequest.requiredBillingContactFields = [.postalAddress, .name]
paymentRequest.requiredShippingContactFields = [.postalAddress, .email, .phone]

// In delegate: handle shipping method selection
func paymentAuthorizationViewController(
    _ controller: PKPaymentAuthorizationViewController,
    didSelectShippingMethod shippingMethod: PKShippingMethod,
    handler completion: @escaping (PKPaymentRequestShippingMethodUpdate) -> Void
) {
    let updatedItems = recalculateItems(with: shippingMethod)
    let update = PKPaymentRequestShippingMethodUpdate(paymentSummaryItems: updatedItems)
    completion(update)
}
```

### ❌ Not handling pass library errors
```swift
// Bad: Silently fails to add pass
let passLibrary = PKPassLibrary()
passLibrary.addPasses([pass], withCompletionHandler: { _ in })
```
✅ **Fix:** Log and handle failures
```swift
passLibrary.addPasses([pass], withCompletionHandler: { success in
    if success {
        print("Pass added successfully")
    } else {
        print("Failed to add pass; check file validity and permissions")
        showErrorAlert()
    }
})
```

---

## Review Checklist

- [ ] `PKPaymentAuthorizationViewController.canMakePayments()` checked before presenting
- [ ] `PKPaymentRequest.merchantIdentifier` set correctly (matches Apple Pay setup)
- [ ] `supportedNetworks` specified (visa, masterCard, amex, discover, etc.)
- [ ] `merchantCapabilities` defined (capability3DS, supportsEMV, supportsCredit, etc.)
- [ ] `paymentSummaryItems` include final item; labels clear for user
- [ ] Required contact fields specified (billing, shipping, email, phone as needed)
- [ ] `PKPaymentToken` sent to backend (never stored locally)
- [ ] Backend validates token with Apple (not accepted blindly)
- [ ] `PKPaymentAuthorizationResult` status correct (success/failure)
- [ ] Pass library availability checked before accessing wallet
- [ ] Passes validated before adding (correct file format, merchant ID)
- [ ] Tests mock PKPaymentAuthorizationViewController for offline testing

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

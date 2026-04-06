# App Store Review Guidelines — iOS Reference

> **When to read:** Dev reads this when submitting to App Store to avoid rejections, verify Info.plist requirements, or understand in-app purchase & privacy rules.

---

## Triage
- **Implement new feature** → Read Common Rejection Reasons + Required Descriptions
- **Fix a bug** → Check Review Checklist first
- **Prepare for submission** → Review Privacy Requirements

---

## Common Rejection Reasons

| Reason | Details | How to Fix |
|--------|---------|-----------|
| **Missing Privacy Descriptions** | No Info.plist usage descriptions for camera, location, etc. | Add all `NS*UsageDescription` keys required by features |
| **Cryptography Disclosure** | Not declared in export docs if using encryption | File ITSAppUsesNonExemptEncryption in App Store Connect |
| **Broken Links** | Support URLs or policy links 404 | Verify all URLs in app + metadata before submission |
| **Misleading Metadata** | Screenshots/description don't match app | Update marketing materials to match actual features |
| **Guideline 4.3** | Design clones, minimal functionality | Ensure unique value, custom UI, clear purpose |
| **Guideline 5.1** | Deceptive pricing, hidden charges | All costs upfront, no surprise fees |
| **Guideline 2.1** | App requests data not used by app | Only request permissions actively needed |
| **Guideline 1.1** | App crashes on launch | Test on multiple iOS versions, devices |
| **Background Tasks** | Unsupported background mode declared | Only declare modes actually used |
| **Spam/Duplicate** | Similar app already submitted | Ensure differentiation from existing apps |

---

## Required Info.plist Entries

Add these keys **only if features are used**:

| Permission | Key | Example Value |
|-----------|-----|----------------|
| **Camera** | `NSCameraUsageDescription` | "We need camera access to take photos for your profile" |
| **Microphone** | `NSMicrophoneUsageDescription` | "Microphone access for voice calls" |
| **Location** | `NSLocationWhenInUseUsageDescription` | "Location used to find nearby stores" |
| **Location (Always)** | `NSLocationAlwaysAndWhenInUseUsageDescription` | "Background location for delivery tracking" |
| **Contacts** | `NSContactsUsageDescription` | "Access contacts to share with friends" |
| **Calendar** | `NSCalendarsUsageDescription` | "Add events to your calendar" |
| **Reminders** | `NSRemindersUsageDescription` | "Create reminders for tasks" |
| **Photos** | `NSPhotoLibraryUsageDescription` | "Choose photos from library for profile" |
| **Photos (Write)** | `NSPhotoLibraryAddOnlyUsageDescription` | "Save edited photos to library" |
| **Health** | `NSHealthShareUsageDescription` | "Read health data for fitness tracking" |
| **Bluetooth** | `NSBluetoothPeripheralUsageDescription` | "Connect to fitness devices" |
| **Bluetooth (Admin)** | `NSBluetoothAlwaysUsageDescription` | "Background Bluetooth for wearables" |
| **Face ID** | `NSFaceIDUsageDescription` | "Authenticate with Face ID" |
| **Media Library** | `NSAppleMusicUsageDescription` | "Access your music library" |
| **Tracking** | `NSUserTrackingUsageDescription` | "Track activity for personalized ads" |
| **Siri** | `NSSiriUsageDescription` | "Use Siri for voice commands" |
| **Clipboard** | No key, but monitored | Accessing `UIPasteboard.general` is visible in privacy dashboard |

---

## Code Examples

**Example 1: Proper permission request with fallback**
```swift
import AVFoundation

func requestCameraPermission() {
    let status = AVCaptureDevice.authorizationStatus(for: .video)

    switch status {
    case .authorized:
        openCamera()
    case .notDetermined:
        AVCaptureDevice.requestAccess(for: .video) { granted in
            DispatchQueue.main.async {
                if granted {
                    self.openCamera()
                } else {
                    showPermissionDeniedAlert()
                }
            }
        }
    case .denied, .restricted:
        showSettingsPrompt()
    @unknown default:
        break
    }
}

func showSettingsPrompt() {
    let alert = UIAlertController(
        title: "Camera Required",
        message: "Open Settings to enable camera access",
        preferredStyle: .alert
    )
    alert.addAction(UIAlertAction(title: "Settings", style: .default) { _ in
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    })
    alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
}
```

**Example 2: Settings deep link (for permission prompts)**
```swift
// User can tap "Open Settings" in app to adjust permissions
func openAppSettings() {
    guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
    UIApplication.shared.open(url, options: [:])
}

// Deep link to Bluetooth settings (iOS 17+)
func openBluetoothSettings() {
    if let url = URL(string: "prefs:root=Bluetooth") {
        UIApplication.shared.open(url)
    }
}
```

**Example 3: In-app purchase validation**
```swift
import StoreKit

class IAP {
    func purchaseProduct(_ productID: String) async {
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let window = windowScene.windows.first else {
            return
        }

        do {
            if let result = try await Product.purchase(id: productID, options: [:]) {
                switch result {
                case .success(let verification):
                    let transaction = try verification.payloadValue
                    await transaction.finish() // Important: finish transaction
                    print("Purchase successful")

                case .userCancelled:
                    print("User cancelled")
                case .pending:
                    print("Transaction pending")
                @unknown default:
                    break
                }
            }
        } catch {
            print("Purchase failed: \(error)")
        }
    }
}
```

---

## Review Process Tips

**Before Submission:**
1. Test on real device (not just simulator)
2. Verify all links in app + metadata work
3. Check all Info.plist permissions are used
4. If using encryption, file ITSAppUsesNonExemptEncryption
5. Review privacy policy (must be accessible in app)
6. Age rating: answer all questions accurately
7. Screenshots match current app state
8. Description, keywords, support URL all present
9. No temporary test accounts/passwords

**After Rejection:**
1. Read rejection reason carefully (usually specific guideline)
2. Don't resubmit identical build (always increment build #)
3. Respond to reviewer comments in Resolution Notes
4. If policy question, link to specific docs
5. Test fix locally before resubmitting

---

## Common Gotchas

**Mistake 1: Requesting permission at launch without user interaction**
```swift
// ❌ WRONG — Request permission before user asks
func appDidLaunch() {
    AVCaptureDevice.requestAccess(for: .video) { _ in } // Rejected
}

// ✅ CORRECT — Request only when user needs feature
Button("Take Photo") {
    AVCaptureDevice.requestAccess(for: .video) { granted in
        if granted { openCamera() }
    }
}
```

**Mistake 2: Misleading age rating**
```swift
// ❌ WRONG — App has nude content but rated 4+
// Select Age Ratings: 4+
// Content includes: User-generated content (unchecked)

// ✅ CORRECT — Honest rating
// Select Age Ratings: 12+ or 17+
// Content includes: User-generated content (checked)
```

**Mistake 3: No privacy policy**
```swift
// ❌ WRONG — App collects data, no privacy policy
// App Store metadata: Privacy Policy URL (empty)

// ✅ CORRECT
// Create privacy policy (GDPR compliant)
// Link in App Store metadata
// Link in Settings/Help in-app
```

**Mistake 4: Incomplete in-app purchase flows**
```swift
// ❌ WRONG — Don't call finish() on transaction
let transaction = try verification.payloadValue
// App closes or crashes, transaction never marked finished
// Apple refunds user, app marked as buggy

// ✅ CORRECT
let transaction = try verification.payloadValue
await transaction.finish()
// Mark transaction complete, prevent refunds
```

**Mistake 5: Ignoring ATS exceptions without justification**
```swift
// ❌ WRONG — Allow HTTP without documented reason
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

// ✅ CORRECT
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>legacy-api.example.com</key>
        <dict>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSIncludesSubdomains</key>
            <true/>
        </dict>
    </dict>
</dict>
<!-- Document in notes: "Required for legacy payment gateway, HTTPS not supported" -->
```

**Mistake 6: Missing Swift 6 concurrency annotations**
```swift
// ❌ WRONG — ATT request off main thread, StoreKit without actor context
Task.detached {
    let status = await ATTrackingManager.requestTrackingAuthorization()
}

// ✅ CORRECT — Use @MainActor, mark Sendable types
@MainActor
func requestTracking() async {
    let status = await ATTrackingManager.requestTrackingAuthorization()
}

// For shared state, mark Sendable
@MainActor
final class AppState: Sendable {
    nonisolated var staticValue: String { "constant" }
}
```

---

## Common Mistakes

- ❌ Requesting all permissions at app launch — ask only when feature is needed
- ❌ Not checking permission denial with fallback — app becomes unusable
- ❌ Ignoring Info.plist privacy descriptions — app rejected without them
- ❌ Not finishing StoreKit 2 transactions — users get refunds, app marked unreliable
- ❌ Missing privacy policy or linking broken URL — auto-rejection
- ❌ Hardcoded test credentials in release build — rejectors find them
- ❌ Age rating mismatch (4+ app with user-generated content) — rejection
- ❌ Allowing HTTP without App Transport Security exception — requires justification

---

## Review Checklist

- [ ] All Info.plist `NS*UsageDescription` keys match features?
- [ ] No permissions requested without active user consent?
- [ ] Privacy policy accessible & linked in App Store?
- [ ] Age rating accurate to content?
- [ ] All metadata (description, keywords, screenshots) accurate?
- [ ] Support email/URL reachable?
- [ ] No hardcoded test accounts or credentials?
- [ ] App doesn't crash on launch (test on iOS 15+)?
- [ ] No external payment methods (use In-App Purchase)?
- [ ] Crypto disclosed if using encryption?
- [ ] Background modes declared match actual usage?
- [ ] No spam, fake reviews, or misleading claims?

---

_Source: Apple App Store Review Guidelines, Privacy Best Practices · Condensed for Ship Framework agent reference_

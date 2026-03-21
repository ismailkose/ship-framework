# Permission Management — iOS Reference

> **When to read:** Dev reads this when implementing centralized permission handling, graceful degradation when denied, or Info.plist setup.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Frameworks/Methods |
|---------|---------|------------------------|
| **AVFoundation** | Camera/microphone | `AVCaptureDevice.authorizationStatus(for:)`, `requestAccess()` |
| **CoreLocation** | GPS/location | `CLLocationManager`, `locationServicesEnabled()` |
| **Contacts** | Contact access | `CNContactStore.authorizationStatus()`, `requestAccess()` |
| **Photos** | Photo library | `PHPhotoLibrary.authorizationStatus()`, `requestAuthorization()` |
| **Reminders** | Calendar/reminders | `EKEventStore.authorizationStatus()`, `requestAccess()` |
| **EventKit** | Calendar events | `EKEventStore.authorizationStatus()` |
| **HealthKit** | Health data | `HKHealthStore.authorizationStatus()`, `requestAuthorization()` |
| **Bluetooth** | Wireless devices | `CBCentralManager`, iOS 13+ requires usage description |
| **Siri** | Voice commands | `INSiriKit`, no explicit request needed |
| **File Access** | Documents/downloads | `NSOpenPanel` (macOS), or user selection on iOS |
| **Tracking (IDFA)** | App Tracking Transparency | `ATTrackingManager.trackingAuthorizationStatus` |

---

## Code Examples

**Example 1: Centralized permission manager with fallback handling**
```swift
import AVFoundation
import CoreLocation
import Photos

class PermissionManager: NSObject, CLLocationManagerDelegate {
    static let shared = PermissionManager()

    private let locationManager = CLLocationManager()

    enum PermissionType {
        case camera
        case microphone
        case location
        case photoLibrary
        case contacts
    }

    enum PermissionStatus {
        case granted
        case denied
        case notDetermined
    }

    func requestPermission(_ type: PermissionType) async -> PermissionStatus {
        switch type {
        case .camera:
            return await requestCameraPermission()
        case .microphone:
            return await requestMicrophonePermission()
        case .location:
            return await requestLocationPermission()
        case .photoLibrary:
            return await requestPhotoLibraryPermission()
        case .contacts:
            return await requestContactsPermission()
        }
    }

    func checkPermission(_ type: PermissionType) -> PermissionStatus {
        switch type {
        case .camera:
            let status = AVCaptureDevice.authorizationStatus(for: .video)
            return mapStatus(status)
        case .microphone:
            let status = AVCaptureDevice.authorizationStatus(for: .audio)
            return mapStatus(status)
        case .location:
            let status = CLLocationManager.authorizationStatus()
            return mapLocationStatus(status)
        case .photoLibrary:
            let status = PHPhotoLibrary.authorizationStatus(for: .readWrite)
            return mapPhotoStatus(status)
        case .contacts:
            let status = CNContactStore.authorizationStatus(forEntityType: .contacts)
            return mapContactStatus(status)
        }
    }

    private func requestCameraPermission() async -> PermissionStatus {
        let status = AVCaptureDevice.authorizationStatus(for: .video)
        if status == .notDetermined {
            let granted = await AVCaptureDevice.requestAccess(for: .video)
            return granted ? .granted : .denied
        }
        return mapStatus(status)
    }

    private func requestMicrophonePermission() async -> PermissionStatus {
        let status = AVCaptureDevice.authorizationStatus(for: .audio)
        if status == .notDetermined {
            let granted = await AVCaptureDevice.requestAccess(for: .audio)
            return granted ? .granted : .denied
        }
        return mapStatus(status)
    }

    private func requestLocationPermission() async -> PermissionStatus {
        let status = CLLocationManager.authorizationStatus()
        if status == .notDetermined {
            locationManager.requestWhenInUseAuthorization()
            return .notDetermined // Will update via delegate
        }
        return mapLocationStatus(status)
    }

    private func requestPhotoLibraryPermission() async -> PermissionStatus {
        let status = PHPhotoLibrary.authorizationStatus(for: .readWrite)
        if status == .notDetermined {
            let granted = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
            return granted == .authorized ? .granted : .denied
        }
        return mapPhotoStatus(status)
    }

    private func requestContactsPermission() async -> PermissionStatus {
        let status = CNContactStore.authorizationStatus(forEntityType: .contacts)
        if status == .notDetermined {
            let store = CNContactStore()
            do {
                try await store.requestAccess(for: .contacts)
                return .granted
            } catch {
                return .denied
            }
        }
        return mapContactStatus(status)
    }

    // Mapping helpers
    private func mapStatus(_ status: AVAuthorizationStatus) -> PermissionStatus {
        switch status {
        case .authorized: return .granted
        case .denied, .restricted: return .denied
        case .notDetermined: return .notDetermined
        @unknown default: return .notDetermined
        }
    }

    private func mapLocationStatus(_ status: CLAuthorizationStatus) -> PermissionStatus {
        switch status {
        case .authorizedWhenInUse, .authorizedAlways: return .granted
        case .denied, .restricted: return .denied
        case .notDetermined: return .notDetermined
        @unknown default: return .notDetermined
        }
    }

    private func mapPhotoStatus(_ status: PHAuthorizationStatus) -> PermissionStatus {
        switch status {
        case .authorized, .limited: return .granted
        case .denied, .restricted: return .denied
        case .notDetermined: return .notDetermined
        @unknown default: return .notDetermined
        }
    }

    private func mapContactStatus(_ status: CNAuthorizationStatus) -> PermissionStatus {
        switch status {
        case .authorized: return .granted
        case .denied, .restricted: return .denied
        case .notDetermined: return .notDetermined
        @unknown default: return .notDetermined
        }
    }
}
```

**Example 2: Graceful degradation when permission denied**
```swift
func usePhotoLibrary() async {
    let status = await PermissionManager.shared.requestPermission(.photoLibrary)

    switch status {
    case .granted:
        // Open photo picker
        presentPhotoPicker()

    case .denied:
        // Show graceful fallback UI
        showPhotoDeniedAlert()

    case .notDetermined:
        // Should not happen, but retry if needed
        print("Permission status indeterminate")
    }
}

func showPhotoDeniedAlert() {
    let alert = UIAlertController(
        title: "Photos Not Available",
        message: "Open Settings to enable photo library access",
        preferredStyle: .alert
    )

    alert.addAction(UIAlertAction(title: "Settings", style: .default) { _ in
        openAppSettings()
    })

    alert.addAction(UIAlertAction(title: "Cancel", style: .cancel) { _ in
        // Continue without photos
        presentAlternativeUI()
    })

    present(alert, animated: true)
}

func openAppSettings() {
    guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
    UIApplication.shared.open(url)
}
```

**Example 3: Complete Info.plist configuration**
```swift
// Info.plist (XML format)
/*
<dict>
    <!-- Camera -->
    <key>NSCameraUsageDescription</key>
    <string>We need camera access to take photos for your profile</string>

    <!-- Microphone -->
    <key>NSMicrophoneUsageDescription</key>
    <string>Microphone access for voice calls</string>

    <!-- Location -->
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>We use your location to find nearby stores and events</string>

    <key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
    <string>Background location is used for delivery tracking</string>

    <!-- Contacts -->
    <key>NSContactsUsageDescription</key>
    <string>Access your contacts to share invitations with friends</string>

    <!-- Photos -->
    <key>NSPhotoLibraryUsageDescription</key>
    <string>Choose photos from your library for your profile</string>

    <key>NSPhotoLibraryAddOnlyUsageDescription</key>
    <string>Save edited photos to your photo library</string>

    <!-- Calendar -->
    <key>NSCalendarsUsageDescription</key>
    <string>Add events to your calendar</string>

    <!-- Reminders -->
    <key>NSRemindersUsageDescription</key>
    <string>Create reminders for your tasks</string>

    <!-- Health -->
    <key>NSHealthShareUsageDescription</key>
    <string>Read your health data for fitness tracking</string>

    <key>NSHealthUpdateUsageDescription</key>
    <string>Save health data from workouts</string>

    <!-- Bluetooth -->
    <key>NSBluetoothPeripheralUsageDescription</key>
    <string>Connect to fitness trackers and wearables</string>

    <key>NSBluetoothAlwaysUsageDescription</key>
    <string>Background Bluetooth for continuous wearable connection</string>

    <!-- Face ID -->
    <key>NSFaceIDUsageDescription</key>
    <string>Authenticate securely using Face ID</string>

    <!-- Siri -->
    <key>NSSiriUsageDescription</key>
    <string>Control the app using voice commands</string>

    <!-- Tracking (IDFA) -->
    <key>NSUserTrackingUsageDescription</key>
    <string>Track your activity to provide personalized ads</string>

    <!-- Background Modes -->
    <key>UIBackgroundModes</key>
    <array>
        <string>fetch</string>
        <string>processing</string>
        <string>remote-notification</string>
    </array>
</dict>
*/
```

---

## Common Mistakes

**Mistake 1: Requesting permission at app launch**
```swift
// ❌ WRONG — User gets permission dialog before understanding why
func applicationDidFinishLaunching(_ application: UIApplication) {
    PermissionManager.shared.requestPermission(.camera)
}

// ✅ CORRECT — Request when feature is needed
@IBAction func takePhotoButtonTapped() {
    Task {
        let status = await PermissionManager.shared.requestPermission(.camera)
        if status == .granted {
            presentPhotoPicker()
        }
    }
}
```

**Mistake 2: Not checking current permission before requesting**
```swift
// ❌ WRONG — Request even if already granted
_ = await AVCaptureDevice.requestAccess(for: .video) // Expensive

// ✅ CORRECT — Check first
let status = AVCaptureDevice.authorizationStatus(for: .video)
if status == .authorized {
    useCamera()
} else if status == .notDetermined {
    let granted = await AVCaptureDevice.requestAccess(for: .video)
    if granted { useCamera() }
}
```

**Mistake 3: Missing graceful fallback**
```swift
// ❌ WRONG — App crashes or blank screen when permission denied
@IBAction func selectPhotos() {
    let status = await PermissionManager.shared.requestPermission(.photoLibrary)
    presentPhotoPicker() // Crashes if denied
}

// ✅ CORRECT — Provide fallback
@IBAction func selectPhotos() {
    let status = await PermissionManager.shared.requestPermission(.photoLibrary)
    if status == .granted {
        presentPhotoPicker()
    } else {
        showAlternativePhotoSourceUI()
    }
}
```

**Mistake 4: Not updating Info.plist for all permissions**
```swift
// ❌ WRONG — Code requests camera, but no Info.plist entry
_ = await AVCaptureDevice.requestAccess(for: .video)
// App rejected: "Missing NSCameraUsageDescription"

// ✅ CORRECT
// Info.plist: NSCameraUsageDescription = "Take photos for profile"
```

**Mistake 5: Ignoring "Limited" photo library permission**
```swift
// ❌ WRONG — Treats .limited as .denied
let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
if status == .authorized {
    loadAllPhotos()
} else {
    showError() // .limited treated as denied
}

// ✅ CORRECT — Handle .limited
let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
if status == .authorized || status == .limited {
    loadAccessiblePhotos() // Works with limited selection
} else if status == .denied {
    showError()
}
```

---

## Review Checklist

- [ ] All Info.plist `NS*UsageDescription` entries present?
- [ ] Permissions only requested when feature is needed?
- [ ] Current permission status checked before requesting?
- [ ] Graceful fallback UI when permission denied?
- [ ] Settings deep link available for denied permissions?
- [ ] No location services without user explicit action?
- [ ] Bluetooth permission checked before connecting?
- [ ] Contact/calendar access minimal (only needed data)?
- [ ] Photo library handles both `.authorized` and `.limited`?
- [ ] Privacy policy explains why each permission is needed?
- [ ] Tested permission denial on real device?
- [ ] No permissions auto-requested on background update?

---

_Source: Apple Developer Documentation · AVFoundation, CoreLocation, Photos, Contacts, HealthKit · Condensed for Ship Framework agent reference_

# App Clips — iOS Reference

> **When to read:** Dev reads this when building an App Clip, configuring invocation URLs, handling location verification, or managing data migration to full app.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `NSUserActivity` | Encodes clip invocation; continues to full app |
| `userActivity.activityType` | Identifier for activity (com.company.app.clip, etc.) |
| `AppClips` | Configuration in App Store Connect; defines invocation rules |
| `CLLocationManager` | For location verification during clip invocation |
| `App Clip Card` | UI shown before launching clip (custom actions, metadata) |
| `AppKit.NSPasteboard` | Share data between clip and full app (if both installed) |

**Key Constants:**
- App Clip bundle max size: **15 MB** (compressed)
- Experience size limit: **10 MB**
- Invocation sources: universal link, App Clip code, NFC, QR code, location

---

## Code Examples

**Example 1: Setup App Clip with NSUserActivity**
```swift
import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        continue userActivity: NSUserActivity,
        restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void
    ) -> Bool {
        // App Clip launched via URL or code
        if userActivity.activityType == NSUserActivityTypeBrowsingWeb {
            guard let url = userActivity.webpageURL else { return false }

            print("Invocation URL: \(url)")

            // Parse parameters from URL
            if let components = URLComponents(url: url, resolvingAgainstBaseURL: true) {
                let params = components.queryItems?.reduce(into: [:]) { dict, item in
                    dict[item.name] = item.value
                } ?? [:]

                print("Parameters: \(params)")
                // Navigate to appropriate screen based on parameters
            }

            return true
        }

        return false
    }

    func application(
        _ application: UIApplication,
        configurationForConnecting connectingSceneSession: UISceneSession,
        options: UIScene.ConnectionOptions
    ) -> UISceneConfiguration {
        // For SwiftUI-based clip
        if let userActivity = options.userActivities.first {
            print("Scene launched with activity: \(userActivity.activityType)")
        }

        let configuration = UISceneConfiguration(
            name: "Default Configuration",
            sessionRole: connectingSceneSession.role
        )
        configuration.delegateClass = SceneDelegate.self
        return configuration
    }
}
```

**Example 2: SwiftUI App Clip with deep linking**
```swift
import SwiftUI

@main
struct AppClipApp: App {
    @Environment(\.scenePhase) var scenePhase
    @State var deepLink: String?

    var body: some Scene {
        WindowGroup {
            ContentView(deepLink: $deepLink)
                .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { userActivity in
                    // Handle web continuation
                    if let url = userActivity.webpageURL {
                        deepLink = url.absoluteString
                        parseAndNavigate(url: url)
                    }
                }
        }
    }

    func parseAndNavigate(url: URL) {
        if let components = URLComponents(url: url, resolvingAgainstBaseURL: true) {
            if let id = components.queryItems?.first(where: { $0.name == "id" })?.value {
                deepLink = id
                // Navigate to detail screen
            }
        }
    }
}

struct ContentView: View {
    @Binding var deepLink: String?

    var body: some View {
        VStack {
            if let link = deepLink {
                Text("Viewing: \(link)")
                Button("Get Full App") {
                    // Open full app
                    if let url = URL(string: "https://apps.apple.com/app/id123456789") {
                        UIApplication.shared.open(url)
                    }
                }
            } else {
                Text("App Clip")
                Button("Try Full Version") {
                    openFullApp()
                }
            }
        }
    }

    func openFullApp() {
        if let url = URL(string: "https://apps.apple.com/app/id123456789") {
            UIApplication.shared.open(url)
        }
    }
}
```

**Example 3: Location verification and data persistence**
```swift
import CoreLocation
import Foundation

class AppClipLocationHandler: NSObject, CLLocationManagerDelegate {
    let locationManager = CLLocationManager()
    var invokedAtLocation: CLLocationCoordinate2D?

    override init() {
        super.init()
        locationManager.delegate = self
    }

    func verifyInvocationLocation() {
        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
    }

    func locationManager(
        _ manager: CLLocationManager,
        didUpdateLocations locations: [CLLocation]
    ) {
        guard let location = locations.last else { return }
        invokedAtLocation = location.coordinate

        // Store in UserDefaults (shared with full app via App Groups)
        let defaults = UserDefaults(suiteName: "group.com.company.appClip")
        defaults?.set(location.latitude, forKey: "clipInvocationLat")
        defaults?.set(location.longitude, forKey: "clipInvocationLon")
        defaults?.set(Date().timeIntervalSince1970, forKey: "clipInvocationTime")

        locationManager.stopUpdatingLocation()
    }
}

// In full app, retrieve clip invocation data
func retrieveAppClipData() {
    let defaults = UserDefaults(suiteName: "group.com.company.appClip")

    if let latitude = defaults?.double(forKey: "clipInvocationLat"),
       let longitude = defaults?.double(forKey: "clipInvocationLon"),
       let timestamp = defaults?.double(forKey: "clipInvocationTime") {

        let location = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
        let invocationDate = Date(timeIntervalSince1970: timestamp)

        print("Clip invoked at: \(location) on \(invocationDate)")
        // Use this data to auto-navigate in full app
    }
}
```

---

## Common Mistakes

**Mistake 1: Exceeding 15 MB App Clip bundle size**
```swift
// ❌ WRONG: Including heavy assets in clip target
// Clip contains all frameworks, images, videos

// ✅ CORRECT: Use app thinning and link only to full app
// In Xcode: Clip target -> Build Phases -> Link Binary
// Only link necessary frameworks; remove unused code
// Use @IBDesignable sparingly (slow to render)
```

**Mistake 2: Not handling universal link invocation**
```swift
// ❌ WRONG: Only handles NSUserActivityTypeBrowsingWeb
func application(_ app: UIApplication, open url: URL) -> Bool {
    // This won't be called for universal links in clip
    return true
}

// ✅ CORRECT: Use scene(_ scene:continue:) instead
func scene(
    _ scene: UIScene,
    continue userActivity: NSUserActivity
) {
    if userActivity.activityType == NSUserActivityTypeBrowsingWeb {
        // Handle universal link
    }
}
```

**Mistake 3: Storing large data without App Groups**
```swift
// ❌ WRONG: App Clip stores data; full app can't access it
UserDefaults.standard.set(largeData, forKey: "myKey")

// ✅ CORRECT: Use shared App Groups container
let defaults = UserDefaults(suiteName: "group.com.company.clip")
defaults?.set(largeData, forKey: "myKey")

// Full app reads from same location
let fullAppDefaults = UserDefaults(suiteName: "group.com.company.clip")
let data = fullAppDefaults?.object(forKey: "myKey")
```

**Mistake 4: Not requesting location permission for invocation context**
```swift
// ❌ WRONG: No location context passed to full app
// Clip invoked at store, but full app doesn't know where

// ✅ CORRECT: Capture and persist location
let locationManager = CLLocationManager()
locationManager.requestWhenInUseAuthorization()
// Store location in App Groups for full app
```

**Mistake 5: Including full app features in clip**
```swift
// ❌ WRONG: App Clip duplicates all code, exceeds 15 MB limit
// Clip target includes account login, settings, full catalog

// ✅ CORRECT: Clip is minimal; features behind "Get Full App" button
struct ContentView: View {
    var body: some View {
        Button("Experience Full App") {
            if let url = URL(string: "itms-apps://apps.apple.com/app/id123456789") {
                UIApplication.shared.open(url)
            }
        }
    }
}
```

---

## Review Checklist

- [ ] App Clip target created in Xcode (separate target)
- [ ] App Clip bundle size checked: < 15 MB
- [ ] Invocation URL configured in App Store Connect (universal link or App Clip code)
- [ ] `NSUserActivity` handled in `scene(_:continue:)` or `application(_:continue:restorationHandler:)`
- [ ] Deep linking parameters parsed from `userActivity.webpageURL`
- [ ] App Groups entitlement enabled (both clip and full app targets)
- [ ] `UserDefaults(suiteName: "group.xxx")` used for data sharing
- [ ] Unnecessary frameworks/assets removed from clip target
- [ ] Location permission requested if clip invoked from location
- [ ] "Get Full App" call-to-action prominently displayed
- [ ] Full app handles clip invocation data on first launch
- [ ] No persistent authentication required in clip (encourage full app)
- [ ] Clip tested on device (simulator limited for App Clip codes)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

<!-- ship-reference
id: ios-frameworks
kind: platform
sources: https://developer.apple.com/documentation (2026-09-23, every row's page checked); iPhoneOS27.0.sdk (Xcode 27.0 27A266a); xcode-bundled-skills@27A266a (IDEIntelligenceChat Resources, pointed to, never copied); swift-ios-skills@8d90fd1 (reviewed 2026-09-28, not suggested, no text); https://developer.apple.com/app-store/review/guidelines/ (Last Updated June 8, 2026; checked 2026-09-23); https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api (reason codes; 2026-09-29); https://developer.apple.com/news/upcoming-requirements/ (upload SDK and minimum target; 2026-09-29); https://developer.apple.com/app-store/subscriptions/ (policy links; 2026-09-29)
reviewed: 2026-09-24
-->
# iOS frameworks — index and signs

The index of Apple frameworks: what each is for, its first iOS, Apple's page, a one-line Ship sign,
and where the depth lives. **Ship's own guides come first** — they're bundled and need no
install; Xcode 27's bundled guides are Apple's own extra depth. **Before building with a
framework:** read the Ship guide below (or the row's Apple page when there's none), apply the sign,
and gate anything newer than the deployment target with `if #available`.

**Ship guides (bundled, loaded on demand — `.claude/skills/ship/ios/references/`)**

| Guide | Frameworks and tasks |
|---|---|
| `data-sync.md` | SwiftData, Core Data, CloudKit, CKSyncEngine, key-value sync, files, App Groups |
| `commerce-identity.md` | StoreKit, PassKit / Apple Pay / Wallet, Authentication Services, Local Authentication, Keychain (Security), CryptoKit, DeviceCheck / App Attest |
| `notifications-background.md` | User Notifications, APNs, Background Tasks, background URLSession, ActivityKit, AlarmKit, PushKit + CallKit |
| `media.md` | PhotosUI, PhotoKit, AVFoundation capture, AVFAudio, AVKit, MediaPlayer Now Playing, Speech, PDFKit, PencilKit, PaperKit, SpriteKit / RealityKit / SceneKit, GameKit |
| `system-integration.md` | App Intents, App Shortcuts, Core Spotlight, WidgetKit + controls, universal links, TipKit, App Clips, Group Activities, share extensions |
| `device-data.md` | Core Location, MapKit, HealthKit (incl. workouts), EventKit, Contacts, Core Motion, WeatherKit, MusicKit, FinanceKit, SensorKit, EnergyKit, PermissionKit, Declared Age Range |
| `accessories.md` | Core Bluetooth, AccessorySetupKit, Core NFC, HomeKit / Matter, DockKit, Wi-Fi Aware |
| `accessibility-ios.md` | Accessibility (VoiceOver, Voice Control, Switch Control, Full Keyboard Access), XCTest accessibility audits |
| `intelligence.md` | Foundation Models, Core ML, Vision, Natural Language, Translation, Image Playground, Visual Intelligence |
| `swiftui-building.md` · `swift-practice.md` | SwiftUI screens, Swift Charts, accessibility, localization, previews · concurrency, URLSession / Network, Codable, Swift Testing |
| `swiftui-performance.md` | Instruments, MetricKit, logging, signposts, sanitizers |

**Legend**
- **iOS** — first iOS version with the framework (Apple's docs page). Individual APIs can be newer:
  check the symbol's `@available` in the SDK before using it (`ios-27.md` has the one-liner).
- **X:** `name` → Xcode 27's bundled Apple skill at
  `$(xcode-select -p)/../PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/name.idechatprompttemplate`
  (its `name-ref-*.md.packaged` files are the details). **XD:** `Name` → `…/Resources/AdditionalDocumentation/Name.md`.
  Apple's text — read it, never copy it. Missing (older Xcode)? Use the Apple docs link.
- SwiftUI and Swift: `swiftui-building.md`, `swift-practice.md`, `swiftui-ship.md` (bundled); Xcode 27's own SwiftUI guides add depth (`ios-27.md` §1).

## App experience

| Framework | Use it for | iOS | Deeper | Ship sign |
|---|---|---|---|---|
| [SwiftUI](https://developer.apple.com/documentation/swiftui) | All new UI | 13 | X: `swiftui-whats-new-27`, `swiftui-specialist` | `swiftui-ship.md` first (registry, API-first) |
| [UIKit](https://developer.apple.com/documentation/uikit) | Bridging, legacy screens | 2 | X: `uikit-app-modernization` · XD: `UIKit-Implementing-Liquid-Glass-Design` | Bridge only what SwiftUI lacks |
| [App Intents](https://developer.apple.com/documentation/appintents) | Siri, Shortcuts, Spotlight, controls, Apple Intelligence actions | 16 | X: `app-intents-specialist`, `app-intents-whats-new-27` · XD: `AppIntents-Updates` | Expose the app's core verbs + entities, not every screen |
| [WidgetKit](https://developer.apple.com/documentation/widgetkit) | Widgets, controls, Smart Stack | 14 | XD: `WidgetKit-Implementing-Liquid-Glass-Design` | Glanceable; a tap deep-links to the exact screen |
| [ActivityKit](https://developer.apple.com/documentation/activitykit) | Live Activities, Dynamic Island | 16.1 | | Only for a live, time-bound task the user started |
| [AlarmKit](https://developer.apple.com/documentation/alarmkit) | Alarms and countdowns that break through | 26 | XD: `SwiftUI-AlarmKit-Integration` | |
| [TipKit](https://developer.apple.com/documentation/tipkit) | Contextual feature tips | 17 | | Use instead of hand-made coach marks |
| [StoreKit](https://developer.apple.com/documentation/storekit) | In-app purchase, subscriptions | 3 | XD: `StoreKit-Updates` | `SubscriptionStoreView`/`ProductView` (17+) before a custom paywall; offer Restore (App Review 3.1.1) |
| [App Clips](https://developer.apple.com/documentation/appclip) | Instant, lightweight entry point | 14 | | |
| [MapKit](https://developer.apple.com/documentation/mapkit) | Maps, search, directions | 3 | XD: `MapKit-GeoToolbox-PlaceDescriptors` | SwiftUI `Map` before `MKMapView` |
| [GeoToolbox](https://developer.apple.com/documentation/geotoolbox) | Place descriptors for coordinates | 26 | XD: `MapKit-GeoToolbox-PlaceDescriptors` | |
| [Core Location](https://developer.apple.com/documentation/corelocation) | Location, region monitoring | 2 | — | Ask for when-in-use, in context |
| [PhotosUI](https://developer.apple.com/documentation/photosui) | Photo picking | 8 | | `PhotosPicker` runs out of process — no library permission needed |
| [PhotoKit](https://developer.apple.com/documentation/photokit) | Reading/writing the library | 8 | | Only when you manage the library, not to pick |
| [AVFoundation](https://developer.apple.com/documentation/avfoundation) | Camera capture, audio session, media | 2.2 | — | |
| [AVKit](https://developer.apple.com/documentation/avkit) | System video player, PiP | 8 | | `VideoPlayer` before a custom player |
| [PDFKit](https://developer.apple.com/documentation/pdfkit) | Show/annotate PDFs | 11 | | |
| [PaperKit](https://developer.apple.com/documentation/paperkit) | System markup canvas | 26 | | |
| [PencilKit](https://developer.apple.com/documentation/pencilkit) | Drawing, Apple Pencil input | 13 | | |
| [WebKit](https://developer.apple.com/documentation/webkit) | SwiftUI `WebView`, web content | 16 (SwiftUI `WebView` 26) | XD: `SwiftUI-WebKit-Integration` | Native `WebView` (26+) before a `WKWebView` wrapper |
| [Swift Charts](https://developer.apple.com/documentation/charts) | Charts | 16 | XD: `Swift-Charts-3D-Visualization` | One insight per chart; label marks for VoiceOver |
| [User Notifications](https://developer.apple.com/documentation/usernotifications) | Local + push notifications | 10 | | Ask after the user sees value; pick the interruption level honestly (`hig-ios.md`) |
| [Group Activities](https://developer.apple.com/documentation/groupactivities) | SharePlay | 15 | | |
| [CarPlay](https://developer.apple.com/documentation/carplay) | CarPlay templates | 12 | | Needs a CarPlay entitlement ([request](https://developer.apple.com/documentation/carplay/requesting-carplay-entitlements)) |
| [Core Spotlight](https://developer.apple.com/documentation/corespotlight) | Index content for search | 9 | X: `app-intents-whats-new-27` (Spotlight indexing ref) | App Intents entities can join the index (`IndexedEntity`, 18+) |
| [RelevanceKit](https://developer.apple.com/documentation/relevancekit) | Widget relevance on Apple Watch | 26 | | |
| [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence) | Appear in visual search results | 26 | XD: `Implementing-Visual-Intelligence-in-iOS` · X: `app-intents-whats-new-27` | |
| [SwiftUI Document](https://developer.apple.com/documentation/swiftui/document) | Document-based apps | 27 | X: `building-document-based-swiftui-applications` | New API on 27; `FileDocument` below 27 |
| [Accessibility](https://developer.apple.com/documentation/accessibility) | VoiceOver, Assistive Access, audits | 14 | XD: `Implementing-Assistive-Access-in-iOS` | Checklist in `hig-ios.md` |
| [Localization](https://developer.apple.com/documentation/xcode/localization) | String Catalogs, formats | — | X: `swiftui-specialist` (localization ref) | String Catalogs; format with `FormatStyle` |

## Data, accounts, services

| Framework | Use it for | iOS | Deeper | Ship sign |
|---|---|---|---|---|
| [SwiftData](https://developer.apple.com/documentation/swiftdata) | Local persistence | 17 | XD: `SwiftData-Class-Inheritance` | Default store for new apps; keep `@Model` types out of views' business logic |
| [Core Data](https://developer.apple.com/documentation/coredata) | Existing stores, advanced persistence | 3 | `data-sync.md` | Keep what the app already uses |
| [CloudKit](https://developer.apple.com/documentation/cloudkit) | iCloud sync and sharing | 8 | | Design for eventual consistency and signed-out users |
| [HealthKit](https://developer.apple.com/documentation/healthkit) | Health data | 8 | | Request only types you use; read denial looks like "no data" — never infer consent |
| [EventKit](https://developer.apple.com/documentation/eventkit) | Calendar, reminders | 4 | | Write-only access when you only add events |
| [Contacts](https://developer.apple.com/documentation/contacts) | Address book | 9 | | Prefer the system picker (`ContactsUI`) when you need one contact |
| [WeatherKit](https://developer.apple.com/documentation/weatherkit) | Weather data | 16 | | Attribution is required — show it |
| [MusicKit](https://developer.apple.com/documentation/musickit) | Apple Music | 15 | | |
| [FinanceKit](https://developer.apple.com/documentation/financekit) | Apple Card/Cash data, Wallet orders | 17 | | Requires an Apple-granted entitlement |
| [PassKit](https://developer.apple.com/documentation/passkit) | Apple Pay, Wallet passes | 6 | | Physical goods/services only — digital unlocks use IAP (3.1.1) |
| [EnergyKit](https://developer.apple.com/documentation/energykit) | Grid forecasts, energy insights | 26 | | |
| [HomeKit](https://developer.apple.com/documentation/homekit) · [Matter](https://developer.apple.com/documentation/matter) | Home accessories | 8 · 16 | | |
| [SensorKit](https://developer.apple.com/documentation/sensorkit) | Research-study sensor data | 14 | | Approved research only |
| [URLSession](https://developer.apple.com/documentation/foundation/urlsession) · [Network](https://developer.apple.com/documentation/network) | HTTP · sockets | 7 · 12 | | `async` URLSession APIs; cancel with the view's `.task` |
| [Background Tasks](https://developer.apple.com/documentation/backgroundtasks) | Deferred background work | 13 | | The system decides when — never promise timing in UI |
| [Declared Age Range](https://developer.apple.com/documentation/declaredagerange) | Age-appropriate experiences | 26 | — | |
| [PermissionKit](https://developer.apple.com/documentation/permissionkit) | Child ↔ parent permission requests | 26 | | |
| [AdAttributionKit](https://developer.apple.com/documentation/adattributionkit) | Privacy-preserving ad attribution | 17.4 | | |

## Intelligence and media

| Framework | Use it for | iOS | Deeper | Ship sign |
|---|---|---|---|---|
| [Foundation Models](https://developer.apple.com/documentation/foundationmodels) | On-device LLM, guided generation, tools | 26 | XD: `FoundationModels-Using-on-device-LLM-in-your-app` | Check `SystemLanguageModel.default.availability` and design the unavailable state |
| [Core ML](https://developer.apple.com/documentation/coreml) | Custom models | 11 | | |
| [Vision](https://developer.apple.com/documentation/vision) | Text, faces, barcodes, image analysis | 11 | | |
| [Natural Language](https://developer.apple.com/documentation/naturallanguage) · [Translation](https://developer.apple.com/documentation/translation) | Language ID, tagging · translation | 12 · 17.4 | | System translation sheet before a custom one |
| [Speech](https://developer.apple.com/documentation/speech) | Transcription | 10 | | |
| [Image Playground](https://developer.apple.com/documentation/imageplayground) | System image generation UI | 18.1 | — | |
| [Media Intelligence](https://developer.apple.com/documentation/mediaintelligence) | Video highlights, face groups | 27 | — | New in 27: gate it |
| [Music Understanding](https://developer.apple.com/documentation/musicunderstanding) | Tempo, structure, loudness | 27 | — | New in 27: gate it |
| [Media Intents](https://developer.apple.com/documentation/mediaintents) | Siri media search/playback | 27 | — | New in 27 |
| [Suggested Actions](https://developer.apple.com/documentation/suggestedactions) | Quick actions next to messages | 27 | — | New in 27 |

## Security and identity

| Framework | Use it for | iOS | Deeper | Ship sign |
|---|---|---|---|---|
| [Authentication Services](https://developer.apple.com/documentation/authenticationservices) | Sign in with Apple, passkeys | 12 | | Third-party login ⇒ offer an equivalent private option (App Review 4.8) |
| [Local Authentication](https://developer.apple.com/documentation/localauthentication) | Face ID / Touch ID | 8 | | Needs `NSFaceIDUsageDescription` |
| [CryptoKit](https://developer.apple.com/documentation/cryptokit) | Hashing, signing, encryption | 13 | | SHA-3 (`SHA3_256/384/512`) is iOS 26+ |
| [Security](https://developer.apple.com/documentation/security) | Keychain, certificates | 2 | X: `audit-xcode-security-settings` | Secrets in Keychain, never `UserDefaults` |
| [CryptoTokenKit](https://developer.apple.com/documentation/cryptotokenkit) | Smart cards, tokens | 13 | | |
| [DeviceCheck](https://developer.apple.com/documentation/devicecheck) | App Attest, fraud signals | 11 | | |
| [Trust Insights](https://developer.apple.com/documentation/trustinsights) | Coercion signals for transactions | 27 | — | New in 27 |
| [BrowserEngineKit](https://developer.apple.com/documentation/browserenginekit) | Alternative browser engines | 17.4 | | Entitlement + region rules |

## Hardware and system

| Framework | Use it for | iOS | Deeper | Ship sign |
|---|---|---|---|---|
| [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth) | BLE devices | 5 | | |
| [AccessorySetupKit](https://developer.apple.com/documentation/accessorysetupkit) | Pairing your accessory | 18 | | Prefer it to raw Bluetooth/Wi-Fi permission prompts |
| [Core NFC](https://developer.apple.com/documentation/corenfc) | NFC tags | 11 | | |
| [Core Motion](https://developer.apple.com/documentation/coremotion) | Motion sensors, pedometer | 4 | | |
| [Core Haptics](https://developer.apple.com/documentation/corehaptics) | Custom haptic patterns | 13 | — | `sensoryFeedback` first (`swiftui-ship.md`) |
| [DockKit](https://developer.apple.com/documentation/dockkit) | Subject-tracking stands | 17 | | |
| [Wi-Fi Aware](https://developer.apple.com/documentation/wifiaware) | Peer-to-peer Wi-Fi | 26 | — | |
| [AudioAccessoryKit](https://developer.apple.com/documentation/audioaccessorykit) | Audio accessory features | 26.4 | | |
| [CallKit](https://developer.apple.com/documentation/callkit) | VoIP calling UI | 10 | | |
| [AppMigrationKit](https://developer.apple.com/documentation/appmigrationkit) | Cross-platform data transfer | 26.1 | | |
| [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit) | Screen capture on iOS | 27 | — | New on iOS in 27 |
| [MetricKit](https://developer.apple.com/documentation/metrickit) | Field performance + diagnostics | 13 | | iOS 27+: `MetricManager` (async reports); `MXMetricManager` is marked to-be-deprecated |
| [StateReporting](https://developer.apple.com/documentation/statereporting) | App state for diagnostics | 27 | — | Pairs with `MetricManager` |

## Games and 3D

| Framework | Use it for | iOS | Deeper | Ship sign |
|---|---|---|---|---|
| [GameKit](https://developer.apple.com/documentation/gamekit) | Game Center | 3 | | |
| [SpriteKit](https://developer.apple.com/documentation/spritekit) | 2D games | 7 | | |
| [RealityKit](https://developer.apple.com/documentation/realitykit) | 3D, AR | 13 | | |
| [SceneKit](https://developer.apple.com/documentation/scenekit) | Existing 3D scenes | 8 | | Keep existing scenes; new 3D → RealityKit (Ship default) |
| [GameSave](https://developer.apple.com/documentation/gamesave) | iCloud save files | 26 | — | |
| [USDKit](https://developer.apple.com/documentation/usdkit) · [Compute Graph](https://developer.apple.com/documentation/computegraph) | USD authoring · RealityKit compute | 27 | — | New in 27 |

TabletopKit is visionOS-only (not in the iPhoneOS SDK). Also new in the iOS 27 SDK and out of
Ship's usual scope: AVSystemRouting, Media Device (media hardware vendors), CrashReportExtension,
AppManagedFeatures (device management; no docs page yet).

## Tooling and App Store

| Need | Go to |
|---|---|
| Profiling, hangs, hitches | `.claude/skills/ship/ios/references/swiftui-performance.md` |
| Build-setting hardening | X: `audit-xcode-security-settings` |
| Simulator automation | `xcrun simctl help` (Apple's simulator tool) |
| Privacy manifest | [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files) — required-reason APIs + collected data |
| Review readiness | [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) |

**App Review checks Ship applies at launch** (guideline numbers as of the June 8, 2026 revision):
2.1 no placeholder content, demo account or demo mode for login · 2.5.1 public APIs only ·
3.1.1 digital unlocks use IAP, restore for restorable purchases · 4.2 more than a wrapped website ·
4.8 equivalent private login when third-party login is primary · 5.1.1 privacy policy link,
purpose strings that say what and why, in-app account deletion when sign-up exists · 5.1.2(i)
tracking (sharing data or a device identifier with ad networks or data brokers) only after the
App Tracking Transparency prompt (`NSUserTrackingUsageDescription`, asked while the app is active).

**Before upload:** a `PrivacyInfo.xcprivacy` that declares every required-reason API the app and its
SDKs use, e.g. `CA92.1` for the app's own UserDefaults and `C617.1` for file dates in its container
(App Store Connect rejects an upload without them), plus tracking domains if it tracks ·
subscription screens link Terms of Use and the privacy policy · built with Xcode 26 and the iOS 26
SDK or later (since April 28, 2026), targeting iOS 13 or later (since September 9, 2026).

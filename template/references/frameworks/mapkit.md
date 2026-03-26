# MapKit — iOS Reference

> **When to read:** Dev reads this when displaying maps, adding markers, or implementing location-aware features.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `Map { }` | SwiftUI view for map display | Replaces MKMapView; declarative |
| `@State var position` | Camera position (center, zoom) | Updated via gesture or programmatically |
| `Marker { }` | Pin/annotation view | Includes label, tappable, custom image |
| `MapCircle`, `MapPolygon` | Overlay shapes | Define regions visually |
| `MKLocalSearch` | Find places & addresses | Query by text or coordinates |
| `CLLocationManager` | Location access & updates | Requests permission, provides coordinates |
| `CLAuthorizationStatus` | Permission state | `.notDetermined`, `.denied`, `.authorizedWhenInUse`, `.authorizedAlways` |
| `CLGeocoder` | Reverse geocoding | Coordinates → address; address → coordinates |
| `CLLocationUpdate.liveUpdates()` | Streaming location updates | Modern async/await replacement for delegates |
| `CLServiceSession` (iOS 18+) | Manages authorization lifetime | Declare scope for location services |
| `MKGeocodingRequest` / `MKReverseGeocodingRequest` (iOS 26+) | MapKit-native geocoding | Returns `MKMapItem` with richer data |
| `PlaceDescriptor` (iOS 26+) | Create place references | From coordinates or addresses |
| `MapCameraPosition` variants | Camera control | `.automatic`, `.region`, `.camera`, `.item`, `.userLocation`, `.rect` |
| `.mapInteractionModes()` | Control map gestures | Pan, zoom, rotate, pitch |

## Code Examples

### CLLocationUpdate.liveUpdates() (iOS 17+)

```swift
// Modern streaming location with async/await
@Observable
final class LocationTracker {
    var currentLocation: CLLocation?

    func startTracking() {
        Task {
            for try await update in CLLocationUpdate.liveUpdates() {
                guard let location = update.location,
                      location.horizontalAccuracy < 50 else { continue }
                self.currentLocation = location
            }
        }
    }
}
```

### CLServiceSession (iOS 18+)

```swift
// Declare authorization scope for the activity lifetime
let session = CLServiceSession(
    authorization: .whenInUse,
    fullAccuracyPurposeKey: "NearbySearchPurpose"
)
// Hold session; release when done
```

### MapCameraPosition Variants

```swift
// Center on region
@State private var position: MapCameraPosition = .region(
    MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 37.334, longitude: -122.009),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )
)

// Follow user location
@State private var position: MapCameraPosition = .userLocation(fallback: .automatic)

// 3D camera angle
@State private var position: MapCameraPosition = .camera(
    MapCamera(centerCoordinate: applePark, distance: 1000, heading: 90, pitch: 60)
)

// Frame specific items
position = .item(MKMapItem.forCurrentLocation())
position = .rect(MKMapRect(...))
```

### Map Interaction Modes

```swift
.mapInteractionModes(.all)           // Default: pan, zoom, rotate, pitch
.mapInteractionModes(.pan)           // Pan only
.mapInteractionModes([.pan, .zoom])  // Pan and zoom
.mapInteractionModes([])             // Static map (no interaction)
```

### Search Debouncing with `.task(id:)`

```swift
@State private var searchText = ""
@State private var results: [MKMapItem] = []

var body: some View {
    TextField("Search", text: $searchText)
        .task(id: searchText) {
            guard !searchText.isEmpty else { results = []; return }
            try? await Task.sleep(for: .milliseconds(300))  // Debounce 300ms
            results = try? await performSearch(searchText)
        }
}
```

### MKGeocodingRequest / MKReverseGeocodingRequest (iOS 26+)

```swift
@available(iOS 26, *)
func reverseGeocode(location: CLLocation) async throws -> MKMapItem? {
    guard let request = MKReverseGeocodingRequest(location: location) else { return nil }
    return try await request.mapItems.first
}

@available(iOS 26, *)
func forwardGeocode(address: String) async throws -> [MKMapItem] {
    guard let request = MKGeocodingRequest(addressString: address) else { return [] }
    return try await request.mapItems
}
```

### PlaceDescriptor (iOS 26+)

```swift
@available(iOS 26, *)
func lookupPlace(name: String, coordinate: CLLocationCoordinate2D) async throws -> MKMapItem {
    let descriptor = PlaceDescriptor(
        representations: [.coordinate(coordinate)],
        commonName: name
    )
    let request = MKMapItemRequest(placeDescriptor: descriptor)
    return try await request.mapItem
}
```

### Cycling Directions (iOS 26+)

```swift
@available(iOS 26, *)
func getCyclingDirections(to destination: MKMapItem) async throws -> MKRoute? {
    let request = MKDirections.Request()
    request.source = MKMapItem.forCurrentLocation()
    request.destination = destination
    request.transportType = .cycling
    return try await MKDirections(request: request).calculate().routes.first
}
```

## Code Examples (Legacy)

```swift
// 1. Basic map with marker and gesture response
import SwiftUI
import MapKit

struct MapView: View {
    @State private var position: MapCameraPosition = .region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194),
            span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
        )
    )

    var body: some View {
        Map(position: $position) {
            Marker("San Francisco", coordinate: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194))
                .tint(.red)
        }
        .mapStyle(.standard)
        .onMapCameraChange { context in
            print("User moved map to: \(context.region.center)")
        }
    }
}

// 2. Multiple markers with custom shapes
struct MultiMarkerView: View {
    let locations = [
        ("Coffee Shop", CLLocationCoordinate2D(latitude: 37.77, longitude: -122.42)),
        ("Park", CLLocationCoordinate2D(latitude: 37.76, longitude: -122.43))
    ]

    var body: some View {
        Map {
            ForEach(locations, id: \.0) { name, coord in
                Marker(name, coordinate: coord)
            }
            MapCircle(center: CLLocationCoordinate2D(latitude: 37.77, longitude: -122.42), radius: 500)
                .foregroundStyle(.blue.opacity(0.2))
        }
    }
}

// 3. Request location permission and get current location
import CoreLocation

@Observable
class LocationManager: NSObject, CLLocationManagerDelegate {
    let manager = CLLocationManager()
    @ObservationIgnored var authorizationStatus: CLAuthorizationStatus = .notDetermined

    override init() {
        super.init()
        manager.delegate = self
    }

    func requestLocationPermission() {
        manager.requestWhenInUseAuthorization()
    }

    func startUpdatingLocation() {
        manager.startUpdatingLocation()
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorizationStatus = manager.authorizationStatus
        if authorizationStatus == .authorizedWhenInUse {
            manager.startUpdatingLocation()
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        print("Current location: \(location.coordinate)")
    }
}

// 4. Local search for nearby places
func searchForRestaurants(near coordinate: CLLocationCoordinate2D) async {
    let request = MKLocalSearch.Request()
    request.naturalLanguageQuery = "restaurants"
    request.region = MKCoordinateRegion(
        center: coordinate,
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )

    let search = MKLocalSearch(request: request)
    do {
        let response = try await search.start()
        for mapItem in response.mapItems {
            print("Found: \(mapItem.name ?? "Unknown")")
            print("Coordinate: \(mapItem.placemark.coordinate)")
        }
    } catch {
        print("Search failed: \(error.localizedDescription)")
    }
}

// 5. Reverse geocoding (coordinates to address)
func reverseGeocode(coordinate: CLLocationCoordinate2D) async {
    let geocoder = CLGeocoder()
    let location = CLLocation(latitude: coordinate.latitude, longitude: coordinate.longitude)

    do {
        let placemarks = try await geocoder.reverseGeocodeLocation(location)
        if let placemark = placemarks.first {
            print("Address: \(placemark.thoroughfare ?? ""), \(placemark.locality ?? "")")
        }
    } catch {
        print("Geocoding failed: \(error.localizedDescription)")
    }
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Not adding location privacy strings in Info.plist | Add `NSLocationWhenInUseUsageDescription` & `NSLocationAlwaysAndWhenInUseUsageDescription` |
| Requesting `.authorizedAlways` without justification | Use `.authorizedWhenInUse` by default; only request always when necessary |
| Not checking authorization status before using location | Check `CLLocationManager.authorizationStatus` first; handle denied state |
| Forgetting `@State` for map position; not binding correctly | Always use `@State private var position` and bind with `$position` |
| Blocking UI thread with synchronous `CLGeocoder` | Use async/await; never block main thread on location/geocoding tasks |

## Review Checklist

- [ ] Privacy strings (NSLocationWhenInUseUsageDescription, etc.) in Info.plist
- [ ] Location permission checked before accessing location data
- [ ] `CLLocationManager` delegate methods implemented
- [ ] Map position bound with `$position` for reactivity
- [ ] Markers/overlays iterate safely (no infinite loops)
- [ ] MKLocalSearch queries include region to limit results
- [ ] Geocoding/reverse geocoding use async/await
- [ ] Location updates stopped when no longer needed (`stopUpdatingLocation()`)
- [ ] Error handling for denied permissions and network failures
- [ ] Map zoom levels reasonable for use case (not too zoomed/out)
- [ ] User notified if location permission denied
- [ ] Sensitive location data not logged or stored insecurely
- [ ] `CLLocationUpdate.liveUpdates()` used instead of CLLocationManagerDelegate (iOS 17+)
- [ ] `CLServiceSession` declared explicitly for authorization scope (iOS 18+)
- [ ] Search queries debounced with `.task(id:)` (at least 300ms)
- [ ] `MKGeocodingRequest` / `MKReverseGeocodingRequest` used for MapKit-native geocoding (iOS 26+)
- [ ] `PlaceDescriptor` used for place references (iOS 26+)
- [ ] `.mapInteractionModes()` restricts gestures appropriately
- [ ] Cycling directions support (iOS 26+) when applicable

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

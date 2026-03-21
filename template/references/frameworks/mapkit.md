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

## Code Examples

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

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

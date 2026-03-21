# WeatherKit — iOS Reference

> **When to read:** Dev reads this when building features with current weather, forecasts, or weather attribution.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `WeatherService` | Main API; fetch weather by location (CLLocationCoordinate2D) |
| `Weather` | Container for current conditions, forecasts, alerts |
| `CurrentWeather` | Current conditions: temperature, humidity, wind, pressure |
| `Forecast` | Daily/hourly/minute forecast; `DayWeather`, `HourWeather`, `MinuteWeather` |
| `WeatherAttribute` | Attribution text and URL; **must be displayed** per terms |
| `Wind` | Direction, speed; `CLLocationDirection`, `Measurement<UnitSpeed>` |
| `Precipitation` | Type, amount, probability |
| `Condition` | Weather state: `.clear`, `.cloudy`, `.rainy`, `.snowy`, etc. |
| `Location` | Latitude, longitude |

---

## Code Examples

### Example 1: Fetch current weather
```swift
import WeatherKit
import CoreLocation

func getCurrentWeather(latitude: Double, longitude: Double) async throws -> CurrentWeather {
    let location = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)

    let weather = try await WeatherService.shared.weather(for: location)
    let current = weather.currentWeather

    print("Temperature: \(current.temperature)")
    print("Condition: \(current.condition)")
    print("Humidity: \(current.humidity)")
    print("Wind: \(current.wind.speed.value) \(current.wind.speed.unit)")

    return current
}

// Usage
Task {
    do {
        let current = try await getCurrentWeather(latitude: 37.7749, longitude: -122.4194)
    } catch {
        print("Weather fetch error: \(error)")
    }
}
```

### Example 2: Fetch daily forecast
```swift
import WeatherKit
import CoreLocation

func getDailyForecast(latitude: Double, longitude: Double) async throws -> [DayWeather] {
    let location = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    let weather = try await WeatherService.shared.weather(for: location)

    let forecast = weather.dailyForecast
    forecast.forEach { day in
        print("Date: \(day.date)")
        print("  High: \(day.highTemperature)")
        print("  Low: \(day.lowTemperature)")
        print("  Condition: \(day.condition)")
        print("  Precipitation: \(day.precipitationChance)")
    }

    return forecast
}
```

### Example 3: Fetch hourly forecast
```swift
import WeatherKit
import CoreLocation

func getHourlyForecast(latitude: Double, longitude: Double) async throws -> [HourWeather] {
    let location = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    let weather = try await WeatherService.shared.weather(for: location)

    let hourlyForecast = weather.hourlyForecast
    hourlyForecast.forEach { hour in
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        print("\(formatter.string(from: hour.date)): \(hour.temperature), \(hour.condition)")
    }

    return hourlyForecast
}
```

### Example 4: Handle weather attribution (required)
```swift
import WeatherKit
import CoreLocation

func getWeatherWithAttribution(latitude: Double, longitude: Double) async throws {
    let location = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    let weather = try await WeatherService.shared.weather(for: location)

    // Display attribution per Apple terms
    let attribution = weather.attribution
    print("Attribution legal text: \(attribution.legalAttribution)")
    print("Service mark: \(attribution.serviceMark)")

    // Construct required attribution UI
    let attributionURL = attribution.attributionURL
    print("Attribution URL: \(attributionURL)")

    // Must be displayed in your weather UI
    displayAttributionInUI(text: attribution.legalAttribution, url: attributionURL)
}

func displayAttributionInUI(text: String, url: URL) {
    // Add attribution label/link to weather view
    // Example: "Powered by Apple Weather"
}
```

### Example 5: Fetch minute-by-minute forecast (24h)
```swift
import WeatherKit
import CoreLocation

func getMinutelyForecast(latitude: Double, longitude: Double) async throws -> [MinuteWeather] {
    let location = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    let weather = try await WeatherService.shared.weather(for: location)

    let minuteForecast = weather.minuteForecast
    minuteForecast.forEach { minute in
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        print("\(formatter.string(from: minute.date)): \(minute.precipitationChance)% precipitation")
    }

    return minuteForecast
}
```

### Example 6: Check data availability
```swift
import WeatherKit

func checkWeatherAvailability() {
    // Check if WeatherKit is available in user's region
    if let availability = WeatherService.availability {
        print("Weather service available: \(availability)")
    }

    // Some features may not be available in all regions
    // Gracefully fall back if needed
}
```

---

## Common Mistakes

### ❌ Not displaying weather attribution
```swift
// Bad: Violates Apple Weather terms; app may be rejected
let weather = try await WeatherService.shared.weather(for: location)
displayTemperature(weather.currentWeather.temperature)
// No attribution shown
```
✅ **Fix:** Always display attribution
```swift
let weather = try await WeatherService.shared.weather(for: location)
displayTemperature(weather.currentWeather.temperature)

let attribution = weather.attribution
displayAttributionLabel(
    text: attribution.legalAttribution,
    url: attribution.attributionURL
)
```

### ❌ Making weather requests on main thread
```swift
// Bad: Blocks UI while fetching
let weather = try await WeatherService.shared.weather(for: location)
updateUI(with: weather)
```
✅ **Fix:** Use Task or async context
```swift
Task {
    do {
        let weather = try await WeatherService.shared.weather(for: location)
        DispatchQueue.main.async {
            updateUI(with: weather)
        }
    } catch {
        print("Weather error: \(error)")
    }
}
```

### ❌ Ignoring regional availability
```swift
// Bad: Assumes WeatherKit available worldwide
let weather = try await WeatherService.shared.weather(for: location)
```
✅ **Fix:** Check availability gracefully
```swift
do {
    let weather = try await WeatherService.shared.weather(for: location)
} catch {
    if error is WeatherError {
        print("WeatherKit not available in this region")
        useAlternativeWeatherSource()
    }
}
```

### ❌ Not caching weather data
```swift
// Bad: Fetches every time; high API usage
func updateWeatherUI() {
    let weather = try await WeatherService.shared.weather(for: location)
    updateUI(with: weather)
}
```
✅ **Fix:** Cache with reasonable TTL
```swift
var cachedWeather: (weather: Weather, timestamp: Date)?
let cacheTTL: TimeInterval = 10 * 60 // 10 minutes

func getWeatherWithCache(for location: CLLocationCoordinate2D) async throws -> Weather {
    if let cached = cachedWeather, Date().timeIntervalSince(cached.timestamp) < cacheTTL {
        return cached.weather
    }

    let weather = try await WeatherService.shared.weather(for: location)
    cachedWeather = (weather, Date())
    return weather
}
```

### ❌ Not handling missing forecast data
```swift
// Bad: Assumes all forecast types available
let daily = weather.dailyForecast
let hourly = weather.hourlyForecast
let minute = weather.minuteForecast
// May be empty or nil in some regions
```
✅ **Fix:** Check data availability
```swift
if !weather.dailyForecast.isEmpty {
    displayDailyForecast(weather.dailyForecast)
}

if !weather.hourlyForecast.isEmpty {
    displayHourlyForecast(weather.hourlyForecast)
}

if !weather.minuteForecast.isEmpty {
    displayMinuteForecast(weather.minuteForecast)
}
```

---

## Review Checklist

- [ ] **Attribution displayed** in weather UI (legal requirement; "Powered by Apple Weather")
- [ ] Attribution URL clickable and links to Apple Weather
- [ ] Weather requests run on background thread; UI updates on main
- [ ] Regional availability checked; graceful fallback if unavailable
- [ ] Data caching implemented (TTL ~10 minutes to avoid excessive API calls)
- [ ] Error handling covers network failures, unavailable regions, missing data
- [ ] Forecast data (daily/hourly/minute) checked for existence before display
- [ ] Temperature units handled correctly (Celsius/Fahrenheit per locale)
- [ ] Wind speed, precipitation amounts use correct measurement units
- [ ] Location coordinate precision adequate (6+ decimal places)
- [ ] Privacy: CoreLocation used only if weather needs real-time location
- [ ] Tests mock WeatherService for offline testing

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

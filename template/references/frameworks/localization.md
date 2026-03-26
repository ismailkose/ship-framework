# Localization — iOS Reference

> **When to read:** Dev reads this when implementing multi-language support, RTL layouts, string catalogs, pluralization, and locale-aware formatting.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Types/Methods |
|---------|---------|-------------------|
| **String Catalogs (.xcstrings)** | Modern localization format | Xcode editor, per-device strings, translations |
| **LocalizedStringKey** | SwiftUI string wrapping | `Text(LocalizedStringKey("key"))` |
| **String Interpolation** | Dynamic localized text | `.init(localized:)` with parameters |
| **Pluralization Rules** | Language-aware plurals | Variations for zero, one, other |
| **DateFormatter** | Locale-aware dates | `.dateStyle`, `.timeStyle`, current locale |
| **NumberFormatter** | Locale-aware numbers | `.numberStyle`, currency, percent |
| **Locale** | User language/region | `Locale.current`, `Locale.preferredLanguages` |
| **Right-to-Left** | Arabic, Hebrew layout | `semanticContentAttribute`, directionality |
| **Accessibility Strings** | Non-UI localization | Comments in .xcstrings for context |
| **Base Localization** | Source language | Development locale, not in app bundle |

---

## Code Examples

**Example 1: Modern String Catalog with SwiftUI**
```swift
// In Xcode: +Localization → Create from source language
// File created: Localizable.xcstrings

struct ProductView: View {
    let productName = "Widget"
    let price = 19.99

    var body: some View {
        VStack {
            // Simple string
            Text(LocalizedStringKey("product_title"))

            // String with interpolation
            Text("Price: \(price)")
                .environment(\.locale, .current)

            // Plural form (in .xcstrings: "item_count" with variations)
            Text(LocalizedStringKey("item_count \(5)"))
        }
    }
}

// .xcstrings format (JSON-like):
// "item_count" → {
//   "localizations": {
//     "en": {
//       "variations": {
//         "plural": {
//           "one": "You have %lld item",
//           "other": "You have %lld items"
//         }
//       }
//     },
//     "es": { ... }
//   }
// }
```

**Example 2: Locale-aware date and number formatting**
```swift
func formatPriceForLocale(_ amount: Double, locale: Locale = .current) -> String {
    let formatter = NumberFormatter()
    formatter.locale = locale
    formatter.numberStyle = .currency
    formatter.currencyCode = locale.currency?.identifier ?? "USD"
    return formatter.string(from: NSNumber(value: amount)) ?? "$\(amount)"
}

func formatDateForLocale(_ date: Date, locale: Locale = .current) -> String {
    let formatter = DateFormatter()
    formatter.locale = locale
    formatter.dateStyle = .long
    formatter.timeStyle = .short
    return formatter.string(from: date)
}

// Usage:
print(formatPriceForLocale(19.99, locale: Locale(identifier: "es_ES"))) // "19,99 EUR"
print(formatDateForLocale(Date(), locale: Locale(identifier: "ja_JP"))) // "2026年3月21日 14:30"
```

**Example 3: Right-to-left layout support**
```swift
struct RTLSafeView: View {
    var body: some View {
        HStack(spacing: 16) {
            VStack(alignment: .leading) {
                Text(LocalizedStringKey("greeting"))
                Text(LocalizedStringKey("subtitle"))
            }
            .environment(\.layoutDirection, .rightToLeft) // For RTL languages

            Image(systemName: "checkmark.circle.fill")
                .semanticContentAttribute(.forceLeftToRight) // Icon direction
        }
        .flipped() // Conditionally flip based on locale
    }
}

extension View {
    func flipped() -> some View {
        if Locale.current.language.languageCode?.identifier == "ar" ||
           Locale.current.language.languageCode?.identifier == "he" {
            return AnyView(self.flipped())
        }
        return AnyView(self)
    }
}
```

---

## LocalizedStringResource for App Intents and Widgets

Use `LocalizedStringResource` when passing localized strings to frameworks that resolve them later (App Intents, widgets, notifications, system frameworks):

```swift
// App Intents require LocalizedStringResource
struct OrderCoffeeIntent: AppIntent {
    static var title: LocalizedStringResource = "Order Coffee"
    static var description: LocalizedStringResource = "Place a coffee order"
}

// Widgets
struct MyWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(
            kind: "timer",
            provider: Provider()
        ) { entry in
            TimerView(entry: entry)
        }
        .configurationDisplayName(LocalizedStringResource("Timer"))
        .description(LocalizedStringResource("Start a quick timer"))
    }
}

// Pass around without resolving yet -- resolved at display time with user's current locale
func showAlert(title: LocalizedStringResource, message: LocalizedStringResource) {
    let resolvedTitle = String(localized: title)
    let resolvedMessage = String(localized: message)
    // Display alert with resolved strings
}
```

## Grammar Agreement Inflection (iOS 17+)

Use `^[...]` syntax for automatic grammatical agreement across languages:

```swift
// Automatically adjusts for gender/number in supported languages
Text("^[\(count) \("photo")](inflect: true) added")
// English: "1 photo added" / "3 photos added"
// Spanish: "1 foto agregada" / "3 fotos agregadas"
```

## Device-Specific String Variations

String Catalogs support device-specific text (iPhone vs iPad vs Mac):

```swift
// In String Catalog editor, enable "Vary by Device" for a key
// iPhone: "Tap to continue"
// iPad:   "Tap or click to continue"
// Mac:    "Click to continue"
```

## @ScaledMetric for Spacing

Scale spacing and sizing with Dynamic Type:

```swift
struct ProductCard: View {
    @ScaledMetric var padding = 16
    @ScaledMetric var titleSize = 18

    var body: some View {
        VStack(spacing: padding) {
            Text("Product Name")
                .font(.system(size: titleSize, weight: .bold))
            Text("Description")
                .font(.body)
        }
        .padding(padding)
    }
}
```

## FormatStyle.list with Grammar

Format lists with proper grammar for different locales:

```swift
let items = ["Apples", "Oranges", "Bananas"]

// Conjunction lists
Text(items.formatted(.list(type: .and)))
// English: "Apples, Oranges, and Bananas"
// French:  "Apples, Oranges et Bananas"

// Disjunction lists
Text(items.formatted(.list(type: .or)))
// English: "Apples, Oranges, or Bananas"
```

## @ScaledMetric for Spacing

Scale spacing and sizing with Dynamic Type:

```swift
struct ProductCard: View {
    @ScaledMetric var padding = 16
    @ScaledMetric var titleSize = 18

    var body: some View {
        VStack(spacing: padding) {
            Text("Product Name")
                .font(.system(size: titleSize, weight: .bold))
            Text("Description")
                .font(.body)
        }
        .padding(padding)
    }
}
```

## Device-Specific String Variations

String Catalogs support device-specific text (iPhone vs iPad vs Mac):

```swift
// In String Catalog editor, enable "Vary by Device" for a key
// iPhone: "Tap to continue"
// iPad:   "Tap or click to continue"
// Mac:    "Click to continue"
```

## Grammar Agreement Inflection (iOS 17+)

Use `^[...]` syntax for automatic grammatical agreement across languages:

```swift
// Automatically adjusts for gender/number in supported languages
Text("^[\(count) \("photo")](inflect: true) added")
// English: "1 photo added" / "3 photos added"
// Spanish: "1 foto agregada" / "3 fotos agregadas"
```

## Pseudolocalization Testing

Test localization without actual translations using Xcode schemes:

```swift
// Set scheme environment variable:
// AppleLanguages: (ja)      // Test with Japanese
// AppleLocale: ja_JP        // Full locale

// For accented/double-length testing:
// Use Xcode's pseudolanguage options to detect:
// - Truncation bugs
// - Layout overflow (German is ~30% longer)
// - RTL issues
// - Untranslated strings
```

## Pseudolocalization Testing

Test localization without actual translations using Xcode schemes:

```swift
// Set scheme environment variable:
// AppleLanguages: (ja)      // Test with Japanese
// AppleLocale: ja_JP        // Full locale

// For accented/double-length testing:
// Use Xcode's pseudolanguage options to detect:
// - Truncation bugs
// - Layout overflow (German is ~30% longer)
// - RTL issues
// - Untranslated strings
```

## Common Mistakes

**Mistake 1: Hardcoded strings without localization**
```swift
// ❌ WRONG — English-only
Text("Welcome to the app")
Button("Submit") { }
Label("Settings", systemImage: "gear")

// ✅ CORRECT — Localized
Text(LocalizedStringKey("welcome_message"))
Button(LocalizedStringKey("submit_button")) { }
Label(LocalizedStringKey("settings_label"), systemImage: "gear")
```

**Mistake 2: String interpolation without locale context**
```swift
// ❌ WRONG — Ignores locale for date/number formatting
Text("Price: \(price)") // Shows "Price: 19.989999999"
Text("Date: \(date)") // Shows US format regardless of locale

// ✅ CORRECT — Use formatters or string catalog variations
Text("Price: \(formatPrice(price))")
Text("Date: \(formatDate(date))")
```

**Mistake 3: Ignoring RTL languages in layout**
```swift
// ❌ WRONG — Assumes LTR, breaks in Arabic/Hebrew
HStack {
    Image("arrow_left")
    Text("Back")
}

// ✅ CORRECT — Use system layout mirroring
HStack {
    Image(systemName: "chevron.left")
        .semanticContentAttribute(.forceLeftToRight)
    Text(LocalizedStringKey("back_button"))
}
.flipped() // Or use HStack with leading alignment only
```

**Mistake 4: No pluralization rules**
```swift
// ❌ WRONG — Grammar breaks in other languages
Text("You have \(count) item\(count == 1 ? "" : "s")")

// ✅ CORRECT — Use string catalog plurals
Text(LocalizedStringKey("item_count \(count)"))
// .xcstrings includes variations: one="You have 1 item", other="You have %d items"
// Automatically handled in French (plural rules differ), Arabic, etc.
```

**Mistake 5: Accessing preferredLanguages incorrectly**
```swift
// ❌ WRONG — Doesn't respect string catalog
let language = Locale.preferredLanguages.first ?? "en"
let bundle = Bundle(path: Bundle.main.path(forResource: language, ofType: "lproj")!)

// ✅ CORRECT — Let Foundation handle locale
Text(LocalizedStringKey("key")) // Respects system language automatically
// Or for custom logic:
let locale = Locale(identifier: Locale.preferredLanguages.first ?? "en")
```

---

## Review Checklist

- [ ] All user-facing strings use `LocalizedStringKey` or `NSLocalizedString`?
- [ ] String Catalog (.xcstrings) created and synced?
- [ ] Pluralization rules defined in .xcstrings for variable counts?
- [ ] No string concatenation (use string interpolation with parameters)?
- [ ] Dates formatted with `DateFormatter`, respecting `locale`?
- [ ] Numbers/currency formatted with `NumberFormatter`?
- [ ] RTL languages supported (Arabic, Hebrew, Urdu)?
- [ ] `semanticContentAttribute` used on icons that have direction?
- [ ] Form labels and hints localized?
- [ ] No locale-specific hardcoded formatting (e.g., "MM/DD/YYYY")?
- [ ] Accessibility strings have comments in .xcstrings?
- [ ] Tested with Arabic/Hebrew locales in simulator?

---

_Source: Apple Developer Documentation · Localization, String Catalogs, Internationalization · Condensed for Ship Framework agent reference_

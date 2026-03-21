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

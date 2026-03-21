# Accessibility — iOS Reference

> **When to read:** Dev reads this when implementing features for VoiceOver support, Dynamic Type, custom actions, and accessibility testing.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Properties/Methods |
|---------|---------|------------------------|
| **Accessibility Label** | Element description for VoiceOver | `accessibilityLabel`, max 40 characters |
| **Accessibility Hint** | Supplemental description | `accessibilityHint`, explains what happens when activated |
| **Accessibility Traits** | Element type (button, image, etc.) | `accessibilityTraits` (`.button`, `.image`, `.link`, `.tab`) |
| **Accessibility Value** | Dynamic state/amount | `accessibilityValue`, e.g., "75% complete" |
| **Custom Actions** | Gesture alternatives | `accessibilityCustomActions` array |
| **accessibilityRepresentation** | SwiftUI custom views | `accessibilityRepresentation()` wrapper |
| **Dynamic Type** | User-adjustable text sizes | `UIFont.preferredFont()`, `ScaledMetric` in SwiftUI |
| **UIAccessibility Notifications** | VoiceOver focus changes | `UIAccessibility.post(notification:argument:)` |
| **Accessibility Inspector** | Developer testing tool | Xcode simulator tool, element hierarchy audit |
| **High Contrast** | Enhanced visibility | `UIColor.systemBackground`, avoid color-only indicators |

---

## Code Examples

**Example 1: SwiftUI button with accessibility**
```swift
Button(action: { submitForm() }) {
    Image(systemName: "checkmark.circle")
        .font(.title2)
}
.accessibilityLabel("Submit Form")
.accessibilityHint("Sends your application to review")
.accessibilityAddTraits(.isButton)
```

**Example 2: Custom action for swipe gesture alternative**
```swift
struct CardView: View {
    var body: some View {
        VStack {
            Text("Card Title")
        }
        .accessibilityCustomActions([
            AccessibilityCustomAction(
                name: "Delete",
                target: self,
                selector: #selector(deleteCard)
            ),
            AccessibilityCustomAction(
                name: "Archive",
                target: self,
                selector: #selector(archiveCard)
            )
        ])
    }

    @objc func deleteCard() {
        // Perform deletion
    }
}
```

**Example 3: Dynamic Type and ScaledMetric for responsive text**
```swift
struct ProductCard: View {
    @ScaledMetric var titleSize = 18
    @ScaledMetric var bodySize = 14

    var body: some View {
        VStack(alignment: .leading) {
            Text("Product Name")
                .font(.system(size: titleSize, weight: .bold))
            Text("Description")
                .font(.system(size: bodySize))
        }
    }
}
```

---

## Common Mistakes

**Mistake 1: No accessibility labels on images**
```swift
// ❌ WRONG — Image has no label
Image("homeIcon")
    .resizable()

// ✅ CORRECT — Always label images
Image("homeIcon")
    .resizable()
    .accessibilityLabel("Home")
    .accessibilityRemoveTraits(.isImage) // If icon is decorative
```

**Mistake 2: Color-only indicators (no text fallback)**
```swift
// ❌ WRONG — Only color indicates status
ZStack {
    Circle()
        .fill(status == .active ? Color.green : Color.red)
}

// ✅ CORRECT — Include text and accessibility value
ZStack {
    Circle()
        .fill(status == .active ? Color.green : Color.red)
    Text(status == .active ? "✓" : "✗")
}
.accessibilityValue(status == .active ? "Active" : "Inactive")
```

**Mistake 3: Ignoring Dynamic Type in custom fonts**
```swift
// ❌ WRONG — Fixed font size ignores user preferences
Text("Title")
    .font(.system(size: 24, weight: .bold))

// ✅ CORRECT — Use scaled metrics
Text("Title")
    .font(.system(size: 24, weight: .bold))
    .lineLimit(nil) // Allow wrapping at larger sizes
    .minimumScaleFactor(0.8) // Or use @ScaledMetric
```

**Mistake 4: Button with no accessibility trait**
```swift
// ❌ WRONG — SwiftUI custom button loses button trait
HStack {
    Image(systemName: "square.and.arrow.up")
    Text("Share")
}
.onTapGesture { share() }

// ✅ CORRECT — Restore button trait
Button(action: { share() }) {
    HStack {
        Image(systemName: "square.and.arrow.up")
        Text("Share")
    }
}
```

**Mistake 5: No announcement when content updates dynamically**
```swift
// ❌ WRONG — VoiceOver user doesn't know count changed
@State var itemCount = 0

var body: some View {
    VStack {
        Text("Items: \(itemCount)")
        Button("Add") { itemCount += 1 }
    }
}

// ✅ CORRECT — Post accessibility notification
var body: some View {
    VStack {
        Text("Items: \(itemCount)")
        Button("Add") {
            itemCount += 1
            UIAccessibility.post(notification: .announcement, argument: "Item added, total: \(itemCount)")
        }
    }
}
```

---

## Review Checklist

- [ ] All interactive elements have `accessibilityLabel`?
- [ ] Button purposes clearly described (not just "Button")?
- [ ] Images have labels or `.isImage` trait removed if decorative?
- [ ] Custom gestures have corresponding `accessibilityCustomActions`?
- [ ] Color not the only visual indicator of state?
- [ ] Text sizes use `ScaledMetric` or `preferredFont()`?
- [ ] Contrast ratio meets WCAG AA (4.5:1 for text)?
- [ ] Form inputs have labels (via `accessibilityLabeledPair`)?
- [ ] Dynamic content updates post `UIAccessibility.post(notification:)`?
- [ ] Test with VoiceOver enabled (simulator Settings)?
- [ ] Accessibility Inspector shows no missing labels?
- [ ] No custom colors used that are inaccessible at 3x zoom?

---

_Source: Apple Developer Documentation · Accessibility, Dynamic Type, VoiceOver · Condensed for Ship Framework agent reference_

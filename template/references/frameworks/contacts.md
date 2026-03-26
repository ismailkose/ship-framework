# Contacts — iOS Reference

> **When to read:** Dev reads this when building features that access or modify contacts: contact picking, contact creation, address book access.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `CNContactStore` | Main API; manages contact access and modifications |
| `CNContact` | Immutable contact; keys indicate which fields are populated |
| `CNMutableContact` | Editable contact; for creation/modification |
| `CNContactFetchRequest` | Query contacts by predicate, specify keys to fetch |
| `CNContactPickerViewController` | Presents native contact picker UI |
| `CNSaveRequest` | Bundles create/update/delete operations; atomic |
| `CNContactFormatter` | Format contact name (`.fullName`, `.phoneticFullName`) |
| `CNLabeledValue` | Wraps value with label (e.g., "work", "home", "iPhone") |
| `CNPhoneNumber` | Phone number; validated format |
| `CNPostalAddress` | Street, city, state, ZIP, country |
| `CNContactRelation` | Relationship type (manager, spouse, parent, etc.) |
| `CNAuthorizationStatus` | `.authorized`, `.denied`, `.restricted`, `.notDetermined`, `.limited` (iOS 18+) |

### Authorization States
| Status | Meaning |
|---|---|
| `.notDetermined` | User has not been prompted yet |
| `.authorized` | Full read/write access granted |
| `.denied` | User denied access; direct to Settings |
| `.restricted` | Parental controls or MDM restrict access |
| `.limited` | iOS 18+: user granted access to selected contacts only |

### Composite Key Descriptors
Use `CNContactFormatter.descriptorForRequiredKeys(for:)` to fetch all keys needed for formatting a contact's name:

```swift
let nameKeys = CNContactFormatter.descriptorForRequiredKeys(for: .fullName)
let keys: [CNKeyDescriptor] = [nameKeys, CNContactPhoneNumbersKey as CNKeyDescriptor]
```

## Authorization States (iOS 18+)

iOS 18 adds `.limited` authorization where the user grants access to selected contacts only:

```swift
let status = CNContactStore.authorizationStatus(for: .contacts)
switch status {
case .authorized:
    // Full read/write access
    break
case .limited:
    // iOS 18+: User granted access to selected contacts only
    break
case .denied, .restricted:
    // Direct user to Settings
    break
case .notDetermined:
    // Will prompt on first use
    break
@unknown default:
    break
}
```

## Contact Picker Predicate Filtering

Filter the contact picker to show only contacts matching specific criteria:

```swift
let picker = CNContactPickerViewController()
// Only show contacts that have an email address
picker.predicateForEnablingContact = NSPredicate(format: "emailAddresses.@count > 0")
// Selecting a contact returns it directly (no detail card)
picker.predicateForSelectionOfContact = NSPredicate(value: true)
```

## CNContactStoreDidChange Observer

Observe contact store changes to refresh cached CNContact objects:

```swift
NotificationCenter.default.addObserver(
    forName: .CNContactStoreDidChange,
    object: nil,
    queue: .main
) { _ in
    // Refetch contacts -- cached CNContact objects are stale
    refreshContacts()
}
```

---

## Code Examples

### Example 1: Pick a contact (native picker)
```swift
import Contacts
import ContactsUI

class ContactPickerViewController: UIViewController, CNContactPickerDelegate {
    func openContactPicker() {
        let picker = CNContactPickerViewController()
        picker.delegate = self
        present(picker, animated: true)
    }

    // MARK: - CNContactPickerDelegate
    func contactPicker(_ picker: CNContactPickerViewController, didSelect contact: CNContact) {
        dismiss(animated: true)
        print("Name: \(CNContactFormatter.string(from: contact, style: .fullName))")
        print("Phone: \(contact.phoneNumbers.first?.value.stringValue ?? "N/A")")
    }

    func contactPickerDidCancel(_ picker: CNContactPickerViewController) {
        dismiss(animated: true)
    }
}
```

### Example 2: Fetch all contacts with predicate
```swift
import Contacts

func fetchContacts(matching predicate: NSPredicate? = nil) throws -> [CNContact] {
    let store = CNContactStore()
    let keysToFetch = [CNContactGivenNameKey, CNContactFamilyNameKey, CNContactPhoneNumbersKey]
    let request = CNContactFetchRequest(keysToFetch: keysToFetch)
    request.predicate = predicate

    var contacts: [CNContact] = []
    try store.enumerateContacts(with: request) { contact in
        contacts.append(contact)
    }
    return contacts
}

// Usage
let predicate = CNContact.predicateForContacts(matchingName: "John")
let results = try fetchContacts(matching: predicate)
```

### Example 3: Create and save a new contact
```swift
import Contacts

func createContact(givenName: String, familyName: String, phone: String) throws {
    let store = CNContactStore()

    // Request authorization if needed
    if CNContactStore.authorizationStatus(for: .contacts) != .authorized {
        try store.requestAccess(for: .contacts) { granted, error in
            if granted {
                // Proceed
            }
        }
    }

    let mutableContact = CNMutableContact()
    mutableContact.givenName = givenName
    mutableContact.familyName = familyName

    let phoneNumber = CNPhoneNumber(stringValue: phone)
    mutableContact.phoneNumbers = [CNLabeledValue(label: CNLabelPhoneNumberIPhone, value: phoneNumber)]

    let saveRequest = CNSaveRequest()
    saveRequest.add(mutableContact, toContainerWithIdentifier: nil)

    do {
        try store.execute(saveRequest)
        print("Contact saved")
    } catch {
        print("Save error: \(error)")
    }
}
```

### Example 3b: Filter the contact picker using predicates
```swift
let picker = CNContactPickerViewController()
// Only show contacts that have an email address
picker.predicateForEnablingContact = NSPredicate(format: "emailAddresses.@count > 0")
// Selecting a contact returns it directly (no detail card)
picker.predicateForSelectionOfContact = NSPredicate(value: true)
```

### Example 3c: Observe contact store changes
```swift
NotificationCenter.default.addObserver(
    forName: .CNContactStoreDidChange,
    object: nil,
    queue: .main
) { _ in
    // Refetch contacts -- cached CNContact objects are stale
    refreshContacts()
}
```

### Example 4: Update and delete contacts
```swift
import Contacts

func updateContact(identifier: String, newPhone: String) throws {
    let store = CNContactStore()
    let keysToFetch = [CNContactPhoneNumbersKey]

    guard let contact = try store.unifiedContact(withIdentifier: identifier, keysToFetch: keysToFetch) as CNContact else {
        return
    }

    let mutableContact = contact.mutableCopy() as! CNMutableContact
    let phoneNumber = CNPhoneNumber(stringValue: newPhone)
    mutableContact.phoneNumbers = [CNLabeledValue(label: CNLabelPhoneNumberMobile, value: phoneNumber)]

    let saveRequest = CNSaveRequest()
    saveRequest.update(mutableContact)
    try store.execute(saveRequest)
    print("Contact updated")
}

func deleteContact(identifier: String) throws {
    let store = CNContactStore()
    guard let contact = try store.unifiedContact(withIdentifier: identifier, keysToFetch: []) as CNContact else {
        return
    }

    let mutableContact = contact.mutableCopy() as! CNMutableContact
    let saveRequest = CNSaveRequest()
    saveRequest.delete(mutableContact)
    try store.execute(saveRequest)
    print("Contact deleted")
}
```

---

## Common Mistakes

### ❌ Not requesting authorization before accessing contacts
```swift
// Bad: Crashes if not authorized
let store = CNContactStore()
let request = CNContactFetchRequest(keysToFetch: [...])
try store.enumerateContacts(with: request) { ... }
```
✅ **Fix:** Check/request authorization first
```swift
if CNContactStore.authorizationStatus(for: .contacts) == .authorized {
    let store = CNContactStore()
    try store.enumerateContacts(with: request) { ... }
} else {
    let store = CNContactStore()
    try store.requestAccess(for: .contacts) { granted, error in
        if granted { /* proceed */ }
    }
}
```

### ❌ Fetching unnecessary contact fields
```swift
// Bad: Loads 50+ fields; slow
let keysToFetch = [CNContactKey] // Loads everything
let request = CNContactFetchRequest(keysToFetch: keysToFetch)
```
✅ **Fix:** Specify only needed keys
```swift
let keysToFetch = [
    CNContactGivenNameKey,
    CNContactFamilyNameKey,
    CNContactPhoneNumbersKey,
    CNContactImageDataKey
]
let request = CNContactFetchRequest(keysToFetch: keysToFetch)
```

### ❌ Modifying immutable contact directly
```swift
// Bad: CNContact is immutable; changes lost
let contact = try store.unifiedContact(withIdentifier: id, keysToFetch: [...])
contact.givenName = "Bob" // No effect
```
✅ **Fix:** Use mutableCopy()
```swift
let contact = try store.unifiedContact(withIdentifier: id, keysToFetch: [...])
let mutable = contact.mutableCopy() as! CNMutableContact
mutable.givenName = "Bob"

let saveRequest = CNSaveRequest()
saveRequest.update(mutable)
try store.execute(saveRequest)
```

### ❌ Mixing multiple save requests
```swift
// Bad: Each execute() is a separate transaction; risky
let req1 = CNSaveRequest()
req1.add(contact1, toContainerWithIdentifier: nil)
try store.execute(req1)

let req2 = CNSaveRequest()
req2.add(contact2, toContainerWithIdentifier: nil)
try store.execute(req2) // What if this fails?
```
✅ **Fix:** Batch operations in single CNSaveRequest
```swift
let saveRequest = CNSaveRequest()
saveRequest.add(contact1, toContainerWithIdentifier: nil)
saveRequest.add(contact2, toContainerWithIdentifier: nil)
saveRequest.delete(contact3)
try store.execute(saveRequest) // Atomic
```

### ❌ Not handling fetch request authorization gracefully
```swift
// Bad: Enumeration silently succeeds with empty list
try store.enumerateContacts(with: request) { contact in
    // Never called if not authorized
}
print("Done") // User thinks there are no contacts
```
✅ **Fix:** Check authorization status explicitly
```swift
let status = CNContactStore.authorizationStatus(for: .contacts)
switch status {
case .authorized:
    try store.enumerateContacts(with: request) { contact in ... }
case .denied, .restricted:
    showAuthorizationAlert()
case .notDetermined:
    try store.requestAccess(for: .contacts) { granted, _ in
        if granted { /* retry */ }
    }
@unknown default:
    break
}
```

---

## Review Checklist

- [ ] `CNContactStore.authorizationStatus(for: .contacts)` checked before any access
- [ ] `requestAccess(for:completionHandler:)` called if `.notDetermined`
- [ ] Authorization denial handled gracefully
- [ ] Only **necessary keys** specified in fetch requests (no fetching everything)
- [ ] `mutableCopy()` used for modifications; immutable CNContact respected
- [ ] Multiple operations batched in single `CNSaveRequest` (atomicity)
- [ ] Phone numbers validated with `CNPhoneNumber`
- [ ] Error handling for network/sync issues (contacts may be cloud-synced)
- [ ] `CNContactFormatter` used for display names (handles localization, formatting)
- [ ] Contact picker (`CNContactPickerViewController`) used when user selects (not manual fetch)
- [ ] Privacy: `NSContactsUsageDescription` in Info.plist
- [ ] Tests mock `CNContactStore` for offline testing

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

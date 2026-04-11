# AppMigrationKit Reference

> **When to read:** Dev reads when building Android-to-iOS data migration.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Overview

AppMigrationKit enables transferring user data from Android apps to iOS during device setup. Uses extension-based architecture.

## Extension Setup

Create an App Migration Extension target:

```swift
import AppMigrationKit

class MigrationExtension: AMDataImportExtension {
  override func importData(from source: AMDataSource) async throws {
    // Read data from Android export
    let userData = try await source.readData(forKey: "user_profile")
    let settings = try await source.readData(forKey: "app_settings")

    // Import into iOS app's data store
    try await importUserProfile(userData)
    try await importSettings(settings)
  }
}
```

## Android Side (Export)

The Android app provides data through a standard export format:

```swift
// Define what data to export
class MigrationExporter: AMDataExportExtension {
  override var exportableKeys: [String] {
    ["user_profile", "app_settings", "favorites", "history"]
  }

  override func exportData(forKey key: String) async throws -> Data {
    switch key {
    case "user_profile": return try JSONEncoder().encode(userProfile)
    case "app_settings": return try JSONEncoder().encode(settings)
    default: return Data()
    }
  }
}
```

## Status Checking

```swift
let status = try await AMDataMigration.shared.migrationStatus
switch status {
case .available(let source):
  // Android data available — offer migration
  showMigrationPrompt(source: source)
case .completed:
  // Already migrated
case .notAvailable:
  // No Android data found
@unknown default: break
}
```

## Common Mistakes
- ❌ Not checking migration status on first launch — miss the migration window
- ❌ Assuming all keys have data — some may be empty or nil
- ❌ Not handling partial migration — some data may fail while others succeed
- ❌ Blocking app launch on migration — run in background, show progress

## Review Checklist
- [ ] Migration extension registered correctly in Info.plist
- [ ] All exportable keys handled with fallbacks
- [ ] Partial migration failures handled gracefully
- [ ] Progress UI shown during migration
- [ ] Migration status checked on first launch

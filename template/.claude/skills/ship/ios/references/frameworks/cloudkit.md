# CloudKit — iOS Reference

> **When to read:** Dev reads this when syncing data with iCloud, sharing records, or querying cloud databases.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `CKContainer` | Gateway to CloudKit | Fetch with `CKContainer.default()` |
| `CKDatabase` | Private, public, or shared | `privateCloudDatabase`, `publicCloudDatabase`, `sharedCloudDatabase` |
| `CKRecord` | CloudKit document | Key-value; includes metadata (ID, timestamps); max 1 MB |
| `CKQuery` | Fetch records by predicate | Filter, sort, limit; async/await API |
| `CKQueryOperation` | Callback-based query execution (legacy) | Older; prefer async/await queries |
| `CKSubscription` | Remote notification trigger | Fires when records change; supports query/database/zone subscriptions |
| `CKSyncEngine` | Recommended sync engine (iOS 17+) | Handles scheduling, retries, change tokens, push notifications |
| `CKRecordZone` | Custom zone | Enables atomic commits, change tracking, sharing |
| `CKRecord.Reference` | Foreign key to another record | Defines relationships |
| `CKError` | Error handling | Codes: `.networkFailure`, `.serverRecordChanged`, `.requestRateLimited`, etc. |
| `NSMetadataQuery` | Monitor iCloud Drive files | Query ubiquitous documents in real-time |
| `NSUbiquitousKeyValueStore` | Simple key-value sync | Max 1024 keys, 1 MB total; for preferences/settings |
| `FileManager` ubiquity APIs | Document-level sync | `setUbiquitous(_:itemAt:destinationURL:)` |

## Code Examples

```swift
// 1. Basic fetch from public database
import CloudKit

func fetchPublicPosts() async {
    let container = CKContainer.default()
    let database = container.publicCloudDatabase

    let query = CKQuery(
        recordType: "Post",
        predicate: NSPredicate(value: true)
    )
    query.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: false)]

    do {
        let records = try await database.records(matching: query, inZoneWith: nil)
        for record in records {
            print("Post: \(record["title"] ?? "")")
        }
    } catch {
        print("Query failed: \(error.localizedDescription)")
    }
}

// 2. Create and save a record to private database
func createPrivateNote(_ text: String) async {
    let container = CKContainer.default()
    let database = container.privateCloudDatabase

    let record = CKRecord(recordType: "Note")
    record["content"] = text as CKRecordValue
    record["createdAt"] = Date() as CKRecordValue

    do {
        let savedRecord = try await database.save(record)
        print("Saved note with ID: \(savedRecord.recordID.recordName)")
    } catch {
        print("Save failed: \(error.localizedDescription)")
    }
}

// 3. Query with predicate and handle errors
func queryUserComments(userID: String) async {
    let container = CKContainer.default()
    let database = container.privateCloudDatabase

    let predicate = NSPredicate(format: "userId == %@", userID)
    let query = CKQuery(recordType: "Comment", predicate: predicate)

    do {
        let records = try await database.records(matching: query)
        print("Found \(records.count) comments")
    } catch let error as CKError {
        switch error.code {
        case .notAuthenticated:
            print("User not signed into iCloud")
        case .networkFailure:
            print("Network error; retry with exponential backoff")
        case .limitExceeded:
            print("Too many requests; implement pagination")
        default:
            print("CloudKit error: \(error.localizedDescription)")
        }
    }
}

// 4. Batch save multiple records
func saveBulkRecords(_ titles: [String]) async {
    let container = CKContainer.default()
    let database = container.privateCloudDatabase

    var records: [CKRecord] = []
    for title in titles {
        let record = CKRecord(recordType: "Item")
        record["title"] = title as CKRecordValue
        records.append(record)
    }

    do {
        let results = try await database.modifyRecords(saving: records, deleting: [])
        print("Saved: \(results.saveResults.count) records")
    } catch {
        print("Batch save failed: \(error.localizedDescription)")
    }
}

// 5. Set up subscription for real-time changes
func subscribeToPostChanges() async {
    let container = CKContainer.default()
    let database = container.publicCloudDatabase

    let predicate = NSPredicate(value: true)
    let subscription = CKQuerySubscription(
        recordType: "Post",
        predicate: predicate,
        subscriptionID: "all-posts",
        options: [.firesOnRecordCreation, .firesOnRecordUpdate, .firesOnRecordDeletion]
    )

    let notificationInfo = CKSubscription.NotificationInfo()
    notificationInfo.shouldSendContentAvailable = true
    notificationInfo.alertBody = "New post"
    subscription.notificationInfo = notificationInfo

    do {
        try await database.save(subscription)
        print("Subscription created")
    } catch {
        print("Subscription failed: \(error.localizedDescription)")
    }
}

// 6. Handle CloudKit with SwiftData integration
@Model
final class CloudSyncedItem {
    var title: String
    var cloudRecordID: String?
    var lastSyncDate: Date?

    init(title: String) {
        self.title = title
        self.cloudRecordID = nil
        self.lastSyncDate = nil
    }

    func syncToCloudKit() async {
        let container = CKContainer.default()
        let database = container.privateCloudDatabase

        let record = CKRecord(recordType: "Item")
        record["title"] = self.title as CKRecordValue

        do {
            let savedRecord = try await database.save(record)
            self.cloudRecordID = savedRecord.recordID.recordName
            self.lastSyncDate = Date()
        } catch {
            print("Sync failed: \(error.localizedDescription)")
        }
    }
}

// 7. CKSyncEngine (iOS 17+) for modern sync
final class SyncManager: CKSyncEngineDelegate {
    let syncEngine: CKSyncEngine
    private var stateSerialization: Data?

    init(container: CKContainer = .default()) {
        let config = CKSyncEngine.Configuration(
            database: container.privateCloudDatabase,
            stateSerialization: loadStateSerialization(),
            delegate: self
        )
        self.syncEngine = CKSyncEngine(config)
    }

    func handleEvent(_ event: CKSyncEngine.Event, syncEngine: CKSyncEngine) {
        switch event {
        case .stateUpdate(let update):
            stateSerialization = update.stateSerialization
            saveStateSerialization(update.stateSerialization)
        case .accountChange:
            print("Account changed")
        case .fetchedRecordZoneChanges(let changes):
            for modification in changes.modifications {
                processRemoteRecord(modification.record)
            }
            for deletion in changes.deletions {
                processRemoteDeletion(deletion.recordID)
            }
        default:
            break
        }
    }

    func nextRecordZoneChangeBatch(
        _ context: CKSyncEngine.SendChangesContext,
        syncEngine: CKSyncEngine
    ) -> CKSyncEngine.RecordZoneChangeBatch? {
        let pending = syncEngine.state.pendingRecordZoneChanges
        return CKSyncEngine.RecordZoneChangeBatch(
            pendingChanges: Array(pending)
        ) { recordID in
            self.recordToSend(for: recordID)
        }
    }

    private func loadStateSerialization() -> Data? {
        UserDefaults.standard.data(forKey: "syncEngineState")
    }

    private func saveStateSerialization(_ data: Data) {
        UserDefaults.standard.set(data, forKey: "syncEngineState")
    }

    private func processRemoteRecord(_ record: CKRecord) { }
    private func processRemoteDeletion(_ id: CKRecord.ID) { }
    private func recordToSend(for id: CKRecord.ID) -> CKRecord { CKRecord(recordType: "Test") }
}

// 8. Custom record zones (Private/Shared only)
func createCustomZone() async throws {
    let container = CKContainer.default()
    let database = container.privateCloudDatabase

    let zoneID = CKRecordZone.ID(zoneName: "NotesZone")
    let zone = CKRecordZone(zoneID: zoneID)
    try await database.save(zone)
}

// 9. iCloud Drive with NSMetadataQuery
func monitorICloudDrive() {
    let query = NSMetadataQuery()
    query.predicate = NSPredicate(format: "%K LIKE '*.pdf'", NSMetadataItemFSNameKey)
    query.searchScopes = [NSMetadataQueryUbiquitousDocumentsScope]

    NotificationCenter.default.addObserver(
        forName: .NSMetadataQueryDidFinishGathering,
        object: query,
        queue: .main
    ) { _ in
        query.disableUpdates()
        for item in query.results as? [NSMetadataItem] ?? [] {
            let name = item.value(forAttribute: NSMetadataItemFSNameKey) as? String
            let status = item.value(
                forAttribute: NSMetadataUbiquitousItemDownloadingStatusKey
            ) as? String
            print("\(name ?? ""): \(status ?? "")")
        }
        query.enableUpdates()
    }
    query.start()
}

// 10. Three-way merge for conflict resolution
func resolveConflict(_ error: CKError) {
    guard error.code == .serverRecordChanged,
          let ancestor = error.ancestorRecord,
          let client = error.clientRecord,
          let server = error.serverRecord
    else { return }

    for key in client.changedKeys() {
        if server[key] == ancestor[key] {
            server[key] = client[key]  // Server unchanged, use client
        } else if client[key] == ancestor[key] {
            // Client unchanged, keep server (already there)
        } else {
            // Both changed, apply custom merge logic
            server[key] = client[key]  // Or implement more sophisticated merge
        }
    }

    Task {
        try await CKContainer.default().privateCloudDatabase.save(server)
    }
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Not checking user authentication status | Check `CKContainer.default().accountStatus()` before queries |
| Ignoring CKError codes; generic error handling | Switch on error code; handle `.networkFailure`, `.serverRecordChanged`, `.quotaExceeded`, etc. |
| Querying without predicates; fetching entire database | Use NSPredicate to filter; implement pagination for large result sets |
| Not using relationships (CKRecord.Reference) for foreign keys | Use CKRecord.Reference for record-to-record relationships |
| Blocking UI on CloudKit operations | Always use `async/await`; never block main thread on network calls |
| Ignoring `.serverRecordChanged` errors | Implement three-way merge with ancestor, client, server records |
| Not persisting change tokens | Save change tokens to disk; required for incremental sync |
| Polling for changes on a timer | Use `CKSubscription` or `CKSyncEngine` for push-based sync |

## CKError Handling

| Error Code | Cause | Strategy |
|---|---|---|
| `.networkFailure`, `.networkUnavailable` | Network issue | Queue for retry when connectivity returns |
| `.serverRecordChanged` | Optimistic lock conflict | Three-way merge (ancestor, client, server); save merged record |
| `.requestRateLimited`, `.zoneBusy`, `.serviceUnavailable` | Rate limit or server busy | Retry after `retryAfterSeconds` delay |
| `.quotaExceeded` | Storage quota full | Notify user; reduce data usage |
| `.notAuthenticated` | User not signed into iCloud | Prompt iCloud sign-in |
| `.partialFailure` | Some items failed | Inspect `partialErrorsByItemID` per item; retry per-item |
| `.changeTokenExpired` | Token invalidated | Reset token; refetch all changes (slow) |
| `.userDeletedZone` | User deleted zone in Settings | Recreate zone; re-upload all data |
| `.accountTemporarilyUnavailable` | iCloud temporarily unavailable | Retry later; usually resolves quickly |

## Custom Record Zones

Custom zones (available on Private and Shared databases) support atomic commits and change tracking:

```swift
let zoneID = CKRecordZone.ID(zoneName: "NotesZone")
let zone = CKRecordZone(zoneID: zoneID)
try await privateDB.save(zone)

// Create records in the zone
let recordID = CKRecord.ID(recordName: UUID().uuidString, zoneID: zoneID)
let record = CKRecord(recordType: "Note", recordID: recordID)
record["title"] = "My Note"
try await privateDB.save(record)
```

## Change Token Persistence

Persist change tokens to disk for incremental sync. Never pass nil on every fetch:

```swift
class ChangeTokenManager {
    private let defaults = UserDefaults.standard
    private let tokenKey = "lastChangeToken"

    func getLastToken() -> CKServerChangeToken? {
        guard let data = defaults.data(forKey: tokenKey) else { return nil }
        return try? NSKeyedUnarchiver.unarchivedObject(
            ofClass: CKServerChangeToken.self, from: data
        )
    }

    func saveToken(_ token: CKServerChangeToken?) {
        guard let token = token else {
            defaults.removeObject(forKey: tokenKey)
            return
        }
        if let data = try? NSKeyedArchiver.archivedData(
            withRootObject: token, requiringSecureCoding: true
        ) {
            defaults.set(data, forKey: tokenKey)
        }
    }
}
```

## NSUbiquitousKeyValueStore

Simple, automatic sync of app preferences and settings:

```swift
let kvStore = NSUbiquitousKeyValueStore.default

// Write (max 1024 keys, 1 MB total)
kvStore.set("dark", forKey: "theme")
kvStore.set(14.0, forKey: "fontSize")
kvStore.synchronize()

// Read
let theme = kvStore.string(forKey: "theme") ?? "system"

// Observe external changes
NotificationCenter.default.addObserver(
    forName: NSUbiquitousKeyValueStore.didChangeExternallyNotification,
    object: kvStore,
    queue: .main
) { notification in
    guard let userInfo = notification.userInfo else { return }
    let reason = userInfo[NSUbiquitousKeyValueStoreChangeReasonKey] as? Int ?? 0

    switch reason {
    case NSUbiquitousKeyValueStoreServerChange:
        reloadSettings()
    case NSUbiquitousKeyValueStoreInitialSyncChange:
        reloadSettings()
    case NSUbiquitousKeyValueStoreQuotaViolationChange:
        handleQuotaExceeded()
    default:
        break
    }
}
```

## Review Checklist

- [ ] `CKContainer.accountStatus()` checked before CloudKit access
- [ ] Appropriate database used (private/public/shared) for data sensitivity
- [ ] CKError handled with specific code switching (not generic catch-all)
- [ ] `.serverRecordChanged` handled with three-way merge into `serverRecord`
- [ ] Queries include predicates; not open-ended
- [ ] Pagination implemented for large datasets
- [ ] Batch operations use `modifyRecords(saving:deleting:)` for efficiency
- [ ] Subscriptions cleaned up (removed) when no longer needed
- [ ] `CKDatabaseSubscription` or `CKSyncEngine` used for push-based sync (not polling)
- [ ] `CKSyncEngine.state` persisted to disk across launches (iOS 17+)
- [ ] Change tokens persisted; not passed as nil on every fetch
- [ ] CKRecord.Reference used for relationships (not duplicate data)
- [ ] Record IDs persisted locally to avoid duplicate syncs
- [ ] `retryAfterSeconds` respected on rate-limit errors
- [ ] `.partialFailure` inspected per-item via `partialErrorsByItemID`
- [ ] `.changeTokenExpired` resets token and refetches all changes
- [ ] `.userDeletedZone` handled by recreating zone and resyncing
- [ ] Custom record zones created for complex sync scenarios
- [ ] NSUbiquitousKeyValueStore observed for setting changes
- [ ] iCloud Drive file sync uses FileManager ubiquity APIs or NSMetadataQuery
- [ ] Sensitive data uses `encryptedValues` on CKRecord
- [ ] Exponential backoff implemented for retries
- [ ] CloudKit + iCloud capability enabled in Xcode capabilities

## Enriched Common Mistakes

- ❌ Not checking iCloud account status before operations — user may be signed out
- ❌ Using unique constraints with CloudKit — CloudKit doesn't support them, causes sync failures
- ❌ Not handling `.serverRecordChanged` errors — must resolve conflicts (usually last-writer-wins)
- ❌ Ignoring `CKSyncEngine` (iOS 17+) — it's now the recommended sync approach over manual zone fetches
- ❌ Not persisting sync state tokens — causes full re-sync on every launch

## Enriched Review Checklist

- [ ] iCloud account status checked before operations
- [ ] `CKSyncEngine` used for sync (iOS 17+) instead of manual fetch/push
- [ ] Conflict resolution strategy implemented for `.serverRecordChanged`
- [ ] Sync state tokens persisted between launches
- [ ] No unique constraints on CloudKit-synced SwiftData models
- [ ] Subscription set up for push-based change notifications

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

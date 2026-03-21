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
| `CKRecord` | CloudKit document | Key-value; includes metadata (ID, timestamps) |
| `CKQuery` | Fetch records by predicate | Filter, sort, limit |
| `CKQueryOperation` | Async query execution | Paginated results |
| `CKSubscription` | Remote notification trigger | Fires when records change |
| `CKRecordZone` | Custom zone | Enables complex sync scenarios |
| `CKRecord.Reference` | Foreign key to another record | Defines relationships |

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
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Not checking user authentication status | Check `CKContainer.default().accountStatus()` before queries |
| Ignoring CKError codes; generic error handling | Switch on error code; handle `.notAuthenticated`, `.networkFailure`, `.limitExceeded` separately |
| Querying without predicates; fetching entire database | Use NSPredicate to filter; implement pagination for large result sets |
| Not using relationships (CKRecord.Reference) for foreign keys | Use CKRecord.Reference for record-to-record relationships |
| Blocking UI on CloudKit operations | Always use `async/await`; never block main thread on network calls |

## Review Checklist

- [ ] User iCloud authentication checked before CloudKit access
- [ ] Appropriate database used (private/public/shared) for data sensitivity
- [ ] CKError handled with specific code switching (not generic catch-all)
- [ ] Queries include predicates; not open-ended
- [ ] Pagination implemented for large datasets
- [ ] Batch operations use `modifyRecords(saving:deleting:)` for efficiency
- [ ] Subscriptions cleaned up (removed) when no longer needed
- [ ] CKRecord.Reference used for relationships (not duplicate data)
- [ ] Record IDs persisted locally to avoid duplicate syncs
- [ ] Sync conflicts resolved (local vs. cloud version)
- [ ] Exponential backoff implemented for retries
- [ ] CloudKit entitlements enabled in Xcode capabilities

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

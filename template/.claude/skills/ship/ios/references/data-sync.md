<!-- ship-reference
id: ios-data-sync
kind: mixed
sources: iPhoneOS27.0.sdk SwiftData / CloudKit / Foundation .swiftinterface (Xcode 27.0 27A266a — every example type-checks via scripts/checks/ios.sh; the conflict merge and error policy run on the host via scripts/checks/ios_runtime); https://developer.apple.com/documentation/swiftdata ; https://developer.apple.com/documentation/cloudkit ; https://developer.apple.com/documentation/cloudkit/cksyncengine ; https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices ; https://developer.apple.com/documentation/foundation/nsubiquitouskeyvaluestore ; https://developer.apple.com/documentation/foundation/optimizing-your-app-s-data-for-icloud-backup (all checked 2026-09-24). Written for Ship from Apple's docs and the SDK; no third-party text. Ideas credited (MIT, verified by Ship's own experiments before use): twostraws/SwiftData-Agent-Skill@922d989 (temporary ids before save, @Query in views, explicit save).
reviewed: 2026-09-25
-->
# Data and sync — store it, migrate it, sync it between devices

**When to read:** a feature saves anything, "sync between devices", "back up", "works offline",
importing a file (CSV) into the app,
"share a list with someone", a schema change, a SwiftData/Core Data/CloudKit error. Tags: **Apple**
= documented platform behaviour or requirement; **Ship** = Ship's default (a product decision in
`DECISIONS.md` overrides it). Secrets never go here — Keychain (`commerce-identity.md` §5).

## 1. Choose the store

| What you keep | Use | Notes |
|---|---|---|
| The app's records (notes, workouts, items) | **SwiftData** (iOS 17+) | Ship default for new apps. Core Data if the app already has it — don't migrate for its own sake |
| Small preferences (sort order, last tab) | `@AppStorage` / `UserDefaults` | Not for records, not for secrets, not for anything over a few KB |
| A few preferences that should follow the person to other devices | `NSUbiquitousKeyValueStore` | Apple limits: 1 MB total, 1,024 keys; needs the iCloud key-value entitlement |
| Documents the person opens, names, and shares as files | Files + `DocumentGroup` (`Document` on 27) | See §6 |
| Large blobs (photos, audio) referenced by records | Files in Application Support; the record keeps the file name | Or `@Attribute(.externalStorage)` |
| Records synced across the person's own devices | SwiftData or Core Data **with CloudKit** (private database) | §4 |
| Records shared with other people (a shared list) | Core Data mirroring with a shared-scope store + `CKShare` (iOS 15), or CKSyncEngine on the shared database | §4–5 — SwiftData's CloudKit option is private-only |
| Private sync you must control (custom conflicts, sync status) | **CKSyncEngine** (iOS 17+) over your own store, one engine per database | §5 |
| Public data every user reads (catalog, leaderboard, announcements) | CloudKit **public** database: `CKQuery` + `CKQuerySubscription`, or Core Data mirroring with public scope | §5 — **Apple:** don't use CKSyncEngine for the public database |
| Data a widget or extension also reads | App Group container | §6 |

Decide sync **before** the first release: SwiftData's CloudKit rules (§4) constrain the schema.

## 2. SwiftData models and queries

- One `ModelContainer` for the app, created once in the `App` and injected with `.modelContainer`.
  Views read with `@Query` (it only works inside views); writes go through `modelContext`. The main
  context autosaves, but *when* isn't specified — call `try context.save()` whenever the result must
  be durable now (before handing off, before using an identifier, before backgrounding).
- Relationships: declare the inverse on one side, pick the delete rule deliberately (`.cascade`
  for owned children, `.nullify` for references). **Apple:** CloudKit sync forbids `.deny` (§4).
- Uniqueness: `@Attribute(.unique)` or `#Unique` (iOS 18) upserts on insert — **not allowed with
  CloudKit sync**; dedupe in code there. Indexes: `#Index` (iOS 18) for properties you filter or
  sort large sets on.
- `#Predicate` compiles to the store's query language. Only stored properties and supported
  operators translate; a predicate over a computed property or an unsupported function type-checks
  and then **fails at runtime** — cover every predicate with a test (§7).
- Page long lists with `FetchDescriptor` (`fetchLimit`, `fetchOffset`) instead of loading all.
- Background work (imports, bulk edits): a `@ModelActor` with its own context. Pass
  `PersistentIdentifier`s between actors, never model objects; re-fetch on the other side.
- **A `@ModelActor` doesn't bring its own background thread.** In Ship's host probe (27 SDK),
  created *or* called from the main actor (a button's `Task`, a `.task`), its insert-and-save loop
  ran on the main thread. **Create and call it inside a `@concurrent` function**
  (`importTripsInBackground` below) and await that from the UI.
- **Identifiers — what Ship's host test found** (27 SDK, on-disk store, `ios_runtime/swiftdata_ids`):
  - Read `persistentModelID` only **after a successful `save()`**. Before it, the ID is temporary
    (no store identifier); it doesn't update when the save happens and never resolves from another
    context.
  - A saved ID resolves in any context of the **same container** (`model(for:)`, or a fetch with
    `persistentModelID ==`).
  - To keep a reference **across launches** (restoration, a widget, a notification), store the ID
    `Codable`-encoded, or store your own key. An in-memory ID from an earlier container instance
    didn't match after the store was reopened; the encoded one did.
  - **Across devices** (CloudKit), IDs are per store: use your own stable key (a `UUID` property).
  - `model(for:)` with an ID that isn't in the store returns an object that traps when a property is
    read. Resolve untrusted IDs with a fetch and handle an empty result.

```swift
import SwiftData

@Model final class Trip {
    var name: String = ""
    var startDate: Date = Date.now
    @Relationship(deleteRule: .cascade, inverse: \Stop.trip) var stops: [Stop]? = []
    init(name: String, startDate: Date) { self.name = name; self.startDate = startDate }
}

@Model final class Stop {
    var title: String = ""
    var trip: Trip?
    init(title: String) { self.title = title }
}

@ModelActor
actor TripImporter {
    /// Inserts in saved batches (call via importTripsInBackground). Returns permanent ids, in order —
    /// ids read before `save()` are temporary and don't resolve anywhere else.
    func importTrips(_ rows: [(String, Date)], batchSize: Int = 500) throws -> [PersistentIdentifier] {
        var ids: [PersistentIdentifier] = []
        var batch: [Trip] = []
        for row in rows {
            try Task.checkCancellation()                       // stop between rows, not mid-save
            let trip = Trip(name: row.0, startDate: row.1)
            modelContext.insert(trip)
            batch.append(trip)
            if batch.count == batchSize {                      // keep memory flat on big imports
                try modelContext.save()
                ids += batch.map(\.persistentModelID)          // permanent now
                batch.removeAll(keepingCapacity: true)
            }
        }
        try modelContext.save()
        ids += batch.map(\.persistentModelID)
        return ids
    }
}

/// The UI entry point: the importer is created and used here, off the main actor, so the
/// insert/save loop doesn't run on the main thread (checked by ios_runtime/import_off_main).
@concurrent nonisolated func importTripsInBackground(_ rows: [(String, Date)],
                                                     into container: ModelContainer) async throws -> [PersistentIdentifier] {
    try await TripImporter(modelContainer: container).importTrips(rows)
}

struct UpcomingTrips: View {
    @Query private var trips: [Trip]

    init(from start: Date = .now) {        // #Predicate can't call Date.now — capture it first
        _trips = Query(filter: #Predicate<Trip> { $0.startDate >= start }, sort: \Trip.startDate)
    }

    var body: some View {
        List(trips) { trip in Text(trip.name) }
            .overlay { if trips.isEmpty { ContentUnavailableView("No trips yet", systemImage: "airplane") } }
    }
}
```

The models above follow the CloudKit rules (defaults on every property, optional relationship) so
turning sync on later doesn't need a migration. The cutoff date is fixed when the view is created
(`#Predicate` can't call `Date.now` itself — the compiler rejects it); re-create the view (e.g. on
scene activation) if "upcoming" must roll over at midnight.

## 3. Migrations

- Every shipped schema is a `VersionedSchema`; changes go through a `SchemaMigrationPlan`.
  Adding an optional property or one with a default, or renaming with `@Attribute(originalName:)`,
  is a *lightweight* stage. Splitting, merging, or deduplicating data is a *custom* stage with
  `willMigrate`/`didMigrate`.
- **Ship:** keep a store file from the previous release in the test bundle and open it with the new
  plan in a test (§7) — a migration never run against a real old store isn't verified.
- With CloudKit on, the CloudKit schema only grows: never delete or rename a synced field in a
  shipped version — older app versions on the person's other devices still write it.

```swift
import SwiftData

enum TripsV1: VersionedSchema {
    static let versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [TripsV1.Trip.self] }
    @Model final class Trip {
        var name: String = ""
        init(name: String) { self.name = name }
    }
}

enum TripsV2: VersionedSchema {
    static let versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [TripsV2.Trip.self] }
    @Model final class Trip {
        var name: String = ""
        var notes: String = ""            // new, with a default: lightweight
        init(name: String) { self.name = name }
    }
}

enum TripsMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] { [TripsV1.self, TripsV2.self] }
    static var stages: [MigrationStage] {
        [.lightweight(fromVersion: TripsV1.self, toVersion: TripsV2.self)]
    }
}

func makeContainer(at url: URL? = nil) throws -> ModelContainer {
    let config = url.map { ModelConfiguration(url: $0) } ?? ModelConfiguration()
    return try ModelContainer(for: Schema(versionedSchema: TripsV2.self),
                              migrationPlan: TripsMigrationPlan.self, configurations: config)
}
```

## 4. Sync the person's data with iCloud (SwiftData or Core Data + CloudKit)

**Prerequisites (Apple):** paid developer account; **iCloud** capability with **CloudKit** and a
container; **Background Modes › Remote notifications** (sync is push-driven); a signed-in iCloud
account. SwiftData uses the entitlements' container (`ModelConfiguration(cloudKitDatabase:)` to pick
one, `.none` to opt out). **Schema rules (Apple):** every property optional or defaulted, every
relationship optional, no unique constraints, no `.deny` delete rule — violations fail when the
container loads, so test with sync on.

**Behaviour to design for:**
- Sync is **eventual**: a change can take seconds to minutes to appear, and never appears while
  the device is offline. Don't show "Synced" claims you can't observe; show the local data.
- **Signed out, restricted, or iCloud Drive off:** the app keeps working on local data. Check
  `CKContainer.default().accountStatus()` if the UI needs to explain why nothing syncs, and listen
  for `.CKAccountChanged`.
- **Account change:** what happens to local mirrored data on sign-out or account switch depends on
  the store configuration — verify it on a device (§7) before promising users anything; never be
  the only copy of unsynced work without telling them.
- **Duplicates:** two devices creating "the same" record offline create two records. Dedupe on a
  stable business key (e.g. a date for a daily log) after import or on fetch.
- **Environments (Apple):** builds you run from Xcode use CloudKit **development**. **TestFlight and
  App Store builds always use production** — even when you uploaded the build from Xcode. So deploy
  the schema to **Production** in CloudKit Console **before the first TestFlight build** that uses
  it, and again after every schema change, before that change goes to TestFlight. A TestFlight
  build against an undeployed schema fails to save new record types and fields (silently, unless
  you surface the errors).

**Choosing the database (they aren't interchangeable):**
- **Private** (the person's own data, on their devices): SwiftData or Core Data mirroring;
  CKSyncEngine when you need custom conflicts or sync status. SwiftData's
  `ModelConfiguration.CloudKitDatabase` offers only `.automatic`, `.private(_:)`, and `.none`.
- **Shared** (records the owner shares with specific people through `CKShare`): Core Data mirroring
  with a second store whose `NSPersistentCloudKitContainerOptions.databaseScope` is `.shared`
  (iOS 15), or a CKSyncEngine on `sharedCloudDatabase`. The owner's copy stays in their private
  database; participants see it in their shared database.
- **Public** (everyone reads, the app or signed-in people write): `publicCloudDatabase` with
  `CKQuery` for reads and `CKQuerySubscription` for change pushes, or Core Data mirroring with
  `databaseScope = .public`, which doesn't sync the way private mirroring does — read Apple's
  public-database notes for mirroring before choosing it. Not CKSyncEngine.
- The SDK header comment on `databaseScope` says private/public only; Apple's docs and sharing
  sample use `.shared` — trust the docs; test sharing on two accounts.

## 5. Custom sync with CKSyncEngine (iOS 17+)

Use it when you own the local store (files, SQLite, SwiftData without mirroring) and need
custom conflict rules or visibility into what synced, for the **private** or **shared** database —
one engine per database (Apple's example runs one for each). **Apple:** don't use it to sync the
public database. The engine schedules fetches and sends,
handles push and retries; your job is **state, records, and conflicts**.

1. Persist `State.Serialization` from every `.stateUpdate` event; pass it back at launch. Losing it
   means a full re-fetch.
2. Record local edits as pending changes (`state.add(pendingRecordZoneChanges: [.saveRecord(id)])`).
   Build `CKRecord`s lazily in `nextRecordZoneChangeBatch`.
3. Apply `.fetchedRecordZoneChanges` to the local store (insert/update/delete), idempotently.
4. Handle every failure in `.sentRecordZoneChanges` (table below). A failed save you ignore is
   data that never syncs.
5. Handle `.accountChange`: sign-out → stop syncing and decide (product decision) whether local
   data stays; switch accounts → clear the previous person's data and the saved state.

| `CKError.Code` | Meaning | Do |
|---|---|---|
| `.serverRecordChanged` | Someone changed it first | Merge into `error.serverRecord`, save that (example) |
| `.zoneNotFound` | Zone doesn't exist yet | Queue `.saveZone`, then re-queue the record |
| `.userDeletedZone` | Person deleted the app's iCloud data | Don't silently re-upload — ask or reset local |
| `.unknownItem` | Record deleted on server | Re-create it or delete locally (product rule) |
| `.networkUnavailable`, `.networkFailure`, `.serviceUnavailable`, `.requestRateLimited`, `.zoneBusy` | Transient | The engine retries; wait `error.retryAfterSeconds` for your own ops |
| `.quotaExceeded` | iCloud is full | Tell the person; keep data local |
| `.notAuthenticated` | No account | Local only; explain if asked |
| `.changeTokenExpired` | Server can't diff from your token | Re-fetch from scratch |

```swift
import CloudKit

/// Conflict policy for a note: the server copy wins for fields this device didn't touch;
/// fields edited locally since the last sync win (last writer per field).
nonisolated func mergeLocalEdits(_ localFields: [String: String], editedKeys: Set<String>,
                     into server: CKRecord) -> CKRecord {
    for key in editedKeys {
        server[key] = localFields[key] as NSString?
    }
    return server   // carries the server change tag, so the next save succeeds
}

/// What to do with one failed save from `.sentRecordZoneChanges`.
enum SaveRetry: Equatable { case resend(CKRecord), createZoneThenResend, askPerson, dropLocal, wait }

nonisolated func retryPlan(for error: CKError, record: CKRecord,
               local: [String: String], edited: Set<String>) -> SaveRetry {
    switch error.code {
    case .serverRecordChanged:
        guard let server = error.serverRecord else { return .wait }
        return .resend(mergeLocalEdits(local, editedKeys: edited, into: server))
    case .zoneNotFound: return .createZoneThenResend
    case .userDeletedZone, .quotaExceeded: return .askPerson
    case .unknownItem: return .dropLocal
    default: return .wait     // transient: the engine reschedules
    }
}

actor NoteSync: CKSyncEngineDelegate {
    private var engine: CKSyncEngine?
    private let zone = CKRecordZone(zoneName: "Notes")
    var savedState: CKSyncEngine.State.Serialization?   // persist to disk in a real app

    func start(container: CKContainer = .default()) {
        let config = CKSyncEngine.Configuration(database: container.privateCloudDatabase,
                                                stateSerialization: savedState, delegate: self)
        engine = CKSyncEngine(config)
    }

    func noteChanged(id: String) {
        let recordID = CKRecord.ID(recordName: id, zoneID: zone.zoneID)
        engine?.state.add(pendingRecordZoneChanges: [.saveRecord(recordID)])
    }

    func handleEvent(_ event: CKSyncEngine.Event, syncEngine: CKSyncEngine) async {
        switch event {
        case .stateUpdate(let update):
            savedState = update.stateSerialization          // write to disk here
        case .fetchedRecordZoneChanges(let changes):
            _ = changes.modifications.map(\.record)          // upsert into the local store
            _ = changes.deletions.map(\.recordID)            // delete locally
        case .sentRecordZoneChanges(let sent):
            for failure in sent.failedRecordSaves {
                let plan = retryPlan(for: failure.error, record: failure.record,
                                     local: [:], edited: [])   // load both from your store
                if case .createZoneThenResend = plan {
                    syncEngine.state.add(pendingDatabaseChanges: [.saveZone(zone)])
                    syncEngine.state.add(pendingRecordZoneChanges: [.saveRecord(failure.record.recordID)])
                }
            }
        case .accountChange(let change):
            if case .switchAccounts = change.changeType { savedState = nil }  // and clear local data
        default:
            break
        }
    }

    func nextRecordZoneChangeBatch(_ context: CKSyncEngine.SendChangesContext,
                                   syncEngine: CKSyncEngine) async -> CKSyncEngine.RecordZoneChangeBatch? {
        let pending = syncEngine.state.pendingRecordZoneChanges.filter { context.options.scope.contains($0) }
        return await CKSyncEngine.RecordZoneChangeBatch(pendingChanges: pending) { id in
            let record = CKRecord(recordType: "Note", recordID: id)
            record["title"] = "…" as NSString                // fill from your store
            return record
        }
    }
}
```

**Sketch, labelled:** `NoteSync` shows where state, pending changes, fetches and failures go — no
local store, state not written to disk, never run against CloudKit. The two functions above it are
complete and host-tested (`ios_runtime/cloudkit_merge`).

## 6. Files, small synced settings, and shared containers

- **Where files go (Apple):** user-visible documents → `Documents` (backed up; visible in Files if
  you opt in with `UIFileSharingEnabled`/`LSSupportsOpeningDocumentsInPlace`); app data →
  Application Support (backed up); re-creatable data → `Caches` (may be purged); temp → `tmp`.
  Large re-downloadable files: set `isExcludedFromBackup` on the URL's resource values.
- **Data protection:** files get `completeUntilFirstUserAuthentication` by default; use
  `.completeFileProtection` for sensitive files that background tasks don't need while locked.
- **Files the person picks** (`.fileImporter`, document picker) are security-scoped: call
  `startAccessingSecurityScopedResource()` and balance it with `stop…` (use `defer`) — the CSV
  example below does both. To reopen later, store a bookmark (`bookmarkData`) and resolve it,
  handling `isStale`.
- **Key-value sync:** `NSUbiquitousKeyValueStore.default` — call `synchronize()` at launch, observe
  `didChangeExternallyNotification`, keep a local fallback value. Apple limits: 1 MB, 1,024 keys.
- **Widgets and extensions:** share an App Group container
  (`FileManager.containerURL(forSecurityApplicationGroupIdentifier:)`,
  `ModelConfiguration(groupContainer: .identifier(…))`, `UserDefaults(suiteName:)`). After the app
  writes, call `WidgetCenter.shared.reloadTimelines(ofKind:)` (`system-integration.md` §3).
  Changes made by an extension reach the app's context through SwiftData history
  (`fetchHistory`, iOS 18).

**Import a CSV (or any big file) without freezing the screen:**
1. Pick with `.fileImporter(allowedContentTypes: [.commaSeparatedText])`; the URL is security-scoped.
2. **Parse off the main actor:** a `@concurrent` function that streams the file
   (`url.resourceBytes`) — a synchronous parser called from `.task` or a button freezes the UI
   (`swift-practice.md` §1). Check cancellation between lines.
3. **Insert off the main actor** in saved batches: `importTripsInBackground` (§2) creates and calls
   `TripImporter` inside a `@concurrent` function — constructing the importer in the button's task
   would run the inserts on the main thread. It returns permanent ids.
4. Show progress and a Cancel button that cancels the task. On cancel, whole batches already saved
   stay: a product decision is either "keep what was imported and say how many" or "tag rows with
   an import id and delete them on cancel".
5. Bad rows (missing name, bad date, too few fields): skip them and report their **physical** line
   numbers, blank lines counted ("skipped 3 rows: lines 12, 40, 41") — `url.lines` drops empty lines,
   so its count drifts. An unreadable file is an error message, not an empty list.
6. **Multi-line cells are rejected, not guessed.** One physical line = one record here: a quoted
   cell that doesn't close on its line stops the import with the line number *before anything is
   saved* (splitting it would import a fragment as a trip). Supporting them needs a record-aware parser.

```swift
// continues: #0 — uses Trip and TripImporter from §2
import SwiftUI
import SwiftData
import UniformTypeIdentifiers

/// Fields of one CSV line (RFC 4180: quoted fields, commas inside quotes, doubled quotes).
/// nil when a quoted field is still open at the end of the line — a multi-line cell or a stray
/// quote. This parser doesn't support multi-line cells; callers must reject the file.
nonisolated func csvFields(_ line: String) -> [String]? {
    var fields: [String] = [], field = "", quoted = false
    var chars = line.makeIterator()
    while let c = chars.next() {
        switch (c, quoted) {
        case ("\"", true):
            if let next = chars.next() {
                if next == "\"" { field.append("\"") } else { quoted = false; if next == "," { fields.append(field); field = "" } else { field.append(next) } }
            } else { quoted = false }
        case ("\"", false) where field.isEmpty: quoted = true
        case (",", false): fields.append(field); field = ""
        default: field.append(c)
        }
    }
    if quoted { return nil }                                   // opened, never closed on this line
    fields.append(field)
    return fields
}

enum CSVImportError: Error, Equatable {
    case unclosedQuote(line: Int)
    var message: String {
        switch self { case .unclosedQuote(let line): "Line \(line) has a quoted cell that doesn't close on that line (a line break inside a cell isn't supported). Nothing was imported." }
    }
}

struct ParsedTrips: Sendable { var rows: [(String, Date)] = []; var skippedLines: [Int] = [] }   // 1-based physical lines

/// Streams and parses off the main actor. Throws CancellationError if cancelled, and
/// CSVImportError before returning any rows if the file uses multi-line cells.
@concurrent nonisolated func parseTripsCSV(at url: URL) async throws -> ParsedTrips {
    let scoped = url.startAccessingSecurityScopedResource()
    defer { if scoped { url.stopAccessingSecurityScopedResource() } }
    var result = ParsedTrips(), lineNumber = 0, bytes: [UInt8] = [], afterCR = false
    func record(_ line: String) throws {
        try Task.checkCancellation()
        lineNumber += 1
        if lineNumber == 1 || line.trimmingCharacters(in: .whitespaces).isEmpty { return }   // header, blank
        guard let fields = csvFields(line) else { throw CSVImportError.unclosedQuote(line: lineNumber) }
        guard fields.count >= 2, !fields[0].isEmpty,
              let start = try? Date(fields[1], strategy: .iso8601.year().month().day()) else {
            result.skippedLines.append(lineNumber); return
        }
        result.rows.append((fields[0], start))
    }
    // Physical lines (LF, CRLF, or CR each end one), so reported numbers match the file.
    for try await byte in url.resourceBytes {
        defer { afterCR = byte == 13 }
        if byte == 10 && afterCR { continue }                  // the LF of a CRLF
        guard byte == 10 || byte == 13 else { bytes.append(byte); continue }
        try record(String(decoding: bytes, as: UTF8.self))
        bytes.removeAll(keepingCapacity: true)
    }
    if !bytes.isEmpty { try record(String(decoding: bytes, as: UTF8.self)) }   // no final line break
    return result
}

struct ImportTripsButton: View {
    @Environment(\.modelContext) private var context
    @State private var picking = false
    @State private var job: Task<Void, Never>?
    @State private var message: String?

    var body: some View {
        VStack(alignment: .leading, spacing: Theme.Spacing.sm) {
            if job != nil {
                HStack { ProgressView(); Button("Cancel") { job?.cancel() } }
            } else {
                Button("Import trips from CSV") { picking = true }
            }
            if let message { Text(message).font(Theme.Typography.caption) }
        }
        .fileImporter(isPresented: $picking, allowedContentTypes: [.commaSeparatedText]) { result in
            guard case .success(let url) = result else { return }
            let container = context.container
            job = Task {
                defer { job = nil }
                do {
                    let parsed = try await parseTripsCSV(at: url)
                    let ids = try await importTripsInBackground(parsed.rows, into: container)   // off main
                    let skipped = parsed.skippedLines
                    message = "Imported \(ids.count) trips" + (skipped.isEmpty ? "." :
                        ", skipped \(skipped.count) rows: line\(skipped.count == 1 ? "" : "s") \(skipped.map(String.init).joined(separator: ", ")).")
                } catch is CancellationError {
                    message = "Import cancelled."
                } catch let error as CSVImportError {
                    message = error.message
                } catch {
                    message = "Couldn't read that file."
                }
            }
        }
    }
}
```

Ship's host tests run this code: `ios_runtime/csv_import` (quoting, escaped quotes, multi-line and
unclosed quotes rejected, physical line numbers under LF/CRLF/CR with blank lines, 20,000 rows,
cancellation) and `ios_runtime/import_off_main` (the button's pattern keeps the main actor free).

## 7. Verify

| What | How | Evidence level |
|---|---|---|
| Models, predicates, queries | Swift Testing with `ModelConfiguration(isStoredInMemoryOnly: true)`; one test per `#Predicate` | Runs in CI (simulator or Mac) |
| Migration | Test opens a store file from the previous release with the new plan and reads it back | Runs in CI — only with a real old store checked in |
| Background import | Import 10k rows on a `@ModelActor`; the UI keeps scrolling (Time Profiler shows no main-actor work) | Simulator/device |
| CloudKit schema | App launches with sync on and no load error; schema deployed to Production before release | Device + CloudKit Console |
| Two-device sync | Same iCloud account on two devices: create, edit, delete on each; offline edit, then reconnect | **Manual, physical devices** — simulators don't prove push-driven sync timing |
| Conflicts | Edit the same record on both devices while one is offline; the merge rule holds | Manual, two devices; merge logic also unit-tested |
| Account changes | Sign out, sign in, switch account; record what happens to local data | **Manual, device** |
| Quota / iCloud off | Turn iCloud off for the app in Settings; app still works locally | Manual, device |

Apple: [SwiftData](https://developer.apple.com/documentation/swiftdata) ·
[Syncing model data](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices) ·
[CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine) ·
[CloudKit Console](https://icloud.developer.apple.com) · Xcode 27: `AdditionalDocumentation/SwiftData-Class-Inheritance.md`.

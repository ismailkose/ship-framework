<!-- ship-reference
id: ios-system-integration
kind: mixed
sources: iPhoneOS27.0.sdk AppIntents / WidgetKit / TipKit / GroupActivities / CoreSpotlight / SwiftUI interfaces (Xcode 27.0 27A266a — examples type-check via scripts/checks/ios.sh; the deep-link parser runs on the host via scripts/checks/ios_runtime); https://developer.apple.com/documentation/appintents ; https://developer.apple.com/documentation/widgetkit ; https://developer.apple.com/documentation/tipkit ; https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app ; https://developer.apple.com/documentation/appclip ; https://developer.apple.com/documentation/groupactivities ; https://developer.apple.com/documentation/groupactivities/drawing-content-in-a-group-session (all checked 2026-09-24); xcode-bundled-skills@27A266a app-intents-specialist / app-intents-whats-new-27 (pointed to). Written for Ship from Apple's docs and the SDK; no third-party text.
reviewed: 2026-09-25
-->
# Beyond the app — Siri, Shortcuts, widgets, controls, links, tips

**When to read:** "add a widget", "a Control Center button", "make it work with Siri / Shortcuts /
Spotlight", "open this screen from a link", universal links, "teach people this feature", showing
a web page, OAuth sign-in, App Clips, SharePlay. One principle across all of them — **Ship:** expose the app's few core verbs and
nouns once, as App Intents and entities, and let every surface reuse them.

## 1. App Intents — the app's verbs and nouns

- An `AppIntent` is one action ("Log water", "Start focus session") with typed `@Parameter`s. An
  `AppEntity` is a noun ("Trip", "Playlist") with an `EntityQuery` that finds it by id and suggests
  some. The same intent powers Siri, Shortcuts, Spotlight, widgets, controls, and Apple
  Intelligence actions.
- **Ship:** start with 2–5 intents for the actions people repeat; don't mirror every screen.
- `AppShortcutsProvider` makes intents available with zero setup; every phrase must include
  `\(.applicationName)`. Keep phrases short and natural.
- An intent that opens the app sets `static let openAppWhenRun = true` (or returns `.result()` after
  navigating through your router); one that works in the background must not touch UI.
- Spotlight: entities conforming to `IndexedEntity` (iOS 18) can be indexed with
  `CSSearchableIndex.default().indexAppEntities(_:)`; delete them from the index when deleted in the app.
- **The intent does the real work, through the same store the app uses** — often in another
  process (Shortcuts, Siri, a widget button): open the shared store (an App Group SwiftData
  container, `data-sync.md` §6), find the record by a **durable key** (your own UUID — not a
  `PersistentIdentifier`, `data-sync.md` §2), change it, `save()`, reload affected widgets, and
  only **then** return a success dialog.
- **Report failure truthfully:** a deleted record, a validation problem, or a failed save throws an
  error with a readable message (`CustomLocalizedStringResourceConvertible`); Siri and Shortcuts show
  it. Never return "Added…" when nothing was saved.
- Share services with intents via `AppDependencyManager.shared.add(dependency:)` at launch and
  `@Dependency` / `@AppDependency` in the intent and query — one container for the app and its
  intents.
- **Details and iOS 26–27 additions:** Xcode 27 `app-intents-specialist` / `app-intents-whats-new-27`.

```swift
import AppIntents
import SwiftData
import WidgetKit

@Model final class SharedTrip {
    var uid: UUID = UUID()                                   // durable key for intents, widgets, links
    var name: String = ""
    var stops: [String] = []
    init(name: String) { self.name = name }
}

enum TripsStore {
    /// The app, its widget, and its intents open the same App Group store.
    static func container(inMemory: Bool = false) throws -> ModelContainer {
        let config = inMemory ? ModelConfiguration(isStoredInMemoryOnly: true)
                              : ModelConfiguration(groupContainer: .identifier("group.com.example.trips"))
        return try ModelContainer(for: SharedTrip.self, configurations: config)
    }
}

struct TripEntity: AppEntity {
    static let typeDisplayRepresentation: TypeDisplayRepresentation = "Trip"
    static let defaultQuery = TripQuery()
    let id: UUID
    let name: String
    var displayRepresentation: DisplayRepresentation { DisplayRepresentation(title: "\(name)") }
}

struct TripQuery: EntityQuery {
    @AppDependency var container: ModelContainer
    func entities(for identifiers: [UUID]) async throws -> [TripEntity] {
        let context = ModelContext(container)
        let trips = try context.fetch(FetchDescriptor<SharedTrip>(predicate: #Predicate { identifiers.contains($0.uid) }))
        return trips.map { TripEntity(id: $0.uid, name: $0.name) }  // deleted ids are simply absent
    }
    func suggestedEntities() async throws -> [TripEntity] {
        var recent = FetchDescriptor<SharedTrip>(sortBy: [SortDescriptor(\.name)])
        recent.fetchLimit = 10
        return try ModelContext(container).fetch(recent).map { TripEntity(id: $0.uid, name: $0.name) }
    }
}

enum TripIntentError: Error, CustomLocalizedStringResourceConvertible {
    case tripGone, emptyPlace
    var localizedStringResource: LocalizedStringResource {
        self == .tripGone ? "That trip no longer exists." : "Say which place to add."
    }
}

struct AddStopIntent: AppIntent {
    static let title: LocalizedStringResource = "Add Stop"
    @Parameter(title: "Trip") var trip: TripEntity
    @Parameter(title: "Place") var place: String
    @Dependency var container: ModelContainer

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let name = place.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !name.isEmpty else { throw TripIntentError.emptyPlace }
        let context = ModelContext(container)
        let uid = trip.id
        guard let stored = try context.fetch(FetchDescriptor<SharedTrip>(predicate: #Predicate { $0.uid == uid })).first
        else { throw TripIntentError.tripGone }
        stored.stops.append(name)
        try context.save()                                       // a failed save throws — no success dialog
        WidgetCenter.shared.reloadTimelines(ofKind: "NextTrip")
        return .result(dialog: "Added \(name) to \(stored.name).")
    }
}

struct TripShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(intent: AddStopIntent(), phrases: ["Add a stop in \(.applicationName)"],
                    shortTitle: "Add Stop", systemImageName: "mappin.and.ellipse")
    }
}
```

Register the container once at launch — `AppDependencyManager.shared.add(dependency: try!
TripsStore.container())` in the `App`'s `init` (use a real error path in production). In unit
tests, set the intent's `@Dependency` property yourself — it only resolves by itself inside the
system's perform flow and traps otherwise. Ship's host
test runs `AddStopIntent.perform()` against an in-memory store: it saves, and it throws — without a
success dialog — for a deleted trip and an empty place (`ios_runtime/app_intent_add_stop`).

## 2. Deep links and universal links

- **Every** external entry (widget tap, notification, universal link, Spotlight, Handoff) resolves
  to one `Route` value (`swiftui-ship.md` §4), parsed in one place and tested. Unknown or stale
  links land on a sensible screen, never a crash or a blank view.
- **Universal links** (Apple): Associated Domains `applinks:<domain>` + an
  `apple-app-site-association` file served over HTTPS without redirects; handle in `.onOpenURL`
  (SwiftUI routes both custom schemes and universal links there). Links in your own app and in
  Safari's address bar don't open the app — test from Notes or Messages.
- Custom URL schemes (`myapp://`) are for your own widgets and extensions; anyone can claim a
  scheme, so never trust one with sensitive actions.

```swift
enum AppRoute: Equatable { case trip(UUID), newTrip, settings }

/// One parser for every entry point: widgets (myapp://trip/<id>) and universal links (https://example.com/trip/<id>).
nonisolated func route(from url: URL) -> AppRoute? {
    let parts = (url.scheme == "https" ? url.pathComponents : [url.host ?? ""] + url.pathComponents)
        .filter { $0 != "/" && !$0.isEmpty }
    switch parts.first {
    case "trip":
        if parts.count == 2, let id = UUID(uuidString: parts[1]) { return .trip(id) }
        return parts.count == 1 ? .newTrip : nil
    case "settings": return .settings
    default: return nil
    }
}
```

## 3. Widgets and controls

- **Content:** glanceable, one purpose per widget, useful without opening the app. Every tap goes
  to the exact place (`widgetURL` / `Link` → §2). Family sizes differ in content, not just scale.
- **Data:** the widget is a separate process. It reads from an App Group container
  (`data-sync.md` §6) — e.g. `ModelContext(try TripsStore.container())` in `getTimeline` with a
  small `FetchDescriptor` — never from the network on every render. Empty or unreadable store →
  a placeholder entry, not a crash. After the app (or an intent, §1) changes data, call
  `WidgetCenter.shared.reloadTimelines(ofKind:)`.
- **Timelines:** give entries for the future you know (next events); the system budgets reloads
  (Apple: typically 40–70 a day for a frequently viewed widget) — `.atEnd`/`.after(date)` are requests,
  not guarantees. Use `Text(date, style: .timer/.relative)` for live clocks instead of reloading.
- **Configuration:** `AppIntentConfiguration` (iOS 17) with a `WidgetConfigurationIntent` lets the
  person pick the trip/playlist the widget shows.
- **Interactive** (iOS 17): `Button(intent:)` / `Toggle(isOn:intent:)` run an App Intent without
  opening the app; the widget reloads afterwards.
- **Controls** (iOS 18): `ControlWidget` for Control Center, Lock Screen, and the Action button —
  a button or toggle backed by an App Intent.
- Rendering modes: support `.accented` and `.vibrant` (Lock Screen, tinted Home Screen) — check
  `@Environment(\.widgetRenderingMode)`; use `.widgetAccentable()` on the parts to tint.
- **Test:** Xcode widget previews / the widget scheme on the simulator for layout in every family
  and mode; reload budgets and real refresh timing only on a device over time.

```swift
import WidgetKit

struct NextTripEntry: TimelineEntry { let date: Date; let title: String; let tripID: UUID? }

struct NextTripProvider: TimelineProvider {
    func placeholder(in context: Context) -> NextTripEntry { .init(date: .now, title: "Weekend in Lisbon", tripID: nil) }
    func getSnapshot(in context: Context, completion: @escaping (NextTripEntry) -> Void) { completion(placeholder(in: context)) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<NextTripEntry>) -> Void) {
        let entry = NextTripEntry(date: .now, title: "Weekend in Lisbon", tripID: nil)  // read the App Group store here
        completion(Timeline(entries: [entry], policy: .after(.now.addingTimeInterval(3600))))
    }
}

struct NextTripWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "NextTrip", provider: NextTripProvider()) { entry in
            VStack(alignment: .leading) {
                Text("Next trip").font(.caption).foregroundStyle(.secondary)
                Text(entry.title).font(.headline).widgetAccentable()
            }
            .containerBackground(.fill.tertiary, for: .widget)
            .widgetURL(entry.tripID.map { URL(string: "myapp://trip/\($0.uuidString)")! })
        }
        .configurationDisplayName("Next Trip")
        .supportedFamilies([.systemSmall, .accessoryRectangular])
    }
}
```

(Widget code uses system type styles because widgets don't load the app's `Theme.swift` unless the
generated file is added to the extension target — **Ship:** add it, then use `Theme.*` there too.)

## 4. TipKit — teaching a feature

- **Ship:** use TipKit instead of hand-made coach marks. Call `try Tips.configure()` once at launch.
- A tip explains one thing, in context, next to the control (`.popoverTip(tip)` or inline
  `TipView`). Rules decide eligibility: a `@Parameter` (e.g. "has created a trip") or an
  `Event` count ("opened the map 3 times"). Invalidate when the person uses the feature
  (`tip.invalidate(reason: .actionPerformed)`).
- Frequency: `.displayFrequency(.daily)` or similar so tips don't stack up.
- **Test:** `Tips.showAllTipsForTesting()` / `Tips.resetDatastore()` in debug builds only.

```swift
import TipKit

struct ReorderTip: Tip {
    var title: Text { Text("Reorder stops") }
    var message: Text? { Text("Touch and hold a stop, then drag it.") }
}

struct StopsHeader: View {
    private let tip = ReorderTip()
    var body: some View {
        Text("Stops")
            .popoverTip(tip)
            .task { try? Tips.configure([.displayFrequency(.daily)]) }   // normally once, in the App
    }
}
```

## 5. Sharing and handoff between apps

- `ShareLink` for sharing items; make your own types `Transferable` (with a `ProxyRepresentation`
  for plain text/URL fallbacks) so they share and drag everywhere.
- Accept incoming content with a **Share Extension** (a separate target, App Group for the data)
  or `.dropDestination(for:)` for drag and drop on iPad.
- Handoff / continuing on another device: `.userActivity(_:element:)` + `.onContinueUserActivity`.

## 6. Web content in the app

- **Ship:** show your own help pages or a web-only flow with SwiftUI `WebView` + `WebPage` (iOS 26,
  `import WebKit`); below 26 wrap `WKWebView`. Links to other sites open in Safari (or
  `SFSafariViewController`) — the app isn't a browser (App Review 4.2 also rejects apps that are
  mostly a wrapped website).
- **Sign-in with a third-party OAuth provider:** `ASWebAuthenticationSession`, never an embedded web
  view (providers block it, and it hides the real URL from the person).
- `WebPage` is observable (`title`, `isLoading`, `estimatedProgress`, `url`); drive a progress bar
  and the navigation title from it. Decide navigation with a `WebPage.NavigationDeciding` type.
- JavaScript: `callJavaScript(_:arguments:)` returns `Any?` — cast defensively; treat anything the
  page sends back as untrusted input. Local HTML: load from the bundle with a file URL.

```swift
import WebKit

@available(iOS 26.0, *)
struct KeepOnOurSite: WebPage.NavigationDeciding {
    let host: String
    @MainActor
    func decidePolicy(for action: WebPage.NavigationAction,
                      preferences: inout WebPage.NavigationPreferences) async -> WKNavigationActionPolicy {
        guard let url = action.request.url, url.host() != host else { return .allow }
        await UIApplication.shared.open(url)          // other sites open in Safari
        return .cancel
    }
}

@available(iOS 26.0, *)
struct HelpCenter: View {
    @State private var page = WebPage(navigationDecider: KeepOnOurSite(host: "help.example.com"))

    var body: some View {
        WebView(page)
            .navigationTitle(page.title)
            .overlay(alignment: .top) { if page.isLoading { ProgressView(value: page.estimatedProgress) } }
            .onAppear { page.load(URLRequest(url: URL(string: "https://help.example.com")!)) }
    }
}
```

## 7. App Clips and SharePlay

- **App Clip:** a small slice of the app for one task (pay for parking, order at a table), launched
  from a link, NFC tag, QR, or App Clip Code. Apple's size limit: uncompressed binary ≤ 15 MB for
  iOS 16; up to 100 MB on iOS 17+ only under extra conditions (e.g. digital invocations only).
  Needs its own target, associated domain `appclips:`, and an App Clip experience in App Store
  Connect. No account wall; offer Sign in with Apple and hand data to the full app via an App
  Group. **Test:** the `_XCAppClipURL` environment variable locally; Local Experiences (Settings ›
  Developer) on a device.
- **SharePlay (Group Activities):** worth it only when doing the thing together is the point
  (watch, play, draw, plan together). Needs the Group Activities capability; FaceTime (or
  Messages) carries the session.
  - **Lifecycle:** define a `GroupActivity` (identifier + metadata); start with
    `activity.activate()` or a share button during a FaceTime call; **every** device — including
    the one that started it — receives the session from `YourActivity.sessions()`. Configure it,
    then `join()`. Watch `state`: `.invalidated` (the call ended, the person left) → tear down,
    back to solo mode. `leave()` exits for you; `end()` ends it for everyone.
  - **Messages:** `GroupSessionMessenger` (`.reliable` for state, `.unreliable` for fast,
    droppable updates like cursors). Keep messages small; large items (images, PDFs) go through
    `GroupSessionJournal` (iOS 17).
  - **State:** each change is an operation with an id and author, applied idempotently (duplicates
    and late messages change nothing); local edits apply at once and are sent. Don't let the
    session be the only copy — save to your store as usual.
  - **Joining late:** devices see membership at different times (a leave and a join can arrive as
    one update), so don't elect a sender from your own view of who's new. The newcomer **asks**; the
    lowest-id participant that holds the canvas *and is still here* answers; the newcomer merges and
    sends back what the group lacked, re-asking on membership changes and on a timer until answered.
    (Apple's drawing sample has every device send catch-up; one answer only saves traffic.)
  - **Test:** two devices (two Apple Accounts) in a FaceTime call; join late; leave and rejoin;
    end the call mid-stroke. The simulator can't prove SharePlay.

```swift
import GroupActivities
import Foundation

struct DrawTogether: GroupActivity {
    static let activityIdentifier = "com.example.trips.draw-together"
    var metadata: GroupActivityMetadata { var m = GroupActivityMetadata(); m.title = "Draw together"; m.type = .generic; return m }
}

/// One drawing operation: a stroke (e.g. a one-stroke PKDrawing's data) on a page, by an author.
nonisolated struct StrokeOp: Codable, Hashable, Sendable { let id: UUID; let page: Int; let author: UUID; let order: Date; let drawing: Data }

/// hello = "I just joined, send me the canvas"; ready = "caught up" + strokes the group lacked.
nonisolated enum CanvasMessage: Codable, Equatable, Sendable { case stroke(StrokeOp), hello, snapshot([StrokeOp], holders: Set<UUID>), ready([StrokeOp]) }

/// Pure, idempotent reconciliation — the part that decides whether two screens agree.
nonisolated struct CanvasLog: Sendable {
    private(set) var ops: [UUID: StrokeOp] = [:]
    /// false when the op was already known (duplicate or echo).
    @discardableResult mutating func apply(_ op: StrokeOp) -> Bool { ops.updateValue(op, forKey: op.id) == nil }
    /// Merges a snapshot and returns our strokes it didn't have.
    @discardableResult mutating func merge(_ snapshot: [StrokeOp]) -> [StrokeOp] {
        let theirs = Set(snapshot.map(\.id))
        snapshot.forEach { apply($0) }
        return ops.values.filter { !theirs.contains($0.id) }
    }
    /// Deterministic order on every device (time, then id), per page.
    func strokes(page: Int) -> [StrokeOp] {
        ops.values.filter { $0.page == page }.sorted { ($0.order, $0.id.uuidString) < ($1.order, $1.id.uuidString) }
    }
}

/// Who holds the canvas and who answers a newcomer — pure, so every membership change is testable.
nonisolated struct CanvasSync: Sendable {
    struct Outgoing: Equatable, Sendable { var message: CanvasMessage; var to: UUID? }   // nil = everyone else
    let me: UUID; private(set) var log: CanvasLog
    private(set) var holding = false
    private var joined = false                       // seen ourselves in activeParticipants
    private var active: Set<UUID> = [], holders: Set<UUID> = [], joiners: Set<UUID> = []   // joiners: asked, not caught up

    init(me: UUID, log: CanvasLog) { self.me = me; self.log = log }

    mutating func draw(_ op: StrokeOp) -> [Outgoing] { log.apply(op); return [Outgoing(message: .stroke(op), to: nil)] }

    /// Every activeParticipants value. Before join() it doesn't contain you — ignored.
    mutating func membershipChanged(_ ids: Set<UUID>) -> [Outgoing] {
        guard ids.contains(me), ids != active else { return [] }
        active = ids
        holders.formIntersection(ids); joiners.formIntersection(ids)   // the departed can't answer
        joined = true
        if holding { return [] }
        return seedIfOnlyJoinersRemain() ?? [Outgoing(message: .hello, to: nil)]
    }

    /// Every few seconds: ask again until caught up (a lost reply, or the holder left).
    func retry() -> [Outgoing] { joined && !holding ? [Outgoing(message: .hello, to: nil)] : [] }

    mutating func received(_ message: CanvasMessage, from sender: UUID) -> [Outgoing] {
        switch message {
        case .stroke(let op): log.apply(op); return []
        case .hello:
            holders.remove(sender); joiners.insert(sender)
            return holding ? answer(sender) : seedIfOnlyJoinersRemain() ?? []
        case .snapshot(let ops, let theirHolders):
            let missing = log.merge(ops)
            holders.formUnion(theirHolders.union([sender]))
            guard !holding else { return [] }
            holding = true; holders.insert(me)
            return [Outgoing(message: .ready(missing), to: nil)]
        case .ready(let ops): log.merge(ops); joiners.remove(sender); holders.insert(sender); return []
        }
    }

    private func answer(_ joiner: UUID) -> [Outgoing] {
        guard holders.intersection(active).min(by: { $0.uuidString < $1.uuidString }) == me else { return [] }
        return [Outgoing(message: .snapshot(Array(log.ops.values), holders: holders), to: joiner)]
    }

    /// Alone, or everyone else here is also still joining (they arrived together): lowest id holds.
    private mutating func seedIfOnlyJoinersRemain() -> [Outgoing]? {
        guard joined, active.subtracting([me]).isSubset(of: joiners),
              active.min(by: { $0.uuidString < $1.uuidString }) == me else { return nil }
        holding = true; holders.insert(me)
        return joiners.intersection(active).flatMap { answer($0) }
    }
}

@MainActor @Observable
final class SharedCanvas {
    private(set) var log = CanvasLog()
    private(set) var isShared = false
    private var session: GroupSession<DrawTogether>?
    private var messenger: GroupSessionMessenger?
    private var sync: CanvasSync?
    private var people: [UUID: Participant] = [:]
    private var tasks: [Task<Void, Never>] = []

    /// Start once (e.g. from the app's root .task); handles every session for the app's lifetime.
    func observeSessions() async { for await session in DrawTogether.sessions() { configure(session) } }

    func draw(_ op: StrokeOp) { if sync == nil { log.apply(op) } else { step { $0.draw(op) } } }   // local first, then share

    func leave() { session?.leave(); tearDown() }

    private func step(_ event: (inout CanvasSync) -> [CanvasSync.Outgoing]) {
        guard var current = sync, let messenger, let session else { return }
        let outgoing = event(&current)
        sync = current; log = current.log
        let others = session.activeParticipants.subtracting([session.localParticipant])
        for item in outgoing {
            let to = item.to.flatMap { people[$0] }.map { Set([$0]) } ?? others
            guard !to.isEmpty else { continue }
            Task { try? await messenger.send(item.message, to: .only(to)) }
        }
    }

    private func configure(_ session: GroupSession<DrawTogether>) {
        tearDown()
        let messenger = GroupSessionMessenger(session: session, deliveryMode: .reliable)
        self.session = session; self.messenger = messenger
        sync = CanvasSync(me: session.localParticipant.id, log: log)
        tasks.append(Task { [weak self] in
            for await (message, context) in messenger.messages(of: CanvasMessage.self) {
                self?.step { $0.received(message, from: context.source.id) }
            }
        })
        tasks.append(Task { [weak self] in
            for await state in session.$state.values {
                if case .invalidated = state { self?.tearDown() }  // call ended or we left
            }
        })
        tasks.append(Task { [weak self] in
            for await participants in session.$activeParticipants.values {
                self?.people = Dictionary(uniqueKeysWithValues: participants.map { ($0.id, $0) })
                self?.step { $0.membershipChanged(Set(participants.map(\.id))) }
            }
        })
        tasks.append(Task { [weak self] in                      // re-ask until caught up
            while !Task.isCancelled { try? await Task.sleep(for: .seconds(3)); self?.step { $0.retry() } }
        })
        session.join()
        isShared = true
    }

    private func tearDown() {
        tasks.forEach { $0.cancel() }; tasks.removeAll()
        session = nil; messenger = nil; sync = nil; people = [:]
        isShared = false                                        // keep `log`: the drawing stays with the person
    }
}
```

  **Not shown:** rendering `log` into `PKCanvasView`s (`media.md` §7), undo across participants,
  and journal attachments. `CanvasLog` and `CanvasSync` run in Ship's host tests
  (`ios_runtime/shareplay_reconcile`: first join, late join, a leave and a join in one update,
  arrivals together, the answering holder leaving, duplicates — over a simulated message bus); the
  `SharedCanvas` adapter compiles and is **not run** — it needs two devices in a FaceTime call.

## 8. Verify

| What | How | Level |
|---|---|---|
| Intents run and return the right dialog | Shortcuts app on the simulator; unit-test `perform()`'s model calls | Simulator + CI |
| Siri phrases | Speak them on a device; App Shortcuts appear in Spotlight | **Device** |
| Deep links | Unit-test the parser with every URL shape (host test); `xcrun simctl openurl booted myapp://trip/<id>` | Host + simulator |
| Universal links | AASA served; tap a link in Notes on a device | **Device + server** |
| Widget families, render modes, tap targets | Widget previews, simulator, Lock Screen | Simulator |
| Widget refresh after app edits | Edit in app → widget updates | Simulator; budgets on a device over time |
| Tips show once and disappear after the action | Debug testing APIs, then a clean install | Simulator |
| Web view: external links leave, progress and title update | Simulator with the real pages | Simulator |
| Intent saves / throws truthfully | Host test (`ios_runtime/app_intent_add_stop`); then Shortcuts on a simulator | CI + simulator |
| SharePlay reconciliation | Host test (`ios_runtime/shareplay_reconcile`) | CI |
| SharePlay session: join late, leave/rejoin, end mid-stroke | Two devices, two accounts, FaceTime | **Manual** |

Apple: [App Intents](https://developer.apple.com/documentation/appintents) ·
[WidgetKit](https://developer.apple.com/documentation/widgetkit) ·
[TipKit](https://developer.apple.com/documentation/tipkit) ·
[Universal links](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app) ·
[App Clips](https://developer.apple.com/documentation/appclip) ·
[Group Activities](https://developer.apple.com/documentation/groupactivities) ·
Xcode 27: `app-intents-specialist`, `app-intents-whats-new-27`, `AdditionalDocumentation/WidgetKit-Implementing-Liquid-Glass-Design.md`.

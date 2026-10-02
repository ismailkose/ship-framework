<!-- ship-reference
id: swiftui-performance
kind: mixed
sources: Xcode 27.0 (27A266a) `xcrun xctrace list templates` / `xctrace help record` (checked 2026-09-23); iPhoneOS27.0.sdk (API availability, machine-checked by scripts/checks/ios.sh); avdlee-swiftui@b24e68a (skills/swiftui-expert-skill: reviewed 2026-09-28, not suggested, nothing copied); https://developer.apple.com/documentation/xcode/improving-your-app-s-performance (2026-09-23)
reviewed: 2026-09-23
-->
# SwiftUI performance — Ship's workflow

**When to read:** Dev before calling a list, feed, scrolling, or frequently updating screen done;
Crit when an iOS diff touches those; anyone asked "why is this slow/janky?"; logging, crashes,
leaks, and sanitizers (§7). Pattern depth lives in
the installed SwiftUI expert skill (`performance-patterns`, `list-patterns`, `image-optimization`,
`trace-recording`, `trace-analysis`); this file is the Ship loop around it.

## 1. Evidence rule

A performance finding is a **suggestion** until a measurement backs it (trace, Instruments
screenshot, MetricKit report, frame counter). With evidence it becomes a fix. Crit's severity:
*Should fix* by default; *Must fix* when measured on a hot path (list rows, scroll, live updates) or
when it causes a hang. Never "optimize" a screen that renders once (settings, about).

## 2. Symptom → first check → instrument

| Symptom | First code check (§3) | Instruments 27 template |
|---|---|---|
| Janky scroll, dropped frames | Identity, row cost, images, geometry in rows | **SwiftUI** (+ **Animation Hitches**) |
| UI freezes / hangs | Synchronous work on the main actor | **Time Profiler** (+ the Hangs instrument) |
| Too many view updates | Broad reads, environment churn | **SwiftUI** (update causes) |
| Slow launch / first screen | Work in `init`/`body`, eager loading | **App Launch** |
| Memory growth | Retained tasks/closures, image caches | **Allocations**, **Leaks** |
| Async work piling up | Unstructured tasks, missing cancellation | **Swift Concurrency** |
| Battery/thermal complaints | Timers, polling, location | **Power Profiler** |

Measure **Release** builds; Debug adds overhead and misleads.

## 3. Code-first scan (do this before recording anything)

1. **Reads too high in the tree.** `@Observable` tracks per property per `body` — a parent that
   reads many properties or a whole collection re-runs for every change and rebuilds children.
   Move each read into the smallest subview that shows it; pass the model, not copied values.
   `ObservableObject` + `@Published` invalidates on *any* change — migrate hot paths to
   `@Observable` (iOS 17+).
2. **Unstable identity.** `id: \.self` on mutable values, `indices`/offsets, `UUID()` created in
   `body` or `.id(UUID())` reset state and animations. Use a stored, stable `id`.
3. **Work in `body`.** Sorting, filtering, grouping, formatter creation, JSON/Markdown parsing.
   Derive once when inputs change (model or `.task(id:)`), format with `FormatStyle`.
4. **Images.** Full-resolution decode on the main actor while scrolling. Downsample off the main
   actor (`byPreparingThumbnail(ofSize:)`, iOS 15+) to the displayed size × `displayScale`.
5. **Geometry in rows.** `GeometryReader` inside lazy rows. Use `containerRelativeFrame` (17+)
   or `onGeometryChange(for:of:action:)` (back-deploys to 16).
6. **Type erasure and identity flips.** `AnyView` in rows; `if cond { v.modifier() } else { v }`
   creates two identities — put the condition in the modifier's value instead.
7. **Broad animation.** `.animation(_:value:)` high on a container animates every layout change
   below it — attach it to the view that changes (values from the motion skill).
8. **Fast-changing environment.** Scroll offsets, timers, or per-frame values in `.environment`
   invalidate every reader. Pass them to the one view that needs them.

```swift
// Parent reads only what it shows; each row reads its own item.
struct InboxList: View {
    let inbox: Inbox                       // @Observable
    var body: some View {
        List(inbox.messages) { message in  // reads `messages` only
            MessageRow(message: message)   // row reads `subject` and `isUnread`
        }
    }
}

struct MessageRow: View {
    let message: Message                   // @Observable
    var body: some View {
        Text(message.subject).fontWeight(message.isUnread ? .semibold : .regular)
    }
}

@Observable final class Message: Identifiable {
    let id = UUID()
    var subject = ""
    var isUnread = true
}

@Observable final class Inbox { var messages: [Message] = [] }
```

Quick debug: `let _ = Self._printChanges()` at the top of `body` prints what triggered an update
(debug builds only; remove before commit).

## 4. Recording a trace

Record with `xctrace` (the SwiftUI template shows view body updates, their causes and hitches;
record only the app with `--attach` or `--launch`: a system-wide recording needs the founder's
explicit OK):

```bash
xcrun xctrace list devices
xcrun xctrace record --template SwiftUI --device "<udid>" --attach "<AppName>" --time-limit 30s --output ./session.trace
xcrun xctrace export ./session.trace --toc             # see what tables were captured
```

The SwiftUI template is most reliable on a physical device or the Mac. If its SwiftUI lane comes
back empty on the Simulator, record **Time Profiler** there instead. Ask the founder for exact
reproduction steps and the device before recording.

**Field data:** MetricKit — `MetricManager` on iOS 27+, `MXMetricManager` below
(`ios-27.md` §3) — plus Xcode Organizer's hang and launch reports.

## 5. Fix loop

1. Pick the biggest measured cost, not the easiest fix.
2. One change at a time: narrow reads → stabilize identity → move work out of `body` → images →
   layout → animation scope.
3. Re-record the same interaction; compare against the first trace; note the numbers in the
   handoff.
4. Check nothing regressed elsewhere (other screens reading the same model).

## 6. Review integration

**Crit (`/shipmate review`, iOS diff touching lists, scroll, or live-updating views):** scan §3 items
1–8; report as `PERF: <what> — <evidence or "unmeasured">` with the §1 severity.

**Dev (`/shipmate build`):** before "done" on such a screen, run the §3 scan; if the screen is a hot
path, record one trace (§4) or say plainly that it's unmeasured.

## 7. Diagnostics — logs, signposts, sanitizers, memory, crashes

- **Logging:** `Logger(subsystem:category:)` (os), one category per feature. Interpolated values
  are **private by default** in release logs — mark only non-personal values `privacy: .public`.
  Never `print` in shipped code; read logs in Console.app or `log stream --predicate 'subsystem == "…"'`.
- **Measure a span:** `OSSignposter` intervals around the work you suspect (decode, first render,
  sync); they appear in Instruments' Points of Interest lane next to SwiftUI and Time Profiler data.
- **Sanitizers (scheme › Diagnostics), one at a time:** Thread Sanitizer for data races in code
  that isn't yet Swift 6 clean; Address Sanitizer for memory corruption in C/unsafe code; Main
  Thread Checker stays on in debug. Run the unit/UI test suite with them, not just the app.
- **Memory:** Xcode's Memory Graph Debugger for retain cycles (closures capturing `self` in stored
  tasks/timers/observers, delegates not `weak`); Instruments **Leaks** and **Allocations**
  (generations) for growth across repeated navigation. A screen pushed and popped 10 times should
  return to baseline.
- **Hangs and crashes in the field:** Xcode Organizer (hangs, crashes, launches, energy) plus
  MetricKit diagnostics (`MetricManager` on iOS 27+, `ios-27.md` §3). Keep dSYMs for every build you ship (archive keeps
  them) so reports symbolicate. Reproduce a reported hang with Time Profiler + the Hangs instrument.
- **CI:** `xcrun xctrace record --template 'Time Profiler' --launch -- <app>` on a device or Mac,
  or `XCTest` `measure(metrics:)` for regressions you want to guard with a baseline.

```swift
import os

enum Diagnostics {
    nonisolated static let sync = Logger(subsystem: "com.example.app", category: "sync")
    nonisolated static let signposter = OSSignposter(logger: sync)
}

nonisolated func importTrips(count: Int) {
    let state = Diagnostics.signposter.beginInterval("Import trips", "\(count, privacy: .public) rows")
    defer { Diagnostics.signposter.endInterval("Import trips", state) }
    Diagnostics.sync.info("Import started for \(count, privacy: .public) rows")
    // … the work; personal data (names, emails) stays private: "\(name)" is redacted in release logs
}
```

**Verify:** the signpost interval shows in Instruments › Points of Interest on a device or
simulator run; logs appear in Console with the subsystem filter; a Release build redacts the
private values. Nothing here is proven by compiling alone.

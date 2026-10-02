<!-- ship-reference
id: ios-accessibility
kind: mixed
sources: iPhoneOS27.0.sdk SwiftUI / UIKit / XCTest interfaces (Xcode 27.0 27A266a — examples type-check via scripts/checks/ios.sh); https://developer.apple.com/documentation/accessibility ; https://developer.apple.com/documentation/swiftui/view/accessibilityinputlabels(_:) ; https://developer.apple.com/documentation/uikit/uiaccessibilitycustomaction ; https://developer.apple.com/design/human-interface-guidelines/accessibility ; https://developer.apple.com/documentation/xctest/xcuiapplication/performaccessibilityaudit(for:_:) ; https://support.apple.com/guide/iphone/use-voice-control-iph2c21a3c88/ios ; https://support.apple.com/guide/iphone/use-switch-control-iph400f5ba5c/ios ; https://support.apple.com/guide/iphone/full-keyboard-access-iph1ca1f7d1d/ios (all checked 2026-09-25). Capability inventory informed by dadederk/iOS-Accessibility-Agent-Skill@dcc3a36 (MIT) — ideas checked against Apple's docs; no text reused.
reviewed: 2026-09-25
-->
# Accessibility by assistive technology — VoiceOver, Voice Control, Switch Control, keyboard

**When to read:** "support Switch Control / Voice Control / Full Keyboard Access", "works with a
keyboard", "people can't reach this button", an accessibility review of a reusable component, or
before calling a screen done for someone who doesn't use touch. The design rules (contrast, target
size, Dynamic Type) are in `hig-ios.md` §3–5 and §9; the SwiftUI modifiers in
`swiftui-building.md` §9. **Apple** = platform behaviour; **Ship** = default.

## 1. One set of semantics, four ways in

All four technologies read the same accessibility tree: an element's **label, value, traits,
actions, and order**. Fix the component once (a registered primitive in `design/components.yaml`)
and every screen that uses it improves.

| Technology | How people use it | What breaks it |
|---|---|---|
| VoiceOver | Swipe through elements, hear label + value + traits, double-tap | Missing/duplicate labels, decorative images read aloud, wrong order, actions only on gestures |
| Voice Control | Say "Tap Save", "Show names", "Show numbers", "Show grid" | Spoken name ≠ visible text; icon buttons with no name; two controls with one name |
| Switch Control | One or more switches step (scan) through items and groups, then pick from a menu of actions | Too many stops (every tiny element separate), actions that need swipes or long-presses, no grouping |
| Full Keyboard Access | Tab / arrows move focus, Space activates, Tab-Z shows actions | Controls that can't take focus, no visible focus, custom gestures with no command |

**Ship:** anything a gesture does (swipe to delete, long-press menu, drag to reorder) is also an
**accessibility action** — that's the path for Switch Control, Full Keyboard Access, and VoiceOver
at once.

## 2. Voice Control

- **The spoken name is the label, and it must match what's visible.** A button showing "Submit"
  is labelled "Submit", not "Send form". Icon-only buttons need a label (they get "Tap Settings").
- Give extra spoken names with `.accessibilityInputLabels(["Settings", "Preferences"])`
  (UIKit: `accessibilityUserInputLabels`), most important first (Apple: Voice Control and Full
  Keyboard Access use them). Useful for long labels ("Tap Reply" for "Reply to Anna's message") and synonyms.
- Unique names on one screen: two "Edit" buttons make people fall back to "Show numbers". Put the
  context in the label ("Edit Lisbon trip") and keep the short visible text.
- Don't put the role in the label ("Save button") — the trait already says it.
- Check it the way people use it: "Show names" overlays every control's spoken name; "Show
  numbers" is the fallback people need when names are missing or repeated (§7 has the full flow).

## 3. Switch Control

- **Reduce scan stops:** a card that acts as one thing is one element
  (`.accessibilityElement(children: .combine)`), with its extra operations as actions. Put related
  controls in a container (`.accessibilityElement(children: .contain)`; UIKit
  `accessibilityContainerType = .semanticGroup`) so a scan can enter or skip the group.
- **Every operation reachable without a gesture:** swipe actions, context-menu items, and
  drag-to-reorder get `.accessibilityAction(named:)` / `accessibilityCustomActions`. Switch
  Control shows them in its menu (UIKit custom actions can carry an image — iOS 14).
- **Timeouts:** nothing important disappears on a timer (toasts with an action, auto-advancing
  pages) unless people can pause or extend it — scanning takes time.
- Order follows reading order; fix odd layouts with `.accessibilitySortPriority` (higher first)
  rather than rebuilding the view.

## 4. Full Keyboard Access and hardware keyboards

- Standard controls take focus automatically. Custom interactive views need `.focusable()` (and
  `.focused` to drive it) so Tab reaches them; the system draws the focus ring — don't remove it
  without drawing a visible replacement.
- Frequent commands get `.keyboardShortcut`: `.defaultAction` (Return) for a sheet's primary
  button, `.cancelAction` (Escape) for Cancel, ⌘N / ⌘F for common commands; iPad apps list commands in the scene's
  `.commands` (menu bar, iPadOS 26). Custom key handling: `.onKeyPress` (iOS 17).
- Tab-Z shows the element's accessibility actions — the same actions as Switch Control.
- Focus must move somewhere sensible after an action: into a new sheet, back to the trigger when
  it closes, to the next row after a delete (`@FocusState` / `@AccessibilityFocusState`).

## 5. VoiceOver and text size (the parts that change per component)

- Values change without the label: `.accessibilityValue("3 of 5")`, not a label that includes it.
- Rotors for long content (`.accessibilityRotor` — headings, links, unread items); headings get
  `.isHeader`.
- Custom content that's secondary (a trip's distance and date) via `.accessibilityCustomContent`
  so VoiceOver reads it on request instead of every time.
- Controls that can't grow with Dynamic Type (tab-bar-like icon rows) show the Large Content
  Viewer: `.accessibilityShowsLargeContentViewer` (long-press shows the enlarged item).

## 6. SwiftUI and UIKit differences that matter

| Need | SwiftUI | UIKit |
|---|---|---|
| Spoken alternatives | `.accessibilityInputLabels` | `accessibilityUserInputLabels` |
| Extra operations | `.accessibilityAction(named:)` / `.accessibilityActions { }` | `accessibilityCustomActions` (`UIAccessibilityCustomAction`, handler returns `Bool`) |
| Grouping | `.accessibilityElement(children: .combine / .contain)` | `isAccessibilityElement` on the container + `accessibilityElements` / `accessibilityContainerType` |
| Reading order | `.accessibilitySortPriority` | `accessibilityElements` array order |
| Keyboard focus | `.focusable()`, `@FocusState` | `canBecomeFocused`, `UIFocusSystem`, `UIKeyCommand` |
| Announce a result | `AccessibilityNotification.Announcement(…).post()` (17) | `UIAccessibility.post(notification: .announcement, …)` |

A SwiftUI view hosted in UIKit (or UIKit in SwiftUI, `swiftui-ship.md` §7) keeps its own tree:
check the seam — the bridged view must expose its own label and actions.

```swift
/// A registered row primitive: one scan stop, a clear spoken name, every gesture as an action.
struct TripRow: View {
    let title: String
    let dates: String
    let onOpen: () -> Void
    let onShare: () -> Void
    let onDelete: () -> Void

    var body: some View {
        Button(action: onOpen) {
            VStack(alignment: .leading, spacing: Theme.Spacing.xs) {
                Text(title).font(Theme.Typography.body)
                Text(dates).font(Theme.Typography.caption).foregroundStyle(Theme.Colors.muted)
            }
        }
        .accessibilityElement(children: .combine)                       // one stop, not two
        .accessibilityInputLabels([Text(title), Text("Trip")])          // "Tap Lisbon" / "Tap Trip"
        .accessibilityAction(named: "Share") { onShare() }              // Switch Control menu, Tab-Z, VoiceOver
        .accessibilityAction(named: "Delete") { onDelete() }
        .swipeActions {                                                 // the touch path for the same actions
            Button("Delete", role: .destructive, action: onDelete)
            Button("Share", action: onShare)
        }
    }
}

struct TripToolbar: ToolbarContent {
    let onNewTrip: () -> Void
    var body: some ToolbarContent {
        ToolbarItem(placement: .primaryAction) {
            Button("New Trip", systemImage: "plus", action: onNewTrip)
                .keyboardShortcut("n", modifiers: .command)           // hardware keyboards and FKA
        }
    }
}
```

```swift
import UIKit

/// UIKit equivalent for a custom cell: names, actions, and one group.
final class TripCell: UITableViewCell {
    var onShare: () -> Void = {}
    var onDelete: () -> Void = {}

    func configure(title: String, dates: String) {
        isAccessibilityElement = true
        accessibilityLabel = title
        accessibilityValue = dates
        accessibilityUserInputLabels = [title, "Trip"]
        accessibilityCustomActions = [
            UIAccessibilityCustomAction(name: "Share", image: UIImage(systemName: "square.and.arrow.up")) { [weak self] _ in
                self?.onShare(); return true
            },
            UIAccessibilityCustomAction(name: "Delete", image: UIImage(systemName: "trash")) { [weak self] _ in
                self?.onDelete(); return true
            },
        ]
    }
}
```

## 7. Verify — automated first, then each technology by hand

**Automated (CI, simulator):** a UI test per screen that runs the system audit — it catches missing
labels, clipped Dynamic Type text, small hit areas, and low contrast. It can't judge whether a name
is *right* or an order *makes sense*.

```swift
import XCTest

nonisolated final class AccessibilityAuditTests: XCTestCase {   // nonisolated: needed when the test
                                                              // target defaults to MainActor isolation
    @MainActor
    func testTripListPassesAudit() throws {
        let app = XCUIApplication()
        app.launch()
        try app.performAccessibilityAudit()      // iOS 17+; filter known issues with the closure form
    }
}
```

**Manual acceptance (not run by Ship — record who ran it, on what device, and the result):**

| Technology | Flow to run on the screen | Pass when |
|---|---|---|
| VoiceOver | Swipe from top to bottom, activate each control, perform each action from the rotor's Actions | Every element reads a sensible name/value/trait in reading order; every action reachable |
| Voice Control | "Show names", then "Tap <name>" for each control; "Show numbers" on a list | Every control has a speakable name matching its visible text; no duplicates force numbers |
| Switch Control | Item scanning through the screen; open the menu on a row and run each action | Rows are one stop each; groups can be skipped; every gesture's action is in the menu |
| Full Keyboard Access | Tab through, Space to activate, Tab-Z for actions, Escape to close sheets | Every control focusable with a visible ring; focus lands sensibly after each action |
| Dynamic Type | AX5 text size, then Bold Text | Nothing truncates essential text; layouts stack (`hig-ios.md` §3) |

Where to run: Full Keyboard Access and the audit work in the simulator (Settings › Accessibility,
Mac keyboard). Voice Control and Switch Control need a **device** for a real pass (speech input,
switch hardware or screen switches); Accessibility Inspector (Xcode › Open Developer Tool) helps
inspect names and actions on either.

Apple: [Accessibility](https://developer.apple.com/documentation/accessibility) ·
[HIG accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) ·
[Accessibility audit](https://developer.apple.com/documentation/xctest/xcuiapplication/performaccessibilityaudit(for:_:)) ·
Xcode 27: `AdditionalDocumentation/Implementing-Assistive-Access-in-iOS.md`.

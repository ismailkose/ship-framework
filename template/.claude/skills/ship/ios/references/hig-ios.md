<!-- ship-reference
id: hig-ios
kind: mixed
sources: https://developer.apple.com/design/human-interface-guidelines (tab-bars, layout, typography, accessibility, color, dark-mode, materials, buttons, sheets, playing-haptics, managing-notifications, onboarding, launching, managing-accounts, settings, toolbars — checked 2026-09-23; privacy — checked 2026-09-29); https://developer.apple.com/app-store/review/guidelines/ (June 8, 2026 revision); iPhoneOS27.0.sdk (API availability, machine-checked by scripts/checks/ios.sh); impeccable@9d715cc (idea only for §10: the platform owns structure, the brand owns an open layer — its skill/reference/ios.md, itself distilled from ehmo/platform-design-skills, MIT; pbakaus/impeccable, Apache-2.0)
reviewed: 2026-09-29
-->
# Apple HIG for iOS — the decisions that change outcomes

Not a copy of the HIG. It keeps the choices and numbers Ship enforces, marks which are Apple's
(**HIG**) and which are Ship's (**Ship**), and gives Eye its checklist (§9).
Full guidelines: https://developer.apple.com/design/human-interface-guidelines

**When to read:** Arc — §1, §7, §8 while planning screens. Dev — §1–§8 while building UI.
Eye — §9 while reviewing (and §4–§5 for numbers). Design tokens always come from the registry
(`swiftui-ship.md` §2); this file says *what* to decide, the registry holds *the values*.

## 1. Navigation structure

| Need | Use | Not |
|---|---|---|
| A few parallel top-level sections | Tab bar (`TabView` + `Tab`, iOS 18+) | Hamburger menu |
| Hierarchy: list → detail → sub-detail | `NavigationStack` (push) | Custom navigation |
| Two/three columns on iPad or wide windows | `NavigationSplitView`, or `.tabViewStyle(.sidebarAdaptable)` | A stretched phone layout |
| A self-contained task (compose, edit, filter) | Sheet with detents | A full-screen push |
| Confirming a destructive action | `.confirmationDialog` or alert with a `.destructive` button | A custom modal |

- **HIG** Tab bars navigate; they don't perform actions. Keep the tab bar visible across sections
  (a modal may cover it). Use as few tabs as the app needs and avoid overflow: extra tabs collapse
  into a *More* tab that hides content. Where available, prefer a tab bar that adapts to a sidebar.
- **HIG** Always keep the back button and the edge-swipe back gesture in push navigation.
- **HIG** Sheets: a Cancel/Close that discards changes; a Done that saves pairs with Cancel (never
  all three of Cancel, Done, Back). Cancel on the leading edge, Done on the trailing edge. On
  iPhone, consider the medium detent for progressive disclosure; only-medium stops full height.
- **Ship** One navigation model per level. Each tab owns its own `NavigationStack` and path.
- **Ship** Deep links resolve to a route (`swiftui-ship.md` §4), never to a view built ad hoc.

```swift
struct AppTabs: View {
    var body: some View {
        TabView {
            Tab("Today", systemImage: "sun.max") { NavigationStack { Text("Today") } }
            Tab("Library", systemImage: "books.vertical") { NavigationStack { Text("Library") } }
            Tab(role: .search) { NavigationStack { Text("Search") } }
        }
        .tabViewStyle(.sidebarAdaptable)
    }
}
```

## 2. Layout and adaptivity

- **HIG** Respect safe areas and system margins; let backgrounds and artwork run full-bleed while
  controls and text stay inside the safe area. `ignoresSafeArea` is for decoration only.
- **HIG** Adapt to size, orientation, window resizing, and multitasking. Decide with size classes
  and the actual container size — **never** with device models or hard-coded bar heights (they
  change per device; read the layout instead).
- **HIG** Place the most important content near the top and leading side; support right-to-left.
- **Ship** Design compact width first, then adapt to regular width. iPad windows resize freely —
  test narrow and wide. Foldable ("iPhone Duo") layouts → Apple's layout docs once iOS 27.1 ships.
- **Ship** Spacing and margins between your own elements are registry tokens
  (`Theme.Spacing.*`), not literals.
- **Apple** iPad apps run in resizable windows (Split View, Stage Manager, iPadOS 26 windowing).
  Opting out with `UIRequiresFullScreen` is deprecated as of iPadOS 26 — design for any width, and
  if a scene truly needs a minimum size, set `UISceneSizeRestrictions` instead. Hardware keyboard:
  app commands go in the scene's `.commands` (they appear in the iPadOS menu bar) and common
  actions get `.keyboardShortcut`.

## 3. Typography

- **HIG** Use text styles so Dynamic Type works; test the largest accessibility sizes. iOS default
  body size 17 pt, minimum 11 pt. Avoid Ultralight, Thin, and Light weights.
- **HIG** Custom fonts must scale with Dynamic Type. Ship's generated `Theme.Typography` already
  uses `.custom(_:size:relativeTo:)` — keep text on those tokens.
- **Ship** At accessibility sizes, stack horizontally laid-out rows instead of truncating.
- **Ship** At most two type families (the brand face + the system face).

```swift
struct MetricRow: View {
    @Environment(\.dynamicTypeSize) private var typeSize
    let label: String
    let value: String

    var body: some View {
        let layout = typeSize.isAccessibilitySize
            ? AnyLayout(VStackLayout(alignment: .leading))
            : AnyLayout(HStackLayout())
        layout {
            Text(label).font(Theme.Typography.body)
            Spacer(minLength: Theme.Spacing.sm)
            Text(value).font(Theme.Typography.body).monospacedDigit()
        }
    }
}
```

## 4. Color, dark mode, materials

**Contrast (HIG, from the accessibility page)**

| Text | Minimum contrast |
|---|---|
| Up to 17 pt, any weight | 4.5:1 |
| 18 pt and larger | 3:1 |
| Bold, any size | 3:1 |

- **HIG** If defaults can't meet this, provide a higher-contrast scheme for *Increase Contrast*.
  Check both appearances.
- **HIG** Don't offer an app-specific appearance toggle — follow the system setting.
- **HIG** Dark Mode colors aren't inversions: backgrounds get dimmer, foregrounds brighter; system
  backgrounds switch between base and elevated levels for sheets and popovers.
- **HIG** Test with Increase Contrast and Reduce Transparency, separately and together.
- **Ship** All colors arrive through `Theme.Colors`; Apple's adaptive colors are mapped in the
  model as `system.<name>`. Custom colors need light *and* dark values in the model.

**Liquid Glass and materials (HIG)**
- Liquid Glass is the layer for controls and navigation floating above content — not for the
  content layer. System bars, tab bars, and toolbars adopt it automatically when built with the
  iOS 26+ SDK.
- Two variants: *regular* (blurs, keeps text legible — most components) and *clear* (for controls
  over rich media). Over bright content, a clear-glass control may need a dark dimming layer
  (Apple suggests 35% opacity).
- Use color on glass sparingly — for the primary action or a status, not every control.
- Content-layer separation uses the standard materials: ultra-thin, thin, regular, thick.
- **Ship** Custom `glassEffect` only where a product decision says so (`swiftui-ship.md` §5), gated
  `if #available(iOS 26, *)` with a material fallback.

## 5. Touch, gestures, haptics

| Rule | Value | Source |
|---|---|---|
| Minimum control size (iOS/iPadOS) | 44 × 44 pt | HIG |
| Padding around bezeled controls | about 12 pt | HIG |
| Padding around borderless controls | about 24 pt around the visible edges | HIG |

- **HIG** Every gesture needs an on-screen alternative (a swipe-to-dismiss also gets a button).
- **HIG** Don't repurpose system gestures: edge swipe = back, pull = refresh, long press = context
  menu, row swipe = row actions.
- **Ship** Extend small visuals to a 44 pt hit area (`.contentShape`, `.frame(minWidth:minHeight:)`)
  rather than enlarging the art.
- **HIG** Haptics: use system patterns for their documented meaning, consistently; pair them with
  visual feedback; keep them optional. Standard controls already play them.
- **Ship** Play haptics with `.sensoryFeedback` (`.success`, `.warning`, `.error`, `.selection`,
  `.impact(…)`) — not UIKit feedback generators. Core Haptics only for custom patterns (games,
  audio-synced effects).

```swift
struct SaveButton: View {
    @State private var saveCount = 0
    var body: some View {
        Button("Save") { saveCount += 1 }
            .sensoryFeedback(.success, trigger: saveCount)
    }
}
```

## 6. Motion

Motion values, springs, curves, interruption, and Reduce Motion behavior belong to the motion
skill: `.claude/skills/ship/motion/SKILL.md`. From the HIG side, only this:
- Reuse system transitions (push, sheet, zoom via `.navigationTransition(.zoom(…))`) instead of
  rebuilding them.
- Loading: skeletons with `.redacted(reason: .placeholder)`; progress with `ProgressView`.

## 7. Components — system first

System components bring Dynamic Type, dark mode, accessibility, and Liquid Glass for free.

| Need | Use |
|---|---|
| Scrolling list of rows | `List` (or `LazyVStack` for custom card layouts) |
| Settings / forms | `Form` |
| Empty state | `ContentUnavailableView` |
| Pull to refresh | `.refreshable` |
| Search | `.searchable` |
| Share | `ShareLink` |
| Quick actions on an item | `.contextMenu`, `.swipeActions` |
| Date, toggle, choice | `DatePicker`, `Toggle`, `Picker` |
| Icons | SF Symbols (match the weight of adjacent text) |
| Feature discovery | TipKit |
| Paywall | `SubscriptionStoreView` / `ProductView` |

More replacements for hand-built UI: `swiftui-ship.md` §3.

**Images, icons, SF Symbols**
- **HIG** App icon: one 1024 × 1024 layered icon made in Icon Composer (included with Xcode), with
  the default, dark, clear, and tinted appearances people can pick on the Home Screen — check all
  four. Keep text and UI screenshots out of the icon.
- **HIG** SF Symbols first for interface icons: match the weight and scale of adjacent text
  (`.imageScale`, `.font`), use the rendering mode that fits (monochrome for controls,
  hierarchical/palette for emphasis, multicolor only where color carries meaning), and prefer
  symbols that exist on the deployment target (check the SF Symbols app's availability).
- **HIG** Custom icons: export as a vector symbol template or PDF/SVG in the asset catalog with
  "Preserve Vector Data"; raster art needs @2x and @3x. Mark template images so they tint.
- **Ship** Decorative images are hidden from VoiceOver; content images get a label (`swiftui-building.md` §9).

## 8. App lifecycle patterns

- **HIG** Launch screen: nearly identical to the first screen, no text, no logos or ads. A splash,
  if any, belongs to onboarding.
- **HIG** Onboarding: short and optional where possible; don't show a skipped tutorial again.
- **HIG** Ask for an account only when core functionality needs it, and as late as possible;
  offer Sign in with Apple, or passkeys otherwise. **App Review 5.1.1(v):** account creation in
  the app ⇒ account deletion in the app.
- **HIG** Ask for permission when the feature needs it, with context; if the app can't work
  without it, ask inside onboarding. Purpose strings say what and why (App Review 5.1.1). A screen of
  your own before the system alert has one button, titled like "Continue" or "Next", that opens the
  alert: never "Allow", and no second action. **Ship** Show it only while the status is undecided
  and no request is on screen; the system asks once, so after a no, point to Settings.
- **HIG** Notifications: choose the interruption level honestly — *passive* (read at leisure),
  *active* (default), *time sensitive* (needs attention now; never marketing), *critical*
  (health/safety, entitlement required).
- **HIG** Restore the previous state on relaunch so people continue where they left off.
  **Ship** Use `@SceneStorage` for per-scene UI state; no splash or reload on return from background.
- **HIG** Settings: few, smart defaults; put view options (sort, filter) in context; don't copy
  system settings such as appearance or text size.

## 9. Design review checklist (Eye)

**Navigation**
- [ ] One navigation model per level (tabs, stack, split view)
- [ ] Tab bar navigates only, stays visible, no More-tab overflow
- [ ] Back button and edge-swipe back intact in push navigation
- [ ] Each tab has its own stack; deep links resolve to routes
- [ ] iPad/wide windows use a split view or sidebar-adaptable tabs
- [ ] Every width an iPad window can take works — no `UIRequiresFullScreen` opt-out
- [ ] Sheets offer Cancel/Close; Done pairs with Cancel

**Typography**
- [ ] All text on text-style-relative tokens; Dynamic Type works through AX5
- [ ] Nothing under 11 pt; no Ultralight/Thin/Light weights
- [ ] At accessibility sizes, horizontal rows stack instead of truncating
- [ ] At most two type families
- [ ] No truncation of essential text at large sizes
- [ ] Custom font sizes come from `Theme.Typography`

**Color & materials**
- [ ] Colors come from `Theme.Colors`; no hex or literal colors in views
- [ ] Contrast meets 4.5:1 (≤17 pt) / 3:1 (≥18 pt or bold) in light and dark
- [ ] Increase Contrast and Reduce Transparency checked
- [ ] No app-specific dark mode toggle
- [ ] Liquid Glass only on controls/navigation, custom glass only by product decision, gated for iOS 26
- [ ] Color on glass reserved for primary action or status
- [ ] System bars and tab bars keep the system glass — not repainted with custom backgrounds

**Touch & interaction**
- [ ] Every tappable element has a 44 × 44 pt hit area
- [ ] Spacing between targets follows §5 (≈12 pt bezeled, ≈24 pt borderless)
- [ ] Every gesture has a visible alternative; system gestures untouched
- [ ] Destructive actions confirm; swipe actions reversible or confirmed
- [ ] Haptics via `.sensoryFeedback`, meaning matches the system pattern
- [ ] **Ship** Primary actions reachable one-handed (bottom half) where the layout allows

**Accessibility**
- [ ] VoiceOver labels on interactive elements; decorative images hidden
- [ ] Hints only where the action isn't obvious from the label
- [ ] Reduce Motion respected — custom movement becomes a short crossfade (not removed); system sheet/navigation transitions untouched (motion skill)
- [ ] Reduce Transparency keeps content readable
- [ ] Keyboard and focus navigation work (iPad, external keyboard)
- [ ] Charts and custom controls expose values to VoiceOver
- [ ] App icon checked in default, dark, clear, and tinted appearances
- [ ] SF Symbols match adjacent text weight; custom icons are vector/template assets

**Lifecycle**
- [ ] Launch screen is plain; no splash on warm start
- [ ] State restored after background/termination
- [ ] Permissions asked in context with honest purpose strings; a screen before the alert has one "Continue" button
- [ ] Notification interruption level matches urgency
- [ ] Sign in with Apple / passkeys offered; in-app account deletion when sign-up exists
- [ ] Settings screen doesn't duplicate system settings (appearance, text size)

**Platform**
- [ ] Nothing hand-built that `swiftui-ship.md` §3 lists as native, unless a reason is stated
- [ ] APIs above the deployment target gated with `#available` + fallback
- [ ] App Review checks in `frameworks.md` hold for launch builds

## 10. Where the brand lives — fixed by the platform, open to the product

A native app earns trust by behaving like the platform, and identity by what it does in the open
layer. Re-skinning what the platform owns reads as a ported website; leaving the open layer at its
defaults reads as a template.

| The platform owns (keep) | The product owns (decide it from the direction) |
|---|---|
| Navigation model, back swipe, tab and sidebar behaviour | **Tint:** one action colour, set once at the app root (`.tint(_:)` plus the AccentColor asset) so controls, links and selection agree |
| Bar and sheet chrome (Liquid Glass on iOS 26), system transitions | **Type:** the system face in a chosen design or width (`Font.system(_:design:weight:)` with `.rounded`, `.serif` or `.monospaced`; `.fontWidth(_:)`), or a brand face that still scales (`Font.custom(_:size:relativeTo:)`) |
| How controls behave: toggles, pickers, menus, text fields, the keyboard | **Symbols:** one SF Symbols weight and rendering mode; brand glyphs as custom symbols made from an SF template, so they scale and animate like the rest |
| Dynamic Type scaling and the accessibility settings | **Shape:** the registry's radius scale, with nested corners kept concentric |
| Safe areas, the home indicator, alerts and permission prompts | **Surfaces:** registry backgrounds and list styling (`.scrollContentBackground(.hidden)`, `.listRowBackground(_:)`), and the content under the glass |
| | **Motion and feel:** the registry's springs; `.sensoryFeedback(_:trigger:)` on the moments that matter |
| | **Imagery and words:** real photos, the empty and loading states, the app icon in light, dark and tinted |

Test: someone fluent in iPhone apps trusts it at once (nothing to relearn), and with every word
garbled the open layer still says what the product is.

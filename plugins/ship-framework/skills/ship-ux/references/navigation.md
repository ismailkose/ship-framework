<!-- ship-reference
id: ux-navigation
kind: mixed
sources: https://developer.apple.com/design/human-interface-guidelines/tab-bars (2026-09-23); https://developer.apple.com/design/human-interface-guidelines/sidebars (2026-09-23); https://m3.material.io/components/navigation-bar/guidelines (2026-09-23); https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture (2026-09-23); https://www.nngroup.com/articles/hamburger-menus/ (2026-09-23); books-and-sites (Jon Yablonski, Laws of UX); lennys-talks-2026 (Mike Krieger: a feature earns its tab; ideas only, 2026-09-30); growth-design-psychology (method of loci; ideas only, 2026-10-01)
reviewed: 2026-10-01
-->

# Navigation

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`).
**Registry first:** screen maps and nav decisions live in `DECISIONS.md` / the plan; the nav
components themselves are entries in `design/components.yaml`. Don't invent a second nav pattern
for one screen.

---

## 1. Choosing the pattern (Arc, Vi)

| Situation | Pattern |
|---|---|
| 2–5 top-level, peer destinations, used often (phone) | **Tab bar / navigation bar** at the bottom (PLATFORM: iOS tab bar, M3 navigation bar with 3–5 destinations). Icons **with** labels. |
| Many sections or deep hierarchy; tablet/desktop | **Sidebar** (iPad/Mac: `NavigationSplitView`; web: side nav; Android: navigation rail on medium, drawer on expanded). |
| Same app across phone and iPad | iOS: `TabView` with `.sidebarAdaptable` style — tabs on iPhone, sidebar on iPad. Android: adaptive navigation suite. |
| Drill-down within a section | Push navigation (stack) with a visible back affordance. |
| Self-contained sub-task | Sheet / modal — returns to where the user was (`ux-principles.md` §5). |
| Rare destinations (settings, help, account) | A profile/settings entry or menu — not a hamburger that hides primary destinations. |

- **A new feature earns its tab (SHIP):** start it inside the screen where its moment happens (a
  note field on Today, not a Journal tab), and give it a tab once people go there on purpose and
  often. A tab added later costs nothing; one taken away costs trust.
- **Hidden navigation costs discovery** (EXPERT, NN/g): primary destinations belong on screen, not
  behind a hamburger.
- **Jakob's law:** phone users expect bottom tabs; desktop users expect a top bar or sidebar;
  everyone expects Back to work.
- **Breadth vs depth (Hick):** group 12 flat items into a few labelled sections rather than a
  deeper tree nobody explores.
- **Search** is navigation: on iOS a dedicated search tab is a system pattern; on web a `⌘K`
  command palette complements, never replaces, visible nav.

## 2. Wayfinding (Pol, Dev)

- **Current location is always visible:** selected tab/sidebar item marked by more than color
  (weight, fill, indicator) — REQ 1.4.1; screen title matches the nav label.
- **Labels:** one or two words naming the destination (Home, Library, Activity), not the action.
  Avoid "Other", "Misc", "Stuff".
- **Consistency:** nav position, order and style never change between screens; help lives in the
  same place (REQ 3.2.6). People remember features by where they are (method of loci): moving one
  costs more than it looks, so move it rarely and say where it went.
- **Tab state is preserved:** switching tabs keeps each tab's stack and scroll; tapping the active
  tab again scrolls to top / pops to root (iOS convention).

## 3. Back, state and deep links

- **Back restores state:** scroll position, filters, sort, pagination, partially-filled input.
- **Every significant screen is addressable.** Web: a URL per screen; route params for identity
  (`/projects/abc`), query params for view state (`?sort=recent&tag=design`) so refresh, back and
  sharing reproduce the view. iOS/Android: universal/app links and a navigation path that can be
  rebuilt from a deep link (`NavigationStack(path:)`, Navigation Compose deep links).
- **System back is sacred (PLATFORM):** iOS left-edge swipe-back works on every pushed screen
  (don't break it with a custom back button or full-screen gestures); Android predictive back
  shows where Back goes — opt in and handle it instead of intercepting it.
- **Modals vs navigation:** a task that returns to the same context is modal (rename, confirm,
  quick add); a full context change is navigation (open another record, full editor). Getting
  this wrong breaks Back.

## 4. QA (Test)

- [ ] Every top-level destination reachable in one tap/click; labels visible.
- [ ] Deep links / URLs open the right screen with the right state, cold and warm.
- [ ] Refresh (web) and relaunch (native) restore the view the user expects.
- [ ] Back restores scroll, filters and input on every list → detail → back path.
- [ ] iOS swipe-back from the left edge works on every pushed screen; Android predictive back previews correctly.
- [ ] Nothing traps the user: every modal has a visible close, Esc (web/iPad keyboard) closes overlays.
- [ ] Active state identical across screens; the same destinations in the same order at every size.

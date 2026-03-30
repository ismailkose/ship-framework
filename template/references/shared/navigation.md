# Navigation Reference

> Agent routing:
> **Vi** → Sections 1 (navigation affects product flow and user mental model)
> **Arc** → Sections 1-2 (plan nav architecture, pattern selection, state management)
> **Dev** → Section 2 (implement nav patterns, deep linking, state preservation)
> **Pol** → Section 2 (audit consistency, back behavior, active states)
> **Test** → Section 3 (verify deep links, back behavior, gesture nav, state preservation)

---

## Section 1: Navigation Architecture

### Pattern Selection Framework

**Bottom Tab Navigation (≤5 destinations)**
Use for flat information architecture where users regularly switch between 3-5 equal-weight top-level sections. Examples: Messages, Posts, Profile (social), Home, Explore, Cart, Account (e-commerce). Bottom placement leverages thumb zone on mobile. Constraint: never exceed 5 items — beyond 5, targets shrink below 44dp touch targets, labels become unreadable, cognitive load spikes.

**Sidebar Navigation (6+ major sections, or complex hierarchy)**
Use for apps with 6+ top-level destinations or deep information hierarchies requiring category grouping. Examples: design tools (File, Edit, View, Insert, Design, Prototype, Inspect), admin dashboards (Users, Settings, Reports, Analytics, Integrations, Billing). Sidebar accommodates more items and supports subsection disclosure. Adaptive: hide below 1024px viewport width to preserve content space.

**Drawer Navigation (secondary actions only)**
Use exclusively for low-frequency secondary navigation: settings, help, feedback, logout. Never use drawer as primary navigation — it hides navigation, reduces discoverability, and studies show engagement drops 50%+ when primary nav is hidden. The "hamburger menu problem" is real: users don't instinctively look for hidden menus, and visibility matters more than screen space.

### Mental Model & Discoverability

**Jakob's Law: Navigation Follows Conventions**
Users expect your navigation to work like apps they already use. Breaking conventions has a cost — disorientation, slower task completion, reduced engagement. Match your user's existing mental models: mobile-first audiences expect bottom tabs; desktop-first audiences expect sidebars; all users expect the back button to work.

**Hick's Law: Breadth vs Depth Tradeoff**
- **Shallow, wide nav** (many visible items): higher discoverability, but higher cognitive load per decision
- **Deep, narrow nav** (collapsible sections): lower overwhelm, but requires more interaction to find content

Balance by grouping: instead of 12 flat sections, create 4 categories with 3 subsections each.

**Active State Visibility**
Users must always know where they are. Disorientation causes abandonment. Active state indicators must be:
- **Visual contrast**: different color, weight, or background from inactive items
- **Obvious**: 3+ second recognition time max
- **Consistent**: same indicator style across all nav surfaces

Never rely on icon alone — pair with label or use clear visual weight change.

### Item Limits & Labels

**Target Size & Label Necessity**
- Bottom nav: 44dp minimum touch target (48dp recommended)
- 5 items at 48dp = 240dp total width, centered with padding — works on any mobile screen
- 6 items at 48dp = 288dp — scroll required, breaks thumb zone, bad UX
- **Icon-only nav fails**: icons require recall (harder), labels enable recognition (faster). Always pair icons with labels for primary navigation.

**Naming Pattern**
Use single-word labels when possible (Home, Explore, Messages, Profile). Two words acceptable (My Stuff). Avoid vague labels ("Other," "More," "Tools"). Label should explain the destination, not the action.

---

## Section 2: Implementation Patterns

### Back Button State Preservation

**The Problem: Lost State**
When users press back and return to a screen, they expect scroll position, applied filters, pagination state, and form input to persist. Losing state feels like a bug, causes re-navigation, increases bounce. Users blame the product.

**Implementation**
- Restore scroll position on back navigation
- Preserve filter/sort state in URL query params
- Cache form input in memory during session
- Use browser history state API or router history stack to store view state

**Correct vs Incorrect**
- ❌ User scrolls to product 50, clicks product, goes back → scroll resets to top
- ✓ User scrolls to product 50, clicks product, goes back → scroll restores to product 50
- ❌ User filters by "Blue" color, clicks product, goes back → filters reset
- ✓ User filters by "Blue" color, clicks product, goes back → URL still has `?color=blue`, view matches

### Deep Linking

**Every Significant Screen Reachable via URL**
A screen without a unique URL cannot be:
- Bookmarked
- Shared (notification routing, email links, social sharing)
- Referenced in onboarding flows
- Recovered from browser history
- Indexed by search (if applicable)

**Implementation**
- `/home` → Home screen
- `/explore?sort=trending&category=design` → Explore with filters applied
- `/profile/user-123` → User profile, directly
- `/editor?file-id=abc123&page=2` → Editor with specific file and page loaded
- `/settings/notifications` → Settings on Notifications tab

URL structure should mirror information hierarchy. Query params for transient state (filters, sort, pagination). Route params for identity (user ID, file ID, entity ID).

### Adaptive Navigation

**Viewport-Based Strategy**
- **≥1024px (tablet landscape, desktop)**: Sidebar visible, content full-width, sidebar 240-280px wide
- **<1024px (mobile, tablet portrait)**: Sidebar hidden, bottom nav visible, content full-width
- **Reasoning**: Touch interaction (mobile) uses thumb zone efficiency; cursor interaction (desktop) uses viewport space efficiency differently. Users expect these patterns.

**Implementation**
```
@media (max-width: 1023px) {
  aside { display: none; }
  nav.bottom-tabs { display: flex; }
}

@media (min-width: 1024px) {
  aside { display: block; }
  nav.bottom-tabs { display: none; }
}
```

### URL State Synchronization

**Query Params for Transient State**
Filters, tabs, sort order, pagination, search queries belong in query params. When user refreshes, the view should restore exactly as it was. Links should be shareable and maintain context.

**Correct vs Incorrect**
- ❌ User sorts by "Price: High to Low," refresh → sort resets to default
- ✓ URL is `/products?sort=price-desc`, refresh → sort persists
- ❌ User filters "In Stock," clicks another item, back → filters lost
- ✓ URL maintains `?in-stock=true`, back button restores filter
- ❌ User navigates to filtered view, no way to share exact view with colleague
- ✓ User can copy URL with all query params and share; colleague sees identical view

### Modals vs Navigation

**Modals**: Subtasks that return to the original context (confirm dialog, rename form, inline editor)
**Navigation**: Full context shifts (view another user's profile, open a different file, edit detailed settings)

Mixing them breaks the back button's mental model and causes disorientation.

**Correct vs Incorrect**
- ✓ Modal for "Confirm Delete" (user returns to same list)
- ❌ Modal for "Full contact editing form" (should be navigation to /contacts/:id/edit)
- ✓ Navigation to `/settings/notifications` (full context, user expects back to take them out)
- ❌ Navigation overlay for quick rename (should be modal, user expects overlay to close without navigation)

---

## Section 3: QA Patterns

### Deep Link Testing Checklist

- [ ] Every top-level destination reachable directly via URL
- [ ] Every significant screen has a unique, shareable URL
- [ ] Direct navigation to nested screens (e.g., `/settings/notifications`) works without navigation flow
- [ ] Query params match rendered state (filters, sort, pagination)
- [ ] Reload on any deep link restores view exactly

### Back Button State Preservation Testing

- [ ] Scroll position restored after back navigation
- [ ] Applied filters persist after back navigation
- [ ] Pagination state preserved (user on page 3, returns to page 3 after back)
- [ ] Form input in progress preserved (half-filled form remains on back)
- [ ] Active tabs/sections maintained

### Gesture Navigation Compatibility

- [ ] iOS swipe-back (right edge swipe) works on all screens
- [ ] Android predictive back gesture works on all screens
- [ ] Back button behavior consistent with system expectations
- [ ] No screens "trap" users or make back non-functional

### Navigation Consistency Audit

- [ ] Active state styling identical across all pages
- [ ] Label naming patterns consistent (all single words, or all descriptive pairs)
- [ ] Icon set consistent (same style, size, weight)
- [ ] Spacing and sizing uniform (margins, padding, target sizes)
- [ ] Bottom nav items never exceed 5; sidebar items properly grouped if >6
- [ ] No navigation surfaces conflict or overlap at breakpoints

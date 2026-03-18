# Component Architecture Reference

> How the team thinks about UI components — from primitives to product.
>
> **Agent routing:**
> Arc → Section 1 + 2 (plan the component architecture). Pick the primitive layer for the stack.
> Dev → Section 1 + 2 (build rules + patterns). Use primitives, don't rebuild what's solved.
> Pol → Section 1 (audit feel). Keyboard nav, focus states, interaction quality.
> Eye → Section 1 (check visuals). Component consistency against design tokens.
> Test → Section 1 (verify it works). Keyboard nav, screen reader, focus order.
> Crit → Section 1 (check adoption). Can a new user figure this out without help?

---

## Section 1: Composition Thinking (Universal)

Every UI component in your product sits on one of three layers. Understanding
which layer you're working on prevents the two most common mistakes: rebuilding
things that are already solved, and fighting your tools instead of using them.

### The Three Layers

**Layer 1: Primitives** — Behavioral building blocks. Handle accessibility,
keyboard navigation, focus management, ARIA attributes, cross-browser quirks.
Zero styling opinions. You never ship these directly to users — they're
foundations other layers build on.

Examples: a headless dialog that manages focus trapping and escape-to-close,
a headless select that handles arrow keys and screen reader announcements,
a headless tooltip that manages positioning and hover/focus triggers.

**Layer 2: Styled Components** — Primitives with your design system applied.
Colors, typography, spacing, border radius, shadows. These look like your
product but are still reusable across contexts.

Examples: your app's Button (primary, secondary, destructive variants), your
Card component (background, shadow, padding), your Dialog (overlay color,
animation, width).

**Layer 3: Product Components** — Styled components composed into features
specific to your product. These are what users actually interact with. They
combine multiple styled components with business logic.

Examples: a CheckInCard that combines Card + Slider + Button + scoring logic,
a UserProfile that combines Avatar + Badge + Dialog + API calls, a PricingTable
that combines Card + Button + feature list + Stripe integration.

### The Layering Rule

**Your design system (Layer 2) overrides where it has opinions. Primitives
(Layer 1) fill the gaps.**

When building a new feature:
1. Check if your design system already has the component → use it
2. If not, check if a headless primitive handles the behavior → style it to match
3. Only build from scratch when neither layer covers what you need

This means your design system doesn't need to be complete. If you have Button
and Card but not Dialog, reach for a headless Dialog primitive and style it
to match your existing tokens. The primitive handles focus trapping, escape key,
click-outside, screen reader announcements. You handle the look.

### What Primitives Handle (So You Don't Have To)

| Concern | What the primitive does | What you'd have to build manually |
|---------|------------------------|----------------------------------|
| Focus trapping | Keeps focus inside dialogs/modals | Track focusable elements, handle Tab/Shift+Tab, restore focus on close |
| Keyboard navigation | Arrow keys in menus, selects, tabs | Track active index, handle wrapping, manage focus vs selection |
| ARIA attributes | Correct roles, states, properties | Research ARIA spec, test across screen readers, update on state change |
| Screen reader announcements | Live regions, descriptions | Manage aria-live, test VoiceOver + NVDA + JAWS |
| Click outside | Dismiss on outside click | Handle event delegation, portal edge cases, nested popover stacking |
| Positioning | Tooltip/popover placement | Handle viewport overflow, scrolling containers, resize, flip logic |
| Scroll locking | Prevent body scroll when modal open | Handle iOS Safari quirks, preserve scroll position, nested scroll contexts |

If you find yourself writing code for any of these, stop. A primitive already
handles it. Use the primitive.

### When to Build Custom

Build from scratch only when:
- The interaction pattern genuinely doesn't exist in any primitive library
- You need behavior that conflicts with how a primitive works (not just styling)
- The primitive adds more complexity than it removes

"I don't like how the API looks" is not a reason to build custom. "This
primitive assumes single selection but I need multi-select with drag reorder"
might be.

### Anti-Patterns

**Don't fight primitives.** If you're overriding internal behavior, using
`!important` on primitive styles, or monkey-patching event handlers — you
picked the wrong primitive or you're working at the wrong layer.

**Don't mix primitive layers.** Picking Dialog from one library and Select from
another creates inconsistent keyboard behavior, conflicting focus management,
and doubled bundle size. Pick one primitive layer and stick with it.

**Don't rebuild accessibility.** Building your own focus trap, keyboard
navigation, or ARIA management is almost always a mistake. These are deceptively
complex, vary across browsers and screen readers, and break in edge cases you
won't discover until a real user hits them.

**Don't skip the middle layer.** Going straight from primitives to product
components (Layer 1 → Layer 3) means every product component re-implements
styling. Extract the styled version (Layer 2) so your next feature gets it free.

---

## Section 2: Web — Base UI + shadcn (React)

If your stack is React-based, the recommended primitive layer is **Base UI**
with **shadcn/ui** as the styled component layer.

### Why This Stack

**Base UI** (Layer 1) — 35 headless React components from the team behind
Material UI, Radix, and Floating UI. Handles all accessibility, keyboard
navigation, and focus management. Zero styling. Production-backed by MUI.

**shadcn/ui** (Layer 2) — Styled components built on headless primitives, using
Tailwind CSS. You own the code (it's copied into your project, not imported
from node_modules). Supports both Radix and Base UI as the primitive layer.

**Your product components** (Layer 3) — You compose shadcn components with
your business logic to build features.

### How They Connect

```
Base UI (headless primitive)
  ↓ accessibility, keyboard nav, focus management
shadcn/ui (styled component)
  ↓ your design tokens, Tailwind classes
Your ProductComponent (feature)
  ↓ business logic, API calls, state
What the user sees
```

### Base UI Primitives

Base UI components are unstyled by default. They provide behavior through
a render function or slot pattern:

**Key concepts:**
- Components handle behavior and accessibility — you handle rendering and styling
- The `render` prop lets you control the exact HTML output
- CSS classes, Tailwind utilities, or any styling approach works
- No styles to override, no specificity wars, no `!important` hacks

**Available primitives:** AlertDialog, Checkbox, Collapsible, Dialog,
DirectionProvider, Field, Fieldset, Form, Input, Menu, NumberField, Popover,
PreviewCard, Progress, RadioGroup, ScrollArea, Select, Separator, Slider,
Switch, Tabs, TextArea, Toast, Toggle, ToggleGroup, Tooltip.

### Setup: shadcn/ui with Base UI

**Initialize shadcn with Base UI as the primitive layer:**

```bash
npx shadcn@latest init --base base
```

The `--base base` flag selects Base UI instead of Radix. This creates
`components.json` configured for Base UI primitives.

**Then install components as needed:**

```bash
npx shadcn@latest add button dialog select
```

Components are copied into your project — modify freely. Your design tokens
in `globals.css` control the visual output.

shadcn/ui handles the Layer 1 → Layer 2 connection. You focus on Layer 3.

### When to Use Base UI Directly (Skip shadcn)

Sometimes you need a primitive that shadcn doesn't wrap, or you need full
control over the markup. In those cases, use Base UI directly:

- shadcn doesn't have a component for what you need
- You need markup control that shadcn's component doesn't expose
- You're building a design system from scratch (no shadcn)

Style it to match your existing design tokens so it looks consistent with
your shadcn components.

### Native Stacks

If your stack is SwiftUI, Compose, or another native framework — Section 1
applies directly. Native frameworks already use composition (views from
primitives). The thinking is the same:

- Know your platform's primitive layer (SwiftUI views, Compose components, UIKit)
- Build styled components with your design tokens
- Compose into product features
- Don't rebuild what the platform provides

You don't need Base UI or shadcn. The architecture pattern is what transfers.

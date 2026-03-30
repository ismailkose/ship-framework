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

---

## Section 3: shadcn/ui Practical Guide (React Web Stacks)

> **Agent routing:**
> Dev → Full section when building React UI with shadcn.
> Arc → Component catalog table (3.1) when planning which components a feature needs.
> Eye → Review checklist (3.9) when checking shadcn consistency.
> Test → Review checklist (3.9) when verifying form validation and accessibility.

This section covers the practical "how" of building with shadcn/ui. Section 2
covers why we use it and how to set it up. This section covers what's available,
how to customize it, and the patterns Dev uses every day.

### 3.1 Component Catalog

Every shadcn/ui component, grouped by category. Scan this before building
anything custom — the component you need probably already exists.

**Form Components**

| Component | Install | When to use |
|-----------|---------|-------------|
| `button` | `npx shadcn@latest add button` | Any clickable action. 6 variants: default, destructive, outline, secondary, ghost, link. 4 sizes: default, sm, lg, icon |
| `input` | `npx shadcn@latest add input` | Single-line text entry. Supports all HTML input types |
| `textarea` | `npx shadcn@latest add textarea` | Multi-line text entry |
| `label` | `npx shadcn@latest add label` | Accessible form labels. Always pair with inputs |
| `checkbox` | `npx shadcn@latest add checkbox` | Boolean toggle (checked/unchecked) |
| `radio-group` | `npx shadcn@latest add radio-group` | Pick one option from a set |
| `select` | `npx shadcn@latest add select` | Dropdown selection. Sub-components: Trigger, Content, Item, Value |
| `switch` | `npx shadcn@latest add switch` | On/off toggle with visual feedback. Settings, feature flags |
| `slider` | `npx shadcn@latest add slider` | Value from a range. Volume, filters, settings |
| `form` | `npx shadcn@latest add form` | Form wrapper with validation. Best with react-hook-form + zod |
| `input-otp` | `npx shadcn@latest add input-otp` | One-time password / verification code input |
| `toggle` | `npx shadcn@latest add toggle` | Pressable on/off button (like bold/italic in a toolbar) |
| `toggle-group` | `npx shadcn@latest add toggle-group` | Group of toggles — single or multiple selection |

**Layout Components**

| Component | Install | When to use |
|-----------|---------|-------------|
| `card` | `npx shadcn@latest add card` | Container for grouped content. Sub-components: Header, Title, Description, Content, Footer |
| `accordion` | `npx shadcn@latest add accordion` | Collapsible content sections. FAQs, settings panels |
| `tabs` | `npx shadcn@latest add tabs` | Content organized into panels, one visible at a time |
| `collapsible` | `npx shadcn@latest add collapsible` | Show/hide content with animation |
| `separator` | `npx shadcn@latest add separator` | Visual divider between content sections |
| `resizable` | `npx shadcn@latest add resizable` | Resizable panel layout. Split views, adjustable sidebars |
| `aspect-ratio` | `npx shadcn@latest add aspect-ratio` | Maintain width-height ratio (16/9, 4/3) |
| `scroll-area` | `npx shadcn@latest add scroll-area` | Custom scrollbar styling |
| `sidebar` | `npx shadcn@latest add sidebar` | App sidebar with navigation, collapsible groups |

**Overlay Components**

| Component | Install | When to use |
|-----------|---------|-------------|
| `dialog` | `npx shadcn@latest add dialog` | Modal overlay. Confirmations, forms, detail views |
| `alert-dialog` | `npx shadcn@latest add alert-dialog` | Modal for important confirmations. Delete actions, destructive operations |
| `sheet` | `npx shadcn@latest add sheet` | Side panel that slides in. Mobile nav, filters, settings |
| `drawer` | `npx shadcn@latest add drawer` | Bottom drawer for mobile. Mobile-first designs |
| `popover` | `npx shadcn@latest add popover` | Floating content container. Mini forms, tooltips with actions |
| `tooltip` | `npx shadcn@latest add tooltip` | Contextual info on hover. Wrap with TooltipProvider |
| `hover-card` | `npx shadcn@latest add hover-card` | Rich content card on hover. User previews, link previews |

**Navigation Components**

| Component | Install | When to use |
|-----------|---------|-------------|
| `navigation-menu` | `npx shadcn@latest add navigation-menu` | Main site navigation with dropdowns |
| `breadcrumb` | `npx shadcn@latest add breadcrumb` | Current page location in hierarchy |
| `pagination` | `npx shadcn@latest add pagination` | Navigate through pages of content |
| `command` | `npx shadcn@latest add command` | Command palette with search and keyboard nav. Uses cmdk |
| `dropdown-menu` | `npx shadcn@latest add dropdown-menu` | Action menu with items, checkboxes, radio groups |
| `context-menu` | `npx shadcn@latest add context-menu` | Right-click menu |
| `menubar` | `npx shadcn@latest add menubar` | Horizontal menu bar (File, Edit, View) |

**Feedback Components**

| Component | Install | When to use |
|-----------|---------|-------------|
| `alert` | `npx shadcn@latest add alert` | Important messages. Variants: default, destructive |
| `sonner` | `npx shadcn@latest add sonner` | Toast notifications. Temporary messages, success/error feedback |
| `progress` | `npx shadcn@latest add progress` | Visual indicator of completion (0-100) |
| `skeleton` | `npx shadcn@latest add skeleton` | Loading placeholder with animation |

**Data Display Components**

| Component | Install | When to use |
|-----------|---------|-------------|
| `table` | `npx shadcn@latest add table` | Structured data in rows and columns. Pair with @tanstack/react-table |
| `badge` | `npx shadcn@latest add badge` | Status indicators, tags, notifications |
| `avatar` | `npx shadcn@latest add avatar` | User profile images with fallback |
| `calendar` | `npx shadcn@latest add calendar` | Date selection interface. Uses react-day-picker |
| `carousel` | `npx shadcn@latest add carousel` | Slideshow. Uses embla-carousel-react |
| `chart` | `npx shadcn@latest add chart` | Data visualization. Built on Recharts |

**46 components total.** If what you need isn't in this list, check Section 1 —
use a Base UI primitive directly and style it to match.

### 3.2 Install Bundles

Don't install one component at a time. Use these bundles to set up entire
categories at once:

```bash
# Essential forms (covers 90% of form needs)
npx shadcn@latest add form input label button select checkbox radio-group switch textarea

# Data display
npx shadcn@latest add table badge avatar progress skeleton calendar

# Overlays and modals
npx shadcn@latest add dialog sheet popover tooltip alert-dialog drawer

# Navigation
npx shadcn@latest add navigation-menu breadcrumb pagination command dropdown-menu

# Layout
npx shadcn@latest add card accordion tabs separator sidebar

# Feedback
npx shadcn@latest add alert sonner progress skeleton
```

Install what the feature needs, not everything. Each component is copied into
your project — only install what you'll use.

### 3.3 Theming System (CSS Variables)

shadcn/ui uses HSL CSS variables for all colors. Every color has a base value
and a `-foreground` variant for text that sits on top of it.

**The color roles** (in `globals.css` or `app/globals.css`):

```css
:root {
  --background: 0 0% 100%;          /* Page background */
  --foreground: 222.2 84% 4.9%;     /* Primary text */

  --primary: 221.2 83.2% 53.3%;     /* Brand color — buttons, links, accents */
  --primary-foreground: 210 40% 98%; /* Text on primary backgrounds */

  --secondary: 210 40% 96.1%;       /* Secondary actions, subtle backgrounds */
  --secondary-foreground: 222.2 47.4% 11.2%;

  --muted: 210 40% 96.1%;           /* Muted backgrounds, disabled states */
  --muted-foreground: 215.4 16.3% 46.9%;

  --accent: 210 40% 96.1%;          /* Hover highlights, selected states */
  --accent-foreground: 222.2 47.4% 11.2%;

  --destructive: 0 84.2% 60.2%;     /* Errors, delete actions, danger */
  --destructive-foreground: 210 40% 98%;

  --border: 214.3 31.8% 91.4%;      /* Border color */
  --input: 214.3 31.8% 91.4%;       /* Input border color */
  --ring: 221.2 83.2% 53.3%;        /* Focus ring color */

  --radius: 0.5rem;                  /* Global border radius */
}
```

**Dark mode** — add a `.dark` class with overridden values:

```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;
  /* ... override all roles for dark mode */
}
```

**HSL format:** `hue saturation% lightness%` — note there are no commas and no
`hsl()` wrapper. shadcn applies the wrapper in Tailwind via `hsl(var(--primary))`.

**Connecting to your design system:** When the founder fills in Color Tokens
in `references/design-system.md`, map those tokens to these CSS variable roles
in `globals.css`. The design system defines the *what* (brand blue, error red),
the CSS variables define the *where* (primary, destructive).

**Dark mode toggle** (Next.js with `next-themes`):

```bash
npm install next-themes
```

```tsx
// app/providers.tsx
"use client"
import { ThemeProvider } from "next-themes"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  )
}

// Wrap in app/layout.tsx:
// <html suppressHydrationWarning> <body> <Providers>{children}</Providers> </body> </html>
```

**Common mistakes:**

❌ Hardcoding hex colors in components:
```tsx
<div className="bg-[#3b82f6] text-white">
```

✅ Using CSS variable roles:
```tsx
<div className="bg-primary text-primary-foreground">
```

❌ Putting `hsl()` in the CSS variable value:
```css
--primary: hsl(221.2, 83.2%, 53.3%); /* WRONG — double-wraps */
```

✅ Raw HSL values without wrapper:
```css
--primary: 221.2 83.2% 53.3%; /* RIGHT — Tailwind adds hsl() */
```

### 3.4 The `cn()` Utility

Every shadcn component uses `cn()` for class merging. It combines `clsx`
(conditional classes) with `tailwind-merge` (intelligent Tailwind conflict
resolution).

```ts
// lib/utils.ts (created by shadcn init)
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**Why it matters:** Without `tailwind-merge`, conflicting classes stack instead
of replacing. `cn()` ensures the last class wins:

❌ String concatenation (class conflicts):
```tsx
// Both p-4 and p-2 end up in the DOM — browser picks one unpredictably
<div className={`p-4 ${className}`}>  {/* if className="p-2" */}
```

✅ Using `cn()` (intelligent merge):
```tsx
// tailwind-merge resolves: p-2 wins over p-4
<div className={cn("p-4", className)}>  {/* if className="p-2" → "p-2" */}
```

Use `cn()` in every component that accepts a `className` prop.

### 3.5 CVA Variant Pattern

shadcn uses `class-variance-authority` (CVA) for component variants. When you
need to add a new variant to an existing component, edit the CVA definition
in `components/ui/`:

**Adding a custom variant to Button:**

```tsx
// components/ui/button.tsx — add to the existing variants
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        // ADD YOUR CUSTOM VARIANT:
        success: "bg-green-600 text-white hover:bg-green-700",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
        // ADD YOUR CUSTOM SIZE:
        xl: "h-12 rounded-md px-10 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

Usage: `<Button variant="success" size="xl">Save</Button>`

**The TypeScript interface** — always extend `VariantProps` so custom variants
are type-safe:

```tsx
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}
```

**Rule:** Edit `components/ui/` for *visual variants* (new colors, sizes).
Create wrapper components for *behavior changes* (loading state, confirmation).

### 3.6 Composite Component Pattern

When you need to add behavior (not just styling), create a wrapper in
`components/` — don't modify `components/ui/`.

**File structure:**
```
components/
  ui/          ← shadcn owns these (variants only)
    button.tsx
    dialog.tsx
  [your-wrappers]/  ← you own these (behavior)
    loading-button.tsx
    confirm-dialog.tsx
```

**Example — LoadingButton:**

```tsx
// components/loading-button.tsx
import { Button, type ButtonProps } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

interface LoadingButtonProps extends ButtonProps {
  loading?: boolean
}

export function LoadingButton({
  loading,
  children,
  disabled,
  ...props
}: LoadingButtonProps) {
  return (
    <Button disabled={loading || disabled} {...props}>
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </Button>
  )
}
```

**Why not modify Button directly?** Because `npx shadcn@latest add button`
would overwrite your changes. Wrappers survive component updates.

### 3.7 Form Integration (react-hook-form + zod)

This is the #1 pattern Dev builds. shadcn's `<Form>` component wraps
react-hook-form with accessible labels, descriptions, and error messages.

**Install:**
```bash
npx shadcn@latest add form input label button
npm install react-hook-form zod @hookform/resolvers
```

**The pattern:**

```tsx
"use client"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
  Form, FormControl, FormDescription,
  FormField, FormItem, FormLabel, FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

// 1. Define schema
const formSchema = z.object({
  email: z.string().email("Invalid email address"),
  name: z.string().min(2, "Name must be at least 2 characters"),
})

// 2. Infer types from schema
type FormValues = z.infer<typeof formSchema>

// 3. Build the form
export function SignupForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: "", name: "" },
  })

  function onSubmit(values: FormValues) {
    // values is fully typed: { email: string, name: string }
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="Your name" {...field} />
              </FormControl>
              <FormDescription>Your public display name.</FormDescription>
              <FormMessage /> {/* Shows zod error automatically */}
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="you@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Sign up</Button>
      </form>
    </Form>
  )
}
```

**Key points:**
- Zod schema is the single source of truth for validation
- `FormMessage` auto-displays the zod error for its field
- `FormLabel` is automatically connected to its `FormControl` for accessibility
- Type inference means no manual `FormValues` interface — derive from schema

**Common mistakes:**

❌ Manual validation in onSubmit:
```tsx
function onSubmit(values) {
  if (!values.email.includes("@")) { setError("Bad email") }
}
```

✅ Zod schema handles validation:
```tsx
const schema = z.object({
  email: z.string().email("Invalid email"),
})
// FormMessage shows errors automatically — no manual setError
```

### 3.8 Blocks (Pre-Built UI Patterns)

shadcn provides complete pre-built blocks — full page sections you can install
and customize. Categories include: dashboard layouts, authentication forms,
sidebar navigation, calendar interfaces, e-commerce product displays.

**When to use blocks vs. building from components:**
- Use blocks when you need a complete page section quickly (login form, dashboard layout)
- Build from components when you need something blocks don't cover or when you want full control

Blocks are starting points, not final code. Install one, then customize it to
match your product. They follow the same theming system — your CSS variables
apply automatically.

### 3.9 Review Checklist (for Eye and Test)

When reviewing a React project using shadcn/ui:

**Theming consistency:**
- [ ] All colors use CSS variable roles (`bg-primary`), not hardcoded hex (`bg-[#3b82f6]`)
- [ ] Dark mode variables defined in `.dark` class in `globals.css`
- [ ] `--radius` set once, consistent across all components
- [ ] Color roles used semantically (destructive for errors, not primary in red)

**Component quality:**
- [ ] `cn()` used for all dynamic className merging (no string concatenation)
- [ ] Custom variants use CVA pattern with TypeScript interfaces
- [ ] Behavior wrappers in `components/` (not modifications to `components/ui/`)
- [ ] No components rebuilt from scratch when a shadcn component exists (check catalog 3.1)

**Form validation:**
- [ ] Forms use shadcn Form + react-hook-form + zod (not manual validation)
- [ ] Every input has a `FormLabel` (accessibility)
- [ ] `FormMessage` present on every field (error display)
- [ ] Zod schema validates on both client and server where applicable

**Accessibility:**
- [ ] All interactive components have visible focus indicators (focus ring)
- [ ] `TooltipProvider` wraps the app when using tooltips
- [ ] Alert dialogs used for destructive confirmations (not regular dialogs)
- [ ] Form errors announced to screen readers via `FormMessage` aria attributes

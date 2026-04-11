# Web Accessibility Reference

> Agent routing:
> Dev → Sections 1-2 (implement accessible components: semantic HTML, ARIA, focus management)
> Crit → Section 2 (review: semantic elements, keyboard nav, screen reader labels, contrast)
> Pol → Section 2 (audit accessibility compliance)
> Test → Section 3 (QA: keyboard flow, screen reader testing, skip link, focus management)
> Arc → Section 1 (plan accessible architecture from the start)

---

## Section 1: Semantic HTML Foundation

### Why Semantic Elements Matter

Semantic HTML elements communicate structure and meaning to browsers and assistive technologies (screen readers, voice control, magnifiers). When you use the right element, you get **behavior for free**: keyboard support, focus management, screen reader announcements, and ARIA role inheritance. This reduces bugs and maintenance burden.

**The core principle**: Use the most specific HTML element that describes your content's meaning. This is cheaper and more reliable than rebuilding semantics with divs and ARIA.

### Element Decision Tree

Choose your element based on purpose:

**Interactive actions** → `<button>`
- User triggers an action on the current page
- Examples: submit form, open modal, toggle state
- Automatic: keyboard (Enter, Space), focus management, semantic role

**Navigation links** → `<a>` or framework Link component
- User navigates to a new URL or page section
- Examples: nav menu, breadcrumb, "Learn More" link
- Automatic: keyboard (Enter), focus, underline affordance

**Page landmarks** → `<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<section>`
- Structure the page into meaningful regions
- `<nav>`: primary or secondary navigation
- `<main>`: page's primary content (one per page)
- `<header>`: introductory content (not to be confused with `<head>`)
- `<footer>`: footer content, often repeated (site-wide or section-specific)
- `<article>`: self-contained composition (blog post, comment, card)
- `<section>`: thematic grouping of content (chapters, tabs, filter results)
- Screen readers announce landmarks and allow users to jump between them

**Form controls** → `<input>`, `<textarea>`, `<select>`, `<label>`
- Always pair with `<label for="id">` (not placeholder as substitute)
- Group with `<fieldset>` and `<legend>` for radio/checkbox groups
- Use `type` attribute correctly (email, password, number, date, etc.)

### Why `<div onClick>` Is Dangerous

A div with a click handler feels interactive but breaks accessibility:

```html
<!-- ❌ BROKEN: Custom button -->
<div onClick={handleClick} style={{cursor: 'pointer'}}>
  Delete Account
</div>
```

What's missing:
- **No keyboard support**: Click handler fires on mouse click only. Tab users can't reach it. Enter/Space don't work.
- **No focus ring**: Invisible to keyboard users. No visual affordance.
- **No screen reader announcement**: Screenreader says "div" with no context. User doesn't know it's interactive.
- **No spacebar/Enter activation**: You'd have to manually add `onKeyDown`, trap codes, manage focus state yourself.
- **Fragile**: Each missing feature is a bug waiting to happen.

```html
<!-- ✅ CORRECT: Semantic button -->
<button onClick={handleClick}>
  Delete Account
</button>
```

Automatic:
- Keyboard support (Enter, Space)
- Visible focus ring (with focus-visible)
- Announced as "button" with label by screen readers
- Native activation behavior

---

## Section 2: ARIA & Focus Patterns

### ARIA as Last Resort

ARIA (Accessible Rich Internet Applications) lets you patch semantics when HTML can't express what you need. But ARIA is a bandage—use it only when semantic HTML doesn't fit.

**ARIA Rule of Thumb**:
1. First: Is there a semantic HTML element? Use it.
2. Second: Can you restructure to use semantic HTML? Do it.
3. Last: Does HTML genuinely lack the expressiveness? Use ARIA.

Violating this rule creates maintenance debt and screen reader confusion.

### Icon Button Pattern

An icon-only button (no visible text) requires `aria-label` or `aria-labelledby` to announce its purpose to screen reader users.

```jsx
// ❌ INACCESSIBLE: Screen reader says "button" (no label context)
<button onClick={deleteItem}>
  <TrashIcon />
</button>

// ✅ ACCESSIBLE: aria-label provides screen reader label
<button onClick={deleteItem} aria-label="Delete item">
  <TrashIcon />
</button>

// ✅ ALSO ACCEPTABLE: Visible text alternative (tooltip on hover)
<button onClick={deleteItem} title="Delete item">
  <TrashIcon />
</button>
```

**Why aria-label is mandatory for icon-only buttons**: Screen readers announce the element's accessible name. Without it, users get "button" alone—no context about what clicking it does.

### Decorative Elements

Images, icons, and dividers that are purely visual must not be announced to screen readers.

```jsx
// ❌ Screen reader reads "image, star" (noise)
<img src="star.svg" alt="star" />

// ✅ Decorative icon ignored by screen readers
<img src="star.svg" alt="" aria-hidden="true" />

// ✅ SVG icon (common pattern)
<svg aria-hidden="true" focusable="false">
  <use href="#star-icon" />
</svg>
```

Use `alt=""` for images that are decorative. Use `aria-hidden="true"` for SVG icons, dividers, or spacing elements that don't add semantic meaning.

### ARIA Live Regions

For dynamic content (toasts, status updates, alerts), use `aria-live` to announce changes without moving focus.

```jsx
// Toast notification: announce immediately
<div aria-live="polite" aria-atomic="true" role="status">
  {toastMessage}
</div>

// Alert: announce with urgency
<div aria-live="assertive" aria-atomic="true" role="alert">
  Error: Please correct the form.
</div>
```

- `aria-live="polite"`: Announce when users finish current action (status, confirmation)
- `aria-live="assertive"`: Announce immediately (errors, critical alerts)
- `aria-atomic="true"`: Announce the entire region (not just the delta)

### Focus Management Patterns

**Modal opens**: Move focus to the first focusable element inside the modal (usually a heading or close button), or to a specific element. Don't leave it on the trigger.

**Modal closes**: Return focus to the trigger element (button that opened the modal). This prevents keyboard users from losing their place.

**Route change**: Move focus to the page's main content (usually the `<main>` heading or a skip link target). Don't leave it at the old scroll position.

```jsx
const Modal = ({ isOpen, onClose }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Move focus into modal
      modalRef.current.focus();
    } else if (!isOpen) {
      // Return focus to trigger (you'd track this separately)
      triggerRef.current?.focus();
    }
  }, [isOpen]);

  return (
    <div ref={modalRef} tabIndex={-1} role="dialog">
      {/* modal content */}
    </div>
  );
};
```

### Focus-Visible vs Focus

Use `focus-visible` for the focus ring, not `focus`. `focus-visible` shows a ring only for keyboard navigation (not mouse clicks), reducing visual noise.

```css
/* ❌ Shows focus ring on mouse click (unwanted) */
button:focus {
  outline: 2px solid blue;
}

/* ✅ Shows focus ring only for keyboard users */
button:focus-visible {
  outline: 2px solid blue;
  outline-offset: 2px;
}
```

**Contrast for focus ring**: Ensure the focus ring has sufficient contrast (4.5:1 minimum). A thin outline on a light background may fail.

### Skip Link

A skip link is the first focusable element on the page. It lets keyboard users jump over repeated navigation and go straight to the main content.

```html
<!-- First element in <body>, before <nav> -->
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<nav>
  <!-- Navigation items -->
</nav>

<main id="main-content">
  <!-- Page content -->
</main>
```

```css
/* Hide visually but keep accessible */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

---

## Section 3: QA Patterns

### Full Keyboard Navigation Test

Keyboard-only users should be able to reach and activate every interactive element.

**Test steps**:
1. Tab through the entire page. Every button, link, form input, and interactive element must be focusable.
2. Verify tab order makes sense (left-to-right, top-to-bottom). No jumps or loops.
3. Check focus ring visibility. If you can't see where focus is, it fails.
4. Activate elements with keyboard:
   - **Button, link, input**: Enter or Space
   - **Form select**: Arrow keys to navigate options, Enter to select
   - **Modal**: Trap focus (Tab doesn't escape). Esc closes it.
5. Verify focus returns to the trigger after dismissing a modal or overlay.

**Common issues**:
- Click-only handlers (divs, spans with onClick) skip keyboard users
- Modals without focus traps (Tab escapes the modal)
- Invisible focus rings (e.g., `outline: none` with no replacement)

### Screen Reader Test

Use NVDA (Windows), JAWS (Windows, paid), or VoiceOver (macOS, free).

**Test steps**:
1. Launch the screen reader.
2. Navigate the page using:
   - **Arrow keys**: Read line by line
   - **H**: Jump to next heading
   - **L**: Jump to next list
   - **B**: Jump to next button
   - **N**: Jump to next nav landmark
   - **R**: Jump to next region/section
3. Check announcements:
   - Headings are announced with level (Heading 1, Heading 2, etc.)
   - Buttons have labels ("Delete", "Submit", not just "icon")
   - Links have descriptive text (not "Click here")
   - Form inputs have labels paired with `<label for="id">`
   - Icons have meaningful alt text or aria-labels
   - Decorative elements are hidden (aria-hidden="true" or alt="")
4. Test form submission and error messages. Errors should be announced in aria-live regions.

**Common issues**:
- Icon-only buttons without aria-labels announced as "button" (no context)
- Links saying "Click here" or "More" (meaningless out of context)
- Form inputs without labels (screen reader can't associate input with question)
- Decorative images announced (noise)
- Error messages not in aria-live regions (users miss them)

### Skip Link Verification

1. Load the page.
2. Press Tab once. The skip link must be visible and focusable.
3. Press Enter. Focus must move to the main content area.
4. Verify the skip link is the very first focusable element (before nav).

**Common issue**: Skip link is present but not the first focusable element, or not visible on focus.

### Focus Trap in Modals

Modals must not let Tab escape.

**Test steps**:
1. Open a modal.
2. Tab repeatedly. Focus should cycle within the modal (last element → first element).
3. Focus should never move to the page behind the modal.
4. Esc should close the modal and return focus to the trigger.

**Implementation**: Use a modal library with built-in focus management (React Modal, Headless UI, Radix), or manually manage with refs and onKeyDown.

### Focus Return on Modal Close

After closing a modal, focus must return to the element that opened it.

**Test steps**:
1. Click a button to open a modal.
2. Close the modal (click close button, press Esc, click outside).
3. Verify focus is back on the open button.

**Why it matters**: Keyboard users need to know where they are after the modal closes. Without focus return, they're lost.

### Heading Hierarchy Check

Headings must follow a logical hierarchy (H1 → H2 → H3). No skipping levels (H1 → H3).

**Test steps**:
1. Use a tool (axe DevTools, WAVE, Lighthouse) or manually check HTML.
2. Verify:
   - Only one H1 per page
   - Headings don't skip levels (e.g., H1 → H2 → H3, not H1 → H3)
   - Headings describe sections (not styled as headings)

**Example**:
```html
<!-- ✅ Correct hierarchy -->
<h1>Page Title</h1>
<h2>Section 1</h2>
<h3>Subsection 1.1</h3>
<h2>Section 2</h2>

<!-- ❌ Skipped level (breaks outline) -->
<h1>Page Title</h1>
<h3>Subsection (missing h2)</h3>
```

### Contrast Verification

Text must have sufficient contrast with its background (4.5:1 for normal text, 3:1 for large text).

**Test steps**:
1. Use a contrast checker (WebAIM, Axe, or browser DevTools).
2. Check all text colors against backgrounds, including:
   - Form placeholders
   - Focus rings
   - Disabled button text
   - Links (default and hover state)

**Common issues**:
- Gray text on light background (insufficient contrast)
- Focus ring too thin or low contrast
- Hover state text not contrasted properly

---

## Quick Reference

| Pattern | Element | Keyboard | Screen Reader | Notes |
|---------|---------|----------|---------------|-------|
| Action | `<button>` | Enter, Space | "Button: [label]" | Default choice for clicks |
| Navigation | `<a>` | Enter | "Link: [text]" | Use for URLs, sections |
| Landmark | `<nav>`, `<main>` | Tab stops | "Navigation", "Main" | Structure the page |
| Form input | `<input>`, `<label>` | Tab, Arrow | "Edit text: [label]" | Always pair with label |
| Icon button | `<button aria-label="...">` | Enter, Space | "Button: [aria-label]" | aria-label required |
| Skip link | `<a href="#main">` | Tab (first) | "Link: Skip to main" | Must be first focusable |
| Modal | `<div role="dialog">` | Tab (trapped) | "Dialog: [title]" | Trap focus, return on close |
| Live region | `<div aria-live="polite">` | Not needed | Announces changes | For toasts, status updates |


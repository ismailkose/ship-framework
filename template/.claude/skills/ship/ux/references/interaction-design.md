# Interaction Design Reference

> Every interactive element has 8 possible states. If you haven't designed all 8, you've designed an incomplete component. This reference teaches the state model, micro-interaction patterns, and gesture design that separate polished interfaces from prototypes.
>
> **Agent routing:**
> Dev → Sections 1-3 (implement all 8 states, wire micro-interactions, build gesture handlers)
> Pol → Sections 1-2 (audit state coverage and micro-interaction consistency)
> Arc → Section 3 (gesture model affects screen architecture and navigation)
> Eye → Sections 1-2 (visually verify every state renders correctly, animation timing feels right)
> Crit → Section 1 (missing states = accessibility failures; disabled and error states are where users get stuck)
>
> **Relationship to other references:**
> - `touch-interaction.md` covers tap targets, safe areas, and haptics (the physical layer)
> - This file covers interaction states, micro-interactions, and gesture design (the behavioral layer)
> - `animation.md` covers timing curves and motion principles (the motion layer)
> - Read all three together for complete interaction coverage.

---

## Section 1: The 8 Interactive States Model

Every interactive element — buttons, inputs, cards, toggles, links — exists in one of 8 states at any moment. Designing only the default and hover states (the AI default) leaves 75% of the interaction unfinished.

### The States

1. **Default** — Resting appearance. No interaction happening. This is what users see first.
2. **Hover** — Pointer is over the element (desktop only). Signals "this is interactive."
3. **Focus** — Element has keyboard or assistive-tech focus. Must be visible — this is how keyboard users navigate.
4. **Active / Pressed** — Element is being clicked or tapped. The moment of engagement.
5. **Disabled** — Element exists but can't be used right now. Must look obviously non-interactive.
6. **Loading** — Action triggered, waiting for result. User needs to know something is happening.
7. **Error** — Something went wrong. User needs to know what and how to fix it.
8. **Success** — Action completed. Confirmation that it worked.

### Why All 8 Matter

Missing states cause real user problems:

- **No focus state** → keyboard users can't tell where they are. WCAG 2.4.7 failure.
- **No loading state** → users click again, causing double-submits.
- **No disabled state** → users click a non-functional button and think the app is broken.
- **No error state** → users don't know what went wrong or how to fix it.
- **No success state** → users don't know if their action worked.

### Implementation Pattern

```css
/* Button: all 8 states defined */
.button {
  /* 1. Default */
  background: var(--color-primary);
  color: var(--color-primary-foreground);
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  cursor: pointer;
  transition: background 150ms ease, transform 100ms ease, box-shadow 150ms ease;
}

/* 2. Hover (pointer devices only) */
@media (hover: hover) {
  .button:hover:not(:disabled) {
    background: var(--color-primary-hover);
  }
}

/* 3. Focus (keyboard navigation) */
.button:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
}

/* 4. Active / Pressed */
.button:active:not(:disabled) {
  transform: scale(0.97);
  background: var(--color-primary-active);
}

/* 5. Disabled */
.button:disabled {
  background: var(--color-muted);
  color: var(--color-muted-foreground);
  cursor: not-allowed;
  opacity: 0.6;
}

/* 6. Loading — via data attribute or class */
.button[data-loading="true"] {
  pointer-events: none;
  position: relative;
  color: transparent; /* hide text, keep width */
}

.button[data-loading="true"]::after {
  content: "";
  position: absolute;
  inset: 0;
  margin: auto;
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 600ms linear infinite;
}

/* 7. Error */
.button[data-state="error"] {
  background: var(--color-error);
  animation: shake 300ms ease;
}

/* 8. Success */
.button[data-state="success"] {
  background: var(--color-success);
}
```

### React Pattern: State Machine for Buttons

```tsx
type ButtonState = "idle" | "hover" | "loading" | "success" | "error";

function ActionButton({ onClick, children }) {
  const [state, setState] = useState<ButtonState>("idle");

  async function handleClick() {
    if (state === "loading") return; // prevent double-click
    setState("loading");
    try {
      await onClick();
      setState("success");
      setTimeout(() => setState("idle"), 1500); // reset after feedback
    } catch {
      setState("error");
      setTimeout(() => setState("idle"), 2000);
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={state === "loading"}
      data-state={state}
      data-loading={state === "loading"}
    >
      {state === "loading" && <Spinner size={16} />}
      {state === "success" && <CheckIcon size={16} />}
      {state === "error" && <XIcon size={16} />}
      {state === "idle" && children}
    </button>
  );
}
```

### Input Field: All 8 States

```css
.input {
  /* 1. Default */
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 10px 12px;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}

/* 2. Hover */
@media (hover: hover) {
  .input:hover:not(:disabled):not(:focus) {
    border-color: var(--color-border-hover);
  }
}

/* 3. Focus */
.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

/* 4. Active (being typed into — same as focus for inputs) */

/* 5. Disabled */
.input:disabled {
  background: var(--color-muted-bg);
  color: var(--color-muted-foreground);
  cursor: not-allowed;
}

/* 6. Loading (async validation in progress) */
.input[data-validating="true"] {
  background-image: url("spinner.svg");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
}

/* 7. Error */
.input[aria-invalid="true"] {
  border-color: var(--color-error);
  box-shadow: 0 0 0 3px var(--color-error-light);
}

/* 8. Success (validated) */
.input[data-valid="true"] {
  border-color: var(--color-success);
}
```

### The State Coverage Audit

Before shipping any interactive component, run this check:

| State | Button | Input | Card | Toggle | Link |
|-------|--------|-------|------|--------|------|
| Default | ✓ | ✓ | ✓ | ✓ | ✓ |
| Hover | ✓ | ✓ | ✓ | ✓ | ✓ |
| Focus | ✓ | ✓ | ✓ | ✓ | ✓ |
| Active | ✓ | ✓ | ✓ | ✓ | ✓ |
| Disabled | ✓ | ✓ | — | ✓ | — |
| Loading | ✓ | ✓ | ✓ | — | — |
| Error | ✓ | ✓ | ✓ | — | — |
| Success | ✓ | ✓ | — | — | — |

Not every component needs all 8. Cards don't have disabled states. Links don't have loading states. But if a state is possible, it must be designed.

---

## Section 2: Micro-Interactions

Micro-interactions are the small, single-purpose animations that give interfaces life. They're not decoration — they communicate state change, provide feedback, and guide attention.

### The 4 Parts of a Micro-Interaction

Every micro-interaction has: **Trigger → Rules → Feedback → Loops/Modes**

1. **Trigger** — What starts it (user action or system event)
2. **Rules** — What happens (the logic)
3. **Feedback** — What the user sees/feels (the animation)
4. **Loops/Modes** — Does it repeat or change over time

### Essential Micro-Interactions (Build These First)

**Toggle switch:**
- Trigger: tap/click
- Feedback: thumb slides (150ms ease-out), track color transitions (200ms)
- State change must be visible within 100ms of interaction

```css
.toggle-thumb {
  transition: transform 150ms ease-out;
}
.toggle-track {
  transition: background-color 200ms ease;
}
.toggle[data-state="on"] .toggle-thumb {
  transform: translateX(20px);
}
```

**Button press:**
- Trigger: mousedown/touchstart
- Feedback: scale to 0.97 (100ms), background darkens
- Release: scale back to 1.0 (150ms ease-out)
- Purpose: confirms the press registered before the action completes

**Form submission:**
- Trigger: submit action
- Feedback sequence: button → loading spinner (immediate) → success checkmark (on complete) → text change ("Saved!")
- The sequence should flow, not jump between states

**Notification entry:**
- Trigger: system event
- Feedback: slide in from top or bottom (200ms ease-out), sit for 3-5s, slide out (150ms ease-in)
- Must respect `prefers-reduced-motion`: replace slide with fade

**Skeleton loading:**
- Trigger: data fetch begins
- Feedback: placeholder shapes matching content layout, shimmer animation (1.5s linear infinite)
- Purpose: sets spatial expectations so content doesn't jump when it loads

### Micro-Interaction Timing Guide

| Interaction | Duration | Easing | Notes |
|-------------|----------|--------|-------|
| Button press | 100ms | ease | Scale down on press |
| Button release | 150ms | ease-out | Scale back to normal |
| Toggle switch | 150ms | ease-out | Thumb translation |
| Color transition | 200ms | ease | Background, border changes |
| Notification enter | 200ms | ease-out | Slide or fade in |
| Notification exit | 150ms | ease-in | Faster out than in |
| Skeleton shimmer | 1500ms | linear | Infinite loop |
| Page transition | 200-300ms | ease-in-out | Content swap |
| Modal open | 200ms | ease-out | Scale from 0.95 + fade |
| Modal close | 150ms | ease-in | Faster close than open |

**Key principle:** Exits are faster than entrances. Users want to see new content arrive (worth watching); they want old content to leave quickly (get out of the way).

### What NOT to Micro-Interact

Not everything needs animation. Over-animation is as bad as no animation.

**Skip micro-interactions for:**
- Static text and headings
- Non-interactive images
- Layout shifts (these should be instant)
- Scroll position changes (use native smooth scroll)
- Repeated rapid actions (typing, scrolling, dragging) — animate the result, not every frame

**Rule of thumb:** If the user does something → animate feedback. If the system changes layout → don't animate.

---

## Section 3: Gesture Design Patterns

Gestures extend touch interaction beyond simple taps. They add efficiency for experienced users while remaining invisible to beginners. Every gesture must have a visible alternative.

### Gesture Complexity Hierarchy

Simpler gestures are more discoverable. Design from simple to complex:

1. **Tap** — Universal. Everyone knows this.
2. **Long press** — Discoverable through experimentation. Use for context menus.
3. **Swipe** — Natural on lists. Use for delete, archive, reveal actions.
4. **Drag** — Reorder, move. Needs a visible handle affordance.
5. **Pinch** — Zoom. Expected on images and maps.
6. **Rotate** — Rare. Only for images and specific tools.
7. **Multi-finger** — Expert only. Never for primary actions.

### Swipe Actions: The Rules

Swipe-to-reveal is powerful but must follow conventions:

**Left swipe** → destructive or secondary actions (delete, archive)
**Right swipe** → constructive or primary actions (mark done, pin, star)

This convention comes from iOS Mail. Users have internalized it. Breaking it causes confusion.

```tsx
// Swipe pattern with visible alternative
function ListItem({ item, onDelete, onArchive }) {
  return (
    <SwipeableRow
      leftAction={{ label: "Archive", color: "blue", onTrigger: onArchive }}
      rightAction={{ label: "Delete", color: "red", onTrigger: onDelete }}
    >
      <div className={styles.content}>
        <span>{item.title}</span>
        {/* Visible alternative: overflow menu */}
        <OverflowMenu actions={[
          { label: "Archive", action: onArchive },
          { label: "Delete", action: onDelete, destructive: true }
        ]} />
      </div>
    </SwipeableRow>
  );
}
```

### Drag Affordance: Always Show the Handle

Draggable elements need a visible handle. Without it, users don't know dragging is possible, and they accidentally trigger drags when trying to scroll.

```tsx
// Correct — visible drag handle
<div className={styles.draggableItem}>
  <GripIcon className={styles.dragHandle} aria-label="Drag to reorder" />
  <span>{item.label}</span>
</div>

// Incorrect — entire row is draggable, no visual cue
<div draggable className={styles.item}>
  <span>{item.label}</span>
</div>
```

### Long Press: Timing and Feedback

Long press triggers at **500ms** (platform convention). The user needs progressive feedback:

- **0-200ms**: nothing (prevents accidental triggers)
- **200-500ms**: subtle visual change (slight scale or highlight) signals "keep holding"
- **500ms**: action triggers, haptic confirmation

```css
/* Progressive long-press feedback */
.long-pressable {
  transition: transform 300ms ease;
}

.long-pressable[data-pressing="true"] {
  transform: scale(0.97);
  background: var(--color-surface-hover);
}

.long-pressable[data-long-pressed="true"] {
  transform: scale(1.0);
  /* context menu appears, haptic fires */
}
```

### Gesture Discoverability

Gestures are invisible by default. Help users discover them:

**First-time hints:** Show a one-time tooltip or animation demonstrating the gesture. "Swipe left to delete" with a ghost animation. Show once, then never again.

**Visual affordances:**
- Drag handles (grip dots icon) → "this can be dragged"
- Peek-through on swipe (colored background visible at rest) → "there's something behind this"
- Pull-to-refresh indicator at top → "pull down to refresh"

**Progressive reveal:** Start with buttons. As users become comfortable, mention gestures as shortcuts. "Tip: You can also swipe left to delete."

### Gesture + Keyboard Parity

Every gesture must have a keyboard equivalent:

| Gesture | Keyboard Equivalent |
|---------|-------------------|
| Tap | Enter or Space |
| Long press | Context menu key or Shift+F10 |
| Swipe to delete | Delete or Backspace key |
| Drag to reorder | Arrow keys with modifier (Alt+↑/↓) |
| Pinch to zoom | Ctrl/Cmd + / Ctrl/Cmd - |
| Pull to refresh | F5 or Ctrl/Cmd+R |

If a gesture can't have a keyboard equivalent, it must have a visible button alternative.

---

## Audit Checklist

**State coverage:**
- [ ] Every interactive component has all applicable states defined
- [ ] Focus states are visible and meet 3:1 contrast (WCAG 2.4.11)
- [ ] Disabled states are obviously non-interactive (not just grayed slightly)
- [ ] Loading states prevent double-submission
- [ ] Error states explain what went wrong and how to fix it
- [ ] Success states confirm the action completed

**Micro-interactions:**
- [ ] Button press feedback within 100ms
- [ ] Exits faster than entrances
- [ ] Reduced motion preference respected (no motion → fade or instant)
- [ ] No animation on non-interactive elements
- [ ] Timing consistent across similar interactions

**Gestures:**
- [ ] Every gesture has a visible button alternative
- [ ] Every gesture has a keyboard equivalent
- [ ] No custom gestures within 20% of screen edges (system gesture conflict)
- [ ] Long press triggers at 500ms with progressive feedback
- [ ] Swipe conventions follow platform norms (left = destructive)
- [ ] Drag elements have visible handle affordance
- [ ] First-time gesture hints shown for non-obvious interactions

---

*Based on the 8-state interaction model from impeccable by Paul Bakaus, micro-interaction principles from Dan Saffer's Microinteractions, and gesture conventions from Apple HIG and Material Design.*

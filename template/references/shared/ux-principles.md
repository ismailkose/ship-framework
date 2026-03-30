# UX Principles Reference

> Psychological principles behind every interface that feels right.
> These are the "why" behind design decisions — learn them so you build
> interfaces that work with how people actually think, not against it.
>
> **Agent routing:**
> Arc → Sections 1 + 2 + 5 (plan screens + interactions + platform patterns). Hick's Law, Miller's Law, Progressive Disclosure affect screen architecture. Section 5 has control hierarchy, thumb zone, onboarding, writing, accessibility, inclusion.
> Dev → Sections 2 + 3 + 5 (build UI). Code examples show correct vs incorrect patterns. Section 5 has device capabilities, data entry, loading, accessibility rules.
> Vi → Section 4 + 5 (define magic moment + onboarding + writing voice). Peak-End and Goal Gradient shape the core experience.
> Crit → Sections 1-5 (review everything). These principles are the "why" behind HEART dimensions. Section 5 adds accessibility and inclusion checks.
> Pol → Sections 3 + 4 + 5 (audit design craft + writing + branding). Proximity, similarity, visual hierarchy, UX writing, and branding rules.
>
> **Deep-dive references:** This file covers the principles (the "why"). For deeper implementation patterns, see:
> - `touch-interaction.md` — extends Section 2 (Fitts's Law) with gesture patterns, haptics, press feedback, safe areas
> - `layout-responsive.md` — extends Section 3 (spacing/hierarchy) with breakpoint reasoning, mobile-first philosophy, grid systems
> - `forms-feedback.md` — extends Section 5 (data entry) with validation patterns, progressive disclosure, empty states
> - `typography-color.md` — extends Section 3 (visual hierarchy) with type scale reasoning, color token systems
>
> This file is the foundation. The deep-dives supplement it — they don't replace it. Always read this file first.

---

## Section 1: Making Decisions Easy

These principles affect how many options per screen, how data is presented,
and how complexity is managed. Arc uses them when planning screen maps.
Crit checks them when reviewing adoption.

### Hick's Law

> The time to make a decision increases with the number and complexity of choices.

More options = more cognitive load. And it's not linear — it's logarithmic.
Going from 2 to 4 choices is noticeable. Going from 8 to 16 is painful.
This doesn't mean minimize everything — it means show what matters now,
reveal complexity when it's needed.

```tsx
// Incorrect — all options at once
function Settings() {
  return (
    <div>
      {allSettings.map(setting => (
        <SettingRow key={setting.id} {...setting} />
      ))}
    </div>
  );
}

// Correct — progressive disclosure
function Settings() {
  return (
    <div>
      {commonSettings.map(setting => (
        <SettingRow key={setting.id} {...setting} />
      ))}
      <details>
        <summary>Advanced</summary>
        {advancedSettings.map(setting => (
          <SettingRow key={setting.id} {...setting} />
        ))}
      </details>
    </div>
  );
}
```

### Miller's Law

> The average person can hold about 7 (plus or minus 2) items in working memory.

Chunk large data sets so they're scannable. Phone numbers, card numbers,
serial codes, long lists — raw data is unreadable, chunked data is instant.

```tsx
// Incorrect — raw unformatted data
<span>4532015112830366</span>
<span>4158675309</span>

// Correct — chunked for readability
<span>4532 0151 1283 0366</span>
<span>415-867-5309</span>
```

### Cognitive Load

> Remove anything that doesn't help the user complete their task.

Decoration, redundant labels, unnecessary options, and extra confirmation
steps all add load. Every element on screen should earn its place.

```tsx
// Incorrect — extraneous elements
function DeleteDialog() {
  return (
    <dialog>
      <Icon name="warning" size={64} />
      <h2>Warning!</h2>
      <p>Are you absolutely sure you want to delete?</p>
      <p>This action is permanent and cannot be undone.</p>
      <p>All associated data will be lost forever.</p>
      <div>
        <button>Cancel</button>
        <button>Delete</button>
        <button>Learn More</button>
      </div>
    </dialog>
  );
}

// Correct — essential information only
function DeleteDialog() {
  return (
    <dialog>
      <h2>Delete this item?</h2>
      <p>This can't be undone.</p>
      <div>
        <button>Cancel</button>
        <button>Delete</button>
      </div>
    </dialog>
  );
}
```

### Progressive Disclosure

> Show what matters now, reveal complexity later.

Don't overwhelm users with everything at once. Basics first, advanced when
needed. This is how the best restaurant menus work — they curate, not list.

```tsx
// Incorrect — all controls visible
function Editor() {
  return (
    <div>
      <BasicTools />
      <AdvancedTools />
      <ExpertTools />
      <DebugTools />
    </div>
  );
}

// Correct — progressive disclosure
function Editor() {
  const [showAdvanced, setShowAdvanced] = useState(false);
  return (
    <div>
      <BasicTools />
      {showAdvanced && <AdvancedTools />}
      <button onClick={() => setShowAdvanced(!showAdvanced)}>
        {showAdvanced ? "Hide" : "More options"}
      </button>
    </div>
  );
}
```

### Tesler's Law

> Every system has irreducible complexity. The question is who handles it.

Move complexity from the user to the system. A raw text input for dates
pushes formatting complexity to the user. A date picker absorbs it.

```tsx
// Incorrect — complexity pushed to user
<input
  type="text"
  placeholder="Enter date as YYYY-MM-DDTHH:mm:ss.sssZ"
/>

// Correct — system absorbs complexity
<DatePicker
  onChange={(date) => setDate(date.toISOString())}
/>
```

### Pareto Principle

> 80% of users use 20% of features. Optimize the critical path first.

Make the most-used features prominent. Put secondary features in overflow
menus. Don't give equal weight to everything.

```tsx
// Incorrect — all features equally prominent
function Toolbar() {
  return (
    <div>
      {allFeatures.map(f => <Button key={f.id}>{f.label}</Button>)}
    </div>
  );
}

// Correct — critical features prominent, rest accessible
function Toolbar() {
  return (
    <div>
      {criticalFeatures.map(f => <Button key={f.id}>{f.label}</Button>)}
      <MoreMenu features={secondaryFeatures} />
    </div>
  );
}
```

---

## Section 2: Making Interactions Work

These principles affect target sizing, response time, input handling, and
progress communication. Dev builds from these. Eye and QA verify them.

### Fitts's Law

> The time to reach a target is a function of the target's size and distance.

Bigger targets are easier to click. 44px minimum for touch. Expand hit
areas with invisible padding using `::before` pseudo-elements — the user
can't see the extra space, but it's there and easy to click.

```css
/* Incorrect — visible size equals hit area */
.icon-button {
  width: 16px;
  height: 16px;
  padding: 0;
}

/* Correct — expanded invisible hit area */
.icon-button {
  position: relative;
  width: 32px;
  height: 32px;
  padding: 8px;
}

/* Alternative — pseudo-element expansion */
.link {
  position: relative;
}

.link::before {
  content: "";
  position: absolute;
  inset: -8px -12px;
}
```

*The 44px tap target rule in your Design Principles comes from Fitts's Law.*

### Doherty Threshold

> Interactions must respond within 400ms to feel instant.

Under 400ms, the user doesn't notice delay. Above it, they start wondering
if something broke. If you can't make it fast, make it *feel* fast —
optimistic UI, skeleton screens, progress indicators.

```tsx
// Incorrect — no feedback during loading
async function handleClick() {
  const data = await fetchData(); // user waits, sees nothing
  setResult(data);
}

// Correct — immediate optimistic feedback
async function handleClick() {
  setResult(optimisticData); // instant visual response
  const data = await fetchData();
  setResult(data); // real data replaces optimistic
}
```

*For animation timing specifics, see `references/animation.md` — the
200-300ms sweet spot aligns with Doherty's threshold.*

### Postel's Law

> Be conservative in what you send, be liberal in what you accept.

Users don't think in formats — they think in meaning. "jan 15 2024" means
the same as "2024-01-15". Accept messy input, output clean data.

```tsx
// Incorrect — rigid format required
function DateInput({ onChange }) {
  return (
    <input
      type="text"
      placeholder="YYYY-MM-DD"
      pattern="\d{4}-\d{2}-\d{2}"
      onChange={onChange}
    />
  );
}

// Correct — accepts multiple formats
function DateInput({ onChange }) {
  function handleChange(e) {
    const parsed = parseFlexibleDate(e.target.value);
    if (parsed) onChange(parsed);
  }

  return (
    <input
      type="text"
      placeholder="Any date format"
      onChange={handleChange}
    />
  );
}
```

### Goal Gradient

> People accelerate behavior as they approach a goal. Show how close they are.

Progress bars, step indicators, completion percentages — these aren't
decoration, they're motivation. A user at "step 3 of 4" moves faster than
one who doesn't know where they are.

```tsx
// Incorrect — no sense of progress
function Onboarding({ step }) {
  return <OnboardingStep step={step} />;
}

// Correct — progress visible
function Onboarding({ step, totalSteps }) {
  return (
    <div>
      <ProgressBar value={step} max={totalSteps} />
      <span>Step {step} of {totalSteps}</span>
      <OnboardingStep step={step} />
    </div>
  );
}
```

---

## Section 3: Making Layout Communicate

These principles affect spacing, consistency, grouping, and visual
hierarchy. Dev builds the layout. Pol audits the craft.

### Proximity

> Elements near each other are perceived as related.

Tighter spacing within groups, larger spacing between groups. This is how
you create visual structure without borders or dividers.

```css
/* Incorrect — uniform spacing between unrelated items */
.form label,
.form input,
.form .hint,
.form .divider {
  margin-bottom: 16px;
}

/* Correct — tighter within groups, larger between */
.form label {
  margin-bottom: 4px;
}

.form input {
  margin-bottom: 2px;
}

.form .hint {
  margin-bottom: 24px; /* gap between field groups */
}
```

### Similarity

> Elements that function the same should look the same.

Visual consistency signals functional consistency. If you have three
different button styles for the same action, the user doesn't know what
to trust.

```css
/* Incorrect — same function, different appearance */
.save-button {
  background: blue;
  border-radius: 8px;
}

.submit-button {
  background: green;
  border-radius: 0;
}

/* Correct — same function, same appearance */
.primary-action {
  background: var(--color-primary);
  color: var(--color-primary-foreground);
  border-radius: 8px;
}
```

### Common Region

> Elements sharing a clearly defined boundary are perceived as a group.

Use sections, cards, and dividers to create visual groups — not just
proximity, but explicit boundaries.

```tsx
// Incorrect — flat list with no visual grouping
function Settings() {
  return (
    <div>
      <Toggle label="Dark mode" />
      <Toggle label="Notifications" />
      <Input label="Email" />
      <Input label="Password" />
    </div>
  );
}

// Correct — bounded sections
function Settings() {
  return (
    <div>
      <section className={styles.group}>
        <h3>Appearance</h3>
        <Toggle label="Dark mode" />
      </section>
      <section className={styles.group}>
        <h3>Account</h3>
        <Input label="Email" />
        <Input label="Password" />
      </section>
    </div>
  );
}
```

### Uniform Connectedness

> Elements visually connected (by lines, color, or frames) are perceived as related.

Step indicators with connector lines, breadcrumbs with separators, linked
cards with shared color — visual connections reinforce relationships.

```tsx
// Incorrect — steps with no visual connection
function Steps({ current }) {
  return (
    <div>
      <span>Step 1</span>
      <span>Step 2</span>
      <span>Step 3</span>
    </div>
  );
}

// Correct — connected with a visual line
function Steps({ current }) {
  return (
    <div className={styles.steps}>
      {steps.map((step, i) => (
        <div key={step.id} className={styles.step} data-active={i <= current}>
          <div className={styles.dot} />
          {i < steps.length - 1 && <div className={styles.connector} />}
          <span>{step.label}</span>
        </div>
      ))}
    </div>
  );
}
```

### Von Restorff Effect

> When multiple similar elements are present, the one that differs is remembered.

Make important actions visually distinct. A destructive button should look
different from a cancel button — not just different text, different treatment.

```tsx
// Incorrect — primary action blends in
<div className={styles.actions}>
  <button className={styles.button}>Cancel</button>
  <button className={styles.button}>Delete Account</button>
</div>

// Correct — destructive action stands out
<div className={styles.actions}>
  <button className={styles.secondary}>Cancel</button>
  <button className={styles.danger}>Delete Account</button>
</div>
```

### Prägnanz

> People interpret complex visuals as the simplest form possible.

Reduce visual noise. If an element looks busy, simplify it. Clear forms
are processed faster than decorated ones.

```css
/* Incorrect — visually noisy */
.card {
  border: 2px dashed red;
  background: linear-gradient(45deg, #f0f, #0ff);
  box-shadow: 5px 5px 0 black, 10px 10px 0 gray;
  outline: 3px dotted blue;
}

/* Correct — clear, simple form */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}
```

### Serial Position Effect

> Users best remember the first and last items in a sequence.

Place the most important actions at the start and end of navigation,
toolbars, and lists. The middle is where things get forgotten.

```tsx
// Incorrect — important action buried in middle
<nav>
  <Link href="/settings">Settings</Link>
  <Link href="/">Home</Link>
  <Link href="/about">About</Link>
</nav>

// Correct — key items at edges
<nav>
  <Link href="/">Home</Link>
  <Link href="/about">About</Link>
  <Link href="/settings">Settings</Link>
</nav>
```

---

## Section 4: Making Experiences Stick

These principles affect how users remember and return to your product.
Vi uses them when defining the magic moment. Crit checks them when
reviewing retention and happiness.

### Peak-End Rule

> People judge experiences by their peak moment and their end.

Invest in success states and completion screens. An abrupt redirect after
form submission wastes the moment. A satisfying confirmation builds
positive memory.

```tsx
// Incorrect — abrupt end after action
async function handleSubmit() {
  await submitForm(data);
  router.push("/"); // gone, no moment to feel good
}

// Correct — satisfying completion state
async function handleSubmit() {
  await submitForm(data);
  setStatus("success");
}

return status === "success" ? (
  <SuccessScreen message="You're all set." />
) : (
  <Form onSubmit={handleSubmit} />
);
```

### Zeigarnik Effect

> People remember incomplete tasks better than completed ones.

Show incomplete states to drive completion. "Profile 60% complete" is
more motivating than showing nothing. Progress creates urgency.

```tsx
// Incorrect — no indication of incomplete profile
function Dashboard() {
  return <DashboardContent />;
}

// Correct — incomplete state visible
function Dashboard({ profile }) {
  return (
    <div>
      {!profile.isComplete && (
        <Banner>
          Complete your profile — {profile.completionPercent}% done
        </Banner>
      )}
      <DashboardContent />
    </div>
  );
}
```

### Jakob's Law

> Users spend most of their time on other sites. They expect yours to work the same way.

Use familiar UI patterns. A hamburger menu should open navigation. A heart
icon should mean "favorite." Custom icons for standard actions create
confusion, not delight.

```tsx
// Incorrect — custom unconventional navigation
function Nav() {
  return (
    <nav>
      <button onClick={() => navigate("/")}>⬡</button>
      <button onClick={() => navigate("/search")}>⬢</button>
    </nav>
  );
}

// Correct — standard recognizable patterns
function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/search">Search</Link>
    </nav>
  );
}
```

### Aesthetic-Usability Effect

> Users perceive aesthetically pleasing design as more usable.

Visual polish isn't vanity — it builds trust. Small details compound.
A product that looks considered feels more reliable than one that looks
thrown together, even if the functionality is identical.

```css
/* Incorrect — unstyled, raw elements */
.card {
  border: 1px solid black;
  padding: 10px;
}

/* Correct — considered visual treatment */
.card {
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}
```

---

## Section 5: Platform-Aware Design

These principles come from Apple's Human Interface Guidelines but apply to
any well-designed app — web, mobile, or desktop. They're the patterns users
already expect because they use them in every other app on their device.

### Control Hierarchy

> Primary actions visible. Secondary actions discoverable.

The most important action on screen should be immediately visible — a prominent
button, a clear CTA. Secondary actions (delete, archive, share) live behind
swipe gestures, long press, overflow menus, or hover states. Don't give
everything equal weight.

```tsx
// Incorrect — all actions equally visible
<div className={styles.actions}>
  <Button>Edit</Button>
  <Button>Share</Button>
  <Button>Archive</Button>
  <Button>Delete</Button>
  <Button>Duplicate</Button>
</div>

// Correct — primary visible, secondary discoverable
<div className={styles.actions}>
  <Button variant="primary">Edit</Button>
  <MoreMenu actions={["Share", "Archive", "Duplicate", "Delete"]} />
</div>
```

### Thumb Zone

> Place primary actions where thumbs naturally rest — the bottom third of mobile screens.

People hold phones one-handed. The top of the screen is hard to reach.
Navigation can live at the top (it's infrequent), but primary CTAs belong
at the bottom where they're easy to tap without shifting grip.

```tsx
// Incorrect — primary CTA at top of mobile screen
<div className={styles.page}>
  <Button className={styles.topCta}>Add Item</Button>
  <ItemList items={items} />
</div>

// Correct — primary CTA in bottom-reachable area
<div className={styles.page}>
  <ItemList items={items} />
  <FloatingAction label="Add Item" icon="plus" />
</div>
```

### Respect System Preferences

> Adapt to the user's chosen appearance, motion, and text size settings.

Users set their preferences once at the system level and expect every app to
honor them. Dark mode, reduced motion, larger text, high contrast — these
aren't features to build, they're expectations to meet.

```css
/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* Respect color scheme preference */
:root {
  color-scheme: light dark;
}
```

### Use Device Capabilities

> Replace manual input with platform features whenever possible.

Camera for scanning, location for addresses, biometrics for auth, payment
APIs for checkout. Every manual input field is a chance to ask: can the
device provide this automatically?

```tsx
// Incorrect — manual address entry
<Input label="Address" placeholder="Type your full address..." />

// Correct — use device capabilities first, manual fallback
<LocationPicker
  onDetect={(location) => setAddress(location)}
  fallback={<Input label="Address" placeholder="Or type manually" />}
/>
```

### Onboarding

> Teach through interaction, not instruction. Delay sign-in until value is shown.

The best onboarding is the product itself. Show the core value before asking
for anything — no sign-up wall, no tutorial carousel, no permission requests
upfront. Let people experience the product first, then ask for commitment.

```tsx
// Incorrect — wall of permissions before value
function App() {
  return isSignedIn ? <Dashboard /> : <SignUpForm />;
}

// Correct — value first, sign-in when needed
function App() {
  return (
    <div>
      <CoreExperience /> {/* works without sign-in */}
      {needsAccount && <SignInPrompt reason="Save your progress" />}
    </div>
  );
}
```

### Smart Data Entry

> Get data from the system. Offer choices instead of text fields. Validate inline.

Every text field is friction. Prefer pickers, toggles, and selectors over
free-text. Pre-fill from context (location, clipboard, previous entries).
Validate as they type — don't wait until submit to show errors.

```tsx
// Incorrect — all text fields, validate on submit
<form onSubmit={validateAll}>
  <input placeholder="Country" />
  <input placeholder="Phone" />
  <input placeholder="Date" />
</form>

// Correct — smart inputs, inline validation
<form>
  <CountryPicker defaultValue={detectCountry()} />
  <PhoneInput format="auto" validateOnChange />
  <DatePicker defaultValue={today()} />
</form>
```

### Feedback Hierarchy

> Match the significance of the event to the weight of the feedback.

Not every success needs a modal. Not every error needs a banner. Small
confirmations → subtle animation or haptic. Important warnings → inline
message. Critical errors → modal that requires action.

```tsx
// Incorrect — modal for every outcome
function handleSave() {
  await save(data);
  alert("Saved successfully!"); // too heavy
}

// Correct — feedback matches significance
function handleSave() {
  await save(data);
  toast("Saved"); // subtle, non-blocking
}

function handleDelete() {
  const confirmed = await confirm("Delete this permanently?");
  if (confirmed) await deleteItem(id); // modal for destructive action
}
```

### Loading & Launching

> Show content immediately. Restore previous state. Never show a blank screen.

The first thing users see should be content, not a spinner. Use skeleton
screens, cached data, or optimistic UI. When users return to your app,
put them exactly where they left off — don't reset to home.

```tsx
// Incorrect — blank screen while loading
function Feed() {
  const { data, loading } = useFeed();
  if (loading) return <Spinner />;
  return <FeedList items={data} />;
}

// Correct — skeleton then content
function Feed() {
  const { data, loading } = useFeed();
  return <FeedList items={data} skeleton={loading} />;
}
```

### Modality

> Use modals only when there's a clear benefit. Keep them focused. Always provide dismiss.

Modals interrupt flow. Use them for self-contained tasks (compose, confirm
destructive action, complete a sub-task) — not for information that could
be inline. Every modal needs a visible way to dismiss.

### Settings

> Smart defaults first. Minimize options. Put task-specific settings in context.

If your defaults are good, most people never touch settings. Put rarely
changed options in a settings screen. Put task-specific options (sort, filter,
view toggle) directly in the screen they affect — don't make people leave
their task to customize it.

### Charts & Data

> Keep charts simple. Add detail on demand. Make them accessible.

A chart should communicate one insight clearly. Don't pack every metric
into one visualization. Use consistent chart types and colors across your
app. Always provide text alternatives for accessibility — chart images
alone aren't enough.

### UX Writing

> Determine voice, match tone to context, be action-oriented, and build language patterns.

Words are part of the interface. Determine your app's voice early (trustworthy?
playful? professional?) and keep it consistent. Then vary tone by context —
celebratory for achievements, direct for errors, encouraging for onboarding.

```tsx
// Incorrect — vague, passive, blame-y
<p>Error: Invalid input was detected.</p>
<button>Click here</button>

// Correct — clear, action-oriented, helpful
<p>Choose a password with at least 8 characters.</p>
<button>Create account</button>
```

**Rules:**
- Action-oriented labels: use verbs on buttons ("Send", "Save", "Continue"), not vague phrases ("Let's do it!", "Click here")
- Consistent capitalization: pick title case or sentence case per element type and stick with it
- Use possessive pronouns sparingly: "Favorites" is clearer than "Your Favorites"
- Avoid "we" — it's unclear who "we" refers to. Say "Unable to load" not "We're having trouble"
- Clear error messages: explain what went wrong and what to do next, placed near the problem
- Empty states: guide users with next steps and a CTA — never leave a blank screen
- Write for each device: "tap" on mobile, "click" on desktop, match gesture vocabulary
- Build language patterns: use consistent terms for navigation ("Continue", "Next", "Done") across all flows

### Accessibility

> Design for everyone. Perceivable, operable, understandable, robust.

Accessibility isn't a feature — it's a quality bar. Every interface should
work for people with visual, hearing, motor, and cognitive differences.
The rules below are universal minimums.

**Contrast and visibility:**
- 4.5:1 contrast ratio for body text (WCAG AA)
- 3:1 for large text (18pt+) and bold text
- Never use color alone to convey meaning — pair with shape, icon, or text
- Support increased contrast mode / high contrast themes

**Tap targets and spacing:**
- 44×44pt minimum on touch devices, 28×28pt on desktop
- 12pt padding between elements with bezels, 24pt for elements without
- Simple gestures for common interactions — avoid complex multitouch

**Keyboard and assistive tech:**
- All core functionality reachable via keyboard alone
- Meaningful focus order (don't trap focus, don't skip elements)
- Proper labels for screen readers — every interactive element needs a label
- Provide alternatives to gestures: if swipe-to-delete, also offer a button

**Motion and timing:**
- Respect `prefers-reduced-motion` — reduce or eliminate animations
- Avoid time-boxed auto-dismissing elements — let users control their pace
- No flashing content faster than 3 times per second

```tsx
// Incorrect — color-only status, no label
<span style={{ color: isActive ? "green" : "red" }}>●</span>

// Correct — color + text + aria label
<span
  style={{ color: isActive ? "green" : "red" }}
  aria-label={isActive ? "Active" : "Inactive"}
>
  {isActive ? "● Active" : "○ Inactive"}
</span>
```

### Inclusion

> Plain language, no jargon, represent diversity, avoid stereotypes.

Inclusive design starts with language. Use simple, direct words. Avoid
colloquial expressions (culture-specific, hard to translate). Use
gender-neutral terms. Represent a range of people in images and examples.
Never use a disability as a negative metaphor.

**Rules:**
- Plain language over jargon — define technical terms when you must use them
- Gender-neutral: "they" over "he or she", role names over gendered titles
- People-first language for disabilities: "person with low vision" not "blind user"
- Avoid culture-specific metaphors, idioms, and humor in UI copy
- Security questions / personalization: reference universal experiences, not assumptions
- Represent diverse people in illustrations, avatars, and examples
- Test with localization in mind: plain language translates better

### Branding

> Branding defers to content. Express identity through voice, accent color, and typography.

Your brand comes through in how the product feels, not how much logo is on
screen. Use accent color, consistent voice, and thoughtful typography to
express identity. Standard platform patterns build trust — don't override
them for brand uniqueness.

**Rules:**
- One accent color for interactive elements — consistent across the app
- Custom font for headings is fine; use system font for body text (legibility)
- Don't plaster logos on every screen — people know which app they're using
- Launch screens are not branding opportunities — they disappear too fast
- Place UI components in expected locations — familiarity beats novelty
- Standard patterns first, brand expression second

---

*Based on [Jon Yablonski's Laws of UX](https://lawsofux.com/), [Raphael Salaja's userinterface.wiki](https://www.userinterface.wiki/), and [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines).*

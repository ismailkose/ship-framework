# UX Principles Reference

> Psychological principles behind every interface that feels right.
> These are the "why" behind design decisions — learn them so you build
> interfaces that work with how people actually think, not against it.
>
> **Agent routing:**
> Arc → Sections 1 + 2 (plan screens + interactions). Hick's Law, Miller's Law, Progressive Disclosure affect screen architecture.
> Dev → Sections 2 + 3 (build UI). Code examples show correct vs incorrect patterns. Learn the technique, adapt to your stack.
> Vi → Section 4 (define magic moment). Peak-End and Goal Gradient shape the core experience.
> Crit → Sections 1-4 (review everything). These principles are the "why" behind HEART dimensions.
> Pol → Sections 3 + 4 (audit design craft). Proximity, similarity, visual hierarchy live here.

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

*Based on [Jon Yablonski's Laws of UX](https://lawsofux.com/) and [Raphael Salaja's userinterface.wiki](https://www.userinterface.wiki/).*

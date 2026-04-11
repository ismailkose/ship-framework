# React & Next.js Patterns Reference

> **Agent routing:**
> **Arc** → Sections 1, 3 (architecture decisions: Server vs Client, composition planning)
> **Dev** → Sections 1–5 (all implementation patterns)
> **Crit** → Section 4 (review: anti-patterns, unnecessary client boundaries, prop drilling)
> **Pol** → Section 3 (audit composition quality)
> **Test** → Section 5 (hydration safety, SSR verification)

---

## Section 1: Server vs Client Architecture

### Why Server Components Are Default

Server Components render once on the server, send only HTML to the browser, and ship zero JavaScript. This means:
- Faster initial page loads (no parsing/compilation in the browser)
- Direct database access without API layers
- Secrets stay on the server
- Large dependencies never reach the client

Every component in Next.js 13+ is a Server Component by default. Treat 'use client' as a boundary you add only when necessary.

### When to Add 'use client'

Add 'use client' only for:
- **Hooks** (useState, useEffect, useContext, useReducer, useCallback, useMemo)
- **Browser APIs** (localStorage, window, document, navigator)
- **Event handlers** (onClick, onChange, onSubmit — interactive elements)
- **Real-time updates** (WebSocket subscriptions, live data)

That's it. Not for "I need to pass props," not for "I want to reuse this component," not for "it's small."

### Keeping the Boundary Deep

Every 'use client' component sends that entire component's code to the browser, along with all its imports. A 'use client' at the root means your whole app is client-rendered.

Keep boundaries deep: mark the smallest possible subtree as client. A Button with onClick? Mark Button as client, not its parent Page.

### Streaming with Suspense

Slow data fetches block page rendering. Wrap slow sections in Suspense:

```jsx
// ❌ Wrong: blocks entire page until sidebar loads
export default async function Page() {
  const sidebar = await fetch('...', { cache: 'no-store' });
  const posts = await fetch('...');
  return <Layout sidebar={sidebar} posts={posts} />;
}

// ✅ Correct: streams fast content while sidebar loads
export default async function Page() {
  return (
    <Layout>
      <Suspense fallback={<PostsSkeleton />}>
        <Posts />
      </Suspense>
      <Suspense fallback={<SidebarSkeleton />}>
        <Sidebar />
      </Suspense>
    </Layout>
  );
}
```

---

## Section 2: Data Fetching & Performance

### Parallel Fetching with Promise.all

Sequential awaits create waterfalls. Each fetch waits for the previous one:

```jsx
// ❌ Waterfall: 2s + 1s = 3s load time
const user = await fetch('/api/user');
const posts = await fetch('/api/posts');

// ✅ Parallel: max(2s, 1s) = 2s load time
const [user, posts] = await Promise.all([
  fetch('/api/user'),
  fetch('/api/posts'),
]);
```

Always parallelize independent requests.

### Co-locate Data Needs

Fetch where you use the data, not in a parent component. This makes dependencies clear and enables independent Suspense boundaries:

```jsx
// ❌ Wrong: PostList doesn't know what it needs
async function PostList({ posts }) {
  return posts.map(p => <Post key={p.id} post={p} />);
}

// ✅ Correct: PostList owns its data fetch
async function PostList() {
  const posts = await fetch('/api/posts');
  return posts.map(p => <Post key={p.id} post={p} />);
}
```

### Caching Strategy

- **unstable_cache**: memoize expensive computations on the server
- **revalidate**: set revalidation time in seconds (0 = no cache, 3600 = 1 hour)
- **ISR (Incremental Static Regeneration)**: revalidate stale pages in the background

```jsx
export const revalidate = 3600; // Revalidate every hour

export default async function Page() {
  const data = await fetch('/api/data', {
    next: { revalidate: 3600 },
  });
  return <div>{data}</div>;
}
```

### Re-render Optimization

Memo, useCallback, useMemo should be added only after measuring slow renders. Premature optimization adds complexity:

```jsx
// ❌ Premature: Button re-renders once per parent render (fine for 99% of cases)
function Button({ onClick }) {
  return <button onClick={onClick}>Click</button>;
}

// ✅ Only if Button re-renders cause visible lag and contain expensive children
const Button = memo(function Button({ onClick }) {
  return <button onClick={onClick}>Click</button>;
});
```

### Uncontrolled Inputs for Forms

Use uncontrolled inputs by default. Less state, simpler code:

```jsx
// ✅ Uncontrolled: form state lives in the DOM
export default function Form() {
  return (
    <form action={submitAction}>
      <input name="email" required />
      <button type="submit">Submit</button>
    </form>
  );
}

// ❌ Controlled: more boilerplate, same result
const [email, setEmail] = useState('');
```

### Context Re-render Pitfall

One big context causes every subscriber to re-render when any value changes. Split contexts by update frequency:

```jsx
// ❌ Wrong: UserPreferences updates cause all consumers to re-render
const UserContext = createContext({ name, theme, settings, avatar });

// ✅ Correct: theme updates only theme consumers
const NameContext = createContext({ name });
const ThemeContext = createContext({ theme });
const SettingsContext = createContext({ settings });
```

---

## Section 3: Component Composition

### Boolean Prop Proliferation

More than 3 boolean props signals a refactor:

```jsx
// ❌ Boolean explosion: size, variant, disabled, loading, outline all control the same thing
<Button size="lg" variant="primary" disabled outline loading />

// ✅ Clear variants: one variant covers the state
<Button variant="primary-lg" disabled loading />
```

### Compound Components

For complex components (Tabs, Accordion, Select, Dialog), use compound components. Each child owns its own state and behavior:

```jsx
// ❌ Config object: hard to customize, props explosion
<Tabs tabs={[
  { label: 'Home', content: <Home /> },
  { label: 'About', content: <About /> },
]} />

// ✅ Compound: clear structure, flexible composition
<Tabs>
  <Tabs.List>
    <Tabs.Trigger value="home">Home</Tabs.Trigger>
    <Tabs.Trigger value="about">About</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="home"><Home /></Tabs.Content>
  <Tabs.Content value="about"><About /></Tabs.Content>
</Tabs>
```

### Children Over Render Props

Prefer children. Cleaner JSX, easier to read:

```jsx
// ❌ Render props: nested callbacks
<Modal render={({ isOpen, toggle }) => (
  <div>{isOpen && <p>Open</p>}</div>
)} />

// ✅ Children with context: clearer structure
<Modal>
  <Modal.Trigger>Open</Modal.Trigger>
  <Modal.Content>Content here</Modal.Content>
</Modal>
```

### Explicit Variants

Define variants as string unions, not booleans. Self-documenting:

```jsx
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

// ✅ Clear what's valid
<Button variant="primary" />

// ❌ Unclear without docs
<Button isPrimary outline={false} danger />
```

### State Lifting into Providers

When multiple components share state, lift into a provider. Keeps state centralized:

```jsx
// ✅ Single source of truth
export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}
```

### Context Interface Design

Contexts should expose state + actions + metadata:

```jsx
// ✅ Complete interface
const ModalContext = createContext({
  isOpen: false,
  open: () => {},
  close: () => {},
  toggle: () => {},
  content: null,
  setContent: () => {},
});
```

---

## Section 4: Review Patterns (Anti-patterns to Flag)

**Unnecessary 'use client':** Server Component doing only data rendering. Remove 'use client'.

**Boolean accumulation:** Component with 4+ boolean props. Suggest variants or compound components.

**Prop drilling 3+ levels:** Parent → Child → Grandchild → Great-grandchild. Use context instead.

**Missing Suspense boundaries:** Slow fetches at the top level without Suspense. Add Suspense to stream fast parts.

**forwardRef in React 19+:** Refs are handled automatically. Remove forwardRef wrapper.

**Importing entire libraries:** `import _ from 'lodash'` instead of `import { map } from 'lodash'`. Tree-shake unused code.

**Controlled inputs without onChange:** Input field has value prop but no onChange handler. Will be read-only and freeze on user input.

---

## Section 5: Hydration Safety

### Controlled Inputs Need onChange

Controlled inputs without handlers cause hydration mismatches and frozen inputs:

```jsx
// ❌ Frozen input: value set but no handler to update it
<input value={state} />

// ✅ Controlled and updateable
<input value={state} onChange={(e) => setState(e.target.value)} />
```

### Date/Time Mismatch

Server and client have different timezones. Always format on client:

```jsx
// ❌ Server renders 'March 30', client renders 'March 29' in PST
<p>{new Date().toLocaleDateString()}</p>

// ✅ Format in useEffect on client
useEffect(() => {
  setDate(new Date().toLocaleDateString());
}, []);
```

### suppressHydrationWarning Usage

Use sparingly. Only suppress warnings you've diagnosed and fixed:

```jsx
// ✅ Only when you're intentionally rendering different content
<div suppressHydrationWarning>
  {isClient ? <ClientContent /> : <Skeleton />}
</div>
```

### Browser-Only Code in useEffect

Wrap browser APIs in useEffect to avoid server-render errors:

```jsx
// ❌ Fails on server: window is undefined
const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

// ✅ Runs only in browser
useEffect(() => {
  const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  setTheme(isDarkMode ? 'dark' : 'light');
}, []);
```

### Dynamic Imports with ssr: false

Components using browser-only libraries should disable SSR:

```jsx
// ✅ Avoids rendering on server
const Map = dynamic(() => import('map-lib'), { ssr: false });
```

---

**Last updated:** 2026-03-30
**Framework:** Next.js 14+ with React 19 patterns

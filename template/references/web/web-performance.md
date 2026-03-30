# Web Performance Reference

> Agent routing:
> Arc → Section 1 (performance budget decisions during planning)
> Dev → Sections 1-3 (implement: images, fonts, virtualization, lazy loading, caching)
> Crit → Section 4 (review: anti-patterns checklist, performance violations)
> Pol → Section 2 (audit image optimization, font loading, bundle size)
> Test → Section 3 (verify: Lighthouse scores, CLS, INP, bundle size)

## Section 1: Core Web Vitals

**Why These Metrics Matter**

- **LCP (Largest Contentful Paint < 2.5s)**: Measures perceived load time. LCP is what users *see* first — a hero image, headline, or main product photo. If LCP is slow, the page feels dead even if other content loads later. Affects user confidence and bounce rates.
- **CLS (Cumulative Layout Shift < 0.1)**: Measures visual stability. Content shifting mid-interaction frustrates users and causes mis-clicks. Sudden layout changes (ads loading, images reflowing, dynamic content inserting) destroy perceived quality.
- **INP (Interaction to Next Paint < 200ms)**: Measures responsiveness. The gap between tap/click and screen response. Lag in this window feels broken and laggy, even if the app is logically fast.

**What Affects Each Metric**

*LCP impacts:*
- Hero image dimensions and file size
- Font loading strategy (invisible text during load)
- Server response time (TTFB)
- Critical CSS delivery

*CLS impacts:*
- Images without width/height attributes
- Dynamic content injection (modals, notifications)
- Font swapping without fallback dimensions
- Unannounced layout shifts from JS

*INP impacts:*
- Main thread blocking (heavy JS execution)
- Long event handlers (>50ms on critical path)
- Unoptimized React renders
- Expensive DOM queries in loops

## Section 2: Optimization Patterns

**Image Optimization**

Why WebP/AVIF: Modern formats are 30-50% smaller than JPEG at identical visual quality. AVIF is better; WebP is safer. Always serve with fallback: `<source srcset="hero.avif" type="image/avif"> <source srcset="hero.webp" type="image/webp"> <img src="hero.jpg">`.

Dimensions on every image: Prevents CLS by reserving space. Always set `width` and `height`. For responsive images, use aspect-ratio CSS: `img { aspect-ratio: 16/9; width: 100%; }`.

Lazy loading: Use `loading="lazy"` for below-fold images. Never lazy-load above-fold hero images (LCP will suffer). Use `fetchpriority="high"` on critical images.

```html
<!-- Good -->
<img src="hero.jpg" width="1200" height="600" alt="Hero" fetchpriority="high" />
<img src="thumbnail.jpg" width="100" height="100" loading="lazy" alt="Product" />

<!-- Bad -->
<img src="hero.jpg" alt="Hero" /> <!-- No dimensions = CLS -->
<img src="thumbnail.jpg" loading="lazy" /> <!-- Lazy loading hero = LCP hit -->
```

**Font Loading**

Why `font-display: swap`: Shows fallback text immediately instead of invisible text during font load. Users see *something* instead of blank space.

Preload critical fonts: `<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>`. Limits FOUT (flash of unstyled text).

Font accumulation: Each font file is a separate network request. Limit to 2-3 font families max. Use variable fonts to reduce variants: `font-weight: 400 900; font-style: normal italic;` from one file instead of four.

```css
/* Good */
@font-face {
  font-family: 'Inter';
  src: url('inter.woff2') format('woff2');
  font-display: swap; /* Show fallback immediately */
}

/* Bad */
@font-face {
  font-family: 'Custom';
  src: url('custom.woff2') format('woff2');
  font-display: block; /* Invisible text for 3s */
}
```

**Virtualization**

Why virtualize: DOM nodes are expensive. Each node costs memory, paint time, and layout calculation. A list of 500 items creates 500 DOM nodes. Virtualization keeps only visible items (20-50) in the DOM.

When to virtualize: Lists with 50+ items. Tables with infinite scroll. Long feeds or chat histories.

Tools: `@tanstack/react-virtual`, `react-window`, `content-visibility: auto` (CSS-only, limited support).

```jsx
/* Good */
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualList({ items }) {
  const virtualizer = useVirtualizer({ count: items.length, size: 35 })
  return virtualizer.getVirtualItems().map(v => (
    <div key={v.index}>{items[v.index]}</div>
  ))
}

/* Bad */
function LongList({ items }) {
  return items.map(item => <div key={item.id}>{item.name}</div>) // DOM explosion
}
```

**Bundle Optimization**

Tree shaking: Use named imports. `import { throttle } from 'lodash-es'` removes unused code. `import _ from 'lodash'` bundles everything.

Route-based code splitting: Lazy-load route components. `const Dashboard = lazy(() => import('./Dashboard'))`. Reduces initial bundle.

Server Components (React 19+): Zero client-side JS for non-interactive sections. Move data fetching, auth checks, and rendering to server. Ship HTML instead of JS.

## Section 3: Testing & Internationalization

**Lighthouse Interpretation**

- Score 90+: Good user experience. Target this.
- Score 50-89: Noticeable performance issues. Prioritize Core Web Vitals fixes.
- Score <50: Poor. User bounce rate likely high.

**CLS Debugging**

Tools: DevTools → Performance tab (recording), Lighthouse, web-vitals library.

Common causes: Images loading without dimensions, fonts swapping mid-render, modals/notifications injecting unstyled content, lazy images above fold.

Debug: Record performance, look for layout shift events. DevTools highlights shifted elements in red.

**INP Debugging**

Tools: DevTools → Interactions, web-vitals library.

Long tasks: Look for JS execution >50ms. Use DevTools Performance tab to find culprits. React DevTools Profiler shows slow render phases.

Heavy handlers: Debounce/throttle expensive event listeners (scroll, resize, input). Move work to requestIdleCallback for non-critical updates.

**Bundle Analysis**

Tools: `webpack-bundle-analyzer`, `source-map-explorer`, `bundlesize`.

Target: Keep initial bundle <100KB gzipped. Lazy load over 50KB chunks.

**Internationalization Rules**

- Dates: Use `Intl.DateTimeFormat` instead of hardcoding. `new Intl.DateTimeFormat('de-DE').format(new Date())` produces `30.3.2026`.
- Numbers/currency: Use `Intl.NumberFormat`. `new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(1234.56)` produces `$1,234.56`.
- Language detection: Use Accept-Language header from browser/server, not IP geolocation. Never guess.
- Non-breaking spaces: Use `&nbsp;` or `\u00A0` to keep "3 MB" or currency pairs together across lines.

## Section 4: Anti-Patterns Checklist

Flag immediately in any review:

- **`user-scalable=no` in viewport meta**: Disables accessibility zoom. Remove it. Violates WCAG.
- **`onPaste preventDefault`**: Blocks password managers and clipboard tools. Never prevent paste.
- **`transition: all`**: Animates every property, causing jank. Use `transition: opacity, transform` instead.
- **`outline: none` without replacement**: Removes keyboard focus indicator. Use `outline: 2px solid blue; outline-offset: 2px;` instead.
- **`<div onClick>` for actions**: No keyboard support, invisible to screen readers. Use `<button>` or add `role="button"` with keydown handler.
- **`<img>` without dimensions**: Causes CLS. Always set width/height.
- **Long `.map()` rendering 50+ items**: DOM explosion. Use virtualization.
- **`<input>` without associated `<label>`**: Screen reader invisible. Use `<label htmlFor="id">Label</label> <input id="id">`.
- **Icon buttons without `aria-label`**: Context invisible. Use `<button aria-label="Close menu">✕</button>`.
- **Hardcoded date/number formats**: i18n failure. Use `Intl` APIs.
- **`autoFocus` on mobile**: Triggers keyboard, stealing screen real estate. Avoid entirely.
- **`forwardRef` in React 19+**: Unnecessary wrapper. Direct props pass through automatically.
- **Boolean prop accumulation 3+**: Refactor. `<Button primary large disabled warning>` → `<Button variant="primary-large-disabled-warning">` or use object prop.


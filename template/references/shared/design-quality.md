# Design Quality Reference

> The difference between amateur and professional design isn't following rules — it's seeing what's off before you can name it. This reference teaches that eye.
>
> Agent routing:
> - Pol → Sections 1-4 (design quality is Pol's primary domain — first impression, consistency, coherence, craft)
> - Vi → Section 1 (first impression shapes product vision)
> - Eye → Sections 2-4 (visual quality assessment)
> - Crit → Section 2 (AI slop hurts user trust and adoption)

## Section 1: First Impression Assessment

This is what gstack calls "Phase 1" of design review. Before auditing details, step back and FEEL the whole.

### Why First Impressions Matter

Users form opinions of your product in 50 milliseconds — before they read a word or click a button (Lindgaard et al.). That split-second judgment shapes whether they trust you, whether they think you're serious or amateur, whether they'll invest attention. You can't argue someone into trusting your design. The visual system decides first.

### The 3-Second Test

Sit someone in front of the design (fresh eyes matter). Set a timer.

**Can they answer within 3 seconds:**
1. "What is this product?" Not the tagline — the actual purpose. Calendar app? Customer support? Expense tracking?
2. "What should I do first?" Where's the entry point? What's the primary action?

If people hesitate, the hierarchy is broken. If they have to read, the design failed the first impression test.

### Emotional Response Check

Before analyzing, ask: "What feeling does this design evoke?" Trustworthy? Modern? Playful? Corporate? Calming? Urgent?

Then ask the harder question: **Does that feeling match the product's intent?**

- A banking app that feels playful is a red flag (users want trustworthiness)
- A creative tool that feels corporate and rigid alienates its audience
- A health app that feels clinical instead of supportive won't build habit
- A productivity tool with too much visual noise exhausts instead of enables

The emotion isn't an accident — it's a design choice. If it's not intentional, it's slop.

### The Screenshot Test: Hierarchy at Scale

Take the current design. Shrink the screenshot to 25% of its original size (or squint hard). Can you still see:
- Where the primary action is?
- The visual hierarchy between sections?
- Where to look first?

If everything blurs into sameness at 25%, the hierarchy is broken. This test exposes designs that have good spacing but no visual weight differentiation — everything is equally important, which means nothing is important.

**Correct example:** A SaaS dashboard where the primary "Create Project" button is visually obvious even at 25% (large, high-contrast color), secondary actions are smaller and muted, and the data grid is clear without its text.

**Incorrect example:** A landing page where the hero heading, subheading, two buttons, and background gradient are all visual equals — you can't tell what to look at first even when viewing full-size.

### Information Density: The Breathing Room Test

Is the screen breathing or suffocating?

- **Suffocating (density too high):** Every pixel filled, no whitespace, lots of copy, too many UI elements. User feels overwhelmed. Hard to find what you need.
- **Breathing (optimal):** Sections separated by whitespace, generous padding, elements have room to exist. User can focus.
- **Empty (density too low):** So much whitespace that the content feels insignificant. A single card floating on a page makes the page feel unfinished.

The right density matches the content. A data-heavy admin panel needs density; a meditation app needs breathing room. Density and purpose must align.

---

## Section 2: AI Slop Pattern Detection

THIS IS CRITICAL for vibe-coding designers. When Claude generates UI, it falls into predictable patterns that look "good enough" but lack craft. A senior designer spots these instantly. Learn to spot them in your own (and Claude's) output, then fix them before shipping.

### Pattern: Generic Hero Sections

**What it looks like:**
- Large centered heading (40-60px)
- Descriptive subheading below
- Two buttons side by side (Primary + Secondary)
- Stock gradient background or hero image
- Perfectly symmetrical, perfectly safe

This is the default. Every AI landing page looks like this because it's statistically common in training data.

**Why it happens:**
Claude sees "hero" in the context, looks at 1000 landing pages, and averages them. The result: competent but invisible.

**The fix:**
Make the hero SPECIFIC to the product. Show the product, don't describe it.
- Replace the gradient with a screenshot of the actual product in use
- Show a real customer use case in the hero, not abstract benefits
- Put the CTA off-center or integrated into content, not symmetrical buttons
- Use specific language ("Sync your calendar with 200+ tools" not "Powerful integrations")

**Correct example:** A scheduling app hero shows a calendar with a real meeting, a notification, and a booking happening — the product in motion, not described.

**Incorrect example:** "The easiest way to manage your schedule" over a blue gradient with "Get Started" and "Learn More" buttons.

---

### Pattern: Card Grid Sameness

**What it looks like:**
- Three identical cards in a row
- Each card: icon + heading + description
- All cards same size, same structure, same visual weight
- Sometimes 6 cards (2x3 grid), same pattern
- No hierarchy between cards
- Scrolls on mobile to a single column (reactive, not intentional)

**Why it happens:**
Cards are the easiest pattern to repeat. AI defaults to: map data to identical cards, iterate.

**The fix:**
Introduce intentional variation:
- Feature one card (larger, different color, additional detail)
- Vary card sizes: 1 large card + 2 small, or 2 medium + 1 small
- Put the most important card first and emphasize it
- Use a featured card pattern with more copy and visuals on one card
- If you have 6 cards, break them into two sections with different layouts

**Correct example:** A features page where the "core value" feature is 2x size with a screenshot, and supporting features are smaller cards in a 2x2 grid.

**Incorrect example:** Six identical feature cards in a 3x2 grid, all same size, all same structure.

---

### Pattern: Decoration Over Meaning

**What it looks like:**
- Gradients used because they look "modern"
- Glassmorphism (frosted glass effect) on cards that don't need it
- Shadows that don't match the depth they're trying to create
- Animated floating shapes in the background
- Rounded corners so extreme (48px on small buttons) that they serve no function
- Color overlays on images "for design"

**Why it happens:**
AI sees these in design systems and uses them as visual seasoning. They look "premium." They're a shortcut to feeling designed.

**The fix:**
Ask of every decorative element: "If I remove this, does the user lose anything?"

If the answer is "no," remove it. Every shadow should show depth. Every gradient should serve contrast or visual continuity. Every rounded corner should match the design language.

A 16px gradient from blue to purple on a button is decoration. A gradient that connects the hero (blue) to the footer (purple) is coherence.

**Correct example:** A button with a subtle shadow (1-2px blur, aligned to light source) that shows it's above the surface.

**Incorrect example:** A button with three layered shadows (inner, outer, bottom), a gradient background, and a glassmorphic overlay — technically impressive, functionally confusing.

---

### Pattern: Spacing That's "Close Enough"

**What it looks like:**
- 14px padding on one component
- 18px on another
- 22px somewhere else
- They're all "close" so it looks okay, but no system
- Sometimes 12px, sometimes 16px, sometimes 20px
- Not aligned to a grid

**Why it happens:**
AI generates numbers that "look reasonable" — 14px seems fine, 18px seems fine. No reason to pick 16px specifically if 18px looks good.

**The fix:**
Snap to a spacing scale. Industry standard is 8px base:
- 8, 16, 24, 32, 40, 48, 56, 64, 72, 80...

Or 4px if you need more granularity:
- 4, 8, 12, 16, 20, 24, 28, 32, 36, 40...

Every space on your page should be one of these values. It looks intentional because it IS intentional.

**Correct example:** All padding is either 16px or 24px (depending on hierarchy), all gaps between sections are 48px or 64px.

**Incorrect example:** Component padding is 14px, section gap is 18px, card padding is 12px, hero padding is 20px.

---

### Pattern: Typography Sameness

**What it looks like:**
- H1: 32px
- H2: 28px
- H3: 24px
- Body: 16px
- Technically different sizes, but they don't LOOK different
- No bold, no color contrast, no personality between levels
- A casual glance doesn't show hierarchy

**Why it happens:**
AI picks safe, proportional sizing (each heading is roughly 1.1-1.2x the previous). Mathematically coherent, visually flat.

**The fix:**
Headings should be OBVIOUSLY bigger. Go bigger than feels safe.

Common working scale:
- H1: 48-56px
- H2: 32-40px
- H3: 24-28px
- Body: 16px
- Small text: 14px

Add weight variation: H1 can be bold (700), H2 can be medium (600), body is normal (400). Color helps: headings darker, body text medium gray.

**Correct example:** H1 is 52px bold, H2 is 36px medium, body is 16px regular. Hierarchy is immediately clear.

**Incorrect example:** H1 is 36px regular, H2 is 32px regular, H3 is 28px regular. They're different but don't feel obviously different.

---

### Pattern: Color Over-Application

**What it looks like:**
- The primary brand color (e.g., blue) on buttons, links, badges, borders, backgrounds
- Appears on 20+ elements across the page
- Nothing stands out because everything is the same color
- Secondary actions lost in the noise

**Why it happens:**
The primary color is the "hero color" in the design system, so AI uses it liberally.

**The fix:**
Primary color = primary actions ONLY.

Everything else uses a neutral palette:
- Primary actions (CTAs, main button): primary color
- Secondary actions (links, secondary buttons): gray or muted variant
- Backgrounds: white or near-white
- Accents: use secondary/tertiary colors sparingly
- Text: dark gray for body, darker for headings

When everything is blue, blue has no power. When only the one button that matters is blue, that button commands attention.

**Correct example:** One "Sign Up" button in brand blue; all other buttons are outlined in gray. Links are brand blue (acceptable), but icons and decorative elements are neutral gray.

**Incorrect example:** Primary nav, buttons, badges, section borders, link text, and highlight colors all use the brand blue.

---

### Pattern: Fake Personality

**What it looks like:**
- Emoji everywhere (😊, 🚀, ✨)
- Overly casual copy ("Let's goooo!")
- Rounded corners pushed to extremes (corners round so much they're almost circular on small buttons)
- Lots of colorful gradients and bouncy animations
- Friendly tone used as a substitute for clear information architecture

**Why it happens:**
AI interprets "modern" and "approachable" as "friendly decoration." Personality becomes a layer on top instead of a core choice.

**The fix:**
Personality comes from intentional design choices, not surface decoration.

Real personality:
- Consistent visual language (rounded OR sharp, dense OR spacious, minimal OR ornate)
- Specific copy that's honest ("No credit card required" not "Let's goooo")
- Coherent motion (if bouncy, everything bounces; if subtle, everything is subtle)
- Design that serves user goals first, feels approachable second

Emoji work if they're functional (status icons) not decorative. Casual copy works if it's specific and honest. Rounded corners work if they're part of the system, not random kindness.

**Correct example:** A fintech app with playful illustrations but precise copy, consistent rounded corners (16px), and warm colors that feel approachable but trustworthy.

**Incorrect example:** A productivity app with emoji in section headings, "Let's boost your productivity!" copy, inconsistent corner radius (32px on buttons, 8px on cards), and three different animation styles.

---

### Pattern: Hover-State Theater

**What it looks like:**
- Every interactive element has an elaborate hover effect
- Cards rotate slightly when hovered
- Buttons glow or grow when hovered
- Text elements have fancy underline animations
- Hover on non-interactive elements (headings, static text)

**Why it happens:**
AI sees hover states in design systems and applies them broadly as a sign of "craft." More animation = more polished.

**The fix:**
Hover states on interactive elements only. Keep effects subtle.

What needs hover:
- Buttons
- Links
- Cards that are clickable
- Form inputs
- Anything the user might click on

What doesn't need hover:
- Headings
- Static text
- Images
- Decorative elements
- Non-interactive containers

Hover effects should be subtle:
- Button: 10% brightness change + subtle scale (1.02-1.05)
- Link: color change + underline
- Card: lift (very slight shadow increase) + slight background change

Avoid:
- Rotation
- Skew
- Complex multi-step animations
- Anything that makes the element feel unstable

**Correct example:** Buttons slightly brighten and subtly grow (1.05x) on hover. Cards lift 2px (shadow change shows depth). Links change color. That's it.

**Incorrect example:** Cards rotate 2 degrees and scale 1.1x. Buttons glow. Static headings have underline animations. Text entries have spin effects on focus.

---

### Pattern: Component Repetition Without Variation

**What it looks like:**
- The same card/list/section layout repeated identically 5+ times in a row
- A vertical list of 8 identical items
- Six feature cards, all structurally identical
- No rhythm breaks, no visual relief

**Why it happens:**
AI sees the pattern (card = good container) and applies it systematically. In data-heavy contexts, repetition is unavoidable, but design can introduce rhythm.

**The fix:**
Break long sequences with variation:
- After 3 identical cards, add a featured card (larger, different layout)
- After a list of 5 items, add a section break (heading, divider, whitespace)
- Use a pull-quote or testimonial between repetitive sections
- Every 3 cards, vary the layout (1 large + 2 small, instead of 3 medium)
- Use accent cards: every 4th card is a different color

Real design has rhythm. Monotony reads as unfinished.

**Correct example:** A pricing page with 3 pricing cards, then a feature comparison table (different layout), then 3 more cards but with one featured. Rhythm established.

**Incorrect example:** Eight identical pricing tiers in a single column, all same height, all same structure.

---

### Pattern: Missing Empty/Error/Loading States

**What it looks like:**
- The design shows only the happy path
- Dashboard with data populated
- Lists with items
- No empty states (new user, just signed up, no projects yet)
- No loading skeletons (while fetching)
- No error states (connection failed, invalid input)
- No 404 pages

**Why it happens:**
AI generates the "full" view first. Edge cases feel like edge cases. But new users see empty states before they see data.

**The fix:**
Design empty, loading, and error states as first-class screens.

**Empty state:**
- Clear message: "You don't have any projects yet"
- Visual cue: illustration or icon (not distracting, shows empathy)
- Clear CTA: "Create your first project" (same button style as normal CTAs)
- Optional: tips or guided steps

**Loading state:**
- Skeleton screens matching the layout (not generic spinners)
- Shimmer or pulse animation (not spinning icons)
- Text placeholders, card placeholders, image placeholders — all matching real layout

**Error state:**
- Clear error message ("Username already taken" not "Error 409")
- What went wrong (specific)
- How to fix it (actionable)
- Retry option

These aren't edge cases. They're the first screens new users see.

**Correct example:** Blank dashboard shows "Get started in 3 steps" with illustrated prompts. Data loading shows skeleton cards with shimmer. Connection error shows "Can't reach the server — check your connection" with a Retry button.

**Incorrect example:** Only the populated dashboard is designed. New users see nothing. Loading is a spinning icon. Errors show error codes.

---

### Pattern: Contrast Theater

**What it looks like:**
- Text passes WCAG contrast check in theory
- But text is small (14px), thin weight (300), on a textured or gradient background
- Technically 4.5:1 on the solid color portion, but unreadable in practice
- Light gray text on white that "passes" because the specific gray is #767676

**Why it happens:**
AI checks the contrast ratio between two flat colors. It doesn't account for font weight, size, background complexity, or real-world viewing conditions (outdoor, dim screen, aging eyes).

**The fix:**
Contrast is a floor, not a ceiling. Aim for 7:1 for body text (WCAG AAA). For text below 16px or weight below 400, add an extra 1.5:1 margin above the minimum. Never place text on gradients or images without a solid overlay.

**Correct example:** Body text at 16px/400 weight uses #333333 on white (12.6:1). Readable in any condition.

**Incorrect example:** Helper text at 13px/300 weight uses #767676 on white (4.5:1). Passes the checker, fails the user.

---

### Pattern: Single-Breakpoint Responsiveness

**What it looks like:**
- Design looks great at 1440px (designer's screen)
- Looks okay at 375px (iPhone mockup)
- Falls apart at 768px (iPad), 1024px (small laptop), 320px (SE)
- Content overflows, columns stack badly, whitespace collapses

**Why it happens:**
AI generates for two widths: desktop and mobile. Everything between is an afterthought because training data skews toward full-width and phone screenshots.

**The fix:**
Design for fluid, not fixed. Use `clamp()`, percentage widths, and container queries instead of fixed breakpoints. Test at 5 widths minimum: 320px, 480px, 768px, 1024px, 1440px. Content should reflow naturally, not jump between layouts.

**Correct example:** A card grid that uses `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` — cards reflow at every width without breakpoints.

**Incorrect example:** A card grid with `@media (max-width: 768px) { grid-template-columns: 1fr; }` — jumps from 3 columns to 1 column with nothing in between.

---

### Pattern: Orphaned Interactive States

**What it looks like:**
- Buttons have hover and active states
- No focus-visible ring (keyboard users invisible)
- No disabled state (or disabled looks like default with `opacity: 0.5`)
- No loading state (user clicks, nothing happens for 2 seconds)
- No error state on the component itself

**Why it happens:**
AI generates the visual states it "sees" most often: default, hover, maybe active. Focus, disabled, loading, error, and success are functional states that require intentional design, not visual memory.

**The fix:**
Use the 8-state model from `interaction-design.md`. Every interactive component needs: default, hover, focus, active, disabled, loading, error, success (where applicable). Define all states upfront — don't add them when bugs are reported.

**Correct example:** A button component with explicit CSS for all 8 states, including `focus-visible` with a 2px offset ring and a loading spinner that replaces the label.

**Incorrect example:** A button with `:hover` and nothing else. Keyboard users can't see focus. Submitting shows no feedback for 3 seconds.

---

### Pattern: Icon-Label Mismatch

**What it looks like:**
- A gear icon labeled "Preferences" (not "Settings")
- A heart icon for "Bookmark" (not "Favorite")
- A paper plane icon for "Submit" (not "Send")
- A cloud icon for "Sync" (inconsistent with the download icon next to it)

**Why it happens:**
AI picks icons that are semantically adjacent but not precise. A gear "kind of" means preferences. A heart "sort of" means bookmark. The mismatch is subtle enough that it passes casual review but creates micro-confusion for every user interaction.

**The fix:**
Icon and label must say the same thing. If the label says "Settings," the icon must be universally recognized as "settings" (gear). If you can't find an icon that precisely matches, use the label alone — no icon beats a wrong icon.

**Correct example:** Gear + "Settings", Trash + "Delete", Download arrow + "Download".

**Incorrect example:** Heart + "Bookmark", Cloud + "Save", Bell + "Updates".

---

### Pattern: Uniform Border Radius

**What it looks like:**
- Every element uses `border-radius: 12px`
- Small badges (24px tall) look like pills
- Large cards look slightly rounded
- Buttons, inputs, cards, modals — all identical radius
- Nothing feels intentionally shaped

**Why it happens:**
AI applies one radius value uniformly. It's "consistent" in the worst sense — consistent like a monotone voice is consistent.

**The fix:**
Scale border radius with element size. Small elements get smaller radius; large elements get larger radius. Create a radius scale tied to the spacing system.

```
Radius scale:
- xs (badges, tags): 4px
- sm (buttons, inputs): 6-8px
- md (cards, dropdowns): 12px
- lg (modals, dialogs): 16px
- full (avatars, toggles): 9999px
```

**Correct example:** Buttons at 8px radius, cards at 12px, modal at 16px, avatar at full circle. Each element feels intentionally shaped.

**Incorrect example:** Everything at 12px. Badges look like pills, buttons look like cards, nothing has visual distinction.

---

### Pattern: Stock Illustration Syndrome

**What it looks like:**
- Purple/blue gradient blobs as backgrounds
- Isometric illustrations of people at computers
- Abstract 3D shapes floating in hero sections
- Illustrations that could belong to any company
- "Diverse team of professionals" stock imagery

**Why it happens:**
AI reaches for the most statistically common visual patterns: gradient blobs (Stripe-era), isometric illustrations (2018-era SaaS), and abstract 3D (2020-era landing pages). These are visual comfort food — recognizable, safe, meaningless.

**The fix:**
Illustrations should be specific to your product. Show the actual product in use. If you must use illustrations, commission or generate ones that reflect your specific brand identity — not generic "tech company" imagery. If you can't do custom, use no illustrations. Clean whitespace beats generic stock.

**Correct example:** A project management tool showing an actual screenshot of a Kanban board with realistic tasks, or a custom illustration of the specific workflow the product enables.

**Incorrect example:** A project management tool hero with an isometric illustration of people standing around a giant calendar that could be any productivity app.

---

### Pattern: Navigation Overload

**What it looks like:**
- Top nav with 8+ items
- Sidebar with 15+ links
- Footer with 30+ links in 5 columns
- Breadcrumb + tabs + sidebar all visible simultaneously
- Mobile hamburger menu opens to reveal 20+ items in a flat list

**Why it happens:**
AI includes every page/feature as a navigation item. It treats nav as a complete index rather than a curated path. More complete = better, in AI logic. But more complete = overwhelming for users.

**The fix:**
Navigation should show 5-7 top-level items maximum (Miller's Law). Group related items under clear categories. Use progressive disclosure: primary nav visible, secondary nav on interaction. Mobile nav should prioritize the 4-5 most-used items, with "More" for the rest.

**Correct example:** Top nav with 5 items (Home, Features, Pricing, Docs, Sign In). Docs page has its own sidebar for sub-navigation. Clean separation.

**Incorrect example:** Top nav with Home, Features, Pricing, About, Blog, Docs, API, Community, Support, Careers, Contact, Partners, Press. User can't find anything because everything is there.

---

### Pattern: Premature Dark Mode

**What it looks like:**
- Dark mode implemented as `filter: invert(1)` or naive color swap
- Images inverted (photos look like negatives)
- Shadows don't work (light shadows on dark backgrounds disappear)
- Contrast breaks (text that was dark-on-light becomes light-on-dark but not enough contrast)
- Colors that vibrate (fully saturated colors on dark backgrounds)

**Why it happens:**
AI treats dark mode as a color swap rather than a redesign. Light mode tokens get inverted rather than re-evaluated. The assumption is: flip the background, flip the text, done.

**The fix:**
Dark mode is a separate design pass, not an inversion. Each color token needs a dark-mode-specific value. Reduce saturation. Increase surface elevation differences (use lighter grays for raised surfaces, not shadows). Test every screen in dark mode independently.

See `dark-mode.md` for the full dark mode reference. Key rules:
- Never use `filter: invert()` — it breaks images, SVGs, and brand colors
- Desaturate all colors by 10-20% for dark backgrounds
- Use surface elevation (lighter = higher) instead of shadows
- Test contrast ratios separately for dark mode — don't assume light mode ratios carry over

**Correct example:** Dark mode with hand-tuned token values: `--surface-raised: #2a2a2a` (lighter than `--surface-base: #1a1a1a`), desaturated primary, elevated cards distinguished by surface color rather than shadow.

**Incorrect example:** Dark mode via `html.dark { filter: invert(1) hue-rotate(180deg); }`. Photos are inverted, brand colors are wrong, and some elements have doubled inversion.

---

## Section 3: Cross-Page Consistency Audit

### Why Consistency Matters Beyond Aesthetics

Inconsistency erodes trust. If a button looks different on the dashboard and the settings page, users wonder: "Are these the same action or different?" If navigation moves between pages, users feel disoriented.

Consistency isn't boring — it's a contract. When users learn that blue buttons are primary actions, that compact cards are clickable, that sections are separated by 64px, they navigate faster and more confidently.

Inconsistency makes even good design feel amateur.

### The Consistency Audit Checklist

Pick 3-5 recurring elements that appear across multiple pages:
- Buttons (primary, secondary, tertiary)
- Cards or list items
- Headings (H1, H2, H3)
- Spacing between sections
- Navigation and header

For each element, open the pages where it appears and compare:

**Buttons:** Same padding? Same corner radius? Same font weight? If "Primary Button" appears on the homepage, dashboard, and settings page, does it look identical?

**Cards:** Same shadow? Same padding? Same corner radius? Same text hierarchy within the card?

**Headings:** Same size, weight, color for each heading level across pages?

**Spacing:** Section gaps the same? Padding within components the same?

**Navigation:** Position, height, styling, animation — identical?

Any deviation = flag it. Document it. Fix it.

### Component Consistency

Same component = same everywhere.

If a "project card" on the dashboard shows an icon, title, description, and date, the project card on the "recent projects" page should have the same structure. Not similar — identical (unless there's a clear intentional reason for variation).

Variations are okay if intentional:
- Featured card vs standard card (same structure, different size/color)
- Mobile card vs desktop card (responsive, but same proportions)
- Hover/active state (same structure, different visual state)

Unintentional variations are confusing:
- Card with icon on one page, no icon on another
- Card with 12px padding here, 20px padding there
- Card with rounded corners on dashboard, sharp corners on settings

### Spacing Rhythm

Vertical rhythm is the heartbeat of a design. If page A separates sections with 64px and page B uses 48px, users feel the inconsistency even if they can't name it.

Pick a spacing increment (typically 8px base: 16, 24, 32, 48, 64, 80, 96).

Audit: what is the gap between major sections?
- Same on every page?
- If not, is there a reason? (modal windows might be tighter; data-heavy pages might be denser)
- Document the rule and enforce it

**Correct example:** All pages use 64px between major sections, 24px between subsections. Even dense pages respect this (just tighter content within sections).

**Incorrect example:** Homepage uses 64px, dashboard uses 48px, settings uses 56px. No system.

### Color Usage Consistency

The primary color should mean the same thing on every page. If blue = primary action on the dashboard, blue shouldn't mean "information" on the settings page.

Audit color usage across pages:
- Primary color: where does it appear? Only on primary CTAs? Always?
- Secondary color: consistent meaning?
- Accent color: used the same way?
- Neutral palette: background, text, borders — consistent?

**Correct example:** Blue = primary action everywhere (buttons, main navigation). Gray = secondary actions. Red = only errors or destructive actions.

**Incorrect example:** Blue = buttons on dashboard, links on settings, badges on homepage. Users can't build a mental model.

### Typography Consistency

H2 should be the same size/weight/color on every page. Not "close" — identical.

Audit each heading level:
- H1: 48px bold on every page?
- H2: 32px medium on every page?
- Body: 16px regular on every page?

If they vary, document why. If there's no reason, standardize.

Same for text colors: body text should be the same gray across pages. Links should be the same color.

**Correct example:** H2 is 32px bold #1a1a1a on every page. If you see H2, you know what size it is.

**Incorrect example:** H2 is 32px on the homepage, 28px on the dashboard, 36px on blog posts.

### Interactive Pattern Consistency

If cards are clickable on one page, similar cards should be clickable everywhere (or obviously non-clickable with different styling).

Users learn: "These cards are links." Don't break that expectation.

Audit interactive patterns:
- Cards: clickable everywhere they appear, or obviously not?
- Lists: selectable everywhere, or obviously not?
- Images: lightbox on some pages but not others?
- Hover states: consistent across similar elements?

**Correct example:** Feature cards are always clickable (link styling, hover effect). Case study cards are always clickable. Article cards are always clickable. Users know: if it's a card, I can click it.

**Incorrect example:** Feature cards are clickable on the homepage but not on the about page. Users click expecting a link and nothing happens.

### Navigation Consistency

Navigation position, style, and behavior should never change across pages.

The moment navigation moves or changes, users feel disoriented. The moment the logo is in different positions, the moment the search bar disappears on one page, the moment the menu style changes — users lose their sense of location.

Audit:
- Navigation always in the same position? (top, left sidebar, bottom)
- Navigation always visible or consistently hidden?
- Logo/home link in the same place?
- Search bar always visible?
- Menu items in the same order?
- Mobile menu consistent across pages?

**Correct example:** Top navigation visible on all pages, logo left side, menu right side, hamburger menu on mobile consistently styled.

**Incorrect example:** Navigation on top of homepage, in a sidebar on the dashboard, at the bottom of the blog. Logo is top-left on some pages, center on others.

---

## Section 4: Visual Coherence

The difference between "all the rules pass" and "this feels like a real product."

### What Coherence Is

Coherence = every design decision reinforces the same identity.

A finance app with playful rounded illustrations, a corporate serif font, and neon colors lacks coherence. Each element says something different:
- Playful illustrations say: "This is fun and experimental"
- Corporate serif says: "This is serious and trusted"
- Neon colors say: "This is edgy and modern"

The user gets confused. Which identity is real?

Real coherence: all elements whisper the same story.

### The Brand Whisper Test

Cover the logo. Can you still tell what kind of product this is?

A product with coherence broadcasts its identity through design alone:
- Finance app: clean, professional, calm colors, grid-based, data-focused
- Creative tool: playful, colorful, asymmetric layouts, expressive typography
- Healthcare app: warm, approachable but trustworthy, illustrations of people, gentle colors
- Developer tool: minimalist, technical, monospace fonts, dark mode option

If you remove the logo and the product identity is gone, the design isn't doing the work.

**Correct example:** A creative agency portfolio has asymmetric layouts, bold colors, expressive photography, and playful typography. You see a project and immediately sense "creative" without reading the company name.

**Incorrect example:** A startup has the logo, but the design is generic: clean cards, stock photos, blue buttons, sans-serif font. Could be anything. Remove the logo and it's just "company site."

### Visual Language Coherence

Does the design have a consistent visual language?

Visual language = the sum of choices about:
- Corners: rounded (friendly) vs sharp (modern)
- Borders: thin (elegant) vs thick (bold)
- Decoration: minimal (clean) vs ornate (rich)
- Density: spacious (calm) vs dense (intense)
- Color: muted (professional) vs vibrant (energetic)
- Typography: geometric sans-serif (modern) vs humanist sans-serif (friendly) vs serif (traditional)

Pick an identity and commit. Mixing creates confusion:
- Rounded corners on buttons (friendly) + sharp geometric sans-serif (modern and cold) = mixed message
- Minimal layout (clean) + ornate serif typography (classical) = mixed message
- Spacious, calm colors (serene) + playful emoji (energetic) = mixed message

All elements should reinforce the same visual language.

**Correct example:** A meditation app: rounded corners, spacious layout, warm (not neon) colors, humanist sans-serif, soft shadows, illustrations of people and nature. Every element says "calm and safe."

**Incorrect example:** A meditation app: rounded buttons, sharp sans-serif headings, spacious layout, bright neon green and purple, geometric icons, lots of emoji. Visual chaos.

### Motion Coherence

All animations should share the same personality.

If you have bouncy easing curves (elastic, playful) on some elements and linear easing (robotic, utilitarian) on others in the same product, it feels disjointed.

Audit animations:
- Are they all similarly playful, or all similarly subtle?
- Do they all move at similar speeds?
- Do they all use similar easing curves?
- Is there a consistent animation language?

**Correct example:** Transitions are all subtle and quick (200-300ms easing-out). Button clicks have a simple scale animation. Card hovers have a slight lift. Navigation changes fade in. All consistently refined.

**Incorrect example:** Button clicks bounce (elastic). Card hovers fade in over 1 second (slow). Navigation changes snap instantly. Modal opens with a wild spring animation. No coherent motion personality.

### Copy Coherence

Does the UI copy match the visual tone?

Playful design + formal copy (or vice versa) creates cognitive dissonance.

Audit copy:
- Is it consistent in tone with the visual design?
- If the design feels playful, is the copy casual and friendly?
- If the design feels corporate, is the copy formal and precise?
- Do error messages, empty states, and CTAs all use the same voice?

**Correct example:** A playful note-taking app with rounded design, colorful icons, and copy like "Jot down your thoughts" and "No notes yet — let's create one!" matches the personality.

**Incorrect example:** The same design with copy like "Add a note object to the system" and "No data found in database." The copy contradicts the visual tone.

### Intentionality Test

Can you explain WHY every design choice was made?

Ask yourself about a random element:
- Why is this button blue and that one gray? (Because blue is primary action, gray is secondary)
- Why is this heading 32px and that one 28px? (H2 vs H3 — different hierarchy levels)
- Why are corners 16px? (Matches our design system scale)
- Why is this section 64px from the next? (Our standard section spacing)

If a choice was made "because it looks nice" or "because it's the default," it's probably not coherent with the system.

Every design choice should reinforce the identity:
- Blue isn't blue because blue is pretty; it's blue because it's the primary action color
- 16px corners aren't arbitrary; they're part of the design language
- Spacing isn't random; it follows a rhythm
- Copy tone isn't casual "because friendly"; it matches the visual identity

**Correct example:** Every color, size, spacing, and animation choice traces back to either a systematic rule or a deliberate product identity choice.

**Incorrect example:** Multiple shades of blue used throughout (different blues in different places), spacing that's "close enough" but not systematic, some elements feel playful and others formal.

---

## Putting It Together: The Senior Designer's Eye

The difference between junior and senior design isn't knowledge — it's automaticity. Seniors spot slop instantly because they've internalized the patterns.

When you review a design:

1. **First Impression (5 seconds):** Does it feel coherent? Does it communicate identity? Does hierarchy exist?

2. **Slop Patterns (30 seconds):** Scan for the 18 patterns above. Generic hero? Card grid sameness? Orphaned states? Stock illustrations? Flag them.

3. **Consistency Audit (2 minutes):** Pick 3 elements. Check them across pages. Anything inconsistent?

4. **Intentionality (1 minute):** Can you explain the why? Is every choice systematic or deliberate?

If the design passes all four, it's professional. If it fails any, you've found the work.

This is the taste layer — the thing that separates AI-generated work from designed work. Train it. Use it to critique your own output and Claude's output. It becomes your eye.

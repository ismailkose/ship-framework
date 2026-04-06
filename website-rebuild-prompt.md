# Ship Framework Website — Rebuild Prompt

Rebuild the Ship Framework landing page with these improvements. Keep the dark terminal aesthetic and dot-matrix headline font. The page structure is: Hero → Problem → Team → Commands → Get Started → Footer.

## 1. Hero Section — Terminal Animation (MOST IMPORTANT)

Replace the current simple terminal that just types the command. Build a full animated terminal conversation that shows the team working:

```
$ /ship-team I want to build a mood journal that uses color instead of words

[Vi]   Who journals with color? People who feel deeply but freeze at a
       blank page. The magic moment: tap a color, see it bloom. 4 seconds.

[Arc]  Build order — 5 features, RICE-scored. Color picker first.
       Stack: Next.js + Framer Motion + OKLCH color space.

[Dev]  Feature 1 done. Radial color picker with haptic zones.
       All tests passing. Committed: 'Add core mood capture flow'

[Eye]  Screenshot captured. Touch targets are 38px — needs 44px minimum.

$ /ship-review

[Crit] 🔴 No error boundary — app white-screens if color API fails.

[Pol]  Design audit — "contrast theater" detected on gradient header.
       Kill the gradient. Colors pop now. This looks like a real product.

$ fix Crit's red issue. ship it.

[Dev]  Error boundary added. Gradient replaced. Tests passing.

[Cap]  ✅ Live at mood-color.vercel.app
       Go get your first user.
```

Animation behavior:
- The `$` command lines type character by character (like someone is typing)
- Each `[Persona]` response fades in as a block after a short delay
- Persona tags `[Vi]`, `[Arc]`, `[Dev]` etc should have a subtle color: Vi=blue, Arc=purple, Dev=green, Crit=red, Pol=amber, Eye=cyan, Cap=orange
- After the full animation plays, it should loop (fade out, restart)
- Terminal should have a dark background (#1a1a2e or similar), subtle border, and `[ CLAUDE CODE ]` header like the current design
- The terminal should be prominently sized — it IS the hero, not an afterthought

## 2. Reduce Dead Space

Cut vertical padding between all sections by 40-50%. The current gaps are too large and make the page feel empty. Sections should flow together with clear visual separation (subtle horizontal lines are fine) but not massive black voids.

## 3. Problem Section — Before/After Instead of Abstract Text

Replace the numbered 01/02/03 list with a visual before/after comparison:

**Left column: "Raw Claude Code"**
Show a terminal-style block with generic, unreviewed output:
```
$ build me a habit tracker
Sure! I'll create a habit tracker app...
[generates 500 lines of code with no plan, no review, generic UI]
```

**Right column: "With Ship Framework"**
Show the team-style output:
```
$ /ship-team build a habit tracker
[Vi]  Who needs this? What do they do today instead?
[Arc] 6 features, prioritized. Magic moment first.
[Crit] 3 issues found. Fixing before ship.
[Cap] ✅ Live. Measurement plan filed.
```

Label the left "One brain. No pushback." and the right "Eight specialists. Every angle covered."

## 4. Team Grid — Add Personality

Each persona card should have:
- A subtle accent color on the left border or top (Vi=blue, Arc=purple, Dev=green, Crit=red, Pol=amber, Eye=cyan, Test=slate, Cap=orange)
- A small monospace icon/emoji in the corner (Vi=💡, Arc=🏗, Dev=⚡, Crit=🔍, Pol=✨, Eye=📸, Test=🧪, Cap=🚀)
- On hover: subtle glow in the persona's accent color
- Keep the current 4x2 grid layout, it works well

## 5. Commands Section — Make Interactive

Each command row should expand on click/hover to show a mini preview of what happens:

```
/ship-team    → "The full pipeline. Plan, build, review, test, ship."
/ship-review  → "Crit finds bugs. Pol catches slop. Eye screenshots."
/ship-launch  → "Pre-flight checks, deploy, post-deploy verify, measurement plan."
/ship-fix     → "3-strike debugging. Systematic, not random guessing."
/ship-money   → "Pricing strategy, payment integration, growth levers."
/ship-browse  → "Research competitors, find inspiration, extract patterns."
```

## 6. Add GitHub Stars Badge

Near the hero buttons (Get Started / How It Works), add a live GitHub stars count:
- Fetch from GitHub API: `https://api.github.com/repos/ismailkose/ship-framework`
- Display as: `★ {count} stars` with a subtle badge style
- If API fails, hide the badge gracefully

## 7. Add Sticky Navigation

Add a minimal sticky header at the top:
- Left: "SHIP FRAMEWORK" in the dot-matrix font (small)
- Right: anchor links — "Team" · "Commands" · "Get Started" · GitHub icon
- Background: transparent when at top, dark with blur when scrolled
- Should feel minimal, not heavy

## 8. Get Started Section

Keep the current install code block but update the setup instructions:
```bash
git clone https://github.com/ismailkose/ship-framework.git
cd your-project
bash ship-framework/setup.sh
```

And add a note below: "Works with Claude Code v2.1.88+. Installs 16 slash commands, 19 design references, 8 AI personas."

## 9. Footer

Keep it minimal. Add:
- "Built for designers who vibe code." tagline
- The version: v2026.03.31

## Technical Notes

- Use Framer Motion for the terminal typing animation and section transitions
- Use `next/font` for the dot-matrix display font (try "Share Tech Mono" or "VT323" from Google Fonts for the headline, keep a clean sans-serif for body text)
- All persona accent colors should use OKLCH for perceptual uniformity if possible
- The terminal animation is the hero — spend the most time making it feel real and satisfying
- Make sure mobile is responsive: terminal scales down, team grid goes to 2x4 or single column
- Add subtle scroll-triggered fade-in animations for each section

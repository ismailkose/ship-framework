# Changelog

All notable changes to Ship Framework are documented here. Versions use date-based format (`YYYY.MM.DD`).

To update an existing project, run `bash update.sh` — it handles everything automatically.

---

## 2026.03.17 — Animation Reference

### Added
- `references/animation.md` — stack-agnostic animation reference with 4 sections
- **Section 1: Design Principles** — motion budget (limit competing patterns per screen, not element count), easing table, golden rules, spring configs, motion hierarchy
- **Section 2: Audit Checklist** — timing, easing, performance, accessibility, balance, and feel checks
- **Section 3: Build Rules** — CSS-first foundations (universal, works in any stack) + Framer Motion patterns (React). Data-attribute triggers, CSS custom properties for dynamic values, keyframe animations
- **Section 4: Pattern Library** — 8 reusable foundations based on Emil Kowalski's "Animations on the Web": reveal on hover, stacking & positioning, staggered reveal, shared element transition, dynamic resize, directional navigation, inline expansion, element-to-view expansion
- Motion budget concept: 1-2 simultaneous motion patterns per screen. A staggered group counts as one pattern
- Crit added as 6th agent checking animation balance
- Arc's motion system now emphasizes restraint alongside spec
- Dev references pattern library as learning material (adapt, don't copy)
- 3 deep-dive reference files (loaded conditionally to keep context lean):
  - `animation-css.md` — transforms, transitions, keyframes, clip-path, data-attribute patterns (universal)
  - `animation-framer-motion.md` — full API: components, AnimatePresence, variants, layout, gestures, drag, hooks (useScroll, useInView, useMotionValue, useSpring), MotionConfig (React only)
  - `animation-performance.md` — 60fps target, GPU properties, will-change, DevTools monitoring, reduced motion testing on each OS, focus management, accessible animation guidelines (universal)
- CHEATSHEET.md: Added Motion Budget quick reference with hierarchy table
- README.md: Added Animation Reference section, updated Arc and Crit descriptions

### Updated
- `template/.claude/commands/architect.md` — motion system includes budget + pattern awareness, scans Framer Motion deep-dive if stack uses it
- `template/.claude/commands/build.md` — references Section 4 patterns + all 3 deep-dives when needed
- `template/.claude/commands/critic.md` — animation balance check + performance deep-dive for diagnostics
- `template/.claude/commands/browse.md` — animation audit checklist + performance deep-dive for DevTools
- `template/.claude/commands/polish.md` — motion feel audit + CSS and Framer Motion deep-dives for specific feedback
- `template/.claude/commands/qa.md` — reduced motion testing + performance deep-dive for testing steps
- `template/references/animation.md` — Section 3B trimmed to pointer (no duplication with deep-dive)
- `setup.sh` — copies references/ directory during project setup
- `update.sh` — copies references/ during updates

### How to update
```bash
bash ship-framework/update.sh
```
This updates your slash commands, references/, cheatsheet, and version stamp. Your CLAUDE.md content and TASKS.md are untouched.

---

## 2026.03.16 — Initial Release

### Added
- 11 agents: Vi, Arc, Dev, Crit, Pol, Cap, Eye, Test, Bug, Retro, Biz
- 13 slash commands including `/team` orchestrator and `/status`
- `setup.sh` interactive setup (4 questions → full project scaffold)
- Built-in product frameworks: JTBD, HEART, RICE
- Multi-phase workflows for Eye (6 phases), Test (8 phases), Cap (7 phases), Retro (9 steps)
- QA health score system (0-100 with severity-based deductions)
- QA tiers: Quick, Standard, Exhaustive
- Retro data analysis: shipping streak, session detection, time patterns, hotspot analysis, trend comparison
- Optional Playwright browser support for Eye and Cap (real screenshots at desktop + mobile viewports)
- Graceful degradation: screenshot mode when Playwright is installed, code mode when it's not
- Takeover route: Arc → Crit → Vi → Biz → roadmap
- Health check route: Vi → Arc → Crit → Biz → Eye → prioritized roadmap
- Date-based versioning (`YYYY.MM.DD`) with VERSION file
- Version stamped into generated CLAUDE.md footer via setup.sh
- `update.sh` for updating existing projects (updates commands + cheatsheet, never touches CLAUDE.md content or TASKS.md)
- CHEATSHEET.md quick reference card with QA health score reference
- TASKS.md persistent task board with stage-specific starter tasks
- README with detailed agent descriptions, setup + update instructions, browser support docs, file structure

### Files
```
setup.sh
update.sh
VERSION
CHANGELOG.md
CHEATSHEET.md
README.md
template/CLAUDE.md
template/.claude/commands/ (13 files)
template/references/animation.md
```

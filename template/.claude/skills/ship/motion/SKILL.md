---
name: ship-motion
description: |
  Animation and motion design routing. (ship)
  Loaded by /ship-build, /ship-review, /ship-qa when animations are involved.
---

# Animation & Motion Skill

This skill routes personas to motion knowledge. Deep rules, timing standards, and patterns live in reference files.

**Reference files:**
- `.claude/skills/ship/motion/references/animation.md` — Motion budget, hierarchy, build rules, 8 pattern foundations
- `.claude/skills/ship/motion/references/animation-css.md` — CSS transforms, transitions, keyframes, View Transitions API
- `.claude/skills/ship/motion/references/animation-framer-motion.md` — Framer Motion API (React only)
- `.claude/skills/ship/motion/references/animation-performance.md` — 60fps optimization, reduced motion testing

## Priority Enforcement — What Blocks Shipping

| Priority | Gate | Reference |
|---|---|---|
| MANDATORY | `prefers-reduced-motion` respected — no exceptions | animation.md Section 2 |
| HIGH | Motion budget ≤2 simultaneous patterns per screen | animation.md Section 1 |
| HIGH | Transform/opacity only — never animate width/height/top/left | animation-performance.md Section 1 |
| HIGH | No `transition: all` — list properties explicitly | animation-css.md |
| MEDIUM | Timing within standard ranges (enter 200-300ms, exit 150-200ms) | animation.md Section 3 |
| MEDIUM | Interruptible — UI stays interactive during all animations | animation.md Section 4 |

## Quick Timing Reference

| Category | Duration | Easing |
|---|---|---|
| Micro-interactions | 100-150ms | ease-out |
| Entering | 200-300ms | ease-out |
| Moving | 200-300ms | ease-in-out |
| Exiting | 150-200ms | ease-in (60-70% of enter) |
| Hover | 150ms | ease |
| Page transitions | 300-400ms | ease-out |
| Stagger per item | 30-50ms delay | — |

**Hard limits:** Never >500ms. Enter >400ms = sluggish. Exit <100ms = jarring.

## Named Primitive Enforcement

If the project has a design contract (DESIGN.md with a motion section, or `design/motion.md`):

- **Every animation must reference a named primitive** by comment tag (e.g., `// motion: gentleEnter` in Swift, `/* motion: gentleEnter */` in CSS).
- **Raw animation values without a primitive tag are blocked.** If Dev writes `.animation(.spring(response: 0.38, damping: 0.85))` without a `// motion: <name>` comment, flag it.
- **New primitives require `/ship-design evolve`** — don't invent unnamed animations inline. Either use an existing primitive or propose a new one.
- If no design contract exists, fall back to the timing reference table above (no primitive enforcement).

Check `touch .claude/.refgate-dim-motion` after reading the motion section so the design gate allows motion-related edits.

## For Building (/ship-build)

When Dev builds animations:

1. **Named primitive check** — if DESIGN.md has a motion section, every new animation must reference a named primitive. Tag it with a comment: `// motion: <primitiveName>`.
2. **Motion budget** — read `.claude/skills/ship/motion/references/animation.md` Section 1. Is there room for this animation?
3. **Timing + easing** — use the table above. Read Section 3 for detailed rules.
4. **Reduced motion** — MANDATORY. Read Section 2 for implementation per platform.
5. **Performance** — read `.claude/skills/ship/motion/references/animation-performance.md` Section 1. Transform/opacity only.
6. **CSS implementation** — read `.claude/skills/ship/motion/references/animation-css.md` for transforms, transitions, keyframes.
7. **Framer Motion** — if using, read `.claude/skills/ship/motion/references/animation-framer-motion.md`.

## For Review (/ship-review)

When Pol or Eye review motion:

1. **Budget audit** — read `.claude/skills/ship/motion/references/animation.md` Section 1. Count simultaneous patterns. Flag >2.
2. **Purpose check** — is each animation serving the user or decorating? Animations used 50x/day should be minimal.
3. **Reduced motion** — verify `prefers-reduced-motion` is respected. If not, flag as Critical.
4. **Performance** — read `.claude/skills/ship/motion/references/animation-performance.md`. Flag layout-triggering properties.
5. **Direction** — forward nav pushes right/down, back pulls left/up. Flag reversals.

## For QA (/ship-qa)

When Test verifies motion:

1. **Reduced motion test** — enable in OS/browser. All animations disable or simplify. Pass/fail gate.
2. **Rapid interaction** — click/tap rapidly during animations. Must queue correctly.
3. **Performance** — monitor frame rate. Flag anything <30fps.
4. **Interrupt** — start animation, interact mid-way. Must respond, not lock up.

Read `.claude/skills/ship/motion/references/animation-performance.md` for full testing steps.

## See Also

- **UX skill** — cognitive principles informing motion (Doherty Threshold), tap targets on animated elements
- **Web skill** — `transition: all` ban, `transform-origin`, CSS performance rules
- **Components skill** — motion tokens in design token system

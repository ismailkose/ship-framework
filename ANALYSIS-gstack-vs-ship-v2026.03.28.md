# gstack vs Ship Framework — Complete Analysis

**Date:** 2026-03-29 (updated with gstack v0.13.0–v0.13.6 findings)
**Purpose:** Identify gaps, overlaps, and architecture decisions for Ship Framework v4
**Scope:** Codex cross-model support is in scope. Factory Droid is not.

---

## 1. Skill-by-Skill Mapping

### gstack Skills (30) vs Ship Commands (11)

| gstack Skill | Ship Equivalent | Gap / Notes |
|---|---|---|
| autoplan | plan.md + build.md | gstack auto-answers intermediate questions via 6 decision principles. Ship requires manual answers. |
| benchmark | — | **Gap.** gstack benchmarks skill quality with LLM-as-judge. Ship has no eval system. |
| browse | browse.md | Similar concept. gstack has a full Bun+Chromium daemon; Ship delegates to MCP. |
| canary | — | **Gap.** gstack deploys to staging and validates before prod. Ship has no canary concept. |
| careful | — | **Gap.** PreToolUse hook blocks destructive commands (rm -rf, DROP TABLE, git push --force). |
| codex | codex.md (PLANNED) | Cross-model verification: Claude builds, Codex reviews adversarially. Ship v4 will add this. |
| connect-chrome | browse.md | gstack installs a Chrome extension; Ship uses MCP browse. |
| cso | — | **Gap.** Chief Security Officer: secrets audit, dependency supply chain, STRIDE modeling. |
| design-consultation | — | **Gap.** Full design system creation with competitive research, 3-layer synthesis. |
| design-review | — | **Gap.** Live site audit: 80-item checklist, dual scores (Design + AI Slop), fix loop. |
| design-shotgun | — | **Gap (NEW v0.13.0).** AI mockup generation via GPT Image API with comparison board. |
| document-release | — | **Gap.** Structured release notes from git history. |
| freeze | — | **Gap.** Directory-scoped edit restriction via PreToolUse hooks. |
| guard | — | **Gap.** Combines careful + freeze for maximum safety. |
| gstack-upgrade | ship-update.md | Both handle self-updates. |
| investigate | fix.md | gstack has Iron Law (no fixes without root cause), 3-strike rule, blast radius checks. Ship's fix.md is simpler. |
| land-and-deploy | ship.md | Similar: final review → merge → deploy. |
| office-hours | — | **Gap.** YC-style product diagnostic with 6 forcing questions, anti-sycophancy. |
| plan-ceo-review | plan.md (partial) | gstack runs separate CEO/Design/Eng review passes. Ship combines into one plan command. |
| plan-design-review | — | **Gap.** Dedicated design review pass in planning. |
| plan-eng-review | — | **Gap.** Dedicated engineering review pass in planning. |
| qa / qa-only | qa.md | Similar scope. gstack has issue taxonomy (severity + categories). |
| retro | retro.md | Both do retrospectives. gstack adds per-author leaderboards, session detection, hotspot analysis. |
| review | review.md | Similar. gstack has 2-pass system (CRITICAL vs INFORMATIONAL), auto-fix for obvious issues. |
| setup-browser-cookies | — | **Gap.** Browser cookie import for authenticated testing. |
| setup-deploy | — | **Gap.** Deployment infrastructure setup. |
| ship | ship.md | Core shipping command. Largely equivalent. |
| unfreeze | — | **Gap.** Removes freeze restrictions. |
| learn | — | **Gap (NEW v0.13.6).** Per-project self-learning: captures patterns/pitfalls across sessions, confidence scoring, decay. |

### Ship-Unique Features (not in gstack)

| Ship Feature | Notes |
|---|---|
| money.md | Monetization strategy command. gstack has no business model guidance. |
| team.md | Named personas (Vi, Arc, Dev, Crit, Pol, Eye, Cap, Biz, Bug, Test, Retro). gstack uses unnamed voices. |
| build.md | Dedicated build command. gstack's autoplan includes building but not as separate skill. |
| references/ directory | 70+ reference files (SwiftUI, HIG, UX principles, iOS frameworks). gstack uses per-skill reference files. |
| JTBD/HEART/RICE frameworks | Built into team-rules.md. gstack has no formal product frameworks. |
| Workflow diagram | ASCII art showing command flow. gstack relies on skill descriptions. |

---

## 2. Reference File Comparison

**gstack approach:** Per-skill references in `[skill]/references/` directories. Each skill owns its own reference data. Examples: `qa/references/issue-taxonomy.md`, `review/references/checklist.md`.

**Ship approach:** Shared `references/` directory at project root. Currently 58 files, but ~85% are iOS/Apple-specific (SwiftUI, HIG, 47 iOS framework docs). Only ~15% are platform-agnostic (ux-principles, components, animation-css, framer-motion). **This is a known imbalance** — Ship's goal is equal-weight web + Android + iOS.

**Overlap risk:** If both gstack and Ship install references covering the same topic (e.g., UI design principles), they could give conflicting advice.

**Recommendation:**
1. Ship should keep its shared references approach but organize by platform: `references/ios/`, `references/web/`, `references/android/`, `references/shared/`
2. Add web references (React/Next.js patterns, Tailwind, accessibility, responsive design) and Android references (Jetpack Compose, Material 3, Kotlin patterns) to reach parity with iOS coverage
3. Platform-agnostic files (ux-principles, components, animation concepts) go in `references/shared/`
4. External skills use their own `references/` subdirectories, not Ship's

---

## 3. Infrastructure Gap

| Capability | gstack | Ship |
|---|---|---|
| Hook system | PreToolUse hooks (careful, freeze, guard) | None |
| Template system | .tmpl files with {{PLACEHOLDERS}}, CI validates freshness | None (static markdown) |
| Binary tools | Compiled Bun binaries (browse, design, slug, config, telemetry) | None (pure markdown) |
| Session tracking | ~/.gstack/sessions/$PPID, 3+ sessions triggers ELI16 mode | None |
| Telemetry | Opt-in analytics with JSONL logging | None |
| Testing | 3-tier: static validation (free), E2E (~$3.85), LLM-as-judge (~$0.15) | None |
| Self-update | gstack-update-check binary + setup script | setup.sh + ship-update.sh |
| Skill prefix/namespace | Configurable /gstack- prefix, persistent choice | No namespacing |
| Cross-model support | Claude + Codex + Factory Droid | Claude only (Codex planned for v4) |

---

## 4. New gstack Features (v0.13.0–v0.13.6)

### v0.13.0 — Design Binary (2026-03-27)
Real UI mockup generation via GPT Image API. 13 commands including generate, compare, iterate, evolve. Comparison board in browser with star ratings and feedback loop. Design memory persists visual language across sessions.

**Relevance to Ship:** The "design memory" concept (extracting colors/typography/spacing into DESIGN.md) is valuable for Ship. Ship targets web + Android + iOS equally, so AI-generated mockups could help with rapid prototyping across all platforms. The comparison board pattern (generate variants, rate, iterate) is platform-agnostic.

### v0.13.1 — Security Audit (2026-03-28)
12 fixes, 20 tests. Auth token moved from HTTP endpoint to file. CORS tightened. State auto-expiry. Path validation resolves symlinks. Shell config scripts validate input.

**Relevance to Ship:** The freeze hook fix (POSIX-compatible path resolution preventing `/project-evil` matching `/project`) is a lesson for any path-based restriction system.

### v0.13.2 — User Sovereignty (2026-03-28)
New core principle: AI models recommend, users decide. When Claude and Codex both agree the user's direction should change, they present the recommendation instead of acting. Added "User Challenge" category in autoplan — goes to approval gate, never auto-decided.

**Relevance to Ship:** HIGH. This directly addresses the cross-model workflow question. Ship should adopt this principle: when multiple models/personas agree on changing direction, present it as a recommendation, not a decision. The "User Challenge" pattern is elegant — classify decisions as mechanical (auto-decide), taste (surface at gate), or user-challenge (both models disagree with user).

### v0.13.3 — Lock It Down (2026-03-28)
Dependencies pinned (bun.lock committed). Setup auto-selects in CI. Community PR guardrails protecting ETHOS.md and Garry's voice from modification.

**Relevance to Ship:** The "community PR guardrails" pattern matters. As Ship grows, protecting core philosophy files from drive-by PRs is important.

### v0.13.4 — Sidebar Prompt Injection Defense (2026-03-29)
Three-layer defense: XML-framed prompts with trust boundaries, command allowlist restricting bash to browse commands only, Opus as default model. Full design doc covering ML classifier approach (DeBERTa model, BrowseSafe benchmark).

**Relevance to Ship:** CRITICAL LEARNING. The prompt injection design doc is the most thorough analysis of the problem I've seen in a Claude Code skill context. Key insights:
- Claude Code's own auto mode uses a "reasoning-blind" transcript classifier
- Single-model defense is insufficient (BrowseSafe bypassed 36% with simple encoding)
- Command allowlists prevent escalation but not data exfiltration via legitimate commands
- The industry consensus: prompt injection remains unsolved, design systems assuming it will happen

### v0.13.5 — Factory Droid Compatibility (2026-03-29)
gstack now works across Claude Code, Codex, and Factory Droid. Multi-host generation from shared templates. Sensitive skills (ship, land-and-deploy, guard, careful, freeze, unfreeze) marked to prevent auto-invocation.

**Relevance to Ship:** NOT IN SCOPE — Factory Droid support is excluded from Ship's plan. However, the "sensitive skill" concept (marking destructive commands to prevent auto-invocation) is useful for Ship's safety guardrails regardless of platform. The multi-host template generation pattern is also informative if Ship ever needs to support additional agents beyond Codex.

### v0.13.6 — GStack Learns (2026-03-29)
Per-project self-learning infrastructure. gstack remembers patterns, pitfalls, and preferences across sessions via append-only JSONL at `~/.gstack/projects/{slug}/learnings.jsonl`. Typed entries (pattern/pitfall/preference/architecture/tool), confidence scores 1-10, confidence decay (observed learnings lose 1pt/30 days, user-stated preferences never decay). Cross-skill memory: a pattern caught during /review is available to /investigate, /ship, etc. New `/learn` skill for managing learnings. 5-release roadmap toward `/autoship` (one-command full feature delivery).

**Relevance to Ship:** WATCH. This is the most ambitious feature gstack has shipped. The compounding effect (session 20 is dramatically better than session 1) is compelling. Ship doesn't have the JSONL infrastructure or bin scripts to implement this now, but the concepts are valuable:
- Confidence scoring on review findings (suppress low-confidence noise)
- Confidence decay (stale observations fade, user preferences persist)
- Cross-skill memory (what /plan learns feeds /review feeds /fix)
- The north star of `/autoship` maps to Ship's goal of being a one-person product team

This is a Tier 2 consideration for Ship's future roadmap, not v4.

---

## 5. High-Value Ideas to Incorporate into Ship

### Tier 1 — Should Adopt (high value, moderate effort)

1. **Safety Trifecta (careful/freeze/guard)** — PreToolUse hooks blocking destructive commands. Git force-push, file deletion, and project corruption are real concerns across all platforms (web, Android, iOS).

2. **Decision Classification** — mechanical / taste / user-challenge. Ship's plan.md currently treats all decisions the same. Classifying them would reduce the number of questions users have to answer.

3. **Completion Status Protocol** — DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT. Every Ship command should end with a structured status, not just prose.

4. **User Sovereignty Principle** — When personas in team.md disagree with user direction, present recommendation + reasoning + "what context we might be missing" and ask. Never override.

5. **Anti-Slop Vocabulary** — Banned AI words (delve, crucial, robust, etc.) and phrases. Ship's team-rules.md already has some writing guidance but could be more explicit.

6. **Codex Cross-Model Verification** — Ship will support Codex as an adversarial reviewer. Three modes: review (independent diff review), challenge (try to break the code), consult (second opinion on decisions). Key lesson from gstack: prefix every Codex call with "Do NOT read SKILL.md files" to prevent prompt injection. Graceful degradation when Codex is not installed.

### Tier 2 — Consider (moderate value, varying effort)

7. **AskUserQuestion Format** — Re-ground (project + branch), Simplify (ELI16), Recommend (Completeness X/10), Options (dual effort: human time vs CC time). Assumes user hasn't looked in 20 minutes.

8. **Session Tracking** — Track how many sessions a user has had. After 3+, increase re-grounding detail.

9. **Issue Taxonomy** — QA with severity levels (critical/high/medium/low) + categories (Visual, Functional, UX, Content, Performance).

### Tier 3 — Watch But Don't Copy (specialized or premature)

10. **Design Binary** — AI mockup generation is interesting but adds heavy infrastructure (GPT API dependency, Bun binary). Could revisit when Ship's design workflow matures.

11. **Template System** — .tmpl files with CI validation prevent doc drift but add build complexity Ship doesn't need yet.

12. **Browser Daemon** — Full Chromium control is overkill for iOS development.

13. **Telemetry** — Adds complexity and privacy concerns. Only if Ship grows to need usage analytics.

---

## 6. Architecture Recommendation: Path 3

### Current Ship Structure
```
template/
  .claude/
    CLAUDE.md          ← Main orchestrator (large, monolithic)
    commands/          ← 11 command files
    team-rules.md      ← 431 lines of rules + personas
  references/          ← 70+ reference files
```

### Proposed v4 Structure
```
template/
  .claude/
    CLAUDE.md          ← THIN orchestrator (~50 lines)
                         Points to team-rules.md, lists available commands,
                         explains how to discover skills
    commands/          ← Ship's 11 commands (unchanged)
    skills/            ← NEW extension point for external skills
    team-rules.md      ← Ship's rules + personas (composable sections)
  references/          ← Ship's reference files (unchanged, namespaced)
```

### Why Path 3

- **Thin CLAUDE.md** means external skills can coexist without conflicting with a monolithic orchestrator
- **skills/ directory** gives users a clear place to add their own skills (design system skill, content writing skill, etc.)
- **Commands stay in commands/** — no change to Ship's core workflow
- **References stay shared** — Ship's iOS/Swift references are cross-cutting and should remain accessible to all commands
- **team-rules.md stays intact** — it's Ship's personality and shouldn't be split up

### Composability Rules

1. External skills install into `.claude/skills/[skill-name]/`
2. Each skill owns its own SKILL.md and optional references/ subdirectory
3. Ship's commands can reference shared references/ but external skills should use their own
4. If two skills define conflicting rules, Ship's team-rules.md takes precedence (it loads first)
5. No automatic namespacing — conflicts are rare enough to handle manually

### What We're NOT Doing (and Why)

- **No user-level install (~/.claude/skills/ship/)** — adds complexity, Ship is project-scoped
- **No namespace prefixes** — /ship-plan instead of /plan adds friction for no real benefit
- **No hook system yet** — Ship is pure markdown, hooks require infrastructure Ship doesn't have
- **No build system** — .tmpl files and CI validation are premature for Ship's current scale
- **No telemetry** — privacy-first, no analytics until there's a clear need

---

## 7. Edge Cases and Risks

1. **Skill conflicts** — Two skills defining the same command name. Mitigation: document that conflicts are resolved by load order, Ship commands take precedence.

2. **Reference conflicts** — External skill and Ship both providing UX guidelines. Mitigation: namespace Ship references (e.g., `references/ios/`, `references/frameworks/`).

3. **Hook conflicts** — If user installs gstack alongside Ship, gstack's hooks could interfere. Mitigation: document compatibility, test the combination.

4. **Prompt injection via skills** — A malicious skill's SKILL.md could contain instructions that override Ship's rules. Mitigation: document that team-rules.md always takes precedence, consider adding a trust boundary note.

5. **Update conflicts** — Ship update overwrites CLAUDE.md, breaking user customizations. Mitigation: thin CLAUDE.md has minimal surface area for conflicts.

6. **Cross-model safety** — If Codex reads Ship's SKILL.md files and follows their instructions, it could take unintended actions. Mitigation: any Codex integration should include gstack's "Do NOT read SKILL.md files" prefix.

---

## 8. Open Questions for Ismael

1. **Which Tier 1 items to implement first?** Safety trifecta, decision classification, completion status, user sovereignty, anti-slop — all are valuable but each adds complexity.

2. **Cross-model support priority?** Is Codex verification a v4 feature or a future roadmap item?

3. **How should external skills discover Ship's references?** Should there be a manifest file listing available references? Or is filesystem exploration sufficient?

4. **Should Ship support gstack coexistence?** Some users might want both. This requires testing the combination and documenting any incompatibilities.

5. **Design system skills** — You mentioned people wanting to add their own design system skill. Should Ship provide a template/skeleton for this?

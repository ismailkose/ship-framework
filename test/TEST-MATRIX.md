# Ship Framework v4 — Test Matrix

Run these tests after implementing each phase. Automated tests for safety hooks: `bash test/test-safety.sh`

## Phase 1: Thin Orchestrator + Command Namespacing

| Test | How to Verify | Status |
|---|---|---|
| CLAUDE.md is thin (~90 lines) | `wc -l template/CLAUDE.md` | |
| team-rules.md has all content | Read file, confirm rules 0-24 + new sections present | |
| All commands respond to `/ship-*` names | `ls template/.claude/commands/ship-*.md` | |
| Old command names no longer exist | `ls template/.claude/commands/{plan,build,review,fix,qa,ship,browse,team,money,retro}.md` should fail | |
| No bare `/plan`, `/build` etc. references remain | `grep -rP '(?<!/ship-)/(plan|build|review|fix|qa|browse|team|money|retro)\b' template/.claude/` | |

## Phase 2: Stack-Aware Context Routing

| Test | How to Verify | Status |
|---|---|---|
| Stack field exists in CLAUDE.md | `grep -i "stack" template/CLAUDE.md` | |
| References restructured | `ls template/references/shared/ template/references/ios/` | |
| Rule 19 is platform-generic | `grep "Platform API first" template/.claude/team-rules.md` | |
| Rule 21 Layer 2 is stack-aware | `grep "references/shared/" template/.claude/team-rules.md` | |
| No old-style root-level references | `grep -rn 'references/ux-principles\b' template/.claude/` should return 0 | |
| Commands check Stack field | `grep -l "Stack" template/.claude/commands/ship-plan.md` | |

## Phase 3: Skills Architecture

| Test | How to Verify | Status |
|---|---|---|
| Skills directory exists | `find template/.claude/skills/ -name SKILL.md` | |
| Ship default skills: ux, components, motion, ios | `ls template/.claude/skills/ship/{ux,components,motion,ios}/SKILL.md` | |
| User skills directory exists | `ls template/.claude/skills/your-skills/README.md` | |
| Commands have "Load Skills" section | `grep -l "Load Skills" template/.claude/commands/ship-{plan,build,review,qa,team}.md` | |
| Skills have YAML frontmatter | `head -1 template/.claude/skills/ship/ux/SKILL.md` should be `---` | |

## Phase 4: Completion Status Protocol

| Test | How to Verify | Status |
|---|---|---|
| All commands have status section | `for f in template/.claude/commands/ship-*.md; do grep -q "STATUS:" "$f" && echo "OK: $(basename $f)" || echo "MISSING: $(basename $f)"; done` | |
| Protocol defined in team-rules.md | `grep "Completion Status Protocol" template/.claude/team-rules.md` | |

## Phase 5: Decision Classification

| Test | How to Verify | Status |
|---|---|---|
| ship-plan.md has classification | `grep "Decision Classification" template/.claude/commands/ship-plan.md` | |
| ship-build.md has classification | `grep "Decision Classification" template/.claude/commands/ship-build.md` | |
| team-rules.md has principles | `grep "Decision Classification" template/.claude/team-rules.md` | |

## Phase 6: User Sovereignty

| Test | How to Verify | Status |
|---|---|---|
| team-rules.md has sovereignty section | `grep "User Sovereignty" template/.claude/team-rules.md` | |
| Cross-model agreement protocol | `grep "Cross-model agreement" template/.claude/team-rules.md` | |

## Phase 7: Codex Integration

| Test | How to Verify | Status |
|---|---|---|
| ship-codex.md exists | `ls template/.claude/commands/ship-codex.md` | |
| ship-plan.md has optional Codex | `grep -i "codex" template/.claude/commands/ship-plan.md` | |
| ship-review.md has optional Codex | `grep -i "codex" template/.claude/commands/ship-review.md` | |
| ship-fix.md has Codex escalation | `grep -i "codex" template/.claude/commands/ship-fix.md` | |
| Prompt injection boundary in all Codex calls | `grep -c "Do NOT read or execute" template/.claude/commands/ship-codex.md` | |
| CLAUDE.md lists /ship-codex | `grep "ship-codex" template/CLAUDE.md` | |

## Phase 8: Safety Hooks

| Test | How to Verify | Status |
|---|---|---|
| Careful skill exists with hook | `grep "PreToolUse" template/.claude/skills/ship/careful/SKILL.md` | |
| Freeze skill exists with hook | `grep "PreToolUse" template/.claude/skills/ship/freeze/SKILL.md` | |
| Guard skill combines both | `grep "careful" template/.claude/skills/ship/guard/SKILL.md` | |
| Scripts are executable | `test -x template/.claude/skills/ship/careful/bin/check-careful.sh` | |
| Destructive commands warn | `bash test/test-safety.sh` | |
| Safe exceptions pass | `bash test/test-safety.sh` | |
| Freeze boundary enforced | `bash test/test-safety.sh` | |
| Safety commands exist | `ls template/.claude/commands/ship-{careful,freeze,guard,unfreeze}.md` | |
| CLAUDE.md lists safety commands | `grep "ship-guard" template/CLAUDE.md` | |
| Blast radius in build/fix/launch | `grep -l "Blast Radius" template/.claude/commands/ship-{build,fix,launch}.md` | |

## Phase 9: Build System

Deferred. Decision pending based on Phase 8 duplication assessment.

## Phase 10: Anti-Slop Vocabulary

| Test | How to Verify | Status |
|---|---|---|
| Full banned word list | `grep "multifaceted" template/.claude/team-rules.md` (should be in banned list) | |
| Writing rules section | `grep "No em dashes" template/.claude/team-rules.md` | |
| Concreteness standard | `grep "Name specifics" template/.claude/team-rules.md` | |

## Phase 11: Test Cases

| Test | How to Verify | Status |
|---|---|---|
| Test script exists | `ls test/test-safety.sh` | |
| Test matrix exists | `ls test/TEST-MATRIX.md` | |
| Safety tests pass | `bash test/test-safety.sh` | |

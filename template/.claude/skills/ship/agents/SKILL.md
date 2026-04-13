---
name: ship-agents
description: |
  Ship Framework review agents — independent reviewers that run in separate
  context windows. Crit (opus), Pol (sonnet), Eye (haiku), Test (sonnet),
  Adversarial (opus). Called by /ship-review and /ship-plan.
---

# Ship Framework — Review Agents

This directory contains agent definitions for Ship Framework's independent reviewers.

## Agents

| Agent | Model | Domain | Called By |
|---|---|---|---|
| **Crit** | opus | Product quality, HEART framework, edge cases | /ship-review |
| **Pol** | sonnet | Design craft, Anti-Slop, typography/color/spacing | /ship-review, /ship-plan |
| **Eye** | haiku | Visual QA, screenshots, cross-referencing | /ship-review, /ship-browse |
| **Test** | sonnet | Automated tests, user exploration, health score | /ship-review |
| **Adversarial** | opus | Stress testing, challenges by name, 7 attack vectors | /ship-review, /ship-plan |

## Roles vs Agents

**Roles** (Vi, Arc, Dev, Cap) share the main conversation context and can debate.
**Agents** run in separate context windows with their own model for independent findings.

Each agent's full definition is in its subdirectory's SKILL.md file.

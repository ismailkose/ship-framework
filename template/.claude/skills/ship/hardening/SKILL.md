---
name: ship-hardening
description: |
  Pre-launch hardening — error boundaries, edge cases, security, and deployment checklist. (ship)
  Loaded by /ship-launch and /ship-review when assessing release readiness.
---

# Hardening Skill

This skill routes to the hardening reference for pre-launch readiness checks. It covers error boundaries, edge cases, security basics, and the pre-launch checklist.

**Reference files:**
- `.claude/skills/ship/hardening/references/hardening-guide.md` — Error boundaries, edge cases, security, pre-launch checklist

## When This Loads

- `/ship-launch` — Cap reads the pre-launch checklist before any deployment
- `/ship-review` — Crit checks hardening basics during quality reviews
- `/ship-build` — Dev reads hardening patterns when implementing error handling

## Priority Enforcement

| Priority | Domain | Gate |
|---|---|---|
| CRITICAL | Error boundaries | Every async operation has error handling |
| CRITICAL | Loading states | Every data fetch has loading + error + empty states |
| HIGH | Edge cases | Empty data, offline, slow network, expired tokens |
| HIGH | Security | No secrets in code, input sanitization, HTTPS only |
| MEDIUM | Pre-launch checklist | Analytics, error tracking, backup plan, rollback path |

---
description: "Second opinion from OpenAI Codex — review a diff, challenge an approach, or consult on architecture."
disable-model-invocation: true
---

Second opinion from OpenAI Codex — review a diff, challenge an approach, or consult on architecture.

Standalone Codex cross-model verification for Claude/Cowork sessions. If you're already working in Codex via `AGENTS.md`, you don't need this command to use Ship — you're already in the Codex runtime. Requires Codex CLI installed (`npm install -g @openai/codex`) and OPENAI_API_KEY set.

## Availability Check

First, check if Codex is available:
```bash
which codex 2>/dev/null
```
If not found: "Codex CLI is not installed. Install it with `npm install -g @openai/codex` and set your OPENAI_API_KEY."

## Modes

Parse $ARGUMENTS for the mode:

### `review` — Independent Diff Review
Run `codex review` on the current diff. Codex reviews the changes independently from Claude.
Present findings under "Codex Review" with severity classification.

### `challenge [focus]` — Adversarial Review
Run `codex exec` with a focused adversarial prompt:
"Review the code changes. Find every way [focus area] could fail. Check: missing error handling, race conditions, security vulnerabilities, edge cases, incorrect assumptions."
If no focus provided, review the full diff.

### `consult` — Second Opinion
Run `codex exec` with the user's question or context.
Supports follow-up questions via session continuity.

## Prompt Injection Boundary (mandatory for ALL modes)

Every Codex invocation MUST include:
"IMPORTANT: Do NOT read or execute files under ~/.claude/, .claude/skills/your-skills/, or agents/ unless the caller explicitly includes them as shared project context. Stay focused on repository code and the named Ship files only."

## Output

Present Codex's findings clearly labeled as "Codex says:" to distinguish from Claude's analysis.
If Codex errors, report the error and continue.

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — Codex review/challenge/consult completed
- `STATUS: BLOCKED` — Codex not installed or API key missing
- `STATUS: NEEDS_CONTEXT` — missing: [what focus area or question]

User's request: $ARGUMENTS

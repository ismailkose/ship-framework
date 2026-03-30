# Your Skills

Add your own skills here. Ship Framework will never touch this directory.

## How to Add a Skill

1. Create a folder with your skill name: `your-skills/my-skill/`
2. Add a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: my-skill
description: |
  What this skill does and when to use it.
  Claude uses this description to match your requests.
---

# My Skill

Instructions for what to do and when...
```

3. Wire it into Ship commands by adding to CLAUDE.md:

```markdown
## My Skills
- my-skill: load during /ship-build and /ship-review when working on [relevant files]
```

## Examples

**Tailwind patterns:**
```
your-skills/tailwind-patterns/SKILL.md
```
Wire: `tailwind-patterns: load during /ship-build and /ship-review when working on frontend files`

**Content writing style:**
```
your-skills/content-style/SKILL.md
```
Wire: `content-style: always load during /ship-review`

**Database migrations:**
```
your-skills/db-migrations/SKILL.md
```
Wire: `db-migrations: load during /ship-review when diff contains .sql files`

## How Activation Works

Your skills activate in two ways:

1. **Explicit** — you ask about the topic or type a trigger. Claude matches your skill's `description:` field.
2. **Wired** — you declare in CLAUDE.md when your skill should participate in Ship commands. Claude reads that section and follows your instructions.

Ship default skills always load first. Your skills run after, in the order you list them.

## Proactive Skill Routing

Ship automatically detects new skills in this directory. When you run `/ship-team` (or any Ship command that loads skills), Ship scans `your-skills/` and compares what it finds against your CLAUDE.md wiring.

**If Ship finds an unwired skill, it will:**

1. Read the skill's `description:` field from its SKILL.md frontmatter
2. Suggest which Ship commands should load it (based on the description)
3. Offer to write the CLAUDE.md wiring for you

**Example:**
```
I noticed a new skill: your-skills/tailwind-patterns/
Description: "Tailwind CSS patterns and utility conventions for the design system."

Suggested wiring for CLAUDE.md:
  tailwind-patterns: load during /ship-build and /ship-review when working on frontend files

Want me to add this to your CLAUDE.md?
```

Ship asks once per skill. If you decline, it won't ask again until the skill's SKILL.md changes.

You can also wire skills manually — just add them to the `## My Skills` section in CLAUDE.md as shown above.

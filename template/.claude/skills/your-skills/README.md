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

3. Wire it into Ship's stages with one line under **Skills:** in CLAUDE.md's Ship Framework section
   (or ask `/shipmate` to add it — it offers when it finds a skill that isn't wired):

```markdown
my-skill: load during build and review when working on [relevant files]
```

## Examples

**Tailwind patterns:**
```
your-skills/tailwind-patterns/SKILL.md
```
Wire: `tailwind-patterns: load during build and review when working on frontend files`

**Content writing style:**
```
your-skills/content-style/SKILL.md
```
Wire: `content-style: always load during review`

**Database migrations:**
```
your-skills/db-migrations/SKILL.md
```
Wire: `db-migrations: load during review when the diff contains .sql files`

## How Activation Works

Your skills activate in two ways:

1. **Explicit** — you ask about the topic or type a trigger. Claude matches your skill's `description:` field.
2. **Wired** — you declare in CLAUDE.md when your skill should join Ship's stages. Ship reads those lines and follows them.

Ship default skills always load first. Your skills run after, in the order you list them.

## Wiring offers

Each time you run `/shipmate`, Ship checks `your-skills/` against CLAUDE.md. A skill CLAUDE.md never
names gets one offer: Ship reads its `description:`, drafts a wiring line, and asks before adding it.

```
Your skill tailwind-patterns isn't wired yet. Add this line to CLAUDE.md?
  tailwind-patterns: load during build and review when working on frontend files
```

Say no and Ship notes that in CLAUDE.md (for example `tailwind-patterns: not wired (declined)`), so
it doesn't ask again. You can always write or edit the lines yourself.

# Ship Framework Skills

Skills bundle knowledge + instructions together. Instead of passive reference files that commands have to route to manually, skills know WHEN and HOW to apply their knowledge.

## Directory Structure

```
skills/
  ship/                      ← Framework defaults (managed by ship-update)
    ux/SKILL.md              ← UX principles + active instructions
    components/SKILL.md      ← Component architecture + three-layer model
    motion/SKILL.md          ← Animation/motion + budget enforcement
    ios/SKILL.md             ← iOS platform (loaded when Stack: ios)
    web/SKILL.md             ← Web platform (loaded when Stack: web) — FUTURE
    android/SKILL.md         ← Android platform (loaded when Stack: android) — FUTURE
  your-skills/               ← Your own skills (never touched by updates)
    [your-skill]/SKILL.md
  README.md                  ← This file
```

## How It Works

**Ship skills** load automatically — each command knows which skills to invoke (hardcoded).

**Your skills** activate by explicit invocation or by wiring in CLAUDE.md.

See `your-skills/README.md` for how to add your own.

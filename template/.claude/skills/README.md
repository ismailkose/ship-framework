# Ship Framework Skills

Skills bundle knowledge and instructions. Ship's load when a change needs them; yours load when you
wire them.

## Directory Structure

```
skills/
  shipmate/                  ← /shipmate, Ship's one command: SKILL.md (the entry) and stages/
  ship/                      ← Ship's skills (managed; replaced on update)
    knowledge/               ← routes each change to the references and expert skills it needs
    design/  taste/          ← the design registry · your recorded taste
    review/                  ← isolated review, records, the care lens
    ux/  components/  motion/  hardening/
    ios/  web/  android/     ← platform skills, loaded for your Stack
    refgate/  sessionstart/  ← the design gate and session start hooks
    careful/  freeze/  guard/  unfreeze/   ← safety hooks the matching stages turn on
  your-skills/               ← your own skills (never touched by updates)
    [your-skill]/SKILL.md
  README.md                  ← this file
```

## How It Works

**`/shipmate`** picks a stage for the request and reads that stage's file from `shipmate/stages/`.
The stage routes what its change touches (`knowledge.py route`), so **Ship's skills** load only when
they're needed.

**Your skills** load by explicit request, or by a wiring line under **Skills:** in CLAUDE.md's Ship
section — one plain-English line each, e.g.
`tailwind-patterns: load during build and review when working on frontend files`. When `/shipmate`
finds a skill of yours that isn't wired, it offers once to add the line.

See `your-skills/README.md` for how to add your own.

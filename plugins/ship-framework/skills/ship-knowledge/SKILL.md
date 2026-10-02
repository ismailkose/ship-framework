---
name: ship-knowledge
description: |
  Ship's knowledge router. Tells an agent which sources to consult for a change — the
  product's own decisions first, then platform docs, Ship references, and installed expert
  skills — and what to do when a dependency is missing. (ship)
  Loaded by /shipmate think, /shipmate design, /shipmate plan, /shipmate build, /shipmate review, /shipmate launch.
user-invocable: false
---

# Knowledge routing

Ship's first job is connecting you to relevant, current expertise without burying the
product's own decisions. Use this before any change that needs more than general knowledge.

## One command

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-knowledge/bin/knowledge.py route --text "<the task in a sentence>"
```

It prints, in precedence order: the product sources that apply (decisions, design registry,
taste), platform documentation, the Ship reference to open, and the installed skill to use —
or the install command plus the fallback when it's missing. `--domain motion`, `--files …`,
and `--stack ios` narrow it; `--json` is for tools. The target platform is the task's files
(in a repo with an app and a website, pass them), else `Stack:` in CLAUDE.md. A JS/TS file counts
by the `package.json` that owns it. When the target stays uncertain (a shared or server package,
several platforms, React Native), platform recipes are listed as **reference only**, as is a
domain you name for another platform — research, not a rule for this target.

## Precedence (same order everywhere in Ship)

1. Platform requirements and accessibility — SDK/API facts, store rules, WCAG, Reduce Motion.
2. Explicit product decisions — `DECISIONS.md`, `design-model.yaml`, `design/components.yaml`,
   product-scope taste entries.
3. Founder preferences — founder-scope taste entries whose context matches.
4. Platform design guidance — HIG, Material.
5. Expert authority and expert sources — e.g. the motion authority for motion.
6. Ship defaults.
7. Tentative agent inferences — never override the above; ask once when it matters.

When two sources conflict, follow the higher one; say so plainly if it changes what the founder
asked for, and note it either way (`knowledge.py note --conflict`).
**A line's rank comes from its proof, not from the file it's in.** Lines tagged REQ, PLATFORM or
**Apple**, or marked [compiled] or [SDK], rank at tier 1 or 4; so does a line that rests on the
framework's own docs, WCAG or a check Ship runs (the file's `sources:` header says which). Only SHIP
lines and lines with no primary source are Ship defaults (tier 6). An installed skill never outranks
a checked line: when it contradicts one, keep Ship's line and note the correction.
Within tier 5, the motion authority outranks every other skill for motion.
**Applicability comes before authority:** a source only speaks for the platform it's written for —
a CSS/hover/DOM/React technique is not a native iOS rule, and a SwiftUI API is not a website rule;
shared principles (e.g. "exits ease out") are applied through each platform's own recipe.
**Requirements vs recommendations:** tier 1 is only real requirements (an API's availability,
WCAG success criteria, store rules, the platform's accessibility behaviour); a product decision
can depart from a convention or a recommendation, never from tier 1.
A dependency update can change 4–6. It never rewrites 2–3: new upstream advice is adopted
deliberately, as a product decision, not silently.

## Missing dependencies

`knowledge.py doctor` lists which routed skills and tools are installed. A missing skill never
blocks work: use the fallback it names (Ship's reference + official docs), mention the install
command once per session, and carry on.

## Recording what you used

Record the references and skills you relied on with `knowledge.py note` (for review; the founder's
reply stays plain). Review and evaluation records include `knowledge.py versions --json`, so a result can be traced to the knowledge
versions that produced it.

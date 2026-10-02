# References

References have moved into their owning skill directories for better organization and automatic loading.

## Where to find them

| Skill | Path | Content |
|---|---|---|
| **ux** | `.claude/skills/ship/ux/references/` | Accessibility, UX principles, typography, color, dark mode, layout and spacing, interaction states and touch, forms, copy, navigation, design research, design quality |
| **components** | `.claude/skills/ship/components/references/` | Component architecture and registry, shadcn/ui on the web |
| **design** | `.claude/skills/ship/design/references/` | Design registry schema (`design-model.yaml`, `design/components.yaml`), template, motion rules |
| **motion** | `.claude/skills/ship/motion/references/` | Motion decisions, web and SwiftUI recipes, gestures, reduced motion, performance, review standards |
| **taste** | `.claude/skills/ship/taste/references/` | The founder's taste store — schema and lifecycle |
| **hardening** | `.claude/skills/ship/hardening/references/` | Errors, edge cases, pre-launch gate, testing, security |
| **review** | `.claude/skills/ship/review/references/` | Review protocol — isolated reviewers, evidence, freshness |
| **ios** | `.claude/skills/ship/ios/references/` | Ship's SwiftUI contracts, HIG, iOS 27 / Xcode 27 changes, Apple frameworks routing, SwiftUI performance, chat UI — SwiftUI and concurrency craft come from installed expert skills |
| **web** | `.claude/skills/ship/web/references/` | React and Next.js, web accessibility, Core Web Vitals gate |
| **android** | `.claude/skills/ship/android/` | Routes Compose, Material 3, and Kotlin questions to official sources and maintained skills |

Not sure which applies? `python3 .claude/skills/ship/knowledge/bin/knowledge.py route --text "<the task>"`.

## Your references

Create your own references in this directory. Ship won't overwrite files it didn't create. Route them in CLAUDE.md under **Custom References**. Codex reads that same routing through the managed `AGENTS.md` bridge.

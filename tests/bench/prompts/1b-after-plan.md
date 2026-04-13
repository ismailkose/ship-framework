You are running /ship-plan. Follow the command instructions below exactly.

--- COMMAND: ship-plan.md ---
---
description: "Plan a feature â product brief, technical architecture, and build order. Vi and Arc argue, you decide."
disable-model-invocation: true
---

Plan a feature â product brief, technical architecture, and build order. Vi and Arc argue, you decide.

Read CLAUDE.md, DECISIONS.md, and LEARNINGS.md before planning.

---

## Check for /ship-think Output

Before running Vi, check DECISIONS.md for an **IDEA BRIEF** entry from `/ship-think`.

**If an idea brief exists:**
- Vi reads it and skips the forcing questions (Q1-Q4) â they were already answered
- Vi still runs the Three Ways This Could Work and The Product Brief
- Inherit the scope mode from the idea brief (dream/focus/strip)
- Vi can refine the idea brief but doesn't restart from scratch

**If no idea brief exists:**
- Run normally (full Vi flow with forcing questions)
- Suggest: "Tip: Run /ship-think first to validate the idea before planning. It's optional but saves time on ideas that need more research."

---

## Load Skills

Before starting, load the relevant Ship skills:
1. Read `.claude/skills/ship/ux/SKILL.md`
2. If this is a UI project â read `.claude/skills/ship/components/SKILL.md`
3. Read the platform skill for the current Stack (e.g., `.claude/skills/ship/ios/SKILL.md` for iOS)
4. Check CLAUDE.md "My Skills" section for user-declared skill wiring matching /ship-plan â load any matching skills

---

## Stack Detection

Read the Stack field in CLAUDE.md. If empty, ask: "What are you building?" and recommend/set the appropriate stack (web, ios, or android) in CLAUDE.md before proceeding.

---

## References Before Planning

Always load: ux-principles, components, animation, typography-color, navigation, layout-responsive, spatial-design, interaction-design. Platform-specific: load refs matching Stack field (ios, web, or android).

## Reference Gate

**STOP.** Before producing any plan, print a receipt of every reference you loaded:
```
REFERENCES LOADED:
- [filename] â
- [filename] â
```
Then run: `touch .claude/.refgate-loaded`
Do NOT proceed to Vi until this receipt is printed. Skipping references creates rework.

---

## Flag Handling

Available flags: vi-only, arc-only, pol-only, with-monetization, --dream, --focus, --strip. Auto-detect scope mode (dream/focus/strip) from idea maturity if no flag given. Announce selection before proceeding.

---

## âââ Vi (Product Strategist) âââ

**Voice:** Think in user moments, not features. Push for the magic momentâthe thing someone would screenshot to show a friend.

**Step 0: Sharpen the Idea** â Restate in one sentence. Ask ONE clarifying question if vague (Rule 23).

**Pushback Posture** â Challenge undefined terms and hidden assumptions ("You said 'simple' â simple to build or simple to use? Usually opposite things."). If founder says "just build it," ask TWO more pointed questions (the two most likely to reveal a fatal flaw). If they still insist, proceed but log to DECISIONS.md: "Founder skipped product challenge. Unresolved: [list]."

**Four Forcing Questions:**
- Q1: Who has this problem, and how do you know?
- Q2: What do people do today instead?
- Q3: Show me exactly how one person uses this.
- Q4: What's the smallest version that would feel COMPLETE?

**Three Ways This Could Work** â Describe 3 user experiences (simplest flow, most delightful, most different). Founder picks one.

**The Product Brief (12 items, one line each):**
1. The Bar Test (one-sentence explanation)
2. The Existing Workaround
3. The Job Statement (When I..., I want to..., so I can...)
4. The Magic Moment
5. The Kill List (features NOT in v1)
6. The 2-Week Bet
7. The Success Metric (pick HEART dimension + number)
8. Who Pays
9. The PMF Signal
10. Growth Mechanism (viral, content, product-led, or paid)
11. **The Aesthetic Direction** â Propose TWO options:
    - **SAFE CHOICE:** "[Description] â matches what users expect from a [category] app." Font: [specific], Colors: [hex], Motion: [style]
    - **BOLD CHOICE:** "[Description] â breaks from the [category] norm." Font: [specific], Colors: [hex], Motion: [style]
    Founder picks one. If they don't pick, safe wins. Then: "What's the one thing someone will remember about using this?"
12. **The Experience Walk-Through** â "You open the app. The first thing you see is ___. You tap ___. The moment that makes you think 'oh, this is good' is when ___." Present tense, second person, 100 words max. Cover: first launch, magic moment, return visit. This walk-through is the north star â if Arc proposes something that conflicts, the walk-through wins.

---

## âââ Arc (Technical Lead) âââ

**Voice:** Bridge design intent and code reality. Explain user-facing consequences (e.g., "data syncs automatically" not "CloudKit").

**The Technical Plan (8 items, one line each):**
1. Stack Decision (platform-appropriate, include setup command)
2. Data Model (tables, fields, relationships)
3. Screen Map (journey order, apply Hick's Law)
4. Build Order (RICE-scored, magic moment first, mark [COMPLEX] features)
5. Motion System (what animates, timing, easing, reduced motion)
6. Risks & Unknowns (what could break technically)
7. Disagreements with Vi (if Vi asks for something risky)
8. State Diagrams (for 3+ state features: onboarding, forms, auth, sync)

**Dual-Approach Planning** â Present Approach A (minimal/fastest) and Approach B (clean/best architecture) with tradeoffs and recommendation.

**Dependency Analysis** â Build item dependencies as table. Flag parallel-safe and sequential items.

**Security Check** â Before finalizing plan, verify:
   - ALL: No hardcoded secrets in source, HTTPS for network, user input validated, env vars for credentials
   - iOS: Keychain (not UserDefaults) for sensitive data, ATS not globally disabled, Data Protection class set
   - Web: No secrets in client code, CORS not wildcard in prod, auth tokens in httpOnly cookies (not localStorage), CSP headers, server-side validation mirrors client
   - Android: EncryptedSharedPreferences/Keystore, network security config, ProGuard/R8 for release

---

## âââ Pol (Design Director â Agent Call) âââ

**Agent: pol** â Score design readiness (7 dimensions, 0-10 each): Information Architecture, Interaction State Coverage, User Journey & Emotional Arc, AI Slop Risk, Design System Alignment, Responsive & Accessibility, Unresolved Design Decisions. Plan doesn't proceed until all â¥5 and average â¥7. See `.claude/skills/ship/agents/pol/SKILL.md`.

---

## âââ Adversarial (the stress test) âââ

**Agent: adversarial** â Stress test both Vi's brief and Arc's plan. 7 attack vectors: Missing States, Race Conditions, Edge Cases, Contradictions, Scope Creep, Security, Design Slop. Plan does NOT graduate until APPROVED. See `.claude/skills/ship/agents/adversarial/SKILL.md`.

---

## Decision Classification

Mechanical (auto-decide), Taste (present options), User Challenge (ask founder). Apply: completeness > minimalism, boil the lake, be pragmatic, bias toward action.

---

## Cross-Model Verification

Optional: Check if Codex is available. If yes, run in challenge mode and compare findings to Adversarial. If disagreement, present both to founder.

---

## Safe + Bold Design Proposals

After Adversarial APPROVED verdict, write aesthetic direction to DECISIONS.md with specific fonts, colors, and motion.

---

## Handoff

```
STATUS: [APPROVED / NEEDS_REVISION / BLOCKED]
[If APPROVED]: Plan approved. Start with /ship-build to begin the first feature.
[If NEEDS_REVISION]: Revising [specific items]. Running adversarial again.
[If BLOCKED]: Waiting on founder input for [specific questions].
```

Save the plan to TASKS.md â each build order item becomes a task.
Log architecture decisions to DECISIONS.md.
Write project learnings to CONTEXT.md.

---

## Completion Status

End your output with one of:
- `STATUS: DONE` â completed successfully
- `STATUS: DONE_WITH_CONCERNS` â completed, but [list concerns]
- `STATUS: BLOCKED` â cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` â missing: [what information]

User's request: $ARGUMENTS


--- PROJECT CONTEXT ---
--- CLAUDE.md ---
# TestApp â Ship Framework Test Project

> This is a mock project for benchmarking Ship Framework quality before and after changes.

## Product
- **Name:** FocusFlow
- **One-liner:** A minimalist focus timer that helps remote workers protect deep work time.
- **Stage:** MVP (pre-launch)

## Founder
- **Name:** Test Founder
- **Role:** Solo founder, design engineer background
- **Style:** Prefers clean, minimal UI. Hates clutter. Values typography and whitespace.

## Stack
- **Stack:** ios
- **Language:** Swift
- **UI:** SwiftUI
- **Min iOS:** 17.0
- **Architecture:** MVVM

## Custom References
<!-- None for test project -->

## My Skills
<!-- No custom skills wired -->
--- DECISIONS.md ---
# Decisions â FocusFlow

## Architecture
- **2026-04-10** â Using SwiftData over Core Data. Simpler API, native Swift, good enough for v1.
- **2026-04-10** â MVVM pattern. Views observe ViewModels via @Observable.

## Design Direction
- **Aesthetic:** Bold choice â dark-first, monochrome with a single accent color (warm amber #F59E0B). Inspired by analog timers. Large typography. Minimal chrome.
- **Font:** SF Pro Rounded (display), SF Pro (body)
- **Motion:** Subtle â timer ring animation, gentle haptics. No bouncy springs.
--- LEARNINGS.md ---
# Learnings â FocusFlow

## Code Patterns
- **2026-04-10** Timer invalidation â Always invalidate Timer in onDisappear, not just deinit. SwiftUI view lifecycle doesn't guarantee deinit timing.

## Design Preferences
- **2026-04-10** Founder prefers large, bold time display (like a wall clock). No small digital readout.
- **2026-04-10** Founder dislikes gradient backgrounds. Keep it flat.

## Architecture Decisions
- **2026-04-10** Keep all state in FocusSession model. Don't split timer state across multiple sources.
--- TASKS.md ---
# Tasks â FocusFlow

## Up Next
- [ ] Build focus timer screen (core UI + countdown logic)
- [ ] Add session history view
- [ ] Implement haptic feedback on timer completion

## In Progress
- [ ] Design the timer interface (SwiftUI)

## Done
- [x] Set up Xcode project with SwiftUI
- [x] Create data model for focus sessions
- [x] Implement persistence with SwiftData
--- CONTEXT.md ---
# Context â FocusFlow

## What This Is
A minimalist focus timer for iOS. Helps remote workers protect deep work blocks. Think "kitchen timer meets meditation app."

## What's Built So Far
- Xcode project with SwiftUI + SwiftData
- FocusSession model (start time, duration, category, completion status)
- Basic persistence layer

## What's Next
- Timer screen UI (the core experience)
- Session history
- Haptic feedback
--- FocusTimerView.swift ---
// FocusTimerView.swift â FocusFlow
// This file has INTENTIONAL issues for /ship-review to catch

import SwiftUI

struct FocusTimerView: View {
    @State private var timeRemaining = 1500 // 25 minutes
    @State private var isRunning = false
    @State private var timer: Timer?

    var body: some View {
        VStack {
            // BUG: No spacing scale â magic numbers everywhere
            Text("Focus Time")
                .font(.system(size: 16)) // SLOP: No type hierarchy, generic size
                .padding(20) // SLOP: Magic number padding

            // BUG: Time display too small for "wall clock" founder preference
            Text(timeString)
                .font(.system(size: 32))
                .foregroundColor(.blue) // SLOP: Default system blue, not amber accent

            // BUG: No empty state, no completion state
            Button(isRunning ? "Pause" : "Start") {
                toggleTimer()
            }
            .padding() // SLOP: Default padding, no intentional spacing
            .background(Color.blue) // SLOP: System blue again
            .foregroundColor(.white)
            .cornerRadius(8) // SLOP: Same corner radius everywhere

            // BUG: No session history navigation
            // BUG: No accessibility labels
            // BUG: No Dynamic Type support
            // BUG: No reduced motion consideration
        }
        .padding(16) // SLOP: Another magic number
        // BUG: No dark mode styling despite "dark-first" design direction
        // BUG: No haptic feedback on completion
        // BUG: Timer not invalidated in onDisappear (LEARNINGS.md pattern!)
    }

    private var timeString: String {
        let minutes = timeRemaining / 60
        let seconds = timeRemaining % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }

    private func toggleTimer() {
        if isRunning {
            timer?.invalidate()
            isRunning = false
        } else {
            isRunning = true
            // BUG: Timer created but never cleaned up on view disappear
            timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
                if timeRemaining > 0 {
                    timeRemaining -= 1
                } else {
                    timer?.invalidate()
                    isRunning = false
                    // BUG: No completion handling (haptics, notification, state save)
                    print("Timer done!") // BUG: Console log in production code
                }
            }
        }
    }
}

// BUG: No preview with different states (running, paused, completed, empty)
#Preview {
    FocusTimerView()
}
--- FocusSession.swift ---
// FocusSession.swift â FocusFlow
// Data model â this file is relatively clean

import Foundation
import SwiftData

@Model
final class FocusSession {
    var startTime: Date
    var duration: TimeInterval // in seconds
    var category: String
    var isCompleted: Bool
    var createdAt: Date

    init(
        startTime: Date = .now,
        duration: TimeInterval = 1500, // 25 min default
        category: String = "Deep Work",
        isCompleted: Bool = false
    ) {
        self.startTime = startTime
        self.duration = duration
        self.category = category
        self.isCompleted = isCompleted
        self.createdAt = .now
    }

    var durationMinutes: Int {
        Int(duration / 60)
    }

    // BUG: No validation â negative duration possible
    // BUG: No Codable conformance for export/backup
}

--- USER INPUT ---
Build a focus timer that helps remote workers protect deep work time. 25-minute sessions with a visual countdown ring.

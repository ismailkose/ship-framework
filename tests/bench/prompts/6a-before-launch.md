You are running /ship-launch. Follow the command instructions below exactly.

--- COMMAND: ship-launch.md ---
---
description: "Deploy to production. Readiness check, launch, measurement plan."
disable-model-invocation: true
---

You are Cap, the Release Manager. Get it LIVE fast. Read CLAUDE.md and .claude/team-rules.md for context.

---

## Phase 0: Branch Resolution

```bash
git branch --show-current
git log main..HEAD --oneline
```

- If on feature branch: merge to main, create PR, or skip (present options)
- If already on main: proceed to Phase 1
- Always confirm destructive git ops with founder
- Clean up merged branches after

---

## Phase 1: Pre-Flight + Plan Completion Audit

```bash
git status
git log main..HEAD --oneline
git diff main --stat
```

Summarize: "Shipping X commits with Y files changed."

**Plan Completion Audit:**

Compare what /ship-plan specified vs what was actually built:

1. Read the last /ship-plan output (from DECISIONS.md or conversation)
2. Read `git diff main --stat`
3. For each item in /ship-plan's build order:
   - Was it built? (check if related files exist in the diff)
   - Was it tested? (check if test files exist)
   - Mark: COMPLETE / PARTIAL / MISSING

If any item is MISSING: "The plan specified [X] but it wasn't built. Ship without it, or build it first?"
If any item is PARTIAL: "[X] was started but not finished. The following is missing: [specifics]."

This catches the case where Dev built 4 of 5 planned items and everyone forgot about #5. Rule 20 (Boil the Lake) says finish it.
- Read `.claude/skills/ship/hardening/references/hardening-guide.md` Section 3:
  - Error boundaries, loading states, empty states on every UI section
  - 404 page designed and routed
  - Cross-browser tested (Chrome, Firefox, Safari, mobile)
- Flag pre-launch hardening gaps

---

## Phase 2: Run Tests

```bash
npm test
```

Show full test output. Classify failures:
- **IN-BRANCH:** You broke it. Hard stop. Fix before shipping.
- **PRE-EXISTING:** Fails on main too. Document and proceed.

Coverage check (platform-aware):
- Below 60%: HARD STOP
- 60-79%: WARNING, ask founder
- 80%+: PASS

If no coverage tool: flag it.

---

## Phase 3: Quality Gate

```bash
npx playwright --version 2>/dev/null  # detect mode
```

Mobile layout check (screenshot or code review):
- Layout works? Tap targets usable? Text readable?

Loading states, error handling, performance:
- Loading indicators present? No blank screens? App recovers gracefully?
- Homepage fast? Large images optimized? Unnecessary API calls?

---

## Phase 4: Ship Readiness

| Item | Status |
|------|--------|
| Meta tags, OG image, favicon | ✓/✗ |
| Analytics installed | ✓/✗ |
| Environment variables set | ✓/✗ |
| Domain connected, HTTPS enabled | ✓/✗ |

Growth checks (if Vi defined growth mechanism):
- Sharing, invite flow, SEO basics, attribution

Code review since last /ship-review:
- Compare HEAD vs LAST_REVIEW_HASH
- Scan for: broken imports, debug code, new TODOs
- Flag anything unsafe

Plan verification gate:
- Run /ship-plan verification steps if they exist
- All must pass or founder approves override

---

## Phase 5: Deploy

```bash
vercel --prod
# OR: git push origin main
```

Wait for deployment. Verify live URL loads.

---

## Phase 6: Post-Deploy Verification

Verify live URL loads, visit it, click main flow. Check on mobile, browser console, OG preview.

```bash
npx playwright screenshot [LIVE_URL] screenshots/ship-launch-live-desktop.png
npx playwright screenshot [LIVE_URL] screenshots/ship-launch-live-mobile.png --viewport-size="375,812"
```

---

## Phase 7: Ship Report

```
Ship Report
URL: [live URL]
Deployed: [date]
Commits: N
Tests: X passing

Quality Gate: Mobile ✓/✗, Loading ✓/✗, Error handling ✓/✗, Performance ✓/✗
Ship Readiness: Meta tags ✓/✗, Analytics ✓/✗
Post-deploy: [all clear / issues]
```

Update TASKS.md:
- Mark completed: `[x] Feature name (shipped 2026-03-27)`
- Note partial: `[ ] Feature name — PARTIAL: [what's missing]`

---

## Phase 8: Measurement Plan

Write to DECISIONS.md and CONTEXT.md:

```
Feature: [what shipped]
Vi's success metric: [HEART dimension + number from /ship-plan]
How to measure: [tool, dashboard, query]
When to check: [1 week / 2 weeks / 30 days]
Success looks like: [specific threshold]
If it fails: [iterate / pivot / kill]
```

Flag if founder hasn't set up analytics.

---

## Phase 8b: Documentation Sync

Check CONTEXT.md reflects shipping:
- Add "Product Learnings" entry
- Update "Active Experiments" if experiment

Check README and CLAUDE.md for staleness. Flag or fix obvious updates.

---

## Completion Status

End with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: DONE_WITH_CONCERNS` — completed, but [list concerns]
- `STATUS: BLOCKED` — cannot proceed: [reason]
- `STATUS: NEEDS_CONTEXT` — missing: [what information]

"It's live at [URL]. Measurement plan filed — Retro will check in on [date]."

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
Ship it. The focus timer is built and reviewed. Let's deploy.

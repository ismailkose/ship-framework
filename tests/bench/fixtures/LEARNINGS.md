# Learnings — FocusFlow

## Code Patterns
- **2026-04-10** Timer invalidation — Always invalidate Timer in onDisappear, not just deinit. SwiftUI view lifecycle doesn't guarantee deinit timing.

## Design Preferences
- **2026-04-10** Founder prefers large, bold time display (like a wall clock). No small digital readout.
- **2026-04-10** Founder dislikes gradient backgrounds. Keep it flat.

## Architecture Decisions
- **2026-04-10** Keep all state in FocusSession model. Don't split timer state across multiple sources.

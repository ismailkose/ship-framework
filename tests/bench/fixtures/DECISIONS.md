# Decisions — FocusFlow

## Architecture
- **2026-04-10** — Using SwiftData over Core Data. Simpler API, native Swift, good enough for v1.
- **2026-04-10** — MVVM pattern. Views observe ViewModels via @Observable.

## Design Direction
- **Aesthetic:** Bold choice — dark-first, monochrome with a single accent color (warm amber #F59E0B). Inspired by analog timers. Large typography. Minimal chrome.
- **Font:** SF Pro Rounded (display), SF Pro (body)
- **Motion:** Subtle — timer ring animation, gentle haptics. No bouncy springs.

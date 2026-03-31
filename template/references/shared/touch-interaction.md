# Touch & Interaction Reference

> Agent routing:
> Arc → Section 1 (interaction model affects screen architecture)
> Dev → Sections 1-2 (implement targets, gestures, feedback, safe areas)
> Eye → Section 1 (verify tap targets visually, press feedback quality)
> Pol → Section 1 (audit interaction consistency)
> Test → Section 2 (verify targets, rapid interaction, gesture conflicts, safe areas)
>
> **Overlap note:** This file covers the *physical layer* — tap targets, safe areas, haptics, press feedback timing. For the *behavioral layer* (8-state model, micro-interaction patterns, gesture design philosophy), see `interaction-design.md`. Both files complement each other.

## Section 1: Touch Target Design

### Why 44pt/48dp Minimum Isn't Arbitrary

Apple's 44pt (approximately 10mm) and Google's 48dp standards derive from Fitts's Law applied to touch surfaces. The average human finger pad is ~10mm across. When designing tap targets, you're not just accounting for the fingertip itself—you need margin for accuracy variance, especially during mobile movement or one-handed use.

**The math:** Apple selected 44pt as the minimum because it represents the sweet spot between adequacy (smaller feels unreliable) and space efficiency (larger wastes screen real estate). Google's 48dp adds a ~2mm safety margin on each side, acknowledging that touch accuracy degrades under motion or cognitive load.

**Consequences of undersizing:**
- Users compensate by tapping harder or multiple times
- Mis-taps increase by ~30% below 40pt
- Users with reduced motor control (tremor, arthritis) become effectively locked out
- Double-tap bugs emerge from users compensating with rapid retaps

### Spacing Between Targets: The 8px Gap Rule

Two buttons at 44pt × 44pt sitting adjacent with zero space create a ~88px span. This invites mis-taps—especially on narrow screens where targets must be packed tight.

**Why 8px minimum:**
- At arm's length (phone height), 8px ≈ 1.5mm visual gap
- This is visible enough to register as distinct targets
- Below 8px, targets appear fused together; eyes don't register the boundary
- Adjacent buttons with zero gap cause 15-20% mis-tap increase

**Platform guidance:**
- iOS: Use safe margins in all directions (8-12px between interactive elements)
- Android: Material Design specifies 8dp gaps; Material 3 extends to 12dp for accessibility
- Web: CSS margin or gap property; don't rely on visual overlap for spacing

### Press Feedback Philosophy

Users need confirmation within 100ms that their tap registered. Without it, they tap again—creating double-submit bugs, unintended purchases, or duplicate actions.

**The 100ms threshold:**
- Human tactile perception peaks at ~100ms latency
- Above 150ms, users perceive a gap and assume the tap didn't register
- At 200ms+, users almost certainly tap again

**Feedback hierarchy (pick one or combine):**
1. **Visual (always required):** Background color shift, slight scale change (1-3%), or highlight color
2. **Haptic (selective):** Light tap for confirmations, medium for irreversible actions
3. **Sonic (rare):** Subtle click sound; overuse causes notification fatigue

**What triggers feedback:**
- Button down or touchstart → immediate visual change
- Button up or touchend → confirmation (optional haptic)
- Never delay feedback to wait for network; show local feedback instantly

### Haptic Feedback: When to Use

Haptic is powerful but easily abused. Too much creates vibration fatigue and battery drain.

**Appropriate use:**
- Confirmations of irreversible actions (delete, submit payment)
- Toggle state change (on/off switch)
- Error states requiring attention
- Long-press successful registration

**Avoid:**
- Every tap (users turn off haptic after 30 seconds)
- Informational modals or dialogs
- Scroll events
- Hover-equivalent feedback on touch
- Rapid-fire haptic (multiple taps in quick succession)

**Technical note:** Prefer `navigator.vibrate([20])` (light tap) or `[50]` (medium) over longer durations. Battery impact is negligible for <100ms patterns.

### Hover vs. Tap: Progressive Enhancement, Not Gatekeeping

Hover is a pointer-device feature. Touch devices do not have hover. Never hide critical functionality behind hover-only states.

**The rule:** If it's important, put it in tap feedback, not hover.

**Safe hover patterns:**
- Tooltip preview (non-critical)
- Subtle color shift (hint, not essential information)
- Expand for details (quick-look, but full info available on tap)

**Never do this:**
- Hide close button on modals until hover
- Require hover to reveal delete option
- Show price/rating only on hover
- Gate advanced settings behind hover menu

**Web implementation:** Test with `@media (hover: none)` queries; design without hover first, then add hover as enhancement.

### Gesture Conflicts with System Gestures

iOS and Android reserve screen edges for system navigation.

**iOS reserved gestures:**
- Left edge swipe-back (navigation, dismissal)
- Bottom swipe-up (home indicator interaction, task switcher)
- Top swipe-down (notification center)

**Android reserved gestures:**
- Predictive back (left edge, 5% of screen width)
- Gesture navigation (swipe-up from bottom for home, swipe from left/right for back)
- Dynamic Island / system bar interactions

**The conflict:** Custom swipes near edges interfere with system gestures. Users swipe to go back and hit your custom gesture instead. Result: frustration, abandoned actions, one-star reviews.

**Solutions:**
- Keep custom horizontal swipes >20% from left/right edges
- If swipe is necessary near edges, require longer gesture (>50% screen width) before activation
- Add visual affordance (drag handle icon) to suggest swipe direction
- Test on actual devices—simulators don't perfectly simulate system gesture detection

### Gesture Alternatives: Accessibility Requirement

Every custom gesture (swipe, pinch, long-press) must have a button alternative. This is not optional.

**Why:**
- Accessibility users (voice control, switch control) cannot perform multi-touch gestures
- Motor impairments may make specific gestures unreliable
- New users don't discover hidden gestures
- Power users prefer explicit actions over guessing

**Pattern:**
- Swipe to delete → Swipe OR three-dot menu with delete
- Pinch to zoom → Pinch OR +/- buttons
- Long-press to edit → Long-press OR double-tap OR edit button
- Rotate gesture → Rotate OR rotate buttons

**Testing:** Use accessibility inspector to verify all gesture features have labeled alternatives.

### Platform-Specific Safe Areas

**iOS:** Account for notch (Dynamic Island on newer models) and home indicator.
- Top margin: 20pt (notch area)
- Bottom margin: 34pt (home indicator)
- Use `safe-area-inset-*` CSS or Safe Area Insets in SwiftUI

**Android:** Account for status bar and navigation bar (when gesture nav disabled).
- Top margin: varies (18-24dp typical)
- Bottom margin: 0dp (gesture nav active) or 48-56dp (legacy nav buttons)
- Use `ViewCompat.setOnApplyWindowInsetsListener()` or `windowInsetsPadding()`

**Web:** Use viewport-fit and env() variables for notches.
```css
@supports (padding: max(0px)) {
  body { padding-left: max(1rem, env(safe-area-inset-left)); }
}
```

### Web-Specific CSS Patterns

**Remove double-tap zoom delay:**
```css
button, [role="button"] { touch-action: manipulation; }
```
Without this, browsers wait 300ms after tap to detect double-tap-to-zoom, delaying your tap handlers.

**Prevent scroll bleed on modals:**
```css
.modal { overscroll-behavior: contain; }
```
Stops momentum scroll from modal from scrolling body content underneath—common source of UX friction.

---

## Section 2: QA Patterns

### Measure Actual Tap Targets (Not Visual Size)

Visible button size ≠ tap target size. Padding counts.

**Testing approach:**
1. Use accessibility inspector (iOS: Accessibility Inspector, Android: Android Studio Layout Inspector, Web: DevTools)
2. Verify hit region, not just visual bounds
3. Check padding on all sides
4. For buttons with icons, ensure padding extends to minimum 44pt in all directions

**Example issue:** A 32pt icon centered in a button with 4pt padding = 40pt hit region (too small). Same icon with 8pt padding = 48pt hit region (acceptable).

### Rapid Tap Testing

Users tap interfaces quickly. Verify your handlers don't break under rapid input.

**Protocol:**
- Tap same button 5-10 times as fast as possible
- Verify single action fires once, not repeated
- Check for double-submit (critical for commerce features)
- Test on actual devices at varying network speeds (slow 4G especially)

**Common failure:** Network request completes after user taps twice; both requests go through. Implement request deduplication or disable button during request.

### Gesture Navigation Alongside App Gestures

If your app uses custom swipe gestures, test that system gestures still work.

**Protocol (iOS):**
- Swipe-back from left edge (should trigger system back, not your gesture)
- Swipe-up from home indicator (should open task switcher, not your gesture)
- Test near edges (within 20% from left/right)

**Protocol (Android):**
- Predictive back gesture (left 5% of screen)
- Task switcher (swipe-up from bottom)
- App switcher (swipe-up and hold)

**Failure case:** User tries to go back, triggers your custom swipe instead. Action gets reversed or unexpected UI appears.

### Safe Area Verification on Notched Devices

Content must not hide behind notches or be inaccessible near home indicators.

**Testing:**
- Test on actual iPhone with notch (or Dynamic Island)
- Test on Android devices with centered punch-hole camera
- Rotate between portrait and landscape
- Verify buttons near bottom are accessible above home indicator

**Common issue:** Fixed bottom button gets covered by home indicator in landscape. Use `safe-area-inset-bottom` to push it up.

### Press Feedback Timing Verification

Measure latency between touchstart and visual feedback.

**Protocol:**
- Record device screen at 60fps (slow-motion video)
- Tap button
- Count frames from touch to visual change (button highlight, scale, etc.)
- Acceptable: ≤2 frames (33ms at 60fps)
- Marginal: 3-5 frames (50-83ms)
- Unacceptable: >150ms

**Tool:** Use frame-by-frame video playback or frame profilers in DevTools. On web, log `performance.now()` at touchstart and visual render to calculate latency.

**Network caveat:** If feedback depends on server response, show local feedback immediately (scale button, color shift), then confirm once response arrives.

---

## Reference Summary

| Pattern | Minimum | Guidance |
|---------|---------|----------|
| Tap target | 44pt/48dp | Never below 40pt; prefer 48pt+ |
| Gap between targets | 8px | 12px+ for crowded layouts |
| Feedback latency | <100ms | Never >150ms |
| Safe area (iOS) | Top 20pt, Bottom 34pt | Use env() and inset utilities |
| Safe area (Android) | Top 18-24dp | Adapt to nav bar state |
| Edge gesture margin | >20% from edge | System gestures take priority |
| Haptic events | Selective | Max 1-2 per interaction |


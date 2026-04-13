// FocusTimerView.swift — FocusFlow
// This file has INTENTIONAL issues for /ship-review to catch

import SwiftUI

struct FocusTimerView: View {
    @State private var timeRemaining = 1500 // 25 minutes
    @State private var isRunning = false
    @State private var timer: Timer?

    var body: some View {
        VStack {
            // BUG: No spacing scale — magic numbers everywhere
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

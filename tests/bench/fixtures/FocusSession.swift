// FocusSession.swift — FocusFlow
// Data model — this file is relatively clean

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

    // BUG: No validation — negative duration possible
    // BUG: No Codable conformance for export/backup
}

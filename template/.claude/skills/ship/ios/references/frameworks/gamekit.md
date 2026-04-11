# GameKit Reference

> **When to read:** Dev reads when implementing Game Center features.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Authentication

**Must authenticate before any GameKit API call:**

```swift
import GameKit

func authenticatePlayer() {
  GKLocalPlayer.local.authenticateHandler = { viewController, error in
    if let vc = viewController {
      // Present Game Center login
      rootViewController.present(vc, animated: true)
    } else if GKLocalPlayer.local.isAuthenticated {
      // Player is signed in — enable Game Center features
      enableGameCenterFeatures()
    } else {
      // Authentication failed — disable Game Center features
      disableGameCenterFeatures()
    }
  }
}
```

## Access Point

System Game Center overlay UI:

```swift
GKAccessPoint.shared.location = .topLeading
GKAccessPoint.shared.showHighlights = true
GKAccessPoint.shared.isActive = true  // show the access point

// Trigger Game Center dashboard
GKAccessPoint.shared.trigger(state: .leaderboards) { }
```

## Leaderboards

```swift
// Submit score
GKLeaderboard.submitScore(
  score,
  context: 0,
  player: GKLocalPlayer.local,
  leaderboardIDs: ["com.app.leaderboard.highscore"]
) { error in
  if let error { print("Score submission failed: \(error)") }
}

// Load scores
let leaderboard = try await GKLeaderboard.loadLeaderboards(IDs: ["com.app.leaderboard.highscore"]).first
let (localEntry, entries, count) = try await leaderboard!.loadEntries(
  for: .global,
  timeScope: .allTime,
  range: NSRange(1...10)
)
```

## Achievements

```swift
// Report progress (0.0 to 100.0)
let achievement = GKAchievement(identifier: "com.app.achievement.firstWin")
achievement.percentComplete = 100.0
achievement.showsCompletionBanner = true

GKAchievement.report([achievement]) { error in
  if let error { print("Achievement failed: \(error)") }
}

// Load achievements
let achievements = try await GKAchievement.loadAchievements()
```

## Real-Time Multiplayer

```swift
// Find match
let request = GKMatchRequest()
request.minPlayers = 2
request.maxPlayers = 4

let match = try await GKMatchmaker.shared().findMatch(for: request)

// Send data to all players
let data = try JSONEncoder().encode(gameState)
try match.sendData(toAllPlayers: data, with: .reliable)

// Receive data
extension GameController: GKMatchDelegate {
  func match(_ match: GKMatch, didReceive data: Data, fromRemotePlayer player: GKPlayer) {
    let state = try? JSONDecoder().decode(GameState.self, from: data)
    // Update game state
  }

  func match(_ match: GKMatch, player: GKPlayer, didChange state: GKPlayerConnectionState) {
    switch state {
    case .connected: // player joined
    case .disconnected: // player left — handle gracefully
    @unknown default: break
    }
  }
}
```

## Turn-Based Multiplayer

```swift
let request = GKMatchRequest()
request.minPlayers = 2
request.maxPlayers = 4

// Create match
GKTurnBasedMatchmakerViewController handles UI

// Take turn
let data = try JSONEncoder().encode(turnData)
try await match.endTurn(
  withNextParticipants: match.participants.filter { $0 != match.currentParticipant },
  turnTimeout: GKTurnTimeoutDefault,
  match: data
)

// End match
try await match.endMatchInTurn(withMatch: finalData)
```

## Common Mistakes
- ❌ Calling GameKit APIs before authentication — all calls will fail
- ❌ Not re-setting `authenticateHandler` after it fires — handler can be called multiple times
- ❌ Ignoring `GKPlayerConnectionState.disconnected` — causes frozen games
- ❌ Assuming all players are Game Center members — some may be guests
- ❌ Not handling restricted players (parental controls) — check `GKLocalPlayer.local.isUnderage`
- ❌ Submitting scores without checking authentication — silent failures

## Review Checklist
- [ ] Authentication handled before any GameKit API call
- [ ] Access Point configured and visible on appropriate screens
- [ ] Leaderboard and achievement IDs match App Store Connect configuration
- [ ] Real-time multiplayer handles disconnection gracefully
- [ ] Turn-based matches handle timeout scenarios
- [ ] Parental restriction checks in place (`isUnderage`, `isMultiplayerGamingRestricted`)

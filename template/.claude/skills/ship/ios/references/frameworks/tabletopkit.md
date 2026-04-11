# TabletopKit Reference

> **When to read:** Dev reads when building visionOS multiplayer board games.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Overview

TabletopKit is a visionOS framework for building multiplayer tabletop games with spatial interactions. Integrates with RealityKit for 3D rendering and GroupActivities for multiplayer.

## Game Setup

```swift
import TabletopKit
import RealityKit

let tabletop = TabletopGame()

// Define the table
let table = TableConfiguration(
  shape: .rectangular(width: 0.8, depth: 0.6),
  surface: .wood
)
tabletop.setup(with: table)
```

## Equipment

```swift
// Cards
let deck = Deck(cards: (1...52).map { Card(id: $0) })
tabletop.add(deck, at: .center)

// Dice
let die = Die(faces: 6)
tabletop.add(die, at: .position(x: 0.2, z: 0.1))

// Tokens/Pieces
let token = GamePiece(model: "pawn", color: .red)
tabletop.add(token, at: .seat(playerIndex: 0))
```

## Actions and Interactions

```swift
// Define valid actions
tabletop.registerAction(.drawCard(from: deck)) { context in
  let card = deck.draw()
  context.player.hand.add(card)
}

tabletop.registerAction(.rollDice(die)) { context in
  let result = die.roll()
  context.broadcast(result)  // all players see the roll
}

// Spatial interactions — players grab, move, place pieces
tabletop.spatialInteraction = .enabled
```

## Common Mistakes
- ❌ Not handling player disconnection in multiplayer — game state becomes inconsistent
- ❌ Forgetting GroupActivities integration for multiplayer — required for shared sessions
- ❌ Not defining valid placement zones — pieces end up in invalid positions

## Review Checklist
- [ ] Game state synchronized across all players
- [ ] Spatial interactions feel natural (grab, place, roll)
- [ ] Turn order enforced correctly
- [ ] Player disconnection handled gracefully
- [ ] Visual feedback for valid/invalid placements

# SpriteKit Reference

> **When to read:** Dev reads when building 2D game scenes.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Scene Setup

```swift
import SpriteKit

class GameScene: SKScene {
  override func didMove(to view: SKView) {
    backgroundColor = .black
    physicsWorld.gravity = CGVector(dx: 0, dy: -9.8)
    physicsWorld.contactDelegate = self
  }

  override func update(_ currentTime: TimeInterval) {
    // Called every frame — game logic here
  }
}

// Present in SwiftUI
struct GameView: View {
  var body: some View {
    SpriteView(scene: GameScene(size: CGSize(width: 390, height: 844)))
      .ignoresSafeArea()
  }
}
```

## Nodes

```swift
// Sprite
let player = SKSpriteNode(imageNamed: "player")
player.position = CGPoint(x: frame.midX, y: frame.midY)
player.size = CGSize(width: 50, height: 50)
addChild(player)

// Shape
let circle = SKShapeNode(circleOfRadius: 25)
circle.fillColor = .red
circle.strokeColor = .white
addChild(circle)

// Label
let score = SKLabelNode(text: "Score: 0")
score.fontName = "AvenirNext-Bold"
score.fontSize = 24
score.position = CGPoint(x: frame.midX, y: frame.maxY - 50)
addChild(score)
```

## Actions

```swift
// Movement
let moveUp = SKAction.moveBy(x: 0, y: 100, duration: 0.5)
let moveDown = moveUp.reversed()

// Sequences and groups
let sequence = SKAction.sequence([moveUp, .wait(forDuration: 0.2), moveDown])
let group = SKAction.group([moveUp, SKAction.fadeOut(withDuration: 0.5)])  // simultaneous

// Repeat
let forever = SKAction.repeatForever(sequence)
player.run(forever, withKey: "bounce")

// Remove by key
player.removeAction(forKey: "bounce")
```

## Physics

```swift
player.physicsBody = SKPhysicsBody(rectangleOf: player.size)
player.physicsBody?.isDynamic = true
player.physicsBody?.categoryBitMask = PhysicsCategory.player
player.physicsBody?.contactTestBitMask = PhysicsCategory.enemy
player.physicsBody?.collisionBitMask = PhysicsCategory.ground

struct PhysicsCategory {
  static let player: UInt32 = 0x1 << 0
  static let enemy: UInt32 = 0x1 << 1
  static let ground: UInt32 = 0x1 << 2
}

// Contact detection
extension GameScene: SKPhysicsContactDelegate {
  func didBegin(_ contact: SKPhysicsContact) {
    let collision = contact.bodyA.categoryBitMask | contact.bodyB.categoryBitMask
    if collision == PhysicsCategory.player | PhysicsCategory.enemy {
      handlePlayerHit()
    }
  }
}
```

## Touch Handling

```swift
override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
  guard let touch = touches.first else { return }
  let location = touch.location(in: self)
  let tappedNodes = nodes(at: location)

  for node in tappedNodes {
    if node.name == "playButton" {
      startGame()
    }
  }
}
```

## Camera

```swift
let camera = SKCameraNode()
addChild(camera)
self.camera = camera

// Follow player
let follow = SKAction.move(to: player.position, duration: 0.2)
camera.run(follow)
```

## Particles

```swift
if let emitter = SKEmitterNode(fileNamed: "Explosion.sks") {
  emitter.position = explosionPoint
  addChild(emitter)
  emitter.run(.sequence([.wait(forDuration: 2), .removeFromParent()]))
}
```

## Common Mistakes
- ❌ Creating a new scene on every game restart — reuse and reset state instead
- ❌ Adding a node to multiple parents — remove from current parent first
- ❌ Wrong contact bit masks — `contactTestBitMask` detects contacts, `collisionBitMask` handles physics
- ❌ Using `SKShapeNode` for complex shapes in production — performance is poor, use sprites
- ❌ Not removing completed particle emitters — memory leak
- ❌ Accessing `frame` in `init` — frame isn't set yet, use `didMove(to:)`

## Review Checklist
- [ ] Scene presented correctly in SwiftUI or UIKit
- [ ] Physics bodies match visual sizes
- [ ] Contact detection bit masks configured correctly
- [ ] Particle emitters removed after completion
- [ ] Touch handling accounts for multiple simultaneous touches
- [ ] Game loop in `update()` uses delta time, not absolute time
- [ ] Nodes properly removed when off-screen
- [ ] Memory profiled for large number of nodes

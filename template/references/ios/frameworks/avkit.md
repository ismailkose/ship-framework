# AVKit Reference

> **When to read:** Dev reads when building video playback features.
> Eye reads Common Mistakes and Review Checklist during review.

---

## AVPlayerViewController (UIKit)

Standard system video player with full transport controls:

```swift
import AVKit

let player = AVPlayer(url: videoURL)
let playerVC = AVPlayerViewController()
playerVC.player = player
playerVC.allowsPictureInPicturePlayback = true
playerVC.canStartPictureInPictureAutomaticallyFromInline = true
present(playerVC, animated: true) {
  player.play()
}
```

Configure audio session for playback:
```swift
try AVAudioSession.sharedInstance().setCategory(.playback, mode: .moviePlayback)
try AVAudioSession.sharedInstance().setActive(true)
```

## SwiftUI VideoPlayer

```swift
import AVKit

struct PlayerView: View {
  @State private var player = AVPlayer(url: videoURL)

  var body: some View {
    VideoPlayer(player: player) {
      // Optional overlay
      VStack {
        Spacer()
        Text("Custom Overlay")
          .padding()
          .background(.ultraThinMaterial)
      }
    }
    .onAppear { player.play() }
    .onDisappear { player.pause() }
  }
}
```

## Picture-in-Picture

Requirements:
1. Set `Audio, AirPlay, and Picture in Picture` background mode in capabilities
2. Configure audio session category to `.playback`
3. Set `allowsPictureInPicturePlayback = true`

```swift
// Respond to PiP lifecycle
extension PlayerCoordinator: AVPlayerViewControllerDelegate {
  func playerViewControllerWillStartPictureInPicture(_ controller: AVPlayerViewController) {
    // PiP starting — update UI state
  }

  func playerViewControllerDidStopPictureInPicture(_ controller: AVPlayerViewController) {
    // PiP ended — restore inline player
  }

  func playerViewController(_ controller: AVPlayerViewController,
    restoreUserInterfaceForPictureInPictureStopWithCompletionHandler handler: @escaping (Bool) -> Void) {
    // System wants to return to app — present player, then call handler(true)
    handler(true)
  }
}
```

## AirPlay

AirPlay routing is automatic with `AVPlayerViewController`. For custom UI:

```swift
import AVKit

// Route picker button
AVRoutePickerView()  // system-provided AirPlay button

// Check if AirPlay is active
NotificationCenter.default.addObserver(
  forName: AVAudioSession.routeChangeNotification,
  object: nil, queue: .main
) { notification in
  let currentRoute = AVAudioSession.sharedInstance().currentRoute
  let isAirPlay = currentRoute.outputs.contains { $0.portType == .airPlay }
}
```

## Subtitles and Closed Captions

```swift
// Load asset with media selection
let asset = AVAsset(url: videoURL)
let mediaCharacteristic = AVMediaCharacteristic.legible  // subtitles
if let group = try await asset.loadMediaSelectionGroup(for: mediaCharacteristic) {
  let options = group.options  // available subtitle tracks
  player.currentItem?.select(options.first, in: group)
}
```

## Transport Controls Customization

```swift
playerVC.showsPlaybackControls = true
playerVC.updatesNowPlayingInfoCenter = true  // Lock Screen controls
playerVC.entersFullScreenWhenPlaybackBegins = false
playerVC.exitsFullScreenWhenPlaybackEnds = true
```

## Common Mistakes
- ❌ Subclassing `AVPlayerViewController` — Apple explicitly prohibits this
- ❌ Forgetting to set audio session category — playback is silent or interrupted
- ❌ Not implementing PiP restoration handler — user can't return to app from PiP
- ❌ Creating new `AVPlayer` on every view appear — reuse the player instance
- ❌ Not calling `player.pause()` on view disappear — audio continues in background
- ❌ Ignoring `AVAudioSession.interruptionNotification` — handle phone calls, alarms

## Review Checklist
- [ ] Audio session category set to `.playback` before player starts
- [ ] PiP background mode enabled if PiP is supported
- [ ] PiP delegate implements restoration handler
- [ ] Player paused/released when view disappears
- [ ] AirPlay routing works (test with AirPlay-capable device)
- [ ] Subtitle tracks load correctly for localized content

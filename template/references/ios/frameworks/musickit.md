# MusicKit — iOS Reference

> **When to read:** Dev reads this when building features that access Apple Music catalog, create playlists, or control playback.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `MusicAuthorization` | Grants library access; `.authorized`, `.denied`, `.notDetermined`, `.restricted` |
| `MusicCatalogSearchRequest` | Query Apple Music catalog; songs, albums, artists, playlists |
| `MusicLibraryRequest` | Access user's Apple Music library |
| `ApplicationMusicPlayer` | Shared playback controller; play, pause, skip, volume |
| `SystemMusicPlayer` | System-wide player; more limited control |
| `MusicSubscriptionStatus` | User's Apple Music subscription state |
| `Song`, `Album`, `Artist`, `Playlist` | Codable models representing media |
| `MediaItem` | Protocol; common interface for Song, Album, etc. |
| `MusicItemCollection` | Paginated results from search/library requests |

---

## Code Examples

### Example 1: Search Apple Music catalog
```swift
import MusicKit

func searchAppleMusic(for query: String) async throws -> MusicItemCollection<Song> {
    var searchRequest = MusicCatalogSearchRequest(term: query, types: [Song.self])
    searchRequest.limit = 10

    let results = try await searchRequest.response()
    return results.songs
}

// Usage
Task {
    do {
        let songs = try await searchAppleMusic(for: "Taylor Swift")
        songs.forEach { song in
            print("\(song.title) by \(song.artistName)")
        }
    } catch {
        print("Search error: \(error)")
    }
}
```

### Example 2: Request music library authorization
```swift
import MusicKit

func requestMusicAuthorization() async {
    let status = MusicAuthorization.currentStatus

    switch status {
    case .authorized:
        print("Already authorized")
    case .denied:
        print("User denied access")
    case .notDetermined:
        let newStatus = await MusicAuthorization.request()
        print("Authorization result: \(newStatus)")
    case .restricted:
        print("Access restricted by parental controls")
    @unknown default:
        break
    }
}
```

### Example 3: Load user's library and create playlist
```swift
import MusicKit

func createPlaylistInLibrary(name: String) async throws {
    // First request authorization
    if MusicAuthorization.currentStatus != .authorized {
        _ = await MusicAuthorization.request()
    }

    guard MusicAuthorization.currentStatus == .authorized else {
        throw NSError(domain: "MusicKit", code: 1, userInfo: [NSLocalizedDescriptionKey: "Not authorized"])
    }

    // Search for some songs
    var searchRequest = MusicCatalogSearchRequest(term: "jazz", types: [Song.self])
    searchRequest.limit = 5
    let searchResults = try await searchRequest.response()

    // Create playlist request
    let playlistRequest = MusicLibraryPlaylistCreationRequest(name: name)
    playlistRequest.songs = searchResults.songs

    let createdPlaylist = try await playlistRequest.response()
    print("Playlist created: \(createdPlaylist.name)")
}
```

### Example 4: Control playback with ApplicationMusicPlayer
```swift
import MusicKit

func playMusic(song: Song) async throws {
    let player = ApplicationMusicPlayer.shared

    var queue = ApplicationMusicPlayer.Queue()
    queue.insert(song, position: .nextUp)

    try await player.queue.insert(contentsOf: [song], position: .nextUp)
    try await player.play()

    print("Now playing: \(song.title)")
}

// Usage: control playback
func controlPlayback() async throws {
    let player = ApplicationMusicPlayer.shared

    // Play/pause
    try await player.pause()
    try await player.play()

    // Skip to next
    try await player.skipToNextEntry()

    // Change volume
    player.volume = 0.8
}
```

### Example 4b: Check current subscription and observe updates
```swift
func checkSubscription() async throws -> Bool {
    let subscription = try await MusicSubscription.current
    return subscription.canPlayCatalogContent
}

// Observe subscription changes
func observeSubscription() async {
    for await subscription in MusicSubscription.subscriptionUpdates {
        if subscription.canPlayCatalogContent {
            // Enable full playback UI
        } else {
            // Show subscription offer
        }
    }
}
```

### Example 4c: Show subscription offer sheet
```swift
struct MusicOfferView: View {
    @State private var showOffer = false

    var body: some View {
        Button("Subscribe to Apple Music") {
            showOffer = true
        }
        .musicSubscriptionOffer(isPresented: $showOffer)
    }
}
```

### Example 4d: SystemMusicPlayer vs ApplicationMusicPlayer
```swift
// CORRECT: App-scoped playback (use ApplicationMusicPlayer)
let player = ApplicationMusicPlayer.shared

// WRONG: Controls system Music app (avoid for app-specific playback)
let systemPlayer = SystemMusicPlayer.shared
```

### MusicSubscription.current and subscriptionUpdates

Check current subscription status and observe subscription changes:

```swift
func checkSubscription() async throws -> Bool {
    let subscription = try await MusicSubscription.current
    return subscription.canPlayCatalogContent
}

// Observe subscription changes
func observeSubscription() async {
    for await subscription in MusicSubscription.subscriptionUpdates {
        if subscription.canPlayCatalogContent {
            // Enable full playback UI
        } else {
            // Show subscription offer
        }
    }
}
```

### musicSubscriptionOffer Modifier

Present the Apple Music subscription offer sheet when the user is not subscribed:

```swift
struct MusicOfferView: View {
    @State private var showOffer = false

    var body: some View {
        Button("Subscribe to Apple Music") {
            showOffer = true
        }
        .musicSubscriptionOffer(isPresented: $showOffer)
    }
}
```

### Example 5: Check subscription status
```swift
import MusicKit

func checkSubscription() async throws {
    let subscriptionStatus = MusicSubscriptionStatus()
    let canPlayCatalogContent = subscriptionStatus.canPlayCatalogContent
    let canPlayStorefrontContent = subscriptionStatus.canPlayStorefrontContent

    if canPlayCatalogContent {
        print("User can play full Apple Music catalog")
    } else {
        print("User has limited or no subscription")
    }

    // Can also check individual availability
    if #available(iOS 16, *) {
        let status = MusicSubscriptionStatus()
        switch status.state {
        case .active:
            print("Subscription active")
        case .inactive, .noSubscription, .trialExpired:
            print("No active subscription")
        @unknown default:
            break
        }
    }
}
```

---

## Common Mistakes

### ❌ Not checking authorization before accessing music library
```swift
// Bad: Crashes or silently fails
var libraryRequest = MusicLibraryRequest()
let results = try await libraryRequest.response()
```
✅ **Fix:** Request authorization first
```swift
if MusicAuthorization.currentStatus != .authorized {
    _ = await MusicAuthorization.request()
}

guard MusicAuthorization.currentStatus == .authorized else {
    print("Music library access denied")
    return
}

var libraryRequest = MusicLibraryRequest()
let results = try await libraryRequest.response()
```

### ❌ Running async MusicKit calls on main thread
```swift
// Bad: Blocks UI
Task {
    let songs = try await searchAppleMusic(for: "query")
    updateUI(with: songs)
}
```
✅ **Fix:** Explicitly run on background, update UI on main
```swift
Task {
    let songs = try await searchAppleMusic(for: "query")
    DispatchQueue.main.async {
        updateUI(with: songs)
    }
}

// Or use @MainActor for UI updates
@MainActor
func updateUI(with songs: [Song]) {
    // Update views
}
```

### ❌ Not paginating large music library requests
```swift
// Bad: May timeout or consume excessive memory
var libraryRequest = MusicLibraryRequest()
// No limit; tries to fetch entire library at once
let allSongs = try await libraryRequest.response()
```
✅ **Fix:** Paginate results
```swift
var libraryRequest = MusicLibraryRequest()
libraryRequest.limit = 50

var allSongs: [Song] = []
var pageOffset = 0

repeat {
    let results = try await libraryRequest.response()
    allSongs.append(contentsOf: results.songs)
    pageOffset += results.songs.count
} while pageOffset < 1000 // Or until no more results
```

### ❌ Assuming catalog availability in all regions
```swift
// Bad: Some content unavailable in user's region
var searchRequest = MusicCatalogSearchRequest(term: "artist", types: [Song.self])
let results = try await searchRequest.response()
```
✅ **Fix:** Check availability; offer fallback
```swift
do {
    var searchRequest = MusicCatalogSearchRequest(term: "artist", types: [Song.self])
    let results = try await searchRequest.response()
    if results.songs.isEmpty {
        print("No results in this region")
        // Show cached content or alternative
    }
} catch {
    print("Search unavailable: \(error)")
    // Use alternative source
}
```

### ❌ Not handling subscription state changes
```swift
// Bad: UI shows full content; user has no subscription
func playFromCatalog(song: Song) async throws {
    try await player.play()
}
```
✅ **Fix:** Check subscription before playing catalog content
```swift
func playFromCatalog(song: Song) async throws {
    let subscriptionStatus = MusicSubscriptionStatus()

    if subscriptionStatus.canPlayCatalogContent {
        try await player.play()
    } else {
        throw NSError(domain: "MusicKit", code: 1, userInfo: [
            NSLocalizedDescriptionKey: "Subscription required to play this content"
        ])
    }
}
```

---

## Review Checklist

- [ ] `MusicAuthorization.currentStatus` checked before library access
- [ ] `MusicAuthorization.request()` called if `.notDetermined`
- [ ] Authorization denial handled gracefully
- [ ] Music operations run on background thread; UI updates on main thread
- [ ] Search/library requests paginated for large result sets
- [ ] Subscription status checked before playing catalog content
- [ ] Regional availability handled (catalog may be unavailable)
- [ ] Queue manipulations use proper insert positions (`.nextUp`, `.end`)
- [ ] Error handling covers network failures, authorization errors
- [ ] Playback state observed (if using ApplicationMusicPlayer.nowPlayingItem)
- [ ] Privacy: `NSAppleMusicUsageDescription` in Info.plist (if accessing library)
- [ ] Tests mock MusicKit requests; handle offline scenarios

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

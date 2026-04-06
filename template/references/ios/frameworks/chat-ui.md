# Chat UI — Production Patterns for Conversational Interfaces

> **When to use:** Any project with a chat, messaging, or AI assistant interface.
> **Source:** Vercel's v0 iOS engineering (React Native) + SwiftUI translation by krispuckett/V0Swift.
> **Applies to:** SwiftUI, React Native, Flutter, Kotlin Compose, Web — Part 1 is universal.

---

## Part 1: Universal Principles

These patterns apply regardless of your tech stack. Every production chat UI
hits the same problems — the platform just changes how you solve them.

---

### 1.1 Architecture Philosophy

> "We did not set out to build a mobile IDE with feature parity with our website.
> Instead, we wanted to build a simple, delightful experience for using AI to
> make things on the go."

**The mental model:** Your app is a thin, beautiful wrapper over your API. Let
the server do the heavy lifting; let the UI create delight.

**Production chat requirements — the checklist:**

- New messages animate in smoothly
- New user messages scroll to the top of the screen (not bottom)
- Assistant messages fade in with staggered animation as they stream
- Composer floats on top of scrollable content (Liquid Glass / blur)
- Opening existing chats starts scrolled to the end
- Keyboard handling feels native (interactive dismissal, no jitter)
- Text input supports images, files, and paste
- Text input supports gestures (swipe up to focus)
- Markdown renders fast with streaming support
- Streaming content limits concurrent animations (pool pattern)

If your chat doesn't meet all of these, users will feel it — even if they can't
articulate what's wrong.

**Composable plugin architecture:** Structure chat as composable features, not a
monolith. Each concern (keyboard, animation, scroll, composer height) is its own
isolated module that composes with the others. This means:

- Keyboard awareness is a modifier/hook, not baked into the scroll view
- Animation sequencing is a modifier/hook, not baked into message rendering
- Composer height tracking is a modifier/hook, not baked into layout
- Blank size calculation is a modifier/hook, not baked into the list

This composability is what lets you iterate on one behavior without breaking the
others.

---

### 1.2 Message Animation Sequencing

**The pattern:** When the user sends a message in a new chat:

1. User message fades in and slides up (spring animation, ~300-400ms)
2. Completion callback fires when user message animation finishes
3. Assistant message fades in (ease-out, ~350ms)
4. Streaming content begins with staggered word fade

**Critical details:**

- Animations only trigger on send (`isMessageSendAnimating` flag), not on chat
  re-open. Without this guard, reopening a chat would replay animations.
- The flag is set `true` on submit, set `false` when user message animation
  completes. Assistant message watches for this transition.
- For existing chats (not new), skip the send animation entirely — use
  `scrollToEnd()` instead.
- Phase-based animation is cleaner than timeline-based: define states
  (hidden → appearing → visible) with their opacity/offset/scale values, then
  transition between phases.

**What breaks if you get this wrong:** Messages appear instantly (jarring),
animations replay when switching between chats, assistant message appears before
user message finishes animating, or animations stutter on low-end devices.

---

### 1.3 The Blank Size Problem

This is the hardest universal problem in chat UI. Vercel's team spent enormous
effort on it.

**The problem:** When you send a message, it should scroll to the top of the
visible area — like iMessage. But by default, new messages appear at the bottom
of the scroll view. You need to push them up.

**The "blank size"** is the distance between the bottom of the last assistant
message and the end of the visible chat area. It's what pushes content to the top.

**Why it's hard:**

- Blank size is dynamic — it depends on keyboard state, composer height, and
  content height
- Assistant messages stream in, changing height on every frame
- When the assistant message gets long enough, blank size reaches zero — new
  edge cases appear
- The keyboard opening/closing changes the visible area, which changes blank size

**What Vercel tried and failed:**

1. **View at bottom of ScrollView** — Strange side effects with layout
2. **Bottom padding on ScrollView** — Poor performance, jitter from frequent
   layout recalculation
3. **TranslateY on content** — Side effects, broke scroll behavior
4. **Minimum height on last message** — Broke layout for long messages

**What works:** Content inset (padding inside the scroll view's content area,
not on the view itself) combined with `scrollToEnd({ offset })`. Content inset
maps to the native scroll view's inset property and performs well because it
doesn't trigger layout recalculation.

**The formula:**

```
blankSize = max(0, visibleHeight - contentHeight)
visibleHeight = containerHeight - keyboardHeight - composerHeight
contentHeight = lastUserMessageHeight + lastAssistantMessageHeight
```

**The scroll-to-end reality:** Due to dynamic heights and streaming content,
you'll likely need to call `scrollToEnd` multiple times. Vercel calls it with
`requestAnimationFrame` and `setTimeout` stacked — they acknowledge it looks
ugly but it was the only reliable approach. In SwiftUI, `.defaultScrollAnchor(.bottom)`
helps but doesn't fully solve streaming content updates.

---

### 1.4 Keyboard Management

**The 6 behaviors your keyboard system must handle:**

1. **Shrink blank size** when keyboard opens (blank size absorbs keyboard height)
2. **Shift content up** when keyboard opens AND you're scrolled to end AND
   there's no blank size to absorb
3. **Don't shift content** when keyboard opens AND you've scrolled up high
   enough — let keyboard overlay content
4. **Interactive dismissal** — dragging the keyboard down via scroll gesture
   should feel smooth and continuous
5. **Content stays in place** when scrolled to end AND blank size > keyboard
   height — the blank size absorbs the keyboard
6. **Shift content up** when scrolled to end AND blank size > 0 but < keyboard
   height — partial absorption

**Production edge cases:**

- **iOS triple-fire bug:** When app goes to background with keyboard open and
  returns, iOS fires `keyboardWillHide` three times. You need event deduplication
  and app state tracking.
- **iOS beta breakage:** Vercel reported that every iOS beta release broke their
  keyboard handling. Budget time for this.
- **Interactive dismissal timing:** The animation curve for keyboard
  opening/closing should use spring physics (stiffness ~500, damping ~45) to
  match native feel.
- **Composer height changes:** When the user types new lines and the composer
  grows, scroll to end ONLY if already at bottom. If scrolled up, don't move.

**Vercel's `useKeyboardAwareMessageList` was ~1,000 lines with unit tests.**
Don't underestimate keyboard handling — it's where most chat UIs feel "off."

---

### 1.5 Floating Composer

**The pattern:** Composer is absolutely positioned at the bottom, floats above
content, sticks above keyboard, with progressive blur/glass behind it.

**Progressive blur implementation:** In SwiftUI, use `.scrollEdgeEffectStyle(.soft, for: .bottom)`
on the `ScrollView` for the progressive blur behind the composer — this is the native API,
not a custom blur overlay. For the composer bar itself, use `.safeAreaBar(edge: .bottom)` (iOS 26+)
which automatically extends the scroll edge effect into the bar area. See `swiftui-core.md`
Section 3 → Scroll Edge Effects for full API reference. **Do NOT hand-roll progressive blur
with `UIVisualEffectView`, gradient masks, or `CIGaussianBlur` — the system API handles this.**

**Key behaviors:**

1. Composer sits at bottom with blur/glass background (`.glassEffect()` or `.ultraThinMaterial`)
2. When keyboard opens, composer rises above it (sticky)
3. Composer height is tracked and fed into content inset calculation
4. When user types new lines, composer grows and content scrolls up (only if at
   bottom)
5. Swipe-up gesture on text input opens keyboard (users expect this)

**The composer-scroll cascade:**

```
User types new line
  → Composer height increases
  → Content inset recalculated (composerHeight is part of the formula)
  → If scrolled to bottom: scrollToEnd() to keep content visible
  → If scrolled up: don't move (user is reading history)
```

**Swipe-up-to-focus:** Vercel added this after watching testers frustratingly
swipe up expecting the keyboard to open. Detect upward pan gesture
(velocity < -250, not already focused) → focus the text input.

**Pasting images:** Support paste events from the system clipboard. If pasted
text is long enough, auto-convert it to a `.txt` file attachment. This is a
small detail that makes the app feel complete.

---

### 1.6 Streaming Text with Animation Pool

**The problem:** When an AI streams a response, rendering every word instantly
looks jarring. But animating every word individually tanks performance.

**The pool pattern (from Vercel):**

- Maintain a pool of maximum **4 concurrent animations**
- Elements request to join the pool when they mount
- `isActive` indicates whether the element should render with animation
- After animation completes (~500ms), `evict()` removes from pool, renders
  children directly without animated wrapper
- This limits GPU/CPU load while maintaining visual smoothness

**Batching and scaling:**

- Stagger delay: **32ms** between elements
- Batch size: **2 items** at a time
- When queue exceeds **10 items** (fast streaming), increase batch size
  proportionally to prevent falling behind

**Text-specific pool:**

- Chunk text into individual words
- Create a separate pool for text elements with limit of **4 words animating
  at once**
- Each word fades in (opacity 0→1, duration 500ms)

**Seen-content tracking:**

- Track which content the user has already seen animate
- If user switches to another chat and comes back before streaming finishes,
  don't re-animate already-seen words
- Implement via a `DisableFadeProvider` at the message tree root
- Use `useState`'s initial value to capture mount-time state (whether fade
  should be enabled)

**Character streaming alternative:** Instead of word chunking, render characters
in batches of 3-5 at 16ms intervals. More fluid for short responses, but word
chunking is better for long-form AI output.

---

### 1.7 Markdown Rendering in Chat

**Requirements:**

- Fast rendering that keeps up with streaming (no lag behind token output)
- Inline code styling (monospace font, subtle background)
- Code blocks with language label and copy button
- Text selection support
- Streaming-aware: don't re-parse entire message on each token, only parse delta

**Code block UX:**

- Header showing language name + copy button
- Horizontal scroll for long lines (no wrapping)
- Copy button transitions: "Copy" → "Copied" with checkmark, resets after 2s
- Monospace font throughout

**The copy button feedback pattern:**

```
Tap copy → clipboard write → icon transitions (doc → checkmark)
  → label transitions ("Copy" → "Copied")
  → 2 second delay → transition back
```

---

### 1.8 Performance Principles

1. **Virtualized lists only.** Never render all messages at once. Use lazy
   loading that only renders visible items (LazyVStack, LegendList, FlatList,
   RecyclerView).

2. **Equatable/memo conformance.** Message views should implement equality
   checks so the framework knows to skip re-renders when message content hasn't
   changed.

3. **Animation state outside render.** Use shared values / animation state that
   updates without triggering re-renders. In React: Reanimated shared values.
   In SwiftUI: `@State` properties that drive `withAnimation` blocks.

4. **Debounced scroll operations.** When streaming causes rapid content size
   changes, debounce `scrollToEnd` calls to ~16ms (one frame). Multiple calls
   within a frame collapse into one.

5. **Batched height measurements.** Use preference keys / layout callbacks that
   batch multiple height measurements into a single update, rather than
   triggering layout per-message.

6. **Synchronous first measurement.** Get message height on first render, not
   after a layout pass. This prevents flash-of-wrong-layout.

7. **Pool concurrent animations.** Never animate more than 4 elements
   simultaneously. Use an actor/pool pattern to queue excess animations.

---

### 1.9 Shared API Architecture

Vercel's approach for sharing backend between web and mobile:

**Share types and helpers, not UI or state.** The mobile app is a thin wrapper
over the API. Business logic lives server-side.

**The API pattern:**

1. Define routes with runtime type safety (Zod schemas for input/output)
2. Generate OpenAPI spec from route definitions
3. Mobile client consumes OpenAPI spec to generate typed helpers
4. Use a query library (Tanstack Query, etc.) for caching and state

**Why this matters:** By making the mobile app a thin API client, you can:

- Ship mobile features by updating the API (no app update needed for logic)
- Share the same API with third-party developers
- Test business logic on the server, not in the client
- Keep the client focused purely on UI/UX delight

**Code sharing boundaries:**

| Share | Don't Share |
|-------|-------------|
| TypeScript/Swift types | UI components |
| API client helpers | State management |
| Validation schemas | Animation logic |
| Business logic (server) | Platform-specific gestures |

---

## Part 2: SwiftUI Implementation

Full code examples for iOS 17+ / iOS 26. Each section maps to a Part 1 concept.

---

### 2.1 Observable State Container + Composable Modifiers

```swift
import SwiftUI
import Observation

// MARK: - Observable State Container (replaces React context providers)
@Observable
final class ChatState {
    var messages: [ChatMessage] = []
    var composerHeight: CGFloat = 0
    var keyboardHeight: CGFloat = 0
    var isMessageSendAnimating: Bool = false
    var blankSize: CGFloat = 0

    var totalBottomInset: CGFloat {
        blankSize + composerHeight + keyboardHeight
    }
}

// MARK: - Message Model
struct ChatMessage: Identifiable, Equatable {
    let id: UUID
    let role: MessageRole
    var content: String
    var isStreaming: Bool = false
    let timestamp: Date

    enum MessageRole: Equatable {
        case user
        case assistant
        case optimisticPlaceholder
    }
}

// MARK: - Chat Container
struct ChatContainerView: View {
    @State private var chatState = ChatState()

    var body: some View {
        ChatMessagesView()
            .environment(chatState)
    }
}

// MARK: - Composable Modifiers (equivalent to RN hooks)
struct ChatMessagesView: View {
    @Environment(ChatState.self) private var state

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach(state.messages) { message in
                        MessageView(message: message)
                            .id(message.id)
                    }
                }
                .padding(.horizontal, 16)
            }
            .keyboardAwareScrolling(proxy: proxy)
            .initialScrollToEnd(proxy: proxy)
            .animateNewMessages()
        }
        .safeAreaInset(edge: .bottom) {
            FloatingComposer()
        }
    }
}
```

---

### 2.2 Message Animation Sequencing

```swift
// MARK: - Animation Phases
enum MessageAnimationPhase: CaseIterable {
    case hidden, appearing, visible

    var opacity: Double {
        switch self {
        case .hidden: 0
        case .appearing: 0.5
        case .visible: 1
        }
    }

    var offset: CGFloat {
        switch self {
        case .hidden: 50
        case .appearing: 10
        case .visible: 0
        }
    }

    var scale: CGFloat {
        switch self {
        case .hidden: 0.95
        case .appearing: 0.98
        case .visible: 1
        }
    }
}

// MARK: - User Message
struct UserMessageView: View {
    let message: ChatMessage
    let isFirstMessage: Bool
    @Environment(ChatState.self) private var state
    @State private var animationComplete = false

    var body: some View {
        HStack {
            Spacer()
            Text(message.content)
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(.blue, in: .rect(cornerRadius: 20))
                .foregroundStyle(.white)
        }
        .modifier(FirstMessageAnimationModifier(
            isEnabled: isFirstMessage && state.isMessageSendAnimating,
            onComplete: {
                animationComplete = true
                state.isMessageSendAnimating = false
            }
        ))
    }
}

// MARK: - First Message Animation Modifier
struct FirstMessageAnimationModifier: ViewModifier {
    let isEnabled: Bool
    let onComplete: () -> Void
    @State private var phase: MessageAnimationPhase = .hidden

    func body(content: Content) -> some View {
        content
            .opacity(isEnabled ? phase.opacity : 1)
            .offset(y: isEnabled ? phase.offset : 0)
            .scaleEffect(isEnabled ? phase.scale : 1)
            .onAppear {
                guard isEnabled else { return }
                withAnimation(.spring(duration: 0.3, bounce: 0.2)) {
                    phase = .appearing
                }
                withAnimation(.spring(duration: 0.4, bounce: 0.15).delay(0.2)) {
                    phase = .visible
                } completion: {
                    onComplete()
                }
            }
    }
}

// MARK: - Assistant Message (fades in after user message completes)
struct AssistantMessageView: View {
    let message: ChatMessage
    let isFirstAssistantMessage: Bool
    @Environment(ChatState.self) private var state
    @State private var isVisible = false

    var body: some View {
        HStack {
            StreamingTextView(text: message.content, isStreaming: message.isStreaming)
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(.secondary.opacity(0.1), in: .rect(cornerRadius: 20))
            Spacer()
        }
        .opacity(shouldAnimate ? (isVisible ? 1 : 0) : 1)
        .onChange(of: state.isMessageSendAnimating) { _, newValue in
            if !newValue && isFirstAssistantMessage {
                withAnimation(.easeOut(duration: 0.35)) {
                    isVisible = true
                }
            }
        }
        .onAppear {
            if !shouldAnimate { isVisible = true }
        }
    }

    private var shouldAnimate: Bool {
        isFirstAssistantMessage && !isVisible
    }
}
```

---

### 2.3 Blank Size + Scroll Position

```swift
// MARK: - Blank Size Calculator
struct BlankSizeCalculator {
    let containerHeight: CGFloat
    let keyboardHeight: CGFloat
    let lastUserMessageHeight: CGFloat
    let lastAssistantMessageHeight: CGFloat
    let composerHeight: CGFloat

    var blankSize: CGFloat {
        let visibleHeight = containerHeight - keyboardHeight - composerHeight
        let contentHeight = lastUserMessageHeight + lastAssistantMessageHeight
        return max(0, visibleHeight - contentHeight)
    }
}

// MARK: - Chat View with Dynamic Blank Size
struct ChatMessagesListView: View {
    @Environment(ChatState.self) private var state
    @State private var containerHeight: CGFloat = 0

    var body: some View {
        GeometryReader { geometry in
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(Array(state.messages.enumerated()),
                                id: \.element.id) { index, message in
                            MessageView(message: message)
                                .id(message.id)
                                .background(
                                    GeometryReader { messageGeo in
                                        Color.clear.preference(
                                            key: MessageHeightPreference.self,
                                            value: [message.id: messageGeo.size.height]
                                        )
                                    }
                                )
                        }
                    }
                    .padding(.horizontal, 16)
                }
                .contentMargins(.bottom, state.blankSize, for: .scrollContent)
                .safeAreaPadding(.bottom, state.composerHeight)
            }
            .onAppear { containerHeight = geometry.size.height }
        }
    }
}

// MARK: - Height Preference Key
struct MessageHeightPreference: PreferenceKey {
    static var defaultValue: [UUID: CGFloat] = [:]
    static func reduce(value: inout [UUID: CGFloat],
                       nextValue: () -> [UUID: CGFloat]) {
        value.merge(nextValue()) { $1 }
    }
}

// MARK: - Modern Scroll Position (iOS 17+)
struct ModernChatScrollView: View {
    @Environment(ChatState.self) private var state
    @State private var scrollPosition: ScrollPosition = .init()

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(state.messages) { message in
                    MessageView(message: message)
                        .id(message.id)
                }
            }
            .scrollTargetLayout()
        }
        .scrollPosition($scrollPosition)
        .contentMargins(.bottom, state.blankSize, for: .scrollContent)
        .defaultScrollAnchor(.bottom)  // iOS 18+
        .onChange(of: state.messages.count) { _, _ in
            if let lastMessage = state.messages.last {
                withAnimation(.spring(duration: 0.3)) {
                    scrollPosition.scrollTo(id: lastMessage.id, anchor: .top)
                }
            }
        }
    }
}
```

---

### 2.4 Keyboard Management

```swift
import Combine

// MARK: - Full Keyboard Observer
@Observable
final class KeyboardObserver {
    var height: CGFloat = 0
    var isVisible: Bool = false
    var animationDuration: TimeInterval = 0.25
    private var cancellables = Set<AnyCancellable>()

    init() { setupObservers() }

    private func setupObservers() {
        NotificationCenter.default.publisher(
            for: UIResponder.keyboardWillShowNotification
        )
        .sink { [weak self] in self?.handleShow($0) }
        .store(in: &cancellables)

        NotificationCenter.default.publisher(
            for: UIResponder.keyboardWillHideNotification
        )
        .sink { [weak self] _ in self?.handleHide() }
        .store(in: &cancellables)

        // iOS triple-fire bug: keyboard events fire 3x on app resume
        NotificationCenter.default.publisher(
            for: UIApplication.didBecomeActiveNotification
        )
        .debounce(for: .milliseconds(100), scheduler: RunLoop.main)
        .sink { [weak self] _ in self?.validateKeyboardState() }
        .store(in: &cancellables)
    }

    private func handleShow(_ notification: Notification) {
        guard let frame = notification.userInfo?[
            UIResponder.keyboardFrameEndUserInfoKey
        ] as? CGRect else { return }

        withAnimation(.interpolatingSpring(stiffness: 500, damping: 45)) {
            height = frame.height
            isVisible = true
        }
    }

    private func handleHide() {
        withAnimation(.interpolatingSpring(stiffness: 500, damping: 45)) {
            height = 0
            isVisible = false
        }
    }

    private func validateKeyboardState() {
        // Verify state matches reality after app resume
    }
}

// MARK: - Keyboard Aware Modifier
struct KeyboardAwareModifier: ViewModifier {
    @Environment(KeyboardObserver.self) private var keyboard
    @Environment(ChatState.self) private var state
    let scrollProxy: ScrollViewProxy
    let isScrolledToEnd: Bool

    func body(content: Content) -> some View {
        content
            .onChange(of: keyboard.height) { oldHeight, newHeight in
                let isOpening = newHeight > oldHeight
                if isOpening {
                    // Shrink blank size first (absorb keyboard)
                    let newBlank = max(0, state.blankSize - newHeight)
                    withAnimation(.interpolatingSpring(
                        stiffness: 500, damping: 45
                    )) {
                        state.blankSize = newBlank
                        state.keyboardHeight = newHeight
                    }
                    // Pin content above keyboard if scrolled to end
                    if isScrolledToEnd,
                       let last = state.messages.last {
                        withAnimation(.interpolatingSpring(
                            stiffness: 500, damping: 45
                        )) {
                            scrollProxy.scrollTo(last.id, anchor: .bottom)
                        }
                    }
                } else {
                    withAnimation(.interpolatingSpring(
                        stiffness: 500, damping: 45
                    )) {
                        state.keyboardHeight = 0
                    }
                }
            }
    }
}

// MARK: - Simplified iOS 26 (often sufficient)
struct SimplifiedChatView: View {
    @State private var messages: [ChatMessage] = []
    @FocusState private var isComposerFocused: Bool

    var body: some View {
        NavigationStack {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack {
                        ForEach(messages) { message in
                            MessageView(message: message).id(message.id)
                        }
                    }
                }
                .scrollDismissesKeyboard(.interactively)
                .defaultScrollAnchor(.bottom)
                .safeAreaInset(edge: .bottom) {
                    ComposerView()
                        .focused($isComposerFocused)
                }
            }
        }
    }
}
```

---

### 2.5 Floating Composer with Liquid Glass

```swift
// MARK: - Floating Composer
struct FloatingComposer: View {
    @Environment(ChatState.self) private var state
    @FocusState private var isFocused: Bool
    @State private var messageText = ""
    @Namespace private var composerNamespace

    var body: some View {
        GlassEffectContainer {
            HStack(spacing: 12) {
                Button {
                    // Handle attachments
                } label: {
                    Image(systemName: "plus.circle.fill")
                        .font(.title2)
                }
                .buttonStyle(.glass)
                .glassEffectID("attachButton", in: composerNamespace)

                TextField("Message", text: $messageText, axis: .vertical)
                    .lineLimit(1...6)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .glassEffect(.regular.interactive)
                    .focused($isFocused)

                Button { sendMessage() } label: {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title2)
                }
                .buttonStyle(.glassProminent)
                .tint(.blue)
                .disabled(messageText.isEmpty)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
        }
        .background(
            GeometryReader { geo in
                Color.clear.preference(
                    key: ComposerHeightPreference.self,
                    value: geo.size.height
                )
            }
        )
        .onPreferenceChange(ComposerHeightPreference.self) { height in
            state.composerHeight = height
        }
    }

    private func sendMessage() {
        guard !messageText.isEmpty else { return }
        let newMessage = ChatMessage(
            id: UUID(), role: .user,
            content: messageText, timestamp: Date()
        )
        state.isMessageSendAnimating = true
        state.messages.append(newMessage)
        messageText = ""

        // Optimistic placeholder
        let placeholder = ChatMessage(
            id: UUID(), role: .optimisticPlaceholder,
            content: "", timestamp: Date()
        )
        state.messages.append(placeholder)
    }
}

struct ComposerHeightPreference: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat,
                       nextValue: () -> CGFloat) { value = nextValue() }
}

// MARK: - Swipe to Focus (Vercel added after user testing)
struct SwipeToFocusModifier: ViewModifier {
    @FocusState.Binding var isFocused: Bool

    func body(content: Content) -> some View {
        content
            .gesture(
                DragGesture(minimumDistance: 20)
                    .onEnded { value in
                        if value.translation.height < -50
                            && value.velocity.height < -250
                            && !isFocused {
                            isFocused = true
                        }
                    }
            )
    }
}
```

---

### 2.6 Streaming Text with Animation Pool

```swift
// MARK: - Animation Pool (limits concurrent animations to 4)
actor AnimationPool {
    private var activeCount = 0
    private let maxConcurrent = 4
    private var waitingQueue: [CheckedContinuation<Void, Never>] = []

    func acquire() async {
        if activeCount < maxConcurrent {
            activeCount += 1
            return
        }
        await withCheckedContinuation { continuation in
            waitingQueue.append(continuation)
        }
        activeCount += 1
    }

    func release() {
        activeCount -= 1
        if let next = waitingQueue.first {
            waitingQueue.removeFirst()
            next.resume()
        }
    }
}

// MARK: - Streaming Text View
struct StreamingTextView: View {
    let text: String
    let isStreaming: Bool
    @State private var displayedText: String = ""
    @State private var wordQueue: [String] = []
    @State private var animatingCount = 0

    private let maxConcurrent = 4
    private let staggerDelay: TimeInterval = 0.032  // 32ms
    private let baseBatchSize = 2

    var body: some View {
        Text(displayedText)
            .onChange(of: text) { oldText, newText in
                guard isStreaming else {
                    displayedText = newText
                    return
                }
                let oldWords = oldText.split(separator: " ").map(String.init)
                let newWords = newText.split(separator: " ").map(String.init)
                let added = Array(newWords.dropFirst(oldWords.count))
                wordQueue.append(contentsOf: added)
                processQueue()
            }
            .onAppear {
                if !isStreaming { displayedText = text }
            }
    }

    private func processQueue() {
        guard animatingCount < maxConcurrent, !wordQueue.isEmpty else { return }

        // Scale batch size when queue > 10 (Vercel's approach)
        let batchSize = wordQueue.count > 10
            ? max(baseBatchSize, wordQueue.count / 5)
            : baseBatchSize

        let count = min(batchSize, wordQueue.count)
        for i in 0..<count {
            guard !wordQueue.isEmpty else { break }
            let word = wordQueue.removeFirst()
            animatingCount += 1

            DispatchQueue.main.asyncAfter(
                deadline: .now() + Double(i) * staggerDelay
            ) {
                withAnimation(.easeOut(duration: 0.5)) {
                    displayedText += (displayedText.isEmpty ? "" : " ") + word
                }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    animatingCount -= 1
                    processQueue()
                }
            }
        }
    }
}

// MARK: - Custom Text Renderer (iOS 26)
struct StreamingTextRenderer: TextRenderer {
    var progress: Double  // 0...1

    func draw(layout: Text.Layout, in context: inout GraphicsContext) {
        let total = layout.flatMap { $0 }.count
        let visible = Int(Double(total) * progress)
        var idx = 0

        for line in layout {
            for run in line {
                for glyph in run {
                    let show = idx < visible
                    let fade = idx < visible - 3
                        ? 1.0
                        : Double(visible - idx) / 3.0
                    context.opacity = show ? fade : 0
                    context.draw(glyph)
                    idx += 1
                }
            }
        }
    }
}
```

---

### 2.7 Markdown Rendering

```swift
// MARK: - Markdown Parser
struct MarkdownRenderer {
    static func render(_ markdown: String) -> AttributedString {
        do {
            var attributed = try AttributedString(
                markdown: markdown,
                options: .init(
                    allowsExtendedAttributes: true,
                    interpretedSyntax: .inlineOnlyPreservingWhitespace,
                    failurePolicy: .returnPartiallyParsedIfPossible
                )
            )
            // Style inline code
            for run in attributed.runs {
                if run.inlinePresentationIntent?.contains(.code) == true {
                    let range = run.range
                    attributed[range].backgroundColor = .secondary.opacity(0.1)
                    attributed[range].font = .system(.body, design: .monospaced)
                }
            }
            return attributed
        } catch {
            return AttributedString(markdown)
        }
    }
}

// MARK: - Code Block with Copy
struct CodeBlockView: View {
    let code: String
    let language: String?
    @State private var isCopied = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                Text(language ?? "code")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Spacer()
                Button {
                    UIPasteboard.general.string = code
                    withAnimation { isCopied = true }
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        withAnimation { isCopied = false }
                    }
                } label: {
                    Label(
                        isCopied ? "Copied" : "Copy",
                        systemImage: isCopied ? "checkmark" : "doc.on.doc"
                    )
                    .font(.caption)
                    .contentTransition(.symbolEffect(.replace))
                }
                .buttonStyle(.glass)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)

            ScrollView(.horizontal, showsIndicators: false) {
                Text(code)
                    .font(.system(.body, design: .monospaced))
                    .textSelection(.enabled)
                    .padding(12)
            }
        }
        .background(.quaternary.opacity(0.5), in: .rect(cornerRadius: 12))
    }
}
```

---

### 2.8 Typing Indicator

```swift
struct OptimisticPlaceholderView: View {
    @State private var dotIndex = 0

    var body: some View {
        HStack {
            HStack(spacing: 4) {
                ForEach(0..<3) { i in
                    Circle()
                        .fill(.secondary)
                        .frame(width: 8, height: 8)
                        .scaleEffect(dotIndex == i ? 1.2 : 0.8)
                        .animation(
                            .easeInOut(duration: 0.4)
                                .repeatForever()
                                .delay(Double(i) * 0.15),
                            value: dotIndex
                        )
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .glassEffect()
            Spacer()
        }
        .onAppear { dotIndex = 1 }
    }
}
```

---

### 2.9 Native Menus and Sheets (iOS 26)

```swift
// MARK: - Context Menu (Liquid Glass automatic in iOS 26)
struct MessageContextMenuView: View {
    let message: ChatMessage

    var body: some View {
        MessageBubble(message: message)
            .contextMenu {
                Button {
                    UIPasteboard.general.string = message.content
                } label: {
                    Label("Copy", systemImage: "doc.on.doc")
                }
                Button {
                    // Share
                } label: {
                    Label("Share", systemImage: "square.and.arrow.up")
                }
                Divider()
                Button(role: .destructive) {
                    // Delete
                } label: {
                    Label("Delete", systemImage: "trash")
                }
            }
    }
}

// MARK: - Sheet with Morphing Transition
struct ChatSettingsSheet: View {
    @Binding var isPresented: Bool
    @Namespace private var ns

    var body: some View {
        Button { isPresented = true } label: {
            Image(systemName: "gear")
        }
        .buttonStyle(.glass)
        .matchedTransitionSource(id: "settings", in: ns)
        .sheet(isPresented: $isPresented) {
            SettingsContentView()
                .presentationDetents([.medium, .large])
                .presentationDragIndicator(.visible)
                .navigationTransition(.zoom(sourceID: "settings", in: ns))
        }
    }
}
```

---

## Part 3: React Native Implementation

Full code examples using Expo + React Native. Maps to Part 1 concepts.

---

### 3.1 Composable Chat with Context Providers

```jsx
// Context providers replace SwiftUI's @Observable + Environment
export function ChatProvider({ children }) {
    return (
        <ComposerHeightProvider>
            <MessageListProvider>
                <NewMessageAnimationProvider>
                    <KeyboardStateProvider>
                        {children}
                    </KeyboardStateProvider>
                </NewMessageAnimationProvider>
            </MessageListProvider>
        </ComposerHeightProvider>
    )
}

// Message list with composable hooks
function MessagesList({ messages }) {
    useKeyboardAwareMessageList()
    useScrollMessageListFromComposerSizeUpdates()
    useUpdateLastMessageIndex()
    const { animatedProps, ref, onContentSizeChange, onScroll } =
        useMessageListProps()

    return (
        <AnimatedLegendList
            animatedProps={animatedProps}
            ref={ref}
            onContentSizeChange={onContentSizeChange}
            onScroll={onScroll}
            enableAverages={false}
            data={messages}
            keyExtractor={(item) => item.id}
            renderItem={({ item, index }) => {
                if (item.role === 'user')
                    return <UserMessage message={item} index={index} />
                if (item.role === 'assistant')
                    return <AssistantMessage message={item} index={index} />
                if (item.role === 'optimistic-placeholder')
                    return <OptimisticAssistantMessage index={index} />
            }}
        />
    )
}
```

---

### 3.2 Message Animation with Reanimated

```jsx
// Sending triggers animation flag (shared value = no re-renders)
const { isMessageSendAnimating } = useNewMessageAnimation()
const chatId = useChatId()

const onSubmit = () => {
    const isNewChat = !chatId
    if (isNewChat) {
        isMessageSendAnimating.set(true)
    }
    send()
}

// User message wraps in animated view
export function UserMessage({ message, index }) {
    const isFirstUserMessage = index === 0
    const { style, ref, onLayout } = useFirstMessageAnimation({
        disabled: !isFirstUserMessage,
    })
    return (
        <Animated.View style={style} ref={ref} onLayout={onLayout}>
            <UserMessageContent message={message} />
        </Animated.View>
    )
}

// The animation hook — measures, animates, signals completion
export function useFirstMessageAnimation({ disabled }) {
    const { keyboardHeight } = useKeyboardContextState()
    const { isMessageSendAnimating } = useNewMessageAnimation()
    const windowHeight = useWindowDimensions().height
    const translateY = useSharedValue(0)
    const progress = useSharedValue(-1)
    const { itemHeight, ref, onLayout } = useMessageRenderedHeight()

    useAnimatedReaction(
        () => {
            const didAnimate = progress.get() !== -1
            if (disabled || didAnimate || !isMessageSendAnimating.get())
                return -1
            return itemHeight.get()
        },
        (messageHeight) => {
            if (messageHeight <= 0) return

            const { start, end, duration, easing, config } =
                getAnimatedValues({
                    itemHeight: messageHeight,
                    windowHeight,
                    keyboardHeight: keyboardHeight.get(),
                })

            translateY.set(
                withTiming(start.translateY, { duration: 0 }, () => {
                    translateY.set(withSpring(end.translateY, config))
                })
            )
            progress.set(
                withTiming(start.progress, { duration: 0 }, () => {
                    progress.set(
                        withTiming(end.progress, { duration, easing }),
                        () => { isMessageSendAnimating.set(false) }
                    )
                })
            )
        }
    )

    const style = useAnimatedStyle(/* ... */)
    const didUserMessageAnimate = useDerivedValue(() => progress.get() === 1)
    return { style, ref, onLayout, didUserMessageAnimate }
}

// Assistant fades in after user animation completes
function AssistantMessage({ message, index }) {
    const isFirstAssistantMessage = index === 1
    const { didUserMessageAnimate } = useFirstMessageAnimation({
        disabled: !isFirstAssistantMessage,
    })

    const style = useAnimatedStyle(() => ({
        opacity: didUserMessageAnimate.get()
            ? withTiming(1, { duration: 350 })
            : 0,
    }))

    return (
        <Animated.View style={style}>
            <AssistantMessageContent message={message} />
        </Animated.View>
    )
}
```

---

### 3.3 Blank Size with contentInset

```jsx
// Assistant message measures itself for blank size
function AssistantMessage({ message, index }) {
    const { onLayout, ref } = useMessageBlankSize({ index })
    return (
        <Animated.View ref={ref} onLayout={onLayout}>
            <AssistantMessageContent message={message} />
        </Animated.View>
    )
}

// Blank size feeds into contentInset (native UIScrollView property)
export function MessagesList(props) {
    const { blankSize, composerHeight, keyboardHeight } =
        useMessageListContext()

    const animatedProps = useAnimatedProps(() => ({
        contentInset: {
            bottom:
                blankSize.get() +
                composerHeight.get() +
                keyboardHeight.get(),
        },
    }))

    return (
        <AnimatedLegendList {...props} animatedProps={animatedProps} />
    )
}
```

---

### 3.4 Keyboard Handling (~1000 lines in production)

```jsx
// Consumption is one line; internals are ~1000 lines
function MessagesList() {
    useKeyboardAwareMessageList()
    // ...rest of list
}

// Built on react-native-keyboard-controller hooks:
// - useKeyboardHandler (onStart, onEnd, onInteractive)
// - Multiple useAnimatedReaction calls for edge cases
// - App state change tracking for iOS triple-fire bug
// - Event deduplication

// What it handles:
// 1. Shrink blankSize when keyboard opens
// 2. Shift content up if scrolled to end + no blank size
// 3. Don't shift if scrolled up high enough
// 4. Interactive keyboard dismissal via scroll
// 5. Content stays if blankSize > keyboard height
// 6. Partial blank size absorption
```

---

### 3.5 Floating Composer with Liquid Glass

```jsx
function Composer() {
    const { composerHeight } = useComposerHeightContext()
    const { onLayout, ref } = useSyncLayoutHandler((layout) => {
        composerHeight.set(layout.height)
    })
    const insets = useInsets()

    return (
        <KeyboardStickyView
            style={{
                position: 'absolute', bottom: 0,
                left: 0, right: 0
            }}
            offset={{ closed: -insets.bottom, opened: -8 }}
        >
            <LiquidGlassContainerView spacing={8}>
                <LiquidGlassView interactive>
                    {/* Input */}
                </LiquidGlassView>
                <LiquidGlassView interactive>
                    {/* Send button */}
                </LiquidGlassView>
            </LiquidGlassContainerView>
        </KeyboardStickyView>
    )
}

// Scroll when composer height changes (user types new lines)
export function useScrollWhenComposerSizeUpdates() {
    const { listRef, scrollToEnd } = useMessageListContext()
    const { composerHeight } = useComposerHeightContext()

    const autoscrollToEnd = () => {
        const list = listRef.current
        if (!list) return
        const state = list.getState()
        const distanceFromEnd =
            state.contentLength - state.scroll - state.scrollLength
        if (distanceFromEnd < 0) {
            scrollToEnd({ animated: false })
            setTimeout(() => scrollToEnd({ animated: false }), 16)
        }
    }

    useAnimatedReaction(
        () => composerHeight.get(),
        (height, prevHeight) => {
            if (height > 0 && height !== prevHeight) {
                scheduleOnRN(autoscrollToEnd)
            }
        }
    )
}
```

---

### 3.6 TextInput Native Patch

Vercel patched `RCTUITextView.mm` to fix multiline TextInput:

```objc
// In RCTUITextView.mm - initWithFrame:
self.showsVerticalScrollIndicator = NO;
self.showsHorizontalScrollIndicator = NO;
self.bounces = NO;
self.alwaysBounceVertical = NO;
self.alwaysBounceHorizontal = NO;
self.keyboardDismissMode = UIScrollViewKeyboardDismissModeInteractive;
[self.panGestureRecognizer addTarget:self
                              action:@selector(_handlePanToFocus:)];

// Pan gesture to focus keyboard on swipe up
- (void)_handlePanToFocus:(UIPanGestureRecognizer *)g {
    if (self.isFirstResponder) { return; }
    if (g.state != UIGestureRecognizerStateBegan) { return; }
    CGPoint v = [g velocityInView:self];
    if (v.y < -250.0 && !self.isFirstResponder) {
        [self becomeFirstResponder];
    }
}
```

**What this fixes:** Ugly scroll indicators on multiline input, content bounce
when no overflow, no interactive keyboard dismissal, no swipe-up-to-focus.

---

### 3.7 Streaming Fade with Pool System

```jsx
// Pool pattern — limits concurrent animated elements
const useIsAnimatedInPool = createUsePool()

function FadeInStaggered({ children }) {
    const { isActive, evict } = useIsAnimatedInPool()
    return isActive
        ? <FadeIn onFadedIn={evict}>{children}</FadeIn>
        : children
}

// Staggered animation (32ms between items, batch of 2)
const useStaggeredAnimation = createUseStaggered(32)

function FadeIn({ children, onFadedIn, Component }) {
    const opacity = useSharedValue(0)

    const startAnimation = () => {
        opacity.set(withTiming(1, { duration: 500 }))
        setTimeout(onFadedIn, 500)
    }

    useStaggeredAnimation(startAnimation)

    return <Component style={{ opacity }}>{children}</Component>
}

// Text-specific: chunk into words, pool of 4
const useShouldTextFadePool = createUsePool(4)

function TextFadeInStaggeredIfStreaming(props) {
    const { isStreaming } = use(MessageContext)
    const { isActive } = useShouldTextFadePool()
    const isFadeDisabled = useDisableFadeContext()
    const [shouldFade] = useState(
        !isFadeDisabled && isActive && isStreaming
    )

    let { children } = props
    if (shouldFade && children) {
        if (typeof children === 'string') {
            children = <AnimatedFadeInText text={children} />
        }
    }
    return children
}

function AnimatedFadeInText({ text }) {
    const chunks = text.split(' ')
    return chunks.map((chunk, i) => (
        <TextFadeInStaggered key={i} text={chunk + ' '} />
    ))
}
```

---

### 3.8 Initial Scroll to End

```jsx
// The ugly truth: multiple scrollToEnd calls are needed
export function useInitialScrollToEnd(
    blankSize, scrollToEnd, hasMessages
) {
    const hasStartedScrolledToEnd = useSharedValue(false)
    const hasScrolledToEnd = useSharedValue(false)

    const scrollToEndJS = useLatestCallback(() => {
        scrollToEnd({ animated: false })
        requestAnimationFrame(() => {
            scrollToEnd({ animated: false })
            setTimeout(() => {
                scrollToEnd({ animated: false })
                requestAnimationFrame(() => {
                    hasScrolledToEnd.set(true)
                })
            }, 16)
        })
    })

    useAnimatedReaction(
        () => {
            if (hasStartedScrolledToEnd.get() || !hasMessages)
                return false
            return blankSize.get() > 0
        },
        (shouldScroll) => {
            if (shouldScroll) {
                hasStartedScrolledToEnd.set(true)
                scheduleOnRN(scrollToEndJS)
            }
        }
    )

    return hasScrolledToEnd
}
```

---

### 3.9 Shared API with Zod + OpenAPI

```typescript
// Server: Define routes with Zod types
import { z } from 'zod'

const ChatMessageSchema = z.object({
    id: z.string().uuid(),
    role: z.enum(['user', 'assistant']),
    content: z.string(),
    timestamp: z.string().datetime(),
})

const SendMessageInput = z.object({
    chatId: z.string().uuid().optional(),
    content: z.string().min(1),
    attachments: z.array(z.string().url()).optional(),
})

const SendMessageOutput = z.object({
    chatId: z.string().uuid(),
    message: ChatMessageSchema,
})

// Route definition with runtime type safety
export const sendMessage = createRoute({
    method: 'POST',
    path: '/api/chat/send',
    input: SendMessageInput,
    output: SendMessageOutput,
    handler: async (input) => {
        // Business logic lives here, not in the client
    },
})

// Generated OpenAPI spec → client helpers
// Mobile consumption with Tanstack Query:
import { chatSendOptions } from '@/api'  // generated
import { useMutation } from '@tanstack/react-query'

export function useSendMessage() {
    return useMutation(chatSendOptions())
}
```

---

## Part 4: Platform Comparison Table

| Concept | SwiftUI (iOS 17+) | React Native | Web / Other |
|---|---|---|---|
| State container | `@Observable` + `.environment()` | Context providers + hooks | Zustand / Jotai / signals |
| Animation values | `@State` + `withAnimation` | Reanimated shared values | CSS transitions / Framer Motion |
| Virtualized list | `LazyVStack` + `ScrollViewReader` | LegendList / FlatList | `react-window` / virtual scroller |
| Reactive effects | `.onChange(of:)` modifier | `useAnimatedReaction` | `useEffect` / signals |
| Content inset | `.contentMargins()` / `.safeAreaPadding()` | `contentInset` on UIScrollView | `padding-bottom` / scroll margin |
| Keyboard sticky | `.safeAreaInset(edge:)` | `KeyboardStickyView` | `position: sticky` + `visualViewport` |
| Glass/blur | Native `.glassEffect()` (iOS 26) | `@callstack/liquid-glass` | `backdrop-filter: blur()` |
| Context menus | Native `contextMenu` / `Menu` | Zeego + `react-native-ios-context-menu` | Custom dropdown / `<menu>` |
| Spring animation | `.spring(duration:bounce:)` | `withSpring(config)` | `spring()` in Framer Motion |
| Scroll anchor | `.defaultScrollAnchor(.bottom)` (iOS 18) | `scrollToEnd()` manual | `scroll-snap` / `scrollIntoView` |
| Keyboard dismiss | `.scrollDismissesKeyboard(.interactively)` | `keyboardDismissMode` patch | `visualViewport` resize event |
| Sheet transitions | `.navigationTransition(.zoom)` (iOS 18) | `presentationStyle="formSheet"` | Dialog API / `<dialog>` |
| Text rendering | `AttributedString` + `TextRenderer` | MDX + `<FadeInStaggered>` | DOM manipulation / `IntersectionObserver` |
| Height measurement | `GeometryReader` + `PreferenceKey` | `ref.current.measure()` (sync) | `ResizeObserver` / `getBoundingClientRect` |

---

## Part 5: Review Checklist

Use this checklist when reviewing any chat UI implementation.

### Animation
- [ ] User message animates in before assistant message appears
- [ ] Completion callback connects user → assistant animation sequence
- [ ] Animations only fire on new message send, not on chat re-open
- [ ] Switching between chats doesn't replay animations
- [ ] Seen-content tracking prevents re-animation of streamed text
- [ ] No more than 4 elements animate simultaneously (pool pattern)
- [ ] Batch size scales when stream queue exceeds 10 items

### Blank Size
- [ ] New messages scroll to top of visible area, not bottom
- [ ] Blank size recalculates when keyboard opens/closes
- [ ] Blank size recalculates when assistant message streams (dynamic height)
- [ ] Blank size reaches zero gracefully for long messages
- [ ] Content inset used (not padding/margin) for blank size

### Keyboard
- [ ] Interactive keyboard dismissal via scroll gesture
- [ ] Spring animation on keyboard open/close (stiffness ~500, damping ~45)
- [ ] Content shifts up only when scrolled to end
- [ ] Content stays when scrolled up (keyboard overlays)
- [ ] App resume doesn't cause jitter (dedup keyboard events)
- [ ] Blank size absorbs keyboard height before shifting content

### Composer
- [ ] Floats above content with blur/glass
- [ ] Sticks above keyboard
- [ ] Height changes cascade to scroll position (only when at bottom)
- [ ] Swipe-up gesture focuses text input
- [ ] Supports image/file paste
- [ ] Multiline input grows without scroll indicators or bounce

### Streaming
- [ ] Text fades in word-by-word with stagger (32ms between batches)
- [ ] Maximum 4 words animate at once
- [ ] Queue scaling when stream is fast (batch size increases)
- [ ] Already-seen content renders immediately (no re-animation)
- [ ] Markdown renders incrementally (no full re-parse per token)
- [ ] Code blocks have copy button with feedback animation

### Performance
- [ ] Virtualized list (only visible messages rendered)
- [ ] Message views implement equality/memo checks
- [ ] Animation state updates don't trigger re-renders
- [ ] Scroll operations debounced to ~16ms
- [ ] Height measurements batched
- [ ] No layout thrashing during streaming

### Platform (iOS specific)
- [ ] Liquid Glass follows Apple guidelines (no glass-on-glass)
- [ ] Context menus use native system menus
- [ ] Sheets use morphing transitions where appropriate
- [ ] `.scrollDismissesKeyboard(.interactively)` enabled
- [ ] `.defaultScrollAnchor(.bottom)` for initial scroll position

---

## Common Mistakes

- ❌ Not virtualizing long message lists — renders all messages, kills performance on 100+ messages
- ❌ Animating messages on every chat re-open — causes replay animations. Use `isMessageSendAnimating` flag to trigger only on send.
- ❌ Hard-coding blank size — dynamic based on keyboard state, composer height, content height. Recalculate on layout changes.
- ❌ Streaming assistant messages without rate limiting — concurrent word animations cause jank. Use animation pool (max 4 words).
- ❌ Re-parsing all markdown on every token — expensive operation. Parse incrementally as tokens arrive.
- ❌ Handling keyboard without interactive dismissal — feels non-native. Use `.scrollDismissesKeyboard(.interactively)` on iOS 16+.
- ❌ Floating composer without blur/glass effect — looks flat, breaks immersion. Use Liquid Glass pattern (iOS 18+).

---

## Review Checklist

### Message Flow
- [ ] New user messages animate in smoothly (spring, ~300-400ms)
- [ ] User message completion callback fires before assistant message appears
- [ ] Assistant messages fade in with staggered streaming animation
- [ ] Opening existing chats scrolls to end WITHOUT animation replay
- [ ] Animation flag (`isMessageSendAnimating`) prevents replay on chat re-open

### Scroll Behavior
- [ ] User messages scroll to top of visible area (not bottom)
- [ ] Blank size (distance to bottom) calculated dynamically
- [ ] Blank size recalculates when keyboard state, composer, or content changes
- [ ] Scroll position synced with blank size changes
- [ ] Scrolling up doesn't shift keyboard away

### Composer
- [ ] Floats above content with Liquid Glass blur (iOS 18+) or semi-transparent background
- [ ] Sticks above keyboard even during interactive dismissal
- [ ] Height changes cascade to scroll position (only when at bottom)
- [ ] Swipe-up gesture focuses text input
- [ ] Supports image/file paste from Photos, Files, clipboard
- [ ] Multiline input grows without horizontal scroll indicators

### Streaming
- [ ] Text fades in word-by-word (32ms stagger between batches)
- [ ] Animation pool limits concurrent animations (max 4 words)
- [ ] Already-seen content renders immediately (no re-animation)
- [ ] Markdown parsed incrementally (not full re-parse per token)
- [ ] Code blocks include copy button with haptic feedback
- [ ] Stream updates don't cause layout thrashing

### Performance
- [ ] Message list virtualized (only visible messages rendered)
- [ ] Message views implement equality checks or memo optimization
- [ ] Animation state updates don't trigger re-renders
- [ ] Scroll operations debounced (~16ms)
- [ ] Height measurements batched
- [ ] Keyboard transitions smooth without jitter

### Platform (iOS)
- [ ] Interactive keyboard dismissal enabled (`.scrollDismissesKeyboard(.interactively)`)
- [ ] Liquid Glass follows Apple guidelines (no glass-on-glass stacking)
- [ ] Context menus use native system menus
- [ ] Sheets use morphing transitions where appropriate
- [ ] Initial scroll position set to bottom (`.defaultScrollAnchor(.bottom)`)
- [ ] Content insets adjust for safe areas and keyboard

---

## Resources

- [How we built the v0 iOS app](https://vercel.com/blog/how-we-built-the-v0-ios-app) — Vercel engineering blog
- [V0Swift](https://github.com/krispuckett/V0Swift) — SwiftUI translation by krispuckett
- [WWDC 2025 - Build a SwiftUI app with the new design](https://developer.apple.com/videos/play/wwdc2025/)
- [WWDC 2025 - Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/)
- [LegendList](https://github.com/LegendApp/legend-list) — Virtualized list for React Native
- [react-native-keyboard-controller](https://github.com/kirillzyusko/react-native-keyboard-controller)
- [react-native-reanimated](https://docs.swmansion.com/react-native-reanimated/)

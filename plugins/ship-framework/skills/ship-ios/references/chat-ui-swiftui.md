<!-- ship-reference
id: chat-ui-swiftui
kind: mixed
sources: iPhoneOS27.0.sdk (the sketch in §4 type-checks via scripts/checks/ios.sh — API names and types only, not behavior); https://developer.apple.com/documentation/swiftui/scrollposition (2026-09-23); v0swift@778a0c0 (krispuckett/V0Swift, MIT — ideas only, no text); https://vercel.com/blog/how-we-built-the-v0-ios-app (2026-09-23, ideas only)
reviewed: 2026-09-23
-->
# Chat and AI-assistant screens in SwiftUI

Chat screens fail in the same places on every platform: where a new message lands, the keyboard,
the composer, and streaming text. These are Ship's decision rules for SwiftUI. Timing and spring
values belong to the motion skill (`${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/SKILL.md`); colors, type, and
spacing come from the registry.

## 1. Structure

- Messages in `ScrollView` + `LazyVStack` with `.scrollTargetLayout()`; each message is an
  `@Observable` model with a stable `id`, so a streaming reply updates only its own row.
- The composer lives in `.safeAreaInset(edge: .bottom)` — or `.safeAreaBar(edge: .bottom)` on
  iOS 26+, which also carries the scroll edge effect under the bar. Never overlay it with a
  `ZStack` and manual padding.
- Keep the conversation logic (send, stream, retry, cancel) in a model the view calls; the view
  only lays out.

## 2. Where messages land

- Opening a conversation: start at the latest message (`.defaultScrollAnchor(.bottom)`, 17+).
- Sending: scroll the new user message to the **top** of the viewport (`ScrollPosition` +
  `scrollTo(id:anchor: .top)`, 18+) so the reply has room to stream beneath it.
- That needs empty space below a short exchange. Reserve it with bottom content margin
  (`.contentMargins(.bottom, …, for: .scrollContent)`), sized to the viewport minus the height of
  the latest exchange, and shrink it to zero as the reply grows. Don't fake it with a spacer view
  or a minimum row height — both break long messages.
- While a reply streams, follow it only if the reader is at the bottom; if they scrolled up to
  read history, don't move them. Track "near bottom" with `.onScrollGeometryChange` (18+).

## 3. Keyboard and composer

- `.scrollDismissesKeyboard(.interactively)` on the message list; `@FocusState` on the composer.
- Composer grows with its text: `TextField(…, axis: .vertical).lineLimit(1...6)`; when it grows
  and the reader is at the bottom, keep the last message visible; otherwise leave the scroll alone.
- Send is disabled for empty drafts; while a reply streams, Send becomes Stop (cancel the task).
- Test: keyboard open/close at the bottom and scrolled up, rotation, iPad split view, hardware
  keyboard (Return sends, Shift-Return adds a line — **Ship default**, confirm per product).

## 4. Streaming and rendering

- Append tokens to one message model; coalesce UI updates (flush a batch per frame or two) instead
  of mutating state per token.
- Don't re-parse the whole message per token. Inline Markdown: `AttributedString(markdown:)` on
  finished paragraphs; code blocks: monospace, horizontal scroll, a Copy button with confirmation.
- New messages animate in only when sent, never when a chat reopens; streamed words may fade in,
  but cap how many fade at once (Vercel reported 4) and skip it under Reduce Motion (fade only).
- When a reply finishes, announce it for VoiceOver
  (`AccessibilityNotification.Announcement(…).post()`, 17+) — not per token.
- Errors stay in the thread next to the failed message, with Retry.
- **Waiting state:** before the first token, show a typing indicator in the reply's own row (so it
  becomes the reply, no layout jump); give it an accessibility label ("Assistant is replying") and
  make it static under Reduce Motion.
- **Message actions:** `.contextMenu` on each message — Copy, Share (`ShareLink`), and for
  assistant replies Regenerate; the same actions reachable by VoiceOver (`.accessibilityActions`).
  Long replies: `.textSelection(.enabled)` so people can copy part of a message.
- On-device generation (Foundation Models) and its unavailable states: `intelligence.md` §2.

**Structural sketch — not the behavior above.** It shows where the pieces go (lazy list with ids,
scroll position, bottom anchor, composer inset). It compiles; compiling checks API names and
types, not behavior, and it has not been run on a simulator. It **omits**: the bottom
`.contentMargins` reservation (so a short exchange can't put the new message at the top), any use
of `readerAtBottom` (streaming-follow isn't implemented), streaming and Stop, `@FocusState`,
the reply's VoiceOver announcement, and Retry. `scrollTo` right after `append` may run before the
new row is laid out — untested. Build those from §2–§4 and check them on a device or simulator:
a short exchange, a long streamed reply, the reader scrolled up, and the keyboard opening/closing.

```swift
@Observable final class ChatMessage: Identifiable {
    enum Role { case user, assistant }
    let id = UUID()
    let role: Role
    var text: String
    init(role: Role, text: String) { self.role = role; self.text = text }
}

@available(iOS 18.0, *)
struct ChatScreen: View {
    @State private var messages: [ChatMessage] = []
    @State private var draft = ""
    @State private var position = ScrollPosition(idType: UUID.self)
    @State private var readerAtBottom = true   // tracked, not yet used: streaming-follow omitted

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: Theme.Spacing.sm) {
                ForEach(messages) { message in Text(message.text).id(message.id) }
            }
            .scrollTargetLayout()
        }
        .scrollPosition($position)
        .defaultScrollAnchor(.bottom)
        .scrollDismissesKeyboard(.interactively)
        .onScrollGeometryChange(for: Bool.self) { geo in
            geo.contentOffset.y + geo.containerSize.height >= geo.contentSize.height - 40
        } action: { _, atBottom in readerAtBottom = atBottom }
        .safeAreaInset(edge: .bottom) {
            HStack {
                TextField("Message", text: $draft, axis: .vertical).lineLimit(1...6)
                Button("Send", systemImage: "arrow.up.circle.fill", action: send)
                    .labelStyle(.iconOnly)
                    .disabled(draft.isEmpty)
            }
            .padding(Theme.Spacing.md)
        }
    }

    private func send() {
        let message = ChatMessage(role: .user, text: draft)
        messages.append(message)
        draft = ""
        position.scrollTo(id: message.id, anchor: .top)   // needs the bottom margin reservation (omitted); animation: motion skill
    }
}
```

## 5. Review checklist (check on a simulator or device — the sketch above doesn't satisfy it)

- [ ] New user message lands at the top; reply streams below it
- [ ] Reader scrolled up is never yanked down by streaming
- [ ] Composer in a safe-area inset/bar; grows to a line limit; Stop while streaming
- [ ] Keyboard dismisses interactively; nothing hidden behind it
- [ ] Rows have stable ids; a streaming reply re-renders only its own row
- [ ] Send animation doesn't replay on reopen; Reduce Motion drops movement
- [ ] Completed replies announced to VoiceOver; failures show Retry in place
- [ ] Typing indicator lives in the reply row; message actions (Copy/Share/Regenerate) in a context menu and for VoiceOver
- [ ] Liquid Glass on the composer only if the design model says so (gated, iOS 26+)

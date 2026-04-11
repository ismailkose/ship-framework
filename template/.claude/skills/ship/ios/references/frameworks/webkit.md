# SwiftUI WebKit — iOS Reference

> **When to read:** Dev reads this when building iOS 26+ article/detail views, help centers, in-app documentation, or other embedded web experiences backed by HTML, CSS, and JavaScript.

> **Cross-reference:** For SwiftUI WebView integration (iOS 26+), see `swiftui-core.md` Section 8.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `WebView` | SwiftUI view for web content | Simple form: `WebView(url:)`; advanced: `WebView(page)` |
| `WebPage` | Observable state machine | `@MainActor`-isolated; tracks loading, navigation, state |
| `URLRequest` | HTTP request configuration | Headers, method, caching policy, timeout |
| `WebPage.NavigationDeciding` | Intercept and decide navigations | Allow, cancel, or customize based on URL/response |
| `WebPage.NavigationAction` | Navigation details | Request, type (linkActivated, formSubmitted, etc.) |
| `.callJavaScript()` | Execute JS from Swift | Returns `Any`; cast to expected type |
| `WebPage.Configuration` | Custom schemes, preferences | Register `URLSchemeHandler` for custom schemes |
| `URLScheme` | Custom protocol handler | Create `URLSchemeHandler` for bundled content |

## Code Examples

### 1. Simple Web View from URL

```swift
import SwiftUI
import WebKit

struct ArticleView: View {
    let url: URL

    var body: some View {
        WebView(url: url)
    }
}
```

### 2. WebPage with Observable State

```swift
@Observable
@MainActor
final class ArticleModel {
    let page = WebPage()

    func load(_ url: URL) async throws {
        for try await _ in page.load(URLRequest(url: url)) {
        }
    }
}

struct ArticleDetailView: View {
    @State private var model = ArticleModel()
    let url: URL

    var body: some View {
        WebView(model.page)
            .task {
                try? await model.load(url)
            }
    }
}
```

### 3. Web View with Navigation Title and Progress

```swift
struct ReaderView: View {
    @State private var page = WebPage()

    var body: some View {
        WebView(page)
            .navigationTitle(page.title ?? "Loading")
            .overlay {
                if page.isLoading {
                    ProgressView(value: page.estimatedProgress)
                }
            }
            .task {
                do {
                    for try await _ in page.load(
                        URLRequest(url: URL(string: "https://example.com")!)
                    ) {
                    }
                } catch {
                    // Handle load failure
                }
            }
    }
}
```

### 4. Observe Navigation Events

```swift
Task {
    for await event in page.navigations {
        // Handle finish, redirect, or failure events
        switch event {
        case .finished:
            print("Navigation finished")
        case .redirected:
            print("Navigation redirected")
        case .failed(let error):
            print("Navigation failed: \(error)")
        @unknown default:
            break
        }
    }
}
```

### 5. Navigation Policy: Keep Internal, Open External

```swift
@MainActor
final class ArticleNavigationDecider: WebPage.NavigationDeciding {
    var urlToOpenExternally: URL?

    func decidePolicy(
        for action: WebPage.NavigationAction,
        preferences: inout WebPage.NavigationPreferences
    ) async -> WKNavigationActionPolicy {
        guard let url = action.request.url else { return .allow }

        if url.host == "example.com" {
            return .allow
        }

        urlToOpenExternally = url
        return .cancel
    }
}
```

### 6. Load Local HTML

```swift
let htmlString = """
    <html>
        <body>
            <h1>Welcome</h1>
            <p>This is local content.</p>
        </body>
    </html>
    """

for try await _ in page.load(html: htmlString, baseURL: nil) {
}
```

### 7. Load Data with MIME Type

```swift
let data = "Local PDF content".data(using: .utf8)!

for try await _ in page.load(data, mimeType: "application/pdf", characterEncoding: "utf-8", baseURL: nil) {
}
```

### 8. Custom URL Scheme Handler

```swift
var configuration = WebPage.Configuration()
configuration.urlSchemeHandlers[URLScheme("docs")!] = DocsSchemeHandler(bundle: .main)

let page = WebPage(configuration: configuration)
for try await _ in page.load(URL(string: "docs://article/welcome")!) {
}
```

### 9. Call JavaScript Function

```swift
let script = """
const headings = [...document.querySelectorAll('h1, h2')];
return headings.map(node => ({
    id: node.id,
    text: node.textContent?.trim()
}));
"""

let result = try await page.callJavaScript(script)
let headings = result as? [[String: Any]] ?? []
```

### 10. Call JavaScript with Arguments

```swift
let result = try await page.callJavaScript(
    "return document.getElementById(sectionID)?.getBoundingClientRect().top ?? null;",
    arguments: ["sectionID": selectedSectionID]
)
```

### 11. Enable Back/Forward Gestures

```swift
WebView(page)
    .webViewBackForwardNavigationGestures(true)
```

### 12. Enable Find in Page

```swift
@State private var isFindPresented = false

WebView(page)
    .findNavigator(isPresented: $isFindPresented)
```

### 13. Sync Scroll Position

```swift
@State private var scrollPosition: CGPoint = .zero

WebView(page)
    .webViewScrollPosition($scrollPosition)
```

### 14. Scroll Geometry Change

```swift
WebView(page)
    .webViewOnScrollGeometryChange { geometry in
        print("Scroll offset: \(geometry.contentOffset)")
    }
```

### 15. Compare Against WKWebView

```swift
// WRONG: UIKit wrapper in iOS 26+ SwiftUI app
struct LegacyWebViewWrapper: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        WKWebView()
    }
    // ...
}

// CORRECT: Use native SwiftUI WebView
struct ModernWebView: View {
    var body: some View {
        WebView(url: url)
    }
}
```

### 16. OAuth Flow (Not Embedded Web View)

```swift
// WRONG: Embedded web view for auth
struct LoginView: View {
    var body: some View {
        WebView(url: oauthURL)
    }
}

// CORRECT: Use ASWebAuthenticationSession
import AuthenticationServices

var body: some View {
    Button("Login with OAuth") {
        let session = ASWebAuthenticationSession(
            url: oauthURL,
            callbackURLScheme: "myapp",
            completionHandler: { url, error in
                // Handle callback
            }
        )
        session.presentationContextProvider = self
        session.start()
    }
}
```

### 17. Load HTML from Bundle

```swift
guard let htmlURL = Bundle.main.url(forResource: "index", withExtension: "html") else {
    return
}

for try await _ in page.load(URLRequest(url: htmlURL)) {
}
```

### 18. Access Back/Forward List

```swift
let backForwardList = page.backForwardList
print("Can go back: \(backForwardList.canGoBack)")
print("Can go forward: \(backForwardList.canGoForward)")
```

### 19. Defensive JavaScript Return Value Casting

```swift
let result = try await page.callJavaScript("return document.title;")
let title = result as? String ?? "Unknown"
```

### 20. Custom Navigation Preferences

```swift
@MainActor
final class CustomDecider: WebPage.NavigationDeciding {
    func decidePolicy(
        for action: WebPage.NavigationAction,
        preferences: inout WebPage.NavigationPreferences
    ) async -> WKNavigationActionPolicy {
        // Tune preferences if needed
        preferences.allowsBackForwardNavigationGestures = true
        return .allow
    }
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Use `WKWebView` wrapper by default in iOS 26+ SwiftUI | Start with `WebView` + `WebPage` for native integration |
| Use embedded web view for OAuth | Use `ASWebAuthenticationSession` instead |
| Forget `@MainActor` on `WebPage` model | Always mark `WebPage` and coordinator as `@MainActor` |
| Build a full browser app around WebView | Use WebView for focused embedded experience, not general browsing |
| Keep all external links inside the app | Intercept and open external domains with `openURL` |
| Use custom URL schemes for remote content | Prefer standard HTTPS for server-hosted pages |
| Treat `callJavaScript` as direct JS-to-native signaling | Use custom navigation policy or callback URLs for signal path |

## Review Checklist

- [ ] `WebView` and `WebPage` are the default path for iOS 26+ SwiftUI web content
- [ ] `ASWebAuthenticationSession` is used for auth flows instead of embedded web views
- [ ] `WebPage` is used whenever the app needs state observation, JS calls, or policy control
- [ ] Navigation policies only intercept the URLs the app actually owns or needs to reroute
- [ ] External domains open externally when appropriate
- [ ] JavaScript return values are cast defensively to concrete Swift types
- [ ] Custom URL schemes are used only for real app-owned resources
- [ ] Back/forward gestures or controls are enabled when multi-page browsing is expected
- [ ] The web experience adds focused native value instead of behaving like a thin browser shell
- [ ] Fallback to `WKWebView` is justified by deployment target or missing API needs

---

_Source: swift-ios-skills · Adapted for Ship Framework agent reference_

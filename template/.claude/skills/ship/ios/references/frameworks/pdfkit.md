# PDFKit Reference

> **When to read:** Dev reads when building PDF viewing or annotation features.
> Eye reads Common Mistakes and Review Checklist during review.

---

## Core Classes

```
PDFDocument → contains PDFPage objects
PDFView → displays PDFDocument with zoom, scroll, navigation
PDFPage → single page with text, annotations, thumbnails
PDFSelection → text selection within a page
PDFAnnotation → highlights, notes, signatures, forms
```

## Display and Navigation

```swift
import PDFKit

struct PDFViewer: UIViewRepresentable {
  let url: URL

  func makeUIView(context: Context) -> PDFView {
    let pdfView = PDFView()
    pdfView.document = PDFDocument(url: url)
    pdfView.autoScales = true
    pdfView.displayMode = .singlePageContinuous
    pdfView.displayDirection = .vertical
    return pdfView
  }

  func updateUIView(_ pdfView: PDFView, context: Context) {}
}
```

Page navigation:
```swift
pdfView.go(to: pdfView.document!.page(at: pageIndex)!)
pdfView.goToFirstPage(nil)
pdfView.goToLastPage(nil)
pdfView.goToNextPage(nil)
pdfView.goToPreviousPage(nil)
```

## Document Loading

```swift
// From URL
let document = PDFDocument(url: fileURL)

// From Data
let document = PDFDocument(data: pdfData)

// Page count
let pageCount = document?.pageCount ?? 0

// Thumbnail generation
if let page = document?.page(at: 0) {
  let thumbnail = page.thumbnail(of: CGSize(width: 100, height: 140), for: .cropBox)
}
```

## Text Operations

```swift
// Search
let selections = document?.findString("search term", withOptions: .caseInsensitive) ?? []
for selection in selections {
  selection.pages  // pages containing match
  selection.string // matched text
}

// Extract text from page
let pageText = document?.page(at: 0)?.string
```

## Annotations

```swift
// Highlight
let highlight = PDFAnnotation(bounds: selectionBounds, forType: .highlight, withProperties: nil)
highlight.color = .yellow.withAlphaComponent(0.5)
page.addAnnotation(highlight)

// Free text note
let note = PDFAnnotation(bounds: rect, forType: .freeText, withProperties: nil)
note.contents = "This is a note"
note.font = UIFont.systemFont(ofSize: 14)
page.addAnnotation(note)

// Remove annotation
page.removeAnnotation(annotation)
```

## SwiftUI Integration

```swift
struct PDFKitView: View {
  let document: PDFDocument
  @State private var currentPage = 0

  var body: some View {
    PDFViewWrapper(document: document, currentPage: $currentPage)
      .overlay(alignment: .bottom) {
        Text("Page \(currentPage + 1) of \(document.pageCount)")
          .padding()
          .background(.ultraThinMaterial)
      }
  }
}
```

## Common Mistakes
- ❌ Force unwrapping `PDFDocument(url:)` — returns nil for invalid/missing files
- ❌ Confusing coordinate systems — PDF uses bottom-left origin, UIKit uses top-left
- ❌ Not checking `pdfView.document?.isEqual(to:)` before updating — causes unnecessary reloads
- ❌ Creating thumbnails on main thread for large documents — use background queue
- ❌ Not setting `autoScales = true` — PDF may display at wrong zoom level

## Review Checklist
- [ ] PDF loading handles nil document gracefully
- [ ] Coordinate system conversions account for bottom-left origin
- [ ] Thumbnails generated on background thread
- [ ] Search results highlight correctly across pages
- [ ] Annotations persist (saved back to document or external storage)
- [ ] Memory handled for large multi-page documents

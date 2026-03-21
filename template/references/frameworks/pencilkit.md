# PencilKit — iOS Reference

> **When to read:** Dev reads this when implementing drawing, annotation, pressure-sensitive input, or sketch persistence features.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `PKCanvasView` | Main drawing canvas; captures pen/touch input automatically |
| `PKDrawing` | Immutable drawing data; serializable to Data |
| `PKToolPicker` | UI for tool selection (pen, marker, eraser, etc.) |
| `PKInkingTool` | Configurable pen tool with color and size |
| `PKEraserTool` | Eraser tool; two modes: raster (pixel) and vector (stroke) |
| `PKLassoTool` | Freeform selection tool |
| `PKToolPickerObserver` | Monitor tool picker visibility and selections |
| `PKContentVersion` | Enum for drawing format compatibility (v1, v2) |
| `PKStroke` | Individual stroke data (iOS 17.4+) |

**Key Properties:**
- `PKCanvasView.drawing` — Current drawing (get/set)
- `PKCanvasView.isOpaque` — Canvas transparency
- `PKCanvasView.delegate` — Responds to drawing changes
- `PKToolPicker.selectedTool` — Currently active tool

---

## Code Examples

**Example 1: Basic drawing canvas setup**
```swift
import PencilKit
import UIKit

class DrawingViewController: UIViewController, PKCanvasViewDelegate {
    @IBOutlet var canvasView: PKCanvasView!

    override func viewDidLoad() {
        super.viewDidLoad()

        // Setup canvas
        canvasView.delegate = self
        canvasView.isOpaque = false
        canvasView.backgroundColor = .white

        // Setup tool picker
        let toolPicker = PKToolPicker()
        toolPicker.addObserver(canvasView)
        toolPicker.setVisible(true, forFirstResponder: canvasView)
        canvasView.becomeFirstResponder()

        // Restore previous drawing if available
        if let savedData = UserDefaults.standard.data(forKey: "drawing") {
            canvasView.drawing = try? PKDrawing(data: savedData)
        }
    }

    // Delegate: drawing changed
    func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
        print("Drawing modified")
        // Auto-save or mark as dirty
    }
}
```

**Example 2: Save and load drawings**
```swift
import PencilKit

func saveDrawing(_ drawing: PKDrawing) {
    do {
        let data = try drawing.dataRepresentation()
        UserDefaults.standard.set(data, forKey: "myDrawing")
        print("Drawing saved, size: \(data.count) bytes")
    } catch {
        print("Save failed: \(error)")
    }
}

func loadDrawing() -> PKDrawing? {
    guard let data = UserDefaults.standard.data(forKey: "myDrawing") else { return nil }
    do {
        return try PKDrawing(data: data)
    } catch {
        print("Load failed: \(error)")
        return nil
    }
}

// For file-based storage (documents directory):
func saveToFile(_ drawing: PKDrawing, fileName: String) throws {
    let url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        .appendingPathComponent(fileName)
    try drawing.dataRepresentation().write(to: url)
}
```

**Example 3: Custom pen configuration and thumbnail**
```swift
import PencilKit

func customizeTools(_ toolPicker: PKToolPicker) {
    // Create custom ink tool
    let customPen = PKInkingTool(.pen, color: .blue, width: 5.0)

    // Create eraser
    let eraser = PKEraserTool(.vector)  // or .raster

    // Assign to tool picker
    toolPicker.selectedTool = customPen
}

func generateThumbnail(from drawing: PKDrawing) -> UIImage? {
    // Draw to CGContext for thumbnail
    let rect = CGRect(x: 0, y: 0, width: 100, height: 100)
    let renderer = UIGraphicsImageRenderer(size: rect.size)

    return renderer.image { context in
        UIColor.white.setFill()
        context.cgContext.fill(rect)

        // Scale drawing to fit thumbnail bounds
        let scale = min(rect.width / drawing.bounds.width,
                       rect.height / drawing.bounds.height)
        context.cgContext.scaleBy(x: scale, y: scale)
        drawing.draw(in: context.cgContext)
    }
}
```

---

## Common Mistakes

**Mistake 1: Not keeping PKToolPicker alive**
```swift
// ❌ WRONG: toolPicker deallocates after method returns
override func viewDidLoad() {
    super.viewDidLoad()
    let toolPicker = PKToolPicker()  // Lost reference
    toolPicker.setVisible(true, forFirstResponder: canvasView)
}

// ✅ CORRECT: Store as property
class DrawingVC: UIViewController {
    let toolPicker = PKToolPicker()
    override func viewDidLoad() {
        toolPicker.setVisible(true, forFirstResponder: canvasView)
    }
}
```

**Mistake 2: Forgetting to make canvas first responder**
```swift
// ❌ WRONG: Tool picker won't appear
toolPicker.setVisible(true, forFirstResponder: canvasView)
// canvasView never became first responder

// ✅ CORRECT: Call becomeFirstResponder()
canvasView.becomeFirstResponder()
toolPicker.setVisible(true, forFirstResponder: canvasView)
```

**Mistake 3: Saving drawing without error handling**
```swift
// ❌ WRONG: Silent failure on serialization error
let data = try? drawing.dataRepresentation()
UserDefaults.standard.set(data, forKey: "drawing")  // Nil if serialization fails

// ✅ CORRECT: Handle errors explicitly
do {
    let data = try drawing.dataRepresentation()
    UserDefaults.standard.set(data, forKey: "drawing")
} catch {
    print("Save failed: \(error)")
    // Show user alert
}
```

**Mistake 4: Not checking canvas bounds before thumbnail generation**
```swift
// ❌ WRONG: Crashes if drawing.bounds is empty
let scale = 100 / drawing.bounds.width  // Divide by zero

// ✅ CORRECT: Validate bounds
guard !drawing.bounds.isEmpty else {
    return UIImage()  // Return blank image
}
let scale = min(100 / drawing.bounds.width, 100 / drawing.bounds.height)
```

**Mistake 5: Ignoring tool picker observer lifecycle**
```swift
// ❌ WRONG: Observer never removed; memory leak
override func viewDidLoad() {
    let toolPicker = PKToolPicker()
    toolPicker.addObserver(canvasView)  // Never removed
}

// ✅ CORRECT: Remove observer in deinit or viewWillDisappear
deinit {
    toolPicker.removeObserver(canvasView)
}
// OR in viewWillDisappear:
override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    toolPicker.setVisible(false, forFirstResponder: canvasView)
}
```

---

## Review Checklist

- [ ] `PKCanvasView` created (via storyboard or programmatically)
- [ ] Canvas delegate (`PKCanvasViewDelegate`) implemented if tracking changes
- [ ] `PKToolPicker` stored as property (not local variable)
- [ ] `canvasView.becomeFirstResponder()` called before showing tool picker
- [ ] Tool picker observer added: `toolPicker.addObserver(canvasView)`
- [ ] Drawing saved via `drawing.dataRepresentation()` with error handling
- [ ] Drawing loaded via `PKDrawing(data:)` with error handling
- [ ] Custom tools (pen, eraser) configured if needed via `PKInkingTool`
- [ ] Thumbnail generation checks for empty bounds (`drawing.bounds.isEmpty`)
- [ ] Canvas background set appropriately (opaque vs. transparent)
- [ ] Tool picker removed from observers in `deinit` or lifecycle method
- [ ] File I/O permissions checked if saving to disk (not UserDefaults)

---

_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

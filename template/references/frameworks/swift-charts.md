# Swift Charts — iOS Reference

> **When to read:** Dev reads this when building bar, line, area, point, pie, or donut charts; when adding chart selection, scrolling, or annotations; when plotting functions with vectorized plots; or when customizing axes, scales, legends, or foregroundStyle grouping.

---

## Triage
- **Implement new feature** → Read Mark Types + Axis Customization
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `Chart` | Container for marks | Content closure init for multi-series; data-driven init for single series |
| `BarMark` | Vertical/horizontal bars | Stacks automatically with same x; use interval marks for Gantt |
| `LineMark` | Trend lines | Use `series:` parameter or `.foregroundStyle(by:)` for multi-line |
| `PointMark` | Scatter plots | Encode with `.symbol(by:)` for shape encoding |
| `AreaMark` | Filled areas | Supports stacked or range band rendering |
| `SectorMark` | Pie/donut slices (iOS 17+) | Limit to 5-7 sectors; group small values to "Other" |
| `RuleMark` | Threshold lines | Use for targets or baselines |
| `RectangleMark` | Heat maps | Encode with `.foregroundStyle(by:)` |
| `AxisMarks` | Axis configuration | Customize grid, ticks, labels with value strides |
| `chartXScale` / `chartYScale` | Scale domains | Set explicit domains for zero-baseline honesty |
| `BarPlot`, `LinePlot`, `AreaPlot`, `PointPlot` | Vectorized marks (iOS 18+) | Use for 1000+ data points |

## Code Examples

### 1. Basic Bar Chart

```swift
struct ChartView: View {
    let sales: [Sale]

    var body: some View {
        Chart(sales) { item in
            BarMark(x: .value("Month", item.month), y: .value("Revenue", item.revenue))
        }
    }
}
```

### 2. Multi-Series Bar Chart (Stacked)

```swift
Chart(data) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
        .foregroundStyle(by: .value("Product", item.product))
}
```

### 3. Multi-Series Line Chart

```swift
Chart {
    ForEach(allCities) { item in
        LineMark(x: .value("Date", item.date), y: .value("Temp", item.temp))
            .foregroundStyle(by: .value("City", item.city))
            .interpolationMethod(.catmullRom)
    }
}
```

### 4. Multi-Series with Explicit Series Parameter

```swift
Chart {
    ForEach(priceData) { item in
        LineMark(
            x: .value("Date", item.date),
            y: .value("Price", item.price),
            series: .value("Ticker", item.ticker)
        )
    }
}
```

### 5. Pie Chart

```swift
Chart(data, id: \.name) { item in
    SectorMark(angle: .value("Sales", item.sales))
        .foregroundStyle(by: .value("Category", item.name))
}
```

### 6. Donut Chart

```swift
Chart(data, id: \.name) { item in
    SectorMark(
        angle: .value("Sales", item.sales),
        innerRadius: .ratio(0.618),
        outerRadius: .inset(10),
        angularInset: 1
    )
    .cornerRadius(4)
    .foregroundStyle(by: .value("Category", item.name))
}
```

### 7. Chart with Custom Axes

```swift
Chart(sales) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
}
.chartXAxis {
    AxisMarks(values: .stride(by: .month)) { value in
        AxisGridLine()
        AxisTick()
        AxisValueLabel(format: .dateTime.month(.abbreviated))
    }
}
.chartYAxis {
    AxisMarks(values: .stride(by: 1000)) { value in
        AxisGridLine()
        AxisTick()
        AxisValueLabel()
    }
}
.chartXAxisLabel("Month", position: .bottom, alignment: .center)
.chartYAxisLabel("Revenue ($)", position: .leading, alignment: .center)
```

### 8. Explicit Scale Domain with Zero Baseline

```swift
Chart(data) {
    LineMark(x: .value("Day", $0.day), y: .value("Score", $0.score))
}
.chartYScale(domain: 0...100)
```

### 9. Logarithmic Scale

```swift
Chart(data) {
    BarMark(x: .value("Category", $0.category), y: .value("Value", $0.value))
}
.chartYScale(domain: 1...10000, type: .log)
```

### 10. Chart with Selection (iOS 17+)

```swift
@State private var selectedDate: Date?

Chart(data) { item in
    LineMark(x: .value("Date", item.date), y: .value("Value", item.value))
}
.chartXSelection(value: $selectedDate)
```

### 11. Range Selection

```swift
@State private var selectedRange: ClosedRange<Date>?

Chart(dailyData) { item in
    BarMark(x: .value("Date", item.date), y: .value("Steps", item.steps))
}
.chartXSelection(range: $selectedRange)
```

### 12. Scrollable Chart (iOS 17+)

```swift
Chart(dailyData) { item in
    BarMark(x: .value("Date", item.date, unit: .day), y: .value("Steps", item.steps))
}
.chartScrollableAxes(.horizontal)
.chartXVisibleDomain(length: 3600 * 24 * 7)  // 7 days visible
.chartScrollPosition(initialX: latestDate)
.chartScrollTargetBehavior(
    .valueAligned(matching: DateComponents(hour: 0), majorAlignment: .page)
)
```

### 13. Annotation

```swift
Chart(data) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
        .annotation(position: .top, alignment: .center, spacing: 4) {
            Text("\(item.sales, format: .number)").font(.caption2)
        }
}
```

### 14. Custom Legend

```swift
Chart(data) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
        .foregroundStyle(by: .value("Category", item.category))
}
.chartLegend(position: .bottom) {
    HStack(spacing: 16) {
        ForEach(categories, id: \.self) { cat in
            Label(cat, systemImage: "circle.fill").font(.caption)
        }
    }
}
```

### 15. Vectorized Plot for Large Datasets (iOS 18+)

```swift
Chart {
    BarPlot(sales, x: .value("Month", \.month), y: .value("Revenue", \.revenue))
        .foregroundStyle(\.barColor)
}
```

### 16. Function Plotting with LinePlot

```swift
Chart {
    LinePlot(x: "x", y: "y", domain: -5...5) { x in sin(x) }
}
```

### 17. Parametric Plot

```swift
Chart {
    LinePlot(x: "x", y: "y", t: "t", domain: 0...(2 * .pi)) { t in
        (x: cos(t), y: sin(t))
    }
}
```

### 18. Threshold Line

```swift
Chart {
    ForEach(data) { item in
        BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
    }
    RuleMark(y: .value("Target", 9000))
        .foregroundStyle(.red)
        .lineStyle(StrokeStyle(dash: [5, 3]))
        .annotation(position: .top, alignment: .leading) {
            Text("Target").font(.caption).foregroundStyle(.red)
        }
}
```

### 19. Accessibility Labels

```swift
Chart(data) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
        .accessibilityLabel("\(item.month)")
        .accessibilityValue("\(item.sales) units sold")
}
```

### 20. KeyPath Modifiers on Vectorized Plots

```swift
BarPlot(data, x: .value("X", \.x), y: .value("Y", \.y))
    .foregroundStyle(\.color)     // KeyPath first
    .opacity(0.8)                  // Value modifier second
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Missing series parameter on multi-line charts | Use `series:` parameter or `.foregroundStyle(by:)` to separate lines |
| Using `ObservableObject` instead of `@Observable` | Use `@Observable` with `@State` for SwiftUI 6 |
| No explicit scale domain when zero matters | Set `.chartYScale(domain: 0...100)` for honest representation |
| Static color overriding data encoding | Remove static `.foregroundStyle(.blue)` when using `.foregroundStyle(by:)` |
| Individual marks for 10,000+ points | Use vectorized plots (`BarPlot`, `LinePlot`, etc.) on iOS 18+ |
| Fixed chart height breaking Dynamic Type | Use `.frame(minHeight: 200, maxHeight: 400)` instead of fixed heights |
| Too many pie/donut slices | Limit to 5-7 sectors; group small values to "Other" |
| KeyPath modifier after value modifier on vectorized plots | Apply KeyPath modifiers first, then value modifiers |
| No accessibility labels | Add `.accessibilityLabel()` and `.accessibilityValue()` to marks |
| Missing axes when data needs context | Configure axes with `.chartXAxis` / `.chartYAxis` with labels |

## Review Checklist

- [ ] Data model uses `Identifiable` or chart uses `id:` key path
- [ ] Model uses `@Observable` with `@State`, not `ObservableObject`
- [ ] Mark type matches goal (bar=comparison, line=trend, sector=proportion)
- [ ] Multi-series lines use `series:` parameter or `.foregroundStyle(by:)`
- [ ] Axes configured with appropriate labels, ticks, and grid lines
- [ ] Scale domain set explicitly when zero-baseline matters
- [ ] Pie/donut limited to 5-7 sectors; small values grouped into "Other"
- [ ] Selection binding type matches axis data type (`Date?` for date axis)
- [ ] Scrollable charts set `.chartXVisibleDomain(length:)` for viewport
- [ ] Vectorized plots used for datasets exceeding 1000 points
- [ ] KeyPath modifiers applied before value modifiers on vectorized plots
- [ ] Accessibility labels added to marks for VoiceOver
- [ ] Chart tested with Dynamic Type and Dark Mode
- [ ] Legend visible and positioned, or intentionally hidden
- [ ] Ensure chart data model types are Sendable; update chart data on @MainActor

## 3D Charts (iOS 26+)

- **`Chart3D`** container for 3D visualizations.
- **`SurfacePlot`** for surface functions: `SurfacePlot(x: "X", y: "Y", z: "Z") { x, y in sin(x) * cos(y) }`
- **`Chart3DPose`** for camera positioning (azimuth, inclination).
- Camera projection: `.perspective`, `.orthographic`, `.automatic`.
- Surface coloring: height-based gradients or normal-based lighting.

---

_Source: swift-ios-skills · Adapted for Ship Framework agent reference_

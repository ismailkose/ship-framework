// Ship's gibberish test for any screenshot (macOS): finds every word with Vision and rebuilds it from
// random letter shapes of the same style on screen — the screen's own typeface, weight and colour — so
// nothing can be read but the style, layout, colour and imagery still show. Then ask someone who wasn't
// told the product what it sells.
//
//   swiftc -O gibberish.swift -o gibberish     (gibberish.py builds and caches this for you)
//   ./gibberish <in.png> <out.png> [seed]
//   ./gibberish --selftest                     renders words, scrambles them, checks OCR can't read them back
// Exit: 0 scrambled · 3 text recognition failed · 4 no words recognised (nothing scrambled; not a blind look)
import AppKit
import Vision

struct Rng {
    var state: UInt64
    mutating func below(_ n: Int) -> Int {
        state = state &* 6364136223846793005 &+ 1442695040888963407
        return Int((state >> 33) % UInt64(max(n, 1)))
    }
}

/// RGBA pixels, row 0 at the top.
final class Bitmap {
    let width: Int, height: Int
    var data: [UInt8]

    init(_ image: CGImage) {
        width = image.width
        height = image.height
        data = [UInt8](repeating: 0, count: width * height * 4)
        data.withUnsafeMutableBytes { raw in
            let ctx = CGContext(data: raw.baseAddress, width: width, height: height, bitsPerComponent: 8,
                                bytesPerRow: width * 4, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
            ctx.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
        }
    }

    func rgb(_ x: Int, _ y: Int) -> (Int, Int, Int) {
        let i = (y * width + x) * 4
        return (Int(data[i]), Int(data[i + 1]), Int(data[i + 2]))
    }

    func image() -> CGImage {
        let provider = CGDataProvider(data: Data(data) as CFData)!
        return CGImage(width: width, height: height, bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: width * 4,
                       space: CGColorSpace(name: CGColorSpace.sRGB)!,
                       bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.premultipliedLast.rawValue),
                       provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent)!
    }
}

func recognizeWords(_ image: CGImage) throws -> [(text: String, rect: CGRect)] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([request])   // a failure is said, never read as "no words"
    let w = CGFloat(image.width), h = CGFloat(image.height)
    var words: [(String, CGRect)] = []
    for observation in request.results ?? [] {
        guard let candidate = observation.topCandidates(1).first else { continue }
        let text = candidate.string
        var index = text.startIndex
        while index < text.endIndex {
            guard let start = text[index...].firstIndex(where: { !$0.isWhitespace }) else { break }
            let end = text[start...].firstIndex(where: { $0.isWhitespace }) ?? text.endIndex
            let box = (try? candidate.boundingBox(for: start..<end))?.boundingBox ?? observation.boundingBox
            // Vision: normalised, origin bottom-left → pixels, origin top-left
            words.append((String(text[start..<end]),
                          CGRect(x: box.minX * w, y: (1 - box.maxY) * h, width: box.width * w, height: box.height * h)))
            index = end
        }
    }
    return words
}

/// One word as the screen draws it: its box, background, and ink runs (letter shapes: columns that differ
/// from the background).
struct Word {
    let x0: Int, x1: Int, y0: Int, y1: Int
    let bg: (Int, Int, Int)
    let runs: [(start: Int, end: Int)]
    let style: String   // size + ink colour + background: letters only move between words that look alike
}

struct Glyph { let width: Int, height: Int; let pixels: [UInt8] }

func measure(_ bmp: Bitmap, _ rect: CGRect) -> Word? {
    let pad = Int((rect.height * 0.14).rounded(.up)) + 1   // Vision's word boxes can cut ascenders and descenders
    let x0 = max(0, Int(rect.minX.rounded(.down))), x1 = min(bmp.width, Int(rect.maxX.rounded(.up)))
    let y0 = max(0, Int(rect.minY.rounded(.down)) - pad), y1 = min(bmp.height, Int(rect.maxY.rounded(.up)) + pad)
    guard x1 - x0 > 4, y1 - y0 > 3 else { return nil }

    // background: median of a ring just outside the box
    var rs: [Int] = [], gs: [Int] = [], bs: [Int] = []
    for x in max(0, x0 - 2)..<min(bmp.width, x1 + 2) {
        for y in [max(0, y0 - 2), min(bmp.height - 1, y1 + 1)] { let p = bmp.rgb(x, y); rs.append(p.0); gs.append(p.1); bs.append(p.2) }
    }
    for y in y0..<y1 {
        for x in [max(0, x0 - 2), min(bmp.width - 1, x1 + 1)] { let p = bmp.rgb(x, y); rs.append(p.0); gs.append(p.1); bs.append(p.2) }
    }
    let median = { (v: [Int]) in v.sorted()[v.count / 2] }
    let bg = (median(rs), median(gs), median(bs))

    var ink = [Bool](repeating: false, count: x1 - x0)
    var inkR: [Int] = [], inkG: [Int] = [], inkB: [Int] = []
    for x in x0..<x1 {
        for y in y0..<y1 {
            let p = bmp.rgb(x, y)
            if abs(p.0 - bg.0) + abs(p.1 - bg.1) + abs(p.2 - bg.2) > 90 {
                ink[x - x0] = true; inkR.append(p.0); inkG.append(p.1); inkB.append(p.2)
            }
        }
    }
    var runs: [(start: Int, end: Int)] = []
    var i = 0
    while i < ink.count {
        if ink[i] { let s = i; while i < ink.count && ink[i] { i += 1 }; runs.append((s + x0, i + x0)) } else { i += 1 }
    }
    guard runs.count >= 2, !inkR.isEmpty else { return nil }
    let q = { (v: Int) in v / 40 }
    let style = "\((y1 - y0) / 6)-\(q(median(inkR))),\(q(median(inkG))),\(q(median(inkB)))-\(q(bg.0)),\(q(bg.1)),\(q(bg.2))"
    return Word(x0: x0, x1: x1, y0: y0, y1: y1, bg: bg, runs: runs, style: style)
}

func glyph(_ bmp: Bitmap, _ word: Word, _ run: (start: Int, end: Int), mirrored: Bool = false) -> Glyph {
    let width = run.end - run.start
    var pixels: [UInt8] = []
    for y in word.y0..<word.y1 {
        for i in 0..<width {
            let x = run.start + (mirrored ? width - 1 - i : i)
            let s = (y * bmp.width + x) * 4
            pixels.append(contentsOf: bmp.data[s..<s + 4])
        }
    }
    return Glyph(width: width, height: word.y1 - word.y0, pixels: pixels)
}

/// Rebuild the word from random letter shapes of the same style (drawn from every word on screen that
/// looks alike), keeping its gaps and bounds: real gibberish, in the screen's own typeface.
func redraw(_ bmp: Bitmap, _ word: Word, _ pool: [Glyph], _ rng: inout Rng) {
    for y in word.y0..<word.y1 {
        for x in word.runs.first!.start..<min(word.runs.last!.end, bmp.width) {
            let d = (y * bmp.width + x) * 4
            bmp.data[d] = UInt8(word.bg.0); bmp.data[d + 1] = UInt8(word.bg.1); bmp.data[d + 2] = UInt8(word.bg.2); bmp.data[d + 3] = 255
        }
    }
    let gaps = zip(word.runs.dropFirst(), word.runs).map { $0.start - $1.end }
    let limit = min(bmp.width, word.x1 + 2)
    var cursor = word.runs.first!.start
    for n in 0..<word.runs.count {
        var g = pool[rng.below(pool.count)]
        for _ in 0..<12 where cursor + g.width > limit { g = pool[rng.below(pool.count)] }
        if cursor + g.width > limit { break }
        let height = word.y1 - word.y0, dy = height - g.height   // align bottoms
        for gx in 0..<g.width where cursor + gx < limit {
            for gy in 0..<g.height {
                let y = word.y0 + gy + dy
                guard y >= word.y0 && y < word.y1 else { continue }
                let s = (gy * g.width + gx) * 4, d = (y * bmp.width + cursor + gx) * 4
                bmp.data[d..<d + 4] = g.pixels[s..<s + 4]
            }
        }
        cursor += g.width + (n < gaps.count ? gaps[n] : 0)
        if cursor >= limit { break }
    }
}

func gibberish(_ image: CGImage, seed: UInt64) throws -> (CGImage, Int) {
    let bmp = Bitmap(image)
    var rng = Rng(state: seed)
    let words = try recognizeWords(image).filter { $0.text.count > 1 }.compactMap { measure(bmp, $0.rect) }
    var pools: [String: [Glyph]] = [:]
    for word in words { pools[word.style, default: []] += word.runs.map { glyph(bmp, word, $0) } }
    // A style with few letters (a lone title) could be decoded from its own letters: add mirrored shapes.
    for word in words where pools[word.style]!.count < 16 {
        pools[word.style]! += word.runs.map { glyph(bmp, word, $0, mirrored: true) }
    }
    for word in words { redraw(bmp, word, pools[word.style]!, &rng) }
    return (bmp.image(), words.count)
}

func load(_ path: String) -> CGImage? {
    guard let image = NSImage(contentsOfFile: path) else { return nil }
    var rect = CGRect(origin: .zero, size: image.size)
    return image.cgImage(forProposedRect: &rect, context: nil, hints: nil)
}

func save(_ image: CGImage, _ path: String) -> Bool {
    let rep = NSBitmapImageRep(cgImage: image)
    guard let png = rep.representation(using: .png, properties: [:]) else { return false }
    return (try? png.write(to: URL(fileURLWithPath: path))) != nil
}

func selftest() -> Int32 {
    let size = CGSize(width: 900, height: 260)
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(size.width), pixelsHigh: Int(size.height),
                               bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                               colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    NSColor(calibratedRed: 0.96, green: 0.94, blue: 0.92, alpha: 1).setFill()
    NSRect(origin: .zero, size: size).fill()
    let lines = [("Dinner cooked on one wood fire", NSFont(name: "Georgia", size: 44) ?? .systemFont(ofSize: 44)),
                 ("Thirty four seats around the hearth", NSFont.systemFont(ofSize: 30)),
                 ("Book a table tonight", NSFont.boldSystemFont(ofSize: 30))]
    for (n, line) in lines.enumerated() {
        NSAttributedString(string: line.0, attributes: [.font: line.1, .foregroundColor: NSColor(calibratedWhite: 0.12, alpha: 1)])
            .draw(at: NSPoint(x: 30, y: size.height - 70 - CGFloat(n) * 70))
    }
    NSGraphicsContext.restoreGraphicsState()
    let source = rep.cgImage!
    let before: Set<String>, after: Set<String>, scrambled: CGImage, count: Int
    do {
        before = Set(try recognizeWords(source).map { $0.text.lowercased() }.filter { $0.count >= 4 })
        (scrambled, count) = try gibberish(source, seed: 7)
        after = Set(try recognizeWords(scrambled).map { $0.text.lowercased() })
    } catch {
        print("gibberish selftest: text recognition failed (\(error)), so nothing could be checked")
        return 3
    }
    let readable = before.intersection(after)
    print("gibberish selftest: \(count) words scrambled; \(before.count) readable before, \(readable.count) still readable after\(readable.isEmpty ? "" : " (\(readable.sorted().joined(separator: ", ")))")")
    return count >= 8 && before.count >= 8 && readable.count <= 1 ? 0 : 1
}

let args = CommandLine.arguments
if args.count == 2 && args[1] == "--selftest" { exit(selftest()) }
guard args.count >= 3, let source = load(args[1]) else {
    FileHandle.standardError.write("usage: gibberish <in.png> <out.png> [seed] | --selftest\n".data(using: .utf8)!)
    exit(2)
}
let result: CGImage, count: Int
do {
    (result, count) = try gibberish(source, seed: args.count > 3 ? UInt64(args[3]) ?? 7 : 7)
} catch {
    print("gibberish: text recognition failed (\(error)), so nothing was scrambled. Don't use it for a blind look.")
    exit(3)
}
if count == 0 {
    print("gibberish: no words recognised, so nothing was scrambled. If the screen has text, recognition missed it; don't use it for a blind look.")
    exit(4)
}
guard save(result, args[2]) else { FileHandle.standardError.write("can't write \(args[2])\n".data(using: .utf8)!); exit(1) }
print("gibberish: \(count) words scrambled → \(args[2])")

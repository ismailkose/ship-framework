# NaturalLanguage + Translation — iOS Reference

> **When to read:** Dev reads this when tokenizing, tagging, and analyzing natural language text; when adding language identification, sentiment analysis, named entity recognition, part-of-speech tagging, text embeddings, or in-app translation.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `NLTokenizer` | Segment text into tokens | `.word`, `.sentence`, `.paragraph`, `.document` units |
| `NLTagger` | Tag text with linguistic labels | `.lexicalClass`, `.nameType`, `.lemma`, `.sentimentScore` schemes |
| `NLLanguageRecognizer` | Identify language | Returns dominant language or multiple hypotheses |
| `NLEmbedding` | Semantic similarity | Word/sentence embeddings; returns cosine distance |
| `TranslationSession` | Programmatic translation | Translate single or batch strings; check availability |
| `LanguageAvailability` | Language availability | `.installed`, `.supported`, `.unsupported` status |
| `.translationPresentation()` | System translation UI | Built-in overlay; simple one-liner |
| `.translationTask()` | Async translation context | SwiftUI view modifier; handles session setup |

## Code Examples

### 1. Tokenization by Words

```swift
import NaturalLanguage

func tokenizeWords(in text: String) -> [String] {
    let tokenizer = NLTokenizer(unit: .word)
    tokenizer.string = text

    let range = text.startIndex..<text.endIndex
    return tokenizer.tokens(for: range).map { String(text[$0]) }
}
```

### 2. Tokenization by Sentences

```swift
func tokenizeSentences(in text: String) -> [String] {
    let tokenizer = NLTokenizer(unit: .sentence)
    tokenizer.string = text

    let range = text.startIndex..<text.endIndex
    return tokenizer.tokens(for: range).map { String(text[$0]) }
}
```

### 3. Enumerate Tokens with Attributes

```swift
let tokenizer = NLTokenizer(unit: .word)
tokenizer.string = text

tokenizer.enumerateTokens(in: text.startIndex..<text.endIndex) { range, attributes in
    if attributes.contains(.numeric) {
        print("Number: \(text[range])")
    }
    return true // continue enumeration
}
```

### 4. Language Identification (Dominant)

```swift
func detectLanguage(for text: String) -> NLLanguage? {
    NLLanguageRecognizer.dominantLanguage(for: text)
}
```

### 5. Language Identification (Multiple Hypotheses)

```swift
func languageHypotheses(for text: String, max: Int = 5) -> [NLLanguage: Double] {
    let recognizer = NLLanguageRecognizer()
    recognizer.processString(text)
    return recognizer.languageHypotheses(withMaximum: max)
}
```

### 6. Language Detection with Constraints

```swift
let recognizer = NLLanguageRecognizer()
recognizer.languageConstraints = [.english, .french, .spanish]
recognizer.processString(text)
let detected = recognizer.dominantLanguage
```

### 7. Part-of-Speech Tagging

```swift
func tagPartsOfSpeech(in text: String) -> [(String, NLTag)] {
    let tagger = NLTagger(tagSchemes: [.lexicalClass])
    tagger.string = text

    var results: [(String, NLTag)] = []
    let range = text.startIndex..<text.endIndex
    let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace]

    tagger.enumerateTags(in: range, unit: .word, scheme: .lexicalClass, options: options) { tag, tokenRange in
        if let tag {
            results.append((String(text[tokenRange]), tag))
        }
        return true
    }
    return results
}
```

### 8. Named Entity Recognition

```swift
func extractEntities(from text: String) -> [(String, NLTag)] {
    let tagger = NLTagger(tagSchemes: [.nameType])
    tagger.string = text

    var entities: [(String, NLTag)] = []
    let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace, .joinNames]

    tagger.enumerateTags(
        in: text.startIndex..<text.endIndex,
        unit: .word,
        scheme: .nameType,
        options: options
    ) { tag, tokenRange in
        if let tag, tag != .other {
            entities.append((String(text[tokenRange]), tag))
        }
        return true
    }
    return entities
}
```

### 9. Sentiment Analysis

```swift
func sentimentScore(for text: String) -> Double? {
    let tagger = NLTagger(tagSchemes: [.sentimentScore])
    tagger.string = text

    let (tag, _) = tagger.tag(
        at: text.startIndex,
        unit: .paragraph,
        scheme: .sentimentScore
    )
    return tag.flatMap { Double($0.rawValue) }
}
```

### 10. Word Similarity with Embeddings

```swift
func wordSimilarity(_ word1: String, _ word2: String) -> Double? {
    guard let embedding = NLEmbedding.wordEmbedding(for: .english) else { return nil }
    return embedding.distance(between: word1, and: word2, distanceType: .cosine)
}
```

### 11. Find Similar Words

```swift
func findSimilarWords(to word: String, count: Int = 5) -> [(String, Double)] {
    guard let embedding = NLEmbedding.wordEmbedding(for: .english) else { return [] }
    return embedding.neighbors(for: word, maximumCount: count, distanceType: .cosine)
}
```

### 12. Sentence Similarity

```swift
func sentenceSimilarity(_ s1: String, _ s2: String) -> Double? {
    guard let embedding = NLEmbedding.sentenceEmbedding(for: .english) else { return nil }
    return embedding.distance(between: s1, and: s2, distanceType: .cosine)
}
```

### 13. System Translation Overlay

```swift
import SwiftUI
import Translation

struct TranslatableView: View {
    @State private var showTranslation = false
    let text = "Hello, how are you?"

    var body: some View {
        Text(text)
            .onTapGesture { showTranslation = true }
            .translationPresentation(
                isPresented: $showTranslation,
                text: text
            )
    }
}
```

### 14. Programmatic Translation

```swift
struct TranslatingView: View {
    @State private var translatedText = ""
    @State private var configuration: TranslationSession.Configuration?

    var body: some View {
        VStack {
            Text(translatedText)
            Button("Translate") {
                configuration = .init(
                    source: Locale.Language(identifier: "en"),
                    target: Locale.Language(identifier: "es")
                )
            }
        }
        .translationTask(configuration) { session in
            let response = try await session.translate("Hello, world!")
            translatedText = response.targetText
        }
    }
}
```

### 15. Batch Translation

```swift
.translationTask(configuration) { session in
    let requests = texts.enumerated().map { index, text in
        TranslationSession.Request(
            sourceText: text,
            clientIdentifier: "\(index)"
        )
    }
    let responses = try await session.translations(from: requests)
    for response in responses {
        print("\(response.sourceText) -> \(response.targetText)")
    }
}
```

### 16. Check Language Availability

```swift
let availability = LanguageAvailability()
let status = await availability.status(
    from: Locale.Language(identifier: "en"),
    to: Locale.Language(identifier: "ja")
)
switch status {
case .installed: print("Ready to translate offline")
case .supported: print("Needs download")
case .unsupported: print("Language pair not available")
}
```

### 17. Lemmatization (Base Form)

```swift
func extractLemmas(from text: String) -> [(String, String)] {
    let tagger = NLTagger(tagSchemes: [.lemma])
    tagger.string = text

    var results: [(String, String)] = []
    let range = text.startIndex..<text.endIndex
    let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace]

    tagger.enumerateTags(in: range, unit: .word, scheme: .lemma, options: options) { tag, tokenRange in
        let word = String(text[tokenRange])
        let lemma = tag?.rawValue ?? word
        results.append((word, lemma))
        return true
    }
    return results
}
```

### 18. Combined NER + POS Tagging

```swift
func tagNameTypeOrLexicalClass(in text: String) -> [(String, NLTag)] {
    let tagger = NLTagger(tagSchemes: [.nameTypeOrLexicalClass])
    tagger.string = text

    var results: [(String, NLTag)] = []
    let range = text.startIndex..<text.endIndex

    tagger.enumerateTags(in: range, unit: .word, scheme: .nameTypeOrLexicalClass, options: []) { tag, tokenRange in
        if let tag {
            results.append((String(text[tokenRange]), tag))
        }
        return true
    }
    return results
}
```

### 19. Thread-Safe Tagger Access

```swift
await withTaskGroup(of: Void.self) { group in
    for _ in 0..<10 {
        group.addTask {
            let tagger = NLTagger(tagSchemes: [.lexicalClass])
            tagger.string = someText
            // process...
        }
    }
}
```

### 20. Per-Token Language Detection

```swift
func detectLanguagePerToken(in text: String) -> [(String, NLLanguage?)] {
    let tagger = NLTagger(tagSchemes: [.language])
    tagger.string = text

    var results: [(String, NLLanguage?)] = []
    let range = text.startIndex..<text.endIndex

    tagger.enumerateTags(in: range, unit: .word, scheme: .language, options: []) { tag, tokenRange in
        let word = String(text[tokenRange])
        let language = tag.flatMap { NLLanguage($0.rawValue) }
        results.append((word, language))
        return true
    }
    return results
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| Share `NLTagger` across threads | Create new instance per thread; they are not thread-safe |
| Force unwrap embedding (e.g., `wordEmbedding(for: .japanese)!`) | Check availability: `guard let embedding = ... else { return }` |
| Create new tagger per token | Set string once, reuse for entire text via enumeration |
| Ignore language hints on short text | Set `languageConstraints` or `languageHints` for accuracy |
| Assume all languages have embeddings | Not all languages available; return nil if unsupported |
| Use Core ML for built-in NLP tasks | Use `NLTagger` for NER, POS; reserve Core ML for custom models |

## Review Checklist

- [ ] `NLTokenizer` and `NLTagger` instances used from a single thread
- [ ] Tagger created once per text, not per token
- [ ] Language detection uses constraints/hints for short text
- [ ] `NLEmbedding` availability checked before use (returns nil if unavailable)
- [ ] Translation `LanguageAvailability` checked before attempting translation
- [ ] `.translationTask()` used within a SwiftUI view hierarchy
- [ ] Batch translation uses `clientIdentifier` to match responses to requests
- [ ] Sentiment scores handled as optional (may return nil for unsupported languages)
- [ ] `.joinNames` option used with NER to keep multi-word names together
- [ ] Custom ML models loaded via `NLModel`, not raw Core ML

---

_Source: swift-ios-skills · Adapted for Ship Framework agent reference_

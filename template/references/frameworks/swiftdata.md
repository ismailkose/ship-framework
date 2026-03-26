# SwiftData — iOS Reference

> **When to read:** Dev reads this when persisting data, querying models, or syncing with CloudKit.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Concept | Purpose | Key Notes |
|---------|---------|-----------|
| `@Model` | Marks class as SwiftData entity | Uses value semantics; stored automatically |
| `@Attribute` | Configures property persistence | `.unique`, `.ephemeral`, `.externalStorage`, `.preserveValueOnDeletion` (iOS 18+), `.transformable(by:)`, `originalName` |
| `@Relationship` | Defines one-to-many or many-to-many | Handles cascade/delete behavior; unidirectional (iOS 18+) with `inverse: nil` |
| `#Unique` | Enforces compound uniqueness (iOS 18+) | `#Unique<Model>([\.field1, \.field2])` |
| `@ModelActor` | Concurrent data handling | Thread-safe context for background work |
| `ModelContainer` | Creates storage stack | Init with schema; thread-safe |
| `ModelContext` | Session for CRUD operations | Inserted/modified/deleted tracking |
| `@Query` | SwiftUI macro for reactive fetch | Auto-refreshes on data changes |
| `FetchDescriptor` | Specifies what/how to fetch | Includes predicate, sort, limit |
| `PersistentModel` | Protocol; conform instead of `@Model` for custom init | Full control over autosave |

## Code Examples

```swift
// 1. Define model with relationships
@Model
final class Book {
    var title: String
    var author: String
    @Attribute(.unique) var isbn: String
    var publicationYear: Int
    @Relationship(deleteRule: .cascade) var chapters: [Chapter]

    init(title: String, author: String, isbn: String, year: Int) {
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publicationYear = year
        self.chapters = []
    }
}

@Model
final class Chapter {
    var number: Int
    var title: String
}

// 2. Setup container & context
let container = try ModelContainer(
    for: Book.self, Chapter.self,
    configurations: ModelConfiguration(isStoredInMemoryOnly: false)
)
let context = ModelContext(container)

// 3. Query with @Query in SwiftUI
struct BookListView {
    @Query(sort: \.title, order: .forward) var books: [Book]

    var body: some View {
        List(books) { book in
            Text(book.title)
                .onDelete { offsets in
                    offsets.forEach { context.delete(books[$0]) }
                }
        }
    }
}

// 4. Manual fetch with predicate
var descriptor = FetchDescriptor<Book>(
    predicate: #Predicate { $0.publicationYear > 2020 }
)
descriptor.fetchLimit = 10
descriptor.propertiesToFetch = [\.title, \.author]  // Optimize: fetch only needed fields
descriptor.relationshipKeyPathsForPrefetching = [\.chapters]  // Prefetch relationships
let recentBooks = try context.fetch(descriptor)

// 5. Transactions and bulk operations (atomic)
try modelContext.transaction {
    let book = Book(title: "New Book", author: "Author", isbn: "123", year: 2025)
    modelContext.insert(book)
}

// 6. Bulk delete
try modelContext.delete(model: Book.self, where: #Predicate { $0.publicationYear < 2000 })

// 7. Fetch identifiers only (efficient for large datasets)
let ids = try modelContext.fetchIdentifiers(descriptor)

// 8. Enumerate with batch size (memory-efficient)
try modelContext.enumerate(descriptor, batchSize: 100) { book in
    book.updated = true
}
```

### Model Inheritance (iOS 26+)

```swift
@Model
final class Book {
    var title: String
    var author: String
    init(title: String, author: String) {
        self.title = title
        self.author = author
    }
}

@Model
final class Textbook: Book {
    var subject: String
    init(title: String, author: String, subject: String) {
        super.init(title: title, author: author)
        self.subject = subject
    }
}
```

### Unidirectional Relationships (iOS 18+)

```swift
// One-way relationship: no inverse needed
@Model
final class Author {
    var name: String
    @Relationship(deleteRule: .cascade, inverse: nil) var books: [Book] = []
}
```

## Common Mistakes

| ❌ Incorrect | ✅ Correct |
|------------|-----------|
| `@Model class MyType { }` (class missing final) | `@Model final class MyType { }` — SwiftData requires final; prevents subclassing issues |
| Not calling `try context.save()` after mutations | Always save after insert/update/delete: `try context.save()` |
| Using `@State` for model instead of binding changes | Use `@Query` macro or pass context to child views |
| Ignoring cascade rules; manual deletes children | Use `@Relationship(deleteRule: .cascade)` to auto-delete related objects |
| Fetching all data into memory for large tables | Use `FetchDescriptor` with predicates & limits for pagination |

## Review Checklist

- [ ] All `@Model` classes marked `final`
- [ ] `@Unique` attributes prevent duplicates
- [ ] `@Relationship(deleteRule:)` matches intended cascade behavior
- [ ] `@Query` used in SwiftUI views, not business logic
- [ ] Large fetches use `FetchDescriptor` with predicates/limits
- [ ] `context.save()` called after every mutation (or autosave config checked)
- [ ] No `@State` wrapping model objects directly
- [ ] Ephemeral properties marked with `@Attribute(.ephemeral)`
- [ ] External storage configured for large binary/media
- [ ] CloudKit sync enabled in ModelConfiguration if needed
- [ ] Thread safety: context not shared across threads
- [ ] Migration plan in place if model schema changes
- [ ] `#Unique` constraints applied for iOS 18+
- [ ] Model inheritance patterns correct (iOS 26+)
- [ ] Unidirectional relationships use `inverse: nil` (iOS 18+)
- [ ] `modelContext.transaction { }` for atomic operations
- [ ] Bulk delete and enumerate operations optimized with batch size
- [ ] `propertiesToFetch` and `fetchIdentifiers` used for large result sets
- [ ] `@ModelActor` used for background work instead of `@MainActor`

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

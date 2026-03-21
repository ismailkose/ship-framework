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
| `@Attribute` | Configures property persistence | `.unique`, `.ephemeral`, `.externalStorage` |
| `@Relationship` | Defines one-to-many or many-to-many | Handles cascade/delete behavior |
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
let recentBooks = try context.fetch(descriptor)
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

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_

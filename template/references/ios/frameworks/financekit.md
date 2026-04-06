# FinanceKit Reference

> **When to read:** Dev reads when accessing financial data (balances, transactions).
> Crit reads Common Mistakes during review.

---

## Requirements

- **Entitlement:** `com.apple.developer.finance-kit` (request from Apple)
- **Info.plist:** `NSFinanceUsageDescription` with clear purpose string
- **Availability:** iPhone only, iOS 17+

```swift
import FinanceKit

// Check availability FIRST
guard FinanceStore.isAvailable else {
  // FinanceKit not available on this device
  return
}
```

## Authorization

```swift
let store = FinanceStore.shared

let status = try await store.requestAuthorization()
switch status {
case .authorized: // proceed
case .denied: // show explanation, link to Settings
case .notDetermined: // shouldn't happen after request
@unknown default: break
}
```

## Account Types

```swift
let accounts = try await store.accounts()
for account in accounts {
  switch account.type {
  case .checking: // ...
  case .savings: // ...
  case .credit: // ...
  case .investment: // ...
  case .loan: // ...
  @unknown default: break
  }
}
```

## Balances

```swift
let balance = try await store.balance(for: account)
let amount = balance.available  // CurrencyAmount
let currency = balance.available.currency  // e.g., "USD"

// Check credit vs debit
if balance.creditDebitIndicator == .credit {
  // positive balance
}
```

## Transactions

```swift
let query = TransactionQuery(
  accountID: account.id,
  startDate: Calendar.current.date(byAdding: .month, value: -3, to: .now),
  endDate: .now
)

let transactions = try await store.transactions(query: query)
for transaction in transactions {
  let amount = transaction.transactionAmount
  let description = transaction.transactionDescription
  let date = transaction.postedDate
  let indicator = transaction.creditDebitIndicator  // .credit or .debit
}
```

## UI Pickers

```swift
// Account picker — system UI for selecting accounts
AccountPicker(selection: $selectedAccount) {
  Text("Choose Account")
}
```

## Common Mistakes
- ❌ Calling FinanceKit APIs without checking `isAvailable` — crashes on unsupported devices
- ❌ Ignoring `creditDebitIndicator` — amounts are always positive, direction matters
- ❌ Not handling authorization denial gracefully — explain why access is needed
- ❌ Missing entitlement — app will crash at runtime without it
- ❌ Assuming all accounts have balances — some account types may not

## Review Checklist
- [ ] `FinanceStore.isAvailable` checked before any API call
- [ ] Entitlement and Info.plist description configured
- [ ] Authorization status handled for all cases
- [ ] Credit/debit indicator used correctly for display
- [ ] Error handling for network/availability failures

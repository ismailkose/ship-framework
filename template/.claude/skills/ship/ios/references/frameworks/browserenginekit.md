# BrowserEngineKit Reference

> **When to read:** Dev reads when building alternative browser engines (EU/Japan distribution).
> Crit reads Common Mistakes during security review.

---

## Overview

BrowserEngineKit enables third-party browser engines on iOS. **Available only in EU and Japan** under Digital Markets Act / similar regulations. Apps must use Web Browser entitlement.

## Eligibility

- Distribution through EU/Japan App Store alternative marketplaces OR direct
- `com.apple.developer.web-browser-engine.` entitlements required
- Must implement multi-process architecture (extension-based)
- Must follow Apple's security requirements for sandboxing

## Architecture

```
┌─────────────────┐     XPC      ┌──────────────────┐
│   Main App      │ ←─────────→  │  Rendering        │
│   (UI process)  │              │  Extension        │
└─────────────────┘              └──────────────────┘
         ↕ XPC                            ↕ XPC
┌─────────────────┐              ┌──────────────────┐
│  Networking     │              │  GPU Process      │
│  Extension      │              │  Extension        │
└─────────────────┘              └──────────────────┘
```

## Process Management

```swift
import BrowserEngineKit

// Launch rendering process
let renderingProcess = try await BEWebContentProcess()
try await renderingProcess.makeLibXPCConnection()

// Launch networking process
let networkProcess = try await BENetworkingProcess()

// Handle process crashes
renderingProcess.onTermination = { reason in
  // Restart process, restore tab state
}
```

## Sandboxing

Each extension runs in a restricted sandbox:
- Rendering: No network access, no file system (except shared memory)
- Networking: Network access, no UI, no file system
- GPU: GPU access only

```swift
// Shared memory for IPC
let sharedMemory = try BESharedMemory(size: 1024 * 1024)
let buffer = sharedMemory.buffer
```

## Common Mistakes
- ❌ Deploying outside EU/Japan — app will be rejected
- ❌ Single-process architecture — multi-process is mandatory
- ❌ Not handling extension crashes — tabs should recover, not crash the app
- ❌ Giving rendering process network access — violates sandbox requirements
- ❌ Not implementing content blockers — expected by users

## Review Checklist
- [ ] Multi-process architecture with proper XPC communication
- [ ] Each extension sandboxed correctly
- [ ] Process crash recovery implemented
- [ ] Distribution limited to eligible regions
- [ ] Security model reviewed (no cross-process data leaks)
- [ ] Content blocking API implemented

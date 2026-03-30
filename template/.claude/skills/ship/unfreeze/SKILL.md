---
name: ship-unfreeze
description: |
  Removes the directory-scoped edit restriction set by /ship-freeze or /ship-guard. (ship)
---

# Unfreeze — Remove Edit Restriction

Removes the freeze boundary, allowing edits to any file again.

## What It Does

Deletes the `.claude/.freeze-path` state file. After this, Edit and Write operations are no longer restricted to a specific directory.

## Usage

`/ship-unfreeze` — removes the active freeze restriction

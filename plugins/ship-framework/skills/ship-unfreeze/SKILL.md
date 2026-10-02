---
name: ship-unfreeze
description: |
  Notes for /shipmate unfreeze, which removes the edit restriction set by /shipmate freeze or (ship)
  /shipmate guard. Not a user command — use /shipmate unfreeze.
user-invocable: false
---

# Unfreeze — Remove Edit Restriction

Removes the freeze boundary, allowing edits to any file again.

## What It Does

Deletes the `.claude/.freeze-path` state file. After this, Edit and Write operations are no longer restricted to a specific directory.

## Usage

`/shipmate unfreeze` — removes the active freeze restriction

#!/usr/bin/env bash
# Ship Framework — freeze hook
# Enforces directory-scoped edit restriction.
# Returns JSON: {} (allow) or {"permissionDecision":"deny","message":"..."} (block)
#
# Input: JSON on stdin with shape {"tool_input": {"file_path": "..."}}
# State: .claude/.freeze-path contains the allowed directory (one line)

set -euo pipefail

FREEZE_STATE=".claude/.freeze-path"

# If no freeze is active, allow everything
if [ ! -f "$FREEZE_STATE" ]; then
  echo '{}'
  exit 0
fi

FREEZE_PATH=$(cat "$FREEZE_STATE" 2>/dev/null || true)

# If freeze file is empty, allow everything
if [ -z "$FREEZE_PATH" ]; then
  echo '{}'
  exit 0
fi

# Read tool input from stdin
INPUT=$(cat)

# Extract file_path from JSON
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//' || true)

# If we can't extract the path, allow (fail open for safety)
if [ -z "$FILE_PATH" ]; then
  echo '{}'
  exit 0
fi

# Resolve paths for comparison (POSIX-portable)
# Use pwd -P to resolve symlinks where possible
resolve_path() {
  local path="$1"
  # If path is relative, prepend pwd
  if [ "${path#/}" = "$path" ]; then
    path="$(pwd)/$path"
  fi
  # Normalize: remove trailing slash, resolve . and ..
  # Use python if available for reliable resolution, fall back to sed
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import os; print(os.path.realpath('$path'))" 2>/dev/null || echo "$path"
  elif command -v realpath >/dev/null 2>&1; then
    realpath -m "$path" 2>/dev/null || echo "$path"
  else
    # Basic normalization: remove trailing slash
    echo "${path%/}"
  fi
}

RESOLVED_FREEZE=$(resolve_path "$FREEZE_PATH")
RESOLVED_FILE=$(resolve_path "$FILE_PATH")

# Check if file is inside the freeze boundary
# File must start with the freeze path (+ trailing slash or exact match)
if [ "$RESOLVED_FILE" = "$RESOLVED_FREEZE" ] || \
   [ "${RESOLVED_FILE#$RESOLVED_FREEZE/}" != "$RESOLVED_FILE" ]; then
  # Inside boundary — allow
  echo '{}'
else
  # Outside boundary — deny
  FREEZE_DIR=$(basename "$RESOLVED_FREEZE")
  FILE_NAME=$(basename "$RESOLVED_FILE")
  echo "{\"permissionDecision\":\"deny\",\"message\":\"Freeze active: edits locked to $FREEZE_DIR/. Cannot edit $FILE_NAME — it's outside the boundary. Use /ship-unfreeze to remove the restriction.\"}"
fi

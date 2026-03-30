#!/usr/bin/env bash
# Ship Framework — careful hook
# Intercepts Bash tool calls and warns on destructive commands.
# Returns JSON: {} (allow) or {"permissionDecision":"ask","message":"..."} (warn)
#
# Input: JSON on stdin with shape {"tool_input": {"command": "..."}}

set -euo pipefail

# Read tool input from stdin
INPUT=$(cat)
# Extract command value — handle escaped quotes inside JSON string
COMMAND=$(echo "$INPUT" | sed 's/.*"command"[[:space:]]*:[[:space:]]*"//;s/"[[:space:]]*[,}].*//' | sed 's/\\"/"/g' || true)

# If we can't extract the command, allow it
if [ -z "$COMMAND" ]; then
  echo '{}'
  exit 0
fi

# Lowercase for case-insensitive matching
CMD_LOWER=$(echo "$COMMAND" | tr '[:upper:]' '[:lower:]')

# --- Safe exceptions for rm -rf ---
# These directories are always safe to delete
SAFE_RM_TARGETS="node_modules|\.next|dist|__pycache__|\.cache|build|\.turbo|coverage|\.parcel-cache|\.nuxt|\.output|tmp|\.vite|\.svelte-kit"

# Check if rm -rf targets only safe directories
is_safe_rm() {
  local cmd="$1"
  # Extract what comes after rm -rf or rm -r
  local targets=$(echo "$cmd" | sed -E 's/.*rm[[:space:]]+-r[f]?[[:space:]]+//')
  # Check each target
  for target in $targets; do
    # Strip trailing slashes and get basename
    local base=$(basename "$target" 2>/dev/null || echo "$target")
    if ! echo "$base" | grep -qE "^($SAFE_RM_TARGETS)$"; then
      return 1  # Not safe
    fi
  done
  return 0  # All targets are safe
}

# --- Destructive pattern checks ---

warn() {
  local msg="$1"
  # Escape quotes for JSON
  msg=$(echo "$msg" | sed 's/"/\\"/g')
  echo "{\"permissionDecision\":\"ask\",\"message\":\"$msg\"}"
  exit 0
}

# rm -rf / rm -r (check safe exceptions first)
if echo "$CMD_LOWER" | grep -qE 'rm[[:space:]]+-r[f]?[[:space:]]'; then
  if ! is_safe_rm "$CMD_LOWER"; then
    warn "Destructive: recursive delete (rm -rf). This permanently removes files. Approve?"
  fi
fi

# DROP TABLE / DROP DATABASE
if echo "$CMD_LOWER" | grep -qiE 'drop[[:space:]]+(table|database|index|view)'; then
  warn "Destructive: SQL DROP detected. This permanently removes database objects. Approve?"
fi

# TRUNCATE
if echo "$CMD_LOWER" | grep -qiE 'truncate[[:space:]]'; then
  warn "Destructive: SQL TRUNCATE detected. This permanently deletes all rows. Approve?"
fi

# git push --force / -f
if echo "$CMD_LOWER" | grep -qE 'git[[:space:]]+push[[:space:]]+.*(-f|--force)'; then
  warn "Destructive: git push --force rewrites remote history. Other collaborators may lose work. Approve?"
fi

# git reset --hard
if echo "$CMD_LOWER" | grep -qE 'git[[:space:]]+reset[[:space:]]+--hard'; then
  warn "Destructive: git reset --hard discards uncommitted changes permanently. Approve?"
fi

# git checkout . / git restore .
if echo "$CMD_LOWER" | grep -qE 'git[[:space:]]+(checkout|restore)[[:space:]]+\.'; then
  warn "Destructive: discards all uncommitted changes in working directory. Approve?"
fi

# git clean -f
if echo "$CMD_LOWER" | grep -qE 'git[[:space:]]+clean[[:space:]]+.*-f'; then
  warn "Destructive: git clean -f removes untracked files permanently. Approve?"
fi

# kubectl delete
if echo "$CMD_LOWER" | grep -qE 'kubectl[[:space:]]+delete'; then
  warn "Destructive: kubectl delete removes resources from the cluster. Approve?"
fi

# docker rm -f / docker system prune
if echo "$CMD_LOWER" | grep -qE 'docker[[:space:]]+(rm[[:space:]]+-f|system[[:space:]]+prune|volume[[:space:]]+prune|image[[:space:]]+prune)'; then
  warn "Destructive: Docker cleanup removes containers/images/volumes. Approve?"
fi

# If we got here, command is safe
echo '{}'

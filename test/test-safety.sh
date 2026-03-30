#!/usr/bin/env bash
# Ship Framework — Safety Hook Tests
# Tests check-careful.sh and check-freeze.sh directly
#
# Usage: bash test/test-safety.sh
# Run from the repo root.

set -euo pipefail

CAREFUL="template/.claude/skills/ship/careful/bin/check-careful.sh"
FREEZE="template/.claude/skills/ship/freeze/bin/check-freeze.sh"

PASS=0
FAIL=0

assert_allow() {
  local desc="$1"
  local input="$2"
  local script="$3"
  local result
  result=$(echo "$input" | bash "$script" 2>/dev/null)
  if [ "$result" = "{}" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc (expected allow, got: $result)"
    FAIL=$((FAIL + 1))
  fi
}

assert_warn() {
  local desc="$1"
  local input="$2"
  local script="$3"
  local result
  result=$(echo "$input" | bash "$script" 2>/dev/null)
  if echo "$result" | grep -q '"permissionDecision"'; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc (expected warn/deny, got: $result)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Testing check-careful.sh ==="
echo ""
echo "--- Should WARN (destructive) ---"

assert_warn "rm -rf /tmp/test" \
  '{"tool_input":{"command":"rm -rf /tmp/test"}}' "$CAREFUL"

assert_warn "rm -r /var/data" \
  '{"tool_input":{"command":"rm -r /var/data"}}' "$CAREFUL"

assert_warn "DROP TABLE users" \
  '{"tool_input":{"command":"psql -c \"DROP TABLE users;\""}}' "$CAREFUL"

assert_warn "TRUNCATE orders" \
  '{"tool_input":{"command":"psql -c \"TRUNCATE orders;\""}}' "$CAREFUL"

assert_warn "git push --force" \
  '{"tool_input":{"command":"git push --force origin main"}}' "$CAREFUL"

assert_warn "git push -f" \
  '{"tool_input":{"command":"git push -f origin main"}}' "$CAREFUL"

assert_warn "git reset --hard" \
  '{"tool_input":{"command":"git reset --hard HEAD~3"}}' "$CAREFUL"

assert_warn "git checkout ." \
  '{"tool_input":{"command":"git checkout ."}}' "$CAREFUL"

assert_warn "git restore ." \
  '{"tool_input":{"command":"git restore ."}}' "$CAREFUL"

assert_warn "git clean -fd" \
  '{"tool_input":{"command":"git clean -fd"}}' "$CAREFUL"

assert_warn "kubectl delete pod" \
  '{"tool_input":{"command":"kubectl delete pod my-pod"}}' "$CAREFUL"

assert_warn "docker system prune" \
  '{"tool_input":{"command":"docker system prune -a"}}' "$CAREFUL"

assert_warn "docker rm -f" \
  '{"tool_input":{"command":"docker rm -f container1"}}' "$CAREFUL"

echo ""
echo "--- Should ALLOW (safe) ---"

assert_allow "ls -la" \
  '{"tool_input":{"command":"ls -la"}}' "$CAREFUL"

assert_allow "git status" \
  '{"tool_input":{"command":"git status"}}' "$CAREFUL"

assert_allow "npm install" \
  '{"tool_input":{"command":"npm install"}}' "$CAREFUL"

assert_allow "rm -rf node_modules" \
  '{"tool_input":{"command":"rm -rf node_modules"}}' "$CAREFUL"

assert_allow "rm -rf .next" \
  '{"tool_input":{"command":"rm -rf .next"}}' "$CAREFUL"

assert_allow "rm -rf dist" \
  '{"tool_input":{"command":"rm -rf dist"}}' "$CAREFUL"

assert_allow "rm -rf __pycache__" \
  '{"tool_input":{"command":"rm -rf __pycache__"}}' "$CAREFUL"

assert_allow "rm -rf coverage" \
  '{"tool_input":{"command":"rm -rf coverage"}}' "$CAREFUL"

assert_allow "git push origin main" \
  '{"tool_input":{"command":"git push origin main"}}' "$CAREFUL"

assert_allow "empty input" \
  '{"tool_input":{"command":""}}' "$CAREFUL"

echo ""
echo "=== Testing check-freeze.sh ==="

# Create temp freeze state
FREEZE_DIR=$(mktemp -d)
echo "src/" > "$FREEZE_DIR/.freeze-path"

echo ""
echo "--- Should ALLOW (inside boundary) ---"

# We need to run from a directory that has .claude/.freeze-path
TESTDIR=$(mktemp -d)
mkdir -p "$TESTDIR/.claude"
echo "$TESTDIR/src/" > "$TESTDIR/.claude/.freeze-path"

cd "$TESTDIR"

assert_allow "Edit inside src/" \
  "{\"tool_input\":{\"file_path\":\"$TESTDIR/src/app.ts\"}}" "$OLDPWD/$FREEZE"

assert_allow "Edit inside src/sub/" \
  "{\"tool_input\":{\"file_path\":\"$TESTDIR/src/components/Button.tsx\"}}" "$OLDPWD/$FREEZE"

echo ""
echo "--- Should DENY (outside boundary) ---"

assert_warn "Edit README.md (outside src/)" \
  "{\"tool_input\":{\"file_path\":\"$TESTDIR/README.md\"}}" "$OLDPWD/$FREEZE"

assert_warn "Edit package.json (outside src/)" \
  "{\"tool_input\":{\"file_path\":\"$TESTDIR/package.json\"}}" "$OLDPWD/$FREEZE"

echo ""
echo "--- No freeze active (should allow all) ---"

rm "$TESTDIR/.claude/.freeze-path"

assert_allow "No freeze: edit anything" \
  "{\"tool_input\":{\"file_path\":\"$TESTDIR/README.md\"}}" "$OLDPWD/$FREEZE"

cd "$OLDPWD"
rm -rf "$TESTDIR" "$FREEZE_DIR"

echo ""
echo "==================================="
echo "Results: $PASS passed, $FAIL failed"
echo "==================================="

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi

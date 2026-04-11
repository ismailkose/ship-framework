#!/usr/bin/env bash
# Ship Framework — reference gate hook (Option D: Hybrid)
# Blocks the FIRST Edit/Write if references haven't been loaded.
# After first successful edit, becomes a no-op for the rest of the session.
# Returns JSON: {} (allow) or {"permissionDecision":"deny","message":"..."} (block)
#
# State files:
#   .claude/.refgate-loaded  — created when REFERENCES LOADED receipt is printed
#   .claude/.refgate-passed  — created after first successful edit (no-op after this)
#
# Input: JSON on stdin with shape {"tool_input": {"file_path": "..."}}

set -euo pipefail

REFS_LOADED=".claude/.refgate-loaded"
GATE_PASSED=".claude/.refgate-passed"

# If the gate has already been passed this session, allow everything (no-op)
if [ -f "$GATE_PASSED" ]; then
  echo '{}'
  exit 0
fi

# If references have been loaded, mark gate as passed and allow
if [ -f "$REFS_LOADED" ]; then
  echo "1" > "$GATE_PASSED"
  echo '{}'
  exit 0
fi

# References NOT loaded and gate NOT passed — block
echo '{"permissionDecision":"deny","message":"Reference Gate: Load references before editing. Run your /ship-* command first, or read the relevant references/ files. The first edit is blocked until references are loaded."}'

#!/bin/bash
# review-fingerprint.sh — print a git tree hash for the working tree as it is right now.
#
# Covers staged, unstaged, deleted, and new non-ignored files; ignored files are excluded.
# Your real index (staging area) is never read or written: every git command below runs
# against ONE private temporary index, which is removed on exit.
#
#   GIT_INDEX_FILE=<tmp> git add -A && git write-tree     # WRONG: the variable reaches only
#                                                         # `git add`; write-tree reads the
#                                                         # real index and misses unstaged edits
#
# The temp index starts from HEAD (`git read-tree HEAD`, or empty in a repo with no commits),
# never from a copy of the real index, so the result depends only on the files on disk.
# Side effect: git writes blob/tree objects for the snapshot into .git/objects (unreferenced;
# `git gc` prunes them later). That's what lets /shipmate review diff against the exact snapshot.
#
# Ship runtime state and Ship's own framework files are excluded so they can't make a
# review of the PRODUCT look stale (updating Ship mid-review isn't a product change):
#   .ship/reviews/ (review records), .ship/state/, .ship/backups/, .ship/manifest.json,
#   .ship/framework.yaml, .claude/skills/ship/, .claude/skills/shipmate/ (the /shipmate entry and
#   its stages), .claude/agents/ship-*, and the pre-/shipmate .claude/commands/ship-* and
#   .claude/skills/ship-*/ mirrors (so their removal on update doesn't count either),
#   .claude/team-rules.md, .claude/.refgate-* (legacy gate markers),
#   .claude/worktrees/ and .worktrees/ (agent/build worktrees — nested checkouts)
#
# Usage: review-fingerprint.sh            → prints the tree hash
#        review-fingerprint.sh --excludes → prints the excluded pathspecs, one per line
# Exit: 0 ok · 2 not a git repository / git failure
# bash 3.2 compatible.

set -u

EXCLUDES=".ship/reviews
.ship/state
.ship/backups
.ship/manifest.json
.ship/framework.yaml
.claude/skills/ship
.claude/skills/shipmate
.claude/skills/ship-*/**
.claude/agents/ship-*
.claude/commands/ship-*
.claude/team-rules.md
.claude/.refgate-*
.claude/worktrees
.worktrees"

if [ "${1:-}" = "--excludes" ]; then
  printf '%s\n' "$EXCLUDES"
  exit 0
fi

top="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "review-fingerprint: not inside a git repository" >&2
  exit 2
}

# Sandboxes (e.g. Codex workspace-write) can make .git read-only. The snapshot's objects then go to
# .ship/state/git-objects (excluded, ignored), with the repo's own objects as an alternate; git
# object IDs are content hashes, so the fingerprint is the same either way. review.py reads the
# same place.
objects="$(cd "$top" && env -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES git rev-parse --git-path objects)"
case "$objects" in /*) ;; *) objects="$top/$objects" ;; esac
side="$top/.ship/state/git-objects"
if [ ! -w "$objects" ]; then
  mkdir -p "$side" || { echo "review-fingerprint: .git is read-only and $side can't be created" >&2; exit 2; }
  export GIT_OBJECT_DIRECTORY="$side" GIT_ALTERNATE_OBJECT_DIRECTORIES="$objects"
elif [ -d "$side" ]; then
  export GIT_ALTERNATE_OBJECT_DIRECTORIES="$side"
fi

tmp="$(mktemp -d "${TMPDIR:-/tmp}/ship-fp.XXXXXX")" || exit 2
trap 'rm -rf "$tmp"' EXIT INT TERM HUP

# Build the exclude pathspecs (glob magic so .claude/.refgate-* matches files).
set -- .
while IFS= read -r ex; do
  [ -n "$ex" ] && set -- "$@" ":(exclude,glob)$ex" ":(exclude,glob)$ex/**"
done <<EOF
$EXCLUDES
EOF

tree="$(
  cd "$top" || exit 2
  export GIT_INDEX_FILE="$tmp/index"            # one temp index for every command below
  if git rev-parse --verify -q HEAD >/dev/null 2>&1; then
    git read-tree HEAD || exit 2
  else
    git read-tree --empty || exit 2               # repo without commits yet
  fi
  git add -A -- "$@" >/dev/null 2>&1 || exit 2   # staged + unstaged + deletions + new non-ignored
  # Excluded paths tracked in HEAD came in with read-tree; drop them from the temp index too,
  # so committing a Ship tooling change does not alter the product fingerprint.
  shift                                           # the remaining args are the exclude pathspecs
  for spec in "$@"; do
    git rm -r -q -f --cached --ignore-unmatch -- ":(glob)${spec#:(exclude,glob)}" >/dev/null 2>&1 || exit 2
  done
  git write-tree || exit 2
)" || { echo "review-fingerprint: git failed" >&2; exit 2; }

[ -n "$tree" ] || { echo "review-fingerprint: empty result" >&2; exit 2; }
printf '%s\n' "$tree"

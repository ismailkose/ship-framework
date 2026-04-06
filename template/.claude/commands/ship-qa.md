⚠️ /ship-qa has been merged into /ship-review. Use /ship-review instead.

This command has been deprecated. The Test persona and health scoring system are now part of /ship-review.

## Quick Migration Guide

| Old command | New command |
|-------------|-------------|
| `/ship-qa` | `/ship-review` (full quality gate with tests) |
| `/ship-qa` (test only) | `/ship-review --test` |
| `/ship-qa` (report only) | `/ship-review --report` |

## Why?

Having separate /ship-review and /ship-qa commands was confusing — users didn't know which to run. Now /ship-review is the single quality gate that includes product review (Crit), design audit (Pol), visual QA (Eye), automated testing (Test), and adversarial challenge. Every run produces a health score.

Use flags for partial runs:
- `--product` — Crit only (HEART dimensions)
- `--design` — Pol only (design craft)
- `--visual` — Eye only (screenshots)
- `--test` — Test only (automated + manual testing)
- `--report` — Full run, report only, no fixes

## Redirecting...

Run /ship-review with the same arguments:

User's request: $ARGUMENTS

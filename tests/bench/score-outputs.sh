#!/bin/bash
# Score E2E outputs from .md files
# Usage: ./score-outputs.sh plan    (scores plan outputs)
#        ./score-outputs.sh review  (scores review outputs)
#        ./score-outputs.sh         (scores both)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUTS="$SCRIPT_DIR/prompts/outputs"
DATA="$SCRIPT_DIR/e2e-data.js"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

ALL_SCENARIOS="plan review build team fix launch think"

score_scenario() {
  local scenario="$1"
  local before_file="$OUTPUTS/${scenario}-before-output.md"
  local after_file="$OUTPUTS/${scenario}-after-output.md"

  echo ""
  echo -e "${BOLD}━━━ /ship-${scenario} ━━━${NC}"
  echo ""

  if [ ! -f "$before_file" ] && [ ! -f "$after_file" ]; then
    echo -e "${YELLOW}No output files found. Save Claude's responses as:${NC}"
    echo "  $OUTPUTS/${scenario}-before-output.md"
    echo "  $OUTPUTS/${scenario}-after-output.md"
    return
  fi

  node -e "
    const fs = require('fs');
    eval(fs.readFileSync('$DATA', 'utf8'));

    const before = fs.existsSync('$before_file') ? fs.readFileSync('$before_file', 'utf8') : '';
    const after = fs.existsSync('$after_file') ? fs.readFileSync('$after_file', 'utf8') : '';
    const markers = MARKERS['$scenario'];

    function check(text, pat) {
      const isAnti = pat.startsWith('!');
      if (isAnti) pat = pat.slice(1);
      const parts = pat.split('|');
      let found = false;
      for (const p of parts) {
        try { if (new RegExp(p, 'i').test(text)) { found = true; break; } }
        catch(e) { if (text.toLowerCase().includes(p.toLowerCase())) { found = true; break; } }
      }
      return isAnti ? !found : found;
    }

    let bPass = 0, aPass = 0, regs = 0, imps = 0;
    const rows = [];

    for (const [name, pattern, cat] of markers) {
      const b = before ? check(before, pattern) : false;
      const a = after ? check(after, pattern) : false;
      if (b) bPass++;
      if (a) aPass++;

      let delta;
      if (b && a) delta = '  ≡ Both pass';
      else if (!b && !a) delta = '  ≡ Both miss';
      else if (b && !a) { delta = '  ▼ REGRESSION'; regs++; }
      else { delta = '  ▲ IMPROVEMENT'; imps++; }

      const bStr = b ? '✅' : '❌';
      const aStr = a ? '✅' : '❌';
      rows.push({ name, cat, bStr, aStr, delta, b, a });
    }

    const total = markers.length;
    const bPct = before ? Math.round(bPass * 100 / total) : 0;
    const aPct = after ? Math.round(aPass * 100 / total) : 0;

    // Print table
    const pad = (s, n) => (s + ' '.repeat(n)).slice(0, n);
    console.log(pad('Quality Marker', 40) + pad('Cat', 14) + pad('BEFORE', 10) + pad('AFTER', 10) + 'Delta');
    console.log('─'.repeat(90));
    for (const r of rows) {
      console.log(pad(r.name, 40) + pad(r.cat, 14) + pad(r.bStr, 10) + pad(r.aStr, 10) + r.delta);
    }
    console.log('─'.repeat(90));

    // Scores
    console.log('');
    if (before) console.log('BEFORE: ' + bPass + '/' + total + ' (' + bPct + '%)');
    else console.log('BEFORE: (no file)');
    if (after) console.log('AFTER:  ' + aPass + '/' + total + ' (' + aPct + '%)');
    else console.log('AFTER:  (no file)');

    // Verdict
    console.log('');
    if (regs === 0) console.log('✅ EQUIVALENT OR BETTER — ' + (imps > 0 ? imps + ' improvement(s), ' : '') + 'no regressions');
    else if (regs <= 2) console.log('⚠️  MINOR GAPS — ' + regs + ' regression(s)');
    else console.log('❌ QUALITY REGRESSION — ' + regs + ' markers lost');
  "
}

echo -e "${BOLD}Ship Framework — E2E Quality Comparison${NC}"
echo -e "${DIM}Scoring from .md files in prompts/outputs/${NC}"

scenario="${1:-all}"

if [ "$scenario" = "all" ]; then
  for s in $ALL_SCENARIOS; do
    score_scenario "$s"
  done
else
  score_scenario "$scenario"
fi

echo ""

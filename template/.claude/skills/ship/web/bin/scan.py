#!/usr/bin/env python3
"""Ship's web scan: deterministic checks for the tells of generated UI and for quality defects,
on a running page or on web source files.

  scan.py <targets…> [--viewport WxH] [--json]

Targets: the running dev-server URL (best: it scans the rendered page), or the changed
.html .css .jsx .tsx .vue .svelte .astro files or their folder. `--viewport 390x844` adds a phone pass
on a URL.

Output: one line per finding (severity, rule, where, what); `--json` prints the raw list of
{antipattern, name, description, severity, category, file, line, snippet}. Exit: 0 clean,
2 findings, 1 a target couldn't be scanned, 3 the scan isn't available here (the reason is printed).

It reads only and writes no files. The engine is an open-source scanner (Apache-2.0) run through
npx: Node 22.18 or newer, and its first run downloads it.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

ENGINE = ["npx", "-y", "impeccable@4", "detect", "--json"]   # pinned major; maintainers/upstreams.yaml


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--viewport")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if not shutil.which("npx"):
        print("web scan: unavailable (needs Node 22.18 or newer with npx)")
        return 3
    cmd = ENGINE + ([f"--viewport", a.viewport] if a.viewport else []) + a.targets
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        print("web scan: unavailable (timed out; offline on its first run?)")
        return 3
    if res.returncode not in (0, 1, 2):
        print(f"web scan: unavailable (engine exit {res.returncode})")
        return 3
    out = res.stdout.strip()
    try:
        findings = json.loads(out[out.index("["):]) if "[" in out else []
    except ValueError:
        print("web scan: unavailable (unreadable output)")
        return 3
    if a.json:
        print(json.dumps(findings, indent=1))
        return res.returncode
    if res.returncode == 1:
        print("web scan: a target couldn't be scanned — " + (res.stderr.strip().splitlines() or [""])[-1][:200])
    if not findings:
        print("web scan: clean (evidence, not proof)")
        return res.returncode
    print(f"web scan: {len(findings)} finding(s)")
    for f in findings:
        where = f.get("file") or "page"
        if os.path.isabs(where):
            where = os.path.relpath(where)
        if f.get("line"):
            where += f":{f['line']}"
        print(f"  {f.get('severity', '?'):8} {f.get('antipattern', '?'):28} {where}  {f.get('description', '')[:160]}")
    return res.returncode


if __name__ == "__main__":
    sys.exit(main())

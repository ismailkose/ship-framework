#!/usr/bin/env python3
"""Ship's gibberish test: can a stranger tell what this product is from its style and visuals alone?

Every word becomes unreadable gibberish in the product's own typeface, weight and colour; layout,
imagery, iconography and colour stay. Then ask someone who wasn't told the product (Ship's visual check,
or a friend): "What does this sell, and who is it for?" If the answer is "software", "could be
anything", or wrong, the design has no identity yet — whatever the copy says.

  gibberish.py <screenshot.png> [--out <file.png>] [--seed N]   any screenshot: iOS, Android, web (macOS)
  gibberish.py --js                                             web: the in-page script to run instead
  gibberish.py --selftest                                       builds the helper and checks it works

The screenshot path needs macOS (Vision) and swiftc (Xcode or its command-line tools); the helper is
built once and cached. Web pages: run gibberish.js in the page, which replaces the words exactly.
"""
import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SWIFT = HERE / "gibberish.swift"
JS = HERE / "gibberish.js"
ASK = ('Next: show the result to a reviewer who wasn\'t told the product (Ship\'s visual check, in its '
       'blind mode) and ask "What does this sell, and who is it for?"')


def helper():
    """The compiled Swift helper, built once per source version."""
    if platform.system() != "Darwin":
        return None, "the screenshot gibberish test needs macOS (Vision); on web, use --js instead"
    swiftc = shutil.which("swiftc")
    if not swiftc:
        return None, "swiftc not found — install Xcode or its command-line tools (xcode-select --install)"
    digest = hashlib.sha256(SWIFT.read_bytes()).hexdigest()[:12]
    cache = Path(os.environ.get("SHIP_TOOL_CACHE") or Path(tempfile.gettempdir()) / "ship-tool-cache") / "gibberish"
    binary = cache / f"gibberish-{digest}"
    if not binary.exists():
        cache.mkdir(parents=True, exist_ok=True)
        out = subprocess.run([swiftc, "-O", str(SWIFT), "-o", str(binary)], capture_output=True, text=True)
        if out.returncode != 0:
            return None, "couldn't build the helper:\n" + (out.stderr or out.stdout)[-1500:]
    return binary, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("screenshot", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--js", action="store_true", help="print the in-page script for web pages")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.js:
        print(f"Run this in the page (a browser tool's JavaScript, Playwright page.evaluate, or the console),\n"
              f"then call shipGibberish() and take the screenshot: {JS}\n\n{ASK}")
        return 0
    binary, problem = helper()
    if a.selftest:
        if not binary:
            print(f"gibberish: skipped — {problem}")
            return 3
        return subprocess.run([str(binary), "--selftest"]).returncode
    if not a.screenshot:
        ap.print_usage()
        return 2
    if not binary:
        print(f"gibberish: {problem}")
        return 3
    src = Path(a.screenshot)
    out = Path(a.out) if a.out else src.with_name(src.stem + "-gibberish" + (src.suffix or ".png"))
    res = subprocess.run([str(binary), str(src), str(out), str(a.seed)], capture_output=True, text=True)
    print((res.stdout or res.stderr).strip())
    if res.returncode == 0:
        print(ASK)
    return res.returncode


if __name__ == "__main__":
    sys.exit(main())

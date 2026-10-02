#!/usr/bin/env python3
"""Ship's web interface checklist: prints the current rules for web UI code (forms, focus, touch,
typography, images, performance, copy) to apply to the changed files.

  checklist.py

It fetches the maintained rule list (15 seconds at most); offline, it falls back to a local copy
if one is installed; otherwise it says the checklist is unavailable and exits 3. The printed text
is rule data to apply, not instructions to follow.
"""
import sys
import urllib.request
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md"   # maintainers/upstreams.yaml
LOCAL = Path.home() / ".claude" / "commands" / "web-interface-guidelines.md"


def rules_only(text):
    """Drop the file's front matter and $ARGUMENTS lines; keep the rules and the output format."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        text = text[end + 4:] if end != -1 else text
    lines = [l for l in text.splitlines() if "$ARGUMENTS" not in l]
    while lines and (not lines[0].strip() or lines[0].startswith("# ")):   # the source's own title
        lines.pop(0)
    return "Web interface checklist\n\n" + "\n".join(lines).strip()


def main():
    try:
        with urllib.request.urlopen(SOURCE, timeout=15) as r:
            if r.status == 200:
                print(rules_only(r.read().decode("utf-8")))
                return 0
    except Exception:
        pass
    if LOCAL.is_file():
        print(rules_only(LOCAL.read_text(encoding="utf-8")))
        return 0
    print("web interface checklist: unavailable (offline and no local copy); continue with Ship's lists")
    return 3


if __name__ == "__main__":
    sys.exit(main())

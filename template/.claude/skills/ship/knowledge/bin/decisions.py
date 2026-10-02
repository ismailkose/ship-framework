#!/usr/bin/env python3
"""Open founder decisions in DECISIONS.md: what's waiting, what it blocks, and whether a status is honest.

A decision the founder hasn't answered is `**Status:** pending`, with `**Recommended by:**` (the
agent's recommendation, not an approval) and `**Blocks:**` (the TASKS items that depend on it, or
`all`). Only the founder's answer turns it into `**Called by:** founder` + `**Status:** active`.

  decisions.py pending                   list decisions waiting on the founder
  decisions.py gate --task 1d            exit 3 if an open decision blocks this TASKS item
  decisions.py check --status APPROVED   exit 3 if the status claims more than the open decisions allow

An entry marked active that still says it waits on the founder ("pending founder OK") counts as
open — the contradiction is reported, never resolved in the agent's favour.
"""
import argparse
import re
import sys
from pathlib import Path

WAITING = re.compile(r"\b(pending|awaiting|waiting on|needs? (the )?founder|founder'?s? (ok|call|answer|approval))\b", re.I)
FIELD = re.compile(r"^\*\*([A-Za-z ]+):\*\*\s*(.*)$")
CLAIMS_APPROVAL = {"APPROVED", "DONE"}


def entries(text):
    """Each `## ` entry → {title, fields}. Comments (the format template) are skipped."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for block in re.split(r"(?m)^## ", text)[1:]:
        lines = block.splitlines()
        fields = {}
        for line in lines[1:]:
            m = FIELD.match(line.strip())
            if m:
                fields[m.group(1).strip().lower()] = m.group(2).strip()
        out.append({"title": lines[0].strip(), "fields": fields})
    return out


def open_decisions(text):
    """Decisions still waiting on the founder, with what they block and why they count as open."""
    found = []
    for e in entries(text):
        f = e["fields"]
        status = f.get("status", "").lower()
        if status.startswith(("reversed", "superseded")):
            continue
        says_waiting = WAITING.search(f.get("called by", "")) or WAITING.search(f.get("status", ""))
        if status.startswith("pending"):
            why = "pending"
        elif says_waiting:
            why = "marked active, but says it waits on the founder — ask, or mark it pending"
        else:
            continue
        blocks = [b.strip().lower() for b in re.split(r"[,;]\s*|\s+and\s+", f.get("blocks", "")) if b.strip()]
        found.append({"title": e["title"], "why": why, "blocks": blocks or ["all"],
                      "recommended": f.get("recommended by") or f.get("called by", "")})
    return found


def blocks_task(d, task):
    return "all" in d["blocks"] or task.lower() in d["blocks"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["pending", "gate", "check"])
    ap.add_argument("--file", default="DECISIONS.md")
    ap.add_argument("--task", help="TASKS item id, e.g. 1d")
    ap.add_argument("--status", help="the workflow status about to be printed")
    a = ap.parse_args(argv)
    path = Path(a.file)
    open_ = open_decisions(path.read_text(encoding="utf-8")) if path.exists() else []

    if a.cmd == "pending":
        for d in open_:
            print(f"OPEN  {d['title']} — {d['why']}; blocks: {', '.join(d['blocks'])}")
        print(f"{len(open_)} open decision(s)" if open_ else "No open decisions.")
        return 0

    if a.cmd == "gate":
        if not a.task:
            ap.error("gate needs --task")
        blocking = [d for d in open_ if blocks_task(d, a.task)]
        for d in blocking:
            hint = "" if d["blocks"] != ["all"] else " (no **Blocks:** line, so it blocks everything — list the items it affects to free the rest)"
            print(f"BLOCKED {a.task}: waits on \"{d['title']}\" — {d['why']}{hint}")
        if blocking:
            print("Build items that don't depend on it, or ask the founder this one question.")
            return 3
        print(f"OK {a.task}: no open decision blocks it.")
        return 0

    if not a.status:
        ap.error("check needs --status")
    if a.status.upper() in CLAIMS_APPROVAL and open_:
        for d in open_:
            print(f"CONTRADICTION: STATUS {a.status.upper()} while \"{d['title']}\" is open — {d['why']}")
        print("Use BLOCKED, name the open decision and the items that can start without it.")
        return 3
    print(f"OK: STATUS {a.status.upper()} is consistent with {len(open_)} open decision(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

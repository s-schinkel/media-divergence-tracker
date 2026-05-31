#!/usr/bin/env python3
"""Update the "Last updated: YYYY-MM-DD" line on the root Erika Kirk tracker.

The Erika tracker's served page is the repository-root index.html, which is
hand-maintained (no JSON->HTML regenerator — see ../CLAUDE.md). This script owns
just the footer date string, so a refresh can stamp the page without touching
anything else.

Usage:
  python3 scripts/bump_date.py                 # date = today (UTC/local)
  python3 scripts/bump_date.py --date 2026-06-07

Run from anywhere; the root index.html path is resolved relative to this file.
Exits non-zero if the "Last updated" line can't be found.
"""

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

ROOT_INDEX = Path(__file__).resolve().parents[2] / "index.html"   # repo-root index.html


def main():
    ap = argparse.ArgumentParser(description="Bump the root Erika tracker's 'Last updated' date")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    args = ap.parse_args()

    date = args.date or _dt.date.today().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        sys.exit(f"ERROR: --date must be YYYY-MM-DD, got {date!r}")

    if not ROOT_INDEX.exists():
        sys.exit(f"ERROR: {ROOT_INDEX} not found")

    html = ROOT_INDEX.read_text(encoding="utf-8")
    new, n = re.subn(r"Last updated: \d{4}-\d{2}-\d{2}", f"Last updated: {date}", html)
    if n == 0:
        sys.exit("ERROR: 'Last updated: <date>' string not found in root index.html")
    if new == html:
        print(f"Already at {date} — no change.")
        return
    ROOT_INDEX.write_text(new, encoding="utf-8")
    print(f"Root Erika tracker 'Last updated' → {date}")


if __name__ == "__main__":
    main()

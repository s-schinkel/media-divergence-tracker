#!/usr/bin/env python3
"""Refresh the Iran/Middle East tracker from the JSON source of record.

Source of truth = middle-east/data/*.json (volume, events, posture, detail).
This script:
  1. validates those files (shape, taxonomy keys, posture classes, month coverage),
  2. regenerates the inline data block in middle-east/index.html (between the
     /* DATA:START */ and /* DATA:END */ markers) so the served artifact stays
     self-contained — you edit the JSON, never the HTML data block,
  3. recomputes middle-east/data/meta.json (row counts + coverage + last_updated),
     which drives the "Last updated" pill + staleness banner in this tracker.

The root Erika tracker owns its own "Last updated" line — see erika-kirk/scripts/bump_date.py.
This script only touches the Middle East tracker.

Usage:
  python3 scripts/build_dataset.py                 # full rebuild, date = today
  python3 scripts/build_dataset.py --date 2026-06-07
  python3 scripts/build_dataset.py --date-only     # only bump meta.json

Run from anywhere; paths are resolved relative to this file.
Exits non-zero (and writes nothing) if validation fails.
"""

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # middle-east/scripts
ME = HERE.parent                                 # middle-east
REPO = ME.parent                                 # repo root
DATA = ME / "data"
ME_INDEX = ME / "index.html"

EVENT_TYPES = {"us_israel_strike", "iran_strike", "diplomatic", "protest", "statement", "policy"}
US_POSTURE = {"Threatening", "Hawkish", "Neutral", "Diplomatic", "Conciliatory"}
OTHER_POSTURE = {"Hostile", "Cautious", "Neutral", "Engaged", "Conciliatory"}
TONE_CODES = {"E", "N", "D", "EN", "ND"}
LEADERS = {"trump", "starmer", "albanese", "ca_pm", "netanyahu", "iran", "mbs", "kallas"}

DATA_START = "/* DATA:START"
DATA_END = "/* DATA:END */"


def _load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def validate(volume, events, posture, detail):
    """Return (errors, months). errors is a list; empty means OK."""
    errs = []
    months = [d.get("month") for d in volume]

    # volume
    if len(months) != len(set(months)):
        errs.append("volume.json: duplicate months")
    if months != sorted(months):
        errs.append("volume.json: months not in ascending order")
    for d in volume:
        for k in ("uk", "usa", "au", "ca"):
            if not isinstance(d.get(k), int):
                errs.append(f"volume.json {d.get('month')}: '{k}' is not an integer")

    mset = set(months)

    # detail
    if set(detail.keys()) != mset:
        miss = mset - set(detail.keys())
        extra = set(detail.keys()) - mset
        errs.append(f"detail.json: month mismatch (missing {sorted(miss)}, extra {sorted(extra)})")
    for m, rec in detail.items():
        for c in ("uk", "usa", "au", "ca"):
            cell = rec.get(c, {})
            if cell.get("tone") not in TONE_CODES:
                errs.append(f"detail.json {m}/{c}: bad tone code {cell.get('tone')!r}")
            if not isinstance(cell.get("topics"), list) or not cell.get("topics"):
                errs.append(f"detail.json {m}/{c}: topics missing/empty")

    # events
    for e in events:
        if e.get("type") not in EVENT_TYPES:
            errs.append(f"events.json {e.get('date')}: bad type {e.get('type')!r}")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(e.get("date", ""))):
            errs.append(f"events.json: bad date {e.get('date')!r}")
        elif e["date"][:7] not in mset:
            errs.append(f"events.json {e['date']}: month outside coverage")
        for k in ("actor", "description", "source"):
            if not e.get(k):
                errs.append(f"events.json {e.get('date')}: missing '{k}'")

    # posture
    for p in posture:
        if p.get("leader") not in LEADERS:
            errs.append(f"posture.json {p.get('month')}: unknown leader {p.get('leader')!r}")
        if p.get("month") not in mset:
            errs.append(f"posture.json: month {p.get('month')!r} outside coverage")
        allowed = US_POSTURE if p.get("leader") == "trump" else OTHER_POSTURE
        if p.get("posture") not in allowed:
            errs.append(f"posture.json {p.get('month')}/{p.get('leader')}: bad posture {p.get('posture')!r}")

    return errs, months


def _js_const(name, obj):
    dumped = json.dumps(obj, ensure_ascii=False, indent=2)
    lines = dumped.split("\n")
    body = "\n".join((("  " + ln) if i else ln) for i, ln in enumerate(lines))
    return f"  const {name} = {body};"


def regen_index(volume, events, posture, detail, months):
    html = ME_INDEX.read_text(encoding="utf-8")
    if DATA_START not in html or DATA_END not in html:
        raise SystemExit("ERROR: DATA:START / DATA:END markers not found in index.html — add them once before first run.")
    pre, rest = html.split(DATA_START, 1)
    _, post = rest.split(DATA_END, 1)
    block = (
        DATA_START + " — generated from data/*.json by scripts/build_dataset.py; edit the JSON, not this block */\n"
        + _js_const("MONTHS", months) + "\n\n"
        + _js_const("VOLUME_DATA", volume) + "\n\n"
        + _js_const("EVENTS_DATA", events) + "\n\n"
        + _js_const("DETAIL", detail) + "\n\n"
        + _js_const("POSTURE_DATA", posture) + "\n  "
        + DATA_END
    )
    ME_INDEX.write_text(pre + block + post, encoding="utf-8")


def update_meta(volume, events, posture, months, date):
    meta_path = DATA / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta.update({
        "last_updated": date,
        "coverage_start": months[0],
        "coverage_end": months[-1],
        "volume_rows": len(volume),
        "events_rows": len(events),
        "posture_rows": len(posture),
    })
    meta.setdefault("note", "Volumes are search-signal approximations. 2026 events verified against primary wire sources.")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Refresh the Iran/Middle East tracker from data/*.json")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--date-only", action="store_true", help="only bump meta.json last_updated; skip data validation/regen")
    args = ap.parse_args()

    date = args.date or _dt.date.today().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        sys.exit(f"ERROR: --date must be YYYY-MM-DD, got {date!r}")

    volume = _load("volume.json")
    events = _load("events.json")
    posture = _load("posture.json")
    detail = _load("detail.json")
    months = [d["month"] for d in volume]

    if args.date_only:
        update_meta(volume, events, posture, months, date)
        print(f"date-only refresh → {date}  (meta.json)")
        return

    errs, months = validate(volume, events, posture, detail)
    if errs:
        print("VALIDATION FAILED — nothing written:", file=sys.stderr)
        for e in errs:
            print("  -", e, file=sys.stderr)
        sys.exit(1)

    regen_index(volume, events, posture, detail, months)
    update_meta(volume, events, posture, months, date)
    print("Rebuilt artifact from data/*.json")
    print(f"  months   : {months[0]} … {months[-1]}  ({len(months)})")
    print(f"  volume   : {len(volume)} rows")
    print(f"  events   : {len(events)} rows")
    print(f"  posture  : {len(posture)} rows")
    print(f"  updated  : {date}")
    print("  wrote    : middle-east/index.html, data/meta.json")


if __name__ == "__main__":
    main()

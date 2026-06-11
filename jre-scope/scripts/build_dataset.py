#!/usr/bin/env python3
"""Validate jre-scope/data/episodes.json and inject it into jre-scope/index.html.

data/episodes.json is the source of record. index.html carries the same data inline
between the `/* DATA:START */` and `/* DATA:END */` markers — that block is GENERATED;
never edit it by hand. Usage:

    cd jre-scope
    python3 scripts/build_dataset.py            # validate -> regenerate index.html
    python3 scripts/build_dataset.py --check    # validate only, write nothing

Validates: canonical topic tags, required fields, ISO dates, episode ordering,
appearance-count consistency. Writes nothing on failure.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "episodes.json"
HTML = ROOT / "index.html"

TAGS = {"COMEDY", "POLITICS_LEFT", "POLITICS_RIGHT", "SCIENCE", "MEDICINE",
        "HEALTH_FITNESS", "MMA_COMBAT", "SPORT_OTHER", "MUSIC", "FILM_TV",
        "MILITARY_INTEL", "TECH_AI", "PHILOSOPHY", "CRIME_TRUE_CRIME", "BUSINESS",
        "ENVIRONMENT", "CONSPIRACY", "HISTORY", "SOLO_EPISODE", "OTHER"}
REQUIRED = {"ep", "title", "guest", "guests", "air_date", "topic_tag",
            "views", "return_guest", "total_appearances", "appearance_n"}
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def validate(doc):
    eps = doc.get("episodes")
    meta = doc.get("meta", {})
    if not eps:
        fail("no episodes")
    prev = 0
    for e in eps:
        missing = REQUIRED - set(e)
        if missing:
            fail(f"ep {e.get('ep')}: missing fields {sorted(missing)}")
        if e["topic_tag"] not in TAGS:
            fail(f"ep {e['ep']}: bad tag {e['topic_tag']!r}")
        if not ISO.match(e["air_date"] or ""):
            fail(f"ep {e['ep']}: bad air_date {e['air_date']!r}")
        if e["ep"] <= prev:
            fail(f"ep {e['ep']}: out of order (after {prev})")
        if not (1 <= e["appearance_n"] <= e["total_appearances"]):
            fail(f"ep {e['ep']}: appearance_n {e['appearance_n']} > total {e['total_appearances']}")
        if e["return_guest"] != (e["appearance_n"] > 1):
            fail(f"ep {e['ep']}: return_guest inconsistent with appearance_n")
        prev = e["ep"]
    for k in ("first_ep", "last_ep", "generated", "source_notes"):
        if k not in meta:
            fail(f"meta missing {k!r}")
    if meta["first_ep"] != eps[0]["ep"] or meta["last_ep"] != eps[-1]["ep"]:
        fail("meta first_ep/last_ep do not match episode list")
    print(f"OK: {len(eps)} episodes #{meta['first_ep']}-#{meta['last_ep']}, "
          f"{sum(1 for e in eps if e['views'] is not None)} with views, "
          f"generated {meta['generated']}")


def inject(doc):
    html = HTML.read_text(encoding="utf-8")
    blob = json.dumps(doc, separators=(",", ":"), ensure_ascii=False)
    new = re.sub(
        r"(/\* DATA:START \*/\n).*?(\n/\* DATA:END \*/)",
        lambda m: m.group(1) + "const DATA = " + blob + ";" + m.group(2),
        html, count=1, flags=re.S)
    if new == html:
        print("index.html unchanged")
        return
    if "/* DATA:START */" not in new:
        fail("DATA markers not found in index.html")
    HTML.write_text(new, encoding="utf-8")
    print(f"wrote {HTML} ({len(blob):,} bytes of data)")


def main():
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    validate(doc)
    if "--check" not in sys.argv:
        inject(doc)


if __name__ == "__main__":
    main()

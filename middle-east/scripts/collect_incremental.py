#!/usr/bin/env python3
"""Collect new months of Iran/Middle East tracker data via the Claude API + web search.

Fetches every month between meta.json's `coverage_end` (exclusive) and today (inclusive),
asks Claude (with the web_search server tool) to research each month, validates the returned
JSON against the taxonomy in ../CLAUDE.md, and merges it into data/*.json. build_dataset.py
then rebuilds index.html from the updated JSON.

USAGE:
  python3 scripts/collect_incremental.py            # collect + merge
  python3 scripts/collect_incremental.py --dry-run  # fetch + validate + print, do NOT merge

Requires ANTHROPIC_API_KEY in the environment (only when there are months to collect).
Model: claude-opus-4-6, max_tokens 8000, web_search_20260209, adaptive thinking.

Month-selection rule: every YYYY-MM strictly after coverage_end up to and including the
current month; the current month is excluded if today is before the 20th (too little signal).
"""

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # middle-east/scripts
ME = HERE.parent                                 # middle-east
DATA = ME / "data"

MODEL = "claude-opus-4-6"
MAX_TOKENS = 8000

# --- taxonomy / scales (must match ../CLAUDE.md) ---
EVENT_TYPES = {"us_israel_strike", "iran_strike", "diplomatic", "protest", "statement", "policy"}
TONE_CODES = {"E", "N", "D", "EN", "ND"}
US_POSTURE = {"Threatening", "Hawkish", "Neutral", "Diplomatic", "Conciliatory"}
OTHER_POSTURE = {"Hostile", "Cautious", "Neutral", "Engaged", "Conciliatory"}
LEADERS = {"trump", "starmer", "albanese", "ca_pm", "netanyahu", "iran", "mbs", "kallas"}
COUNTRIES = ("uk", "usa", "au", "ca")

MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

SYSTEM_PROMPT = """You are a media-and-conflict data researcher for an interactive tracker of \
Iran / Middle East coverage. For the single month you are given, use the web_search tool to \
research real coverage and events, then return the data as ONE JSON object.

Collect, for that month:

A. MEDIA VOLUME per country — UK, USA, AU, CA — an APPROXIMATE relative story-count integer \
(no Factiva/LexisNexis; estimate from search-signal density; the June-2025 12-day war is the \
series peak for calibration). Outlets:
  UK : BBC News, The Guardian, The Times, Sky News, The Telegraph, The Independent
  USA: New York Times, Washington Post, Reuters, AP, Fox News, Politico, Wall Street Journal
  AU : ABC News (Australia), Sydney Morning Herald, The Australian, The Age, Guardian Australia, SBS News
  CA : The Globe and Mail, CBC News, National Post, Toronto Star, CTV News

B. DETAIL per country — exactly 3 dominant-topic bullet points, and a tone code:
   E = Escalatory(+1), N = Neutral(0), D = De-escalatory(-1), EN = mixed esc/neutral, ND = mixed neutral/de-esc.

C. POSTURE — for each leader with a notable, findable Iran statement/action this month, using \
the leader's slug and class. Trump uses the US scale; all others use the non-US scale. Omit a \
leader entirely if there is no signal (do NOT interpolate).
   leader slugs : trump, starmer (UK PM), albanese (AU PM), ca_pm (Canada PM), netanyahu, iran (Supreme Leader; note Pezeshkian divergence in summary), mbs, kallas (EU High Rep)
   US scale     (trump only): Threatening, Hawkish, Neutral, Diplomatic, Conciliatory
   non-US scale (all others): Hostile, Cautious, Neutral, Engaged, Conciliatory

D+E. EVENTS — new confirmed kinetic strikes and flash-point events this month. type must be \
one of: us_israel_strike, iran_strike (direct strikes); diplomatic, protest, policy, statement \
(flash points). Use actor "USA+Israel" for clearly-joint operations. target_type only for \
strikes (nuclear facility / military base / naval / drone-missile / other), else null.

Return ONLY the JSON object below — no preamble, no markdown fences, no trailing commentary:

{
  "month": "YYYY-MM",
  "volume": {"uk": 0, "usa": 0, "au": 0, "ca": 0},
  "detail": {
    "uk": {"tone": "N", "topics": ["...", "...", "..."]},
    "usa": {"tone": "N", "topics": ["...", "...", "..."]},
    "au":  {"tone": "N", "topics": ["...", "...", "..."]},
    "ca":  {"tone": "N", "topics": ["...", "...", "..."]}
  },
  "posture": [
    {"leader": "trump", "posture": "Hawkish", "summary": "...", "source": "..."}
  ],
  "events": [
    {"date": "YYYY-MM-DD", "type": "diplomatic", "actor": "...", "target_type": null, "description": "...", "source": "..."}
  ]
}

If a month has thin coverage, still return best-effort approximate volumes and note the thinness \
in the topics. Prefer primary/major-outlet sources."""


# ----------------------------------------------------------------------------- month selection
def months_to_collect(coverage_end, today):
    """Every YYYY-MM strictly after coverage_end through the current month; drop the
    current month if today is before the 20th."""
    cur_ym = today.strftime("%Y-%m")
    y, m = (int(x) for x in coverage_end.split("-"))
    out = []
    while True:
        m += 1
        if m > 12:
            m, y = 1, y + 1
        ym = f"{y:04d}-{m:02d}"
        if ym > cur_ym:
            break
        out.append(ym)
    if out and out[-1] == cur_ym and today.day < 20:
        out.pop()  # current partial month — too little signal
    return out


# ----------------------------------------------------------------------------- API
def collect_month(ym):
    """Call Claude with web search for one month; return the parsed JSON dict (or raise)."""
    import anthropic  # lazy — the no-op path must run without the SDK installed

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    y, m = (int(x) for x in ym.split("-"))
    user = (f"Collect the Iran / Middle East media & conflict data for {MONTH_NAMES[m]} {y} "
            f"(month \"{ym}\"). Research with web search, then return the JSON object for this month only.")
    system = [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}]
    tools = [{"type": "web_search_20260209", "name": "web_search"}]
    messages = [{"role": "user", "content": user}]

    resp = None
    for _ in range(6):  # server web-search loop can return pause_turn at its iteration cap
        resp = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=system, tools=tools, messages=messages,
        )
        if resp.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": resp.content})
            continue
        break

    if resp.stop_reason == "max_tokens":
        print(f"  ⚠ {ym}: response hit max_tokens ({MAX_TOKENS}) — JSON may be truncated.")
    text = "".join(b.text for b in resp.content if b.type == "text")
    # strip fences / preamble, isolate the JSON object
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        raise ValueError(f"no JSON object found in response for {ym}")
    return json.loads(text[s:e + 1])


# ----------------------------------------------------------------------------- validation
def validate_month(ym, d):
    """Return a list of warning strings (does not abort)."""
    w = []
    if d.get("month") != ym:
        w.append(f"month field is {d.get('month')!r}, expected {ym!r}")
    vol = d.get("volume", {})
    for c in COUNTRIES:
        if not isinstance(vol.get(c), int):
            w.append(f"volume.{c} is not an integer ({vol.get(c)!r})")
    det = d.get("detail", {})
    for c in COUNTRIES:
        cell = det.get(c, {})
        if cell.get("tone") not in TONE_CODES:
            w.append(f"detail.{c}.tone invalid: {cell.get('tone')!r}")
        topics = cell.get("topics")
        if not isinstance(topics, list) or len(topics) != 3:
            w.append(f"detail.{c}.topics should be 3 bullets (got {topics!r})")
    for p in d.get("posture", []):
        leader = p.get("leader")
        if leader not in LEADERS:
            w.append(f"posture: unknown leader {leader!r}")
        allowed = US_POSTURE if leader == "trump" else OTHER_POSTURE
        if p.get("posture") not in allowed:
            w.append(f"posture[{leader}]: invalid class {p.get('posture')!r}")
        if not p.get("summary") or not p.get("source"):
            w.append(f"posture[{leader}]: missing summary/source")
    for ev in d.get("events", []):
        if ev.get("type") not in EVENT_TYPES:
            w.append(f"event {ev.get('date')}: invalid type {ev.get('type')!r}")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(ev.get("date", ""))):
            w.append(f"event: bad date {ev.get('date')!r}")
        for k in ("actor", "description", "source"):
            if not ev.get(k):
                w.append(f"event {ev.get('date')}: missing {k!r}")
    return w


# ----------------------------------------------------------------------------- merge
def _load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def _write(name, obj):
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def merge_month(d):
    ym = d["month"]
    volume = _load("volume.json")
    events = _load("events.json")
    posture = _load("posture.json")
    detail = _load("detail.json")

    volume = [r for r in volume if r.get("month") != ym]  # idempotent: drop any prior copy
    volume.append({"month": ym, **{c: d["volume"][c] for c in COUNTRIES}})
    volume.sort(key=lambda r: r["month"])

    detail[ym] = {c: {"tone": d["detail"][c]["tone"], "topics": d["detail"][c]["topics"]} for c in COUNTRIES}

    events = [e for e in events if e.get("date", "")[:7] != ym]
    for ev in d.get("events", []):
        events.append({"date": ev["date"], "type": ev["type"], "actor": ev["actor"],
                       "target_type": ev.get("target_type"), "description": ev["description"],
                       "source": ev["source"]})
    events.sort(key=lambda e: e["date"])

    posture = [p for p in posture if p.get("month") != ym]
    for p in d.get("posture", []):
        posture.append({"month": ym, "leader": p["leader"], "posture": p["posture"],
                        "summary": p["summary"], "source": p["source"]})

    _write("volume.json", volume)
    _write("detail.json", detail)
    _write("events.json", events)
    _write("posture.json", posture)
    return volume, events, posture


def update_meta(last_month, volume, events, posture, today):
    meta = _load("meta.json")
    meta["coverage_end"] = last_month
    meta["last_updated"] = today
    meta["volume_rows"] = len(volume)
    meta["events_rows"] = len(events)
    meta["posture_rows"] = len(posture)
    _write("meta.json", meta)


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Collect new months for the Iran/Middle East tracker")
    ap.add_argument("--dry-run", action="store_true", help="fetch + validate + print; do not merge")
    args = ap.parse_args()

    meta = _load("meta.json")
    today = _dt.date.today()
    months = months_to_collect(meta["coverage_end"], today)
    if not months:
        print("Coverage is current — nothing to collect")
        return 0

    print(f"Collecting {len(months)} new month(s): {', '.join(months)}"
          + ("  [DRY RUN — no merge]" if args.dry_run else ""))
    collected = []
    for ym in months:
        print(f"\n=== {ym} ===")
        try:
            d = collect_month(ym)
        except Exception as exc:  # don't abort the whole run on one bad month
            print(f"  ✗ failed to collect {ym}: {exc}")
            continue
        warns = validate_month(ym, d)
        for msg in warns:
            print(f"  ⚠ {msg}")
        if args.dry_run:
            print(json.dumps(d, ensure_ascii=False, indent=2))
        collected.append(d)

    if args.dry_run:
        print(f"\nDRY RUN complete — {len(collected)}/{len(months)} month(s) fetched, nothing merged.")
        return 0

    if not collected:
        print("\nNo months were successfully collected — nothing merged.")
        return 1

    last = None
    vol = ev = po = None
    for d in collected:
        vol, ev, po = merge_month(d)
        last = d["month"]
    update_meta(last, vol, ev, po, today.isoformat())

    print("\n=== merged ===")
    for d in collected:
        print(f"  {d['month']}: volume(4) + {len(d.get('posture', []))} posture + {len(d.get('events', []))} events")
    print(f"  meta: coverage_end={last}, volume_rows={len(vol)}, events_rows={len(ev)}, posture_rows={len(po)}")
    print("  Run build_dataset.py to rebuild index.html from the updated JSON.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

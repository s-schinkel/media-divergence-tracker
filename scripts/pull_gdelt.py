#!/usr/bin/env python3
"""Pull mainstream news data for Tab 1 from the GDELT 2.0 DOC API.

Outputs:
  data/gdelt_volume.json   — daily volume-intensity timeline
  data/gdelt_tone.json     — daily tone timeline (-100..+100 raw)
  data/gdelt_monthly.json  — monthly aggregates (vol sum, tone avg)
  data/gdelt_articles/<YYYYMM>.json — top ~25 articles per month

Rate limit: GDELT enforces 1 request per ~5 seconds. This script
spaces calls at 18s to be safe. Total runtime ~3 minutes.

Usage:
  python3 scripts/pull_gdelt.py [--start YYYYMMDD] [--end YYYYMMDD]
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ARTICLES = DATA / "gdelt_articles"
QUERY = '"Erika Kirk"'
BASE = "https://api.gdeltproject.org/api/v2/doc/doc"


def call(params, attempts=4):
    url = f"{BASE}?" + urllib.parse.urlencode({**params, "format": "json"})
    for i in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=45) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            if "Please limit requests" in body:
                wait = 18 * (i + 1)
                print(f"  rate-limited; sleeping {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            return json.loads(body)
        except Exception as e:
            print(f"  attempt {i + 1} failed: {e}", file=sys.stderr)
            time.sleep(10)
    raise RuntimeError(f"GDELT call exhausted retries: {params}")


def fetch_timeline(mode, start, end):
    print(f"Fetching {mode} for {start} → {end}...")
    return call({
        "query": QUERY, "mode": mode,
        "startdatetime": f"{start}000000", "enddatetime": f"{end}235959",
    })


def fetch_articles(start, end, ym):
    out = ARTICLES / f"{ym}.json"
    print(f"  {ym} articles...")
    data = call({
        "query": QUERY, "mode": "artlist", "maxrecords": 25,
        "sort": "hybridrel",
        "startdatetime": f"{start}000000", "enddatetime": f"{end}235959",
    })
    out.write_text(json.dumps(data, indent=2))
    return data


def aggregate_by_month(timeline_json, label):
    series = timeline_json["timeline"][0]["data"]
    monthly = defaultdict(list)
    for point in series:
        ym = point["date"][:6]
        monthly[ym].append(point["value"])
    return {ym: vals for ym, vals in monthly.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="20250701")
    parser.add_argument("--end",   default="20260531")
    args = parser.parse_args()

    DATA.mkdir(exist_ok=True)
    ARTICLES.mkdir(exist_ok=True)

    # 1) Full-range timeline pulls
    vol = fetch_timeline("timelinevol", args.start, args.end)
    (DATA / "gdelt_volume.json").write_text(json.dumps(vol, indent=2))
    time.sleep(18)
    tone = fetch_timeline("timelinetone", args.start, args.end)
    (DATA / "gdelt_tone.json").write_text(json.dumps(tone, indent=2))

    # 2) Aggregate to monthly
    vol_m  = aggregate_by_month(vol,  "vol")
    tone_m = aggregate_by_month(tone, "tone")

    months = sorted(set(vol_m) | set(tone_m))
    summary = {}
    print(f"\n{'Month':<8} {'vol_sum':>10} {'tone_avg':>10}")
    for ym in months:
        v = vol_m.get(ym, [])
        t = [x for x in tone_m.get(ym, []) if x != 0]
        v_sum = sum(v)
        t_avg = sum(t) / len(t) if t else 0.0
        summary[ym] = {"vol_sum": v_sum, "tone_avg": t_avg, "tone_days_nz": len(t)}
        print(f"{ym:<8} {v_sum:>10.4f} {t_avg:>10.3f}")
    (DATA / "gdelt_monthly.json").write_text(json.dumps(summary, indent=2))

    # 3) Per-month article lists (only for months with vol > 0)
    print("\nFetching article lists for active months...")
    for ym in months:
        if summary[ym]["vol_sum"] == 0:
            continue
        time.sleep(18)
        y, m = ym[:4], ym[4:6]
        # last day of month — approximate; GDELT clamps
        last = "31"
        start = f"{ym}01"
        end   = f"{y}{m}{last}"
        fetch_articles(start, end, ym)

    print(f"\nDone. Output in {DATA}/")


if __name__ == "__main__":
    main()

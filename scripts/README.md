# Pull scripts

End-to-end data refresh for both tabs. All scripts read API credentials from environment variables; no secrets in this repo.

## Tab 1 (mainstream vs. social divergence)

```bash
# 1. Pull GDELT volume + tone timelines and per-month article lists
#    Runtime ~3 min (rate-limited at 1 req/5s; this script spaces at 18s)
python3 scripts/pull_gdelt.py

# 2. Score GDELT headlines + curated social snippets via HuggingFace
#    Requires HF token with "Inference Providers" scope (NOT the default
#    read-only scope — see HF settings)
HF_TOKEN=hf_... python3 scripts/score_hf.py

# 3. Combine into Tab 1 composite rows
python3 scripts/build_tab1.py
```

Outputs land in `data/`. Updating `index.html` after a refresh is manual — copy values from `data/tab1_rows.json` into the YT SVG polylines and the `MONTH_DATA` JS object near the bottom of the file.

## Tab 2 (YouTube audience trends)

```bash
# Pull all 8 channels: handle resolution → uploads playlist walk → bulk video stats
# Quota cost: ~150 units (of 10,000/day free). Runtime ~30s.
YT_KEY=AIza... python3 scripts/pull_youtube.py
```

Output: `data/youtube_pull.json` with per-channel monthly view totals. Re-index to Jul 2025 = 100 (or first-active-month = 100 for Real Baron and Josh Hammer) and update the SVG polylines + `YT_DATA` JS object in `index.html`.

## API key setup

**HuggingFace** — https://huggingface.co/settings/tokens → New token → check **"Make calls to Inference Providers"** (the default "Read" scope is not enough).

**YouTube Data API v3** — https://console.cloud.google.com → new project → APIs & Services → Library → enable "YouTube Data API v3" → Credentials → Create credentials → API key. No OAuth needed for public channel reads.

**GDELT** — no key required; rate-limited globally.

## Why `playlistItems.list`, not `search.list`

`search.list` with `publishedAfter` / `publishedBefore` filters costs **100 units per call**. For 8 channels × 11 months that's ~8,800 units before pagination — would blow the daily quota.

`playlistItems.list` walking each channel's uploads playlist costs **1 unit per page of 50 videos**. The full 8-channel pull comes in at ~150 units total. ~60× cheaper.

This is documented inside the methodology section of the artifact too, but worth flagging at the top of any agent's mental model before they pick a quota strategy.

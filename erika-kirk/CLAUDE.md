# CLAUDE.md — agent guidance for the Erika Kirk tracker

Project: a single-file HTML tracker measuring the gap between mainstream news and social media coverage of Erika Kirk (July 2025 → May 2026), plus a companion view of YouTube audience trends across eight commentary channels. Live at https://s-schinkel.github.io/media-divergence-tracker/.

> **This is one of several trackers in the repo.** See the repo-root `../CLAUDE.md` for the
> multi-tracker map. The rules below apply to the Erika Kirk tracker specifically.

> **⚠ The served file is `../index.html` at the REPO ROOT — not in this folder.** It must
> stay at the root, byte-stable, to preserve the externally-shared URL. This `erika-kirk/`
> folder holds only the docs and data pipeline. When you "edit the artifact", you edit
> `../index.html`. Do not move, rename, or relocate it.

## Layout (Erika tracker)

```
<repo root>/
├── index.html              ← the entire artifact (HTML + CSS + SVG + JS, no deps) — SERVED PAGE
└── erika-kirk/             ← this folder: docs + data pipeline for the artifact above
    ├── README.md           ← project overview + reproducibility notes
    ├── CLAUDE.md           ← this file
    ├── scripts/            ← data-pull scripts (Python 3, stdlib only)
    │   ├── pull_gdelt.py
    │   ├── pull_youtube.py
    │   ├── score_hf.py
    │   ├── build_tab1.py
    │   └── README.md       ← how-to-run guide
    └── data/               ← latest pulled snapshots
        ├── gdelt_volume.json
        ├── gdelt_tone.json
        ├── gdelt_monthly.json
        ├── gdelt_articles/<YYYYMM>.json
        ├── hf_results.json
        └── youtube_pull.json
```

The artifact is `../index.html`. Everything renders client-side from data hardcoded in the file. There is no build step, bundler, or runtime dependency.

## Deploy

GitHub Pages auto-rebuilds on every push to `main`. Typical first-byte-after-push latency: 1–2 min. Verify with:

```bash
gh api repos/s-schinkel/media-divergence-tracker/pages/builds/latest --jq '{status, commit, updated_at}'
curl -sI https://s-schinkel.github.io/media-divergence-tracker/ | head -3
```

## Two-tab structure

Top of `index.html`:
- `<nav class="tabs">` with two `<button class="tab-btn" data-tab="tab-N">`
- `<div id="tab-1" class="tab-panel active">` ... `</div>` — Tab 1 (mainstream vs. social)
- `<div id="tab-2" class="tab-panel">` ... `</div>` — Tab 2 (YouTube)

The tab-switching JS is at the bottom of `index.html` inside the single `<script>` block.

## Chart conventions

All chart SVGs use the same X-axis positions (one viewBox-unit per month, 11 months):

```
x = 60 + i * 72   for i in 0..10   →   60, 132, 204, 276, 348, 420, 492, 564, 636, 708, 780
```

Y-axis formulas (panel-specific):

| Panel | viewBox | Y range | Formula |
|---|---|---|---|
| Tab 1 composite | 820×340 | 0.0 to 1.0 | `y = 290 - composite*260` |
| Tab 2 top panel | 820×340 | 0 to 400 | `y = 290 - (idx/400)*260` |
| Tab 2 bottom panel | 820×210 | 0 to 7000 | `y = 170 - (idx/7000)*140` |
| Composite overlay on Tab 2 bottom | (right axis) | 0 to 1 | `y = 170 - composite*140` |

X-axis labels for both Tab 2 panels live inside their respective `<svg>` blocks (not shared) so each chart is readable in isolation.

## Channel color palette (Tab 2)

```
Joe Rogan:           #457b9d  (steel blue)
Ben Shapiro:         #d4a017  (gold)
Candace Owens:       #e63946  (red)
Ian Carroll Show:    #e76f51  (terracotta)
Real Baron Podcast:  #6d597a  (mauve)
Josh Hammer Show:    #2a9d8f  (teal)
Valhalla VFT:        #06b6d4  (cyan)
Paramount Tactical:  #c2410c  (burnt orange)
Tab 1 composite:     #2b59c3  (blue, dashed)
```

Defined in two places:
- CSS `.yt-l-*::before { color: ... }` rules in `<style>` block (for the legend swatches)
- JS `CHANNEL_COLOR` map (for click-card colored dots)

Keep these in sync.

## Click-card data (two JS objects)

`MONTH_DATA` (Tab 1) and `YT_DATA` (Tab 2) live in the `<script>` block at the bottom of `index.html`. Both have the same shape:

```js
const MONTH_DATA = { "202507": { label, composite, confidence, events }, ... };
const YT_DATA    = { "202507": { label, avg, composite, summary, channels: [{name, idx, raw}, ...] }, ... };
```

Click handlers attach to `.chart-point` (Tab 1) and `.yt-point` (Tab 2) — any `<circle>` with these classes is automatically interactive, no per-point JS needed.

## Intentional design choices — DO NOT "fix" without reading the rationale

1. **Paramount Tactical is excluded from the Tab 2 top-panel average.** Its July baseline (9 videos / 55K views) is anomalously low, producing a 60× indexed value in September. Including it in any mean would dominate the average. The 5-channel average is Rogan + Shapiro + Owens + Carroll + Valhalla VFT only. This is explained in the table caption and methodology section inside the artifact.
2. **Real Baron Podcast and Josh Hammer Show are on the bottom panel.** Real Baron didn't exist before September 2025 (no July baseline); Josh Hammer's playlist begins in October. Both are indexed to their own first-active month and shown on the bottom panel because their indexed values go off the top panel's 0–400 scale.
3. **Dual-panel chart, not log scale.** Considered both. Log scale would visually flatten Ben Shapiro's 54% decline, Candace Owens's 1.95× September spike, and other moderate swings — those *are* the story for the top-panel channels. Dual-panel preserves linear-scale legibility while giving the off-scale channels their own visualization.
4. **GDELT volume-intensity, not raw counts.** `mode=timelinevolraw` would give absolute counts but routinely times out for multi-month windows. `timelinevol` (percentage of all monitored articles that match) is GDELT's recommended metric for this kind of analysis. Both are valid; this project standardizes on volume-intensity for consistency.
5. **`playlistItems.list`, not `search.list`.** ~90× cheaper on YouTube Data API quota for the same per-month pull. See `scripts/README.md` for the math.
6. **No frameworks.** Single HTML file, vanilla everything. Adding React/Vue/etc. would require a build step and break the "one-file artifact" property. The artifact has ~1,200 lines and is maintainable as-is.

## When updating the data

Run scripts from inside this `erika-kirk/` folder (paths below are relative to it).

1. Re-run the appropriate pull script (`scripts/pull_gdelt.py` for Tab 1 GDELT side; `scripts/score_hf.py` for sentiment; `scripts/pull_youtube.py` for Tab 2).
2. Outputs land in `erika-kirk/data/` — inspect them.
3. Hand-update the SVG polyline `points="..."` attributes and the `MONTH_DATA` / `YT_DATA` JS objects in `../index.html` (the served file at the repo root). There is no auto-regenerate step.
4. Both tables in each tab (indexed + raw views) also need updating.
5. Open `../index.html` locally to visual-check before pushing.
6. Commit and push to `main`.

## Common task patterns

| Task | Where to edit |
|---|---|
| Add a YouTube channel | `pull_youtube.py` CHANNELS list; then re-run, update Tab 2 SVG + table + YT_DATA + `CHANNEL_COLOR` + CSS `.yt-l-*` rules |
| Update a month's social-volume estimate | `scripts/build_tab1.py` SOCIAL_VOLUME dict; re-run; update the social-mentions column in Tab 1 table |
| Refresh sentiment | re-run `score_hf.py`; update `hf_*_avg` columns in Tab 1 table and the SVG points |
| Change the composite formula | `scripts/build_tab1.py` and the methodology section inside the artifact (search for "composite =") |

## Repo location

Working copy lives at `~/code/media-divergence-tracker` on the maintainer's machine. The
Erika tracker's served file is `index.html` at that repo root; this folder
(`erika-kirk/`) holds its docs and pipeline.

## Caveats inherited from the data layer

These are real and not bugs:
- GDELT's article corpus skews global/tabloid (BoredPanda, IBTimes UK, etc.) — tone is mildly negative across all months.
- `cardiffnlp/twitter-roberta-base-sentiment` can't separate "negative defense" from "negative attack" — Shapiro defending Erika by calling Owens "evil" scores the same as Carroll calling Erika "caught" in a TPUSA "secret."
- YouTube "monthly views" = sum of `viewCount` across videos *published* in that month, as of pull date. Older videos have had longer to accumulate views; the trajectory shape is robust to this but absolute view counts are not stable over time.
- Social-volume estimates are anchored to documented viral events, not real mention counts (no Brandwatch / Talkwalker API).

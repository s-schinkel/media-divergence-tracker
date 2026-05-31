# Media Divergence Tracker — Erika Kirk Coverage

**Live:** https://s-schinkel.github.io/media-divergence-tracker/

> **Where the served file lives:** the page above is served from **`index.html` at the
> repository root**, one level up from this folder — *not* from `erika-kirk/`. That root
> file is the entire self-contained artifact (all data inlined) and must stay at the root
> to keep the externally-shared URL stable. This `erika-kirk/` folder holds the tracker's
> supporting docs and data pipeline only. See the repo-root [`README.md`](../README.md)
> for the multi-tracker layout. To edit the live page, edit `../index.html`.

A single-file HTML tracker measuring the gap between mainstream news and social media coverage of Erika Kirk from July 2025 through May 2026, with a companion view of YouTube audience trends across eight commentary channels over the same window.

**Picking up this project? Read [CLAUDE.md](./CLAUDE.md) first** — it covers repo layout, chart conventions, intentional design choices, and where to edit when refreshing data. The rest of this file is for general readers.

## What this measures

The tracker has two tabs.

### Tab 1 — Mainstream vs. social divergence

A composite divergence score per month, combining three components:

- **Topic overlap** (0–1) — Jaccard of dominant topic clusters between mainstream and social
- **Sentiment delta** — mainstream HF sentiment − social HF sentiment, each on [−1, +1]
- **Volume asymmetry** — `social_mentions / GDELT_volume_intensity`, normalized to September 2025 baseline, log-scaled, capped at 1.0

```
composite = (1 − topic_overlap)    × 0.5
          + abs(sentiment_delta)   × 0.3
          + volume_asymmetry       × 0.2
```

Months where composite > 0.60 are flagged **HIGH DIVERGENCE**. The headline finding: Jan and Feb 2026 are the only HIGH months in the series; the four-month "plateau" implied by my v1 estimates compressed to two months once the data was hardened.

### Tab 2 — YouTube audience trends

Real YouTube Data API v3 numbers for eight channels, each indexed to that channel's first available month (July 2025 = 100 where possible):

| Channel | Channel ID / playlist | Panel | Baseline |
|---|---|---|---|
| Joe Rogan | `UCzQUP1qoWDoEbmsQxvdjxgQ` | Top | Jul = 100 |
| Ben Shapiro | `UCnQC_G5Xsjhp9fEJKuIcrSw` | Top | Jul = 100 |
| Candace Owens | `UCL0u5uz7KZ9q-pe-VC8TY-w` | Top | Jul = 100 |
| Ian Carroll Show | `UCCgpGpylCfrJIV-RwA_L7tg` | Top | Jul = 100 |
| Valhalla VFT | `UCPibkYslKyJFp30ocgPryCA` | Top | Jul = 100 |
| Josh Hammer Show | playlist `PLbJbsiKs77FxKl9EuhpMDR-LgFrPKtlfX` | Top | Oct = 100 |
| Real Baron Podcast | `UCkEowWfq-LO_3EEYYzKoSoA` | Bottom | Sep = 100 |
| Paramount Tactical | `UCWCLMT5T_ondX8VyCdCjOLQ` | Bottom | Jul = 100 |

3,118 videos enumerated; 143 quota units used total (out of 10,000 daily free tier).

Tab 1's composite divergence is overlaid on both YouTube panels for shape comparison.

## Data sources

| Source | What it provides | Cost |
|---|---|---|
| [GDELT 2.0 DOC API](https://api.gdeltproject.org/api/v2/doc/doc) | Mainstream article counts (`timelinevol`), average tone (`timelinetone`), top headlines (`artlist`) | Free; rate-limited 1 req / 5s |
| HuggingFace Inference Providers (`router.huggingface.co/hf-inference`) | Twitter-RoBERTa sentiment scoring on ~280 headlines + social snippets | Free tier; token must have "Inference Providers" scope |
| [YouTube Data API v3](https://developers.google.com/youtube/v3) | Channel resolution, uploads playlist walk, per-video view counts | Free; 10,000 units / day; this project used 143 |
| News reporting | Documented viral events for social-volume anchors (CBS, NPR, CNN, Hollywood Reporter, Media Matters, Snopes, IBTimes UK, etc.) | — |

## How to reproduce

The artifact is a single self-contained HTML file (`index.html`). No build step, no dependencies — open it directly in a browser.

To refresh the data layer (run from this `erika-kirk/` directory):

```bash
cd erika-kirk            # paths below are relative to this folder

# Tab 1 (GDELT + HuggingFace)
python3 scripts/pull_gdelt.py                          # ~3 min, no key needed
HF_TOKEN=hf_... python3 scripts/score_hf.py            # ~3 min, free tier
python3 scripts/build_tab1.py                          # instant

# Tab 2 (YouTube Data API v3)
YT_KEY=AIza... python3 scripts/pull_youtube.py         # ~30s, 150 quota units
```

Outputs land in `erika-kirk/data/`. Updating the live page after a refresh is currently manual — copy the new values into the SVG polylines and JS data objects in `../index.html` (the served file at the repo root). See [CLAUDE.md](./CLAUDE.md) for the chart conventions (x positions, y formulas, channel colors).

**API key setup, key gotchas, full directory layout** — see [`scripts/README.md`](./scripts/README.md).

**Critical quota note:** Tab 2 uses `playlistItems.list` (1 unit per page of 50 videos), not `search.list` (100 units per call). The same data pull would cost ~7,000 units with `search.list` and ~150 units with `playlistItems.list` — a 90× difference, and the default mental model for "date-bounded YouTube search" is the expensive one.

## Important caveats

These are surfaced inside the artifact, but worth flagging here:

- **GDELT tone is mildly negative across the whole window** (−1.4 to −2.9 on the raw scale). GDELT's article mix tilts global/tabloid, over-representing BoredPanda, IBTimes UK, Times of India, news.meaww.com — useful for relative shape, less useful for absolute "is mainstream news positive or negative" claims.
- **The Twitter-RoBERTa model cannot distinguish negative-defense from negative-attack.** Ben Shapiro defending Erika by calling Candace Owens "evil" registers identically to Ian Carroll calling Erika "caught" in a TPUSA "secret." Title-level sentiment is a blunt instrument.
- **Social mention volumes are estimates**, anchored to documented viral events but not raw mention counts from a social-listening API (no Brandwatch / Talkwalker access). Each month carries a HIGH/MED/LOW confidence flag tied to a specific anchor.
- **YouTube "monthly views"** = sum of `statistics.viewCount` across videos *published* in that month as of the pull date. Older videos have had more time to accumulate views, slightly favoring earlier months. The trajectory shape is unaffected for channels' bread-and-butter content cadences.
- **Paramount Tactical's July baseline is anomalously small** (9 videos / 55K views), producing a 60× September spike on the index. The value is real but skews any cross-channel average, so it's excluded from the top-panel mean and shown on the bottom panel.

## Subject and context

Erika Kirk is the widow of Charlie Kirk, founder of Turning Point USA, who was assassinated on September 10, 2025, at Utah Valley University. She became CEO of TPUSA in the weeks that followed and has been the subject of substantial media coverage — including a public feud with Candace Owens that drove much of the divergence captured in Tab 1 during Q1 2026.

This is a side project. The artifact is a *measurement framework*, not a position on the events or the coverage.

## Stack

- Single `index.html` — vanilla HTML, CSS, SVG, JavaScript
- No build step, no dependencies, no framework
- Hosted on GitHub Pages from the `main` branch — every push redeploys

## Project history

The artifact went through six versions:

1. v1 — qualitative estimates, manual sentiment coding
2. v2 — hardened with GDELT + HF; data layer made defensible
3. v3 (Tab 1 polish) — plain-English intro, clickable month cards, uncertainty bands
4. v3 (Tab 2 added) — initial per-video HF sentiment scoring across six YouTube channels
5. v3 (Tab 2 pivot) — switched from per-episode sentiment to channel audience trends
6. v3 (Tab 2 hardened) — replaced estimates with real YouTube Data API v3 numbers; added Valhalla VFT and Paramount Tactical for an eight-channel set

Each version is preserved in the git history.

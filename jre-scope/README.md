# JRE Guest Scope — topic diversity tracker

A data-driven dashboard exploring how the topical range of **The Joe Rogan Experience**
guest roster has moved over time, from episode **#1000 (August 2017)** to the present.
Live at https://s-schinkel.github.io/media-divergence-tracker/jre-scope/ — part of the
[media-divergence-tracker](../) collection.

The page deliberately editorialises nothing: it assigns one canonical topic tag per guest,
aggregates by month, and lets the charts answer whether the show's scope has narrowed,
widened, or held steady.

## What's on the page

1. **Monthly views & topic diversity** — dual-axis line chart: total YouTube views of the
   month's episodes (left axis) vs. a topic diversity score (right axis: distinct topic
   tags that month as a % of all 20 possible tags), with the diversity mean as a reference
   line.
2. **Topic distribution over time** — episodes per month stacked by topic tag. Clicking a
   month drives the drill-down below.
3. **Episode drill-down** — the selected month's episodes (default: 10 most recent) with
   guest, tag, one-line bio, views, and return-guest ordinal.
4. **Return guests** — collapsible ranked table of repeat guests since #1000.

## Data & methodology

- **Source of record:** [`data/episodes.json`](./data/episodes.json) — one row per numbered
  episode ≥ #1000 (non-numbered specials like MMA Shows and Fight Companions are out of
  scope).
- **Episode list & air dates:** jrelibrary.com's episode index (Datawrapper dataset),
  cross-checked against the official RSS feed (`feeds.megaphone.fm/GLT1412515089`); the RSS
  publish date wins where both exist.
- **Topic tags:** one of 20 canonical tags per **guest** (their primary public domain — why
  they're known, not what a given episode discussed), applied to each episode via its
  first-listed guest. Tags were assigned editorially, with web verification for
  less-known names.
- **Views:** scraped from the `@joerogan` YouTube uploads on the generation date. Full
  episodes were removed from YouTube during the Spotify-exclusive era (Dec 2020 – Feb 2024)
  and later re-uploaded, so view counts for older episodes reflect accumulation since
  re-upload, not original popularity; episodes never (re)uploaded are `null`.
- **Return-guest counts** include pre-#1000 appearances (computed across the full #1–
  present catalog).

## Refreshing

`data/episodes.json` is the source of truth. `index.html` carries that data inline between
the `/* DATA:START */` / `/* DATA:END */` markers — a **generated** block; never hand-edit
it. To refresh:

```bash
cd jre-scope
# edit data/episodes.json (append new episodes, update views, bump meta.generated)
python3 scripts/build_dataset.py            # validate -> regenerate index.html
python3 scripts/build_dataset.py --check    # validate only
```

The script validates (canonical tags, ISO dates, episode ordering, appearance-count
consistency) and writes nothing on failure.

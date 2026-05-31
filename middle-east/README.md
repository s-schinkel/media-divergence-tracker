# Iran / Middle East — Media &amp; Conflict Tracker

**Live:** https://s-schinkel.github.io/media-divergence-tracker/middle-east/

A data-dense, interactive tracker of Middle East media coverage versus real-world events,
**January 2025 → present**. The goal is to surface *leading and trailing indicators* — does
media coverage anticipate or lag kinetic and diplomatic events? — and to track the posture
of key world leaders over time.

This is a side project, not affiliated with any employer. It is a **measurement framework**,
not a position on the events or the coverage. It is part of the
[`media-divergence-tracker`](../README.md) collection; see that hub README for why this
tracker lives at a subpath.

> **Status: scaffolded, not yet populated.** Phase 1 data collection has not been run. The
> served page is currently a placeholder shell. This README describes the intended design.

## What it will measure

Month-by-month, Jan 2025 → present:

| Category | Contents |
|---|---|
| **A. Media volume** | Story volume mentioning Iran across **UK / Australia / USA / Canada**, dominant-topic summary, tone (Escalatory +1 / Neutral 0 / De-escalatory −1), source examples |
| **B. US presidential posture** | Trump statements on Iran (Truth Social, news aggregators, press/EOs); classified Threatening / Hawkish / Neutral / Diplomatic / Conciliatory; formal policy actions logged |
| **C. Other world leaders** | UK PM, AU PM, CA PM, Netanyahu, Khamenei/Pezeshkian, MBS, EU High Representative — posture classified Hostile / Cautious / Neutral / Engaged / Conciliatory |
| **D. Kinetic events** | Confirmed direct strikes (USA / Israel / Iran / proxy): date, actor, target type, description, source |
| **E. Flash points** | Diplomatic expulsions, protests, sanctions, nuclear negotiations, hostage/prisoner events, proxy events, UNSC actions, assassinations |

## Planned visualisation

- **"The Wave"** — D3 filled-area chart of total story volume across all 4 countries, with
  4 thin per-country overlay lines.
- **Event markers** — floating dots above the wave, colour/shape-coded by event type
  (see `CLAUDE.md` for the taxonomy), with hover tooltips.
- **Posture timeline** — a horizontal swimlane per leader, monthly posture as a coloured
  block.
- **Tone comparison panel** — Chart.js stacked bars of Escalatory/Neutral/De-escalatory
  tone, switchable by country.
- **Always-visible key/legend**, top summary panel (total stories, total events, date
  range), horizontal scroll when months exceed viewport width.

## Stack

- Single `index.html`, rendered client-side.
- **D3.js** (main wave chart) and **Chart.js** (secondary panels) loaded from CDN.
- Dark theme (`#0d1117`), JetBrains Mono for dates/labels, Inter for prose.
- Hosted on GitHub Pages from `main` — every push redeploys.

> Note: unlike the sibling Erika Kirk tracker (deliberately zero-dependency vanilla
> HTML/SVG), this tracker uses CDN charting libraries by design, given the density of the
> visuals. This divergence in approach is intentional and recorded in `CLAUDE.md`.

## Data &amp; methodology notes

- **Volume figures are approximate.** Without Factiva / LexisNexis access, monthly story
  counts are estimated from search-result signal density. The *relative month-by-month
  shape* is meaningful; absolute numbers are not. Thin-coverage months are flagged with ⚠.
- **Truth Social coverage is indirect** — major Trump statements are captured via Reuters /
  AP / major-outlet verbatim quotes rather than direct API access.
- Where a leader made no notable Iran statement in a month, posture is left blank (grey).
- Primary sources (official statements, directly quoted articles) are preferred over
  aggregated summaries.

## Reproducing the data

See [`scripts/README.md`](./scripts/README.md). Outputs land in [`data/`](./data/). The
pipeline is currently **stubs** — `scripts/` defines the intended collection steps but does
not yet perform live collection.

## How to view locally

It's a static page — open `index.html` in a browser, or serve the folder:

```bash
cd middle-east && python3 -m http.server 8000   # then open http://localhost:8000/
```

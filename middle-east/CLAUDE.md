# CLAUDE.md — agent guidance for the Iran / Middle East tracker

An interactive tracker of Middle East media coverage vs. real-world events, Jan 2025 →
present. Served at https://s-schinkel.github.io/media-divergence-tracker/middle-east/ from
`middle-east/index.html`. Part of the multi-tracker repo — see `../CLAUDE.md` for the repo
map and the rules around the frozen root URL.

> **Status: scaffolded, not populated.** `index.html` is currently a placeholder shell and
> `scripts/` are stubs. The build proceeds in phases (below). Do not assume data exists.

## This folder is self-contained

Everything for this tracker lives under `middle-east/`. Do not reach into sibling trackers
or the repo root (other than linking back to `../`). A change here must not require editing
the Erika tracker or the root `index.html`.

```
middle-east/
├── index.html          ← the served artifact (placeholder until Phase 2)
├── README.md           ← public overview + methodology
├── CLAUDE.md           ← this file
├── scripts/            ← data-collection pipeline (Python; STUBS for now)
│   ├── collect_media_volume.py     ← Cat. A: per-country monthly volume + tone
│   ├── collect_leader_posture.py   ← Cat. B + C: leader posture classifications
│   ├── collect_events.py           ← Cat. D + E: kinetic events + flash points
│   ├── build_dataset.py            ← merge collectors → data/dataset.json for index.html
│   └── README.md
└── data/               ← collected snapshots (empty until Phase 1 runs)
```

## Build phases (from the project spec)

1. **Phase 1 — data collection.** Month-by-month web search, Jan 2025 → present. Produce a
   structured data table for the maintainer to **validate before any visualisation**.
   Expect multiple passes (e.g. UK+USA first, then AU+CA). Categories A–E (see README).
2. **Phase 2 — visualisation.** Build the interactive `index.html`: the D3 "wave", event
   markers, posture swimlanes, Chart.js tone panel, always-visible legend, top summary
   panel.
3. **Phase 3 — design polish.** Dark theme, JetBrains Mono for dates/labels, horizontal
   scroll, high-contrast tooltips, ⚠ flags on thin-coverage months.

Do not skip the Phase 1 validation gate — the maintainer wants to check the data table
before the artifact is built.

## Event-marker taxonomy (Phase 2) — colour + shape are both load-bearing

| Event type | Colour | Shape |
|---|---|---|
| US/Israel strike | Red | ✕ cross |
| Iranian strike / retaliation | Orange | ▲ triangle |
| Diplomatic flash point | Yellow | ◆ diamond |
| Protest / civil event | Teal | ● circle |
| Leadership statement | Blue | ■ square |
| Policy / sanctions | Purple | ★ star |

## Posture colour scale (Phase 2 swimlanes)

| Posture | Colour |
|---|---|
| Hostile | dark red |
| Cautious | amber |
| Neutral | grey |
| Engaged | light blue |
| Conciliatory | green |

Leaders shown as swimlanes: Trump (USA), UK PM, AU PM, CA PM, Netanyahu (Israel),
Khamenei/Iran, MBS (Saudi). Blank month = grey (no notable statement).

## Stack — intentional choices

- **D3.js + Chart.js from CDN** (not vanilla SVG). This *deliberately differs* from the
  sibling Erika tracker. The wave + dense event overlay + swimlanes justify D3; tone panels
  use Chart.js. Recorded here so it isn't "corrected" toward the other tracker's style.
- Single `index.html`, client-side. The collected dataset is loaded as inlined JSON or a
  fetched `data/dataset.json` — decide at Phase 2; if fetched, note that opening the file
  via `file://` won't work and a local server is needed.
- Dark `#0d1117`, JetBrains Mono (dates/labels) + Inter (prose), already wired in the
  placeholder.

## Data contract (what `build_dataset.py` should emit)

A single `data/dataset.json` consumed by `index.html`. Suggested shape (firm up in Phase 1):

```jsonc
{
  "meta": { "date_range": "2025-01..2025-XX", "total_stories": 0, "total_events": 0 },
  "months": [
    { "month": "2025-01",
      "volume": { "UK": 0, "AU": 0, "USA": 0, "CA": 0 },
      "tone":   { "UK": 0, "AU": 0, "USA": 0, "CA": 0 },   // +1 / 0 / -1
      "summary": { "UK": "…", "AU": "…", "USA": "…", "CA": "…" },
      "thin_coverage": false,                              // → ⚠ flag
      "posture": { "trump": "Hawkish", "uk_pm": "Cautious", "...": "" }
    }
  ],
  "events": [
    { "date": "2025-06-13", "type": "us_israel_strike",   // keys match the taxonomy above
      "actor": "Israel", "description": "…", "source": "…" }
  ]
}
```

## Data caveats (carry into the artifact, like the Erika tracker does)

- Volume = approximate, from search-signal density, not true article counts (no
  Factiva/LexisNexis). Relative shape meaningful; absolutes not.
- Truth Social posture captured indirectly via major-outlet verbatim quotes.
- Sanity-check well-documented anchors before trusting a pass — e.g. confirm the date of
  Australia's expulsion of Iranian diplomats.
- Flag thin-coverage months with ⚠ rather than fabricating volume.

## Deploy

Pushing to `main` redeploys the whole repo (all trackers). Verify just this tracker:

```bash
curl -sI https://s-schinkel.github.io/media-divergence-tracker/middle-east/ | head -3
```

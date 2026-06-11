# media-divergence-tracker

A personal collection of **independent, single-purpose media/geopolitical trackers**, each
a self-contained interactive HTML artifact hosted on GitHub Pages. This is a side project —
not affiliated with any employer.

## Trackers in this repo

| Tracker | Subject | Folder | Live URL |
|---|---|---|---|
| **Erika Kirk media divergence** | Gap between mainstream news and social coverage of Erika Kirk (Jul 2025 → May 2026) + YouTube audience trends | served from root `index.html`; docs & pipeline in [`erika-kirk/`](./erika-kirk/) | https://s-schinkel.github.io/media-divergence-tracker/ |
| **Iran / Middle East media & conflict** | Leading/trailing indicators in media coverage vs. real-world events across UK/AU/USA/CA, leader posture, kinetic events (Jan 2025 → present) | [`middle-east/`](./middle-east/) | https://s-schinkel.github.io/media-divergence-tracker/middle-east/ |
| **JRE guest scope** | Topic diversity of Joe Rogan Experience guests, episode #1000 (Aug 2017) → present: monthly topic mix, YouTube views, return guests | [`jre-scope/`](./jre-scope/) | https://s-schinkel.github.io/media-divergence-tracker/jre-scope/ |

Each tracker is fully self-contained in (or, for the Erika tracker, anchored from) its own
folder, with its own `README.md`, `CLAUDE.md`, data pipeline, and data snapshots.

## A note on the repo name and the root URL

This repo is named `media-divergence-tracker` and its **root** URL
(`https://s-schinkel.github.io/media-divergence-tracker/`) serves the **Erika Kirk**
tracker. That name and that URL are deliberately frozen: the link has been shared
externally and described in prior correspondence, so it must keep resolving to the same
artifact.

Rather than rename the repo (which would break the shared link) when adding further
trackers, **new trackers are added as subfolders** and served at subpaths like
`/middle-east/`. So the repo name describes its *first* tracker, not all of them — an
intentional, documented trade-off in favour of URL stability. If the external link is ever
retired, the repo could be renamed and the root turned into a proper landing page.

## Layout

```
.
├── index.html        ← Erika Kirk tracker — the SERVED page at the root URL (do not move)
├── erika-kirk/       ← Erika tracker docs + data pipeline (README, CLAUDE, scripts/, data/)
├── middle-east/      ← Iran / Middle East tracker (its own index.html, docs, pipeline)
├── jre-scope/        ← JRE guest scope tracker (its own index.html, docs, pipeline)
├── README.md         ← this file (repo hub)
└── CLAUDE.md         ← agent guidance for the repo as a whole
```

## Stack & hosting

- Each artifact is client-side HTML/CSS/JS. The Erika tracker is deliberately
  zero-dependency vanilla HTML+SVG; the Middle East tracker uses D3.js + Chart.js from CDN
  for its denser visuals; the JRE tracker uses Chart.js only. (See each tracker's own docs.)
- Hosted on **GitHub Pages from the `main` branch** — every push to `main` redeploys the
  whole site. There is no build step.

## Working on a specific tracker?

Read that tracker's own `README.md` and `CLAUDE.md` first
([`erika-kirk/`](./erika-kirk/), [`middle-east/`](./middle-east/), [`jre-scope/`](./jre-scope/)), then the repo-level
[`CLAUDE.md`](./CLAUDE.md) for cross-tracker conventions.

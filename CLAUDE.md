# CLAUDE.md — repo-level agent guidance

This repository hosts **multiple independent trackers**, each a self-contained interactive
HTML artifact served by GitHub Pages. This file is the repo map; each tracker has its own
`CLAUDE.md` with the chart/data conventions specific to it.

## ⚠ Two things that will trip you up — read first

1. **Root `index.html` IS the Erika Kirk tracker and must never move, rename, or change
   identity.** It is the page served at `https://s-schinkel.github.io/media-divergence-tracker/`,
   which has been shared externally and must stay stable. The Erika tracker's docs and data
   pipeline live in `erika-kirk/`, deliberately split from the served file at the root. So
   for the Erika tracker, "the artifact" = `./index.html`, but its scripts/docs = `erika-kirk/`.

2. **The repo name is frozen.** It's called `media-divergence-tracker` and the root URL
   serves the Erika tracker for the historical reasons above — do not propose renaming the
   repo or moving the root page to add new trackers. New trackers go in **new subfolders**
   served at subpaths (e.g. `/middle-east/`). See `README.md` for the full rationale.

## Trackers

| Tracker | Served file | Docs / pipeline | Live path |
|---|---|---|---|
| Erika Kirk media divergence | `index.html` (repo root) | `erika-kirk/` | `/` |
| Iran / Middle East media & conflict | `middle-east/index.html` | `middle-east/` | `/middle-east/` |
| JRE guest scope (topic diversity) | `jre-scope/index.html` | `jre-scope/` | `/jre-scope/` |

Each tracker is otherwise independent: its own data, scripts, design conventions, and
`CLAUDE.md`. When working on one, read that tracker's `CLAUDE.md` for specifics.

## Layout

```
.
├── index.html        ← Erika Kirk tracker — SERVED at root URL (do not move/rename)
├── erika-kirk/       ← Erika docs + Python data pipeline + data snapshots
│   ├── README.md  CLAUDE.md
│   ├── scripts/   data/
├── middle-east/      ← Iran / Middle East tracker — fully self-contained
│   ├── index.html ← served at /middle-east/
│   ├── README.md  CLAUDE.md
│   ├── scripts/   data/
├── jre-scope/        ← JRE guest scope tracker — fully self-contained
│   ├── index.html ← served at /jre-scope/
│   ├── README.md  CLAUDE.md
│   ├── scripts/   data/
├── README.md         ← repo hub (public-facing)
└── CLAUDE.md         ← this file
```

## Deploy

GitHub Pages auto-rebuilds on every push to `main`; every tracker redeploys together.
First-byte-after-push latency is typically 1–2 min. No build step. Verify:

```bash
gh api repos/s-schinkel/media-divergence-tracker/pages/builds/latest --jq '{status, commit, updated_at}'
curl -sI https://s-schinkel.github.io/media-divergence-tracker/ | head -3            # Erika (root)
curl -sI https://s-schinkel.github.io/media-divergence-tracker/middle-east/ | head -3 # Middle East
```

Because a push redeploys the **whole** site, double-check the root `index.html` is
untouched whenever you push changes scoped to another tracker.

## Conventions across trackers

- Each tracker folder is self-contained: no cross-imports between trackers, no shared
  build. A change to one tracker should not require touching another.
- Stacks differ by tracker on purpose (Erika = zero-dependency vanilla HTML/SVG; Middle
  East = D3 + Chart.js CDN). Don't "harmonize" them — each tracker's `CLAUDE.md` records
  its intentional choices.
- Data-pull scripts read credentials from environment variables only; no secrets in the
  repo.

## Repo location

Working copy lives at `~/code/media-divergence-tracker` on the maintainer's machine.
Default branch is `main`.

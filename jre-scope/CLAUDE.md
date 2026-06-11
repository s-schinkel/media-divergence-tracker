# CLAUDE.md — agent guidance for the JRE Guest Scope tracker

A single-page dashboard of Joe Rogan Experience guest topic diversity, episodes #1000 →
present. Served at https://s-schinkel.github.io/media-divergence-tracker/jre-scope/ from
`jre-scope/index.html`. Part of the multi-tracker repo — see `../CLAUDE.md` for the repo
map and the frozen-root-URL rules.

## Refreshing the data (do NOT hand-edit the inline HTML data block)

`data/episodes.json` is the source of record. `index.html` mirrors it inline between the
`/* DATA:START */` and `/* DATA:END */` markers — that block is **generated**:

```bash
cd jre-scope
# edit data/episodes.json, then:
python3 scripts/build_dataset.py            # validate -> regen the DATA block
python3 scripts/build_dataset.py --check    # validate only
```

The script writes nothing on validation failure. Everything else in `index.html`
(CSS, chart config, panel rendering) is hand-authored and editable directly.

## Conventions & intentional choices

- **Stack: Chart.js v4 only** (CDN), dark `#0d1117` theme, Inter + JetBrains Mono — visual
  language matches the Middle East tracker, but no D3 here on purpose: both charts are
  plain line/stacked-bar, which Chart.js covers without a second dependency.
- **One tag per guest, not per episode.** `topic_tag` is the primary guest's main public
  domain, applied to the episode via the first-listed guest. The return-guest table's
  "tag contexts" column derives entirely from this — don't invent per-episode retagging.
- **Diversity score** = distinct tags in a month / 20 × 100. The denominator is the full
  canonical tag list (`TAGS` in both index.html and scripts/build_dataset.py — keep in sync).
- **Views caveat is load-bearing:** YouTube full episodes were removed Dec 2020 – Feb 2024
  and re-uploaded later, so old-episode view counts restarted from zero at re-upload.
  `meta.source_notes` documents this and is rendered verbatim on the page — keep it honest.
- **Scope:** numbered episodes only (≥ #1000). MMA Shows / Fight Companions / specials are
  deliberately excluded.
- Neutral copy only: section labels describe what is shown ("Topic distribution over
  time"), never a conclusion ("the narrowing of JRE").

## This folder is self-contained

Everything for this tracker lives under `jre-scope/`. Do not reach into sibling trackers or
the repo root (other than linking back to `../`). A change here must not require editing
the Erika tracker, the Middle East tracker, or the root `index.html`.

```
jre-scope/
├── index.html          ← the served artifact (data inline, generated block)
├── README.md           ← public overview + methodology
├── CLAUDE.md           ← this file
├── scripts/
│   └── build_dataset.py  ← validate data/episodes.json -> inject into index.html
└── data/
    └── episodes.json     ← source of record (one row per numbered episode ≥ #1000)
```

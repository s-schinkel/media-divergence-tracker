# Data pipeline — Iran / Middle East tracker

**Status: stubs.** These scripts define the *intended* Phase 1 collection steps and the
data contract. They do not yet perform live collection — collection is a manual,
web-search-driven, multi-pass effort (see `../CLAUDE.md`, "Build phases").

## Pipeline

```
collect_media_volume.py   →  data/media_volume.json     (Cat. A: per-country volume + tone + summary)
collect_leader_posture.py →  data/leader_posture.json   (Cat. B + C: posture classifications)
collect_events.py         →  data/events.json           (Cat. D + E: kinetic events + flash points)
build_dataset.py          →  data/dataset.json          (merge of the above; consumed by index.html)
```

Run from the `middle-east/` directory. All scripts read any API credentials from
environment variables; no secrets in the repo.

```bash
cd middle-east
python3 scripts/collect_media_volume.py
python3 scripts/collect_leader_posture.py
python3 scripts/collect_events.py
python3 scripts/build_dataset.py
```

## Approach notes

- **Volume is approximate.** Estimate monthly story counts from search-result signal
  density (no Factiva/LexisNexis). Capture the relative month-by-month shape; absolute
  numbers are secondary. Flag thin-coverage months (`thin_coverage: true`).
- **Sources** — UK: BBC, Guardian, Sky. AU: ABC, SMH, The Australian. USA: NYT, WaPo, Fox.
  CA: Globe and Mail, CBC, National Post.
- **Trump / Truth Social** — capture via Reuters/AP/major-outlet verbatim quotes and
  press/EO records, not direct API.
- Prefer primary sources (official statements, directly quoted articles) over aggregators.

See `../CLAUDE.md` for the full `dataset.json` contract and the event/posture taxonomies.

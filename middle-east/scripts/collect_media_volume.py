#!/usr/bin/env python3
"""Category A — media volume + tone (STUB; manual web-search collection).

Writes two files (the source of record consumed by build_dataset.py):
  - data/volume.json  : per-month {month, uk, usa, au, ca}  (approximate counts)
  - data/detail.json  : per-month per-country {tone, topics[]}  (tone code + topics)

For each month (Jan 2025 -> present) and each country (UK, AU, USA, CA):
  - approximate story volume mentioning Iran (estimated from search-signal density)
  - 2-3 dominant topics
  - tone code: E escalatory / N neutral / D de-escalatory  (EN, ND for mixed)
  - example sources (for your notes; not stored in the artifact)

Sources by country:
  UK : BBC, Guardian, Sky        AU : ABC, SMH, The Australian
  USA: NYT, WaPo, Fox            CA : Globe and Mail, CBC, National Post

Volume is APPROXIMATE — no Factiva/LexisNexis access. Capture relative shape, flag
thin-coverage months. After editing the JSON, run:  python3 scripts/build_dataset.py
See ../CLAUDE.md for the data contract.
"""

COUNTRIES = ["UK", "AU", "USA", "CA"]


def main() -> None:
    raise NotImplementedError(
        "Collection is performed via web search and hand-curated into data/volume.json "
        "and data/detail.json, then 'build_dataset.py' regenerates the artifact. "
        "This stub documents the inputs and output contract."
    )


if __name__ == "__main__":
    main()

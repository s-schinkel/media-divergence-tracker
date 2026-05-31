#!/usr/bin/env python3
"""Category A — media volume + tone (STUB).

Intended output: data/media_volume.json

For each month (Jan 2025 -> present) and each country (UK, AU, USA, CA):
  - approximate story volume mentioning Iran (estimated from search-signal density)
  - dominant-topic summary (2-3 sentences)
  - tone score: +1 escalatory / 0 neutral / -1 de-escalatory
  - example sources used

Sources by country:
  UK : BBC, Guardian, Sky
  AU : ABC, SMH, The Australian
  USA: NYT, WaPo, Fox
  CA : Globe and Mail, CBC, National Post

Volume is APPROXIMATE — no Factiva/LexisNexis access. Capture relative shape, flag
thin-coverage months. See ../CLAUDE.md for the dataset contract.
"""

COUNTRIES = ["UK", "AU", "USA", "CA"]


def main() -> None:
    raise NotImplementedError(
        "Phase 1 collection is performed via web search, not automated here yet. "
        "This stub records the intended output (data/media_volume.json) and inputs."
    )


if __name__ == "__main__":
    main()

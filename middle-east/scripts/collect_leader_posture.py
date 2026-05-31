#!/usr/bin/env python3
"""Categories B + C — world-leader posture (STUB).

Intended output: data/leader_posture.json

Per month, classify each leader's posture on Iran. Leave blank where no notable
statement was made that month.

B. US president (Trump): Threatening / Hawkish / Neutral / Diplomatic / Conciliatory.
   Capture via Truth Social quotes (indirect, via Reuters/AP/major-outlet verbatim),
   press statements, and executive orders. Log formal policy actions separately.

C. Other leaders: Hostile / Cautious / Neutral / Engaged / Conciliatory.
   - UK Prime Minister
   - Australian Prime Minister
   - Canadian Prime Minister
   - Israeli PM Netanyahu
   - Iranian Supreme Leader Khamenei / President Pezeshkian
   - Saudi Crown Prince MBS
   - EU High Representative for Foreign Affairs

See ../CLAUDE.md for the posture colour scale and dataset contract.
"""

LEADERS = [
    "trump", "uk_pm", "au_pm", "ca_pm",
    "netanyahu", "khamenei_iran", "mbs", "eu_hr",
]


def main() -> None:
    raise NotImplementedError(
        "Phase 1 collection is performed via web search, not automated here yet. "
        "This stub records the intended output (data/leader_posture.json) and inputs."
    )


if __name__ == "__main__":
    main()

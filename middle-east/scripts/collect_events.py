#!/usr/bin/env python3
"""Categories D + E — kinetic events + flash points (STUB).

Intended output: data/events.json

D. Kinetic events — confirmed direct strikes / military actions:
   date, actor (USA / Israel / Iran / proxy), target type (nuclear facility /
   military base / naval / drone-missile), 1-sentence description, source.

E. Flash points — significant non-strike events that moved the narrative:
   diplomatic expulsions (e.g. Australia expelling Iranian diplomats), protests /
   flotillas, sanctions, nuclear negotiations or breakdowns, hostage / prisoner
   exchanges, major proxy events (Houthi, Hezbollah), UNSC resolutions / vetoes,
   assassinations. Each: date, event type, country/actor, 1-sentence description.

Each event's `type` must match the marker taxonomy keys in ../CLAUDE.md
(us_israel_strike, iran_strike, diplomatic, protest, statement, policy).

Sanity-check well-documented anchors (e.g. confirm the date of Australia's Iranian
diplomat expulsion) before trusting a collection pass.
"""

EVENT_TYPES = ["us_israel_strike", "iran_strike", "diplomatic", "protest", "statement", "policy"]


def main() -> None:
    raise NotImplementedError(
        "Phase 1 collection is performed via web search, not automated here yet. "
        "This stub records the intended output (data/events.json) and inputs."
    )


if __name__ == "__main__":
    main()

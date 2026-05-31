#!/usr/bin/env python3
"""Merge collectors into the single dataset consumed by index.html (STUB).

Reads:
    data/media_volume.json     (collect_media_volume.py)
    data/leader_posture.json   (collect_leader_posture.py)
    data/events.json           (collect_events.py)

Writes:
    data/dataset.json

Output shape (see ../CLAUDE.md "Data contract" for the authoritative spec):

    {
      "meta":   { "date_range", "total_stories", "total_events" },
      "months": [ { "month", "volume", "tone", "summary", "thin_coverage", "posture" }, ... ],
      "events": [ { "date", "type", "actor", "description", "source" }, ... ]
    }

`meta.total_stories` and `meta.total_events` are derived here (summed from months/events)
so the top summary panel in index.html can read them directly.
"""


def main() -> None:
    raise NotImplementedError(
        "Implement once the three collector outputs exist. This stub records the merge "
        "step and the data/dataset.json contract."
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Combine GDELT and HF outputs into Tab 1's per-month composite divergence rows.

Reads:
  data/gdelt_monthly.json  (from pull_gdelt.py)
  data/hf_results.json     (from score_hf.py)

Writes:
  data/tab1_rows.json — per-month composite breakdown ready for the HTML

Composite formula (unchanged from v2):
  composite = (1 - topic_overlap) * 0.5
            + abs(sentiment_delta) * 0.3
            + volume_asymmetry_score * 0.2

The topic clusters and social-volume estimates are hardcoded below because
they're curator-assembled (not API-derived). Update them when refreshing.

Usage:
  python3 scripts/build_tab1.py
"""
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Hand-curated per-month social-volume estimates anchored to documented viral events.
# Each entry: {mentions, confidence, anchor}. See README "Caveats" for limitations.
SOCIAL_VOLUME = {
    "202507": {"mentions": 1_500,       "confidence": "LOW",  "anchor": "No documented viral activity"},
    "202508": {"mentions": 2_500,       "confidence": "LOW",  "anchor": "Pre-event background level"},
    "202509": {"mentions": 11_000_000,  "confidence": "HIGH", "anchor": "Assassination news event"},
    "202510": {"mentions": 4_500_000,   "confidence": "MED",  "anchor": "Snopes Air Force 2 / Soros lawsuit"},
    "202511": {"mentions": 8_000_000,   "confidence": "MED",  "anchor": "Yahoo 'never dated' viral cycle"},
    "202512": {"mentions": 14_000_000,  "confidence": "MED",  "anchor": "AmericaFest + Owens + book launch"},
    "202601": {"mentions": 12_000_000,  "confidence": "MED",  "anchor": "Primetimer/Snopes pregnancy rumor"},
    "202602": {"mentions": 18_000_000,  "confidence": "MED",  "anchor": "WaPo Owens 'Bride of Charlie'"},
    "202603": {"mentions": 95_000_000,  "confidence": "HIGH", "anchor": "Druski 80M+ views on X"},
    "202604": {"mentions": 65_000_000,  "confidence": "HIGH", "anchor": "CNN/TMZ WHCD-tears viral clip"},
    "202605": {"mentions": 22_000_000,  "confidence": "MED",  "anchor": "Newsweek/CBS UGA-threats cycle"},
}

CLUSTERS = {
    "202507": {"mainstream": ["TPUSA spouse mentions"], "social": ["TPUSA spouse mentions"], "shared": 1},
    "202508": {"mainstream": ["TPUSA events","summer tour"], "social": ["TPUSA events"], "shared": 1},
    "202509": {"mainstream": ["assassination","first remarks","CEO succession","funeral","forgiveness","political violence","investigation"],
               "social":     ["assassination","forgiveness reactions","conspiracy theories","shooter motive","political polarization","succession","grief"], "shared": 4},
    "202510": {"mainstream": ["Medal of Freedom","TPUSA tour","CEO role","Ole Miss event"],
               "social":     ["Medal of Freedom","Air Force 2 rumor","fake Soros lawsuit","early Vance-hug speculation"], "shared": 1},
    "202511": {"mainstream": ["Jesse Watters interview","Patriot Awards","Legacy Award","Fox Nation doc","courtroom cameras"],
               "social":     ["never dated viral","interview tears clips","Vance speculation","faith comments parodied","courtroom cameras"], "shared": 2},
    "202512": {"mainstream": ["book launch","AmericaFest 30K crowd","JD Vance 2028 endorsement","CBS town hall","Owens private meeting"],
               "social":     ["Owens vs Kirk tensions","endorsement skepticism","book promo criticism","female-crowd narrative","pregnancy rumors begin","Vance affair speculation"], "shared": 2},
    "202601": {"mainstream": ["Make Heaven Crowded Tour","TPUSA expansion","SOTU guest preview"],
               "social":     ["pregnancy rumor","Rolling Loud AI deepfake","Vance affair memes","outfit scrutiny","remarriage rumors"], "shared": 0},
    "202602": {"mainstream": ["courtroom cameras fight","Club America Montana","State of the Union","TPUSA partnerships"],
               "social":     ["wedding photo removed","missing wedding ring","Owens Bride of Charlie series","Vance affair narrative","SOTU outfit scrutiny"], "shared": 1},
    "202603": {"mainstream": ["Air Force Academy Board","Hillsdale commencement","TIME100 Next","Arkansas Club America"],
               "social":     ["Druski parody","Vance affair memes peak","Air Force board backlash","TIME100 mockery","Hillsdale backlash"], "shared": 2},
    "202604": {"mainstream": ["WHCD shooting","tears clip","step-back","political violence","UGA event prep"],
               "social":     ["WHCD shooting reactions","tears clip viral","WHCD conspiracy","Vance affair continues","step-back skepticism"], "shared": 3},
    "202605": {"mainstream": ["UGA threats","Secret Service no-credible-threat","step-back","Newsweek interview"],
               "social":     ["UGA threats skepticism","threat-narrative debunking","Vance speculation","return-to-public framing"], "shared": 2},
}

MONTH_LABEL = {
    "202507": "Jul 2025", "202508": "Aug 2025", "202509": "Sep 2025",
    "202510": "Oct 2025", "202511": "Nov 2025", "202512": "Dec 2025",
    "202601": "Jan 2026", "202602": "Feb 2026", "202603": "Mar 2026",
    "202604": "Apr 2026", "202605": "May 2026",
}


def main():
    gdelt = json.loads((DATA / "gdelt_monthly.json").read_text())
    hf    = json.loads((DATA / "hf_results.json").read_text())

    # Baseline = September social/GDELT ratio (Jul has zero GDELT vol so we can't use it)
    sep = gdelt["202509"]
    baseline_ratio = SOCIAL_VOLUME["202509"]["mentions"] / sep["vol_sum"]
    print(f"Baseline (Sept) ratio: {baseline_ratio:,.0f}")

    rows = []
    for ym, label in MONTH_LABEL.items():
        g = gdelt.get(ym, {"vol_sum": 0, "tone_avg": 0})
        h = hf.get(ym, {})
        sv = SOCIAL_VOLUME[ym]
        cl = CLUSTERS[ym]

        ms_sent  = h.get("mainstream_hf_avg") or 0.0
        soc_sent = h.get("social_hf_avg") or 0.0
        sentiment_delta = ms_sent - soc_sent

        union = len(set(cl["mainstream"]) | set(cl["social"]))
        topic_overlap = cl["shared"] / union if union > 0 else 0.0

        if g["vol_sum"] > 0:
            raw_ratio = sv["mentions"] / g["vol_sum"]
            normalized = raw_ratio / baseline_ratio
            volume_score = min(1.0, max(0.0, math.log10(max(normalized, 1.0)) / 2.0))
        else:
            normalized = None
            volume_score = 0.0

        composite = (
            (1 - topic_overlap) * 0.5
            + abs(sentiment_delta) * 0.3
            + volume_score * 0.2
        )

        rows.append({
            "ym": ym, "label": label,
            "gdelt_vol_sum": round(g["vol_sum"], 4),
            "gdelt_tone_norm": round(g["tone_avg"] / 100.0, 4),
            "hf_mainstream_avg": round(ms_sent, 4),
            "hf_social_avg":     round(soc_sent, 4),
            "social_mentions": sv["mentions"],
            "social_confidence": sv["confidence"],
            "topic_overlap": round(topic_overlap, 3),
            "sentiment_delta": round(sentiment_delta, 4),
            "volume_normalized": None if normalized is None else round(normalized, 2),
            "volume_score": round(volume_score, 3),
            "composite": round(composite, 3),
            "high": composite > 0.60,
        })

    print(f"\n{'Month':<10} {'overlap':>8} {'sentΔ':>8} {'vol':>7} {'comp':>6} {'HIGH':>5}")
    for r in rows:
        print(f"{r['label']:<10} {r['topic_overlap']:>8.3f} {r['sentiment_delta']:>+8.3f} {r['volume_score']:>7.3f} {r['composite']:>6.3f} {'★' if r['high'] else ''}")

    (DATA / "tab1_rows.json").write_text(json.dumps(rows, indent=2))
    print(f"\nWrote {DATA}/tab1_rows.json")


if __name__ == "__main__":
    main()

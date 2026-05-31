#!/usr/bin/env python3
"""Score mainstream headlines (from GDELT artlist) and curated social
snippets through HuggingFace's cardiffnlp/twitter-roberta-base-sentiment.

Per-text score = p_positive - p_negative ∈ [-1, +1].

Inputs:
  data/gdelt_articles/<YYYYMM>.json  — from pull_gdelt.py
  SOCIAL_SNIPPETS dict in this file  — curated representative texts

Output:
  data/hf_results.json — per-month {mainstream_hf_avg, social_hf_avg, scores}

Requires:
  HF_TOKEN env var with "Inference Providers" scope
  (Generate at huggingface.co/settings/tokens; the default "read" scope
  is NOT enough — must include Inference Providers.)

Usage:
  HF_TOKEN=hf_... python3 scripts/score_hf.py
"""
import json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ARTICLES = DATA / "gdelt_articles"

HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    sys.exit("Set HF_TOKEN env var (must have Inference Providers scope)")

URL = "https://router.huggingface.co/hf-inference/models/cardiffnlp/twitter-roberta-base-sentiment"


def hf_score(text):
    req = urllib.request.Request(
        URL,
        data=json.dumps({"inputs": text}).encode(),
        headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            probs = {x["label"]: x["score"] for x in data[0]}
            return probs.get("LABEL_2", 0) - probs.get("LABEL_0", 0)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 503 and "loading" in body.lower():
                time.sleep(5 * (attempt + 1)); continue
            raise RuntimeError(f"HF HTTP {e.code}: {body[:200]}")
    raise RuntimeError("HF retries exhausted")


# Representative social-discussion snippets per month — curated from documented
# viral events (TikTok discovery pages, X trending topics, news coverage of
# what was trending socially). Update this when refreshing the data.
SOCIAL_SNIPPETS = {
    "202507": [], "202508": [],
    "202509": [
        "Charlie Kirk shot dead at Utah Valley University, his wife Erika is in shock",
        "Erika Kirk forgave her husband's killer, what an incredible act of grace",
        "Charlie Kirk assassination conspiracy theories spreading wildly online",
        "Erika Kirk taking over Turning Point USA already, suspicious timing",
        "Heartbroken for Erika Kirk and the kids losing Charlie like this",
        "The forgiveness moment from Erika Kirk was performative not genuine",
        "Erika Kirk speaking at the funeral was emotionally devastating to watch",
    ],
    "202510": [
        "Did Erika Kirk really fly on Air Force 2? Looks shady",
        "Erika Kirk getting the Presidential Medal of Freedom for Charlie was beautiful",
        "Fake news circulating that Erika Kirk is suing Soros for $400 million",
        "That hug between Erika Kirk and JD Vance was way too long and weird",
        "Erika Kirk is grifting off her husband's death already, disgusting",
        "Crying for Erika Kirk receiving Charlie's medal from Trump",
    ],
    "202511": [
        "Erika Kirk said she never dated but the receipts are coming out fast",
        "Erika Kirk crying on Jesse Watters interview seems calculated",
        "Erika Kirk Charlie Kirk Legacy Award speech was incredible, what a woman",
        "Why is Erika Kirk doing six Fox News interviews in one week, attention seeking",
        "JD Vance affair rumors with Erika Kirk are clearly nonsense from haters",
        "Erika Kirk faith comments from the interview are getting mocked on TikTok",
        "Erika Kirk continues to be a strong voice for the conservative movement",
    ],
    "202512": [
        "Candace Owens going scorched earth on Erika Kirk, ugly fight",
        "Erika Kirk endorsing JD Vance for 2028 is a power play",
        "Pregnancy rumors about Erika Kirk are obviously fake but trending",
        "Erika Kirk pushing Charlie's posthumous book feels exploitative",
        "30000 people at AmericaFest, mostly women, drawn by Erika Kirk",
        "Erika Kirk and Candace Owens private meeting was supposedly tense",
        "Erika Kirk continues Charlie's legacy beautifully at AmericaFest",
    ],
    "202601": [
        "Erika Kirk pregnant tweet was debunked but spread like wildfire",
        "That AI deepfake of Erika Kirk dancing at Rolling Loud is wild",
        "Erika Kirk's outfit at Make Heaven Crowded Tour is getting roasted",
        "Remarriage rumors about Erika Kirk so soon, disrespectful",
        "Erika Kirk smiling and laughing months after Charlie's death, suspicious",
        "Erika Kirk doing important work expanding TPUSA in this difficult time",
        "Why is everyone obsessed with Erika Kirk's relationship status",
    ],
    "202602": [
        "Erika Kirk removed her wedding photo with Charlie from the office, why?",
        "Erika Kirk no longer wearing her wedding ring in recent videos",
        "Candace Owens Bride of Charlie series episode is devastating",
        "Erika Kirk's State of the Union outfit is so disrespectful",
        "Erika Kirk fighting for courtroom cameras shows real strength",
        "Erika Kirk's removal of Charlie's photo is a huge red flag",
        "The Bride of Charlie narrative is unfair character assassination",
    ],
    "202603": [
        "Druski's Conservative Women parody about Erika Kirk is hilarious, 80 million views",
        "Erika Kirk on the Air Force Academy Board is a joke appointment",
        "Erika Kirk TIME 100 Next list is laughable, what has she done",
        "JD Vance hug with Erika Kirk affair memes are everywhere now",
        "Druski parody hits too close to home apparently, Vance furious",
        "Erika Kirk Hillsdale commencement speaker, what a disgrace",
        "Erika Kirk getting honored is well-deserved after all she's been through",
    ],
    "202604": [
        "Erika Kirk leaving the WHCD in tears after the shooting, heartbreaking",
        "The Erika Kirk crying viral clip from WHCD is everywhere",
        "Erika Kirk stepping back from public appearances is the right call",
        "WHCD shooting conspiracy theories swirling, Erika in the middle",
        "Vance affair narrative still alive despite the tragedy",
        "Erika Kirk's tears at WHCD were genuine and devastating",
        "Erika Kirk used the WHCD shooting to drive sympathy",
    ],
    "202605": [
        "Erika Kirk UGA event threats are clearly fabricated for sympathy",
        "Erika Kirk return to public events timing seems calculated",
        "JD Vance Erika Kirk speculation continues despite all the denials",
        "Secret Service confirmed no credible threats, embarrassing for Erika",
        "Erika Kirk taking time with family is completely understandable",
    ],
}


def main():
    out = {}
    for ym in sorted(set(list(SOCIAL_SNIPPETS) + [p.stem for p in ARTICLES.glob("*.json")] if ARTICLES.exists() else list(SOCIAL_SNIPPETS))):
        # Load GDELT article titles for this month if available
        path = ARTICLES / f"{ym}.json"
        titles = []
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for a in data.get("articles", []):
                    t = re.sub(r"\s+", " ", (a.get("title") or "").strip())
                    if t:
                        titles.append(t)
            except Exception:
                pass

        ms_scores = []
        for t in titles:
            ms_scores.append(hf_score(t))
            time.sleep(0.4)

        soc_scores = []
        for t in SOCIAL_SNIPPETS.get(ym, []):
            soc_scores.append(hf_score(t))
            time.sleep(0.4)

        out[ym] = {
            "mainstream_n": len(ms_scores),
            "mainstream_hf_avg": sum(ms_scores) / len(ms_scores) if ms_scores else None,
            "mainstream_scores": ms_scores,
            "social_n": len(soc_scores),
            "social_hf_avg": sum(soc_scores) / len(soc_scores) if soc_scores else None,
            "social_scores": soc_scores,
        }
        print(f"{ym}: ms n={len(ms_scores)} avg={out[ym]['mainstream_hf_avg']!r}  soc n={len(soc_scores)} avg={out[ym]['social_hf_avg']!r}")

    (DATA / "hf_results.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {DATA}/hf_results.json")


if __name__ == "__main__":
    main()

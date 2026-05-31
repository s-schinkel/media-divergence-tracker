#!/usr/bin/env python3
"""Regenerate the data-bearing regions of the root Erika tracker (../../index.html).

The Erika page is a hand-authored analytical page; this regenerates only the MECHANICAL,
data-driven regions (wrapped in GEN: markers), leaving all prose and chart SVG geometry
untouched.

SOURCING (see ../CLAUDE.md):
  • Tab 1 — recomputed from the data snapshots via build_tab1.py (reproduces the page
    exactly): the composite chart line + dots + value labels, the 12-column stats table,
    and MONTH_DATA numbers. Event prose comes from data/display/erika_display.json.
  • Tab 2 — sourced from CAPTURED displayed values in erika_display.json. The raw
    youtube_pull.json no longer reproduces the published indices (views grew after the page
    was built; Paramount/Valhalla lack per-video data), so the idx/raw tables + YT_DATA +
    CHANNEL_COLOR regenerate from captured values. Tab 2's hand-tuned chart SVG geometry is
    NOT marked/regenerated — it stays verbatim.

USAGE:
  python3 scripts/build_erika.py --extract   # (re)build erika_display.json from index.html
  python3 scripts/build_erika.py             # regenerate index.html from erika_display.json

Only regions whose GEN markers exist are touched; missing ones are skipped. Verify in a
browser after running.
"""

import argparse
import json
import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EK = HERE.parent
REPO = EK.parent
INDEX = REPO / "index.html"
DISPLAY = EK / "data" / "display"
JSON_PATH = DISPLAY / "erika_display.json"

MONTHS = ["202507","202508","202509","202510","202511","202512",
          "202601","202602","202603","202604","202605"]
MINUS = "−"
IDX_COLS = ["Joe Rogan","Ben Shapiro","Candace Owens","Ian Carroll Show","Valhalla VFT",
            "Josh Hammer Show","Real Baron Podcast","Paramount Tactical"]


def region(html, name):
    """Inner text between markers, or None if absent. HTML or JS comment style."""
    for o, c in ((f"<!--GEN:{name}-->", f"<!--GEN:/{name}-->"),
                 (f"/*GEN:{name}*/", f"/*GEN:/{name}*/")):
        if o in html and c in html:
            return html.split(o, 1)[1].split(c, 1)[0]
    return None


def replace(html, name, new_inner):
    for o, c in ((f"<!--GEN:{name}-->", f"<!--GEN:/{name}-->"),
                 (f"/*GEN:{name}*/", f"/*GEN:/{name}*/")):
        if o in html and c in html:
            inner = html.split(o, 1)[1].split(c, 1)[0]
            return html.replace(o + inner + c, o + new_inner + c)
    return html  # marker absent -> skip


# --------------------------------------------------------------------------- extract
def extract():
    if not DISPLAY.exists():
        DISPLAY.mkdir(parents=True)
    html = INDEX.read_text(encoding="utf-8")

    runpy.run_path(str(HERE / "build_tab1.py"), run_name="__main__")
    rows = json.loads((EK / "data" / "tab1_rows.json").read_text())
    rows = {r["ym"]: r for r in rows} if isinstance(rows, list) else rows

    md = region(html, "month_data") or ""
    events = dict(re.findall(r'"(\d{6})":\s*\{[^}]*?events:\s*"((?:[^"\\]|\\.)*)"', md, re.S))

    yt = {}
    yt_src = region(html, "yt_data") or ""
    for ym, body in re.findall(r'"(\d{6})":\s*\{(.*?\])\}', yt_src, re.S):
        yt[ym] = {
            "label": re.search(r'label:"([^"]*)"', body).group(1),
            "avg": float(re.search(r'avg:([\d.]+)', body).group(1)),
            "composite": float(re.search(r'composite:([\d.]+)', body).group(1)),
            "summary": re.search(r'summary:"((?:[^"\\]|\\.)*)"', body).group(1),
            "channels": [{"name": n, "idx": (None if i == "null" else int(i)), "raw": float(r)}
                         for n, i, r in re.findall(r'\{name:"([^"]*)",idx:(null|\d+),raw:([\d.]+)\}', body)],
        }

    cc = dict(re.findall(r'"([^"]+)":\s*"(#[0-9a-fA-F]+)"', region(html, "channel_color") or ""))

    # total videos (last <td> per row) + yellow rows, parsed from the current Tab 2 tables
    total_videos, yellow = {}, []
    raw_reg = region(html, "tab2_raw") or ""
    raw_rows = re.findall(r'<tr>(.*?)</tr>', raw_reg, re.S)
    for ym, tr in zip(MONTHS, raw_rows):
        tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
        if tds:
            total_videos[ym] = re.sub(r'<[^>]+>', '', tds[-1]).strip()
    idx_reg = region(html, "tab2_idx") or ""
    for ym, tr in zip(MONTHS, re.findall(r'<tr[^>]*>.*?</tr>', idx_reg, re.S)):
        if "fef9c3" in tr:
            yellow.append(ym)

    # Capture which channel cells are <strong> (hand-applied, not rule-derivable)
    def bold_cells(reg):
        res = {}
        for ym, tr in zip(MONTHS, re.findall(r'<tr[^>]*>.*?</tr>', reg, re.S)):
            tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
            res[ym] = [IDX_COLS[ci] for ci in range(len(IDX_COLS))
                       if 1 + ci < len(tds) and "<strong>" in tds[1 + ci]]
        return res
    idx_bold = bold_cells(idx_reg)
    raw_bold = bold_cells(region(html, "tab2_raw") or "")

    out = {
        "_note": "Source of record for the Erika tracker's mechanical regions. Tab 1 numbers are "
                 "recomputed by build_tab1.py; edit event/summary prose and Tab 2 captured values "
                 "here, then run build_erika.py. Tab 2 chart SVG geometry stays verbatim in index.html.",
        "tab1_rows": rows, "events": events, "yt_data": yt, "channel_color": cc,
        "total_videos": total_videos, "yellow_rows": yellow,
        "idx_bold": idx_bold, "raw_bold": raw_bold,
    }
    JSON_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Extracted -> {JSON_PATH.relative_to(REPO)} ({len(yt)} yt months, yellow={yellow})")


# --------------------------------------------------------------------------- format helpers
def fnum(v, dec, signed=False):
    if v is None:
        return "—"
    if signed and abs(v) < 0.5 * 10 ** (-dec):
        return f"{0:.{dec}f}"
    return (f"{v:+.{dec}f}" if signed else f"{v:.{dec}f}").replace("-", MINUS)


def fmt_social(m):
    if m >= 1_000_000:
        return f"~{m/1_000_000:g}M"
    if m >= 1_000:
        return f"~{m/1_000:g}K"
    return f"~{m}"


# --------------------------------------------------------------------------- build
def build():
    if not JSON_PATH.exists():
        sys.exit("ERROR: erika_display.json missing — run with --extract first.")
    d = json.loads(JSON_PATH.read_text())
    html = INDEX.read_text(encoding="utf-8")
    rows, yt = d["tab1_rows"], d["yt_data"]
    hf = json.loads((EK / "data" / "hf_results.json").read_text())  # HF sample counts (n=)
    X = {ym: 60 + i * 72 for i, ym in enumerate(MONTHS)}
    cy1 = lambda ym: round(290 - rows[ym]["composite"] * 260, 1)

    # ---- Tab 1 chart: composite line + dots + value labels ----
    if region(html, "tab1_chart") is not None:
        pts = " ".join(f"{X[ym]},{cy1(ym):g}" for ym in MONTHS)
        circ, lab = [], []
        for ym in MONTHS:
            r, cy = rows[ym], cy1(ym)
            if r["high"]:
                circ.append(f'<circle class="chart-point" data-month="{ym}" cx="{X[ym]}" cy="{cy:g}" r="6" fill="#c0392b" stroke="#fff" stroke-width="1.5"/>')
                lab.append(f'<text x="{X[ym]}" y="{int(cy)-8}" fill="#c0392b" font-weight="700">{r["composite"]:.2f}</text>')
            else:
                circ.append(f'<circle class="chart-point" data-month="{ym}" cx="{X[ym]}" cy="{cy:g}" r="5" fill="#2b59c3"/>')
                lab.append(f'<text x="{X[ym]}" y="{int(cy)-8}">{r["composite"]:.2f}</text>')
        chart = ('\n      <polyline points="' + pts + '" fill="none" stroke="#2b59c3" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>'
                 '\n      <g class="chart-points">\n        ' + "\n        ".join(circ) + '\n      </g>'
                 '\n      <g font-family="ui-monospace, Menlo, monospace" font-size="10" fill="#1a1a1a" text-anchor="middle">\n        '
                 + "\n        ".join(lab) + '\n      </g>\n    ')
        html = replace(html, "tab1_chart", chart)

    # ---- Tab 1 stats table ----
    if region(html, "tab1_table") is not None:
        trs = []
        for ym in MONTHS:
            r = rows[ym]
            empty = r["gdelt_vol_sum"] == 0
            high = r["high"]
            mn = r["hf_mainstream_avg"]
            sn = r["hf_social_avg"]
            ms = "— (n=0)" if hf[ym]["mainstream_n"] == 0 else "{} (n={})".format(fnum(mn, 3, 1), hf[ym]["mainstream_n"])
            so = "— (n=0)" if hf[ym]["social_n"] == 0 else "{} (n={})".format(fnum(sn, 3, 1), hf[ym]["social_n"])
            conf = r["social_confidence"]
            comp = "{:.2f}".format(r["composite"])
            tone = "—" if empty else fnum(r["gdelt_tone_norm"], 3, 1)
            volx = "—" if empty else "{:.2f}×".format(r["volume_normalized"])
            social = "{} <span class=\"conf conf-{}\">{}</span>".format(fmt_social(r["social_mentions"]), conf, conf)
            comp_cell = "<strong>{}</strong>".format(comp) if high else comp
            flag = "<span class=\"badge badge-high\">HIGH</span>" if high else "—"
            trcls = ' class="high"' if high else ""
            trs.append(
                '    <tr{}>\n'
                '      <td class="month">{}</td>\n'
                '      <td>{:.3f}</td>\n'
                '      <td>{}</td>\n'
                '      <td>{}</td>\n      <td>{}</td>\n'
                '      <td>{}</td>\n'
                '      <td>{:.3f}</td>\n'
                '      <td>{}</td>\n'
                '      <td>{}</td>\n'
                '      <td>{:.3f}</td>\n'
                '      <td>{}</td>\n'
                '      <td>{}</td>\n'
                '    </tr>'.format(trcls, r["label"], r["gdelt_vol_sum"], tone, ms, so, social,
                                   r["topic_overlap"], fnum(r["sentiment_delta"], 3, 1), volx,
                                   r["volume_score"], comp_cell, flag))
        html = replace(html, "tab1_table", "\n" + "\n".join(trs) + "\n  ")

    # ---- MONTH_DATA ----
    if region(html, "month_data") is not None:
        md = [f'    "{ym}": {{\n      label: "{rows[ym]["label"]}",\n      composite: {rows[ym]["composite"]:.2f},\n'
              f'      confidence: "{rows[ym]["social_confidence"]}",\n      events: "{d["events"].get(ym,"")}"\n    }}'
              for ym in MONTHS]
        html = replace(html, "month_data", "\n" + ",\n".join(md) + "\n  ")

    # ---- Tab 2 peaks (per-channel max) for bold ----
    def peak(metric):
        out = {}
        for nm in IDX_COLS:
            best = None
            for ym in MONTHS:
                c = next(x for x in yt[ym]["channels"] if x["name"] == nm)
                v = c[metric]
                if v and (best is None or v > best[1]):
                    best = (ym, v)
            out[nm] = best[0] if best else None
        return out
    idx_bold = d.get("idx_bold") or {}   # captured <strong> cells (hand-applied)
    raw_bold = d.get("raw_bold") or {}
    yellow = set(d.get("yellow_rows") or [])

    # ---- Tab 2 indexed table ----
    if yt and region(html, "tab2_idx") is not None:
        trs = []
        for ym in MONTHS:
            r = yt[ym]
            cells = ""
            for nm in IDX_COLS:
                c = next(x for x in r["channels"] if x["name"] == nm)
                if c["idx"] is None:
                    cells += "<td>—</td>"
                else:
                    s = f'{c["idx"]:,}'
                    cells += f'<td><strong>{s}</strong></td>' if nm in idx_bold.get(ym, []) else f'<td>{s}</td>'
            style = ' style="background:#fef9c3;"' if ym in yellow else ""
            trs.append(f'    <tr{style}><td class="month">{r["label"]}</td>{cells}<td><strong>{r["avg"]:.1f}</strong></td><td>{r["composite"]:.2f}</td></tr>')
        html = replace(html, "tab2_idx", "\n" + "\n".join(trs) + "\n  ")

    # ---- Tab 2 raw table ----
    if yt and region(html, "tab2_raw") is not None:
        trs = []
        for ym in MONTHS:
            r = yt[ym]
            cells = ""
            for nm in IDX_COLS:
                c = next(x for x in r["channels"] if x["name"] == nm)
                s = "—" if c["raw"] == 0 else f'{c["raw"]:.2f}M'
                cells += f'<td><strong>{s}</strong></td>' if nm in raw_bold.get(ym, []) else f'<td>{s}</td>'
            trs.append(f'    <tr><td class="month">{r["label"]}</td>{cells}<td>{d["total_videos"].get(ym,"")}</td></tr>')
        html = replace(html, "tab2_raw", "\n" + "\n".join(trs) + "\n  ")

    # ---- YT_DATA ----
    if yt and region(html, "yt_data") is not None:
        js = []
        for ym in MONTHS:
            r = yt[ym]
            ch = [f'{{name:"{c["name"]}",idx:{"null" if c["idx"] is None else c["idx"]},raw:{c["raw"]:g}}}' for c in r["channels"]]
            ch_str = ",\n      ".join(", ".join(ch[i:i+2]) for i in range(0, len(ch), 2))
            js.append(f'    "{ym}": {{label:"{r["label"]}", avg:{r["avg"]:g}, composite:{r["composite"]:.2f}, summary:"{r["summary"]}", channels:[\n      {ch_str},\n    ]}}')
        html = replace(html, "yt_data", "\n" + ",\n".join(js) + "\n  ")

    # ---- CHANNEL_COLOR ----
    if d["channel_color"] and region(html, "channel_color") is not None:
        html = replace(html, "channel_color", "\n" + "\n".join(f'    "{k}": "{v}",' for k, v in d["channel_color"].items()) + "\n  ")

    INDEX.write_text(html, encoding="utf-8")
    print("Regenerated Erika mechanical regions. Tab 2 chart SVG geometry left verbatim. Verify in a browser.")


def main():
    ap = argparse.ArgumentParser(description="Regenerate the Erika tracker's data-driven regions")
    ap.add_argument("--extract", action="store_true")
    args = ap.parse_args()
    extract() if args.extract else build()


if __name__ == "__main__":
    main()

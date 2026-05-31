#!/usr/bin/env python3
"""Pull monthly view totals for Tab 2 from the YouTube Data API v3.

Resolves the 8 channels (by handle, channel ID, or playlist), walks each
channel's uploads playlist back to the date window, then bulk-fetches
videos.list statistics. Aggregates by month.

Quota cost: ~150 units total. Free daily quota is 10,000 units.

Output:
  data/youtube_pull.json  — per-channel monthly aggregates + video lists

Requires:
  YT_KEY env var — YouTube Data API v3 key
  (Generate one at https://console.cloud.google.com → enable YouTube Data API v3)

Usage:
  YT_KEY=AIza... python3 scripts/pull_youtube.py
"""
import json, os, sys, time, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

API_KEY = os.environ.get("YT_KEY")
if not API_KEY:
    sys.exit("Set YT_KEY env var to your YouTube Data API v3 key")

WINDOW_START = "2025-07-01T00:00:00Z"
WINDOW_END   = "2026-05-31T23:59:59Z"
BASE = "https://www.googleapis.com/youtube/v3"

CHANNELS = [
    {"name": "Joe Rogan",          "handle": "@joerogan"},
    {"name": "Ben Shapiro",        "handle": "@BenShapiro"},
    {"name": "Candace Owens",      "handle": "@RealCandaceO"},
    {"name": "Ian Carroll Show",   "handle": "@Iancarrollshow"},
    {"name": "Real Baron Podcast", "handle": "@realbaronpodcast"},
    {"name": "Valhalla VFT",       "handle": "@ValhallaVFT"},
    {"name": "Paramount Tactical", "channel_id": "UCWCLMT5T_ondX8VyCdCjOLQ"},
    # Josh Hammer Show is the Newsweek-hosted playlist, not the channel uploads
    {"name": "Josh Hammer Show",   "playlist": "PLbJbsiKs77FxKl9EuhpMDR-LgFrPKtlfX"},
]

quota_used = 0


def call(path, params):
    """One YouTube Data API call. Each call = 1 unit for the endpoints used here."""
    global quota_used
    params = {**params, "key": API_KEY}
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())
    quota_used += 1
    return data


def resolve(c):
    """Resolve handle / channel_id / playlist to (uploads_playlist_id, stats)."""
    if "handle" in c:
        d = call("channels", {"part": "id,statistics,contentDetails,snippet", "forHandle": c["handle"]})
        item = d["items"][0]
        return {
            "channel_id": item["id"],
            "uploads_playlist": item["contentDetails"]["relatedPlaylists"]["uploads"],
            "subs": int(item["statistics"].get("subscriberCount") or 0),
            "total_views": int(item["statistics"].get("viewCount") or 0),
            "video_count": int(item["statistics"].get("videoCount") or 0),
            "is_playlist_only": False,
        }
    if "channel_id" in c:
        d = call("channels", {"part": "id,statistics,contentDetails,snippet", "id": c["channel_id"]})
        item = d["items"][0]
        return {
            "channel_id": item["id"],
            "uploads_playlist": item["contentDetails"]["relatedPlaylists"]["uploads"],
            "subs": int(item["statistics"].get("subscriberCount") or 0),
            "total_views": int(item["statistics"].get("viewCount") or 0),
            "video_count": int(item["statistics"].get("videoCount") or 0),
            "is_playlist_only": False,
        }
    # Playlist-only (Josh Hammer Show): we walk the playlist directly
    d = call("playlists", {"part": "snippet,contentDetails", "id": c["playlist"]})
    pl = d["items"][0]
    host_id = pl["snippet"]["channelId"]
    h = call("channels", {"part": "statistics,snippet", "id": host_id})
    host = h["items"][0] if h.get("items") else {}
    stats = host.get("statistics", {})
    return {
        "channel_id": host_id,
        "uploads_playlist": c["playlist"],
        "subs": int(stats.get("subscriberCount") or 0),
        "total_views": int(stats.get("viewCount") or 0),
        "video_count": int(stats.get("videoCount") or 0),
        "is_playlist_only": True,
    }


def walk_playlist(playlist_id):
    """Page through playlistItems back to the window start."""
    vids = []
    token = None
    pages = 0
    while True:
        params = {"part": "snippet,contentDetails", "playlistId": playlist_id, "maxResults": 50}
        if token:
            params["pageToken"] = token
        d = call("playlistItems", params)
        pages += 1
        items = d.get("items", [])
        if not items:
            break
        oldest = None
        for it in items:
            vid = it["contentDetails"]["videoId"]
            pub = it["contentDetails"].get("videoPublishedAt") or it["snippet"]["publishedAt"]
            vids.append({"video_id": vid, "published_at": pub, "title": it["snippet"]["title"]})
            if oldest is None or pub < oldest:
                oldest = pub
        token = d.get("nextPageToken")
        if oldest and oldest < WINDOW_START:
            break
        if not token or pages > 80:
            break
    return vids


def fetch_stats(video_ids):
    out = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        d = call("videos", {"part": "statistics", "id": ",".join(batch)})
        for item in d.get("items", []):
            out[item["id"]] = int(item["statistics"].get("viewCount") or 0)
    return out


def main():
    results = {}
    for c in CHANNELS:
        print(f"\n=== {c['name']} ===")
        info = resolve(c)
        print(f"  channel_id={info['channel_id']}  uploads={info['uploads_playlist']}")
        print(f"  subs={info['subs']:,}  total_views={info['total_views']:,}  videos={info['video_count']}")
        vids = walk_playlist(info["uploads_playlist"])
        print(f"  walked {len(vids)} items")
        in_window = [v for v in vids if WINDOW_START <= v["published_at"] <= WINDOW_END]
        print(f"  {len(in_window)} in window")
        stats = fetch_stats([v["video_id"] for v in in_window])

        by_month = defaultdict(lambda: {"count": 0, "views": 0, "video_ids": []})
        for v in in_window:
            ym = v["published_at"][:7].replace("-", "")
            by_month[ym]["count"] += 1
            by_month[ym]["views"] += stats.get(v["video_id"], 0)
            by_month[ym]["video_ids"].append(v["video_id"])
        for ym in sorted(by_month):
            b = by_month[ym]
            print(f"    {ym}: {b['count']:3d} videos, {b['views']:>14,} views")
        results[c["name"]] = {"channel_info": info, "by_month": dict(by_month)}

    print(f"\nQuota used: {quota_used} units (of 10,000/day free tier)")
    (DATA / "youtube_pull.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"Wrote {DATA}/youtube_pull.json")


if __name__ == "__main__":
    main()

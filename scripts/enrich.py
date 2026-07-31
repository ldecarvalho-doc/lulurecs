#!/usr/bin/env python3
"""Enrich lulurecs entries with TMDB metadata (description + poster).

Usage:
    export TMDB_API_KEY=your_key            # free key from themoviedb.org/settings/api
    python3 scripts/enrich.py               # fills missing posters/descriptions in all entries
    python3 scripts/enrich.py --only bad-buddy   # just one entry
    python3 scripts/enrich.py --overwrite   # replace existing descriptions too

Only 'poster' is overwritten by default; existing descriptions and all your
notes/ratings/tags are never touched unless you pass --overwrite.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
IMG_BASE = "https://image.tmdb.org/t/p/w500"


def tmdb(path, api_key, **params):
    params["api_key"] = api_key
    url = f"https://api.themoviedb.org/3/{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.load(r)


def search(entry, api_key):
    if entry["type"] not in ("series", "movie", "musical"):
        return None, None
    kind = "tv" if entry["type"] == "series" else "movie"
    q = entry["title"].split("(")[0].strip()
    res = tmdb(f"search/{kind}", api_key, query=q, first_air_date_year=entry.get("year", ""))
    results = res.get("results") or tmdb(f"search/{kind}", api_key, query=q).get("results")
    return (results[0], kind) if results else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="lgbtq-visual-media.json", help="data file in data/ to enrich")
    ap.add_argument("--only", help="entry id to enrich")
    ap.add_argument("--overwrite", action="store_true", help="also replace existing descriptions")
    args = ap.parse_args()
    data_file = os.path.join(DATA_DIR, args.file)

    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        sys.exit("Set TMDB_API_KEY first (free key: https://www.themoviedb.org/settings/api)")

    with open(data_file, encoding="utf-8") as f:
        entries = json.load(f)

    changed = 0
    for e in entries:
        if args.only and e["id"] != args.only:
            continue
        needs_poster = not e.get("poster")
        needs_desc = args.overwrite or not e.get("description")
        if not (needs_poster or needs_desc):
            continue
        try:
            hit, kind = search(e, api_key)
        except Exception as exc:
            print(f"  ! {e['id']}: {exc}")
            continue
        if not hit:
            print(f"  ? {e['id']}: no TMDB match")
            continue
        if needs_poster and hit.get("poster_path"):
            e["poster"] = IMG_BASE + hit["poster_path"]
            changed += 1
        if needs_desc and hit.get("overview"):
            e["description"] = hit["overview"]
            changed += 1
        name = hit.get("name") or hit.get("title")
        print(f"  ✓ {e['id']} ← TMDB {kind}: {name}")

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Done — {changed} fields updated.")


if __name__ == "__main__":
    main()

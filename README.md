# lulurecs ✦

My recommendations for friends — a static site, versioned in git, deployed free on GitHub Pages.

## How it works

No build step. `index.html` reads JSON files from `data/` and renders cards with search, filters, tags, ratings, my notes, and a favorites feature (saved in each visitor's browser via localStorage — no accounts, no backend).

```
index.html                  ← the whole site
data/categories.json        ← list of categories (set "enabled": true to launch one)
data/lgbtq-visual-media.json ← the recs for that category
scripts/enrich.py           ← optional: pull descriptions/posters from TMDB
```

## Adding a recommendation

Add an object to the category's JSON file:

```json
{
  "id": "unique-slug",
  "title": "Show Name",
  "type": "series",          // series | movie | list (add your own types freely)
  "country": "TH",           // ISO code → flag is automatic
  "year": 2024,
  "luRating": 5,             // 1–5, or null if unrated
  "description": "Neutral synopsis (or let enrich.py fill it from TMDB).",
  "notes": "Your personal take — shown as 'Lu's notes'.",
  "tags": ["bl", "free-on-youtube"],
  "links": [{ "label": "Watch on YouTube", "url": "https://..." }],
  "poster": null             // URL, or let enrich.py fill it from TMDB
}
```

Commit, push, done — that's the versioning system.

## Posters & descriptions from TMDB

Get a free API key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api), then:

```bash
export TMDB_API_KEY=yourkey
python3 scripts/enrich.py
```

It fills in missing `poster` and `description` fields (never touches your notes, ratings, or tags). Posters are hotlinked from TMDB's CDN, so the repo stays tiny.

## Rec lists (curated groups for friends)

`data/lists.json` holds named lists that group existing recs by their `id` — no tags involved, and lists can mix categories:

```json
{
  "id": "gabi",
  "title": "listinha pro gabi 💜",
  "description": "optional blurb shown at the top",
  "items": ["bad-buddy", "heartstopper", "hamilton"]
}
```

Items appear in the order you write them ("Curated order" sort). Every list gets a shareable link: `https://<your-site>/#list=gabi` opens the site with that list already selected. Delete an entry from `lists.json` any time; the recs themselves are untouched.

## Adding a new category

1. Create `data/music.json` (same entry format — omit fields that don't apply).
2. In `data/categories.json`, set that category's `"enabled": true`.

## Local preview

```bash
python3 -m http.server
# → http://localhost:8000
```

(Opening index.html directly won't work — browsers block fetch() on file://.)

## Deploying on GitHub Pages

1. Push to `main`.
2. Repo → Settings → Pages → Source: **Deploy from a branch** → `main` / `/ (root)`.
3. Site appears at `https://ldecarvalho-doc.github.io/lulurecs/`.

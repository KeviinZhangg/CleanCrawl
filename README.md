# CleanCrawl

**GNOMI Hackathon 2026** — A respectful crawler for news articles, blog posts, and wiki-style pages.

CleanCrawl discovers, cleans, deduplicates, and scores informational web pages while respecting `robots.txt`, detecting anti-bot blocks, and avoiding crawler traps.

## Build order (for you + Cursor)

| Order | Plan | What it builds |
|---|---|---|
| 1 | Pipeline (`main.py`, `crawler/*`) | Core crawl logic — phases 0–8 |
| 2 | `FRONTEND_PLAN.md` | FastAPI wrapper + React dashboard |
| 3 | `CLOUD_PLAN.md` | Docker, Postgres, live deploy |

**Don't cloud-package or UI-wrap a broken pipeline** — get `python main.py demo` and `pytest` green first.

## Quick Start

```bash
pip install -r requirements.txt
python main.py demo          # Run offline demo with fixtures + stats
python main.py stats         # Show crawl dashboard
python main.py crawl seeds.txt
```

### Web Dashboard (React + FastAPI)

**Terminal 1 — API** (use Python 3.11+; 3.14 may break FastAPI/Pydantic):

```bash
/opt/homebrew/bin/python3.11 -m uvicorn api.server:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 — start a crawl, watch the live activity feed, browse articles with explainable quality breakdown.

**Production** (single port):

```bash
cd frontend && npm run build
/opt/homebrew/bin/python3.11 -m uvicorn api.server:app --port 8000
# serves API + built UI at http://localhost:8000
```

**UI-only dev** (no backend): set `VITE_USE_MOCK=true` in `frontend/.env`

## Cloud / Docker (one command)

```bash
docker compose up --build
# → http://localhost:8000 (UI + API + Postgres, data persists across restarts)
```

See [DEPLOY.md](DEPLOY.md) for Render deployment, env vars, and demo seeding.

**Interview line:** *"Same Docker image runs locally and in the cloud — only env vars differ."*

## Architecture

```
URL → trap check → fetch → classify → extract → dedup → quality score → store
```

| Module | Purpose |
|---|---|
| `crawler/fetcher.py` | robots.txt, rate limits, retries, anti-bot detection |
| `crawler/classifier.py` | Article vs listing/login/tag pages |
| `crawler/extractor.py` | trafilatura + fallbacks, messy HTML handling |
| `crawler/deduplicator.py` | Canonical URL, normalization, MinHash near-dup |
| `crawler/traps.py` | Pagination, archive, filter URL traps |
| `crawler/quality.py` | Explainable 5-factor quality score |
| `storage/db.py` | SQLAlchemy persistence — SQLite local, Postgres cloud |
| `api/server.py` | FastAPI + SSE + `/api/health` |
| `stats/report.py` | Rich dashboard from crawl logs |

## CLI Commands

```bash
# Crawl from seed file
python main.py crawl demo_seeds.txt

# With JS rendering fallback (requires: playwright install chromium)
python main.py crawl seeds.txt --render

# Link following (depth 1)
python main.py crawl seeds.txt --max-depth 1

# Stats dashboard
python main.py stats

# Full demo (crawl + stats)
python main.py demo
```

## Demo Strategy

The `demo_seeds.txt` file mixes live URLs (Wikipedia) with **offline fixtures** (`fixture://...`) that exercise every code path:

- Clean article extraction
- Broken HTML / messy flag
- Category page classification skip
- Cloudflare block detection
- 5 duplicate URL variants → 1 stored
- Near-duplicate text detection
- Crawler trap skip (`/archive/.../page/400`)

## Tests

```bash
pytest tests/ -v
```

## Design Decisions (for judges)

- **Async + per-domain locks** — parallel across domains, serial within one (politeness at scale)
- **trafilatura** — generalizes across site templates better than hand-rolled rules
- **MinHash + LSH** — sublinear near-duplicate lookup as corpus grows
- **Never trust HTTP 200 alone** — Cloudflare challenges return 200 with challenge bodies
- **Explainable quality** — weighted factors + human-readable reasons, not a black-box score

## Rubric Coverage

| Area | Module |
|---|---|
| Crawl safety | `fetcher.py`, `traps.py`, `frontier.py` |
| Anti-bot detection | `fetcher.py` |
| Content extraction | `extractor.py` |
| Duplicate detection | `deduplicator.py` |
| Messy HTML | `extractor.py` |
| Page classification | `classifier.py` |
| Quality scoring | `quality.py` |
| Stats dashboard | `stats/report.py` |
| JS fallback (bonus) | `browser.py` |
| Recrawl scheduler (bonus) | `scheduler/recrawl.py` |

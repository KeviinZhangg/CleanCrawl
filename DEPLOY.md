# CleanCrawl — Deployment Guide

Same Docker image runs locally and in the cloud — only env vars differ.

## Prerequisites

- Docker + Docker Compose
- (Optional) Render account for live URL

## Local — full cloud parity

```bash
docker compose up --build
```

Open http://localhost:8000

- UI at `/`
- API at `/api/*`
- Health check at `/api/health`
- Postgres persists data in the `pgdata` volume

**Verify persistence:** run a crawl → `docker compose restart` → articles still there.

## Pre-seed demo data

```bash
# With compose running:
docker compose exec app python scripts/seed_demo.py
```

Or locally without Docker:

```bash
python3 main.py demo
```

## Environment variables

Copy `.env.example` → `.env`. Key vars:

| Variable | Local default | Cloud |
|---|---|---|
| `DATABASE_URL` | `sqlite:///cleancrawl.db` | `postgresql+psycopg2://...` from platform |
| `PORT` | `8000` | Set by platform (Render injects this) |
| `CORS_ORIGINS` | localhost dev origins | Your deployed URL |
| `ENABLE_BROWSER` | `false` | `false` (keeps image small) |
| `MAX_CRAWL_SEEDS` | `30` | `30` (prevents accidental huge crawls) |

## Deploy to Render

1. Push repo to GitHub
2. Create **New Blueprint** → connect repo → Render reads `render.yaml`
3. Provisioned automatically:
   - Web service (Docker)
   - Postgres database (`cleancrawl-db`)
4. Set `CORS_ORIGINS` to your Render URL (e.g. `https://cleancrawl.onrender.com`)
5. After first deploy, seed data:
   ```bash
   # Render shell or one-off job:
   python scripts/seed_demo.py
   ```

## Demo strategy at the venue

1. **Primary:** `docker compose up` on your laptop (no Wi-Fi dependency)
2. **Reveal:** "It's also live at [URL]" — open the deployed instance
3. Narrate the live activity feed → stats → article quality breakdown

## Troubleshooting

| Issue | Fix |
|---|---|
| Empty dashboard after redeploy | Using SQLite on ephemeral disk — switch to Postgres `DATABASE_URL` |
| `/api/health` fails | Check `PORT` env; uvicorn must bind `0.0.0.0` |
| CORS errors | Add your origin to `CORS_ORIGINS` |
| Playwright needed | Rebuild with `ENABLE_BROWSER=true` build arg (large image) |

## Build browser-enabled image (optional)

```bash
docker build --build-arg ENABLE_BROWSER=true -t cleancrawl:browser .
```

Set `ENABLE_BROWSER=true` at runtime. Only use if JS rendering demo is required.

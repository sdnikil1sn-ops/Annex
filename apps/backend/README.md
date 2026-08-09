# ANNEX Backend

FastAPI service for the ANNEX platform — hardened core, Supabase data layer,
Firebase Auth, Redis, and Celery.

## Run locally

```bash
cp .env.example .env
docker compose up -d postgres redis
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8010

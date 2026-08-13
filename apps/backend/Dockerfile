FROM python:3.13-slim

# Install uv (the package manager you already use)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies (cached layer) — paths are from the REPO ROOT
COPY apps/backend/pyproject.toml apps/backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the backend
COPY apps/backend/ .

# Run migrations, then start the API on Render's $PORT
#CMD ["sh", "-c", "ls -la /etc/secrets 2>&1; uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
#CMD ["sh", "-c", "echo '=== DB DIAG ==='; uv run python -c \"from app.core.config import get_settings; import psycopg; s=get_settings(); u=s.database_url; print('APP_DB_URL=' + u); c=psycopg.connect(u.replace('+psycopg',''), connect_timeout=10); print('RAW_CONNECT_OK=' + str(c.execute('select 1').fetchone()))\" 2>&1; uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT"]

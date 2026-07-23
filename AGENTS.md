# AGENTS.md

## Cursor Cloud specific instructions

This is a Python 3.11+ FastAPI service (the "Business Analytics Platform") managed with Poetry. It
depends on PostgreSQL and Redis. Standard commands live in `README.md` and `CONTRIBUTING.md`; the
notes below only cover non-obvious, environment-specific gotchas for running it in the cloud VM.

### Services and startup

The update script only refreshes Python dependencies (`poetry install --with dev`). System services
are NOT started by it — start them yourself at the beginning of a session if they are not already up:

- PostgreSQL 16: `sudo pg_ctlcluster 16 main start`
- Redis 7: `sudo redis-server --daemonize yes --dir /var/lib/redis`

A `.env` (git-ignored) must exist for the app and for running it locally. If missing, create it from
`.env.example`, then apply the two required fixes below. The dev database role/db are
`analytics`/`analytics` (password `analytics`), created with:
`sudo -u postgres psql -c "CREATE ROLE analytics LOGIN PASSWORD 'analytics';" -c "CREATE DATABASE analytics OWNER analytics;"`

Run the app in dev mode: `poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
(API docs at `/docs`). Lint: `poetry run black --check src tests`, `poetry run ruff check src tests`,
`poetry run mypy src`. Tests: `poetry run pytest`.

### Non-obvious gotchas

- Poetry is installed to `~/.local/bin` (on `PATH` via `~/.bashrc`). Use a login shell (`bash -l`) if
  `poetry` is not found.
- `.env.example` ships `ALLOWED_ORIGINS=*`, which pydantic-settings CANNOT parse for the `List[str]`
  field and crashes startup. In your `.env` use JSON form: `ALLOWED_ORIGINS=["*"]` (or omit the line
  to use the default). Also set a real `SECRET_KEY` (`openssl rand -hex 32`) and point `DATABASE_URL`
  at the local db: `postgresql+asyncpg://analytics:analytics@localhost:5432/analytics`.
- Tests use an in-memory SQLite DB (via `aiosqlite`) for the ORM, but several tests
  (`test_etl.py`, `test_concurrency.py`) require a live Redis at `localhost:6379`.
- Known pre-existing failures unrelated to environment setup (do NOT treat as env breakage):
  - `GET /ready` returns 503 if the code passes a raw `"SELECT 1"` string to `session.execute`
    (SQLAlchemy 2.0 requires `text(...)`). This is fixed in the codebase on branches with CI fixes.
- The `SecurityHeadersMiddleware` CSP blocks the CDN-hosted Swagger UI assets, so `/docs` renders
  blank in a browser out of the box (the API and `/openapi.json` still work fine via curl). Loading
  `/docs` in a browser requires allowing `https://cdn.jsdelivr.net` in the CSP.

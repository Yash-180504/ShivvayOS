# ShivvayOS

ShivvayOS is a multi-agent autonomous business operating system. The current MVP has a FastAPI backend, a Next.js dashboard, PostgreSQL persistence, LLM provider abstraction, prompt versioning, workflow context propagation, response validation, and task quality scoring.

## Architecture

- `backend/` - FastAPI API, orchestration service, agents, LLM providers, prompt registry, validation, SQLAlchemy models, and tests.
- `frontend/` - Next.js App Router dashboard for workflow submission, run history, task execution, and timelines.
- `alembic/` - PostgreSQL schema migrations.
- `docker-compose.yml` - local production-style orchestration for backend and frontend.

The backend uses async SQLAlchemy with `asyncpg`. Plain Neon URLs like `postgresql://...?...sslmode=require` are normalized internally to `postgresql+asyncpg://...` with SSL connect args.

## Environment

Create `.env.local` from `.env.example`:

```bash
cp .env.example .env.local
```

Set:

```bash
DATABASE_URL=postgresql://USER:PASSWORD@HOST/neondb?sslmode=require&channel_binding=require
DEFAULT_LLM_PROVIDER=mock
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
INTERNAL_API_BASE_URL=http://backend:8000
```

Use `openai` or `anthropic` for `DEFAULT_LLM_PROVIDER` only after setting the matching API key. Secrets belong in `.env.local`, which is ignored by git.

## Docker Setup

Build and start both services:

```bash
make start
```

Run migrations against Neon from inside the backend container:

```bash
make migrate
```

Open:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`

Stop services:

```bash
make stop
```

Follow logs:

```bash
make logs
```

Build images only:

```bash
make build
```

## Local Development

Backend:

```bash
pip install -r backend/requirements.txt
alembic upgrade head
uvicorn backend.main:app --reload
```

Frontend:

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

## Tests And Validation

Backend tests:

```bash
make test
```

Frontend production build:

```bash
make frontend-build
```

Docker build:

```bash
docker compose --env-file .env.local build
```

## API Surface

- `POST /api/v1/workflows/run`
- `GET /api/v1/workflows`
- `GET /api/v1/workflows/{run_id}`
- `GET /api/v1/workflows/{run_id}/timeline`
- `GET /api/v1/tasks/{task_id}`

## Persistence

The backend persists:

- workflow runs
- task execution states
- task quality scores
- workflow timeline events
- final CEO executive synthesis

Task results include:

- `confidence_score`
- `reasoning_quality_score`
- `schema_validity_score`

## Screenshots

Add screenshots here after running a populated workflow:

- Dashboard overview: `docs/screenshots/dashboard.png`
- Workflow detail: `docs/screenshots/workflow-detail.png`

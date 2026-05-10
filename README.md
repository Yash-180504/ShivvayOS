# ShivvayOS

## Backend Setup

1. Create a Python virtual environment and install dependencies:
   - `pip install -r backend/requirements.txt`
2. Configure environment variables in `.env`:
   - `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/shivvayos`
3. Run migrations:
   - `alembic upgrade head`
4. Start API:
   - `uvicorn backend.main:app --reload`

## Persistence Layer

The backend now persists:
- workflow runs (`workflow_runs`)
- task execution states (`task_executions`)
- workflow timeline events (`workflow_events`)
- final CEO executive synthesis (`workflow_runs.executive_summary`)

## Query APIs

- `GET /api/v1/workflows`
- `GET /api/v1/workflows/{run_id}`
- `GET /api/v1/workflows/{run_id}/timeline`
- `GET /api/v1/tasks/{task_id}`

## Tests

- Run unit tests: `pytest backend/tests -q`

## LLM providers

Configure optional providers in `.env` (see `.env.example`):

- `DEFAULT_LLM_PROVIDER` — `mock` (default), `openai`, or `anthropic`
- `OPENAI_API_KEY` / `DEFAULT_OPENAI_MODEL`
- `ANTHROPIC_API_KEY` / `DEFAULT_ANTHROPIC_MODEL`
- `LLM_REQUEST_TIMEOUT_SECONDS`

If `openai` or `anthropic` is selected but the API key is missing, the app falls back to the mock provider.

Prompt templates live under `backend/prompts/` (`ceo/`, `marketing/`, `finance/`).

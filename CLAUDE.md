# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XAdmin is a full-stack admin system:

- Backend: FastAPI, SQLModel/SQLAlchemy, PostgreSQL, Alembic, pytest, uv
- Frontend: Vue 3, TypeScript, Vite, Pinia, Pinia Colada, Element Plus, Vue Router, Vue I18n
- Runtime: Docker Compose with Traefik, PostgreSQL, backend, frontend, and a backend prestart service

The backend exposes `/api/v1` APIs and OpenAPI JSON; the frontend generates an axios-based client from that OpenAPI schema.

## Common Commands

### Full stack with Docker Compose

Compose commands expect required variables from `.env` such as `STACK_NAME`, database credentials, image names, domain/frontend host, and first superuser settings.

```bash
# Start development stack
docker compose watch
docker compose up -d --build

# Logs
docker compose logs backend
docker compose logs frontend

# Stop services
docker compose stop backend frontend
docker compose down
```

Development ports from `docker-compose.override.yml`:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Traefik dashboard: `http://localhost:8090`

### Backend

```bash
cd backend
uv sync
uv run fastapi dev app/main.py
uv run fastapi run --reload app/main.py

# Tests
uv run bash scripts/tests-start.sh
uv run pytest
uv run pytest app/tests/api/routes/test_users.py
uv run pytest app/tests/api/routes/test_users.py -k test_name
bash scripts/test.sh app/tests/api/routes/test_users.py -k test_name  # from repo root, Docker

# Lint/format/type-check
uv run ruff check app scripts
uv run ruff check app scripts --fix
uv run ruff format app scripts
uv run mypy app
bash scripts/format.sh

# Migrations
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

`backend/scripts/tests-start.sh` waits for DB readiness via `app/tests_pre_start.py`, then runs `backend/scripts/test.sh`, which uses coverage around pytest.

### Frontend

```bash
cd frontend
pnpm install
pnpm run dev
pnpm run build
pnpm run lint
pnpm run lint-fix
pnpm run format
pnpm run typecheck
pnpm run preview

# Regenerate client from existing frontend/openapi.json
pnpm run generate-client
```

### Repository scripts

```bash
# Format backend and frontend from repo root
bash scripts/format.sh

# Regenerate API client from backend schema
bash scripts/generate-client.sh

# Build/deploy helpers
bash scripts/build.sh
bash scripts/build-push.sh
bash scripts/deploy.sh
```

## Backend Architecture

`backend/app/main.py` creates the FastAPI app, configures CORS/docs, registers `/api/v1` routes, and records operation logs in middleware. `backend/app/api/main.py` composes login, users, rules, roles, operation logs, and utility routers.

Data layer pattern:

- `app/models/`: SQLModel table models and API schemas (`*Base`, table model, `*Create`, `*Update`, `*Public`).
- `app/crud/`: model-specific database operations.
- `app/crud/common.py`: pagination, ordering, and common-search filtering.
- `app/models/link.py`: many-to-many link tables.
- `app/alembic/`: migration environment and revisions.

Permission data is centered around `app/core/security.py` and `app/models/security.py`. `ApiPermissions` paths expand into CRUD-like scopes required by routes with `Security(...)`; `rules` connects frontend navigation and permission nodes.

Common table filtering crosses frontend and backend: `XaTable` sends JSON `common_search` using operators from `app/models/query.py`; `build_common_search_params` parses it, and `app/crud/common.py` converts it into SQLModel/SQLAlchemy where clauses. Keep frontend operator strings aligned with backend `Operator`.

Database setup flows through the `prestart` service in Docker Compose, which runs `backend/scripts/prestart.sh`; local test startup uses `app/tests_pre_start.py` to wait for PostgreSQL before running pytest.

## Frontend Architecture

`frontend/src/main.ts` initializes Vue. `src/router/index.ts` uses hash history, NProgress/loading state, and lazy-loads route i18n through `src/lang/autoload.ts`.

API calls use the generated client in `src/client/`, configured by `openapi-ts.config.ts` and `src/hey-api.ts`. Regenerate this client after backend OpenAPI changes.

CRUD admin pages use `src/utils/xaTable.ts` for table query state, form state, Pinia Colada queries/mutations, common-search serialization, selection, and add/edit/delete flow. System pages under `src/views/system/` instantiate `XaTable` and pair page `index.vue` files with popup forms.

Pinia stores under `src/stores/` hold app config, current user info, nav tabs, and cached constants. Permission-sensitive UI uses auth helpers from `src/utils/common.ts` / `src/utils/useAuth.ts` and should align with backend scopes.

## Configuration Files

- `.env`: Compose and application environment variables.
- `docker-compose.yml`: main service graph for db, prestart, backend, frontend, and Traefik labels.
- `docker-compose.override.yml`: local development ports, reload commands, and Compose watch settings.
- `backend/pyproject.toml`: backend dependencies plus ruff and mypy configuration.
- `frontend/package.json`: frontend scripts and dependency versions.
- `frontend/openapi-ts.config.ts`: generated API client configuration.

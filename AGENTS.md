# Repository Guidelines

## Project Structure & Module Organization

XAdmin is a full-stack admin app. Backend code lives in `backend/app`: FastAPI routes in `api/routes`, SQLModel models in `models`, CRUD helpers in `crud`, configuration in `core`, and Alembic migrations in `alembic`. Backend tests mirror these areas under `backend/tests`.

Frontend code lives in `frontend/src`: pages in `views`, UI in `components`, routing in `router`, stores in `stores`, styles in `styles`, and generated API client files in `client`. Static screenshots are in `img`; Compose files and root scripts support local and CI workflows.

## Build, Test, and Development Commands

### Frontend

- `bun run dev`: start the Vite frontend.
- `bun run build`: build for production.
- `bun run preview`: preview the production build.
- `bun run lint`, `bun run format`, `bun run typecheck`: run ESLint, Prettier, and Vue checks.
- `bun run test` or `bun run test:ui`: run Playwright headlessly or with the UI.
- `bun run generate-client`: regenerate frontend API client from OpenAPI schema.

### Backend

- `cd backend && fastapi dev app/main.py`: start the backend dev server.
- `cd backend && uv run bash scripts/test.sh`: run pytest with coverage report.
- `cd backend && uv run bash scripts/lint.sh`: run mypy, `ty`, Ruff lint, and Ruff format check.
- `cd backend && uv run alembic upgrade head`: apply database migrations.
- `cd backend && uv run alembic downgrade -1`: rollback one migration.
- `cd backend && uv run alembic revision --autogenerate -m "description"`: generate a new migration.

### Full Stack (Docker Compose)

- `docker compose watch`: start the full local stack in watch mode (preferred for development).
- `docker compose up -d`: start the full local stack in detached mode.
- `docker compose logs <service>`: view logs for a specific service (e.g., `backend`, `frontend`, `db`).
- `bash scripts/test.sh`: build containers, run backend and Playwright tests, then tear down.
- `bash scripts/generate-client.sh`: regenerate `frontend/src/client` after backend API changes.

### Pre-commit Hooks

The project uses `prek` (a modern pre-commit alternative). Install it once:

- `cd backend && uv run prek install -f`

Run manually on all files:

- `cd backend && uv run prek run --all-files`

## Environment Prerequisites

- [bun](https://bun.sh) for frontend package management and scripts.
- [uv](https://docs.astral.sh/uv) for Python environment and dependency management.
- Docker and Docker Compose for local stack development.
- PostgreSQL (via Docker Compose) for the database.

## Quick Start

For new contributors:

```bash
# 1. Install dependencies
cd frontend && bun install
cd ../backend && uv sync

# 2. Configure environment
cp .env .env.local  # Edit secrets in .env.local

# 3. Start the full stack
docker compose watch

# 4. Apply database migrations (first run only)
cd backend && uv run alembic upgrade head
```

## Local Development URLs

When running locally:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs (Swagger UI): http://localhost:8000/docs
- Traefik UI (Docker Compose): http://localhost:8090

## Coding Style & Naming Conventions

Python targets 3.10 and uses Ruff plus strict mypy. Keep backend modules lowercase with snake_case filenames, classes in PascalCase, and functions, variables, and pytest tests in snake_case.

Frontend uses Vue 3, TypeScript, Vite, Element Plus, ESLint, and Prettier. Prefer PascalCase for Vue components, camelCase for TypeScript symbols, and route/view names that match the feature area. Do not hand-edit `frontend/src/client`; regenerate it.

## Testing Guidelines

Backend tests use pytest and coverage. Place tests under `backend/tests/<area>/test_*.py`, matching the module being exercised. Update API route, CRUD, and model tests when backend behavior changes.

Frontend end-to-end tests use Playwright from `frontend/playwright.config.ts`. Keep specs focused on user workflows and run `bun run test` before submitting UI changes.

## Commit & Pull Request Guidelines

Git history uses concise Conventional Commit-style prefixes such as `fix:`, `chore:`, and `refactor:`; Chinese descriptions are common and acceptable. Keep commits scoped to one change.

Pull requests should include a short summary, test results, issue links when available, and screenshots or recordings for visible UI changes. Note migrations, `.env` changes, or regenerated client code.

## Gotchas

- `CLAUDE.md` is a symlink to `AGENTS.md`. Edit `AGENTS.md` to update project guidelines.
- The backend lint script runs both `mypy` and `ty` (a newer Python type checker). Both must pass.
- You can mix local and Docker Compose development: both the local dev servers and Docker Compose use the same ports (frontend 5173, backend 8000). Stop a Docker service and start its local equivalent without changing URLs.
- The `docker compose watch` command is the preferred way to run the full stack during development, as it auto-reloads on file changes.
- Pre-commit hooks use `prek` (not the traditional `pre-commit` package). After installing with `uv run prek install -f`, hooks run automatically on `git commit`.
- The pre-commit hooks include `generate-client.sh`: modifying backend API code automatically regenerates `frontend/src/client`. If you see unstaged client changes after committing backend code, that's expected — stage them and commit again.

## Security & Configuration Tips

Local configuration is read from `.env`. Replace default secrets such as `SECRET_KEY`, `FIRST_SUPERUSER_PASSWORD`, and `POSTGRES_PASSWORD`, and do not commit real credentials.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XAdmin is a full-stack admin system with:
- **Backend**: FastAPI + SQLModel + PostgreSQL + Alembic
- **Frontend**: Vue 3 + TypeScript + Vite + Pinia + Pinia Colada + Element Plus
- **DevOps**: Docker Compose + Traefik

Based on [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) and [BuildAdmin](https://github.com/build-admin/buildadmin).

## Development Commands

### Docker Compose (Recommended)

```bash
# Start full development stack
docker compose watch

# View logs
docker compose logs
docker compose logs backend

# Stop services
docker compose stop frontend
docker compose stop backend

# Run tests in running stack
docker compose exec backend bash scripts/tests-start.sh
docker compose exec backend bash scripts/tests-start.sh -x  # stop on first error
```

### Backend (Local)

```bash
cd backend

# Install dependencies
uv sync
source .venv/bin/activate

# Run development server
fastapi dev app/main.py
# or
fastapi run --reload app/main.py

# Run tests
bash ../scripts/test.sh

# Database migrations (run inside container or with local env)
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Linting and formatting
ruff check .
ruff check --fix .
mypy .
```

### Frontend (Local)

```bash
cd frontend

# Install dependencies (uses pnpm)
pnpm install

# Development server
pnpm run dev

# Build
pnpm run build

# Lint and format
pnpm run lint
pnpm run lint-fix
pnpm run format
pnpm run typecheck

# Generate API client from OpenAPI schema
pnpm run generate-client
```

### Scripts

Located in `./scripts/`:
- `test.sh` - Run backend tests in Docker
- `test-local.sh` - Run backend tests locally
- `generate-client.sh` - Generate frontend API client
- `format.sh` - Format backend code
- `build.sh`, `build-push.sh`, `deploy.sh` - Build and deployment

## Architecture

### Backend (`./backend/`)

**Tech Stack**: FastAPI, SQLModel (SQLAlchemy + Pydantic), PostgreSQL, Alembic, pytest, uv

**Directory Structure**:
```
app/
├── api/routes/        # API endpoints (FastAPI routers)
│   ├── users.py       # User CRUD and auth
│   ├── roles.py       # Role management
│   ├── rules.py       # Permission rules (menu/tree structure)
│   └── operation_logs.py
├── crud/              # CRUD operations
│   ├── user.py
│   ├── role.py
│   ├── rule.py
│   └── common.py      # Search/filter utilities
├── models/            # SQLModel models
│   ├── user.py
│   ├── role.py
│   ├── rule.py
│   ├── operation_log.py
│   ├── security.py    # Permission models
│   └── link.py        # Many-to-many link tables
├── core/              # Core configuration
│   ├── config.py      # Settings from env
│   ├── db.py          # Database engine/session
│   ├── security.py    # JWT, passwords, ApiPermissions enum
│   └── deps.py        # FastAPI dependencies
├── alembic/           # Database migrations
└── tests/             # pytest tests
```

**Key Patterns**:

1. **Permission System**: Auto-generated CRUD permissions based on API paths defined in `ApiPermissions` enum (`core/security.py`). Each API path gets create/read/update/delete scopes.

2. **Model Pattern**: SQLModel classes with:
   - `*Base` - Shared fields
   - `*` - Table model (database)
   - `*Create`, `*Update` - API input schemas
   - `*Public`, `*Public` - API output schemas

3. **CRUD Pattern**: Functions in `crud/` accept `SessionDep` and operate on models. Common search/filter logic in `crud/common.py`.

4. **API Pattern**: Routes use `Security(get_current_user, scopes=[...])` for permission checks. Common query params (pagination, ordering, search) in `api/deps.py`.

5. **Database Migrations**: Alembic with autogenerate. New models must be imported in `models/__init__.py` for detection.

### Frontend (`./frontend/`)

**Tech Stack**: Vue 3, TypeScript, Vite, Pinia, Pinia Colada (data fetching), Element Plus, Vue Router, Vue I18n

**Directory Structure**:
```
src/
├── client/            # Auto-generated OpenAPI client (@hey-api)
├── components/        # Vue components
│   ├── table/         # Table, TableHeader components
│   ├── xaInput/       # Input components including remoteSelect
│   └── formItem/      # Form field wrapper
├── views/             # Page components (routes)
│   ├── system/        # System management (users, roles, rules, logs)
│   ├── routine/       # User profile, etc.
│   └── home.vue       # Dashboard
├── router/            # Vue Router configuration
├── stores/            # Pinia stores
│   ├── config.ts      # App config (theme, layout)
│   ├── userInfo.ts    # Current user state
│   └── navTabs.ts     # Tab navigation state
├── utils/             # Utilities
│   ├── xaTable.ts     # Table class with CRUD operations
│   ├── request.ts     # HTTP request handling
│   ├── router.ts      # Router guards
│   └── common.ts      # Common utilities
└── lang/              # i18n translations
    ├── zh-cn/
    └── en/
```

**Key Patterns**:

1. **Table CRUD**: Uses `XaTableClass` (`utils/xaTable.ts`) which encapsulates:
   - API calls (index, add, edit, del)
   - Form state management
   - Table actions and events
   - Common search/filter

2. **Data Fetching**: Uses Pinia Colada (`useQuery`, `useMutation`) for:
   - Server state caching
   - Background refetching
   - Loading states

3. **API Client**: Auto-generated from OpenAPI schema via `@hey-api/openapi-ts`. Generated files in `src/client/`.

4. **Permission Display**: Frontend shows/hides UI based on user scopes. Scope names generated from `ApiPermissions` enum.

5. **I18n**: Language files organized by route path. Auto-loading configured in `lang/autoload.ts`.

## Key Configuration Files

- `.env` - Main environment configuration (domain, database, secrets)
- `docker-compose.yml` - Production stack
- `docker-compose.override.yml` - Development overrides (volume mounts, hot reload)
- `backend/pyproject.toml` - Python dependencies and tool config (ruff, mypy)
- `frontend/package.json` - Node dependencies and scripts

## Common Development Tasks

### Adding a New Database Model

1. Create model in `backend/app/models/`
2. Import in `backend/app/models/__init__.py`
3. Create CRUD functions in `backend/app/crud/`
4. Create API routes in `backend/app/api/routes/`
5. Add to `backend/app/api/main.py` router
6. Generate migration: `alembic revision --autogenerate -m "Add model"`
7. Apply migration: `alembic upgrade head`
8. Regenerate frontend client: `./scripts/generate-frontend-client.sh`

### Adding API Permissions

Add new `ApiPermissions` enum value in `backend/app/core/security.py`:
```python
V1_NEW_RESOURCE = ApiPermission(path=f"{settings.API_V1_STR}/new-resource/")
```
This auto-generates create/read/update/delete scopes.

### Frontend Table Page

Use `XaTableClass` pattern from existing views like `views/system/role/`:
- `index.vue` - Page with Table, TableHeader, PopupForm
- `popupForm.vue` - Add/Edit form component
- Inject `xaTable` instance and use its state/methods

## URLs (Development)

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Traefik UI: http://localhost:8090

## Testing

Backend uses pytest. Tests in `backend/app/tests/`.

```bash
# Run all tests
bash scripts/test.sh

# Run in active stack
docker compose exec backend bash scripts/tests-start.sh

# Coverage report generated at htmlcov/index.html
```

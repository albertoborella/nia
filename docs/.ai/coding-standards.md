# Coding Standards — NIA

## General Principles

- Readability over cleverness
- Explicit over implicit
- Fail fast, fail loud
- Small files, single responsibility
- No comments unless the "why" is non-obvious

## Python / FastAPI Backend

### Structure

```
backend/app/
├── main.py           # App entry, middleware registration
├── config.py         # Pydantic Settings (env vars)
├── database.py       # SQLModel engine + session dependency
├── models/           # SQLModel table models (one entity per file)
├── schemas/          # Pydantic request/response models
├── routers/          # FastAPI routers (one per domain)
├── services/         # Business logic (pure functions preferred)
└── utils/            # Helpers, constants
```

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Files | `snake_case.py` | `boletin_service.py` |
| Classes | `PascalCase` | `BoletinCreate` |
| Functions | `snake_case` | `get_boletin_by_id()` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_FILE_SIZE_MB` |
| DB tables | `snake_case` (plural) | `boletines`, `incidentes` |
| API routes | `kebab-case` | `/api/v1/boletines/{id}/completar-seccion` |

### Models (SQLModel)

```python
class Boletin(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str
    estado: str = Field(default="borrador")
    # Use enums for fixed sets
    # Reference other tables with Field(foreign_key="table.id")
```

- One model per file in `models/`
- Separate table models from schema models
- Use `uuid.uuid4` as default for all IDs
- Enums: define as Python `Enum`, use `sa_column` for DB

### Schemas (Pydantic)

- Separate `*Create`, `*Update`, `*Response` schemas
- Response schemas use `model_config = ConfigDict(from_attributes=True)`
- Never expose `password_hash` in response schemas

### Routers

- One router per domain file in `routers/`
- Use `APIRouter(prefix="/api/v1/...", tags=[...])`
- Dependency injection for DB sessions: `def get_db()`
- Explicit status codes: `status_code=status.HTTP_201_CREATED`

### Services

- Pure functions preferred (no side effects unless necessary)
- Business logic lives here, not in routers
- Raise `HTTPException` with specific status codes and detail messages
- Log errors with structured context (user_id, action, entity)

### Error Handling

```python
# Standard error response
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={"code": "BOLETIN_NOT_FOUND", "message": "Boletin not found"}
)
```

## SvelteKit Frontend

### Structure

```
frontend/src/
├── routes/           # File-based routing
│   ├── +layout.svelte    # Main layout (nav, auth)
│   ├── login/            # Login page
│   ├── dashboard/        # Main dashboard
│   └── boletines/[id]/   # Newsletter detail
├── lib/
│   ├── api/          # API client (fetch wrapper)
│   ├── components/   # Reusable components (PascalCase)
│   ├── stores/       # Svelte stores
│   └── utils/        # Helpers
```

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Components | `PascalCase.svelte` | `BoletinCard.svelte` |
| Routes | `kebab-case/` | `boletines/`, `notas-colaborador/` |
| Stores | `snake_case.ts` | `auth.store.ts` |
| Utils | `snake_case.ts` | `format-date.ts` |
| CSS classes | `kebab-case` | `.boletin-card`, `.status-badge` |

### Components

- Single responsibility: one component, one job
- Props use `export let` (Svelte 4) or `$props()` (Svelte 5)
- Keep templates readable; extract complex logic to utils
- Use `{#if}` / `{#each}` for conditional/list rendering

### API Calls

```typescript
// Use the project's fetch wrapper, not raw fetch
import { api } from '$lib/api/client';

const data = await api.get('/boletines');
const created = await api.post('/boletines', { body: payload });
```

- Handle errors with try/catch
- Show user feedback on success/failure
- Never store tokens in localStorage (cookies only)

### Stores

- Use Svelte stores for global state (auth, current boletin)
- Prefer `$page.data` for route-level data
- Keep stores minimal — derive where possible

## SQLModel / PostgreSQL

- Use `alembic` for ALL schema changes (never manual SQL)
- Migrations must be reversible
- Use `uuid` for primary keys (not auto-increment)
- Foreign keys with explicit `Field(foreign_key="table.column")`
- JSONB for flexible content (section content, audit details)
- Index columns used in WHERE/JOIN frequently
- Use `ON DELETE CASCADE` or `SET NULL` explicitly on FKs

## File Naming Summary

| Location | Pattern | Example |
|----------|---------|---------|
| Backend models | `entity.py` | `boletin.py` |
| Backend schemas | `entity.py` | `boletin.py` |
| Backend routers | `entities.py` | `boletines.py` |
| Backend services | `entity_service.py` | `boletin_service.py` |
| Frontend components | `Entity.svelte` | `BoletinCard.svelte` |
| Frontend routes | `kebab-case/` | `boletines/` |
| Migrations | `{id}_{description}.py` | `001_initial_schema.py` |

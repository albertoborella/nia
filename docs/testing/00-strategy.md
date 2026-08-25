# Testing Strategy — NIA

> This strategy covers the full NIA system. For business rules under test, see [business-rules.md](../requirements/business-rules.md). For use case workflows, see the [use-cases/](../use-cases/) directory.

## 1. Testing Philosophy

NIA is an internal editorial tool with strict data integrity requirements. A food safety bulletin must be accurate, complete, and reproducible. Testing exists to guarantee that correctness.

### Guiding principles

- **Test the contract, not the implementation.** API endpoints and data schemas are the source of truth; tests verify behavior against them.
- **Deterministic over realistic.** Mock external dependencies (AI, file storage) to produce repeatable results. Real integration tests run separately in controlled environments.
- **Fail early, fail loud.** A test that passes silently is worse than no test. If a business rule is violated, the test suite must block the pipeline.
- **Data correctness is non-negotiable.** Every database write, every enum constraint, every foreign key relationship gets exercised. A corruption in bulletin data is a production incident.

### Test pyramid

```
        ╱  E2E  ╲           Fewer, slower, higher confidence
       ╱──────────╲
      ╱ Integration ╲        Moderate count, verify contracts
     ╱────────────────╲
    ╱      Unit        ╲     Many, fast, isolated
   ╱────────────────────╲
```

| Level | Count | Speed | Confidence | Scope |
|-------|-------|-------|------------|-------|
| Unit | Many (~70%) | Milliseconds | Component correctness | Models, services, utilities, pure logic |
| Integration | Moderate (~20%) | Seconds | Contract correctness | API endpoints, DB operations, AI service boundaries |
| E2E | Few (~10%) | Minutes | User workflow correctness | Full browser workflows, critical paths only |

### AI testing considerations

AI calls are non-deterministic and costly. Every test that touches AI must use mocked responses by default. Real AI integration tests are opt-in and gated behind a slow-test flag (`pytest -m ai_real`).

---

## 2. Testing Levels

### 2.1 Unit Tests

**Scope:** Pure logic with no external dependencies. Tests verify business rules from [business-rules.md](../requirements/business-rules.md) and functional requirements from [functional-requirements.md](../requirements/functional-requirements.md).

| Area | What to test | Example |
|------|-------------|---------|
| **Models** | Field defaults, enum validation, relationship cardinality | `Boletin.estado` defaults to `borrador` |
| **Schemas** | Pydantic validation, serialization/deserialization, field constraints | `BoletinCreate.nombre` rejects empty strings |
| **Services** | Business logic branches, state transitions, error paths | `boletin_service.complete_section()` validates ordering |
| **Utils** | Date formatting, markdown transformation, slug generation | `format_period()` handles edge cases |
| **Prompt templates** | Variable substitution, missing variable handling | `render_prompt()` raises on missing `{{periodo_inicio}}` |

**Location:** `backend/tests/unit/`, colocated with the source file when appropriate.

### 2.2 Integration Tests

**Scope:** Components working together through defined interfaces. Validates API contracts from [01-api-design.md](../architecture/01-api-design.md).

| Area | What to test | Example |
|------|-------------|---------|
| **API endpoints** | Request/response contract, status codes, auth middleware | `POST /api/v1/boletines` creates and returns 201 |
| **Database operations** | CRUD through SQLModel, migrations, constraint enforcement | Duplicate email rejected at DB level |
| **Auth flow** | Login, token refresh, role-based access control | Collaborator blocked from `POST /api/v1/prompts/execute` |
| **AI service boundary** | Prompt construction, response parsing, error handling | `ia_service.consultar_incidentes()` handles malformed AI response |
| **File operations** | Upload validation, storage, retrieval | `.pdf` accepted, `.exe` rejected |

**Location:** `backend/tests/integration/`

**Database strategy:** Use testcontainers to spin up an ephemeral PostgreSQL instance per test session. Each test gets a clean transaction that rolls back on teardown. No shared mutable state between tests.

### 2.3 End-to-End Tests

**Scope:** Full user workflows through the browser, verifying the entire stack. Workflows are derived from use cases in [use-cases/](../use-cases/).

| Workflow | Priority | Coverage |
|----------|----------|----------|
| Login → create bulletin → complete first section | P0 | Full path (UC-01, UC-02, UC-03) |
| Login → AI incident consultation → edit table → generate article | P0 | Full path (UC-04, UC-06, UC-07) |
| Login → upload note → assign to bulletin | P1 | Full path (UC-05) |
| Director-only action blocked for collaborator | P1 | Auth guard (UC-01) |
| Bulletin closure → immutability check | P0 | Data integrity (UC-02, BN-08) |

**Location:** `frontend/tests/e2e/` (Playwright)

**Rules:**
- E2E tests run against a seeded database, not production.
- Each test cleans up after itself (or uses a shared teardown).
- Network calls to the real API are allowed; external AI calls are mocked at the service layer.

### 2.4 Performance Tests

**Scope:** Response times and throughput for critical operations.

| Metric | Target | How |
|--------|--------|-----|
| API endpoint response time (p95) | < 500ms | Locust or k6 |
| AI consultation (mocked) | < 2s end-to-end | Integration test with timer |
| Bulletin compilation (mocked) | < 5s | Integration test with timer |
| Concurrent users (auth) | 20 simultaneous | Locust |

**Location:** `backend/tests/performance/`

Performance tests are excluded from the default CI run and triggered manually or on release candidates.

---

## 3. Testing Tools

### Backend

| Tool | Purpose | Configuration |
|------|---------|---------------|
| `pytest` | Test runner | `pyproject.toml` `[tool.pytest.ini_options]` |
| `pytest-asyncio` | Async test support for FastAPI | `asyncio_mode = "auto"` |
| `pytest-cov` | Coverage reporting | `--cov=app --cov-report=html --cov-fail-under=80` |
| `pytest-postgresql` | Ephemeral PostgreSQL fixtures | `postgresql_proc` fixture |
| `httpx` + `TestClient` | Async HTTP testing with FastAPI | `AsyncClient(transport=ASGITransport(app=app))` |
| `factory-boy` | Test data factories | Custom factories per entity |
| `respx` | Mock HTTP calls to AI API | For `ia_service` boundary tests |

### Frontend

| Tool | Purpose | Configuration |
|------|---------|---------------|
| `vitest` | Unit/component tests | Integrated with Vite config |
| `@testing-library/svelte` | DOM assertion helpers | — |
| `playwright` | E2E browser testing | `playwright.config.ts` |

### Database

| Tool | Purpose | Configuration |
|------|---------|---------------|
| `testcontainers` | Ephemeral PostgreSQL in Docker/Podman | `PostgresContainer` class |
| `alembic` | Migration testing | Run migrations in CI against test DB |

### AI Mocking

```python
# Pattern for mocking AI responses in tests
# backend/tests/integration/test_ia_service.py

import respx
import httpx

@respx.mock
async def test_consultar_incidentes_returns_structured_data():
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=MOCK_AI_RESPONSE)
    )
    result = await ia_service.consultar_incidentes(
        periodo_inicio="2026-01-01",
        periodo_fin="2026-03-31"
    )
    assert len(result) > 0
    assert result[0]["pais"] is not None
```

**Factory for AI responses:** Create a dedicated fixture module (`tests/fixtures/ai_responses.py`) with representative JSON payloads for each prompt type:
- `INCIDENT_QUERY_RESPONSE` — array of incident objects
- `ARTICLE_GENERATION_RESPONSE` — markdown content
- `MALFORMED_RESPONSE` — missing required fields
- `EMPTY_RESPONSE` — empty array
- `ERROR_RESPONSE` — AI service error

---

## 4. Coverage Targets

| Layer | Minimum | Target | Enforcement |
|-------|---------|--------|-------------|
| Backend overall | 80% | 90% | CI blocks on < 80% |
| Critical paths (services, models) | 90% | 95% | CI blocks on < 90% |
| Frontend overall | 70% | 80% | CI warns on < 70% |
| E2E critical workflows | 100% of P0 workflows | — | Manual review |

### Critical paths (always required at 90%+):

- `boletin_service` — state transitions, section ordering (BN-01, BN-08)
- `ia_service` — prompt rendering, response parsing (BN-04)
- `auth_service` — login, token refresh, role checks (BN-09)
- `notas` — upload, status transitions, assignment (BN-03)
- `incidentes` — creation, editing, article generation (BN-04, BN-05)

### Coverage reporting

```bash
# Backend
pytest --cov=app --cov-report=html --cov-report=term --cov-fail-under=80

# Frontend
vitest run --coverage
```

HTML reports generated at `htmlcov/` (backend) and `coverage/` (frontend). CI uploads artifacts for review.

---

## 5. Test Data Management

### Factory pattern

Each entity gets a factory using `factory-boy`:

```python
# backend/tests/factories.py

import factory
import uuid
from app.models.boletin import Boletin

class BoletinFactory(factory.Factory):
    class Meta:
        model = Boletin

    id = factory.LazyFunction(uuid.uuid4)
    nombre = factory.Sequence(lambda n: f"Boletin Test {n}")
    periodo_inicio = "2026-01-01"
    periodo_fin = "2026-03-31"
    fecha_publicacion_estimada = "2026-04-15"
    estado = "borrador"
```

### Fixtures hierarchy

```
conftest.py (root)
├── db_session          # Fresh DB session per test (rollback)
├── db_container        # PostgreSQL container (session scope)
├── authenticated_client # httpx client with valid JWT
├── director_client     # Client authenticated as director
├── collaborator_client # Client authenticated as collaborator
└── sample_boletin      # Pre-created bulletin for tests
```

### Database cleanup

- **Unit tests:** No DB access (pure functions).
- **Integration tests:** Transaction-per-test with rollback. No cleanup needed.
- **E2E tests:** Database reset before each test suite via `TRUNCATE ... CASCADE` or Alembic downgrade/upgrade cycle.

### Test data principles

- Never hardcode UUIDs — use factories that generate them.
- Use `factory.Sequence` for unique fields (names, emails).
- Use `factory.LazyFunction` for computed defaults.
- Test fixtures live in `tests/fixtures/` — not in test files.

---

## 6. AI Testing Strategy

AI is a critical dependency. Tests must cover three dimensions:

### 6.1 Mocked responses (default, fast)

Every test that touches AI uses mocked HTTP responses. No network calls.

| Test | Mock | Assertion |
|------|------|-----------|
| Prompt rendering | — | Variables substituted correctly |
| Response parsing (happy path) | Valid JSON array | All fields mapped to Incident model |
| Response parsing (malformed) | Missing fields | Graceful error, no crash |
| Response parsing (empty) | `[]` | Empty list returned |
| AI service error | 500 / timeout | Retry logic or user-friendly error |
| Article generation | Markdown string | Stored in section content |

### 6.2 Real AI integration (optional, slow)

```bash
# Run only when explicitly requested
pytest -m ai_real
```

- Gated behind `pytest.mark.ai_real`.
- Requires `IA_API_KEY` in environment.
- Runs against a fixed prompt with a known input.
- Validates response **structure** (not content) — ensures the AI returns parseable JSON.
- Skipped in CI by default; available for manual validation.

### 6.3 Response format validation

AI responses are validated against a Pydantic schema before storage:

```python
class AIIncidentResponse(BaseModel):
    incidente: str
    producto: str
    patogeno: str
    organismo: str
    pais: str
    riesgo: Literal["alto", "medio", "bajo"]
    fecha_inicio: date | None
    # ...
```

If the AI returns data that doesn't match, the service rejects it and logs the raw response for debugging. Tests must verify this rejection path.

---

## 7. CI/CD Integration

### Pipeline stages

```
push/PR → lint → typecheck → unit tests → integration tests → build → (E2E on main)
```

### Stage details

| Stage | Tools | Blocks merge? | Timeout |
|-------|-------|---------------|---------|
| Lint | `ruff`, `eslint`, `prettier` | Yes | 1 min |
| Type check | `pyright`, `svelte-check` | Yes | 2 min |
| Unit tests | `pytest -m "not ai_real"` | Yes | 3 min |
| Integration tests | `pytest` with testcontainers | Yes | 10 min |
| Coverage check | `pytest-cov --fail-under=80` | Yes | — |
| Build | `podman build` | Yes | 5 min |
| E2E (main only) | `playwright` | No (warn) | 15 min |
| Performance (manual) | `locust` | No | — |

### Coverage in CI

```yaml
# Example CI step
- name: Run tests with coverage
  run: |
    pytest --cov=app --cov-report=xml --cov-fail-under=80
    coverage report --fail-under=80

- name: Upload coverage report
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: htmlcov/
```

### Performance benchmarks

- Not blocking in CI.
- Run against staging environment on release candidates.
- Track p50, p95, p99 latencies for key endpoints.
- Fail if p95 degrades by > 20% from baseline.

---

## 8. Test Naming Conventions

### Backend (pytest)

```
test_<function_or_method>_<scenario>_<expected_outcome>
```

| Pattern | Example |
|---------|---------|
| `test_complete_section_valid_order_returns_completed` | Happy path |
| `test_complete_section_wrong_order_raises_error` | Validation failure |
| `test_complete_section_already_completed_is_idempotent` | Edge case |
| `test_create_boletin_missing_nombre_returns_422` | Schema validation |
| `test_consultar_incidentes_ai_timeout_returns_503` | External failure |

**Module naming:** Mirror the source structure.

```
tests/
├── unit/
│   ├── test_boletin_model.py          → tests app/models/boletin.py
│   ├── test_boletin_service.py        → tests app/services/boletin_service.py
│   └── test_prompt_renderer.py        → tests app/utils/prompt_renderer.py
├── integration/
│   ├── test_boletines_api.py          → tests app/routers/boletines.py
│   ├── test_auth_flow.py              → tests app/routers/auth.py + services/auth_service.py
│   └── test_ia_service_boundary.py    → tests app/services/ia_service.py (with mocked HTTP)
└── factories.py                       → test data factories
```

### Frontend (Vitest)

```
<ComponentName>.test.ts
```

| File | Tests |
|------|-------|
| `BoletinCard.test.ts` | Renders correctly, handles click, shows status badge |
| `IncidentTable.test.ts` | Sorts by column, filters by country, empty state |
| `formatDate.test.ts` | Formats ISO string, handles null, handles timezone |

### E2E (Playwright)

```
<workflow>.spec.ts
```

| File | Workflow |
|------|----------|
| `bulletin-creation.spec.ts` | Login → create → verify in list |
| `incident-pipeline.spec.ts` | Login → query AI → edit table → generate article |
| `auth-roles.spec.ts` | Director access vs collaborator restrictions |

---

## 9. Test Environment Configuration

### Environment variables for testing

```bash
# backend/.env.test
DATABASE_URL=postgresql://test:test@localhost:5433/nia_test
IA_API_KEY=test-key-not-real
SECRET_KEY=test-secret-for-testing-only
IA_API_BASE_URL=http://localhost:8080/mock
ENVIRONMENT=testing
```

### Test database

- Separate database from development (`nia_test`).
- Created by `testcontainers` or a pre-provisioned CI service.
- Migrations run automatically at session start.
- No data persists between test sessions.

---

## Appendix: Checklist for New Features

Before merging any new feature:

- [ ] Unit tests for business logic
- [ ] Integration tests for new API endpoints
- [ ] Schema validation tests for new request/response models
- [ ] AI mock fixtures if the feature touches AI
- [ ] Coverage delta: no decrease in overall coverage
- [ ] Existing tests still pass
- [ ] Performance regression check (if touching hot path)

# Workflow — NIA

## Git Workflow

### Branching

```
main          ← production-ready code
  └── feature/*    ← new features (e.g., feature/incident-table)
  └── fix/*        ← bug fixes
  └── docs/*       ← documentation-only changes
```

- `main` is always deployable
- Feature branches merge via Pull Request (PR)
- Squash commits on merge for clean history

### Commits

- Use **conventional commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- One logical change per commit
- Never commit secrets, `.env`, or credentials
- Include scope when helpful: `feat(backend): add incident CRUD`

### Pull Requests

- PR title summarizes the change
- PR description: what changed, why, how to test
- Reference related issues if applicable
- Keep PRs under 400 lines (use chained PRs for larger changes)

## SDD Documentation Flow

This project follows **Specification-Driven Development**. Changes go through:

```
Vision → Requirements → Domain → Architecture → Spec → Design → Tasks → Apply → Verify → Archive
```

### Phase Artifacts

| Phase | Produces | Lives in |
|-------|----------|----------|
| Explore | Context analysis | `docs/specs/{change}/explore` |
| Propose | Change proposal | `docs/specs/{change}/proposal` |
| Spec | Requirements + scenarios | `docs/specs/{change}/spec` |
| Design | Technical design | `docs/specs/{change}/design` |
| Tasks | Implementation plan | `docs/specs/{change}/tasks` |
| Apply | Code implementation | Source code |
| Verify | Test results | `docs/specs/{change}/verify` |
| Archive | Consolidated specs | `docs/specs/` + source |

### Key Rules

- Each phase must complete before the next starts
- Specs define **what**; design defines **how**
- Tasks must be atomic and independently testable
- Archive consolidates delta specs into main documentation

## Code Review

- Every PR requires review before merge
- Review lens: Risk → Readability → Reliability → Resilience
- Check: Does the code match the spec? Are tests passing?
- Security-sensitive changes (auth, prompts) require extra scrutiny

## Testing

| Type | Tool | Scope |
|------|------|-------|
| Unit tests | pytest | Services, utilities |
| API tests | pytest + httpx | Endpoint contracts |
| Frontend tests | Vitest | Components, stores |
| Integration | pytest + testcontainers | DB + API flows |
| E2E | Playwright (future) | Critical user journeys |

- Test before implementing (TDD encouraged)
- All new endpoints require tests
- Test both success and error paths

## Deployment

- **Dev**: `podman-compose up` (hot reload)
- **Production**: `podman-compose -f compose.prod.yml up -d`
- Migrations: `alembic upgrade head` after deploy
- No zero-downtime for MVP (single instance)
- Backup: daily `pg_dump` via cron

## Definition of Ready

Before starting work, confirm:
- [ ] Spec exists and is approved
- [ ] Design is complete (for non-trivial changes)
- [ ] Tasks are broken down
- [ ] Test strategy is defined

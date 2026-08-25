# Definition of Done — NIA

A task or change is **done** when ALL applicable criteria are met.

## Code Quality

- [ ] Code follows project coding standards (`coding-standards.md`)
- [ ] No linter errors (Python: ruff; Svelte: svelte-check)
- [ ] No type errors (Python: mypy/pyright; TS: tsc)
- [ ] No hardcoded secrets, credentials, or API keys
- [ ] Error handling covers all failure paths (DB, AI API, file uploads)
- [ ] Input validation on all API endpoints (Pydantic schemas)

## Testing

- [ ] Unit tests for new business logic (services)
- [ ] API tests for new/modified endpoints (happy + error paths)
- [ ] All existing tests still pass (`pytest`, `npm test`)
- [ ] Edge cases tested (empty states, invalid input, unauthorized access)

## Documentation

- [ ] SDD spec exists and matches implementation (if applicable)
- [ ] API endpoints documented (OpenAPI auto-generated from FastAPI)
- [ ] Environment variables documented in `.env.example`
- [ ] Migration scripts included (if schema changed)

## Security

- [ ] Auth checks on protected endpoints (JWT validation + role check)
- [ ] No SQL injection vectors (parameterized queries only)
- [ ] Prompt injection prevention (user input not concatenated into prompts)
- [ ] File upload validation (type, size, UUID naming)
- [ ] Sensitive data not logged (passwords, tokens, AI responses with PII)

## Performance

- [ ] No N+1 queries (use joins/preloading)
- [ ] Pagination on list endpoints
- [ ] AI calls have timeout configured
- [ ] No blocking operations in request handlers

## Integration

- [ ] Frontend consumes the API correctly (no contract mismatches)
- [ ] Database migrations are reversible
- [ ] Container builds succeed (Dockerfile/Podman)
- [ ] Works in dev environment (`podman-compose up`)

## Review

- [ ] PR reviewed by at least one person
- [ ] CI checks pass (lint, test, build)
- [ ] Changelog updated (if user-facing change)

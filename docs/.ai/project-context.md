# NIA — Project Context

## What is NIA?

**NIA** (Noticias Inocuidad Alimentaria) is an **internal editorial platform** for producing a periodic food safety newsletter. It is NOT a public-facing site.

- **Purpose**: Help editors collect, organize, analyze, and publish food safety incident reports from around the world
- **AI role**: Assist human editorial work (collect, organize, synthesize). Humans decide and sign.
- **Product**: A structured newsletter with 6 sections published periodically

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | SvelteKit (SSR + CSR) |
| Backend | FastAPI (Python) |
| ORM | SQLModel |
| Database | PostgreSQL 16+ |
| Auth | JWT in httpOnly cookies |
| Containers | Podman (Dockerfile-compatible) |
| Migrations | Alembic |

## Newsletter Sections (ordered)

1. **Editorial** — Director's opinion piece (human-written)
2. **Global Incidents Article** — AI-assisted analysis of food safety incidents (core value)
3. **Contributor Notes** — External articles (.pdf/.docx) from scientific sources
4. **Incidents Table** — Structured table of selected global incidents
5. **Sponsors** — Sponsor acknowledgments (manual)
6. **Index** — Auto-generated table of contents

## Key Entities

| Entity | Description |
|--------|------------|
| Boletín | A newsletter edition with status lifecycle: `borrador` → `en_progreso` → `completado` → `cerrado` |
| Sección | One of the 6 newsletter parts, each with type-specific content in JSONB |
| Incidente | Structured food safety incident data (AI-generated, human-reviewed) |
| Prompt | Predefined AI prompt templates with variables (`{{periodo_inicio}}`, etc.) |
| Nota de Colaborador | Uploaded article (.pdf/.docx) from external contributors |
| Auspiciante | Newsletter sponsor |
| Usuario | System user with role: `director` or `colaborador` |

## Core Workflow

```
Predefined Prompt → AI returns JSON → DB table → Editor reviews/cleans
    → Article generation prompt → AI generates Markdown → Human edits
    → Publication format
```

## Repository Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI entry
│   ├── config.py         # Settings & env vars
│   ├── database.py       # SQLModel connection
│   ├── models/           # SQLModel entities
│   ├── schemas/          # Pydantic request/response
│   ├── routers/          # API endpoints by domain
│   ├── services/         # Business logic
│   └── middleware/       # CORS, logging, audit
├── alembic/              # DB migrations
└── tests/

frontend/
├── src/
│   ├── routes/           # SvelteKit file-based routing
│   └── lib/
│       ├── api/          # API client (fetch wrapper)
│       ├── components/   # Reusable Svelte components
│       └── stores/       # Svelte stores (global state)
```

## Key Documentation

| Path | Content |
|------|---------|
| `docs/vision/` | Project purpose, scope, objectives |
| `docs/requirements/` | Functional/non-functional requirements, business rules |
| `docs/domain/` | Entity definitions, data model |
| `docs/architecture/` | System architecture, API design, security, deployment |
| `docs/specs/` | SDD specifications |
| `docs/decisions/` | Architecture decision records |

## Environment Variables (sensitive — never commit)

- `DATABASE_URL`, `JWT_SECRET_KEY`, `IA_API_KEY`, `IA_API_BASE_URL`, `CORS_ORIGINS`
- Use `.env` (gitignored); provide `.env.example` without real values

## Constraints

- Internal admin tool only — no public users, no registration
- AI assists, humans decide and sign every published piece
- All data must be traceable to sources (scientific rigor)
- Sections complete in strict chronological order
- Closed newsletters cannot be edited (create new edition for corrections)

# ADR-001: Technology Stack Selection

**Date:** 2026-08-25
**Status:** Accepted
**Deciders:** Alberto Borella

---

## Context

NIA (Noticias Inocuidad Alimentaria) is an internal editorial platform for producing a monthly food safety bulletin. The system requires:

- A server-rendered frontend with rich interactivity for content editing
- A REST API backend with async request handling for AI calls
- A relational database with strict referential integrity across complex editorial entities
- A modern Python ecosystem compatible with SQLModel (Pydantic + SQLAlchemy)

The team is a solo developer building the MVP. Technology choices must minimize cognitive overhead while supporting a small but long-lived internal tool.

## Decision

**SvelteKit + FastAPI + SQLModel + PostgreSQL**

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | SvelteKit (latest stable) | SSR for initial load, CSR for interactivity, file-based routing, minimal boilerplate |
| Backend | FastAPI (latest stable) | Native async for AI API calls, automatic OpenAPI docs, Pydantic validation |
| ORM | SQLModel (latest stable) | Unifies Pydantic schemas and SQLAlchemy models in a single class; native to FastAPI |
| Database | PostgreSQL 16+ | JSONB for flexible section content, mature full-text search, proven relational integrity |

## Alternatives Considered

### React / Next.js
- **Pros:** Massive ecosystem, large talent pool, excellent component libraries.
- **Cons:** Heavier runtime, more complex state management, React Server Components add architectural overhead for a small app. Overkill for a content-focused internal tool.
- **Verdict:** Rejected — complexity not justified for the scale of this project.

### Django + Django REST Framework
- **Pros:** Batteries-included admin, mature ORM, built-in auth.
- **Cons:** Sync-first architecture complicates async AI calls. Template engine less flexible than SvelteKit for interactive editing. Heavier footprint.
- **Verdict:** Rejected — FastAPI's async-native approach better fits the AI integration pattern.

### MongoDB (Document Database)
- **Pros:** Flexible schema for varied section content, easy horizontal scaling.
- **Cons:** Weaker referential integrity, no JOINs for editorial relationships, eventual consistency challenges for multi-section bulletins. Requires manual application-level constraints.
- **Verdict:** Rejected — relational model better matches the domain's entity relationships.

## Consequences

**Positive:**
- Type safety end-to-end: SQLModel models serve as both API schemas and ORM mappings, reducing duplication
- FastAPI's async handling natively supports long-running AI API calls without blocking
- SvelteKit's SSR provides fast initial loads for the editorial dashboard
- PostgreSQL's JSONB column in `secciones.contenido` allows flexible section-specific content without schema changes

**Negative:**
- SvelteKit has a smaller ecosystem than React; fewer third-party component libraries available
- SQLModel is relatively young; edge cases may require falling back to raw SQLAlchemy
- Team requires learning curve for SvelteKit reactivity model if coming from React
- PostgreSQL requires managed service (RDS) or manual setup for production

**Mitigations:**
- SvelteKit's component ecosystem is growing; Shadcn-Svelte ports are available
- SQLModel allows raw SQLAlchemy escape hatches when needed
- Learning investment is front-loaded during MVP phase with minimal ongoing cost

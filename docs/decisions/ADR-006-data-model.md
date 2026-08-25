# ADR-006: Data Modeling Approach

**Date:** 2026-08-25
**Status:** Accepted
**Deciders:** Alberto Borella

---

## Context

NIA has a complex domain with multiple interconnected entities: bulletins, sections, contributor notes, incidents, prompts, sponsors, users, and audit logs. The data model must:

- Enforce relational integrity across editorial entities (e.g., sections belong to bulletins, incidents are assigned to bulletins)
- Support flexible content per section type (editorial text, incident article markdown, note references)
- Track all mutations via audit logging
- Enable efficient queries for common operations (list bulletins by status, search incidents by country/date, filter notes by topic)

## Decision

**SQLModel with PostgreSQL, explicit foreign keys, audit logging table, JSONB for flexible content**

| Aspect | Design |
|--------|--------|
| ORM | SQLModel (Pydantic + SQLAlchemy unified models) |
| Database | PostgreSQL 16+ with JSONB support |
| Primary keys | UUID v4 (`gen_random_uuid()`) on all tables |
| Foreign keys | Explicit `REFERENCES` with `ON DELETE CASCADE` where appropriate |
| Flexible content | JSONB column on `secciones.contenido` for type-specific content |
| Audit trail | Dedicated `log_auditoria` table for all mutations |
| Migrations | Alembic with auto-generate from SQLModel changes |
| Indexes | Composite indexes on high-frequency query patterns |

### Core Tables

```
usuarios          → User accounts with bcrypt passwords and RBAC roles
boletines         → Bulletin editions with lifecycle states
secciones         → Bulletin sections (6 types) with JSONB content
notas_colaboradores → Contributor notes with file references
incidentes        → Structured incident data (AI-generated, human-curated)
prompts           → AI prompt templates with configuration
auspiciantes      → Sponsor entities
boletin_auspiciantes → Many-to-many pivot (bulletin ↔ sponsor)
log_auditoria     → Audit trail for all mutations
```

### JSONB Content Patterns

Each section type stores type-specific content in `secciones.contenido`:

| Section Type | JSONB Structure |
|-------------|----------------|
| `editorial` | `{ "texto": "markdown content" }` |
| `incidentes` | `{ "articulo_markdown": "...", "version": 1 }` |
| `notas_colaboradores` | `{ "notas_ids": ["uuid1", "uuid2"] }` |
| `tabla_incidentes` | `{ "incidentes_ids": [...], "orden_seleccion": [...] }` |
| `auspiciantes` | `{ "auspiciantes_ids": ["uuid1"] }` |
| `indice` | `{ "generado_automaticamente": true, "items": [...] }` |

### Indexing Strategy

```sql
-- High-frequency queries
idx_incidentes_pais_fecha       → incident filtering by country + date range
idx_incidentes_boletin_estado   → bulletin incident lookup
idx_notas_estado_colaborador    → collaborator note filtering
idx_secciones_boletin_orden     → section ordering within bulletins
idx_log_auditoria_fecha         → audit log date range queries
```

## Alternatives Considered

### NoSQL (MongoDB / Document Database)
- **Pros:** Schema flexibility, natural fit for varied section content, horizontal scaling.
- **Cons:** No referential integrity at database level, manual application-level constraints for relationships, no JOINs, eventual consistency challenges for multi-entity bulletin compilation.
- **Verdict:** Rejected — relational model better enforces the complex entity relationships in the editorial domain.

### ORM-only Approach (No Explicit SQL Constraints)
- **Pros:** Simpler model definitions, faster initial development.
- **Cons:** Relies entirely on application code for data integrity, no database-level protection against orphaned records, harder to audit direct database changes.
- **Verdict:** Rejected — database-level constraints provide defense-in-depth for data integrity.

### Schema-less JSONB for Everything
- **Pros:** Maximum flexibility, no migrations needed.
- **Cons:** No type safety, no referential integrity, difficult to query and index, no clear entity boundaries, makes auditing nearly impossible.
- **Verdict:** Rejected — over-flexibility leads to data quality issues in a structured editorial workflow.

## Consequences

**Positive:**
- SQLModel unifies Pydantic schemas and SQLAlchemy models: one class serves as API request/response schema AND database model
- Explicit foreign keys prevent orphaned records (e.g., deleting a bulletin cascades to its sections)
- JSONB `contenido` column on `secciones` allows adding new section types without schema migrations
- UUID primary keys enable safe URL exposure and prevent sequential ID guessing
- Composite indexes optimize the most common query patterns (incidents by country+date, notes by status+collaborator)
- Audit log table provides full traceability for compliance and debugging

**Negative:**
- Alembic migrations required for every schema change (adds workflow step)
- SQLModel is younger than SQLAlchemy alone; some advanced ORM features may require raw SQLAlchemy escape hatches
- JSONB content is not type-checked at the database level (application responsibility)
- PostgreSQL-specific features (JSONB, gen_random_uuid) create vendor lock-in

**Mitigations:**
- Alembic auto-generate (`alembic revision --autogenerate`) minimizes migration authoring effort
- SQLModel allows dropping to raw SQLAlchemy for edge cases without losing Pydantic integration
- Pydantic validation on JSONB content in API schemas provides type safety at the application layer
- PostgreSQL is the intended long-term database; vendor lock-in is acceptable

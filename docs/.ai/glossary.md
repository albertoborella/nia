# Glossary — NIA

Supplement to the global SDD glossary (`docs/GLOSSARY.md`). Terms specific to this project.

## Newsletter Terms

| Term | Definition |
|------|-----------|
| **Boletín** | A complete edition of the newsletter "Noticias sobre Inocuidad Alimentaria" |
| **Sección** | One of the 6 parts of a newsletter, completed in strict order |
| **Período** | The date range a newsletter covers (`periodo_inicio` to `periodo_fin`) |
| **Compilación** | Process of assembling all sections into the final newsletter document |
| **Cierre** | Marking a newsletter as final; closed newsletters cannot be edited |

## Food Safety Terms

| Term | Definition |
|------|-----------|
| **Inocuidad alimentaria** | Food safety — absence of hazards that could cause illness or injury |
| **Incidente** | A confirmed food safety event: outbreak, contamination, recall, or alert |
| **Patógeno** | Causative agent: bacteria (Salmonella, E. coli), virus, parasite, or chemical |
| **Severidad** | Impact level: `crítico` (deaths), `alto` (hospitalizations), `medio` (illnesses), `bajo` (low impact) |
| **Riesgo** | Threat level: `alto`, `medio`, `bajo` — assessed by editor based on scope and impact |
| **Retiro** | Product recall — removal of contaminated products from market |
| **Alerta** | Official warning from a food safety authority (FDA, ANMAT, EFSA, etc.) |
| **Brote** | Outbreak — multiple related cases of foodborne illness |

## AI Pipeline Terms

| Term | Definition |
|------|-----------|
| **Prompt predefinido** | Stored prompt template in DB with variables; never hardcoded in frontend |
| **Consulta de incidentes** | AI call to collect structured incident data for a time period |
| **Generación de artículo** | AI call to produce a Markdown draft from reviewed incident data |
| **Revisión humana** | Editor's review, correction, and approval of AI-generated content |
| **Trazabilidad** | Every published fact must trace back to a verifiable source |

## Role Terms

| Term | Definition |
|------|-----------|
| **Director** | Full access: create newsletters, write editorials, query AI, review notes, compile |
| **Colaborador** | Limited: upload notes, view own notes. Cannot create newsletters or query AI |

## Entity States

| Entity | States |
|--------|--------|
| Boletín | `borrador` → `en_progreso` → `completado` → `cerrado` |
| Sección | `pendiente` → `en_edicion` → `completada` |
| Nota | `pendiente` → `aprobada` / `archivada` |
| Incidente | `confirmado` / `en_investigacion` / `descartado` |

## Technical Abbreviations

| Term | Meaning |
|------|---------|
| **JSONB** | PostgreSQL binary JSON column — stores structured data with indexing |
| **httpOnly cookie** | Cookie inaccessible to JavaScript (XSS protection) |
| **Alembic** | Python migration tool for SQLAlchemy/SQLModel |
| **Podman** | Daemonless, rootless container runtime (Docker-compatible) |
| **AWS ECR Public** | Public container image registry (no auth needed for pulls) |

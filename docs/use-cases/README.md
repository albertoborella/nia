# Use Cases — NIA

Define las interacciones entre los actores y el sistema para lograr un
objetivo concreto.

---

## Casos de Uso

| Archivo | Caso de Uso | Actor Principal | Descripción |
| ------- | ----------- | --------------- | ----------- |
| `authentication.md` | UC-01: Autenticación y Autorización | Director, Collaborator | Login, JWT, cookies httpOnly, refresh, logout |
| `bulletin-management.md` | UC-02: Gestión de Boletines | Director | Crear, editar, cerrar, compilar boletines |
| `editorial-section.md` | UC-03: Sección Editorial | Director | Escribir y guardar contenido editorial |
| `global-incidents-article.md` | UC-04: Artículo de Incidentes | Director | Generación asistida por IA de artículos |
| `contributor-notes.md` | UC-05: Notas de Colaboradores | Director, Collaborator | Subir, revisar, aprobar notas PDF/DOCX |
| `incident-management.md` | UC-06: Gestión de Incidentes | Director, Collaborator | Crear, editar, importar incidentes |
| `world-incidents-table.md` | UC-07: Tabla de Incidentes | Director | Seleccionar y ordenar tabla destacada |
| `sponsors-management.md` | UC-08: Gestión de Auspiciantes | Director | Crear, asignar auspiciantes a boletines |
| `user-management.md` | UC-09: Gestión de Usuarios | Director | Crear, editar, desactivar usuarios |
| `prompt-management.md` | UC-10: Gestión de Prompts IA | Director | Crear, probar, versionar prompts |

---

## Convenciones

- Cada archivo sigue el formato: Actor, Precondición, Flujo Principal (numerado), Flujos Alternativos, Postcondición.
- Los flujos referencian endpoints de la API (`/api/v1/...`).
- Los campos y enums coinciden con las entidades definidas en `docs/domain/entities.md`.

---

## Consejos

- Un caso de uso debe ser accionable: el lector entiende qué hace el sistema.
- Los casos de uso alimentan los casos de prueba de `docs/testing/`.


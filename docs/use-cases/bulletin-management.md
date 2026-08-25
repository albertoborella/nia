# UC-02: Gestión de Boletines

## Descripción
El director crea, edita y administra boletines del bulletin "Noticias sobre Inocuidad Alimentaria". Cada boletín tiene secciones que se completan en orden cronológico.

## Actor
- **Director**: Crear, editar, cerrar y compilar boletines.

## Precondición
- El usuario está autenticado como Director.

---

## Flujo Principal: Crear Nuevo Boletín

1. El director navega a `/boletines/nueva`.
2. El sistema muestra el formulario de creación con campos:
   - `nombre` (string, requerido): Ej: "Edición Marzo 2026"
   - `periodo_inicio` (date, requerido): Fecha de inicio del período de cobertura.
   - `periodo_fin` (date, requerido): Fecha de fin del período de cobertura.
   - `fecha_publicacion_estimada` (date, opcional): Fecha estimada de publicación.
3. El director completa el formulario y envía.
4. El frontend envía `POST /api/v1/boletines` con los datos.
5. El backend crea el boletín con estado `borrador` y genera 6 secciones en orden:
   | Orden | Tipo | Estado Inicial |
   |-------|------|----------------|
   | 1 | `editorial` | `pendiente` |
   | 2 | `incidentes` | `pendiente` |
   | 3 | `notas_colaboradores` | `pendiente` |
   | 4 | `tabla_incidentes` | `pendiente` |
   | 5 | `auspiciantes` | `pendiente` |
   | 6 | `indice` | `pendiente` |
6. El backend retorna `201` con el boletín y sus secciones.
7. El frontend redirige a `/boletines/{id}/editorial` (primera sección).

---

## Flujo Principal: Listar Boletines

1. El director navega a `/boletines`.
2. El frontend envía `GET /api/v1/boletines?page=1&limit=20`.
3. El backend retorna la lista paginada con: `id`, `nombre`, `periodo_inicio`, `periodo_fin`, `estado`, `secciones_completadas`, `secciones_total`, `fecha_creacion`.
4. El frontend muestra una tabla con el progreso de cada boletín.

---

## Flujo Principal: Ver Detalle de Boletín

1. El director selecciona un boletín de la lista.
2. El frontend envía `GET /api/v1/boletines/{id}`.
3. El backend retorna el boletín con todas sus secciones y su estado.
4. El frontend muestra el dashboard del boletín con las secciones y su progreso.

---

## Flujos Alternativos

### FA-01: Editar Boletín (solo en estado `borrador`)
1. El director selecciona un boletín en estado `borrador`.
2. El frontend envía `PUT /api/v1/boletines/{id}` con los campos actualizados.
3. El backend actualiza solo si `estado == "borrador"`.
4. Si el boletín no está en borrador, retorna `409` con `{ "detail": { "code": "INVALID_STATE", "message": "Solo se pueden editar boletines en borrador" } }`.

### FA-02: Marcar Sección como Completada
1. El director completa el contenido de una sección.
2. El frontend envía `POST /api/v1/boletines/{id}/completar-seccion` con `{ "tipo": "editorial" }`.
3. El backend marca la sección como `completada` y actualiza `completado_por` y `fecha_completado`.
4. El backend actualiza el estado del boletín a `en_progreso` si era `borrador`.

### FA-03: Cerrar Boletín
1. El director verifica que todas las secciones estén completadas.
2. El frontend envía `POST /api/v1/boletines/{id}/cerrar`.
3. El backend valida que `secciones_completadas == secciones_total`.
4. Si no todas están completadas, retorna `409`.
5. Si todas están completadas: cambia estado a `cerrado`, establece `fecha_cierre`, y marca el boletín como inmutable.

### FA-04: Compilar Boletín
1. El director solicita compilar el boletín cerrado.
2. El frontend envía `POST /api/v1/boletines/{id}/compilar`.
3. El backend consolida todas las secciones en el documento final.
4. El backend retorna `200` con `boletin_compilado` en formato markdown.

### FA-05: Exportar Boletín
1. El director solicita exportar el boletín compilado.
2. El frontend envía `GET /api/v1/boletines/{id}/exportar?formato=pdf`.
3. El backend retorna el archivo en el formato solicitado.

---

## Postcondición
- Boletín creado con estado `borrador` y 6 secciones generadas.
- Boletín cerrado es inmutable.
- Boletín compilado está listo para distribución.

---

## Estados del Boletín
```
borrador → en_progreso → completado → cerrado
```

---

## Endpoints Relacionados
- `GET /api/v1/boletines`
- `POST /api/v1/boletines`
- `GET /api/v1/boletines/{id}`
- `PUT /api/v1/boletines/{id}`
- `POST /api/v1/boletines/{id}/completar-seccion`
- `POST /api/v1/boletines/{id}/cerrar`
- `POST /api/v1/boletines/{id}/compilar`
- `GET /api/v1/boletines/{id}/exportar`

> See [01-api-design.md](../architecture/01-api-design.md#boletines) for full request/response schemas.

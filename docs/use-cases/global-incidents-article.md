# UC-04: Artículo de Incidentes Mundiales (Asistido por IA)

## Descripción
El director genera un artículo sobre incidentes de inocuidad alimentaria utilizando IA. El proceso incluye: consultar incidentes por período, generar datos estructurados, y generar un artículo en markdown.

## Actor
- **Director**: Ejecutar consultas IA, editar resultados, generar artículos.

## Precondición
- El usuario está autenticado como Director.
- Prompts predefinidos existen en la base de datos (tipo `consulta_incidentes` y `redaccion_articulo`).

---

## Flujo Principal: Generar Artículo Completo

### Fase 1: Consulta de Incidentes
1. El director accede a `/boletines/{id}/incidentes`.
2. El frontend muestra un formulario para seleccionar el período:
   - `periodo_inicio` (date, requerido)
   - `periodo_fin` (date, requerido)
3. El director selecciona las fechas y hace clic en "Consultar incidentes".
4. El frontend envía `POST /api/v1/incidentes/consultar` con:
   ```json
   {
     "periodo_inicio": "2026-03-01",
     "periodo_fin": "2026-03-31"
   }
   ```
5. El backend:
   - Recupera el prompt predefinido de tipo `consulta_incidentes`.
   - Reemplaza las variables `{{periodo_inicio}}` y `{{periodo_fin}}`.
   - Envía el prompt a la API de IA.
   - Recibe un JSON con array de incidentes.
   - Almacena cada incidente en la tabla `incidente`.
6. El backend retorna `200` con:
   ```json
   {
     "incidentes": [...],
     "prompt_utilizado": "uuid",
     "tokens_consumidos": 1500
   }
   ```
7. El frontend muestra una tabla editable con los incidentes generados.

### Fase 2: Revisión y Edición de Incidentes
1. El director revisa cada registro en la tabla.
2. El director puede:
   - **Editar**: Modificar campos de un incidente existente.
   - **Eliminar**: Marcar un incidente como descartado.
   - **Agregar**: Añadir un incidente manualmente.
3. Los cambios se envían vía `PUT /api/v1/incidentes/{id}` o `DELETE /api/v1/incidentes/{id}`.

### Fase 3: Generación del Artículo
1. El director selecciona los incidentes que desea incluir en el artículo.
2. El frontend envía `POST /api/v1/incidentes/{boletin_id}/generar-articulo`.
3. El backend:
   - Recupera el prompt predefinido de tipo `redaccion_articulo`.
   - Alimenta el prompt con los datos de los incidentes seleccionados.
   - Envía a la API de IA.
   - Recibe un artículo en formato markdown.
   - Almacena el artículo en `seccion.contenido.articulo_markdown`.
4. El backend retorna `200` con:
   ```json
   {
     "articulo_markdown": "# Incidentes de inocuidad...\n\n...",
     "version": 1,
     "incidentes_incluidos": 5
   }
   ```
5. El frontend muestra el artículo en un editor markdown.

### Fase 4: Edición del Artículo
1. El director edita libremente el texto generado por la IA.
2. El director guarda la versión editada.
3. El frontend envía `PUT /api/v1/incidentes/{boletin_id}/articulo` con:
   ```json
   {
     "articulo_markdown": "# Incidentes de inocuidad...\n\n(versión editada)",
     "version": 2
   }
   ```
4. El backend almacena la nueva versión.

---

## Flujos Alternativos

### FA-01: Regenerar con diferentes parámetros
1. El director no está satisfecho con los resultados.
2. El director solicita regenerar la consulta o el artículo.
3. El sistema repite la fase correspondiente con los mismos o diferentes parámetros.

### FA-02: Escritura manual del artículo
1. El director opta por no usar IA.
2. El director escribe directamente el artículo en el editor markdown.
3. El frontend envía `PUT /api/v1/boletines/{id}/secciones/incidentes` con el contenido manual.

### FA-03: Editar prompt antes de usar
1. El director quiere modificar el prompt predefinido antes de ejecutar.
2. El director accede a la gestión de prompts (UC-10).
3. El director modifica el prompt y guarda los cambios.
4. El director regresa al pipeline de incidentes y ejecuta con el prompt actualizado.

### FA-04: Error en servicio de IA
1. El backend recibe error de la API de IA.
2. El backend retorna `503` con `{ "detail": { "code": "IA_SERVICE_UNAVAILABLE", "message": "Servicio de IA no disponible" } }`.
3. El frontend muestra el error y sugiere reintentar.

---

## Postcondición
- Incidentes almacenados en la base de datos.
- Artículo generado en markdown y almacenado en la sección `incidentes`.
- Sección lista para marcar como completada.

---

## Endpoints Relacionados
- `POST /api/v1/incidentes/consultar`
- `GET /api/v1/incidentes`
- `PUT /api/v1/incidentes/{id}`
- `DELETE /api/v1/incidentes/{id}`
- `POST /api/v1/incidentes/{boletin_id}/generar-articulo`
- `GET /api/v1/incidentes/{boletin_id}/articulo`
- `PUT /api/v1/incidentes/{boletin_id}/articulo`

> See [01-api-design.md](../architecture/01-api-design.md#incidentes) for full request/response schemas.

# UC-05: Gestión de Notas de Colaboradores

## Descripción
Director y colaboradores suben, revisan y administran notas (artículos) en formato PDF o DOCX. Las notas se pueden asignar a boletines específicos o archivar para uso futuro.

## Actor
- **Director**: Subir notas, revisar, aprobar, archivar, asignar a boletines.
- **Colaborador**: Subir notas, ver estado de sus propias notas.

## Precondición
- El usuario está autenticado.
- El colaborador tiene notas propias para gestionar.

---

## Flujo Principal: Subir Nota

1. El usuario accede a `/notas/nueva`.
2. El sistema muestra el formulario de carga con campos:
   - `titulo` (string, requerido): Título del artículo.
   - `autor` (string, requerido): Nombre del autor.
   - `fuente` (string, opcional): Revista, organismo o medio de origen.
   - `tema` (string, opcional): Categoría (ej: "bacterias", "regulación", "alertas").
   - `archivo` (file, requerido): Archivo .pdf o .docx, máximo 10 MB.
3. El usuario completa el formulario y selecciona el archivo.
4. El frontend envía `POST /api/v1/notas` como `multipart/form-data`.
5. El backend:
   - Valida tipo MIME y extensión del archivo.
   - Valida tamaño (máximo 10 MB).
   - Genera nombre de archivo con UUID para evitar path traversal.
   - Almacena el archivo fuera del directorio público.
   - Crea el registro de nota con estado `pendiente`.
   - Registra en log de auditoría.
6. El backend retorna `201` con los datos de la nota.

---

## Flujo Principal: Revisar Nota (Director)

1. El director accede a `/notas`.
2. El frontend envía `GET /api/v1/notas?estado=pendiente&page=1&limit=20`.
3. El backend retorna la lista paginada de notas pendientes.
4. El director selecciona una nota para revisar.
5. El frontend muestra los detalles de la nota: título, autor, fuente, tema, fecha de recepción.
6. El director descarga el archivo para revisión.
7. El frontend envía `GET /api/v1/notas/{id}/descarga`.
8. El backend retorna el archivo binario (.pdf o .docx).

---

## Flujo Principal: Aprobar Nota y Asignar a Boletín

1. El director revisa la nota y decide aprobarla.
2. El director selecciona el boletín donde se incluirá.
3. El frontend envía `PUT /api/v1/notas/{id}/estado` con:
   ```json
   {
     "estado": "aprobada",
     "boletin_asignado": "uuid-del-boletin",
     "observaciones": "Artículo relevante para la edición actual"
   }
   ```
4. El backend:
   - Actualiza el estado de la nota a `aprobada`.
   - Asigna la nota al boletín especificado.
   - Registra `fecha_revision` y `revisado_por`.
   - Registra en log de auditoría.
5. El backend retorna `200` con la nota actualizada.

---

## Flujos Alternativos

### FA-01: Archivar Nota
1. El director revisa la nota y decide archivarla.
2. El frontend envía `PUT /api/v1/notas/{id}/estado` con:
   ```json
   {
     "estado": "archivada",
     "boletin_asignado": null,
     "observaciones": "No aplica para esta edición"
   }
   ```
3. El backend marca la nota como `archivada`.
4. La nota permanece disponible para publicaciones futuras.

### FA-02: Editar Metadatos de Nota
1. El usuario selecciona una nota para editar sus metadatos.
2. El frontend envía `PUT /api/v1/notas/{id}` con los campos actualizados (título, autor, fuente, tema).
3. El backend actualiza los metadatos sin modificar el archivo.

### FA-03: Eliminar Nota
1. El director selecciona una nota para eliminar.
2. El frontend muestra confirmación: "¿Estás seguro? Esta acción no se puede deshacer."
3. Si confirma, el frontend envía `DELETE /api/v1/notas/{id}`.
4. El backend elimina el registro y el archivo asociado.

### FA-04: Buscar Notas
1. El usuario accede a `/notas` con filtros de búsqueda.
2. El frontend envía `GET /api/v1/notas?tema=bacterias&autor=Juan&estado=pendiente`.
3. El backend retorna las notas que coinciden con los filtros.

### FA-05: Colaborador ve sus Notas
1. El colaborador accede a `/notas`.
2. El frontend envía `GET /api/v1/notas` (el backend filtra por `colaborador_id` del usuario autenticado).
3. El colaborador solo ve sus propias notas y su estado.

---

## Postcondición
- Nota almacenada en el sistema con metadatos y archivo.
- Nota aprobada asignada al boletín especificado.
- Nota archivada disponible para uso futuro.

---

## Restricciones
- Solo el director puede aprobar, archivar o eliminar notas.
- El colaborador solo puede subir notas y ver las suyas.
- Archivos máximos de 10 MB.
- Tipos permitidos: .pdf, .docx.

---

## Endpoints Relacionados
- `GET /api/v1/notas`
- `POST /api/v1/notas`
- `GET /api/v1/notas/{id}`
- `PUT /api/v1/notas/{id}`
- `PUT /api/v1/notas/{id}/estado`
- `GET /api/v1/notas/{id}/descarga`

> See [01-api-design.md](../architecture/01-api-design.md#notas-de-colaboradores) for full request/response schemas.

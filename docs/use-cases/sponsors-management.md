# UC-08: Gestión de Auspiciantes

## Descripción
El director administra los auspiciantes (patrocinadores) que aparecen en los boletines. Los auspiciantes se pueden crear, editar y asignar a boletines específicos.

## Actor
- **Director**: Crear, editar, eliminar auspiciantes; asignar a boletines.

## Precondición
- El usuario está autenticado como Director.

---

## Flujo Principal: Crear Auspiciante

1. El director accede a `/admin/auspiciantes/nuevo`.
2. El sistema muestra el formulario con campos:
   - `nombre` (string, requerido): Nombre del auspiciante.
   - `logo` (file, requerido): Archivo de imagen del logo.
   - `enlace` (string, opcional): URL del auspiciante.
   - `descripcion` (string, opcional): Descripción breve.
3. El director completa el formulario y selecciona el archivo de logo.
4. El frontend envía `POST /api/v1/auspiciantes` como `multipart/form-data`.
5. El backend:
   - Valida tipo MIME y extensión del archivo de logo.
   - Almacena el logo fuera del directorio público.
   - Crea el registro de auspiciante con `activo=true`.
6. El backend retorna `201` con los datos del auspiciante.

---

## Flujo Principal: Asignar Auspiciantes a Boletín

1. El director accede a `/boletines/{id}/auspiciantes`.
2. El frontend envía `GET /api/v1/auspiciantes?activo=true`.
3. El backend retorna la lista de auspiciantes activos.
4. El frontend muestra una lista de selección con los auspiciantes disponibles.
5. El director selecciona los auspiciantes para el boletín.
6. El frontend envía `PUT /api/v1/boletines/{id}/auspiciantes` con:
   ```json
   {
     "auspiciantes_ids": ["uuid1", "uuid2"]
   }
   ```
7. El backend actualiza la sección `auspiciantes` del boletín.
8. El backend retorna `200` con los auspiciantes asignados.

---

## Flujo Principal: Listar Auspiciantes

1. El director accede a `/admin/auspiciantes`.
2. El frontend envía `GET /api/v1/auspiciantes`.
3. El backend retorna la lista de auspiciantes activos.

---

## Flujos Alternativos

### FA-01: Editar Auspiciante
1. El director selecciona un auspiciante de la lista.
2. El frontend muestra los campos editables.
3. El director modifica nombre, enlace, descripción o logo.
4. El frontend envía `PUT /api/v1/auspiciantes/{id}` con los campos actualizados.
5. El backend actualiza el registro.

### FA-02: Eliminar Auspiciante (Soft Delete)
1. El director selecciona un auspiciante para eliminar.
2. El frontend muestra confirmación: "¿Estás seguro? El auspiciante no aparecerá en nuevos boletines."
3. Si confirma, el frontend envía `DELETE /api/v1/auspiciantes/{id}`.
4. El backend marca `activo=false` (soft delete).
5. El auspiciante permanece en boletines anteriores donde fue asignado.

### FA-03: Ver Historial de Auspiciantes
1. El director accede a `/admin/auspiciantes/historial`.
2. El frontend envía `GET /api/v1/auspiciantes?include_inactive=true`.
3. El backend retorna todos los auspiciantes, incluyendo los inactivos.

### FA-04: Cambiar Logo de Auspiciante
1. El director selecciona un auspiciante.
2. El director sube un nuevo archivo de logo.
3. El frontend envía `PUT /api/v1/auspiciantes/{id}` con el nuevo logo.
4. El backend reemplaza el archivo anterior.

---

## Postcondición
- Auspiciante creado con logo y metadatos.
- Auspiciante asignado al boletín especificado.
- Auspiciante eliminado (soft delete) no aparece en nuevos boletines.

---

## Restricciones
- Solo el director puede crear, editar o eliminar auspiciantes.
- Los auspiciantes eliminados permanecen en boletines anteriores.
- El logo debe ser una imagen válida (PNG, JPG, SVG).

---

## Endpoints Relacionados
- `GET /api/v1/auspiciantes`
- `POST /api/v1/auspiciantes`
- `PUT /api/v1/auspiciantes/{id}`
- `DELETE /api/v1/auspiciantes/{id}`
- `GET /api/v1/boletines/{id}/auspiciantes`
- `PUT /api/v1/boletines/{id}/auspiciantes`

> See [01-api-design.md](../architecture/01-api-design.md#auspiciantes) for full request/response schemas.

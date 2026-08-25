# UC-10: Gestión de Prompts de IA

## Descripción
El director administra los prompts predefinidos que se utilizan para consultas a la IA. Los prompts se pueden crear, editar, probar y versionar.

## Actor
- **Director**: Crear, editar, eliminar, probar prompts.

## Precondición
- El usuario está autenticado como Director.

---

## Flujo Principal: Crear Nuevo Prompt

1. El director accede a `/admin/prompts/nuevo`.
2. El sistema muestra el formulario con campos:
   - `nombre` (string, requerido): Nombre descriptivo del prompt.
   - `descripcion` (string, requerido): Qué hace y cuándo usarlo.
   - `template` (text, requerido): Texto del prompt con variables (ej: `{{periodo_inicio}}`, `{{periodo_fin}}`).
   - `tipo` (enum, requerido): `consulta_incidentes`, `redaccion_articulo`, `otro`.
   - `configuracion` (jsonb, opcional): Parámetros: modelo, temperatura, max_tokens, etc.
3. El director completa el formulario y envía.
4. El frontend envía `POST /api/v1/prompts` con:
   ```json
   {
     "nombre": "Consulta Incidentes Mensual",
     "descripcion": "Busca incidentes de inocuidad en un período dado",
     "template": "Busca incidentes de inocuidad alimentaria desde {{periodo_inicio}} hasta {{periodo_fin}}. Retorna JSON estructurado.",
     "tipo": "consulta_incidentes",
     "configuracion": {
       "modelo": "gpt-4",
       "temperatura": 0.3,
       "max_tokens": 2000
     }
   }
   ```
5. El backend:
   - Crea el prompt con `activo=true`.
   - Registra en log de auditoría.
6. El backend retorna `201` con los datos del prompt.

---

## Flujo Principal: Listar Prompts

1. El director accede a `/admin/prompts`.
2. El frontend envía `GET /api/v1/prompts`.
3. El backend retorna la lista de prompts activos.

---

## Flujo Principal: Probar Prompt

1. El director selecciona un prompt para probar.
2. El frontend muestra el prompt con campos para ingresar valores de prueba.
3. El director ingresa valores de ejemplo:
   - `periodo_inicio`: "2026-03-01"
   - `periodo_fin`: "2026-03-31"
4. El frontend envía `POST /api/v1/prompts/{id}/test` con los valores de prueba.
5. El backend:
   - Reemplaza las variables en el template.
   - Envía el prompt a la API de IA.
   - Retorna la respuesta de la IA.
6. El frontend muestra la respuesta para revisión.

---

## Flujos Alternativos

### FA-01: Editar Prompt
1. El director selecciona un prompt de la lista.
2. El frontend muestra los campos editables.
3. El director modifica el template, configuración o metadatos.
4. El frontend envía `PUT /api/v1/prompts/{id}` con los campos actualizados.
5. El backend actualiza el prompt.

### FA-02: Desactivar Prompt
1. El director selecciona un prompt para desactivar.
2. El frontend muestra confirmación: "¿Estás seguro? El prompt no estará disponible para uso."
3. Si confirma, el frontend envía `PUT /api/v1/prompts/{id}` con `{ "activo": false }`.
4. El backend marca `activo=false`.

### FA-03: Eliminar Prompt
1. El director selecciona un prompt para eliminar.
2. El frontend muestra confirmación: "¿Estás seguro? Esta acción no se puede deshacer."
3. Si confirma, el frontend envía `DELETE /api/v1/prompts/{id}`.
4. El backend elimina el registro.

### FA-04: Ver Historial de Prompts
1. El director accede a `/admin/prompts/historial`.
2. El frontend envía `GET /api/v1/prompts?include_inactive=true`.
3. El backend retorna todos los prompts, incluyendo los inactivos.

### FA-05: Duplicar Prompt
1. El director selecciona un prompt existente.
2. El director hace clic en "Duplicar".
3. El frontend envía `POST /api/v1/prompts` con los datos del prompt original pero con un nuevo nombre.
4. El backend crea un nuevo prompt basado en el original.

---

## Postcondición
- Prompt creado con template y configuración.
- Prompt probado y verificado.
- Prompt desactivado o eliminado según la acción.

---

## Restricciones
- Solo el director puede crear, editar o eliminar prompts.
- Los prompts se almacenan en la base de datos, no en el frontend.
- Nunca concatenar input del usuario directamente en el prompt de IA.

---

## Variables Soportadas en Templates
- `{{periodo_inicio}}`: Fecha de inicio del período.
- `{{periodo_fin}}`: Fecha de fin del período.
- `{{incidentes}}`: Array de incidentes para redacción.
- `{{boletin_nombre}}`: Nombre del boletín.

---

## Endpoints Relacionados
- `GET /api/v1/prompts`
- `POST /api/v1/prompts`
- `GET /api/v1/prompts/{id}`
- `PUT /api/v1/prompts/{id}`
- `DELETE /api/v1/prompts/{id}`
- `POST /api/v1/prompts/{id}/test`

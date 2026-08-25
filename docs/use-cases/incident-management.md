# UC-06: Gestión de Incidentes

## Descripción
Director y colaboradores administran incidentes de inocuidad alimentaria. Los incidentes pueden ser generados por IA, importados manualmente o editados después de la generación.

## Actor
- **Director**: Crear, editar, eliminar incidentes; importar desde fuentes externas.
- **Colaborador**: Ver incidentes asignados (solo lectura).

## Precondición
- El usuario está autenticado.
- Existen datos de incidentes en la base de datos (generados por IA o importados).

---

## Flujo Principal: Agregar Incidente Manualmente

1. El director accede a `/incidentes/nuevo`.
2. El sistema muestra el formulario con campos:
   - `incidente` (string, requerido): Nombre o descripción breve.
   - `producto` (string, requerido): Producto alimentario afectado.
   - `patogeno` (string, requerido): Agente causal (bacteria, virus, parásito, químico).
   - `organismo` (string, requerido): Organismo o empresa involucrada.
   - `pais` (string, requerido): País donde ocurrió.
   - `riesgo` (enum, requerido): `alto`, `medio`, `bajo`.
   - `fecha_inicio` (date, requerido): Fecha de inicio del incidente.
   - `fecha_cierre` (date, opcional): Fecha de cierre (null si activo).
   - `observaciones` (text, opcional): Detalles adicionales.
   - `texto_noticia` (text, opcional): Texto original de la fuente.
   - `fuente_url` (string, opcional): URL de la fuente original.
   - `fuente_nombre` (string, opcional): Nombre del organismo o revista.
   - `severidad` (enum, requerido): `critico`, `alto`, `medio`, `bajo`.
   - `estado` (enum, requerido): `confirmado`, `en_investigacion`, `descartado`.
3. El director completa el formulario y envía.
4. El frontend envía `POST /api/v1/incidentes` con los datos.
5. El backend crea el registro y retorna `201`.

---

## Flujo Principal: Importar desde Fuente Externa

1. El director accede a `/incidentes/importar`.
2. El director selecciona el archivo o fuente de datos.
3. El frontend envía los datos para importación.
4. El backend procesa y almacena los incidentes.
5. El backend retorna el número de incidentes importados.

---

## Flujo Principal: Listar y Buscar Incidentes

1. El usuario accede a `/incidentes`.
2. El frontend envía `GET /api/v1/incidentes?page=1&limit=20` con filtros opcionales:
   - `pais`: Filtrar por país.
   - `riesgo`: Filtrar por nivel de riesgo.
   - `estado`: Filtrar por estado.
   - `periodo_inicio` / `periodo_fin`: Filtrar por rango de fechas.
3. El backend retorna la lista paginada de incidentes.

---

## Flujos Alternativos

### FA-01: Editar Incidente
1. El director selecciona un incidente de la lista.
2. El frontend muestra los campos editables.
3. El director modifica los campos necesarios.
4. El frontend envía `PUT /api/v1/incidentes/{id}` con los campos actualizados.
5. El backend actualiza el registro.

### FA-02: Eliminar Incidente
1. El director selecciona un incidente para eliminar.
2. El frontend muestra confirmación: "¿Estás seguro? Esta acción no se puede deshacer."
3. Si confirma, el frontend envía `DELETE /api/v1/incidentes/{id}`.
4. El backend elimina el registro.

### FA-03: Ver Historial de Incidente
1. El director selecciona un incidente.
2. El frontend envía `GET /api/v1/incidentes/{id}`.
3. El backend retorna el incidente completo con su historial de cambios.

### FA-04: Filtrar por Período
1. El director selecciona un rango de fechas.
2. El frontend envía `GET /api/v1/incidentes?periodo_inicio=2026-03-01&periodo_fin=2026-03-31`.
3. El backend retorna los incidentes dentro del rango especificado.

### FA-05: Colaborador ve Incidentes
1. El colaborador accede a `/incidentes`.
2. El frontend envía `GET /api/v1/incidentes` (el backend retorna solo incidentes visibles para colaboradores).
3. El colaborador tiene acceso de solo lectura.

---

## Postcondición
- Incidente almacenado en la base de datos.
- Incidente disponible para inclusión en tablas y artículos.
- Cambios registrados en log de auditoría.

---

## Estados del Incidente

El incidente tiene dos dimensiones de estado independientes:

### Estado de verificación (calidad de datos)
```
confirmado · en_investigacion · descartado
```

### Estado editorial (flujo de trabajo)
```
generado → revisado → aprobado → incluido
```

## Severidad
```
critico → alto → medio → bajo
```

---

## Endpoints Relacionados
- `GET /api/v1/incidentes`
- `POST /api/v1/incidentes`
- `GET /api/v1/incidentes/{id}`
- `PUT /api/v1/incidentes/{id}`
- `DELETE /api/v1/incidentes/{id}`
- `POST /api/v1/incidentes/consultar`

> See [01-api-design.md](../architecture/01-api-design.md#incidentes) for full request/response schemas.

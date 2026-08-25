# UC-07: Tabla de Incidentes Destacados

## Descripción
El director genera y administra la tabla de incidentes destacados que se incluye en el boletín. La tabla se genera automáticamente a partir de los incidentes almacenados, y el director puede seleccionar y ordenar los registros.

## Actor
- **Director**: Seleccionar incidentes, ordenar la tabla, exportar.

## Precondición
- El boletín existe y tiene incidentes almacenados en la base de datos.
- La sección `tabla_incidentes` está en estado `pendiente` o `en_edicion`.

---

## Flujo Principal: Generar Tabla

1. El director accede a `/boletines/{id}/tabla-incidentes`.
2. El frontend envía `GET /api/v1/incidentes?periodo_inicio={boletin.periodo_inicio}&periodo_fin={boletin.periodo_fin}`.
3. El backend retorna los incidentes del período del boletín.
4. El frontend muestra una tabla con los incidentes disponibles para seleccionar.

---

## Flujo Principal: Seleccionar y Ordenar Incidentes

1. El director selecciona los incidentes que desea incluir en la tabla.
2. El director ordena los incidentes seleccionados arrastrando y soltando.
3. El frontend envía `PUT /api/v1/boletines/{id}/tabla-incidentes` con:
   ```json
   {
     "incidentes_ids": ["uuid1", "uuid2", "uuid3"],
     "orden": ["uuid2", "uuid1", "uuid3"]
   }
   ```
4. El backend actualiza la sección `tabla_incidentes` con la selección y orden.
5. El backend retorna `200` con la tabla actualizada.

---

## Flujo Principal: Vista Previa de la Tabla

1. El director solicita vista previa de la tabla.
2. El frontend renderiza la tabla en formato markdown:
   ```markdown
   | País | Incidente | Producto | Patógeno | Riesgo | Fecha |
   |------|-----------|----------|----------|--------|-------|
   | Argentina | Brote de Salmonella | Leche entera | Salmonella enteritidis | Alto | 2026-03-05 |
   ```
3. El director revisa el formato y contenido.

---

## Flujos Alternativos

### FA-01: Agregar Incidente Manual a la Tabla
1. El director quiere incluir un incidente no generado por IA.
2. El director agrega el incidente manualmente (UC-06).
3. El director selecciona el nuevo incidente para la tabla.

### FA-02: Eliminar Incidente de la Tabla
1. El director deselecciona un incidente de la tabla.
2. El frontend actualiza la lista de `incidentes_ids`.
3. El frontend envía `PUT /api/v1/boletines/{id}/tabla-incidentes` sin el incidente eliminado.

### FA-03: Cambiar Orden de la Tabla
1. El director reordena los incidentes arrastrando y soltando.
2. El frontend actualiza el array `orden`.
3. El frontend envía `PUT /api/v1/boletines/{id}/tabla-incidentes` con el nuevo orden.

### FA-04: Exportar Tabla a Diferentes Formatos
1. El director solicita exportar la tabla.
2. El frontend envía `GET /api/v1/boletines/{id}/tabla-incidentes?formato=markdown`.
3. El backend retorna la tabla en el formato solicitado (markdown, HTML, CSV).

### FA-05: Personalizar Columnas de la Tabla
1. El director selecciona qué columnas mostrar en la tabla.
2. El frontend muestra opciones: País, Incidente, Producto, Patógeno, Riesgo, Fecha, Severidad.
3. El frontend guarda las preferencias de visualización.

---

## Postcondición
- Tabla de incidentes seleccionados y ordenados almacenada en la sección `tabla_incidentes`.
- Tabla lista para inclusión en el boletín compilado.
- Sección lista para marcar como completada.

---

## Contenido de la Sección `tabla_incidentes`
```json
{
  "incidentes_ids": ["uuid1", "uuid2", "uuid3"],
  "orden_seleccion": ["uuid2", "uuid1", "uuid3"]
}
```

---

## Endpoints Relacionados
- `GET /api/v1/boletines/{id}/tabla-incidentes`
- `PUT /api/v1/boletines/{id}/tabla-incidentes`
- `GET /api/v1/incidentes`

> See [01-api-design.md](../architecture/01-api-design.md#tabla-de-incidentes-destacados) for full request/response schemas.

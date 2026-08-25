# Reglas de Negocio — NIA

> See [functional-requirements.md](functional-requirements.md) for the complete functional requirements mapping.

## BN-01: Publicación cronológica por secciones

Cada boletín se arma en orden cronológico de secciones. El sistema debe guiar al editor paso a paso a través de cada sección hasta completar la publicación.

**Implemented by**: RF-01.2, RF-01.3

**Orden obligatorio:**
1. Editorial
2. Artículo de incidentes mundiales
3. Notas de colaboradores / Artículos de interés
4. Tabla de incidentes destacados
5. Auspiciantes
6. Índice (generado automáticamente)

Una sección debe estar marcada como "completada" antes de avanzar a la siguiente.

---

## BN-02: Editorial

- Solo el director de la editorial puede escribir la editorial.
- La editorial se escribe directamente en el sistema (área de texto dedicada).
- La editorial no requiere revisión de fuentes externas; es opinión del director.
- Una editorial aprobada no se puede editar sin crear una nueva versión.

**Implemented by**: RF-02.1, RF-02.2

---

## BN-03: Notas de colaboradores / Artículos de interés

- Todas las notas se tratan como **externas**: se接收 como archivos `.pdf` o `.docx`.
- Incluso si un miembro del equipo escribe un artículo, lo exporta a .pdf/.docx y lo sube a la plataforma.
- Las notas se almacenan en una carpeta/subcarpeta organizada por colaborador o tema.
- Una nota puede estar en tres estados:
  - **Pendiente de revisión**: recién subida, sin evaluar.
  - **Aprobada para publicación**: revisada, controlada, lista para incluir en un boletín.
  - **Archivada para futuro**: revisada pero no incluida en el boletín actual.
- Una nota aprobada se incluye en el próximo boletín; una archivada queda disponible para publicaciones futuras.
- Cada nota debe registrar: autor, fecha de recepción, fuente/revista/organismo, y estado.

**Implemented by**: RF-03.1, RF-03.2, RF-03.3, RF-03.4, RF-03.5, RF-03.6

---

## BN-04: Artículo de incidentes mundiales (sección core)

### Generación de datos

- El sistema debe ofrecer **prompts predefinidos** para consultar a la IA sobre incidentes de inocuidad alimentaria en un período determinado.
- La IA responde con un **JSON estructurado** con los campos del schema de incidentes.
- Los JSON se almacenan en una tabla de la base de datos para su reutilización.
- El editor puede **editar, corregir o eliminar** registros del JSON antes de continuar.

### Generación del artículo

- Con los datos de la tabla, el sistema alimenta un **prompt de redacción** que genera el artículo en formato markdown.
- El artículo generado se presenta al editor para **revisión y corrección**.
- El editor puede modificar libremente el texto generado por la IA.
- El artículo editado se transforma al **formato de publicación** (definido en fase de diseño).

**Implemented by**: RF-04A.1, RF-04A.2, RF-04A.3, RF-04A.4, RF-04B.1, RF-04B.2, RF-04B.3, RF-04B.4, RF-04B.5

### Campos del schema de incidentes

Campos iniciales (obligatorios):

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `incidente` | string | Nombre o descripción breve del incidente |
| `producto` | string | Producto alimentario afectado |
| `patogeno` | string | Agente causal (bacteria, virus, parásito, químico) |
| `organismo` | string | Organismo o empresa involucrada |
| `pais` | string | País donde ocurrió el incidente |
| `riesgo` | string | Nivel de riesgo (alto / medio / bajo) |
| `fecha_inicio` | date | Fecha de inicio del incidente |
| `fecha_cierre` | date | Fecha de cierre o actualización (si aplica) |
| `observaciones` | text | Detalles adicionales relevantes |
| `texto_noticia` | text | Texto original de la noticia fuente |

Campos adicionales sugeridos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fuente_url` | string | URL de la fuente original (trazabilidad) |
| `fuente_nombre` | string | Nombre del organismo o revista fuente |
| `fecha_consulta` | date | Fecha en que se consultó la IA |
| `estado` | enum | `confirmado` / `en_investigacion` / `descartado` |
| `severidad` | enum | `critico` / `alto` / `medio` / `bajo` |
| `boletin_asignado` | ref | ID del boletín donde se incluyó (si aplica) |

---

## BN-05: Tabla de incidentes destacados

- Se genera automáticamente a partir de los JSON almacenados.
- Muestra los incidentes más representativos del período.
- El editor puede **seleccionar y ordenar** qué incidentes aparecen en la tabla.
- La tabla se incluye como sección del boletín.

**Implemented by**: RF-05.1, RF-05.2, RF-05.3

---

## BN-06: Auspiciantes

- El editor puede cargar información de auspiciantes (nombre, logo, enlace).
- Los auspiciantes se muestran en la sección correspondiente del boletín.
- Esta sección es de carga manual; no se genera con IA.

**Implemented by**: RF-06.1, RF-06.2

---

## BN-07: Índice

- Se genera **automáticamente** al finalizar todas las secciones.
- Lista todas las secciones del boletín con enlaces internos.
- Se actualiza si se modifica alguna sección después de generado.

**Implemented by**: RF-07.1, RF-07.2

---

## BN-08: Almacenamiento del boletín completo

- Una vez completado, el boletín se almacena como un documento cerrado.
- El boletín almacenado es la **fuente de verdad** para distribución futura.
- Un boletín cerrado no se puede editar; cualquier corrección requiere una nueva edición.

**Implemented by**: RF-08.1, RF-08.2, RF-08.3

---

## BN-09: Seguridad y acceso

- Solo usuarios autenticados pueden acceder al sistema.
- El director de editorial tiene acceso total.
- Los colaboradores tienen acceso limitado a sus secciones asignadas.
- Todas las acciones quedan registradas (quién, cuándo, qué).

**Implemented by**: RF-09.1, RF-09.2, RF-09.3, RF-09.4, RF-09.5

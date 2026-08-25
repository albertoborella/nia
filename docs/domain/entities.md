# Entidades — NIA

## 1. Boletín

Representa una edición completa del boletín `Noticias sobre Inocuidad Alimentaria`.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único. |
| `nombre` | string | Nombre del boletín (ej: "Edición Marzo 2026"). |
| `periodo_inicio` | date | Fecha de inicio del período de cobertura. |
| `periodo_fin` | date | Fecha de fin del período de cobertura. |
| `fecha_publicacion_estimada` | date | Fecha estimada de publicación. |
| `estado` | enum | `borrador` · `en_progreso` · `completado` · `cerrado` |
| `creado_por` | ref → Usuario | Quién creó el boletín. |
| `fecha_creacion` | timestamp | Cuándo se creó. |
| `fecha_cierre` | timestamp | Cuándo se cerró (null si está abierto). |

---

## 2. Sección

Cada parte del boletín. Las secciones se completan en orden cronológico.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único. |
| `boletin_id` | ref → Boletín | Boletín al que pertenece. |
| `tipo` | enum | `editorial` · `incidentes` · `notas_colaboradores` · `tabla_incidentes` · `auspiciantes` · `indice` |
| `orden` | int | Posición en el boletín (1-6). |
| `estado` | enum | `pendiente` · `en_edicion` · `completada` |
| `contenido` | jsonb | Contenido específico de la sección (varía por tipo). |
| `completado_por` | ref → Usuario | Quién marcó como completada. |
| `fecha_completado` | timestamp | Cuándo se completó. |

### Contenido por tipo de sección

- **editorial**: `{ "texto": "markdown del editorial" }`
- **incidentes**: `{ "articulo_markdown": "...", "version": 1 }`
- **notas_colaboradores**: `{ "notas_ids": [...] }`
- **tabla_incidentes**: `{ "incidentes_ids": [...], "orden_seleccion": [...] }`
- **auspiciantes**: `{ "auspiciantes_ids": [...] }`
- **indice**: `{ "generado_automaticamente": true, "items": [...] }`

---

## 3. Nota de Colaborador

Artículo o nota recibida (interna o externamente) en formato .pdf o .docx.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único. |
| `titulo` | string | Título del artículo. |
| `autor` | string | Nombre del autor. |
| `colaborador_id` | ref → Colaborador | Colaborador que subió la nota (si aplica). |
| `fuente` | string | Revista, organismo o medio de origen. |
| `tema` | string | Categoría o tema (ej: "bacterias", "regulación", "alertas"). |
| `archivo_url` | string | Ruta al archivo subido (.pdf/.docx). |
| `archivo_tipo` | enum | `pdf` · `docx` |
| `estado` | enum | `pendiente` · `aprobada` · `archivada` |
| `boletin_asignado` | ref → Boletín | Boletín donde se incluyó (null si archivada). |
| `fecha_recepcion` | date | Cuándo se recibió. |
| `fecha_revision` | date | Cuándo fue revisada. |
| `revisado_por` | ref → Usuario | Quién la revisó. |
| `observaciones` | text | Notas del revisor. |

---

## 4. Incidente

Dato estructurado sobre un incidente de inocuidad alimentaria, generado por IA y revisado por el equipo.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único. |
| `incidente` | string | Nombre o descripción breve del incidente. |
| `producto` | string | Producto alimentario afectado. |
| `patogeno` | string | Agente causal (bacteria, virus, parásito, químico). |
| `organismo` | string | Organismo o empresa involucrada. |
| `pais` | string | País donde ocurrió. |
| `riesgo` | enum | `alto` · `medio` · `bajo` |
| `fecha_inicio` | date | Fecha de inicio del incidente. |
| `fecha_cierre` | date | Fecha de cierre (null si activo). |
| `observaciones` | text | Detalles adicionales. |
| `texto_noticia` | text | Texto original de la fuente. |
| `fuente_url` | string | URL de la fuente original. |
| `fuente_nombre` | string | Nombre del organismo o revista. |
| `fecha_consulta` | date | Fecha en que se consultó la IA. |
| `estado` | enum | `confirmado` · `en_investigacion` · `descartado` |
| `severidad` | enum | `critico` · `alto` · `medio` · `bajo` |
| `boletin_asignado` | ref → Boletín | Boletín donde se incluyó (null si no asignado). |
| `creado_por` | ref → Usuario | Quién ejecutó la consulta IA. |
| `fecha_creacion` | timestamp | Cuándo se creó el registro. |

---

## 5. Prompt

Prompt predefinido para consultas a la IA.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único. |
| `nombre` | string | Nombre descriptivo del prompt. |
| `descripcion` | string | Qué hace y cuándo usarlo. |
| `template` | text | Texto del prompt con variables (ej: `{{periodo_inicio}}`, `{{periodo_fin}}`). |
| `tipo` | enum | `consulta_incidentes` · `redaccion_articulo` · `otro` |
| `activo` | boolean | Si está habilitado para uso. |
| `configuracion` | jsonb | Parámetros: modelo, temperatura, max_tokens, etc. |
| `creado_por` | ref → Usuario | Quién creó el prompt. |
| `fecha_creacion` | timestamp | Fecha de creación. |

---

## 6. Auspiciante

Entidad que patrocina la publicación.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único. |
| `nombre` | string | Nombre del auspiciante. |
| `logo_url` | string | Ruta al archivo del logo. |
| `enlace` | string | URL del auspiciante (opcional). |
| `descripcion` | string | Descripción breve (opcional). |
| `activo` | boolean | Si está habilitado para incluir en boletines. |

---

## 7. Usuario

Persona con acceso al sistema administrativo.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único. |
| `nombre` | string | Nombre completo. |
| `email` | string | Correo electrónico (únicopara login). |
| `password_hash` | string | Contraseña hasheada (bcrypt). |
| `rol` | enum | `director` · `colaborador` |
| `activo` | boolean | Si tiene acceso al sistema. |
| `fecha_creacion` | timestamp | Cuándo se creó. |
| `ultimo_acceso` | timestamp | Último login. |

### Permisos por rol

| Acción | Director | Colaborador |
|--------|----------|-------------|
| Crear boletín | ✅ | ❌ |
| Escribir editorial | ✅ | ❌ |
| Consultar IA | ✅ | ❌ |
| Generar artículo | ✅ | ❌ |
| Revisar notas | ✅ | ❌ |
| Seleccionar incidentes | ✅ | ❌ |
| Compilar/cerrar boletín | ✅ | ❌ |
| Subir notas | ✅ | ✅ |
| Ver estado de notas propias | ✅ | ✅ |

---

## 8. Log de Auditoría

Registro de acciones realizadas en el sistema.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único. |
| `usuario_id` | ref → Usuario | Quién realizó la acción. |
| `accion` | string | Acción realizada (ej: "crear_boletin", "aprobar_nota"). |
| `entidad_tipo` | string | Tipo de entidad afectada (ej: "boletin", "nota"). |
| `entidad_id` | UUID | ID de la entidad afectada. |
| `detalles` | jsonb | Información adicional de la acción. |
| `fecha` | timestamp | Cuándo ocurrió. |
| `ip` | string | Dirección IP de origen. |

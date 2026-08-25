# Diseño de API — NIA

## Convenciones

- **Base URL**: `/api/v1`
- **Formato**: JSON (`application/json`)
- **Autenticación**: Cookie httpOnly con JWT
- **Errores**: Formato estándar `{ "detail": { "code": "ERROR_CODE", "message": "..." } }`
- **Paginación**: Query params `?page=1&limit=20`
- **Ordenamiento**: `?sort=campo&order=asc|desc`

## Autenticación

> **Use case**: [UC-01 — Autenticación y Autorización](../use-cases/authentication.md)

### POST /api/v1/auth/login
Login del usuario.

**Request:**
```json
{
  "email": "director@nia.com",
  "password": "..."
}
```

**Response (200):**
```json
{
  "user": {
    "id": "uuid",
    "nombre": "Director",
    "email": "director@nia.com",
    "rol": "director"
  }
}
```
**Cookies seteadas:** `access_token` (15 min), `refresh_token` (7 días)

---

### POST /api/v1/auth/refresh
Renueva el access token usando el refresh token (cookie).

**Response (200):**
```json
{ "message": "Token refreshed" }
```
**Cookies seteadas:** `access_token` renovado

---

### POST /api/v1/auth/logout
Elimina cookies de autenticación.

**Response (200):**
```json
{ "message": "Logged out" }
```

---

### GET /api/v1/auth/me
Obtiene el usuario autenticado actual.

**Response (200):**
```json
{
  "id": "uuid",
  "nombre": "Director",
  "email": "director@nia.com",
  "rol": "director"
}
```

---

### PUT /api/v1/auth/change-password
Cambia la contraseña del usuario autenticado.

**Request:**
```json
{
  "current_password": "contraseña_actual",
  "new_password": "nueva_contraseña"
}
```

**Response (200):**
```json
{ "message": "Password updated" }
```

---

## Usuarios

> **Use case**: [UC-09 — Gestión de Usuarios](../use-cases/user-management.md)

### GET /api/v1/usuarios
Lista todos los usuarios activos (solo director).

**Query params:** `?page=1&limit=20&rol=colaborador`

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "nombre": "Juan Pérez",
      "email": "juan@nia.com",
      "rol": "colaborador",
      "activo": true,
      "fecha_creacion": "2026-01-15T10:00:00Z",
      "ultimo_acceso": "2026-03-15T08:30:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

---

### POST /api/v1/usuarios
Crea un nuevo usuario (solo director).

**Request:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@nia.com",
  "password": "contraseña_segura",
  "rol": "colaborador"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "nombre": "Juan Pérez",
  "email": "juan@nia.com",
  "rol": "colaborador",
  "activo": true,
  "fecha_creacion": "2026-03-15T10:00:00Z"
}
```

---

### PUT /api/v1/usuarios/{id}
Actualiza un usuario (solo director).

**Request:**
```json
{
  "nombre": "Juan Pérez Updated",
  "email": "juan.updated@nia.com",
  "rol": "colaborador"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "nombre": "Juan Pérez Updated",
  "email": "juan.updated@nia.com",
  "rol": "colaborador",
  "activo": true,
  "fecha_creacion": "2026-01-15T10:00:00Z"
}
```

---

### POST /api/v1/usuarios/{id}/reset-password
Restablece la contraseña de un usuario (solo director). Genera una contraseña temporal y la envía por email.

**Response (200):**
```json
{ "message": "Password reset email sent" }
```

---

### GET /api/v1/usuarios/{id}/actividad
Obtiene el log de auditoría de un usuario (solo director).

**Query params:** `?page=1&limit=20`

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "accion": "login",
      "fecha": "2026-03-15T08:30:00Z",
      "ip": "192.168.1.100",
      "detalles": "Login exitoso"
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 20
}
```

---

## Boletines

> **Use case**: [UC-02 — Gestión de Boletines](../use-cases/bulletin-management.md)

### GET /api/v1/boletines
Lista boletines del usuario.

**Query params:** `?page=1&limit=20&estado=borrador`

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "nombre": "Edición Marzo 2026",
      "periodo_inicio": "2026-03-01",
      "periodo_fin": "2026-03-31",
      "estado": "en_progreso",
      "secciones_completadas": 2,
      "secciones_total": 6,
      "fecha_creacion": "2026-03-10T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

---

### POST /api/v1/boletines
Crea un nuevo boletín.

**Request:**
```json
{
  "nombre": "Edición Marzo 2026",
  "periodo_inicio": "2026-03-01",
  "periodo_fin": "2026-03-31",
  "fecha_publicacion_estimada": "2026-04-05"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "nombre": "Edición Marzo 2026",
  "estado": "borrador",
  "secciones": [
    { "tipo": "editorial", "orden": 1, "estado": "pendiente" },
    { "tipo": "incidentes", "orden": 2, "estado": "pendiente" },
    { "tipo": "notas_colaboradores", "orden": 3, "estado": "pendiente" },
    { "tipo": "tabla_incidentes", "orden": 4, "estado": "pendiente" },
    { "tipo": "auspiciantes", "orden": 5, "estado": "pendiente" },
    { "tipo": "indice", "orden": 6, "estado": "pendiente" }
  ]
}
```

---

### GET /api/v1/boletines/{id}
Detalle de un boletín con todas sus secciones.

---

### PUT /api/v1/boletines/{id}
Actualiza datos del boletín (solo en estado `borrador`).

---

### POST /api/v1/boletines/{id}/completar-seccion
Marca una sección como completada.

**Request:**
```json
{
  "tipo": "editorial"
}
```

---

### POST /api/v1/boletines/{id}/cerrar
Cierra el boletín (solo si todas las secciones están completadas).

---

## Secciones

> **Use case**: [UC-03 — Sección Editorial](../use-cases/editorial-section.md)

### GET /api/v1/boletines/{id}/secciones
Lista las secciones de un boletín.

---

### GET /api/v1/boletines/{id}/secciones/{tipo}
Obtiene el contenido de una sección específica.

---

### PUT /api/v1/boletines/{id}/secciones/{tipo}
Actualiza el contenido de una sección.

**Request (editorial):**
```json
{
  "contenido": {
    "texto": "# Editorial\n\nEn este número..."
  }
}
```

---

## Notas de Colaboradores

> **Use case**: [UC-05 — Gestión de Notas de Colaboradores](../use-cases/contributor-notes.md)

### GET /api/v1/notas
Lista todas las notas.

**Query params:** `?page=1&limit=20&estado=pendiente&tema=bacterias&autor=Juan`

---

### POST /api/v1/notas
Sube una nueva nota (multipart/form-data).

**Fields:**
- `titulo` (string, required)
- `autor` (string, required)
- `fuente` (string, optional)
- `tema` (string, optional)
- `archivo` (file, required: .pdf o .docx)

---

### GET /api/v1/notas/{id}
Detalle de una nota.

---

### PUT /api/v1/notas/{id}
Actualiza los metadatos de una nota (sin modificar el archivo).

**Request:**
```json
{
  "titulo": "Nuevo título del artículo",
  "autor": "Autor Actualizado",
  "fuente": "Revista Nueva",
  "tema": "regulación"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "titulo": "Nuevo título del artículo",
  "autor": "Autor Actualizado",
  "fuente": "Revista Nueva",
  "tema": "regulación",
  "estado": "pendiente",
  "fecha_recepcion": "2026-03-10T10:00:00Z"
}
```

---

### DELETE /api/v1/notas/{id}
Elimina una nota y su archivo asociado (solo director).

**Response (200):**
```json
{ "message": "Note deleted" }
```

---

### PUT /api/v1/notas/{id}/estado
Cambia el estado de una nota.

**Request:**
```json
{
  "estado": "aprobada",
  "boletin_asignado": "uuid",
  "observaciones": "Artículo relevante para la edición actual"
}
```

---

### GET /api/v1/notas/{id}/descarga
Descarga el archivo de la nota.

**Response:** Archivo binario (.pdf o .docx)

---

## Incidentes

> **Use cases**: [UC-06 — Gestión de Incidentes](../use-cases/incident-management.md), [UC-04 — Artículo de Incidentes Mundiales](../use-cases/global-incidents-article.md)

### POST /api/v1/incidentes
Crea un incidente manualmente (solo director).

**Request:**
```json
{
  "incidente": "Brote de Salmonella en leche",
  "producto": "Leche entera",
  "patogeno": "Salmonella enteritidis",
  "organismo": "Lácteos XYZ",
  "pais": "Argentina",
  "riesgo": "alto",
  "fecha_inicio": "2026-03-05",
  "fecha_cierre": null,
  "observaciones": "Retiro voluntario de 50.000 litros",
  "texto_noticia": "...",
  "fuente_url": "https://...",
  "fuente_nombre": "ANMAT",
  "severidad": "alto",
  "estado": "confirmado"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "incidente": "Brote de Salmonella en leche",
  "producto": "Leche entera",
  "patogeno": "Salmonella enteritidis",
  "organismo": "Lácteos XYZ",
  "pais": "Argentina",
  "riesgo": "alto",
  "fecha_inicio": "2026-03-05",
  "fecha_cierre": null,
  "observaciones": "Retiro voluntario de 50.000 litros",
  "texto_noticia": "...",
  "fuente_url": "https://...",
  "fuente_nombre": "ANMAT",
  "severidad": "alto",
  "estado": "confirmado",
  "fecha_creacion": "2026-03-15T10:00:00Z"
}
```

---

### GET /api/v1/incidentes/{id}
Obtiene un incidente por ID.

**Response (200):**
```json
{
  "id": "uuid",
  "incidente": "Brote de Salmonella en leche",
  "producto": "Leche entera",
  "patogeno": "Salmonella enteritidis",
  "organismo": "Lácteos XYZ",
  "pais": "Argentina",
  "riesgo": "alto",
  "fecha_inicio": "2026-03-05",
  "fecha_cierre": null,
  "observaciones": "Retiro voluntario de 50.000 litros",
  "texto_noticia": "...",
  "fuente_url": "https://...",
  "fuente_nombre": "ANMAT",
  "severidad": "alto",
  "estado": "confirmado",
  "fecha_creacion": "2026-03-15T10:00:00Z"
}
```

---

### POST /api/v1/incidentes/consultar
Consulta a la IA sobre incidentes en un período.

**Request:**
```json
{
  "periodo_inicio": "2026-03-01",
  "periodo_fin": "2026-03-31"
}
```

**Response (200):**
```json
{
  "incidentes": [
    {
      "incidente": "Brote de Salmonella en leche",
      "producto": "Leche entera",
      "patogeno": "Salmonella enteritidis",
      "organismo": "Lácteos XYZ",
      "pais": "Argentina",
      "riesgo": "alto",
      "fecha_inicio": "2026-03-05",
      "fecha_cierre": null,
      "observaciones": "Retiro voluntario de 50.000 litros",
      "texto_noticia": "...",
      "fuente_url": "https://...",
      "fuente_nombre": "ANMAT",
      "fecha_consulta": "2026-03-15",
      "estado": "confirmado",
      "severidad": "alto"
    }
  ],
  "prompt_utilizado": "uuid",
  "tokens_consumidos": 1500
}
```

---

### GET /api/v1/incidentes
Lista incidentes almacenados.

**Query params:** `?page=1&limit=20&pais=Argentina&riesgo=alto&estado=confirmado`

---

### PUT /api/v1/incidentes/{id}
Edita un incidente.

---

### DELETE /api/v1/incidentes/{id}
Elimina un incidente.

---

### POST /api/v1/incidentes/{boletin_id}/generar-articulo
Genera el artículo de incidentes para un boletín.

**Response (200):**
```json
{
  "articulo_markdown": "# Incidentes de inocuidad...\n\n...",
  "version": 1,
  "incidentes_incluidos": 5
}
```

---

### GET /api/v1/incidentes/{boletin_id}/articulo
Obtiene el artículo generado para edición.

---

### PUT /api/v1/incidentes/{boletin_id}/articulo
Guarda la versión editada del artículo.

**Request:**
```json
{
  "articulo_markdown": "# Incidentes de inocuidad...\n\n(versión editada)",
  "version": 2
}
```

---

## Prompts

> **Use case**: [UC-10 — Gestión de Prompts de IA](../use-cases/prompt-management.md)

### GET /api/v1/prompts
Lista prompts disponibles.

---

### POST /api/v1/prompts
Crea un nuevo prompt (solo director).

---

### GET /api/v1/prompts/{id}
Obtiene un prompt por ID.

**Response (200):**
```json
{
  "id": "uuid",
  "nombre": "Consulta Incidentes Mensual",
  "descripcion": "Busca incidentes de inocuidad en un período dado",
  "template": "Busca incidentes de inocuidad alimentaria desde {{periodo_inicio}} hasta {{periodo_fin}}.",
  "tipo": "consulta_incidentes",
  "configuracion": {
    "modelo": "gpt-4",
    "temperatura": 0.3,
    "max_tokens": 2000
  },
  "activo": true,
  "fecha_creacion": "2026-03-01T10:00:00Z"
}
```

---

### PUT /api/v1/prompts/{id}
Actualiza un prompt.

---

### DELETE /api/v1/prompts/{id}
Elimina un prompt (solo director).

**Response (200):**
```json
{ "message": "Prompt deleted" }
```

---

### POST /api/v1/prompts/{id}/test
Prueba un prompt con datos de ejemplo.

---

## Auspiciantes

> **Use case**: [UC-08 — Gestión de Auspiciantes](../use-cases/sponsors-management.md)

### GET /api/v1/auspiciantes
Lista auspiciantes activos.

---

### POST /api/v1/auspiciantes
Crea un auspiciante (solo director).

---

### PUT /api/v1/auspiciantes/{id}
Actualiza un auspiciante.

---

### DELETE /api/v1/auspiciantes/{id}
Desactiva un auspiciante (soft delete).

---

## Tabla de Incidentes Destacados

> **Use case**: [UC-07 — Tabla de Incidentes Destacados](../use-cases/world-incidents-table.md)

### GET /api/v1/boletines/{id}/tabla-incidentes
Obtiene la tabla de incidentes seleccionados para el boletín.

---

### PUT /api/v1/boletines/{id}/tabla-incidentes
Actualiza la selección y orden de incidentes de la tabla.

**Request:**
```json
{
  "incidentes_ids": ["uuid1", "uuid2", "uuid3"],
  "orden": ["uuid2", "uuid1", "uuid3"]
}
```

---

## Auspiciantes del Boletín

> **Use case**: [UC-08 — Gestión de Auspiciantes](../use-cases/sponsors-management.md)

### GET /api/v1/boletines/{id}/auspiciantes
Lista auspiciantes asignados al boletín.

---

### PUT /api/v1/boletines/{id}/auspiciantes
Actualiza los auspiciantes del boletín.

**Request:**
```json
{
  "auspiciantes_ids": ["uuid1", "uuid2"]
}
```

---

## Índice

### GET /api/v1/boletines/{id}/indice
Genera y retorna el índice del boletín. El índice se genera dinámicamente a partir de las secciones del boletín, no se almacena como una sección separada en la base de datos.

**Response (200):**
```json
{
  "indice": [
    { "seccion": "editorial", "titulo": "Editorial del mes", "pagina": 1 },
    { "seccion": "incidentes", "titulo": "Incidentes Globales", "pagina": 2 },
    { "seccion": "notas_colaboradores", "titulo": "Notas de Colaboradores", "pagina": 5 },
    { "seccion": "tabla_incidentes", "titulo": "Tabla de Incidentes", "pagina": 8 },
    { "seccion": "auspiciantes", "titulo": "Auspiciantes", "pagina": 10 }
  ]
}
```

---

## Compilación

### POST /api/v1/boletines/{id}/compilar
Compila todas las secciones en el documento final.

**Response (200):**
```json
{
  "boletin_compilado": {
    "editorial": { "texto": "..." },
    "articulo_incidentes": { "markdown": "..." },
    "tabla_incidentes": { "html": "..." },
    "notas": [...],
    "auspiciantes": [...],
    "indice": [...]
  },
  "formato": "markdown"
}
```

---

### GET /api/v1/boletines/{id}/exportar
Exporta el boletín compilado.

**Query params:** `?formato=pdf|markdown`

---

## Errores

| Código HTTP | Significado |
|-------------|-------------|
| 400 | Request inválido |
| 401 | No autenticado |
| 403 | Sin permisos para esta acción |
| 404 | Recurso no encontrado |
| 409 | Conflicto (ej: boletín ya cerrado) |
| 422 | ValidationError (campos inválidos) |
| 500 | Error interno del servidor |
| 503 | Servicio de IA no disponible |

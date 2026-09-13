# Guía de Prueba de Endpoints — NIA

Flujo cronológico para probar el backend completo, siguiendo el orden real de armado de una publicación.

> **Prompts pre-cargados:** Al iniciar el sistema se crean 5 prompts por defecto.
> Consultá `GET /api/v1/prompts` para verlos. El prompt "Consulta Incidentes Mensual"
> es el que usa el flujo de incidentes (paso 5). Los demás son para uso manual
> (copiar → pegar en IA → usar la respuesta libremente).

---

## Orden de Prueba

```
1. Login
2. Crear Boletín
3. Escribir Editorial (prompt manual)
4. Subir Notas de Colaboradores
5. Consultar Incidentes IA (prompt → respuesta guardada)
6. Importar Incidentes
7. Generar Artículo de Incidentes
8. Editar Artículo
9. Seleccionar Tabla de Incidentes
10. Asignar Auspiciantes
11. Completar Secciones
12. Cerrar Boletín
13. Verificar Health Check
14. Revisar Auditoría
```

---

## 1. Login

**Endpoint:** `POST /api/v1/auth/login`

```json
{
  "email": "director@nia.com",
  "password": "Director123!"
}
```

**Resultado:** Cookies `access_token` y `refresh_token` seteadas automáticamente.

> En Swagger: click "Authorize" → login → las cookies se aplican a todos los endpoints siguientes.

---

## 2. Crear Boletín

**Endpoint:** `POST /api/v1/boletines`

```json
{
  "nombre": "Edición Marzo 2026",
  "periodo_inicio": "2026-03-01",
  "periodo_fin": "2026-03-31",
  "fecha_publicacion_estimada": "2026-04-05"
}
```

**Resultado:** Boletín creado en estado `borrador` con 6 secciones automáticas:
1. editorial (pendiente)
2. incidentes (pendiente)
3. notas_colaboradores (pendiente)
4. tabla_incidentes (pendiente)
5. auspiciantes (pendiente)
6. indice (pendiente)

**Guardar:** `boletin_id` de la respuesta.

---

## 3. Escribir Editorial (Prompt Manual)

> Este prompt es solo para ayudarte a redactar. La respuesta NO se guarda en el sistema.
> Copiá el prompt, pegalo en cualquier IA, y escribí la editorial directamente en el sistema.

**Prompt para copiar:**

```
Sos editor de una publicación especializada en inocuidad alimentaria llamada 
"Noticias sobre Inocuidad Alimentaria". 

Escribí una editorial para la edición de Marzo 2026 con las siguientes 
directrices:

- Extensión: 300-500 palabras
- Tono: profesional pero accesible
- Tema central: Importancia de la vigilancia epidemiológica en la cadena 
  alimentaria
- Incluí: al menos 2 eventos o tendencias relevantes del período
- Cierre: invitar al lector a profundizar en las secciones del boletín

Formato: Markdown con títulos y párrafos separados.
```

**Después de obtener la respuesta:**

1. Guardá el texto en la sección editorial del boletín:

**Endpoint:** `PUT /api/v1/boletines/{boletin_id}/secciones/editorial`

```json
{
  "contenido": {
    "texto": "# Editorial\n\nAcá pegás el texto generado por la IA...\n\n## Título del editorial...\n\nPárrafos..."
  }
}
```

2. Completá la sección:

**Endpoint:** `POST /api/v1/boletines/{boletin_id}/completar-seccion`

```json
{
  "tipo": "editorial"
}
```

---

## 4. Subir Notas de Colaboradores

### 4.1 Subir nota PDF

**Endpoint:** `POST /api/v1/notas` (multipart/form-data)

| Campo | Tipo | Valor |
|-------|------|-------|
| titulo | string | "Brote de Listeria en Quesos Artesanales" |
| autor | string | "Dr. María García" |
| fuente | string | "Revista de Inocuidad" |
| tema | string | "bacterias" |
| archivo | file |Seleccioná un archivo .pdf |

### 4.2 Subir nota DOCX

**Endpoint:** `POST /api/v1/notas` (multipart/form-data)

| Campo | Tipo | Valor |
|-------|------|-------|
| titulo | string | "Regulación de Alimentos Genéticamente Modificados" |
| autor | string | "Lic. Carlos López" |
| fuente | string | "ANMAT" |
| tema | string | "regulacion" |
| archivo | file | Seleccioná un archivo .docx |

### 4.3 Revisar y aprobar nota

**Endpoint:** `PUT /api/v1/notas/{nota_id}/estado`

```json
{
  "estado": "aprobada",
  "boletin_asignado": "{boletin_id}",
  "observaciones": "Artículo relevante para la edición actual"
}
```

### 4.4 Completar sección de notas

**Endpoint:** `POST /api/v1/boletines/{boletin_id}/completar-seccion`

```json
{
  "tipo": "notas_colaboradores"
}
```

---

## 5. Consultar Incidentes IA (Prompt → Guardado)

> Este prompt SÍ guarda la respuesta en el sistema para importar incidentes.

### 5.1 Listar prompts pre-cargados

> Los prompts ya vienen pre-cargados al iniciar el sistema. No es necesario crearlos.

**Endpoint:** `GET /api/v1/prompts`

**Prompts disponibles:**
| Nombre | Tipo | Uso |
|--------|------|-----|
| Consulta Incidentes Mensual | consulta_incidentes | Guarda respuesta en archivos |
| Redacción Editorial | otro | Uso manual, NO guarda |
| Resumen Ejecutivo para Directorio | otro | Uso manual, NO guarda |
| Revisión de Normativa | otro | Uso manual, NO guarda |
| Redacción de Artículos de Colaboradores | otro | Uso manual, NO guarda |

**Obtener el prompt de consulta:**

**Endpoint:** `GET /api/v1/prompts` → filtrar por nombre "Consulta Incidentes Mensual"

**Guardar:** `prompt_id` de la respuesta.

### 5.2 Renderizar prompt con variables

**Endpoint:** `POST /api/v1/prompts/{prompt_id}/render`

```json
{
  "variables": {
    "periodo_inicio": "2026-03-01",
    "periodo_fin": "2026-03-31"
  }
}
```

**Resultado:** Texto renderizado listo para copiar.

### 5.3 Copiar y preguntar a la IA

1. Copiá el `rendered_text` de la respuesta
2. Pegalo en ChatGPT, Claude, o cualquier IA
3. Copiá la respuesta JSON que te devuelva

### 5.4 Subir respuesta de la IA

**Endpoint:** `POST /api/v1/prompts/{prompt_id}/upload-response?boletin_id={boletin_id}`

```json
{
  "incidentes": [
    {
      "incidente": "Brote de Salmonella en leche pasteurizada",
      "producto": "Leche pasteurizada",
      "patogeno": "Salmonella enteritidis",
      "organismo": "Lácteos del Sur S.A.",
      "pais": "Argentina",
      "riesgo": "alto",
      "fecha_inicio": "2026-03-05",
      "observaciones": "Retiro voluntario de 50.000 litros",
      "fuente_url": "https://www.anmat.gov.ar",
      "fuente_nombre": "ANMAT",
      "severidad": "alto"
    },
    {
      "incidente": "Contaminación por Listeria en queso",
      "producto": "Queso fontina",
      "patogeno": "Listeria monocytogenes",
      "organismo": "Queserías Patagónicas",
      "pais": "Argentina",
      "riesgo": "alto",
      "fecha_inicio": "2026-03-10",
      "observaciones": "Producto retirado de supermercados",
      "fuente_url": "https://www.anmat.gov.ar",
      "fuente_nombre": "ANMAT",
      "severidad": "alto"
    }
  ],
  "prompt_rendered": "Texto del prompt renderizado que usaste"
}
```

**Resultado:** Archivos guardados en `backend/data/responses/{prompt_id}/{boletin_id}/{timestamp}/`

### 5.5 Importar incidentes a la base de datos

**Endpoint:** `POST /api/v1/incidentes/importar?prompt_id={prompt_id}&boletin_id={boletin_id}`

**Resultado:** Incidentes insertados en la tabla `incidentes` con `boletin_asignado = {boletin_id}`.

---

## 6. Revisar y Editar Incidentes

### 6.1 Listar incidentes importados

**Endpoint:** `GET /api/v1/incidentes?boletin_asignado={boletin_id}`

### 6.2 Editar un incidente

**Endpoint:** `PUT /api/v1/incidentes/{incidente_id}`

```json
{
  "observaciones": "Observaciones actualizadas después de revisión manual",
  "estado_verificacion": "confirmado"
}
```

### 6.3 Eliminar un incidente (si es necesario)

**Endpoint:** `DELETE /api/v1/incidentes/{incidente_id}`

---

## 7. Generar Artículo de Incidentes

**Endpoint:** `POST /api/v1/incidentes/{boletin_id}/generar-articulo`

**Resultado:** Artículo markdown generado y guardado en `backend/data/articulos/{boletin_id}/articulo.md`

El artículo se genera agrupado por nivel de riesgo con tabla resumen por país.

---

## 8. Editar Artículo

### 8.1 Obtener artículo generado

**Endpoint:** `GET /api/v1/incidentes/{boletin_id}/articulo`

### 8.2 Guardar edición del artículo

**Endpoint:** `PUT /api/v1/incidentes/{boletin_id}/articulo`

```json
{
  "articulo_markdown": "# Incidentes de Inocuidad Alimentaria\n\n## RIESGO ALTO\n\n### 1. Brote de Salmonella...\n\n(texto editado por vos)\n\n## Resumen\n\n| País | Cantidad | Riesgo Máximo |\n|------|----------|---------------|\n| Argentina | 5 | alto |",
  "version": 2
}
```

### 8.3 Guardar en la sección del boletín

**Endpoint:** `PUT /api/v1/boletines/{boletin_id}/secciones/incidentes`

```json
{
  "contenido": {
    "articulo_markdown": "El mismo markdown que guardaste arriba",
    "version": 2
  }
}
```

### 8.4 Completar sección

**Endpoint:** `POST /api/v1/boletines/{boletin_id}/completar-seccion`

```json
{
  "tipo": "incidentes"
}
```

---

## 9. Tabla de Incidentes Destacados

### 9.1 Obtener tabla actual

**Endpoint:** `GET /api/v1/boletines/{boletin_id}/tabla-incidentes`

### 9.2 Actualizar selección y orden

**Endpoint:** `PUT /api/v1/boletines/{boletin_id}/secciones/tabla_incidentes`

```json
{
  "contenido": {
    "incidentes_ids": ["uuid1", "uuid2", "uuid3"],
    "orden_seleccion": ["uuid2", "uuid1", "uuid3"]
  }
}
```

### 9.3 Completar sección

**Endpoint:** `POST /api/v1/boletines/{boletin_id}/completar-seccion`

```json
{
  "tipo": "tabla_incidentes"
}
```

---

## 10. Asignar Auspiciantes

### 10.1 Crear auspiciante (si no existe)

**Endpoint:** `POST /api/v1/auspiciantes`

```json
{
  "nombre": "Sponsor Food Safety Corp",
  "enlace": "https://www.example.com",
  "descripcion": "Líder en soluciones de control de calidad alimentaria"
}
```

### 10.2 Asignar auspiciantes al boletín

**Endpoint:** `PUT /api/v1/boletines/{boletin_id}/auspiciantes`

```json
{
  "auspiciantes_ids": ["auspiciante_id_1", "auspiciante_id_2"]
}
```

### 10.3 Completar sección

**Endpoint:** `POST /api/v1/boletines/{boletin_id}/completar-seccion`

```json
{
  "tipo": "auspiciantes"
}
```

---

## 11. Completar Índice

El índice se genera dináricamente, pero la sección debe marcarse como completada:

**Endpoint:** `POST /api/v1/boletines/{boletin_id}/completar-seccion`

```json
{
  "tipo": "indice"
}
```

---

## 12. Cerrar Boletín

**Precondición:** Todas las 6 secciones deben estar en estado `completada`.

**Endpoint:** `POST /api/v1/boletines/{boletin_id}/cerrar`

**Resultado:** Boletín pasa a estado `cerrado` con `fecha_cierre` seteada. No se puede editar más.

---

## 13. Health Check

**Endpoint:** `GET /api/v1/health`

No requiere autenticación.

```json
{
  "status": "healthy",
  "services": {
    "database": "healthy"
  }
}
```

---

## 14. Revisar Auditoría

**Endpoint:** `GET /api/v1/auditoria`

Solo director puede ver los logs.

---

## Prompts Adicionales (Uso Manual)

Estos prompts son para ayudarte a redactar. NO guardan respuesta en el sistema.

### Prompt: Redacción de Artículos de Colaboradores

```
Sos editor de la publicación "Noticias sobre Inocuidad Alimentaria".

Redactá un artículo de 800-1200 palabras sobre el siguiente tema:
[Tema del artículo]

Estructura:
1. Título atractivo
2. Introducción con contexto
3. Desarrollo con datos y fuentes
4. Conclusiones
5. Referencias

Tono: profesional, técnico pero accesible para profesionales del sector alimentario.
Formato: Markdown
```

### Prompt: Resumen Ejecutivo para Directorio

```
Sos asesor de comunicación especializado en seguridad alimentaria.

Generá un resumen ejecutivo de 200 palabras sobre los incidentes de 
inocuidad más relevantes del período [fecha inicio] a [fecha fin].

El resumen debe:
- Destacar los 3-5 incidentes más críticos
- Mencionar tendencias
- Incluir recomendaciones breves
- Tono ejecutivo, directo

Formato: Texto plano
```

### Prompt: Revisión de Normativa

```
Sos experto en regulación alimentaria de Argentina.

Analizá la siguiente normativa y explicá:
[Número de normativa o descripción]

1. Objeto de la norma
2. Alcance
3. Requisitos principales
4. Plazos de cumplimiento
5. Sanciones por incumplimiento

Formato: Markdown con secciones claras
```

### Prompt: Traducción Técnica

```
Sos traductor especializado en seguridad alimentaria.

Traducí al español el siguiente texto técnico sobre inocuidad alimentaria:
[Texto en inglés]

Mantené la terminología técnica precisa. 
Formato: Markdown
```

---

## Resumen del Flujo

```
LOGIN → CREAR BOLETÍN → EDITORIAL (prompt manual) → SUBIR NOTAS
    ↓
CONSULTAR INCIDENTES (prompt → guardar respuesta) → IMPORTAR A DB
    ↓
GENERAR ARTÍCULO → EDITAR → GUARDAR EN SECCIÓN
    ↓
TABLA DESTACADOS → AUSPICIANTES → ÍNDICE
    ↓
CERRAR BOLETÍN → VERIFICAR HEALTH → REVISAR AUDITORÍA
```

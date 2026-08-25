# Modelo de Datos — NIA

## Diagrama de relaciones

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   USUARIO    │     │   BOLETÍN    │     │  AUSPICIANTE │
│──────────────│     │──────────────│     │──────────────│
│ id (PK)      │◄────│ creado_por   │     │ id (PK)      │
│ nombre       │     │ id (PK)      │     │ nombre       │
│ email        │     │ nombre       │     │ logo_url     │
│ password_hash│     │ periodo_*    │     │ enlace       │
│ rol          │     │ estado       │     │ activo       │
│ activo       │     │ fecha_*      │     └──────┬───────┘
└──────┬───────┘     └──────┬───────┘            │
       │                    │                    │
       │            ┌───────┴────────┐           │
       │            │    SECCIÓN     │           │
       │            │────────────────│           │
       │            │ id (PK)        │           │
       │            │ boletin_id(FK) │           │
       │            │ tipo           │           │
       │            │ orden          │           │
       │            │ estado         │           │
       │            │ contenido      │           │
       │            └────────────────┘           │
       │                                        │
       │  ┌───────────────────┐                  │
       │  │ NOTA_COLABORADOR  │                  │
       │  │───────────────────│                  │
       ├─►│ id (PK)           │                  │
       │  │ colaborador_id    │    BOLETÍN_AUSPICIANTE
       │  │ boletin_asign(FK) │    (tabla pivote)
       │  │ estado            │    ┌─────────────────────┐
       │  │ archivo_*         │    │ boletin_id (FK, PK) │
       │  └───────────────────┘    │ auspiciante_id(FK,PK)│
       │                           └─────────────────────┘
       │  ┌───────────────────┐
       │  │    INCIDENTE      │
       │  │───────────────────│
       ├─►│ id (PK)           │
       │  │ boletin_asign(FK) │
       │  │ incidente         │
       │  │ producto          │
       │  │ patogeno          │
       │  │ pais              │
       │  │ riesgo            │
       │  │ severidad         │
       │  │ fecha_*           │
       │  │ fuente_*          │
       │  │ estado            │
       │  └───────────────────┘
       │
       │  ┌───────────────────┐     ┌───────────────────┐
       │  │     PROMPT        │     │ LOG_AUDITORIA     │
       │  │───────────────────│     │───────────────────│
       └─►│ id (PK)           │     │ id (PK)           │
          │ creado_por (FK)   │     │ usuario_id (FK)   │
          │ nombre            │     │ accion            │
          │ template          │     │ entidad_tipo      │
          │ tipo              │     │ entidad_id        │
          │ configuracion     │     │ detalles          │
          └───────────────────┘     │ fecha             │
                                    └───────────────────┘
```

## Tablas

### usuarios

```sql
CREATE TABLE usuarios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(255) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    rol             VARCHAR(20) NOT NULL CHECK (rol IN ('director', 'colaborador')),
    activo          BOOLEAN DEFAULT TRUE,
    fecha_creacion  TIMESTAMP DEFAULT NOW(),
    ultimo_acceso   TIMESTAMP
);
```

### boletines

```sql
CREATE TABLE boletines (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre                    VARCHAR(255) NOT NULL,
    periodo_inicio            DATE NOT NULL,
    periodo_fin               DATE NOT NULL,
    fecha_publicacion_estimada DATE,
    estado                    VARCHAR(20) NOT NULL DEFAULT 'borrador'
                                CHECK (estado IN ('borrador', 'en_progreso', 'completado', 'cerrado')),
    creado_por                UUID REFERENCES usuarios(id),
    fecha_creacion            TIMESTAMP DEFAULT NOW(),
    fecha_cierre              TIMESTAMP
);
```

### secciones

```sql
CREATE TABLE secciones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    boletin_id      UUID NOT NULL REFERENCES boletines(id) ON DELETE CASCADE,
    tipo            VARCHAR(30) NOT NULL
                      CHECK (tipo IN ('editorial', 'incidentes', 'notas_colaboradores',
                                      'tabla_incidentes', 'auspiciantes', 'indice')),
    -- Nota: El tipo 'indice' se incluye aquí para consistencia del esquema,
    -- pero el contenido se genera dinámicamente por el endpoint GET /boletines/{id}/indice
    orden           INT NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                      CHECK (estado IN ('pendiente', 'en_edicion', 'completada')),
    contenido       JSONB DEFAULT '{}',
    completado_por  UUID REFERENCES usuarios(id),
    fecha_completado TIMESTAMP,
    UNIQUE (boletin_id, tipo),
    UNIQUE (boletin_id, orden)
);
```

### notas_colaboradores

```sql
CREATE TABLE notas_colaboradores (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo            VARCHAR(500) NOT NULL,
    autor             VARCHAR(255) NOT NULL,
    colaborador_id    UUID REFERENCES usuarios(id),
    fuente            VARCHAR(500),
    tema              VARCHAR(100),
    archivo_url       VARCHAR(1000) NOT NULL,
    archivo_tipo      VARCHAR(10) NOT NULL CHECK (archivo_tipo IN ('pdf', 'docx')),
    estado            VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                        CHECK (estado IN ('pendiente', 'aprobada', 'archivada')),
    boletin_asignado  UUID REFERENCES boletines(id),
    fecha_recepcion   DATE NOT NULL,
    fecha_revision    DATE,
    revisado_por      UUID REFERENCES usuarios(id),
    observaciones     TEXT
);
```

### incidentes

```sql
CREATE TABLE incidentes (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incidente         VARCHAR(500) NOT NULL,
    producto          VARCHAR(255) NOT NULL,
    patogeno          VARCHAR(255) NOT NULL,
    organismo         VARCHAR(255),
    pais              VARCHAR(100) NOT NULL,
    riesgo            VARCHAR(10) NOT NULL CHECK (riesgo IN ('alto', 'medio', 'bajo')),
    fecha_inicio      DATE NOT NULL,
    fecha_cierre      DATE,
    observaciones     TEXT,
    texto_noticia     TEXT,
    fuente_url        VARCHAR(1000),
    fuente_nombre     VARCHAR(500),
    fecha_consulta    DATE NOT NULL,
    estado_verificacion VARCHAR(20) NOT NULL DEFAULT 'confirmado'
                        CHECK (estado_verificacion IN ('confirmado', 'en_investigacion', 'descartado')),
    estado_editorial VARCHAR(20) NOT NULL DEFAULT 'generado'
                        CHECK (estado_editorial IN ('generado', 'revisado', 'aprobado', 'incluido')),
    severidad         VARCHAR(10) NOT NULL CHECK (severidad IN ('critico', 'alto', 'medio', 'bajo')),
    boletin_asignado  UUID REFERENCES boletines(id),
    creado_por        UUID REFERENCES usuarios(id),
    fecha_creacion    TIMESTAMP DEFAULT NOW()
);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_incidentes_pais ON incidentes(pais);
CREATE INDEX idx_incidentes_patogeno ON incidentes(patogeno);
CREATE INDEX idx_incidentes_riesgo ON incidentes(riesgo);
CREATE INDEX idx_incidentes_fecha ON incidentes(fecha_inicio);
CREATE INDEX idx_incidentes_estado_verificacion ON incidentes(estado_verificacion);
CREATE INDEX idx_incidentes_estado_editorial ON incidentes(estado_editorial);
CREATE INDEX idx_incidentes_boletin ON incidentes(boletin_asignado);
```

### prompts

```sql
CREATE TABLE prompts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(255) NOT NULL,
    descripcion     TEXT,
    template        TEXT NOT NULL,
    tipo            VARCHAR(30) NOT NULL CHECK (tipo IN ('consulta_incidentes', 'redaccion_articulo', 'otro')),
    activo          BOOLEAN DEFAULT TRUE,
    configuracion   JSONB DEFAULT '{}',
    creado_por      UUID REFERENCES usuarios(id),
    fecha_creacion  TIMESTAMP DEFAULT NOW()
);
```

### auspiciantes

```sql
CREATE TABLE auspiciantes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      VARCHAR(255) NOT NULL,
    logo_url    VARCHAR(1000),
    enlace      VARCHAR(1000),
    descripcion TEXT,
    activo      BOOLEAN DEFAULT TRUE
);
```

### boletin_auspiciantes (pivote)

```sql
CREATE TABLE boletin_auspiciantes (
    boletin_id      UUID REFERENCES boletines(id) ON DELETE CASCADE,
    auspiciante_id  UUID REFERENCES auspiciantes(id) ON DELETE CASCADE,
    PRIMARY KEY (boletin_id, auspiciante_id)
);
```

### log_auditoria

```sql
CREATE TABLE log_auditoria (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id    UUID REFERENCES usuarios(id),
    accion        VARCHAR(100) NOT NULL,
    entidad_tipo  VARCHAR(50) NOT NULL,
    entidad_id    UUID,
    detalles      JSONB DEFAULT '{}',
    fecha         TIMESTAMP DEFAULT NOW(),
    ip            VARCHAR(45)
);

-- Índice para consultas por fecha
CREATE INDEX idx_log_auditoria_fecha ON log_auditoria(fecha);
CREATE INDEX idx_log_auditoria_usuario ON log_auditoria(usuario_id);
```

## Índices compuestos

```sql
-- Buscar incidentes por país y rango de fechas
CREATE INDEX idx_incidentes_pais_fecha ON incidentes(pais, fecha_inicio);

-- Buscar incidentes por boletín y estado editorial
CREATE INDEX idx_incidentes_boletin_estado_editorial ON incidentes(boletin_asignado, estado_editorial);

-- Buscar notas por estado y colaborador
CREATE INDEX idx_notas_estado_colaborador ON notas_colaboradores(estado, colaborador_id);

-- Buscar secciones de un boletín en orden
CREATE INDEX idx_secciones_boletin_orden ON secciones(boletin_id, orden);
```

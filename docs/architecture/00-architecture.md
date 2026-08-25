# Arquitectura General — NIA

## Visión del sistema

NIA es una aplicación web con arquitectura **cliente-servidor** separada:

```
┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR                             │
│              SvelteKit (SSR + Client)                    │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Edición    │  │  Gestión    │  │  Panel de       │  │
│  │  Boletín    │  │  Notas      │  │  Incidentes     │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (JSON)
                         │ Cookie-based auth
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    SERVIDOR                              │
│              FastAPI + SQLModel                          │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Auth     │  │ Boletín  │  │ Notas    │  │ IA      │ │
│  │ Module   │  │ Module   │  │ Module   │  │ Module  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────────┐│
│  │              SQLModel ORM                            ││
│  └──────────────────────────────────────────────────────┘│
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL (AWS RDS public image)           │
└─────────────────────────────────────────────────────────┘
```

## Stack tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| **Frontend** | SvelteKit | Última estable |
| **Backend** | FastAPI | Última estable |
| **ORM** | SQLModel | Última estable |
| **Base de datos** | PostgreSQL | 16+ |
| **Auth** | JWT + Refresh Token | — |
| **Contenedores** | Podman | Última estable |
| **Imágenes base** | AWS ECR Public | — |

## Principios arquitectónicos

### 1. Separación clara frontend/backend

- SvelteKit maneja **SSR para la interfaz** y **CSR para interactividad**.
- FastAPI expone **únicamente API REST** (JSON).
- No hay lógica de negocio en el frontend; el frontend es un consumidor de la API.

### 2. Autenticación basada en cookies

- JWT se envía en **httpOnly cookie** (no en headers Authorization).
- Refresh token en cookie separada con mayor duración.
- El frontend nunca lee ni almacena tokens en localStorage.

### 3. Backend stateless

- El servidor no guarda estado de sesión en memoria.
- Todo estado relevante está en la base de datos o en las cookies firmadas.
- Escalable horizontalmente sin sticky sessions.

### 4. Módulos del backend

```
backend/
├── app/
│   ├── main.py              # Entrada FastAPI
│   ├── config.py            # Settings y variables de entorno
│   ├── database.py          # Conexión y sesiones SQLModel
│   ├── models/              # Modelos SQLModel (entidades)
│   │   ├── usuario.py
│   │   ├── boletin.py
│   │   ├── seccion.py
│   │   ├── nota.py
│   │   ├── incidente.py
│   │   ├── prompt.py
│   │   └── auspiciante.py
│   ├── schemas/             # Pydantic schemas (request/response)
│   │   ├── auth.py
│   │   ├── boletin.py
│   │   └── ...
│   ├── routers/             # Endpoints agrupados por dominio
│   │   ├── auth.py
│   │   ├── boletines.py
│   │   ├── secciones.py
│   │   ├── notas.py
│   │   ├── incidentes.py
│   │   ├── prompts.py
│   │   └── auspiciantes.py
│   ├── services/            # Lógica de negocio
│   │   ├── auth_service.py
│   │   ├── boletin_service.py
│   │   ├── ia_service.py
│   │   └── ...
│   ├── middleware/          # CORS, logging, auditoría
│   └── utils/               # Helpers, constantes
├── alembic/                 # Migraciones de BD
├── tests/
├── Dockerfile               # (Podman compatible)
└── requirements.txt
```

### 5. Estructura del frontend

```
frontend/
├── src/
│   ├── routes/              # SvelteKit file-based routing
│   │   ├── +layout.svelte   # Layout principal (nav, auth check)
│   │   ├── login/           # Login
│   │   ├── dashboard/       # Panel principal
│   │   ├── boletines/
│   │   │   ├── [id]/
│   │   │   │   ├── editorial/
│   │   │   │   ├── incidentes/
│   │   │   │   ├── notas/
│   │   │   │   └── ...
│   │   │   └── nueva/
│   │   ├── notas/
│   │   └── admin/           # Solo director
│   ├── lib/
│   │   ├── api/             # Cliente API (fetch wrapper)
│   │   ├── components/      # Componentes Svelte reutilizables
│   │   ├── stores/          # Stores de Svelte (estado global)
│   │   └── utils/           # Helpers
│   └── app.html
├── static/
├── svelte.config.js
├── vite.config.ts
└── package.json
```

## Flujo de datos del pipeline de incidentes

```
1. Editor selecciona período
        │
        ▼
2. Frontend llama POST /api/incidentes/consultar
   { periodo_inicio, periodo_fin }
        │
        ▼
3. Backend ejecuta prompt predefinido contra API de IA
        │
        ▼
4. IA responde JSON con array de incidentes
        │
        ▼
5. Backend almacena incidentes en PostgreSQL
        │
        ▼
6. Frontend muestra tabla editable de incidentes
        │
        ▼
7. Editor corrige/elimina registros
        │
        ▼
8. Frontend llama POST /api/incidentes/{boletin_id}/generar-articulo
        │
        ▼
9. Backend construye prompt de redacción con datos de la tabla
        │
        ▼
10. IA genera artículo en markdown
        │
        ▼
11. Backend almacena artículo en seccion.contenido
        │
        ▼
12. Frontend muestra markdown para edición del editor
        │
        ▼
13. Editor guarda versión final
        │
        ▼
14. Artículo listo para compilación del boletín
```

## Decisiones técnicas clave

| Decisión | Elección | Motivación |
|----------|----------|------------|
| ORM | SQLModel | Combina Pydantic + SQLAlchemy en un solo modelo. Nativo de FastAPI. |
| Auth | JWT en cookies httpOnly | Más seguro que localStorage. Protege contra XSS. |
| Refresh token | Obligatorio | Sesiones largas sin comprometer seguridad. Access token corto (15 min). |
| API | REST | Contrato claro, herramientas de testing, fácil de documentar con OpenAPI. |
| Contenedores | Podman | Daemonless, rootless, compatible con Dockerfile. Imágenes AWS ECR Public. |
| Frontend SSR | SvelteKit | SEO, carga inicial rápida, hidratación para interactividad. |

## Dependencias externas

| Servicio | Uso | Configuración |
|----------|-----|---------------|
| API de IA (OpenAI/Anthropic) | Generación de datos y artículos | Variable de entorno `IA_API_KEY` |
| PostgreSQL | Persistencia | Variable de entorno `DATABASE_URL` |
| AWS ECR Public | Imágenes de contenedores | Acceso público, sin credenciales |
| Almacenamiento de archivos | Notas .pdf/.docx, logos | Local (MVP), S3 compatible (futuro) |

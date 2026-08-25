# Despliegue — NIA

## Estrategia de contenedores

NIA usa **Podman** como runtime de contenedores (daemonless, rootless, compatible con Dockerfile).

### Imágenes base

Se utilizan **imágenes públicas de AWS ECR Public** para evitar dependencia de Docker Hub:

| Servicio | Imagen base | Nota |
|----------|-------------|------|
| **Backend** | `public.ecr.aws/docker/library/python:3.12-slim` | Python latest stable |
| **Frontend** | `public.ecr.aws/docker/library/node:22-slim` | Node LTS |
| **PostgreSQL** | `public.ecr.aws/docker/library/postgres:16` | Última estable |

---

## Arquitectura de despliegue

### Desarrollo local

```
┌─────────────────────────────────────────────┐
│  Podman Compose (dev)                        │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ frontend │  │ backend  │  │ postgres │   │
│  │ :5173    │  │ :8000    │  │ :5432    │   │
│  └──────────┘  └──────────┘  └──────────┘   │
│                                              │
│  Hot reload activado en ambos servicios      │
└─────────────────────────────────────────────┘
```

### Producción

```
┌─────────────────────────────────────────────┐
│  Servidor / VM                               │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  Nginx / Caddy (reverse proxy)       │    │
│  │  - TLS termination                    │    │
│  │  - Static files (frontend build)      │    │
│  │  - Proxy /api → backend:8000          │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ frontend │  │ backend  │  │ postgres │   │
│  │ (build)  │  │ :8000    │  │ :5432    │   │
│  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────┘
```

---

## Estructura de contenedores

### Backend (FastAPI)

```dockerfile
# Dockerfile.backend
FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Puerto
EXPOSE 8000

# Ejecución
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (SvelteKit)

```dockerfile
# Dockerfile.frontend
FROM public.ecr.aws/docker/library/node:22-slim AS builder

WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM public.ecr.aws/docker/library/node:22-slim AS runner
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json .

EXPOSE 5173
CMD ["node", "build"]
```

### PostgreSQL

```dockerfile
# Dockerfile.postgres
FROM public.ecr.aws/docker/library/postgres:16

# Copiar scripts de inicialización
COPY init.sql /docker-entrypoint-initdb.d/

# Variables de entorno
ENV POSTGRES_DB=nia
ENV POSTGRES_USER=nia_user
```

---

## Podman Compose (desarrollo)

```yaml
# compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/app:/app/app
    environment:
      - DATABASE_URL=postgresql://nia_user:nia_pass@postgres:5432/nia
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - IA_API_KEY=${IA_API_KEY}
      - CORS_ORIGINS=http://localhost:5173
    depends_on:
      - postgres

  postgres:
    build:
      context: ./postgres
      dockerfile: Dockerfile.postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=nia
      - POSTGRES_USER=nia_user
      - POSTGRES_PASSWORD=nia_pass

volumes:
  pgdata:
```

---

## Comandos de desarrollo

```bash
# Levantar entorno completo
podman-compose up -d

# Ver logs en tiempo real
podman-compose logs -f

# Detener
podman-compose down

# Reconstruir después de cambios en dependencias
podman-compose up -d --build

# Ejecutar migraciones
podman-compose exec backend alembic upgrade head

# Crear usuario inicial
podman-compose exec backend python -m app.scripts.create_admin

# Acceder a la consola de PostgreSQL
podman-compose exec postgres psql -U nia_user -d nia
```

---

## Migraciones de base de datos

Usar **Alembic** (integrado con SQLModel):

```bash
# Generar migración después de cambiar modelos
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history
```

### Estructura de migraciones

```
backend/
├── alembic/
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_severity_field.py
│   │   └── ...
│   ├── env.py
│   └── script.py.mako
└── alembic.ini
```

---

## Variables de entorno

### .env.example

```bash
# Base de datos
DATABASE_URL=postgresql://nia_user:nia_pass@localhost:5432/nia

# JWT
JWT_SECRET_KEY=generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# IA
IA_PROVIDER=openai
IA_API_KEY=sk-your-key-here
IA_API_BASE_URL=https://api.openai.com/v1
IA_MODEL=gpt-4

# CORS
CORS_ORIGINS=http://localhost:5173

# Archivos
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10

# Entorno
ENVIRONMENT=development
```

---

## Despliegue en producción

### Requisitos del servidor

- Linux (Debian/Ubuntu recomendado)
- Podman + podman-compose instalados
- 4 GB RAM mínimo (8 GB recomendado)
- 40 GB disco
- Puerto 80 y 443 abiertos

### Pasos de despliegue

```bash
# 1. Clonar el repositorio
git clone git@github.com:albertoborella/nia.git
cd nia

# 2. Configurar variables de entorno
cp .env.example .env
nano .env  # configurar valores reales

# 3. Generar secretos
openssl rand -hex 32  # para JWT_SECRET_KEY

# 4. Levantar servicios
podman-compose -f compose.prod.yml up -d

# 5. Ejecutar migraciones
podman-compose exec backend alembic upgrade head

# 6. Crear usuario administrador
podman-compose exec backend python -m app.scripts.create_admin

# 7. Verificar estado
podman-compose ps
podman-compose logs backend --tail 50
```

### Compose de producción (compose.prod.yml)

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
    volumes:
      - uploads:/app/uploads

  postgres:
    image: public.ecr.aws/docker/library/postgres:16
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

  nginx:
    image: public.ecr.aws/docker/library/nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - frontend
      - backend

volumes:
  pgdata:
  uploads:
```

---

## Backup de base de datos

```bash
# Backup manual
podman-compose exec postgres pg_dump -U nia_user nia > backup_$(date +%Y%m%d).sql

# Restaurar
cat backup_20260315.sql | podman-compose exec -T postgres psql -U nia_user -d nia

# Backup automático (cron)
0 2 * * * cd /path/to/nia && podman-compose exec -T postgres pg_dump -U nia_user nia | gzip > /backups/nia_$(date +\%Y\%m\%d).sql.gz
```

---

## Monitoreo básico

```bash
# Estado de contenedores
podman-compose ps

# Logs en tiempo real
podman-compose logs -f --tail 100

# Uso de recursos
podman stats

# Salud del backend
curl http://localhost:8000/health
```

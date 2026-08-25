# Seguridad — NIA

## Modelo de autenticación

### JWT + Cookies httpOnly

```
┌─────────────────────────────────────────────────────┐
│  NAVEGADOR                                           │
│                                                      │
│  Cookie: access_token (httpOnly, secure, samesite)  │
│  Cookie: refresh_token (httpOnly, secure, samesite) │
│                                                      │
│  Nunca se accede a tokens desde JavaScript           │
└────────────────────────┬────────────────────────────┘
                         │
                         │ Request con cookie automática
                         ▼
┌─────────────────────────────────────────────────────┐
│  FastAPI                                             │
│                                                      │
│  1. Extrae access_token de cookie                    │
│  2. Valida JWT (firma, expiración)                   │
│  3. Si expiró → usa refresh_token para renovar       │
│  4. Si refresh inválido → 401                        │
└─────────────────────────────────────────────────────┘
```

### Tokens

| Token | Duración | Almacenamiento | Propósito |
|-------|----------|----------------|-----------|
| `access_token` | 15 minutos | Cookie httpOnly | Acceso a endpoints protegidos |
| `refresh_token` | 7 días | Cookie httpOnly separada | Renovar access_token sin login |

### Configuración de cookies

```
access_token:
  - httpOnly: true      (no accesible desde JS)
  - secure: true         (solo HTTPS)
  - sameSite: lax        (protección CSRF básica)
  - path: /api
  - maxAge: 900          (15 min)

refresh_token:
  - httpOnly: true
  - secure: true
  - sameSite: lax
  - path: /api/v1/auth/refresh
  - maxAge: 604800       (7 días)
```

### Flujo de login

```
1. POST /api/v1/auth/login { email, password }
2. Backend valida credenciales contra bcrypt hash
3. Backend genera access_token (15 min) y refresh_token (7 días)
4. Backend setea ambas cookies en la respuesta
5. Frontend redirige a /dashboard
6. Todas las requests posteriores envían cookies automáticamente
```

### Flujo de refresh

```
1. Frontend detecta 401 en una request
2. Frontend llama POST /api/v1/auth/refresh
3. Backend valida refresh_token de cookie
4. Si válido → genera nuevo access_token, setea cookie, retry original
5. Si inválido → responde 401, frontend redirige a /login
```

---

## Autorización

### Roles

| Rol | Permisos |
|-----|----------|
| `director` | Acceso total: crear boletines, escribir editorial, consultar IA, revisar notas, compilar, administrar prompts y auspiciantes. |
| `colaborador` | Subir notas, ver estado de sus propias notas. No puede: crear boletines, escribir editorial, consultar IA, compilar. |

### Control de acceso por endpoint

| Endpoint | Director | Colaborador | No autenticado |
|----------|----------|-------------|----------------|
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `POST /auth/refresh` | ✅ | ✅ | ✅ (con cookie) |
| `GET /boletines` | ✅ | ❌ | ❌ |
| `POST /boletines` | ✅ | ❌ | ❌ |
| `PUT /boletines/{id}/secciones/editorial` | ✅ | ❌ | ❌ |
| `POST /incidentes/consultar` | ✅ | ❌ | ❌ |
| `POST /incidentes/{id}/generar-articulo` | ✅ | ❌ | ❌ |
| `POST /notas` (subir) | ✅ | ✅ | ❌ |
| `GET /notas` (ver propias) | ✅ | ✅ | ❌ |
| `PUT /notas/{id}/estado` | ✅ | ❌ | ❌ |
| `GET /prompts` | ✅ | ❌ | ❌ |
| `POST /prompts` | ✅ | ❌ | ❌ |

---

## Protección contra vulnerabilidades

### XSS (Cross-Site Scripting)

- JWT en cookie httpOnly: **inaccesible desde JavaScript**.
- SvelteKit escapa automáticamente el output de templates.
- CSP (Content-Security-Policy) en headers de respuesta.
- Nunca renderizar HTML proveniente de inputs del usuario sin sanitizar.

### CSRF (Cross-Side Request Forgery)

- Cookie sameSite: `lax` por defecto.
- Para mutations sensibles (POST/PUT/DELETE): considerar token CSRF en header.
- FastAPI: middleware que valida header `X-Requested-With` o similar.

### SQL Injection

- SQLModel/SQLAlchemy usan **parámetros bind** (nunca concatenación de strings).
- Nunca ejecutar queries raw con interpolación de user input.

### Inyección de prompts (Prompt Injection)

- Los prompts predefinidos están **almacenados en BD**, no en el frontend.
- El backend construye el prompt completo; el frontend solo envía parámetros (fechas).
- Nunca concatenar input del usuario directamente en el prompt de IA.
- Logging de todas las llamadas a IA para auditoría.

### Access Control

- Middleware de autenticación que verifica JWT en cada request protegido.
- Decorador de rol que valida `current_user.rol == 'director'` para endpoints restringidos.
- Los IDs de boletines y notas se validan contra el usuario autenticado.

---

## Seguridad de datos

### Contraseñas

- Hasheadas con **bcrypt** (cost factor 12+).
- Nunca se almacena la contraseña en texto plano.
- Nunca se retorna el hash en responses de API.

### Datos sensibles en logs

- **Nunca** logear: contraseñas, tokens, contenido de JWT, datos de IA sensibles.
- Logear: usuario_id, acción, timestamp, IP (sin datos sensibles).

### Archivos subidos

- Almacenados fuera del directorio público (no accesible directamente por URL).
- Validación de tipo MIME y extensión.
- Límite de tamaño: 10 MB por archivo.
- Names generados con UUID para evitar path traversal.

---

## HTTPS

- Todas las comunicaciones cliente-servidor cifradas con TLS.
- En desarrollo local: certificado auto-firmado o herramienta como `mkcert`.
- HSTS header para forzar HTTPS en producción.

---

## Variables de entorno sensibles

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Conexión a PostgreSQL | `postgresql://user:pass@host:5432/nia` |
| `JWT_SECRET_KEY` | Secret para firmar JWT | (generar con `openssl rand -hex 32`) |
| `JWT_ALGORITHM` | Algoritmo de firma | `HS256` |
| `IA_API_KEY` | API key del proveedor de IA | `sk-...` |
| `IA_API_BASE_URL` | URL base de la API de IA | `https://api.openai.com/v1` |
| `CORS_ORIGINS` | Orígenes permitidos | `http://localhost:5173` |

**Nunca** commitear estas variables al repositorio. Usar `.env` (gitignored) y proveer `.env.example` sin valores reales.

# UC-01: Autenticación y Autorización

## Descripción
El usuario accede al sistema mediante credenciales válidas y obtiene una sesión JWT basada en cookies httpOnly.

## Actor
- **Director**: Acceso completo a todas las funcionalidades.
- **Colaborador**: Acceso limitado a subir notas y ver sus propias notas.

## Precondición
- El usuario tiene credenciales válidas registradas en el sistema.
- El sistema está disponible y la base de datos conectada.

---

## Flujo Principal

1. El usuario navega a `/login`.
2. El sistema muestra el formulario de login con campos `email` y `password`.
3. El usuario ingresa sus credenciales y envía el formulario.
4. El frontend envía `POST /api/v1/auth/login` con `{ "email": "...", "password": "..." }`.
5. El backend valida las credenciales contra el hash bcrypt almacenado.
6. El backend genera un `access_token` (15 min) y un `refresh_token` (7 días).
7. El backend establece ambas cookies httpOnly en la respuesta:
   - `access_token`: `httpOnly=true`, `secure=true`, `sameSite=lax`, `path=/api`, `maxAge=900`
   - `refresh_token`: `httpOnly=true`, `secure=true`, `sameSite=lax`, `path=/api/v1/auth/refresh`, `maxAge=604800`
8. El backend retorna `200` con los datos del usuario: `{ "id", "nombre", "email", "rol" }`.
9. El frontend redirige a `/dashboard`.

---

## Flujos Alternativos

### FA-01: Credenciales inválidas
- **Paso 5**: El backend detecta credenciales incorrectas.
- El backend retorna `401` con `{ "detail": { "code": "INVALID_CREDENTIALS", "message": "Email o contraseña incorrectos" } }`.
- El frontend muestra un mensaje de error en el formulario.

### FA-02: Token de acceso expirado
- En cualquier request autenticada, el backend detecta que `access_token` expiró.
- El backend valida `refresh_token` de la cookie.
- Si `refresh_token` es válido: genera nuevo `access_token`, establece cookie, reintenta la operación original.
- Si `refresh_token` es inválido: retorna `401`, frontend redirige a `/login`.

### FA-03: Cerrar sesión
1. El usuario hace clic en "Cerrar sesión".
2. El frontend envía `POST /api/v1/auth/logout`.
3. El backend elimina las cookies `access_token` y `refresh_token`.
4. El backend retorna `200` con `{ "message": "Logged out" }`.
5. El frontend redirige a `/login`.

### FA-04: Verificar sesión actual
- El frontend llama `GET /api/v1/auth/me` al cargar el layout principal.
- Si retorna `200`: el usuario está autenticado, se muestran datos en el navbar.
- Si retorna `401`: se intenta refresh; si falla, se redirige a `/login`.

---

## Postcondición
- Sesión JWT activa establecida en cookies httpOnly.
- Todas las requests posteriores incluyen cookies automáticamente.
- El usuario es redirigido a `/dashboard` según su rol.

---

## Permisos por Rol

| Acción | Director | Colaborador |
|--------|----------|-------------|
| Login | ✅ | ✅ |
| Refresh token | ✅ | ✅ |
| Ver perfil propio | ✅ | ✅ |
| Logout | ✅ | ✅ |

---

## Endpoint Relacionado
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

> See [01-api-design.md](../architecture/01-api-design.md#autenticación) for full request/response schemas.

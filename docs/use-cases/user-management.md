# UC-09: Gestión de Usuarios

## Descripción
El director administra los usuarios del sistema: crear cuentas, asignar roles, editar detalles y desactivar usuarios.

## Actor
- **Director**: Crear, editar, desactivar usuarios; gestionar roles.

## Precondición
- El usuario está autenticado como Director.

---

## Flujo Principal: Crear Nuevo Usuario

1. El director accede a `/admin/usuarios/nuevo`.
2. El sistema muestra el formulario con campos:
   - `nombre` (string, requerido): Nombre completo del usuario.
   - `email` (string, requerido): Correo electrónico (único para login).
   - `password` (string, requerido): Contraseña inicial (mínimo 8 caracteres).
   - `rol` (enum, requerido): `director` o `colaborador`.
3. El director completa el formulario y envía.
4. El frontend envía `POST /api/v1/usuarios` con:
   ```json
   {
     "nombre": "Juan Pérez",
     "email": "juan@nia.com",
     "password": "contraseña_segura",
     "rol": "colaborador"
   }
   ```
5. El backend:
   - Valida que el email no esté registrado.
   - Hashea la contraseña con bcrypt (cost factor 12+).
   - Crea el usuario con `activo=true`.
   - Registra en log de auditoría.
6. El backend retorna `201` con los datos del usuario (sin password_hash).

---

## Flujo Principal: Listar Usuarios

1. El director accede a `/admin/usuarios`.
2. El frontend envía `GET /api/v1/usuarios`.
3. El backend retorna la lista de usuarios activos con: `id`, `nombre`, `email`, `rol`, `activo`, `fecha_creacion`, `ultimo_acceso`.

---

## Flujo Principal: Editar Usuario

1. El director selecciona un usuario de la lista.
2. El frontend muestra los campos editables: nombre, email, rol.
3. El director modifica los campos necesarios.
4. El frontend envía `PUT /api/v1/usuarios/{id}` con los campos actualizados.
5. El backend actualiza el registro.

---

## Flujos Alternativos

### FA-01: Desactivar Usuario
1. El director selecciona un usuario para desactivar.
2. El frontend muestra confirmación: "¿Estás seguro? El usuario no podrá acceder al sistema."
3. Si confirma, el frontend envía `PUT /api/v1/usuarios/{id}` con `{ "activo": false }`.
4. El backend marca `activo=false`.
5. El usuario desactivado no puede hacer login.

### FA-02: Restablecer Contraseña
1. El director selecciona un usuario.
2. El director hace clic en "Restablecer contraseña".
3. El frontend envía `POST /api/v1/usuarios/{id}/reset-password`.
4. El backend genera una contraseña temporal y la envía por email.
5. El usuario debe cambiar la contraseña en el próximo login.

### FA-03: Cambiar Contraseña Propia
1. El usuario accede a `/perfil/cambiar-contraseña`.
2. El sistema muestra el formulario con campos:
   - `current_password` (string, requerido): Contraseña actual.
   - `new_password` (string, requerido): Nueva contraseña (mínimo 8 caracteres).
3. El usuario completa el formulario y envía.
4. El frontend envía `PUT /api/v1/auth/change-password` con:
   ```json
   {
     "current_password": "contraseña_actual",
     "new_password": "nueva_contraseña"
   }
   ```
5. El backend valida la contraseña actual y actualiza con la nueva.

### FA-04: Ver Actividad de Usuario
1. El director selecciona un usuario.
2. El frontend envía `GET /api/v1/usuarios/{id}/actividad`.
3. El backend retorna el log de auditoría del usuario: acciones realizadas, fechas, IPs.

### FA-05: Cambiar Propio Rol (No permitido)
1. El director intenta cambiar su propio rol.
2. El backend retorna `403` con `{ "detail": { "code": "SELF_ROLE_CHANGE", "message": "No puedes cambiar tu propio rol" } }`.

---

## Postcondición
- Usuario creado con rol asignado y contraseña hasheada.
- Usuario desactivado no puede acceder al sistema.
- Contraseña restablecida enviada por email.
- Cambios registrados en log de auditoría.

---

## Restricciones
- Solo el director puede crear, editar o desactivar usuarios.
- Un usuario no puede cambiar su propio rol.
- La contraseña debe tener mínimo 8 caracteres.
- El email debe ser único en el sistema.

---

## Permisos por Rol

| Acción | Director | Colaborador |
|--------|----------|-------------|
| Crear usuario | ✅ | ❌ |
| Editar usuario | ✅ | ❌ |
| Desactivar usuario | ✅ | ❌ |
| Restablecer contraseña | ✅ | ❌ |
| Cambiar contraseña propia | ✅ | ✅ |
| Ver actividad de usuario | ✅ | ❌ |

---

## Endpoints Relacionados
- `GET /api/v1/usuarios`
- `POST /api/v1/usuarios`
- `GET /api/v1/usuarios/{id}`
- `PUT /api/v1/usuarios/{id}`
- `POST /api/v1/usuarios/{id}/reset-password`
- `GET /api/v1/usuarios/{id}/actividad`
- `PUT /api/v1/auth/change-password`

# UC-03: Sección Editorial

## Descripción
El director escribe y administra el contenido editorial del boletín. La sección editorial es la primera sección que se completa en el orden del boletín.

## Actor
- **Director**: Escribir, editar y guardar el contenido editorial.

## Precondición
- El boletín existe y está en estado `borrador` o `en_progreso`.
- La sección `editorial` está en estado `pendiente` o `en_edicion`.

---

## Flujo Principal: Escribir Editorial

1. El director accede a `/boletines/{id}/editorial`.
2. El frontend envía `GET /api/v1/boletines/{id}/secciones/editorial`.
3. El backend retorna el contenido actual de la sección:
   ```json
   {
     "tipo": "editorial",
     "orden": 1,
     "estado": "pendiente",
     "contenido": { "texto": "" }
   }
   ```
4. El frontend muestra un editor de texto con soporte para formato rico (Markdown).
5. El director escribe el contenido de la editorial.
6. El director guarda el contenido.
7. El frontend envía `PUT /api/v1/boletines/{id}/secciones/editorial` con:
   ```json
   {
     "contenido": {
       "texto": "# Editorial\n\nEn este número abordamos..."
     }
   }
   ```
8. El backend actualiza el contenido y cambia estado de la sección a `en_edicion`.
9. El backend retorna `200` con la sección actualizada.

---

## Flujo Principal: Vista Previa

1. El director solicita vista previa del editorial.
2. El frontend renderiza el markdown del campo `contenido.texto`.
3. El director revisa el formato y contenido.

---

## Flujos Alternativos

### FA-01: Auto-guardado
1. El frontend detecta inactividad de 30 segundos después de la última edición.
2. El frontend envía automáticamente `PUT /api/v1/boletines/{id}/secciones/editorial` con el contenido actual.
3. El backend actualiza la sección.
4. El frontend muestra un indicador "Guardado automático".

### FA-02: Historial de versiones
1. El director solicita ver el historial de cambios.
2. El frontend consulta el historial de versiones de la sección.
3. El sistema muestra las versiones anteriores con: autor, fecha, contenido.
4. El director puede restaurar una versión anterior.

### FA-03: Descartar cambios
1. El director hace clic en "Descartar cambios".
2. El frontend muestra confirmación: "¿Estás seguro? Se perderán los cambios no guardados."
3. Si confirma, el frontend recarga el contenido desde el backend.

### FA-04: Marcar sección como completada
1. El director verifica que el editorial esté completo.
2. El frontend envía `POST /api/v1/boletines/{id}/completar-seccion` con `{ "tipo": "editorial" }`.
3. El backend cambia el estado de la sección a `completada`.
4. El frontend avanza a la siguiente sección (`incidentes`).

---

## Postcondición
- Contenido editorial guardado en la sección.
- Sección marcada como `completada` cuando el director lo aprueba.
- El boletín avanza al siguiente paso del pipeline.

---

## Restricciones
- Solo el director puede editar la sección editorial.
- La sección debe estar en estado `pendiente` o `en_edicion` para编辑ar.
- Una vez completada, la sección es inmutable.

---

## Endpoint Relacionado
- `GET /api/v1/boletines/{id}/secciones/{tipo}`
- `PUT /api/v1/boletines/{id}/secciones/{tipo}`
- `POST /api/v1/boletines/{id}/completar-seccion`

# User Stories — NIA

## Historias del Director Editorial

### HE-01: Crear un nuevo boletín

**Como** director de la editorial,
**Quiero** crear un nuevo boletín indicando nombre y período de cobertura,
**Para que** el sistema me guíe paso a paso para completar todas las secciones.

**Criterios de aceptación:**
- Puedo ingresar nombre, período y fecha estimada de publicación.
- El sistema muestra las 6 secciones en orden con su estado actual.
- La primera sección (Editorial) queda habilitada para edición.

---

### HE-02: Escribir la editorial

**Como** director de la editorial,
**Quiero** tener un área de texto dedicada para escribir la editorial,
**Para que** el boletín tenga la sección inaugural con mi análisis del estado actual.

**Criterios de aceptación:**
- Solo yo puedo acceder y editar esta sección.
- El texto admite formato rico (títulos, negritas, enlaces).
- Puedo guardar borradores y publicar la versión final.
- Cada edición queda registrada con fecha y hora.

---

### HE-03: Consultar incidentes con IA

**Como** director de la editorial,
**Quiero** usar prompts predefinidos para consultar a la IA sobre incidentes de inocuidad en un período,
**Para que** obtenga datos estructurados para generar el artículo principal.

**Criterios de aceptación:**
- Puedo seleccionar el período de consulta.
- La IA responde con un JSON que puedo revisar antes de guardarlo.
- Los datos se almacenan en una tabla que puedo editar.

---

### HE-04: Generar el artículo de incidentes

**Como** director de la editorial,
**Quiero** que el sistema genere un artículo en markdown a partir de los datos de la tabla,
**Para que** tenga un borrador que pueda editar y mejorar antes de publicar.

**Criterios de aceptación:**
- El sistema genera un artículo completo con introducción, desarrollo y cierre.
- El artículo se muestra en formato markdown para edición.
- Puedo modificar cualquier parte del texto generado.
- La versión editada se guarda como la versión final.

---

### HE-05: Revisar notas de colaboradores

**Como** director de la editorial,
**Quiero** revisar las notas subidas por colaboradores y decidir cuáles incluir en el boletín,
**Para que** solo se publiquen artículos aprobados y relevantes.

**Criterios de aceptación:**
- Puedo ver todas las notas pendientes de revisión.
- Puedo descargar el archivo (.pdf o .docx) para revisarlo.
- Puedo cambiar el estado: aprobada o archivada.
- Puedo asignar notas aprobadas al boletín actual.

---

### HE-06: Seleccionar incidentes para la tabla

**Como** director de la editorial,
**Quiero** seleccionar y ordenar los incidentes que aparecen en la tabla destacada,
**Para que** la tabla muestre los casos más relevantes del período.

**Criterios de aceptación:**
- Puedo filtrar la tabla por país, patógeno, riesgo o fecha.
- Puedo seleccionar qué incidentes incluir.
- Puedo definir el orden de aparición.
- La tabla se genera automáticamente en formato markdown.

---

### HE-07: Compilar y cerrar el boletín

**Como** director de la editorial,
**Quiero** compilar todas las secciones en un documento final y cerrar el boletín,
**Para que** quede almacenado como versión inmutable para distribución futura.

**Criterios de aceptación:**
- El sistema genera un documento completo con todas las secciones.
- El índice se genera automáticamente.
- Una vez cerrado, el boletín no se puede editar.
- Puedo exportar el boletín en PDF.

---

## Historias del Colaborador

### HC-01: Subir una nota

**Como** colaborador,
**Quiero** subir un artículo en .pdf o .docx a una carpeta organizada,
**Para que** quede registrado y disponible para revisión del director.

**Criterios de aceptación:**
- Puedo subir archivos .pdf y .docx.
- Puedo indicar autor, tema y fuente del artículo.
- La nota queda en estado "pendiente de revisión".
- La nota se almacena en la carpeta/subcarpeta correspondiente.

---

### HC-02: Ver mis notas

**Como** colaborador,
**Quiero** ver el estado de las notas que he subido,
**Para que** sepa si fueron aprobadas, archivadas o siguen pendientes.

**Criterios de aceptación:**
- Puedo ver una lista de mis notas con su estado actual.
- Puedo filtrar por estado (pendiente, aprobada, archivada).
- Veo la fecha de recepción y el boletín asignado (si aplica).

---

## Resumen de prioridades

| Prioridad | Historias |
|-----------|-----------|
| **MUST** (fase 1) | HE-01, HE-02, HE-03, HE-04, HC-01 |
| **SHOULD** (fase 2) | HE-05, HE-06, HC-02 |
| **SHOULD** (fase 3) | HE-07 |

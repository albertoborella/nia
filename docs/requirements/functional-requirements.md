# Requisitos Funcionales — NIA

## RF-01: Gestión de boletines

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-01.1 | El sistema debe permitir **crear un nuevo boletín** con nombre, período de cobertura y fecha de publicación estimada. | MUST |
| RF-01.2 | El sistema debe **guiar cronológicamente** al editor por cada sección del boletín en el orden definido. | MUST |
| RF-01.3 | El sistema debe permitir **marcar una sección como completada** antes de avanzar a la siguiente. | MUST |
| RF-01.4 | El sistema debe **almacenar boletines completados** como documentos cerrados e inmutables. | MUST |
| RF-01.5 | El sistema debe permitir **crear una nueva edición** a partir de un boletín anterior (copiar estructura, no contenido). | SHOULD |

---

## RF-02: Editorial

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-02.1 | El sistema debe proveer un **área de texto dedicada** para que el director escriba la editorial. | MUST |
| RF-02.2 | El sistema debe **restringir la edición de la editorial** solo al director de la editorial. | MUST |
| RF-02.3 | La editorial debe admitir **formato rico** (títulos, negritas, enlaces). | SHOULD |
| RF-02.4 | El sistema debe registrar **versiones** de la editorial (quién editó, cuándo). | SHOULD |

---

## RF-03: Notas de colaboradores / Artículos de interés

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-03.1 | El sistema debe permitir **subir archivos** en formato `.pdf` y `.docx`. | MUST |
| RF-03.2 | Las notas deben almacenarse en una **estructura de carpetas/subcarpetas** organizada por colaborador o tema. | MUST |
| RF-03.3 | El sistema debe registrar por cada nota: **autor, fecha de recepción, fuente, y estado**. | MUST |
| RF-03.4 | El sistema debe permitir **cambiar el estado** de una nota: pendiente → aprobada / archivada. | MUST |
| RF-03.5 | El sistema debe permitir **asignar una nota aprobada** a un boletín específico. | MUST |
| RF-03.6 | Las notas archivadas deben permanecer **disponibles para publicaciones futuras**. | MUST |
| RF-03.7 | El sistema debe permitir **buscar notas** por autor, tema, fecha o estado. | SHOULD |

---

## RF-04: Artículo de incidentes mundiales

### RF-04A: Generación de datos

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-04A.1 | El sistema debe ofrecer **prompts predefinidos** para consultar a la IA sobre incidentes de inocuidad en un período dado. | MUST |
| RF-04A.2 | La IA debe responder con un **JSON estructurado** según el schema de incidentes definido en BN-04. | MUST |
| RF-04A.3 | Los JSON deben **almacenarse en una tabla** de la base de datos. | MUST |
| RF-04A.4 | El editor debe poder **editar, corregir o eliminar** registros del JSON antes de continuar. | MUST |
| RF-04A.5 | El sistema debe permitir **filtrar y buscar** registros en la tabla de incidentes. | SHOULD |

### RF-04B: Generación del artículo

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-04B.1 | El sistema debe alimentar un **prompt de redacción** con los datos de la tabla para generar el artículo. | MUST |
| RF-04B.2 | El artículo generado debe entregarse en **formato markdown** para edición. | MUST |
| RF-04B.3 | El editor debe poder **modificar libremente** el texto generado por la IA. | MUST |
| RF-04B.4 | El sistema debe **almacenar la versión editada** del artículo. | MUST |
| RF-04B.5 | El sistema debe permitir **transformar el artículo** al formato de publicación. | MUST |

---

## RF-05: Tabla de incidentes destacados

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-05.1 | El sistema debe **generar automáticamente** la tabla a partir de los JSON almacenados. | MUST |
| RF-05.2 | El editor debe poder **seleccionar y ordenar** los incidentes que aparecen en la tabla. | MUST |
| RF-05.3 | La tabla debe mostrarse en formato **markdown/tabla** para inclusión en el boletín. | MUST |

---

## RF-06: Auspiciantes

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-06.1 | El sistema debe permitir **cargar información de auspiciantes**: nombre, logo, enlace. | MUST |
| RF-06.2 | Los auspiciantes deben mostrarse en la sección correspondiente del boletín. | MUST |

---

## RF-07: Índice

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-07.1 | El sistema debe **generar automáticamente** el índice al completar todas las secciones. | MUST |
| RF-07.2 | El índice debe **actualizarse** si se modifica alguna sección. | MUST |

---

## RF-08: Publicación y almacenamiento

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-08.1 | El sistema debe **compilar todas las secciones** en un documento final del boletín. | MUST |
| RF-08.2 | El boletín compilado debe **almacenarse como documento cerrado**. | MUST |
| RF-08.3 | Un boletín cerrado debe ser **inmutable** (solo lectura). | MUST |
| RF-08.4 | El sistema debe permitir **exportar el boletín** en formato PDF. | SHOULD |

---

## RF-09: Autenticación y acceso

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-09.1 | El sistema debe require **autenticación** para acceder. | MUST |
| RF-09.2 | El sistema debe diferenciar **roles**: director editorial y colaborador. | MUST |
| RF-09.3 | El director debe tener **acceso total** a todas las secciones y funciones. | MUST |
| RF-09.4 | Los colaboradores deben tener **acceso limitado** a sus secciones asignadas. | MUST |
| RF-09.5 | Todas las acciones deben quedar **registradas** (log de auditoría). | SHOULD |

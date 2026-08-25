# Modelo de Dominio — NIA

> See [data-model.md](data-model.md) for the SQL schema and table definitions.

## Visión general

NIA es un sistema editorial que produce **boletines informativos** sobre inocuidad alimentaria. Cada boletín se compone de **secciones** que se completan cronológicamente. El corazón del sistema es el pipeline de **incidentes**: datos estructurados provenientes de IA que se transforman en artículos periodísticos.

## Conceptos principales

```
┌─────────────────────────────────────────────────────────┐
│                      BOLETÍN                            │
│  (documento cerrado, inmutable después de publicación)  │
├─────────────────────────────────────────────────────────┤
│  Período de cobertura · Estado · Fecha creación         │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
       ┌───────▼────────┐        ┌────────▼────────┐
       │    SECCIÓN      │        │    SECCIÓN      │
       │  (Editorial)    │        │ (Incidentes)    │
       └─────────────────┘        └────────┬────────┘
                                           │
                                  ┌────────▼────────┐
                                  │   INCIDENTE      │
                                  │ (JSON → Artículo)│
                                  └─────────────────┘
```

## Mapa de relaciones

| Relación | Cardinalidad | Descripción |
|----------|-------------|-------------|
| Boletín → Sección | 1 : N | Un boletín tiene múltiples secciones en orden fijo. |
| Boletín → Incidente | 1 : N | Un boletín puede incluir múltiples incidentes. |
| Incidente → Boletín | N : 1 | Un incidente puede asignarse a un solo boletín (o ninguno si está archivado). |
| Nota de Colaborador → Boletín | N : 1 | Una nota se incluye en un boletín o queda para futuro. |
| Nota de Colaborador → Colaborador | N : 1 | Cada nota pertenece a un colaborador. |
| Sección → Prompt | 1 : N | Una sección puede usar uno o más prompts predefinidos. |
| Boletín → Auspiciante | N : M | Un boletín puede tener múltiples auspiciantes; un auspiciante puede estar en múltiples boletines. |
| Usuario → Boletín | 1 : N | Un usuario puede crear/editar múltiples boletines. |

## Estados del dominio

### Boletín
```
borrador → en_progreso → completado → cerrado
```
- **borrador**: creado, sin secciones completadas.
- **en_progreso**: al menos una sección completada.
- **todas_las_secciones_completadas**: listo para cierre.
- **cerrado**: inmutable, listo para distribución.

### Sección
```
pendiente → en_edicion → completada
```
- **pendiente**: no iniciada.
- **en_edicion**: contenido siendo trabajado.
- **completada**: aprobada, no se edita más.

### Nota de Colaborador
```
pendiente → aprobada | archivada
```
- **pendiente**: recién subida, sin revisar.
- **aprobada**: revisada, incluida en un boletín.
- **archivada**: revisada, disponible para publicaciones futuras.

### Incidente

El incidente tiene **dos dimensiones de estado independientes** que se gestionan por separado:

#### Estado de verificación (calidad de datos)
```
confirmado · en_investigacion · descartado
```
- **confirmado**: datos verificados contra fuentes oficiales.
- **en_investigacion**: pendiente de verificación.
- **descartado**: descartado tras investigación.

#### Estado editorial (flujo de trabajo)
```
generado → revisado → aprobado → incluido
```
- **generado**: JSON recién recibido de la IA.
- **revisado**: editado por el editor.
- **aprobado**: listo para generar artículo.
- **incluido**: artículo generado y publicado en boletín.

## Contextos del dominio

### Contexto Editorial
Gestiona la creación y edición de secciones de contenido: editorial, notas de colaboradores, artículos generados.

**Entidades**: Boletín, Sección, Editorial, Nota de Colaborador, Artículo de Incidentes.

### Contexto de Datos
Gestiona la recopilación y almacenamiento de datos estructurados de incidentes.

**Entidades**: Incidente (JSON), Prompt, Tabla de Incidentes.

### Contexto de Publicación
Gestiona la compilación, cierre y distribución del boletín.

**Entidades**: Boletín (cerrado), Índice, Auspiciante, Formato de Salida.

### Contexto de Acceso
Gestiona usuarios, autenticación y permisos.

**Entidades**: Usuario, Rol, Sesión, Log de Auditoría.

> Each context maps to specific tables in [data-model.md](data-model.md).

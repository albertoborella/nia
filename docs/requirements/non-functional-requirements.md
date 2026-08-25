# Requisitos No Funcionales — NIA

## RNF-01: Rendimiento

| ID | Requisito | Meta |
|----|-----------|------|
| RNF-01.1 | La carga de un boletín existente no debe demorar más de **3 segundos**. | < 3s |
| RNF-01.2 | La generación de artículos por IA no debe bloquear la interfaz; debe mostrar **progreso**. | Feedback visual |
| RNF-01.3 | La subida de archivos (.pdf, .docx) no debe demorar más de **10 segundos** para archivos de hasta 10 MB. | < 10s |

---

## RNF-02: Usabilidad

| ID | Requisito | Descripción |
|----|-----------|-------------|
| RNF-02.1 | **Flujo guiado**: el editor nunca debe preguntarse "qué hago ahora". El sistema muestra claramente el paso actual y el siguiente. | Onboarding integrado |
| RNF-02.2 | **Feedback inmediato**: cada acción (guardar, cambiar estado, generar artículo) debe mostrar confirmación visual. | UX confiable |
| RNF-02.3 | **Responsive**: la interfaz debe funcionar en desktop (1280px+) como mínimo. | Escritorio primero |

---

## RNF-03: Seguridad

| ID | Requisito | Descripción |
|----|-----------|-------------|
| RNF-03.1 | Las credenciales de acceso deben almacenarse **hasheadas** (bcrypt o equivalente). | Seguridad de contraseñas |
| RNF-03.2 | La comunicación entre cliente y servidor debe usar **HTTPS**. | Transporte seguro |
| RNF-03.3 | Las llamadas a la API de IA no deben exponer **credenciales en el cliente**. | Proxy server-side |
| RNF-03.4 | Los archivos subidos deben almacenarse en una ubicación **aislada y con permisos restringidos**. | Aislamiento de datos |

---

## RNF-04: Mantenibilidad

| ID | Requisito | Descripción |
|----|-----------|-------------|
| RNF-04.1 | El código debe seguir **convenciones de naming** consistentes (ver coding-standards). | Consistencia |
| RNF-04.2 | La arquitectura debe permitir **agregar nuevas secciones** al boletín sin modificar el motor de publicación. | Extensibilidad |
| RNF-04.3 | Los prompts de IA deben ser **configurables** sin modificar código fuente. | Separación de configuración |
| RNF-04.4 | El schema de incidentes debe ser **extensible** (nuevos campos sin migraciones destructivas). | Evolución del modelo |

---

## RNF-05: Disponibilidad de datos

| ID | Requisito | Descripción |
|----|-----------|-------------|
| RNF-05.1 | Los boletines completados deben tener **backup** automático. | Respaldo |
| RNF-05.2 | Los archivos subidos (notas de colaboradores) deben tener **copia de seguridad** periódica. | Respaldo |
| RNF-05.3 | La base de datos debe permitir **exportación** de datos en formato estándar (JSON, CSV). | Portabilidad |

---

## RNF-06: Integración con IA

| ID | Requisito | Descripción |
|----|-----------|-------------|
| RNF-06.1 | El sistema debe soportar **múltiples proveedores de IA** (OpenAI, Anthropic, etc.) mediante configuración. | Proveedor agnóstico |
| RNF-06.2 | Las llamadas a la IA deben tener **timeout configurable** y manejo de errores gracefully. | Resiliencia |
| RNF-06.3 | Los prompts predefinidos deben almacenarse como **configuración**, no como código. | Configurabilidad |
| RNF-06.4 | El sistema debe registrar **uso de tokens** por llamada para control de costos. | Observabilidad |

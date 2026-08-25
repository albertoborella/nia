# Alcance — NIA

## Qué es NIA

- Una plataforma editorial **de uso interno** (sito administrativo) para el director editorial y colaboradores.
- Un sistema para producir un boletín informativo periódico sobre inocuidad alimentaria.
- Un asistente IA para la recopilación, organización y síntesis de información científica.

## Qué NO es NIA

- **No es un sitio público**: no tiene sección de lectores externos, registros de usuarios o paywall.
- **No es un reemplazo del análisis humano**: la IA asiste, el humano decide y firma.
- **No es un agregador de noticias automatizado**: cada publicación pasa por control editorial.
- **No es una base de datos de incidentes**: es un sistema editorial que produce un producto periodístico.

## Secciones del boletín

El boletín `Noticias sobre Inocuidad Alimentaria` está conformado por las siguientes secciones:

| Sección | Descripción | Fuente |
| ------- | ----------- | ------ |
| **Editorial** | Artículo escrito por el director de la editorial. Contexto, opinión y análisis del estado actual de la inocuidad. | Redacción humana directa. |
| **Artículo de incidentes mundiales** | Análisis profundo de uno o más incidentes globales de inocuidad alimentaria. Sección principal y de mayor valor del boletín. | Datos obtenidos vía IA + revisión humana. |
| **Notas de colaboradores** | Artículos de interés científico de revistas u organismos mundialmente reconocidos. | Fuentes externas seleccionadas por el equipo. |
| **Incidentes destacados** | Tabla de los incidentes más representativos a nivel mundial sobre inocuidad alimentaria. | Alimentación automática parcial + revisión. |
| **Auspiciantes** | Reconocimiento a los auspiciantes de la publicación. | Carga manual. |
| **Índice** | Índice navegable del boletín completo. | Generado automáticamente. |

## Direccionamiento por fases

El sistema se construye de forma incremental, completando una sección a la vez:

1. **Primera**: Editorial + Artículo de incidentes mundiales (secciones core).
2. **Segunda**: Tabla de incidentes destacados + Notas de colaboradores.
3. **Tercera**: Auspiciantes + Índice + pulido del boletín final.

Cada fase se valida antes de pasar a la siguiente.

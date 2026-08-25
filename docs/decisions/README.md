# Decisions

Registro de Decisiones de Arquitectura (ADR): decisiones importantes, su
contexto, la alternativa elegida y el motivo.

---

## ADRs

| ADR | Decisión | Estado |
|-----|----------|--------|
| [ADR-001](ADR-001-tech-stack.md) | Technology Stack Selection | Accepted |
| [ADR-002](ADR-002-authentication.md) | Authentication Strategy | Accepted |
| [ADR-003](ADR-003-ai-integration.md) | AI Integration Approach | Accepted |
| [ADR-004](ADR-004-document-processing.md) | Document Processing Strategy | Accepted |
| [ADR-005](ADR-005-deployment.md) | Deployment Strategy | Accepted |
| [ADR-006](ADR-006-data-model.md) | Data Modeling Approach | Accepted |

---

## Formato ADR

Cada decisión de arquitectura importante se registra como ADR numerado:

```
ADR-XXX-nombre-breve.md
```

Contenido mínimo:

| Sección | Qué contiene |
| ------- | ------------ |
| Título | Número y nombre de la decisión. |
| Contexto | Problema o situación que motivó la decisión. |
| Decisión | Qué se decidió, concreto y sin ambigüedad. |
| Alternativas | Qué se descartó y por qué. |
| Consecuencias | Impacto positivo y negativo de la decisión. |

## Consejos

- Un ADR se escribe cuando se TOMA la decisión, no después.
- Los ADR son inmutables: si la decisión cambia, se crea un ADR nuevo.


# ADR-003: AI Integration Approach

**Date:** 2026-08-25
**Status:** Accepted
**Deciders:** Alberto Borella

---

## Context

NIA uses AI to assist (not replace) human editorial work in two primary flows:

1. **Incident discovery:** Query an AI API for food safety incidents within a date range, return structured data
2. **Article generation:** Generate markdown articles from curated incident data for editorial review

The system must:
- Keep the human editor in control at every step
- Produce consistent, parseable output for storage in the relational database
- Support multiple AI providers (OpenAI, Anthropic) via configuration
- Log all AI interactions for cost tracking and audit

## Decision

**Predefined prompts stored in DB → structured JSON response → article generation → human editing**

| Component | Design |
|-----------|--------|
| Prompt storage | Database table `prompts` with template, type, and configuration |
| Prompt templates | Variable substitution: `{{periodo_inicio}}`, `{{periodo_fin}}`, `{{incidentes}}` |
| Response parsing | JSON structured output validated against Pydantic schemas |
| Article flow | AI generates markdown → stored in `seccion.contenido` → editor refines |
| Provider abstraction | Backend service layer abstracts OpenAI/Anthropic behind a common interface |
| Logging | Every AI call logged: prompt used, tokens consumed, response summary |

### Incident Query Flow

```
1. Director selects date range
2. Backend fetches active prompt (tipo: consulta_incidentes)
3. Backend substitutes variables: {{periodo_inicio}}, {{periodo_fin}}
4. Backend sends prompt to AI API
5. AI returns JSON array of incidents
6. Backend validates response against IncidentResponse schema
7. Incidents stored in DB for editor review
8. Editor corrects/removes records in editable table
```

### Article Generation Flow

```
1. Director triggers article generation for a bulletin
2. Backend fetches prompt (tipo: redaccion_articulo)
3. Backend substitutes {{incidentes}} with curated incident data
4. AI generates markdown article
5. Article stored in seccion.contenido
6. Director edits markdown in rich text editor
7. Final version saved
```

## Alternatives Considered

### Real-time AI Suggestions (Copilot-style)
- **Pros:** Continuous assistance, faster editing.
- **Cons:** Requires persistent connection, higher token consumption, unpredictable latency, difficult to validate structured output, high API costs for a small team.
- **Verdict:** Rejected — over-engineered for editorial workflows that are batch-oriented, not real-time.

### Fully Automated Generation (No Human Review)
- **Pros:** Minimal human effort, faster publication.
- **Cons:** Unacceptable for food safety content where accuracy is critical. No editorial control. Risk of publishing incorrect or misleading information.
- **Verdict:** Rejected — food safety content demands human oversight.

### Prompt-as-Code (Hardcoded Prompts)
- **Pros:** Simpler implementation, version-controlled with source code.
- **Cons:** Requires code changes to modify prompts, editor cannot tune prompts independently, harder to test variations.
- **Verdict:** Rejected — violates RNF-04.3 (prompts configurable without code changes).

## Consequences

**Positive:**
- Human editor retains full control: AI drafts, human refines
- Database-stored prompts are independently tunable without code deploys
- Structured JSON responses integrate cleanly with the relational data model
- Provider-agnostic design: swap OpenAI for Anthropic by changing configuration
- Token consumption logging enables cost monitoring

**Negative:**
- Prompt management adds a new admin feature (prompts CRUD with test capability)
- JSON parsing from AI can fail on malformed responses; requires robust error handling
- Template variable substitution must be sandboxed (no user input directly in prompts — security concern)
- AI output quality varies; editor must review every generated article

**Mitigations:**
- Pydantic validation catches malformed AI responses; prompt test endpoint validates before production use
- Prompts stored server-side only; frontend sends parameters, never raw prompt text
- Fallback: editor can write articles manually if AI is unavailable

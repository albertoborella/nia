# Prompt Guide — NIA

## Design Principle

AI assists human editorial work. Prompts generate **drafts and structured data** that humans review, edit, and approve before publication. No AI output goes directly to the final newsletter.

## Prompt Types

### 1. Incident Query (`consulta_incidentes`)

Collects structured food safety incidents for a time period.

**Template variables:**
- `{{periodo_inicio}}` — Start date (YYYY-MM-DD)
- `{{periodo_fin}}` — End date (YYYY-MM-DD)

**Required JSON response format:**
```json
{
  "incidentes": [
    {
      "incidente": "string — brief description",
      "producto": "string — affected food product",
      "patogeno": "string — causative agent (bacteria/virus/parasite/chemical)",
      "organismo": "string — company or organization involved",
      "pais": "string — country where it occurred",
      "riesgo": "alto|medio|bajo",
      "fecha_inicio": "YYYY-MM-DD",
      "fecha_cierre": "YYYY-MM-DD|null",
      "observaciones": "string — additional details",
      "texto_noticia": "string — original source text",
      "fuente_url": "string — source URL (for traceability)",
      "fuente_nombre": "string — source organization/journal name"
    }
  ]
}
```

**Quality criteria:**
- Every incident MUST include `fuente_url` and `fuente_nombre` for traceability
- Risk levels: `alto` (immediate health threat), `medio` (contained outbreak), `bajo` (low impact)
- Dates must be real, verifiable dates (not placeholders)
- Pathogen names should use scientific nomenclature where possible

### 2. Article Generation (`redaccion_articulo`)

Generates a Markdown article from structured incident data.

**Input:** Table of reviewed incidents from the DB.

**Output format:** Markdown with:
- Title (`# Incidents of Food Safety — [Period]`)
- Introduction paragraph
- Each incident as a subsection with structured analysis
- Source citations inline
- Conclusion/summary

**Quality criteria:**
- Written in Spanish (matching newsletter language)
- Professional scientific tone, not sensationalist
- Every claim must reference a source
- No invented data — only use provided incident records

## Prompt Management Rules

| Rule | Detail |
|------|--------|
| Storage | Prompts stored in DB, never hardcoded in frontend |
| Versioning | Each prompt has a version; changes are logged |
| Testing | Use `POST /api/v1/prompts/{id}/test` before activating |
| Access | Only `director` role can create/edit prompts |
| Security | User input NEVER concatenated directly into prompts (prompt injection prevention) |

## AI Integration Boundaries

**AI DOES:**
- Collect and structure incident data from multiple sources
- Generate article drafts in Markdown
- Summarize and synthesize information

**AI DOES NOT:**
- Make editorial decisions
- Publish content without human review
- Access user credentials or sensitive data
- Replace human judgment on severity, risk, or relevance

## Token & Cost Control

- Each prompt config includes `max_tokens` and `temperature`
- Log token usage per call (`tokens_consumidos` in API response)
- Set timeout per provider (default 30s, configurable)

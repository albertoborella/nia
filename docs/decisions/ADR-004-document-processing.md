# ADR-004: Document Processing Strategy

**Date:** 2026-08-25
**Status:** Accepted
**Deciders:** Alberto Borella

---

## Context

NIA receives contributor notes (articles) in PDF and DOCX format. These are uploaded by collaborators and reviewed by the director. The system needs to:

- Store uploaded documents safely
- Track metadata (title, author, source, topic, status)
- Allow download for manual review
- Assign notes to specific bulletins

The notes are not parsed for content extraction at this stage — they are treated as reference documents that the director reviews externally.

## Decision

**Treat all notes as external documents: extract metadata on upload, store file references, serve as downloadable files**

| Aspect | Design |
|--------|--------|
| File storage | Local filesystem (`./uploads/`) outside public directory; S3-compatible storage planned for future |
| File naming | UUID-based names to prevent path traversal and collisions |
| Accepted formats | `.pdf` and `.docx` only (validated by MIME type + extension) |
| Max file size | 10 MB |
| Metadata | Extracted from upload form: title, author, source, topic |
| Search | By metadata fields (title, author, topic, status) — not by file content |
| Download | Binary file served through authenticated endpoint |

### Upload Flow

```
1. User fills form: title, author, source, topic
2. User selects .pdf or .docx file (max 10 MB)
3. Frontend sends POST /api/v1/notas as multipart/form-data
4. Backend validates MIME type and extension
5. Backend validates file size
6. Backend generates UUID-based filename
7. Backend stores file in ./uploads/ (outside public dir)
8. Backend creates nota record with estado=pendiente
9. Backend logs to audit table
```

## Alternatives Considered

### Convert to Internal Format (Markdown/HTML)
- **Pros:** Unified content format, easier search and indexing, consistent rendering.
- **Cons:** Loss of original formatting (tables, images, fonts), conversion errors for complex PDFs, DOCX-to-markdown converters are unreliable, original authors may need to reference their submitted format.
- **Verdict:** Rejected — preserving original format is more valuable than unified internal format for this use case.

### OCR for Scanned Documents
- **Pros:** Makes scanned PDFs searchable and extractable.
- **Cons:** Adds dependency on OCR service (Tesseract or cloud API), significant processing time, accuracy varies by document quality, not needed for MVP since most submissions are native digital documents.
- **Verdict:** Deferred — may revisit if scanned submissions become common.

### Direct Content Extraction (PDF/DOCX Parsing)
- **Pros:** Full text search, automated content analysis.
- **Cons:** PDF extraction is fragile (layout-dependent), DOCX parsing requires python-docx maintenance, extracted text loses structure, adds significant complexity for minimal benefit in an editorial review workflow.
- **Verdict:** Rejected — over-engineered for the current use case.

## Consequences

**Positive:**
- Original document format is always preserved — no conversion fidelity loss
- Simple implementation: file storage + metadata table, no parsing libraries
- UUID-based filenames prevent path traversal and file name collisions
- Metadata-based search covers the primary use case (find notes by topic/author)
- File isolation from public directory prevents direct URL access

**Negative:**
- No full-text search within documents — director must download to review content
- File storage on local filesystem doesn't scale horizontally (needs shared storage in multi-server deployment)
- No automated content extraction for future AI-assisted features
- PDF/DOCX files require manual backup strategy separate from database backups

**Mitigations:**
- Future: migrate file storage to S3-compatible service for horizontal scaling
- Future: add optional content extraction as a background job if search-within-documents becomes a requirement
- Backup script covers both database and uploads directory

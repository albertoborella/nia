# Pages — NIA

Screen definitions, navigation routing, and empty/error states for every page in the application.

---

## Login — `/login`

**Route**: `/login`
**Auth required**: No (redirects to `/dashboard` if already authenticated)
**Layout**: Minimal (no sidebar, no header)

### Purpose

Authenticate the user via email and password.

### Fields

| Field | Type | Validation |
|-------|------|------------|
| Email | `<input type="email">` | Required, valid email format |
| Password | `<input type="password">` | Required, min 8 characters |

### Behavior

- Submit calls `POST /api/v1/auth/login`. See [01-api-design.md](../architecture/01-api-design.md#autenticación).
- On success: redirect to `returnUrl` query param or `/dashboard`.
- On failure: inline error message below form, password field cleared.
- "Forgot password" link placeholder (not implemented in MVP).

### Layout

```
┌─────────────────────────────────┐
│                                 │
│         [NIA Logo]              │
│    Noticias Inocuidad           │
│        Alimentaria              │
│                                 │
│  ┌───────────────────────────┐  │
│  │ Email                     │  │
│  ├───────────────────────────┤  │
│  │ Password                  │  │
│  ├───────────────────────────┤  │
│  │       [Sign In]           │  │
│  └───────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

---

## Dashboard — `/dashboard`

**Route**: `/dashboard`
**Auth required**: Yes
**Role**: Director only (collaborators redirected to `/notas`)

### Purpose

Overview of all bulletins and recent activity.

### Sections

#### Active Bulletins

Table of bulletins in `borrador` or `en_progreso` state. See [01-api-design.md](../architecture/01-api-design.md#boletines) for endpoint details.

| Column | Description |
|--------|-------------|
| Name | Bulletin name (e.g., "Edicion Marzo 2026") |
| Period | `periodo_inicio` – `periodo_fin` |
| Status | Badge: `borrador` (gray), `en_progreso` (blue), `completado` (green) |
| Progress | Visual indicator: `secciones_completadas` / `secciones_total` |
| Last Updated | `fecha_creacion` or last section edit |

Row click → navigate to bulletin detail (`/boletines/[id]`).

#### Quick Actions

- "New Bulletin" button → opens create bulletin modal.
- "Query AI for Incidents" button → navigates to `/incidentes` with date picker.

#### Recent Activity

Last 10 audit log entries relevant to the director.

| Item | Display |
|------|---------|
| Action icon | Color-coded by type (create, edit, approve) |
| Description | "{user} {action} {entity}" |
| Timestamp | Relative time (e.g., "2 hours ago") |

#### Stats Cards (top row)

| Card | Value | Description |
|------|-------|-------------|
| Active Bulletins | Count | Bulletins not yet closed |
| Pending Notes | Count | Notes in `pendiente` state |
| Incidents This Period | Count | Incidents for current month |
| Avg. Completion Time | Duration | Average days from creation to closure |

### Empty State

```
┌─────────────────────────────────────────┐
│                                         │
│     [Illustration: empty inbox]         │
│                                         │
│     No bulletins yet                    │
│     Create your first bulletin to       │
│     get started.                        │
│                                         │
│     [Create Bulletin]                   │
│                                         │
└─────────────────────────────────────────┘
```

---

## Bulletin List — `/boletines`

**Route**: `/boletines`
**Auth required**: Yes
**Role**: Director

### Purpose

List all bulletins with filtering and search.

### Header

- Title: "Bulletins"
- "New Bulletin" button (opens create modal)
- Filter bar: Status dropdown (All, Borrador, En Progreso, Completado, Cerrado)

### Table

| Column | Description |
|--------|-------------|
| Name | Bulletin name, clickable |
| Period | Date range |
| Status | Badge |
| Sections | Progress bar |
| Created | Date |
| Actions | Dropdown: Edit, Duplicate, Close (if all sections complete) |

### Pagination

20 items per page. Page controls at bottom.

---

## Bulletin Detail — `/boletines/[id]`

**Route**: `/boletines/[id]`
**Auth required**: Yes
**Role**: Director

### Purpose

Edit a specific bulletin. Shows section progress and provides access to each section editor.

### Header

- Back arrow → `/boletines`
- Bulletin name (editable inline)
- Status badge
- Period display
- "Compile" button (enabled only when all sections are `completada`)
- "Export" dropdown (PDF, Markdown)

### Section Navigator

Horizontal tab bar showing all 6 sections with status indicators:

```
[1. Editorial ✓] [2. Incidents ✓] [3. Notes ○] [4. Table ○] [5. Sponsors ○] [6. Index ○]
```

| Status | Icon | Meaning |
|--------|------|---------|
| `pendiente` | Gray circle | Not started |
| `en_edicion` | Blue circle (pulsing) | Currently being edited |
| `completada` | Green checkmark | Done, locked |

Click on a section tab → navigates to the section editor below the tab bar.

### Section Content Area

The active section editor renders here. See section editors below.

### Bulletin Metadata Sidebar (right, collapsible)

- Created by
- Created at
- Last modified
- Estimated publication date
- Sections summary (list with status)

---

## Editorial Editor — `/boletines/[id]/editorial`

**Section**: Editorial (order: 1)

### Purpose

Write the editorial introduction for the bulletin.

### Editor

- Rich text editor (Markdown-based with toolbar).
- Toolbar: Bold, Italic, Heading (H2, H3), Link, Quote, List (ordered/unordered).
- Split view toggle: Edit | Preview side-by-side.
- Auto-save every 30 seconds (visual indicator).
- Manual save: "Save" button (Cmd+S shortcut).
- "Mark as Complete" button (opens confirmation dialog).

### Toolbar Actions

| Action | Description |
|--------|-------------|
| Save | Persist current content via `PUT /api/v1/boletines/{id}/secciones/editorial`. See [01-api-design.md](../architecture/01-api-design.md#secciones). |
| Mark Complete | Calls `POST /api/v1/boletines/{id}/completar-seccion` with `tipo: "editorial"` |
| Version History | Opens sidebar with previous versions (future) |

### Empty State

```
Start writing the editorial for this edition.

This section is the opening piece of the bulletin. Write about
the current state of food safety and what readers can expect
in this edition.

[Begin Writing]
```

### Constraints

- Only the director can edit this section.
- Cannot mark as complete if content is empty (< 10 characters).
- Once marked complete, editing is locked unless reopened (director action).

---

## Global Incidents Editor — `/boletines/[id]/incidentes`

**Section**: Global Incidents Article (order: 2)

### Purpose

Generate and edit the AI-written article about global food safety incidents.

### Workflow

> For endpoint schemas, see [01-api-design.md](../architecture/01-api-design.md#incidentes).

```
1. Select date range for query
2. Click "Query AI" → POST /api/v1/incidentes/consultar
3. AI returns structured incident data
4. Review incidents in editable table
5. Click "Generate Article" → POST /api/v1/incidentes/{id}/generar-articulo
6. AI returns markdown article
7. Edit article in markdown editor
8. Save and mark complete
```

### Step 1: Date Range Selection

- Two date pickers: Start Date, End Date.
- Default: first day of current month to today.
- "Query AI" button (disabled until both dates set).

### Step 2: Incident Data Table

After AI query, display results in an editable table:

| Column | Editable | Description |
|--------|----------|-------------|
| Incident | Yes | Brief description |
| Product | Yes | Affected food product |
| Pathogen | Yes | Causal agent |
| Country | Yes | Location |
| Risk | Yes (dropdown) | `alto` / `medio` / `bajo` |
| Severity | Yes (dropdown) | `critico` / `alto` / `medio` / `bajo` |
| Start Date | Yes | Incident start |
| Status | Yes (dropdown) | `confirmado` / `en_investigacion` / `descartado` |
| Source | Read-only | Original source name |
| Actions | — | Edit, Delete row |

Row-level actions: Edit (opens inline edit), Delete (confirmation dialog).

### Step 3: Article Editor

Markdown editor with the same toolbar as editorial. Additional features:

- "Regenerate" button (re-runs article generation with current data).
- Word count display.
- Estimated reading time.

### Empty State

```
Generate the global incidents article.

Select a date range and query the AI to retrieve
structured incident data. You can then review,
edit, and generate a complete article.

[Date Range Picker]
[Query AI for Incidents]
```

---

## Contributor Notes — `/boletines/[id]/notas`

**Section**: Contributor Notes (order: 3)

### Purpose

Select which uploaded notes to include in this bulletin.

### View

Two-panel layout:

**Left panel (available notes)**: Notes with estado `aprobada` not yet assigned to a bulletin.

| Column | Description |
|--------|-------------|
| Title | Note title |
| Author | Author name |
| Topic | Theme tag |
| Received | Date |

Checkbox on each row for selection.

**Right panel (selected notes)**: Notes assigned to this bulletin.

- Drag-and-drop reordering.
- Remove button (unassigns without deleting).
- Order determines appearance in final bulletin.

### Actions

- "Assign Selected" button → calls `PUT /api/v1/boletines/{id}/secciones/notas_colaboradores`
- "Mark as Complete" button

### Empty State (no available notes)

```
No approved notes available for assignment.

Notes must be uploaded and approved before they
can be included in a bulletin.

[View All Notes]
```

---

## Incidents Table Editor — `/boletines/[id]/tabla-incidentes`

**Section**: Incidents Table (order: 4)

### Purpose

Select and order the featured incidents for the summary table.

### View

Full-width table of all incidents stored for this bulletin period.

| Column | Description |
|--------|-------------|
| ☐ | Selection checkbox |
| Incident | Description |
| Product | Affected product |
| Pathogen | Causal agent |
| Country | Location |
| Risk | Colored badge (alto=red, medio=amber, bajo=green) |
| Date | Start date |
| ▲▼ | Drag handle for reordering (only for selected) |

### Filter Bar

- Search by keyword (filters across all text fields).
- Country dropdown (auto-populated from data).
- Risk level multi-select.
- Status filter.

### Actions

- "Add Selected to Table" → adds checked incidents to the ordered list.
- "Remove from Table" → removes from ordered list (keeps in data).
- "Preview Table" → shows markdown table preview.
- "Mark as Complete"

### Empty State

```
No incidents available for this period.

Generate incident data first in the Global Incidents
section (step 2).

[Go to Global Incidents]
```

---

## Sponsors Editor — `/boletines/[id]/auspiciantes`

**Section**: Sponsors (order: 5)

### Purpose

Select sponsors to feature in this bulletin.

### View

Two-column grid:

**Available Sponsors**: All active sponsors not yet assigned.

| Element | Display |
|---------|---------|
| Logo | Thumbnail (64x64) |
| Name | Sponsor name |
| Link | External URL (truncated) |
| Checkbox | For selection |

**Selected Sponsors**: Sponsors assigned to this bulletin.

- Order via drag-and-drop.
- Remove button.
- Logo preview at full size on hover.

### Actions

- "Assign Selected" → saves to `PUT /api/v1/boletines/{id}/auspiciantes`. See [01-api-design.md](../architecture/01-api-design.md#auspiciantes-del-boletín).
- "Mark as Complete"

### Empty State

```
No sponsors configured.

Add sponsors in the Admin section before assigning
them to bulletins.

[Manage Sponsors]
```

---

## Index — `/boletines/[id]/indice`

**Section**: Index (order: 6)

### Purpose

Review the auto-generated table of contents.

### View

Read-only display of the index, generated from all completed sections.

```
1. Editorial ........................................ p. 1
2. Global Incidents ................................ p. 3
   2.1 Salmonella Outbreak in Dairy Products ....... p. 3
   2.2 Listeria Contamination in Ready-to-Eat ....... p. 4
3. Contributor Notes ................................ p. 6
   3.1 [Note Title] ................................. p. 6
4. Incidents Table .................................. p. 8
5. Sponsors ......................................... p. 10
```

### Actions

- "Regenerate Index" (if sections changed since last generation).
- "Mark as Complete"
- "Compile Bulletin" → compiles all sections, generates final document.

### Empty State

```
Complete all other sections first.

The index is automatically generated from the
completed sections of the bulletin.

Sections remaining: 4 of 6
```

---

## Notes List — `/notas`

**Route**: `/notas`
**Auth required**: Yes
**Role**: Director (sees all), Collaborator (sees own)

### Purpose

View, filter, and manage all contributor notes.

### Header

- Title: "Notes"
- "Upload Note" button
- Filter bar: Status, Author, Topic, Date range

### Table

> For endpoint schemas, see [01-api-design.md](../architecture/01-api-design.md#notas-de-colaboradores).

| Column | Description |
|--------|-------------|
| Title | Note title, clickable |
| Author | Author name |
| Topic | Theme tag (color-coded) |
| Status | Badge: `pendiente` (yellow), `aprobada` (green), `archivada` (gray) |
| Assigned To | Bulletin name (if assigned) |
| Received | Date |
| Actions | View, Download, Change Status (director only) |

### Note Detail Modal

Opens on row click or "View" action.

| Field | Display |
|-------|---------|
| Title | Full title |
| Author | Author name |
| Source | Origin publication/organization |
| Topic | Theme |
| Status | Current status with change dropdown (director) |
| File | Download link (.pdf / .docx) |
| Assigned Bulletin | Bulletin name or "Unassigned" |
| Review Notes | Director's observations (editable) |
| Received Date | Date |
| Reviewed Date | Date (if reviewed) |

**Director actions**: Change status (approve/archive), assign to bulletin, add review notes.

### Empty State

```
No notes uploaded yet.

Upload articles and documents for review.

[Upload Note]
```

---

## Upload Note — `/notas/nueva`

**Route**: `/notas/nueva`
**Auth required**: Yes
**Role**: Director, Collaborator

### Purpose

Upload a new contributor note.

### Form

| Field | Type | Validation |
|-------|------|------------|
| Title | `<input type="text">` | Required |
| Author | `<input type="text">` | Required |
| Source | `<input type="text">` | Optional |
| Topic | `<select>` | Optional (predefined list) |
| File | `<input type="file">` | Required, .pdf or .docx, max 10MB |

### File Upload

- Drag-and-drop zone with file type icons.
- Click to browse files.
- Shows file name, size, and type after selection.
- Upload progress bar.
- Validation errors inline (wrong type, too large).

### Behavior

- Submit calls `POST /api/v1/notas` (multipart/form-data). See [01-api-design.md](../architecture/01-api-design.md#notas-de-colaboradores).
- On success: redirect to `/notas` with success toast.
- On failure: inline error, form values preserved.

---

## Incidents (Global View) — `/incidentes`

**Route**: `/incidentes`
**Auth required**: Yes
**Role**: Director

### Purpose

View and manage all incidents across all bulletins.

### Header

- Title: "Incidents"
- "New Query" button → opens date range picker modal
- Filter bar: Country, Pathogen, Risk, Status, Date range, Bulletin

### Table

> For endpoint schemas, see [01-api-design.md](../architecture/01-api-design.md#incidentes).

| Column | Description |
|--------|-------------|
| Incident | Description |
| Product | Affected product |
| Pathogen | Causal agent |
| Country | Location |
| Risk | Badge |
| Severity | Badge |
| Date | Start date |
| Status | Badge |
| Bulletin | Assigned bulletin name |
| Actions | Edit, Delete |

### Pagination

20 items per page. Server-side pagination via `?page=1&limit=20`.

### Empty State

```
No incidents recorded.

Query the AI for food safety incidents in a
specific date range to populate this view.

[New Query]
```

---

## Admin — `/admin`

**Route**: `/admin`
**Auth required**: Yes
**Role**: Director only

### Sub-routes

| Route | Purpose |
|-------|---------|
| `/admin/prompts` | Manage AI prompts |
| `/admin/auspiciantes` | Manage sponsors |
| `/admin/users` | Manage users |

---

## Admin > Prompts — `/admin/prompts`

### Purpose

Create and manage predefined AI prompts.

### Table

| Column | Description |
|--------|-------------|
| Name | Prompt name |
| Type | Badge: `consulta_incidentes`, `redaccion_articulo`, `otro` |
| Active | Toggle switch |
| Created By | User name |
| Actions | Edit, Test, Delete |

### Prompt Editor Modal

| Field | Type |
|-------|------|
| Name | Text input |
| Description | Textarea |
| Type | Select |
| Template | Large textarea with syntax highlighting for variables (`{{variable}}`) |
| Temperature | Slider (0–2) |
| Max Tokens | Number input |
| Active | Toggle |

### Test Panel

- Input: date range (for incident prompts) or sample data.
- Output: AI response displayed in formatted JSON/markdown.
- Token usage display.

---

## Admin > Sponsors — `/admin/auspiciantes`

### Purpose

Manage sponsor entities.

### Grid View

Card-based layout:

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  [Logo]     │  │  [Logo]     │  │  [Logo]     │
│  Name       │  │  Name       │  │  Name       │
│  Link       │  │  Link       │  │  Link       │
│  Active ✓   │  │  Active ✓   │  │  Inactive ✗ │
│  [Edit]     │  │  [Edit]     │  │  [Edit]     │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Sponsor Editor Modal

| Field | Type | Validation |
|-------|------|------------|
| Name | Text input | Required |
| Logo | File upload (image) | Required for new, optional for edit |
| Link | URL input | Optional |
| Description | Textarea | Optional |
| Active | Toggle | Default: true |

---

## Admin > Users — `/admin/users`

### Purpose

Manage system users.

### Table

| Column | Description |
|--------|-------------|
| Name | User name |
| Email | Email address |
| Role | Badge: `director` or `colaborador` |
| Active | Status indicator |
| Last Access | Timestamp |
| Actions | Edit, Deactivate |

### User Editor Modal

| Field | Type | Validation |
|-------|------|------------|
| Name | Text input | Required |
| Email | Email input | Required, unique |
| Role | Select (Director, Collaborator) | Required |
| Password | Password input | Required for new, optional for edit |
| Active | Toggle | Default: true |

---

## Settings — `/settings`

**Route**: `/settings`
**Auth required**: Yes
**Role**: All

### Sections

| Section | Fields |
|---------|--------|
| Profile | Name, email (read-only) |
| Appearance | Theme (light/dark), language (future) |
| Notifications | Email notifications toggle (future) |

### Behavior

- Save calls `PUT /api/v1/auth/me` (profile) or updates `localStorage` (appearance). See [01-api-design.md](../architecture/01-api-design.md#autenticación).
- Success toast on save.

---

## Route Summary

| Route | Auth | Role | Parent |
|-------|------|------|--------|
| `/login` | No | — | — |
| `/dashboard` | Yes | Director | — |
| `/boletines` | Yes | Director | — |
| `/boletines/[id]` | Yes | Director | `/boletines` |
| `/boletines/[id]/editorial` | Yes | Director | `/boletines/[id]` |
| `/boletines/[id]/incidentes` | Yes | Director | `/boletines/[id]` |
| `/boletines/[id]/notas` | Yes | Director | `/boletines/[id]` |
| `/boletines/[id]/tabla-incidentes` | Yes | Director | `/boletines/[id]` |
| `/boletines/[id]/auspiciantes` | Yes | Director | `/boletines/[id]` |
| `/boletines/[id]/indice` | Yes | Director | `/boletines/[id]` |
| `/notas` | Yes | All | — |
| `/notas/nueva` | Yes | All | `/notas` |
| `/incidentes` | Yes | Director | — |
| `/admin` | Yes | Director | — |
| `/admin/prompts` | Yes | Director | `/admin` |
| `/admin/auspiciantes` | Yes | Director | `/admin` |
| `/admin/users` | Yes | Director | `/admin` |
| `/settings` | Yes | All | — |

# Components — NIA

Reusable UI components for the NIA admin interface. All components follow the SvelteKit conventions and consume data exclusively from the FastAPI REST API.

---

## Form Components

### RichTextEditor

Markdown-based editor with toolbar for formatted content.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `string` | `''` | Markdown content |
| `placeholder` | `string` | `'Write here...'` | Placeholder text |
| `disabled` | `boolean` | `false` | Read-only mode |
| `minLength` | `number` | `0` | Minimum character count for validation |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `change` | `string` | Content updated |
| `save` | `string` | Manual save triggered |

**Toolbar**: Bold, Italic, H2, H3, Link, Quote, Ordered List, Unordered List.

**Split View**: Toggle between edit-only and side-by-side edit/preview.

**Usage**:

```svelte
<RichTextEditor
  bind:value={editorialContent}
  placeholder="Write the editorial..."
  minLength={10}
  on:save={handleSave}
/>
```

---

### FileUpload

Drag-and-drop file upload with validation.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `accept` | `string[]` | `['.pdf', '.docx']` | Allowed file extensions |
| `maxSize` | `number` | `10485760` | Max file size in bytes (10MB) |
| `disabled` | `boolean` | `false` | Disable upload |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `upload` | `File` | File selected and validated |
| `error` | `{ message: string }` | Validation error |

**States**:

| State | Display |
|-------|---------|
| Empty | Dashed border zone, file type icons, "Drop file or click to browse" |
| Hover | Border color change, background highlight |
| Loading | Progress bar with percentage |
| Success | File name, size, type, remove button |
| Error | Inline error message below zone |

**Usage**:

```svelte
<FileUpload
  accept={['.pdf', '.docx']}
  maxSize={10 * 1024 * 1024}
  on:upload={handleFileUpload}
  on:error={handleUploadError}
/>
```

---

### DateRangePicker

Two connected date pickers for selecting a period.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `start` | `string` | `''` | Start date (YYYY-MM-DD) |
| `end` | `string` | `''` | End date (YYYY-MM-DD) |
| `maxRange` | `number` | `90` | Maximum range in days |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `change` | `{ start: string, end: string }` | Both dates updated |

**Validation**: End date must be after start date. Range must not exceed `maxRange`.

---

### SearchInput

Global search with keyboard shortcut (Cmd+K).

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `string` | `''` | Search query |
| `placeholder` | `string` | `'Search...'` | Placeholder text |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `search` | `string` | Search submitted (on Enter or debounced 300ms) |
| `clear` | — | Search cleared |

**Behavior**: Opens as overlay on Cmd+K. Closes on Escape. Shows recent searches.

---

### FormField

Wrapper for form inputs with label, validation, and help text.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | Required | Field label |
| `error` | `string` | `''` | Validation error message |
| `helpText` | `string` | `''` | Help text below input |
| `required` | `boolean` | `false` | Shows required indicator |

**Slot**: Default slot for the input element.

**Usage**:

```svelte
<FormField label="Email" required error={emailError}>
  <input type="email" bind:value={email} />
</FormField>
```

---

### Select

Dropdown select with search filtering.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `options` | `{ value: string, label: string }[]` | Required | Options list |
| `value` | `string` | `''` | Selected value |
| `placeholder` | `string` | `'Select...'` | Placeholder |
| `searchable` | `boolean` | `false` | Enable type-to-filter |
| `disabled` | `boolean` | `false` | Disabled state |

---

## Data Display Components

### DataTable

Sortable, filterable data table with pagination.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `columns` | `Column[]` | Required | Column definitions |
| `rows` | `any[]` | Required | Data rows |
| `sortable` | `boolean` | `true` | Enable column sorting |
| `selectable` | `boolean` | `false` | Enable row selection (checkboxes) |
| `selected` | `string[]` | `[]` | Selected row IDs |
| `loading` | `boolean` | `false` | Show skeleton rows |
| `emptyMessage` | `string` | `'No data'` | Empty state message |
| `onRowClick` | `(row) => void` | — | Row click handler |

**Column Definition**:

```typescript
interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: any) => string; // custom cell renderer
}
```

**States**:

| State | Display |
|-------|---------|
| Loading | 5 skeleton rows with shimmer effect |
| Empty | Centered illustration + `emptyMessage` + action button |
| Error | Error illustration + retry button |
| Normal | Full table with alternating row colors |

**Pagination**: Server-side. Shows "Showing X–Y of Z" with page controls.

---

### Card

Container for grouped content.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `padding` | `'sm' \| 'md' \| 'lg'` | `'md'` | Inner padding |
| `bordered` | `boolean` | `true` | Show border |
| `hoverable` | `boolean` | `false` | Hover shadow effect |

**Slots**: `header`, default (body), `footer`.

---

### StatusBadge

Colored badge for entity states.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `status` | `string` | Required | Status value |
| `variant` | `'default' \| 'success' \| 'warning' \| 'danger' \| 'info'` | `'default'` | Color variant |

**Status-to-variant mapping**:

| Status | Variant |
|--------|---------|
| `borrador` | `default` |
| `en_progreso` | `info` |
| `completado` | `success` |
| `cerrado` | `default` (muted) |
| `pendiente` | `warning` |
| `en_edicion` | `info` |
| `completada` | `success` |
| `aprobada` | `success` |
| `archivada` | `default` |
| `confirmado` | `success` |
| `en_investigacion` | `warning` |
| `descartado` | `default` |
| `generado` | `default` |
| `revisado` | `info` |
| `aprobado` | `success` |
| `incluido` | `success` |
| `alto` / `critico` | `danger` |
| `medio` | `warning` |
| `bajo` | `success` |

---

### ProgressBar

Visual progress indicator for bulletin sections.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `number` | Required | Current value (0–100) |
| `max` | `number` | `100` | Maximum value |
| `label` | `string` | `''` | Accessible label |
| `showValue` | `boolean` | `false` | Display percentage text |

---

### StatCard

Metric display card for dashboard.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | Required | Metric name |
| `value` | `string \| number` | Required | Metric value |
| `icon` | `string` | `''` | Icon identifier |
| `trend` | `'up' \| 'down' \| 'neutral'` | `'neutral'` | Trend indicator |
| `trendValue` | `string` | `''` | e.g., "+12%" |

---

### EmptyState

Dedicated component for empty list/listing views.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | Required | Primary message |
| `description` | `string` | `''` | Secondary message |
| `icon` | `string` | `''` | Illustration/icon name |
| `actionLabel` | `string` | `''` | Button text |
| `actionHref` | `string` | `''` | Button link (if applicable) |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `action` | — | Action button clicked |

---

## Navigation Components

### Sidebar

Fixed left navigation panel.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `items` | `NavItem[]` | Required | Navigation items |
| `collapsed` | `boolean` | `false` | Collapsed state (icons only) |
| `role` | `'director' \| 'colaborador'` | Required | Determines visible items |

**NavItem**:

```typescript
interface NavItem {
  label: string;
  href: string;
  icon: string;
  badge?: number; // notification count
  children?: NavItem[]; // nested items
}
```

**Director items**:

```
Dashboard (icon: grid)
Bulletins (icon: document)
  └── (children rendered when bulletin selected)
Incidents (icon: alert-triangle)
Notes (icon: file-text)
Admin (icon: settings)
  └── Prompts
  └── Sponsors
  └── Users
Settings (icon: cog)
```

**Collaborator items**:

```
My Notes (icon: file-text)
Upload Note (icon: upload)
Settings (icon: cog)
```

---

### Breadcrumbs

Context-aware breadcrumb trail.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `items` | `{ label: string, href?: string }[]` | Required | Breadcrumb items |

**Example**: Dashboard > Bulletins > Edicion Marzo > Editorial

Last item is always plain text (current page). Previous items are links.

---

### TabBar

Horizontal tab navigation for bulletin sections.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `tabs` | `Tab[]` | Required | Tab definitions |
| `active` | `string` | Required | Active tab key |

**Tab**:

```typescript
interface Tab {
  key: string;
  label: string;
  status: 'pending' | 'editing' | 'completed';
  order: number;
}
```

**Status indicators**: Gray circle (pending), blue pulsing circle (editing), green checkmark (completed).

---

### TopBar

Fixed top header bar.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `user` | `{ name: string, email: string, role: string }` | Required | Current user |
| `theme` | `'light' \| 'dark'` | Required | Current theme |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `toggleTheme` | — | Theme toggle clicked |
| `logout` | — | Logout action |
| `search` | `string` | Search query |

**Layout**: Logo (left) | Search (center) | Theme toggle, User avatar dropdown (right).

---

## Modal / Dialog Components

### Modal

Generic modal dialog.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `open` | `boolean` | `false` | Visibility state |
| `title` | `string` | Required | Modal title |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Width variant |
| `closable` | `boolean` | `true` | Show close button |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `close` | — | Modal dismissed |

**Slots**: `header`, default (body), `footer`.

**Behavior**: Closes on Escape key. Closes on backdrop click (if `closable`). Focus trap inside modal.

---

### ConfirmDialog

Confirmation dialog for destructive actions.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `open` | `boolean` | `false` | Visibility |
| `title` | `string` | `'Confirm'` | Dialog title |
| `message` | `string` | Required | Confirmation message |
| `confirmLabel` | `string` | `'Confirm'` | Confirm button text |
| `cancelLabel` | `string` | `'Cancel'` | Cancel button text |
| `variant` | `'danger' \| 'warning' \| 'default'` | `'default'` | Confirm button color |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `confirm` | — | User confirmed |
| `cancel` | — | User cancelled |

**Usage examples**:

```svelte
<ConfirmDialog
  open={showDeleteConfirm}
  title="Delete Incident"
  message="This action cannot be undone. Are you sure?"
  confirmLabel="Delete"
  variant="danger"
  on:confirm={handleDelete}
  on:cancel={() => showDeleteConfirm = false}
/>
```

---

### Toast

Global notification system.

**Props** (via store, not direct component):

```typescript
interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number; // default: 3000ms
  dismissible?: boolean; // default: true
}
```

**API**:

```typescript
import { toast } from '$lib/stores/toast';

toast.success('Bulletin saved');
toast.error('Failed to save', { duration: 5000 });
toast.warning('AI generation partially completed');
toast.info('Export started');
```

**Behavior**: Bottom-right position. Stack up to 3. Auto-dismiss. Click to dismiss manually.

---

## Layout Components

### PageHeader

Standard page header with title, description, and actions.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | Required | Page title |
| `description` | `string` | `''` | Subtitle/description |

**Slots**: `actions` (right-aligned button group).

---

### SkeletonLoader

Content placeholder during loading.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'text' \| 'circle' \| 'rect' \| 'card' \| 'table-row'` | `'text'` | Shape variant |
| `width` | `string` | `'100%'` | Width |
| `height` | `string` | Depends on variant | Height |

**Usage**:

```svelte
{#if loading}
  <div class="space-y-3">
    {#each Array(5) as _}
      <SkeletonLoader variant="table-row" />
    {/each}
  </div>
{/if}
```

---

### Spinner

Loading indicator for inline use.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Spinner size |
| `label` | `string` | `'Loading...'` | Accessible label |

---

### Alert

Inline alert banner for page-level messages.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `'info' \| 'success' \| 'warning' \| 'error'` | Required | Alert type |
| `title` | `string` | `''` | Bold title |
| `dismissible` | `boolean` | `false` | Show close button |

**Slots**: Default slot for message content.

---

## AI-Specific Components

### AIQueryPanel

Panel for querying AI with date range.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `loading` | `boolean` | `false` | Query in progress |
| `lastQuery` | `{ start: string, end: string } \| null` | `null` | Previous query params |

**Events**:

| Event | Payload | Description |
|-------|---------|-------------|
| `query` | `{ start: string, end: string }` | Query submitted |

**States**:

| State | Display |
|-------|---------|
| Idle | Date pickers + "Query AI" button |
| Loading | Spinner + "Querying AI for incidents..." + elapsed time + "Cancel" button |
| Success | "X incidents found" + "Generate Article" button |
| Error | Error message + "Retry" button |

---

### MarkdownPreview

Rendered markdown display for AI-generated articles.

**Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `content` | `string` | `''` | Markdown content |
| `wordCount` | `boolean` | `false` | Show word count |
| `readingTime` | `boolean` | `false` | Show estimated reading time |

---

## Component File Structure

```
src/lib/components/
├── forms/
│   ├── RichTextEditor.svelte
│   ├── FileUpload.svelte
│   ├── DateRangePicker.svelte
│   ├── SearchInput.svelte
│   ├── FormField.svelte
│   └── Select.svelte
├── data-display/
│   ├── DataTable.svelte
│   ├── Card.svelte
│   ├── StatusBadge.svelte
│   ├── ProgressBar.svelte
│   ├── StatCard.svelte
│   └── EmptyState.svelte
├── navigation/
│   ├── Sidebar.svelte
│   ├── Breadcrumbs.svelte
│   ├── TabBar.svelte
│   └── TopBar.svelte
├── modal/
│   ├── Modal.svelte
│   ├── ConfirmDialog.svelte
│   └── Toast.svelte
├── layout/
│   ├── PageHeader.svelte
│   ├── SkeletonLoader.svelte
│   ├── Spinner.svelte
│   └── Alert.svelte
└── ai/
    ├── AIQueryPanel.svelte
    └── MarkdownPreview.svelte
```

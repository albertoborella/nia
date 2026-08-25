# UI Overview — NIA

NIA is an internal admin interface for producing the **Noticias sobre Inocuidad Alimentaria** newsletter. It is a SvelteKit application that consumes a FastAPI REST API over cookie-based JWT authentication.

## Application Model

```
Browser (SvelteKit SSR + CSR)
        │
        │ REST API (JSON) + httpOnly cookies
        ▼
FastAPI Backend + PostgreSQL
```

- **SSR**: Initial page load, auth redirects, and layout rendering.
- **CSR**: All interactive editing, data tables, and real-time state updates after hydration.
- No business logic lives in the frontend. The UI is a pure consumer of the API.

## Modes

### Dark / Light Mode

| Property | Light | Dark |
|----------|-------|------|
| Default | Yes (initial load) | Toggle available |
| Storage | `localStorage` key `nia-theme` | Persisted across sessions |
| Detection | Manual toggle | Respects `prefers-color-scheme` on first visit |
| Implementation | CSS custom properties on `:root` | Overrides on `:root[data-theme="dark"]` |

The theme toggle is located in the top-right corner of the global header. All components read from CSS custom properties so switching is instantaneous.

### Responsive Breakpoints

| Name | Width | Target |
|------|-------|--------|
| Desktop | >= 1280px | Primary editing experience |
| Tablet | 768px – 1279px | Review and approval workflows |
| Mobile | < 768px | **Not supported** (internal tool, desktop-first) |

The layout collapses the sidebar into a hamburger drawer below 1280px. All editing surfaces remain fully functional on tablet.

## Role-Based Views

The UI adapts based on the authenticated user's `rol` field:

| Capability | Director | Collaborator |
|------------|----------|-------------|
| See Dashboard | Yes | No (redirected to Notes) |
| Create / edit bulletins | Yes | No |
| Write editorial | Yes | No |
| Query AI for incidents | Yes | No |
| Generate incident article | Yes | No |
| Select incidents for table | Yes | No |
| Compile / close bulletin | Yes | No |
| Upload notes | Yes | Yes |
| View own note status | Yes | Yes |
| Access admin section (prompts, sponsors, users) | Yes | No |

Navigation items are conditionally rendered. Routes guarded by role check server-side via `+layout.server.ts` and client-side via Svelte stores.

## Global Layout

```
┌──────────────────────────────────────────────────────────┐
│  Header: Logo · Search · Notifications · Theme · Profile  │
├────────────┬─────────────────────────────────────────────┤
│            │                                             │
│  Sidebar   │            Main Content                     │
│            │                                             │
│  Nav       │  (routed via +page.svelte)                  │
│  items    │                                             │
│            │                                             │
├────────────┴─────────────────────────────────────────────┤
│  Footer: Version · Last sync timestamp                   │
└──────────────────────────────────────────────────────────┘
```

### Header

- Fixed top bar, height `48px`.
- Left: NIA logo + application name.
- Center: Global search (Cmd+K shortcut). Searches bulletins, notes, incidents.
- Right: Theme toggle, notification bell (future), user avatar with dropdown (profile, logout).

### Sidebar

- Fixed left column, width `240px` (collapsed: `64px`).
- Navigation items change by role (see below).
- Active route highlighted with accent color.
- Collapsible on tablet via hamburger icon.

### Main Content

- Fluid area, max-width `1200px`, centered.
- Padding: `24px` all sides.
- Scrollable independently of sidebar.

## Navigation Structure

### Director

```
Dashboard
Bulletins
  └── [Bulletin] ── Editorial
                   └── Global Incidents
                   └── Contributor Notes
                   └── Incidents Table
                   └── Sponsors
                   └── Index
Incidents (global view)
Notes (all)
Admin
  └── Prompts
  └── Sponsors
  └── Users
Settings
```

### Collaborator

```
My Notes
Upload Note
Settings
```

## Loading States

| State | Behavior |
|-------|----------|
| Initial load | Skeleton screen matching target layout |
| Data fetch (list) | Skeleton rows (3–5 placeholder lines) |
| Data fetch (detail) | Skeleton card with shimmer |
| Mutation (save) | Inline spinner on save button, content remains visible |
| AI generation | Progress indicator with elapsed time, cancel button |
| Export | Download progress bar, toast on completion |

## Error States

| State | Behavior |
|-------|----------|
| 401 Unauthorized | Redirect to `/login` with return URL |
| 403 Forbidden | Inline banner: "You don't have permission to access this resource" |
| 404 Not Found | Full-page illustration with "Back to Dashboard" link |
| 500 Server Error | Toast notification with retry option |
| 503 AI Service Unavailable | Banner on incident page: "AI service is temporarily unavailable. Try again later." |
| Network error | Toast with retry, all mutation buttons disabled |

## Empty States

Each major list view has a dedicated empty state:

| View | Empty Message | Action |
|------|--------------|--------|
| Bulletins (none) | "No bulletins yet" | "Create your first bulletin" button |
| Notes (none) | "No notes uploaded" | "Upload a note" button |
| Incidents (none) | "No incidents for this period" | "Query AI for incidents" button |
| Admin > Users | "No users found" | "Invite a user" button |
| Search results | "No results for '{query}'" | Suggestion to refine search |

## Auth Flow

```
1. User visits any route
2. +layout.server.ts checks for access_token cookie
3. If missing/invalid → redirect to /login
4. User submits credentials → POST /api/v1/auth/login
5. Backend sets httpOnly cookies → redirect to /dashboard
6. If access_token expires → frontend detects 401
7. Frontend calls POST /api/v1/auth/refresh (uses refresh_token cookie)
8. If refresh succeeds → retry original request
9. If refresh fails → redirect to /login
```

The frontend never reads or stores JWT tokens. All token handling is automatic via cookies.

## Toast Notifications

Global notification system for non-blocking feedback:

| Type | Duration | Use Case |
|------|----------|----------|
| Success | 3s | Save confirmed, section marked complete |
| Error | 5s (or until dismissed) | API error, validation failure |
| Warning | 4s | AI generation partial failure, approaching token limit |
| Info | 3s | Export started, bulletin compiled |

Position: bottom-right. Stack up to 3 toasts. Dismissible by click.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Open global search |
| `Cmd/Ctrl + S` | Save current form |
| `Cmd/Ctrl + Enter` | Submit / confirm action |
| `Escape` | Close modal / cancel edit |
| `?` | Show keyboard shortcuts help |

## Accessibility

- All interactive elements must be keyboard-navigable.
- Focus ring visible on all focusable elements (2px accent color, 2px offset).
- Color contrast ratio >= 4.5:1 for normal text, >= 3:1 for large text.
- ARIA labels on icon-only buttons.
- Form inputs associated with visible `<label>` elements.
- Error messages linked to inputs via `aria-describedby`.
- Skip-to-content link as first element in DOM.

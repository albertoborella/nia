# Design System — NIA

Visual rules for the NIA admin interface. All components read from CSS custom properties, enabling instant theme switching.

---

## Color Palette

### Primary

The primary palette is professional and trust-oriented, evoking food safety and institutional credibility.

| Token | Light Value | Dark Value | Usage |
|-------|-------------|------------|-------|
| `--color-primary-50` | `#EBF5FF` | `#1A2A3D` | Light background |
| `--color-primary-100` | `#CCE5FF` | `#1E3450` | Hover background |
| `--color-primary-200` | `#99CBFF` | `#2A4A6B` | Borders |
| `--color-primary-300` | `#66B0FF` | `#3A6090` | — |
| `--color-primary-400` | `#3396FF` | `#4A7AB5` | — |
| `--color-primary-500` | `#0070E0` | `#5B90D0` | **Primary actions** |
| `--color-primary-600` | `#005CB8` | `#6BA0E0` | Hover primary |
| `--color-primary-700` | `#004890` | `#7BB0F0` | — |
| `--color-primary-800` | `#003468` | `#8BC0FF` | — |
| `--color-primary-900` | `#002040` | `#9BD0FF` | — |

### Neutral

| Token | Light Value | Dark Value | Usage |
|-------|-------------|------------|-------|
| `--color-neutral-0` | `#FFFFFF` | `#0D1117` | Background |
| `--color-neutral-50` | `#F8F9FA` | `#161B22` | Card background |
| `--color-neutral-100` | `#F0F1F3` | `#1C2128` | Input background |
| `--color-neutral-200` | `#D0D4DA` | `#2D333B` | Borders |
| `--color-neutral-300` | `#AEB5BF` | `#444C56` | Borders (strong) |
| `--color-neutral-400` | `#848D97` | `#6E7681` | Placeholder text |
| `--color-neutral-500` | `#656D76` | `#8B949E` | Secondary text |
| `--color-neutral-600` | `#4D555E` | `#ADBAC7` | Primary text (dark mode) |
| `--color-neutral-700` | `#373E47` | `#C9D1D9` | Primary text |
| `--color-neutral-800` | `#24292F` | `#E6EDF3` | Heading text (dark mode) |
| `--color-neutral-900` | `#1B1F23` | `#F0F6FC` | Heading text |

### Semantic

| Token | Light Value | Dark Value | Usage |
|-------|-------------|------------|-------|
| `--color-success-50` | `#E6FFEC` | `#0D2818` | Success background |
| `--color-success-500` | `#1A7F37` | `#3FB950` | Success text/badge |
| `--color-success-600` | `#116329` | `#56D364` | Success hover |
| `--color-warning-50` | `#FFF8E1` | `#2D1E00` | Warning background |
| `--color-warning-500` | `#BF8700` | `#D29922` | Warning text/badge |
| `--color-warning-600` | `#9A6700` | `#E3B341` | Warning hover |
| `--color-danger-50` | `#FFEBE9` | `#2D0D0D` | Danger background |
| `--color-danger-500` | `#CF222E` | `#F85149` | Danger text/badge |
| `--color-danger-600` | `#A40E26` | `#FF7B72` | Danger hover |
| `--color-info-50` | `#E6F6FF` | `#0C2D4A` | Info background |
| `--color-info-500` | `#0550AE` | `#58A6FF` | Info text/badge |
| `--color-info-600` | `#0349A0` | `#79C0FF` | Info hover |

### Food Safety Theme

Specialized colors for risk and severity indicators.

| Token | Value | Usage |
|-------|-------|-------|
| `--color-risk-high` | `#CF222E` | High risk badge |
| `--color-risk-medium` | `#BF8700` | Medium risk badge |
| `--color-risk-low` | `#1A7F37` | Low risk badge |
| `--color-severity-critical` | `#8B1A1A` | Critical severity (darker red) |
| `--color-severity-high` | `#CF222E` | High severity |
| `--color-severity-medium` | `#BF8700` | Medium severity |
| `--color-severity-low` | `#1A7F37` | Low severity |

---

## Typography

### Font Stack

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
```

Inter is loaded via Google Fonts. Fallback stack ensures readability on all platforms.

### Type Scale

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `--text-xs` | `12px` | `16px` | 400 | Captions, helper text |
| `--text-sm` | `14px` | `20px` | 400 | Secondary text, table cells |
| `--text-base` | `16px` | `24px` | 400 | Body text, form inputs |
| `--text-lg` | `18px` | `28px` | 500 | Card titles, section headers |
| `--text-xl` | `20px` | `28px` | 600 | Page subtitles |
| `--text-2xl` | `24px` | `32px` | 600 | Page titles |
| `--text-3xl` | `30px` | `36px` | 700 | Dashboard stats |
| `--text-4xl` | `36px` | `40px` | 700 | Hero headings (login) |

### Monospace

| Token | Size | Usage |
|-------|------|-------|
| `--text-mono-sm` | `12px` | Code blocks, JSON display |
| `--text-mono-base` | `14px` | Prompt templates, API responses |

---

## Spacing

Base unit: `4px`. All spacing values are multiples of this base.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-0` | `0px` | — |
| `--space-1` | `4px` | Tight spacing (icon gaps) |
| `--space-2` | `8px` | Small gaps (badge padding, inline elements) |
| `--space-3` | `12px` | Form field gaps |
| `--space-4` | `16px` | Card padding (sm), list item gaps |
| `--space-5` | `20px` | — |
| `--space-6` | `24px` | Card padding (md), page margins |
| `--space-8` | `32px` | Section spacing |
| `--space-10` | `40px` | Large section spacing |
| `--space-12` | `48px` | Page header to content |
| `--space-16` | `64px` | Hero spacing (login) |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-none` | `0px` | — |
| `--radius-sm` | `4px` | Badges, small elements |
| `--radius-md` | `6px` | Buttons, inputs, cards |
| `--radius-lg` | `8px` | Modals, large cards |
| `--radius-xl` | `12px` | — |
| `--radius-full` | `9999px` | Avatars, pills |

---

## Shadows

### Light Mode

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |
| `--shadow-md` | `0 2px 8px rgba(0,0,0,0.08)` | Cards, dropdowns |
| `--shadow-lg` | `0 4px 16px rgba(0,0,0,0.12)` | Modals, popovers |
| `--shadow-focus` | `0 0 0 2px var(--color-primary-500)` | Focus ring |

### Dark Mode

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.3)` |
| `--shadow-md` | `0 2px 8px rgba(0,0,0,0.4)` |
| `--shadow-lg` | `0 4px 16px rgba(0,0,0,0.5)` |
| `--shadow-focus` | `0 0 0 2px var(--color-primary-400)` |

---

## Dark Mode Implementation

### Strategy

CSS custom properties on `:root` with overrides on `:root[data-theme="dark"]`.

### Toggle Mechanism

1. On first visit: check `localStorage('nia-theme')`. If absent, check `prefers-color-scheme`.
2. Write `data-theme` attribute to `<html>`.
3. Persist choice to `localStorage`.
4. Toggle flips between `light` and `dark`.

### CSS Structure

```css
:root {
  --color-bg: var(--color-neutral-0);
  --color-text: var(--color-neutral-900);
  /* ... all tokens ... */
}

:root[data-theme="dark"] {
  --color-bg: var(--color-neutral-0); /* dark value */
  --color-text: var(--color-neutral-700); /* light-on-dark value */
  /* ... overrides ... */
}
```

### Component Guidelines

- All components MUST use CSS custom properties, never hardcoded colors.
- Use semantic tokens (`--color-success-500`) not raw hex values.
- Test every new component in both themes before merging.

---

## Component Tokens

### Buttons

| Token | Value |
|-------|-------|
| `--btn-height-sm` | `32px` |
| `--btn-height-md` | `40px` |
| `--btn-height-lg` | `48px` |
| `--btn-padding-sm` | `0 12px` |
| `--btn-padding-md` | `0 16px` |
| `--btn-padding-lg` | `0 24px` |

**Variants**:

| Variant | Background | Text | Border | Hover |
|---------|-----------|------|--------|-------|
| Primary | `--color-primary-500` | white | none | `--color-primary-600` |
| Secondary | transparent | `--color-primary-500` | `--color-primary-500` | `--color-primary-50` bg |
| Danger | `--color-danger-500` | white | none | `--color-danger-600` |
| Ghost | transparent | `--color-neutral-700` | none | `--color-neutral-100` bg |

### Inputs

| Token | Value |
|-------|-------|
| `--input-height` | `40px` |
| `--input-padding` | `0 12px` |
| `--input-border` | `1px solid var(--color-neutral-200)` |
| `--input-radius` | `var(--radius-md)` |
| `--input-focus-ring` | `0 0 0 2px var(--color-primary-200)` |

### Tables

| Token | Value |
|-------|-------|
| `--table-header-bg` | `var(--color-neutral-50)` |
| `--table-row-hover` | `var(--color-neutral-100)` |
| `--table-border` | `1px solid var(--color-neutral-200)` |
| `--table-cell-padding` | `12px 16px` |

---

## Accessibility

### Focus Management

- All interactive elements receive a visible focus ring on keyboard navigation.
- Focus ring: `2px solid var(--color-primary-500)` with `2px` offset.
- Never remove outline without providing an alternative focus indicator.

### Color Contrast

| Element | Minimum Ratio | Standard |
|---------|--------------|----------|
| Normal text (< 18px) | 4.5:1 | WCAG AA |
| Large text (>= 18px bold or >= 24px) | 3:1 | WCAG AA |
| UI components and graphical objects | 3:1 | WCAG AA |

### Motion

- Respect `prefers-reduced-motion: reduce` by disabling non-essential animations.
- Skeleton shimmer, spinner rotation, and toast slide-in are the only animated elements.
- All transitions use `transition-duration: 150ms` or `200ms` (never more than 300ms).

### Semantic HTML

- Use `<nav>`, `<main>`, `<header>`, `<footer>`, `<aside>` for landmarks.
- Use `<h1>`–`<h6>` in hierarchical order (never skip levels).
- Use `<table>` with `<thead>`/`<tbody>` for data tables (never layout tables).
- Use `<label>` associated with every form input.

### ARIA

| Pattern | Usage |
|---------|-------|
| `aria-label` | Icon-only buttons, search input |
| `aria-describedby` | Form error messages, help text |
| `aria-expanded` | Dropdowns, collapsible sections |
| `aria-hidden="true"` | Decorative icons |
| `role="alert"` | Toast notifications |
| `role="dialog"` | Modals |
| `aria-live="polite"` | Dynamic content updates (loading states) |

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `Tab` | Move focus forward |
| `Shift+Tab` | Move focus backward |
| `Enter` / `Space` | Activate button/link |
| `Escape` | Close modal/dropdown |
| `Arrow keys` | Navigate within table rows, tabs, dropdown options |

### Skip Link

First element in DOM: "Skip to main content" link. Visible on focus, hidden otherwise. Jumps to `<main>`.

---

## Responsive Design

### Desktop (>= 1280px)

- Full sidebar (240px) + content area.
- Multi-column layouts where applicable.
- Full table width.

### Tablet (768px – 1279px)

- Collapsed sidebar (64px, icon-only) with hamburger toggle.
- Content area fills remaining width.
- Tables scroll horizontally if needed.
- Modals are full-width with margins.

### Breakpoint Tokens

```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
```

---

## Icons

Use a consistent icon set (e.g., Lucide or Heroicons). Icons are 16px by default, 20px in navigation, 24px in page headers.

| Context | Size |
|---------|------|
| Inline text | 16px |
| Button icon | 16px |
| Navigation item | 20px |
| Page header | 24px |
| Empty state illustration | 48px–64px |

---

## Print Styles

For bulletin export (PDF), the following overrides apply:

- Remove sidebar, header, footer.
- White background, black text.
- No shadows, no borders (except tables).
- Page breaks before each major section.
- Font size: 12pt body, 16pt headings.

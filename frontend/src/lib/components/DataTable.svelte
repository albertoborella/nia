<script lang="ts">
  import type { Snippet } from "svelte";

  interface Column {
    key: string;
    label: string;
    sortable?: boolean;
    width?: string;
    align?: "left" | "center" | "right";
    render?: (row: any, value: any) => string;
  }

  let {
    columns = [],
    rows = [],
    sortable = false,
    loading = false,
    emptyMessage = "No hay datos disponibles",
    onRowClick,
    rowSnippet,
  }: {
    columns?: Column[];
    rows?: any[];
    sortable?: boolean;
    loading?: boolean;
    emptyMessage?: string;
    onRowClick?: (row: any) => void;
    rowSnippet?: Snippet<[any, Column[]]>;
  } = $props();

  let sortKey = $state<string | null>(null);
  let sortDirection = $state<"asc" | "desc">("asc");

  function toggleSort(key: string) {
    if (!sortable) return;
    if (sortKey === key) {
      sortDirection = sortDirection === "asc" ? "desc" : "asc";
    } else {
      sortKey = key;
      sortDirection = "asc";
    }
  }

  let sortedRows = $derived(() => {
    if (!sortKey || !sortable) return rows;
    return [...rows].sort((a, b) => {
      const aVal = a[sortKey!];
      const bVal = b[sortKey!];
      const cmp = String(aVal ?? "").localeCompare(String(bVal ?? ""), "es", { numeric: true });
      return sortDirection === "asc" ? cmp : -cmp;
    });
  });

  function alignClass(align?: string): string {
    if (align === "center") return "text-center";
    if (align === "right") return "text-right";
    return "text-left";
  }
</script>

<div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
  <div class="overflow-x-auto">
    <table class="w-full">
      <thead>
        <tr>
          {#each columns as col (col.key)}
            <th
              class="whitespace-nowrap {alignClass(col.align)} {sortable && col.sortable ? 'cursor-pointer select-none hover:bg-slate-100 dark:hover:bg-slate-800' : ''}"
              style={col.width ? `width: ${col.width}` : undefined}
              onclick={() => col.sortable && toggleSort(col.key)}
            >
              <span class="inline-flex items-center gap-1">
                {col.label}
                {#if sortable && col.sortable && sortKey === col.key}
                  <span class="text-teal-600">
                    {sortDirection === "asc" ? "↑" : "↓"}
                  </span>
                {/if}
              </span>
            </th>
          {/each}
        </tr>
      </thead>

      <tbody>
        {#if loading}
          {#each Array(5) as _, i}
            <tr class="animate-pulse">
              {#each columns as col (col.key)}
                <td>
                  <div class="h-4 bg-slate-100 dark:bg-slate-800 rounded {col.align === 'center' ? 'mx-auto' : ''} {col.align === 'right' ? 'ml-auto' : ''}" style="width: {col.width ?? '70%'}"></div>
                </td>
              {/each}
            </tr>
          {/each}
        {:else if sortedRows().length === 0}
          <tr>
            <td colspan={columns.length} class="text-center py-12 text-sm text-slate-500 dark:text-slate-400">
              {emptyMessage}
            </td>
          </tr>
        {:else}
          {#each sortedRows() as row, i (row.id ?? i)}
            <tr
              class={onRowClick ? 'cursor-pointer' : ''}
              onclick={() => onRowClick?.(row)}
            >
              {#each columns as col (col.key)}
                <td class="{alignClass(col.align)}">
                  {#if col.render}
                    {@html col.render(row, row[col.key])}
                  {:else}
                    {row[col.key] ?? ""}
                  {/if}
                </td>
              {/each}
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>

<script lang="ts">
  import type { Snippet } from "svelte";

  let {
    padding = "md",
    bordered = true,
    hoverable = false,
    header,
    children,
    footer,
  }: {
    padding?: "sm" | "md" | "lg";
    bordered?: boolean;
    hoverable?: boolean;
    header?: Snippet;
    children: Snippet;
    footer?: Snippet;
  } = $props();

  const paddingClasses: Record<string, string> = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };
</script>

<div
  class="bg-white dark:bg-slate-900 rounded-xl shadow-sm {bordered ? 'border border-slate-200 dark:border-slate-700' : ''} {hoverable ? 'hover:shadow-md transition-shadow duration-200' : ''} {paddingClasses[padding]}"
>
  {#if header}
    <div class="pb-4 mb-4 border-b border-slate-100 dark:border-slate-700">
      {@render header()}
    </div>
  {/if}

  <div>
    {@render children()}
  </div>

  {#if footer}
    <div class="pt-4 mt-4 border-t border-slate-100 dark:border-slate-700">
      {@render footer()}
    </div>
  {/if}
</div>

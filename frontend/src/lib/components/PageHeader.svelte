<script lang="ts">
  import type { Snippet } from "svelte";

  let {
    title,
    description,
    actions,
  }: {
    title: string;
    description?: string;
    actions?: Snippet;
  } = $props();
</script>

<div class="flex items-start justify-between gap-4 mb-8">
  <div class="min-w-0">
    <h1 class="text-xl font-semibold text-slate-800 dark:text-slate-100 tracking-tight">{title}</h1>
    {#if description}
      <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">{description}</p>
    {/if}
  </div>

  {#if actions}
    <div class="flex items-center gap-2 shrink-0">
      {@render actions()}
    </div>
  {/if}
</div>

<script lang="ts">
  let {
    title,
    description,
    actionLabel,
    actionHref,
  }: {
    title: string;
    description?: string;
    actionLabel?: string;
    actionHref?: string;
  } = $props();
</script>

<div class="flex flex-col items-center justify-center py-16 px-4">
  <div class="w-14 h-14 rounded-full bg-teal-50 dark:bg-teal-950 flex items-center justify-center mb-4">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7 text-teal-400">
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  </div>

  <h3 class="text-sm font-semibold text-slate-800 dark:text-slate-100">{title}</h3>

  {#if description}
    <p class="mt-1 text-sm text-slate-500 dark:text-slate-400 text-center max-w-xs">{description}</p>
  {/if}

  {#if actionLabel && actionHref}
    <a
      href={actionHref}
      class="mt-5 inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
    >
      {actionLabel}
    </a>
  {/if}
</div>

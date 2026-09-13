<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import SectionSidebar from "$lib/components/SectionSidebar.svelte";

  interface IndiceEntry {
    tipo: string;
    titulo: string;
    pagina: number | null;
    seccion: string;
  }

  let indice = $state<IndiceEntry[]>([]);
  let loading = $state(true);
  let markingComplete = $state(false);
  let completed = $state(false);

  let id = $derived($page.params.id);

  onMount(async () => {
    await loadIndice();
  });

  async function loadIndice() {
    loading = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones/indice`);
      if (res.ok) {
        const data = await res.json();
        indice = (data.items ?? data.indice ?? data ?? []).map((e: Record<string, unknown>) => ({
          tipo: e.tipo ?? "nota",
          titulo: e.titulo ?? "",
          pagina: e.pagina ?? null,
          seccion: e.seccion ?? "",
        }));
      }
    } catch {
      // Show empty state
    } finally {
      loading = false;
    }
  }

  async function markComplete() {
    markingComplete = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones/indice/completar`, {
        method: "POST",
      });
      if (res.ok) {
        completed = true;
        setTimeout(() => goto(`/boletines/${id}`), 1200);
      }
    } catch {
      // Handle error
    } finally {
      markingComplete = false;
    }
  }

  function tipoIcon(tipo: string): string {
    const map: Record<string, string> = {
      nota: "M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z",
      editorial: "M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z",
      articulo: "M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z",
      incidente: "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z",
      auspicante: "M12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2",
    };
    return map[tipo] ?? map.nota;
  }
</script>

<svelte:head>
  <title>Índice - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-6">
    <div class="flex items-center gap-4">
      <a
        href="/boletines/{id}"
        aria-label="Volver al boletín"
        class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </a>
      <div class="flex-1 min-w-0">
        <h1 class="text-xl font-semibold text-slate-800 dark:text-slate-100">Índice</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Índice automático del boletín — solo lectura</p>
      </div>
      <button
        onclick={markComplete}
        disabled={markingComplete || completed}
        class="px-4 py-2 text-sm font-medium rounded-lg transition-colors
          {completed
            ? 'text-teal-700 bg-teal-100'
            : 'text-teal-700 bg-teal-100 hover:bg-teal-200'}"
      >
        {completed ? "Completada ✓" : markingComplete ? "Marcando..." : "Marcar como Completada"}
      </button>
    </div>

    <div class="grid grid-cols-[240px_1fr] gap-6">
      <SectionSidebar activeSection="indice" />
      <div class="space-y-6">

    {#if loading}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-8">
        <div class="space-y-3">
          {#each Array(6) as _}
            <div class="h-8 bg-slate-100 dark:bg-slate-800 rounded animate-pulse"></div>
          {/each}
        </div>
      </div>
    {:else if indice.length === 0}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-12 text-center">
        <div class="w-14 h-14 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto mb-4">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7 text-slate-400 dark:text-slate-500">
            <path d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        </div>
        <p class="text-sm text-slate-500 dark:text-slate-400">El índice se generará automáticamente cuando las secciones tengan contenido.</p>
      </div>
    {:else}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 py-4 border-b border-slate-200 dark:border-slate-700">
          <h2 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">Contenido del Boletín</h2>
        </div>
        <div class="divide-y divide-slate-100 dark:divide-slate-700">
          {#each indice as entry, i (i)}
            <div class="flex items-center gap-4 px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
              <div class="w-8 h-8 rounded-lg bg-teal-50 dark:bg-teal-950 flex items-center justify-center shrink-0">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 text-teal-600 dark:text-teal-300">
                  <path d={tipoIcon(entry.tipo)} />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-800 dark:text-slate-100">{entry.titulo}</p>
                <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{entry.seccion}</p>
              </div>
              {#if entry.pagina !== null}
                <span class="text-xs text-slate-400 dark:text-slate-500 tabular-nums">p. {entry.pagina}</span>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}
      </div>
    </div>
  </div>
</AppLayout>

<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import SectionSidebar from "$lib/components/SectionSidebar.svelte";

  interface Incidente {
    id: string;
    fecha: string;
    tipo: string;
    titulo: string;
    ubicacion: string;
    severidad: string;
    selected: boolean;
  }

  let incidentes = $state<Incidente[]>([]);
  let loading = $state(true);
  let querying = $state(false);
  let dateFrom = $state("");
  let dateTo = $state("");

  let articleContent = $state("");
  let generating = $state(false);
  let showArticle = $state(false);

  let id = $derived($page.params.id);

  onMount(async () => {
    await loadIncidentes();
  });

  async function loadIncidentes() {
    loading = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones/incidentes`);
      if (res.ok) {
        const data = await res.json();
        incidentes = (data.items ?? data ?? []).map((i: Record<string, unknown>) => ({
          id: i.id ?? "",
          fecha: i.fecha ?? "",
          tipo: i.tipo ?? "",
          titulo: i.titulo ?? "",
          ubicacion: i.ubicacion ?? "",
          severidad: i.severidad ?? "baja",
          selected: false,
        }));
      }
    } catch {
      // Show empty state
    } finally {
      loading = false;
    }
  }

  async function queryAI() {
    querying = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones/incidentes/consultar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fecha_desde: dateFrom || undefined,
          fecha_hasta: dateTo || undefined,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        incidentes = (data.items ?? data ?? []).map((i: Record<string, unknown>) => ({
          id: i.id ?? "",
          fecha: i.fecha ?? "",
          tipo: i.tipo ?? "",
          titulo: i.titulo ?? "",
          ubicacion: i.ubicacion ?? "",
          severidad: i.severidad ?? "baja",
          selected: false,
        }));
      }
    } catch {
      // Handle error
    } finally {
      querying = false;
    }
  }

  async function generateArticle() {
    const selectedIds = incidentes.filter((i) => i.selected).map((i) => i.id);
    if (selectedIds.length === 0) return;

    generating = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones/incidentes/generar-articulo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ incidente_ids: selectedIds }),
      });
      if (res.ok) {
        const data = await res.json();
        articleContent = data.content ?? data.articulo ?? "";
        showArticle = true;
      }
    } catch {
      // Handle error
    } finally {
      generating = false;
    }
  }

  async function saveArticle() {
    try {
      await fetch(`/api/v1/boletines/${id}/secciones/incidentes`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ article: articleContent }),
      });
    } catch {
      // Handle error
    }
  }

  function severidadColor(s: string): string {
    const map: Record<string, string> = {
      critica: "bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300",
      alta: "bg-orange-100 dark:bg-orange-950 text-orange-700 dark:text-orange-300",
      media: "bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300",
      baja: "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300",
    };
    return map[s] ?? "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300";
  }

  function formatDate(iso: string): string {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleDateString("es-AR", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    } catch {
      return iso;
    }
  }

  let selectedCount = $derived(incidentes.filter((i) => i.selected).length);
</script>

<svelte:head>
  <title>Incidentes - NIA</title>
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
        <h1 class="text-xl font-semibold text-slate-800 dark:text-slate-100">Incidentes</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Selección y redacción de incidentes para el boletín</p>
      </div>
    </div>

    <div class="grid grid-cols-[240px_1fr] gap-6">
      <SectionSidebar activeSection="incidentes" />

      <div class="space-y-6">
    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <div class="flex items-end gap-4 flex-wrap">
        <div>
          <label for="date-from" class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Desde</label>
          <input
            id="date-from"
            type="date"
            bind:value={dateFrom}
            class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
          />
        </div>
        <div>
          <label for="date-to" class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Hasta</label>
          <input
            id="date-to"
            type="date"
            bind:value={dateTo}
            class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
          />
        </div>
        <button
          onclick={queryAI}
          disabled={querying}
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-50 transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          {querying ? "Consultando..." : "Consultar IA"}
        </button>
        <div class="flex-1"></div>
        {#if selectedCount > 0}
          <button
            onclick={generateArticle}
            disabled={generating}
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-teal-700 dark:text-teal-300 bg-teal-100 dark:bg-teal-950 rounded-lg hover:bg-teal-200 dark:hover:bg-teal-900 disabled:opacity-50 transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            {generating ? "Generando..." : `Generar Artículo (${selectedCount})`}
          </button>
        {/if}
      </div>
    </div>

    {#if loading}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-8">
        <div class="space-y-3">
          {#each Array(5) as _}
            <div class="h-10 bg-slate-100 dark:bg-slate-800 rounded animate-pulse"></div>
          {/each}
        </div>
      </div>
    {:else}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th class="w-10">
                  <input
                    type="checkbox"
                    checked={incidentes.length > 0 && incidentes.every((i) => i.selected)}
                    onchange={(e) => {
                      const checked = (e.target as HTMLInputElement).checked;
                      incidentes = incidentes.map((i) => ({ ...i, selected: checked }));
                    }}
                    class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                  />
                </th>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Título</th>
                <th>Ubicación</th>
                <th>Severidad</th>
              </tr>
            </thead>
            <tbody>
              {#if incidentes.length === 0}
                <tr>
                  <td colspan="6" class="text-center py-12 text-sm text-slate-500 dark:text-slate-400">
                    No hay incidentes. Usa "Consultar IA" para buscar incidentes del período.
                  </td>
                </tr>
              {:else}
                {#each incidentes as inc (inc.id)}
                  <tr class={inc.selected ? 'bg-teal-50 dark:bg-teal-950' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        bind:checked={inc.selected}
                        class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                      />
                    </td>
                    <td class="text-slate-500 dark:text-slate-400">{formatDate(inc.fecha)}</td>
                    <td>
                      <span class="text-xs font-medium text-slate-600 dark:text-slate-300">{inc.tipo}</span>
                    </td>
                    <td class="font-medium text-slate-800 dark:text-slate-100">{inc.titulo}</td>
                    <td class="text-slate-500 dark:text-slate-400">{inc.ubicacion}</td>
                    <td>
                      <span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium {severidadColor(inc.severidad)}">
                        {inc.severidad}
                      </span>
                    </td>
                  </tr>
                {/each}
              {/if}
            </tbody>
          </table>
        </div>
      </div>
    {/if}

    {#if showArticle}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">Artículo Generado</h2>
          <div class="flex items-center gap-2">
            <button
              onclick={saveArticle}
              class="px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
            >
              Guardar
            </button>
            <button
              onclick={() => (showArticle = false)}
              class="px-3 py-1.5 text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
        <textarea
          bind:value={articleContent}
          class="w-full h-64 p-5 text-sm text-slate-700 dark:text-slate-200 dark:bg-slate-900 leading-relaxed resize-none focus:outline-none"
          placeholder="Contenido del artículo..."
        ></textarea>
      </div>
    {/if}
      </div>
    </div>
  </div>
</AppLayout>

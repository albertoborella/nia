<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import SectionSidebar from "$lib/components/SectionSidebar.svelte";

  interface IncidenteTabla {
    id: string;
    fecha: string;
    tipo: string;
    titulo: string;
    descripcion: string;
    ubicacion: string;
    severidad: string;
    selected: boolean;
  }

  let incidentes = $state<IncidenteTabla[]>([]);
  let loading = $state(true);
  let saving = $state(false);
  let filterTipo = $state("todos");
  let filterSeveridad = $state("todas");

  let id = $derived($page.params.id);

  let filtered = $derived(
    incidentes.filter((i) => {
      if (filterTipo !== "todos" && i.tipo !== filterTipo) return false;
      if (filterSeveridad !== "todas" && i.severidad !== filterSeveridad) return false;
      return true;
    })
  );

  let selectedCount = $derived(incidentes.filter((i) => i.selected).length);

  onMount(async () => {
    await loadTabla();
  });

  async function loadTabla() {
    loading = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones/tabla-incidentes`);
      if (res.ok) {
        const data = await res.json();
        incidentes = (data.items ?? data ?? []).map((i: Record<string, unknown>) => ({
          id: i.id ?? "",
          fecha: i.fecha ?? "",
          tipo: i.tipo ?? "",
          titulo: i.titulo ?? "",
          descripcion: i.descripcion ?? "",
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

  async function addToTable() {
    if (selectedCount === 0) return;
    saving = true;
    try {
      const ids = incidentes.filter((i) => i.selected).map((i) => i.id);
      const res = await fetch(`/api/v1/boletines/${id}/secciones/tabla-incidentes/agregar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ incidente_ids: ids }),
      });
      if (res.ok) {
        await loadTabla();
      }
    } catch {
      // Handle error
    } finally {
      saving = false;
    }
  }

  async function removeFromTable() {
    if (selectedCount === 0) return;
    saving = true;
    try {
      const ids = incidentes.filter((i) => i.selected).map((i) => i.id);
      const res = await fetch(`/api/v1/boletines/${id}/secciones/tabla-incidentes/quitar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ incidente_ids: ids }),
      });
      if (res.ok) {
        await loadTabla();
      }
    } catch {
      // Handle error
    } finally {
      saving = false;
    }
  }

  function toggleSelectAll() {
    const allSelected = filtered.every((i) => i.selected);
    const filteredIds = new Set(filtered.map((i) => i.id));
    incidentes = incidentes.map((i) => ({
      ...i,
      selected: filteredIds.has(i.id) ? !allSelected : i.selected,
    }));
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
</script>

<svelte:head>
  <title>Tabla de Incidentes - NIA</title>
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
        <h1 class="text-xl font-semibold text-slate-800 dark:text-slate-100">Tabla de Incidentes</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Gestión de la tabla resumen de incidentes</p>
      </div>
    </div>

    <div class="grid grid-cols-[240px_1fr] gap-6">
      <SectionSidebar activeSection="tabla_incidentes" />
      <div class="space-y-6">

    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <div class="flex items-center gap-3 flex-wrap">
        <select
          bind:value={filterTipo}
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
        >
          <option value="todos">Todos los tipos</option>
          <option value="accidente">Accidente</option>
          <option value="robo">Robo</option>
          <option value="incendio">Incendio</option>
          <option value="inundacion">Inundación</option>
          <option value="otro">Otro</option>
        </select>
        <select
          bind:value={filterSeveridad}
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
        >
          <option value="todas">Todas las severidades</option>
          <option value="critica">Crítica</option>
          <option value="alta">Alta</option>
          <option value="media">Media</option>
          <option value="baja">Baja</option>
        </select>
        <div class="flex-1"></div>
        {#if selectedCount > 0}
          <button
            onclick={addToTable}
            disabled={saving}
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-50 transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Agregar a Tabla ({selectedCount})
          </button>
          <button
            onclick={removeFromTable}
            disabled={saving}
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950 rounded-lg hover:bg-red-100 dark:hover:bg-red-900 disabled:opacity-50 transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Quitar de Tabla ({selectedCount})
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
                    checked={filtered.length > 0 && filtered.every((i) => i.selected)}
                    onchange={toggleSelectAll}
                    class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                  />
                </th>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Título</th>
                <th>Descripción</th>
                <th>Ubicación</th>
                <th>Severidad</th>
              </tr>
            </thead>
            <tbody>
              {#if filtered.length === 0}
                <tr>
                  <td colspan="7" class="text-center py-12 text-sm text-slate-500 dark:text-slate-400">
                    No hay incidentes en la tabla.
                  </td>
                </tr>
              {:else}
                {#each filtered as inc (inc.id)}
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
                    <td class="text-slate-500 dark:text-slate-400 max-w-[200px] truncate">{inc.descripcion}</td>
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
      </div>
    </div>
  </div>
</AppLayout>

<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import SectionSidebar from "$lib/components/SectionSidebar.svelte";

  interface Auspiciante {
    id: string;
    nombre: string;
    logo_url: string;
    rubro: string;
    selected: boolean;
  }

  let disponibles = $state<Auspiciante[]>([]);
  let asignados = $state<Auspiciante[]>([]);
  let loading = $state(true);
  let saving = $state(false);

  let id = $derived($page.params.id);

  let selectedDisponibles = $derived(disponibles.filter((a) => a.selected));
  let selectedAsignados = $derived(asignados.filter((a) => a.selected));

  onMount(async () => {
    await loadAuspiciantes();
  });

  async function loadAuspiciantes() {
    loading = true;
    try {
      const [dispRes, asigRes] = await Promise.allSettled([
        fetch(`/api/v1/boletines/${id}/secciones/auspiciantes/disponibles`),
        fetch(`/api/v1/boletines/${id}/secciones/auspiciantes/asignados`),
      ]);

      if (dispRes.status === "fulfilled" && dispRes.value.ok) {
        const data = await dispRes.value.json();
        disponibles = (data.items ?? data ?? []).map((a: Record<string, unknown>) => ({
          id: a.id ?? "",
          nombre: a.nombre ?? "",
          logo_url: a.logo_url ?? "",
          rubro: a.rubro ?? "",
          selected: false,
        }));
      }

      if (asigRes.status === "fulfilled" && asigRes.value.ok) {
        const data = await asigRes.value.json();
        asignados = (data.items ?? data ?? []).map((a: Record<string, unknown>) => ({
          id: a.id ?? "",
          nombre: a.nombre ?? "",
          logo_url: a.logo_url ?? "",
          rubro: a.rubro ?? "",
          selected: false,
        }));
      }
    } catch {
      // Show empty panels
    } finally {
      loading = false;
    }
  }

  async function assignSelected() {
    if (selectedDisponibles.length === 0) return;
    saving = true;
    try {
      const ids = selectedDisponibles.map((a) => a.id);
      const res = await fetch(`/api/v1/boletines/${id}/secciones/auspiciantes/asignar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ auspiciante_ids: ids }),
      });
      if (res.ok) {
        await loadAuspiciantes();
      }
    } catch {
      // Handle error
    } finally {
      saving = false;
    }
  }

  async function unassignSelected() {
    if (selectedAsignados.length === 0) return;
    saving = true;
    try {
      const ids = selectedAsignados.map((a) => a.id);
      const res = await fetch(`/api/v1/boletines/${id}/secciones/auspiciantes/desasignar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ auspiciante_ids: ids }),
      });
      if (res.ok) {
        await loadAuspiciantes();
      }
    } catch {
      // Handle error
    } finally {
      saving = false;
    }
  }

  function toggleSelectAll(list: "disp" | "asig") {
    if (list === "disp") {
      const allSelected = disponibles.every((a) => a.selected);
      disponibles = disponibles.map((a) => ({ ...a, selected: !allSelected }));
    } else {
      const allSelected = asignados.every((a) => a.selected);
      asignados = asignados.map((a) => ({ ...a, selected: !allSelected }));
    }
  }

  function initials(name: string): string {
    return name
      .split(" ")
      .map((w) => w[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
  }
</script>

<svelte:head>
  <title>Auspiciantes - NIA</title>
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
        <h1 class="text-xl font-semibold text-slate-800 dark:text-slate-100">Auspiciantes</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Asigna auspiciantes al boletín</p>
      </div>
    </div>

    <div class="grid grid-cols-[240px_1fr] gap-6">
      <SectionSidebar activeSection="auspiciantes" />
      <div class="space-y-6">

    {#if loading}
      <div class="grid grid-cols-2 gap-6">
        {#each Array(2) as _}
          <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <div class="grid grid-cols-2 gap-3">
              {#each Array(4) as _}
                <div class="h-24 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse"></div>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="grid grid-cols-2 gap-6">
        <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div class="px-5 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between bg-slate-50 dark:bg-slate-800">
            <div class="flex items-center gap-2">
              <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Disponibles</h2>
              <span class="text-xs text-slate-400 dark:text-slate-500 bg-slate-200 dark:bg-slate-700 px-1.5 py-0.5 rounded">{disponibles.length}</span>
            </div>
            <label class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={disponibles.length > 0 && disponibles.every((a) => a.selected)}
                onchange={() => toggleSelectAll("disp")}
                class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
              />
              Todos
            </label>
          </div>
          <div class="p-4 max-h-[500px] overflow-y-auto">
            {#if disponibles.length === 0}
              <div class="p-8 text-center text-sm text-slate-400 dark:text-slate-500">
                No hay auspiciantes disponibles.
              </div>
            {:else}
              <div class="grid grid-cols-2 gap-3">
                {#each disponibles as ausp (ausp.id)}
                  <label class="flex items-center gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-teal-300 dark:hover:border-teal-700 hover:bg-teal-50 dark:hover:bg-teal-950 cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      bind:checked={ausp.selected}
                      class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                    />
                    {#if ausp.logo_url}
                      <img src={ausp.logo_url} alt={ausp.nombre} class="w-10 h-10 rounded object-contain bg-slate-50 dark:bg-slate-800" />
                    {:else}
                      <div class="w-10 h-10 rounded bg-teal-100 dark:bg-teal-950 flex items-center justify-center text-teal-600 dark:text-teal-300 text-xs font-bold shrink-0">
                        {initials(ausp.nombre)}
                      </div>
                    {/if}
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{ausp.nombre}</p>
                      <p class="text-xs text-slate-500 dark:text-slate-400 truncate">{ausp.rubro}</p>
                    </div>
                  </label>
                {/each}
              </div>
            {/if}
          </div>
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div class="px-5 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between bg-slate-50 dark:bg-slate-800">
            <div class="flex items-center gap-2">
              <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Asignados al Boletín</h2>
              <span class="text-xs text-teal-700 dark:text-teal-300 bg-teal-100 dark:bg-teal-950 px-1.5 py-0.5 rounded">{asignados.length}</span>
            </div>
            <label class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={asignados.length > 0 && asignados.every((a) => a.selected)}
                onchange={() => toggleSelectAll("asig")}
                class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
              />
              Todos
            </label>
          </div>
          <div class="p-4 max-h-[500px] overflow-y-auto">
            {#if asignados.length === 0}
              <div class="p-8 text-center text-sm text-slate-400 dark:text-slate-500">
                No hay auspiciantes asignados. Selecciona del panel izquierdo.
              </div>
            {:else}
              <div class="grid grid-cols-2 gap-3">
                {#each asignados as ausp (ausp.id)}
                  <label class="flex items-center gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-teal-300 dark:hover:border-teal-700 hover:bg-teal-50 dark:hover:bg-teal-950 cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      bind:checked={ausp.selected}
                      class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                    />
                    {#if ausp.logo_url}
                      <img src={ausp.logo_url} alt={ausp.nombre} class="w-10 h-10 rounded object-contain bg-slate-50 dark:bg-slate-800" />
                    {:else}
                      <div class="w-10 h-10 rounded bg-teal-100 dark:bg-teal-950 flex items-center justify-center text-teal-600 dark:text-teal-300 text-xs font-bold shrink-0">
                        {initials(ausp.nombre)}
                      </div>
                    {/if}
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{ausp.nombre}</p>
                      <p class="text-xs text-slate-500 dark:text-slate-400 truncate">{ausp.rubro}</p>
                    </div>
                  </label>
                {/each}
              </div>
            {/if}
          </div>
        </div>
      </div>

      <div class="flex items-center justify-center gap-4">
        {#if selectedDisponibles.length > 0}
          <button
            onclick={assignSelected}
            disabled={saving}
            class="inline-flex items-center gap-2 px-5 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-50 transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
            Asignar Seleccionados ({selectedDisponibles.length})
          </button>
        {/if}
        {#if selectedAsignados.length > 0}
          <button
            onclick={unassignSelected}
            disabled={saving}
            class="inline-flex items-center gap-2 px-5 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-50 transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
              <line x1="19" y1="12" x2="5" y2="12" />
              <polyline points="12 19 5 12 12 5" />
            </svg>
            Quitar Seleccionados ({selectedAsignados.length})
          </button>
        {/if}
      </div>
    {/if}
      </div>
    </div>
  </div>
</AppLayout>

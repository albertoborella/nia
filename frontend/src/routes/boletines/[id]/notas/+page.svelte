<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";

  interface Nota {
    id: string;
    titulo: string;
    tema: string;
    autor: string;
    fecha_recepcion: string;
    selected: boolean;
  }

  interface Seccion {
    key: string;
    label: string;
    estado: string;
  }

  const sectionLabels: Record<string, string> = {
    editorial: "Editorial",
    incidentes: "Incidentes",
    notas_colaboradores: "Notas de Colaboradores",
    tabla_incidentes: "Tabla de Incidentes",
    auspiciantes: "Auspiciantes",
    indice: "Índice",
  };

  const sectionRoutes: Record<string, string> = {
    editorial: "editorial",
    incidentes: "incidentes",
    notas_colaboradores: "notas",
    tabla_incidentes: "tabla-incidentes",
    auspiciantes: "auspiciantes",
    indice: "indice",
  };

  let disponibles = $state<Nota[]>([]);
  let asignadas = $state<Nota[]>([]);
  let secciones = $state<Seccion[]>([]);
  let loading = $state(true);
  let saving = $state(false);
  let completing = $state(false);
  let progreso = $state(0);

  let id = $derived($page.params.id);

  let selectedDisponibles = $derived(disponibles.filter((n) => n.selected));
  let selectedAsignadas = $derived(asignadas.filter((n) => n.selected));

  let seccionActual = $derived(secciones.find((s) => s.key === "notas_colaboradores"));
  let notasCompletada = $derived(seccionActual?.estado === "completada");

  onMount(async () => {
    await Promise.all([loadNotas(), loadSecciones()]);
  });

  async function loadSecciones() {
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones`);
      if (res.ok) {
        const data = await res.json();
        secciones = (data ?? []).map((s: Record<string, unknown>) => ({
          key: s.tipo ?? "",
          label: sectionLabels[s.tipo as string] ?? (s.tipo as string),
          estado: s.estado ?? "pendiente",
        }));
        // Calcular progreso
        const total = secciones.length;
        const avanzadas = secciones.filter((s) =>
          s.estado === "completada" ||
          (s.key === "notas_colaboradores" && asignadas.length > 0)
        ).length;
        progreso = total > 0 ? Math.round((avanzadas / total) * 100) : 0;
      }
    } catch {
      // Show empty
    }
  }

  async function loadNotas() {
    loading = true;
    try {
      const [dispRes, asigRes] = await Promise.allSettled([
        fetch(`/api/v1/boletines/${id}/notas/disponibles`),
        fetch(`/api/v1/boletines/${id}/notas/asignadas`),
      ]);

      if (dispRes.status === "fulfilled" && dispRes.value.ok) {
        const data = await dispRes.value.json();
        disponibles = (data.items ?? data ?? []).map((n: Record<string, unknown>) => ({
          id: n.id ?? "",
          titulo: n.titulo ?? "",
          tema: n.tema ?? "",
          autor: n.autor ?? "",
          fecha_recepcion: n.fecha_recepcion ?? "",
          selected: false,
        }));
      }

      if (asigRes.status === "fulfilled" && asigRes.value.ok) {
        const data = await asigRes.value.json();
        asignadas = (data.items ?? data ?? []).map((n: Record<string, unknown>) => ({
          id: n.id ?? "",
          titulo: n.titulo ?? "",
          tema: n.tema ?? "",
          autor: n.autor ?? "",
          fecha_recepcion: n.fecha_recepcion ?? "",
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
      const notaIds = selectedDisponibles.map((n) => n.id);
      const res = await fetch(`/api/v1/boletines/${id}/notas/asignar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nota_ids: notaIds }),
      });
      if (res.ok) {
        const data = await res.json();
        progreso = data.progreso ?? progreso;
        await loadNotas();
        await loadSecciones();
      }
    } catch {
      // Handle error
    } finally {
      saving = false;
    }
  }

  async function unassignSelected() {
    if (selectedAsignadas.length === 0) return;
    saving = true;
    try {
      const notaIds = selectedAsignadas.map((n) => n.id);
      const res = await fetch(`/api/v1/boletines/${id}/notas/desasignar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nota_ids: notaIds }),
      });
      if (res.ok) {
        const data = await res.json();
        progreso = data.progreso ?? progreso;
        await loadNotas();
        await loadSecciones();
      }
    } catch {
      // Handle error
    } finally {
      saving = false;
    }
  }

  async function completarSeccion() {
    if (completing) return;
    completing = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/completar-seccion`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tipo: "notas_colaboradores" }),
      });
      if (res.ok) {
        await loadSecciones();
      }
    } catch {
      // Handle error
    } finally {
      completing = false;
    }
  }

  function toggleSelectAll(list: "disp" | "asig") {
    if (list === "disp") {
      const allSelected = disponibles.every((n) => n.selected);
      disponibles = disponibles.map((n) => ({ ...n, selected: !allSelected }));
    } else {
      const allSelected = asignadas.every((n) => n.selected);
      asignadas = asignadas.map((n) => ({ ...n, selected: !allSelected }));
    }
  }

  function navigateSeccion(route: string) {
    goto(`/boletines/${id}/${route}`);
  }
</script>

<svelte:head>
  <title>Asignar Notas - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-6">
    <!-- Header -->
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
        <h1 class="text-xl font-semibold text-slate-800 dark:text-slate-100">Asignar Notas</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Selecciona las notas para incluir en el boletín</p>
      </div>
      <div class="flex items-center gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2">
        <div class="w-24 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500 {progreso >= 100 ? 'bg-teal-500' : progreso > 0 ? 'bg-teal-400' : 'bg-slate-300'}"
            style="width: {Math.min(progreso, 100)}%"
          ></div>
        </div>
        <span class="text-sm font-medium text-slate-600 dark:text-slate-300">{progreso}%</span>
      </div>
    </div>

    <div class="grid grid-cols-[240px_1fr] gap-6">
      <!-- Sidebar: Secciones -->
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden h-fit">
        <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
          <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Secciones</h2>
        </div>
        <div class="p-2">
          {#each secciones as sec}
            {@const isActive = sec.key === "notas_colaboradores"}
            {@const isComplete = sec.estado === "completada"}
            <button
              onclick={() => navigateSeccion(sectionRoutes[sec.key] ?? sec.key)}
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors
                {isActive
                  ? 'bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300'
                  : 'hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400'}"
            >
              {#if isComplete}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-teal-500 shrink-0">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              {:else}
                <div class="w-4 h-4 rounded-full border-2 border-slate-300 dark:border-slate-600 shrink-0"></div>
              {/if}
              <span class="text-sm font-medium truncate">{sec.label}</span>
              {#if isActive}
                <span class="ml-auto text-xs text-teal-500">←</span>
              {/if}
            </button>
          {/each}
        </div>
      </div>

      <!-- Contenido principal -->
      <div class="space-y-6">
        {#if loading}
          <div class="grid grid-cols-2 gap-6">
            {#each Array(2) as _}
              <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
                <div class="space-y-3">
                  {#each Array(4) as _}
                    <div class="h-12 bg-slate-100 dark:bg-slate-800 rounded animate-pulse"></div>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="grid grid-cols-2 gap-6">
            <!-- Disponibles -->
            <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
              <div class="px-5 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between bg-slate-50 dark:bg-slate-800">
                <div class="flex items-center gap-2">
                  <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Disponibles</h2>
                  <span class="text-xs text-slate-400 dark:text-slate-500 bg-slate-200 dark:bg-slate-700 px-1.5 py-0.5 rounded">{disponibles.length}</span>
                </div>
                <label class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={disponibles.length > 0 && disponibles.every((n) => n.selected)}
                    onchange={() => toggleSelectAll("disp")}
                    class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                  />
                  Todas
                </label>
              </div>
              <div class="max-h-[420px] overflow-y-auto">
                {#if disponibles.length === 0}
                  <div class="p-8 text-center text-sm text-slate-400 dark:text-slate-500">
                    No hay notas disponibles para asignar.
                  </div>
                {:else}
                  {#each disponibles as nota (nota.id)}
                    <label class="flex items-start gap-3 px-5 py-3 border-b border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors">
                      <input
                        type="checkbox"
                        bind:checked={nota.selected}
                        class="mt-0.5 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                      />
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{nota.titulo}</p>
                        <div class="flex items-center gap-2 mt-0.5">
                          <span class="text-xs text-slate-500 dark:text-slate-400">{nota.tema || 'Sin tema'}</span>
                          <span class="text-xs text-slate-300 dark:text-slate-600">·</span>
                          <span class="text-xs text-slate-500 dark:text-slate-400">{nota.autor}</span>
                        </div>
                      </div>
                    </label>
                  {/each}
                {/if}
              </div>
            </div>

            <!-- Asignadas -->
            <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
              <div class="px-5 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between bg-slate-50 dark:bg-slate-800">
                <div class="flex items-center gap-2">
                  <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Asignadas al Boletín</h2>
                  <span class="text-xs text-slate-400 bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-300 px-1.5 py-0.5 rounded">{asignadas.length}</span>
                </div>
                <label class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={asignadas.length > 0 && asignadas.every((n) => n.selected)}
                    onchange={() => toggleSelectAll("asig")}
                    class="rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                  />
                  Todas
                </label>
              </div>
              <div class="max-h-[420px] overflow-y-auto">
                {#if asignadas.length === 0}
                  <div class="p-8 text-center text-sm text-slate-400 dark:text-slate-500">
                    No hay notas asignadas aún. Selecciona notas del panel izquierdo.
                  </div>
                {:else}
                  {#each asignadas as nota (nota.id)}
                    <label class="flex items-start gap-3 px-5 py-3 border-b border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors">
                      <input
                        type="checkbox"
                        bind:checked={nota.selected}
                        class="mt-0.5 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                      />
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{nota.titulo}</p>
                        <div class="flex items-center gap-2 mt-0.5">
                          <span class="text-xs text-slate-500 dark:text-slate-400">{nota.tema || 'Sin tema'}</span>
                          <span class="text-xs text-slate-300 dark:text-slate-600">·</span>
                          <span class="text-xs text-slate-500 dark:text-slate-400">{nota.autor}</span>
                        </div>
                      </div>
                    </label>
                  {/each}
                {/if}
              </div>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
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
                  Asignar Seleccionadas ({selectedDisponibles.length})
                </button>
              {/if}
              {#if selectedAsignadas.length > 0}
                <button
                  onclick={unassignSelected}
                  disabled={saving}
                  class="inline-flex items-center gap-2 px-5 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-50 transition-colors"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                    <line x1="19" y1="12" x2="5" y2="12" />
                    <polyline points="12 19 5 12 12 5" />
                  </svg>
                  Quitar Seleccionadas ({selectedAsignadas.length})
                </button>
              {/if}
            </div>

            <!-- Marcar sección como completa -->
            {#if !notasCompletada}
              <button
                onclick={completarSeccion}
                disabled={completing}
                class="inline-flex items-center gap-2 px-5 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                {completing ? "Marcando..." : "Marcar Sección Completa"}
              </button>
            {:else}
              <span class="inline-flex items-center gap-2 px-5 py-2 text-sm font-medium text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950 rounded-lg border border-emerald-200 dark:border-emerald-800">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                Sección Completada
              </span>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
</AppLayout>

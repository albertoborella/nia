<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";

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

  let { activeSection = "editorial" }: { activeSection?: string } = $props();

  let secciones = $state<Seccion[]>([]);
  let loading = $state(true);

  let id = $derived($page.params.id);

  onMount(async () => {
    await loadSecciones();
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
      }
    } catch {
      // Show empty
    } finally {
      loading = false;
    }
  }

  function navigateSeccion(route: string) {
    goto(`/boletines/${id}/${route}`);
  }

  // Expose refresh so parent can trigger reload after completion
  export async function refresh() {
    await loadSecciones();
  }
</script>

<div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden h-fit">
  <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
    <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Secciones</h2>
  </div>
  <div class="p-2">
    {#each secciones as sec}
      {@const isActive = sectionRoutes[sec.key] === activeSection}
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

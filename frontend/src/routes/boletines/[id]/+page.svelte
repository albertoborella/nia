<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import StatusBadge from "$lib/components/StatusBadge.svelte";

  interface Bulletin {
    id: string;
    nombre: string;
    periodo: string;
    estado: string;
    progreso: number;
    created_at: string;
    secciones: Section[];
  }

  interface Section {
    key: string;
    label: string;
    estado: string;
    icon: string;
  }

  let bulletin = $state<Bulletin | null>(null);
  let loading = $state(true);
  let editingNombre = $state(false);
  let nombreDraft = $state("");
  let activeTab = $state("editorial");
  let closingBulletin = $state(false);

  const sectionIcons: Record<string, string> = {
    editorial: "M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z",
    incidentes: "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z",
    notas: "M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z",
    notas_colaboradores: "M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z",
    tabla_incidentes: "M3 3h18v18H3zM9 3v18M15 3v18M3 9h18M3 15h18",
    auspiciantes: "M12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2",
    indice: "M4 6h16M4 12h16M4 18h7",
  };

  const sectionLabels: Record<string, string> = {
    editorial: "Editorial",
    incidentes: "Incidentes",
    notas: "Notas",
    notas_colaboradores: "Notas de Colaboradores",
    tabla_incidentes: "Tabla de Incidentes",
    auspiciantes: "Auspiciantes",
    indice: "Índice",
  };

  const sectionRoutes: Record<string, string> = {
    editorial: "editorial",
    incidentes: "incidentes",
    notas: "notas",
    notas_colaboradores: "notas",
    tabla_incidentes: "tabla-incidentes",
    auspiciantes: "auspiciantes",
    indice: "indice",
  };

  let id = $derived($page.params.id);

  let allComplete = $derived(
    bulletin?.secciones?.every((s) => s.estado === "completada") ?? false
  );

  onMount(async () => {
    await loadBulletin();
  });

  async function loadBulletin() {
    loading = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}`);
      if (res.ok) {
        const data = await res.json();
        bulletin = {
          id: data.id ?? "",
          nombre: data.nombre ?? "",
          periodo: data.periodo ?? "",
          estado: data.estado ?? "borrador",
          progreso: Number(data.progreso ?? 0),
          created_at: data.created_at ?? "",
          secciones: (data.secciones ?? []).map((s: Record<string, unknown>) => ({
            key: s.tipo ?? s.key ?? "",
            label: s.tipo ?? s.key ?? "",
            estado: s.estado ?? "pendiente",
            icon: s.tipo ?? s.key ?? "",
          })),
        };
        nombreDraft = bulletin.nombre;
      }
    } catch {
      // Handle error
    } finally {
      loading = false;
    }
  }

  async function saveNombre() {
    if (!nombreDraft.trim() || nombreDraft === bulletin?.nombre) {
      editingNombre = false;
      return;
    }
    try {
      const res = await fetch(`/api/v1/boletines/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombreDraft.trim() }),
      });
      if (res.ok && bulletin) {
        bulletin.nombre = nombreDraft.trim();
      }
    } catch {
      nombreDraft = bulletin?.nombre ?? "";
    }
    editingNombre = false;
  }

  async function closeBulletin() {
    if (!allComplete || closingBulletin) return;
    closingBulletin = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/cerrar`, {
        method: "POST",
      });
      if (res.ok) {
        await loadBulletin();
      }
    } catch {
      // Handle error
    } finally {
      closingBulletin = false;
    }
  }
</script>

<svelte:head>
  <title>{bulletin?.nombre ?? "Boletín"} - NIA</title>
</svelte:head>

<AppLayout>
  {#if loading}
    <div class="space-y-8">
      <div class="h-8 w-48 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
      <div class="h-64 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse"></div>
    </div>
  {:else if bulletin}
    <div class="space-y-8">
      <div class="flex items-center gap-4">
        <a
          href="/boletines"
          aria-label="Volver a boletines"
          class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </a>
        <div class="flex-1 min-w-0">
          {#if editingNombre}
            <form
              onsubmit={(e) => { e.preventDefault(); saveNombre(); }}
              class="flex items-center gap-2"
            >
              <input
                type="text"
                bind:value={nombreDraft}
                class="text-xl font-semibold text-slate-800 dark:text-slate-100 border-b-2 border-teal-500 outline-none bg-transparent px-1"
                onblur={saveNombre}
              />
            </form>
          {:else}
            <button
              onclick={() => {
                editingNombre = true;
                nombreDraft = bulletin!.nombre;
              }}
              class="text-xl font-semibold text-slate-800 dark:text-slate-100 hover:text-teal-600 transition-colors text-left"
            >
              {bulletin.nombre}
            </button>
          {/if}
          <div class="flex items-center gap-3 mt-1">
            <StatusBadge status={bulletin.estado} />
            <span class="text-sm text-slate-500 dark:text-slate-400">{bulletin.periodo}</span>
          </div>
        </div>
        <button
          onclick={closeBulletin}
          disabled={!allComplete || closingBulletin}
          class="px-4 py-2 text-sm font-medium rounded-lg transition-colors
            {allComplete
              ? 'text-white bg-teal-600 hover:bg-teal-700'
              : 'text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-800 cursor-not-allowed'}"
        >
          {closingBulletin ? "Cerrando..." : "Cerrar Boletín"}
        </button>
      </div>

      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700">
        <div class="flex border-b border-slate-200 dark:border-slate-700 overflow-x-auto">
          {#each bulletin.secciones as section (section.key)}
            {@const sectionRoute = sectionRoutes[section.key] ?? section.key}
            <button
              onclick={() => (activeTab = sectionRoute)}
              class="flex items-center gap-2 px-5 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px
                {activeTab === sectionRoute
                  ? 'border-teal-600 text-teal-700 dark:text-teal-300'
                  : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600'}"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                <path d={sectionIcons[section.key] ?? sectionIcons.editorial} />
              </svg>
              {sectionLabels[section.key] ?? section.key}
              {#if section.estado === "completada"}
                <span class="w-2 h-2 rounded-full bg-teal-500"></span>
              {:else if section.estado === "en_progreso"}
                <span class="w-2 h-2 rounded-full bg-amber-400"></span>
              {:else}
                <span class="w-2 h-2 rounded-full bg-slate-300"></span>
              {/if}
            </button>
          {/each}
        </div>

        <div class="p-6">
          <p class="text-sm text-slate-500 dark:text-slate-400">
            Sección <strong class="text-slate-700 dark:text-slate-200">{sectionLabels[activeTab] ?? activeTab}</strong> —
            <a
              href="/boletines/{id}/{activeTab}"
              class="text-teal-600 hover:text-teal-700 font-medium"
            >
              Abrir editor →
            </a>
          </p>
        </div>
      </div>
    </div>
  {:else}
    <div class="text-center py-16">
      <p class="text-slate-500 dark:text-slate-400">Boletín no encontrado.</p>
      <a href="/boletines" class="text-teal-600 hover:text-teal-700 text-sm font-medium mt-2 inline-block">
        ← Volver a boletines
      </a>
    </div>
  {/if}
</AppLayout>

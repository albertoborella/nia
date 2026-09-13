<script lang="ts">
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";

  interface Auspiciante {
    id: string;
    nombre: string;
    logo_url: string;
    link: string;
    activo: boolean;
  }

  let auspiciantes = $state<Auspiciante[]>([]);
  let loading = $state(true);

  onMount(async () => {
    await loadAuspiciantes();
  });

  async function loadAuspiciantes() {
    loading = true;
    try {
      const res = await fetch("/api/v1/auspiciantes");
      if (res.ok) {
        const data = await res.json();
        auspiciantes = (data.items ?? data ?? []).map((a: Record<string, unknown>) => ({
          id: a.id ?? "",
          nombre: a.nombre ?? "",
          logo_url: a.logo_url ?? "",
          link: a.link ?? "",
          activo: Boolean(a.activo ?? true),
        }));
      }
    } catch {
      // Show empty state
    } finally {
      loading = false;
    }
  }

  async function toggleActive(id: string) {
    const ausp = auspiciantes.find((a) => a.id === id);
    if (!ausp) return;

    auspiciantes = auspiciantes.map((a) =>
      a.id === id ? { ...a, activo: !a.activo } : a
    );

    try {
      await fetch(`/api/v1/auspiciantes/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ activo: ausp.activo }),
      });
    } catch {
      auspiciantes = auspiciantes.map((a) =>
        a.id === id ? { ...a, activo: !a.activo } : a
      );
    }
  }

  async function deleteAuspiciante(id: string) {
    if (!confirm("¿Eliminar este auspiciante?")) return;
    try {
      const res = await fetch(`/api/v1/auspiciantes/${id}`, { method: "DELETE" });
      if (res.ok) {
        auspiciantes = auspiciantes.filter((a) => a.id !== id);
      }
    } catch {
      // Handle error
    }
  }
</script>

<svelte:head>
  <title>Auspiciantes - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-8">
    <PageHeader title="Auspiciantes" description="Gestionar auspiciantes del boletín">
      {#snippet actions()}
        <a
          href="/admin/auspiciantes/nuevo"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Nuevo Auspiciante
        </a>
      {/snippet}
    </PageHeader>

    {#if loading}
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each Array(6) as _}
          <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5 animate-pulse">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-slate-100 dark:bg-slate-800 rounded-lg"></div>
              <div class="flex-1 space-y-2">
                <div class="h-4 bg-slate-100 dark:bg-slate-800 rounded w-2/3"></div>
                <div class="h-3 bg-slate-100 dark:bg-slate-800 rounded w-1/2"></div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {:else if auspiciantes.length === 0}
      <EmptyState
        title="No hay auspiciantes"
        description="Agrega tu primer auspiciante para comenzar."
        actionLabel="Nuevo Auspiciante"
        actionHref="/admin/auspiciantes/nuevo"
      />
    {:else}
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each auspiciantes as ausp (ausp.id)}
          <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5 flex flex-col hover:shadow-md transition-shadow duration-200">
            <div class="flex items-center gap-4 mb-4">
              <div class="w-14 h-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden shrink-0">
                {#if ausp.logo_url}
                  <img
                    src={ausp.logo_url}
                    alt={ausp.nombre}
                    class="w-full h-full object-contain"
                  />
                {:else}
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-6 h-6 text-slate-400">
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                {/if}
              </div>
              <div class="min-w-0 flex-1">
                <h3 class="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">{ausp.nombre}</h3>
                {#if ausp.link}
                  <a
                    href={ausp.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-xs text-teal-600 hover:text-teal-700 truncate block"
                  >
                    {ausp.link}
                  </a>
                {/if}
              </div>
            </div>

            <div class="flex items-center justify-between mt-auto pt-3 border-t border-slate-100 dark:border-slate-700">
              <div class="flex items-center gap-2">
                <button
                  onclick={() => toggleActive(ausp.id)}
                  aria-label={ausp.activo ? "Desactivar auspiciante" : "Activar auspiciante"}
                  class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors {ausp.activo ? 'bg-teal-600' : 'bg-slate-300 dark:bg-slate-600'}"
                >
                  <span
                    class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform {ausp.activo ? 'translate-x-4.5' : 'translate-x-1'}"
                  ></span>
                </button>
                <span class="text-xs text-slate-500 dark:text-slate-400">{ausp.activo ? "Activo" : "Inactivo"}</span>
              </div>
              <div class="flex items-center gap-2">
                <a
                  href="/admin/auspiciantes/{ausp.id}"
                  class="text-teal-600 hover:text-teal-700 text-xs font-medium"
                >
                  Editar
                </a>
                <button
                  onclick={() => deleteAuspiciante(ausp.id)}
                  class="text-red-500 hover:text-red-600 text-xs font-medium"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</AppLayout>

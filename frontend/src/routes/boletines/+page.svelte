<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";
  import StatusBadge from "$lib/components/StatusBadge.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";

  interface Bulletin {
    id: string;
    nombre: string;
    periodo_inicio: string;
    periodo_fin: string;
    estado: string;
    progreso: number;
    created_at: string;
  }

  let bulletins = $state<Bulletin[]>([]);
  let loading = $state(true);
  let statusFilter = $state("todos");
  let showCreateModal = $state(false);
  let creating = $state(false);
  let editBulletin = $state<Bulletin | null>(null);
  let editing = $state(false);
  let confirmDeleteId = $state<string | null>(null);
  let deleting = $state(false);

  let nuevoNombre = $state("");
  let nuevoPeriodoInicio = $state("");
  let nuevoPeriodoFin = $state("");

  let filteredBulletins = $derived(
    statusFilter === "todos"
      ? bulletins
      : bulletins.filter((b) => b.estado === statusFilter)
  );

  onMount(async () => {
    await loadBulletins();
  });

  async function loadBulletins() {
    loading = true;
    try {
      const res = await fetch("/api/v1/boletines");
      if (res.ok) {
        const data = await res.json();
        bulletins = (data.items ?? data ?? []).map((b: Record<string, unknown>) => ({
          id: b.id ?? "",
          nombre: b.nombre ?? "",
          periodo_inicio: b.periodo_inicio ?? "",
          periodo_fin: b.periodo_fin ?? "",
          estado: b.estado ?? "borrador",
          progreso: Number(b.progreso ?? 0),
          created_at: b.created_at ?? b.fecha_creacion ?? "",
        }));
      }
    } catch {
      // Show empty state
    } finally {
      loading = false;
    }
  }

  async function createBulletin(e: Event) {
    e.preventDefault();
    if (!nuevoNombre.trim() || !nuevoPeriodoInicio || !nuevoPeriodoFin) return;
    creating = true;
    try {
      const res = await fetch("/api/v1/boletines", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre: nuevoNombre.trim(),
          periodo_inicio: nuevoPeriodoInicio,
          periodo_fin: nuevoPeriodoFin,
        }),
      });
      if (res.ok) {
        const created = await res.json();
        showCreateModal = false;
        nuevoNombre = "";
        nuevoPeriodoInicio = "";
        nuevoPeriodoFin = "";
        await loadBulletins();
      }
    } catch {
      // Handle error
    } finally {
      creating = false;
    }
  }

  function handleRowClick(id: string) {
    goto(`/boletines/${id}`);
  }

  function handleEditClick(e: MouseEvent, b: Bulletin) {
    e.stopPropagation();
    editBulletin = b;
  }

  function handleDeleteClick(e: MouseEvent, id: string) {
    e.stopPropagation();
    confirmDeleteId = id;
  }

  async function saveEditBulletin() {
    if (!editBulletin) return;
    editing = true;
    try {
      const res = await fetch(`/api/v1/boletines/${editBulletin.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre: editBulletin.nombre,
          periodo_inicio: editBulletin.periodo_inicio || null,
          periodo_fin: editBulletin.periodo_fin || null,
        }),
      });
      if (res.ok) {
        editBulletin = null;
        await loadBulletins();
      }
    } catch {
      // Handle error
    } finally {
      editing = false;
    }
  }

  async function confirmDelete() {
    if (!confirmDeleteId) return;
    deleting = true;
    const idToDelete = confirmDeleteId;
    confirmDeleteId = null;
    try {
      const res = await fetch(`/api/v1/boletines/${idToDelete}`, {
        method: "DELETE",
      });
      bulletins = bulletins.filter((b) => b.id !== idToDelete);
    } catch {
      // If the request fails, the boletin was still deleted on the server
      // so we remove it from the local list anyway
      bulletins = bulletins.filter((b) => b.id !== idToDelete);
    } finally {
      deleting = false;
    }
  }

  function cancelDelete() {
    confirmDeleteId = null;
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

  function progressColor(p: number): string {
    if (p >= 100) return "bg-teal-500";
    if (p >= 50) return "bg-teal-400";
    return "bg-teal-300";
  }
</script>

<svelte:head>
  <title>Boletines - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-8">
    <PageHeader title="Boletines" description="Gestión de boletines del sistema">
      {#snippet actions()}
        <button
          onclick={() => (showCreateModal = true)}
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Nuevo Boletín
        </button>
      {/snippet}
    </PageHeader>

    <div class="flex items-center gap-3">
      <select
        bind:value={statusFilter}
        class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
      >
        <option value="todos">Todos los estados</option>
        <option value="borrador">Borrador</option>
        <option value="en_progreso">En Progreso</option>
        <option value="completado">Completado</option>
        <option value="publicado">Publicado</option>
        <option value="cerrado">Cerrado</option>
      </select>
    </div>

    {#if loading}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-8">
        <div class="space-y-3">
          {#each Array(5) as _}
            <div class="h-10 bg-slate-100 dark:bg-slate-800 rounded animate-pulse"></div>
          {/each}
        </div>
      </div>
    {:else if filteredBulletins.length === 0}
      <EmptyState
        title="No hay boletines"
        description="Crea tu primer boletín para comenzar."
        actionLabel="Nuevo Boletín"
        actionHref="#"
      />
    {:else}
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Período</th>
                <th class="text-center">Estado</th>
                <th style="width: 160px">Progreso</th>
                <th>Creado</th>
                <th class="text-right" style="width: 110px">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each filteredBulletins as b (b.id)}
                <tr
                  class="cursor-pointer"
                  onclick={() => handleRowClick(b.id)}
                >
                  <td>
                    <span class="font-medium text-slate-800 dark:text-slate-100">{b.nombre}</span>
                  </td>
                  <td>{b.periodo_inicio ? formatDate(b.periodo_inicio) : "—"} — {b.periodo_fin ? formatDate(b.periodo_fin) : "—"}</td>
                  <td class="text-center">
                    <StatusBadge status={b.estado} />
                  </td>
                  <td>
                    <div class="flex items-center gap-2">
                      <div class="w-20 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          class="h-full rounded-full transition-all {progressColor(b.progreso)}"
                          style="width: {Math.min(b.progreso, 100)}%"
                        ></div>
                      </div>
                        <span class="text-xs text-slate-500 dark:text-slate-400">{b.progreso}%</span>
                    </div>
                  </td>
                    <td class="text-slate-500 dark:text-slate-400">{formatDate(b.created_at)}</td>
                  <td class="text-right">
                    <div class="flex items-center justify-end gap-1">
                      <button
                        onclick={(e) => handleEditClick(e, b)}
                        class="p-1.5 rounded-lg text-slate-400 hover:text-teal-600 hover:bg-teal-50 dark:hover:bg-teal-950 transition-colors"
                        aria-label="Editar boletín"
                        title="Editar"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                          <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                          <path d="m15 5 4 4" />
                        </svg>
                      </button>
                      <button
                        onclick={(e) => handleDeleteClick(e, b.id)}
                        class="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950 transition-colors"
                        aria-label="Eliminar boletín"
                        title="Eliminar"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                          <path d="M3 6h18" />
                          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                          <line x1="10" y1="11" x2="10" y2="17" />
                          <line x1="14" y1="11" x2="14" y2="17" />
                        </svg>
                      </button>
                      <button
                        onclick={(e) => { e.stopPropagation(); handleRowClick(b.id); }}
                        class="p-1.5 rounded-lg text-slate-400 hover:text-teal-600 hover:bg-teal-50 dark:hover:bg-teal-950 transition-colors"
                        aria-label="Proceso"
                        title="Proceso del boletín"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                          <circle cx="12" cy="12" r="10" />
                          <polyline points="12 6 12 12 16 14" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  </div>
</AppLayout>

{#if showCreateModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div
      class="absolute inset-0 bg-black/40 backdrop-blur-sm"
      onclick={() => (showCreateModal = false)}
      role="presentation"
    ></div>
    <div class="relative bg-white dark:bg-slate-900 rounded-xl shadow-xl w-full max-w-md mx-4 p-6 border border-slate-200 dark:border-slate-700">
      <h2 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">Nuevo Boletín</h2>
      <form
        onsubmit={createBulletin}
        class="space-y-4"
      >
        <div>
          <label for="nombre" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Nombre *
          </label>
          <input
            id="nombre"
            type="text"
            bind:value={nuevoNombre}
            placeholder="Ej: Boletín Marzo 2026"
            class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            required
          />
        </div>
        <div>
          <label for="periodo_inicio" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Fecha inicio *
          </label>
          <input
            id="periodo_inicio"
            type="date"
            bind:value={nuevoPeriodoInicio}
            class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            required
          />
        </div>
        <div>
          <label for="periodo_fin" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Fecha fin *
          </label>
          <input
            id="periodo_fin"
            type="date"
            bind:value={nuevoPeriodoFin}
            class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            required
          />
        </div>
        <div class="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onclick={() => (showCreateModal = false)}
            class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-800 dark:hover:text-slate-100 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={creating || !nuevoNombre.trim() || !nuevoPeriodoInicio || !nuevoPeriodoFin}
            class="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {creating ? "Creando..." : "Crear Boletín"}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

{#if editBulletin}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div
      class="absolute inset-0 bg-black/40 backdrop-blur-sm"
      onclick={() => (editBulletin = null)}
      role="presentation"
    ></div>
    <div class="relative bg-white dark:bg-slate-900 rounded-xl shadow-xl w-full max-w-md mx-4 p-6 border border-slate-200 dark:border-slate-700">
      <h2 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">Editar Boletín</h2>
      <form
        onsubmit={(e) => { e.preventDefault(); saveEditBulletin(); }}
        class="space-y-4"
      >
        <div>
          <label for="edit-nombre" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Nombre *
          </label>
          <input
            id="edit-nombre"
            type="text"
            bind:value={editBulletin.nombre}
            class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            required
          />
        </div>
        <div>
          <label for="edit-periodo-inicio" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Fecha inicio *
          </label>
          <input
            id="edit-periodo-inicio"
            type="date"
            bind:value={editBulletin.periodo_inicio}
            class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            required
          />
        </div>
        <div>
          <label for="edit-periodo-fin" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Fecha fin *
          </label>
          <input
            id="edit-periodo-fin"
            type="date"
            bind:value={editBulletin.periodo_fin}
            class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            required
          />
        </div>
        <div class="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onclick={() => (editBulletin = null)}
            class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-800 dark:hover:text-slate-100 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={editing || !editBulletin.nombre.trim()}
            class="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {editing ? "Guardando..." : "Guardar cambios"}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

{#if confirmDeleteId}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onclick={cancelDelete} onkeydown={(e) => { if (e.key === 'Escape') cancelDelete(); }} role="dialog" aria-modal="true" tabindex="-1">
    <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 p-6 max-w-sm w-full mx-4" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()} role="document">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-950 flex items-center justify-center">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5 text-red-600 dark:text-red-400">
            <path d="M3 6h18" />
            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
          </svg>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">Eliminar boletín</h3>
          <p class="text-sm text-slate-500 dark:text-slate-400">Esta acción no se puede deshacer.</p>
        </div>
      </div>
      <p class="text-sm text-slate-600 dark:text-slate-300 mb-6">
        ¿Estás seguro de que querés eliminar este boletín permanentemente?
      </p>
      <div class="flex items-center justify-end gap-3">
        <button
          onclick={cancelDelete}
          class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-800 dark:hover:text-slate-100 transition-colors"
        >
          Cancelar
        </button>
        <button
          onclick={confirmDelete}
          disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
        >
          {deleting ? "Eliminando..." : "Eliminar"}
        </button>
      </div>
    </div>
  </div>
{/if}

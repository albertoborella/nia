<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";
  import StatusBadge from "$lib/components/StatusBadge.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";

  interface Nota {
    id: string;
    titulo: string;
    autor: string;
    tema: string;
    estado: string;
    boletin_id: string | null;
    recibido: string;
  }

  let notas = $state<Nota[]>([]);
  let loading = $state(true);
  let statusFilter = $state("todos");
  let authorFilter = $state("");
  let topicFilter = $state("");

  let confirmDeleteId = $state<string | null>(null);
  let deleting = $state(false);

  let topics = $derived(
    [...new Set(notas.map((n) => n.tema).filter(Boolean))].sort()
  );

  let filteredNotas = $derived(
    notas.filter((n) => {
      if (statusFilter !== "todos" && n.estado !== statusFilter) return false;
      if (authorFilter && n.autor !== authorFilter) return false;
      if (topicFilter && n.tema !== topicFilter) return false;
      return true;
    })
  );

  onMount(async () => {
    await loadNotas();
  });

  async function loadNotas() {
    loading = true;
    try {
      const res = await fetch("/api/v1/notas");
      if (res.ok) {
        const data = await res.json();
        notas = (data.items ?? data ?? []).map((n: Record<string, unknown>) => ({
          id: n.id ?? "",
          titulo: n.titulo ?? "",
          autor: n.autor ?? "",
          tema: n.tema ?? "",
          estado: n.estado ?? "borrador",
          boletin_id: n.boletin_id ?? null,
          recibido: n.recibido ?? n.created_at ?? "",
        }));
      }
    } catch {
      // Show empty state
    } finally {
      loading = false;
    }
  }

  function handleEdit(e: MouseEvent, id: string) {
    e.stopPropagation();
    goto(`/notas/${id}/editar`);
  }

  function handleDeleteClick(e: MouseEvent, id: string) {
    e.stopPropagation();
    confirmDeleteId = id;
  }

  async function confirmDelete() {
    if (!confirmDeleteId) return;
    deleting = true;
    try {
      const res = await fetch(`/api/v1/notas/${confirmDeleteId}`, {
        method: "DELETE",
      });
      if (res.ok) {
        notas = notas.filter((n) => n.id !== confirmDeleteId);
        confirmDeleteId = null;
      } else {
        const data = await res.json().catch(() => null);
        alert(data?.detail?.message || "Error al eliminar la nota");
      }
    } catch {
      alert("Error de conexión al eliminar la nota");
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
</script>

<svelte:head>
  <title>Notas - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-8">
    <PageHeader title="Notas" description="Gestión de notas del sistema">
      {#snippet actions()}
        <a
          href="/notas/nueva"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Subir Nota
        </a>
      {/snippet}
    </PageHeader>

    <div class="flex items-center gap-3">
      <select
        bind:value={statusFilter}
        class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
      >
        <option value="todos">Todos los estados</option>
        <option value="borrador">Borrador</option>
        <option value="pendiente">Pendiente</option>
        <option value="aprobada">Aprobada</option>
        <option value="rechazada">Rechazada</option>
        <option value="publicada">Publicada</option>
      </select>

      {#if topics.length > 0}
        <select
          bind:value={topicFilter}
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
        >
          <option value="">Todos los temas</option>
          {#each topics as topic}
            <option value={topic}>{topic}</option>
          {/each}
        </select>
      {/if}
    </div>

    {#if loading}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-8">
        <div class="space-y-3">
          {#each Array(5) as _}
            <div class="h-10 bg-slate-100 dark:bg-slate-800 rounded animate-pulse"></div>
          {/each}
        </div>
      </div>
    {:else if filteredNotas.length === 0}
      <EmptyState
        title="No hay notas"
        description="Sube tu primera nota para comenzar."
        actionLabel="Subir Nota"
        actionHref="/notas/nueva"
      />
    {:else}
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th>Título</th>
                <th>Autor</th>
                <th>Tema</th>
                <th class="text-center">Estado</th>
                <th>Boletín</th>
                <th>Recibido</th>
                <th class="text-right" style="width: 90px">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each filteredNotas as nota (nota.id)}
                <tr
                  class="cursor-pointer"
                  onclick={() => goto(`/notas/${nota.id}`)}
                >
                  <td>
                    <span class="font-medium text-slate-800 dark:text-slate-100">{nota.titulo}</span>
                  </td>
                  <td>{nota.autor || "—"}</td>
                  <td>{nota.tema || "—"}</td>
                  <td class="text-center">
                    <StatusBadge status={nota.estado} />
                  </td>
                  <td>{nota.boletin_id ? "—" : "—"}</td>
                  <td class="text-slate-500 dark:text-slate-400">{formatDate(nota.recibido)}</td>
                  <td class="text-right">
                    <div class="flex items-center justify-end gap-1">
                      <button
                        onclick={(e) => handleEdit(e, nota.id)}
                        class="p-1.5 rounded-lg text-slate-400 hover:text-teal-600 hover:bg-teal-50 dark:hover:bg-teal-950 transition-colors"
                        aria-label="Editar nota"
                        title="Editar"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                          <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                          <path d="m15 5 4 4" />
                        </svg>
                      </button>
                      <button
                        onclick={(e) => handleDeleteClick(e, nota.id)}
                        class="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950 transition-colors"
                        aria-label="Eliminar nota"
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

  {#if confirmDeleteId}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onclick={cancelDelete} onkeydown={(e) => { if (e.key === 'Escape') cancelDelete(); }} role="dialog" aria-modal="true">
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
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">Eliminar nota</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">Esta acción no se puede deshacer.</p>
          </div>
        </div>
        <p class="text-sm text-slate-600 dark:text-slate-300 mb-6">
          ¿Estás seguro de que querés eliminar esta nota permanentemente?
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
</AppLayout>

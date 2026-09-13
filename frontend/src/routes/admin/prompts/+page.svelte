<script lang="ts">
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";
  import StatusBadge from "$lib/components/StatusBadge.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";

  interface Prompt {
    id: string;
    nombre: string;
    tipo: string;
    activo: boolean;
    creado_por: string;
    created_at: string;
  }

  let prompts = $state<Prompt[]>([]);
  let loading = $state(true);

  onMount(async () => {
    await loadPrompts();
  });

  async function loadPrompts() {
    loading = true;
    try {
      const res = await fetch("/api/v1/prompts");
      if (res.ok) {
        const data = await res.json();
        prompts = (data.items ?? data ?? []).map((p: Record<string, unknown>) => ({
          id: p.id ?? "",
          nombre: p.nombre ?? "",
          tipo: p.tipo ?? "general",
          activo: Boolean(p.activo ?? true),
          creado_por: p.creado_por ?? "",
          created_at: p.created_at ?? "",
        }));
      }
    } catch {
      // Show empty state
    } finally {
      loading = false;
    }
  }

  function toggleActive(id: string) {
    prompts = prompts.map((p) =>
      p.id === id ? { ...p, activo: !p.activo } : p
    );
    fetch(`/api/v1/prompts/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ activo: prompts.find((p) => p.id === id)?.activo }),
    }).catch(() => {
      prompts = prompts.map((p) =>
        p.id === id ? { ...p, activo: !p.activo } : p
      );
    });
  }

  function deletePrompt(id: string) {
    if (!confirm("¿Eliminar este prompt?")) return;
    fetch(`/api/v1/prompts/${id}`, { method: "DELETE" })
      .then(() => {
        prompts = prompts.filter((p) => p.id !== id);
      })
      .catch(() => {});
  }

  function tipoVariant(tipo: string): "info" | "success" | "warning" | "default" {
    const map: Record<string, "info" | "success" | "warning" | "default"> = {
      generacion: "info",
      revision: "warning",
      resumen: "success",
    };
    return map[tipo] ?? "default";
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
  <title>Prompts - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-8">
    <PageHeader title="Prompts" description="Gestionar prompts del sistema de IA">
      {#snippet actions()}
        <a
          href="/admin/prompts/nuevo"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Nuevo Prompt
        </a>
      {/snippet}
    </PageHeader>

    {#if loading}
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-8">
        <div class="space-y-3">
          {#each Array(5) as _}
            <div class="h-10 bg-slate-100 dark:bg-slate-800 rounded animate-pulse"></div>
          {/each}
        </div>
      </div>
    {:else if prompts.length === 0}
      <EmptyState
        title="No hay prompts"
        description="Crea tu primer prompt para comenzar."
        actionLabel="Nuevo Prompt"
        actionHref="/admin/prompts/nuevo"
      />
    {:else}
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th>Nombre</th>
                <th class="text-center">Tipo</th>
                <th class="text-center">Activo</th>
                <th>Creado por</th>
                <th class="text-right" style="width: 120px">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each prompts as prompt (prompt.id)}
                <tr>
                  <td>
                    <span class="font-medium text-slate-800 dark:text-slate-100">{prompt.nombre}</span>
                  </td>
                  <td class="text-center">
                    <StatusBadge status={prompt.tipo} variant={tipoVariant(prompt.tipo)} />
                  </td>
                  <td class="text-center">
                    <button
                      onclick={() => toggleActive(prompt.id)}
                      aria-label={prompt.activo ? "Desactivar prompt" : "Activar prompt"}
                      class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors {prompt.activo ? 'bg-teal-600' : 'bg-slate-300 dark:bg-slate-600'}"
                    >
                      <span
                        class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform {prompt.activo ? 'translate-x-4.5' : 'translate-x-1'}"
                      ></span>
                    </button>
                  </td>
                   <td class="text-slate-500 dark:text-slate-400">{prompt.creado_por || "—"}</td>
                  <td class="text-right">
                    <div class="flex items-center justify-end gap-2">
                      <a
                        href="/admin/prompts/{prompt.id}"
                        class="text-teal-600 hover:text-teal-700 text-sm font-medium"
                      >
                        Editar
                      </a>
                      <button
                        onclick={() => deletePrompt(prompt.id)}
                        class="text-red-500 hover:text-red-600 text-sm font-medium"
                      >
                        Eliminar
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

<script lang="ts">
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";
  import StatusBadge from "$lib/components/StatusBadge.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";

  interface User {
    id: string;
    nombre: string;
    email: string;
    rol: string;
    activo: boolean;
    ultimo_acceso: string;
  }

  let users = $state<User[]>([]);
  let loading = $state(true);

  onMount(async () => {
    await loadUsers();
  });

  async function loadUsers() {
    loading = true;
    try {
      const res = await fetch("/api/v1/usuarios");
      if (res.ok) {
        const data = await res.json();
        users = (data.items ?? data ?? []).map((u: Record<string, unknown>) => ({
          id: u.id ?? "",
          nombre: u.nombre ?? "",
          email: u.email ?? "",
          rol: u.rol ?? "colaborador",
          activo: Boolean(u.activo ?? true),
          ultimo_acceso: u.ultimo_acceso ?? "",
        }));
      }
    } catch {
      // Show empty state
    } finally {
      loading = false;
    }
  }

  async function toggleActive(id: string) {
    const user = users.find((u) => u.id === id);
    if (!user) return;

    users = users.map((u) =>
      u.id === id ? { ...u, activo: !u.activo } : u
    );

    try {
      await fetch(`/api/v1/usuarios/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ activo: user.activo }),
      });
    } catch {
      users = users.map((u) =>
        u.id === id ? { ...u, activo: !u.activo } : u
      );
    }
  }

  function deleteUser(id: string) {
    if (!confirm("¿Eliminar este usuario?")) return;
    fetch(`/api/v1/usuarios/${id}`, { method: "DELETE" })
      .then(() => {
        users = users.filter((u) => u.id !== id);
      })
      .catch(() => {});
  }

  function rolVariant(rol: string): "danger" | "info" | "default" {
    const map: Record<string, "danger" | "info" | "default"> = {
      director: "danger",
      admin: "danger",
      editor: "info",
      colaborador: "default",
    };
    return map[rol] ?? "default";
  }

  function formatDate(iso: string): string {
    if (!iso) return "Nunca";
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
  <title>Usuarios - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-8">
    <PageHeader title="Usuarios" description="Gestionar usuarios y permisos del sistema">
      {#snippet actions()}
        <a
          href="/admin/users/nuevo"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Nuevo Usuario
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
    {:else if users.length === 0}
      <EmptyState
        title="No hay usuarios"
        description="Crea el primer usuario para comenzar."
        actionLabel="Nuevo Usuario"
        actionHref="/admin/users/nuevo"
      />
    {:else}
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Email</th>
                <th class="text-center">Rol</th>
                <th class="text-center">Activo</th>
                <th>Último Acceso</th>
                <th class="text-right" style="width: 120px">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each users as user (user.id)}
                <tr>
                  <td>
                    <span class="font-medium text-slate-800 dark:text-slate-100">{user.nombre}</span>
                  </td>
                  <td class="text-slate-500 dark:text-slate-400">{user.email}</td>
                  <td class="text-center">
                    <StatusBadge status={user.rol} variant={rolVariant(user.rol)} />
                  </td>
                  <td class="text-center">
                    <button
                      onclick={() => toggleActive(user.id)}
                      aria-label={user.activo ? "Desactivar usuario" : "Activar usuario"}
                      class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors {user.activo ? 'bg-teal-600' : 'bg-slate-300 dark:bg-slate-600'}"
                    >
                      <span
                        class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform {user.activo ? 'translate-x-4.5' : 'translate-x-1'}"
                      ></span>
                    </button>
                  </td>
                  <td class="text-slate-500 dark:text-slate-400">{formatDate(user.ultimo_acceso)}</td>
                  <td class="text-right">
                    <div class="flex items-center justify-end gap-2">
                      <a
                        href="/admin/users/{user.id}"
                        class="text-teal-600 hover:text-teal-700 text-sm font-medium"
                      >
                        Editar
                      </a>
                      <button
                        onclick={() => deleteUser(user.id)}
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

<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";
  import StatusBadge from "$lib/components/StatusBadge.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";

  interface Incidente {
    id: string;
    nombre: string;
    producto: string;
    patogeno: string;
    pais: string;
    riesgo: string;
    severidad: string;
    fecha: string;
    estado: string;
    boletin_id: string | null;
  }

  let incidentes = $state<Incidente[]>([]);
  let loading = $state(true);
  let countryFilter = $state("");
  let pathogenFilter = $state("");
  let riskFilter = $state("");
  let statusFilter = $state("todos");
  let dateFrom = $state("");
  let dateTo = $state("");
  let bulletinFilter = $state("");

  let countries = $derived(
    [...new Set(incidentes.map((i) => i.pais).filter(Boolean))].sort()
  );
  let pathogens = $derived(
    [...new Set(incidentes.map((i) => i.patogeno).filter(Boolean))].sort()
  );

  let filteredIncidentes = $derived(
    incidentes.filter((i) => {
      if (countryFilter && i.pais !== countryFilter) return false;
      if (pathogenFilter && i.patogeno !== pathogenFilter) return false;
      if (riskFilter && i.riesgo !== riskFilter) return false;
      if (statusFilter !== "todos" && i.estado !== statusFilter) return false;
      if (bulletinFilter && i.boletin_id !== bulletinFilter) return false;
      if (dateFrom && i.fecha && i.fecha < dateFrom) return false;
      if (dateTo && i.fecha && i.fecha > dateTo) return false;
      return true;
    })
  );

  onMount(async () => {
    await loadIncidentes();
  });

  async function loadIncidentes() {
    loading = true;
    try {
      const res = await fetch("/api/v1/incidentes");
      if (res.ok) {
        const data = await res.json();
        incidentes = (data.items ?? data ?? []).map((i: Record<string, unknown>) => ({
          id: i.id ?? "",
          nombre: i.nombre ?? "",
          producto: i.producto ?? "",
          patogeno: i.patogeno ?? "",
          pais: i.pais ?? "",
          riesgo: i.riesgo ?? "bajo",
          severidad: i.severidad ?? "leve",
          fecha: i.fecha ?? "",
          estado: i.estado ?? "pendiente",
          boletin_id: i.boletin_id ?? null,
        }));
      }
    } catch {
      // Show empty state
    } finally {
      loading = false;
    }
  }

  function handleRowClick(id: string) {
    goto(`/incidentes/${id}`);
  }

  function handleOpenClick(e: MouseEvent, id: string) {
    e.stopPropagation();
    goto(`/incidentes/${id}`);
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

  function riskVariant(riesgo: string): "danger" | "warning" | "info" | "default" {
    const map: Record<string, "danger" | "warning" | "info" | "default"> = {
      alto: "danger",
      medio: "warning",
      bajo: "info",
    };
    return map[riesgo] ?? "default";
  }

  function severityVariant(sev: string): "danger" | "warning" | "info" | "default" {
    const map: Record<string, "danger" | "warning" | "info" | "default"> = {
      critica: "danger",
      alta: "danger",
      media: "warning",
      baja: "info",
    };
    return map[sev] ?? "default";
  }
</script>

<svelte:head>
  <title>Incidentes - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-8">
    <PageHeader title="Incidentes" description="Vista global de incidentes de seguridad alimentaria">
      {#snippet actions()}
        <a
          href="/incidentes/nuevo"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Nueva Consulta
        </a>
      {/snippet}
    </PageHeader>

    <div class="flex flex-wrap items-center gap-3">
      <select
        bind:value={countryFilter}
        class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
      >
        <option value="">Todos los países</option>
        {#each countries as country}
          <option value={country}>{country}</option>
        {/each}
      </select>

      <select
        bind:value={pathogenFilter}
        class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
      >
        <option value="">Todos los patógenos</option>
        {#each pathogens as p}
          <option value={p}>{p}</option>
        {/each}
      </select>

      <select
        bind:value={riskFilter}
        class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
      >
        <option value="">Todos los riesgos</option>
        <option value="alto">Alto</option>
        <option value="medio">Medio</option>
        <option value="bajo">Bajo</option>
      </select>

      <select
        bind:value={statusFilter}
        class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
      >
        <option value="todos">Todos los estados</option>
        <option value="pendiente">Pendiente</option>
        <option value="en_investigacion">En Investigación</option>
        <option value="confirmado">Confirmado</option>
        <option value="resuelto">Resuelto</option>
        <option value="cerrado">Cerrado</option>
      </select>

      <div class="flex items-center gap-2">
        <input
          type="date"
          bind:value={dateFrom}
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
        />
        <span class="text-slate-400">—</span>
        <input
          type="date"
          bind:value={dateTo}
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
        />
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
    {:else if filteredIncidentes.length === 0}
      <EmptyState
        title="No hay incidentes"
        description="No se encontraron incidentes con los filtros seleccionados."
        actionLabel="Nueva Consulta"
        actionHref="/incidentes/nuevo"
      />
    {:else}
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th>Incidente</th>
                <th>Producto</th>
                <th>Patógeno</th>
                <th>País</th>
                <th class="text-center">Riesgo</th>
                <th class="text-center">Severidad</th>
                <th>Fecha</th>
                <th class="text-center">Estado</th>
                <th>Boletín</th>
                <th class="text-right" style="width: 80px">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each filteredIncidentes as inc (inc.id)}
                <tr
                  class="cursor-pointer"
                  onclick={() => handleRowClick(inc.id)}
                >
                  <td>
                    <span class="font-medium text-slate-800 dark:text-slate-100">{inc.nombre}</span>
                  </td>
                  <td>{inc.producto || "—"}</td>
                  <td>{inc.patogeno || "—"}</td>
                  <td>{inc.pais || "—"}</td>
                  <td class="text-center">
                    <StatusBadge status={inc.riesgo} variant={riskVariant(inc.riesgo)} />
                  </td>
                  <td class="text-center">
                    <StatusBadge status={inc.severidad} variant={severityVariant(inc.severidad)} />
                  </td>
                  <td class="text-slate-500 dark:text-slate-400">{formatDate(inc.fecha)}</td>
                  <td class="text-center">
                    <StatusBadge status={inc.estado} />
                  </td>
                  <td>{inc.boletin_id ? "—" : "—"}</td>
                  <td class="text-right">
                    <button
                      onclick={(e) => handleOpenClick(e, inc.id)}
                      class="text-teal-600 hover:text-teal-700 text-sm font-medium"
                    >
                      Abrir
                    </button>
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

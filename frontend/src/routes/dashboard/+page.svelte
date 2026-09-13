<script lang="ts">
  import { auth } from "$lib/stores/auth";
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";

  let loading = $state(true);
  let stats = $state({
    boletinesActivos: 0,
    notasPendientes: 0,
    incidentesPeriodo: 0,
    tiempoPromedio: "—",
  });

  interface Bulletin {
    id: string;
    nombre: string;
    periodo: string;
    estado: string;
    progreso: number;
    ultimaActualizacion: string;
  }

  let bulletins: Bulletin[] = $state([]);

  interface Activity {
    id: string;
    tipo: string;
    descripcion: string;
    fecha: string;
  }

  let activities: Activity[] = $state([]);

  onMount(async () => {
    if (!$auth) {
      window.location.href = "/login";
      return;
    }
    await loadDashboardData();
    loading = false;
  });

  async function loadDashboardData() {
    try {
      const [statsRes, bulletinsRes, activityRes] = await Promise.allSettled([
        fetch("/api/v1/dashboard/stats"),
        fetch("/api/v1/boletines?limit=5"),
        fetch("/api/v1/activity?limit=6"),
      ]);

      if (statsRes.status === "fulfilled" && statsRes.value.ok) {
        const data = await statsRes.value.json();
        stats = {
          boletinesActivos: data.boletines_activos ?? 0,
          notasPendientes: data.notas_pendientes ?? 0,
          incidentesPeriodo: data.incidentes_periodo ?? 0,
          tiempoPromedio: data.tiempo_promedio ?? "—",
        };
      }

      if (bulletinsRes.status === "fulfilled" && bulletinsRes.value.ok) {
        const data = await bulletinsRes.value.json();
        bulletins = (data.items ?? data ?? []).map((b: Record<string, unknown>) => ({
          id: b.id ?? "",
          nombre: b.nombre ?? "",
          periodo: b.periodo ?? `${b.periodo_inicio ?? ""} — ${b.periodo_fin ?? ""}`,
          estado: b.estado ?? "",
          progreso: Number(b.progreso ?? 0),
          ultimaActualizacion: b.ultima_actualizacion ?? b.fecha_creacion ?? "",
        }));
      }

      if (activityRes.status === "fulfilled" && activityRes.value.ok) {
        const data = await activityRes.value.json();
        activities = (data.items ?? data ?? []).map((a: Record<string, unknown>) => ({
          id: a.id ?? "",
          tipo: a.tipo ?? "",
          descripcion: a.descripcion ?? "",
          fecha: a.fecha ?? "",
        }));
      }
    } catch {
      // Dashboard will show zeros / empty states
    }
  }

  const statCards = $derived([
    {
      label: "Boletines Activos",
      value: stats.boletinesActivos,
      icon: "boletines",
      color: "teal",
    },
    {
      label: "Notas Pendientes",
      value: stats.notasPendientes,
      icon: "notas",
      color: "amber",
    },
    {
      label: "Incidentes del Período",
      value: stats.incidentesPeriodo,
      icon: "incidentes",
      color: "red",
    },
    {
      label: "Tiempo Promedio",
      value: stats.tiempoPromedio,
      icon: "tiempo",
      color: "blue",
    },
  ]);

  function estadoBadge(estado: string): string {
    const map: Record<string, string> = {
      activo: "bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-300",
      borrador: "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300",
      publicado: "bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-300",
      archivado: "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400",
      en_curso: "bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300",
    };
    return map[estado] ?? "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300";
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

  function activityIcon(tipo: string): string {
    const map: Record<string, string> = {
      nota_creada: "📝",
      nota_aprobada: "✅",
      boletin_generado: "📋",
      incidente_reportado: "⚠️",
      usuario_creado: "👤",
    };
    return map[tipo] ?? "📌";
  }
</script>

<svelte:head>
  <title>Dashboard - NIA</title>
</svelte:head>

{#if loading}
  <div class="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
    <div class="flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-teal-200 border-t-teal-600 rounded-full animate-spin"></div>
      <p class="text-sm text-slate-500 dark:text-slate-400 font-medium">Cargando dashboard...</p>
    </div>
  </div>
{:else}
  <AppLayout>
    <div class="space-y-10">
      <div class="mb-4">
        <h1 class="text-2xl font-semibold text-slate-800 dark:text-slate-100">Dashboard</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Bienvenido, {$auth?.nombre}. Resumen general del sistema.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {#each statCards as card}
          <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-6 flex items-center gap-4">
            <div class="w-11 h-11 rounded-lg flex items-center justify-center shrink-0
              {card.color === 'teal' ? 'bg-teal-100 text-teal-600' : ''}
              {card.color === 'amber' ? 'bg-amber-100 text-amber-600' : ''}
              {card.color === 'red' ? 'bg-red-100 text-red-600' : ''}
              {card.color === 'blue' ? 'bg-blue-100 text-blue-600' : ''}"
            >
              {#if card.icon === "boletines"}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
              {:else if card.icon === "notas"}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
              {:else if card.icon === "incidentes"}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
                  <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              {:else}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
              {/if}
            </div>
            <div>
              <p class="text-2xl font-semibold text-slate-800 dark:text-slate-100">{card.value}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{card.label}</p>
            </div>
          </div>
        {/each}
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700">
          <div class="px-5 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
            <h2 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">Boletines Activos</h2>
            <a href="/boletines" class="text-xs font-medium text-teal-600 hover:text-teal-700">
              Ver todos
            </a>
          </div>
          {#if bulletins.length === 0}
            <div class="p-8 text-center text-sm text-slate-400 dark:text-slate-500">No hay boletines para mostrar.</div>
          {:else}
            <div class="overflow-x-auto">
              <table>
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Período</th>
                    <th>Estado</th>
                    <th>Progreso</th>
                    <th>Última Actualización</th>
                  </tr>
                </thead>
                <tbody>
                  {#each bulletins as b (b.id)}
                    <tr>
                      <td class="font-medium text-slate-800 dark:text-slate-100">{b.nombre}</td>
                      <td>{b.periodo}</td>
                      <td>
                        <span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium {estadoBadge(b.estado)}">
                          {b.estado.replace("_", " ")}
                        </span>
                      </td>
                      <td>
                        <div class="flex items-center gap-2">
                          <div class="w-20 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div
                              class="h-full bg-teal-500 rounded-full transition-all"
                              style="width: {Math.min(b.progreso, 100)}%"
                            ></div>
                          </div>
                          <span class="text-xs text-slate-500 dark:text-slate-400">{b.progreso}%</span>
                        </div>
                      </td>
                      <td class="text-slate-500 dark:text-slate-400">{formatDate(b.ultimaActualizacion)}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {/if}
        </div>

        <div class="space-y-6">
          <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
            <h2 class="font-semibold text-slate-800 dark:text-slate-100 text-sm mb-4">Acciones Rápidas</h2>
            <div class="flex flex-col gap-2">
              <a
                href="/boletines/nueva"
                class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-teal-50 dark:hover:bg-teal-950 transition-colors group"
              >
                <div class="w-8 h-8 rounded-lg bg-teal-100 flex items-center justify-center group-hover:bg-teal-200 transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-teal-600">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-slate-700 dark:text-slate-200">Nuevo Boletín</span>
              </a>
              <a
                href="/notas/nueva"
                class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-amber-50 dark:hover:bg-amber-950 transition-colors group"
              >
                <div class="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center group-hover:bg-amber-200 transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-amber-600">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-slate-700 dark:text-slate-200">Subir Nota</span>
              </a>
              <a
                href="/incidentes/nuevo"
                class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-950 transition-colors group"
              >
                <div class="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center group-hover:bg-red-200 transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-red-600">
                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-slate-700 dark:text-slate-200">Reportar Incidente</span>
              </a>
              <a
                href="/admin/usuarios"
                class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-950 transition-colors group"
              >
                <div class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-blue-600">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <line x1="19" y1="8" x2="19" y2="14" />
                    <line x1="22" y1="11" x2="16" y2="11" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-slate-700 dark:text-slate-200">Gestionar Usuarios</span>
              </a>
            </div>
          </div>

          <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
            <h2 class="font-semibold text-slate-800 dark:text-slate-100 text-sm mb-4">Actividad Reciente</h2>
            {#if activities.length === 0}
              <p class="text-sm text-slate-400 dark:text-slate-500">Sin actividad reciente.</p>
            {:else}
              <div class="flex flex-col gap-3">
                {#each activities as act (act.id)}
                  <div class="flex items-start gap-3">
                    <span class="text-base mt-0.5">{activityIcon(act.tipo)}</span>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm text-slate-700 dark:text-slate-200 leading-snug">{act.descripcion}</p>
                      <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{formatDate(act.fecha)}</p>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
{/if}

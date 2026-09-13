<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";

  const notaId = $derived(page.params.id);

  let titulo = $state("");
  let autor = $state("");
  let fuente = $state("");
  let tema = $state("");
  let archivoTipo = $state("");
  let archivoUrl = $state("");
  let submitting = $state(false);
  let loading = $state(true);
  let error = $state("");

  const temas = [
    "Contaminación",
    "Brotes",
    "Regulaciones",
    "Recalls",
    "Alérgenos",
    "Adulteración",
    "Seguridad Alimentaria",
    "Otros",
  ];

  onMount(async () => {
    try {
      const res = await fetch(`/api/v1/notas/${notaId}`);
      if (res.ok) {
        const nota = await res.json();
        titulo = nota.titulo || "";
        autor = nota.autor || "";
        fuente = nota.fuente || "";
        tema = nota.tema || "";
        archivoTipo = nota.archivo_tipo || "";
        archivoUrl = nota.archivo_url || "";
      } else {
        error = "No se pudo cargar la nota";
      }
    } catch {
      error = "Error de conexión";
    } finally {
      loading = false;
    }
  });

  async function handleSubmit(e: Event) {
    e.preventDefault();
    if (!titulo.trim()) return;

    submitting = true;
    error = "";

    try {
      const res = await fetch(`/api/v1/notas/${notaId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          titulo: titulo.trim(),
          autor: autor.trim() || null,
          fuente: fuente.trim() || null,
          tema: tema || null,
        }),
      });

      if (res.ok) {
        goto("/notas");
      } else {
        const data = await res.json().catch(() => null);
        error = data?.detail?.message || "Error al actualizar la nota";
      }
    } catch {
      error = "Error de conexión al actualizar la nota";
    } finally {
      submitting = false;
    }
  }
</script>

<svelte:head>
  <title>Editar Nota - NIA</title>
</svelte:head>

<AppLayout>
  <div class="max-w-2xl space-y-8">
    <PageHeader title="Editar Nota" description="Modificá los datos de la nota" />

    {#if loading}
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
        <div class="space-y-4">
          {#each Array(4) as _}
            <div class="h-10 bg-slate-100 dark:bg-slate-800 rounded animate-pulse"></div>
          {/each}
        </div>
      </div>
    {:else if error && !titulo}
      <div class="p-4 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-xl text-sm text-red-600 dark:text-red-300">
        {error}
      </div>
    {:else}
      <form
        onsubmit={handleSubmit}
        class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 space-y-5"
      >
        <div>
          <label for="titulo" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Título *
          </label>
          <input
            id="titulo"
            type="text"
            bind:value={titulo}
            placeholder="Título de la nota"
            class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            required
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="autor" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
              Autor
            </label>
            <input
              id="autor"
              type="text"
              bind:value={autor}
              placeholder="Nombre del autor"
              class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            />
          </div>
          <div>
            <label for="fuente" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
              Fuente
            </label>
            <input
              id="fuente"
              type="text"
              bind:value={fuente}
              placeholder="Fuente de la nota"
              class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            />
          </div>
        </div>

        <div>
          <label for="tema" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Tema
          </label>
          <select
            id="tema"
            bind:value={tema}
            class="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
          >
            <option value="">Seleccionar tema</option>
            {#each temas as t}
              <option value={t}>{t}</option>
            {/each}
          </select>
        </div>

        {#if archivoTipo}
          <div class="p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg">
            <p class="text-sm text-slate-500 dark:text-slate-400">
              Archivo actual: <span class="font-medium text-slate-700 dark:text-slate-200 uppercase">.{archivoTipo}</span>
            </p>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
              Para reemplazar el archivo, subí una nueva nota.
            </p>
          </div>
        {/if}

        {#if error}
          <div class="p-3 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-300">
            {error}
          </div>
        {/if}

        <div class="flex items-center justify-end gap-3 pt-2">
          <a
            href="/notas"
            class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-800 dark:hover:text-slate-100 transition-colors"
          >
            Cancelar
          </a>
          <button
            type="submit"
            disabled={submitting || !titulo.trim()}
            class="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? "Guardando..." : "Guardar cambios"}
          </button>
        </div>
      </form>
    {/if}
  </div>
</AppLayout>

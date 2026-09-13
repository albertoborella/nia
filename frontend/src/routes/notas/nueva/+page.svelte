<script lang="ts">
  import { goto } from "$app/navigation";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";

  let titulo = $state("");
  let autor = $state("");
  let fuente = $state("");
  let tema = $state("");
  let archivo = $state<File | null>(null);
  let submitting = $state(false);
  let dragOver = $state(false);
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

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragOver = false;
    const file = e.dataTransfer?.files?.[0];
    if (file) validateAndSetFile(file);
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragOver = true;
  }

  function handleDragLeave() {
    dragOver = false;
  }

  function handleFileSelect(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) validateAndSetFile(file);
  }

  function validateAndSetFile(file: File) {
    const allowed = [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"];
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!allowed.includes(ext)) {
      error = "Solo se permiten archivos PDF, DOC, DOCX, TXT, RTF o ODT";
      return;
    }
    error = "";
    archivo = file;
  }

  function removeFile() {
    archivo = null;
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    if (!titulo.trim() || !archivo) return;

    submitting = true;
    error = "";

    try {
      const formData = new FormData();
      formData.append("titulo", titulo.trim());
      formData.append("autor", autor.trim());
      formData.append("fuente", fuente.trim());
      formData.append("tema", tema);
      formData.append("archivo", archivo);

      const res = await fetch("/api/v1/notas", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        goto("/notas");
      } else {
        const data = await res.json().catch(() => null);
        error = data?.detail?.message || "Error al subir la nota";
      }
    } catch {
      error = "Error de conexión al subir la nota";
    } finally {
      submitting = false;
    }
  }
</script>

<svelte:head>
  <title>Subir Nota - NIA</title>
</svelte:head>

<AppLayout>
  <div class="max-w-2xl space-y-8">
    <PageHeader title="Subir Nota" description="Carga una nueva nota al sistema" />

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

      <div>
        <label for="file-input" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
          Archivo *
        </label>
        {#if archivo}
          <div class="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5 text-teal-500 shrink-0">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <span class="text-sm text-slate-700 dark:text-slate-200 flex-1 truncate">{archivo.name}</span>
            <span class="text-xs text-slate-400 dark:text-slate-500">{(archivo.size / 1024).toFixed(0)} KB</span>
            <button
              type="button"
              onclick={removeFile}
              aria-label="Eliminar archivo"
              class="text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        {:else}
          <div
            class="border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer
              {dragOver ? 'border-teal-400 bg-teal-50 dark:bg-teal-950' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'}"
            ondrop={handleDrop}
            ondragover={handleDragOver}
            ondragleave={handleDragLeave}
            onclick={() => document.getElementById("file-input")?.click()}
            onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') document.getElementById("file-input")?.click(); }}
            role="button"
            tabindex="0"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-8 h-8 text-slate-400 dark:text-slate-500 mx-auto mb-2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              Arrastra un archivo aquí o <span class="text-teal-600 dark:text-teal-300 font-medium">selecciona</span>
            </p>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">PDF, DOC, DOCX, TXT, RTF o ODT, máximo 10 MB</p>
            <input
              id="file-input"
              type="file"
              accept=".pdf,.doc,.docx,.txt,.rtf,.odt"
              class="hidden"
              onchange={handleFileSelect}
            />
          </div>
        {/if}
      </div>

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
          disabled={submitting || !titulo.trim() || !archivo}
          class="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {submitting ? "Subiendo..." : "Subir Nota"}
        </button>
      </div>
    </form>
  </div>
</AppLayout>

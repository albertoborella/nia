<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import AppLayout from "$lib/components/AppLayout.svelte";
  import SectionSidebar from "$lib/components/SectionSidebar.svelte";

  let content = $state("");
  let saving = $state(false);
  let loading = $state(true);
  let lastSaved = $state<string | null>(null);
  let markedComplete = $state(false);

  let id = $derived($page.params.id);

  onMount(async () => {
    await loadContent();
  });

  async function loadContent() {
    loading = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones/editorial`);
      if (res.ok) {
        const data = await res.json();
        const cont = data.contenido ?? {};
        content = cont.text ?? (typeof cont === "string" ? cont : "");
      }
    } catch {
      // Show empty editor
    } finally {
      loading = false;
    }
  }

  async function saveContent() {
    saving = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/secciones/editorial`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contenido: { text: content } }),
      });
      if (res.ok) {
        lastSaved = new Date().toLocaleTimeString("es-AR");
      }
    } catch {
      // Handle error
    } finally {
      saving = false;
    }
  }

  async function markComplete() {
    saving = true;
    try {
      const res = await fetch(`/api/v1/boletines/${id}/completar-seccion`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tipo: "editorial" }),
      });
      if (res.ok) {
        markedComplete = true;
        setTimeout(() => goto(`/boletines/${id}`), 1200);
      }
    } catch {
      // Handle error
    } finally {
      saving = false;
    }
  }

  function insertMarkdown(prefix: string, suffix = "") {
    const textarea = document.querySelector("#editor-content") as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = content.substring(start, end);
    const replacement = `${prefix}${selected || "texto"}${suffix}`;

    content = content.substring(0, start) + replacement + content.substring(end);

    requestAnimationFrame(() => {
      textarea.focus();
      const cursorPos = start + prefix.length + (selected ? selected.length : 4);
      textarea.setSelectionRange(cursorPos, cursorPos);
    });
  }
</script>

<svelte:head>
  <title>Editorial - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-6">
    <div class="flex items-center gap-4">
      <a
        href="/boletines/{id}"
        aria-label="Volver al boletín"
        class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </a>
      <div class="flex-1 min-w-0">
        <h1 class="text-xl font-semibold text-slate-800 dark:text-slate-100">Editorial</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Redacción del editorial del boletín</p>
      </div>
      {#if lastSaved}
        <span class="text-xs text-slate-400 dark:text-slate-500">Guardado {lastSaved}</span>
      {/if}
      <button
        onclick={saveContent}
        disabled={saving}
        class="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-50 transition-colors"
      >
        {saving ? "Guardando..." : "Guardar"}
      </button>
      <button
        onclick={markComplete}
        disabled={saving || markedComplete}
        class="px-4 py-2 text-sm font-medium rounded-lg transition-colors
          {markedComplete
            ? 'text-teal-700 bg-teal-100'
            : 'text-teal-700 bg-teal-100 hover:bg-teal-200'}"
      >
        {markedComplete ? "Completada ✓" : "Marcar como Completada"}
      </button>
    </div>

    <div class="grid grid-cols-[240px_1fr] gap-6">
      <SectionSidebar activeSection="editorial" />

      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="flex items-center gap-1 px-3 py-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
        <button
          onclick={() => insertMarkdown("**", "**")}
          class="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
          title="Negrita"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
            <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
            <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
          </svg>
        </button>
        <button
          onclick={() => insertMarkdown("*", "*")}
          class="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
          title="Cursiva"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
            <line x1="19" y1="4" x2="10" y2="4" />
            <line x1="14" y1="20" x2="5" y2="20" />
            <line x1="15" y1="4" x2="9" y2="20" />
          </svg>
        </button>
        <button
          onclick={() => insertMarkdown("## ")}
          class="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
          title="Título"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <path d="M4 12h8M4 18V6M12 18V6M17 12l3-2v12" />
          </svg>
        </button>
        <button
          onclick={() => insertMarkdown("\n- ")}
          class="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
          title="Lista"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <line x1="8" y1="6" x2="21" y2="6" />
            <line x1="8" y1="12" x2="21" y2="12" />
            <line x1="8" y1="18" x2="21" y2="18" />
            <line x1="3" y1="6" x2="3.01" y2="6" />
            <line x1="3" y1="12" x2="3.01" y2="12" />
            <line x1="3" y1="18" x2="3.01" y2="18" />
          </svg>
        </button>
        <button
          onclick={() => insertMarkdown("\n> ")}
          class="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
          title="Cita"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z" />
            <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z" />
          </svg>
        </button>
        <div class="w-px h-5 bg-slate-300 mx-1"></div>
        <button
          onclick={() => insertMarkdown("[", "](url)")}
          class="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
          title="Enlace"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
        </button>
      </div>

      {#if loading}
        <div class="p-6 space-y-3">
          {#each Array(8) as _}
            <div class="h-4 bg-slate-100 dark:bg-slate-800 rounded animate-pulse"></div>
          {/each}
        </div>
      {:else}
        <textarea
          id="editor-content"
          bind:value={content}
          placeholder="Escribe el editorial aquí... (Markdown soportado)"
          class="w-full h-[500px] p-6 text-sm text-slate-700 dark:text-slate-200 dark:bg-slate-900 leading-relaxed resize-none focus:outline-none font-mono"
        ></textarea>
      {/if}
      </div>
    </div>
  </div>
</AppLayout>

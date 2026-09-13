<script lang="ts">
  import { auth } from "$lib/stores/auth";
  import { onMount } from "svelte";

  let {
    sidebarCollapsed = false,
    onToggleSidebar,
  }: {
    sidebarCollapsed?: boolean;
    onToggleSidebar?: () => void;
  } = $props();

  let user = $derived($auth);
  let darkMode = $state(false);

  const roleLabels: Record<string, string> = {
    director: "Director",
    colaborador: "Colaborador",
  };

  function toggleDarkMode() {
    darkMode = !darkMode;
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('nia-dark-mode', darkMode ? 'true' : 'false');
  }

  onMount(() => {
    const saved = localStorage.getItem('nia-dark-mode');
    if (saved === 'true' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      darkMode = true;
      document.documentElement.classList.add('dark');
    }
  });

  async function handleLogout() {
    try {
      await fetch("/api/v1/auth/logout", { method: "POST" });
    } catch {
      // proceed even if request fails
    }
    auth.logout();
    window.location.href = "/login";
  }
</script>

<header
  class="fixed top-0 right-0 h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 z-30 flex items-center justify-between px-4 transition-all duration-300 ease-in-out"
  style="left: {sidebarCollapsed ? '64px' : '260px'}"
>
  <div class="flex items-center gap-3">
    {#if onToggleSidebar}
      <button
        onclick={onToggleSidebar}
        class="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-600 dark:text-slate-300"
        aria-label="Toggle sidebar"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
    {/if}
    <button
      onclick={toggleDarkMode}
      class="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-600 dark:text-slate-300"
      aria-label="Toggle dark mode"
    >
      {#if darkMode}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2" />
          <path d="M12 20v2" />
          <path d="m4.93 4.93 1.41 1.41" />
          <path d="m17.66 17.66 1.41 1.41" />
          <path d="M2 12h2" />
          <path d="M20 12h2" />
          <path d="m6.34 17.66-1.41 1.41" />
          <path d="m19.07 4.93-1.41 1.41" />
        </svg>
      {:else}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
          <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
        </svg>
      {/if}
    </button>
    <span class="font-semibold text-slate-800 dark:text-slate-100 text-base tracking-tight">NIA</span>
  </div>

  <div class="flex items-center gap-3">
    {#if user}
      <span class="text-sm text-slate-600 dark:text-slate-300 font-medium hidden sm:inline">
        {user.nombre}
      </span>
      <span class="text-xs px-2 py-0.5 rounded-full bg-teal-100 dark:bg-teal-950 text-teal-600 dark:text-teal-300 font-medium capitalize">
        {roleLabels[user.rol] ?? user.rol}
      </span>
    {/if}
    <button
      onclick={handleLogout}
      class="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-500 dark:text-slate-400 hover:text-red-600"
      aria-label="Cerrar sesión"
      title="Cerrar sesión"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
        <polyline points="16 17 21 12 16 7" />
        <line x1="21" y1="12" x2="9" y2="12" />
      </svg>
    </button>
  </div>
</header>

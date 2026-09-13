<script lang="ts">
  import { page } from "$app/stores";
  import { auth } from "$lib/stores/auth";

  let { collapsed = $bindable(false) }: { collapsed?: boolean } = $props();

  interface NavItem {
    label: string;
    href: string;
    icon: string;
    roles?: string[];
  }

  const directorItems: NavItem[] = [
    { label: "Dashboard", href: "/dashboard", icon: "dashboard" },
    { label: "Boletines", href: "/boletines", icon: "boletines" },
    { label: "Incidentes", href: "/incidentes", icon: "incidentes" },
    { label: "Notas", href: "/notas", icon: "notas" },
    { label: "Prompts", href: "/admin/prompts", icon: "prompts", roles: ["director"] },
    { label: "Auspiciantes", href: "/admin/auspiciantes", icon: "auspiciantes", roles: ["director"] },
    { label: "Usuarios", href: "/admin/usuarios", icon: "usuarios", roles: ["director"] },
  ];

  const colaboradorItems: NavItem[] = [
    { label: "Mis Notas", href: "/notas", icon: "notas" },
    { label: "Subir Nota", href: "/notas/nueva", icon: "boletines" },
  ];

  let navItems = $derived(
    $auth?.rol === "director" ? directorItems : colaboradorItems
  );

  let currentPath = $derived($page.url.pathname);

  function isActive(href: string): boolean {
    if (href === "/dashboard") return currentPath === "/dashboard";
    return currentPath.startsWith(href);
  }
</script>

<aside
  class="fixed left-0 top-0 h-full bg-slate-800 text-white z-40 flex flex-col transition-all duration-300 ease-in-out"
  class:w-[260px]={!collapsed}
  class:w-[64px]={collapsed}
>
  <!-- Logo section with top padding -->
  <div
    class="flex items-center shrink-0"
    style="padding: 24px 24px 20px 24px; border-bottom: 1px solid rgba(51, 65, 85, 0.6);"
  >
    <div
      class="w-8 h-8 rounded-lg bg-teal-500 flex items-center justify-center font-bold text-sm shrink-0"
    >
      NIA
    </div>
    {#if !collapsed}
      <span class="font-normal text-sm tracking-wide whitespace-nowrap text-slate-200" style="margin-left: 12px;">
        Panel Admin
      </span>
    {/if}
  </div>

  <!-- Navigation items with pixel spacing -->
  <nav class="flex-1 overflow-y-auto" style="padding: 24px 12px;">
    {#each navItems as item (item.href)}
      <a
        href={item.href}
        class="flex items-center rounded-lg text-sm transition-all duration-150
          {isActive(item.href)
          ? 'bg-teal-600/30 text-teal-300 border-l-3 border-teal-400'
          : 'text-slate-300 hover:bg-slate-700/60 hover:text-white'}"
        style="padding: 10px 12px; margin-bottom: 8px; margin-left: 12px; margin-right: 8px;"
        title={collapsed ? item.label : undefined}
      >
        <span class="shrink-0 w-5 h-5">
          {#if item.icon === "dashboard"}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
              <rect x="3" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="3" width="7" height="7" rx="1" />
              <rect x="3" y="14" width="7" height="7" rx="1" />
              <rect x="14" y="14" width="7" height="7" rx="1" />
            </svg>
          {:else if item.icon === "boletines"}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
          {:else if item.icon === "incidentes"}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          {:else if item.icon === "notas"}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <line x1="10" y1="9" x2="8" y2="9" />
            </svg>
          {:else if item.icon === "prompts"}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          {:else if item.icon === "auspiciantes"}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>
          {:else if item.icon === "usuarios"}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          {/if}
        </span>
        {#if !collapsed}
          <span class="whitespace-nowrap" style="margin-left: 12px;">{item.label}</span>
        {/if}
      </a>
    {/each}
  </nav>
</aside>

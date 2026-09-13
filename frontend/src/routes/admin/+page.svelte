<script lang="ts">
  import AppLayout from "$lib/components/AppLayout.svelte";
  import PageHeader from "$lib/components/PageHeader.svelte";

  const sections = [
    {
      title: "Prompts",
      description: "Gestionar prompts del sistema de IA",
      href: "/admin/prompts",
      icon: "prompts",
    },
    {
      title: "Auspiciantes",
      description: "Administrar auspiciantes del boletín",
      href: "/admin/auspiciantes",
      icon: "auspiciantes",
    },
    {
      title: "Usuarios",
      description: "Gestionar usuarios y permisos del sistema",
      href: "/admin/users",
      icon: "usuarios",
    },
  ];
</script>

<svelte:head>
  <title>Administración - NIA</title>
</svelte:head>

<AppLayout>
  <div class="space-y-8">
    <PageHeader title="Administración" description="Configuración y gestión del sistema" />

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each sections as section (section.href)}
        <a
          href={section.href}
          class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5 flex items-center gap-4 hover:shadow-md transition-shadow duration-200 group"
        >
          <div class="w-12 h-12 rounded-xl bg-teal-100 flex items-center justify-center shrink-0 group-hover:bg-teal-200 transition-colors">
            {#if section.icon === "prompts"}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6 text-teal-600">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            {:else if section.icon === "auspiciantes"}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6 text-teal-600">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
              </svg>
            {:else}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6 text-teal-600">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            {/if}
          </div>
          <div class="min-w-0">
            <h3 class="text-sm font-semibold text-slate-800 dark:text-slate-100 group-hover:text-teal-700 dark:group-hover:text-teal-300 transition-colors">
              {section.title}
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{section.description}</p>
          </div>
        </a>
      {/each}
    </div>
  </div>
</AppLayout>

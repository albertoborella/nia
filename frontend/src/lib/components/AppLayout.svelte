<script lang="ts">
  import type { Snippet } from "svelte";
  import Sidebar from "./Sidebar.svelte";
  import TopBar from "./TopBar.svelte";

  let { children }: { children: Snippet } = $props();
  let sidebarCollapsed = $state(false);

  function toggleSidebar() {
    sidebarCollapsed = !sidebarCollapsed;
  }
</script>

<div class="min-h-screen bg-slate-50 dark:bg-slate-950">
  <Sidebar bind:collapsed={sidebarCollapsed} />
  <TopBar {sidebarCollapsed} onToggleSidebar={toggleSidebar} />

  <main
    class="min-h-screen transition-all duration-300 ease-in-out"
    style="margin-left: {sidebarCollapsed ? '64px' : '260px'}; padding-top: 64px;"
  >
    <div style="padding: 48px 56px; max-width: 1200px; margin: 0 auto;">
      {@render children()}
    </div>
  </main>
</div>

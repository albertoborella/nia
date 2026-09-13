<script lang="ts">
  import "../app.css";
  import { onMount } from "svelte";
  import { auth } from "$lib/stores/auth";
  import type { Snippet } from "svelte";

  let { children }: { children: Snippet } = $props();
  let loading = $state(true);

  onMount(async () => {
    try {
      const response = await fetch("/api/v1/auth/me");
      if (response.ok) {
        const user = await response.json();
        auth.setUser(user);
      } else {
        auth.logout();
      }
    } catch {
      auth.logout();
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <div class="flex items-center justify-center min-h-screen bg-slate-50 dark:bg-slate-950">
    <div class="flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-teal-200 border-t-teal-600 rounded-full animate-spin"></div>
      <p class="text-sm text-slate-500 dark:text-slate-400 font-medium">Cargando...</p>
    </div>
  </div>
{:else}
  {@render children()}
{/if}

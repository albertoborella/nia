<script lang="ts">
  import { auth } from "$lib/stores/auth";
  import { onMount } from "svelte";

  let email = $state("");
  let password = $state("");
  let error = $state("");
  let loading = $state(false);

  onMount(() => {
    if ($auth) {
      window.location.href = "/dashboard";
    }
  });

  async function handleLogin(event: Event) {
    event.preventDefault();
    loading = true;
    error = "";

    try {
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        error = data.detail?.message || "Credenciales inválidas";
        return;
      }

      const data = await response.json();
      auth.setUser(data.user);
      window.location.href = "/dashboard";
    } catch {
      error = "Error de red. Verifique su conexión.";
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Iniciar Sesión - NIA</title>
</svelte:head>

<main class="min-h-screen flex items-center justify-center bg-gradient-to-br from-teal-50 via-teal-100 to-teal-200 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 px-4">
  <div class="w-full max-w-md">
    <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-xl p-12 border border-slate-200 dark:border-slate-700">
      <div class="flex flex-col items-center mb-10">
        <div class="w-16 h-16 rounded-2xl bg-teal-500 flex items-center justify-center mb-5">
          <span class="text-white font-bold text-xl tracking-tight">NIA</span>
        </div>
        <h1 class="text-xl font-semibold text-slate-800 dark:text-slate-100">Panel de Administración</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Noticias sobre Inocuidad Alimentaria</p>
      </div>

      {#if error}
        <div class="mb-6 p-4 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800">
          <p class="text-sm text-red-700 dark:text-red-300 font-medium">{error}</p>
        </div>
      {/if}

      <form onsubmit={handleLogin} class="flex flex-col gap-6">
        <div class="flex flex-col gap-2">
          <label for="email" class="text-sm font-medium text-slate-700 dark:text-slate-200">Correo electrónico</label>
          <input
            id="email"
            type="email"
            bind:value={email}
            required
            placeholder="director@nia.com"
            class="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 text-sm text-slate-800 dark:text-slate-200 dark:bg-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-teal-400 transition-colors"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label for="password" class="text-sm font-medium text-slate-700 dark:text-slate-200">Contraseña</label>
          <input
            id="password"
            type="password"
            bind:value={password}
            required
            placeholder="••••••••"
            class="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 text-sm text-slate-800 dark:text-slate-200 dark:bg-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-teal-400 transition-colors"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          class="mt-5 w-full py-3 rounded-lg bg-teal-500 hover:bg-teal-600 disabled:bg-teal-300 disabled:cursor-not-allowed text-white font-medium text-sm transition-colors flex items-center justify-center gap-2"
        >
          {#if loading}
            <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>Ingresando...</span>
          {:else}
            <span>Iniciar Sesión</span>
          {/if}
        </button>
      </form>
    </div>

    <p class="text-center text-xs text-teal-600/60 mt-8">
      © {new Date().getFullYear()} NIA — Noticias sobre Inocuidad Alimentaria
    </p>
  </div>
</main>

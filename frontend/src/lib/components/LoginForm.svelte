<script lang="ts">
  import { auth } from "$lib/stores/auth";

  let email = $state("");
  let password = $state("");
  let error = $state("");
  let loading = $state(false);

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
        error = data.detail?.message || "Login failed";
        return;
      }

      const data = await response.json();
      auth.setUser(data.user);
      window.location.href = "/dashboard";
    } catch {
      error = "Network error. Please check your connection.";
    } finally {
      loading = false;
    }
  }
</script>

<form onsubmit={handleLogin}>
  <div>
    <label for="email">Email</label>
    <input
      id="email"
      type="email"
      bind:value={email}
      required
      placeholder="director@nia.com"
    />
  </div>

  <div>
    <label for="password">Password</label>
    <input
      id="password"
      type="password"
      bind:value={password}
      required
      placeholder="Password"
    />
  </div>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <button type="submit" disabled={loading}>
    {loading ? "Logging in..." : "Login"}
  </button>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 320px;
  }

  div {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  label {
    font-size: 0.875rem;
    font-weight: 500;
  }

  input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 0.375rem;
    font-size: 1rem;
  }

  .error {
    color: #dc2626;
    font-size: 0.875rem;
  }

  button {
    padding: 0.625rem;
    background: #1d4ed8;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 1rem;
    cursor: pointer;
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>

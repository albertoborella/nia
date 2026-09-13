<script lang="ts">
  import { auth } from "$lib/stores/auth";
  import { onMount } from "svelte";

  onMount(() => {
    if ($auth) {
      window.location.href = "/dashboard";
    } else {
      window.location.href = "/login";
    }
  });
</script>

<p>Redirecting...</p>

<script lang="ts">
  type Variant = "default" | "success" | "warning" | "danger" | "info";

  let { status, variant }: { status: string; variant?: Variant } = $props();

  const variantClasses: Record<Variant, string> = {
    default: "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200",
    success: "bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-300",
    warning: "bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300",
    danger: "bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300",
    info: "bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300",
  };

  const statusVariantMap: Record<string, Variant> = {
    borrador: "default",
    pendiente: "warning",
    en_progreso: "info",
    programado: "info",
    completado: "success",
    publicado: "success",
    activo: "success",
    inactivo: "danger",
    cancelado: "danger",
    cerrado: "danger",
  };

  const statusLabels: Record<string, string> = {
    borrador: "Borrador",
    pendiente: "Pendiente",
    en_progreso: "En Progreso",
    programado: "Programado",
    completado: "Completado",
    publicado: "Publicado",
    activo: "Activo",
    inactivo: "Inactivo",
    cancelado: "Cancelado",
    cerrado: "Cerrado",
  };

  let resolvedVariant = $derived(variant ?? statusVariantMap[status] ?? "default");
  let label = $derived(statusLabels[status] ?? status);
</script>

<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {variantClasses[resolvedVariant]}">
  {label}
</span>

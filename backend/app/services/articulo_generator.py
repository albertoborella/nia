from datetime import date

from app.models.incidente import Incidente


def generate_markdown_article(incidentes: list[Incidente], boletin_nombre: str = "") -> str:
    if not incidentes:
        return "# Incidentes de Inocuidad Alimentaria\n\nNo hay incidentes para generar el articulo.\n"

    fechas = [i.fecha_inicio for i in incidentes]
    fecha_inicio = min(fechas)
    fecha_fin = max(fechas)

    markdown = "# Incidentes de Inocuidad Alimentaria\n\n"
    if boletin_nombre:
        markdown += f"**Boletin:** {boletin_nombre}\n\n"
    markdown += f"**Periodo:** {fecha_inicio} - {fecha_fin}\n\n"
    markdown += f"**Total de incidentes:** {len(incidentes)}\n\n"

    riesgo_order = ["critico", "alto", "medio", "bajo"]
    riesgo_labels = {
        "critico": "RIESGO CRITICO",
        "alto": "RIESGO ALTO",
        "medio": "RIESGO MEDIO",
        "bajo": "RIESGO BAJO",
    }

    for riesgo in riesgo_order:
        incidents_by_risk = [i for i in incidentes if i.riesgo == riesgo]
        if not incidents_by_risk:
            continue

        markdown += f"## {riesgo_labels.get(riesgo, riesgo.upper())}\n\n"

        for idx, inc in enumerate(incidents_by_risk, 1):
            markdown += f"### {idx}. {inc.incidente}\n\n"
            markdown += f"- **Producto:** {inc.producto}\n"
            markdown += f"- **Patogeno:** {inc.patogeno}\n"
            markdown += f"- **Pais:** {inc.pais}\n"
            if inc.organismo:
                markdown += f"- **Organismo:** {inc.organismo}\n"
            markdown += f"- **Severidad:** {inc.severidad}\n"
            markdown += f"- **Fecha inicio:** {inc.fecha_inicio}\n"
            if inc.fecha_cierre:
                markdown += f"- **Fecha cierre:** {inc.fecha_cierre}\n"
            if inc.observaciones:
                markdown += f"- **Observaciones:** {inc.observaciones}\n"
            if inc.fuente_nombre:
                markdown += f"- **Fuente:** {inc.fuente_nombre}"
                if inc.fuente_url:
                    markdown += f" ({inc.fuente_url})"
                markdown += "\n"
            markdown += "\n"

    markdown += "## Resumen\n\n"
    markdown += "| Pais | Cantidad | Riesgo Maximo |\n"
    markdown += "|------|----------|---------------|\n"

    paises = {}
    for inc in incidentes:
        if inc.pais not in paises:
            paises[inc.pais] = {"cantidad": 0, "riesgo_max": "bajo"}
        paises[inc.pais]["cantidad"] += 1
        if riesgo_order.index(inc.riesgo) < riesgo_order.index(paises[inc.pais]["riesgo_max"]):
            paises[inc.pais]["riesgo_max"] = inc.riesgo

    for pais, info in sorted(paises.items()):
        markdown += f"| {pais} | {info['cantidad']} | {info['riesgo_max']} |\n"

    return markdown

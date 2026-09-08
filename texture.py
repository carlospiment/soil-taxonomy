"""Clases texturales USDA: Soil Survey Manual (2017), capítulo 3, figura 3-7."""
import math

FRACTIONS = ["Arena (%)", "Limo (%)", "Arcilla (%)"]
AUTO = "Fracción calculada"
SOURCE = "https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf"
# Vértices (arena, limo, arcilla). Los límites compartidos se resuelven
# con las desigualdades de classify_texture, no con proximidad al centro.
REGIONS = {
    "Arenosa": [(100,0,0),(85,15,0),(90,0,10)],
    "Arenosa franca": [(85,15,0),(70,30,0),(85,0,15),(90,0,10)],
    "Franco arenosa": [(70,30,0),(50,50,0),(43,50,7),(52,41,7),(52,28,20),(80,0,20),(85,0,15)],
    "Franca": [(43,50,7),(23,50,27),(45,28,27),(52,28,20),(52,41,7)],
    "Franco limosa": [(50,50,0),(23,50,27),(0,73,27),(0,88,12),(8,80,12),(20,80,0)],
    "Limosa": [(20,80,0),(8,80,12),(0,88,12),(0,100,0)],
    "Franco arcillo arenosa": [(52,28,20),(45,28,27),(45,20,35),(65,0,35),(80,0,20)],
    "Franco arcillosa": [(45,28,27),(20,53,27),(20,40,40),(45,15,40)],
    "Franco arcillo limosa": [(20,53,27),(0,73,27),(0,60,40),(20,40,40)],
    "Arcillo arenosa": [(65,0,35),(45,20,35),(45,0,55)],
    "Arcillo limosa": [(20,40,40),(0,60,40),(0,40,60)],
    "Arcillosa": [(45,15,40),(20,40,40),(0,40,60),(0,0,100),(45,0,55)],
}
ENGLISH = dict(zip(REGIONS, ["sand", "loamy sand", "sandy loam", "loam", "silt loam", "silt", "sandy clay loam", "clay loam", "silty clay loam", "sandy clay", "silty clay", "clay"]))
COLORS = ["#f6d79a", "#edc178", "#dfe6a1", "#b6d69d", "#c2e2d6", "#d6ebee", "#b7ca7c", "#95b79d", "#95c6c1", "#b48c70", "#87a6b8", "#a78aa5"]


def is_number(v):
    return isinstance(v, (int, float)) and math.isfinite(v)


def classify_texture(sand, silt, clay):
    if not all(is_number(v) and 0 <= v <= 100 for v in (sand, silt, clay)):
        raise ValueError("Completa tres porcentajes válidos entre 0 y 100.")
    if abs(sand+silt+clay-100) > 0.000001:
        raise ValueError("Las tres fracciones deben sumar 100 %; no se normalizan automáticamente.")
    if silt + 1.5*clay < 15: return "Arenosa"
    if silt + 2*clay < 30: return "Arenosa franca"
    if (7 <= clay < 20 and sand > 52) or (clay < 7 and silt < 50): return "Franco arenosa"
    if 7 <= clay < 27 and 28 <= silt < 50 and sand <= 52: return "Franca"
    if (silt >= 50 and 12 <= clay < 27) or (50 <= silt < 80 and clay < 12): return "Franco limosa"
    if silt >= 80 and clay < 12: return "Limosa"
    if 20 <= clay < 35 and silt < 28 and sand > 45: return "Franco arcillo arenosa"
    if 27 <= clay < 40 and 20 < sand <= 45: return "Franco arcillosa"
    if 27 <= clay < 40 and sand <= 20: return "Franco arcillo limosa"
    if clay >= 35 and sand > 45: return "Arcillo arenosa"
    if clay >= 40 and silt >= 40: return "Arcillo limosa"
    if clay >= 40 and sand <= 45 and silt < 40: return "Arcillosa"
    raise ValueError("Composición no resuelta; revisa las fracciones.")


def complete_texture(row, edited=()):
    row = dict(row)
    auto = row.get(AUTO)
    if auto in FRACTIONS and auto in edited:
        auto = None  # Una edición explícita convierte ese valor en manual.
    if auto in FRACTIONS:
        row[auto] = None
    known = [f for f in FRACTIONS if is_number(row.get(f))]
    if len(known) == 2:
        empty = next(f for f in FRACTIONS if f not in known)
        remainder = round(100 - sum(row[f] for f in known), 6)
        if all(0 <= row[f] <= 100 for f in known) and 0 <= remainder <= 100:
            row[empty] = remainder
            auto = empty
    row[AUTO] = auto if auto in FRACTIONS else None
    try:
        row["Clase textural USDA"] = classify_texture(*(row.get(f) for f in FRACTIONS))
    except ValueError:
        row["Clase textural USDA"] = None
    return row


def apply_editor_changes(rows, changes):
    """Aplica una edición de Streamlit conservando la fracción derivada por fila."""
    updated = []
    deleted = set(changes.get("deleted_rows", []))
    edits = changes.get("edited_rows", {})
    for i, original in enumerate(rows):
        if i in deleted:
            continue
        delta = edits.get(i, edits.get(str(i), {}))
        updated.append(complete_texture({**original, **delta}, delta))
    for row in changes.get("added_rows", []):
        updated.append(complete_texture(row, row))
    return updated


def texture_figure(row=None):
    import plotly.graph_objects as go
    fig = go.Figure()
    for (name, vertices), color in zip(REGIONS.items(), COLORS):
        vertices = vertices + [vertices[0]]
        fig.add_trace(go.Scatterternary(
            a=[v[2] for v in vertices], b=[v[0] for v in vertices], c=[v[1] for v in vertices],
            mode="lines", fill="toself", fillcolor=color, line=dict(color="#52645d", width=1),
            name=name, text=[f"{name} ({ENGLISH[name]})"]*len(vertices), hovertemplate="%{text}<extra></extra>",
        ))
    if row and row.get("Clase textural USDA"):
        sand, silt, clay = [row[f] for f in FRACTIONS]
        fig.add_trace(go.Scatterternary(a=[clay], b=[sand], c=[silt], mode="markers",
            name=str(row.get("Horizonte") or "Horizonte seleccionado"),
            marker=dict(size=14, color="#c82e31", line=dict(color="white", width=2)),
            text=[row["Clase textural USDA"]],
            hovertemplate="%{text}<br>Arena: %{b:.2f}%<br>Limo: %{c:.2f}%<br>Arcilla: %{a:.2f}%<extra></extra>"))
    axis = dict(min=0, dtick=10, ticks="outside", gridcolor="#d8ded8")
    fig.update_layout(ternary=dict(sum=100, aaxis=dict(title="Arcilla (%)", **axis),
        baxis=dict(title="Arena (%)", **axis), caxis=dict(title="Limo (%)", **axis)),
        height=590, margin=dict(l=45,r=45,t=35,b=30), paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=11)), font=dict(family="Arial"))
    return fig

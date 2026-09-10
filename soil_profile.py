"""Validación de evidencias del perfil; no infiere diagnósticos desde pH."""
import math

SOURCE_URL = "https://www.nrcs.usda.gov/sites/default/files/2022-09/Keys-to-Soil-Taxonomy.pdf"
EDITION = "Keys to Soil Taxonomy, 13.ª edición (2022)"
STATES = ["No evaluado", "Presente", "Ausente"]
DIAGNOSTICS = [
    "Epipedón mólico", "Epipedón úmbrico", "Epipedón ócrico",
    "Epipedón hístico", "Epipedón fólico", "Epipedón melánico",
    "Epipedón antrópico", "Epipedón plaggen",
    "Horizonte argílico", "Horizonte kándico", "Horizonte nátrico",
    "Horizonte cámbico", "Horizonte óxico", "Horizonte espódico",
    "Horizonte cálcico", "Horizonte petrocálcico", "Horizonte gípsico",
    "Horizonte petrogypsic", "Horizonte sálico", "Horizonte sulfúrico",
    "Fragipán", "Duripán", "Horizonte plácico", "Horizonte sómbrico (sombric)",
    "Horizonte glósico", "Horizonte ágrico", "Propiedades frágicas",
    "Propiedades ándicas", "Materiales espódicos", "Materiales álbicos",
    "Plintita", "Petroplintita", "Propiedades vérticas",
    "Condiciones ácuicas", "Permafrost", "Crioturbación",
]
HORIZON_COLUMNS = [
    "Horizonte", "Techo (cm)", "Base (cm)", "Arena (%)", "Limo (%)",
    "Arcilla (%)", "Clase textural USDA", "Fragmentos (%)", "Color húmedo (Munsell)",
    "Color seco (Munsell)", "Estructura", "Películas de arcilla",
    "Rasgos redox", "Carbono orgánico (%)", "pH H2O", "pH KCl",
    "SB suma cationes (%)", "SB NH4OAc pH 7 (%)", "CIC NH4OAc (cmolc/kg suelo)",
    "CIC (cmolc/kg arcilla)", "CICE (cmolc/kg arcilla)",
    "Densidad aparente (g/cm³)", "Retención de P (%)",
    "Al oxalato (%)", "Fe oxalato (%)", "Vidrio volcánico (%)",
    "CaCO3 equivalente (%)", "Yeso (%)", "CE extracto saturado (dS/m)",
    "Na intercambiable (%)", "COLE", "Slickensides (%)",
    "Nódulos / plintita (%)", "Retención agua 1500 kPa (%)", "ODOE",
    "Métodos / muestra / observaciones",
]
TEXT_COLUMNS = {
    "Horizonte", "Clase textural USDA", "Color húmedo (Munsell)", "Color seco (Munsell)",
    "Estructura", "Películas de arcilla", "Rasgos redox",
    "Métodos / muestra / observaciones",
}


def missing(value):
    return value is None or (isinstance(value, float) and math.isnan(value)) or str(value).strip() == ""


def validate_profile(horizons, diagnostics, depth):
    """Errores de coherencia y faltantes, sin convertir ausencia de datos en ausencia del rasgo."""
    errors, pending = [], []
    if depth is None:
        pending.append("Registrar la profundidad realmente observada del perfil.")
    previous = None
    if not horizons:
        pending.append("Describir al menos un horizonte.")
    for i, row in enumerate(horizons, 1):
        if missing(row.get('Horizonte')):
            pending.append(f'Horizonte {i}: registrar identificación del horizonte o intervalo.')
        measured_laboratory = [k for k in HORIZON_COLUMNS[13:] if k not in TEXT_COLUMNS and k not in ('Slickensides (%)', 'Nódulos / plintita (%)') and not missing(row.get(k))]
        if measured_laboratory and missing(row.get('Métodos / muestra / observaciones')):
            pending.append(f'Horizonte {i}: documentar muestra, método y criterio USDA de las mediciones de laboratorio.')
        top, bottom = row.get("Techo (cm)"), row.get("Base (cm)")
        if missing(top) or missing(bottom):
            pending.append(f"Horizonte {i}: completar techo y base.")
        elif type(top) not in (int, float) or type(bottom) not in (int, float) or not math.isfinite(top) or not math.isfinite(bottom) or top < 0 or bottom <= top:
            errors.append(f"Horizonte {i}: la base debe ser mayor que el techo y las profundidades deben ser válidas.")
        else:
            if previous is not None and top < previous:
                errors.append(f"Horizonte {i}: se superpone con el anterior o está fuera de orden.")
            if previous is not None and top > previous:
                pending.append(f"Hay un intervalo sin describir entre {previous:g} y {top:g} cm.")
            if previous is None and top > 0:
                pending.append(f"Falta describir el intervalo superficial de 0 a {top:g} cm.")
            if depth is not None and bottom > depth:
                errors.append(f"Horizonte {i}: excede la profundidad observada.")
            previous = bottom
        fractions = [row.get(f"{part} (%)") for part in ("Arena", "Limo", "Arcilla")]
        if all(type(v) in (int, float) and math.isfinite(v) for v in fractions) and abs(sum(fractions) - 100) > 0.000001:
            errors.append(f"Horizonte {i}: arena + limo + arcilla debe sumar 100 %. Borra una fracción para calcularla por diferencia o revisa las mediciones.")
        elif sum(v for v in fractions if isinstance(v, (int, float)) and math.isfinite(v)) > 100.000001:
            errors.append(f"Horizonte {i}: las fracciones introducidas ya superan 100 %; no se puede calcular una tercera negativa.")
        for key, value in row.items():
            if key in TEXT_COLUMNS or missing(value):
                continue
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                errors.append(f"Horizonte {i}: {key} debe ser un número finito.")
            elif value < 0 or ("(%)" in key and value > 100) or (key.startswith("pH") and value > 14):
                errors.append(f"Horizonte {i}: {key} está fuera del intervalo permitido.")
    if depth is not None and previous is not None and previous < depth:
        pending.append(f"Falta describir el intervalo de {previous:g} a {depth:g} cm.")
    for row in diagnostics:
        if row.get("Estado") == 'Ausente' and missing(row.get('Evidencia / método / criterio')):
            pending.append(f"{row['Diagnóstico']}: documentar la evidencia de ausencia; no equivale a no evaluado.")
        if row.get("Estado") != "Presente":
            continue
        name = row["Diagnóstico"]
        top, bottom = row.get("Techo (cm)"), row.get("Base (cm)")
        if missing(top) or missing(bottom) or missing(row.get("Evidencia / método / criterio")):
            pending.append(f"{name}: registrar intervalo y evidencia del diagnóstico.")
        elif top < 0 or bottom <= top or (depth is not None and bottom > depth):
            errors.append(f"{name}: intervalo incompatible con la profundidad observada.")
    return errors, pending


def evaluate_route(rows, profile_errors):
    """Audita una determinación manual; nunca la presenta como clasificación automática."""
    if profile_errors:
        return "Ruta bloqueada por inconsistencias del perfil", None
    completed = []
    for row in rows:
        if (not str(row.get("Taxón", "")).strip()
                or not str(row.get("Clave / página", "")).strip()
                or not str(row.get("Evidencia y exclusión de anteriores", "")).strip()
                or row.get("Revisión") != "Cumple; anteriores descartados"):
            break
        completed.append(row)
    if len(completed) == 4:
        return "Subgrupo documentado por el usuario; pendiente de validación taxonómica independiente", completed[-1]["Taxón"]
    level = completed[-1]["Nivel"] if completed else "ninguno"
    return f"Subgrupo pendiente. Último nivel documentado: {level}.", None

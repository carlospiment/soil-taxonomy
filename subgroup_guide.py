"""Recorrido asistido de claves publicadas; los criterios los evalúa el usuario."""
import json
from pathlib import Path

KEYS = json.loads(Path(__file__).with_name("subgroup_keys.json").read_text(encoding="utf-8"))


def resolve_key(group, decisions, parent_verified=False, blockers=()):
    if not parent_verified:
        return {"status": "pending", "reason": "Documenta primero el orden, suborden y gran grupo.", "subgroup": None}
    if blockers:
        return {"status": "pending", "reason": "Resuelve los errores y faltantes del perfil antes de concluir.", "subgroup": None}
    trail = []
    for entry in KEYS[group]["entries"]:
        decision = decisions.get(entry["code"], {})
        outcome = decision.get("outcome", "No evaluado")
        evidence = decision.get("evidence", "").strip()
        if outcome == "No evaluado" or not evidence:
            return {"status": "pending", "reason": f"Falta evaluar y documentar {entry['code']}.", "subgroup": None, "trail": trail}
        if entry["fallback"] and outcome != "Cumple":
            return {"status": "pending", "reason": "La salida residual requiere revisar la exclusión documentada de todas las anteriores.", "subgroup": None, "trail": trail}
        trail.append({"code": entry["code"], **decision})
        if outcome == "Cumple":
            return {"status": "assisted", "reason": "Resultado condicionado a los diagnósticos y evaluaciones declarados por el usuario.", "subgroup": entry["name"], "code": entry["code"], "trail": trail}
        if outcome != "No cumple":
            return {"status": "pending", "reason": "Evaluación no reconocida.", "subgroup": None, "trail": trail}
    return {"status": "pending", "reason": "Revisar la ruta.", "subgroup": None}


def render_guide(route, blockers, profile_fingerprint):
    import streamlit as st
    st.subheader("Clave guiada de subgrupo")
    st.caption("Cobertura inicial: Hapludults (15 salidas) y Dystrudepts (26). El sistema respeta la precedencia; la evaluación de cada definición sigue siendo pedológica, no automática.")
    group = st.selectbox("Gran grupo de la clave guiada", ["Selecciona…"] + list(KEYS), key="guide_group", help="Selecciona un gran grupo previamente documentado en la ruta, no a partir de la textura.")
    if group not in KEYS:
        return None
    spec = KEYS[group]
    expected = spec["path"]
    parent_verified = all(
        r["Taxón"].strip().casefold() == taxon.casefold()
        and r["Revisión"] == "Cumple; anteriores descartados"
        and r["Clave / página"].strip()
        and r["Evidencia y exclusión de anteriores"].strip()
        for r, taxon in zip(route[:3], expected)
    )
    st.write("Ruta requerida: " + " → ".join(expected))
    pages = spec["printed_pages"]
    url = "https://www.govinfo.gov/content/pkg/GOVPUB-A57-PURL-gpo224020/pdf/GOVPUB-A57-PURL-gpo224020.pdf"
    st.markdown(f"[Criterios oficiales en inglés, pp. {pages[0]}–{pages[-1]} (2022)]({url}#page={spec['pdf_pages'][0]}). Las definiciones y notas de las claves también se aplican.")
    if not parent_verified:
        result = resolve_key(group, {}, False)
        st.warning(result["reason"])
        return {"group": group, **result}
    # Si cambia la evidencia, se invalidan las decisiones anteriores para evitar
    # presentar como vigente una determinación de un perfil ya modificado.
    fingerprint_key = f"guide_fingerprint_{group}"
    if st.session_state.get(fingerprint_key) != profile_fingerprint:
        for entry in spec["entries"]:
            for suffix in ("outcome", "evidence"):
                st.session_state.pop(f"guide_{entry['code']}_{suffix}", None)
        st.session_state[fingerprint_key] = profile_fingerprint
    decisions = {}
    for entry in spec["entries"]:
        code = entry["code"]
        with st.expander(f"{code} · {entry['name']}", expanded=True):
            st.text(entry["criteria"])
            if code == "HCGA":
                st.caption("Nota de la clave: el contacto lítico puede existir solo en parte de cada pedón o fluctuar desde menos de 50 cm a más de 50 cm dentro de cada pedón.")
            if entry["fallback"]:
                st.caption("Solo se llega aquí tras descartar todas las salidas anteriores con evidencia. Revisa esa exclusión antes de marcar Cumple.")
            outcome = st.selectbox("Evaluación de todos los requisitos de esta entrada", ["No evaluado", "No cumple", "Cumple"], key=f"guide_{code}_outcome", help="Revisa todos los AND/OR, intervalos y notas. Un criterio sin evaluar bloquea las salidas posteriores.")
            evidence = st.text_area("Evidencia: horizontes, valores, métodos, profundidades y requisito que cumple o descarta", key=f"guide_{code}_evidence", help="Explica con mediciones por qué cumple o no cumple; no basta repetir el nombre del subgrupo.")
            decisions[code] = {"outcome": outcome, "evidence": evidence}
        if outcome != "No cumple" or not evidence.strip() or entry["fallback"]:
            break
    result = resolve_key(group, decisions, parent_verified, blockers)
    if result["subgroup"]:
        st.success(f"Subgrupo por clave asistida: {result['subgroup']} ({result['code']})")
    else:
        st.warning("Subgrupo pendiente")
    st.info(result["reason"])
    return {"group": group, "decisions": decisions, **result}

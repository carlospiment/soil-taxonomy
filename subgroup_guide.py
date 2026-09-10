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
    parent_verified = len(route) >= 3 and all(
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
    # Durable decisions are separate from widget state (which Streamlit removes
    # when a group or a subsequent entry is temporarily not displayed).
    fingerprint_key = f"guide_fingerprint_{group}"
    memory_key = f'guide_decisions_{group}'
    review_key = f'guide_requires_review_{group}'
    restored = st.session_state.get('study_guide')
    if restored and restored.get('group') == group:
        st.session_state[memory_key] = restored.get('decisions', {})
        st.session_state[review_key] = restored.get('requires_review', False)
        st.session_state[fingerprint_key] = restored.get('evidence_fingerprint', profile_fingerprint)
        st.session_state.pop('study_guide')
    memory = dict(st.session_state.get(memory_key, {}))
    previous = st.session_state.get(fingerprint_key)
    if previous != profile_fingerprint:
        if previous is not None and any(d.get('evidence') or d.get('outcome', 'No evaluado') != 'No evaluado' for d in memory.values()):
            st.session_state[review_key] = True
        st.session_state[fingerprint_key] = profile_fingerprint
    requires_review = st.session_state.get(review_key, False)
    if not parent_verified:
        result = resolve_key(group, {}, False)
        st.warning(result['reason'])
        return {'group': group, 'decisions': memory, 'requires_review': requires_review,
                'evidence_fingerprint': profile_fingerprint, **result}
    if requires_review:
        st.warning('Cambió la evidencia taxonómica. Las decisiones se conservaron; revisa todas las evaluaciones del recorrido antes de confirmar su vigencia.')
        if st.button('Confirmar que revisé las decisiones con la evidencia actual', key=f'guide_confirm_{group}'):
            st.session_state[review_key] = False
            requires_review = False
    decisions = {}
    for entry in spec["entries"]:
        code = entry["code"]
        with st.expander(f"{code} · {entry['name']}", expanded=True):
            page = entry.get('printed_page', pages[0])
            st.markdown(f'[USDA 2022 · {code} · p. {page}]({url}#page={page + 8})')
            st.text(entry["criteria"])
            if code == "HCGA":
                st.caption("Nota de la clave: el contacto lítico puede existir solo en parte de cada pedón o fluctuar desde menos de 50 cm a más de 50 cm dentro de cada pedón.")
            if entry["fallback"]:
                st.caption("Solo se llega aquí tras descartar todas las salidas anteriores con evidencia. Revisa esa exclusión antes de marcar Cumple.")
            for suffix in ('outcome', 'evidence'):
                widget_key = f'guide_{code}_{suffix}'
                if widget_key not in st.session_state and code in memory:
                    st.session_state[widget_key] = memory[code][suffix]
            outcome = st.selectbox("Evaluación de todos los requisitos de esta entrada", ["No evaluado", "No cumple", "Cumple"], key=f"guide_{code}_outcome", help="Revisa todos los AND/OR, intervalos y notas. Un criterio sin evaluar bloquea las salidas posteriores.")
            evidence = st.text_area("Evidencia: horizontes, valores, métodos, profundidades y requisito que cumple o descarta", key=f"guide_{code}_evidence", help="Explica con mediciones por qué cumple o no cumple; no basta repetir el nombre del subgrupo.")
            decisions[code] = {"outcome": outcome, "evidence": evidence}
        if outcome != "No cumple" or not evidence.strip() or entry["fallback"]:
            break
    memory.update(decisions)
    st.session_state[memory_key] = memory
    result = resolve_key(group, decisions, parent_verified, list(blockers) + (['Revisar decisiones tras cambios de evidencia.'] if requires_review else []))
    if result["subgroup"]:
        st.success(f"Subgrupo por clave asistida: {result['subgroup']} ({result['code']})")
    else:
        st.warning("Subgrupo pendiente")
    st.info(result["reason"])
    return {"group": group, "decisions": memory, 'requires_review': requires_review,
            'evidence_fingerprint': profile_fingerprint, **result}

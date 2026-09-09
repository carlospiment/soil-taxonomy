import pandas as pd
import streamlit as st
from soil_profile import HORIZON_COLUMNS, TEXT_COLUMNS
from texture import AUTO, FRACTIONS, apply_editor_changes, texture_figure, ENGLISH
from field_help import column_help
from visual_observations import ensure_horizon_ids


def render_horizons():
    st.caption("Introduce dos fracciones de arena/limo/arcilla en cualquier orden. Al confirmar la celda con Enter o salir de ella, se calcula la tercera y se actualizan clase y gráfico. La columna Fracción calculada identifica el valor derivado.")
    st.caption("Si cambias una fracción medida, se recalcula la derivada. Si editas directamente la derivada, las tres pasan a ser manuales. Borra una para volver al cálculo automático. No se corrigen sumas superiores a 100 %.")
    columns = HORIZON_COLUMNS + [AUTO]
    if "horizon_rows" not in st.session_state:
        st.session_state.horizon_rows = [{}]
        st.session_state.horizon_revision = 0
    editor_key = f"profile_horizons_{st.session_state.horizon_revision}"

    def commit():
        st.session_state.horizon_rows = ensure_horizon_ids(
            apply_editor_changes(st.session_state.horizon_rows, st.session_state[editor_key]))
        st.session_state.horizon_revision += 1

    st.session_state.horizon_rows = ensure_horizon_ids(st.session_state.horizon_rows)
    rows = st.session_state.horizon_rows
    initial = pd.DataFrame({c: pd.Series([r.get(c) for r in rows], dtype="object" if c in TEXT_COLUMNS or c == AUTO else "float64") for c in columns})
    configs = {}
    for c in columns:
        if c in TEXT_COLUMNS or c == AUTO:
            configs[c] = st.column_config.TextColumn(c, help=column_help(c))
        else:
            maximum = 100.0 if "(%)" in c else (14.0 if c.startswith("pH") else None)
            configs[c] = st.column_config.NumberColumn(c, min_value=0.0, max_value=maximum, help=column_help(c))
    st.data_editor(initial, num_rows="dynamic", column_config=configs, disabled=[AUTO, "Clase textural USDA"],
        hide_index=True, key=editor_key, on_change=commit)
    horizons = initial.drop(columns=[AUTO])
    active = [r for r in rows if any(r.get(f) is not None for f in FRACTIONS) or r.get("Horizonte")]
    selected = None
    if active:
        idx = st.selectbox("Horizonte para el triángulo", range(len(active)),
            format_func=lambda i: f"{i+1}. {active[i].get('Horizonte') or 'Sin nombre'}", key="texture_selected",
            help="El punto representa únicamente el horizonte seleccionado. Edita sus fracciones en la tabla para moverlo.")
        selected = active[idx]
        label = selected.get("Clase textural USDA")
        if label:
            st.write(f"**Resultado textural: {label} ({ENGLISH[label]})**")
            st.caption(" · ".join(f"{f}: {selected[f]:g}" for f in FRACTIONS))
        else:
            st.warning("Textura pendiente: completa dos porcentajes válidos; si introdujiste tres, deben sumar 100 %.")
    st.plotly_chart(texture_figure(selected), width="stretch", key="texture_triangle")
    st.caption("USDA: 12 clases de tierra fina (<2 mm). Pasa el cursor sobre las regiones y el punto. La textura no determina por sí sola el subgrupo.")
    return horizons, [{"fila": i+1, "fraccion": r.get(AUTO)} for i,r in enumerate(rows) if r.get(AUTO)]

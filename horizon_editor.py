import pandas as pd
import streamlit as st
from soil_profile import HORIZON_COLUMNS, TEXT_COLUMNS
from texture import AUTO, FRACTIONS, apply_editor_changes, texture_figure, ENGLISH
from field_help import column_help
from visual_observations import ensure_horizon_ids
from taxonomy_scope import HORIZON_USES


FIELD_COLUMNS = {
    "Horizonte", "Techo (cm)", "Base (cm)", "Fragmentos (%)",
    "Color húmedo (Munsell)", "Color seco (Munsell)", "Estructura",
    "Películas de arcilla", "Rasgos redox", "Slickensides (%)",
    "Nódulos / plintita (%)",
}
BASIC_COLUMNS = {"Horizonte", "Techo (cm)", "Base (cm)"}


def horizon_presentation(column):
    """Visual labels only; retain original column names for data and archives."""
    if column in (AUTO, "Clase textural USDA"):
        marker, source = '🟪', 'Automático: resultado generado por la aplicación.'
    elif column in FRACTIONS:
        marker, source = '🟦', 'Laboratorio / cálculo: introduce fracciones medidas; la columna Fracción calculada identifica la obtenida por diferencia.'
    elif column in FIELD_COLUMNS:
        marker, source = '🟩', 'Campo: descripción u observación del horizonte. Si procede de otro método, documenta su origen.'
    elif column == "Métodos / muestra / observaciones":
        marker, source = '⬜', 'Trazabilidad: documenta la muestra, procedencia y método de los datos.'
    else:
        marker, source = '🟦', 'Laboratorio: transcribe el resultado y documenta método y unidades; este campo todavía no se calcula automáticamente.'
    requirement = ('Dato básico para identificar y delimitar cada horizonte descrito.'
                   if column in BASIC_COLUMNS else
                   'Se completa según los datos disponibles y los requisitos de la clave; no es obligatorio para todos los perfiles.')
    label = f'{marker} {column}' + (' *' if column in BASIC_COLUMNS else '')
    return label, f'{source} {requirement} {column_help(column)} USDA 2022: {HORIZON_USES.get(column, "Cálculo derivado de textura; no determina el taxón.")}'


def render_horizons():
    from assisted_forms import field, interval, choose_record
    from usda_capture import render_morphology
    from visual_observations import HORIZON_ID
    from texture import complete_texture
    st.caption('Una ficha por horizonte. Las mediciones desconocidas quedan vacías. Los cambios se conservan al pasar a otra ficha; descarga el estudio para conservarlo al cerrar la sesión.')
    if 'horizon_rows' not in st.session_state:
        st.session_state.horizon_rows = [{}]
        st.session_state.horizon_revision = 0
    st.session_state.horizon_rows = ensure_horizon_ids(st.session_state.horizon_rows)
    rows = st.session_state.horizon_rows
    if st.button('Añadir horizonte', key='profile_add_horizon'):
        rows.extend(ensure_horizon_ids([{}]))
        st.session_state['profile_horizon_selected'] = len(rows)-1
        st.rerun()
    if st.session_state.get('profile_removed_horizon') and st.button('Restaurar último horizonte retirado', key='profile_restore_horizon'):
        index, removed = st.session_state.pop('profile_removed_horizon')
        rows.insert(min(index, len(rows)), removed)
        st.rerun()
    if not rows:
        st.info('Añade un horizonte para comenzar la descripción.')
    else:
        index = choose_record(rows, 'profile_horizon_selected', 'Horizonte que deseas describir', lambda r: r.get('Horizonte') or 'Sin designación')
        row = rows[index]
        uid = row[HORIZON_ID]
        key = 'profile_horizon_' + uid
        field(row, 'Horizonte', key+'_name', label='Designación del horizonte', options=['O', 'Oi', 'Oe', 'Oa', 'A', 'Ap', 'E', 'B', 'Bt', 'Bw', 'Bg', 'C', 'Cg', 'R', 'AB', 'BA', 'BC', 'CB'], help='Designaciones habituales; no confirman diagnósticos. Para subdivisiones, discontinuidades u otra designación utiliza el campo de código completo.')
        if st.checkbox('Editar código completo de horizonte', key=key+'_custom_name'):
            field(row, 'Horizonte', key+'_full_name', label='Código completo (por ejemplo 2Bt1)', help='Keys 2022, capítulo 18. Conserva el orden de prefijos, símbolos y sufijos.')
        top, bottom = interval(row, key, st.session_state.get('profile_depth'))
        if index and top is not None and rows[index-1].get('Base (cm)') is not None:
            previous = rows[index-1]['Base (cm)']
            if top < previous:
                st.error('Este horizonte se superpone con el anterior.')
            elif top > previous:
                st.warning(f'Queda un intervalo sin describir entre {previous:g} y {top:g} cm.')
        view = st.selectbox('Contenido de la ficha', ['Textura y color', 'Descripción de campo', 'Mediciones para diagnósticos'], key='profile_horizon_view')
        if view == 'Textura y color':
            st.caption('Introduce dos porcentajes medidos: se calcula la tercera fracción. Si editas la calculada, pasa a ser una medición manual.')
            def recalculate(name):
                def update():
                    row.update(complete_texture(row, [name]))
                return update
            for part in FRACTIONS:
                field(row, part, key+'_'+part, numeric=True, maximum=100., help=column_help(part), changed=recalculate(part))
            if row.get(AUTO):
                st.caption('Fracción calculada: ' + row[AUTO])
            if row.get('Clase textural USDA'):
                st.write(f"**Resultado textural: {row['Clase textural USDA']} ({ENGLISH[row['Clase textural USDA']]})**")
            elif any(row.get(f) is not None for f in FRACTIONS):
                st.warning('Completa dos fracciones válidas; si registras tres, deben sumar 100 %.')
            st.plotly_chart(texture_figure(row), width='stretch', key='texture_triangle')
            for name in ('Color húmedo (Munsell)', 'Color seco (Munsell)'):
                field(row, name, key+'_'+name, help=column_help(name))
            st.caption('Copia matiz, valor y croma de la carta en la condición indicada. La textura y el color aislados no determinan el subgrupo.')
        elif view == 'Descripción de campo':
            render_morphology(row, uid)
            with st.expander('Observaciones del horizonte y registros anteriores'):
                for name in ('Estructura', 'Películas de arcilla', 'Rasgos redox'):
                    field(row, name, key+'_legacy_'+name, multiline=True, help=column_help(name))
                for name in ('Fragmentos (%)', 'Slickensides (%)', 'Nódulos / plintita (%)'):
                    field(row, name, key+'_'+name, numeric=True, maximum=100., help=column_help(name))
        else:
            measures = [c for c in HORIZON_COLUMNS if c not in TEXT_COLUMNS and c not in BASIC_COLUMNS and c not in FRACTIONS and c not in ('Fragmentos (%)', 'Slickensides (%)', 'Nódulos / plintita (%)')]
            measurement = st.selectbox('Medición que deseas registrar', measures, key=key+'_measurement')
            maximum = 100. if '(%)' in measurement else 14. if measurement.startswith('pH') else None
            field(row, measurement, key+'_'+measurement, numeric=True, maximum=maximum, help=column_help(measurement))
            st.caption(HORIZON_USES[measurement])
            for c in measures:
                if row.get(c) is not None:
                    st.caption(f'{c}: {row[c]:g}')
        field(row, 'Métodos / muestra / observaciones', key+'_notes', multiline=True, help='Identifica muestra, método, base, criterio USDA y procedencia. Las observaciones originales se conservan al cambiar de sección.')
        if st.button('Retirar este horizonte', key=key+'_remove'):
            st.session_state.profile_removed_horizon = (index, rows.pop(index))
            st.session_state.pop('profile_horizon_selected', None)
            st.rerun()
    initial = pd.DataFrame({c: pd.Series([r.get(c) for r in rows], dtype='object' if c in TEXT_COLUMNS else 'float64') for c in HORIZON_COLUMNS})
    return initial, [{'fila': i+1, 'fraccion': r[AUTO]} for i, r in enumerate(rows) if r.get(AUTO)]

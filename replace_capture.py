from pathlib import Path

p = Path('horizon_editor.py')
s = p.read_text(encoding='utf-8')
s = s[:s.index('def render_horizons():')] + '''def render_horizons():
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
'''
p.write_text(s, encoding='utf-8')

p = Path('laboratory.py')
s = p.read_text(encoding='utf-8')
s = s[:s.index('def render_laboratory(')] + '''def render_laboratory(depth=None):
    import json
    import streamlit as st
    from assisted_forms import field, interval, choose_record
    from uuid import uuid4
    st.caption('Una ficha por determinación. Selecciona el parámetro y registra el valor original, con su método y unidad. No se infieren diagnósticos ni fertilidad.')
    tables = st.session_state.setdefault('study_tables', {})
    saved = tables.setdefault('profile_laboratory', [])
    legacy = st.session_state.get('study_laboratory_legacy', []) + [r for r in saved if r.get('Parámetro') not in TAXONOMIC_CATALOG and r.get('Parámetro') is not None or r.get('Estado del laboratorio') not in (None, '', 'No informado')]
    st.session_state.study_laboratory_legacy_current = list({json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in legacy}.values())
    rows = [r for r in saved if r.get('Parámetro') in TAXONOMIC_CATALOG or r.get('Parámetro') is None]
    tables['profile_laboratory'] = rows
    if st.button('Añadir análisis', key='profile_add_lab'):
        rows.append({})
        st.session_state['profile_lab_selected'] = len(rows)-1
        st.rerun()
    if st.session_state.get('profile_removed_lab') and st.button('Restaurar último análisis retirado', key='profile_restore_lab'):
        i, item = st.session_state.pop('profile_removed_lab')
        rows.insert(min(i, len(rows)), item)
        st.rerun()
    if not rows:
        st.info('Añade únicamente análisis que respalden la clave que estás evaluando.')
        return []
    index = choose_record(rows, 'profile_lab_selected', 'Análisis que deseas completar', lambda r: (r.get('Muestra') or 'Sin muestra') + ' · ' + (r.get('Parámetro') or 'Sin parámetro'))
    row = rows[index]
    key = f'profile_lab_{index}'
    name = field(row, 'Parámetro', key+'_parameter', options=list(TAXONOMIC_CATALOG))
    if name:
        st.caption(LAB_USES[name])
        field(row, 'Resultado', key+'_result', help='Resultado original: 5.13, 0,02, <0,02 o ND. Un resultado ausente no se sustituye por cero.')
        unit = field(row, 'Unidad', key+'_unit', options=list(TAXONOMIC_CATALOG[name]))
        if unit and unit not in TAXONOMIC_CATALOG[name]:
            st.error('La unidad anterior no corresponde al parámetro. Selecciona una unidad compatible.')
        field(row, 'Base de reporte', key+'_basis', options=['Suelo seco (masa)', 'Suelo por volumen', 'Extracto / solución', 'Arcilla'])
        methods = (['Agua', 'KCl', 'CaCl₂'] if name == 'pH' else ['Extracto de pasta saturada'] if name == 'Conductividad eléctrica' else ['Oxalato de amonio'] if name in ('Al oxalato', 'Fe oxalato', 'ODOE') else ['NH₄OAc pH 7', 'Suma de cationes', 'KCl'] if ('intercambiable' in name or 'CIC' in name or name in ('Saturación de bases', 'Saturación de Na', 'Suma de bases')) else [])
        method = field(row, 'Método / extractante', key+'_method', options=methods + ['Otro: documentar'], help='Selecciona el método del informe; confirma su adecuación en la clave. No se convierten métodos entre sí.')
        if method == 'Otro: documentar':
            field(row, 'Detalle del método', key+'_method_detail', multiline=True, help='Nombre completo del procedimiento, preparación y referencia del laboratorio.')
        if name == 'pH':
            field(row, 'Relación suelo:solución', key+'_ratio', options=['1:1', '1:2', '1:2.5', '1:5', 'Pasta saturada', 'Otra: documentar'])
        if 'CIC' in name or name in ('Saturación de bases', 'Saturación de Na', 'Suma de bases'):
            field(row, 'Denominador / fórmula', key+'_formula', multiline=True)
    field(row, 'Muestra', key+'_sample')
    horizon_labels = [r.get('Horizonte') for r in st.session_state.get('horizon_rows', []) if r.get('Horizonte')]
    field(row, 'Horizonte / intervalo', key+'_horizon', options=list(dict.fromkeys(horizon_labels)), help='La asociación no copia profundidades automáticamente: confirma el intervalo realmente analizado.')
    interval(row, key, depth)
    for col in ('Laboratorio / informe', 'Fecha del análisis', 'Criterio USDA / clave / página'):
        field(row, col, key+'_'+col)
    field(row, 'Observaciones', key+'_notes', multiline=True)
    errors, pending = laboratory_issues([row], depth)
    for error in errors:
        st.error(error)
    for item in pending:
        st.warning(item)
    try:
        result = normalize_result(row)
        if result['valor'] is not None:
            st.write(f"Resultado normalizado: **{result['calificador']} {result['valor']:g} {result['unidad']}**")
    except ValueError:
        pass
    if st.button('Retirar este análisis', key=key+'_remove'):
        st.session_state.profile_removed_lab = (index, rows.pop(index))
        st.session_state.pop('profile_lab_selected', None)
        st.rerun()
    return [{c: r.get(c) for c in COLUMNS if c != 'Estado del laboratorio'} for r in rows if any(v not in (None, '') for v in r.values())]
'''
p.write_text(s, encoding='utf-8')

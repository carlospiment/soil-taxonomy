"""Soil laboratory capture: preserve reported values and normalize units only."""
import math

CATALOG = {}


def _add(names, units):
    for name in names.split('|'):
        CATALOG[name] = units


_add('pH|pH tampón', {'sin unidad': 1})
_add('Materia orgánica|Carbono orgánico|Nitrógeno total|Carbonato de calcio equivalente|Yeso|Arena|Limo|Arcilla', {'%': 1, 'g/kg': 0.1})
_add('Fósforo extraíble (P)|Potasio extraíble (K)|Calcio extraíble (Ca)|Magnesio extraíble (Mg)|Sodio extraíble (Na)|Zinc extraíble (Zn)|Manganeso extraíble (Mn)|Hierro extraíble (Fe)|Cobre extraíble (Cu)|Boro extraíble (B)|Nitrógeno nítrico (N-NO3)|Nitrógeno amoniacal (N-NH4)|Azufre sulfato (S-SO4)', {'mg/kg': 1, 'ppm': 1})
_add('Potasio intercambiable (K)|Calcio intercambiable (Ca)|Magnesio intercambiable (Mg)|Sodio intercambiable (Na)|Aluminio intercambiable (Al)|Acidez intercambiable (Al + H)|CIC del suelo|CICE del suelo|Suma de bases|Ca + Mg', {'cmolc/kg suelo': 1, 'meq/100 g suelo': 1})
_add('CIC de la arcilla|CICE de la arcilla', {'cmolc/kg arcilla': 1, 'meq/100 g arcilla': 1})
_add('Conductividad eléctrica', {'dS/m': 1, 'mS/cm': 1, 'µS/cm': 0.001})
_add('Saturación de bases|Saturación de aluminio|Saturación de acidez|Saturación de K|Saturación de Ca|Saturación de Mg|Saturación de Na', {'%': 1})
_add('Ca/K|Mg/K|Ca/Mg|(Ca + Mg)/K|Relación C/N', {'sin unidad': 1})
_add('Densidad aparente', {'g/cm³': 1, 'Mg/m³': 1})

COLUMNS = ['Muestra', 'Horizonte / intervalo', 'Techo (cm)', 'Base (cm)',
           'Laboratorio / informe', 'Fecha del análisis', 'Parámetro', 'Resultado',
           'Unidad', 'Base de reporte', 'Método / extractante', 'Relación suelo:solución',
           'Denominador / fórmula', 'Estado del laboratorio', 'Observaciones']
STATES = ['No informado', 'Muy bajo', 'Bajo', 'Medio', 'Alto', 'Muy alto', 'Aceptable', 'Otro']


def normalize_result(row):
    """Return normalized value, retaining qualifiers; unknown units stay pending."""
    name, raw = row.get('Parámetro'), str(row.get('Resultado') or '').strip()
    if name not in CATALOG:
        raise ValueError('Selecciona un parámetro del catálogo.')
    if not raw or raw.upper() in ('ND', 'NE', 'N/D'):
        return {'valor': None, 'calificador': raw or 'No medido', 'unidad': None}
    qualifier = '='
    for prefix in ('<=', '>=', '<', '>', '≤', '≥'):
        if raw.startswith(prefix):
            qualifier, raw = prefix, raw[len(prefix):].strip()
            break
    try:
        value = float(raw.replace(',', '.'))
    except ValueError:
        raise ValueError('Resultado numérico inválido; usa 0,02, <0,02 o ND.') from None
    if not math.isfinite(value) or value < 0:
        raise ValueError('El resultado debe ser finito y no negativo.')
    units = CATALOG[name]
    unit = row.get('Unidad')
    if unit in (None, '', 'No informada'):
        return {'valor': None, 'calificador': qualifier, 'unidad': None}
    if unit not in units:
        raise ValueError('Unidad incompatible con el parámetro.')
    basis = row.get('Base de reporte')
    canonical = next(iter(units))
    if canonical in ('mg/kg', 'cmolc/kg suelo', '%') and basis in ('Extracto / solución', 'Suelo por volumen', 'Arcilla'):
        return {'valor': None, 'calificador': qualifier, 'unidad': None}
    if canonical == 'cmolc/kg arcilla' and basis in ('Suelo seco (masa)', 'Suelo por volumen', 'Extracto / solución'):
        return {'valor': None, 'calificador': qualifier, 'unidad': None}
    if unit == 'ppm' and row.get('Base de reporte') != 'Suelo seco (masa)':
        return {'valor': None, 'calificador': qualifier, 'unidad': None}
    value *= units[unit]
    if (canonical == '%' and value > 100) or (name.startswith('pH') and value > 14):
        raise ValueError('Resultado fuera del intervalo permitido.')
    return {'valor': value, 'calificador': qualifier, 'unidad': canonical}


def validate_rows(rows):
    if not isinstance(rows, list) or len(rows) > 1000:
        raise ValueError('Tabla de laboratorio incompatible (máximo 1000 resultados).')
    for row in rows:
        if not isinstance(row, dict) or set(row) - set(COLUMNS):
            raise ValueError('Columnas de laboratorio incompatibles.')
        for key, value in row.items():
            if key in ('Techo (cm)', 'Base (cm)'):
                if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                    raise ValueError('Profundidad de laboratorio inválida.')
            elif value is not None and not isinstance(value, str):
                raise ValueError('Campo de laboratorio incompatible: ' + key)
        top, bottom = row.get('Techo (cm)'), row.get('Base (cm)')
        if top is not None and bottom is not None and bottom <= top:
            raise ValueError('La base de la muestra debe ser mayor que el techo.')
        normalize_result(row)


def render_laboratory():
    import json
    import pandas as pd
    import streamlit as st
    st.caption('Una fila por determinación y muestra. Puedes pegar filas desde una hoja de cálculo. Conserva el método del informe; un dato vacío significa no medido.')
    st.info('Materia orgánica y carbono orgánico se registran por separado. CIC del suelo y de la arcilla tienen bases distintas. P extraíble no equivale a retención de P; Fe y Al extraíbles no equivalen a oxalato.')
    with st.expander('Catálogo de parámetros y unidades admitidas'):
        st.dataframe(pd.DataFrame([{'Parámetro': k, 'Unidades admitidas': ', '.join(v)} for k, v in CATALOG.items()]), hide_index=True)
        st.caption('Métodos: documenta agua/KCl/CaCl₂ y relación para pH; Olsen/Bray/Mehlich para P; DTPA/Mehlich para micronutrientes; NH₄OAc/KCl para intercambio; Walkley–Black/combustión/pérdida por ignición para C o materia orgánica; pasta saturada/1:5 para CE. No se convierten métodos entre sí.')
    saved = st.session_state.get('study_tables', {}).get('profile_laboratory', [])
    frame = pd.DataFrame({c: pd.Series([r.get(c) for r in saved], dtype='float64' if c in ('Techo (cm)', 'Base (cm)') else 'object') for c in COLUMNS})
    config = {
        'Parámetro': st.column_config.SelectboxColumn(options=list(CATALOG), required=True),
        'Unidad': st.column_config.SelectboxColumn(options=['No informada'] + list(dict.fromkeys(u for units in CATALOG.values() for u in units))),
        'Base de reporte': st.column_config.SelectboxColumn(options=['No informada', 'Suelo seco (masa)', 'Suelo por volumen', 'Extracto / solución', 'Arcilla']),
        'Estado del laboratorio': st.column_config.SelectboxColumn(options=STATES),
        'Resultado': st.column_config.TextColumn(help='Valor original: 5.13, 0,02, <0.02 o ND. ND conserva el estado sin sustituirlo por cero.'),
        'Denominador / fórmula': st.column_config.TextColumn(help='Para saturaciones: CIC pH 7, CICE o suma de bases, según informe. Para relaciones, transcribe la fórmula.'),
        'Fecha del análisis': st.column_config.TextColumn(help='Fecha tal como aparece en el informe, preferiblemente AAAA-MM-DD.'),
    }
    for c in ('Techo (cm)', 'Base (cm)'):
        config[c] = st.column_config.NumberColumn(min_value=0.0)
    edited = st.data_editor(frame, num_rows='dynamic', hide_index=True, column_config=config, key='profile_laboratory')
    rows = [r for r in json.loads(edited.to_json(orient='records')) if any(v is not None and str(v).strip() for v in r.values())]
    normalized = []
    for index, row in enumerate(rows, 1):
        try:
            validate_rows([row])
            result = normalize_result(row)
            normalized.append({'Fila': index, 'Muestra': row.get('Muestra'), 'Parámetro': row['Parámetro'], **result})
            missing = [c for c in ('Muestra', 'Laboratorio / informe', 'Método / extractante', 'Base de reporte') if not row.get(c) or row.get(c) == 'No informada']
            if missing:
                st.warning(f"Fila {index}: completa " + ', '.join(missing) + '.')
            if row['Parámetro'].startswith('Saturación') or row['Parámetro'] in ('Ca/K', 'Mg/K', 'Ca/Mg', '(Ca + Mg)/K', 'Ca + Mg', 'Suma de bases', 'CICE del suelo'):
                if not row.get('Denominador / fórmula'):
                    st.warning(f'Fila {index}: documenta el denominador o la fórmula del informe.')
            if row.get('Resultado') and result['unidad'] is None and result['calificador'] not in ('ND', 'NE', 'N/D'):
                st.warning(f'Fila {index}: normalización pendiente; confirma unidad y base de reporte (ppm requiere suelo seco por masa).')
        except ValueError as error:
            st.error(f'Laboratorio, fila {index}: {error}')
    if normalized:
        st.markdown('**Resultados normalizados**')
        st.dataframe(pd.DataFrame(normalized), hide_index=True)
    st.caption('Conversión de unidades: meq/100 g = cmolc/kg; ppm = mg/kg solo sobre masa de suelo; 1 mS/cm = 1 dS/m. No se convierten concentraciones de extractos a suelo ni suelo por volumen a masa. Los estados son los del laboratorio; no se asignan umbrales universales. Las relaciones y saturaciones se transcriben con su fórmula, sin suponer denominadores.')
    return rows

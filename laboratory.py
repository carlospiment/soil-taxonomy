"""Soil laboratory capture: preserve reported values and normalize units only."""
import math
from taxonomy_scope import LAB_USES

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
_add('Retención de P|Al oxalato|Fe oxalato|Vidrio volcánico|Retención agua 1500 kPa', {'%': 1})
_add('ODOE|COLE', {'sin unidad': 1})
TAXONOMIC_CATALOG = {name: CATALOG[name] for name in LAB_USES}

COLUMNS = ['Muestra', 'Horizonte / intervalo', 'Techo (cm)', 'Base (cm)',
           'Laboratorio / informe', 'Fecha del análisis', 'Parámetro', 'Resultado',
           'Unidad', 'Base de reporte', 'Método / extractante', 'Relación suelo:solución',
           'Denominador / fórmula', 'Estado del laboratorio', 'Observaciones', 'Criterio USDA / clave / página']
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


def validate_rows(rows, check_results=True):
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
        if check_results and top is not None and bottom is not None and bottom <= top:
            raise ValueError('La base de la muestra debe ser mayor que el techo.')
        if row.get('Parámetro') not in CATALOG:
            raise ValueError('Selecciona un parámetro del catálogo.')
        if check_results:
            normalize_result(row)


def laboratory_issues(rows, depth=None):
    errors, pending = [], []
    for index, row in enumerate(rows, 1):
        prefix = f'Laboratorio, fila {index}: '
        try:
            validate_rows([row])
            if row.get('Parámetro') not in TAXONOMIC_CATALOG:
                errors.append(prefix + 'parámetro fuera del alcance taxonómico.')
                continue
            result = normalize_result(row)
            fields = ('Muestra', 'Laboratorio / informe', 'Método / extractante', 'Base de reporte', 'Criterio USDA / clave / página')
            absent = [c for c in fields if not str(row.get(c) or '').strip() or row.get(c) == 'No informada']
            if absent:
                pending.append(prefix + 'completar ' + ', '.join(absent) + '.')
            top, bottom = row.get('Techo (cm)'), row.get('Base (cm)')
            if top is None or bottom is None:
                pending.append(prefix + 'registrar techo y base de la muestra.')
            elif depth is not None and bottom > depth:
                errors.append(prefix + 'la muestra excede la profundidad observada.')
            if result['valor'] is None:
                pending.append(prefix + 'resultado no medido o normalización pendiente; revisar unidad y base.')
            if row['Parámetro'] in ('Saturación de bases', 'Saturación de Na', 'Suma de bases', 'CICE del suelo', 'CICE de la arcilla', 'CIC de la arcilla') and not str(row.get('Denominador / fórmula') or '').strip():
                pending.append(prefix + 'documentar denominador, fórmula y correcciones.')
            if row['Parámetro'] == 'pH' and not str(row.get('Relación suelo:solución') or '').strip():
                pending.append(prefix + 'documentar relación suelo:solución.')
        except ValueError as exc:
            errors.append(prefix + str(exc))
    return errors, pending


def render_laboratory(depth=None):
    import json
    import pandas as pd
    import streamlit as st
    st.caption('Una fila por determinación y muestra. Puedes pegar filas desde una hoja de cálculo. Conserva el método del informe; un dato vacío significa no medido.')
    st.info('Registra únicamente determinaciones utilizadas por un criterio de USDA Soil Taxonomy. Indica la clave o definición, método, unidad, base e intervalo. No se interpretan fertilidad ni necesidades de fertilización.')
    with st.expander('Catálogo de parámetros y unidades admitidas'):
        st.dataframe(pd.DataFrame([{'Parámetro': k, 'Unidades admitidas': ', '.join(v), 'Uso y referencia USDA 2022': LAB_USES[k]} for k, v in TAXONOMIC_CATALOG.items()]), hide_index=True)
        st.caption('No se intercambian métodos: pH en agua y KCl, saturación por NH₄OAc y suma de cationes, CIC por kg de suelo y por kg de arcilla son determinaciones diferentes. Documenta el método exigido por la entrada elegida.')
    saved = st.session_state.get('study_tables', {}).get('profile_laboratory', [])
    visible = [r for r in saved if r.get('Parámetro') in TAXONOMIC_CATALOG]
    legacy = st.session_state.get('study_laboratory_legacy', []) + [r for r in saved if r.get('Parámetro') not in TAXONOMIC_CATALOG or r.get('Estado del laboratorio') not in (None, '', 'No informado')]
    # A legacy row may contain both a usable measurement and an agronomic rating.
    # Preserve its original in the history without copying the rating to evidence.
    legacy = list({json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in legacy}.values())
    st.session_state.study_laboratory_legacy_current = legacy
    visible_columns = [c for c in COLUMNS if c != 'Estado del laboratorio']
    frame = pd.DataFrame({c: pd.Series([r.get(c) for r in visible], dtype='float64' if c in ('Techo (cm)', 'Base (cm)') else 'object') for c in visible_columns})
    config = {
        'Parámetro': st.column_config.SelectboxColumn(options=list(TAXONOMIC_CATALOG), required=True),
        'Unidad': st.column_config.SelectboxColumn(options=['No informada'] + list(dict.fromkeys(u for units in TAXONOMIC_CATALOG.values() for u in units))),
        'Base de reporte': st.column_config.SelectboxColumn(options=['No informada', 'Suelo seco (masa)', 'Suelo por volumen', 'Extracto / solución', 'Arcilla']),
        'Criterio USDA / clave / página': st.column_config.TextColumn(help='Entrada o definición de Keys to Soil Taxonomy 2022 que utiliza este dato. Confirma allí el método y profundidad exigidos.'),
        'Resultado': st.column_config.TextColumn(help='Valor original: 5.13, 0,02, <0.02 o ND. ND conserva el estado sin sustituirlo por cero.'),
        'Denominador / fórmula': st.column_config.TextColumn(help='Para saturaciones: CIC pH 7, CICE o suma de bases, según informe. Para relaciones, transcribe la fórmula.'),
        'Fecha del análisis': st.column_config.TextColumn(help='Fecha tal como aparece en el informe, preferiblemente AAAA-MM-DD.'),
    }
    for c in ('Techo (cm)', 'Base (cm)'):
        config[c] = st.column_config.NumberColumn(min_value=0.0)
    edited = st.data_editor(frame, num_rows='dynamic', hide_index=True, column_config=config, key='profile_laboratory')
    rows = [r for r in json.loads(edited.to_json(orient='records')) if any(v is not None and str(v).strip() for v in r.values())]
    normalized = []
    errors, pending = laboratory_issues(rows, depth)
    for error in errors:
        st.error(error)
    for item in pending:
        st.warning(item)
    for index, row in enumerate(rows, 1):
        try:
            validate_rows([row])
            result = normalize_result(row)
            normalized.append({'Fila': index, 'Muestra': row.get('Muestra'), 'Parámetro': row['Parámetro'], **result})
        except ValueError:
            pass  # Already included in the shared error list.
    if normalized:
        st.markdown('**Resultados normalizados**')
        st.dataframe(pd.DataFrame(normalized), hide_index=True)
    st.caption('Conversión de unidades: meq/100 g = cmolc/kg; 1 mS/cm = 1 dS/m. No se convierten métodos ni se transfieren resultados automáticamente a los horizontes. Los límites < o > se conservan y deben interpretarse en la clave.')
    return rows

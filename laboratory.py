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
_add('Relación de adsorción de sodio (SAR)', {'(mmolc/L)^0.5': 1})
TAXONOMIC_CATALOG = {name: CATALOG[name] for name in LAB_USES}

COLUMNS = ['Muestra', 'Horizonte / intervalo', 'Techo (cm)', 'Base (cm)',
           'Laboratorio / informe', 'Fecha del análisis', 'Parámetro', 'Resultado',
           'Unidad', 'Base de reporte', 'Método / extractante', 'Relación suelo:solución',
           'Denominador / fórmula', 'Estado del laboratorio', 'Observaciones', 'Criterio USDA / clave / página', 'Detalle del método']
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
            if row.get('Método / extractante') == 'Otro: documentar' and not str(row.get('Detalle del método') or '').strip():
                pending.append(prefix + 'documentar el método elegido como otro.')
            top, bottom = row.get('Techo (cm)'), row.get('Base (cm)')
            if top is None or bottom is None:
                pending.append(prefix + 'registrar techo y base de la muestra.')
            elif depth is not None and bottom > depth:
                errors.append(prefix + 'la muestra excede la profundidad observada.')
            if result['valor'] is None:
                pending.append(prefix + 'resultado no medido o normalización pendiente; revisar unidad y base.')
            if row['Parámetro'] in ('Saturación de bases', 'Saturación de Na', 'Suma de bases', 'CICE del suelo', 'CICE de la arcilla', 'CIC de la arcilla', 'Relación de adsorción de sodio (SAR)') and not str(row.get('Denominador / fórmula') or '').strip():
                pending.append(prefix + 'documentar denominador, fórmula y correcciones.')
            if row['Parámetro'] == 'pH' and not str(row.get('Relación suelo:solución') or '').strip():
                pending.append(prefix + 'documentar relación suelo:solución.')
        except ValueError as exc:
            errors.append(prefix + str(exc))
    return errors, pending


def render_laboratory(depth=None):
    import json
    import streamlit as st
    from assisted_forms import field, interval, choose_record
    st.caption('Una ficha por determinación. Selecciona el parámetro y registra el valor original, con su método y unidad. No se infieren diagnósticos ni fertilidad.')
    tables = st.session_state.setdefault('study_tables', {})
    saved = tables.setdefault('profile_laboratory', [])
    legacy = st.session_state.get('study_laboratory_legacy', []) + [r for r in saved if r.get('Parámetro') not in TAXONOMIC_CATALOG and r.get('Parámetro') is not None or r.get('Estado del laboratorio') not in (None, '', 'No informado')]
    st.session_state.study_laboratory_legacy_current = list({json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in legacy}.values())
    st.session_state.study_laboratory_legacy = st.session_state.study_laboratory_legacy_current
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
        if 'CIC' in name or name in ('Saturación de bases', 'Saturación de Na', 'Suma de bases', 'Relación de adsorción de sodio (SAR)'):
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

"""Field Book 4.0 (2024) descriptors, separate from taxonomic conclusions."""
from assisted_forms import field
import streamlit as st

FIELD_BOOK = 'https://www.nrcs.usda.gov/sites/default/files/2025-04/Field-Book-for-Describing-and-Sampling-Soils-v4.pdf'
STRUCTURES = ['Granular (GR)', 'Bloques angulares (ABK)', 'Bloques subangulares (SBK)',
              'Lenticular (LP)', 'Laminar (PL)', 'Cuñas (WEG)', 'Prismática (PR)',
              'Columnar (COL)', 'Grano simple (SGR)', 'Masiva (MA)']
STRUCTURELESS = {'Grano simple (SGR)', 'Masiva (MA)'}


def structure_size(kind, mm):
    if kind is None or kind in STRUCTURELESS or mm is None:
        return None
    bounds = [1, 2, 5, 10] if kind in ('Granular (GR)', 'Laminar (PL)') else [10, 20, 50, 100, 500] if kind in ('Prismática (PR)', 'Columnar (COL)', 'Cuñas (WEG)') else [5, 10, 20, 50]
    labels = ['Muy fina', 'Fina', 'Mediana', 'Gruesa', 'Muy gruesa', 'Extremadamente gruesa']
    if kind == 'Laminar (PL)':
        labels = ['Muy delgada', 'Delgada', 'Mediana', 'Gruesa', 'Muy gruesa']
    return labels[next((i for i, limit in enumerate(bounds) if mm < limit), len(bounds))]


def boundary_class(cm):
    if cm is None:
        return None
    return next((label for limit, label in [(0.5, 'Muy abrupto'), (2, 'Abrupto'), (5, 'Claro'), (15, 'Gradual')] if cm < limit), 'Difuso')


def render_site():
    record = st.session_state.setdefault('profile_site_description', {})
    with st.expander('1C. Sitio, relieve y material parental'):
        st.markdown(f'[Guía de descripción USDA: Field Book 4.0, capítulo 1]({FIELD_BOOK}#page=18)')
        field(record, 'elevacion_m', 'profile_site_elevation', label='Elevación (m s. n. m.)', numeric=True, minimum=None)
        field(record, 'posicion_ladera', 'profile_site_position', label='Posición en la ladera', options=['Cima (summit)', 'Hombro (shoulder)', 'Ladera media (backslope)', 'Pie de ladera (footslope)', 'Base de ladera (toeslope)'])
        field(record, 'forma_longitudinal', 'profile_site_shape', label='Forma longitudinal de la pendiente', options=['Cóncava', 'Convexa', 'Lineal'])
        field(record, 'forma_transversal', 'profile_site_cross_shape', label='Forma transversal de la pendiente', options=['Cóncava', 'Convexa', 'Lineal'])
        field(record, 'geoforma', 'profile_site_landform', label='Geoforma / posición fisiográfica', options=['Terraza', 'Llanura aluvial', 'Abanico aluvial', 'Colina', 'Montaña', 'Depresión', 'Duna', 'Otra: documentar'])
        field(record, 'material_parental', 'profile_site_parent', label='Material parental: origen', options=['Aluvión', 'Coluvión', 'Residuo de meteorización', 'Material eólico', 'Depósito lacustre', 'Depósito marino', 'Till glacial', 'Material piroclástico', 'Material transportado por humanos', 'Otro: documentar'])
        field(record, 'naturaleza_material', 'profile_site_nature', label='Naturaleza del material y evidencia', multiline=True, help='Describe litología, estratificación, discontinuidades y fuente. No deduzcas automáticamente un orden por origen volcánico o aluvial.')
        field(record, 'drenaje', 'profile_site_drainage', label='Clase de drenaje natural', options=['Subacuático (SA)', 'Muy pobremente drenado (VP)', 'Pobremente drenado (PD)', 'Algo pobremente drenado (SP)', 'Moderadamente bien drenado (MW)', 'Bien drenado (WD)', 'Algo excesivamente drenado (SE)', 'Excesivamente drenado (ED)'])
        field(record, 'evidencia_sitio', 'profile_site_evidence', label='Fuente y evidencia de la descripción del sitio', multiline=True)
        st.caption('La clase de drenaje describe el sitio; no confirma por sí sola condiciones ácuicas ni régimen de humedad. Pendiente (%) se registra una sola vez en los rasgos diferenciales.')
    return record


def render_morphology(row, uid):
    all_records = st.session_state.setdefault('profile_horizon_descriptions', {})
    record = all_records.setdefault(uid, {})
    key = 'profile_morph_' + uid
    section = st.selectbox('Descripción que deseas completar', ['Estructura', 'Consistencia', 'Límite inferior', 'Rasgos redox', 'Fragmentos y carbonatos', 'Raíces y poros', 'Mineralogía'], key=key + '_section')
    if section == 'Estructura':
        st.markdown(f'[Estructura: tipo, grado y tamaño, pp. 2–53 a 2–56]({FIELD_BOOK}#page=103)')
        kind = field(record, 'estructura_tipo', key+'_structure', label='Tipo de estructura', options=STRUCTURES)
        if kind and kind not in STRUCTURELESS:
            field(record, 'estructura_grado', key+'_grade', label='Grado de estructura', options=['Débil (1)', 'Moderada (2)', 'Fuerte (3)'])
            mm = field(record, 'estructura_mm', key+'_size', label='Menor dimensión del agregado (mm)', numeric=True, help='Para estructura laminar mide espesor; para los otros tipos, la menor dimensión. No estimar desde una foto sin escala.')
            size = structure_size(kind, mm)
            if size:
                st.caption(f'Clase de tamaño calculada para este tipo: {size}.')
        else:
            st.caption('Masiva y grano simple son estados sin unidades estructurales; no se solicita grado ni tamaño de agregados.')
        field(record, 'estructura_notas', key+'_structure_notes', label='Estructura compuesta / observaciones', multiline=True)
        if kind and st.button('Aplicar esta descripción al horizonte', key=key+'_apply_structure'):
            parts = [kind]
            if kind not in STRUCTURELESS:
                parts += [record.get('estructura_grado'), structure_size(kind, record.get('estructura_mm'))]
            parts += [record.get('estructura_notas')]
            row['Estructura'] = ' · '.join(p for p in parts if p)
            st.rerun()
        if row.get('Estructura'):
            st.caption('Descripción registrada: ' + row['Estructura'])
    elif section == 'Consistencia':
        st.markdown(f'[Consistencia: pp. 2–63 a 2–67]({FIELD_BOOK}#page=113)')
        field(record, 'consistencia_seca', key+'_dry', label='Resistencia a ruptura en seco', options=['Suelta', 'Blanda', 'Ligeramente dura', 'Moderadamente dura', 'Dura', 'Muy dura', 'Extremadamente dura', 'Rígida'])
        field(record, 'consistencia_humeda', key+'_moist', label='Resistencia a ruptura húmeda', options=['Suelta', 'Muy friable', 'Friable', 'Firme', 'Muy firme', 'Extremadamente firme', 'Ligeramente rígida', 'Rígida', 'Muy rígida'])
        field(record, 'plasticidad', key+'_plastic', label='Plasticidad', options=['No plástica', 'Ligeramente plástica', 'Moderadamente plástica', 'Muy plástica'], help='Rollo de 4 cm: no sostiene 6 mm, sostiene 6 pero no 4 mm, sostiene 4 pero no 2 mm, o sostiene 2 mm, respectivamente. Evaluar humedad de máxima plasticidad.')
        field(record, 'pegajosidad', key+'_sticky', label='Pegajosidad', options=['No pegajosa', 'Ligeramente pegajosa', 'Moderadamente pegajosa', 'Muy pegajosa'])
    elif section == 'Límite inferior':
        cm = field(record, 'transicion_cm', key+'_transition', label='Espesor de la transición al siguiente horizonte (cm)', numeric=True)
        if cm is not None:
            st.caption('Nitidez calculada: ' + boundary_class(cm) + '. USDA Field Book 4.0, p. 2–6.')
        field(record, 'limite_topografia', key+'_boundary', label='Topografía del límite', options=['Plano (smooth)', 'Ondulado (wavy)', 'Irregular', 'Discontinuo (broken)'])
    elif section == 'Rasgos redox':
        status = field(record, 'redox_estado', key+'_redox_status', label='Rasgos redox observados', options=['Presentes', 'Ausentes en el intervalo evaluado'])
        if status == 'Presentes':
            field(record, 'redox_tipo', key+'_redox_type', label='Tipo de rasgo', options=['Concentraciones redox', 'Depleciones redox', 'Matriz reducida'])
            field(record, 'redox_color', key+'_redox_color', label='Color Munsell del rasgo')
            field(record, 'redox_porcentaje', key+'_redox_amount', label='Abundancia del rasgo (%)', numeric=True, maximum=100.)
            field(record, 'redox_mm', key+'_redox_size', label='Tamaño del rasgo (mm)', numeric=True)
            field(record, 'redox_contraste', key+'_redox_contrast', label='Contraste', options=['Débil (faint)', 'Distinto (distinct)', 'Prominente (prominent)'])
            field(record, 'redox_localizacion', key+'_redox_location', label='Localización y distribución', multiline=True)
        field(record, 'redox_evidencia', key+'_redox_evidence', label='Evidencia, intervalo y condiciones de observación', multiline=True)
    elif section == 'Fragmentos y carbonatos':
        field(record, 'fragmentos_base', key+'_fragment_basis', label='Base del porcentaje de fragmentos del horizonte', options=['Volumen', 'Masa'], help='No convertir automáticamente un porcentaje antiguo de base desconocida a volumen.')
        field(record, 'fragmentos_tipo', key+'_fragment_type', label='Tipo de fragmentos', options=['Grava', 'Piedras / cobbles', 'Bloques / stones', 'Bloques grandes / boulders', 'Fragmentos planos', 'Mezcla: documentar'])
        field(record, 'fragmentos_naturaleza', key+'_fragment_nature', label='Naturaleza y tamaño de los fragmentos')
        field(record, 'efervescencia', key+'_effervescence', label='Reacción a carbonatos: efervescencia', options=['Ninguna', 'Muy ligera', 'Ligera', 'Fuerte', 'Violenta'])
        field(record, 'reactivo_carbonatos', key+'_reagent', label='Reactivo, concentración y condición de la muestra', help='La efervescencia no sustituye el CaCO₃ equivalente medido; USDA Field Book, p. 2–89.')
    elif section == 'Raíces y poros':
        for item in ('raíces', 'poros'):
            field(record, item+'_cantidad', key+'_'+item+'_quantity', label='Cantidad de '+item, options=['Ausentes', 'Pocos', 'Comunes', 'Muchos'], help='Clases dependientes del tamaño y área de referencia: Field Book 4.0, pp. 2–70 a 2–73. Documenta el área observada.')
            field(record, item+'_mm', key+'_'+item+'_mm', label='Diámetro representativo de '+item+' (mm)', numeric=True)
            field(record, item+'_distribucion', key+'_'+item+'_distribution', label='Distribución y área de referencia de '+item, multiline=True)
    else:
        field(record, 'mineralogia', key+'_minerals', label='Mineral identificado por análisis', options=['Caolinita', 'Esmectita', 'Illita', 'Vermiculita', 'Clorita', 'Gibbsita', 'Mezcla / otro: documentar'])
        field(record, 'mineralogia_metodo', key+'_mineral_method', label='Método, fracción, resultados e informe', multiline=True, help='Registrar resultados medidos. No asigna automáticamente una clase mineralógica de familia.')
    return record

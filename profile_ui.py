"""Ficha pedológica y documentación de la determinación taxonómica."""
import json
import pandas as pd
import streamlit as st
from field_help import help_for, table_help
from horizon_editor import render_horizons
from laboratory import render_laboratory, laboratory_issues
from taxonomy_scope import evidence_fingerprint, validate_extra, determination, DIAGNOSTIC_ENGLISH, EXTRA_USES, HORIZON_USES
from field_media import render_location_photos, make_archive
from subgroup_guide import render_guide
from visual_observations import HORIZON_ID, extend_report, new_id
from soil_profile import (
    SOURCE_URL, EDITION, STATES, DIAGNOSTICS, validate_profile, evaluate_route,
)


def study_editor(data, **kwargs):
    from assisted_forms import field, interval, choose_record
    from subgroup_guide import KEYS
    key = kwargs['key']
    tables = st.session_state.setdefault('study_tables', {})
    rows = tables.setdefault(key, json.loads(data.to_json(orient='records')))
    if key == 'profile_route':
        for i, row in enumerate(rows):
            with st.expander(f"{i+1}. {row['Nivel']}", expanded=i == 0):
                options = ['Alfisols', 'Andisols', 'Aridisols', 'Entisols', 'Gelisols', 'Histosols', 'Inceptisols', 'Mollisols', 'Oxisols', 'Spodosols', 'Ultisols', 'Vertisols'] if i == 0 else None
                if i in (1, 2):
                    options = [spec['path'][i] for spec in KEYS.values() if spec['path'][:i] == [r.get('Taxón') for r in rows[:i]]]
                if i == 3:
                    options = [e['name'] for e in KEYS.get(rows[2].get('Taxón'), {}).get('entries', [])]
                custom = st.checkbox('Transcribir otro taxón de la clave oficial', key=f'{key}_{i}_custom') if i else False
                field(row, 'Taxón', f'{key}_{i}_taxon', options=None if custom else options, help='Lista completa de órdenes; en niveles inferiores solo se sugieren rutas de la cobertura guiada. Para otro taxón, transcribe su nombre y referencia.')
                field(row, 'Clave / página', f'{key}_{i}_reference')
                field(row, 'Evidencia y exclusión de anteriores', f'{key}_{i}_evidence', multiline=True)
                field(row, 'Revisión', f'{key}_{i}_review', options=['Pendiente', 'No cumple', 'Cumple; anteriores descartados'])
                for col in ('Taxón', 'Clave / página', 'Evidencia y exclusión de anteriores'):
                    row[col] = row.get(col) or ''
                row['Revisión'] = row.get('Revisión') or 'Pendiente'
                if i and any(r.get('Revisión') != 'Cumple; anteriores descartados' for r in rows[:i]):
                    st.warning('Completa y revisa los niveles anteriores antes de concluir este nivel.')
        return pd.DataFrame(rows)
    description = (lambda r: DIAGNOSTIC_ENGLISH[r['Diagnóstico']] + ' · ' + str(r.get('Estado') or 'No evaluado')) if key == 'profile_diagnostics' else (lambda r: r['Parámetro'])
    index = choose_record(rows, key+'_selected', 'Diagnóstico que deseas evaluar' if key == 'profile_diagnostics' else 'Medida adicional que deseas registrar', description)
    row = rows[index]
    prefix = f'{key}_{index}'
    if key == 'profile_diagnostics':
        state = field(row, 'Estado', prefix+'_status', options=STATES)
        row['Estado'] = state or 'No evaluado'
        if state in ('Presente', 'Ausente'):
            interval(row, prefix, st.session_state.get('profile_depth'))
            field(row, 'Evidencia / método / criterio', prefix+'_evidence', multiline=True, help='Documenta cada requisito, método, intervalo y exclusión. Un rasgo aislado no confirma el diagnóstico.')
            if not row.get('Evidencia / método / criterio'):
                st.warning('Registra evidencia para sostener la presencia o ausencia declarada.')
        st.caption('Puedes evaluar solo los diagnósticos pertinentes al recorrido. Los demás permanecen como no evaluados.')
    else:
        st.caption(EXTRA_USES.get(row['Parámetro'], 'Documenta el criterio y método de la clave.'))
        maximum = 100. if row['Unidad'] == '%' and row['Parámetro'] != 'Pendiente' else 366. if row['Unidad'] == 'días' else None
        field(row, 'Valor', prefix+'_value', label=f"{row['Parámetro']} ({row['Unidad']})", numeric=True, maximum=maximum)
        field(row, 'Intervalo / método / evidencia', prefix+'_evidence', multiline=True)
        local_errors, _ = validate_extra([row], st.session_state.get('profile_depth'))
        for error in local_errors:
            st.error(error)
    return pd.DataFrame(rows)


def render_profile():
    if "profile_uid" not in st.session_state:
        st.session_state.profile_uid = new_id()
    if "visual_observations" not in st.session_state:
        st.session_state.visual_observations = []
    st.header("Perfil pedológico e identificación al subgrupo")
    st.write("Registra las evidencias y documenta cada paso de las claves: orden → suborden → gran grupo → subgrupo.")
    st.info("Este módulo organiza una determinación asistida. Incluye claves guiadas de Hapludults y Dystrudepts; los demás grupos requieren la clave oficial. Un dato vacío significa no medido, no cero; un diagnóstico no evaluado no equivale a ausente.")
    st.markdown(f"Referencia: [{EDITION}]({SOURCE_URL}). Consultar las definiciones completas y las claves del orden correspondiente.")
    summary = st.container()
    st.caption('Etapas: documentación del pedón → evidencias por horizonte → diagnósticos y rasgos → claves → determinación. Completa las mediciones que exija tu recorrido; la aplicación no deduce un diagnóstico de un valor aislado.')
    with st.expander('Qué documenta cada campo y dónde se utiliza en USDA'):
        references = {**HORIZON_USES, **EXTRA_USES}
        topic = st.selectbox('Campo sobre el que necesitas ayuda', list(references), key='profile_help_topic')
        st.write(references[topic])
        st.caption('Las referencias indican usos posibles. La entrada oficial elegida determina si un dato es necesario y qué método, intervalo y combinaciones AND/OR se aplican. El catálogo no sustituye las definiciones completas.')

    with st.expander("1. Documentación del pedón, profundidad y regímenes", expanded=True):
        st.caption('Identificador, responsable, fecha, ubicación y fotos documentan las observaciones; no son criterios de pertenencia a un taxón. Regímenes y profundidades: Keys 2022, capítulos 3 y 4.')
        left, right = st.columns(2)
        with left:
            profile_id = st.text_input("Identificador del perfil", key="profile_id", help=help_for('profile_id'))
            observer = st.text_input("Nombre del responsable", key="profile_observer", help=help_for('profile_observer'))
            observed_date = st.date_input("Fecha de descripción", value=None, format="DD/MM/YYYY", key="profile_date", help=help_for("profile_date"))
            depth = st.number_input("Profundidad observada (cm)", min_value=0.0, value=None, key="profile_depth", help=help_for('profile_depth'))
            reference = st.selectbox("Origen de las profundidades", ["Superficie del suelo", "Superficie del suelo mineral"], key="profile_reference", help=help_for('profile_reference'))
            st.caption("Usa un mismo origen en las tablas. La clave puede requerir profundidades desde la superficie mineral; documenta la conversión cuando corresponda.")
            contact = st.selectbox("Contacto limitante", ["No evaluado", "No observado hasta la profundidad explorada", "Lítico", "Paralítico", "Dénsico"], key="profile_contact", help=help_for('profile_contact'))
            contact_depth = st.number_input("Profundidad del contacto (cm)", min_value=0.0, value=None, key="profile_contact_depth", help=help_for('profile_contact_depth'))
        with right:
            moisture = st.selectbox("Régimen de humedad verificado", ["No evaluado", "Árídico / tórrico", "Údico", "Perúdico", "Ústico", "Xérico", "Ácuico", "Perácuico"], key="profile_moisture", help=help_for('profile_moisture'))
            temperature = st.selectbox("Régimen de temperatura verificado", ["No evaluado", "Gélico", "Cryic", "Frígido", "Mésico", "Térmico", "Hipertérmico", "Isofrígido", "Isomésico", "Isotérmico", "Isohipertérmico"], key="profile_temperature", help=help_for('profile_temperature'))
            mean_temp = st.number_input("Temperatura media anual del suelo (°C)", value=None, key="profile_mean_temp", help=help_for('profile_mean_temp'))
            seasonal_temp = st.number_input("Diferencia verano–invierno del suelo (°C)", min_value=0.0, value=None, key="profile_seasonal_temp", help=help_for('profile_seasonal_temp'))
            climate_evidence = st.text_area("Evidencia de los regímenes: profundidad, sección de control, período y método", key="profile_climate_evidence", help=help_for('profile_climate_evidence'))
            st.caption('Términos USDA: aridic/torric, udic, perudic, ustic, xeric, aquic y peraquic. Aquic conditions se evalúan además en los rasgos diagnósticos; no se deducen solo del régimen seleccionado. Temperatura: gelic, cryic, frigid, mesic, thermic, hyperthermic y variantes iso según definición.')
    location, photos = render_location_photos()
    from usda_capture import render_site, description_issues
    site_description = render_site()
    with st.expander("2. Descripción y laboratorio por horizonte", expanded=True):
        st.caption("Completa una ficha por horizonte o intervalo. Porcentajes texturales sobre tierra fina; conserva el método y base de cada medición.")
        horizons, derived_fractions = render_horizons()
    with st.expander("2b. Determinaciones de laboratorio para la clave USDA", expanded=False):
        laboratory_rows = render_laboratory(depth)
    with st.expander("3. Horizontes y propiedades diagnósticas"):
        st.caption("Marca Presente solo si se cumplen todos los criterios de la definición, incluidos espesor, profundidad y método. Una designación Bt o Bw no confirma por sí misma un horizonte diagnóstico.")
        st.markdown(f'[Definiciones oficiales: capítulo 3, Keys 2022]({SOURCE_URL}#page=19). Conserva en la evidencia el nombre oficial, sección o página y los requisitos evaluados.')
        with st.expander('Correspondencia de términos con USDA'):
            term = st.selectbox('Término que deseas consultar', list(DIAGNOSTIC_ENGLISH), key='profile_diagnostic_help')
            st.write(DIAGNOSTIC_ENGLISH[term])
            st.caption('Los rasgos vérticos y la cementación por hierro se documentan como evidencias; estas etiquetas no confirman por sí mismas un horizonte diagnóstico.')
        diagnostics = study_editor(pd.DataFrame({
            "Diagnóstico": DIAGNOSTICS, "Estado": ["No evaluado"] * len(DIAGNOSTICS),
            "Techo (cm)": [None] * len(DIAGNOSTICS), "Base (cm)": [None] * len(DIAGNOSTICS),
            "Evidencia / método / criterio": [""] * len(DIAGNOSTICS),
        }), hide_index=True, disabled=["Diagnóstico"], column_config=table_help(["Diagnóstico", "Estado", "Techo (cm)", "Base (cm)", "Evidencia / método / criterio"], {
            "Estado": st.column_config.SelectboxColumn(options=STATES, required=True),
            "Techo (cm)": st.column_config.NumberColumn(min_value=0.0),
            "Base (cm)": st.column_config.NumberColumn(min_value=0.0),
        }), key="profile_diagnostics")
    with st.expander("4. Saturación, reducción y rasgos diferenciales"):
        left, right = st.columns(2)
        with left:
            saturation = st.selectbox("Tipo de saturación", ["No evaluado", "Endosaturación", "Episaturación", "Saturación antrópica", "No observada en el período evaluado"], key="profile_saturation", help=help_for('profile_saturation'))
            water_depth = st.number_input("Profundidad de saturación observada (cm)", min_value=0.0, value=None, key="profile_water_depth", help=help_for('profile_water_depth'))
            water_days = st.number_input("Duración observada de saturación (días/año)", min_value=0, max_value=366, value=None, key="profile_water_days", help=help_for('profile_water_days'))
            reduction = st.selectbox("Evidencia de reducción", STATES, key="profile_reduction", help=help_for('profile_reduction'))
            redox_notes = st.text_area("Profundidad, abundancia y colores de depleciones/concentraciones; prueba de reducción y fechas", key="profile_redox_notes", help=help_for('profile_redox_notes'))
        with right:
            cracks_width = st.number_input("Ancho de grietas (mm)", min_value=0.0, value=None, key="profile_cracks_width", help=help_for('profile_cracks_width'))
            cracks_depth = st.number_input("Profundidad de grietas (cm)", min_value=0.0, value=None, key="profile_cracks_depth", help=help_for('profile_cracks_depth'))
            cracks_days = st.number_input("Duración de apertura (días/año)", min_value=0, max_value=366, value=None, key="profile_cracks_days", help=help_for('profile_cracks_days'))
            other = st.text_area("Otros rasgos: extensibilidad lineal y espesor evaluado, cuñas, discontinuidades, estratificación, distribución de carbono, materiales orgánicos/fibras, cementación, sulfuros o rasgos requeridos por la clave", key="profile_other", help=help_for('profile_other'))
        st.caption("Para aplicar criterios de espesor, volumen y duración, registra las medidas adicionales y la sección evaluada. COLE y extensibilidad lineal en cm son magnitudes distintas.")
        extra_fields = [
            ("Pendiente", "%"), ("Material transportado por humanos: espesor", "cm"),
            ("Saturación: máximo de días consecutivos en años normales", "días"),
            ("Saturación: días acumulados en años normales", "días"),
            ("Extensibilidad lineal integrada", "cm"),
            ("Capa con grietas: espesor", "cm"),
            ("Capa con slickensides o cuñas: techo", "cm"),
            ("Capa con slickensides o cuñas: espesor", "cm"),
            ("Propiedades frágicas: volumen", "%"),
            ("Propiedades frágicas: techo", "cm"),
            ("Propiedades frágicas: espesor", "cm"),
            ("Materiales orgánicos: espesor", "cm"),
            ("Fibras después de frotamiento", "%"),
        ]
        extra = study_editor(pd.DataFrame({
            "Parámetro": [p for p, u in extra_fields], "Unidad": [u for p, u in extra_fields],
            "Valor": pd.Series([None] * len(extra_fields), dtype="float64"),
            "Intervalo / método / evidencia": [""] * len(extra_fields),
        }), hide_index=True, disabled=["Parámetro", "Unidad"], column_config=table_help(["Parámetro", "Unidad", "Valor", "Intervalo / método / evidencia"], {
            "Valor": st.column_config.NumberColumn(min_value=0.0),
        }), key="profile_extra")

    records = json.loads(horizons.to_json(orient="records"))
    populated_indices = [i for i, r in enumerate(records) if any(v is not None and str(v).strip() for v in r.values())]
    records = [records[i] for i in populated_indices]
    horizon_refs = [{
        "horizon_uid": st.session_state.horizon_rows[i][HORIZON_ID],
        "row_number": n + 1,
        "label": records[n].get("Horizonte"),
    } for n, i in enumerate(populated_indices)]
    diagnostic_records = json.loads(diagnostics.to_json(orient="records"))
    errors, pending = validate_profile(records, diagnostic_records, depth)
    extra_records = json.loads(extra.to_json(orient='records'))
    for new_errors, new_pending in (laboratory_issues(laboratory_rows, depth), validate_extra(extra_records, depth), description_issues(st.session_state.get('profile_horizon_descriptions', {}), st.session_state.horizon_rows)):
        errors.extend(new_errors)
        pending.extend(new_pending)
    documentation = []
    for label, value in (('identificador del perfil', profile_id), ('responsable', observer), ('fecha de descripción', observed_date)):
        if value is None or not str(value).strip():
            documentation.append(f'Completar {label}.')
    if location and not location.get("completa"):
        documentation.append("Completar o corregir la ubicación que se empezó a registrar.")
    if contact in ["Lítico", "Paralítico", "Dénsico"]:
        if contact_depth is None:
            pending.append("Registrar la profundidad del contacto limitante.")
        elif depth is not None and contact_depth > depth:
            errors.append("El contacto está por debajo de la profundidad observada; amplía o justifica la observación.")
    if moisture == "No evaluado" or temperature == "No evaluado" or not climate_evidence.strip():
        pending.append("Documentar los regímenes y su evidencia; no inferirlos solo a partir del clima regional.")
    for label, measured_depth in (('Saturación', water_depth), ('Grietas', cracks_depth)):
        if measured_depth is not None and depth is not None and measured_depth > depth:
            errors.append(f'{label}: la profundidad supera la observación del perfil.')
    if contact in ('No evaluado', 'No observado hasta la profundidad explorada') and contact_depth is not None:
        pending.append('Revisar profundidad del contacto: no hay un tipo de contacto identificado.')
    if saturation == 'No observada en el período evaluado' and (water_depth is not None or (water_days or 0) > 0):
        errors.append('Saturación: se declararon medidas positivas junto con no observada; revisar el período y la evidencia.')
    st.subheader("Control de evidencias")
    for error in errors:
        st.error(error)
    for item in pending:
        st.warning(item)
    for item in documentation:
        st.warning('Documentación del pedón: ' + item)
    st.caption(f"{sum(r['Estado'] == 'No evaluado' for r in diagnostic_records)} diagnósticos no evaluados. La clave elegida determina cuáles son necesarios; no todos son obligatorios para cada perfil.")

    with st.expander("5. Ruta taxonómica documentada", expanded=True):
        st.write("Transcribe el taxón y código de la clave oficial en cada nivel. Documenta por qué cumple y por qué no entra en las opciones anteriores. Typic no es una salida por falta de datos.")
        route = study_editor(pd.DataFrame({
            "Nivel": ["Orden", "Suborden", "Gran grupo", "Subgrupo"],
            "Taxón": [""] * 4, "Clave / página": [""] * 4,
            "Evidencia y exclusión de anteriores": [""] * 4,
            "Revisión": ["Pendiente"] * 4,
        }), hide_index=True, disabled=["Nivel"], column_config=table_help(["Nivel", "Taxón", "Clave / página", "Evidencia y exclusión de anteriores", "Revisión"], {
            "Revisión": st.column_config.SelectboxColumn(options=["Pendiente", "No cumple", "Cumple; anteriores descartados"], required=True),
        }), key="profile_route")
        route_records = route.to_dict(orient="records")
        status, subgroup = evaluate_route(route_records, errors)
        if pending and subgroup:
            status = "Subgrupo propuesto por el usuario con evidencias pendientes; no validado"
        st.caption("Se comprueba la documentación, no la validez del nombre ni la coherencia taxonómica de esta ruta manual. La determinación requiere revisar las claves completas.")

    report = {
        "referencia": EDITION, "fuente": SOURCE_URL, "estado": status,
        "subgrupo_registrado_por_usuario": subgroup, "identificador": profile_id,
        "responsable": observer, "fecha_descripcion": observed_date.isoformat() if observed_date else None,
        "ubicacion": location, "fotos": [{k:v for k,v in photo.items() if k != "data"} for photo in photos],
        "fracciones_calculadas": [{"fila": populated_indices.index(d['fila'] - 1) + 1, "fraccion": d['fraccion']} for d in derived_fractions if d['fila'] - 1 in populated_indices],
        "profundidad_cm": depth, "origen_profundidades": reference,
        "contacto": contact, "profundidad_contacto_cm": contact_depth,
        "regimen_humedad": moisture, "regimen_temperatura": temperature,
        "temperatura_media_suelo_c": mean_temp, "diferencia_estacional_c": seasonal_temp,
        "evidencia_regimenes": climate_evidence, "horizontes": records,
        "diagnosticos": diagnostic_records, "saturacion": saturation,
        "profundidad_saturacion_cm": water_depth, "duracion_saturacion_dias": water_days,
        "reduccion": reduction, "evidencia_redox": redox_notes,
        "grietas_ancho_mm": cracks_width, "grietas_profundidad_cm": cracks_depth,
        "grietas_duracion_dias": cracks_days, "otros_rasgos": other,
        "medidas_adicionales": extra_records,
        "laboratorio": laboratory_rows,
        "descripcion_asistida": {'sitio': site_description, 'horizontes': st.session_state.get('profile_horizon_descriptions', {})},
        "laboratorio_historico_no_taxonomico": st.session_state.get('study_laboratory_legacy_current', []),
        "pendientes_documentacion": documentation,
        "ruta": route_records, "errores": errors, "pendientes": pending,
    }
    # La fila manual de subgrupo no modifica las evidencias de entrada de la guía.
    fingerprint = evidence_fingerprint(report)
    manual_proposal = str(route_records[-1].get('Taxón') or '').strip() or None
    manual_review = st.session_state.get('profile_manual_review', {})
    if manual_review.get('evidence_fingerprint') not in (None, fingerprint) and manual_review.get('had_proposal'):
        manual_review['requires_review'] = True
    manual_review.update(evidence_fingerprint=fingerprint, had_proposal=bool(manual_proposal))
    if manual_review.get('requires_review') and manual_proposal:
        st.warning('Cambió la evidencia que respalda la ruta manual. Se conservaron los textos; revisa su vigencia.')
        if st.button('Confirmar revisión de la ruta manual con la evidencia actual', key='profile_confirm_manual'):
            manual_review['requires_review'] = False
    if not manual_proposal:
        manual_review['requires_review'] = False
    st.session_state.profile_manual_review = manual_review
    report['revision_ruta_manual'] = dict(manual_review)
    with st.expander("6. Identificación con claves guiadas", expanded=True):
        guide = render_guide(route_records, errors + pending, fingerprint)
    report["clave_guiada"] = guide
    conclusion_pending = list(pending)
    if manual_proposal and (not subgroup or manual_review.get('requires_review')):
        conclusion_pending.append('Completar o revisar la ruta manual con la evidencia actual.')
    conclusion = determination(manual_proposal, guide, errors, conclusion_pending)
    report['pendientes_determinacion'] = conclusion_pending + ([guide['reason']] if guide and not guide.get('subgroup') else [])
    report['contradicciones'] = ['Los subgrupos manual y asistido difieren; revisar la ruta y las decisiones.'] if conclusion['discrepancia'] else []
    completed_levels = []
    for row in route_records:
        if row.get('Revisión') != 'Cumple; anteriores descartados' or any(not str(row.get(c) or '').strip() for c in ('Taxón', 'Clave / página', 'Evidencia y exclusión de anteriores')):
            break
        completed_levels.append(row['Nivel'])
    report['ultimo_nivel_documentado'] = completed_levels[-1] if completed_levels else None
    report['determinacion'] = conclusion
    report['estado'] = conclusion['estado']
    report['subgrupo_registrado_por_usuario'] = manual_proposal
    report['estado_ficha'] = 'Ficha incompleta' if documentation else 'Documentación básica completa'
    with summary:
        st.info(report['estado'])
        st.caption(f"{len(errors)} errores · {len(report['pendientes_determinacion'])} pendientes de determinación · {len(report['contradicciones'])} contradicciones · {len(documentation)} faltantes de documentación. {report['estado_ficha']}.")
    st.subheader('7. Determinación documentada y descarga')
    st.info(report['estado'])
    st.caption(f"Último nivel documentado en la ruta manual: {report['ultimo_nivel_documentado'] or 'ninguno'}.")
    st.write(f"Ruta manual: **{manual_proposal or 'Pendiente'}** · Clave asistida: **{conclusion['subgrupo_asistido'] or 'Pendiente'}**")
    if conclusion['discrepancia']:
        st.error('Los subgrupos difieren. Revisa las evidencias y corrige la ruta o las decisiones de la guía; no se adopta un subgrupo mientras exista la discrepancia.')
    st.write(f"Subgrupo adoptado: **{conclusion['subgrupo_adoptado'] or 'Pendiente'}**")
    st.caption('El resultado está condicionado a la evidencia declarada y a la revisión de las claves completas. No constituye una validación taxonómica independiente.')
    st.caption('JSON: ficha, ruta y evidencias, sin imágenes originales. ZIP de ficha: añade fotos del perfil. Guardar estudio completo, al final de la app: respaldo editable con originales e historial de análisis.')
    # La trazabilidad no forma parte de la huella de evidencia taxonómica:
    # registrar/revisar una propuesta no equivale a modificar el perfil.
    report = extend_report(report, profile_uid=st.session_state.profile_uid,
                           horizon_refs=horizon_refs,
                           observations=st.session_state.visual_observations)
    st.session_state.study_report = report
    st.session_state.study_current_photos = photos
    st.download_button("Descargar ficha y ruta (JSON)", json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), "perfil_taxonomico.json", "application/json", key="profile_download")
    st.download_button("Descargar ficha + fotos (ZIP)", make_archive(report, photos), "perfil_con_fotos.zip", "application/zip", key="profile_download_zip",
        help="Incluye el JSON con coordenadas, fecha, resultados y decisiones, más los archivos originales de las fotos aceptadas.")

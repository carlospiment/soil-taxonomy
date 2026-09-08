"""Ficha pedológica y documentación de la determinación taxonómica."""
import json
import hashlib
import pandas as pd
import streamlit as st
from field_help import help_for, table_help
from horizon_editor import render_horizons
from field_media import render_location_photos, make_archive
from subgroup_guide import render_guide
from soil_profile import (
    SOURCE_URL, EDITION, STATES, DIAGNOSTICS, validate_profile, evaluate_route,
)


def render_profile():
    st.header("Perfil pedológico e identificación al subgrupo")
    st.write("Registra las evidencias y documenta cada paso de las claves: orden → suborden → gran grupo → subgrupo.")
    st.info("Este módulo organiza una determinación asistida. Incluye claves guiadas de Hapludults y Dystrudepts; los demás grupos requieren la clave oficial. Un dato vacío significa no medido, no cero; un diagnóstico no evaluado no equivale a ausente.")
    st.markdown(f"Referencia: [{EDITION}]({SOURCE_URL}). Consultar las definiciones completas y las claves del orden correspondiente.")

    with st.expander("1. Identificación, profundidad y regímenes", expanded=True):
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
            moisture = st.selectbox("Régimen de humedad verificado", ["No evaluado", "Árídico / tórrico", "Údico", "Perúdico", "Ústico", "Xérico"], key="profile_moisture", help=help_for('profile_moisture'))
            temperature = st.selectbox("Régimen de temperatura verificado", ["No evaluado", "Gélico", "Cryic", "Frígido", "Mésico", "Térmico", "Hipertérmico", "Isofrígido", "Isomésico", "Isotérmico", "Isohipertérmico"], key="profile_temperature", help=help_for('profile_temperature'))
            mean_temp = st.number_input("Temperatura media anual del suelo (°C)", value=None, key="profile_mean_temp", help=help_for('profile_mean_temp'))
            seasonal_temp = st.number_input("Diferencia verano–invierno del suelo (°C)", min_value=0.0, value=None, key="profile_seasonal_temp", help=help_for('profile_seasonal_temp'))
            climate_evidence = st.text_area("Evidencia de los regímenes: profundidad, sección de control, período y método", key="profile_climate_evidence", help=help_for('profile_climate_evidence'))
    location, photos = render_location_photos()
    with st.expander("2. Descripción y laboratorio por horizonte", expanded=True):
        st.caption("Añade una fila por horizonte o intervalo de muestreo. Porcentajes texturales sobre tierra fina. Mantén separados los métodos de saturación de bases y las unidades de CIC del suelo y de la arcilla.")
        horizons, derived_fractions = render_horizons()
    with st.expander("3. Horizontes y propiedades diagnósticas"):
        st.caption("Marca Presente solo si se cumplen todos los criterios de la definición, incluidos espesor, profundidad y método. Una designación Bt o Bw no confirma por sí misma un horizonte diagnóstico.")
        diagnostics = st.data_editor(pd.DataFrame({
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
        extra = st.data_editor(pd.DataFrame({
            "Parámetro": [p for p, u in extra_fields], "Unidad": [u for p, u in extra_fields],
            "Valor": pd.Series([None] * len(extra_fields), dtype="float64"),
            "Intervalo / método / evidencia": [""] * len(extra_fields),
        }), hide_index=True, disabled=["Parámetro", "Unidad"], column_config=table_help(["Parámetro", "Unidad", "Valor", "Intervalo / método / evidencia"], {
            "Valor": st.column_config.NumberColumn(min_value=0.0),
        }), key="profile_extra")

    records = json.loads(horizons.to_json(orient="records"))
    records = [r for r in records if any(v is not None and str(v).strip() for v in r.values())]
    diagnostic_records = json.loads(diagnostics.to_json(orient="records"))
    errors, pending = validate_profile(records, diagnostic_records, depth)
    if location and not location.get("completa"):
        pending.append("Completar o corregir la ubicación que se empezó a registrar.")
    if contact in ["Lítico", "Paralítico", "Dénsico"]:
        if contact_depth is None:
            pending.append("Registrar la profundidad del contacto limitante.")
        elif depth is not None and contact_depth > depth:
            errors.append("El contacto está por debajo de la profundidad observada; amplía o justifica la observación.")
    if moisture == "No evaluado" or temperature == "No evaluado" or not climate_evidence.strip():
        pending.append("Documentar los regímenes y su evidencia; no inferirlos solo a partir del clima regional.")
    st.subheader("Control de evidencias")
    for error in errors:
        st.error(error)
    for item in pending:
        st.warning(item)
    st.caption(f"{sum(r['Estado'] == 'No evaluado' for r in diagnostic_records)} diagnósticos no evaluados. La clave elegida determina cuáles son necesarios; no todos son obligatorios para cada perfil.")

    with st.expander("5. Ruta taxonómica documentada", expanded=True):
        st.write("Transcribe el taxón y código de la clave oficial en cada nivel. Documenta por qué cumple y por qué no entra en las opciones anteriores. Typic no es una salida por falta de datos.")
        route = st.data_editor(pd.DataFrame({
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
        st.info(status)
        if subgroup:
            st.write(f"Subgrupo registrado: **{subgroup}**")
        st.caption("Se comprueba la documentación, no la validez del nombre ni la coherencia taxonómica de esta ruta manual. La determinación requiere revisar las claves completas.")

    report = {
        "referencia": EDITION, "fuente": SOURCE_URL, "estado": status,
        "subgrupo_registrado_por_usuario": subgroup, "identificador": profile_id,
        "responsable": observer, "fecha_descripcion": observed_date.isoformat() if observed_date else None,
        "ubicacion": location, "fotos": [{k:v for k,v in photo.items() if k != "data"} for photo in photos],
        "fracciones_calculadas": derived_fractions,
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
        "medidas_adicionales": json.loads(extra.to_json(orient="records")),
        "ruta": route_records, "errores": errors, "pendientes": pending,
    }
    # La fila manual de subgrupo no modifica las evidencias de entrada de la guía.
    guide_input = {**report, "ruta": route_records[:3]}
    guide_input.pop("estado")
    guide_input.pop("subgrupo_registrado_por_usuario")
    fingerprint = hashlib.sha256(json.dumps(guide_input, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    with st.expander("6. Identificación con claves guiadas", expanded=True):
        guide = render_guide(route_records, errors + pending, fingerprint)
    report["clave_guiada"] = guide
    if guide and guide.get("subgroup"):
        report["estado"] = "Subgrupo por clave asistida; condicionado a la evidencia declarada"
    st.download_button("Descargar ficha y ruta (JSON)", json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), "perfil_taxonomico.json", "application/json", key="profile_download")
    st.download_button("Descargar ficha + fotos (ZIP)", make_archive(report, photos), "perfil_con_fotos.zip", "application/zip", key="profile_download_zip",
        help="Incluye el JSON con coordenadas, fecha, resultados y decisiones, más los archivos originales de las fotos aceptadas.")

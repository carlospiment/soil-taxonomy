"""ROI, calidad y estimación orientativa; nunca aplica datos confirmados."""
import hashlib
import io
import json
import math
import zipfile

import streamlit as st

from image_io import STRUCTURE_POLICY, load_rgb_image
from soil_color.roi import ROI_VERSION, extract_roi, masked_preview, rectangle_from_percent, selection_preview
from soil_color.quality_control import QUALITY_VERSION, assess_quality
from visual_observations import HORIZON_ID, create_observation
from soil_color.color_spaces import load_srgb_image
from soil_color.munsell import COLOR_VERSION, estimate_color


def evaluation_archive(observation, original, image_format):
    """Paquete reproducible: coordenadas/máscara declarativa y archivo original."""
    if hashlib.sha256(original).hexdigest() != observation["image_sha256"]:
        raise ValueError("La imagen no corresponde a la evaluación.")
    extension = {"JPEG": "jpg", "PNG": "png"}[image_format]
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("evaluacion_color.json", json.dumps(observation, ensure_ascii=False, indent=2, allow_nan=False))
        archive.writestr(f"imagen_original.{extension}", original)
    return output.getvalue()


def render_color():
    st.header("Color del suelo: región y calidad")
    st.write("Selecciona una zona representativa del suelo y revisa la fotografía antes de estudiar su color.")
    st.caption("Evaluación local y orientativa. La foto no se envía a Roboflow. La estimación de color no está calibrada ni sustituye la determinación de campo.")
    estimate = st.checkbox("Estimar Munsell orientativo (imagen no calibrada)", key="color_estimate")

    source = st.radio("Origen de la fotografía de color", ["Subir fotografía", "Cámara"], horizontal=True, key="color_source")
    if source == "Cámara":
        uploaded = st.camera_input("Fotografía de la muestra para color", key="color_camera")
    else:
        uploaded = st.file_uploader("Fotografía para seleccionar la región de color", type=["jpg", "jpeg", "png"], key="color_photo")
    if uploaded is None:
        st.session_state.pop("color_qc_result", None)
        return
    data = uploaded.getvalue()
    try:
        image, metadata = load_srgb_image(data) if estimate else load_rgb_image(data, STRUCTURE_POLICY)
    except ValueError as error:
        st.session_state.pop("color_qc_result", None)
        st.error(str(error))
        return

    rows = {r[HORIZON_ID]: r for r in st.session_state.get("horizon_rows", [])
            if str(r.get("Horizonte") or "").strip()}
    if not rows:
        st.info("Añade y nombra al menos un horizonte en «Perfil y subgrupo» para vincular la selección.")
        st.session_state.pop("color_qc_result", None)
        st.image(image, width="stretch")
        return
    horizon = st.selectbox("Horizonte de la muestra", [None] + list(rows),
        format_func=lambda uid: "Selecciona un horizonte" if uid is None else f"{rows[uid]['Horizonte']} · {rows[uid].get('Techo (cm)')}–{rows[uid].get('Base (cm)')} cm · {uid[:8]}",
        key="color_horizon")
    moisture = st.radio("Condición de la muestra fotografiada", ["Sin indicar", "Seco", "Húmedo"], horizontal=True, key="color_moisture")
    preparation = st.text_input("Preparación de la muestra", key="color_preparation", help="Por ejemplo: superficie natural, agregado o muestra triturada y alisada.")
    illumination = st.text_input("Iluminación utilizada", key="color_illumination", help="Describe la luz y las condiciones de captura; no implica calibración.")
    device = st.text_input("Dispositivo (si lo conoces)", key="color_device")
    target = st.selectbox("Qué representa la región", ["Matriz del suelo", "Depleción", "Concentración", "Agregado", "Otro"], key="color_target")

    st.subheader("Selecciona la región de interés (ROI)")
    st.caption("Verde: región elegida. Rojo: zonas excluidas. Los controles se refieren a la imagen orientada, independientemente del tamaño de la pantalla.")
    horizontal = st.slider("Límites horizontales de la región (%)", 0, 100, (10, 90), key="color_x")
    vertical = st.slider("Límites verticales de la región (%)", 0, 100, (10, 90), key="color_y")
    count = st.selectbox("Número de zonas a excluir", [0, 1, 2, 3], key="color_exclusion_count")
    exclusions = []
    try:
        box = rectangle_from_percent(image.size, horizontal, vertical)
        for i in range(count):
            x = st.slider(f"Exclusión {i+1}: límites horizontales (%)", 0, 100, (40, 60), key=f"color_exclusion_x_{i}")
            y = st.slider(f"Exclusión {i+1}: límites verticales (%)", 0, 100, (40, 60), key=f"color_exclusion_y_{i}")
            exclusions.append(rectangle_from_percent(image.size, x, y))
        crop, mask = extract_roi(image, box, exclusions)
    except ValueError as error:
        st.session_state.pop("color_qc_result", None)
        st.error(str(error))
        return
    st.image(selection_preview(image, box, exclusions), caption="Selección sobre la fotografía", width="stretch")
    st.image(masked_preview(crop, mask), caption="Región seleccionada; gris indica píxeles excluidos", width="stretch")
    st.caption("Excluye manualmente raíces, piedras, residuos, carta, sombras fuertes y reflejos. El sistema no reconoce esos objetos automáticamente. No elimines rasgos redox si son el objeto de estudio.")

    selected = rows.get(horizon, {})
    snapshot = {"horizon_uid": horizon, "label": selected.get("Horizonte")}
    for field in ("Techo (cm)", "Base (cm)"):
        value = selected.get(field)
        snapshot[field] = float(value) if isinstance(value, (int, float)) and math.isfinite(value) else None
    context = {"image": metadata, "horizon_snapshot": snapshot,
               "profile_label": st.session_state.get("profile_id", ""),
               "preparation": preparation, "illumination": illumination,
               "device": device or None, "target": target,
               "calibration": {"applied": False, "reference": None},
               "roi": {"algorithm_version": ROI_VERSION, "box": box, "exclusions": exclusions,
                       "coordinate_system": "oriented-image-pixels; origin=top-left; right/bottom exclusive"}}
    signature = hashlib.sha256(json.dumps({"context": context, "moisture": moisture,
        "profile_uid": st.session_state.profile_uid, "quality_version": QUALITY_VERSION,
        "color_version": COLOR_VERSION if estimate else None},
        sort_keys=True, allow_nan=False).encode()).hexdigest()
    saved = st.session_state.get("color_qc_result")
    if saved and saved["signature"] != signature:
        st.session_state.pop("color_qc_result", None)
    if horizon is None or moisture == "Sin indicar":
        st.info("Selecciona el horizonte y la condición seca/húmeda antes de registrar la evaluación.")
    if st.button("Evaluar y registrar selección", key="color_evaluate", disabled=horizon is None or moisture == "Sin indicar"):
        quality = assess_quality(crop, mask)
        predicted = estimate_color(quality) if estimate else {
            "stage": "roi_quality_only", "munsell": None,
            "rgb_observed_median": quality["metrics"].get("rgb_median")}
        # Un registro de calidad rechazado se conserva como evidencia del intento.
        # No asigna Munsell ni modifica las columnas manuales del horizonte.
        context["evaluation_signature"] = signature
        ledger = st.session_state.visual_observations
        previous = next((o for o in ledger if o.get("context", {}).get("evaluation_signature") == signature), None)
        observation = previous or create_observation(
            profile_uid=st.session_state.profile_uid, horizon_uid=horizon,
            image_sha256=metadata["sha256"], kind="color",
            moisture_state={"Seco": "dry", "Húmedo": "moist"}[moisture],
            predicted_value=predicted,
            method="uncalibrated-renotation" if estimate else "roi-quality-exploratory",
            algorithm_version=COLOR_VERSION if estimate else QUALITY_VERSION,
            context=context, quality=quality)
        archive = evaluation_archive(observation, data, metadata["formato"])
        if previous is None:
            st.session_state.visual_observations = ledger + [observation]
        st.session_state.color_qc_result = {"signature": signature, "observation": observation, "archive": archive}
        # Actualiza las descargas del perfil, renderizadas en la primera pestaña.
        st.rerun()

    saved = st.session_state.get("color_qc_result")
    if saved:
        observation = saved["observation"]
        quality = observation["quality"]
        st.subheader("Evaluación exploratoria")
        if quality["status"] == "rejected":
            st.error("Región no adecuada para esta evaluación. Ajusta la selección o toma otra fotografía.")
        elif quality["status"] == "review":
            st.warning("La fotografía requiere revisión visual de los indicadores siguientes.")
        else:
            st.info("No se activaron las alertas iniciales. Esto no certifica calidad colorimétrica ni calibración.")
        for issue in quality["issues"]:
            st.write("• " + issue["message"])
        st.caption("Umbrales exploratorios, todavía no validados con muestras de suelo. Oscuridad puede ser color real; poco detalle puede ser uniformidad y no desenfoque. RGB describe la imagen, no un color absoluto.")
        st.json(quality)
        prediction = observation["predicted_value"]
        if prediction.get("status") == "not_estimated":
            st.warning("No se estimó Munsell: ajusta la región o la exposición y repite la evaluación. Los indicadores se conservaron.")
        if prediction.get("munsell"):
            st.subheader("Munsell estimado — imagen no calibrada")
            st.write(prediction["munsell"])
            st.caption("Candidato más próximo en la renotación discreta. ΔE00 mide distancia al candidato, no confianza ni precisión frente al suelo real. Las alternativas pueden no existir en tu carta de campo.")
            st.write(f"Distancia ΔE00: {prediction['delta_e00']:.2f}")
            st.dataframe(prediction["alternatives"], hide_index=True)
            with st.expander("Conversiones y trazabilidad del color"):
                st.json(prediction)
        st.download_button("Descargar evaluación e imagen original (ZIP)", saved["archive"],
                           "evaluacion_color.zip", "application/zip", key="color_download")
        st.caption("Selección registrada como pendiente en esta sesión. El ZIP incluye la foto y los indicadores; la ficha del perfil incluye la observación, pero solo incluye esta foto si también la adjuntas allí. Descarga antes de cerrar. No hay guardado permanente ni validación humana aplicada.")

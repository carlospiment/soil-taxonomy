"""Interfaz experimental de estructura; no aplica propuestas a la taxonomía."""
import hashlib
import json
import os
from datetime import datetime, timezone

import numpy as np
import streamlit as st

from image_io import load_rgb_image
from soil_structure.prediction import summarize_predictions
from soil_structure.roboflow_client import WorkflowConfig, WorkflowError, run_workflow


def _setting(name):
    value = os.environ.get(name, "")
    if not value:
        try:
            value = st.secrets.get(name, "")
        except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
            pass
    return value


def render_estructura_usda():
    st.header("Análisis de Estructura USDA")
    st.write("Sube una fotografía cercana y nítida de la muestra de suelo o toma una foto.")
    st.caption("Al pulsar Analizar, la imagen se enviará a Roboflow. Las etiquetas dependen del modelo entrenado y requieren revisión de campo.")
    api_key = _setting("ROBOFLOW_API_KEY")
    if not api_key:
        api_key = st.text_input("Clave API de Roboflow", type="password", key="rf_api_key",
                                help="También puedes configurar ROBOFLOW_API_KEY en los secretos de Streamlit o como variable de entorno.")
    try:
        config = WorkflowConfig(workflow_version_id=_setting("ROBOFLOW_WORKFLOW_VERSION_ID") or None)
    except (TypeError, ValueError):
        st.error("Revisa la versión del workflow configurada en ROBOFLOW_WORKFLOW_VERSION_ID.")
        st.session_state.pop("rf_result", None)
        return

    origen = st.radio("Origen de la imagen", ["Subir fotografía", "Cámara"], horizontal=True, key="rf_source")
    if origen == "Cámara":
        archivo = st.camera_input("Toma una fotografía del suelo", key="rf_camera")
    else:
        archivo = st.file_uploader("Selecciona una imagen de suelo", type=["jpg", "jpeg", "png"], key="rf_photo")
    if archivo is None:
        st.session_state.pop("rf_result", None)
        return
    try:
        imagen, metadata = load_rgb_image(archivo.getvalue())
    except ValueError as error:
        st.session_state.pop("rf_result", None)
        st.error(str(error))
        return

    st.image(imagen, caption="Muestra de suelo", width="stretch")
    # Conservado como referencia orientativa, independiente de la inferencia.
    miniatura = imagen.copy()
    miniatura.thumbnail((256, 256))
    rgb = np.rint(np.asarray(miniatura).mean(axis=(0, 1))).astype(int)
    hexadecimal = "#{:02X}{:02X}{:02X}".format(*rgb)
    st.write(f"Color promedio de la fotografía: RGB {tuple(int(c) for c in rgb)} · {hexadecimal}")
    st.caption("Color orientativo de toda la imagen, incluido el fondo; no es una medición Munsell ni un color por horizonte.")

    identity = hashlib.sha256(json.dumps({"image": metadata["sha256"],
        "config": config.metadata(), "credential": hashlib.sha256(str(api_key).encode()).hexdigest()},
        sort_keys=True).encode()).hexdigest()
    saved = st.session_state.get("rf_result")
    if not isinstance(saved, dict) or saved.get("identity") != identity:
        st.session_state.pop("rf_result", None)
    if st.button("Analizar estructura", key="rf_analyze", disabled=not bool(api_key)):
        st.session_state.pop("rf_result", None)
        try:
            with st.spinner("Analizando la imagen con Roboflow…"):
                raw = run_workflow(imagen, api_key, config)
                summary = summarize_predictions(raw["outputs"])
                # Valida también la serialización antes de guardar/presentar.
                result = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
                          "image": metadata, "workflow": config.metadata(),
                          "summary": summary, "raw_response": raw}
                json.dumps(result, allow_nan=False)
            st.session_state["rf_result"] = {"identity": identity, "result": result}
        except WorkflowError as error:
            st.error(str(error))
            return
        except Exception:
            st.error("No se pudo preparar o interpretar el resultado de Roboflow. Revisa la configuración del workflow.")
            return

    saved = st.session_state.get("rf_result")
    if saved:
        result = saved["result"]
        summary = result["summary"]
        st.subheader("Resultados del workflow")
        if summary["status"] == "empty":
            st.info("El workflow no devolvió salidas para esta fotografía.")
        elif summary["status"] == "no_detections":
            st.info("Las listas de predicciones reconocidas están vacías. Consulta la respuesta completa para otras salidas.")
        elif summary["status"] == "unrecognized":
            st.info("El formato de salida todavía no tiene un resumen compatible. Consulta la respuesta completa.")
        if summary["predictions"]:
            st.dataframe([{"Clase propuesta": p["class"], "Confianza": p["confidence"],
                           "Salida": p["source"]} for p in summary["predictions"]], hide_index=True)
        if summary["partial"]:
            st.warning("El resumen no interpreta todas las predicciones. Revisa la respuesta completa.")
        st.json(result["raw_response"])
        st.download_button("Descargar resultado de estructura (JSON)",
                           json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False),
                           "estructura_suelo.json", "application/json", key="rf_download")
        st.caption("Resultado experimental. El archivo conserva la respuesta y la configuración; no confirma el tipo, tamaño o grado ni modifica el perfil.")

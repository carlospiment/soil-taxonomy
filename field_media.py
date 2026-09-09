"""Ubicación, fotografías y exportación autocontenida del perfil."""
import hashlib
import io
import json
import math
import re
import zipfile
from image_io import PROFILE_POLICY, inspect_image
from pyproj import Transformer


def utm_to_geographic(zone, hemisphere, easting, northing):
    if not isinstance(zone, int) or not 1 <= zone <= 60 or hemisphere not in ("Norte", "Sur"):
        raise ValueError("Selecciona una zona UTM (1–60) y un hemisferio.")
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (easting, northing)):
        raise ValueError("Completa Este y Norte en metros.")
    if not 100000 <= easting <= 900000 or not 0 <= northing <= 10000000:
        raise ValueError("Coordenadas fuera del intervalo de trabajo UTM: Este 100000–900000 m; Norte 0–10000000 m.")
    epsg = (32600 if hemisphere == "Norte" else 32700) + zone
    lon, lat = Transformer.from_crs(epsg, 4326, always_xy=True).transform(easting, northing, errcheck=True)
    if not -80 <= lat <= 84 or (hemisphere == "Norte" and lat < -1e-8) or (hemisphere == "Sur" and lat > 1e-8):
        raise ValueError("La ubicación no corresponde al hemisferio o cobertura UTM (80°S–84°N).")
    return {"latitud": lat, "longitud": lon, "epsg_origen": epsg, "epsg_destino": 4326}


def validate_photo(data):
    return inspect_image(data, PROFILE_POLICY)


def make_archive(report, photos):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("perfil_taxonomico.json", json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
        for photo in photos:
            archive.writestr(photo["ruta_zip"], photo["data"])
    return stream.getvalue()


def render_location_photos():
    import streamlit as st
    location = {}
    with st.expander("1B. Coordenadas y fotografías", expanded=True):
        mode = st.selectbox("Sistema de coordenadas", ["Sin registrar", "Geográficas (grados decimales)", "UTM (metros)"], key="location_mode",
            help="Elige el sistema indicado por tu GPS o cartografía. No confundas grados decimales con grados/minutos/segundos.")
        if mode != "Sin registrar":
            datum = st.selectbox("Datum", ["WGS 84", "Otro (solo registro)"], key="location_datum",
                help="Referencia geodésica de las coordenadas. La conversión automática está disponible únicamente para WGS 84.")
            other = st.text_input("Nombre del otro datum / código EPSG", key="location_other_datum", help="Copia la referencia exacta de la fuente. Estos datos se guardan sin transformación.") if datum != "WGS 84" else ""
            location = {"sistema": mode, "datum": datum if not other else other}
            if mode.startswith("Geográficas"):
                lat = st.number_input("Latitud (°)", min_value=-90.0, max_value=90.0, value=None, format="%.6f", key="location_lat", help="Grados decimales: norte positivo, sur negativo. Ejemplo ilustrativo: 8.982400.")
                lon = st.number_input("Longitud (°)", min_value=-180.0, max_value=180.0, value=None, format="%.6f", key="location_lon", help="Grados decimales: este positivo, oeste negativo. En Panamá la longitud es negativa.")
                location.update(latitud=lat, longitud=lon, completa=lat is not None and lon is not None)
                if not location["completa"]:
                    st.warning("Completa latitud y longitud para registrar la ubicación.")
            else:
                zone = st.selectbox("Zona UTM", list(range(1,61)), index=None, key="location_zone", help="Número de zona 1–60. Cópialo del GPS; no lo deduzcas únicamente por el país.")
                hemisphere = st.selectbox("Hemisferio UTM", ["Norte", "Sur"], index=None, key="location_hemisphere", help="Norte o sur del ecuador. No es la letra de banda latitudinal de una cuadrícula UTM.")
                east = st.number_input("Este UTM (m)", min_value=0.0, value=None, format="%.3f", key="location_east", help="Easting en metros; no longitud en grados.")
                north = st.number_input("Norte UTM (m)", min_value=0.0, value=None, format="%.3f", key="location_north", help="Northing en metros; requiere zona, hemisferio y datum para ser interpretable.")
                location.update(zona=zone, hemisferio=hemisphere, este_m=east, norte_m=north, completa=all(v is not None for v in [zone, hemisphere, east, north]))
                if datum == "WGS 84":
                    try:
                        converted = utm_to_geographic(zone, hemisphere, east, north)
                        location["geograficas_wgs84"] = converted
                        st.caption(f"WGS 84: latitud {converted['latitud']:.6f}°, longitud {converted['longitud']:.6f}° · EPSG:{converted['epsg_origen']}")
                    except ValueError as exc:
                        location["completa"] = False
                        st.warning(str(exc))
                elif not location["completa"]:
                    st.warning("Completa zona, hemisferio, Este y Norte.")
            if datum != "WGS 84":
                location["transformacion"] = "No realizada; datum distinto de WGS 84"
                if not other.strip():
                    location["completa"] = False
                    st.warning("Indica el nombre del datum o su EPSG.")
            location["precision_m"] = st.number_input("Precisión horizontal estimada (m)", min_value=0.0, value=None, key="location_precision", help="Incertidumbre reportada por el GPS o la fuente cartográfica; no el número de decimales.")
        files = st.file_uploader("Fotografías del perfil", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="profile_photos",
            help="Hasta 10 fotos, 20 MB por foto y 60 MB en total. Añade una escala y el identificador del perfil cuando sea posible.")
        st.caption("Las fotos se conservan en esta sesión. Para guardarlas, descarga el ZIP al final; el JSON por sí solo contiene únicamente sus referencias y descripciones.")
        photos = []
        files = files or []
        if len(files) > 10 or sum(f.size for f in files) > 60 * 1024 * 1024:
            st.warning("Reduce la selección a un máximo de 10 fotos y 60 MB en total.")
            files = []
        for i, file in enumerate(files):
            data = file.getvalue()
            try:
                info = validate_photo(data)
            except ValueError as exc:
                st.warning(f"{file.name}: {exc}")
                continue
            sha = hashlib.sha256(data).hexdigest()
            safe_name = re.sub(r"[^\w.\-]", "_", file.name.replace("\\", "/").split("/")[-1])
            st.image(data, caption=file.name, width=350)
            caption = st.text_input("Descripción / horizonte de la foto", key=f"photo_caption_{i}_{sha}", help="Indica qué muestra la imagen, horizonte o profundidad, orientación y escala.")
            photos.append({"nombre_original": file.name, "ruta_zip": f"fotos/{i+1:02d}_{safe_name}", "descripcion": caption, "sha256": sha, **info, "data": data})
    return location, photos

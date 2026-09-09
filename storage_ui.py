"""Portable storage with validation before session replacement."""
import streamlit as st
from study_storage import build_study, load_study, restore_state


def render_study_import():
    with st.expander('Abrir estudio guardado'):
        st.caption('Abre un ZIP de estudio o una exportación anterior con fotos. Guarda primero el estudio actual.')
        uploaded = st.file_uploader('Archivo de estudio (ZIP)', type=['zip'], key='study_upload')
        confirmed = st.checkbox('Reemplazar el estudio abierto con el archivo seleccionado', key='study_replace')
        if st.button('Abrir estudio', disabled=uploaded is None or not confirmed, key='study_open'):
            try:
                study = load_study(uploaded.getvalue())
                state = restore_state(study['report'])
            except ValueError as error:
                st.error(str(error))
            else:
                for key in list(st.session_state):
                    if key.startswith(('profile_', 'horizon_', 'location_', 'guide_', 'color_', 'review_', 'reviewer_', 'reason_', 'action_', 'correction_', 'apply_', 'photo_caption_', 'study_')) or key in ('visual_observations', 'texture_selected', 'rf_result', 'rf_photo', 'rf_camera'):
                        if key not in ('study_upload', 'study_replace', 'study_open'):
                            del st.session_state[key]
                st.session_state.update(state)
                st.session_state.study_photos = study['photos']
                st.session_state.study_images = study['images']
                st.session_state.study_structures = study['structures']
                st.session_state.study_loaded = 'Estudio recuperado' + (' y migrado desde ZIP anterior.' if study['migrated'] else '.')
                st.rerun()
        if st.session_state.get('study_loaded'):
            st.success(st.session_state.study_loaded)


def render_study_export():
    st.subheader('Guardar estudio y respaldo')
    st.caption('Descarga el ZIP después de editar. Conserva otra copia en una ubicación independiente y comprueba que abre. El acceso a fotos, ubicación y responsables depende de los permisos de la carpeta donde lo guardes. El ZIP no está cifrado ni firmado.')
    report = st.session_state.get('study_report')
    if report is None:
        st.warning('La ficha del perfil todavía no está disponible para guardar. Abre Perfil y subgrupo. Si el aviso persiste, comprueba que profile_ui.py y storage_ui.py estén actualizados juntos en el despliegue.')
    else:
        try:
            archive = build_study(report, st.session_state.get('study_current_photos', []), st.session_state.get('study_images', {}), st.session_state.get('study_structures', []))
            st.download_button('Guardar estudio completo (ZIP)', archive, 'estudio_suelo.zip', 'application/zip', key='study_download')
        except ValueError as error:
            st.warning(str(error))
    if st.session_state.get('study_structures'):
        with st.expander('Resultados de estructura conservados'):
            st.json(st.session_state.study_structures)
    if st.session_state.get('study_images'):
        with st.expander('Fotografías originales conservadas para análisis'):
            from field_media import validate_photo
            for sha, data in st.session_state.study_images.items():
                st.image(data, caption=sha, width=350)
                extension = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}[validate_photo(data)['formato']]
                st.download_button('Descargar original ' + sha[:8], data, sha + '.' + extension, key='study_image_' + sha)

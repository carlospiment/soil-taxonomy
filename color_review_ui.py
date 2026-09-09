"""Revisión disponible aunque ya no esté cargada la fotografía."""
import json
import streamlit as st
from soil_color.validation import review_color, apply_color
from visual_observations import HORIZON_ID


def render_color_reviews():
    ledger = st.session_state.get('visual_observations', [])
    colors = [o for o in ledger if o['kind'] == 'color']
    if not colors:
        return
    with st.expander('Revisar y aplicar observaciones de color'):
        options = {o['observation_id']: o for o in colors}
        uid = st.selectbox('Observación a revisar', list(options), key='review_color_id',
            format_func=lambda key: f"{options[key]['context'].get('horizon_snapshot', {}).get('label', '')} · {options[key]['moisture_state']} · {options[key]['created_at']} · {key[:8]}")
        observation = options[uid]
        st.write('Propuesta original:', observation['predicted_value'].get('munsell') or 'Sin estimación Munsell')
        st.write('Estado:', observation['status'])
        st.json({'quality': observation['quality'], 'validated_value': observation['validated_value'],
                 'reviews': observation['reviews'], 'applications': observation.get('applications', [])})
        st.caption('Revisa la fotografía original y contrasta la determinación. El nombre del responsable es declarado, sin autenticación. Revisar no aplica el dato al perfil.')
        reviewer = st.text_input('Responsable de revisión/aplicación', key=f'reviewer_{uid}')
        reason = st.text_input('Motivo y evidencia de la revisión', key=f'reason_{uid}')
        action = st.selectbox('Decisión', ['Aceptar', 'Corregir', 'Rechazar'], key=f'action_{uid}')
        correction = st.text_input('Munsell corregido', key=f'correction_{uid}') if action == 'Corregir' else None
        if st.button('Guardar revisión', key=f'review_save_{uid}', disabled=bool(observation.get('applications'))):
            try:
                updated = review_color(observation, {'Aceptar': 'accepted', 'Corregir': 'corrected', 'Rechazar': 'rejected'}[action], reviewer, reason, correction)
                st.session_state.visual_observations = [updated if o['observation_id'] == uid else o for o in ledger]
                st.rerun()
            except ValueError as error:
                st.error(str(error))
        if observation['status'] in ('accepted', 'corrected') and not observation.get('applications'):
            row = next((r for r in st.session_state.horizon_rows if r[HORIZON_ID] == observation['horizon_uid']), None)
            if row is None:
                st.warning('El horizonte fue eliminado; esta observación no puede aplicarse.')
            else:
                field = 'Color seco (Munsell)' if observation['moisture_state'] == 'dry' else 'Color húmedo (Munsell)'
                previous = row.get(field)
                proposed = observation['validated_value']['munsell']
                st.write(f"Horizonte {row.get('Horizonte')}: {field}: {previous or '(vacío)'} → {proposed}")
                confirmed = st.checkbox('Confirmo aplicar este cambio al horizonte', key=f'apply_confirm_{uid}_{previous}_{proposed}')
                if st.button('Aplicar color confirmado al perfil', key=f'apply_color_{uid}', disabled=not confirmed):
                    try:
                        updated, rows = apply_color(observation, st.session_state.horizon_rows, st.session_state.profile_uid, previous, reviewer)
                        st.session_state.visual_observations = [updated if o['observation_id'] == uid else o for o in ledger]
                        st.session_state.horizon_rows = rows
                        st.session_state.horizon_revision += 1
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))
        if observation.get('applications'):
            st.info('Aplicación registrada. Las ediciones manuales posteriores no se deshacen desde aquí; una nueva determinación puede sustituir el dato mediante otra aplicación explícita.')
        st.download_button('Descargar observación revisada (JSON)', json.dumps(observation, ensure_ascii=False, indent=2, allow_nan=False),
                           'observacion_revisada.json', 'application/json', key=f'review_download_{uid}')

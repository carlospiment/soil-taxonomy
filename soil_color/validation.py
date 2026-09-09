"""Revisión y aplicación explícita de colores; operaciones sobre copias."""
from copy import deepcopy
import re

from visual_observations import HORIZON_ID, review_observation, new_id, _timestamp


def normalize_munsell(value):
    text = str(value or '').strip().upper()
    match = re.fullmatch(r'N\s*(\d+(?:\.\d+)?)\s*(?:/\s*0)?', text)
    if match and 0 <= float(match[1]) <= 10:
        return f'N{float(match[1]):g}'
    match = re.fullmatch(r'(\d+(?:\.\d+)?)(YR|GY|BG|PB|RP|R|Y|G|B|P)\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)', text)
    if match:
        hue, family, value, chroma = match.groups()
        if 0 < float(hue) <= 10 and 0 < float(value) < 10 and 0 < float(chroma) <= 50:
            return f'{float(hue):g}{family} {float(value):g}/{float(chroma):g}'
    raise ValueError('Usa notación Munsell, por ejemplo 10YR 4/3 o N5. Se comprueba formato y rango, no existencia en una carta.')


def review_color(observation, action, reviewer, reason, correction=None):
    if observation['kind'] != 'color':
        raise ValueError('La revisión requiere una observación de color.')
    if observation.get('applications'):
        raise ValueError('Esta observación ya fue aplicada. Conserva su historial y registra una nueva determinación para sustituirla.')
    corrected = None
    if action == 'accepted':
        normalize_munsell(observation['predicted_value'].get('munsell'))
    elif action == 'corrected':
        corrected = {'munsell': normalize_munsell(correction), 'source': 'human_review'}
    return review_observation(observation, action=action, reviewer=reviewer,
                              reason=reason, corrected_value=corrected)


def apply_color(observation, rows, profile_uid, expected_value, reviewer):
    if observation['profile_uid'] != profile_uid or observation['kind'] != 'color':
        raise ValueError('La observación no corresponde a este perfil.')
    if observation['status'] not in ('accepted', 'corrected') or not observation['reviews']:
        raise ValueError('Primero acepta o corrige la propuesta.')
    if observation.get('applications'):
        raise ValueError('Esta observación ya fue aplicada.')
    if not reviewer.strip():
        raise ValueError('Indica quién aplica el dato.')
    field = {'dry': 'Color seco (Munsell)', 'moist': 'Color húmedo (Munsell)'}[observation['moisture_state']]
    matches = [i for i, row in enumerate(rows) if row.get(HORIZON_ID) == observation['horizon_uid']]
    if len(matches) != 1:
        raise ValueError('El horizonte ya no existe o su identidad es ambigua.')
    index = matches[0]
    if rows[index].get(field) != expected_value:
        raise ValueError('El valor del horizonte cambió. Revisa el cambio antes de aplicar.')
    value = normalize_munsell(observation['validated_value'].get('munsell'))
    updated_rows, updated = deepcopy(rows), deepcopy(observation)
    updated_rows[index][field] = value
    updated['applications'] = [{'application_id': new_id(), 'review_id': updated['reviews'][-1]['review_id'],
        'applied_at': _timestamp(), 'reviewer': reviewer.strip(), 'field': field,
        'previous_value': expected_value, 'applied_value': value}]
    return updated, updated_rows

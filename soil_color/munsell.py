"""Búsqueda discreta ΔE00 en renotación real; no catálogo de una carta comercial."""
from functools import lru_cache
import hashlib
import json

import colour
import numpy as np

from soil_color.color_spaces import srgb_to_spaces

COLOR_VERSION = 'renotation-real-de00-v1'


@lru_cache(maxsize=1)
def _catalogue():
    entries, coordinates = [], []
    for (hue, value, chroma), xyY in colour.MUNSELL_COLOURS['real']:
        entries.append({'munsell': f'{hue} {value:g}/{chroma:g}',
                        'hue': hue, 'value': float(value), 'chroma': float(chroma)})
        coordinates.append([float(xyY[0]), float(xyY[1]), float(xyY[2]) / 100])
    # Neutros por función publicada de renotación; no asignar matiz a un gris.
    with colour.utilities.domain_range_scale('reference'):
        for value in range(1, 10):
            entries.append({'munsell': f'N{value}', 'hue': 'N', 'value': float(value), 'chroma': 0.0})
            coordinates.append(colour.munsell_colour_to_xyY(f'N{value}').tolist())
        white = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['C']
        labs = colour.XYZ_to_Lab(colour.xyY_to_XYZ(coordinates), illuminant=white)
    digest = hashlib.sha256(json.dumps([entries, coordinates], sort_keys=True).encode()).hexdigest()
    labs.setflags(write=False)
    return entries, labs, digest


def nearest_munsell(lab):
    lab = np.asarray(lab, dtype=float)
    if lab.shape != (3,) or not np.isfinite(lab).all():
        raise ValueError('Lab debe contener tres valores finitos.')
    entries, labs, digest = _catalogue()
    with colour.utilities.domain_range_scale('reference'):
        distances = colour.delta_E(lab, labs, method='CIE 2000')
    indices = np.argsort(distances, kind='stable')[:5]
    matches = [{**entries[i], 'delta_e00': float(distances[i])} for i in indices]
    return {'nearest': matches[0], 'alternatives': matches[1:],
            'catalogue': {'source': "colour.MUNSELL_COLOURS['real'] + N1..N9",
                          'count': len(entries), 'sha256': digest}}


def estimate_color(quality, calibration=None):
    result = {'stage': 'uncalibrated_color', 'munsell': None, 'calibrated': False,
              'algorithm_version': COLOR_VERSION, 'colour_version': colour.__version__,
              'rgb_observed_median': quality['metrics'].get('rgb_median'),
              'rgb_corrected': None, 'status': 'not_estimated',
              'method': 'component median encoded sRGB; Bradford D65 to C; nearest real renotation CIEDE2000',
              'observer': 'CIE 1931 2 degree', 'xyz_scale': 'Y white=1', 'lab_white': 'C'}
    if quality['status'] == 'rejected' or result['rgb_observed_median'] is None:
        result['reason'] = 'quality_rejected'
        return result
    if any(issue['code'] in ('dark', 'clipping') for issue in quality.get('issues', [])):
        result['reason'] = 'exposure_requires_review'
        return result
    rgb = result['rgb_observed_median']
    if calibration is not None:
        from soil_color.calibration import correct_rgb
        try:
            rgb = correct_rgb(rgb, calibration)
        except ValueError as error:
            result['reason'] = str(error)
            return result
        result.update({'rgb_corrected': rgb, 'calibrated': True,
                       'stage': 'neutral_reference_color', 'calibration': calibration,
                       'observed_spaces': srgb_to_spaces(result['rgb_observed_median'])})
        result['method'] = 'neutral linear RGB gains; ' + result['method']
    result.update(srgb_to_spaces(rgb))
    matches = nearest_munsell(result['lab_c'])
    result.update(matches)
    result.update(matches['nearest'])
    result['status'] = 'estimated_unvalidated'
    return result

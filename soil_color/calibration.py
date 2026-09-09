"""Corrección diagonal en RGB lineal con un parche neutro de reflectancia conocida.

No caracteriza la respuesta espectral de la cámara ni constituye validación científica.
"""
import colour
import numpy as np

CALIBRATION_VERSION = 'neutral-linear-gains-v1'


def fit_neutral_reference(quality, reflectance, reference_id):
    if not reference_id.strip():
        raise ValueError('Indica la identificación y procedencia de la referencia.')
    if not np.isfinite(reflectance) or not 0.02 <= reflectance <= 0.90:
        raise ValueError('La reflectancia debe estar entre 0.02 y 0.90.')
    if quality['status'] == 'rejected' or any(i['code'] in ('dark', 'clipping', 'variable_color') for i in quality['issues']):
        raise ValueError('La referencia es pequeña, heterogénea o tiene exposición inadecuada.')
    rgb = np.asarray(quality['metrics'].get('rgb_median'), dtype=float)
    if rgb.shape != (3,) or not np.isfinite(rgb).all() or np.any((rgb <= 10) | (rgb >= 245)):
        raise ValueError('La referencia necesita tres canales sin recorte ni oscuridad extrema.')
    with colour.utilities.domain_range_scale('reference'):
        linear = colour.cctf_decoding(rgb / 255, function='sRGB')
    gains = reflectance / linear
    if np.any((gains < .25) | (gains > 4)):
        raise ValueError('La corrección requerida es excesiva; revisa la referencia y la exposición.')
    return {'algorithm_version': CALIBRATION_VERSION, 'reference': reference_id.strip(),
            'reflectance': float(reflectance), 'reference_rgb': rgb.tolist(),
            'linear_gains': gains.tolist(), 'quality': quality,
            'scientifically_validated': False, 'scope': 'neutral balance and exposure only',
            'gain_limits': [.25, 4]}


def correct_rgb(rgb, calibration):
    rgb = np.asarray(rgb, dtype=float)
    gains = np.asarray(calibration['linear_gains'], dtype=float)
    if rgb.shape != (3,) or gains.shape != (3,) or not np.isfinite(rgb).all() or not np.isfinite(gains).all() or np.any((rgb < 0) | (rgb > 255)) or np.any((gains < .25) | (gains > 4)):
        raise ValueError('RGB o ganancias de calibración no válidos.')
    with colour.utilities.domain_range_scale('reference'):
        corrected = colour.cctf_decoding(rgb / 255, function='sRGB') * gains
        if np.any(corrected > 1) or np.any(corrected < 0):
            raise ValueError('El color corregido queda fuera de sRGB; no se recorta silenciosamente.')
        return (255 * colour.cctf_encoding(corrected, function='sRGB')).tolist()

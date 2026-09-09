"""Conversiones explícitas sRGB/D65 y adaptación Bradford a C, observador 2°."""
import io

import colour
import numpy as np
from PIL import Image, ImageCms, ImageOps

from image_io import load_rgb_image


def load_srgb_image(data):
    image, metadata = load_rgb_image(data)
    with Image.open(io.BytesIO(data)) as original:
        if 'A' in original.getbands() or 'transparency' in original.info:
            raise ValueError('Para estimar color utiliza una fotografía sin transparencia.')
        profile = original.info.get('icc_profile')
        if profile:
            try:
                oriented = ImageOps.exif_transpose(original)
                image = ImageCms.profileToProfile(oriented,
                    ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                    ImageCms.createProfile('sRGB'), outputMode='RGB', renderingIntent=1)
            except (ImageCms.PyCMSError, OSError, ValueError):
                raise ValueError('No se pudo convertir el perfil ICC a sRGB.') from None
        elif original.mode not in ('RGB', 'L'):
            raise ValueError('Sin perfil ICC se requiere una imagen RGB o gris.')
    metadata['color_management'] = 'ICC to sRGB; relative colorimetric' if profile else 'assumed sRGB; no ICC'
    metadata['pillow_version'] = Image.__version__
    return image, metadata


def srgb_to_spaces(rgb):
    rgb = np.asarray(rgb, dtype=float)
    if rgb.shape != (3,) or not np.isfinite(rgb).all() or np.any((rgb < 0) | (rgb > 255)):
        raise ValueError('RGB debe contener tres valores finitos entre 0 y 255.')
    whites = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']
    with colour.utilities.domain_range_scale('reference'):
        linear = colour.cctf_decoding(rgb / 255, function='sRGB')
        xyz = colour.sRGB_to_XYZ(rgb / 255)
        xyz_c = colour.adaptation.chromatic_adaptation_VonKries(
            xyz, colour.xy_to_XYZ(whites['D65']), colour.xy_to_XYZ(whites['C']), transform='Bradford')
        lab = colour.XYZ_to_Lab(xyz_c, illuminant=whites['C'])
    return {'srgb_linear': linear.tolist(), 'xyz_d65': xyz.tolist(),
            'xyz_c': xyz_c.tolist(), 'lab_c': lab.tolist()}

"""Lectura en memoria; verifica contenido real, sin calibración cromática."""
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError


@dataclass(frozen=True)
class ImagePolicy:
    formats: tuple[str, ...]
    max_pixels: int
    max_bytes: int = 20 * 1024 * 1024


PROFILE_POLICY = ImagePolicy(("JPEG", "PNG", "WEBP"), 40_000_000)
STRUCTURE_POLICY = ImagePolicy(("JPEG", "PNG"), 25_000_000)


def inspect_image(data, policy=PROFILE_POLICY):
    if not isinstance(data, bytes) or not data:
        raise ValueError("Selecciona una fotografía válida.")
    if len(data) > policy.max_bytes:
        raise ValueError(f"La fotografía supera {policy.max_bytes // (1024 * 1024)} MB.")
    try:
        with Image.open(BytesIO(data)) as original:
            if original.format not in policy.formats:
                raise ValueError("Formato no admitido. Usa " + ", ".join(policy.formats) + ".")
            if original.width * original.height > policy.max_pixels:
                raise ValueError(f"La imagen supera {policy.max_pixels // 1_000_000} megapíxeles.")
            if getattr(original, "n_frames", 1) != 1:
                raise ValueError("Selecciona una fotografía estática, no una animación.")
            info = {"ancho_px": original.width, "alto_px": original.height,
                    "formato": original.format}
            original.verify()
        # verify() no decodifica los píxeles de todos los formatos (p. ej. JPEG).
        with Image.open(BytesIO(data)) as decoded:
            decoded.load()
        return info
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
        raise ValueError("El archivo no es una imagen válida o está dañado.") from None


def load_rgb_image(data, policy=STRUCTURE_POLICY):
    """Orienta para análisis; conserva hash y metadatos del archivo original.

    RGB no implica sRGB calibrado: no interpreta ni modifica perfiles ICC.
    Los originales se conservan por separado en el cargador/exportación.
    """
    info = inspect_image(data, policy)
    try:
        with Image.open(BytesIO(data)) as original:
            orientation = original.getexif().get(274, 1)
            has_icc = bool(original.info.get("icc_profile"))
            image = ImageOps.exif_transpose(original).convert("RGB")
    except (OSError, SyntaxError, ValueError):
        raise ValueError("No se pudo preparar la fotografía.") from None
    return image, {**info, "sha256": sha256(data).hexdigest(),
                   "orientacion_exif": orientation, "perfil_icc_presente": has_icc,
                   "ancho_analisis_px": image.width, "alto_analisis_px": image.height}

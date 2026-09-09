"""Rectángulos en la imagen orientada: origen superior izquierdo, fin exclusivo."""
import math

import numpy as np
from PIL import Image, ImageDraw

ROI_VERSION = "rectangles-v1"


def rectangle_from_percent(size, horizontal, vertical):
    width, height = size
    for interval in (horizontal, vertical):
        if len(interval) != 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in interval):
            raise ValueError("Los límites de la región deben ser números finitos.")
        if not 0 <= interval[0] < interval[1] <= 100:
            raise ValueError("Cada intervalo debe tener un inicio menor que su fin, entre 0 y 100 %.")
    if width < 1 or height < 1:
        raise ValueError("La imagen debe tener dimensiones positivas.")
    return [math.floor(width * horizontal[0] / 100), math.floor(height * vertical[0] / 100),
            math.ceil(width * horizontal[1] / 100), math.ceil(height * vertical[1] / 100)]


def validate_rectangle(box, size):
    if len(box) != 4 or not all(isinstance(v, int) and not isinstance(v, bool) for v in box):
        raise ValueError("La región requiere cuatro coordenadas enteras.")
    left, top, right, bottom = box
    if not (0 <= left < right <= size[0] and 0 <= top < bottom <= size[1]):
        raise ValueError("La región está vacía o fuera de la imagen.")


def extract_roi(image, box, exclusions=()):
    """Máscara exacta; las exclusiones se intersectan con la ROI, sin duplicarlas."""
    validate_rectangle(box, image.size)
    for exclusion in exclusions:
        validate_rectangle(exclusion, image.size)
    left, top, right, bottom = box
    mask = np.ones((bottom-top, right-left), dtype=bool)
    for x0, y0, x1, y1 in exclusions:
        x0, x1 = max(left, x0), min(right, x1)
        y0, y1 = max(top, y0), min(bottom, y1)
        if x1 > x0 and y1 > y0:
            mask[y0-top:y1-top, x0-left:x1-left] = False
    return image.crop(tuple(box)), mask


def selection_preview(image, box, exclusions=()):
    """Vista reducida; las coordenadas de análisis nunca dependen de la pantalla."""
    validate_rectangle(box, image.size)
    preview = image.copy()
    preview.thumbnail((900, 650))
    draw = ImageDraw.Draw(preview)
    sx, sy = preview.width/image.width, preview.height/image.height
    for rect, color in [(box, "#00ff70")] + [(e, "#ff4050") for e in exclusions]:
        validate_rectangle(rect, image.size)
        scaled = (round(rect[0]*sx), round(rect[1]*sy),
                  max(round(rect[0]*sx), round(rect[2]*sx)-1),
                  max(round(rect[1]*sy), round(rect[3]*sy)-1))
        draw.rectangle(scaled, outline=color, width=3)
    return preview


def masked_preview(crop, mask):
    preview = crop.copy()
    preview.thumbnail((600, 450))
    visible = Image.fromarray(mask).resize(preview.size, Image.Resampling.NEAREST)
    return Image.composite(preview, Image.new("RGB", preview.size, "#dddddd"), visible.convert("L"))

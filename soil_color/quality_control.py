"""Indicadores técnicos exploratorios; umbrales iniciales NO validados en suelos.

No identifica raíces/piedras, no calibra, no certifica nitidez ni estima Munsell.
Las métricas cromáticas se calculan sobre RGB codificado, no sobre luminancia CIE.
"""
from dataclasses import asdict, dataclass

import numpy as np
from PIL import Image

QUALITY_VERSION = "roi-qc-v1"


@dataclass(frozen=True)
class QualityThresholds:
    min_pixels: int = 1024
    min_side: int = 16
    dark_channel: int = 10
    bright_channel: int = 245
    max_dark_fraction: float = 0.20
    max_clipped_fraction: float = 0.20
    min_laplacian_variance: float = 15.0
    max_rgb_std: float = 40.0
    max_sample_side: int = 512


def assess_quality(crop, mask, thresholds=None):
    limits = thresholds or QualityThresholds()
    if crop.mode != "RGB" or mask.dtype != bool or mask.shape != (crop.height, crop.width):
        raise ValueError("La imagen RGB y la máscara deben tener las mismas dimensiones.")
    useful = int(np.count_nonzero(mask))
    issues = []
    if useful < limits.min_pixels or min(crop.size) < limits.min_side:
        issues.append({"code": "small_roi", "severity": "reject", "message": "La región útil es demasiado pequeña para esta evaluación."})
    # Métricas acotadas: nunca se convierte la imagen completa a float64.
    sample = crop.copy()
    sample.thumbnail((limits.max_sample_side, limits.max_sample_side), Image.Resampling.NEAREST)
    sampled_mask = np.asarray(Image.fromarray(mask).resize(sample.size, Image.Resampling.NEAREST), dtype=bool)
    values = np.asarray(sample)
    pixels = values[sampled_mask]
    metrics = {"roi_pixels": int(mask.size), "usable_pixels": useful,
               "excluded_fraction": float(1-useful/mask.size),
               "sample_width": sample.width, "sample_height": sample.height,
               "sample_pixels": int(len(pixels))}
    if len(pixels) == 0:
        issues.append({"code": "empty_sample", "severity": "reject", "message": "No quedan píxeles útiles en la muestra de evaluación."})
    else:
        clipped = float(np.mean(np.any(pixels >= limits.bright_channel, axis=1)))
        bright = float(np.mean(np.all(pixels >= limits.bright_channel, axis=1)))
        dark = float(np.mean(np.all(pixels <= limits.dark_channel, axis=1)))
        std = np.std(pixels.astype(np.float32), axis=0)
        metrics.update({"dark_fraction": dark, "clipped_channel_fraction": clipped,
                        "bright_neutral_fraction": bright,
                        "rgb_median": [float(v) for v in np.median(pixels, axis=0)],
                        "rgb_std": [float(v) for v in std]})
        if dark > limits.max_dark_fraction:
            issues.append({"code": "dark", "severity": "warning", "message": "Muchos píxeles oscuros: revisa sombras o subexposición; también podría ser el color real del suelo."})
        if clipped > limits.max_clipped_fraction:
            issues.append({"code": "clipping", "severity": "warning", "message": "Muchos canales próximos al máximo: revisa sobreexposición o reflejos."})
        if float(np.max(std)) > limits.max_rgb_std:
            issues.append({"code": "variable_color", "severity": "warning", "message": "La región presenta alta variación RGB; revisa mezcla de materiales, iluminación y rasgos redox."})
        # Contraste local, solo donde el centro y sus cuatro vecinos son útiles.
        gray = values.astype(np.float32).mean(axis=2)
        interior = (sampled_mask[1:-1, 1:-1] & sampled_mask[:-2, 1:-1]
                    & sampled_mask[2:, 1:-1] & sampled_mask[1:-1, :-2]
                    & sampled_mask[1:-1, 2:])
        laplacian = (gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2]
                     + gray[1:-1, 2:] - 4*gray[1:-1, 1:-1])
        if np.any(interior):
            score = float(np.var(laplacian[interior]))
            metrics["laplacian_variance"] = score
            if score < limits.min_laplacian_variance:
                issues.append({"code": "low_detail", "severity": "warning", "message": "Poco detalle local: comprueba el enfoque. Una superficie uniforme puede producir el mismo indicador."})
        else:
            metrics["laplacian_variance"] = None
            issues.append({"code": "no_detail_sample", "severity": "warning", "message": "No hay suficientes píxeles vecinos útiles para evaluar el detalle."})
    status = "rejected" if any(i["severity"] == "reject" for i in issues) else ("review" if issues else "no_flags")
    return {"status": status, "algorithm_version": QUALITY_VERSION,
            "thresholds": asdict(limits), "metrics": metrics, "issues": issues,
            "calibrated": False, "scientifically_validated": False,
            "sampling": "nearest-neighbor, max 512 px por lado con parámetros por defecto"}

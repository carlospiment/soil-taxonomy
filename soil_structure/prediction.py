"""Resumen conservador: la respuesta original siempre se conserva aparte.

Admite listas de detecciones con class/class_name y confidence. Otros esquemas
se muestran sin interpretación hasta verificar el contrato del workflow real.
"""
from copy import deepcopy
import math


def summarize_predictions(outputs):
    predictions, unknown = [], False
    recognized = 0

    def visit(node, path):
        nonlocal recognized, unknown
        if isinstance(node, dict):
            for key, value in node.items():
                child_path = f"{path}.{key}"
                if key == "predictions" and isinstance(value, list):
                    recognized += 1
                    for item in value:
                        label = item.get("class", item.get("class_name")) if isinstance(item, dict) else None
                        score = item.get("confidence") if isinstance(item, dict) else None
                        if (not isinstance(label, str) or not label.strip()
                                or isinstance(score, bool) or not isinstance(score, (float, int))
                                or not math.isfinite(score) or not 0 <= score <= 1):
                            unknown = True
                            continue
                        predictions.append({"class": label, "confidence": score,
                                            "source": child_path, "original": deepcopy(item)})
                elif isinstance(value, (dict, list)):
                    before = recognized
                    visit(value, child_path)
                    if key == "predictions" and recognized == before:
                        unknown = True
                elif key == "predictions":
                    unknown = True
        elif isinstance(node, list):
            for i, value in enumerate(node):
                visit(value, f"{path}[{i}]")

    visit(outputs, "outputs")
    status = "predictions" if predictions else ("no_detections" if recognized and not unknown else "unrecognized")
    if outputs == []:
        status = "empty"
    return {"status": status, "predictions": predictions,
            "partial": bool(unknown), "adapter_version": "1"}

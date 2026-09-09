"""Transporte Workflows equivalente al SDK 1.5.2, con timeout por solicitud.

No cambia el SDK ni sesiones globales. No reintenta POST automáticamente: un
timeout no demuestra que el servidor no haya ejecutado/contabilizado el workflow.
"""
import base64
from dataclasses import asdict, dataclass
from io import BytesIO
import math
import re

import requests
from PIL import Image


class WorkflowError(Exception):
    """Solo contiene mensajes públicos; nunca el cuerpo o excepción del proveedor."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class WorkflowConfig:
    workspace: str = "carlos-pimentel"
    workflow_id: str = "usda-soil-structure"
    workflow_version_id: str | None = None
    confidence: float = 0.4
    connect_timeout: float = 10
    read_timeout: float = 60

    def __post_init__(self):
        for value in (self.workspace, self.workflow_id):
            if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
                raise ValueError("Identificador de workflow no válido.")
        if self.workflow_version_id is not None and not re.fullmatch(r"[A-Za-z0-9_-]+", self.workflow_version_id):
            raise ValueError("Versión de workflow no válida.")
        if not math.isfinite(self.confidence) or not 0 <= self.confidence <= 1:
            raise ValueError("La confianza debe estar entre 0 y 1.")
        if not all(math.isfinite(v) and v > 0 for v in (self.connect_timeout, self.read_timeout)):
            raise ValueError("Los tiempos límite deben ser positivos y finitos.")

    def metadata(self):
        return {**asdict(self), "api_url": "https://serverless.roboflow.com",
                "transport": "http-workflows-v1", "preprocessing": "exif-rgb-jpeg-v1"}


def run_workflow(image, api_key, config=None):
    config = config or WorkflowConfig()
    if not isinstance(api_key, str) or not api_key.strip() or any(c in api_key for c in "\r\n"):
        raise WorkflowError("authentication", "Configura una clave API válida de Roboflow.")
    if not isinstance(image, Image.Image) or image.mode != "RGB":
        raise ValueError("El cliente requiere una imagen Pillow RGB validada.")
    # Misma codificación JPEG por defecto que pillow_image_to_base64_jpeg del SDK.
    with BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    payload = {"use_cache": True, "enable_profiling": False,
               "inputs": {"image": {"type": "base64", "value": encoded},
                          "confidence": config.confidence}}
    if config.workflow_version_id is not None:
        payload["workflow_version_id"] = config.workflow_version_id
    url = f"https://serverless.roboflow.com/{config.workspace}/workflows/{config.workflow_id}"
    try:
        # Sin redirecciones: las credenciales solo se envían al endpoint elegido.
        with requests.post(url, json=payload,
                           headers={"Authorization": f"Bearer {api_key.strip()}",
                                    "Content-Type": "application/json"},
                           timeout=(config.connect_timeout, config.read_timeout),
                           allow_redirects=False) as response:
            if response.status_code in (401, 403):
                raise WorkflowError("authentication", "Roboflow rechazó la clave o el acceso al workflow.")
            if response.status_code == 429:
                raise WorkflowError("rate_limit", "Roboflow alcanzó el límite de solicitudes o cuota. Inténtalo más tarde.")
            if response.status_code == 404:
                raise WorkflowError("not_found", "No se encontró el workflow o la versión configurada.")
            if response.status_code >= 500:
                raise WorkflowError("server", "Roboflow no está disponible temporalmente. Inténtalo más tarde.")
            if not 200 <= response.status_code < 300:
                raise WorkflowError("request", "Roboflow no aceptó la solicitud. Revisa image, confidence y la configuración del workflow.")
            try:
                result = response.json()
            except ValueError:
                raise WorkflowError("response", "Roboflow devolvió una respuesta que no es JSON válido.") from None
    except requests.Timeout:
        raise WorkflowError("timeout", "Se agotó la espera de conexión o lectura de Roboflow. El servidor podría haber procesado la imagen; no se reintentó automáticamente.") from None
    except requests.RequestException:
        raise WorkflowError("connection", "No se pudo conectar con Roboflow. Revisa la conexión e inténtalo nuevamente.") from None
    if not isinstance(result, dict) or not isinstance(result.get("outputs"), list):
        raise WorkflowError("response", "La respuesta de Roboflow no contiene una lista outputs válida.")
    return result

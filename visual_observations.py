"""Contrato de observaciones visuales, sin Streamlit ni decisiones taxonómicas.

Las operaciones devuelven copias JSON independientes. Una revisión agrega un
evento; nunca sustituye la predicción original ni aplica datos al horizonte.
"""
import json
import re
from datetime import datetime, timezone
from uuid import UUID, uuid4

SCHEMA_VERSION = 1
HORIZON_ID = "_horizon_uid"


def new_id():
    return str(uuid4())


def _uuid(value):
    if not isinstance(value, str):
        raise ValueError("El identificador debe ser un UUID.")
    try:
        UUID(value)
    except ValueError as exc:
        raise ValueError("El identificador debe ser un UUID.") from exc
    return value


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Falta {field}.")
    return value.strip()


def _timestamp(value=None):
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    try:
        parsed = datetime.fromisoformat(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("La fecha debe ser ISO 8601 con zona horaria.") from exc
    if parsed.tzinfo is None:
        raise ValueError("La fecha debe incluir zona horaria.")
    return parsed.astimezone(timezone.utc).isoformat()


def _copy(value):
    """Rechaza NaN, infinito, imágenes y objetos no serializables."""
    try:
        return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError("La observación debe contener datos JSON finitos.") from exc


def ensure_horizon_ids(rows):
    """Asigna identidad a filas nuevas; conserva identidad al editar o reordenar."""
    result, seen = [], set()
    for row in rows:
        item = dict(row)
        uid = _uuid(item[HORIZON_ID]) if HORIZON_ID in item else new_id()
        if uid in seen:
            raise ValueError("Hay identificadores de horizonte duplicados.")
        seen.add(uid)
        item[HORIZON_ID] = uid
        result.append(item)
    return result


def create_observation(*, profile_uid, horizon_uid, image_sha256, kind,
                       moisture_state, predicted_value, method, algorithm_version,
                       context=None, quality=None, raw_result=None, created_at=None):
    """Crea una propuesta; context conserva ROI, captura, calibración y modelo.

    predicted_value contiene los resultados/intermedios disponibles, sin imponer
    una conversión Munsell. Campos no medidos deben permanecer ausentes o null.
    """
    if kind not in ("color", "structure"):
        raise ValueError("Tipo de observación no reconocido.")
    allowed = ("dry", "moist") if kind == "color" else ("dry", "moist", "unknown")
    if moisture_state not in allowed:
        raise ValueError("Indica la condición seca/húmeda de la muestra.")
    if not isinstance(image_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", image_sha256):
        raise ValueError("La imagen requiere su SHA-256 en hexadecimal minúsculo.")
    if not isinstance(predicted_value, dict) or not predicted_value:
        raise ValueError("La propuesta debe ser un objeto no vacío.")
    if context is not None and not isinstance(context, dict):
        raise ValueError("El contexto debe ser un objeto.")
    if quality is not None and not isinstance(quality, dict):
        raise ValueError("La calidad debe ser un objeto.")
    return _copy({
        "schema_version": SCHEMA_VERSION,
        "observation_id": new_id(),
        "profile_uid": _uuid(profile_uid),
        "horizon_uid": _uuid(horizon_uid),
        "image_sha256": image_sha256,
        "kind": kind,
        "moisture_state": moisture_state,
        "created_at": _timestamp(created_at),
        "method": _text(method, "método"),
        "algorithm_version": _text(algorithm_version, "versión del algoritmo"),
        "context": context or {},
        "quality": quality,
        "raw_result": raw_result,
        "predicted_value": predicted_value,
        "validated_value": None,
        "status": "pending",
        "reviews": [],
    })


def review_observation(observation, *, action, reviewer, reason,
                       corrected_value=None, reviewed_at=None):
    """Acepta, corrige o rechaza mediante un nuevo evento, sin borrar revisiones."""
    result = _copy(observation)
    if action not in ("accepted", "corrected", "rejected"):
        raise ValueError("Acción de revisión no reconocida.")
    if action == "corrected":
        if not isinstance(corrected_value, dict) or not corrected_value:
            raise ValueError("La corrección debe ser un objeto no vacío.")
        validated = _copy(corrected_value)
    else:
        if corrected_value is not None:
            raise ValueError("Solo una corrección admite un valor corregido.")
        validated = _copy(result["predicted_value"]) if action == "accepted" else None
    timestamp = _timestamp(reviewed_at)
    previous_time = result["reviews"][-1]["reviewed_at"] if result["reviews"] else result["created_at"]
    if datetime.fromisoformat(timestamp) < datetime.fromisoformat(previous_time):
        raise ValueError("La revisión no puede ser anterior al registro previo.")
    result["reviews"].append({
        "review_id": new_id(), "action": action,
        "reviewer": _text(reviewer, "responsable de revisión"),
        "reason": _text(reason, "motivo de revisión"),
        "reviewed_at": timestamp, "validated_value": validated,
    })
    result["status"] = action
    result["validated_value"] = _copy(validated)
    return result


def extend_report(report, *, profile_uid, horizon_refs, observations):
    """Extensión aditiva del JSON/ZIP anterior, sin modificar sus campos.

    Se conservan observaciones de horizontes borrados, señaladas como huérfanas.
    La presencia de una imagen solo significa que está incluida en las fotos del
    reporte; el hash permite identificarla aunque ya no esté adjunta.
    """
    profile_uid = _uuid(profile_uid)
    result = _copy(report)
    if "trazabilidad_visual" in result:
        raise ValueError("El reporte ya contiene trazabilidad visual.")
    refs = _copy(horizon_refs)
    ids = [_uuid(ref["horizon_uid"]) for ref in refs]
    if len(ids) != len(set(ids)) or len(refs) != len(report["horizontes"]):
        raise ValueError("Las referencias deben corresponder a los horizontes exportados.")
    ledger = _copy(observations)
    seen = set()
    for observation in ledger:
        if observation["schema_version"] != SCHEMA_VERSION:
            raise ValueError("Versión de observación no compatible.")
        if observation["profile_uid"] != profile_uid:
            raise ValueError("La observación pertenece a otro perfil.")
        uid = _uuid(observation["observation_id"])
        if uid in seen:
            raise ValueError("Hay observaciones duplicadas.")
        seen.add(uid)
    image_ids = {photo.get("sha256") for photo in result.get("fotos", [])}
    result["trazabilidad_visual"] = {
        "schema_version": SCHEMA_VERSION,
        "profile_uid": profile_uid,
        "horizons": refs,
        "observations": ledger,
        "orphaned_observation_ids": [o["observation_id"] for o in ledger if o["horizon_uid"] not in ids],
        "unattached_image_sha256": sorted({o["image_sha256"] for o in ledger if o["image_sha256"] not in image_ids}),
    }
    return result

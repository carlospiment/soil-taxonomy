"""Portable study archives. JSON only; never extract files or restore arbitrary state."""
import hashlib
import io
import json
import math
import zipfile
from copy import deepcopy
from datetime import date
from pathlib import PurePosixPath

from field_media import validate_photo
from visual_observations import HORIZON_ID, extend_report, ensure_horizon_ids, new_id, _uuid, _timestamp, review_observation
from texture import AUTO
from soil_profile import HORIZON_COLUMNS, TEXT_COLUMNS, DIAGNOSTICS, STATES
from subgroup_guide import KEYS
from laboratory import validate_rows

VERSION = 1
MAX_ARCHIVE = 100 * 1024 * 1024
MAX_JSON = 8 * 1024 * 1024
FIELDS = dict(zip(
    'profile_id profile_observer profile_date profile_depth profile_reference profile_contact profile_contact_depth profile_moisture profile_temperature profile_mean_temp profile_seasonal_temp profile_climate_evidence profile_saturation profile_water_depth profile_water_days profile_reduction profile_redox_notes profile_cracks_width profile_cracks_depth profile_cracks_days profile_other'.split(),
    'identificador responsable fecha_descripcion profundidad_cm origen_profundidades contacto profundidad_contacto_cm regimen_humedad regimen_temperatura temperatura_media_suelo_c diferencia_estacional_c evidencia_regimenes saturacion profundidad_saturacion_cm duracion_saturacion_dias reduccion evidencia_redox grietas_ancho_mm grietas_profundidad_cm grietas_duracion_dias otros_rasgos'.split()))
TABLES = {'profile_diagnostics': 'diagnosticos', 'profile_extra': 'medidas_adicionales', 'profile_route': 'ruta'}


def _number(value, low=None, high=None, integer=False):
    if value is None:
        return
    if type(value) not in (int, float) or not math.isfinite(value) or (low is not None and value < low) or (high is not None and value > high) or (integer and int(value) != value):
        raise ValueError('Medición fuera de formato o rango.')


def _string(value):
    if not isinstance(value, str):
        raise ValueError('Se esperaba texto.')


def _validate_controls(report):
    description = report.get('descripcion_asistida', {})
    if not isinstance(description, dict) or set(description) - {'sitio', 'horizontes'}:
        raise ValueError('Descripción asistida incompatible.')
    for section in ('sitio', 'horizontes'):
        if not isinstance(description.get(section, {}), dict):
            raise ValueError('Descripción asistida incompatible.')
    for row in [description.get('sitio', {})] + list(description.get('horizontes', {}).values()):
        if not isinstance(row, dict) or any(not isinstance(k, str) or (v is not None and type(v) not in (str, int, float)) for k, v in row.items()):
            raise ValueError('Campo de descripción asistida incompatible.')
        for value in row.values():
            if type(value) in (int, float):
                _number(value)
    review = report.get('revision_ruta_manual', {})
    if not isinstance(review, dict):
        raise ValueError('Revisión de la ruta incompatible.')
    for flag in ('requires_review', 'had_proposal'):
        if flag in review and type(review[flag]) is not bool:
            raise ValueError('Estado de revisión incompatible.')
    if 'evidence_fingerprint' in review:
        _string(review['evidence_fingerprint'])
    numeric = {'profundidad_cm', 'profundidad_contacto_cm', 'temperatura_media_suelo_c', 'diferencia_estacional_c', 'profundidad_saturacion_cm', 'duracion_saturacion_dias', 'grietas_ancho_mm', 'grietas_profundidad_cm', 'grietas_duracion_dias'}
    for field in FIELDS.values():
        if field not in report:
            raise ValueError('Ficha incompleta: ' + field)
        if field in numeric:
            days = field in ('duracion_saturacion_dias', 'grietas_duracion_dias')
            _number(report[field], None if field == 'temperatura_media_suelo_c' else 0, 366 if days else None, days)
        elif field != 'fecha_descripcion':
            _string(report[field])
    enums = {
        'origen_profundidades': ['Superficie del suelo', 'Superficie del suelo mineral'],
        'contacto': ['No evaluado', 'No observado hasta la profundidad explorada', 'Lítico', 'Paralítico', 'Dénsico'],
        'regimen_humedad': ['No evaluado', 'Árídico / tórrico', 'Údico', 'Perúdico', 'Ústico', 'Xérico', 'Ácuico', 'Perácuico'],
        'regimen_temperatura': ['No evaluado', 'Gélico', 'Cryic', 'Frígido', 'Mésico', 'Térmico', 'Hipertérmico', 'Isofrígido', 'Isomésico', 'Isotérmico', 'Isohipertérmico'],
        'saturacion': ['No evaluado', 'Endosaturación', 'Episaturación', 'Saturación antrópica', 'No observada en el período evaluado'], 'reduccion': STATES,
    }
    for field, allowed in enums.items():
        if report[field] not in allowed:
            raise ValueError('Opción incompatible: ' + field)
    for row in report['horizontes']:
        for key, value in row.items():
            if key not in HORIZON_COLUMNS:
                raise ValueError('Columna de horizonte incompatible.')
            if key in TEXT_COLUMNS:
                if value is not None:
                    _string(value)
            else:
                _number(value, 0, 100 if '(%)' in key else 14 if key.startswith('pH') else None)
    if [r.get('Diagnóstico') for r in report['diagnosticos']] != DIAGNOSTICS:
        raise ValueError('Catálogo de diagnósticos incompatible.')
    for row in report['diagnosticos']:
        if row['Estado'] not in STATES:
            raise ValueError('Estado diagnóstico incompatible.')
        _number(row['Techo (cm)'], 0)
        _number(row['Base (cm)'], 0)
        _string(row['Evidencia / método / criterio'])
    for row in report['medidas_adicionales']:
        for field in ('Parámetro', 'Unidad', 'Intervalo / método / evidencia'):
            _string(row[field])
        _number(row['Valor'], 0)
    if [r.get('Nivel') for r in report['ruta']] != ['Orden', 'Suborden', 'Gran grupo', 'Subgrupo']:
        raise ValueError('Ruta incompatible.')
    for row in report['ruta']:
        for field in ('Taxón', 'Clave / página', 'Evidencia y exclusión de anteriores'):
            _string(row[field])
        if row['Revisión'] not in ['Pendiente', 'No cumple', 'Cumple; anteriores descartados']:
            raise ValueError('Revisión de ruta incompatible.')
    location = report['ubicacion']
    if location:
        if location['sistema'] not in ('Geográficas (grados decimales)', 'UTM (metros)'):
            raise ValueError('Sistema de coordenadas incompatible.')
        _string(location['datum'])
        for field, bounds in {'latitud': (-90, 90), 'longitud': (-180, 180), 'zona': (1, 60), 'este_m': (0, None), 'norte_m': (0, None), 'precision_m': (0, None)}.items():
            _number(location.get(field), *bounds, integer=field == 'zona')
        if location.get('hemisferio') not in (None, 'Norte', 'Sur'):
            raise ValueError('Hemisferio incompatible.')
    guide = report.get('clave_guiada') or {}
    if guide:
        if 'requires_review' in guide and type(guide['requires_review']) is not bool:
            raise ValueError('Estado de revisión de clave incompatible.')
        if 'evidence_fingerprint' in guide:
            _string(guide['evidence_fingerprint'])
        if guide['group'] not in KEYS:
            raise ValueError('Clave guiada incompatible.')
        codes = {e['code'] for e in KEYS[guide['group']]['entries']}
        for code, decision in guide.get('decisions', {}).items():
            if code not in codes or decision['outcome'] not in ('No evaluado', 'No cumple', 'Cumple'):
                raise ValueError('Decisión incompatible.')
            _string(decision['evidence'])


def _json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Claves JSON duplicadas.')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Número JSON no finito.')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def _dump(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True).encode('utf-8')


def _safe(name):
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name and str(path) == name


def restore_state(report):
    """Map known report fields to editable controls; no executable serialization."""
    state = {key: report[field] for key, field in FIELDS.items() if field in report}
    if state.get('profile_date'):
        state['profile_date'] = date.fromisoformat(state['profile_date'])
    trace = report['trazabilidad_visual']
    state['profile_uid'] = trace['profile_uid']
    state['visual_observations'] = deepcopy(trace['observations'])
    rows = deepcopy(report['horizontes'])
    for row, ref in zip(rows, trace['horizons']):
        row[HORIZON_ID] = ref['horizon_uid']
    for item in report.get('fracciones_calculadas', []):
        if 1 <= item['fila'] <= len(rows):
            rows[item['fila'] - 1][AUTO] = item['fraccion']
    state['horizon_rows'] = ensure_horizon_ids(rows or [{}])
    state['horizon_revision'] = 0
    state['study_tables'] = {key: deepcopy(report[field]) for key, field in TABLES.items()}
    state['study_tables']['profile_laboratory'] = deepcopy(report.get('laboratorio', []))
    state['study_laboratory_legacy'] = deepcopy(report.get('laboratorio_historico_no_taxonomico', []))
    state['profile_manual_review'] = deepcopy(report.get('revision_ruta_manual', {}))
    description = report.get('descripcion_asistida', {})
    state['profile_site_description'] = deepcopy(description.get('sitio', {}))
    state['profile_horizon_descriptions'] = deepcopy(description.get('horizontes', {}))
    location = report.get('ubicacion', {})
    state['location_mode'] = location.get('sistema', 'Sin registrar')
    datum = location.get('datum', 'WGS 84')
    state['location_datum'] = 'WGS 84' if datum == 'WGS 84' else 'Otro (solo registro)'
    state['location_other_datum'] = '' if datum == 'WGS 84' else datum
    for key, field in {'lat': 'latitud', 'lon': 'longitud', 'zone': 'zona', 'hemisphere': 'hemisferio', 'east': 'este_m', 'north': 'norte_m', 'precision': 'precision_m'}.items():
        if field in location:
            state['location_' + key] = location[field]
    guide = report.get('clave_guiada') or {}
    if guide.get('group'):
        state['guide_group'] = guide['group']
        state['study_guide'] = deepcopy(guide)
    return state


def validate_report(report):
    if not isinstance(report, dict):
        raise ValueError('La ficha debe ser un objeto.')
    # A portable draft preserves invalid measurements as text, while enforcing
    # the schema. The profile evaluator reports and blocks their scientific use.
    validate_rows(report.get('laboratorio', []), check_results=False)
    validate_rows(report.get('laboratorio_historico_no_taxonomico', []), check_results=False)
    for field in ('horizontes', 'diagnosticos', 'medidas_adicionales', 'ruta', 'fotos'):
        if not isinstance(report.get(field), list) or len(report[field]) > 1000 or not all(isinstance(r, dict) for r in report[field]):
            raise ValueError('Tabla ausente o incompatible: ' + field)
    trace = report.get('trazabilidad_visual')
    _validate_controls(report)
    if not isinstance(trace, dict) or trace.get('schema_version') != 1:
        raise ValueError('Versión de trazabilidad incompatible.')
    base = {k: v for k, v in report.items() if k != 'trazabilidad_visual'}
    checked = extend_report(base, profile_uid=trace['profile_uid'], horizon_refs=trace['horizons'], observations=trace['observations'])
    for obs in trace['observations']:
        from visual_observations import create_observation
        rebuilt = create_observation(**{k: obs[k] for k in ('profile_uid', 'horizon_uid', 'image_sha256', 'kind', 'moisture_state', 'predicted_value', 'method', 'algorithm_version', 'context', 'quality', 'raw_result', 'created_at')})
        if not isinstance(obs['context'].get('horizon_snapshot', {}), dict):
            raise ValueError('Contexto de horizonte incompatible.')
        if obs['kind'] == 'color' and obs['predicted_value'].get('munsell') is not None:
            _string(obs['predicted_value']['munsell'])
        if obs['status'] not in ('pending', 'accepted', 'corrected', 'rejected') or not isinstance(obs['reviews'], list):
            raise ValueError('Revisión incompatible.')
        if obs['status'] in ('accepted', 'corrected') and not isinstance(obs['validated_value'], dict):
            raise ValueError('Falta el valor revisado.')
        review_ids = set()
        for review in obs['reviews']:
            uid = _uuid(review['review_id'])
            if uid in review_ids:
                raise ValueError('Revisión duplicada.')
            review_ids.add(uid)
            rebuilt = review_observation(rebuilt, action=review['action'], reviewer=review['reviewer'], reason=review['reason'], reviewed_at=review['reviewed_at'], corrected_value=review['validated_value'] if review['action'] == 'corrected' else None)
            if rebuilt['validated_value'] != review['validated_value']:
                raise ValueError('Valor de revisión inconsistente.')
        if rebuilt['status'] != obs['status'] or rebuilt['validated_value'] != obs['validated_value']:
            raise ValueError('Historial de revisión inconsistente.')
        applications = obs.get('applications', [])
        if not isinstance(applications, list) or len(applications) > 1:
            raise ValueError('Historial de aplicación incompatible.')
        for event in applications:
            from soil_color.validation import normalize_munsell
            _uuid(event['application_id'])
            if not obs['reviews'] or event['review_id'] != obs['reviews'][-1]['review_id'] or obs['status'] not in ('accepted', 'corrected'):
                raise ValueError('Aplicación sin revisión válida.')
            field = {'dry': 'Color seco (Munsell)', 'moist': 'Color húmedo (Munsell)'}.get(obs['moisture_state'])
            if obs['kind'] != 'color' or event['field'] != field or event['applied_value'] != normalize_munsell(obs['validated_value']['munsell']):
                raise ValueError('Aplicación de color inconsistente.')
            if _timestamp(event['applied_at']) < _timestamp(obs['reviews'][-1]['reviewed_at']):
                raise ValueError('Fecha de aplicación inconsistente.')
            _string(event['reviewer'])
            if not event['reviewer'].strip():
                raise ValueError('Falta responsable de aplicación.')
            if event['previous_value'] is not None:
                _string(event['previous_value'])
    restore_state(checked)
    for i, ref in enumerate(trace['horizons']):
        if ref['row_number'] != i + 1:
            raise ValueError('Orden de horizontes incompatible.')
    for item in report.get('fracciones_calculadas', []):
        if type(item['fila']) is not int or not 1 <= item['fila'] <= len(report['horizontes']) or item['fraccion'] not in ('Arena (%)', 'Limo (%)', 'Arcilla (%)'):
            raise ValueError('Fracción calculada incompatible.')
    paths = set()
    for photo in report['fotos']:
        for key in ('nombre_original', 'descripcion', 'sha256', 'ruta_zip'):
            _string(photo[key])
        if not _safe(photo['ruta_zip']) or not photo['ruta_zip'].startswith('fotos/') or photo['ruta_zip'] in paths:
            raise ValueError('Ruta de fotografía incompatible.')
        paths.add(photo['ruta_zip'])
    if len(paths) > 10:
        raise ValueError('Más de 10 fotografías de perfil.')
    return checked


def build_study(report, photos, images=None, structures=None):
    report = validate_report(deepcopy(report))
    if not isinstance(structures or [], list):
        raise ValueError('Historial de estructura incompatible.')
    for result in structures or []:
        if not isinstance(result, dict) or result.get('schema_version') != 1 or not isinstance(result.get('image'), dict) or not isinstance(result.get('summary'), dict) or 'raw_response' not in result:
            raise ValueError('Versión o resultado estructural incompatible.')
    blobs = dict(images or {})
    for photo in photos:
        blobs[photo['sha256']] = photo['data']
    for sha, data in blobs.items():
        if hashlib.sha256(data).hexdigest() != sha:
            raise ValueError('La imagen no corresponde a su hash.')
        validate_photo(data)
    required = {p['sha256'] for p in report['fotos']} | {o['image_sha256'] for o in report['trazabilidad_visual']['observations']}
    required |= {r['image']['sha256'] for r in structures or []}
    if required - blobs.keys():
        raise ValueError('Faltan imágenes originales del estudio. Adjunta las fotografías antes de guardar un estudio completo.')
    if sum(len(blobs[p['sha256']]) for p in report['fotos']) > 60 * 1024 * 1024:
        raise ValueError('Las fotos del perfil superan 60 MB.')
    files = {'estudio.json': _dump({'schema_version': VERSION, 'report': report, 'structures': structures or []})}
    files.update({'imagenes/' + sha: data for sha, data in blobs.items()})
    if len(files) > 201 or len(files['estudio.json']) > MAX_JSON or sum(map(len, files.values())) > MAX_ARCHIVE:
        raise ValueError('El estudio supera los límites de almacenamiento (100 MB, 200 imágenes, JSON 8 MB).')
    files['manifest.json'] = _dump({'schema_version': VERSION, 'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}})
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    if output.tell() > MAX_ARCHIVE:
        raise ValueError('El ZIP supera 100 MB.')
    return output.getvalue()


def load_study(data):
    """Validate entirely in memory before the caller changes the active study."""
    try:
        if len(data) > MAX_ARCHIVE:
            raise ValueError('Archivo mayor de 100 MB.')
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            names = [i.filename for i in entries]
            if len(entries) > 202 or len(names) != len(set(names)) or any(not _safe(n) for n in names):
                raise ValueError('Rutas o entradas ZIP inválidas.')
            if sum(i.file_size for i in entries) > MAX_ARCHIVE or any(i.flag_bits & 1 or (i.external_attr >> 16) & 0o170000 == 0o120000 for i in entries):
                raise ValueError('ZIP cifrado, enlace o tamaño no admitido.')
            if any(i.file_size > MAX_JSON for i in entries if i.filename.endswith('.json')):
                raise ValueError('JSON demasiado grande.')
            files = {name: archive.read(name) for name in names}
        legacy = 'manifest.json' not in files
        if legacy:
            report = _json(files.pop('perfil_taxonomico.json'))
            if 'trazabilidad_visual' not in report:
                report = extend_report(report, profile_uid=new_id(), horizon_refs=[{'horizon_uid': new_id(), 'row_number': i+1, 'label': r.get('Horizonte')} for i, r in enumerate(report['horizontes'])], observations=[])
            structures = []
            blobs = {}
            for photo in report['fotos']:
                blobs[photo['sha256']] = files.pop(photo['ruta_zip'])
            if files:
                raise ValueError('El ZIP antiguo contiene archivos desconocidos.')
        else:
            manifest = _json(files.pop('manifest.json'))
            if manifest['schema_version'] != VERSION or set(manifest['files']) != set(files):
                raise ValueError('Manifiesto incompatible.')
            if any(hashlib.sha256(files[n]).hexdigest() != sha for n, sha in manifest['files'].items()):
                raise ValueError('Archivo dañado: no coincide la integridad SHA-256.')
            payload = _json(files.pop('estudio.json'))
            if payload['schema_version'] != VERSION:
                raise ValueError('Versión de estudio incompatible.')
            report, structures = payload['report'], payload['structures']
            if any(not n.startswith('imagenes/') for n in files):
                raise ValueError('Archivo no reconocido.')
            blobs = {n.removeprefix('imagenes/'): value for n, value in files.items()}
        report = validate_report(report)
        photos = [{**p, 'data': blobs[p['sha256']]} for p in report['fotos']]
        # Same completeness and media checks for old and new archives.
        build_study(report, photos, blobs, structures)
        return {'report': report, 'photos': photos, 'images': blobs, 'structures': structures, 'migrated': legacy}
    except (KeyError, TypeError, AttributeError, IndexError, OSError, UnicodeError, RecursionError, zipfile.BadZipFile, NotImplementedError) as exc:
        raise ValueError('Estudio dañado, incompleto o de esquema incompatible.') from exc

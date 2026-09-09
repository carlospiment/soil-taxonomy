"""Summarize held-out field pairs. No claim of independence can be verified by code."""
import argparse
import json
from pathlib import Path
from soil_color.validation import normalize_munsell


def evaluate_field_study(dataset):
    if dataset.get('schema_version') != 1:
        raise ValueError('Versión de estudio de campo incompatible.')
    for key in ('study_id', 'independent_team', 'protocol', 'sampling', 'algorithm_version', 'structure_model_version', 'independence_statement'):
        if not isinstance(dataset.get(key), str) or not dataset[key].strip():
            raise ValueError('Documenta ' + key)
    records = dataset.get('records')
    if not isinstance(records, list) or not records:
        raise ValueError('No hay pares de campo: desempeño aún no evaluado.')
    seen, groups = set(), {'color_dry': [], 'color_moist': [], 'structure': []}
    for row in records:
        for key in ('sample_id', 'profile_id', 'horizon_id', 'reference_reviewer', 'reference_evidence', 'image_sha256'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('Falta ' + key)
        import re
        if not re.fullmatch('[0-9a-f]{64}', row['image_sha256']):
            raise ValueError('Hash de imagen inválido.')
        kind = row['kind']
        if kind not in ('color', 'structure') or row['moisture'] not in ('dry', 'moist', 'unknown') or (kind == 'color' and row['moisture'] == 'unknown'):
            raise ValueError('Tipo o humedad incompatible.')
        identity = (row['sample_id'], kind, row['moisture'])
        if identity in seen:
            raise ValueError('Par de campo duplicado.')
        seen.add(identity)
        reference, predicted = row['reference'], row['predicted']
        if not isinstance(reference, str) or not reference.strip():
            raise ValueError('Falta referencia independiente.')
        if predicted is not None and (not isinstance(predicted, str) or not predicted.strip()):
            raise ValueError('Predicción inválida; usa null para abstención.')
        if predicted is None and not row.get('abstention_reason'):
            raise ValueError('Documenta la abstención.')
        if kind == 'color':
            reference = normalize_munsell(reference)
            predicted = normalize_munsell(predicted) if predicted is not None else None
        groups['color_' + row['moisture'] if kind == 'color' else 'structure'].append((reference, predicted))
    metrics = {}
    for key, pairs in groups.items():
        emitted = [(r, p) for r, p in pairs if p is not None]
        correct = sum(r == p for r, p in emitted)
        matrix = {}
        for ref, pred in pairs:
            bucket = matrix.setdefault(ref, {})
            label = pred if pred is not None else '(abstención)'
            bucket[label] = bucket.get(label, 0) + 1
        metrics[key] = {'n_reference': len(pairs), 'n_predicted': len(emitted), 'n_abstained': len(pairs) - len(emitted),
                        'coverage': len(emitted) / len(pairs) if pairs else None,
                        'exact_agreement_predicted': correct / len(emitted) if emitted else None,
                        'exact_agreement_all': correct / len(pairs) if pairs else None, 'confusion': matrix}
    return {'schema_version': 1, 'study_id': dataset['study_id'], 'status': 'Descriptive results; independence declared, not certified',
            'metadata': {k: v for k, v in dataset.items() if k != 'records'},
            'n_profiles': len({r['profile_id'] for r in records}), 'metrics': metrics,
            'limitations': ['Exact Munsell agreement is not perceptual color error.', 'Repeated photos or horizons within profiles are not independent samples.', 'No field acceptance threshold or confidence interval is inferred.', 'Structure labels must use the preregistered reference-to-model mapping.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        result = evaluate_field_study(json.loads(args.input.read_text(encoding='utf-8')))
        # Never overwrite field evidence or an existing report.
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, str(error) + '\n')

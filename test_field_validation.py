import unittest
from field_validation import evaluate_field_study


class FieldValidationTests(unittest.TestCase):
    def dataset(self):
        metadata = {key: 'synthetic-test' for key in ('study_id', 'independent_team', 'protocol', 'sampling', 'algorithm_version', 'structure_model_version', 'independence_statement')}
        def row(sample, kind, moisture, reference, prediction):
            return dict(sample_id=sample, profile_id='P1', horizon_id='H1', reference_reviewer='Test', reference_evidence='Synthetic fixture', image_sha256='a'*64, kind=kind, moisture=moisture, reference=reference, predicted=prediction, abstention_reason='quality' if prediction is None else '')
        return dict(schema_version=1, **metadata, records=[row('1', 'color', 'dry', '10YR 4/3', '10yr 4/3'), row('2', 'color', 'dry', '10YR 4/3', None), row('3', 'structure', 'unknown', 'granular', 'blocky')])

    def test_coverage_counts_failures_and_separates_moisture(self):
        result = evaluate_field_study(self.dataset())
        dry = result['metrics']['color_dry']
        self.assertEqual(dry['coverage'], .5)
        self.assertEqual(dry['exact_agreement_predicted'], 1)
        self.assertEqual(dry['exact_agreement_all'], .5)
        self.assertIsNone(result['metrics']['color_moist']['coverage'])
        self.assertEqual(result['metrics']['structure']['confusion'], {'granular': {'blocky': 1}})
        self.assertEqual(result['n_profiles'], 1)

    def test_no_fake_validation_or_duplicate_pairs(self):
        data = self.dataset()
        data['records'].append(data['records'][0])
        with self.assertRaises(ValueError):
            evaluate_field_study(data)
        for field, value in [('records', []), ('independent_team', ''), ('schema_version', 99)]:
            data = self.dataset()
            data[field] = value
            with self.assertRaises(ValueError):
                evaluate_field_study(data)

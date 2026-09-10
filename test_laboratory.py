import unittest
from copy import deepcopy
from laboratory import normalize_result, validate_rows


class LaboratoryTests(unittest.TestCase):
    def row(self, name, value, unit, **extra):
        return {'Parámetro': name, 'Resultado': value, 'Unidad': unit, **extra}

    def test_charge_units_and_original_preserved(self):
        row = self.row('Calcio intercambiable (Ca)', '3,47', 'meq/100 g suelo')
        before = deepcopy(row)
        self.assertEqual(normalize_result(row)['valor'], 3.47)
        self.assertEqual(normalize_result(row)['unidad'], 'cmolc/kg suelo')
        self.assertEqual(row, before)

    def test_qualifier_and_unknown_not_zero(self):
        row = self.row('Fósforo extraíble (P)', '<0,02', 'ppm', **{'Base de reporte': 'Suelo seco (masa)'})
        self.assertEqual(normalize_result(row), {'valor': 0.02, 'calificador': '<', 'unidad': 'mg/kg'})
        row['Base de reporte'] = 'Extracto / solución'
        self.assertIsNone(normalize_result(row)['valor'])
        row['Resultado'] = 'ND'
        self.assertIsNone(normalize_result(row)['valor'])

    def test_conversions_and_invalid_values(self):
        self.assertEqual(normalize_result(self.row('Conductividad eléctrica', '500', 'µS/cm'))['valor'], 0.5)
        self.assertAlmostEqual(normalize_result(self.row('Materia orgánica', '39.6', 'g/kg'))['valor'], 3.96)
        for row in [self.row('pH', '15', 'sin unidad'), self.row('pH', 'nan', 'sin unidad'), self.row('CICE de la arcilla', '8.48', 'meq/100 g suelo'), self.row('Materia orgánica', '-1', '%')]:
            with self.assertRaises(ValueError):
                validate_rows([row])

    def test_capture_and_archive_roundtrip(self):
        from streamlit.testing.v1 import AppTest
        from study_storage import build_study, load_study, restore_state
        row = self.row('CICE del suelo', '8.48', 'No informada', Muestra='M1')
        app = AppTest.from_file('app.py').run(timeout=30)
        self.assertFalse(app.exception)
        app.session_state['study_tables'] = {'profile_laboratory': [row]}
        app.run(timeout=30)
        self.assertFalse(app.exception)
        report = app.session_state['study_report']
        self.assertEqual(report['laboratorio'][0]['Resultado'], '8.48')
        restored = restore_state(load_study(build_study(report, []))['report'])
        self.assertEqual(restored['study_tables']['profile_laboratory'], report['laboratorio'])
        reopened = AppTest.from_file('app.py')
        for key, value in restored.items():
            reopened.session_state[key] = value
        reopened.run(timeout=30)
        self.assertFalse(reopened.exception)
        self.assertEqual(reopened.session_state['study_report']['laboratorio'], report['laboratorio'])
        legacy = deepcopy(report)
        legacy.pop('laboratorio')
        self.assertEqual(restore_state(legacy)['study_tables']['profile_laboratory'], [])


if __name__ == '__main__':
    unittest.main()

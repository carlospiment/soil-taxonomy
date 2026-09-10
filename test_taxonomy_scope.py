"""Regression tests for the approved USDA-only profile workflow."""
import io
import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from PIL import Image
from streamlit.testing.v1 import AppTest
from laboratory import TAXONOMIC_CATALOG, laboratory_issues
from taxonomy_scope import HORIZON_USES, EXTRA_USES, evidence_fingerprint, validate_extra, determination
from soil_profile import HORIZON_COLUMNS
from study_storage import build_study, load_study, restore_state
from field_media import validate_photo


def ready_app():
    app = AppTest.from_file('app.py')
    app.session_state['horizon_rows'] = [{'Horizonte': 'A', 'Techo (cm)': 0., 'Base (cm)': 20.}]
    app.session_state['horizon_revision'] = 0
    app.session_state['profile_depth'] = 20.
    app.session_state['profile_moisture'] = 'Údico'
    app.session_state['profile_temperature'] = 'Isotérmico'
    app.session_state['profile_climate_evidence'] = 'Evidencia sintética; no pedón de referencia.'
    route = [{'Nivel': level, 'Taxón': taxon, 'Clave / página': 'Referencia sintética',
              'Evidencia y exclusión de anteriores': 'Evidencia sintética', 'Revisión': 'Cumple; anteriores descartados'}
             for level, taxon in zip(['Orden', 'Suborden', 'Gran grupo', 'Subgrupo'], ['Ultisols', 'Udults', 'Hapludults', 'Lithic-Ruptic-Entic Hapludults'])]
    app.session_state['study_tables'] = {'profile_route': route}
    return app


class ScopeTests(unittest.TestCase):
    def test_every_horizon_has_a_reference(self):
        self.assertEqual(set(HORIZON_COLUMNS), set(HORIZON_USES))
        self.assertEqual(len(EXTRA_USES), 13)
        for excluded in ('pH tampón', 'Materia orgánica', 'Fósforo extraíble (P)', 'Ca/K', 'Saturación de K'):
            self.assertNotIn(excluded, TAXONOMIC_CATALOG)

    def test_fingerprint_ignores_administration_but_tracks_measurements(self):
        report = {'horizontes': [{'Horizonte': 'A', 'Base (cm)': 20}], 'ruta': [{}, {}, {}, {}]}
        before = evidence_fingerprint(report)
        report.update(responsable='Ana', fotos=[{'descripcion': 'Foto corregida'}], identificador='P1', ubicacion={'latitud': 8})
        report['ruta'][3]['Taxón'] = 'Cambio manual'
        self.assertEqual(before, evidence_fingerprint(report))
        report['horizontes'][0]['Base (cm)'] = 21
        self.assertNotEqual(before, evidence_fingerprint(report))

    def test_units_and_intervals(self):
        rows = [{'Parámetro': 'Propiedades frágicas: volumen', 'Valor': 150, 'Unidad': '%'},
                {'Parámetro': 'Saturación: días acumulados en años normales', 'Valor': 400, 'Unidad': 'días'},
                {'Parámetro': 'Capa con slickensides o cuñas: techo', 'Valor': 90, 'Unidad': 'cm'},
                {'Parámetro': 'Capa con slickensides o cuñas: espesor', 'Valor': 20, 'Unidad': 'cm'}]
        errors, pending = validate_extra(rows, 100)
        self.assertEqual(len(errors), 3)
        self.assertEqual(len(pending), 4)
        self.assertFalse(validate_extra([{'Parámetro': 'Pendiente', 'Valor': 150, 'Unidad': '%', 'Intervalo / método / evidencia': 'KFGL'}], 100)[0])

    def test_conflicting_results_not_adopted(self):
        result = determination('Lithic Hapludults', {'subgroup': 'Typic Hapludults'}, [], [])
        self.assertTrue(result['discrepancia'])
        self.assertIsNone(result['subgrupo_adoptado'])

    def test_lab_limits_missing_methods_and_depth(self):
        errors, _ = laboratory_issues([{'Parámetro': 'pH', 'Resultado': '20', 'Unidad': 'sin unidad'}], 20)
        self.assertTrue(errors)
        errors, pending = laboratory_issues([{'Parámetro': 'pH', 'Resultado': '5', 'Unidad': 'sin unidad', 'Techo (cm)': 0, 'Base (cm)': 25}], 20)
        self.assertTrue(any('profundidad' in e for e in errors))
        self.assertTrue(any('Método' in p for p in pending))

    def test_invalid_lab_reaches_report_and_blocks_guide(self):
        app = ready_app()
        app.session_state['study_tables']['profile_laboratory'] = [{'Parámetro': 'pH', 'Resultado': '20', 'Unidad': 'sin unidad'}]
        app.run(timeout=60)
        app.selectbox(key='guide_group').set_value('Hapludults').run()
        app.selectbox(key='guide_HCGA_outcome').set_value('Cumple')
        app.text_area(key='guide_HCGA_evidence').set_value('Evidencia sintética')
        app.run()
        self.assertFalse(app.exception)
        report = app.session_state['study_report']
        self.assertTrue(any('Laboratorio' in e for e in report['errores']))
        self.assertIsNone(report['clave_guiada']['subgroup'])
        self.assertIsNone(report['determinacion']['subgrupo_adoptado'])
        loaded = load_study(build_study(report, []))['report']
        self.assertEqual(loaded['laboratorio'][0]['Resultado'], '20')
        self.assertEqual(loaded['errores'], report['errores'])

    def test_observer_preserves_decisions_measurement_requires_review_and_roundtrip(self):
        app = ready_app().run(timeout=60)
        app.selectbox(key='guide_group').set_value('Hapludults').run()
        app.selectbox(key='guide_HCGA_outcome').set_value('Cumple')
        app.text_area(key='guide_HCGA_evidence').set_value('Evidencia conservada')
        app.run()
        self.assertIsNotNone(app.session_state['study_report']['clave_guiada']['subgroup'])
        app.text_input(key='profile_observer').set_value('Ana').run()
        self.assertEqual(app.text_area(key='guide_HCGA_evidence').value, 'Evidencia conservada')
        self.assertFalse(app.session_state['study_report']['clave_guiada']['requires_review'])
        app.number_input(key='profile_mean_temp').set_value(23.).run()
        report = app.session_state['study_report']
        self.assertTrue(report['clave_guiada']['requires_review'])
        self.assertIsNone(report['clave_guiada']['subgroup'])
        restored = restore_state(load_study(build_study(report, []))['report'])
        reopened = AppTest.from_file('app.py')
        for k, v in restored.items():
            reopened.session_state[k] = v
        reopened.run(timeout=60)
        self.assertFalse(reopened.exception)
        self.assertEqual(reopened.text_area(key='guide_HCGA_evidence').value, 'Evidencia conservada')
        self.assertTrue(reopened.session_state['study_report']['clave_guiada']['requires_review'])
        reopened.button(key='guide_confirm_Hapludults').click().run()
        self.assertIsNotNone(reopened.session_state['study_report']['clave_guiada']['subgroup'])
        self.assertIsNone(reopened.session_state['study_report']['determinacion']['subgrupo_adoptado'])
        reopened.button(key='profile_confirm_manual').click().run()
        self.assertIsNotNone(reopened.session_state['study_report']['determinacion']['subgrupo_adoptado'])

    def test_switching_guided_groups_preserves_work(self):
        app = ready_app().run(timeout=60)
        app.selectbox(key='guide_group').set_value('Hapludults').run()
        app.selectbox(key='guide_HCGA_outcome').set_value('No cumple')
        app.text_area(key='guide_HCGA_evidence').set_value('Evidencia de exclusión')
        app.run()
        app.selectbox(key='guide_group').set_value('Dystrudepts').run()
        app.selectbox(key='guide_group').set_value('Hapludults').run()
        self.assertEqual(app.text_area(key='guide_HCGA_evidence').value, 'Evidencia de exclusión')
        self.assertEqual(app.selectbox(key='guide_HCGA_outcome').value, 'No cumple')

    def test_history_keeps_agronomic_results_outside_evidence(self):
        app = ready_app()
        old = {'Parámetro': 'Fósforo extraíble (P)', 'Resultado': '15', 'Unidad': 'mg/kg', 'Estado del laboratorio': 'Alto'}
        app.session_state['study_tables']['profile_laboratory'] = [old]
        app.run(timeout=60)
        self.assertFalse(app.exception)
        report = app.session_state['study_report']
        self.assertEqual(report['laboratorio'], [])
        self.assertEqual(report['laboratorio_historico_no_taxonomico'], [old])
        saved = load_study(build_study(report, []))['report']
        self.assertEqual(restore_state(saved)['study_laboratory_legacy'], [old])

    def test_horizon_views_preserve_hidden_data(self):
        app = ready_app()
        app.session_state['horizon_rows'][0].update({'pH H2O': 5.1, 'Métodos / muestra / observaciones': 'M1, agua 1:1, criterio documentado'})
        app.run(timeout=60)
        app.selectbox(key='profile_horizon_view').set_value('Descripción de campo').run()
        self.assertEqual(app.session_state['study_report']['horizontes'][0]['pH H2O'], 5.1)
        app.selectbox(key='profile_horizon_view').set_value('Mediciones para diagnósticos').run()
        self.assertEqual(app.session_state['study_report']['horizontes'][0]['Horizonte'], 'A')

    def test_restored_photo_caption_can_be_edited_and_excluded(self):
        import hashlib
        stream = io.BytesIO()
        Image.new('RGB', (12, 12), 'green').save(stream, format='PNG')
        data = stream.getvalue()
        sha = hashlib.sha256(data).hexdigest()
        photo = {'data': data, 'sha256': sha, 'nombre_original': 'p.png', 'ruta_zip': 'fotos/p.png', 'descripcion': 'Antes', **validate_photo(data)}
        app = ready_app()
        app.session_state['study_photos'] = [photo]
        app.run(timeout=60)
        app.text_input(key=f'photo_caption_{sha}').set_value('Horizonte A, húmedo').run()
        self.assertEqual(app.session_state['study_report']['fotos'][0]['descripcion'], 'Horizonte A, húmedo')
        app.checkbox(key=f'profile_photo_exclude_{sha}').check().run()
        self.assertEqual(app.session_state['study_report']['fotos'], [])
        app.checkbox(key=f'profile_photo_exclude_{sha}').uncheck().run()
        self.assertEqual(len(app.session_state['study_report']['fotos']), 1)


if __name__ == '__main__':
    unittest.main()

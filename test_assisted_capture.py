"""Interaction regressions for form capture and portable persistence."""
import unittest
from copy import deepcopy
from streamlit.testing.v1 import AppTest
from test_taxonomy_scope import ready_app
from study_storage import build_study, load_study, restore_state
from usda_capture import structure_size, boundary_class, description_issues


class AssistedCaptureTests(unittest.TestCase):
    def test_description_checks_only_active_observations(self):
        horizons = [{'_horizon_uid': 'h1', 'Horizonte': 'A'}]
        record = {'estructura_tipo': 'Granular (GR)', 'estructura_mm': 0}
        errors, pending = description_issues({'h1': record}, horizons)
        self.assertTrue(errors)
        self.assertTrue(pending)
        record['estructura_tipo'] = 'Masiva (MA)'
        self.assertEqual(description_issues({'h1': record}, horizons), ([], []))
        record.update(redox_estado='Presentes', redox_porcentaje=101)
        errors, pending = description_issues({'h1': record}, horizons)
        self.assertTrue(errors)
        self.assertTrue(pending)
        self.assertEqual(description_issues({'h1': record}, []), ([], []))

    def test_no_editable_tables_or_observations_created_on_open(self):
        app = AppTest.from_file('app.py').run(timeout=60)
        self.assertFalse(app.exception)
        self.assertFalse(app.get('data_editor'))
        self.assertFalse(app.session_state['study_report']['horizontes'])
        self.assertEqual(app.session_state['study_report']['descripcion_asistida']['sitio'], {})

    def test_texture_and_navigation_preserve_records(self):
        app = ready_app().run(timeout=60)
        uid = app.session_state['horizon_rows'][0]['_horizon_uid']
        key = 'profile_horizon_' + uid
        app.number_input(key=key+'_Arena (%)').set_value(40.).run()
        app.number_input(key=key+'_Limo (%)').set_value(40.).run()
        self.assertEqual(app.session_state['horizon_rows'][0]['Arcilla (%)'], 20.)
        app.button(key='profile_add_horizon').click().run()
        uid2 = app.session_state['horizon_rows'][1]['_horizon_uid']
        app.selectbox(key='profile_horizon_'+uid2+'_name').set_value('Bt').run()
        app.selectbox(key='profile_horizon_selected').set_value(0).run()
        self.assertEqual(app.number_input(key=key+'_Arena (%)').value, 40.)
        app.number_input(key=key+'_Arena (%)').set_value(50.).run()
        self.assertEqual(app.session_state['horizon_rows'][0]['Arcilla (%)'], 10.)
        app.selectbox(key='profile_horizon_view').set_value('Descripción de campo').run()
        app.selectbox(key='profile_horizon_view').set_value('Textura y color').run()
        self.assertEqual(app.number_input(key=key+'_Arcilla (%)').value, 10.)
        self.assertFalse(app.exception)

    def test_conditional_structure_keeps_hidden_values_and_roundtrips(self):
        app = ready_app().run(timeout=60)
        uid = app.session_state['horizon_rows'][0]['_horizon_uid']
        key = 'profile_morph_' + uid
        app.selectbox(key='profile_horizon_view').set_value('Descripción de campo').run()
        app.selectbox(key=key+'_structure').set_value('Granular (GR)').run()
        app.selectbox(key=key+'_grade').set_value('Moderada (2)').run()
        app.number_input(key=key+'_size').set_value(3.).run()
        app.selectbox(key=key+'_structure').set_value('Masiva (MA)').run()
        self.assertNotIn(key+'_size', [w.key for w in app.number_input])
        report = deepcopy(app.session_state['study_report'])
        restored = restore_state(load_study(build_study(report, []))['report'])
        reopened = AppTest.from_file('app.py')
        for k, v in restored.items():
            reopened.session_state[k] = v
        reopened.run(timeout=60)
        reopened.selectbox(key='profile_horizon_view').set_value('Descripción de campo').run()
        reopened.selectbox(key=key+'_structure').set_value('Granular (GR)').run()
        self.assertEqual(reopened.number_input(key=key+'_size').value, 3.)
        self.assertEqual(reopened.selectbox(key=key+'_grade').value, 'Moderada (2)')

    def test_laboratory_new_edit_clear_switch_and_undo(self):
        app = ready_app().run(timeout=60)
        app.button(key='profile_add_lab').click().run()
        app.selectbox(key='profile_lab_0_parameter').set_value('pH').run()
        self.assertEqual(app.selectbox(key='profile_lab_0_unit').options, ['No evaluado', 'sin unidad'])
        app.text_input(key='profile_lab_0_result').set_value('5,2').run()
        app.text_input(key='profile_lab_0_sample').set_value('M1').run()
        app.button(key='profile_add_lab').click().run()
        app.selectbox(key='profile_lab_1_parameter').set_value('Carbono orgánico').run()
        app.text_input(key='profile_lab_1_result').set_value('2.5').run()
        app.selectbox(key='profile_lab_selected').set_value(0).run()
        self.assertEqual(app.text_input(key='profile_lab_0_result').value, '5,2')
        app.text_input(key='profile_lab_0_sample').set_value('').run()
        self.assertEqual(app.session_state['study_report']['laboratorio'][0]['Muestra'], '')
        app.button(key='profile_lab_0_remove').click().run()
        self.assertEqual(app.session_state['study_report']['laboratorio'][0]['Resultado'], '2.5')
        app.button(key='profile_restore_lab').click().run()
        self.assertEqual(app.session_state['study_report']['laboratorio'][0]['Resultado'], '5,2')
        self.assertFalse(app.exception)

    def test_legacy_laboratory_survives_multiple_reruns(self):
        app = ready_app()
        old = {'Parámetro': 'Fósforo extraíble (P)', 'Resultado': '15', 'Unidad': 'mg/kg'}
        app.session_state['study_tables']['profile_laboratory'] = [old]
        app.run(timeout=60)
        app.text_input(key='profile_observer').set_value('Ana').run()
        app.run()
        self.assertEqual(app.session_state['study_report']['laboratorio_historico_no_taxonomico'], [old])

    def test_diagnostic_switch_keeps_evidence(self):
        app = ready_app().run(timeout=60)
        app.selectbox(key='profile_diagnostics_0_status').set_value('Presente').run()
        app.text_area(key='profile_diagnostics_0_evidence').set_value('Evidencia sintética').run()
        app.selectbox(key='profile_diagnostics_selected').set_value(1).run()
        app.selectbox(key='profile_diagnostics_selected').set_value(0).run()
        self.assertEqual(app.text_area(key='profile_diagnostics_0_evidence').value, 'Evidencia sintética')
        self.assertFalse(app.exception)

    def test_reference_boundaries(self):
        self.assertEqual(structure_size('Granular (GR)', 5), 'Gruesa')
        self.assertEqual(structure_size('Prismática (PR)', 5), 'Muy fina')
        self.assertEqual(structure_size('Prismática (PR)', 500), 'Extremadamente gruesa')
        self.assertIsNone(structure_size('Masiva (MA)', 5))
        self.assertEqual(boundary_class(0.5), 'Abrupto')
        self.assertEqual(boundary_class(2), 'Claro')
        self.assertEqual(boundary_class(15), 'Difuso')


if __name__ == '__main__':
    unittest.main()

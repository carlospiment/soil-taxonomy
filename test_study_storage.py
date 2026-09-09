"""Round trips and hostile input use synthetic data, never field validation."""
import hashlib
import io
import json
import unittest
import zipfile
from copy import deepcopy
from datetime import date
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest
from field_media import make_archive, validate_photo
from study_storage import build_study, load_study, restore_state
from visual_observations import create_observation, HORIZON_ID
from soil_color.validation import review_color, apply_color
from texture import complete_texture, AUTO


class StudyTests(unittest.TestCase):
    def test_export_without_profile_does_not_crash_or_invent_report(self):
        with patch('storage_ui.build_study') as build:
            app = AppTest.from_string('from storage_ui import render_study_export\nrender_study_export()').run(timeout=30)
            self.assertFalse(app.exception)
            self.assertTrue(any('todavía no está disponible' in w.value for w in app.warning))
            self.assertNotIn('study_report', app.session_state)
            build.assert_not_called()

    @classmethod
    def setUpClass(cls):
        app = AppTest.from_file('app.py').run(timeout=30)
        assert not app.exception
        cls.base = deepcopy(app.session_state['study_report'])

    def fixture(self):
        report = deepcopy(self.base)
        stream = io.BytesIO()
        Image.new('RGB', (12, 12), (100, 70, 40)).save(stream, 'PNG')
        data = stream.getvalue()
        sha = hashlib.sha256(data).hexdigest()
        photo = {'sha256': sha, 'ruta_zip': 'fotos/01.png', 'nombre_original': '01.png', 'descripcion': 'A', **validate_photo(data), 'data': data}
        report['fotos'] = [{k: v for k, v in photo.items() if k != 'data'}]
        from visual_observations import new_id
        uid = new_id()
        row = complete_texture({'Horizonte': 'A', 'Techo (cm)': 0, 'Base (cm)': 20, 'Arena (%)': 40, 'Limo (%)': 40})
        report['fracciones_calculadas'] = [{'fila': 1, 'fraccion': row.pop(AUTO)}]
        trace = report['trazabilidad_visual']
        obs = create_observation(profile_uid=trace['profile_uid'], horizon_uid=uid, image_sha256=sha, kind='color', moisture_state='dry', predicted_value={'munsell': '10YR 4/3', 'Lab': [40, 8, 16]}, method='synthetic', algorithm_version='1')
        obs = review_color(obs, 'accepted', 'Reviewer', 'Synthetic reference')
        obs, rows = apply_color(obs, [{**row, HORIZON_ID: uid}], trace['profile_uid'], None, 'Reviewer')
        rows[0].pop(HORIZON_ID)
        report['horizontes'] = rows
        trace['horizons'] = [{'horizon_uid': uid, 'row_number': 1, 'label': 'A'}]
        trace['observations'] = [obs]
        report['identificador'] = 'Estudio prueba'
        report['fecha_descripcion'] = '2026-09-09'
        report['diagnosticos'][0]['Evidencia / método / criterio'] = 'Saved evidence'
        report['medidas_adicionales'][0]['Valor'] = 12.0
        report['ruta'][0]['Taxón'] = 'Ultisols'
        structures = [{'schema_version': 1, 'image': {'sha256': sha}, 'raw_response': {'outputs': []}, 'summary': {'status': 'empty'}}]
        return report, [photo], structures

    def test_backup_roundtrip_and_migration(self):
        report, photos, structures = self.fixture()
        packed = build_study(report, photos, structures=structures)
        recovered = load_study(packed)
        self.assertEqual(recovered['report']['trazabilidad_visual']['observations'], report['trazabilidad_visual']['observations'])
        self.assertEqual(recovered['photos'][0]['data'], photos[0]['data'])
        self.assertEqual(recovered['structures'], structures)
        state = restore_state(recovered['report'])
        self.assertEqual(state['profile_date'], date(2026, 9, 9))
        self.assertEqual(state['horizon_rows'][0][AUTO], 'Arcilla (%)')
        backup = load_study(build_study(recovered['report'], recovered['photos'], recovered['images'], recovered['structures']))
        self.assertEqual(backup, recovered)
        migrated = load_study(make_archive(report, photos))
        self.assertTrue(migrated['migrated'])
        self.assertEqual(migrated['report'], recovered['report'])

    def test_reject_missing_images_invalid_version_and_tampering(self):
        report, photos, _ = self.fixture()
        with self.assertRaises(ValueError):
            build_study(report, [])
        packed = build_study(report, photos)
        with zipfile.ZipFile(io.BytesIO(packed)) as archive:
            files = {n: archive.read(n) for n in archive.namelist()}
        for name, replacement in [('estudio.json', b'{}'), ('manifest.json', b'{"schema_version":99,"files":{}}')]:
            bad = io.BytesIO()
            with zipfile.ZipFile(bad, 'w') as archive:
                for key, value in files.items():
                    archive.writestr(key, replacement if key == name else value)
            with self.assertRaises(ValueError):
                load_study(bad.getvalue())

    def test_reject_paths_duplicates_and_invalid_controls(self):
        for path in ('../outside', '/absolute', 'C:/private', 'folder\\file'):
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as archive:
                archive.writestr(path, b'no extraction')
            with self.assertRaises(ValueError):
                load_study(stream.getvalue())
        report, photos, _ = self.fixture()
        for field, value in [('profundidad_cm', -1), ('regimen_humedad', 'unknown'), ('fecha_descripcion', 'bad')]:
            invalid = deepcopy(report)
            invalid[field] = value
            with self.assertRaises(ValueError):
                load_study(make_archive(invalid, photos))
        for mutate in (
            lambda o: o.update(schema_version=99),
            lambda o: o['context'].update(horizon_snapshot=[]),
            lambda o: o.update(status='pending'),
            lambda o: o['applications'][0].update(applied_value='N5'),
        ):
            invalid = deepcopy(report)
            mutate(invalid['trazabilidad_visual']['observations'][0])
            with self.assertRaises(ValueError):
                load_study(make_archive(invalid, photos))

    def test_limits_duplicates_and_no_filesystem_extraction(self):
        import warnings
        report, photos, _ = self.fixture()
        packed = build_study(report, photos)
        with patch('zipfile.ZipFile.extractall') as extract, patch('pathlib.Path.write_bytes') as write:
            load_study(packed)
            extract.assert_not_called()
            write.assert_not_called()
        with patch('study_storage.MAX_ARCHIVE', 20):
            with self.assertRaises(ValueError):
                load_study(packed)
        stream = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(stream, 'w') as archive:
                archive.writestr('manifest.json', '{}')
                archive.writestr('manifest.json', '{}')
        with self.assertRaises(ValueError):
            load_study(stream.getvalue())

    def test_ui_recovers_edits_and_rejects_without_replacing(self):
        report, photos, structures = self.fixture()
        uploaded = io.BytesIO(build_study(report, photos, structures=structures))
        def upload(*args, **kwargs):
            if kwargs.get('key') == 'study_upload':
                return uploaded
            return [] if kwargs.get('key') == 'profile_photos' else None
        downloads = {}
        def download(label, data, *args, **kwargs):
            downloads[kwargs.get('key')] = data
            return False
        with patch('streamlit.file_uploader', side_effect=upload), patch('streamlit.download_button', side_effect=download), patch('structure_ui.run_workflow') as remote:
            app = AppTest.from_file('app.py').run(timeout=30)
            app.session_state['rf_api_key'] = 'secret-never-export'
            app.checkbox(key='study_replace').check().run()
            app.button(key='study_open').click().run(timeout=30)
            self.assertFalse(app.exception)
            self.assertEqual(app.text_input(key='profile_id').value, 'Estudio prueba')
            recovered = load_study(downloads['study_download'])
            self.assertEqual(recovered['photos'], photos)
            self.assertEqual(recovered['structures'], structures)
            self.assertEqual(recovered['report']['trazabilidad_visual']['observations'], report['trazabilidad_visual']['observations'])
            self.assertEqual(recovered['report']['horizontes'][0]['Color seco (Munsell)'], '10YR 4/3')
            for key in ('diagnosticos', 'medidas_adicionales', 'ruta', 'fecha_descripcion'):
                self.assertEqual(recovered['report'][key], report[key])
            self.assertEqual(app.session_state['horizon_rows'][0][AUTO], 'Arcilla (%)')
            with zipfile.ZipFile(io.BytesIO(downloads['study_download'])) as archive:
                self.assertNotIn(b'secret-never-export', archive.read('estudio.json'))
            app.text_input(key='profile_id').set_value('Edited').run()
            app.run()
            self.assertEqual(load_study(downloads['study_download'])['report']['identificador'], 'Edited')
            uploaded.seek(0)
            uploaded.truncate()
            uploaded.write(b'corrupt')
            app.button(key='study_open').click().run()
            self.assertTrue(app.error)
            self.assertEqual(app.text_input(key='profile_id').value, 'Edited')
            remote.assert_not_called()

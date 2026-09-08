import io
import json
import unittest
import zipfile
from unittest.mock import patch
from PIL import Image
from streamlit.testing.v1 import AppTest
from texture import FRACTIONS, AUTO, REGIONS, classify_texture, complete_texture, apply_editor_changes, texture_figure
from field_media import utm_to_geographic, validate_photo, make_archive


class TextureTests(unittest.TestCase):
    def test_twelve_reference_compositions(self):
        examples = [(95,3,2),(82,10,8),(65,25,10),(40,40,20),(20,65,15),(5,90,5),
                    (60,15,25),(35,30,35),(10,55,35),(55,5,40),(5,50,45),(20,20,60)]
        self.assertEqual([classify_texture(*v) for v in examples], list(REGIONS))

    def test_all_integer_compositions_have_class(self):
        for sand in range(101):
            for silt in range(101-sand):
                self.assertIn(classify_texture(sand,silt,100-sand-silt), REGIONS)

    def test_every_polygon_interior_matches_class(self):
        for name, vertices in REGIONS.items():
            center = [sum(v[i] for v in vertices)/len(vertices) for i in range(3)]
            self.assertEqual(classify_texture(*center), name)

    def test_boundaries(self):
        self.assertEqual(classify_texture(85,15,0), "Arenosa franca")
        self.assertEqual(classify_texture(70,30,0), "Franco arenosa")
        self.assertEqual(classify_texture(20,80,0), "Limosa")
        self.assertEqual(classify_texture(20,53,27), "Franco arcillo limosa")
        self.assertEqual(classify_texture(20,40,40), "Arcillo limosa")

    def test_any_third_fraction_is_completed(self):
        for missing in FRACTIONS:
            row = {f:40.0 for f in FRACTIONS if f != missing}
            result=complete_texture(row)
            self.assertEqual(result[missing],20)
            self.assertEqual(result[AUTO],missing)

    def test_recalculation_and_manual_override(self):
        row = complete_texture({FRACTIONS[0]:40,FRACTIONS[1]:40})
        changed=apply_editor_changes([row], {"edited_rows":{0:{FRACTIONS[0]:60}}})[0]
        self.assertEqual(changed[FRACTIONS[2]],0)
        changed=apply_editor_changes([changed], {"edited_rows":{0:{FRACTIONS[2]:10}}})[0]
        self.assertIsNone(changed[AUTO])
        self.assertIsNone(changed["Clase textural USDA"])

    def test_clear_measured_value_removes_stale_derived(self):
        row = complete_texture({FRACTIONS[0]:40,FRACTIONS[1]:40})
        changed=apply_editor_changes([row], {"edited_rows":{0:{FRACTIONS[0]:None}}})[0]
        self.assertIsNone(changed[FRACTIONS[2]])
        self.assertIsNone(changed["Clase textural USDA"])

    def test_invalid_sum_never_negative_or_normalized(self):
        row = complete_texture({FRACTIONS[0]:80,FRACTIONS[1]:30})
        self.assertIsNone(row.get(FRACTIONS[2]))
        for values in [(40,40,19.9),(-1,50,51),(float("nan"),50,50)]:
            with self.assertRaises(ValueError): classify_texture(*values)

    def test_add_delete_and_point(self):
        rows=apply_editor_changes([{}], {"deleted_rows":[0],"added_rows":[{FRACTIONS[0]:40,FRACTIONS[1]:40}]})
        self.assertEqual(len(rows),1)
        point=texture_figure(rows[0]).data[-1]
        self.assertEqual(list(point.a),[20])
        self.assertEqual(list(point.b),[40])
        self.assertEqual(list(point.c),[40])

    def test_ui_renders_computed_horizon(self):
        app=AppTest.from_file("app.py")
        app.session_state["horizon_rows"]=[complete_texture({"Horizonte":"A", "Techo (cm)":0, "Base (cm)":20, FRACTIONS[0]:40,FRACTIONS[1]:40})]
        app.session_state["horizon_revision"]=0
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("Resultado textural: Franca" in m.value for m in app.markdown))


class LocationPhotoTests(unittest.TestCase):
    def test_known_utm_origins(self):
        for zone, longitude in [(17,-81),(31,3),(60,177)]:
            for hemi,north in [("Norte",0),("Sur",10000000)]:
                converted=utm_to_geographic(zone,hemi,500000,north)
                self.assertAlmostEqual(converted["latitud"],0,places=6)
                self.assertAlmostEqual(converted["longitud"],longitude,places=6)

    def test_incomplete_and_invalid_utm(self):
        for args in [(None,"Norte",500000,0),(61,"Norte",500000,0),(17,None,500000,0),(17,"Norte",10,0),(17,"Norte",500000,10000000)]:
            with self.assertRaises(ValueError): utm_to_geographic(*args)

    def test_photo_and_zip_round_trip(self):
        stream=io.BytesIO()
        Image.new("RGB",(20,10),"green").save(stream,format="PNG")
        data=stream.getvalue()
        self.assertEqual(validate_photo(data)["ancho_px"],20)
        report={"responsable":"Ana", "fecha_descripcion":"2026-09-07", "fotos":[{"ruta_zip":"fotos/01_perfil.png"}]}
        with zipfile.ZipFile(io.BytesIO(make_archive(report,[{"ruta_zip":"fotos/01_perfil.png","data":data}]))) as archive:
            self.assertEqual(json.loads(archive.read("perfil_taxonomico.json")),report)
            self.assertEqual(archive.read("fotos/01_perfil.png"),data)

    def test_invalid_photo_rejected(self):
        with self.assertRaises(ValueError): validate_photo(b"not a photo")

    def test_separate_date_and_utm_ui(self):
        from datetime import date
        app=AppTest.from_file("app.py").run(timeout=30)
        app.text_input(key="profile_observer").set_value("Ana")
        app.date_input(key="profile_date").set_value(date(2026,9,7))
        app.selectbox(key="location_mode").set_value("UTM (metros)").run()
        app.selectbox(key="location_zone").set_value(17)
        app.selectbox(key="location_hemisphere").set_value("Norte")
        app.number_input(key="location_east").set_value(500000)
        app.number_input(key="location_north").set_value(1000000)
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.date_input(key="profile_date").value,date(2026,9,7))
        self.assertEqual(app.text_input(key="profile_observer").value,"Ana")
        self.assertTrue(any("EPSG:32617" in c.value for c in app.caption))

    def test_actual_form_export_includes_photo_date_and_location(self):
        from datetime import date
        from types import SimpleNamespace
        image = io.BytesIO()
        Image.new("RGB", (12,12), "green").save(image, format="PNG")
        data = image.getvalue()
        photo = SimpleNamespace(name="perfil.png", size=len(data), getvalue=lambda: data)
        downloads = {}

        def upload(*args, **kwargs):
            return [photo] if kwargs.get("key") == "profile_photos" else None

        def download(label, data, *args, **kwargs):
            downloads[kwargs["key"]] = data
            return False

        with patch("streamlit.file_uploader", side_effect=upload), patch("streamlit.download_button", side_effect=download):
            app=AppTest.from_file("app.py").run(timeout=30)
            app.text_input(key="profile_observer").set_value("Ana")
            app.date_input(key="profile_date").set_value(date(2026,9,7))
            app.selectbox(key="location_mode").set_value("Geográficas (grados decimales)").run()
            app.number_input(key="location_lat").set_value(8.98)
            app.number_input(key="location_lon").set_value(-79.52)
            app.run()
            self.assertFalse(app.exception)
        report=json.loads(downloads["profile_download"])
        self.assertEqual(report["responsable"],"Ana")
        self.assertEqual(report["fecha_descripcion"],"2026-09-07")
        self.assertEqual(report["ubicacion"]["longitud"],-79.52)
        self.assertEqual(len(report["fotos"]),1)
        with zipfile.ZipFile(io.BytesIO(downloads["profile_download_zip"])) as archive:
            self.assertEqual(archive.read(report["fotos"][0]["ruta_zip"]),data)
            self.assertEqual(json.loads(archive.read("perfil_taxonomico.json")),report)


if __name__ == "__main__": unittest.main()

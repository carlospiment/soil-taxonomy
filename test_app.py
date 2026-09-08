"""Pruebas del dashboard con datos sintéticos; no validan taxonomía USDA."""
import io
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest


class DashboardTests(unittest.TestCase):
    def datos(self):
        return pd.DataFrame({
            "pH": [5.0, np.nan, 6.0, 7.0] * 6,
            "Region": ["Norte", "Sur", None, "Este"] * 6,
            "Orden": ["Alfisol", "Ultisol"] * 12,
        })

    def ejecutar(self, df, features, extension="csv", expected_error=None):
        archivo = io.BytesIO()
        if extension == "xlsx":
            df.to_excel(archivo, index=False)
        else:
            archivo.write(df.to_csv(index=False).encode("utf-8"))
        archivo.name = f"sintetico.{extension}"

        def cargar(*args, **kwargs):
            if kwargs.get("key") == "profile_photos":
                return []
            archivo.seek(0)
            return archivo

        with patch("streamlit.file_uploader", side_effect=cargar):
            app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run(timeout=30)
            app.multiselect(key="ml_features").set_value(features)
            app.selectbox(key="ml_target").set_value("Orden")
            app.run(timeout=30)
            self.assertFalse(app.exception)
            if expected_error:
                self.assertTrue(any(expected_error in e.value for e in app.error), list(app.error))
                self.assertEqual(len(app.metric), 0)
                return
            self.assertFalse(app.error, [e.value for e in app.error])
            self.assertEqual(len(app.metric), 1)
            app.button[0].click().run(timeout=30)
            self.assertFalse(app.exception)
            self.assertFalse(app.error, [e.value for e in app.error])
            self.assertTrue(any("El suelo predicho es:" in s.value for s in app.success))

    def test_inicio(self):
        app = AppTest.from_file("app.py").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs), 2)

    def test_csv_mixto_con_faltantes(self):
        self.ejecutar(self.datos(), ["pH", "Region"])

    def test_excel_mixto(self):
        self.ejecutar(self.datos(), ["pH", "Region"], "xlsx")

    def test_solo_numeros(self):
        self.ejecutar(self.datos(), ["pH"])

    def test_solo_texto(self):
        self.ejecutar(self.datos(), ["Region"])

    def test_resultados_faltantes(self):
        df = self.datos()
        df.loc[0, "Orden"] = None
        self.ejecutar(df, ["pH", "Region"])

    def test_fuga_resultado(self):
        self.ejecutar(self.datos(), ["Orden"], expected_error="no puede ser también predictora")

    def test_columna_vacia(self):
        df = self.datos()
        df["pH"] = np.nan
        self.ejecutar(df, ["pH"], expected_error="no tienen valores válidos")

    def test_muestra_insuficiente(self):
        self.ejecutar(self.datos().iloc[:2], ["pH"], expected_error="dos filas")


if __name__ == "__main__":
    unittest.main()

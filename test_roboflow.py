"""Verifica el envío y los errores sin consumir la API de Roboflow."""
import io
import os
import unittest
from unittest.mock import MagicMock, patch

from PIL import Image
from streamlit.testing.v1 import AppTest
from soil_structure.roboflow_client import WorkflowError


class RoboflowTests(unittest.TestCase):
    def ejecutar(self, error=False):
        archivo = io.BytesIO()
        Image.new("RGB", (20, 20), (110, 80, 50)).save(archivo, "PNG")

        def cargar(*args, **kwargs):
            if kwargs.get("key") == "rf_photo":
                return archivo
            if kwargs.get("key") == "profile_photos":
                return []
            return None

        cliente = MagicMock()
        cliente.return_value = {"outputs": [{"predictions": []}]}
        if error:
            cliente.side_effect = WorkflowError("timeout", "Se agotó la espera de Roboflow.")
        with patch.dict(os.environ, {"ROBOFLOW_API_KEY": "private-test-key"}), \
             patch("streamlit.file_uploader", side_effect=cargar), \
             patch("structure_ui.run_workflow", new=cliente):
            app = AppTest.from_file("app.py").run(timeout=30)
            self.assertFalse(app.exception)
            cliente.assert_not_called()
            app.button(key="rf_analyze").click().run(timeout=30)
            self.assertFalse(app.exception)
            imagen, clave, config = cliente.call_args.args
            self.assertEqual(config.workspace, "carlos-pimentel")
            self.assertEqual(config.workflow_id, "usda-soil-structure")
            self.assertEqual(config.confidence, 0.4)
            self.assertIsInstance(imagen, Image.Image)
            if error:
                self.assertTrue(app.error)
                self.assertNotIn("private-test-key", app.error[0].value)
            else:
                self.assertFalse(app.error)
                self.assertTrue(app.json)
                app.run(timeout=30)
                cliente.assert_called_once()
                self.assertTrue(app.json)
                self.assertEqual(app.session_state["rf_result"]["result"]["raw_response"], cliente.return_value)
                archivo.seek(0)
                archivo.truncate()
                Image.new("RGB", (10, 10), "blue").save(archivo, "PNG")
                app.run(timeout=30)
                cliente.assert_called_once()
                self.assertNotIn('rf_result', app.session_state)
                self.assertEqual(len(app.session_state['study_structures']), 1)

    def test_envio_y_persistencia(self):
        self.ejecutar()

    def test_error_sin_exponer_clave(self):
        self.ejecutar(error=True)

import unittest
from soil_profile import validate_profile, evaluate_route
from subgroup_guide import KEYS, resolve_key
from streamlit.testing.v1 import AppTest


class ProfileTests(unittest.TestCase):
    def test_empty_is_pending(self):
        errors, pending = validate_profile([], [], None)
        self.assertFalse(errors)
        self.assertEqual(len(pending), 2)

    def test_overlap_and_texture(self):
        errors, _ = validate_profile([
            {"Techo (cm)": 0, "Base (cm)": 30},
            {"Techo (cm)": 20, "Base (cm)": 50, "Arena (%)": 60, "Limo (%)": 30, "Arcilla (%)": 30},
        ], [], 50)
        self.assertEqual(len(errors), 2)

    def test_diagnostic_requires_evidence(self):
        _, pending = validate_profile([], [{"Diagnóstico": "Argílico", "Estado": "Presente"}], 100)
        self.assertTrue(any("Argílico" in p for p in pending))

    def test_missing_intervals(self):
        _, pending = validate_profile([{"Techo (cm)": 10, "Base (cm)": 30}], [], 100)
        self.assertEqual(len(pending), 2)

    def test_manual_route_cannot_skip_parent(self):
        rows = [{"Nivel": level, "Taxón": "X", "Clave / página": "p1", "Evidencia y exclusión de anteriores": "Dato", "Revisión": "Cumple; anteriores descartados"} for level in ["Orden", "Suborden", "Gran grupo", "Subgrupo"]]
        rows[1]["Revisión"] = "Pendiente"
        status, subgroup = evaluate_route(rows, [])
        self.assertIsNone(subgroup)
        self.assertIn("Orden", status)

    def test_default_ui_has_no_subgroup(self):
        app = AppTest.from_file("app.py").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.success)
        app.selectbox(key="guide_group").set_value("Hapludults").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("Documenta primero" in w.value for w in app.warning))


class GuidedKeyTests(unittest.TestCase):
    def test_complete_source_sequences(self):
        for group, prefix, n in [("Hapludults", "HCG", 15), ("Dystrudepts", "KFG", 26)]:
            entries = KEYS[group]["entries"]
            self.assertEqual([e["code"] for e in entries], [prefix + chr(65+i) for i in range(n)])
            self.assertEqual(entries[-1]["name"], "Typic " + group)
            self.assertTrue(all(e["criteria"] for e in entries))

    def test_unknown_predecessor_blocks_lithic(self):
        result = resolve_key("Hapludults", {"HCGB": {"outcome": "Cumple", "evidence": "Contacto a 40 cm"}}, True)
        self.assertIsNone(result["subgroup"])
        self.assertIn("HCGA", result["reason"])

    def test_lithic_after_exclusion(self):
        result = resolve_key("Hapludults", {
            "HCGA": {"outcome": "No cumple", "evidence": "Contacto continuo; argílico continuo"},
            "HCGB": {"outcome": "Cumple", "evidence": "Contacto lítico a 40 cm desde superficie mineral"},
        }, True)
        self.assertEqual(result["subgroup"], "Lithic Hapludults")

    def test_first_match_wins(self):
        result = resolve_key("Dystrudepts", {
            "KFGA": {"outcome": "Cumple", "evidence": "Contacto a 40 cm y colores requeridos en 18 cm"},
            "KFGB": {"outcome": "Cumple", "evidence": "Contacto a 40 cm"},
        }, True)
        self.assertEqual(result["subgroup"], "Humic Lithic Dystrudepts")

    def test_typic_needs_all_exclusions(self):
        entries = KEYS["Hapludults"]["entries"]
        decisions = {e["code"]: {"outcome": "No cumple", "evidence": "Exclusión documentada para prueba"} for e in entries[:-1]}
        self.assertIsNone(resolve_key("Hapludults", decisions, True)["subgroup"])
        decisions["HCGO"] = {"outcome": "Cumple", "evidence": "Revisadas las 14 exclusiones anteriores"}
        self.assertEqual(resolve_key("Hapludults", decisions, True)["subgroup"], "Typic Hapludults")
        decisions["HCGC"]["evidence"] = ""
        self.assertIsNone(resolve_key("Hapludults", decisions, True)["subgroup"])

    def test_unverified_parent_and_invalid_profile_block(self):
        decisions = {"HCGA": {"outcome": "Cumple", "evidence": "Dato"}}
        self.assertIsNone(resolve_key("Hapludults", decisions)["subgroup"])
        self.assertIsNone(resolve_key("Hapludults", decisions, True, ["Error"])["subgroup"])

    def test_guide_ui_and_changed_evidence(self):
        def guide_app():
            import streamlit as st
            from subgroup_guide import render_guide
            revision = st.text_input("Revisión del perfil", value="1", key="revision")
            route = [{"Taxón": taxon, "Revisión": "Cumple; anteriores descartados", "Clave / página": "Referencia de prueba", "Evidencia y exclusión de anteriores": "Evidencia de prueba"} for taxon in ["Ultisols", "Udults", "Hapludults"]]
            render_guide(route, [], revision)
        app = AppTest.from_function(guide_app).run(timeout=30)
        app.selectbox(key="guide_group").set_value("Hapludults").run()
        app.selectbox(key="guide_HCGA_outcome").set_value("No cumple")
        app.text_area(key="guide_HCGA_evidence").set_value("Contacto continuo y argílico continuo")
        app.run()
        app.selectbox(key="guide_HCGB_outcome").set_value("Cumple")
        app.text_area(key="guide_HCGB_evidence").set_value("Contacto lítico a 40 cm")
        app.run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Lithic Hapludults" in s.value for s in app.success))
        app.text_input(key="revision").set_value("2").run()
        self.assertFalse(app.exception)
        self.assertFalse(app.success)
        self.assertEqual(app.selectbox(key="guide_HCGA_outcome").value, "No evaluado")


if __name__ == "__main__":
    unittest.main()

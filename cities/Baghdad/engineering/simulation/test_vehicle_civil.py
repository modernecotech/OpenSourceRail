import unittest

from cities.Baghdad.engineering.simulation.vehicle_civil import evaluate


class AirportEngineeringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = evaluate()
        cls.short = evaluate(dict(cars=3, material="hybrid", span_m=25))

    def test_loads_close_at_all_nine_points(self):
        for name, cases in self.reference["cases"].items():
            self.assertLess(cases["low"]["loaded_train_kg"], cases["high"]["loaded_train_kg"], name)
            for case in cases.values():
                self.assertAlmostEqual(case["tare_train_kg"], 6*sum(case["group_kg_per_car"].values()))
                self.assertAlmostEqual(case["gravity_balance_kg"],0)
                self.assertAlmostEqual(case["moment_balance_kg_m"],0)
                self.assertGreaterEqual(min(case["axle_kg_per_car"]),0)

    def test_parent_and_revision_scope(self):
        self.assertEqual(self.reference["parent_candidate_id"],self.short["parent_candidate_id"])
        self.assertNotEqual(self.reference["physical_id"],self.short["physical_id"])
        self.assertEqual(self.short["selected"]["people"],350)
        self.assertIsNone(self.short["structure"]["body_vertical"])
        self.assertEqual(self.short["selected_span"]["stock_length_m"],25)
        with self.assertRaises(ValueError):
            evaluate(dict(cars=4))

    def test_civil_and_door_bounds(self):
        spans = self.reference["spans"]
        for row in spans.values():
            self.assertEqual(row["beams"]*row["stock_length_m"],3600)
            self.assertGreater(row["eccentric_footing_min_kpa"],0)
        self.assertGreater(spans["10"]["effective_strand_margin_kn_by_loss"]["0.3"],0)
        self.assertLess(spans["20"]["effective_strand_margin_kn_by_loss"]["0.3"],0)
        s = self.reference["selected_span_load_cases"]
        self.assertGreater(s["high"]["span_actions"]["highest_pad_reaction_kn"], s["low"]["span_actions"]["highest_pad_reaction_kn"])
        self.assertAlmostEqual(self.reference["interfaces"]["allocated_door_clear_margin_mm"],10)
        self.assertLess(self.reference["interfaces"]["aged_80pct_capacity_margin_kwh"],0)
        self.assertLess(self.reference["interfaces"]["brake_adhesion_at_0p08_margin"],0)

    def test_steel_linear_response_increases_with_load(self):
        screens = self.reference["structure"]["body_vertical"]
        self.assertGreater(screens["high"]["1.3"]["peak_section_stress_mpa"],screens["low"]["1.3"]["peak_section_stress_mpa"])
        self.assertAlmostEqual(screens["central"]["1.3"]["peak_section_stress_mpa"]/screens["central"]["1.0"]["peak_section_stress_mpa"],1.3,4)

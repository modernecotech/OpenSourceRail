import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from cities.Baghdad.engineering.simulation import corridor, vehicle_audit as audit


class VehicleAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.evaluate()

    def test_original_steel_bounds_and_axle_equilibrium(self):
        for state, loaded, axle in (("low", 165835.9582, 7018.55555),
                                    ("central", 198635.9582, 8707.487841666665),
                                    ("high", 246035.9582, 11213.737841666667)):
            case = self.result["mass_cases"][state]
            self.assertAlmostEqual(case["loaded_train_kg"], loaded)
            self.assertAlmostEqual(case["max_loaded_static_axle_kg"], axle)
            self.assertAlmostEqual(sum(a["loaded_kg"] for a in case["axles"].values()), loaded)
            self.assertAlmostEqual(sum(a["tare_kg"] for a in case["axles"].values()), case["tare_train_kg"])
            self.assertAlmostEqual(case["moment_balance_kg_m"], 0, places=8)
        self.assertTrue(all(row["installed_mass_kg"] is None for row in self.result["released_steel_bom"]))
        self.assertFalse(self.result["physical_accepted"])

    def test_independent_stop_high_load_exceeds_comparator(self):
        for state, expected_force, expected_stop in (("central", 14.3764, 379.9230),
                                                      ("high", 17.8070, 495.7459)):
            row = next(row for row in self.result["braking"][state] if row["downgrade_pct"] == 2
                       and row["coast_delay_s"] == 2 and row["wheel_adhesion_assumed"] == .08
                       and row["target_net_deceleration_m_s2"] == .6)
            rail = row["cases"]["none_wheel_brakes/1_rail_modules_out"]
            combined_fault = row["cases"]["one_out_wheel_brakes/1_rail_modules_out"]
            self.assertAlmostEqual(rail["required_force_per_available_module_kn"], expected_force, places=4)
            self.assertAlmostEqual(rail["stop_at_comparator"]["stop_distance_m"], expected_stop, places=4)
            self.assertAlmostEqual(rail["stop_at_target"]["stop_distance_m"], 386.9294, places=4)
            self.assertAlmostEqual(rail["stop_at_target"]["work_energy_residual_kwh"], 0, places=10)
            self.assertIsNone(rail["stop_wheel_only"]["stop_distance_m"])
            self.assertGreater(combined_fault["wheel_force_upper_bound_kn"], rail["wheel_force_upper_bound_kn"])
        self.assertIsNone(rail["target_stop_room_margin_m"])
        self.assertAlmostEqual(self.result["battery"]["end_of_life_margin_kwh"], -8.8)
        self.assertAlmostEqual(self.result["fit"]["doubled_loaded_distortion_margin_mm"], 2)
        self.assertLess(self.result["fit"]["passive_incremental_payload_cases"]["central"]["0.6"]
                        ["trial_40mm_stroke_margin_mm"], 0)
        high_traction = self.result["traction"]["high"]
        self.assertAlmostEqual(high_traction["min_driven_static_load_fraction"], .95705766)
        self.assertGreater(high_traction["layouts"][-2]["margin_kn"], 0)
        self.assertLess(high_traction["layouts"][-1]["margin_kn"], 0)

    def test_route_grade_changes_duty_and_train_length_remains_centred(self):
        route = corridor.evaluate({"cars": 3, "grade_pct": -1})
        child = audit.evaluate(cars=3, route=route, available_stop_m=500, overlap_m=25)
        self.assertEqual(child["inputs"]["grade_pct"], 1)
        self.assertEqual(child["physical"]["car_centres_train_x_m"], [-17.5, 0.0, 17.5])
        self.assertEqual(child["physical"]["length_m"], 52)
        self.assertEqual(child["candidate_id"], audit.evaluate(cars=3)["candidate_id"])
        self.assertNotEqual(child["duty_id"], audit.evaluate(cars=3)["duty_id"])
        row = child["braking"]["central"][-1]["cases"]["none_wheel_brakes/1_rail_modules_out"]
        self.assertAlmostEqual(row["target_stop_room_margin_m"], 475 - row["stop_at_target"]["stop_distance_m"])
        with self.assertRaisesRegex(ValueError, "different candidates"):
            audit.evaluate(cars=6, route=route)
        with self.assertRaisesRegex(ValueError, "different candidates"):
            audit.evaluate(cars=3, route=route, grade_pct=2)

    def test_claim_checks_identity_and_attachment_only(self):
        form = deepcopy(self.result["return_template"])
        form["kind"] = "synthetic-fixture"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.txt"
            path.write_text("synthetic test fixture")
            form["documents"][path.name] = dict(sha256=audit.sha(path.read_bytes()), issuer="Fixture", date="2026-11-24")
            form["returns"]["braking"] = dict(document=path.name, article_serial="FIXTURE", procedure_revision="TEST",
                                              witness="Synthetic fixture")
            result = audit.evaluate(evidence_return=form, evidence_directory=path.parent)["return_assessment"]
            self.assertEqual(result["claim"], "synthetic-fixture")
            self.assertFalse(result["physical_accepted"])
            with self.assertRaisesRegex(ValueError, "exact vehicle and duty"):
                audit.evaluate(cars=3, evidence_return=form, evidence_directory=path.parent)
            path.write_text("changed fixture")
            with self.assertRaisesRegex(ValueError, "Missing or changed"):
                audit.evaluate(evidence_return=form, evidence_directory=path.parent)
        json.dumps(self.result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()

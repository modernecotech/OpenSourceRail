"""Independent checks on Baghdad supplier mass and feed-voltage arithmetic."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from power_interface import build, load_bus, mass_form, mass_return, report


class PowerInterfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build()

    def test_reference_and_equipment_count(self):
        r = self.result
        self.assertEqual(r["load_basis"], "selected planning load")
        self.assertIsNone(r["mass"]["returned_tare_kg"])
        self.assertEqual(len(r["mass"]["missing_groups"]), 7)
        self.assertAlmostEqual(r["bare_frame_stock_kg_per_train"], 31177.086)
        self.assertAlmostEqual(r["traction_rating_mw"], 5.004002756)
        self.assertEqual(r["traction_and_supply_counts"]["powered_sections"], 114)
        self.assertEqual(report(r), (Path(__file__).parent / "SECTION-POWER.md").read_text())

    def test_mixed_identity_or_untraced_mass_rejected(self):
        baseline = self.result["basis"]
        form = mass_form(baseline)
        with self.assertRaises(ValueError):
            mass_return(form, {**baseline, "braced_revision": "other"})
        form["train_mass_groups"]["power_and_control"]["kg"] = 300
        with self.assertRaises(ValueError):
            mass_return(form, baseline)

    def test_complete_weight_substitution_and_partial_tare(self):
        form = mass_form(self.result["basis"])
        for row in form["train_mass_groups"].values():
            row.update(kg=30000, evidence="arithmetic fixture")
        payload = form["train_mass_groups"]["crowd_payload"]
        payload.update(kg=None, evidence=None)
        partial = mass_return(form, form["basis"])
        self.assertEqual(partial["returned_tare_kg"], 180000)
        self.assertIsNone(partial["returned_crowd_train_kg"])
        payload.update(kg=30000, evidence="test crowd fixture")
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "weights.json"
            path.write_text(json.dumps(form))
            changed = build(path)
        self.assertEqual(changed["load_basis"], "supplier return")
        self.assertAlmostEqual(changed["loaded_t"], 210)
        self.assertAlmostEqual(changed["axle_mean_t"], 8.75)
        self.assertAlmostEqual(changed["traction_rating_mw"] / self.result["traction_rating_mw"],
                               210 / self.result["reference_loaded_t"])
        self.assertLess(changed["section_cases"][0]["collector_kv"], self.result["section_cases"][0]["collector_kv"])
        self.assertNotEqual(changed["evaluation_id"], self.result["evaluation_id"])

    def test_symmetric_feeds_kirchhoff_and_pulse_energy(self):
        rows = self.result["section_cases"]
        self.assertEqual([row["status"] for row in rows], ["within voltage screen"] + ["below voltage screen"] * 3)
        self.assertAlmostEqual(rows[1]["collector_kv"], rows[2]["collector_kv"])
        for row in rows:
            branch_ka = row["branch_peak_ka"]
            self.assertAlmostEqual(row["collector_kv"] * row["feeds"] * branch_ka, row["peak_collector_mw"])
            self.assertAlmostEqual(1.5 - row["collector_kv"], branch_ka * (0.010 + (0.008 + 0.004) * 2.47))
            self.assertAlmostEqual(row["feeds"] * row["peak_source_input_mw_per_feed"] - row["peak_collector_mw"],
                                   row["peak_loop_loss_mw"])
            self.assertGreater(row["cycle_average_loop_loss_kw"], row["peak_loop_loss_mw"] * 1000 * 20/150)
            self.assertLess(row["branch_rms_ka"], branch_ka)

    def test_receiving_brake_energy_against_time_integration(self):
        b = self.result["braking_reception"]
        self.assertAlmostEqual(b["kinetic_kwh"], 0.5 * 201092 * 20**2 / 3.6e6)
        for row in b["cases"]:
            steps = 10000
            dt = b["duration_s"] / steps
            received = sum(min(row["sink_mw"], b["offered_peak_mw"] * (1 - (i + 0.5)/steps))
                           for i in range(steps)) * dt / 3.6
            self.assertAlmostEqual(received, row["potentially_received_kwh"], places=6)
            self.assertAlmostEqual(row["unreceived_kwh"] + received, b["offered_dc_kwh"], places=6)
        self.assertGreater(b["cases"][0]["unreceived_kwh"], 6)
        self.assertEqual(b["cases"][1]["unreceived_peak_mw"], 0)

    def test_transfer_limit_and_cost_break_even(self):
        self.assertIsNone(load_bus(1.5, 0.1, 6.0))
        self.assertEqual(load_bus(2, 1, 1), (1, 1))
        cost = self.result["cost"]
        self.assertAlmostEqual(cost["direct_one_off_upgrade_break_even_usd_m_per_site"] * 30 * 1.105 * 1.20,
                               cost["reference_30y_advantage_usd_m"])

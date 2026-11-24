"""Checks for the selection boundary on the fixed seven-line planning offer."""
import unittest

from cities.Baghdad.engineering import network_option_audit as audit


class NetworkOptionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.evaluate()

    def test_local_controls_are_bound_to_their_source(self):
        basis = self.report["basis"]
        cfg = audit.system.load(network="first")
        for path, entry in basis["inputs_by_toml_key"].items():
            value = cfg
            for key in path.split("."):
                value = value[key]
            self.assertEqual(entry["value"], value)
        self.assertEqual(basis["inputs_by_toml_key"]["vehicle.peak_headway_s"]["use"], "local_service_offer")
        self.assertIn("safety.independent_stop", basis["mandatory_obligations"])
        self.assertEqual(self.report["audit_id"], audit.system._id(
            {key: value for key, value in self.report.items() if key != "audit_id"}
        ))

    def test_priced_alternatives_remain_held(self):
        self.assertEqual(len(self.report["cases"]), 32)
        self.assertIsNone(self.report["selection_id"])
        for row in self.report["cases"]:
            self.assertFalse(row["selection_eligible"])
            self.assertEqual(row["declared_hard_screen"], "unknown")
            decision = row["engineering_and_delivery"]
            self.assertIsNone(decision["additional_yard_and_front_cost_usd"])
            self.assertEqual(decision["active_fleet_lower_bound_for_this_offer"], 208)
            self.assertFalse(decision["actual_crane_at_radius_verified"])
            self.assertAlmostEqual(decision["all_axles_driven_min_adhesion_for_declared_duty"], .095681, places=6)

    def test_buyer_discount_basis_keeps_assets_and_changes_the_price(self):
        alternative = audit.evaluate(.055)
        self.assertEqual(alternative["real_discount_rate"], .055)
        for old, row in zip(self.report["cases"], alternative["cases"]):
            self.assertEqual(old["physical_id"], row["physical_id"])
            self.assertLess(row["priced_30y_pv_usd_m"], old["priced_30y_pv_usd_m"])
            self.assertEqual(row["priced_30y_pv_usd_m"], row["pv_usd_m_by_real_discount_rate"]["0.055"])

    def test_discount_trial_reprices_the_same_assets(self):
        for row in self.report["cases"]:
            self.assertAlmostEqual(row["pv_usd_m_by_real_discount_rate"]["0.04"], row["priced_30y_pv_usd_m"])
        layout = {row["supply"]: row["pv_usd_m_by_real_discount_rate"] for row in self.report["cases"]
                  if row["span_m"] == 10 and row["pier"] == "separate"}
        self.assertAlmostEqual(layout["limited_conductor_battery"]["0.04"] - layout["overhead"]["0.04"], 6.62, places=2)
        self.assertAlmostEqual(layout["limited_conductor_battery"]["0.08"] - layout["overhead"]["0.08"], -34.51, places=2)


if __name__ == "__main__":
    unittest.main()

"""Check rate-based feeder sensitivities independently of solved duty receipts."""

from copy import deepcopy
import unittest

from . import audit_feeder_cost as costing, motion_power, scenario


class AuditFeederCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = motion_power.reference()

    def inputs(self, name, pv=1000):
        design = vars(motion_power.make_feeder(name, [0, 3990, 6400, 8200, 12145, 17450], 1.,
                                               self.reference, alignment_id="test alignment"))
        quantities = dict(grid_sites=len(design["sites"]), track_km=34.9)
        context = dict(feeder=design, alignment_id="test alignment", demand_evaluation_id="test demand",
                       vehicle_candidate_id="test train", vehicle_duty_id="test duty")
        operations = dict(working_day_completed=True, operated_annual_train_km=85, annual_completed_journeys=40,
                          annual_paid_journeys_proxy=30)
        prices = dict(inputs=context, quantities=quantities, cash={"profiles": {"base": {"priced_30y_pv_usd": pv}}},
                      operation_basis=operations,
                      source_sha256={"sourcing-estimate.json": scenario.sha(costing.PRICE_REGISTER.read_bytes()),
                                     "cities/Baghdad/system.toml": scenario.sha(costing.SYSTEM.read_bytes())})
        physical = dict(alignment_id=context["alignment_id"], feeder=design)
        rows = [dict(feeder_physical=physical, feeder_physical_id=scenario._id(physical), evaluation_id=case,
                     numerical_valid=valid, peak_site_ka=peak)
                for case, valid, peak in (("normal", True, 6.), ("high-mass", True, 8.), ("invalid", False, 100.))]
        return prices, rows

    def test_radial_quantities_use_corrected_track_and_rates(self):
        prices, rows = self.inputs("radial30")
        comparable, _ = self.inputs("paired6", pv=1200)
        original = deepcopy(prices)
        result = costing.evaluate(prices, rows, comparison=comparable)
        self.assertEqual(prices, original)
        self.assertEqual(result["quantities"]["dc_source_groups"], 30)
        self.assertEqual(result["quantities"]["outgoing_circuits"], 116)
        self.assertEqual(result["quantities"]["midpoint_ties"], 58)
        self.assertEqual(result["duty_proxy"]["governing_evaluation_id"], "high-mass")
        self.assertEqual(result["duty_proxy"]["dc_mw_pricing_proxy"], 12.)
        self.assertIsNone(result["duty_proxy"]["installed_nameplate_mw"])
        base = result["cases"]["base"]
        self.assertAlmostEqual(base["parts_usd"]["protected_positive_and_return_paths"], 34.9 * 1_050_000)
        self.assertAlmostEqual(base["parts_usd"]["railway_side_supply_sites_and_plant"], 30 * 10_000_000)
        self.assertAlmostEqual(base["rail_side_annual_upkeep_usd"], base["known_rail_side_direct_subtotal_usd"] * .01)
        self.assertEqual(result["priced_cash_break_even"]["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"], 200)
        comparable["operation_basis"]["annual_completed_journeys"] = 39
        unmatched = costing.evaluate(prices, rows, comparison=comparable)["priced_cash_break_even"]
        self.assertFalse(unmatched["achieved_service_comparable"])
        self.assertIsNone(unmatched["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"])
        self.assertIsNone(result["offsite_utility_usd"])
        self.assertIsNone(result["installed_package_usd"])
        self.assertIsNone(result["renewal_usd"])

    def test_paired_allowance_and_missing_rated_duty(self):
        prices, rows = self.inputs("paired6")
        result = costing.evaluate(prices, rows)
        self.assertEqual(result["quantities"]["branch_disconnect_and_test_points"], 80)
        self.assertAlmostEqual(result["conductor_proxy"]["conductance_factor"], 3)
        self.assertIsNone(result["conductor_proxy"]["installed_conductor_area_mm2"])
        self.assertLess(result["cases"]["low"]["known_rail_side_direct_subtotal_usd"],
                        result["cases"]["high"]["known_rail_side_direct_subtotal_usd"])
        missing = costing.evaluate(prices, rows[-1:])
        self.assertIsNone(missing["cases"]["base"]["parts_usd"]["railway_side_supply_sites_and_plant"])
        self.assertIsNone(missing["cases"]["base"]["rail_side_annual_upkeep_usd"])
        with self.assertRaisesRegex(ValueError, "exact physical feeder"):
            costing.evaluate(prices, [dict(rows[0], feeder_physical_id="wrong")])
        with self.assertRaisesRegex(ValueError, "finite"):
            costing.evaluate(prices, [dict(rows[0], peak_site_ka=float("inf"))])


if __name__ == "__main__":
    unittest.main()

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
                       vehicle_candidate_id="test train", vehicle_duty_id="test duty", civil_row_id="test girder")
        operations = dict(working_day_completed=True, operated_annual_train_km=85, annual_completed_journeys=40,
                          annual_paid_journeys_proxy=30)
        prices = dict(inputs=context, quantities=quantities, cash=dict(profiles={"base": {"priced_30y_pv_usd": pv}},
                      scope={"unpriced_lots_by_group": {}}, constant_currency="2026 USD", discount_rate_real=.04, service_start_year=4),
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
        screens = {"failed_equipment_layouts": [], "failed_operating_layouts": [], "unmatched_duties": []}
        result = costing.evaluate(prices, rows, comparison=comparable, operating_comparison=screens)
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
        rejected = costing.priced_cash_gap(prices, comparable, dict(screens, failed_equipment_layouts=["radial30"]))
        self.assertTrue(rejected["achieved_service_comparable"])
        self.assertIsNone(rejected["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"])
        incomparable = dict(screens, failed_operating_layouts=["radial30"], unmatched_duties=["combined"])
        gap = costing.priced_cash_gap(prices, comparable, incomparable)
        self.assertTrue(gap["ordinary_service_comparable"])
        self.assertFalse(gap["achieved_service_comparable"])
        self.assertIsNone(gap["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"])
        self.assertIsNone(costing.priced_cash_gap(prices, comparable, None)["achieved_service_comparable"])
        comparable["cash"]["service_start_year"] += 1
        delayed = costing.priced_cash_gap(prices, comparable, screens)
        self.assertFalse(delayed["matched_pricing_boundary"])
        self.assertIsNone(delayed["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"])
        comparable["cash"]["service_start_year"] -= 1
        prices["pricings"] = [dict(lot_id="feeder-renewal-radial-electronics", group="renewal-schedule",
                                    equipment_class="dc_source_groups", year=12, quantity=30,
                                    installed_population=30, replacement_exclusions=["annual maintenance"])]
        scoped = costing.priced_cash_gap(prices, comparable, screens)
        self.assertFalse(scoped["matched_pricing_boundary"])
        self.assertIsNone(scoped["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"])
        comparable["pricings"] = [dict(lot_id="feeder-renewal-paired-power-modules", group="renewal-schedule",
                                        equipment_class="dc_source_groups", year=12, quantity=6,
                                        installed_population=6, replacement_exclusions=["annual maintenance"])]
        equal_coverage = costing.priced_cash_gap(prices, comparable, screens)
        self.assertTrue(equal_coverage["matched_pricing_boundary"])
        self.assertEqual(equal_coverage["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"], 200)
        comparable["pricings"][0]["quantity"] = 3
        self.assertFalse(costing.priced_cash_gap(prices, comparable, screens)["matched_pricing_boundary"])
        comparable["pricings"][0]["quantity"] = 6
        comparable["pricings"][0]["year"] = 13
        self.assertFalse(costing.priced_cash_gap(prices, comparable, screens)["matched_pricing_boundary"])
        comparable["pricings"][0]["year"] = 12
        comparable["pricings"][0]["replacement_exclusions"] = ["annual maintenance", "site civil"]
        self.assertFalse(costing.priced_cash_gap(prices, comparable, screens)["matched_pricing_boundary"])
        prices.pop("pricings")
        comparable.pop("pricings")
        comparable["cash"]["scope"]["unpriced_lots_by_group"] = {"opening-direct": ["unpriced extra lot"]}
        gap = costing.priced_cash_gap(prices, comparable, screens)
        self.assertFalse(gap["matched_pricing_boundary"])
        self.assertIsNone(gap["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"])
        comparable["operation_basis"]["annual_completed_journeys"] = 39
        unmatched = costing.evaluate(prices, rows, comparison=comparable, operating_comparison=screens)["priced_cash_break_even"]
        self.assertFalse(unmatched["achieved_service_comparable"])
        self.assertIsNone(unmatched["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"])
        self.assertIsNone(result["offsite_utility_usd"])
        self.assertIsNone(result["installed_package_usd"])
        self.assertIsNone(result["renewal_usd"])

    def test_equal_normal_day_can_hide_an_unavailable_route_or_different_outage_load(self):
        layouts = ("paired6", "radial30")
        decisions = {layout: dict(assemblies={"feeder": layout}, operating_screen="passed",
                                  equipment_return_screen="unknown", complete_equipment_duty_screen="unknown")
                     for layout in layouts}
        rows = [dict(topology=layout, candidate_id=layout, condition=duty, completed=72, booked=72,
                     numerical_valid=True, served=7000) for duty in motion_power.CONDITIONS for layout in layouts]
        high = [row.copy() for row in rows if row["condition"] == "combined"]
        self.assertEqual(costing.compare_operating_duties(rows, high, decisions)["unmatched_duties"], [])
        decisions["paired6"]["complete_equipment_duty_screen"] = "fail"
        thermal_failed = costing.compare_operating_duties(rows, high, decisions)
        self.assertEqual(thermal_failed["failed_equipment_layouts"], ["paired6"])
        radial, _ = self.inputs("radial30")
        paired, _ = self.inputs("paired6", pv=1200)
        self.assertIsNone(costing.priced_cash_gap(radial, paired, thermal_failed)
                          ["extra_unpriced_pv_own_minus_other_for_equal_totals_usd"])
        decisions["paired6"]["complete_equipment_duty_screen"] = "unknown"
        for row in rows:
            if row["condition"] == "combined" and row["topology"] == "radial30":
                row.update(completed=0, served=0)
        high[0]["served"] -= 10
        decisions["radial30"]["operating_screen"] = "failed"
        actual = costing.compare_operating_duties(rows, high, decisions)
        self.assertEqual(actual, dict(unmatched_duties=["combined", "high_mass_combined"],
                                      failed_operating_layouts=["radial30"], failed_equipment_layouts=[]))
        with self.assertRaisesRegex(ValueError, "both physical layouts"):
            costing.compare_operating_duties(rows, high[:1], decisions)
        high[0]["candidate_id"] = "old feeder revision"
        with self.assertRaisesRegex(ValueError, "another physical design"):
            costing.compare_operating_duties(rows, high, decisions)

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

import unittest

from cities.Baghdad import airport_opening, operating_alternatives


class OperatingAlternativesTest(unittest.TestCase):
    def test_three_offers_preserve_scope_and_expose_unpriced_trial(self):
        record = operating_alternatives.compare(*airport_opening.opening_inputs())
        cases = record["cases"]
        airport = cases["airport_15_minute"]
        reduced = cases["airport_30_minute_trial"]
        urban = cases["urban_15_minute"]
        self.assertEqual(len({row["candidate_id"] for row in cases.values()}), 3)
        self.assertEqual(airport["normal_places_hour_direction"], urban["normal_places_hour_direction"])
        self.assertEqual(airport["annual_place_km"], 2 * reduced["annual_place_km"])
        self.assertEqual(airport["scheduled_trips_day"], 2 * reduced["scheduled_trips_day"])
        self.assertEqual(airport["station_count"], reduced["station_count"])
        self.assertEqual(reduced["fleet_sets"] - reduced["active_sets"], 3)
        self.assertTrue(reduced["terminal_and_block_screen"])
        self.assertFalse(reduced["terminal_conflicts"])
        self.assertIn("payroll exceeds", reduced["price_hold"])
        self.assertIsNone(reduced["annual_opex_usd_m"])
        self.assertEqual(reduced["illustrative_peak_load_cases"][-1]["remaining_places_hour_direction"], -700)
        for row in cases.values():
            self.assertIsNone(row["observed_peak_directional_load"])
            self.assertFalse(row["operating_authorisation"])
        self.assertFalse(record["investment_rankable"])

    def test_cost_sensitivity_preserves_reference_and_scales_only_variable_work(self):
        record = operating_alternatives.compare(*airport_opening.opening_inputs())
        result = record["airport_cost_sensitivity"]
        reference = result["cases"]["airport_15_minute"]
        reduced = result["cases"]["airport_30_minute_trial"]
        self.assertEqual(reduced["candidate_id"], record["cases"]["airport_30_minute_trial"]["candidate_id"])
        self.assertEqual(reduced["mileage_ratio_to_15_minute"], .5)
        self.assertEqual(reduced["retained_reference_payroll_usd_m"], reference["retained_reference_payroll_usd_m"])
        self.assertEqual(reduced["capital_if_all_six_sets_retained_usd_m"], reference["capital_usd_m"])
        self.assertAlmostEqual(reference["capital_usd_m"] - reduced["capital_usd_m"], 11.24448)
        for split, base in reference["annual_cost_cases"].items():
            trial = reduced["annual_cost_cases"][split]
            self.assertAlmostEqual(base["annual_opex_usd_m"], 9.7633342858)
            self.assertEqual(trial["fixed_payroll_and_upkeep_usd_m"], base["fixed_payroll_and_upkeep_usd_m"])
            self.assertAlmostEqual(trial["variable_electricity_usd_m"], base["variable_electricity_usd_m"] / 2)
            self.assertAlmostEqual(trial["variable_train_mileage_usd_m"], base["variable_train_mileage_usd_m"] / 2)
            self.assertLess(trial["annual_opex_usd_m"], base["annual_opex_usd_m"])
        self.assertIsNone(result["complete_opening_cost_usd_m"])

    def test_procurement_sensitivity_retains_site_bom_and_buyer_capital(self):
        record = operating_alternatives.compare(*airport_opening.opening_inputs())
        result = record["airport_procurement_cost_sensitivity"]
        reference = result["cases"]["airport_15_minute"]
        reduced = result["cases"]["airport_30_minute_trial"]
        self.assertEqual(reference["candidate_id"], result["source_packet_candidate_id"])
        self.assertNotEqual(reference["candidate_id"], reduced["candidate_id"])
        self.assertEqual(result["projected_bundle"]["grid_sites"], 30)
        self.assertEqual(result["fixed_opening_bom"]["dc_outgoing_breaker_circuits"]["quantity"], 116)
        self.assertIsNone(result["fixed_opening_bom"]["installed and tested rectifier cabinets"])
        self.assertAlmostEqual(reference["capital_usd_m"], 1124.321028464)
        self.assertAlmostEqual(reduced["capital_usd_m"], 1113.076548464)
        self.assertEqual(reduced["capital_scopes_usd_m"]["extra-haul"], reference["capital_scopes_usd_m"]["extra-haul"])
        midpoint = "half_train_nonlabour_variable"
        self.assertAlmostEqual(reference["annual_cost_cases"][midpoint]["annual_opex_usd_m"], 13.090963124)
        self.assertAlmostEqual(reduced["annual_cost_cases"][midpoint]["annual_opex_usd_m"], 12.250110063)
        self.assertFalse(result["requalified_feeder"])

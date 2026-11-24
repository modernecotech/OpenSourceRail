"""Regression checks for the independently dimensioned straight-viaduct trials."""
from math import ceil
import unittest

from cities.Baghdad.engineering.mechanical.civil import family_comparison as family


class ViaductFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = family.evaluate()

    def test_inventory_and_datum(self):
        rows = self.study["rows"]
        reference = rows[0]
        self.assertAlmostEqual(reference["section"]["volume_m3"], 13.404)
        self.assertEqual(reference["actions"]["strand_count"], 12)
        self.assertEqual(self.study["axle_count"], 24)
        self.assertEqual({r["span_m"] for r in rows}, {10, 15, 20, 25, 30})
        self.assertEqual(len({r["physical_id"] for r in rows}), len(rows))
        for row in rows:
            bays = ceil(12000/row["span_m"])
            self.assertEqual(row["supports"], (bays+1) * (1 if row["shared_pier"] else 2))
            self.assertEqual(row["bearings"], 8*bays)
            self.assertEqual(row["haul_trips"], row["beams"]*row["actions"]["segments"])
            self.assertFalse(row["eligible_for_selection"])
            self.assertIsNone(row["complete_installed_usd"])

    def test_signed_handling_screen_and_stressing_stage(self):
        for row in self.study["rows"]:
            a = row["actions"]
            self.assertLess(a["handling_moments_knm"][0], 0)
            self.assertLess(a["handling_moments_knm"][-1], 0)
            self.assertGreater(a["handling_moments_knm"][1], 0)
            self.assertEqual(a["checks"]["positive_bearing_reactions"],
                             a["minimum_bearing_independent_envelopes_kn"] > 0)
            self.assertLessEqual(row["support"]["peak_soil_kpa"], 200)
            self.assertGreaterEqual(row["support"]["minimum_soil_kpa"], 0)
            self.assertGreaterEqual(row["support"]["cap_outer_pad_edge_margin_m"], .25 - 1e-9)
            self.assertEqual(row["checks"]["independent_footings_clear"],
                             row["shared_pier"] or row["support"]["footing_width_m"] < 4.50)
            if a["segments"] == 2:
                self.assertFalse(a["checks"]["release_fibre_min"])
                self.assertGreater(a["tower_reaction_two_halves_kn"], 0)
                self.assertEqual(a["straight_handling_strands"], 0)
                self.assertIn("temporary_tower_and_joint", row["priced_cases"]["base"]["installed_breakdown_usd"])
            if row["span_m"] == 30:
                self.assertFalse(a["checks"]["lift_fibre_min"])
        self.assertEqual(family.markdown(self.study), (family.HERE/"SPAN-FAMILIES.md").read_text())

    def test_prices_and_whole_life_boundary(self):
        for row in self.study["rows"]:
            prices = row["priced_cases"]
            self.assertLess(prices["low"]["installed_usd"], prices["base"]["installed_usd"])
            self.assertLess(prices["base"]["installed_usd"], prices["high"]["installed_usd"])
            base = prices["base"]
            self.assertAlmostEqual(sum(base["installed_breakdown_usd"].values()), base["installed_usd"])
            expected = base["installed_usd"] + sum(base["annual_inspection_usd"]/(1.04**y) for y in range(1, 31))
            expected += base["year20_bearings_usd"]/1.04**20
            self.assertAlmostEqual(expected, base["lifecycle_pv_usd"], places=5)
            soil = row["soil_sensitivity"]
            self.assertGreaterEqual(soil["150"]["footing_width_m"], soil["250"]["footing_width_m"])
            self.assertEqual(soil["200"]["installed_usd_per_km"], base["installed_usd"]/12)

    def test_upstream_inputs_and_partial_end_bays(self):
        changed = family.evaluate(route_km=.101, cars=3, material="hybrid", soil_kpa=150)
        self.assertNotEqual(changed["evaluation_id"], self.study["evaluation_id"])
        self.assertLess(changed["passenger_train_kg"], self.study["passenger_train_kg"])
        self.assertEqual(changed["axle_count"], 12)
        self.assertEqual(changed["rows"][0]["beams"], 22)
        self.assertEqual(changed["rows"][0]["closure_bay_m"], 1.)
        self.assertEqual(changed["rows"][0]["ordered_excess_length_per_track_m"], 9.)
        self.assertFalse(changed["rows"][0]["checks"]["full_length_standard_bays"])
        for row in changed["rows"]:
            self.assertLessEqual(row["support"]["peak_soil_kpa"], 150)
        with self.assertRaises(ValueError):
            family.evaluate(route_km=0)

    def test_decimal_route_at_bay_boundary(self):
        for route, bays, closure in [(8.06, 403, None), ("8.060000000000000001", 404, 1e-15)]:
            result = family.evaluate(route_km=route)
            row = next(r for r in result["rows"] if r["span_m"] == 20)
            self.assertEqual(row["beams"], 2*bays)
            self.assertEqual(row["closure_bay_m"], closure)
            self.assertEqual(row["checks"]["full_length_standard_bays"], closure is None)
            if closure is None:
                self.assertEqual(row["ordered_excess_length_per_track_m"], 0)

    def test_quotation_leaders_depend_on_rates_and_available_crane(self):
        open_crane = family.evaluate(route_km=18, soil_kpa=150)
        capped = family.evaluate(route_km=18, soil_kpa=150, crane_limit_t=60)
        self.assertIn("15m U", open_crane["quotation_leaders"]["low"]["label"])
        self.assertIn("20m U", open_crane["quotation_leaders"]["base"]["label"])
        self.assertIn("15m U", capped["quotation_leaders"]["base"]["label"])
        self.assertGreater(open_crane["passing_trial_count"], capped["passing_trial_count"])
        for case, quote in capped["quotation_leaders"].items():
            row = next(r for r in capped["rows"] if r["physical_id"] == quote["physical_id"])
            self.assertTrue(all(row["checks"].values()))
            self.assertLessEqual(row["actions"]["chart_class_t_at_12m"], 60)
            self.assertEqual(row["priced_cases"][case]["lifecycle_pv_usd"], quote["lifecycle_pv_usd"])
        self.assertIsNone(capped["physical_selection"])

    def test_route_with_only_unresolved_closures_has_no_quotation_leader(self):
        data = family.evaluate(route_km=12.003)
        self.assertEqual(data["passing_trial_count"], 0)
        self.assertTrue(all(q is None for q in data["quotation_leaders"].values()))
        self.assertIn("No trial passes all checks", family.markdown(data))


if __name__ == "__main__":
    unittest.main()

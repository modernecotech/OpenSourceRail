"""Regression checks for the independently dimensioned straight-viaduct trials."""
from math import ceil
import unittest
from unittest.mock import patch

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

    def test_actual_hook_demand_independent_of_price_band(self):
        capacity = 95.5
        candidate = family.evaluate(crane_limit_t=capacity)
        for row in candidate["rows"]:
            self.assertEqual(row["checks"]["available_crane"], row["actions"]["chart_demand_t"] <= capacity)
        self.assertTrue(any(r["checks"]["available_crane"] and r["actions"]["chart_class_t_at_12m"] > capacity
                            for r in candidate["rows"]))
        self.assertIsNone(self.study["crane_limit_t_at_12m"])
        self.assertTrue(all("available_crane" not in r["checks"] for r in self.study["rows"]))
        for capacity in (0, -7, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                family.evaluate(crane_limit_t=capacity)

    def test_supplied_chart_point_at_other_radius_has_no_matched_rate(self):
        at_reference = family.evaluate(crane_limit_t=95.5)
        at_site = family.evaluate(crane_limit_t=95.5, lift_radius_m=18.25)
        self.assertEqual(at_reference["crane_limit_t_at_12m"], 95.5)
        self.assertIsNone(at_site["crane_limit_t_at_12m"])
        self.assertEqual(at_site["crane_limit_t"], 95.5)
        self.assertEqual(at_site["lift_radius_m"], 18.25)
        self.assertNotEqual(at_site["evaluation_id"], at_reference["evaluation_id"])
        self.assertEqual(at_site["passing_trial_count"], at_reference["passing_trial_count"])
        self.assertEqual(at_site["priced_trial_count"], 0)
        self.assertTrue(all(q is None for q in at_site["quotation_leaders"].values()))
        for site, reference in zip(at_site["rows"], at_reference["rows"], strict=True):
            self.assertEqual(site["physical_id"], reference["physical_id"])
            self.assertEqual(site["actions"]["chart_demand_t"], reference["actions"]["chart_demand_t"])
            self.assertEqual(site["checks"]["available_crane"], reference["checks"]["available_crane"])
            self.assertIsNone(site["matched_crane_price_class_t"])
            self.assertIsNone(site["traffic_shifts"])
            self.assertIn("18.25 m", site["pricing_hold"])
        self.assertIn("95.5 t of available capacity at 18.25 m", family.markdown(at_site))
        for radius in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                family.evaluate(lift_radius_m=radius)

    def test_higher_demand_remains_an_unpriced_lift_trial(self):
        with patch.dict(family.TRIALS, rigging_t=200):
            result = family.evaluate(crane_limit_t=510.6)
            text = family.markdown(result)
        self.assertGreater(result["passing_trial_count"], 0)
        self.assertEqual(result["priced_trial_count"], 0)
        self.assertEqual(result["priced_passing_trial_count"], 0)
        self.assertIsNone(result["quotation_leaders"]["base"])
        self.assertIn("Passing trials need an erection quote", text)
        for row in result["rows"]:
            self.assertTrue(row["checks"]["available_crane"])
            self.assertIsNone(row["actions"]["chart_class_t_at_12m"])
            self.assertIsNone(row["traffic_shifts"])
            self.assertTrue(row["pricing_hold"])

    def test_entered_soil_and_unresolved_foundation(self):
        ordinary = family.evaluate(route_km=1500, soil_kpa=175.5)
        self.assertEqual(ordinary["soil_kpa"], 175.5)
        self.assertGreater(ordinary["priced_passing_trial_count"], 0)
        for row in ordinary["rows"]:
            self.assertLessEqual(row["support"]["peak_soil_kpa"], 175.5)
            self.assertEqual(set(row["soil_sensitivity"]), {"150", "200", "250"})
        weak = family.evaluate(soil_kpa=.01)
        self.assertEqual(weak["unresolved_foundation_count"], len(weak["rows"]))
        self.assertEqual(weak["priced_trial_count"], 0)
        self.assertEqual(weak["passing_trial_count"], 0)
        self.assertTrue(all(q is None for q in weak["quotation_leaders"].values()))
        self.assertIn("Site foundation design required", family.markdown(weak))
        for row in weak["rows"]:
            self.assertIsNone(row["support"]["footing_width_m"])
            self.assertIsNone(row["support"]["independent_footings_clear"])
            self.assertIsNone(row["support"]["peak_soil_kpa"])
            self.assertIn("foundation", row["pricing_hold"])
            self.assertEqual(row["actions"], next(r["actions"] for r in ordinary["rows"] if r["label"] == row["label"]))

    def test_route_and_soil_numeric_domain(self):
        for route in ("1e10000000", "1e-10000000", "NaN"):
            with self.assertRaises(ValueError):
                family.evaluate(route_km=route)
        for soil in (0, -10, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                family.evaluate(soil_kpa=soil)

    def test_scoped_erection_quote_and_partial_subtotals(self):
        reference = next(r for r in self.study["rows"] if r["label"] == "20m U 1.55m / shared")
        quantity = reference["placements"]
        quote = dict(supplier="Trial supplier", offer_id="A", physical_id=reference["physical_id"], placements=quantity,
                     lift_radius_m=18.25, working_load_t=95.5, haul_usd_per_placement=1200,
                     erection_usd_per_placement=3500, placements_per_shift=3)
        # The faster B costs more per lift, but pays for fewer closure shifts.
        faster = dict(quote, supplier="Second trial supplier", offer_id="B", erection_usd_per_placement=3700,
                      placements_per_shift=6)
        wrong_radius = dict(quote, offer_id="wrong radius", lift_radius_m=12)
        low_chart = dict(quote, offer_id="short chart", working_load_t=30)
        wrong_count = dict(quote, offer_id="different lot", placements=quantity+1)
        result = family.evaluate(lift_radius_m=18.25, erection_offers=[quote, faster, low_chart, wrong_radius, wrong_count])
        self.assertEqual(result["priced_trial_count"], 1)
        self.assertEqual(result["priced_passing_trial_count"], 1)
        self.assertIsNone(result["physical_selection"])
        self.assertEqual({q["offer"]["offer_id"]: q["status"] for q in result["erection_offers"]},
                         {"A":"matched", "B":"matched", "wrong radius":"different lift radius",
                          "different lot":"different order quantity", "short chart":"offered working load below hook demand"})
        for row in result["rows"]:
            if row["physical_id"] == reference["physical_id"]:
                self.assertEqual(row["priced_cases"]["low"]["offer_id"], "A")
                self.assertEqual(row["traffic_shifts"], quantity//6)
                actual = row["priced_cases"]["base"]
                self.assertEqual(actual["offer_id"], "B")
                self.assertEqual(actual["logistics_source"], "contractor offer")
                self.assertEqual(actual["installed_breakdown_usd"]["haul"], 1200*quantity)
                self.assertEqual(actual["installed_breakdown_usd"]["erection"], 3700*quantity)
                self.assertEqual(actual["installed_breakdown_usd"]["road_occupation"], quantity//6*2400)
                self.assertIsNone(row["soil_sensitivity"]["150"]["installed_usd_per_km"])
                self.assertAlmostEqual(row["soil_sensitivity"]["200"]["installed_usd_per_km"], actual["installed_usd"]/12)
            else:
                self.assertFalse(row["priced_cases"])
                partial = row["partial_cost_cases"]["base"]
                self.assertIsNone(partial["installed_usd"])
                self.assertIsNone(partial["lifecycle_pv_usd"])
                self.assertEqual(partial["missing_cost_scope"], ["haul", "erection", "road occupation"])
                for key in ("materials", "fabrication", "forms", "supports"):
                    self.assertGreater(partial["installed_breakdown_usd"][key], 0)
                self.assertEqual(partial["known_installed_subtotal_usd"], sum(partial["installed_breakdown_usd"].values()))
        self.assertEqual(result["quotation_leaders"]["base"]["offer_id"], "B")


if __name__ == "__main__":
    unittest.main()

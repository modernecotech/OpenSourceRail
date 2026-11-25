"""Exercise Airport site allowance boundaries and provenance."""

from copy import deepcopy
import unittest

from cities.Baghdad.engineering.simulation import airport_alignment, site_costs


def profile():
    result = {
        "alignment_id": "reviewed-airport-route",
        "route_m": 46.0,
        "samples": [
            dict(chainage_m=0, soffit_height_m=6.25, clay_pct=31.0, water_occurrence_pct=0),
            dict(chainage_m=18, soffit_height_m=9.25, clay_pct=33.0, water_occurrence_pct=41),
            dict(chainage_m=40, soffit_height_m=7.25, clay_pct=52.0, water_occurrence_pct=4),
            dict(chainage_m=46, soffit_height_m=6.25, clay_pct=None, water_occurrence_pct=None),
        ],
    }
    return {**result, "site_profile_id": airport_alignment.identity(result)}


def girder():
    breakup = dict(materials=200, supports=300, haul=500, forms=100, common_elevated_scope=800)
    return dict(
        physical_id="twenty-metre-shared-pier",
        route_km=.046, span_m=20, full_standard_bays=2, closure_bay_m=6,
        shared_pier=True, supports=4,
        quantities=dict(standard_supports=3),
        support=dict(cap_depth_m=1.25, concrete_m3=65, footing_width_m=4, footing_depth_m=1),
        governing_bent_load="high",
        load_case_actions={"high": dict(bearing_offset_m=.8, dead_track_reaction_kn=340,
                                       dynamic_live_reaction_kn=300, end_torque_knm=5)},
        standard_only_cost_cases={name: dict(installed_breakdown_usd=breakup, installed_usd=1900)
                                  for name in site_costs.CASES},
    )


class SiteAllowanceTest(unittest.TestCase):
    def test_site_cost_uses_matching_support_and_explicit_closure_quantities(self):
        result = site_costs.evaluate(profile(), girder())
        self.assertEqual([row["chainage_m"] for row in result["support_profile"]], [0, 20, 40, 46])
        self.assertTrue(result["support_profile"][-1]["closure_end_support"])
        self.assertAlmostEqual(result["support_profile"][1]["trial_column_height_m"], 8 - 2 * 2 / 22)
        self.assertEqual(result["support_profile"][1]["water_occurrence_pct"], 41)
        self.assertEqual(result["quantities"]["supports_without_water_value"], 1)
        self.assertEqual(result["quantities"]["supports_without_clay_value"], 1)
        self.assertEqual(result["quantities"]["supports_with_repeated_historical_water"], 1)
        self.assertGreater(result["quantities"]["extra_column_concrete_m3"], 0)
        footings = result["footing_sensitivity"]["resized_footings"]
        self.assertLessEqual(footings["low"]["extra_pad_concrete_m3"], footings["high"]["extra_pad_concrete_m3"])
        self.assertEqual(footings["base"]["unresolved_supports"], 0)
        self.assertEqual(result["lots"]["gis-end-closure-allowance"]["usd"]["base"], 500)
        self.assertEqual(result["cases"]["high"]["trial_shaft_support_chainages_m"], [20, 40])
        self.assertLess(result["cases"]["low"]["foundation_allowance_usd"],
                        result["cases"]["high"]["foundation_allowance_usd"])
        self.assertEqual(result["cases"]["base"]["opening_site_known_subtotal_usd"],
                         sum(lot["usd"]["base"] for lot in result["lots"].values()))

    def test_material_proxy_does_not_change_bearing_scenario(self):
        baseline = site_costs.evaluate(profile(), girder())
        changed = deepcopy(profile())
        for row in changed["samples"]:
            row.update(clay_pct=100, water_occurrence_pct=100)
        del changed["site_profile_id"]
        changed["site_profile_id"] = airport_alignment.identity(changed)
        comparison = site_costs.evaluate(changed, girder())
        self.assertEqual(comparison["footing_sensitivity"]["failed_support_count_by_assumed_bearing_kpa"],
                         baseline["footing_sensitivity"]["failed_support_count_by_assumed_bearing_kpa"])
        self.assertGreater(comparison["cases"]["base"]["trial_shaft_support_count"],
                           baseline["cases"]["base"]["trial_shaft_support_count"])
        self.assertEqual(comparison["footing_sensitivity"]["resized_footings"]["base"]["supports_enlarged"], 0)

    def test_reject_changed_profile_and_mixed_route(self):
        edited = profile()
        edited["samples"][0]["soffit_height_m"] = 9
        with self.assertRaisesRegex(ValueError, "profile identity"):
            site_costs.evaluate(edited, girder())

        wrong_route = {**girder(), "route_km": .047}
        with self.assertRaisesRegex(ValueError, "different route lengths"):
            site_costs.evaluate(profile(), wrong_route)

        mixed_stock_order = {**girder(), "supports": 5}
        with self.assertRaisesRegex(ValueError, "support population"):
            site_costs.evaluate(profile(), mixed_stock_order)

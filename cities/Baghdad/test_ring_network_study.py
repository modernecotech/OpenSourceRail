"""Regression checks for the comparison tiers used in the ring layout study."""

import unittest

from .ring_network_study import _pick


BASE = {
    "route_km": 730., "lines": 34, "walk_1200_pct": 73.5,
    "households_two_changes_pct": 70.1, "wide_trips_pct": 57.9, "wide_two_changes_pct": 46.1,
    "parallel_pair_km": 17., "direct_routes": ["C1", "M01"],
}


class RingNetworkStudyTests(unittest.TestCase):
    def test_equivalent_reach_uses_less_parallel_route(self):
        summary = {"wider": BASE, "new_axis": BASE | {"parallel_pair_km": 26., "wide_two_changes_pct": 47.8},
                   "new_axis_with_cut": BASE | {"parallel_pair_km": 22., "wide_two_changes_pct": 47.6,
                                                "direct_routes": ["C1", "M01", "G09"]}}
        revisions = {key: {"changed_alignment": key != "wider"} for key in summary}
        selected, tier = _pick(summary, revisions)
        self.assertEqual(selected, "new_axis_with_cut")
        self.assertEqual(tier["basis"], "matched kilometres, route count and access")

    def test_station_only_changes_do_not_become_a_route_redesign(self):
        summary = {"wider": BASE, "stations": BASE | {"wide_trips_pct": 63.}, "routes": BASE}
        revisions = {"stations": {"changed_alignment": False}, "routes": {"changed_alignment": True}}
        self.assertEqual(_pick(summary, revisions)[0], "routes")

    def test_fallback_for_unmatched_access_is_recorded(self):
        summary = {"wider": BASE, "routes": BASE | {"walk_1200_pct": 72.}}
        revisions = {"routes": {"changed_alignment": True}}
        self.assertEqual(_pick(summary, revisions)[1]["basis"], "matched kilometres and route count")


if __name__ == "__main__":
    unittest.main()

"""Check the wider orbital against the retained Baghdad network and GIS data."""

import unittest

from . import holistic_network as network
from . import ring_corridors, spaced_ring_geometry, wider_ring_geometry


class WiderRingGeometryTests(unittest.TestCase):
    def test_wider_ring_and_retained_outer_alignment(self):
        graph = network.walking_graph()
        context = network.read(network.INPUTS[-1])
        published = network.read(network.CITY / "baghdad-network.json")["network"]
        outer, _ = ring_corridors.evaluate_rings(published, graph, context, include_inner=False)
        result = wider_ring_geometry.evaluate(outer, graph, context)
        selected = result["selected"]
        self.assertIsNotNone(selected)
        self.assertGreaterEqual(selected["one_way_km"], 22.)
        self.assertLessEqual(selected["one_way_km"], 23.)
        self.assertGreaterEqual(selected["enclosed_area_km2"], 9.11)
        self.assertGreaterEqual(selected["minimum_rotated_footprint_width_km"], 3.07)
        self.assertGreaterEqual(selected["minimum_ring_separation_m"], 5_000.)
        self.assertEqual(selected["tunnels"], 0)
        self.assertGreaterEqual(len(selected["screened_spokes"]), 2)
        self.assertEqual({row["bank"] for row in selected["screened_transfer_sites"]}, {"east", "west"})
        alternative = result["connectivity_alternative"]
        self.assertIsNotNone(alternative)
        self.assertGreaterEqual(alternative["minimum_ring_separation_m"], 5_000.)
        self.assertGreaterEqual(len(alternative["screened_spokes"]), 3)
        self.assertGreaterEqual(len(alternative["screened_transfer_sites"]), 7)
        self.assertLessEqual(len(result["checked_candidates"]), wider_ring_geometry.MAX_TRANSFER_TRIALS)
        revised, evidence = spaced_ring_geometry.insert(outer, selected, graph, context)
        self.assertEqual(revised["lines"]["M09"], outer["lines"]["M09"])
        self.assertGreaterEqual(evidence["minimum_ring_separation_m"], 5_000.)
        self.assertEqual(network.validate(revised), revised["topology"])
        self.assertFalse(revised["physical_accepted"])

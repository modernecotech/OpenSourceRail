"""Check compact Baghdad orbital geometry and retained-network interfaces."""

from copy import deepcopy
import unittest

import numpy as np
from shapely.geometry import Point, Polygon

from . import holistic_network, ring_corridors, spaced_ring_geometry


class SpacedRingGeometryTests(unittest.TestCase):
    def test_full_segment_clearance_detects_a_gap_that_vertex_checks_miss(self):
        metres = holistic_network.LOCAL_METRES
        outline = [(0, 0), (10_000, 0), (10_000, 10_000), (5_000, 5_000), (0, 10_000), (0, 0)]
        sampled = [(2_000, 4_000), (8_000, 4_000), (8_000, 2_000), (2_000, 2_000), (2_000, 4_000)]
        outer = {"loop": True, "geometry": (np.asarray(outline) / metres).tolist()}
        inner = (np.asarray(sampled) / metres).tolist()
        result = spaced_ring_geometry.separation(outer, inner)
        self.assertAlmostEqual(result["minimum_ring_separation_m"], 1_000.)
        boundary = Polygon(outline).boundary
        self.assertGreater(min(boundary.distance(Point(point)) for point in sampled), 1_000.)
        np.testing.assert_allclose(np.asarray(result["nearest_inner_coordinates"]) * metres, [5_000, 4_000])

    def test_compact_ring_and_actual_mapped_interchanges(self):
        h = holistic_network
        graph = h.walking_graph()
        context = h.read(h.INPUTS[-1])
        published = h.read(h.CITY / "baghdad-network.json")["network"]
        outer, _ = ring_corridors.evaluate_rings(
            published, graph, context, retained=h.evaluate(graph), include_inner=False,
        )
        saved = deepcopy(outer)
        result = spaced_ring_geometry.evaluate_geometry(outer["lines"]["M09"], outer, context, walking_graph=graph)
        selected = result["selected"]
        self.assertAlmostEqual(selected["one_way_km"], 11.3288993574)
        self.assertAlmostEqual(selected["minimum_ring_separation_m"], 6919.3982248494)
        self.assertEqual(selected["bridges"], ["14 July Bridge", "Al-Sinak Bridge"])
        self.assertEqual(selected["screened_spokes"], ["C1", "M02"])
        self.assertEqual(result["one_bank"]["topology"], "one-bank")
        self.assertFalse(result["one_bank"]["passes_connectivity_screen"])
        self.assertTrue(any(row["one_way_km"] < selected["one_way_km"] and not row["passes_connectivity_screen"]
                            for row in result["bridge_pairs"]))
        self.assertTrue(any(row["one_way_km"] > selected["one_way_km"] and row["passes_connectivity_screen"]
                            for row in result["bridge_pairs"]))
        revised, evidence = spaced_ring_geometry.insert(outer, selected, graph, context)
        self.assertEqual(outer, saved)
        self.assertEqual(outer["lines"]["M09"], revised["lines"]["M09"])
        self.assertEqual(evidence["transfers_by_bank"], {"east": 2, "west": 2})
        self.assertEqual(evidence["direct_spokes_between_rings"], ["C1", "M02"])
        self.assertEqual(evidence["tunnels"], 0)
        self.assertGreaterEqual(evidence["minimum_ring_separation_m"], 5_000.)
        self.assertEqual(h.validate(revised), revised["topology"])
        self.assertFalse(revised["physical_accepted"])

"""Check the ring layouts against the retained Baghdad passenger geography."""

from copy import deepcopy
import unittest

import numpy as np
from shapely.geometry import Point

from . import holistic_network, ring_corridors


class RingCorridorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = holistic_network.walking_graph()
        cls.context = holistic_network.read(holistic_network.INPUTS[-1])
        cls.retained = holistic_network.evaluate(cls.graph)
        cls.baseline = holistic_network.read(holistic_network.CITY / "baghdad-network.json")["network"]

    def test_inner_only_keeps_current_outer_arc_and_walking_paths(self):
        revised, evidence = ring_corridors.inner_only(self.baseline, self.graph, self.context)
        self.assertEqual(evidence["ring_ids"], ["M15"])
        self.assertEqual(revised["lines"]["M09"], self.baseline["lines"]["M09"])
        self.assertEqual(revised["station_site_links"], self.baseline["station_site_links"])
        self.assertAlmostEqual(evidence["route_km_added"], 41.12880669)
        self.assertEqual(holistic_network.validate(revised), revised["topology"])

    def test_ring_options_preserve_current_network_and_restore_real_geometry(self):
        saved = deepcopy(self.baseline)
        one, one_evidence = ring_corridors.evaluate_rings(
            self.baseline, self.graph, self.context, include_inner=False, retained=self.retained,
        )
        two, two_evidence = ring_corridors.evaluate_rings(
            self.baseline, self.graph, self.context, retained=self.retained,
        )

        self.assertEqual(self.baseline, saved)
        self.assertEqual(one_evidence["ring_ids"], ["M09"])
        self.assertEqual(two_evidence["ring_ids"], ["M09", "M15"])
        self.assertFalse(self.baseline["lines"]["M09"]["loop"])
        self.assertAlmostEqual(one["lines"]["M09"]["one_way_km"], 97.75197749)
        self.assertAlmostEqual(one_evidence["route_km_added"], 28.66645469)
        self.assertEqual(len(one_evidence["outer_restoration"]["restored_station_ids"]), 7)
        self.assertEqual(one["lines"]["M09"], two["lines"]["M09"])
        self.assertAlmostEqual(two_evidence["route_km_added"] - one_evidence["route_km_added"], 41.12880669)
        self.assertEqual(one["station_site_links"], self.baseline["station_site_links"])
        self.assertEqual(two["station_site_links"], self.baseline["station_site_links"])
        self.assertTrue(two_evidence["outer_gis_context"]["mapped_water_crossings"])
        self.assertTrue(two_evidence["inner_road_screen"]["mapped_water_crossings"])

        anchor = Point(np.array(two_evidence["nesting"]["common_enclosed_anchor"]) * holistic_network.LOCAL_METRES)
        self.assertEqual(two_evidence["nesting"]["common_enclosed_anchor_basis"], "Mansour mapped station")
        self.assertGreater(two_evidence["nesting"]["minimum_ring_separation_m"], 600)
        self.assertTrue(two_evidence["direct_spokes_between_rings"])
        for code, evidence in two_evidence["rings"].items():
            self.assertTrue(ring_corridors._ring_polygon(two["lines"][code]).contains(anchor))
            for interchange in evidence["interchanges"]:
                stop = interchange["station_id"]
                self.assertIn(code, interchange["lines"])
                self.assertGreater(len(interchange["lines"]), 1)
                self.assertIn(stop, two["lines"][code]["station_ids"])
                self.assertEqual(set(interchange["lines"]), set(two["stations"][stop]["lines"]))
        self.assertEqual(holistic_network.validate(two), two["topology"])
        self.assertFalse(two["physical_accepted"])
        self.assertFalse(two["operating_timetable_validated"])

"""Check that junction sites preserve rail routes and useful walking coverage."""

from copy import deepcopy
import unittest

import numpy as np

from . import central_access, central_junction_sites, holistic_access
from .test_network_station_sites import EMPTY_WATER, crossing_fixture, point, streets


class CentralJunctionSitesTests(unittest.TestCase):
    def test_merge_at_the_actual_crossing_with_two_way_walking(self):
        base = crossing_fixture(a_call=(600, 0), b_call=(1000, 150))
        graph = streets([(600, 0), (1000, 0), (1000, 150)],
                        [(0, 1, 400), (1, 0, 400), (1, 2, 150), (2, 1, 150)])
        revised, audit = central_junction_sites.consolidate(base, graph, EMPTY_WATER)
        action, = audit["actions"]
        self.assertEqual(action["platforms"]["A"]["coordinates"], point(1000, 0))
        self.assertAlmostEqual(action["platforms"]["B"]["chainage_km"], 1)
        self.assertEqual(action["source_access"]["A1"]["walks_m"], [400, 400])
        self.assertEqual(action["source_access"]["B1"]["walks_m"], [150, 150])
        self.assertEqual(revised["stations"]["A1"]["lines"], ["A", "B"])
        self.assertEqual(revised["lines"]["A"]["geometry"], base["lines"]["A"]["geometry"])

    def test_preserve_named_control_and_link_separate_platforms(self):
        base = crossing_fixture()
        original = deepcopy(base)
        graph = streets([(900, 0), (1000, 0), (1000, 75)],
                        [(0, 1, 100), (1, 0, 100), (1, 2, 75), (2, 1, 75)])
        revised, audit = central_junction_sites.consolidate(base, graph, EMPTY_WATER,
                                                           protected_stations=("A1",))
        self.assertFalse(audit["actions"])
        link, = revised["station_site_links"]
        self.assertEqual(link["station_ids"], ["A1", "B1"])
        self.assertEqual(link["walks_m"], [175, 175])
        self.assertEqual(base, original)

    def test_keep_call_with_additional_population_at_1300_m(self):
        base = crossing_fixture(a_call=(600, 0), b_call=(1000, 150))
        graph = streets([(600, 0), (1000, 0), (1000, 150), (600, 1150)],
                        [(0, 1, 400), (1, 0, 400), (1, 2, 150), (2, 1, 150),
                         (0, 3, 1150), (3, 0, 1150)])
        coordinates = np.asarray([point(600, 1150)])
        population = holistic_access.Population({}, coordinates, np.array([22.]), np.array([0.]),
                                                np.array([3]), central_access._points(coordinates))
        revised, audit = central_junction_sites.consolidate(base, graph, EMPTY_WATER, population=population)
        self.assertFalse(audit["actions"])
        self.assertIn("A1", revised["stations"])
        held, = [row for row in audit["held"] if "additional_residents" in row]
        self.assertEqual(held["additional_residents"], 22)

    def test_mapped_water_blocks_a_street_edge_as_well_as_a_snap_connector(self):
        graph = streets([(900, 0), (1000, 0), (1000, 75)],
                        [(0, 1, 100), (1, 0, 100), (1, 2, 75), (2, 1, 75)])
        ring = [point(945, -5), point(955, -5), point(955, 5), point(945, 5), point(945, -5)]
        context = {"layers": {"water": [{"geometry": {"type": "Polygon", "coordinates": [ring]}}]}}
        revised, audit = central_junction_sites.consolidate(crossing_fixture(), graph, context)
        self.assertFalse(audit["actions"])
        self.assertFalse(revised["station_site_links"])


if __name__ == "__main__":
    unittest.main()

"""Check that coverage uses connected walking edges and actual train calls."""

import unittest

import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

from . import central_access


class CentralAccessTests(unittest.TestCase):
    def test_coverage_uses_station_access_and_street_connectivity(self):
        lon_lat = [(44.3900, 33.3400), (44.3910, 33.3400), (44.3901, 33.3401)]
        coordinates = central_access._points(lon_lat)
        matrix = csr_matrix([[0., 130., 0.], [130., 0., 0.], [0., 0., 0.]])
        graph = (None, matrix, np.arange(3), cKDTree(coordinates), {})
        first = (44.3899, 33.3400)
        distance, excluded = central_access.distances_from_stops({"origin": first}, graph)
        self.assertEqual(excluded, 0)
        self.assertGreater(distance[0], 0.)
        self.assertAlmostEqual(distance[1], distance[0] + 130.)
        self.assertTrue(np.isinf(distance[2]))
        distance, excluded = central_access.distances_from_stops({"far": (44.35, 33.34)}, graph)
        self.assertEqual(excluded, 1)
        self.assertTrue(np.isinf(distance).all())

    def test_full_budget_contains_deferred_and_reserved_sections(self):
        baseline, lines, stations, _ = central_access.original_cases()
        self.assertEqual(set(baseline["unresolved_groups"]), {"M01", "M02", "M04", "M09"})
        self.assertEqual(len(lines), 26)
        self.assertEqual(sum(f["properties"]["status"] != "clockface calls" for f in lines), 11)
        self.assertGreater(len(stations["clockface"]), len(stations["original"]))
        self.assertNotIn("M-075", stations["clockface"])
        self.assertIn("airport-terminal", stations["clockface"])

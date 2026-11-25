"""Check cardinal long-route screening and bridge approaches."""

import unittest
from unittest.mock import patch

import numpy as np
from scipy.spatial import cKDTree

from . import holistic_grid as grid
from .holistic_network import LOCAL_METRES, Track, _physical_line
from .holistic_through import DirectionalRoads, MAX_STOP_GAP_M, STOP_SPACING_M

ORIGIN = np.array([44., 33.]) * LOCAL_METRES


def point(x, y):
    return ((ORIGIN + [x, y]) / LOCAL_METRES).tolist()


def fixture(locate, geometry, water):
    coordinates = {"a": locate(0, 0), "a1": locate(0, 2200),
                   "b": locate(16_000, 0), "b1": locate(16_000, 2200),
                   "c": locate(4600, -1600), "c1": locate(4600, 2200),
                   "d": locate(11_600, -1600), "d1": locate(11_600, 2200)}
    orders = {"A": ["a", "a1"], "B": ["b", "b1"], "C": ["c", "c1"], "D": ["d", "d1"]}
    stations = {key: {"name": key, "coordinates": coordinates[key], "lines": [code]}
                for code, keys in orders.items() for key in keys}
    lines = {code: _physical_line([coordinates[key] for key in keys], keys, stations, [], "fixture")
             for code, keys in orders.items()}
    track = Track(geometry)
    raw = np.asarray([track.at(x) for x in np.linspace(0, track.km, 650)]) * LOCAL_METRES
    graph = None, None, None, cKDTree(raw), None
    cells = [{"coordinates": locate(x, 150), "beyond_1200_m": 5000} for x in (1700, 3400, 9500, 14_400)]
    return {"lines": lines, "stations": stations}, {"layers": {"water": water}}, graph, cells


class GridCandidateTests(unittest.TestCase):
    def test_cardinal_axes_keep_exact_endpoints_and_two_intermediate_transfers(self):
        for locate, orientation in ((point, "east–west"), (lambda x, y: point(y, x), "north–south")):
            with self.subTest(orientation=orientation):
                geometry = [locate(0, 0), locate(16_000, 0)]
                network, context, graph, cells = fixture(locate, geometry, [])
                road = DirectionalRoads.from_paths([geometry])
                with patch.object(grid, "_street_layers", return_value=(road, road)):
                    result = grid.generate(network, context, graph, cells)
                    self.assertEqual(result, grid.generate(network, context, graph, cells[::-1]))
                row = next(row for row in result if row["terminal_ids"] == ["a", "b"])
                self.assertEqual(row["geometry"], geometry)
                self.assertAlmostEqual(row["one_way_km"], 16)
                self.assertEqual(row["screening"]["orientation"], orientation)
                self.assertEqual(row["screening"]["geometry_type"], "straight")
                self.assertEqual([transfer["line_id"] for transfer in row["required_interchanges"]], ["C", "D"])
                track = Track(row["geometry"])
                chainages = [0, track.km, *(item["chainage_km"] for item in row["stops"]),
                             *(item["chainage_km"] for item in row["required_interchanges"])]
                self.assertGreaterEqual(min(np.diff(sorted(chainages))) * 1000, STOP_SPACING_M)
                self.assertLessEqual(max(np.diff(sorted(chainages))) * 1000, MAX_STOP_GAP_M)
                self.assertTrue(all(item["coordinates"] == track.at(item["chainage_km"]) for item in row["stops"]))

    def test_bridge_approach_preserves_exact_crossings_and_tags_at_water(self):
        bridge = [point(7_000, 700), point(8_000, 700)]
        geometry = [point(0, 0), *bridge, point(16_000, 0)]
        rim = [point(7350, -1200), point(7650, -1200), point(7650, 1800),
               point(7350, 1800), point(7350, -1200)]
        network, context, graph, cells = fixture(
            point, geometry, [{"geometry": {"type": "Polygon", "coordinates": [rim]}}],
        )
        roads = DirectionalRoads.from_paths([geometry])
        mapped_bridge = DirectionalRoads.from_paths([bridge])
        reaches = [np.asarray(bridge) * LOCAL_METRES]
        with (patch.object(grid, "_street_layers", return_value=(roads, mapped_bridge)),
              patch.object(grid, "_bridge_reaches", return_value=reaches)):
            result = grid.generate(network, context, graph, cells)
        row = next(row for row in result if row["terminal_ids"] == ["a", "b"])
        self.assertEqual(row["screening"]["geometry_type"], "bridge approach")
        self.assertEqual(row["geometry"][1:-1], bridge)
        self.assertLess(row["directness"], 1.01)
        self.assertEqual(row["screening"]["mapped_water_contacts"][0]["mapped_wet_width_m"], 300)
        self.assertEqual([transfer["line_id"] for transfer in row["required_interchanges"]], ["C", "D"])
        with (patch.object(grid, "_street_layers", return_value=(roads, mapped_bridge)),
              patch.object(grid, "_bridge_reaches", return_value=[])):
            self.assertEqual(grid.generate(network, context, graph, cells), [])

    def test_extensions_retain_the_prior_central_segment(self):
        alignment = [point(0, 0), point(5500, 500), point(11_000, 650), point(18_000, 0)]
        points = np.asarray(alignment) * LOCAL_METRES
        demand = np.asarray([point(4000, 500), point(13_000, 500)]) * LOCAL_METRES
        axis, trials = grid._extension_trials(1, 2, points, [{line} for line in "ABCD"],
                                             demand, np.array([4000, 6000]))
        self.assertEqual(grid.ORIENTATIONS[axis], "east–west")
        self.assertEqual(len(trials), 1)
        trial, route = trials[0]
        self.assertEqual(trial[1:3], (0, 3))
        np.testing.assert_array_equal(route, points)

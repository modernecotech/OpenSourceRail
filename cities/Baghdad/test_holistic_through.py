"""Exercise direct axes, station placements and mapped water screens."""

import unittest
from unittest.mock import patch

import numpy as np
from scipy.spatial import cKDTree

from . import holistic_through as through
from .holistic_network import LOCAL_METRES, Track, _physical_line

ORIGIN = np.array([44., 33.]) * LOCAL_METRES


def point(x, y):
    return ((ORIGIN + [x, y]) / LOCAL_METRES).tolist()


class ThroughCandidateTests(unittest.TestCase):
    def test_water_requires_a_directionally_compatible_carriageway_bridge(self):
        context = {"layers": {"water": [{"geometry": {
            "type": "Polygon", "coordinates": [[point(350, -300), point(650, -300),
                                               point(650, 300), point(350, 300), point(350, -300)]],
        }}]}}
        start, end = np.asarray([point(0, 0), point(1000, 0)]) * LOCAL_METRES
        water = through.WaterGeometry.from_context(context)
        same = through.DirectionalRoads.from_paths([[point(290, -20), point(710, -20)]])
        crossing = through.DirectionalRoads.from_paths([[point(500, -300), point(500, 300)]])
        offset = through.DirectionalRoads.from_paths([[point(290, 130), point(710, 130)]])
        screen = through._water_screen(start, end, context, water, same)
        self.assertEqual(screen[0]["mapped_wet_width_m"], 300)
        self.assertGreater(screen[0]["maximum_tagged_bridge_offset_m"], 0)
        self.assertIsNone(through._water_screen(start, end, context, water, crossing))
        self.assertIsNone(through._water_screen(start, end, context, water, offset))

    def test_mapped_line_only_canal_also_needs_bridge_support(self):
        context = {"layers": {"water": [{"geometry": {
            "type": "LineString", "coordinates": [point(505, -600), point(505, 600)],
        }}]}}
        start, end = np.asarray([point(0, 0), point(1000, 0)]) * LOCAL_METRES
        water = through.WaterGeometry.from_context(context)
        none = through.DirectionalRoads.from_paths([])
        self.assertIsNone(through._water_screen(start, end, context, water, none))

    def test_generation_retains_exact_geometry_and_station_spacing(self):
        orders = {"A": ["a", "a1"], "B": ["b", "b1"], "C": ["c", "c1"]}
        coordinates = {"a": point(0, 0), "a1": point(0, 2200),
                       "b": point(8000, 0), "b1": point(8000, 2200),
                       "c": point(4000, -1600), "c1": point(4000, 2200)}
        stations = {key: {"name": key, "coordinates": coordinates[key], "lines": [code]}
                    for code, keys in orders.items() for key in keys}
        lines = {code: _physical_line([coordinates[key] for key in keys], keys, stations, [], "fixture")
                 for code, keys in orders.items()}
        network = {"lines": lines, "stations": stations}
        context = {"layers": {"water": []}}
        raw = np.asarray([point(x, 0) for x in range(0, 8001, 25)]) * LOCAL_METRES
        graph = None, None, None, cKDTree(raw), None
        road = through.DirectionalRoads.from_paths([[coordinates["a"], coordinates["b"]]])
        cells = [{"coordinates": point(x, 150), "beyond_1200_m": 5000} for x in (1700, 3400, 5050, 6650)]
        with patch.object(through, "_street_layers", return_value=(road, road)):
            candidates = through.generate(network, context, graph, cells)
            self.assertEqual(candidates, through.generate(network, context, graph, cells[::-1]))
        axis = next(row for row in candidates if row["terminal_ids"] == ["a", "b"])
        self.assertEqual(axis["id"], "T01")
        self.assertEqual(axis["key"], "T-a--b")
        self.assertEqual(axis["geometry"], [coordinates["a"], coordinates["b"]])
        self.assertEqual(axis["directness"], 1)
        self.assertEqual(axis["required_interchanges"][0]["line_id"], "C")
        track = Track(axis["geometry"])
        self.assertAlmostEqual(axis["required_interchanges"][0]["chainage_km"], 4)
        self.assertGreater(len(axis["stops"]), 2)
        for row in axis["stops"]:
            self.assertEqual(row["coordinates"], track.at(row["chainage_km"]))
            self.assertLessEqual(row["street_offset_m"], through.SNAP_M)
        chainages = [0, track.km, *(row["chainage_km"] for row in axis["required_interchanges"]),
                     *(row["chainage_km"] for row in axis["stops"])]
        self.assertGreaterEqual(min(np.diff(sorted(chainages))) * 1000, through.STOP_SPACING_M)

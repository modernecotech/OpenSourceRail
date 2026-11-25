"""Check bent-gap placement, continuity and sustained rail duplication."""

import unittest
from unittest.mock import patch

import numpy as np
from scipy.spatial import cKDTree

from . import holistic_gaps, holistic_network, holistic_through, network_gap_routes
from .holistic_network import LOCAL_METRES, Track
from .test_holistic_through import point


class GapRouteTests(unittest.TestCase):
    def test_search_uses_demand_waypoint_and_preserves_connected_network(self):
        coords = {"a": point(0, 0), "b": point(6000, 0), "hub": point(0, -4000)}
        stations = {key: {"coordinates": coord, "name": key, "basis": "fixture",
                          "lines": {"a": ["A"], "b": ["B"], "hub": ["A", "B"]}[key]}
                    for key, coord in coords.items()}
        lines = {code: holistic_network._physical_line([coords[key], coords["hub"]],
                                                      [key, "hub"], stations, [], "fixture")
                 for code, key in (("A", "a"), ("B", "b"))}
        transfer = {"id": "hub", "station_ids": ["hub"], "lines": ["A", "B"]}
        network = {"lines": lines, "stations": stations, "transfers": [transfer]}
        context = {"layers": {"water": []}}
        bend = point(3000, 1000)
        route = [coords["a"], bend, coords["b"]]
        track = Track(route)
        graph = None, None, None, cKDTree(
            np.asarray([track.at(km) for km in np.linspace(0, track.km, 400)]) * LOCAL_METRES), None
        cells = [{"coordinates": bend, "people": 15_000, "beyond_1200_m": 14_000},
                 {"coordinates": point(5000, 0), "people": 300, "beyond_1200_m": 20}]
        seed = holistic_gaps.prioritize(cells, network)[0]["id"]
        roads = holistic_through.DirectionalRoads.from_paths([route])
        with patch.object(holistic_through, "_street_layers", return_value=(roads, roads)):
            result = network_gap_routes.generate(network, context, graph, coverage_cells=cells, gap_ids=[seed])
            self.assertEqual(result, network_gap_routes.generate(
                network, context, graph, coverage_cells=cells[::-1], gap_ids=[seed]))
            self.assertEqual(network_gap_routes.generate(
                network, context, graph, coverage_cells=cells, gap_ids=["unknown"]), [])
        row = result[0]
        self.assertLess(np.linalg.norm((np.asarray(row["geometry"][1]) - bend) * LOCAL_METRES), 5)
        self.assertEqual(row["terminal_ids"], ["a", "b"])
        self.assertEqual(row["screening"]["seed_gap_id"], seed)
        self.assertTrue(row["terminal_link_only"])
        self.assertGreaterEqual(len(row["stops"]), 2)
        updated = holistic_network.insert_through_lines(network, [row], context=context, graph=graph)
        self.assertEqual(updated["topology"]["connected_components"], 1)
        self.assertNotIn(row["id"], network["lines"])
        for station in row["stops"]:
            self.assertEqual(updated["stations"][station["id"]]["coordinates"], station["coordinates"])

    def test_nearby_parallel_veto_and_perpendicular_crossing(self):
        candidate = {"id": "new", "geometry": [point(0, 0), point(5000, 0)]}
        nearby = {"parallel": {"geometry": [point(0, 900), point(5000, 900)]}}
        runs = network_gap_routes.parallel_runs(candidate, nearby)
        self.assertEqual(runs[0]["kind"], "nearby_parallel")
        self.assertGreaterEqual(runs[0]["length_m"], 2000)
        crossing = {"crossing": {"geometry": [point(2500, -2000), point(2500, 2000)]}}
        self.assertEqual(network_gap_routes.parallel_runs(candidate, crossing), [])

    def test_bend_cannot_hide_canal_contact_at_leg_endpoint(self):
        context = {"layers": {"water": [{"geometry": {
            "type": "LineString", "coordinates": [point(3000, 0), point(3000, 2000)],
        }}]}}
        gap = {"coordinates": point(3000, 1000), "bounds_wsen": [43.9, 32.9, 44.1, 33.1]}
        water = holistic_through.WaterGeometry.from_context(context)
        self.assertEqual(network_gap_routes._waypoints(gap, [], context, water), [])


if __name__ == "__main__":
    unittest.main()

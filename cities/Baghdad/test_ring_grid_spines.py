"""Check ring-grid geometry and service-withdrawal bookkeeping."""

import unittest

import numpy as np

from .holistic_network import _identity, _physical_line, validate
from .ring_grid_spines import _bearing_delta, _bridge_paths, _cross, _withdraw


class RingGridSpineTests(unittest.TestCase):
    def test_bridge_approach_follows_diagonal_and_keeps_the_route_direct(self):
        first = np.array([0., 0.])
        last = np.array([14_000., 14_000.])
        bridge = np.array([[6800., 7200.], [7300., 7700.]])
        paths = _bridge_paths(first, last, [bridge[::-1], bridge[:, ::-1] + 10_000])
        self.assertEqual(len(paths), 1)
        np.testing.assert_array_equal(paths[0][1:3], bridge)
        east = {"geometry": [[44, 33], [44.2, 33]]}
        north = {"geometry": [[44, 33.2], [44, 33]]}
        self.assertAlmostEqual(_bearing_delta(east, north), 90)

    def test_crossing_requires_an_intermediate_shared_station_on_both_axes(self):
        layout = {"lines": {"A": {"station_ids": ["same", "cross", "a"]},
                            "B": {"station_ids": ["same", "b", "cross"]}}}
        self.assertFalse(_cross(layout, "A", "B"))
        layout["lines"]["B"]["station_ids"] = ["same", "cross", "b"]
        self.assertTrue(_cross(layout, "A", "B"))

    def test_withdrawal_drops_only_walking_links_with_a_closed_platform(self):
        coordinates = {"a": [44., 33.], "x": [44.01, 33.], "p": [44.02, 33.],
                       "b": [44.03, 33.], "q": [44.04, 33.], "y": [44.05, 33.]}
        routes = {"C1": ["a", "x", "p"], "C2": ["b", "q"], "T99": ["x", "y"]}
        stations = {stop: {"coordinates": point, "name": stop,
                           "lines": sorted(line for line, seq in routes.items() if stop in seq)}
                    for stop, point in coordinates.items()}
        lines = {code: _physical_line([coordinates[seq[0]], coordinates[seq[-1]]], seq, stations, [], "fixture")
                 for code, seq in routes.items()}
        for code in routes:
            lines[code]["name"] = code
        links = []
        for a, b in (("p", "b"), ("q", "y")):
            path = [coordinates[a], coordinates[b]]
            links.append({"id": f"{a}-{b}", "station_ids": [a, b], "walks_m": [1000, 1000],
                          "geometry": [path, path[::-1]]})
        network = _identity({
            "lines": lines, "stations": stations, "station_site_links": links,
            "transfers": [{"id": "x", "station_ids": ["x"], "lines": ["C1", "T99"]}],
        })
        revised, actions, dropped = _withdraw(network, {"T99"}, {"a"})
        self.assertEqual(validate(revised)["connected_components"], 1)
        self.assertEqual([row["id"] for row in revised["station_site_links"]], ["p-b"])
        self.assertEqual([row["id"] for row in dropped], ["q-y"])
        self.assertEqual(actions[0]["closed_stations"], ["y"])
        self.assertEqual(network["station_site_links"], links)
        with self.assertRaisesRegex(ValueError, "Protected stations removed"):
            _withdraw(network, {"T99"}, {"y"})


if __name__ == "__main__":
    unittest.main()

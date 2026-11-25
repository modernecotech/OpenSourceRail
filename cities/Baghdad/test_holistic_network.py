"""Check the integrated Baghdad map against route, station and interchange contracts."""

from copy import deepcopy
import unittest

import numpy as np
from scipy.spatial import cKDTree

from . import holistic_network as network


class BaghdadNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = network.evaluate()

    def test_every_line_has_an_end_to_end_passenger_path(self):
        lines = self.record["lines"]
        self.assertEqual(len(lines), 16)
        self.assertEqual(network.validate(self.record)["connected_components"], 1)
        self.assertFalse(self.record["physical_accepted"])
        self.assertFalse(self.record["operating_timetable_validated"])
        self.assertTrue(lines["M09"]["loop"])
        self.assertTrue(all(row["name"] for row in self.record["stations"].values()))
        for line in lines.values():
            self.assertFalse(any(section.startswith("B-X") for section in line["source_sections"]))
            if not line["loop"]:
                self.assertAlmostEqual(line["station_chainage_km"][line["station_ids"][-1]], line["one_way_km"])

    def test_airport_alignment_is_a_contiguous_prefix_of_a_through_service(self):
        original = network.read(network.AIRPORT)
        line = self.record["lines"]["C1"]
        path = np.asarray(original["features"][0]["geometry"]["coordinates"])
        # The site profile repeats some coordinates at a station discontinuity.
        path = path[np.r_[True, np.any(np.abs(np.diff(path, axis=0)) > 1e-12, axis=1)]]
        self.assertTrue(np.allclose(path, line["geometry"][:len(path)], rtol=0, atol=1e-8))
        self.assertTrue(set(f"Airport-{i:02}" for i in range(6)) <= set(line["station_ids"]))
        self.assertEqual(line["station_ids"][0], "Airport-00")
        self.assertEqual(line["station_ids"][-1], "Zayouna")
        self.assertIn("Airport-01", self.record["lines"]["M05"]["station_ids"])
        self.assertNotIn("airport-terminal", self.record["stations"])
        self.assertEqual(self.record["stations"]["Tahrir"]["lines"], ["C1", "C2"])

    def test_geometric_crossings_alone_cannot_connect_lines(self):
        shared_point = [44.1, 33.1]
        shared = {"name": "Central", "coordinates": shared_point, "lines": ["A", "B"]}
        stations = {"a": {"coordinates": [44., 33.], "lines": ["A"]},
                    "b": {"coordinates": [44.2, 33.], "lines": ["B"]}, "x": shared}
        lines = {code: network._physical_line([stations[stop]["coordinates"], shared_point],
                                               [stop, "x"], stations, ["synthetic"], "test")
                 for code, stop in (("A", "a"), ("B", "b"))}
        record = {"stations": stations, "lines": lines,
                  "transfers": [{"id": "x", "station_ids": ["x"], "lines": ["A", "B"]}]}
        self.assertEqual(network.validate(record)["connected_components"], 1)
        record["stations"]["x"] = shared | {"lines": ["A"]}
        record["stations"]["y"] = shared | {"lines": ["B"]}
        record["lines"]["B"]["station_ids"][-1] = "y"
        chainage = record["lines"]["B"]["station_chainage_km"]
        chainage["y"] = chainage.pop("x")
        record["transfers"] = []
        with self.assertRaisesRegex(ValueError, "Disconnected passenger lines"):
            network.validate(record)

    def test_infill_reuses_exact_track_chainage_and_preserves_base_record(self):
        base = self.record
        line = base["lines"]["C1"]
        km = 2.5
        addition = {"line_id": "C1", "chainage_km": km, "id": "trial", "name": "Trial", "basis": "fixture"}
        revised = network.insert_stations(base, [addition])
        self.assertNotIn("trial", base["stations"])
        self.assertEqual(revised["stations"]["trial"]["coordinates"], network.Track(line["geometry"]).at(km))
        self.assertEqual(revised["topology"]["stations"], base["topology"]["stations"] + 1)
        self.assertNotEqual(revised["candidate_id"], base["candidate_id"])
        self.assertEqual(revised["evaluation_id"], network.insert_stations(base, [addition])["evaluation_id"])
        with self.assertRaisesRegex(ValueError, "Invalid station insertion"):
            network.insert_stations(base, [addition | {"chainage_km": .1}])

    def test_geojson_exports_topology_ids_and_no_unserved_guideway(self):
        record = self.record
        data = network.geojson(record)
        mapped_lines = {f["properties"]["line_id"]: f["properties"]["station_ids"] for f in data["features"]
                        if f["geometry"]["type"] == "LineString"}
        mapped_stations = {f["properties"]["station_id"] for f in data["features"]
                           if f["geometry"]["type"] == "Point"}
        self.assertEqual(data["candidate_id"], record["candidate_id"])
        self.assertEqual(mapped_lines, {code: row["station_ids"] for code, row in record["lines"].items()})
        self.assertEqual(mapped_stations, record["stations"].keys())
        tampered = deepcopy(record)
        tampered["transfers"].pop()
        with self.assertRaisesRegex(ValueError, "Every interchange"):
            network.validate(tampered)

    def test_water_screen_respects_islands_and_empty_sample(self):
        water = {"layers": {"water": [{"geometry": {"type": "Polygon", "coordinates": [
            [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]],
            [[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]],
        ]}}]}}
        self.assertEqual(network.dry_points([[.5, .5], [2.5, 2.5], [5., 5.]], water).tolist(), [False, True, True])
        self.assertEqual(network.dry_points([], water).tolist(), [])


class ThroughLineTests(unittest.TestCase):
    def setUp(self):
        points = {"a0": [44., 33.], "a1": [44., 33.06], "b0": [44.06, 33.],
                  "b1": [44.06, 33.06], "x": [44., 33.03], "y": [44.06, 33.03]}
        orders = {"A": ["a0", "x", "a1"], "B": ["b0", "y", "b1"], "C": ["x", "y"]}
        stations = {stop: {"name": stop, "coordinates": point, "basis": "fixture",
                           "lines": [code for code, stops in orders.items() if stop in stops]}
                    for stop, point in points.items()}
        lines = {code: network._physical_line([points[stops[0]], points[stops[-1]]],
                                               stops, stations, ["fixture"], "fixture")
                 for code, stops in orders.items()}
        self.record = {"stations": stations, "lines": lines, "transfers": [
            {"id": stop, "station_ids": [stop], "lines": stations[stop]["lines"]} for stop in ("x", "y")
        ]}
        self.line = {"id": "D", "name": "Diagonal", "terminal_ids": ["a0", "b1"],
                     "geometry": [points["a0"], points["b1"]],
                     "required_interchanges": [{"line_id": "C", "point": [44.03, 33.03]}],
                     "stops": [{"id": "d0", "name": "Local", "chainage_m": 800}]}
        self.other = {"id": "E", "name": "Cross-town", "terminal_ids": ["a1", "b0"],
                      "geometry": [points["a1"], [44.02, 33.03], [44.048, 33.041], points["b0"]],
                      "required_interchanges": [{"line_id": "C", "point": [44.02, 33.03]}]}
        track_d, track_e = (network.Track(row["geometry"]) for row in (self.line, self.other))
        street_points = [*points.values(), [44.03, 33.03], [44.02, 33.03], track_d.at(.8),
                         *network._crossings(track_d, track_e)]
        self.graph = (None, None, None, cKDTree(np.asarray(street_points) * network.LOCAL_METRES), None)
        self.context = {"layers": {"water": []}}

    def insert(self, *lines, **options):
        return network.insert_through_lines(
            self.record, lines, **({"graph": self.graph, "context": self.context} | options))

    def test_through_line_adds_two_endpoint_links_and_exact_intermediate_transfer(self):
        revised = self.insert(self.line)
        summary = revised["through_lines"]["D"]
        crossing, = summary["required_intermediate_transfer_ids"]
        self.assertEqual(summary["transfer_ids"], ["a0", crossing, "b1"])
        self.assertEqual(summary["transfer_count"], 3)
        self.assertEqual(revised["stations"][crossing]["coordinates"], [44.03, 33.03])
        self.assertEqual(revised["stations"][crossing]["lines"], ["C", "D"])
        self.assertEqual(revised["lines"]["D"]["station_chainage_km"]["d0"], .8)
        self.assertEqual(revised["topology"]["connected_components"], 1)
        self.assertEqual(revised["candidate_id"], self.insert(self.line)["candidate_id"])
        self.assertNotIn("D", self.record["lines"])
        self.assertNotIn(crossing, self.record["stations"])
        self.assertEqual(self.record["stations"]["a0"]["lines"], ["A"])

    def test_exact_existing_intermediate_station_keeps_its_identity(self):
        point = [44.03, 33.03]
        self.record["stations"]["existing"] = {
            "name": "Existing", "coordinates": point, "basis": "fixture", "lines": ["C"],
        }
        line = self.record["lines"]["C"]
        network._add(line, "existing", network.Track(line["geometry"]).locate(point)[0])
        revised = self.insert(self.line)
        self.assertEqual(revised["through_lines"]["D"]["required_intermediate_transfer_ids"], ["existing"])
        self.assertEqual(revised["stations"]["existing"]["lines"], ["C", "D"])
        self.assertEqual(revised["stations"]["existing"]["coordinates"], point)

    def test_selected_through_lines_can_gain_a_shared_transfer(self):
        revised = self.insert(self.line, self.other, connect_through_lines=True)
        joint, = set(revised["through_lines"]["D"]["transfer_ids"]) & set(revised["through_lines"]["E"]["transfer_ids"])
        self.assertEqual(revised["stations"][joint]["lines"], ["D", "E"])
        self.assertEqual(revised["through_lines"]["E"]["transfer_count"], 4)
        self.assertEqual(revised["evaluation_id"], self.insert(self.line, self.other,
                                                               connect_through_lines=True)["evaluation_id"])

    def test_short_terminal_link_requires_disjoint_routes_and_no_claimed_middle_connection(self):
        points = {stop: self.record["stations"][stop]["coordinates"] for stop in ("a0", "b1", "x", "y")}
        connector = self.line | {"terminal_link_only": True, "terminal_ids": ["a0", "y"],
                                 "geometry": [points["a0"], points["y"]], "stops": [],
                                 "required_interchanges": []}
        summary = self.insert(connector)["through_lines"]["D"]
        self.assertTrue(summary["terminal_link_only"])
        self.assertEqual(summary["transfer_ids"], ["a0", "y"])
        self.assertEqual(summary["required_intermediate_transfer_ids"], [])
        for changes in ({"terminal_ids": ["a0", "b1"], "geometry": [points["a0"], points["b1"]]},
                        {"terminal_ids": ["x", "y"], "geometry": [points["x"], points["y"]]},
                        {"required_interchanges": self.line["required_interchanges"]}):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, "terminal-only connector"):
                self.insert(connector | changes)

    def test_invalid_through_line_inputs_are_rejected(self):
        interchanges = self.line["required_interchanges"]
        invalid = [
            ({"terminal_ids": ["a0", "unknown"]}, "two distinct existing terminal"),
            ({"terminal_ids": ["a0", "a1"]}, "terminal connections to distinct existing routes"),
            ({"geometry": [[43.99, 33.], *self.line["geometry"]]}, "stray path"),
            ({"required_interchanges": []}, "requires an intermediate interchange"),
            ({"required_interchanges": [{"line_id": "C", "point": [44.03, 33.031]}]}, "exact alignment crossing"),
            ({"required_interchanges": interchanges * 2}, "Duplicate shared station"),
            ({"stops": [{"id": "bad", "name": "Bad", "chainage_km": float("nan")}]}, "chainage or spacing"),
            ({"stops": [{"id": "bad", "name": "Bad", "chainage_m": 100}]}, "chainage or spacing"),
        ]
        for changes, expected in invalid:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, expected):
                self.insert(self.line | changes)

    def test_water_and_street_access_are_checked_at_the_crossing(self):
        ring = [[44.029, 33.029], [44.031, 33.029], [44.031, 33.031],
                [44.029, 33.031], [44.029, 33.029]]
        water = {"layers": {"water": [{"geometry": {"type": "Polygon", "coordinates": [ring]}}]}}
        with self.assertRaisesRegex(ValueError, "inside mapped water"):
            self.insert(self.line, context=water)
        graph = (None, None, None, cKDTree(np.asarray([[44., 33.]]) * network.LOCAL_METRES), None)
        with self.assertRaisesRegex(ValueError, "mapped street access limit"):
            self.insert(self.line, graph=graph)

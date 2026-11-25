"""Check the integrated Baghdad map against route, station and interchange contracts."""

from copy import deepcopy
import unittest

import numpy as np

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

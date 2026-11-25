"""Regression tests for the separate connected central Baghdad option."""

import math
import unittest

from cities.Baghdad import central_service


class CentralServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = central_service.evaluate()

    def test_all_mapped_stops_have_trains_in_both_directions(self):
        lines = self.case["lines"]
        stations = self.case["stations"]
        self.assertEqual(set(stations), set().union(*(set(row["station_ids"]) for row in lines.values())))
        self.assertEqual(set(lines["C1"]["station_ids"]) & set(lines["C2"]["station_ids"]), {"Tahrir"})
        for name, line in lines.items():
            ordered = line["station_ids"]
            self.assertEqual([[r[0] for r in pattern] for pattern in line["patterns"]], [ordered, ordered[::-1]], name)
            self.assertEqual(line["geometry"][0], stations[ordered[0]]["coordinates"], name)
            self.assertEqual(line["geometry"][-1], stations[ordered[-1]]["coordinates"], name)
            self.assertTrue(math.isclose(line["station_chainage_km"][ordered[-1]], line["one_way_km"]), name)
            self.assertGreater(line["departures"], 0, name)

    def test_crossing_and_conservative_resource_screen(self):
        self.assertEqual(len(self.case["lines"]["C1"]["tigris_crossings"]), 1)
        self.assertEqual(self.case["lines"]["C2"]["tigris_crossings"], [])
        self.assertEqual(self.case["headway_s"], 900)
        self.assertFalse(self.case["service_trials"]["600"]["resource_screen_passed"])
        self.assertTrue(self.case["service_trials"]["900"]["resource_screen_passed"])
        self.assertGreaterEqual(min(self.case["minimum_clearances_s"].values()), 0)

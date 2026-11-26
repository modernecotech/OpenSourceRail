"""Check named suburb journeys at matched service and with directed walking access."""

from dataclasses import replace
import unittest
from unittest.mock import patch

import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

from . import central_access, coverage_destinations, coverage_through_journeys
from . import holistic_journeys, holistic_network, holistic_pathways


class NamedSuburbanJourneysTests(unittest.TestCase):
    def setUp(self):
        anchor = np.array([44.36, 33.32])
        self.points = {
            name: tuple(anchor + np.asarray(xy) / holistic_network.LOCAL_METRES)
            for name, xy in {
                "A": (0, 0), "B": (2_000, 0), "C": (4_000, 0), "D": (6_000, 0),
                "H": (2_000, 12_000), "Basmaya": (0, -300), "Nahrawan": (2_000, -200),
                "Tajiyat": (7_000, -500), "Market": (6_000, -400), "Park": (4_000, -400),
            }.items()
        }
        self.split = {"AB": ["A", "B"], "BC": ["B", "C"], "CD": ["C", "D"]}
        nodes = list(self.points)
        edges = [("Basmaya", "A", 300), ("B", "Nahrawan", 200), ("C", "Park", 400), ("D", "Market", 400)]
        matrix = csr_matrix(
            ([m for _, _, m in edges], ([nodes.index(a) for a, _, _ in edges],
                                       [nodes.index(b) for _, b, _ in edges])),
            shape=(len(nodes), len(nodes)),
        )
        self.graph = None, matrix, np.arange(len(nodes)), cKDTree(central_access._points(self.points.values())), {}
        self.destinations = [holistic_pathways.CentreDestination(name, self.points[name], weight=weight)
                             for name, weight in (("Market", 3), ("Park", 1))]
        self.assumptions = replace(holistic_journeys.JourneyAssumptions(), headway_s=60, walk_limit_m=1300)

    def network(self, layout):
        stations, lines = {}, {}
        for line, stops in layout.items():
            for stop in stops:
                stations.setdefault(stop, {"coordinates": self.points[stop], "lines": []})["lines"].append(line)
            lines[line] = holistic_network._physical_line(
                [self.points[stop] for stop in stops], stops, stations, [line], "fixture", loop=False)
        return {"stations": stations, "lines": lines, "transfers": [
            {"id": stop, "station_ids": [stop], "lines": station["lines"]}
            for stop, station in stations.items() if len(station["lines"]) > 1
        ]}

    def compare(self, alternative, **options):
        origins = {name: self.points[name] for name in ("Basmaya", "Nahrawan", "Tajiyat")}
        with patch.object(coverage_destinations, "locations", return_value=origins):
            return coverage_through_journeys.compare(
                {"published": self.network(self.split), "alternative": self.network(alternative)},
                graph=self.graph, destinations=self.destinations, assumptions=self.assumptions, **options)["variants"]

    def test_through_service_improves_same_station_access_with_unchanged_train_km(self):
        cases = self.compare({"AD": ["A", "B", "C", "D"]})
        previous = cases["published"]["origins"]["Basmaya"]
        revised = cases["alternative"]["origins"]["Basmaya"]
        self.assertEqual(previous["destination_count_by_max_transfers"], {"0": 0, "1": 1, "2": 2})
        self.assertEqual(revised["destination_count_by_max_transfers"], {"0": 2, "1": 2, "2": 2})
        self.assertEqual(revised["walk_m"], previous["walk_m"])
        self.assertEqual(revised["walk_m"], 300)
        self.assertEqual(cases["alternative"]["running_train_km_day"], cases["published"]["running_train_km_day"])
        market = revised["destinations"]["Market"]
        self.assertEqual(market["minimum_transfers"], 0)
        self.assertEqual(market["assigned_transfers"], 0)
        self.assertLess(market["elapsed_delta_vs_reference_min"], 0)

    def test_direct_availability_does_not_depend_on_fastest_assigned_route(self):
        cases = self.compare(self.split | {"AHD": ["A", "H", "D"]})
        revised = cases["alternative"]["origins"]["Basmaya"]
        self.assertGreater(cases["alternative"]["directional_headway_s"], 60)
        self.assertEqual(revised["destination_count_by_max_transfers"], {"0": 1, "1": 2, "2": 2})
        self.assertEqual(revised["destinations"]["Market"]["minimum_transfers"], 0)
        self.assertEqual(revised["destinations"]["Market"]["assigned_transfers"], 2)

    def test_unreachable_pairs_carry_no_trip_time(self):
        cases = self.compare({"AD": ["A", "B", "C", "D"]})
        for name in ("Nahrawan", "Tajiyat"):
            origin = cases["alternative"]["origins"][name]
            self.assertFalse(origin["walk_eligible"])
            self.assertIsNone(origin["walk_m"])
            self.assertEqual(origin["destination_count_by_max_transfers"], {"0": 0, "1": 0, "2": 0})
            self.assertTrue(all(value is None for value in origin["destinations"]["Market"].values()))

    def test_named_through_services_count_only_a_ride_between_distinct_stations(self):
        self.destinations.append(holistic_pathways.CentreDestination("At departure station", self.points["A"]))
        cases = self.compare({"AD": ["A", "B", "C", "D"]},
                             through_routes={"published": ["CD"], "alternative": ["AD"]})
        previous = cases["published"]["origins"]["Basmaya"]
        revised = cases["alternative"]["origins"]["Basmaya"]
        self.assertEqual(previous["walkable_through_routes"], {})
        self.assertEqual(previous["direct_through_destination_count"], 0)
        self.assertEqual(revised["walkable_through_routes"], {"AD": 300})
        self.assertEqual(revised["direct_through_destination_count"], 2)

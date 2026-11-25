"""Check transfer-constrained paths, directed access and common demand weights."""

from dataclasses import replace
from types import SimpleNamespace
import unittest

import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

from cities.Baghdad import central_access, holistic_access, holistic_journeys, holistic_network, holistic_pathways


class HousingPathwaysTests(unittest.TestCase):
    def setUp(self):
        anchor = np.array([44.36, 33.32])
        self.points = {
            code: tuple(anchor + np.asarray(xy) / holistic_network.LOCAL_METRES)
            for code, xy in {"A": (0, 0), "B": (2_000, 0), "C": (4_000, 0),
                             "D": (6_000, 0), "E": (8_000, 0), "H": (0, 12_000),
                             "home": (0, -300), "centre": (8_000, -400)}.items()
        }
        self.fast = {"AB": ["A", "B"], "BC": ["B", "C"], "CD": ["C", "D"], "DE": ["D", "E"]}
        self.detour = self.fast | {"AHC": ["A", "H", "C"]}
        self.assumptions = replace(holistic_journeys.JourneyAssumptions(), headway_s=60)

    def street(self, edges=()):
        codes = list(self.points)
        coords = central_access._points(self.points.values())
        matrix = csr_matrix(([m for _, _, m in edges],
                             ([codes.index(a) for a, _, _ in edges], [codes.index(b) for _, b, _ in edges])),
                            shape=(len(codes), len(codes)))
        return None, matrix, np.arange(len(codes)), cKDTree(coords), {"id": "street-fixture"}

    def network(self, layout):
        stations, lines = {}, {}
        for line, stops in sorted(layout.items()):
            for stop in stops:
                station = stations.setdefault(stop, {"coordinates": self.points[stop], "lines": []})
                station["lines"].append(line)
            lines[line] = holistic_network._physical_line(
                [self.points[stop] for stop in stops], stops, stations, [line], "fixture", loop=False)
        return {"stations": stations, "lines": lines, "transfers": [
            {"id": stop, "station_ids": [stop], "lines": station["lines"]}
            for stop, station in stations.items() if len(station["lines"]) > 1
        ]}

    def compare(self, layouts, origins=("A",), destinations=("E",), edges=(), **options):
        return holistic_pathways.compare(
            {name: self.network(layout) for name, layout in layouts.items()},
            origins=[holistic_pathways.HousingOrigin(code, self.points[code], 100 if code in ("A", "home") else 50)
                     for code in origins],
            destinations=[holistic_pathways.CentreDestination(code, self.points[code], weight=i + 1)
                          for i, code in enumerate(destinations)],
            graph=self.street(edges), assumptions=self.assumptions, **options,
        )

    def test_two_transfer_detour_remains_eligible_when_fastest_path_takes_three(self):
        detour = self.network(self.detour)
        access = np.full((2, len(detour["stations"])), np.inf)
        columns = sorted(detour["stations"])
        access[0, columns.index("A")] = access[1, columns.index("E")] = 0
        route = holistic_journeys._assignment_graph(detour, access, self.assumptions, self.assumptions.headway_s)
        _, boards, _, _ = holistic_journeys._assign(route, SimpleNamespace(weights=np.ones((2, 2))))
        self.assertEqual(boards[0, 1], 4)

        result = self.compare({"fast": self.fast, "detour": self.detour})
        fast = result["variants"]["fast"]
        detour = result["variants"]["detour"]
        self.assertEqual(fast["journeys"]["served_share_pct"], 0)
        self.assertEqual(fast["journeys"]["eligible_but_unserved_share_pct"], 100)
        self.assertIsNone(fast["journeys"]["elapsed_p90_min"])
        self.assertEqual(detour["journeys"]["transfer_share_of_all_pct"], {"0": 0, "1": 0, "2": 100})
        self.assertEqual(detour["journeys"]["reachable_with_at_most_share_of_all_pct"], {"0": 0, "1": 0, "2": 100})
        witness = detour["pathway_witnesses"]["2"]
        self.assertEqual([leg["line"] for leg in witness["rail_legs"]], ["AHC", "CD", "DE"])
        self.assertEqual(witness["transfer_stations"], ["C", "D"])
        self.assertEqual(witness["rail_legs"][0]["board_station"], "A")
        self.assertEqual(witness["rail_legs"][-1]["alight_station"], "E")
        self.assertEqual(detour["concentration"]["busiest_directed_segment_share_of_served_pct"], 100)
        expected = (2 * self.assumptions.station_access_s + 3 * self.assumptions.headway_s / 2
                    + self.assumptions.dwell_s + 2 * self.assumptions.transfer_walk_s
                    + sum(holistic_journeys._running_time(
                        (np.linalg.norm((np.asarray(self.points[a]) - self.points[b])
                                        * holistic_network.LOCAL_METRES)), self.assumptions)
                          for a, b in (("A", "H"), ("H", "C"), ("C", "D"), ("D", "E"))))
        self.assertAlmostEqual(witness["elapsed_min"], expected / 60, places=3)
        self.assertEqual(witness["generalised_min"] - witness["elapsed_min"], 4)

    def test_outgoing_egress_and_common_unserved_weight(self):
        single = {"AE": ["A", "E"]}
        edges = (("home", "A", 300), ("E", "centre", 400))
        report = self.compare({"forward": single}, ("home", "H"), ("centre", "D"), edges)
        forward = report["variants"]["forward"]
        self.assertAlmostEqual(forward["journeys"]["served_share_pct"], 100 * 2 / 9, places=4)
        self.assertEqual(forward["journeys"]["served_od_pairs"], 1)
        self.assertEqual(forward["journeys"]["walking_eligible_od_pairs"], 1)
        self.assertEqual(forward["sample_access"]["origin_population_with_station"], 100)
        self.assertEqual(forward["destinations"]["centre"]["nearest_station_walk_m"], 400)
        self.assertFalse(forward["destinations"]["D"]["destination_walk_eligible"])
        witness = forward["pathway_witnesses"]["0"]
        self.assertEqual(witness["origin_walk_m"], 300)
        self.assertEqual(witness["destination_walk_m"], 400)
        reversed_direction = self.compare({"forward": single}, ("centre",), ("home",), edges)
        self.assertEqual(reversed_direction["variants"]["forward"]["journeys"]["served_share_pct"], 0)
        self.assertEqual(reversed_direction["variants"]["forward"]["journeys"]["walking_eligible_share_pct"], 0)

    def test_direct_availability_is_reported_when_a_change_is_faster(self):
        layouts = {"mixed": {"AHE": ["A", "H", "E"], "AC": ["A", "C"], "CE": ["C", "E"]}}
        journeys = self.compare(layouts)["variants"]["mixed"]["journeys"]
        self.assertEqual(journeys["reachable_with_at_most_share_of_all_pct"], {"0": 100, "1": 100, "2": 100})
        self.assertEqual(journeys["transfer_share_of_all_pct"], {"0": 0, "1": 100, "2": 0})

    def test_a_city_can_define_its_own_metric_street_projection(self):
        raw, matrix, active, street, source = self.street()
        shift = np.array([10000., -3000.])
        graph = raw, matrix, active, cKDTree(street.data + shift), source
        report = holistic_pathways.compare(
            {"line": self.network({"AE": ["A", "E"]})},
            origins=[holistic_pathways.HousingOrigin("home", self.points["A"], 100)],
            destinations=[holistic_pathways.CentreDestination("centre", self.points["E"])],
            graph=graph, project=lambda points: central_access._points(points) + shift)
        self.assertEqual(report["variants"]["line"]["journeys"]["served_share_pct"], 100)

    def test_service_matching_and_ordering(self):
        layouts = {"short": {"AE": ["A", "E"]}, "long": {"AHE": ["A", "H", "E"]}}
        result = self.compare(layouts, match_service_to="short")
        reverse_order = self.compare(dict(reversed(list(layouts.items()))), match_service_to="short")
        self.assertEqual(result, reverse_order)
        short = result["variants"]["short"]["service"]
        long = result["variants"]["long"]["service"]
        self.assertEqual(short["running_train_km_day"], long["running_train_km_day"])
        self.assertEqual(short["headway_to_nominal_ratio"], 1)
        self.assertGreater(long["headway_to_nominal_ratio"], short["headway_to_nominal_ratio"])

    def test_population_tiles_exclude_centre_pixels_before_aggregation(self):
        coordinates = np.array([self.points[code] for code in ("A", "B", "C")])
        retained = holistic_access.Population(
            {"id": "fixture"}, coordinates, np.array([7., 11., 13.]), np.zeros(3), np.arange(3),
            np.array([(1., 1.), (2., 1.), (3., 1.)]))
        results = holistic_pathways.sample_origins(
            retained, tile_m=1_000, exclude_bounds=(44.359, 33.319, 44.361, 33.321))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].people, 24)
        self.assertEqual(results[0].coordinates, self.points["C"])

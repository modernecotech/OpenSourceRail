"""Exercise paired service, street access and directed loads on known Baghdad fixtures."""

from dataclasses import replace
import unittest

import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

from cities.Baghdad import central_access, holistic_access, holistic_journeys, holistic_map, holistic_network


class JourneyTests(unittest.TestCase):
    def setUp(self):
        self.assumptions = holistic_journeys.JourneyAssumptions(tile_m=1_000)
        scale = holistic_network.LOCAL_METRES
        anchor = np.array([44.36, 33.32])
        self.points = {
            name: (anchor + np.array(xy) / scale).tolist()
            for name, xy in {
                "A": (0, 0), "B": (4_000, 0), "C": (4_000, 4_000), "D": (4_000, 1_000),
            }.items()
        }
        codes = ("A", "B", "C", "D")
        coordinates = np.array([self.points[code] for code in codes])
        xy = central_access._points(coordinates)
        tree = cKDTree(xy)
        street = csr_matrix(([4_000.] * 6, ([0, 1, 1, 2, 0, 3], [1, 0, 2, 1, 3, 0])), shape=(4, 4))
        self.graph = (None, street, np.arange(4), tree, {"fixture": True})
        self.population = holistic_access.Population(
            {"id": "fixture"}, coordinates, np.array([120., 40., 200., 30.]), np.zeros(4), np.arange(4), xy
        )

    def network(self, layout):
        stations = {}
        lines = {}
        for name, (order, loop) in layout.items():
            for code in order:
                station = stations.setdefault(code, {"coordinates": self.points[code], "lines": []})
                station["lines"].append(name)
            path = [self.points[code] for code in (order + order[:1] if loop else order)]
            lines[name] = holistic_network._physical_line(path, order, stations, [name], "fixture", loop=loop)
        return {"lines": lines, "stations": stations, "transfers": [
            {"id": code, "station_ids": [code], "lines": station["lines"]}
            for code, station in stations.items() if len(station["lines"]) > 1
        ]}

    def test_rail_directions_and_transfer_cost_match_hand_calculation(self):
        junction = self.network({"West": (["A", "B"], False), "North": (["B", "C"], False)})
        sample = holistic_journeys.sample_demand(self.population, self.assumptions)
        coordinates = [tuple(row) for row in sample.coordinates]
        a, c, d = (coordinates.index(tuple(self.points[code])) for code in ("A", "C", "D"))
        access = holistic_journeys._street_access({"junction": junction}, sample, self.graph, 1_200)["junction"]
        self.assertTrue(np.isinf(access[d]).all())
        train = holistic_journeys._assignment_graph(junction, access, self.assumptions, 360)
        generalised, boards, counts, loads = holistic_journeys._assign(train, sample)
        self.assertEqual(boards[a, c], 2)
        self.assertEqual(boards[c, a], 2)
        self.assertAlmostEqual(generalised[a, c], 2 * 60 + 2 * 180 + 2 * 225 + 120 + 120)
        self.assertAlmostEqual(generalised[c, a], generalised[a, c])
        self.assertAlmostEqual(counts.sum(), (sample.weights * boards).sum())
        self.assertAlmostEqual(loads.sum(), counts.sum())
        self.assertEqual(np.count_nonzero(loads), 4)
        self.assertTrue(np.isinf(generalised[d, c]))

    def test_ring_uses_closure_in_both_directions_and_reduces_transfers(self):
        ring = self.network({"Ring": (["A", "B", "C"], True)})
        junction = self.network({"West": (["A", "B"], False), "North": (["B", "C"], False)})
        options = {"junction": junction, "ring": ring}
        result = holistic_journeys.compare(options, graph=self.graph, population=self.population,
                                          assumptions=self.assumptions, match_service_to="junction")
        other = holistic_journeys.compare(dict(reversed(tuple(options.items()))), graph=self.graph,
                                         population=self.population, assumptions=self.assumptions,
                                         match_service_to="junction")
        self.assertEqual(result, other)
        reference, candidate = (result["variants"][name] for name in ("junction", "ring"))
        self.assertGreater(candidate["service"]["directional_headway_s"], 360)
        self.assertEqual(candidate["service"]["running_train_km_day"], reference["service"]["running_train_km_day"])
        self.assertEqual(candidate["journeys"]["served_share_pct"], reference["journeys"]["served_share_pct"])
        self.assertEqual(candidate["journeys"]["direct_share_of_served_pct"], 100)
        self.assertEqual(candidate["journeys"]["at_most_one_transfer_share_of_served_pct"], 100)
        self.assertLess(reference["journeys"]["direct_share_of_served_pct"], 100)
        self.assertEqual(candidate["paired_journeys"]["served_only_by_candidate_share_pct"], 0)
        self.assertEqual(candidate["paired_journeys"]["served_only_by_reference_share_pct"], 0)
        self.assertLess(candidate["paired_journeys"]["candidate_minus_reference_elapsed_mean_min"], 0)
        segment = candidate["concentration"]["busiest_directed_segment"]
        self.assertEqual({segment["from_station"], segment["to_station"]}, {"A", "C"})

    def test_no_street_access_is_reported_as_unserved(self):
        network = self.network({"Line": (["A", "B", "C"], False)})
        population = replace(self.population, offsets_m=np.full(4, 150.))
        result = holistic_journeys.compare({"only": network}, graph=self.graph, population=population,
                                          assumptions=self.assumptions)["variants"]["only"]
        self.assertEqual(result["journeys"]["served_share_pct"], 0)
        self.assertIsNone(result["journeys"]["elapsed_p90_min"])
        self.assertIsNone(result["concentration"]["busiest_line"])
        self.assertEqual(result["sample_access"]["tiles_with_a_station"], 0)

    def test_headway_sensitivity_keeps_running_train_km_and_checkable_pressure(self):
        options = {"grid": self.network({"West": (["A", "B"], False), "North": (["B", "C"], False)})}
        kwargs = dict(graph=self.graph, population=self.population, assumptions=self.assumptions)
        uniform = holistic_journeys.compare(options, **kwargs)["variants"]["grid"]
        balanced = holistic_journeys.compare(options, balance_frequencies=True, **kwargs)["variants"]["grid"]
        self.assertEqual(balanced["service"]["running_train_km_day"], uniform["service"]["running_train_km_day"])
        self.assertLessEqual(balanced["concentration"]["peak_load_per_departure_index"],
                             uniform["concentration"]["peak_load_per_departure_index"])
        self.assertEqual(balanced["journeys"]["served_share_pct"], uniform["journeys"]["served_share_pct"])

    def test_layout_ranking_counts_concentration_and_walking_shortfall(self):
        def option(transfer, peak, time):
            return {"journeys": {"at_most_one_transfer_share_of_all_pct": transfer},
                    "paired_journeys": {"candidate_elapsed_p90_min": time, "reference_elapsed_p90_min": 60.},
                    "concentration": {"busiest_directed_segment_share_of_served_pct": peak}}

        reference = option(50., 10., 60.)
        fast = option(60., 20., 55.)
        balanced = option(54., 11., 60.)
        self.assertLess(holistic_map.layout_rank(balanced, reference, 0, 110),
                        holistic_map.layout_rank(fast, reference, 0, 100))
        self.assertLess(holistic_map.layout_rank(fast, reference, 0, 100),
                        holistic_map.layout_rank(balanced, reference, 1_000, 110))

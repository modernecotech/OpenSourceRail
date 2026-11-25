"""Verify the shared OD and equal-service ring/grid comparison."""

import unittest

import numpy as np

from cities.Baghdad import (
    central_access, holistic_access, holistic_journeys, holistic_network, ring_grid_journeys, test_holistic_journeys,
)


class RingGridJourneysTests(unittest.TestCase):
    def test_wide_angle_is_an_inter_district_subset(self):
        west, south, east, north = central_access.CORE
        centre = np.array([(west + east) / 2, (south + north) / 2])
        coordinates = centre + np.array([[0, 0], [10_000, 0], [0, 12_000], [20_000, 1_000]]) / (
            holistic_network.LOCAL_METRES
        )
        population = holistic_access.Population(
            {"id": "fixture"}, coordinates, np.ones(4), np.zeros(4), np.arange(4),
            central_access._points(coordinates),
        )
        sample = holistic_journeys.sample_demand(population)
        weights = ring_grid_journeys._cohort_weights(sample)
        a, b, c, d = (sample.coordinates.tolist().index(point) for point in coordinates.tolist())
        wide = weights[ring_grid_journeys.WIDE_ANGLE_COHORT]
        self.assertGreater(weights["centre–outer"][a, b], 0)
        self.assertGreater(weights["inter-district"][b, d], 0)
        self.assertEqual(wide[b, d], 0)
        self.assertGreater(wide[b, c], 0)
        self.assertEqual(wide[b, c], wide[c, b])

    def test_distribution_distinguishes_unserved_and_three_transfers(self):
        result = ring_grid_journeys._trip_metrics(
            np.full(5, .2), np.array([300, 600, 900, 1_200, np.inf]), np.array([1, 2, 3, 4, 0]), 120,
        )
        self.assertEqual(set(result["transfer_distribution_share_of_all_pct"].values()), {20.})
        self.assertEqual(result["at_most_two_transfers_share_of_all_pct"], 60.)
        self.assertEqual(result["at_most_two_transfers_share_of_served_pct"], 75.)

    def test_same_od_and_train_km_for_loop_comparison(self):
        fixture = test_holistic_journeys.JourneyTests()
        fixture.setUp()
        ring = fixture.network({"Ring": (["A", "B", "C"], True)})
        junction = fixture.network({"West": (["A", "B"], False), "North": (["B", "C"], False)})
        kwargs = dict(reference="junction", graph=fixture.graph, population=fixture.population,
                      assumptions=fixture.assumptions)
        result = ring_grid_journeys.compare({"ring": ring, "junction": junction}, **kwargs)
        candidate = result["variants"]["ring"]
        reference = result["variants"]["junction"]
        self.assertEqual(candidate["service"]["running_train_km_day"], reference["service"]["running_train_km_day"])
        self.assertGreater(candidate["service"]["directional_headway_s"], reference["service"]["directional_headway_s"])
        self.assertLess(candidate["paired_journeys"]["candidate_minus_reference_elapsed_mean_min"], 0.)
        for cohort, metrics in candidate["cohorts"].items():
            paired = candidate["paired_cohorts"][cohort]
            self.assertEqual(metrics["served_share_pct"], paired["served_by_both_share_pct"])
            self.assertEqual(metrics["elapsed_p90_min"], paired["candidate_elapsed_p90_min"])

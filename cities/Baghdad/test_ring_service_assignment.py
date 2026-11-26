"""Check ring journey attribution against the existing evaluator."""

import unittest

import numpy as np

from . import holistic_journeys, ring_service_assignment, test_holistic_journeys


class RingServiceAssignmentTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_holistic_journeys.JourneyTests()
        self.fixture.setUp()
        self.fixture.points["D"][0] += .02
        self.network = self.fixture.network({
            "M09": (["A", "B", "D"], True),
            "M15": (["B", "C", "D"], True),
            "connector": (["A", "D"], False),
        })

    def test_ring_path_attribution_matches_the_reference_replay(self):
        fixture = self.fixture
        sample = holistic_journeys.sample_demand(fixture.population, fixture.assumptions)
        walks = holistic_journeys._street_access({"fixture": self.network}, sample, fixture.graph, 1_200)["fixture"]
        route = holistic_journeys._assignment_graph(self.network, walks, fixture.assumptions, 360)
        costs, boards, rings, rides = ring_service_assignment._trace(route, sample.weights)
        original_costs, original_boards, _, original_rides = holistic_journeys._assign(route, sample)
        np.testing.assert_array_equal(costs, original_costs)
        np.testing.assert_array_equal(boards, original_boards)
        np.testing.assert_allclose(rides, original_rides)
        coordinates = sample.coordinates.tolist()
        a, b, c = (coordinates.index(fixture.points[code]) for code in ("A", "B", "C"))
        self.assertEqual(rings[a, b], 1)
        self.assertEqual(rings[b, c], 2)
        self.assertEqual(rings[a, c], 3)
        self.assertEqual(boards[a, c], 2)

    def test_ring_priority_buys_shorter_headways_with_the_other_line_budget(self):
        fixture = self.fixture
        result = ring_service_assignment.compare(
            {"same": self.network}, reference="same", graph=fixture.graph, population=fixture.population,
            assumptions=fixture.assumptions,
        )
        uniform = result["variants"]["same"]
        priority = result["ring_priority_variants"]["same"]
        base_service, priority_service = uniform["service"], priority["service"]
        self.assertEqual(base_service["running_train_km_day"], priority_service["running_train_km_day"])
        self.assertAlmostEqual(priority_service["line_headways_s"]["M09"], 360 / 1.25)
        self.assertGreater(priority_service["line_headways_s"]["connector"], 360)
        use = uniform["ring_use"]
        self.assertGreater(use["both"]["share_of_all_pct"], 0)
        self.assertAlmostEqual(use["M09"]["share_of_all_pct"] + use["M15"]["share_of_all_pct"],
                               use["either"]["share_of_all_pct"] + use["both"]["share_of_all_pct"], places=3)
        self.assertEqual(use["both"]["share_of_all_pct"], use["both"]["at_most_two_changes_share_of_all_pct"])
        with self.assertRaisesRegex(ValueError, "positive frequency"):
            ring_service_assignment._headways(self.network, 1_000, 18, 10.)

    def test_journey_reference_can_differ_from_the_train_km_reference(self):
        fixture = self.fixture
        control = fixture.network({"baseline": (["A", "B", "C"], False)})
        result = ring_service_assignment.compare(
            {"control": control, "rings": self.network}, reference="control", paired_reference="rings",
            graph=fixture.graph, population=fixture.population, assumptions=fixture.assumptions,
            ring_frequency_multipliers=(1., 1.1),
        )
        self.assertEqual(result["assumptions"]["paired_journey_reference"], "rings")
        control_row = result["variants"]["control"]
        ring_row = result["variants"]["rings"]
        self.assertEqual(control_row["service"]["line_headways_s"]["baseline"], 360)
        self.assertEqual(ring_row["service"]["running_train_km_day"], control_row["service"]["running_train_km_day"])
        self.assertEqual(ring_row["paired_vs_reference"]["candidate_minus_reference_elapsed_mean_min"], 0.)
        self.assertNotEqual(control_row["paired_vs_reference"]["candidate_minus_reference_elapsed_mean_min"], 0.)

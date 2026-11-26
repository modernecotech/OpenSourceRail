"""Check that central access is measured consistently and selection preserves its spread."""

import unittest

import numpy as np

from . import central_ring_study as study


class CentralRingStudyTests(unittest.TestCase):
    def test_1300m_catchment_includes_its_distance_boundary(self):
        result = study._shares(np.array([1., 2., 4., 8.]), np.array([1200., 1250., 1300., 1300.1]),
                               np.ones(4, dtype=bool))
        self.assertEqual(result["1200"]["people"], 1)
        self.assertEqual(result["1300"]["people"], 7)

    def test_central_balance_survives_parallel_reduction_ranking(self):
        policy = {"access": {"walking_loss_pp": .5},
                  "network_redesign": {"max_two_change_loss_pp": .5},
                  "corridor_selection": {"served_loss_pp": .75}}
        prior = {"metro_walk_1300_pct": 76., "central_walk_1300_pct": 88., "housing_two_changes_pct": 74.,
                 "wide_trips_pct": 64., "central_ring_named_centres": 3, "central_centres_via_connection": 6,
                 "inner_walk_1300_pct": 34., "parallel_pair_km": 23., "stations": 629, "close_site_pairs": 16,
                 "worst_central_sector_pct": 60., "worst_inner_sector_pct": 0.}
        longer = prior | {"central_ring_named_centres": 5, "inner_walk_1300_pct": 56., "stations": 607,
                          "parallel_pair_km": 18.5, "worst_central_sector_pct": 49.5}
        balanced = longer | {"inner_walk_1300_pct": 54., "parallel_pair_km": 20.6, "worst_central_sector_pct": 65.}
        selected, proof = study._pick({"prior": prior, "longer": longer, "balanced": balanced},
                                      ("longer", "balanced"), policy)
        self.assertEqual(selected, "balanced")
        self.assertEqual(proof["preserves_weakest_sector"], ["balanced"])


if __name__ == "__main__":
    unittest.main()

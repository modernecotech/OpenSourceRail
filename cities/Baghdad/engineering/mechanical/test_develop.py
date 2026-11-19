"""Independent small closed-form checks for the mechanical quotation screen."""
import math
import unittest

from develop import evaluate, moving_load


class MechanicalInterfaces(unittest.TestCase):
    def test_single_axle_solution(self):
        result = moving_load([0], 10, 0.25, 80)
        self.assertEqual(result["max_live_moment_knm_sampled"], 80*10/4)
        self.assertEqual(result["max_end_reaction_kn_sampled"], 80)

    def test_tandem_maximum(self):
        # Two equal loads P separated by a: peak under a wheel when wheel
        # and load centroid straddle midspan equally, M = P(2L-a)^2 / 8L.
        result = moving_load([-1, 1], 10, 0.25, 80)
        self.assertAlmostEqual(result["max_live_moment_knm_sampled"], 80*18**2/80)
        self.assertAlmostEqual(result["max_end_reaction_kn_sampled"], 80*(2-2/10))

    def test_opposite_track_and_door_sweep(self):
        rows = evaluate()["station"]["platform_edge_schedule_per_boarding_side"]
        centres = [r["platform_x_m"] for r in rows]
        self.assertEqual(centres, [-x for x in reversed(centres)])
        self.assertEqual(len(set(centres)), 24)
        edges = [r["edge_keep_clear_x_m"] for r in rows]
        self.assertTrue(all(b[0] > a[1] for a, b in zip(edges, edges[1:])))
        self.assertEqual(edges[-1], [48.9, 51.2])

    def test_radius_sweep_preserves_pivot_locations(self):
        p = 6.4
        for row in evaluate()["train"]["curve_screen"]:
            radius = row["radius_m"]
            h = radius - row["inward_midbody_throw_mm"] / 1000
            self.assertAlmostEqual(math.hypot(h, p), radius, delta=0.00006)

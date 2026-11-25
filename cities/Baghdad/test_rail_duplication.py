"""Exercise the Baghdad rail duplication screen on controlled alignments."""

import unittest

from .holistic_network import LOCAL_METRES
from .rail_duplication import screen


def line(*metric_points, loop=False):
    origin = [44.4, 33.3]
    return {"geometry": [(origin + point / LOCAL_METRES).tolist() for point in metric_points],
            "loop": loop}


class RailDuplicationTests(unittest.TestCase):
    def test_parallel_run_uses_both_chainages_in_reverse_orientation(self):
        routes = {
            "A": line((0, 0), (10_000, 0)),
            "B": line((7000, 400), (3000, 400)),
        }
        runs = screen(routes)["runs"]
        self.assertEqual(len(runs), 1)
        run = runs[0]
        self.assertEqual(run["kind"], "nearby_parallel")
        self.assertEqual(run["chainage_m"], {"A": [3000.0, 7000.0], "B": [0.0, 4000.0]})
        self.assertEqual(run["length_m"], 4000)
        self.assertEqual(run["median_distance_m"], 400)
        self.assertEqual(run["max_distance_m"], 400)
        self.assertFalse(run["terminal_codeparture"])

    def test_common_track_and_diverging_terminal_departures(self):
        routes = {
            "A": line((0, 0), (10_000, 0)),
            "B": line((10_000, 1500), (4000, 0), (2000, 0), (0, 0)),
        }
        common, nearby = sorted(screen(routes)["runs"], key=lambda run: run["kind"])
        self.assertEqual(common["kind"], "common_alignment")
        self.assertTrue(common["terminal_codeparture"])
        self.assertAlmostEqual(common["length_m"], 4000, delta=100)
        self.assertEqual(nearby["kind"], "nearby_parallel")
        self.assertFalse(nearby["terminal_codeparture"])

    def test_crossings_near_misses_and_short_coincidence(self):
        routes = {
            "A": line((0, 0), (10_000, 0)),
            "B": line((5000, -5000), (5000, 5000)),
            "C": line((0, -750), (10_000, 750)),
            "D": line((10_200, 25), (15_000, 25)),
            "E": line((3500, 0), (5100, 0)),
        }
        result = screen(routes, pair_filter=[("B", "A"), ("A", "C"), ("A", "D"), ("A", "E")])
        self.assertEqual(result["pairs_screened"], 4)
        self.assertEqual(result["runs"], [])

    def test_exiting_separation_window_splits_runs(self):
        routes = {
            "A": line((0, 0), (14_000, 0)),
            "B": line((0, 300), (4000, 300), (5500, 1500), (8500, 1500),
                      (10_000, 300), (14_000, 300)),
        }
        runs = sorted(screen(routes)["runs"], key=lambda run: run["chainage_m"]["A"])
        self.assertEqual(len(runs), 2)
        self.assertLess(runs[0]["chainage_m"]["A"][1], 5500)
        self.assertGreater(runs[1]["chainage_m"]["A"][0], 8500)

    def test_parallel_loop_has_no_terminal(self):
        routes = {
            "A": line((0, 0), (7000, 0), (7000, 3000), (0, 3000), (0, 0), loop=True),
            "B": line((0, -200), (6500, -200)),
        }
        run, = screen(routes)["runs"]
        self.assertFalse(run["terminal_codeparture"])

    def test_bad_thresholds_and_pair_identity_fail(self):
        routes = {"A": line((0, 0), (4000, 0))}
        with self.assertRaisesRegex(ValueError, "thresholds"):
            screen(routes, common_m=1200)
        with self.assertRaisesRegex(ValueError, "distinct known lines"):
            screen(routes, pair_filter=[("A", "X")])

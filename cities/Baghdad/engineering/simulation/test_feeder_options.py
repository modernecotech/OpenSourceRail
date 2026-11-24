from math import sqrt
import unittest

from cities.Baghdad.engineering.simulation import feeder_options as options


class FeederOptionTest(unittest.TestCase):
    def test_equal_spacing_and_single_train_independent_solution(self):
        args = options.parser().parse_args(["--snapshot-spacing-km", "2.1", "--cars", "3"])
        result = options.evaluate(args)
        self.assertEqual(result["site_count"], 7)
        self.assertEqual(result["source_spacing_max_m"], 2000)
        self.assertEqual(result["normal_places_per_train"], 350)
        self.assertIsNone(result["moving_service_result"])
        feed = result["feeder"]
        # For one intact constant-power load at a tie, source droop, loop
        # on half a bay with two paths, and the contact are in series.
        ohm = feed["droop"] + (feed["outward"] + feed["return_path"])/2 + .001
        source = result["source_no_load_v"]
        volts = (source + sqrt(source**2 - 4 * ohm * result["requested_train_w"]))/2
        self.assertAlmostEqual(volts, result["minimum_live_voltage_v"], delta=.02)
        self.assertTrue(result["numerical_screen"])
        self.assertFalse(result["protection_approved"])

    def test_moving_outage_and_price_identity(self):
        args = options.parser().parse_args(["--moving", "paired8", "--cars", "3", "--condition", "combined",
                                           "--failed-site", "3", "--failed-path", "3", "--loop-resistance-factor", ".9"])
        result = options.evaluate(args)
        self.assertEqual(result["site_count"], 8)
        self.assertEqual(result["live_source_sections"], 7)
        self.assertEqual(result["failure"]["site"], 3)
        self.assertEqual(result["failure"]["path_bay"], 3)
        self.assertEqual(result["metrics"]["booked_passenger_trips"], 144)
        self.assertTrue(result["gates"]["all_workings_complete"])
        self.assertTrue(result["gates"]["dc_numerical_screen"])
        self.assertFalse(result["gates"]["thermal_ratings_verified"])
        self.assertEqual(result["price_basis"]["status"], "held")
        self.assertEqual(result["feeder"]["trunk_factor"], .9)
        self.assertLess(result["tare_train_kg"], result["loaded_train_kg"])

    def test_reject_unused_or_oversized_outage_and_layout(self):
        for condition, site, path in [("normal", 0, None), ("combined", 8, 0), ("path_out", None, 7)]:
            with self.subTest(condition=condition):
                from argparse import Namespace
                with self.assertRaises(ValueError):
                    options.outage(Namespace(condition=condition, failed_site=site, failed_path=path), 8)
        for spacing in (0, -1, float("nan"), "Infinity", "malformed"):
            with self.assertRaises(ValueError):
                options.spacing_sites(12000, spacing)

    def test_snapshot_spacing_and_explicit_computational_budget(self):
        self.assertEqual(len(options.spacing_sites(12000, "0.3")), 41)
        self.assertEqual(options.spacing_sites(12000, "13"), (0., 12000.))
        self.assertEqual(len(options.spacing_sites(12000, "0.299999999999999999999")), 42)
        with self.assertRaisesRegex(ValueError, "requires 41 sites.*budget is 40"):
            options.spacing_sites(12000, ".30", 40)
        args = options.parser().parse_args(["--snapshot-spacing-km", ".05", "--snapshot-site-budget", "241"])
        result = options.evaluate(args)
        self.assertEqual(result["site_count"], 241)
        self.assertEqual(result["source_spacing_max_m"], 50)
        self.assertEqual(result["snapshot_site_budget"], 241)


if __name__ == "__main__":
    unittest.main()

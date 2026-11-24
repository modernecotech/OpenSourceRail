import unittest
from dataclasses import replace

from cities.Baghdad.engineering.prototype import yard_offers as yard


class YardOfferTests(unittest.TestCase):
    def setUp(self):
        self.workcell = yard.reference_offer()

    def test_yard_occupation_and_release_dates(self):
        offers = [self.workcell, replace(self.workcell, cycle_hours=48),
                  replace(self.workcell, cycle_hours=48, moulds=16)]
        report = yard.report(offers, beams=80, deadline_days=11)
        results = report["comparisons"]
        for row, days in zip(results, (10+4/24, 20+4/24, 11+4/24)):
            self.assertAlmostEqual(row["finish_days"], days)
            self.assertLessEqual(row["schedule"]["peak_resource_occupation"]["mould"], row["offer"]["moulds"])
            self.assertEqual(row["schedule"]["completed_units"]["accepted"], 80)
            self.assertEqual(row["price_status"], "quote requested")
        self.assertEqual([r["meets_deadline"] for r in results], [True, False, False])

    def test_shift_windows_crew_and_yield_are_independent(self):
        offer = replace(self.workcell, moulds=50, crews=1, cycle_hours=4, pour_hours=2,
                        shift_hours=8, availability=.75, yield_rate=.8, quote_usd=4000)
        first = yard.evaluate(offer, 8)
        second = yard.evaluate(replace(offer, shifts=2), 8)
        self.assertEqual(first["attempted_castings"], 10)
        self.assertEqual(first["schedule"]["completed_units"], {"accepted": 8, "rejected": 2})
        self.assertEqual(first["schedule"]["peak_resource_occupation"]["crew"], 1)
        self.assertAlmostEqual(first["finish_days"], 3+4/24)
        self.assertAlmostEqual(second["finish_days"], 1+12/24)
        self.assertEqual(second["price_status"], "offered")
        self.assertTrue(second["finish_days"] < first["finish_days"])

    def test_constrained_and_unpriced_are_different_results(self):
        for change in [dict(crews=0), dict(availability=0), dict(moulds=0), dict(yield_rate=0),
                       dict(pour_hours=8)]:
            row = yard.evaluate(replace(self.workcell, **change), 8, 12)
            self.assertIsNone(row["finish_days"])
            self.assertFalse(row["meets_deadline"])
        valid = yard.evaluate(self.workcell, 8)
        self.assertGreater(valid["finish_days"], 0)
        self.assertIsNone(valid["capital_or_service_total_usd"])
        self.assertIsNone(valid["meets_deadline"])
        with self.assertRaises(ValueError):
            yard.evaluate(replace(self.workcell, shifts=4), 8)


if __name__ == "__main__":
    unittest.main()

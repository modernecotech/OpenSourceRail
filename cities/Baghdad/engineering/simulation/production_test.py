"""Regression checks for the source-bound factory and cash model."""

import unittest

from cities.Baghdad.engineering.simulation import production


class ProductionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = production.evaluate()
        cls.alternative = production.evaluate({
            "candidate_id": cls.reference["candidate_id"], "scenario_id": "proof-three-car-paired",
            "cars": 3, "sets": 5, "topology": "paired6", "span_m": 20, "material": "hybrid",
            "annual_train_km": 400000, "energy_kwh_per_train_km": 7, "annual_paid_journeys": 1_200_000,
        })

    def test_reference_source_cost_and_stock(self):
        data = self.reference
        self.assertAlmostEqual(data["decision_summary"]["priced_capital_base_usd"], 1124321028.464282, places=4)
        self.assertAlmostEqual(data["decision_summary"]["annual_opex_base_usd"], 13090963.123636, places=4)
        stock = data["scenarios"]["normal"]["stock"]
        self.assertEqual((stock["gross_saw_bars"], stock["gross_plate_sheets"]), (819, 44))
        for key in ("saw_blank_length_yield", "plate_area_yield"):
            self.assertGreater(stock[key], 0.5)
            self.assertLess(stock[key], 1)
        self.assertIsNone(data["localisation"]["verified_domestic_share"])
        self.assertIsNone(data["localisation"]["scope_credits"]["approved_usd"])
        self.assertIsNone(data["complete_installed_price_usd"])

    def test_disruptions_and_capacity(self):
        observed = self.reference["scenarios"]
        normal = observed["normal"]
        for row in observed.values():
            self.assertEqual(row["completed_units"]["installed_beams"], 2400)
            self.assertEqual(row["completed_units"]["pier_positions_assumed"], 2402)
            self.assertEqual(row["completed_units"]["proved_sets"], 6)
            for resource, peak in row["peak_resource_occupation"].items():
                self.assertLessEqual(peak, row["capacity"][resource])
            self.assertLessEqual(row["peak_beam_staging_reserved"], row["capacity"]["civil-stock-position"])
        for key in ("delayed-material", "reduced-capacity", "rejected-first-article"):
            self.assertGreater(observed[key]["last_completion_workday"], normal["last_completion_workday"])
        self.assertEqual(observed["rejected-first-article"]["completed_units"]["rejected_articles"], 1)
        self.assertGreater(observed["rejected-first-article"]["stock"]["gross_saw_bars"],
                           normal["stock"]["gross_saw_bars"])

    def test_cash_and_alternative_identity(self):
        alt = self.alternative
        self.assertNotEqual(alt["evaluation_id"], self.reference["evaluation_id"])
        self.assertEqual((alt["quantities"]["cars"], alt["quantities"]["beams"], alt["quantities"]["grid_sites"]),
                         (15, 1200, 6))
        self.assertEqual(alt["scenarios"]["normal"]["completed_units"]["delivered_cars"], 15)
        lots = {row["lot_id"]: row for row in alt["priced_lots"]}
        self.assertNotIn("traction-sites", lots)
        self.assertIn("six-site-parallel", lots)
        self.assertEqual(lots["opex-power"]["quantity"], 2.8)
        for receipt in (self.reference, alt):
            data = receipt["cash"]
            for row in data["profiles"].values():
                self.assertEqual(sum(year["opex_usd"] > 0 for year in row["cash_by_year"]), 30)
                self.assertAlmostEqual(sum(year["capital_usd"] for year in row["cash_by_year"]), row["capital_usd"], places=4)
            quantiles = data["sensitivity"]["priced_30y_pv_usd"]
            self.assertEqual(quantiles, sorted(quantiles))

    def test_mixed_sources_and_unidentified_revisions_are_refused(self):
        with self.assertRaisesRegex(ValueError, "pinned"):
            production.evaluate({"candidate_id": "different"})
        with self.assertRaisesRegex(ValueError, "scenario_id"):
            production.evaluate({"sets": 5, "cars": 6})
        self.assertEqual(self.reference["evaluation_id"], production.evaluate()["evaluation_id"])


if __name__ == "__main__":
    unittest.main()

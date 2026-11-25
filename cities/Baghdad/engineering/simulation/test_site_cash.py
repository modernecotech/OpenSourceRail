"""Regressions for adding GIS planning allowances to candidate-bound cash."""

from copy import deepcopy
import unittest

from cities.Baghdad.engineering.simulation import assumption_audit, audit_production, production, site_cash


class SiteCashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = assumption_audit.audit()
        cls.expected_prices = {"low": 1_000_000, "base": 2_000_000, "high": 3_000_000}

    def test_cash_replaces_feeder_scope_and_carries_one_site_allowance(self):
        site = audit_production.make_lot(
            "simulated-drainage-installation", site_cash.OPENING, 1000, "metres",
            self.expected_prices, "Test site allowance"
        )
        site["alignment_id"] = self.audit["alignment"]["alignment_id"]
        empty = dict.fromkeys(site_cash.LAYOUTS, [])
        baseline = site_cash.evaluate(self.audit, empty)
        revised = site_cash.evaluate(self.audit, dict.fromkeys(site_cash.LAYOUTS, [site]))
        for name in site_cash.LAYOUTS:
            with self.subTest(layout=name):
                model = self.audit["production"][name]
                row = revised["layouts"][name]
                lot = {item["lot_id"]: item for item in row["lots"]}
                self.assertIsNone(next(item for item in model["pricings"]
                                       if item["lot_id"] == "revised-feeder-package")["usd"])
                self.assertEqual(lot["revised-feeder-package"]["usd"]["base"],
                                 self.audit["feeder_price_sensitivities"][name]["cases"]["base"]
                                 ["known_rail_side_direct_subtotal_usd"])
                self.assertEqual(lot["simulated-feeder-renewal-protection"]["year"], 15)
                self.assertEqual(lot["simulated-feeder-renewal-line-power"]["year"], 25)
                self.assertEqual(lot["offsite-feed"]["quantity"], model["quantities"]["grid_sites"])
                multiplier = (1 + production.OPENING_TEST_RATE + production.OPENING_DESIGN_RATE) * (
                    1 + production.OPENING_CONTINGENCY_RATE
                )
                for case in production.PRICES:
                    first = baseline["layouts"][name]["cash"]["profiles"][case]
                    second = row["cash"]["profiles"][case]
                    self.assertAlmostEqual(second["capital_usd"] - first["capital_usd"],
                                           self.expected_prices[case] * multiplier, places=5)
                    self.assertEqual(second["annual_opex_usd"], first["annual_opex_usd"])
                    self.assertGreater(second["renewals_30y_undiscounted_usd"], 0)
                self.assertEqual(row["remaining_unpriced_lots"], [])
        self.assertTrue(revised["service_comparison"]["ordinary_service_comparable"])
        self.assertFalse(revised["service_comparison"]["matched_through_required_duties"])

    def test_reject_other_candidate_and_duplicate_lots(self):
        wrong = audit_production.make_lot(
            "drainage", site_cash.OPENING, 1, "site", self.expected_prices, "Test site allowance"
        )
        wrong["alignment_id"] = "another-corridor"
        with self.assertRaisesRegex(ValueError, "another Airport alignment"):
            site_cash.evaluate(self.audit, dict.fromkeys(site_cash.LAYOUTS, [wrong]))
        wrong.pop("alignment_id")
        wrong["lot_id"] = "revised-feeder-package"
        with self.assertRaisesRegex(ValueError, "duplicates"):
            site_cash.evaluate(self.audit, dict.fromkeys(site_cash.LAYOUTS, [wrong]))

    def test_reject_stale_feeder_rates(self):
        stale = deepcopy(self.audit)
        stale["feeder_price_sensitivities"]["paired6"]["cases"]["base"]["rail_side_annual_upkeep_usd"] += 1
        with self.assertRaisesRegex(ValueError, "Feeder sensitivity record identity"):
            site_cash.evaluate(stale, dict.fromkeys(site_cash.LAYOUTS, []))


if __name__ == "__main__":
    unittest.main()

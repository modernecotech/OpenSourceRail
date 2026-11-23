import copy
import unittest

from .sourcing import compare_lot, demonstration


class CompetitionTests(unittest.TestCase):
    def setUp(self):
        self.lot = dict(lot_id="trial", quantity=6, unit="sets", price_period="one-time",
                        low_usd=900, base_usd=1000, high_usd=1100)
        self.packet = dict(lots=[self.lot], candidate_id="physical", evaluation_id="price")
        self.offer = dict(candidate_id="physical", evaluation_id="price", lot_id="trial", supplier="A",
                          quotation="Q-A", quantity=6, unit="sets", currency="USD", direct_usd=920,
                          annual_upkeep_usd=10, renewals_usd={"20": 100}, exclusions=[], evidence_kind="software-fixture")

    def compare(self, **kwargs):
        return compare_lot(self.packet, "trial", [dict(self.offer, **kwargs)])["offers"][0]

    def test_finance_and_coverage(self):
        expected = 920 + sum(10 / 1.04**y for y in range(1, 31)) + 100 / 1.04**20
        result = self.compare()
        self.assertEqual(result["pv_30y_4pct_usd"], round(expected, 2))
        self.assertEqual(result["difference_from_base_usd"], -80)
        self.assertEqual(result["estimate_band_position"], "within")
        for terms in (None, ["Delivery excluded"]):
            with self.subTest(terms=terms):
                partial = self.compare(exclusions=terms)
                self.assertIsNone(partial["pv_30y_4pct_usd"])
                self.assertIsNone(partial["difference_from_base_usd"])
                self.assertFalse(partial["comparable_direct"])

    def test_quantity_sensitivity_uses_the_full_requested_quantity(self):
        self.lot.update(quantity=6, low_usd=500, high_usd=2400, scenario_quantities={"low": 5, "base": 6, "high": 12})
        result = compare_lot(self.packet, "trial", [dict(self.offer, direct_usd=1800)])
        self.assertEqual(result["period_benchmark_usd"]["high"], 2400)
        self.assertEqual(result["enquiry_quantity_benchmark_usd"]["high"], 1200)
        self.assertEqual(result["offers"][0]["estimate_band_position"], "above")

    def test_missing_versus_zero(self):
        for unknown in (dict(annual_upkeep_usd=None), dict(renewals_usd=None)):
            result = self.compare(**unknown)
            self.assertIsNone(result["pv_30y_4pct_usd"])
            self.assertTrue(result["comparable_direct"])
        result = self.compare(annual_upkeep_usd=0, renewals_usd={})
        self.assertEqual(result["pv_30y_4pct_usd"], 920)
        self.lot.update(low_usd=None, base_usd=None, high_usd=None)
        self.assertIsNone(self.compare()["difference_from_base_usd"])

    def test_identity_units_and_invalid_input(self):
        for changed in ({"candidate_id": "other"}, {"evaluation_id": "next"}, {"lot_id": "other"},
                        {"quantity": 1}, {"unit": "other"}, {"currency": "IQD"}, {"evidence_kind": "x"},
                        {"direct_usd": True}, {"annual_upkeep_usd": -1}, {"direct_usd": float("nan")},
                        {"renewals_usd": {"31": 1}}, {"exclusions": "none"}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                self.compare(**changed)

    def test_distinct_parties_deterministic_result(self):
        result = demonstration(self.packet, None)
        self.assertEqual(result["scope_comparable_suppliers"], 2)
        self.assertEqual(result["direct_spread_usd"], 60)
        a,b,c = result["offers"]
        self.assertLess(a["direct_usd"], b["direct_usd"])
        self.assertLess(b["pv_30y_4pct_usd"], a["pv_30y_4pct_usd"])
        self.assertIsNone(c["pv_30y_4pct_usd"])
        self.assertIsNone(result["selection"])
        self.assertEqual(demonstration(copy.deepcopy(self.packet), "trial"), result)
        with self.assertRaises(ValueError):
            compare_lot(self.packet, "trial", [self.offer, self.offer])
        with self.assertRaises(ValueError):
            compare_lot(self.packet, "trial", [self.offer, dict(self.offer, supplier="B", quotation="QB",
                                                               evidence_kind="supplier-offer")])

    def test_periodic_prices_counted_once(self):
        self.lot["price_period"] = "annual"
        annual = self.compare(annual_upkeep_usd=0, renewals_usd={})
        self.assertEqual(annual["pv_30y_4pct_usd"], round(sum(920 / 1.04**y for y in range(1, 31)), 2))
        with self.assertRaises(ValueError):
            self.compare()
        self.lot["price_period"] = "scheduled"
        scheduled = self.compare(annual_upkeep_usd=0, renewals_usd={"20": 920})
        self.assertEqual(scheduled["pv_30y_4pct_usd"], round(920 / 1.04**20, 2))
        with self.assertRaises(ValueError):
            self.compare(annual_upkeep_usd=0, renewals_usd={})
        self.lot["operating_year"] = 15
        with self.assertRaises(ValueError):
            self.compare(annual_upkeep_usd=0, renewals_usd={"20": 920})

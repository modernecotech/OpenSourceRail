"""Buyer offer comparisons retain unawarded competing supplier returns."""

from copy import deepcopy
import unittest

from cities.Baghdad.engineering.simulation import audit_offers, audit_production


class BuyerOfferTests(unittest.TestCase):
    def setUp(self):
        self.context = {"feeder": {"name": "paired6"}, "alignment_id": "alignment-a", "motion_evaluation_id": "duty-a"}
        self.rows = [
            dict(audit_production.make_lot("fleet", "opening-direct", 8, "trainsets",
                                            {"low": 90, "base": 110, "high": 130}, "estimate"),
                 current_unit="trainsets"),
            dict(audit_production.make_lot("revised-feeder-package", "opening-direct", 6, "DC source groups",
                                            None, "unpriced"), current_unit="DC source groups"),
        ]
        audit_production.replace_offers(self.rows, self.context, ())
        self.a = self.offer("quote-a", self.rows[0]["scope_id"], 105)
        self.b = self.offer("quote-b", self.rows[0]["scope_id"], 115)
        self.c = self.offer("quote-c", self.rows[1]["scope_id"], 80)
        self.award = dict(scope_id=self.b["scope_id"], offer_id=self.b["offer_id"], buyer_award_reference="ERP/PO-123")

    @staticmethod
    def offer(name, scope, price):
        return dict(offer_id=name, scope_id=scope, price_usd=price, supplier=f"supplier {name}",
                    buyer_review_reference=f"technical review {name}", offer_sha256="d"*64,
                    claimed_domestic_value_usd=None)

    def document(self, offers, awards=()):
        return dict(schema=audit_offers.SCHEMA, layouts={
            "paired6": dict(offers=list(offers), awards=list(awards)),
            "radial30": dict(offers=[], awards=[]),
        })

    def choose(self, doc):
        return audit_offers.choices(doc, "paired6", self.rows, self.context)

    def test_all_bids_remain_visible_and_only_explicit_awards_replace_prices(self):
        original = deepcopy(self.rows)
        selected, comparisons = self.choose(self.document([self.a, self.b, self.c], [self.award]))
        self.assertEqual(selected, [self.b])
        self.assertEqual([entry["status"] for entry in comparisons], ["eligible", "awarded", "eligible"])
        self.assertEqual([entry["difference_vs_base_usd"] for entry in comparisons], [-5, 5, None])
        self.assertEqual([entry["difference_vs_lowest_offer_usd"] for entry in comparisons], [0, 10, 0])
        self.assertEqual(comparisons[1]["buyer_award_reference"], "ERP/PO-123")
        self.assertEqual(self.rows, original)
        self.assertEqual(self.choose(self.document([self.a, self.b]))[0], [])
        raw = [{key: value for key, value in row.items() if key not in audit_offers.PRICING_OUTPUT_FIELDS}
               for row in self.rows]
        replaced, = audit_production.replace_offers(raw, self.context, selected)
        self.assertEqual(replaced["displaced_usd"]["base"], 110)
        self.assertEqual(raw[0]["usd"]["base"], 115)
        self.assertIsNone(raw[1]["usd"])

    def test_wrong_layout_stale_baseline_duplicate_bid_and_duplicate_award_refused(self):
        stale = dict(self.a, scope_id="wrong scope")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.choose(self.document([stale]))
        with self.assertRaisesRegex(ValueError, "unique offer ID"):
            self.choose(self.document([self.a, self.a]))
        with self.assertRaisesRegex(ValueError, "one eligible offer"):
            self.choose(self.document([self.a, self.b], [self.award, self.award]))
        with self.assertRaisesRegex(ValueError, "one eligible offer"):
            self.choose(self.document([self.a], [self.award]))
        self.rows[0]["usd"]["base"] = 9
        with self.assertRaisesRegex(ValueError, "unchanged baseline"):
            self.choose(self.document([self.a]))
        with self.assertRaisesRegex(ValueError, "matching feeder"):
            audit_offers.choices(self.document([self.a]), "radial30", self.rows, self.context)

    def test_reuses_complete_offer_validation(self):
        with self.assertRaisesRegex(ValueError, "document SHA-256"):
            self.choose(self.document([dict(self.a, offer_sha256="bad")]))
        with self.assertRaisesRegex(ValueError, "claimed origin value"):
            self.choose(self.document([dict(self.a, claimed_domestic_value_usd=10_000)]))


if __name__ == "__main__":
    unittest.main()

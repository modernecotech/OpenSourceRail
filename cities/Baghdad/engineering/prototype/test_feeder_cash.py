import unittest
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from cities.Baghdad import airport_integration, airport_opening
from cities.Baghdad.engineering.commissioning import feeder
from cities.Baghdad.engineering.prototype import car, feeder_cash


class FeederCashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = airport_integration.build()
        cls.opening = car.build(parent)["opening"]
        cls.service = parent["service"]
        cls.cfg = airport_opening.opening_inputs()[0]

    def offer(self, topology, direct, annual, renewals):
        f = feeder.return_form(self.opening, topology)
        f.update(record_kind="engineering-sensitivity", document_revision="Software fixture",
                 coverage="Entire topology, synthetic price test")
        f["price_2026_usd"] = {
            "installed_direct": dict.fromkeys(feeder.PRICE_ITEMS, direct),
            "annual_upkeep": annual, "renewals_by_year": renewals,
        }
        return f

    def compare(self, radial, alt, **kwargs):
        return feeder_cash.compare(self.opening, self.service, self.cfg, radial, alt, **kwargs)

    def test_price_difference_finances_only_the_changed_scope(self):
        radial = self.offer("priced_radial", 2e6, 3e5, {"15": 1e6})
        alt = self.offer("six_site_parallel", 1e6, 1e5, {"10": 2e5})
        result = self.compare(radial, alt)
        cash = result["annual_cash_difference_usd_m"]
        self.assertEqual(len(cash), 33)
        self.assertEqual(result["installed_difference_usd_m"], -4)
        self.assertIsNone(result["absolute_repriced_opening_capital_usd_m"])
        for r, share in zip(cash[:3], (.20, .45, .35), strict=True):
            self.assertAlmostEqual(r["capital"], -4 * share)
        self.assertAlmostEqual(sum(r["operations"] for r in cash), -.2 * 30)
        self.assertAlmostEqual(sum(r["borrowing"] for r in cash), -2)
        self.assertAlmostEqual(sum(r["principal"] for r in cash), -2)
        self.assertAlmostEqual(cash[-1]["closing_debt"], 0)
        self.assertAlmostEqual(cash[12]["renewals"], .2)
        self.assertAlmostEqual(cash[17]["renewals"], -1)
        for r in cash:
            self.assertAlmostEqual(r["public_cash_after_fares"], r["capital"] - r["borrowing"]
                + r["interest"] + r["principal"] + r["operations"] + r["renewals"])
        expected_pv = -4 + sum(-.2/1.04**y for y in range(1,31)) + .2/1.04**10 - 1/1.04**15
        self.assertAlmostEqual(result["whole_life_difference_30y_at_4pct_usd_m"], expected_pv)

    def test_incomplete_price_and_explicit_zero(self):
        radial = self.offer("priced_radial", 0, 0, {})
        alt = self.offer("six_site_quotation", 0, 0, {})
        self.assertTrue(all(r["buyer_cash"] == 0 for r in self.compare(radial, alt)["annual_cash_difference_usd_m"]))
        partial = deepcopy(alt)
        partial["price_2026_usd"]["renewals_by_year"] = None
        self.assertIsNone(self.compare(radial, partial)["annual_cash_difference_usd_m"])
        with self.assertRaises(ValueError):
            self.compare(alt, radial)
        alt["scope"]["rectifier_sites"] = 5
        with self.assertRaises(ValueError):
            self.compare(radial, alt)

    def test_offsite_documented_difference_applied_once(self):
        radial = self.offer("priced_radial", 1, 0, {})
        alt = self.offer("six_site_parallel", 1, 0, {})
        review = feeder_cash.scope_form(radial, alt)
        with TemporaryDirectory() as directory:
            for name in ("r.txt", "a.txt", "scope.txt"):
                data = f"Synthetic test only: {name}".encode()
                (Path(directory)/name).write_bytes(data)
                review["documents"][name] = {"issuer":"Test", "date":"2026-11-23", "sha256":sha256(data).hexdigest()}
            review.update(bid_document={"radial":"r.txt", "alternative":"a.txt"},
                          scope_review_document="scope.txt", offsite_boundary="excluded from both bids",
                          separate_installed_offsite_usd={"radial":30e6, "alternative":6e6})
            out = self.compare(radial, alt, scope_review=review, directory=directory)
            self.assertEqual(out["installed_difference_usd_m"], -24)
            self.assertAlmostEqual(sum(r["capital"] for r in out["annual_cash_difference_usd_m"]), -24)
            review["offsite_boundary"] = "included in both bids"
            with self.assertRaisesRegex(ValueError,"only once"):
                self.compare(radial, alt, scope_review=review, directory=directory)
            review["separate_installed_offsite_usd"] = None
            self.assertEqual(self.compare(radial, alt, scope_review=review, directory=directory)["installed_difference_usd_m"], 0)
            alt["price_2026_usd"]["annual_upkeep"] = 1
            with self.assertRaisesRegex(ValueError, "exact two"):
                self.compare(radial, alt, scope_review=review, directory=directory)


if __name__ == "__main__":
    unittest.main()

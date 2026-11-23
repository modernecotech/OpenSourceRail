from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cities.Baghdad import airport_integration, airport_opening
from cities.Baghdad.engineering.prototype import car, commercial


class CommercialReturnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = airport_integration.build()
        cls.article, _ = car.artifacts(cls.parent)
        cls.opening = cls.article["opening"]
        cls.cfg = airport_opening.opening_inputs()[0]
        cls.service = cls.parent["service"]

    def assess(self, form=None, directory=None):
        return commercial.assess(self.opening, self.service, self.cfg, form, directory)

    def submit(self, directory):
        f = commercial.form(self.opening)
        attachment = Path(directory) / "trial.txt"
        attachment.write_bytes(b"Software fixture. Synthetic figures only.\n")
        f["documents"][attachment.name] = {
            "issuer": "Software test",
            "date": "2026-11-23",
            "sha256": sha256(attachment.read_bytes()).hexdigest(),
        }
        return f, attachment

    def test_empty_return_reproduces_all_33_phased_cash_rows(self):
        expected = self.article["finance"]["phased_cash"]["annual"]
        actual = self.assess()
        self.assertEqual(len(expected), 33)
        for previous, revised in zip(expected, actual["annual_cash"], strict=True):
            for key in previous:
                self.assertAlmostEqual(revised[key], previous[key], places=9)
            self.assertIsNone(revised["documented_allocation_usd_m"])
            self.assertIsNone(revised["uncovered_usd_m"])
        self.assertIsNone(actual["funded_opening_capital_usd_m"])
        self.assertFalse(actual["authorised_for_purchase"])

    def test_site_and_fleet_replacements_displace_each_original_scope_once(self):
        with TemporaryDirectory() as directory:
            f, attachment = self.submit(directory)
            scope = "Terminal and depot turnout premiums"
            original = self.opening["iraq_site_estimate"]["scenarios"]["base"]["items"][scope]
            f["site_replacements"][scope] = dict(
                document=attachment.name, unit="turnouts", quantity=4, unit_usd=1e6
            )
            old_fleet = self.opening["scopes_usd_m"]["Fleet, including spare sets"]
            f["supplier_prices"]["lots"]["trainsets"] = dict(
                direct_price_usd_m=old_fleet + 3,
                annual_maintenance_change_usd_m=0.25,
                renewal_changes_usd_m={"15": 0.5},
                review_reference=attachment.name,
            )
            result = self.assess(f, directory)
        rates = self.cfg["capital_rates_usd_m"]
        factor = (1 + rates["design_fraction"] + rates["testing_fraction"]) * (
            1 + rates["project_allowance_fraction"]
        )
        base = self.assess()
        self.assertAlmostEqual(
            result["priced_capital_usd_m"] - base["priced_capital_usd_m"],
            (4 - original["direct_usd_m"] + 3) * factor,
        )
        self.assertAlmostEqual(
            sum(x["capital"] for x in result["annual_cash"]), result["priced_capital_usd_m"]
        )
        self.assertAlmostEqual(sum(x["borrowing"] - x["principal"] for x in result["annual_cash"]), 0)
        self.assertAlmostEqual(
            sum(
                x["operations"] - y["operations"] for x, y in zip(result["annual_cash"], base["annual_cash"])
            ),
            7.5,
        )
        self.assertAlmostEqual(
            sum(x["renewals"] - y["renewals"] for x, y in zip(result["annual_cash"], base["annual_cash"])),
            0.5,
        )

    def test_sample_od_fares_and_explicit_zero_allocations(self):
        with TemporaryDirectory() as directory:
            f, attachment = self.submit(directory)
            first, last = self.service["patterns"][0][:: len(self.service["patterns"][0]) - 1]
            f["demand_survey"] = dict(
                document=attachment.name,
                sample_date_from="2026-11-20",
                sample_date_to="2026-11-22",
                observed_days=2,
                od=[{"from": first["id"], "to": last["id"], "all": 25, "paying": 20}],
                net_usd_per_paid_journey=0.5,
            )
            f["public_allocations_usd_m"] = {
                "3": {"document": attachment.name, "amount": 0},
                "4": {"document": attachment.name, "amount": 150},
            }
            result = self.assess(f, directory)
            cash = result["annual_cash"]
            self.assertEqual(result["demand_survey"]["annual_passenger_km"], 25 * 12 * 365 / 2)
            self.assertEqual(result["annual_net_fares_usd_m"], 20 * 0.5 * 365 / 2 / 1e6)
            self.assertAlmostEqual(sum(x["net_fares"] for x in cash), result["annual_net_fares_usd_m"] * 30)
            self.assertEqual(cash[2]["uncovered_usd_m"], cash[2]["public_cash_after_fares"])
            self.assertEqual(cash[3]["uncovered_usd_m"], max(0, cash[3]["public_cash_after_fares"] - 150))
            self.assertIsNone(cash[4]["uncovered_usd_m"])
            f["demand_survey"]["od"][0].update(all=0, paying=0)
            self.assertEqual(self.assess(f, directory)["annual_net_fares_usd_m"], 0.0)

    def test_malformed_submissions_and_cross_candidate_inputs_rejected(self):
        with TemporaryDirectory() as directory:
            form, attachment = self.submit(directory)
            for change in (
                {"opening_evaluation_id": "old"},
                {"candidate_id": self.parent["opening"]["candidate_id"]},
                {"supplier_prices": None},
                {"public_allocations_usd_m": {"0": {"amount": 1, "document": "trial.txt"}}},
                {"public_allocations_usd_m": {"3": {"amount": False, "document": "trial.txt"}}},
                {"public_allocations_usd_m": {"3": {"amount": 0, "document": []}}},
                {
                    "site_replacements": {
                        "Terminal and depot turnout premiums": {
                            "quantity": 0.5,
                            "unit": "turnouts",
                            "document": "trial.txt",
                            "unit_usd": 33,
                        }
                    }
                },
                {"demand_survey": {"document": "absent"}},
                {"documents": {"../moved": form["documents"]["trial.txt"]}},
            ):
                with self.subTest(change=change), self.assertRaises(ValueError):
                    self.assess({**form, **change}, directory)
            attachment.write_text("Changed")
            with self.assertRaises(ValueError):
                self.assess(form, directory)
            attachment.unlink()
            with self.assertRaises(ValueError):
                self.assess(form, directory)
            target = Path(directory) / "alternate"
            target.write_bytes(b"Software fixture. Synthetic figures only.\n")
            attachment.symlink_to(target)
            with self.assertRaises(ValueError):
                self.assess(form, directory)
        service = deepcopy(self.service)
        service["patterns"][0][0]["fraction"] = 0.75
        with self.assertRaises(ValueError):
            commercial.assess(self.opening, service, self.cfg)

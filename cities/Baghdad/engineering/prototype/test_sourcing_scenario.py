from copy import deepcopy
from decimal import Decimal
import unittest

from deployment.erpnext.apps.osr_erpnext.osr_erpnext.sourcing_comparison import compare_lot
from deployment.erpnext.apps.osr_erpnext.osr_erpnext.sourcing_contract import digest
from deployment.erpnext.apps.osr_erpnext.osr_erpnext.sourcing_scenario import opening_scenario

from .sourcing_estimates import estimate_lots


class OpeningScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = estimate_lots()
        cls.lots = {row["lot_id"]: row for row in cls.packet["lots"]}

    def offer(self, lot_id="fleet", amount=53_000_000, *, rfq=None, quotation=None,
              project="BGHD-AIRPORT", as_of="2026-11-23", valid_until="2026-12-10",
              recorded_on="2026-11-18", status="received", exclusions=None,
              kind="supplier-offer"):
        lot = self.lots[lot_id]
        rfq = rfq or "Test-RFQ-" + lot_id
        quotation = quotation or "Test-Quote-" + lot_id
        supplier = "Test Supplier"
        quote = {
            "candidate_id": self.packet["candidate_id"], "evaluation_id": self.packet["evaluation_id"],
            "lot_id": lot_id, "supplier": supplier, "quotation": quotation,
            "quantity": lot["quantity"], "unit": lot["unit"],
            "currency": "USD", "direct_usd": amount, "annual_upkeep_usd": None,
            "renewals_usd": None, "exclusions": [] if exclusions is None else exclusions,
            "evidence_kind": kind,
        }
        trace = {
            "supplier": supplier, "quotation": quotation, "status": status,
            "recorded_on": recorded_on, "valid_until": valid_until,
        }
        response = {
            "project": project, "rfq": rfq, "rfq_docstatus": 1, "as_of": as_of,
            "lot_id": lot_id, "suppliers": [trace], "unattributed_quotations": [],
            "comparison": compare_lot(self.packet, lot_id, [quote]),
        }
        return response, quotation

    def test_matched_comparable_replacements_and_allowances(self):
        fleet = self.offer()
        stations = self.offer("stations", 70_000_000)
        result = opening_scenario(self.packet, [fleet, stations])
        self.assertEqual(result, opening_scenario(self.packet, [stations, fleet]))
        self.assertAlmostEqual(
            result["original_central_opening_usd"],
            self.packet["subtotal_opening_priced_allowances"]["base_usd"], places=2,
        )
        delta = Decimal(53_000_000 - 50_880_000 + 70_000_000 - 78_000_000)
        self.assertEqual(result["direct_delta_usd"], float(delta))
        self.assertEqual(result["opening_delta_usd"], float(delta * Decimal("1.326")))
        self.assertEqual(result["revised_central_direct_usd"], 842_024_244.69)
        self.assertEqual(result["revised_central_opening_usd"], 1_116_524_148.46)
        self.assertEqual(result["revised_central_allowances_usd"]["integrated-test"], 21_050_606.12)
        self.assertEqual(result["replacements"][0]["comparison_receipt_sha256"], digest(fleet[0]))
        self.assertEqual(result["replacements"][0]["comparison_holds"], ["annual upkeep unquoted", "renewals unquoted"])
        self.assertEqual(result["scenario_id"], digest({key: value for key, value in result.items() if key != "scenario_id"}))
        self.assertFalse(result["procurement_authorized"])
        self.assertEqual(result["physical_acceptance"], "open")
        self.assertIsNone(result["complete_opening_cost_usd"])

    def test_full_explicit_coverage_and_single_credit_at_enquiry_quantity(self):
        direct_lots = self.packet["additive_groups"]["opening-direct"]["lot_ids"]
        selections = [self.offer(lot_id, round(self.lots[lot_id]["base_usd"], 2)) for lot_id in direct_lots]
        result = opening_scenario(self.packet, selections)
        self.assertEqual(len(result["replacements"]), len(direct_lots))
        row = next(replacement for replacement in result["replacements"] if replacement["lot_id"] == "extra-foundation")
        shaft = self.lots["extra-foundation"]
        self.assertEqual(row["quantity"], shaft["quantity"])
        self.assertEqual(row["displaced_central_direct_usd"], round(shaft["base_usd"], 2))
        self.assertEqual(result["replacements"][0]["as_of"], "2026-11-23")

    def test_holds_duplicate_mixed_and_invalid(self):
        fleet = self.offer()
        for selections in (
            [], [fleet, fleet], [fleet, self.offer(rfq="Different-RFQ", quotation="Other")],
            [fleet, self.offer("stations", rfq=fleet[0]["rfq"])],
            [fleet, self.offer("stations", quotation=fleet[1])],
            [fleet, self.offer("stations", project="Other Project")],
            [fleet, self.offer("stations", as_of="2026-11-24")],
            [self.offer(valid_until="2026-11-22")],
            [self.offer(recorded_on="2026-11-24")],
            [self.offer(status="integrity-hold")],
            [self.offer(exclusions=["Delivery"])], [self.offer(kind="software-fixture")],
            [self.offer("opex-power")], [self.offer("pilot-car")], [self.offer("six-site-parallel")],
            [self.offer("integrated-test")], [self.offer("tax-and-duties")],
        ):
            with self.subTest(selections=selections), self.assertRaises(ValueError):
                opening_scenario(self.packet, selections)

    def test_source_tampering_and_mixed_estimate_rejected(self):
        response, quotation = self.offer()
        for field in ("candidate_id", "estimate_evaluation_id"):
            with self.subTest(field=field):
                altered = deepcopy(response)
                altered["comparison"][field] = "f" * 64
                altered["comparison"].pop("comparison_id")
                altered["comparison"]["comparison_id"] = digest(altered["comparison"])
                with self.assertRaisesRegex(ValueError, "does not match"):
                    opening_scenario(self.packet, [(altered, quotation)])
        altered = deepcopy(response)
        altered["comparison"]["offers"][0]["direct_usd"] = 1
        with self.assertRaisesRegex(ValueError, "does not match"):
            opening_scenario(self.packet, [(altered, quotation)])
        packet = deepcopy(self.packet)
        packet["subtotal_opening_priced_allowances"]["base_usd"] += 1
        packet.pop("evaluation_id")
        packet["evaluation_id"] = digest(packet)
        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            opening_scenario(packet, [(response, quotation)])


if __name__ == "__main__":
    unittest.main()

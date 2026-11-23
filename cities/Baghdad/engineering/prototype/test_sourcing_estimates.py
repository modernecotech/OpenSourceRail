from hashlib import sha256
from io import BytesIO
import json
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

from cities.Baghdad.engineering.prototype.sourcing_estimates import PACKET, estimate_lots
from engineering.outline.baghdad_system import _id


class SourcingEstimateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = estimate_lots()
        cls.lots = {row["lot_id"]: row for row in cls.result["lots"]}

    def test_deterministic_candidate_sources_and_prices(self):
        result = self.result
        self.assertEqual(estimate_lots(PACKET), result)
        self.assertEqual(result["evaluation_id"], _id({
            key: value for key, value in result.items() if key != "evaluation_id"
        }))
        self.assertEqual(len(self.lots), len(result["lots"]))
        for lot_id, row in self.lots.items():
            with self.subTest(lot=lot_id):
                self.assertLessEqual(set(row["sources"]), set(result["sources"]))
                self.assertTrue(all(result["sources"][key]["url"].startswith("https://") for key in row["sources"]))
                self.assertGreater(row["quantity"], 0)
                self.assertEqual(round(row["quantity"], 3), row["quantity"])
                self.assertIsNone(row["firm_price_usd"])
                self.assertEqual(row["physical_acceptance"], "open")
                self.assertTrue(all(row[key] for key in ("basis", "exclusions", "deliverables", "unit")))
                for relation in ("overlaps_lot_ids", "alternative_to_lot_ids"):
                    self.assertLessEqual(set(row.get(relation, ())), set(self.lots) - {lot_id})
                low, base, high = (row[k] for k in ("low_usd", "base_usd", "high_usd"))
                if low is None:
                    self.assertIsNone(base)
                    self.assertIsNone(high)
                else:
                    self.assertGreater(low, 0)
                    self.assertLessEqual(low, base)
                    self.assertLessEqual(base, high)
        self.assertFalse(result["authorised_for_purchase"])
        self.assertIsNone(result["funded_opening_capital_usd"])
        self.assertIsNone(result["complete_opening_cost_usd"])

    def test_opening_scenarios_annual_operations_and_renewals_reconcile(self):
        with ZipFile(PACKET) as archive:
            opening = json.loads(archive.read("opening.json"))
            cash = json.loads(archive.read("cash.json"))
        result = self.result
        groups = result["additive_groups"]
        self.assertEqual(result["candidate_id"], opening["candidate_id"])
        self.assertEqual(result["opening_evaluation_id"], opening["evaluation_id"])
        self.assertEqual(result["commercial_evaluation_id"], cash["evaluation_id"])
        self.assertAlmostEqual(result["subtotal_opening_priced_allowances"]["base_usd"] / 1e6, cash["priced_capital_usd_m"])
        for cap, ops in (("low", "upside"), ("base", "central"), ("high", "downside")):
            price = cap + "_usd"
            self.assertAlmostEqual(
                result["subtotal_opening_priced_allowances"][price] / 1e6,
                opening["iraq_site_estimate"]["scenarios"][cap]["capital_usd_m"],
            )
            self.assertAlmostEqual(
                groups["first-full-year-operations"][price] / 1e6,
                opening["iraq_operations"]["cases"][ops]["opex_usd_m"],
            )
            self.assertAlmostEqual(
                groups["renewal-schedule"][price] / 1e6,
                sum(event["usd_m"] for event in opening["renewals"]),
            )
        self.assertEqual(groups["first-full-year-operations"]["price_period"], "annual")
        self.assertEqual(groups["renewal-schedule"]["price_period"], "scheduled")
        self.assertEqual({self.lots[key]["operating_year"] for key in groups["renewal-schedule"]["lot_ids"]}, {15, 25})
        shaft = self.lots["extra-foundation"]
        self.assertEqual(shaft["quantity"], round(shaft["source_quantity"], 3))
        self.assertEqual(shaft["source_quantity"], shaft["scenario_quantities"]["base"])
        self.assertNotEqual(shaft["scenario_quantities"]["low"], shaft["scenario_quantities"]["high"])

    def test_enquiries_and_competing_feeders_are_price_backed_and_excluded_from_opening(self):
        ids = self.lots
        included = {lot_id for group in self.result["additive_groups"].values() for lot_id in group["lot_ids"]}
        for key in (
            "pilot-car", "pilot-bogie", "pilot-beam", "pilot-station-bay", "pilot-traction-controls",
            "test-vehicle", "test-civil", "test-traction-controls", "test-operator", "demand-survey",
            "alignment-survey", "ground-investigation", "procurement-assurance",
            "six-site-quotation", "six-site-parallel",
        ):
            with self.subTest(lot=key):
                self.assertNotIn(key, included)
                self.assertGreater(ids[key]["low_usd"], 0)
                self.assertLess(ids[key]["low_usd"], ids[key]["high_usd"])
                self.assertTrue(ids[key].get("overlaps_lot_ids") or ids[key].get("alternative_to_lot_ids"))
        for key in ("six-site-quotation", "six-site-parallel"):
            feeder = ids[key]
            self.assertEqual(feeder["quantity"], 6)
            self.assertEqual(feeder["outgoing_circuits"], 20)
            self.assertEqual(feeder["midpoint_ties"], 10)
            self.assertEqual(feeder["protected_track_km"], 24)
            self.assertEqual(set(feeder["alternative_to_lot_ids"]), {"traction-line", "traction-sites", "offsite-feed"})
            for scenario, components in feeder["direct_breakdown_by_scenario_usd"].items():
                self.assertEqual(feeder[scenario + "_usd"], sum(components.values()))
        self.assertNotEqual(ids["six-site-quotation"]["design_id"], ids["six-site-parallel"]["design_id"])
        self.assertGreater(ids["six-site-parallel"]["base_usd"], ids["six-site-quotation"]["base_usd"])
        self.assertEqual(ids["six-site-parallel-upkeep"]["price_period"], "annual")

    def test_reject_corrupt_member_and_valid_manifest_with_mixed_candidate(self):
        with ZipFile(PACKET) as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        for rehash in (False, True):
            with self.subTest(rehash=rehash):
                manifest = json.loads(members["manifest.json"])
                mechanics = json.loads(members["mechanical.json"])
                mechanics["candidate_id"] = "f" * 64
                altered = {**members, "mechanical.json": json.dumps(mechanics).encode()}
                if rehash:
                    manifest["sha256"]["mechanical.json"] = sha256(altered["mechanical.json"]).hexdigest()
                    manifest["evaluation_id"] = _id(manifest["sha256"])
                    altered["manifest.json"] = json.dumps(manifest).encode()
                packet = BytesIO()
                with ZipFile(packet, "w", compression=ZIP_DEFLATED) as archive:
                    for name, raw in altered.items():
                        archive.writestr(name, raw)
                pattern = "requires the matched Airport" if rehash else "packet member changed"
                with self.assertRaisesRegex(ValueError, pattern):
                    estimate_lots(packet)


if __name__ == "__main__":
    unittest.main()

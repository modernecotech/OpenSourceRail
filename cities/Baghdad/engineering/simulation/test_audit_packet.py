"""Exercise Airport buyer packet custody with a bounded working-day fixture."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from deployment.erpnext.apps.osr_erpnext.osr_erpnext.sourcing_comparison import compare_lot
from deployment.erpnext.apps.osr_erpnext.osr_erpnext.sourcing_contract import estimate_payload
from cities.Baghdad.engineering.simulation import (
    assumption_audit, audit_erpnext, audit_offers, audit_packet, motion_power, scenario, test_assumption_audit,
)


class AuditPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        phase = dict(phase_s=300, conflicts=0, positioning_slack_s=0)
        with (patch.object(motion_power, "evaluate", side_effect=test_assumption_audit.AssumptionAuditTests.short_day),
              patch.object(assumption_audit, "phase_options", return_value=dict(as_booked=phase, best=phase)),
              patch.object(assumption_audit, "positioning_trial", return_value=phase)):
            cls.result = assumption_audit.audit(cache=None)

    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)

    def issue(self, layout="paired6", filename="packet.zip"):
        path = self.directory / filename
        return path, audit_packet.issue(self.result, layout, path)

    def test_reproducible_payload_and_manifest(self):
        first, manifest = self.issue()
        second, repeated = self.issue(filename="again.zip")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(manifest, repeated)
        self.assertEqual(audit_packet.verify(first, expected_issue_id=manifest["issue_id"]), manifest)
        self.assertEqual(manifest["layout"], "paired6")
        self.assertEqual(manifest["parent_candidate_id"], self.result["alignment"]["parent_candidate_id"])
        self.assertEqual(manifest["candidate_id"], self.result["decision"]["candidates"]["paired6"]["physical_candidate_id"])
        self.assertEqual(manifest["evaluation_id"], self.result["evaluation_id"])
        self.assertTrue(manifest["issue_id"])
        payloads = {"README.md", "engineering/alignment.json", "engineering/route.geojson",
                    "engineering/vehicle.json", "engineering/station.json", "engineering/service.json",
                    "engineering/feeder.json", "engineering/civil.json", "factory/routing-basis.json",
                    "pricing/production.json", "pricing/supplier-comparisons.json", "returns/buyer-offers.json",
                    "returns/vehicle.json", "returns/feeder.json", "decision.json"}
        with ZipFile(first) as archive:
            self.assertCountEqual(archive.namelist(), payloads | {"manifest.json"})
            self.assertEqual(json.loads(archive.read("manifest.json")), manifest)
            self.assertEqual(manifest["members_sha256"],
                             {name: sha256(archive.read(name)).hexdigest() for name in payloads})

    def test_issue_shell_accepts_its_offer_and_rejects_cross_layout_reuse(self):
        paired, paired_manifest = self.issue()
        radial, radial_manifest = self.issue("radial30", "radial.zip")
        self.assertNotEqual(paired_manifest["candidate_id"], radial_manifest["candidate_id"])
        self.assertNotEqual(paired_manifest["issue_id"], radial_manifest["issue_id"])
        with ZipFile(paired) as archive:
            shell = json.loads(archive.read("returns/buyer-offers.json"))
            paired_production = json.loads(archive.read("pricing/production.json"))
        self.assertEqual(set(shell["layouts"]), {"paired6"})
        self.assertEqual(audit_offers.choices(shell, "paired6", paired_production["pricings"],
                                              paired_production["inputs"]), ([], []))
        row = next(row for row in paired_production["pricings"] if row["lot_id"] == "revised-feeder-package")
        offer = dict(offer_id="test feeder offer", supplier="Synthetic supplier", scope_id=row["scope_id"],
                     buyer_review_reference="Test review", offer_sha256="1"*64, price_usd=1,
                     claimed_domestic_value_usd=None)
        award = dict(scope_id=row["scope_id"], offer_id=offer["offer_id"], buyer_award_reference="Test award")
        shell["layouts"]["paired6"] = {"offers": [offer], "awards": [award]}
        selected, _ = audit_offers.choices(shell, "paired6", paired_production["pricings"], paired_production["inputs"])
        self.assertEqual(selected, [offer])
        with ZipFile(radial) as archive:
            radial_shell = json.loads(archive.read("returns/buyer-offers.json"))
            radial_production = json.loads(archive.read("pricing/production.json"))
        radial_shell["layouts"]["radial30"] = shell["layouts"]["paired6"]
        with self.assertRaises(ValueError):
            audit_offers.choices(radial_shell, "radial30", radial_production["pricings"], radial_production["inputs"])

    def test_mutated_payload_breaks_verification(self):
        path, manifest = self.issue()
        changed = self.directory / "changed.zip"
        with ZipFile(path) as original, ZipFile(changed, "w") as archive:
            for name in original.namelist():
                content = original.read(name)
                archive.writestr(name, content + b"\n" if name == "pricing/production.json" else content)
        with self.assertRaises(ValueError):
            audit_packet.verify(changed, manifest["issue_id"])

    def test_rehashed_archive_cannot_mix_layouts(self):
        paired, manifest = self.issue()
        radial, _ = self.issue("radial30", "radial.zip")
        target = self.directory / "mixed.zip"
        member = "engineering/feeder.json"
        with ZipFile(radial) as donor:
            replacement = donor.read(member)
        original_issue_id = manifest["issue_id"]
        manifest["members_sha256"][member] = sha256(replacement).hexdigest()
        manifest.pop("issue_id")
        manifest["issue_id"] = scenario._id(manifest)
        with ZipFile(paired) as original, ZipFile(target, "w") as archive:
            for name in original.namelist():
                if name == "manifest.json":
                    archive.writestr(name, json.dumps(manifest))
                else:
                    archive.writestr(name, replacement if name == member else original.read(name))
        with self.assertRaisesRegex(ValueError, "trusted issue ID"):
            audit_packet.verify(target, original_issue_id)
        with self.assertRaisesRegex(ValueError, "identify different"):
            audit_packet.verify(target, manifest["issue_id"])

    def test_rejects_stale_evaluation_and_swapped_child_results(self):
        stale = deepcopy(self.result)
        stale["evaluation_id"] = "f"*64
        for label, result in (("stale evaluation", stale),
                              ("parent swap", dict(self.result, alignment={
                                  **self.result["alignment"], "parent_candidate_id": "e"*64})),
                              ("candidate swap", dict(self.result, production={
                                  **self.result["production"], "paired6": self.result["production"]["radial30"]}))):
            with self.subTest(label=label):
                if result is not stale:
                    result["evaluation_id"] = scenario._id({key: value for key, value in result.items()
                                                            if key != "evaluation_id"})
                target = self.directory / "rejected.zip"
                with self.assertRaises(ValueError):
                    audit_packet.issue(result, "paired6", target)
                self.assertFalse(target.exists())

    def test_native_erpnext_estimate_and_review_round_trip(self):
        path, manifest = self.issue()
        edition_date = "2026-11-24"
        pin = dict(expected_issue_id=manifest["issue_id"])
        estimate = estimate_payload(audit_erpnext.portal_estimate(path, edition_date, **pin))
        self.assertEqual(estimate["issue_id"], manifest["issue_id"])
        self.assertEqual(estimate["candidate_id"], manifest["candidate_id"])
        lot_id = "revised-feeder-package"
        lot = next(lot for lot in estimate["lots"] if lot["lot_id"] == lot_id)
        self.assertEqual(lot["quantity"], 1)
        self.assertIsNone(lot["base_usd"])
        self.assertEqual(lot["supplier_scope"]["quantity"], self.result["production"]["paired6"]["quantities"]["grid_sites"])
        quote = dict(candidate_id=estimate["candidate_id"], evaluation_id=estimate["evaluation_id"], lot_id=lot_id,
                     unit=lot["unit"], quantity=1, currency="USD", supplier="Test supplier", quotation="Q-TEST",
                     evidence_kind="supplier-offer", direct_usd=500, annual_upkeep_usd=None, renewals_usd=None, exclusions=[])
        comparison = compare_lot(estimate, lot_id, [quote])
        identity = dict(project="Test Project", rfq="OSR-RFQ-test", lot_id=lot_id)
        trace = dict(quotation="Q-TEST", supplier=quote["supplier"], status="received",
                     recorded_on="2026-11-24", valid_until="2026-12-24", **identity)
        export = dict(comparison=comparison, rfq_docstatus=1, as_of=edition_date, suppliers=[trace], **identity)
        source = self.directory / "test-offer.txt"
        source.write_text("Synthetic offer for contract test")
        review = dict(quotation="Q-TEST", buyer_review_reference="Test review", buyer_award_reference="Test decision",
                      quotation_document=source)
        result = audit_erpnext.reviewed_offers(path, edition_date, export, [review], **pin)
        offer, = result["layouts"]["paired6"]["offers"]
        self.assertEqual(offer["price_usd"], 500)
        self.assertEqual(offer["offer_sha256"], sha256(source.read_bytes()).hexdigest())
        self.assertEqual(offer["scope_id"], lot["design_id"])
        self.assertIn(f'"rfq": "{identity["rfq"]}"', offer["buyer_review_reference"])
        self.assertIn("comparison_receipt_sha256", offer["buyer_review_reference"])
        for updates in (
            dict(rfq_docstatus=True), dict(rfq_docstatus=1.0), dict(as_of="2026-12-25"),
            dict(as_of="2026-11-23"), dict(as_of="20261124"), dict(suppliers=[trace, trace]),
            dict(project="Different Project"), dict(lot_id="fleet"), dict(rfq="OSR-RFQ-other"),
            dict(suppliers=[dict(trace, status="expired")]),
            dict(suppliers=[dict(trace, supplier="Different Supplier")]),
            dict(suppliers=[dict(trace, recorded_on="20261124")]),
            dict(suppliers=[dict(trace, valid_until="20261224")]),
        ):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                audit_erpnext.reviewed_offers(path, edition_date, dict(export, **updates), [review], **pin)
        with self.assertRaisesRegex(ValueError, "comparison must bind"):
            audit_erpnext.reviewed_offers(path, "2026-11-25", export, [review], **pin)
        with self.assertRaises(ValueError):
            audit_erpnext.portal_estimate(path, edition_date, expected_issue_id="f"*64)
        with self.assertRaises(ValueError):
            audit_erpnext.reviewed_offers(path, edition_date, export, [review], expected_issue_id="f"*64)


if __name__ == "__main__":
    unittest.main()

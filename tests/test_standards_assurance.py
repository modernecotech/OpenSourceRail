"""Regression tests for standards evidence and change impact."""

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from engineering.assurance.standards import REGISTER, change_impact, compile_register

REVIEW_DATE = date(2026, 11, 24)
CONFIG = """schema = 1
reviewed = 2026-11-24
review_due = 2027-02-24
[standards]
example = "https://www.iso.org/standard/9001"
[[control]]
id = "QMS"
subject = "Quality"
standards = ["example"]
scope = "Workshop sample"
risk = "Wrong revision"
objective = "Trace each part"
match = "The sample shows one record"
evidence = ["evidence.txt"]
maturity = "sample"
owner = "Manufacturer"
gap = "Inspect the fitted article"
"""


class StandardsAssuranceTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.register = self.root / REGISTER
        self.register.parent.mkdir(parents=True)
        self.register.write_text(CONFIG)
        self.evidence = self.root / "evidence.txt"
        self.evidence.write_text("original evidence")

    def compile(self):
        return compile_register(self.root, today=REVIEW_DATE)

    def test_evidence_changes_reopen_mapped_control(self):
        old = self.compile()
        self.assertEqual(change_impact(old, self.compile()), {})
        self.evidence.write_text("revised evidence")
        current = self.compile()
        self.assertEqual(change_impact(old, current)["QMS"]["changed_evidence"], ["evidence.txt"])
        self.assertEqual(current["controls"]["QMS"]["acceptance"], "open")
        self.assertEqual(current["controls"]["QMS"]["deployment_applicability"], "open")

    def test_publisher_changes_require_review(self):
        old = self.compile()
        self.register.write_text(CONFIG.replace("/9001", "/79427"))
        self.assertEqual(change_impact(old, self.compile())["QMS"]["changed_publishers"], ["example"])

    def test_missing_and_uncontained_evidence_are_rejected(self):
        self.evidence.unlink()
        with self.assertRaisesRegex(ValueError, "Missing evidence file"):
            self.compile()
        self.register.write_text(CONFIG.replace("evidence.txt", "../evidence.txt"))
        with self.assertRaisesRegex(ValueError, "must stay in the checkout"):
            self.compile()

    def test_expired_review_and_unknown_standard_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Review the publisher records"):
            compile_register(self.root, today=date(2027, 2, 25))
        self.register.write_text(CONFIG.replace('["example"]', '["unregistered"]'))
        with self.assertRaisesRegex(ValueError, "registered standards"):
            self.compile()

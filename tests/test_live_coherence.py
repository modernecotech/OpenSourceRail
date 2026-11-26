"""Regression cases for independent live spec, code, records and reader drift."""

import gzip
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from engineering.live_coherence import REGISTER, check


class LiveCoherenceTest(unittest.TestCase):
    def setUp(self):
        workspace = TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        self.write(REGISTER, r"""
[[spec]]
id = "sample-stock"
source = "civil/source.py"
symbol = "SPAN"
unit = "m"

[[spec.code]]
path = "civil/evaluate.py"
symbol = "SPAN"
reference = "source.SPAN"
import_alias = "source"
import_module = "civil.source"

[[spec.record]]
path = "civil/stock.json.gz"
scope = "active.*"
keys = ["span"]
provenance = ["source_sha256"]
verify_all_sources = ["source_sha256"]

[[spec.reader]]
path = "guide.md"
values = ['Current stock uses (?P<value>\d+) m']
required = ['\]\(civil/stock\.json\.gz\)']

[[spec.artifact]]
path = "guide.pdf"
receipt = "guide.receipt.json"
sources = ["guide.md"]

[spec.inventory]
globs = ["*.md"]
targets = ["civil/stock.json.gz"]
markers = ['Current stock uses (?P<value>\d+) m']
strict_readers = ["guide.md"]
obsolete_claims = ['\b10 m track beams?\b']

[[spec.reader]]
path = "published.html"
same_as = "source.html"
""")
        self.write("civil/source.py", "SPAN = 20\n")
        self.write("civil/alignment.txt", "Committed station position\n")
        self.write("civil/evaluate.py", "from . import source\nSPAN = source.SPAN\n")
        self.write("guide.md", "Current stock uses 20 m. [Stock](civil/stock.json.gz)\n"
                   "Earlier 10 m comparators retain their scope.\n")
        self.write("retained.md", "Retained 10 m design reference.\n")
        self.write("source.html", "<p>20 m stock</p>\n")
        self.write("published.html", "<p>20 m stock</p>\n")
        self.write("guide.pdf", "%PDF-example\n")
        self.refresh_pdf_receipt()
        self.write_record()

    def write(self, name, payload):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload.encode() if isinstance(payload, str) else payload)

    def digest(self, name):
        return hashlib.sha256((self.root / name).read_bytes()).hexdigest()

    def refresh_pdf_receipt(self):
        self.write("guide.receipt.json", json.dumps({
            "artifact": "guide.pdf",
            "sha256": self.digest("guide.pdf"),
            "source_sha256": {"guide.md": self.digest("guide.md")},
        }))

    def write_record(self, span=20):
        self.write("civil/stock.json.gz", gzip.compress(json.dumps({
            "active": {
                "river": {"span": span, "source_sha256": {
                    "civil/source.py": self.digest("civil/source.py"),
                    "civil/alignment.txt": self.digest("civil/alignment.txt"),
                }},
            },
            "retained": {"span": 10},
        }).encode()))

    def test_retained_values_and_production_code_are_not_executed(self):
        self.write("civil/evaluate.py", "from . import source\nSPAN = source.SPAN\nraise RuntimeError\n")
        report = check(self.root)
        self.assertEqual(report.errors, [])
        self.assertGreaterEqual(report.checks, 10)

    def test_stale_code_numeric_record_and_reader_each_fail(self):
        self.write("civil/evaluate.py", "from . import source\nSPAN = 10\n")
        self.write_record(span=10)
        self.write("guide.md", "Current stock uses 10 m. [Stock](civil/stock.json.gz)\n")
        self.refresh_pdf_receipt()
        errors = "\n".join(check(self.root).errors)
        self.assertIn("civil/evaluate.py:2 SPAN: expected source expression", errors)
        self.assertIn("civil/stock.json.gz:active.river.span: expected 20 m, found 10", errors)
        self.assertIn("guide.md:1 'Current stock uses 10 m': expected 20 m, found 10.0", errors)

    def test_defined_source_change_invalidates_dependents(self):
        self.write("civil/source.py", "SPAN = 24\n")
        errors = "\n".join(check(self.root).errors)
        self.assertIn("expected 24 m", errors)
        self.assertIn("missing or stale SHA-256 for civil/source.py", errors)

    def test_unlisted_design_input_drift_invalidates_full_provenance(self):
        self.write("civil/alignment.txt", "Changed station position\n")
        errors = "\n".join(check(self.root).errors)
        self.assertIn("missing or stale SHA-256 for civil/alignment.txt", errors)

    def test_unregistered_inbound_pointer_or_live_claim_fails(self):
        self.write("new-pointer.md", "Procurement: [Source](civil/stock.json.gz#sizes).\n")
        self.write("new-claim.md", "Current stock uses 10 m.\n")
        errors = "\n".join(check(self.root).errors)
        self.assertIn("new-pointer.md:1: unregistered live claim or pointer", errors)
        self.assertIn("new-claim.md:1: unregistered live claim or pointer", errors)

    def test_missing_or_repointed_link_fails(self):
        self.write("guide.md", "Current stock uses 20 m. [Stock](retained.md)\n")
        self.refresh_pdf_receipt()
        errors = "\n".join(check(self.root).errors)
        self.assertIn("guide.md: missing current claim or link", errors)

    def test_pdf_source_and_artifact_both_stay_bound(self):
        self.write("guide.md", "Current stock uses 20 m. [Stock](civil/stock.json.gz)\nNew detail.\n")
        self.write("guide.pdf", "%PDF-example\nChanged.\n")
        errors = "\n".join(check(self.root).errors)
        self.assertIn("guide.pdf: artifact digest differs", errors)
        self.assertIn("guide.receipt.json: missing or stale SHA-256 for guide.md", errors)

    def test_render_receipt_fails_for_an_old_view_of_current_geometry(self):
        spec = self.root / REGISTER
        self.write(REGISTER, spec.read_text() + """
[[spec.artifact]]
path = "train.jpg"
receipt = "render.receipt.json"
receipt_scope = "views.front"
digest_key = "render_sha256"
source_key = "sources"
sources = ["civil/source.py"]
""")
        self.write("train.jpg", "render of the approved geometry")
        self.write("render.receipt.json", json.dumps({
            "views": {"front": {"render_sha256": self.digest("train.jpg")}},
            "sources": {"civil/source.py": self.digest("civil/source.py")},
        }))
        self.assertEqual(check(self.root).errors, [])
        self.write("train.jpg", "older render with a driver compartment")
        self.assertIn("train.jpg: artifact digest differs", check(self.root).errors[0])

    def test_obsolete_sentence_fails_even_when_live_claim_is_correct(self):
        path = self.root / "guide.md"
        self.write("guide.md", path.read_text() + "Representative 10 m track beam quantities follow.\n")
        self.refresh_pdf_receipt()
        self.assertIn("guide.md:3: obsolete live claim '10 m track beam'", check(self.root).errors[0])

    def test_published_html_must_match_maintained_reader(self):
        self.write("published.html", "<p>10 m stock</p>\n")
        self.assertIn("published.html: differs from the maintained reader source.html", check(self.root).errors[0])


if __name__ == "__main__":
    unittest.main()

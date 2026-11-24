import json
from pathlib import Path
import tempfile
import unittest

from replay import DEMO_CASES, SOURCE_FILES, contract, demo, review, PROTOTYPE


class ManufacturingHandoffTests(unittest.TestCase):
    def setUp(self):
        self.job = contract()

    def test_demo_faults_hold_evidence_and_inspection_failure_routes_to_rework(self):
        for case in DEMO_CASES:
            with self.subTest(case=case):
                result = review(self.job, demo(self.job, case))
                expected = {
                    "nominal": "training-review-ready",
                    "failed-inspection": "rework-review",
                }.get(case, "held")
                self.assertEqual(result["state"], expected)
                self.assertFalse(result["equipment_start_permission"])
                self.assertFalse(result["fabrication_release"])

    def test_missing_revision_or_future_measurement_holds_review(self):
        trace = demo(self.job, "nominal")
        trace["samples"][0]["binding"] = dict(trace["samples"][0]["binding"])
        trace["samples"][0]["binding"].pop("drawing_revision")
        self.assertIn("drawing_revision", review(self.job, trace)["reason"])
        trace = demo(self.job, "nominal")
        trace["inspection"]["timestamp_ms"] = trace["review_timestamp_ms"] + 1
        self.assertEqual(review(self.job, trace)["state"], "held")

    def test_accepted_working_sample_and_intermediate_disconnect(self):
        trace = demo(self.job, "nominal")
        first, last = trace["samples"]
        working = dict(first, sequence=2, timestamp_ms=2_000, state="working")
        last["sequence"] = 3
        trace["samples"].insert(1, working)
        self.assertEqual(review(self.job, trace)["state"], "training-review-ready")
        working["connected"] = False
        self.assertIn("connection lost", review(self.job, trace)["reason"])

    def test_source_program_and_frame_changes_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in SOURCE_FILES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((PROTOTYPE / relative).read_bytes())
            nc = root / "cam/training/practice.nc"
            nc.write_bytes(nc.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "native CAM receipt"):
                contract(root)
            nc.write_bytes((PROTOTYPE / "cam/training/practice.nc").read_bytes())
            ga = root / "vehicle-factory/installed-ga.json"
            value = json.loads(ga.read_text())
            value["frame_revision"] = "superseded"
            ga.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "frame_revision"):
                contract(root)


if __name__ == "__main__":
    unittest.main()

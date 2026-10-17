"""Review assertions preserve adverse evidence, exact counts and safe links."""

from copy import deepcopy
from html.parser import HTMLParser
import unittest

from engineering.generative_design.hierarchical_review import render


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.text, self.scripts = [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.links.append(attrs.get("href"))
        if tag == "script":
            self.scripts.append(attrs)

    def handle_data(self, data):
        self.text.append(data)


def fixture():
    flags = dict(
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )
    candidate = dict(
        id="beam-a",
        variables={"depth_m": 1.4},
        objectives={"mass_kg": 1000},
        checks=[
            dict(id="strength", state="pass"),
            dict(id="site-data", state="unknown"),
        ],
    )
    adverse = dict(
        candidate,
        id="beam-b",
        variables={"depth_m": 1.6},
        checks=[
            dict(id="strength", state="pass"),
            dict(id="footing-pressure", state="fail"),
            dict(id="site-data", state="unknown"),
        ],
    )
    return dict(
        schema="osr-hierarchical-pilot/1",
        plan=dict(
            work_package_count=999,
            items=[
                dict(
                    id="complete-viaduct-bay",
                    kind="assembly",
                    parents=[],
                    function="Connected bay",
                    missing_capability_ids=["cap-ground"],
                ),
                dict(
                    id="CIV-PILOT",
                    kind="work-package",
                    parents=["complete-viaduct-bay"],
                    function="Bay beam",
                    missing_capability_ids=["cap-ground"],
                ),
            ],
            missing_capabilities=[
                dict(
                    id="cap-ground",
                    item_id="complete-viaduct-bay",
                    capability="Ground resistance model",
                    missing_inputs=["Accepted boreholes"],
                    scenarios=["adverse"],
                    acceptance=["Independent benchmark"],
                    state="HOLD",
                )
            ],
        ),
        engineering=dict(
            mechanical={},
            civil=dict(adverse=adverse, repaired=candidate),
            adverse_cases=[
                dict(
                    id="local-beam-parent-failure",
                    parent_candidate_id="beam-b",
                    locally_passing=True,
                    parent_checks=adverse["checks"],
                    disposition="REJECT",
                )
            ],
            complete_bay=dict(
                disposition="HOLD",
                complete_bay_evaluator_executed=False,
                declared_supports=["left", "right"],
            ),
            coupling=dict(
                status="HOLD-missing-capability-or-input",
                trace=[],
                scope="Missing two-way physical model",
            ),
        ),
        software_execution="Not yet executed",
        promotions=[
            dict(
                candidate_id="software-fixed",
                baseline_id="software-base",
                disposition="ADOPT-EXPERIMENTAL",
                reasons=[],
                experimental_revision={"id": "experimental-pilot"},
            )
        ],
        **flags
    )


def execution():
    return dict(
        schema="osr-bounded-agent-execution/1",
        concurrency=2,
        results=[
            dict(
                proposal_id="software-fixed",
                role="software-developer",
                status="completed",
                base_commit="a" * 40,
                artifact_directory="jobs/id/attempt-001",
                changed_paths=["source.py"],
                tools=[
                    dict(
                        state="passed",
                        argv=["python", "acceptance.py"],
                        log="tool-000.log",
                        timeout_seconds=10,
                    )
                ],
                error=None,
            )
        ],
        physical_release=False,
    )


class HierarchicalReviewTests(unittest.TestCase):
    def test_counts_follow_actual_rows_and_adverse_unknowns_remain_visible(self):
        html = render(fixture(), execution())
        doc = Document(html)
        text = " ".join(doc.text)
        self.assertIn("2", text)
        self.assertIn("<span>1</span>work packages mapped", html)
        self.assertNotIn("999", html)
        for evidence in [
            "footing-pressure",
            "site-data",
            "REJECT",
            "HOLD",
            "Accepted boreholes",
            "left",
            "right",
            "Missing two-way physical model",
        ]:
            self.assertIn(evidence, text)
        self.assertIn(
            "Engineering design completion, manufacturing release and physical release remain false",
            text,
        )
        self.assertIn("ADOPT-EXPERIMENTAL", text)
        self.assertIn("experimental-pilot", text)

    def test_actual_worker_artifact_paths_and_source_report_are_linked(self):
        doc = Document(render(fixture(), execution()))
        self.assertIn("report.json", doc.links)
        for file in ["candidate.patch", "evaluation.json", "tool-000.log"]:
            self.assertIn("execution/jobs/id/attempt-001/" + file, doc.links)
        self.assertFalse(doc.scripts)
        self.assertTrue(any(link.startswith("#item-") for link in doc.links))
        self.assertTrue(any(link.startswith("#request-") for link in doc.links))

    def test_absent_executor_does_not_invent_actual_tools(self):
        doc = Document(render(fixture()))
        self.assertIn("Not executed in this report.", " ".join(doc.text))
        self.assertFalse(any("tool-000.log" in link for link in doc.links))
        self.assertIn(
            "<span>0</span>actual isolated worker evaluations", render(fixture())
        )

    def test_untrusted_names_are_escaped_and_external_paths_rejected(self):
        report = fixture()
        report["engineering"]["civil"]["adverse"]["id"] = "<script>alert(1)</script>"
        report["plan"]["items"][0]["function"] = "<img src=x onerror=alert(2)>"
        html = render(report)
        self.assertFalse(Document(html).scripts)
        self.assertNotIn("<img", html)
        for path in ["../escape", "/absolute", "https://example.test", "foo\\bar"]:
            with self.subTest(path=path):
                record = execution()
                record["results"][0]["artifact_directory"] = path
                with self.assertRaisesRegex(ValueError, "safe relative"):
                    render(fixture(), record)
        record = execution()
        record["results"][0]["tools"][0]["log"] = "../../outside.log"
        with self.assertRaisesRegex(ValueError, "safe relative"):
            render(fixture(), record)

    def test_release_claim_and_wrong_report_types_are_rejected(self):
        for field in [
            "engineering_design_complete",
            "manufacturing_release",
            "physical_release",
        ]:
            report = fixture()
            report[field] = True
            with self.assertRaisesRegex(ValueError, "unreleased"):
                render(report)
        report = fixture()
        report["schema"] = "another-report"
        with self.assertRaisesRegex(ValueError, "pilot report"):
            render(report)
        record = execution()
        record["schema"] = "invented-execution"
        with self.assertRaisesRegex(ValueError, "bounded execution"):
            render(fixture(), record)

    def test_changed_variables_are_compared_to_same_discipline_baseline(self):
        report = fixture()
        original = deepcopy(report)
        html = render(report)
        self.assertIn("&quot;variable&quot;: &quot;depth_m&quot;", html)
        self.assertIn("&quot;previous&quot;: 1.6", html)
        self.assertIn("&quot;proposed&quot;: 1.4", html)
        self.assertEqual(report, original)


if __name__ == "__main__":
    unittest.main()

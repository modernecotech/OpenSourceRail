from __future__ import annotations

import json
from pathlib import Path
import runpy

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools/automation/validate-supplier-technical-support.py"
SOURCE = ROOT / "lib/templates/supplier-technical-support-readiness.toml"


def _module() -> dict:
    return runpy.run_path(str(SCRIPT))


def test_public_supplier_support_template_is_complete_and_fail_closed() -> None:
    status = _module()["build_status"]()
    assert status["summary"] == {
        "catalogue_leads": 3,
        "qualified_leads": 0,
        "work_packages": 8,
        "accepted_work_packages": 0,
        "interfaces": 8,
        "accepted_interfaces": 0,
        "cost_buckets": 8,
        "priced_cost_buckets": 0,
        "accepted_cost_buckets": 0,
        "gates": 7,
        "passed_gates": 0,
        "claims": 7,
        "evidenced_claims": 0,
        "technical_claims_evidenced": 0,
        "railway_acceptance_granted": False,
        "engagement_defined": False,
        "baseline_frozen": False,
        "technical_support_ready": False,
    }
    assert all(not row["qualified"] for row in status["catalogue_leads"])
    assert all(not row["accepted_and_evidenced"] for row in status["work_packages"])
    assert all(not row["accepted_and_evidenced"] for row in status["interface_packages"])
    assert all(not row["accepted_and_scoped"] for row in status["cost_buckets"])
    assert all(not row["passed_and_evidenced"] for row in status["gates"])
    assert all(not row["evidenced"] for row in status["claim_controls"])
    assert status["rfq_intake_contract"] == {
        "path": "design/component-catalogue/catalog/buildable-trainset/evidence/rfq-response-template.json",
        "schema_version": "2.0",
        "authority_fields_present": True,
        "baseline_fields_present": True,
        "separated_cost_bucket_count": 8,
        "lifecycle_import_present": True,
        "responsibility_record_present": True,
    }


def test_tracked_supplier_support_outputs_match_source() -> None:
    module = _module()
    status = module["build_status"]()
    assert json.loads(
        (ROOT / "docs/commercial/supplier-technical-support-readiness.json").read_text()
    ) == status
    assert (
        ROOT / "docs/commercial/supplier-technical-support-readiness.md"
    ).read_text() == module["render_markdown"](status)


def test_status_words_cannot_replace_missing_evidence(tmp_path: Path) -> None:
    module = _module()
    text = SOURCE.read_text(encoding="utf-8")
    text = text.replace('status = "screening-source-only"', 'status = "qualified"', 1)
    text = text.replace('status = "proposed"', 'status = "accepted"', 1)
    text = text.replace('status = "open"', 'status = "accepted"', 1)
    text = text.replace('status = "unquoted"', 'status = "accepted"', 1)
    text = text.replace('decision = "open"', 'decision = "pass"', 1)
    source = tmp_path / "unsupported.toml"
    source.write_text(text, encoding="utf-8")
    status = module["build_status"](source)
    assert status["catalogue_leads"][0]["qualified"] is False
    assert status["work_packages"][0]["accepted_and_evidenced"] is False
    assert status["interface_packages"][0]["accepted_and_evidenced"] is False
    assert status["cost_buckets"][0]["accepted_and_scoped"] is False
    assert status["gates"][0]["passed_and_evidenced"] is False
    assert status["summary"]["technical_support_ready"] is False


def test_positive_claim_requires_supporting_reference(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "unsupported-claim.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8").replace(
            'supplier_support_committed = "unverified"',
            'supplier_support_committed = "committed"',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="supplier_support_ref"):
        module["build_status"](source)


def test_missing_or_escaping_osr_input_is_rejected(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "bad-path.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8").replace(
            '"docs/rolling-stock/light-metro-3car/README.md"',
            '"../outside.md"',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="repository-relative"):
        module["build_status"](source)


def test_unknown_related_work_package_is_rejected(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "unknown-work-package.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8").replace(
            'related_work_packages = ["TS-WP-01", "TS-WP-02", "TS-WP-08"]',
            'related_work_packages = ["TS-WP-NOT-DECLARED"]',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown work packages"):
        module["build_status"](source)


def test_catalogue_lead_portfolio_has_no_fixed_limit(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "additional-lead.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8")
        + '''

[[catalogue_lead]]
id = "LEAD-ADDITIONAL"
display_name = "Additional supplier"
public_source = "docs/rolling-stock/light-metro-3car/README.md"
published_scope = "A separately screened alternative"
possible_use = "Competitive configuration or independent review"
limitations = "No commitment or authority is inferred"
legal_entity = ""
authority_chain_ref = ""
controlled_offer_ref = ""
evidence_refs = []
status = "screening-source-only"
''',
        encoding="utf-8",
    )
    status = module["build_status"](source)
    assert status["summary"]["catalogue_leads"] == 4
    assert status["catalogue_leads"][-1]["qualified"] is False


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "duplicate.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8").replace(
            'id = "TS-WP-02"', 'id = "TS-WP-01"', 1
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="work-package IDs"):
        module["build_status"](source)

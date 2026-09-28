from __future__ import annotations

import json
from pathlib import Path
import runpy

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools/automation/validate-commercial-partnership.py"
SOURCE = ROOT / "lib/templates/commercial-partnership-readiness.toml"


def _module() -> dict:
    return runpy.run_path(str(SCRIPT))


def test_public_partnership_template_is_complete_and_fail_closed() -> None:
    status = _module()["build_status"]()
    assert status["summary"] == {
        "opportunity_ready": False,
        "candidates_screened_or_active": 4,
        "candidates_total": 4,
        "candidates_shortlisted": 0,
        "candidates_selected_and_evidenced": 0,
        "parties_ready": 0,
        "parties_total": 3,
        "contributions_accepted": 0,
        "contributions_total": 8,
        "ip_items_ready": 0,
        "ip_items_total": 6,
        "commercial_controls_ready": 0,
        "commercial_controls_total": 4,
        "localisation_stages_complete": 0,
        "localisation_stages_total": 4,
        "gates_accepted": 0,
        "gates_total": 5,
        "funding_ready": False,
        "exclusivity_controlled": True,
        "public_claims_evidenced": False,
        "development_agreement_ready": False,
        "equity_jv_ready": False,
        "candidate_project_ready": False,
        "replication_ready": False,
        "partnership_ready": False,
    }
    assert all(status["validation"].values())
    assert status["claim_controls"]["customer_order"] == "absent"
    assert status["claim_controls"]["railway_acceptance"] == "not-granted"
    assert all(not row["accepted"] for row in status["contributions"])
    assert all(not row["accepted"] for row in status["gates"])


def test_tracked_partnership_outputs_match_source() -> None:
    module = _module()
    status = module["build_status"]()
    assert json.loads((ROOT / "docs/commercial/partnership-readiness.json").read_text()) == status
    assert (ROOT / "docs/commercial/partnership-readiness.md").read_text() == module["render_status"](status)


def test_status_words_do_not_override_missing_evidence(tmp_path: Path) -> None:
    module = _module()
    text = SOURCE.read_text(encoding="utf-8")
    text = text.replace('status = "proposed"', 'status = "accepted"', 1)
    text = text.replace('status = "not-started"', 'status = "complete"', 1)
    text = text.replace('decision = "open"', 'decision = "accepted"', 1)
    source = tmp_path / "unsupported.toml"
    source.write_text(text, encoding="utf-8")
    status = module["build_status"](source)
    assert status["contributions"][0]["accepted"] is False
    assert status["localisation_stages"][0]["complete"] is False
    assert status["gates"][0]["accepted"] is False
    assert status["summary"]["partnership_ready"] is False


def test_unknown_contributing_party_is_rejected(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "unknown-party.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8").replace(
            'party_id = "PARTY-OSR"', 'party_id = "PARTY-NOT-DECLARED"', 1
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown party"):
        module["build_status"](source)


def test_exclusivity_requires_scope_term_performance_and_exit(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "exclusive.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8").replace("enabled = false", "enabled = true", 1),
        encoding="utf-8",
    )
    status = module["build_status"](source)
    assert status["exclusivity"]["controlled"] is False
    assert status["summary"]["partnership_ready"] is False


def test_claim_status_without_supporting_reference_remains_unproven(tmp_path: Path) -> None:
    module = _module()
    text = SOURCE.read_text(encoding="utf-8")
    replacements = {
        'customer_order = "absent"': 'customer_order = "evidenced"',
        'industrial_partner_commitment = "unverified"': 'industrial_partner_commitment = "evidenced"',
        'manufacturer_authorization = "unverified"': 'manufacturer_authorization = "evidenced"',
        'all_in_cost_advantage = "unproven"': 'all_in_cost_advantage = "independently-demonstrated"',
        'railway_acceptance = "not-granted"': 'railway_acceptance = "authority-evidenced"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new, 1)
    source = tmp_path / "unsupported-claims.toml"
    source.write_text(text, encoding="utf-8")
    status = module["build_status"](source)
    assert status["claim_controls"]["all_evidenced"] is False
    assert status["summary"]["public_claims_evidenced"] is False


def test_candidate_portfolio_accepts_additional_examples_without_a_fixed_limit(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "additional-candidate.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8")
        + '''

[[reference_candidate]]
id = "CAND-ADDITIONAL"
candidate_type = "other"
country = "Example country"
city_or_site = "Example site"
scope = "A separately controlled additional opportunity"
source_ref = "evidence/candidate-source"
customer_legal_name = ""
customer_need_ref = ""
funded_scope_ref = ""
site_evidence_ref = ""
approval_route_ref = ""
reuse_case = "Demonstrate that the portfolio is not capped"
selection_criteria = ["identified customer", "funded scope"]
selection_evidence_refs = []
status = "screening"
''',
        encoding="utf-8",
    )
    status = module["build_status"](source)
    assert status["summary"]["candidates_total"] == 5
    assert status["reference_candidates"][-1]["id"] == "CAND-ADDITIONAL"
    assert status["reference_candidates"][-1]["selected_and_evidenced"] is False


def test_invalid_procurement_role_and_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "invalid-role.toml"
    source.write_text(
        SOURCE.read_text(encoding="utf-8").replace(
            'procurement_role = "undecided"', 'procurement_role = "both-sides"'
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid procurement role"):
        module["build_status"](source)

    duplicate = tmp_path / "duplicate.toml"
    duplicate.write_text(
        SOURCE.read_text(encoding="utf-8").replace(
            'id = "PARTY-INDUSTRIAL"', 'id = "PARTY-OSR"', 1
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="party IDs"):
        module["build_status"](duplicate)

import copy

import pytest

from tools.automation import component_rfc_readiness


def source():
    import tomllib

    return tomllib.loads(component_rfc_readiness.SOURCE.read_text(encoding="utf-8"))


def test_all_promoted_component_rfcs_have_complete_open_packages() -> None:
    report = component_rfc_readiness.compile_readiness()
    assert report["passed"]
    assert report["package_count"] == 5
    assert report["release_ready_count"] == 0
    assert all(row["release_blockers"] and not row["release_ready"] for row in report["packages"])


def test_missing_required_field_fails_closed() -> None:
    changed = copy.deepcopy(source())
    changed["packages"][0]["test_evidence_required"] = []
    with pytest.raises(ValueError, match="test_evidence_required"):
        component_rfc_readiness.compile_readiness(changed)

def test_uncontrolled_part_and_unknown_hazard_fail_closed() -> None:
    changed = copy.deepcopy(source())
    changed["packages"][1]["part_ids"].append("INVENTED-PART")
    with pytest.raises(ValueError, match="uncontrolled parts"):
        component_rfc_readiness.compile_readiness(changed)
    changed = copy.deepcopy(source())
    changed["packages"][1]["hazard_ids"].append("H-NOT-REAL")
    with pytest.raises(ValueError, match="unknown hazard"):
        component_rfc_readiness.compile_readiness(changed)


def test_acceptance_claim_fails_closed() -> None:
    changed = copy.deepcopy(source())
    changed["packages"][2]["acceptance_status"] = "accepted"
    with pytest.raises(ValueError, match="may not imply"):
        component_rfc_readiness.compile_readiness(changed)

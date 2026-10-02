import copy
import importlib.util
import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("digital_assurance", ROOT / "tools/automation/digital-assurance.py")
ASSURANCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASSURANCE)


def sources():
    config = tomllib.loads((ROOT / "lib/templates/digital-assurance.toml").read_text())
    fmea = tomllib.loads((ROOT / "lib/templates/system-fmea.toml").read_text())
    return config, fmea


def test_current_assurance_is_complete_but_not_physical_release():
    report = ASSURANCE.compile_assurance(ROOT)
    assert report["digital_gate_passed"] is True
    assert report["digital_coherence_gate"] == "pass"
    assert report["conformity_state"] == "not-assessed"
    assert report["release_ready"] is False
    config, fmea = sources()
    assert report["counts"]["standards"] == len(config["standards"])
    assert report["counts"]["profiles"] == len(config["profiles"])
    assert report["counts"]["control_objectives"] == len(config["controls"])
    assert report["counts"]["digital_checks"] == len(config["checks"])
    assert report["counts"]["failure_modes"] == len(fmea["failure_modes"])
    assert report["counts"]["inventory_items_screened"] > 0
    assert report["counts"]["inventory_item_reviews_open"] == report["counts"]["inventory_items_screened"]
    assert report["counts"]["physical_evidence_open"] == sum(
        bool(row.get("physical_evidence_required")) for row in fmea["failure_modes"]
    )
    assert all(row["count"] >= 1 for row in report["fmea_coverage"])
    assert len({row["inventory_id"] for row in report["inventory_coverage"]}) == report["counts"]["inventory_items_screened"]
    assert {row["scope"] for row in report["inventory_coverage"]} == {
        "train-product",
        "train-assembly",
        "station-product",
        "station-assembly",
        "civil-type",
        "software-crate",
    }
    assert all(row["release_blocking"] for row in report["inventory_coverage"])
    assert "remain open" in report["interpretation"]
    assert all(row["machine_status"] == "evidence-linked-and-hashed" for row in report["checks"])
    assert all(row["conformity_status"] == "not-assessed" for row in report["checks"])


def test_missing_domain_level_fails_closed():
    config, fmea = sources()
    fmea["failure_modes"] = [row for row in fmea["failure_modes"] if not (row["domain"] == "civil" and row["level"] == "system")]
    with pytest.raises(ValueError, match="FMEA coverage gaps"):
        ASSURANCE.compile_assurance(ROOT, config, fmea)


def test_catastrophic_mode_cannot_waive_physical_evidence():
    config, fmea = sources()
    fmea = copy.deepcopy(fmea)
    row = next(row for row in fmea["failure_modes"] if row["severity"] == 5)
    row["physical_evidence_required"] = False
    with pytest.raises(ValueError, match="cannot waive physical evidence"):
        ASSURANCE.compile_assurance(ROOT, config, fmea)


def test_missing_or_escaping_evidence_fails_closed(tmp_path):
    config, fmea = sources()
    config = copy.deepcopy(config)
    config["checks"][0]["evidence"] = ["../outside"]
    with pytest.raises(ValueError, match="repository-relative"):
        ASSURANCE.compile_assurance(ROOT, config, fmea)


def test_report_is_deterministic():
    first = ASSURANCE.outputs(ROOT)
    second = ASSURANCE.outputs(ROOT)
    assert first == second


def test_registry_review_expiry_fails_closed():
    config, fmea = sources()
    with pytest.raises(ValueError, match="review overdue"):
        ASSURANCE.compile_assurance(ROOT, config, fmea, today=ASSURANCE.date(2028, 1, 1))


def test_change_impact_reopens_mapped_controls():
    current = ASSURANCE.compile_assurance(ROOT)
    previous = copy.deepcopy(current)
    path = next(iter(previous["evidence_hashes"]))
    previous["evidence_hashes"][path] = "0" * 64
    impact = ASSURANCE.change_impact(previous, current)
    assert impact["changed_paths"] == [path]
    assert impact["decision"] == "reopen-affected-controls-and-dependent-gates"
    assert impact["impacted"]["controls"]

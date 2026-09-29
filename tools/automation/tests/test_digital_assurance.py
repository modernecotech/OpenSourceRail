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
    assert report["release_ready"] is False
    assert report["counts"] == {
        "standards": 10,
        "digital_checks": 8,
        "failure_modes": 18,
        "inventory_items_screened": 279,
        "inventory_item_reviews_open": 279,
        "physical_evidence_open": 18,
    }
    assert all(row["count"] >= 1 for row in report["fmea_coverage"])
    assert len({row["inventory_id"] for row in report["inventory_coverage"]}) == 279
    assert {row["scope"] for row in report["inventory_coverage"]} == {
        "train-product",
        "train-assembly",
        "station-product",
        "station-assembly",
        "civil-type",
        "software-crate",
    }
    assert all(row["release_blocking"] for row in report["inventory_coverage"])
    assert "cannot be replaced" in report["interpretation"]


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

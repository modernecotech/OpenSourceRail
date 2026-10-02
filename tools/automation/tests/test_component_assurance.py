import copy
from pathlib import Path
import tomllib

import pytest

from tools.automation import component_assurance


ROOT = Path(__file__).resolve().parents[3]


def config() -> dict:
    return tomllib.loads(component_assurance.CONFIG.read_text(encoding="utf-8"))


def test_every_controlled_item_has_one_fail_closed_assurance_passport() -> None:
    report = component_assurance.compile_register()
    assert report["summary"]["controlled_items"] == (
        report["summary"]["engineering_inventory_items"]
        + report["summary"]["platform_services"]
    )
    assert report["summary"]["engineering_inventory_items"] > 0
    assert report["summary"]["platform_services"] == len(config()["platform_components"])
    assert report["summary"]["released_items"] == 0
    assert set(report["summary"]["routes"]) == {
        "business-supervision",
        "civil-infrastructure",
        "rolling-stock",
        "software-control",
        "station-wayside",
    }
    assert len({row["assurance_id"] for row in report["passports"]}) == report["summary"]["controlled_items"]
    assert all(row["release_state"] == "blocked-after-g0" for row in report["passports"])
    assert all(list(row["gate_status"]) == ["G0", "G1", "G2", "G3", "G4"] for row in report["passports"])
    assert all(row["gate_status"]["G0"] == "pass-baseline-recorded" for row in report["passports"])
    assert all(not any(row["gate_status"][gate].startswith("pass") for gate in ("G1", "G2", "G3", "G4")) for row in report["passports"])


def test_missing_or_duplicate_route_fails_closed() -> None:
    changed = copy.deepcopy(config())
    changed["routes"] = [row for row in changed["routes"] if row["id"] != "civil-infrastructure"]
    with pytest.raises(ValueError, match="unrouted inventory scopes"):
        component_assurance.compile_register(config=changed)

    changed = copy.deepcopy(config())
    changed["routes"][1]["scopes"].append("train-product")
    with pytest.raises(ValueError, match="multiple routes"):
        component_assurance.compile_register(config=changed)


def test_gate_order_and_platform_sources_fail_closed() -> None:
    changed = copy.deepcopy(config())
    changed["gates"].reverse()
    with pytest.raises(ValueError, match="exactly G0 through G4"):
        component_assurance.compile_register(config=changed)

    changed = copy.deepcopy(config())
    changed["platform_components"][0]["source"] = "docs/certification/missing.md"
    with pytest.raises(ValueError, match="missing component source"):
        component_assurance.compile_register(config=changed)


def test_generated_registers_are_deterministic_and_current() -> None:
    first = component_assurance.outputs(ROOT)
    second = component_assurance.outputs(ROOT)
    assert first == second
    assert component_assurance.OUTPUT_MARKDOWN.read_text(encoding="utf-8") == first[0]
    assert component_assurance.OUTPUT_JSON.read_text(encoding="utf-8") == first[1]

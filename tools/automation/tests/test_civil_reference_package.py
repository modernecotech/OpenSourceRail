"""Civil graph propagation, recorded solver provenance and pending release."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("civil_reference",ROOT/"tools/automation/civil_reference.py")
module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_civil_reference_keeps_unresolved_design_and_evidence_blocked():
    r=module.compile_package()
    assert not r["release_ready"] and not r["authority_accepted"] and not r["independently_checked_design"]
    assert r["quantities"]["beam_count"] == 4
    assert r["foundation_comparison"]["selected_id"] is None
    assert all(not b["lifting_check_passed"] for b in r["lifting_budgets"].values())
    assert len(r["connections"]) == 7 and len(r["failure_modes"]) == 7
    assert r["comparator"]["installed_cost_usd"] is None
    assert all(not s["incorporated_material"] for s in r["references"])


def test_drain_change_reaches_operational_risk_and_release_gate():
    r=module.compile_package();impact=r["graph"]["drain_change_impact"]
    chain=impact["trace_paths"]["CIVIL-GATE"]
    assert chain == ["DRAIN-01","CF-01","CF-01-CHAIN-1","CF-01-CHAIN-2","CF-01-CHAIN-3","CF-01-CHAIN-4","CF-01-CHAIN-5","CF-01-REQ","CF-01-EVIDENCE","CIVIL-GATE"]
    thread=module.load_thread();old=r["graph"]
    changed={**old,"edges":[e for e in old["edges"] if not (e["from"] == "DRAIN-01" and e["to"] == "CF-01")]}
    assert "CIVIL-GATE" in thread.change_impact(old,changed)["trace_paths"]


def test_recorded_solver_sanity_has_native_provenance_and_hydraulic_rejections():
    r=module.compile_package()
    beam=r["demonstrations"]["beam-sanity"]
    assert beam["sanity_passed"] and beam["project_design_accepted"] is False
    assert len(beam["results"]) == 4 and len(beam["output_hashes"]) == 12
    assert all(row["calculix_relative_error"] < .01 for row in beam["results"])
    drainage=r["demonstrations"]["drainage-sanity"]["scenarios"]
    assert drainage["normal"]["illustrative_limit_findings"] == []
    assert drainage["blocked-drain"]["illustrative_limit_findings"]
    assert drainage["backwater"]["illustrative_limit_findings"]

"""Civil graph propagation, recorded solver provenance and pending release."""
import importlib.util
import json

import pytest
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
    chain=["CF-01","CF-01-SATURATION","CF-01-FOUNDATION","CF-01-BEARING","CF-01-TRACK","CF-01-OPERATION"]
    assert set(chain) <= set(impact["impacted"]["failure_modes"])
    edges={(e["from"],e["to"],e["relation"]) for e in r["graph"]["edges"]}
    assert all((a,b,"propagates_to") in edges for a,b in zip(chain,chain[1:]))
    assert "CIVIL-GATE" in impact["trace_paths"]
    modes={f["id"]:f for f in r["shared_failure_modes"]}
    for identifier in chain:
        assert modes[identifier]["ownership"]["responsible_role"]
        assert modes[identifier]["calculation_or_observation_reference"]
        assert modes[identifier]["required_response"]
    thread=module.load_thread();old=r["graph"]
    changed={**old,"edges":[e for e in old["edges"] if not (e["from"] == "DRAIN-01" and e["to"] == "CF-01")]}
    assert "CIVIL-GATE" in thread.change_impact(old,changed)["trace_paths"]


def test_recorded_solver_sanity_has_native_provenance_and_hydraulic_rejections():
    r=module.compile_package()
    beam=r["demonstrations"]["beam-sanity"]
    assert beam["sanity_passed"] and beam["project_design_accepted"] is False
    assert len(beam["results"]) == 4 and len(beam["output_hashes"]) == 24
    assert all(row["calculix_relative_error"] < .01 for row in beam["results"])
    drainage=r["demonstrations"]["drainage-sanity"]["scenarios"]
    assert drainage["normal"]["illustrative_limit_findings"] == []
    assert drainage["blocked-drain"]["illustrative_limit_findings"]
    assert drainage["backwater"]["illustrative_limit_findings"]


def test_layout_change_recalculates_quantities_mass_and_reopens_evidence():
    source=json.loads((ROOT/module.SOURCE).read_text());old=module.compile_package(source_data=source)
    for asset in source["asset_register"]["assets"]:
        if asset["asset_type"] == "span":
            first=asset["from_station_m"] == 0
            asset.update(from_station_m=0 if first else 25,to_station_m=25 if first else 50,variant_id="Pi25")
        else: asset["from_station_m"]=50
    for support in source["asset_register"]["supports"]:
        if support["chainage_m"] == 20: support["chainage_m"]=25
        elif support["chainage_m"] == 45: support["chainage_m"]=50
    after=module.compile_package(source_data=source);q=after["quantities"]
    assert q["span_lengths_m"] == [25]
    assert q["bare_beam_concrete_m3"] > old["quantities"]["bare_beam_concrete_m3"]
    assert q["bare_mass_by_asset_kg"]["PI20-T1"] == pytest.approx(74937.5)
    assert q["at_grade_route_length_m"] == 15 and q["at_grade_track_length_m"] == 30
    assert q["installed_cost_usd"] is None
    assert "16 seats" not in after["bearings"]["candidate_layout"]
    assert "45–65" not in next(r for r in after["drainage_objects"] if r["kind"] == "transition")["definition"]
    assert "15 m" in module.markdown(after)
    assert "stale design revision: PI20-T1" in after["graph"]["gaps"]["OSR-CIVIL-REF-A"]
    assert "failure analysis binds an earlier design revision" in after["graph"]["gaps"]["CF-05"]
    impact=module.load_thread().change_impact(old["graph"],after["graph"])
    assert "CF-05-EVIDENCE" in impact["impacted"]["evidence"] and "CIVIL-GATE" in impact["impacted"]["decisions"]


def test_layout_cannot_shorten_its_own_authoritative_extent():
    source=json.loads((ROOT/module.SOURCE).read_text())
    for a in source["asset_register"]["assets"]:
        if a["asset_type"] != "span": a["to_station_m"]=60
    for interval in source["asset_register"]["coverage_intervals"]: interval["to_station_m"]=60
    with pytest.raises(ValueError,match="authoritative route"): module.compile_package(source_data=source)


@pytest.mark.parametrize("mutation,match", [
    (lambda c:c["failure_modes"][0].pop("ownership"),"missing required"),
    (lambda c:c["scenarios"][0].update(acceptance_criteria={"physical_validation_required":False}),"derive from requirements"),
    (lambda c:c["decisions"][0].update(state="accepted"),"cannot manufacture"),
    (lambda c:next(r for r in c["failure_modes"] if r["id"] == "CF-01-OPERATION").update(propagates_to=["CF-01"]),"cycle in propagates_to"),
])
def test_civil_assembly_uses_shared_validation(mutation,match):
    source=json.loads((ROOT/module.SOURCE).read_text())
    c=json.loads((ROOT/source["assurance_path"]).read_text());mutation(c)
    with pytest.raises(ValueError,match=match):
        module.load_thread().compile_thread(ROOT,c,config_source=source["assurance_path"],import_catalog=False,include_controller_execution=False)


def test_production_and_maintenance_are_identified_pending_records():
    graph=module.compile_package()["graph"];nodes={n["id"]:n for n in graph["nodes"]}
    production=nodes["DEMO-CIVIL-MIX-PI25"]
    assert production["item_ids"] == [nodes[production["occurrence_ids"][0]]["design_item"]] == ["PI25-T1"]
    assert all(nodes[f]["item_id"] == "PI25-T1" for f in production["failure_mode_ids"])
    assert production["state"] == "planned" and production["material_controls"]["mix_revision"] is None
    incident=nodes["DEMO-CIVIL-DRAIN-INSPECTION"]
    assert nodes[incident["occurrence_id"]]["design_item"] == "DRAIN-01"
    assert incident["engineering_handback"] == "open"
    assert not graph["release_ready"]

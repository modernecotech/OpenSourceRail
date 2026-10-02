"""Regression cases for omitted assets, fabricated outputs and hydraulic failure."""
import csv
import json
from copy import deepcopy
from pathlib import Path

import pytest

from engineering.analysis import civil_evidence as evidence, drainage_ground_design as drainage, structural_release


def review():
    return dict(decision="accepted", producer="designer", checker="independent checker", signed_at="2026-10-02", controlled_reference="TEST")


def register():
    return {"schema":"osr-civil-assets/1", "design_sha256":"a"*64, "review":review(),
        "assets":[dict(asset_id=f"A-{i}",line_id="L1",asset_type="span",from_station_m=i*25,to_station_m=(i+1)*25,coverage_group="track",support_ids=[f"S-{i}",f"S-{i+1}"],foundation_ref=f"S-{i}") for i in range(2)],
        "supports":[dict(support_id=f"S-{i}",scope_type="line",scope_id="L1",chainage_m=i*25,zone_id="G1") for i in range(3)],
        "coverage_intervals":[dict(line_id="L1",coverage_group="track",from_station_m=0,to_station_m=50)]}


def test_one_row_cannot_cover_whole_line():
    r=register()
    assert evidence.inspect_register(r,"a"*64,{"L1"},set()) == []
    rows=[{**r["assets"][0],"to_station_m":50}]
    assert evidence.reconcile(rows,r["assets"],"asset_id",("from_station_m","to_station_m"))
    r["assets"][1]["from_station_m"] = 26
    assert any("gaps" in f for f in evidence.inspect_register(r,"a"*64,{"L1"},set()))


@pytest.mark.parametrize("invalid", [float("nan"),float("inf"),-1])
def test_invalid_chainage_is_blocked(invalid):
    r=register();r["supports"][0]["chainage_m"]=invalid
    assert evidence.inspect_register(r,"a"*64,{"L1"},set())


def numerical_fixture(tmp_path):
    output=tmp_path/"results.csv"
    output.write_text("asset_id,load_case_id,metric,value,unit\nA,LC-S,displacement,-0.002,m\nA,LC-C,displacement,-0.001,m\n")
    native=tmp_path/"model.dat";native.write_text("native test solver output\n")
    report={"output_hashes":{p.name:evidence.sha(p) for p in (output,native)},"numerical_results_path":output.name,"native_output_paths":[native.name],"load_case_ids":["LC-S","LC-C"]}
    basis={"review":review(),"required_load_cases":{"opensees":["LC-S","LC-C"]},"criteria":{"opensees":[dict(asset_id="A",load_case_id=case,metric="displacement",operator="abs-max",limit=.003,unit="m",stage=stage) for case,stage in (("LC-S","service"),("LC-C","construction"))]}}
    return output,report,basis


def test_actual_results_and_numerical_limits(tmp_path):
    output,report,basis=numerical_fixture(tmp_path)
    assert evidence.inspect_results(report,tmp_path,basis,"opensees",{"A"}) == []
    basis["criteria"]["opensees"][0]["limit"]=.0001
    assert any("acceptance failed" in f for f in evidence.inspect_results(report,tmp_path,basis,"opensees",{"A"}))
    output.write_text(output.read_text().replace("-0.002","nan"))
    report["output_hashes"][output.name]=evidence.sha(output)
    assert any("non-finite" in f for f in evidence.inspect_results(report,tmp_path,basis,"opensees",{"A"}))


def test_missing_case_asset_and_changed_output_are_blocked(tmp_path):
    output,report,basis=numerical_fixture(tmp_path)
    output.write_text(output.read_text().split("A,LC-C")[0])
    findings=evidence.inspect_results(report,tmp_path,basis,"opensees",{"A","OMITTED"})
    assert any("hash mismatch" in f for f in findings)
    assert any("coverage" in f for f in findings)
    assert any("combinations" in f for f in findings)


def test_output_paths_cannot_escape_evidence(tmp_path):
    with pytest.raises(ValueError): evidence.controlled_path(tmp_path,"../external.dat")
    outside=tmp_path.parent/"outside.dat";outside.write_text("secret test data")
    (tmp_path/"link.dat").symlink_to(outside)
    with pytest.raises(ValueError): evidence.controlled_path(tmp_path,"link.dat")


def test_zero_continuity_does_not_hide_backwater_failure():
    root=drainage.REPO_ROOT/"engineering/assurance/civil-reference"
    r=json.loads((root/"calculations/drainage-sanity.json").read_text())
    limits=r["illustrative_limits"]
    normal=drainage.replay_swmm(root/"drainage/normal.inp")
    backwater=drainage.replay_swmm(root/"drainage/backwater.inp")
    assert abs(backwater["routing_error_percent"]) < 1
    assert drainage.inspect_hydraulic_performance(normal,limits) == []
    findings=drainage.inspect_hydraulic_performance(backwater,limits)
    assert any("flooding_volume" in f for f in findings)
    assert any("peak_head" in f for f in findings)
    assert any("outfall_peak_flow" in f for f in findings)


def test_adverse_labels_need_actual_geometry_or_boundary_change(tmp_path):
    root=drainage.REPO_ROOT/"engineering/assurance/civil-reference/drainage"
    normal=root/"normal.inp";replay=drainage.replay_swmm(normal)
    comments=tmp_path/"fake.inp";comments.write_text(normal.read_text()+"\n; Blocked-drain or backwater label only\n")
    assert drainage.inspect_adverse_model("blocked-drain",normal,comments,replay)
    assert drainage.inspect_adverse_model("backwater",normal,comments,replay)
    assert drainage.inspect_adverse_model("blocked-drain",normal,root/"blocked-drain.inp",replay) == []
    assert drainage.inspect_adverse_model("backwater",normal,root/"backwater.inp",replay) == []


@pytest.mark.parametrize("count,length",[("0","18"),("1.5","18"),("1","nan"),("1","inf")])
def test_invalid_deep_foundation_rows_return_findings(tmp_path,count,length):
    rules=drainage.read_requirements();path=tmp_path/"schedule.csv"
    with path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=rules["foundation_schedule"]["required_columns"]);writer.writeheader()
        writer.writerow(dict(support_id="S-0",scope_type="line",scope_id="L1",chainage_m="0",zone_id="G1",system_kind="foundation",system_id="bored-shaft",actual_length_m=length,actual_element_count=count,design_quantity="60",design_unit="m3",design_capacity="1000",predicted_settlement_mm="5",verification_method="TEST",status="checked"))
    _,findings=drainage.inspect_foundation_schedule(path,[{"id":"L1"}],[],rules,register())
    assert any("invalid element count" in f for f in findings)

"""Regression cases for omitted assets, fabricated outputs and hydraulic failure."""
import csv
import json
from copy import deepcopy
from pathlib import Path

import pytest

from engineering.analysis import civil_evidence as evidence, drainage_ground_design as drainage, structural_release, solver_results


def review():
    return dict(decision="accepted", producer="designer", checker="independent checker", signed_at="2026-10-02", controlled_reference="TEST")


def register():
    return {"schema":"osr-civil-assets/1", "design_sha256":"a"*64, "review":review(),
        "assets":[dict(asset_id=f"A-{i}",line_id="L1",asset_type="span",from_station_m=i*25,to_station_m=(i+1)*25,coverage_group="track",support_ids=[f"S-{i}",f"S-{i+1}"],foundation_ref=f"S-{i}") for i in range(2)],
        "supports":[dict(support_id=f"S-{i}",scope_type="line",scope_id="L1",chainage_m=i*25,zone_id="G1") for i in range(3)],
        "coverage_intervals":[dict(line_id="L1",coverage_group="track",from_station_m=0,to_station_m=50)]}


def inspect(r, line_ids=None, stations=None, station_lines=None):
    return evidence.inspect_register(r,"a"*64,line_ids or {"L1"},stations or set(),station_lines or {},register()["coverage_intervals"])


def test_one_row_cannot_cover_whole_line():
    r=register()
    assert inspect(r) == []
    rows=[{**r["assets"][0],"to_station_m":50}]
    assert evidence.reconcile(rows,r["assets"],"asset_id",("from_station_m","to_station_m"))
    r["assets"][1]["from_station_m"] = 26
    assert any("gaps" in f for f in inspect(r))


@pytest.mark.parametrize("invalid", [float("nan"),float("inf"),-1])
def test_invalid_chainage_is_blocked(invalid):
    r=register();r["supports"][0]["chainage_m"]=invalid
    assert inspect(r)


def numerical_fixture(tmp_path,solver="opensees"):
    output=tmp_path/"results.csv"
    output.write_text("asset_id,load_case_id,metric,value,unit\nA,LC-S,displacement,-0.002,m\nA,LC-C,displacement,-0.001,m\n")
    native=tmp_path/"model.out";native.write_text("1 -0.002\n2 -0.001\n")
    model=tmp_path/"model.tcl";model.write_text("# Synthetic fixture with metre displacement basis\n")
    report={"input_sha256":evidence.sha(model),"output_hashes":{p.name:evidence.sha(p) for p in (output,native)},"numerical_results_path":output.name,"native_output_paths":[native.name],"load_case_ids":["LC-S","LC-C"]}
    spec={"parser_id":solver_results.PARSERS["opensees"],"model_sha256":report["input_sha256"],"model_units":{"displacement":"m"},
        "files":{native.name:{"nodes":[21],"dofs":[2],"time_column":True,"response":"disp"}},
        "selectors":[dict(asset_id="A",load_case_id=case,metric="displacement",path=native.name,node_id=21,dof=2,time=i,quantity="displacement",operation="signed") for i,case in enumerate(("LC-S","LC-C"),1)]}
    if solver == "calculix":
        native.write_text(" S T E P 1\n displacements (vx,vy,vz) for set MID and time 1.0\n\n 21 0.0 -0.002 0.0\n S T E P 2\n displacements (vx,vy,vz) for set MID and time 2.0\n\n 21 0.0 -0.001 0.0\n")
        spec["parser_id"]=solver_results.PARSERS[solver];spec["files"]={native.name:{}}
        for i,selector in enumerate(spec["selectors"],1): selector.update(step=i,set_name="MID")
        report["output_hashes"][native.name]=evidence.sha(native)
    report["native_parser"]=solver_results.parser_provenance(solver,spec)
    basis={"review":review(),"required_load_cases":{"opensees":["LC-S","LC-C"]},"native_output_spec":{"opensees":spec},"criteria":{"opensees":[dict(asset_id="A",load_case_id=case,metric="displacement",operator="abs-max",limit=.003,unit="m",stage=stage) for case,stage in (("LC-S","service"),("LC-C","construction"))]}}
    if solver != "opensees":
        for field in ("required_load_cases","native_output_spec","criteria"):
            basis[field][solver]=basis[field].pop("opensees")
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


@pytest.mark.parametrize("solver",["opensees","calculix"])
def test_native_100mm_cannot_pass_as_csv_1mm_below_2mm_limit(tmp_path,solver):
    output, report, basis = numerical_fixture(tmp_path,solver)
    native=tmp_path/report["native_output_paths"][0]
    native.write_text(native.read_text().replace("-0.002","0.100"))
    output.write_text(output.read_text().replace("-0.002","0.001"))
    for path in (native,output): report["output_hashes"][path.name]=evidence.sha(path)
    basis["criteria"][solver][0]["limit"]=.002
    assert any("CSV/native" in f for f in evidence.inspect_results(report,tmp_path,basis,solver,{"A"}))


@pytest.mark.parametrize("mutation", [
    lambda report,basis: report["native_parser"].update(version="uncontrolled"),
    lambda report,basis: basis["native_output_spec"]["opensees"].update(model_sha256="b"*64),
    lambda report,basis: basis["native_output_spec"]["opensees"]["selectors"][0].update(node_id=999),
    lambda report,basis: basis["native_output_spec"]["opensees"]["selectors"][0].update(load_case_id="invented"),
    lambda report,basis: basis["native_output_spec"]["opensees"]["model_units"].update(displacement="mm"),
])
def test_changed_native_binding_or_parser_is_blocked(tmp_path,mutation):
    _,report,basis=numerical_fixture(tmp_path);mutation(report,basis)
    assert evidence.inspect_results(report,tmp_path,basis,"opensees",{"A"})


def test_native_unit_conversion_is_pinned_by_reviewed_spec(tmp_path):
    output,report,basis=numerical_fixture(tmp_path)
    for criterion in basis["criteria"]["opensees"]: criterion.update(unit="mm",limit=3)
    rows=solver_results.extract_results(report,tmp_path,basis,"opensees")
    assert rows[0]["value"] == -2 and rows[0]["unit"] == "mm"
    solver_results.write_exchange(output,rows);report["output_hashes"][output.name]=evidence.sha(output)
    assert evidence.inspect_results(report,tmp_path,basis,"opensees",{"A"}) == []


def test_calculix_adapter_selects_native_step_set_node_and_rejects_duplicate(tmp_path):
    path=tmp_path/"native.dat"
    path.write_text(" S T E P 1\n displacements (vx,vy,vz) for set MID and time 1.0\n\n 21 0.0 -1.0D-1 0.0\n")
    selector=dict(step=1,set_name="MID",time=1,node_id=21,dof=2,quantity="displacement")
    assert solver_results.calculix_value(path,{},selector) == -.1
    with pytest.raises(ValueError): solver_results.calculix_value(path,{},dict(selector,step=2))
    path.write_text(path.read_text()+" 21 0.0 -1.0D-1 0.0\n")
    with pytest.raises(ValueError,match="duplicate"): solver_results.calculix_value(path,{},selector)


def test_matching_chainages_cannot_hide_other_line_supports():
    r=register()
    r["coverage_intervals"].append(dict(line_id="L2",coverage_group="track",from_station_m=0,to_station_m=50))
    for support in r["supports"]: support["scope_id"]="L2"
    assert any("another line/station" in f for f in inspect(r,{"L1","L2"}))
    r["shared_support_relationships"]=[dict(asset_id=a["asset_id"],support_id=s,review=review()) for a in r["assets"] for s in a["support_ids"]]
    extents=deepcopy(r["coverage_intervals"])
    # Complete second line with its own spans; the approved cross-line pairs remain explicit.
    r["assets"] += [{**a,"asset_id":a["asset_id"]+"-L2","line_id":"L2"} for a in deepcopy(r["assets"])]
    assert evidence.inspect_register(r,"a"*64,{"L1","L2"},set(),{},extents) == []
    r["shared_support_relationships"][0]["review"]["checker"]="designer"
    assert evidence.inspect_register(r,"a"*64,{"L1","L2"},set(),{},extents)


def test_station_support_requires_actual_line_affiliation():
    r=register();r["supports"][0].update(scope_type="station",scope_id="ST")
    assert any("another line/station" in f for f in inspect(r,stations={"ST"},station_lines={"ST":{"L2"}}))
    assert inspect(r,stations={"ST"},station_lines={"ST":{"L1"}}) == []


def test_self_declared_shorter_register_cannot_hide_missing_route():
    r=register();r["assets"].pop();r["coverage_intervals"][0]["to_station_m"]=25
    assert any("authoritative route" in f for f in inspect(r))

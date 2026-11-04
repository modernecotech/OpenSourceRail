from copy import deepcopy
from pathlib import Path
import gzip
import json
import shutil
import tempfile

import pytest

from engineering.design_search import search_delivery as d
from engineering.station_rail.common import encoded,identity,digest


@pytest.fixture(scope="module")
def package():
    with tempfile.TemporaryDirectory(prefix="search-delivery-test-",dir=d.ROOT/"build") as folder:
        parent=Path(folder)
        with pytest.MonkeyPatch.context() as m:
            c=d.native_campaign;spec=c.specification()
            spec.update(proposals_per_generation=4,evaluations_per_generation=2,detailed_finalists=1)
            spec["refinement"]["maximum_new_assessments"]=2
            m.setattr(c,"specification",lambda root=c.ROOT:deepcopy(spec))
            result=d.run(search_state=parent/"search",output=parent/"delivery",generations=0,
                maximum_new_evaluations=0,section_torsion_jobs=0,native_cad_jobs=0)
        yield parent/"delivery",result


def stage(folder,name):return d._read(folder/(name+".json.gz"),compressed=True)


def test_finalist_drives_every_canonical_stage_and_cost_scope(package):
    folder,result=package;handoff=stage(folder,"input")
    assert result["verified"] and result["computational_workflow_complete"]
    assert result["native_geometry_complete"] is False
    assert result["cost_scopes"]==14 and result["manufacturing_routes"]>0
    assert result["body_candidate_id"]!=result["candidate_id"]
    structure=stage(folder,"structure")
    assert structure["coarse_frame"]["candidate_id"]==result["body_candidate_id"]
    assert structure["coarse_frame"]["native_admission"] is False
    assert result["structural_model_holds"]==structure["coarse_frame"]["domain_holds"]
    for name in d.STAGES:
        value=stage(folder,name)
        assert value["candidate_id"]==(result["body_candidate_id"] if name=="geometry" else result["candidate_id"])
    inventory=stage(folder,"inventory")
    assert inventory["known_accounted_mass_subtotal_kg"]==pytest.approx(handoff["bundle"]["mass"]["accounted_tare_kg_per_car"])
    assert result["complete_installed_mass_kg"] is None
    assert all(result[k] is False for k in d.FLAGS)


def test_assumed_journeys_cannot_fill_supported_motion_hold(package):
    folder,result=package;supported=stage(folder,"supported_motion");conditional=stage(folder,"conditional_journey")
    assert supported["forward_motion"]["execution"]=="not-run"
    assert supported["forward_motion"]["admission"]["admitted"] is False
    assert len(conditional["cases"])==3
    for row in conditional["cases"]:
        assert row["test_only"] is True and row["available_motor_map_id"] is None
        assert row["physical_journey_completed"] is False
    assert result["physical_journey_completed"] is False


def test_workforce_accounts_for_distinct_shifts_and_disabled_drafts(package):
    folder,_=package;plan=stage(folder,"work_plan");cost=stage(folder,"economics")["model_cost"]
    assert plan["production_shifts_per_day"]==plan["civil_shifts_per_day"]==2
    assert plan["operations_shifts_per_day_cases"]==[2,2,3]
    assert plan["operations_staffing"]==next(r for r in cost["cost_line_items"] if r["line_key"]=="control-room-and-station-staffing")["quantity"]
    for lane in plan["factory_lanes"]:
        for case in d.model_cost.CASES:
            assert lane["staffed_positions_across_shifts"][case]==2*lane["parallel_lanes"][case]
    assert len(plan["ERPNext"]["routings"])==cost["provisional_manufacturing_plan"]["route_count"]
    assert {r["source_route_id"] for r in plan["ERPNext"]["routings"]}=={r["route_id"] for r in cost["provisional_manufacturing_plan"]["routes"]}
    for row in plan["ERPNext"]["routings"]+plan["Frappe_HR"]["shift_type_drafts"]:
        assert row["docstatus"]==0 and row["disabled"]==1 and row["submission_allowed"] is False
    assert plan["external_transactions_performed"] is False and plan["production_orders"]==[]
    assert plan["controls"]["movement_authority"] is False and plan["controls"]["command_tags"]==[]


def test_full_numerical_replay_uses_no_search_or_native_exports(package,monkeypatch):
    folder,expected=package
    def forbidden(*args,**kwargs):raise AssertionError("Read-only replay launched search/native geometry")
    from engineering.design_search import search_geometry
    monkeypatch.setattr(d.native_campaign,"run",forbidden)
    monkeypatch.setattr(search_geometry.grammar_geometry,"export",forbidden)
    monkeypatch.setattr(search_geometry.wheel_twin,"_ifc",forbidden)
    result=d.verify(folder,replay=True)
    assert result["replayed"] and result["package_id"]==expected["package_id"]


def reseal(folder,name,value):
    path=folder/(name+".json.gz");path.write_bytes(gzip.compress(encoded(value),mtime=0))
    index=json.loads((folder/"index.json").read_bytes());index["stage_ids"][name]=identity(value)
    index["package_id"]=identity({k:v for k,v in index.items() if k!="package_id"})
    (folder/"index.json").write_bytes(encoded(index))
    manifest=json.loads((folder/"manifest.json").read_bytes());manifest["package_id"]=index["package_id"]
    manifest["files_sha256"][path.name]=digest(path);manifest["files_sha256"]["index.json"]=digest(folder/"index.json")
    manifest["manifest_id"]=identity({k:v for k,v in manifest.items() if k!="manifest_id"})
    (folder/"manifest.json").write_bytes(encoded(manifest))


@pytest.mark.parametrize("mutation",["identity","release","numerical"])
def test_resealed_mixed_promoted_or_wrong_result_rejected(package,tmp_path,mutation):
    source,_=package;folder=tmp_path/"copy";shutil.copytree(source,folder)
    name="supported_motion";value=stage(folder,name)
    if mutation=="identity":value["candidate_id"]="0"*64
    elif mutation=="release":value["physical_accepted"]=True
    else:value["required_demand"]["trace_sha256"]="0"*64
    reseal(folder,name,value)
    with pytest.raises(ValueError,match="candidate|release|replay"):
        d.verify(folder,replay=mutation=="numerical")


def test_storage_is_compact_and_immutable(package):
    folder,result=package
    index=json.loads((folder/"index.json").read_bytes())
    assert "inventory" not in index and set(index["stage_ids"])==set(d.STAGES)
    assert result["compressed_package_bytes"]<2_000_000
    with pytest.raises(FileExistsError):d.run(search_state=folder.parent/"search",output=folder)


def test_sources_paths_and_reader_limits_fail_closed(package,tmp_path,monkeypatch):
    folder,_=package
    with pytest.raises(ValueError,match="private"):d._private_path(tmp_path,d.ROOT)
    bad=tmp_path/"bad.json";bad.write_text('{"same":1,"same":2}')
    with pytest.raises(ValueError,match="Duplicate"):d._read(bad)
    monkeypatch.setitem(d.LOADED,d.PRODUCER,"0"*64)
    with pytest.raises(ValueError,match="source changed"):d.verify(folder)


def test_research_delivery_cli_exposes_bounded_run_options():
    import subprocess,sys
    result=subprocess.run([sys.executable,"-m","engineering.design_search.search_delivery","run","--help"],cwd=d.ROOT,
        capture_output=True,text=True,timeout=15,check=True)
    assert "--search-state" in result.stdout and "--native-cad" in result.stdout


def test_native_geometry_reuse_has_a_separate_explicit_budget(package):
    folder,_=package
    with pytest.raises(ValueError,match="reuse or one new"):
        d.run(search_state=folder.parent/"search",output=folder.parent/"conflict",
            native_cad_jobs=1,reuse_geometry=folder/"geometry-export")


@pytest.mark.parametrize("mutation",["axis-order","gene","cost"])
def test_embedded_program_reconstructs_body_and_primary_cost(package,mutation):
    folder,_=package;handoff=stage(folder,"input");program=handoff["source_program"]
    if mutation=="axis-order":program["axis_names"].reverse()
    elif mutation=="gene":program["genes"][-1]=(program["genes"][-1]+1)%len(program["axes"][program["axis_names"][-1]])
    else:
        row=program["primary_row"];row["metrics"]["factory_gate_base_iqd"]=0.
        row["evaluation_id"]=identity({k:v for k,v in row.items() if k!="evaluation_id"})
    with pytest.raises(ValueError,match="axis|body|quantities"):
        d._verify_program(handoff["body"],program,d.ROOT)

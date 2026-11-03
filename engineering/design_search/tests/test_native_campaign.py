"""Real grammar successors, resumable budgets and cache integrity controls."""
from copy import deepcopy
import gzip
import json
import os

import pytest

from engineering.design_search import native_campaign as c, native_search
from engineering.station_rail.common import encoded, identity


@pytest.fixture
def small(monkeypatch):
    original=c.specification()
    spec=deepcopy(original)
    spec.update(proposals_per_generation=4,evaluations_per_generation=2,detailed_finalists=0,seed_bracing=[False])
    monkeypatch.setattr(c,"specification",lambda root=c.ROOT:deepcopy(spec))
    registry=c.shape_families.registry()
    recipes={name:registry[name] for name in ("aluminium_spaceframe","modular_segments")}
    monkeypatch.setattr(c.shape_families,"registry",lambda root=c.ROOT:deepcopy(recipes))
    return recipes


def read(result):
    return json.loads(open(result["output"]).read())


def test_new_generations_materialise_real_successors_and_resume_frontier(tmp_path,small):
    state=tmp_path/"state"
    first=read(c.run(state=state,generations=1,maximum_new_evaluations=1))
    assert len(first["generations"])==1
    assert len(first["deferred"])==3
    initial={a["proposal_id"] for a in first["attempts"]}
    second=read(c.run(state=state,generations=1,maximum_new_evaluations=1))
    assert len(second["deferred"])==2
    assert {a["proposal_id"] for a in second["attempts"]}>initial
    assert second["cache_statistics"]["completed_attempts_resumed"]==len(first["attempts"])
    assert len(second["generations"])==1  # No regeneration of the same genes.
    final=read(c.run(state=state,generations=2,maximum_new_evaluations=8))
    assert len(final["generations"])==2
    seeds={a["candidate_id"] for a in final["attempts"] if a["operator"]=="seed"}
    successors=[a for a in final["attempts"] if a["generation"]>0 and a.get("candidate_id") not in seeds]
    assert successors
    evaluations={e["evaluation_id"]:e for e in final["evaluations"]}
    for attempt in final["attempts"]:
        assert attempt["variable_registry_id"]==final["contract"]["variable_registry_id"]
        for parent in attempt["parent_evaluations"]:
            assert evaluations[parent["evaluation_id"]]["candidate_id"]==parent["candidate_id"]
    assert final["integrated_selection"] is None
    assert final["numerical_solver_dispatch_count"]==0
    assert all(final[k] is False for k in c.FLAGS)


def test_inactive_parameter_keeps_distinct_definitions_without_overwriting_archive(tmp_path,small,monkeypatch):
    original=c.NativeSearch.propose
    def alias_proposals(kernel,**request):
        result=original(kernel,**request)
        domains=c.axes();names=list(domains)
        parent=next(p for p in request["parents"] if p["genes"][0]==domains["family"].index("aluminium_spaceframe"))
        programs=[]
        for thickness in (.015,.04):
            genes=parent["genes"].copy();genes[names.index("core_thickness_m")]=domains["core_thickness_m"].index(thickness)
            programs.append(dict(genes=genes,operator="exploit",parent_candidate_ids=[parent["candidate_id"]]))
        return dict(result,proposals=programs)
    monkeypatch.setattr(c.NativeSearch,"propose",alias_proposals)
    value=read(c.run(state=tmp_path,generations=1,maximum_new_evaluations=2))
    seed=next(a for a in value["attempts"] if a["operator"]=="seed" and a["genes"][0]==0)
    aliases=[e for e in value["evaluations"] if e["candidate_id"]==seed["candidate_id"]]
    assert len(aliases)==3
    assert len({e["definition_id"] for e in aliases})==3
    assert value["archive_contexts"][seed["candidate_id"]]==seed["evaluation_id"]


def candidate(small):
    return c.grammar.build(c.grammar.parameters(),recipes=small,
        reason="Native-search materialisation; ancestry is bound by the proposal record")


def test_geometry_cache_rejects_resealed_manufacturing_change(tmp_path,small):
    parameters=c.grammar.parameters()
    c._geometry(parameters,small,tmp_path,c.ROOT)
    path=next((tmp_path/"geometry").iterdir())
    value=json.loads(gzip.decompress(path.read_bytes()))
    value["candidate"]["parts"][0]["process"]="FORGED-PROCESS"
    value["candidate"].pop("definition_id")
    value["candidate"]["definition_id"]=identity(value["candidate"])
    value.pop("record_id");value["record_id"]=identity(value)
    path.write_bytes(gzip.compress(encoded(value),mtime=0))
    with pytest.raises(RuntimeError,match="does not replay"):
        c._geometry(parameters,small,tmp_path,c.ROOT)


def test_resealed_zero_mass_and_cost_cannot_enter_archive(tmp_path,small):
    body=candidate(small);a=c.model_cost.assumptions()
    c._evaluate(body,a,tmp_path,c.ROOT)
    path=next((tmp_path/"stock-cost").iterdir());value=json.loads(path.read_bytes())
    value["cost_estimate"]={"candidate_id":body["candidate_id"]}
    value["metrics"]={key:0 for key in c.OBJECTIVES}
    value.pop("evaluation_id");value["evaluation_id"]=identity(value)
    path.write_bytes(encoded(value))
    with pytest.raises(RuntimeError,match="Conflicting immutable"):
        c._evaluate(body,a,tmp_path,c.ROOT)


@pytest.mark.parametrize("kind",["fifo","symlink","oversize"])
def test_cache_reader_rejects_special_or_oversized_files(tmp_path,kind):
    path=tmp_path/"record.json"
    if kind=="fifo":os.mkfifo(path)
    elif kind=="symlink":
        original=tmp_path/"original";original.write_bytes(b"{}\n");path.symlink_to(original)
    else:
        with path.open("wb") as handle:handle.truncate(native_search.MAX_BYTES+1)
    with pytest.raises((ValueError,RuntimeError)):
        c._store(path,{})


def test_source_contract_includes_bridge_and_stage_cost_implementation(small,tmp_path):
    assert "engineering/design_search/native_search.py" in c._sources(c.ROOT)
    body=candidate(small);a=c.model_cost.assumptions()
    value,_=c._evaluate(body,a,tmp_path,c.ROOT)
    assert c.PRODUCER in value["request"]["evaluator_sources"]


def test_cheap_stage_matches_existing_cost_and_does_not_invent_equipment(tmp_path,small):
    body=candidate(small);a=c.model_cost.assumptions()
    cheap,_=c._evaluate(body,a,tmp_path,c.ROOT)
    reference=c.design_portfolio._evaluate(body,small[body["parameters"]["family"]],"control",a,c.ROOT)
    assert cheap["metrics"]["nominal_stock_kg"]==pytest.approx(reference["metrics"]["known_gross_structure_stock_kg"])
    assert cheap["cost_estimate"]==reference["cost_estimate"]
    assert cheap["complete_installed_mass_kg"] is None
    assert cheap["complete_installed_cost_iqd"] is None
    assert cheap["structural_analysis"]=="not-run"


def test_actual_evaluation_allocation_retains_all_exploration_categories():
    programs=[dict(genes=[i],operator=op) for i,op in enumerate(
        ["exploit"]*30+["alternative-family"]*30+["unconventional"]*30)]
    chosen=c._shortlist(programs,list(range(90)),10)
    counts={op:sum(programs[i]["operator"]==op for i in chosen) for op in (
        "exploit","alternative-family","unconventional")}
    assert counts==dict(exploit=5,**{"alternative-family":3,"unconventional":2})


def test_resealed_frontier_edit_cannot_borrow_rust_program_identity(tmp_path,small):
    result=read(c.run(state=tmp_path,generations=1,maximum_new_evaluations=1))
    path=tmp_path/"checkpoints"/(result["contract_id"]+".json")
    value=json.loads(path.read_bytes())
    value["deferred"][0]["genes"][1]=(value["deferred"][0]["genes"][1]+1)%6
    value.pop("checkpoint_id");value["checkpoint_id"]=identity(value)
    path.write_bytes(encoded(value))
    with pytest.raises(RuntimeError,match="immutable generation journal"):
        c.run(state=tmp_path,generations=1,maximum_new_evaluations=1)


def test_checkpoint_size_rejection_preserves_last_resumable_bytes(tmp_path,monkeypatch):
    path=tmp_path/"checkpoint.json"
    c._checkpoint(path,{"previous":"valid"});original=path.read_bytes()
    monkeypatch.setattr(native_search,"MAX_BYTES",len(original)+1)
    with pytest.raises(RuntimeError,match="prior checkpoint"):
        c._checkpoint(path,{"oversize":"x"*1000})
    assert path.read_bytes()==original


def test_checkpoint_refuses_dangling_symlink(tmp_path):
    path=tmp_path/"checkpoint.json";path.symlink_to(tmp_path/"missing")
    with pytest.raises(RuntimeError,match="Symlinked checkpoint"):
        c._checkpoint(path,{"value":"new"})
    assert path.is_symlink()


@pytest.mark.parametrize("mutation",["remove-proposal","duplicate-proposal","remove-seed","duplicate-seed"])
def test_resealed_checkpoint_cannot_drop_or_duplicate_frontier_work(tmp_path,small,mutation):
    result=read(c.run(state=tmp_path,generations=1,maximum_new_evaluations=1))
    path=tmp_path/"checkpoints"/(result["contract_id"]+".json")
    value=json.loads(path.read_bytes())
    if mutation=="remove-proposal":value["deferred"].pop()
    elif mutation=="duplicate-proposal":value["deferred"].append(deepcopy(value["deferred"][0]))
    elif mutation=="remove-seed":value["attempts"]=[p for p in value["attempts"] if p["operator"]!="seed"][1:]
    else:value["attempts"].append(deepcopy(next(p for p in value["attempts"] if p["operator"]=="seed")))
    value.pop("checkpoint_id");value["checkpoint_id"]=identity(value)
    path.write_bytes(encoded(value))
    with pytest.raises(RuntimeError,match="coverage/uniqueness"):
        c.run(state=tmp_path,generations=1,maximum_new_evaluations=1)


def test_cost_model_domain_failure_is_preserved_without_zero_estimate(tmp_path,small,monkeypatch):
    def unavailable(*args,**kwargs):raise ValueError("Unsupported material cost route")
    monkeypatch.setattr(c.design_portfolio,"_factory_gate_stock_estimate",unavailable)
    with pytest.raises(ValueError,match="No executable seed"):
        c.run(state=tmp_path,generations=0)
    attempts=[json.loads(path.read_bytes()) for path in (tmp_path/"attempts").iterdir()]
    assert len(attempts)==2
    assert all(a["state"]=="cost-model-domain-unresolved" and a["candidate_id"] for a in attempts)
    assert all("evaluation_id" not in a for a in attempts)


def test_runtime_is_an_explicit_search_and_cache_context(tmp_path,small):
    body=candidate(small);a=c.model_cost.assumptions()
    value,_=c._evaluate(body,a,tmp_path,c.ROOT)
    assert value["request"]["runtime"]["numpy_version"]==c.np.__version__
    assert c._geometry_key(body["parameters"],small,c.ROOT)["runtime"]==c._runtime()


def test_run_fails_closed_on_unsafe_geometry_cache(tmp_path,small):
    parameters=c.grammar.parameters()
    key=identity(c._geometry_key(parameters,small,c.ROOT))
    path=tmp_path/"geometry"/(key+".json.gz");path.parent.mkdir();os.mkfifo(path)
    with pytest.raises(RuntimeError,match="Cache integrity/read failure"):
        c.run(state=tmp_path,generations=0)
    assert not (tmp_path/"attempts").exists()


def test_overlapping_coordinators_are_rejected_without_waiting(tmp_path,small):
    with c._state_lock(tmp_path):
        with pytest.raises(RuntimeError,match="active coordinator"):
            c.run(state=tmp_path,generations=0)


def test_topology_genome_changes_actual_geometry_and_preserves_materialisation_parent(tmp_path,small):
    parameters=c.grammar.parameters()
    base,_=c._geometry(parameters,small,tmp_path,c.ROOT)
    child,_=c._geometry(parameters,small,tmp_path,c.ROOT,"add-longitudinal-spine")
    assert child["candidate_id"]!=base["candidate_id"]
    assert child["parent_candidate_ids"]==[base["candidate_id"]]
    assert len(child["structure"]["members"])>len(base["structure"]["members"])
    assert child["retained_equipment_accounts"]==base["retained_equipment_accounts"]
    a=c.model_cost.assumptions()
    row,_=c._evaluate(child,a,tmp_path,c.ROOT)
    reference,_=c._evaluate(base,a,tmp_path,c.ROOT)
    assert row["descriptor"]["topology"]=="add-longitudinal-spine"
    assert row["metrics"]["nominal_stock_kg"]>reference["metrics"]["nominal_stock_kg"]
    assert row["complete_installed_mass_kg"] is None


def controls(monkeypatch):
    spec=c.specification();spec.update(seed_bracing=[False,True],detailed_finalists=1)
    spec["refinement"]["maximum_new_assessments"]=2
    monkeypatch.setattr(c,"specification",lambda root=c.ROOT:deepcopy(spec))


def test_finalists_receive_analytical_evidence_with_zero_native_budget(tmp_path,small,monkeypatch):
    controls(monkeypatch)
    def forbidden(*args,**kwargs):raise AssertionError("Zero budget dispatched a solver")
    monkeypatch.setattr(c.native_refinement.grammar_structure,"run",forbidden)
    value=read(c.run(state=tmp_path,generations=0,native_jobs=0))
    assert len(value["refinement"]["assessments"])==2
    assert value["refinement"]["axial_model_archives"]
    assert value["refinement"]["assessment_counts"]==dict(inherited=0,additional=2,maximum_additional=2,total=2,maximum_total=64)
    assert value["numerical_solver_dispatch_count"]==0
    assert value["native_dispatch_allowed"] is False
    assert value["refinement"]["native_evidence_reused"]==0
    assert all(not a["whole_body_rejected"] for a in value["refinement"]["assessments"])
    for package in value["refinement"]["packages"]:
        assert package["request"]["resources"]["native_jobs"]==0
        assert package["result"]["native_state"]=="not-requested"


def test_missing_solver_is_a_preserved_dependency_hold(tmp_path,small,monkeypatch):
    controls(monkeypatch)
    monkeypatch.setattr(c.native_refinement,"_tool",lambda:dict(path="/missing/ccx",sha256=None,available=False))
    def forbidden(*args,**kwargs):raise AssertionError("Missing solver was dispatched")
    monkeypatch.setattr(c.native_refinement.grammar_structure,"run",forbidden)
    value=read(c.run(state=tmp_path,generations=0,native_jobs=1))
    assert value["numerical_solver_dispatch_count"]==0
    assert any(p.get("state")=="solver-dependency-held" for p in value["refinement"]["packages"])
    assert value["physical_accepted"] is False


def test_topology_shortlist_does_not_starve_heavier_new_load_paths():
    programs=[dict(genes=[t,i],operator="unconventional") for t in range(3) for i in range(5)]
    proxies=[float(100*t+i) for t in range(3) for i in range(5)]
    chosen=c._shortlist(programs,proxies,3,topology_axis=0)
    assert {programs[i]["genes"][0] for i in chosen}=={0,1,2}


def test_structural_feedback_changes_rust_parent_weights_without_dropping_unknowns(tmp_path,small,monkeypatch):
    spec=c.specification();spec.update(seed_bracing=[False,True],detailed_finalists=0)
    spec["feedback"].update(maximum_new_assessments=2,maximum_total_assessments=4)
    monkeypatch.setattr(c,"specification",lambda root=c.ROOT:deepcopy(spec))
    def forbidden(*args,**kwargs):raise AssertionError("Parent feedback dispatched a native solver")
    monkeypatch.setattr(c.native_refinement.grammar_structure,"run",forbidden)
    result=read(c.run(state=tmp_path,generations=2,maximum_new_evaluations=8,native_jobs=0))
    snapshots=[json.loads((tmp_path/"feedback"/(g["parent_feedback_snapshot_id"]+".json")).read_bytes()) for g in result["generations"]]
    first=snapshots[0]["plan"]
    assert len(first["parents"])==4 and all(p["weight"]>0 for p in first["parents"])
    assert any(p["weight"]>=3 and p["candidate_id"] not in first["cost_archive"]["retained_candidate_ids"] for p in first["parents"])
    assert len(snapshots[1]["observations"])>len(snapshots[0]["observations"])
    assert result["refinement"]["assessment_counts"]==dict(inherited=4,additional=0,maximum_additional=12,total=4,maximum_total=64)
    assert result["refinement"]["axial_model_archives"]==result["refinement"]["parent_feedback_plan"]["axial_archives"]
    for generation,snapshot in zip(result["generations"],snapshots):
        journal=json.loads((tmp_path/"generated"/(generation["generation_id"]+".json")).read_bytes())
        expected={p["candidate_id"]:p["weight"] for p in snapshot["plan"]["parents"]}
        assert {p["candidate_id"]:p["weight"] for p in journal["request"]["parents"]}==expected
        assert all(p["parent_feedback_snapshot_id"]==snapshot["snapshot_id"] for p in journal["programs"])
    assert result["numerical_solver_dispatch_count"]==0 and result["integrated_selection"] is None


def test_feedback_snapshot_edit_cannot_be_resealed_into_generation_history(tmp_path,small):
    result=read(c.run(state=tmp_path,generations=1,maximum_new_evaluations=1))
    sid=result["generations"][0]["parent_feedback_snapshot_id"]
    path=tmp_path/"feedback"/(sid+".json");value=json.loads(path.read_bytes())
    value["plan"]["parents"][0]["weight"]=1000
    path.write_bytes(encoded(value))
    with pytest.raises(RuntimeError,match="feedback does not replay"):
        c.run(state=tmp_path,generations=1,maximum_new_evaluations=1)


def test_comparison_cohort_binds_functional_loading_not_candidate_mass(small,tmp_path):
    p=c.grammar.parameters();p["braced"]=True
    thin,_=c._geometry(p,small,tmp_path,c.ROOT)
    p["chord_wall_m"]*=1.5
    thick,_=c._geometry(p,small,tmp_path,c.ROOT)
    assert thin["known_structure_stock_kg"]!=thick["known_structure_stock_kg"]
    assert c._comparison_context(thin)==c._comparison_context(thick)
    other=deepcopy(thick);other["structure"]["load_basis"]["normal_people"]+=1
    assert c._comparison_context(thin)!=c._comparison_context(other)

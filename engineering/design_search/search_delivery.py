"""One searched body through a canonical, unreleased railway delivery study.

The supported-motion hold and the assumption-only journey are separate records.
Completing this computational workflow cannot release a vehicle or a railway.
Large records are stored once, compressed; the index contains identities only.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from math import ceil
from pathlib import Path
import argparse
import gzip
import json
import os
import platform
import shutil
import stat
import sys
import time

import numpy as np
import scipy

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity, digest
from engineering.development_baseline import factory_draft
from . import (native_campaign, shape_families, design_grammar, railway_bundle,
               railway_campaign, system_inventory, system_motion, model_cost,
               conditional_journey_study, railway_delivery, grammar_geometry,
               native_refinement, frame_refinement)

PRODUCER = "engineering/design_search/search_delivery.py"
MAX_BYTES = 64 * 1024**2
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, physical_journey_completed=False,
             selected_reference_changed=False)
MODULES = (railway_delivery, conditional_journey_study, system_inventory,
           system_motion, grammar_geometry, native_refinement, frame_refinement)
LOADED={m.PRODUCER:digest(m.__file__) for m in MODULES}
LOADED[PRODUCER]=digest(__file__)
STAGES = ("geometry", "inventory", "interfaces", "structure", "architecture", "propulsion",
          "supported_motion", "conditional_journey", "civil", "economics",
          "delivery", "work_plan")


def _runtime():
    return dict(python=platform.python_version(), executable=str(Path(sys.executable).resolve()),
        numpy=np.__version__, scipy=scipy.__version__,
        threads={k:os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")})


def _sources(root):
    from . import search_geometry
    if any(digest(Path(root)/p)!=sha for p,sha in LOADED.items()):
        raise ValueError("Loaded search delivery source changed")
    paths = [PRODUCER, search_geometry.PRODUCER, conditional_journey_study.CONFIG,
             "engineering/development_baseline/factory_draft.py", "engineering/development_baseline/__init__.py",
             *[m.PRODUCER for m in MODULES]]
    return dict(sorted({**native_campaign._sources(root), **railway_campaign.source_epoch(root),
        **{p:digest(Path(root)/p) for p in paths}}.items()))


def _private_path(path,root):
    path=Path(path).absolute()
    if not path.resolve().is_relative_to(Path(root)/"build"):
        raise ValueError("Keep private search/delivery artifacts inside this checkout's build directory")
    for part in (path,*path.parents):
        if part==root:break
        if part.is_symlink():raise ValueError("Ordinary private artifact paths required")
    return path


def _read(path, *, compressed=False):
    path=Path(path)
    with path.open("rb") as source:
        before=os.fstat(source.fileno())
        if path.is_symlink() or not stat.S_ISREG(before.st_mode) or before.st_size>MAX_BYTES:
            raise ValueError("Bounded regular delivery record required")
        if compressed:
            with gzip.GzipFile(fileobj=source) as stream:raw=stream.read(MAX_BYTES+1)
        else:raw=source.read(MAX_BYTES+1)
        after=os.fstat(source.fileno())
    if len(raw)>MAX_BYTES or any(getattr(before,k)!=getattr(after,k) for k in
            ("st_dev","st_ino","st_size","st_mtime_ns","st_ctime_ns")):
        raise ValueError("Delivery record changed or exceeds its reader budget")
    def pairs(items):
        value={}
        for k,v in items:
            if k in value:raise ValueError("Duplicate delivery JSON key")
            value[k]=v
        return value
    def bad(_):raise ValueError("Nonfinite delivery JSON value")
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)


def _write(path,value,*,compressed=False):
    raw=encoded(value)
    if len(raw)>MAX_BYTES:raise ValueError("Delivery record exceeds its writer budget")
    with Path(path).open("xb") as target:
        target.write(gzip.compress(raw,compresslevel=3,mtime=0) if compressed else raw)


def _body(search,state,body_id,root):
    """Reconstruct the evaluated physical program, never accept an attached mesh."""
    rows={r["candidate_id"]:r for r in search["evaluations"]
          if search["archive_contexts"].get(r["candidate_id"])==r["evaluation_id"]}
    if body_id is None:
        eligible={r["assessment"]["candidate_id"] for r in search["refinement"]["frame_assessments"]}
        if not eligible:raise ValueError("A frame-assessed research finalist is required for this handoff")
        body_id=min(eligible,key=lambda cid:(rows[cid]["metrics"]["factory_gate_base_iqd"],cid))
    if body_id not in rows:raise ValueError("Requested body has no primary nominal-stock evaluation")
    row=rows[body_id]
    attempt=next(a for a in search["attempts"] if a.get("evaluation_id")==row["evaluation_id"])
    # Canonical JSON sorts mapping keys. Genes follow the configuration's
    # declared axis order, so restore that order rather than iterating JSON.
    domains=native_campaign.axes(root)
    if domains!=search["axes"]:raise ValueError("Search genome domains differ from the current registry")
    body=native_campaign._load_genome(attempt["genes"],domains,shape_families.registry(root),Path(state),root)
    if body["candidate_id"]!=body_id or body["definition_id"]!=row["definition_id"]:
        raise ValueError("Search handoff mixed the physical body and evaluation definition")
    program=dict(genes=deepcopy(attempt["genes"]),axis_names=list(domains),axes=domains,
        generation=attempt["generation"],operator=attempt["operator"],parent_candidate_ids=attempt["parent_candidate_ids"],
        proposal_id=attempt["proposal_id"],primary_row=row)
    return body,row,program


def _verify_program(body,program,root):
    domains=native_campaign.axes(root)
    if program["axes"]!=domains or program["axis_names"]!=list(domains):raise ValueError("Source genome axis order differs")
    parameters,topology=native_campaign._decode_genes(program["genes"],domains)
    reconstructed,_=native_campaign._materialise(parameters,shape_families.registry(root),topology)
    if reconstructed!=body:raise ValueError("Physical source program does not reconstruct the handed-off body")
    row=program["primary_row"]
    if (row["evaluation_id"]!=identity({k:v for k,v in row.items() if k!="evaluation_id"})
            or row["candidate_id"]!=body["candidate_id"] or row["definition_id"]!=body["definition_id"]
            or any(row.get(k) is not False for k in native_campaign.FLAGS)):
        raise ValueError("Primary search evaluation identity or body differs")
    cost=native_campaign.design_portfolio._factory_gate_stock_estimate(body,model_cost.assumptions(root),root)
    metrics=dict(nominal_stock_kg=sum(p["mass_kg"] for p in body["parts"]),
        factory_gate_base_iqd=cost["scenarios_iqd"]["base"],factory_process_hours=cost["process_hours"]["base"])
    if row["metrics"]!=metrics or row["cost_estimate"]!=cost:raise ValueError("Primary search quantities/cost do not replay")


def work_plan(bundle,inventory,cost,delivery):
    """Serialize existing process-hour proxies and shifts into disabled drafts."""
    cid=bundle["candidate_id"]
    for value in (inventory,cost,delivery):
        if value["candidate_id"]!=cid:raise ValueError("Work plan mixes canonical railway identities")
    production=cost["production_plan"];routes=cost["provisional_manufacturing_plan"]["routes"]
    scope=identity(dict(purpose="research-delivery-demonstration",candidate_id=cid))
    candidate=dict(selection_id=scope,evaluation_id=cost["evaluation_id"],**{k:bundle[k] for k in
        ("candidate_id","body_candidate_id","support_component_id","propulsion_component_id")})
    packages=[dict(line_id=r["cost_line_id"],line_key=r["stock_id"],process_template=r["provisional_process"],
        process_hours_per_train={case:r["labor_hours_per_car"][case]*bundle["cars"] for case in model_cost.CASES},
        occurrence_ids=[r["stock_id"]],source_ids=[r["route_id"]]) for r in routes]
    resources=factory_draft.resource_envelope(packages,candidate,cost["evaluation_id"],production["productive_utilisation"])
    # Stock-occurrence routing is a conditional capacity schedule, not a machine
    # programme. Keep assembly precedence and unlocated equipment separately.
    schedule=[];families={}
    for route in routes:families.setdefault(route["provisional_process"],[]).append(route)
    days=production["planned_working_days"]
    capacity_day=(production["production_shifts_per_day"]*production["production_hours_per_shift"]
                  *production["productive_utilisation"])
    lanes=[]
    for process,parts in sorted(families.items()):
        hours={case:sum(r["fleet_labor_hours"][case] for r in parts) for case in model_cost.CASES}
        count={case:max(1,ceil(hours[case]/(days*capacity_day))) for case in model_cost.CASES}
        lane_id=identity(dict(candidate_id=cid,process=process))
        lanes.append(dict(resource_id=lane_id,process=process,parallel_lanes=count,
            persons_per_lane_per_shift_hypothesis=1,staffed_positions_across_shifts={case:
                count[case]*production["production_shifts_per_day"] for case in model_cost.CASES},
            physical_machine_selected=False,tooling_qualified=False))
        elapsed={case:0. for case in model_cost.CASES}
        for row in sorted(parts,key=lambda r:r["stock_id"]):
            start=dict(elapsed)
            for case in model_cost.CASES:elapsed[case]+=row["fleet_labor_hours"][case]/(count[case]*capacity_day)
            schedule.append(dict(route_id=row["route_id"],stock_id=row["stock_id"],resource_id=lane_id,
                fleet_quantity=row["fleet_cars"],start_workday=start,finish_workday=dict(elapsed),
                basis="Perfectly divisible batches and one person-hour per process-hour; no machine, cure, rework or arrival-time validation"))
    def draft(doctype,**fields):
        value=dict(doctype=doctype,candidate_id=cid,body_candidate_id=bundle["body_candidate_id"],
            docstatus=0,disabled=1,submission_allowed=False,import_validation_required=True,**fields)
        value["draft_id"]=identity(value);return value
    routing=[draft("Routing",source_route_id=r["route_id"],stock_id=r["stock_id"],
        process_template=r["provisional_process"],hours_per_car=r["labor_hours_per_car"],
        source_cost_line_id=r["cost_line_id"],approved_work_instruction=None) for r in routes]
    shifts=[draft("Shift Type",name="Research factory/civil shift "+str(i+1),hours=8,
        staffed_independently=True,company=None) for i in range(2)]
    operations=next(r for r in cost["cost_line_items"] if r["line_key"]=="control-room-and-station-staffing")["quantity"]
    value=dict(schema="osr-searched-railway-work-plan/1",candidate_id=cid,body_candidate_id=bundle["body_candidate_id"],
        source_cost_evaluation_id=cost["evaluation_id"],research_selection_context_id=scope,
        source_manufacturing_plan_id=cost["provisional_manufacturing_plan"]["plan_id"],
        factory_resources=resources,factory_lanes=lanes,stock_batch_schedule=schedule,
        assembly_precedence=deepcopy(inventory["assembly_operation_graph"]),
        civil_schedule=deepcopy(production["construction_schedule_days"]),
        operations_staffing=deepcopy(operations),production_shifts_per_day=production["production_shifts_per_day"],
        civil_shifts_per_day=production["civil_shifts_per_day"],operations_shifts_per_day_cases=production["operations_shifts_per_day_cases"],
        ERPNext=dict(items=delivery["ERPNext"]["items"],BOM=delivery["ERPNext"]["BOM"],routings=routing,
            workstations=[draft("Workstation",resource_plan=r) for r in lanes],
            projects=[draft("Project",source_cost_evaluation_id=cost["evaluation_id"],
                planned_calendar_dates=None,planning_workdays=days,construction=production["construction_schedule_days"])],posted=False),
        Frappe_HR=dict(shift_type_drafts=shifts,staffing_plan_drafts=[draft("Staffing Plan",
            resource_plan=r,actual_employees=None) for r in lanes],operations_staffing_cases=deepcopy(operations),posted=False),
        controls=dict(candidate_id=cid,purpose="Read-only asset/engineering handoff",movement_authority=False,
            command_tags=[],protection_qualified=False,live_gateway_configured=False),
        external_transactions_performed=False,production_orders=[],ready_for_import=False,
        limitations=["Capacity and batch schedule use provisional process-hour proxies, not measured machine cycles",
            "Parallel divisible batches, one-person lanes and complete input availability are unverified hypotheses",
            "Final assembly, equipment installation, QA/curing and procurement remain explicit separate accounts and precedence requirements",
            "Civil schedule retains the cost engine's concurrent crew envelope; it is not an approved site critical path",
            "ERPNext/Frappe custom fields, company, skills, relief rosters, safe work instructions and calendar require review"],**FLAGS)
    value["evaluation_id"]=identity(value);return value


def _calculate(body,bundle,root):
    geometry=grammar_geometry.mass_properties(body)
    inventory=system_inventory.evaluate(body,bundle_id=bundle["candidate_id"],source_root=root,
        component_substitutions=bundle["component_substitutions"],extra_equipment_tasks=bundle["unweighed_architecture_equipment"])
    if abs(inventory["known_accounted_mass_subtotal_kg"]-bundle["mass"]["accounted_tare_kg_per_car"])>1e-6:
        raise ValueError("Search inventory and railway dynamics use different mass accounts")
    interfaces=railway_campaign._interfaces(body,bundle)
    axial=native_refinement.assess(body,root=root)
    frame=frame_refinement.assess(body,root=root)
    if frame["model"] is not None and abs(frame["model"]["load_basis"]["sprung_mass_hypothesis_kg"]-bundle["normal_sprung_mass_hypothesis_kg"])>1e-6:
        raise ValueError("Body frame and railway bundle have different structural load masses")
    structure=dict(candidate_id=bundle["candidate_id"],body_candidate_id=body["candidate_id"],
        axial= axial,coarse_frame=frame,engineering_validated=False,
        purpose="Same-body axial and rigid-joint frame research hypotheses, not whole-vehicle qualification",**FLAGS)
    structure["evaluation_id"]=identity(structure)
    architecture=railway_bundle.assess_architecture(bundle)
    propulsion=railway_campaign.propulsion(bundle,architecture)
    supported=system_motion.evaluate(bundle,available_map=None)
    try:
        conditional=conditional_journey_study.evaluate_bundle(bundle,conditional_journey_study.specification(root),root)
    except ValueError as exc:
        # Definition/necessary-force failure is a terminal research result, never
        # a synthetic force-map admission or a zero-cost/mass substitute.
        if "Base assumed LIM force cannot reach" not in str(exc):raise
        conditional=dict(candidate_id=bundle["candidate_id"],body_candidate_id=body["candidate_id"],
            execution="infeasible-under-declared-base-force-assumption",reason=str(exc),cases=[],
            design_study_complete=True,journey_results_assumption_only=True,**FLAGS)
        conditional["evaluation_id"]=identity(conditional)
    civil=railway_bundle.assess_civil(bundle)
    economics=railway_campaign.economics(bundle,inventory,architecture,propulsion,supported,civil,root=root)
    delivery=railway_delivery.compile(bundle,body,inventory)
    plan=work_plan(bundle,inventory,economics["model_cost"],delivery)
    values=dict(zip(STAGES,(geometry,inventory,interfaces,structure,architecture,propulsion,supported,conditional,civil,economics,delivery,plan)))
    for name,value in values.items():
        expected=body["candidate_id"] if name=="geometry" else bundle["candidate_id"]
        if value["candidate_id"]!=expected:raise ValueError("End-to-end stage changed candidate: "+name)
    return values


def _summary(body,bundle,values,native):
    cost=values["economics"]["model_cost"];inventory=values["inventory"];conditional=values["conditional_journey"]
    if cost["model_cost_missing_scopes"] or set(cost["required_cost_scopes"])!=set(model_cost.SCOPES):
        raise ValueError("Whole-railway cost scope is incomplete")
    routed=cost["provisional_manufacturing_plan"]["coverage"]
    if routed["unrouted_stock_ids"]:raise ValueError("Unrouted located body stock")
    return dict(candidate_id=bundle["candidate_id"],body_candidate_id=body["candidate_id"],
        bundle_definition_id=bundle["definition_id"],computational_workflow_complete=True,
        design_study_complete=conditional["design_study_complete"],
        native_geometry_complete=native["execution"]=="completed-known-stock",
        engineering_validated=False,approved_for_manufacture_or_operation=False,
        located_stock_occurrences=routed["located_stock_occurrences"],cost_scopes=len(cost["required_cost_scopes"]),
        accounted_tare_kg_per_car=bundle["mass"]["accounted_tare_kg_per_car"],
        complete_installed_mass_kg=None,model_based_installed_CAPEX_iqd=cost["model_based_installed_CAPEX_iqd"],
        model_based_whole_life_NPV_iqd=cost["model_based_whole_life_NPV_iqd"],
        conditional_journeys=[dict(case=r["case"],state=r["forward"]["state"],
            berth_stop=r["trajectory_summary"]["berth_stop"],elapsed_s=r["trajectory_summary"]["elapsed_s"])
            for r in conditional["cases"]],
        supported_journey_state=values["supported_motion"]["forward_motion"]["execution"],
        structural_model_holds=values["structure"]["coarse_frame"]["domain_holds"],
        open_component_tasks=len(inventory["component_tasks"]),
        manufacturing_routes=cost["provisional_manufacturing_plan"]["route_count"],
        operations_shifts_per_day_cases=cost["production_plan"]["operations_shifts_per_day_cases"],
        computational_scope="All declared stages have results or explicit infeasibility/physical-evidence holds; this is not installed design completeness",
        **FLAGS)


def run(*,search_state,output,body_candidate_id=None,root=ROOT,native_cad_jobs=0,
        generations=None,maximum_new_evaluations=None,section_torsion_jobs=1,reuse_geometry=None,
        canonical_backend="python",canonical_extension=None):
    from . import search_geometry
    root=Path(root).resolve()
    if root!=Path(ROOT).resolve():raise ValueError("Use the imported source checkout")
    output=_private_path(output,root);search_state=_private_path(search_state,root)
    if output.exists() or output.is_symlink():raise FileExistsError("Fresh immutable search delivery directory required")
    if type(native_cad_jobs) is not int or native_cad_jobs not in (0,1):raise ValueError("Explicit zero-or-one CAD job budget required")
    if reuse_geometry is not None and native_cad_jobs:
        raise ValueError("Choose exact geometry reuse or one new native CAD job")
    if os.statvfs(root).f_bavail*os.statvfs(root).f_frsize<4*1024**3:
        raise ValueError("At least 4 GiB free disk required before an end-to-end search handoff")
    sources=_sources(root);started=time.monotonic()
    search_summary=native_campaign.run(root=root,state=Path(search_state),generations=generations,
        maximum_new_evaluations=maximum_new_evaluations,section_torsion_jobs=section_torsion_jobs,
        canonical_backend=canonical_backend,canonical_extension=canonical_extension)
    search=_read(search_summary["output"])
    body,row,program=_body(search,search_state,body_candidate_id,root)
    bundle=railway_bundle.materialize(body,family="P1",root=root)
    output.mkdir(parents=True,exist_ok=False)
    # Failures preserve the exact selected inputs; no partial success manifest.
    handoff=dict(schema="osr-search-delivery-input/1",body=body,bundle=bundle,
        search_contract_id=search["contract_id"],search_run_id=search["run_id"],
        search_result_sha256=digest(search_summary["output"]),primary_evaluation_id=row["evaluation_id"],
        source_program=program,search_result_path=str(Path(search_summary["output"]).relative_to(root)),
        search_encoder=search["contract"].get("canonical_backend",dict(mode="python")),
        ancestry_scope="Exact source-program, physical body and primary quantity/cost replay; full parent-selection replay additionally needs the retained campaign journals",
        purpose="Demonstration handoff from the partial-cost finalist set; not an integrated or physical selection")
    _write(output/"input.json.gz",handoff,compressed=True)
    values=_calculate(body,bundle,root)
    for name,value in values.items():_write(output/(name+".json.gz"),value,compressed=True)
    reused_from=None
    if reuse_geometry is not None:
        previous=_private_path(reuse_geometry,root)
        native=search_geometry.verify(body,bundle,previous,root=root)
        if native["execution"]!="completed-known-stock":raise ValueError("Geometry reuse needs completed same-candidate CAD/IFC evidence")
        reused_from=dict(path=str(previous),manifest_id=native["manifest_id"])
        shutil.copytree(previous,output/"geometry-export")
        if search_geometry.verify(body,bundle,output/"geometry-export",root=root)!=native:
            raise ValueError("Copied exact geometry evidence differs")
    else:
        native=search_geometry.build(body,bundle,output/"geometry-export",root=root,native_cad_jobs=native_cad_jobs)
    summary=_summary(body,bundle,values,native)
    if _sources(root)!=sources:raise ValueError("End-to-end source epoch changed")
    index=dict(schema="osr-search-delivery-package/1",source_sha256=sources,runtime=_runtime(),
        input_id=identity(handoff),summary=summary,
        stage_ids={name:identity(value) for name,value in values.items()},
        native_geometry_id=identity(native),native_CAD_jobs_new=native_cad_jobs,
        geometry_reused_from=reused_from,**FLAGS)
    index["package_id"]=identity(index);_write(output/"index.json",index)
    files={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob("*")) if p.is_file()}
    manifest=dict(schema="osr-search-delivery-manifest/1",package_id=index["package_id"],files_sha256=files,**FLAGS)
    manifest["manifest_id"]=identity(manifest);_write(output/"manifest.json",manifest)
    result=verify(output,root=root,replay=False)
    return dict(result,elapsed_s=time.monotonic()-started,search_summary=search_summary)


def verify(output,*,root=ROOT,replay=False):
    from . import search_geometry
    output=Path(output);root=Path(root).resolve()
    if type(replay) is not bool:raise ValueError("Explicit replay policy required")
    if output.is_symlink() or not output.is_dir():raise ValueError("Regular search delivery directory required")
    paths=list(output.rglob("*"))
    if any(p.is_symlink() or not (p.is_file() or p.is_dir()) for p in paths):raise ValueError("Ordinary delivery package files required")
    manifest=_read(output/"manifest.json");index=_read(output/"index.json")
    if (manifest["manifest_id"]!=identity({k:v for k,v in manifest.items() if k!="manifest_id"})
            or manifest["files_sha256"]!={p.relative_to(output).as_posix():digest(p) for p in paths if p.is_file() and p!=output/"manifest.json"}):
        raise ValueError("Search delivery manifest or payload differs")
    if (index["package_id"]!=identity({k:v for k,v in index.items() if k!="package_id"})
            or manifest["package_id"]!=index["package_id"] or index["source_sha256"]!=_sources(root) or index["runtime"]!=_runtime()
            or any(v.get(k) is not False for v in (index,manifest) for k in FLAGS)):
        raise ValueError("Search delivery source, runtime, identity or disposition differs")
    handoff=_read(output/"input.json.gz",compressed=True);body=handoff["body"];bundle=handoff["bundle"]
    design_grammar.validate(body);railway_bundle.validate(bundle)
    if identity(handoff)!=index["input_id"] or body["candidate_id"]!=bundle["body_candidate_id"] or body["definition_id"]!=bundle["body_definition_id"]:
        raise ValueError("Search delivery input candidate differs")
    if railway_bundle.materialize(body,family="P1",root=root)!=bundle:raise ValueError("Canonical railway bundle does not replay")
    _verify_program(body,handoff["source_program"],root)
    if handoff["primary_evaluation_id"]!=handoff["source_program"]["primary_row"]["evaluation_id"]:
        raise ValueError("Input primary evaluation differs from its source program")
    values={name:_read(output/(name+".json.gz"),compressed=True) for name in STAGES}
    if index["stage_ids"]!={name:identity(value) for name,value in values.items()}:raise ValueError("Delivery stage identities differ")
    for name,value in values.items():
        expected=body["candidate_id"] if name=="geometry" else bundle["candidate_id"]
        if value.get("candidate_id")!=expected or ("body_candidate_id" in value and value["body_candidate_id"]!=body["candidate_id"]):
            raise ValueError("Delivery stage mixed canonical candidate: "+name)
        if any(value[k] is not False for k in FLAGS if k in value):raise ValueError("Delivery stage grants a release: "+name)
    native=search_geometry.verify(body,bundle,output/"geometry-export",root=root)
    if index["native_geometry_id"]!=identity(native) or _summary(body,bundle,values,native)!=index["summary"]:
        raise ValueError("Delivery completion or native geometry differs")
    reused=index.get("geometry_reused_from")
    if (type(index.get("native_CAD_jobs_new")) is not int or index["native_CAD_jobs_new"] not in (0,1)
            or (reused is not None and (index["native_CAD_jobs_new"]!=0 or reused["manifest_id"]!=native["manifest_id"]))
            or (reused is None and index["native_CAD_jobs_new"]!=native["native_CAD_jobs"])):
        raise ValueError("Native geometry execution/reuse accounting differs")
    if replay and _calculate(body,bundle,root)!=values:raise ValueError("End-to-end numerical/delivery replay differs")
    if _sources(root)!=index["source_sha256"]:raise ValueError("Source epoch changed during delivery replay")
    return dict(verified=True,replayed=replay,package_id=index["package_id"],manifest_id=manifest["manifest_id"],
        output=str(output),compressed_package_bytes=sum(p.stat().st_size for p in paths if p.is_file()),
        native_CAD_jobs_new=index["native_CAD_jobs_new"],geometry_evidence_reused=reused is not None,**index["summary"])


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest="command",required=True)
    run_parser=commands.add_parser("run")
    run_parser.add_argument("--search-state",type=Path,required=True)
    run_parser.add_argument("--output",type=Path,required=True)
    run_parser.add_argument("--body-candidate-id")
    run_parser.add_argument("--native-cad",action="store_true")
    run_parser.add_argument("--reuse-geometry",type=Path)
    run_parser.add_argument("--generations",type=int)
    run_parser.add_argument("--evaluations",type=int)
    run_parser.add_argument("--section-torsion-jobs",type=int,default=1)
    run_parser.add_argument("--canonical-backend",choices=("python","rust"),default="python")
    run_parser.add_argument("--canonical-extension",type=Path)
    verify_parser=commands.add_parser("verify")
    verify_parser.add_argument("output",type=Path)
    verify_parser.add_argument("--replay",action="store_true")
    args=parser.parse_args(argv)
    value=(run(search_state=args.search_state,output=args.output,body_candidate_id=args.body_candidate_id,
        native_cad_jobs=int(args.native_cad),generations=args.generations,maximum_new_evaluations=args.evaluations,
        section_torsion_jobs=args.section_torsion_jobs,reuse_geometry=args.reuse_geometry,
        canonical_backend=args.canonical_backend,canonical_extension=args.canonical_extension) if args.command=="run" else verify(args.output,replay=args.replay))
    print(json.dumps(value,indent=2));return 0


if __name__=="__main__":raise SystemExit(main())

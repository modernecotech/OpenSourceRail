"""Reanalyse the same frame with bounded, replayed actual-wall torsion data.

The Bredt frame remains a separate reference evaluation. Section refinement
changes neither physical stock nor material/joint/shear qualification.
"""
from copy import deepcopy
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from . import frame_analysis, frame_refinement, section_torsion, section_torsion_job

PRODUCER="engineering/design_search/frame_section_refinement.py"
MODULES=(frame_analysis,frame_refinement,section_torsion,section_torsion_job)
LOADED={module.PRODUCER:digest(module.__file__) for module in MODULES}
LOADED[PRODUCER]=digest(__file__)


def _sources(candidate,root):
    values=frame_refinement._sources(candidate,root)
    for module in MODULES:
        if digest(module.__file__)!=LOADED[module.PRODUCER] or digest(Path(root)/module.PRODUCER)!=LOADED[module.PRODUCER]:
            raise ValueError("Loaded refined-frame dependency changed: "+module.PRODUCER)
    if digest(__file__)!=LOADED[PRODUCER] or digest(Path(root)/PRODUCER)!=LOADED[PRODUCER]:
        raise ValueError("Loaded refined-frame producer changed")
    return dict(sorted({**values,**LOADED}.items()))


def _basis(geometry,request,result,folder):
    gate=result["gate"]
    row=section_torsion_job._parse(section_torsion_job._read(folder/"level-8.json"))
    if (row["evaluation_id"]!=gate["selected_evaluation_id"]
            or row["geometry"]!=dict(kind="rhs",**geometry)
            or row["J_energy_m4"]!=gate["selected_J_m4"]):
        raise ValueError("Refined frame differs from the selected same-section numerical field")
    basis=dict(schema="osr-section-torsion-basis/1",geometry=deepcopy(geometry),geometry_id=row["geometry_id"],
        request_id=request["request_id"],selected_evaluation_id=row["evaluation_id"],J_m4=gate["selected_J_m4"],
        method="actual-wall-saint-venant-P1/1",source_epoch_id=identity(request["sources"]),
        runtime_id=identity(request["child_runtime"]),convergence_rule_id=identity(request["policy"]))
    basis["basis_id"]=identity(basis)
    return basis


def assess(candidate,cache,*,root=ROOT,maximum_new_jobs=1):
    """Opt-in higher fidelity; cached section fields are replayed, never trusted."""
    if type(maximum_new_jobs) is not int or not 0<=maximum_new_jobs<=3:
        raise ValueError("Explicit zero-to-three new section-worker budget required")
    source=_sources(candidate,root)
    base=frame_refinement.assess(candidate,root=root)
    result=dict(schema="osr-section-refined-frame-assessment/1",candidate_id=candidate["candidate_id"],
        definition_id=candidate["definition_id"],requirement_revision=candidate["requirement_revision"],
        reference_assessment_id=base["assessment_id"],reference_model_id=base["model_id"],
        execution="held",state="held-section-evidence",model=None,model_id=None,frame_result=None,
        hypothesis_id=None,section_studies=[],new_section_jobs=0,reused_section_jobs=0,
        source_sha256=source,runtime=base["runtime"],domain_holds=[],numerical_validity="unknown",engineering_screen="unknown",
        native_admission=False,native_validation_state="Cross-section numerical study only; no full-frame native or physical validation",
        whole_body_rejected=False,physical_candidate_changed=False,integrated_selection=None,complete_installed_mass_kg=None,
        limitations=[*base["limitations"],"Sharp-corner uniform-wall section; real corner radii, welds and tolerances remain unverified",
            "Declared successive-mesh rule has no certified error lower bound"],**frame_refinement.FLAGS)
    if base["model"] is None:
        result["domain_holds"]=["reference-frame-material-or-model-domain-unavailable"]
    else:
        model=deepcopy(base["model"])
        geometries={}
        for member in model["members"]:
            geometry={k:member["section"][k] for k in ("width_m","height_m","wall_m")}
            geometries[identity(geometry)]=geometry
        bases={}
        for key,geometry in sorted(geometries.items()):
            request=section_torsion_job.request(geometry,root=root)
            folder=Path(cache)/request["request_id"]
            if folder.exists():
                study=section_torsion_job.verify(folder,root=root)
                result["reused_section_jobs"]+=1
            elif result["new_section_jobs"]<maximum_new_jobs:
                study=section_torsion_job.run(geometry,folder,root=root)
                result["new_section_jobs"]+=1
            else:
                result["domain_holds"].append("section-worker-budget-exhausted")
                result["section_studies"].append(dict(geometry=geometry,request_id=request["request_id"],state="deferred-budget"))
                continue
            result["section_studies"].append(dict(geometry=geometry,output=str(folder),request_id=request["request_id"],result=study))
            if study.get("verified") is not True or study["gate"]["state"]!="converged-under-declared-rule":
                result["domain_holds"].append("section-torsion-numerical-evidence-unresolved")
                continue
            bases[key]=_basis(geometry,request,study,folder)
        if len(bases)==len(geometries):
            for member in model["members"]:
                geometry={k:member["section"][k] for k in ("width_m","height_m","wall_m")}
                member["section"]["torsion_basis"]=deepcopy(bases[identity(geometry)])
            hypothesis=dict(reference_hypothesis_id=base["hypothesis_id"],torsion_method="actual-wall-saint-venant-P1/1",
                section_basis_ids=sorted(value["basis_id"] for value in bases.values()),
                unchanged="Physical candidate, E/nu, bending inertias, joints, roll, supports and loads")
            model["hypothesis_id"]=identity(hypothesis)
            result.update(hypothesis=hypothesis,hypothesis_id=model["hypothesis_id"],model=model,model_id=identity(model))
            frame=frame_analysis.evaluate(model)
            diagnostics=frame_refinement.model_diagnostics(model,frame,base["hypothesis"])
            result.update(diagnostics,frame_result=frame)
            if base.get("normal_force_mass_relative_residual",1.)>1e-8:
                result["domain_holds"].append("normal-force-and-accounted-mass-hypothesis-mismatch")
            result["state"]=("held-unsolved-property-refined-frame" if result["execution"]!="completed" else
                "computed-property-refined-frame-domain-held" if result["domain_holds"] else "computed-conditional-property-refined-frame")
            result["reference_metrics"]={k:base["frame_result"].get(k) for k in
                ("maximum_nodal_displacement_m","maximum_nodal_rotation_rad","strain_energy_J")} if base["frame_result"] else None
    result["comparison_context_id"]=identity(dict(model_id=result["model_id"],hypothesis_id=result["hypothesis_id"],
        source_sha256=source,runtime=result["runtime"],scope="Same physical candidate and own load; different explicit section model"))
    result["next_tasks"]=[dict(kind="section-frame-evidence",state="open",detail=value)
                          for value in result["domain_holds"]+result["limitations"]]
    if _sources(candidate,root)!=source:raise ValueError("Refined frame source epoch changed")
    result["assessment_id"]=identity(result)
    return result

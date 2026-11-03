"""Candidate-bound exploratory 3D frame assessment; no joint or body approval."""
from copy import deepcopy
from math import isfinite
from pathlib import Path

import numpy as np

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from . import frame_analysis, native_refinement

PRODUCER="engineering/design_search/frame_refinement.py"
MODULES=((frame_analysis,frame_analysis.PRODUCER),(native_refinement,native_refinement.PRODUCER))
LOADED={name:digest(module.__file__) for module,name in MODULES}
LOADED[PRODUCER]=digest(__file__)
FLAGS=dict(frame_analysis.FLAGS,physical_journey_completed=False,selected_reference_changed=False)
OPEN=["Real connection stiffness, eccentricity, cuts and attachments remain unverified",
      "Shear deformation, warping and local/global buckling require separate methods",
      "Shell participation, fatigue, modes, crash, fire and installed equipment remain open",
      "Source-bound numerical execution is not independent physical qualification"]


def hypothesis():
    return dict(schema="osr-coarse-frame-hypothesis/1",joint_hypothesis=frame_analysis.JOINT,
        scope="One 17 m car underfloor RHS centroid frame; other body/equipment stock contributes mass without shell stiffness in this method",
        isotropic_aluminium_nu=.33,
        material_basis="Existing aluminium reference E/density plus declared provisional isotropic Poisson ratio; no qualified lot/HAZ law",
        orientation="Project global Y normal to each member; use global Z when projected norm <=1e-8; local y is section width",
        orientation_fallback_threshold=1e-8,
        short_member_slenderness_advisory=10.,thin_wall_ratio_advisory=.1,
        member_relative_translation_limit=.01,maximum_rotation_rad=.01,
        numerical_relative_residual_limit=1e-7,
        limits_scope="Numerical small-displacement research model domain, not vehicle acceptance limits")


def _check_hypothesis(value):
    expected=hypothesis()
    if not isinstance(value,dict) or set(value)!=set(expected):raise ValueError("Complete explicit frame hypothesis required")
    for key in set(expected)-{"isotropic_aluminium_nu"}:
        if value[key]!=expected[key]:raise ValueError("Unsupported frame hypothesis: "+key)
    nu=value["isotropic_aluminium_nu"]
    if type(nu) not in (int,float) or not isfinite(nu) or not -1<nu<.5:
        raise ValueError("Stable explicit provisional isotropic Poisson ratio required")


def _sources(candidate,root):
    root=native_refinement._root(root)
    source=native_refinement._candidate(candidate,root)
    for module,name in MODULES:
        if digest(module.__file__)!=LOADED[name] or digest(Path(root)/name)!=LOADED[name]:
            raise ValueError("Loaded frame evaluator source changed: "+name)
    if digest(__file__)!=LOADED[PRODUCER] or digest(Path(root)/PRODUCER)!=LOADED[PRODUCER]:
        raise ValueError("Loaded frame assessment source changed")
    return dict(sorted({**source,**LOADED}.items()))


def _model(candidate,assumptions):
    graph=candidate["structure"]
    materials={}
    for member in graph["members"]:
        mid=member["section"]["material_id"]
        if mid!="aluminium_reference":
            raise ValueError("Frame shear/orthotropic law unavailable for "+mid+"; axial E alone is insufficient")
        material=candidate["materials"][mid]
        materials[mid]=dict(law=frame_analysis.LAW,E_Pa=material["E_Pa"],
            density_kg_m3=material["density_kg_m3"],nu=assumptions["isotropic_aluminium_nu"],
            source_basis=material["source_basis"]+"; "+assumptions["material_basis"])
    xyz={n["id"]:np.asarray(n["at_m"],dtype=float) for n in graph["nodes"]}
    members=[]
    for member in graph["members"]:
        axis=xyz[member["end_node"]]-xyz[member["start_node"]]
        length=float(np.linalg.norm(axis))
        if not isfinite(length) or length<=0:raise ValueError("Distinct finite frame member endpoints required")
        axis/=length
        reference=np.array([0.,1.,0.]);local_y=reference-float(reference@axis)*axis
        if float(np.linalg.norm(local_y))<=assumptions["orientation_fallback_threshold"]:
            reference=np.array([0.,0.,1.]);local_y=reference-float(reference@axis)*axis
        local_y/=float(np.linalg.norm(local_y))
        members.append(dict(id=member["id"],start_node=member["start_node"],end_node=member["end_node"],
            section={k:member["section"][k] for k in ("width_m","height_m","wall_m")},
            material_id=member["section"]["material_id"],local_y=local_y.tolist()))
    loads=graph.get("loads")
    if not isinstance(loads,list) or not loads:raise ValueError("Explicit candidate frame load case required")
    return dict(schema=frame_analysis.SCHEMA,candidate_id=candidate["candidate_id"],definition_id=candidate["definition_id"],
        requirement_revision=candidate["requirement_revision"],hypothesis_id=identity(assumptions),
        joint_hypothesis=assumptions["joint_hypothesis"],nodes=deepcopy(graph["nodes"]),members=members,materials=materials,
        supports=deepcopy(graph["supports"]),
        loads=[dict(node_id=row["node_id"],force_N=deepcopy(row["force_N"]),moment_Nm=[0.,0.,0.]) for row in loads],
        load_basis=deepcopy(graph["load_basis"]),
        load_policy="Exact candidate uniform tributary sprung-force vector at existing nodes; added applied moments explicitly zero; no installed load-location evidence",
        support_policy="Exact declared translational constraints; all rotations free; no artificial rotational support",
        physical_joint_policy="Candidate pin/clevis ports retained; rigid moment continuity is a separate unverified evaluation hypothesis")


def assess(candidate,*,root=ROOT,assumptions=None):
    source=_sources(candidate,root)
    assumptions=deepcopy(hypothesis() if assumptions is None else assumptions)
    _check_hypothesis(assumptions)
    result=dict(schema="osr-coarse-frame-assessment/1",candidate_id=candidate["candidate_id"],definition_id=candidate["definition_id"],
        requirement_revision=candidate["requirement_revision"],hypothesis=assumptions,hypothesis_id=identity(assumptions),
        input_axial_graph_id=identity(candidate["structure"]),source_sha256=source,runtime=native_refinement._runtime(),
        model=None,model_id=None,frame_result=None,domain_holds=[],numerical_validity="unknown",engineering_screen="unknown",
        execution="held",native_admission=False,native_admission_scope="Bounded numerical method request only; physical joints/materials/body remain unqualified",
        native_validation_state="unverified",whole_body_rejected=False,integrated_selection=None,complete_installed_mass_kg=None,
        limitations=OPEN,**FLAGS)
    try:
        model=_model(candidate,assumptions);result.update(model=model,model_id=identity(model))
        mass=model["load_basis"].get("sprung_mass_hypothesis_kg")
        if type(mass) not in (int,float) or not isfinite(mass) or mass<=0:
            raise ValueError("Explicit positive accounted sprung-mass hypothesis required")
        expected=np.array([0.,0.,-mass*9.80665])
        actual=sum((np.asarray(row["force_N"],dtype=float) for row in model["loads"]),np.zeros(3))
        result["normal_force_mass_relative_residual"]=float(np.linalg.norm(actual-expected))/float(np.linalg.norm(expected))
        if result["normal_force_mass_relative_residual"]>1e-8:
            result["domain_holds"].append("normal-force-and-accounted-mass-hypothesis-mismatch")
        frame=frame_analysis.evaluate(model);result["frame_result"]=frame
        if frame["model_id"]!=result["model_id"] or any(frame[k] is not False for k in frame_analysis.FLAGS):
            raise RuntimeError("Frame evaluator mixed model identity or acceptance disposition")
        if frame["state"]!="completed-linear-frame-research-only":
            result["domain_holds"].append("singular-or-unsupported-frame-model")
        else:
            result["execution"]="completed"
            force_scale=max(sum(float(np.linalg.norm(row["force_N"])) for row in model["loads"]),1.)
            coordinates=np.asarray([n["at_m"] for n in model["nodes"]])
            length=max(float(np.linalg.norm(np.ptp(coordinates,axis=0))),1.)
            moment_scale=max(sum(float(np.linalg.norm(row["moment_Nm"])) for row in model["loads"]),force_scale*length,1.)
            force_error=max(abs(v) for v in frame["force_equilibrium_residual_N"])/force_scale
            moment_error=max(abs(v) for v in frame["moment_equilibrium_residual_Nm"])/moment_scale
            energy_error=abs(frame["strain_energy_J"]-frame["external_work_J"])/max(abs(frame["external_work_J"]),1e-30)
            free_force_error=frame["numerical"]["free_force_residual_N_max"]/force_scale
            free_moment_error=frame["numerical"]["free_moment_residual_Nm_max"]/moment_scale
            result["residuals"]=dict(force_relative=force_error,moment_relative=moment_error,energy_relative=energy_error,
                free_force_relative=free_force_error,free_moment_relative=free_moment_error)
            if max(result["residuals"].values())<assumptions["numerical_relative_residual_limit"]:
                result["numerical_validity"]="equilibrium-and-energy-confirmed-only"
            else:result["domain_holds"].append("numerical-equilibrium-or-energy-unresolved")
            if (frame["maximum_member_relative_translation_over_length"]>=assumptions["member_relative_translation_limit"]
                    or frame["maximum_nodal_rotation_rad"]>=assumptions["maximum_rotation_rad"]):
                result["domain_holds"].append("outside-small-displacement-frame-domain")
            if frame["domain"]["short_member_ids_advisory_lt_10"]:
                result["domain_holds"].append("shear-deformation-and-short-member-applicability-unresolved")
            if any(p["wall_to_min_outer_dimension"]>=.1 for p in frame["member_properties"].values()):
                result["domain_holds"].append("thin-wall-torsion-applicability-unresolved")
        result["state"]=("held-unsolved-frame-model" if result["execution"]!="completed" else
            "completed-exploratory-frame-domain-held" if result["domain_holds"] else "completed-conditional-rigid-frame-model")
        result["native_admission"]=not result["domain_holds"]
    except (ValueError,KeyError,TypeError,np.linalg.LinAlgError) as exc:
        result.update(state="held-frame-model-domain",reason=str(exc),execution="held",native_admission=False)
        result["domain_holds"].append("material-geometry-load-or-model-definition-unavailable")
    result["next_tasks"]=[dict(kind="frame-model-domain-and-joint-evidence",state="open",detail=hold) for hold in result["domain_holds"]]
    result["next_tasks"].extend(dict(kind="physical-qualification",state="open",detail=detail) for detail in OPEN)
    result["comparison_context_id"]=identity(dict(hypothesis_id=result["hypothesis_id"],model_id=result["model_id"],
        source_sha256=source,runtime=result["runtime"],scope="Same explicit six-DOF frame, roll, load and support hypothesis only; no pin-graph or cross-candidate ranking"))
    if _sources(candidate,root)!=source:raise ValueError("Frame assessment source changed during execution")
    result["assessment_id"]=identity(result)
    return result

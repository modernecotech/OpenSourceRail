"""Conditional stepped-beam mechanics for the source-bound civil portfolio.

This evaluates actual nominal geometry under a common accounted train load.
An analytical moving-load/virtual-work envelope bounds the declared elastic
model, without claiming to bound a cracked, slipping or incompletely installed
physical structure. Cost reserves supply weight only; they supply no resistance.
"""
import argparse
from copy import deepcopy
from functools import lru_cache
import gzip
import json
from math import isfinite
from pathlib import Path
import shutil
import tempfile
import time
import tomllib

from engineering.development_baseline import selection
from engineering.station_rail import ROOT, civil
from engineering.station_rail.common import digest, encoded, identity
from . import civil_beam as beam
from . import civil_section_model as sections
from . import civil_shape_portfolio as parent, quality_diversity, portable_gzip

PRODUCER = "engineering/design_search/civil_shape_mechanics.py"
CAMPAIGN = "campaigns/civil-shape-mechanics.toml"
OUTPUT = "docs/design-engine/civil-shape-mechanics"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    configuration_adopted=False, selected_reference_changed=False,
    manufacturing_release=False, operating_release=False)
OBJECTIVES = ("crowd_high_mass_model_deflection_upper_m", "lift_adjusted_scoped_installed_base_iqd", "nominal_stock_mass_kg")


def specification(root=ROOT):
    spec = tomllib.loads((Path(root)/CAMPAIGN).read_text())
    expected = dict(schema="osr-civil-shape-mechanics/1", purpose="next-experiment",
        reference_changes_allowed=False, span_m=20., maximum_cases=189,
        load_cases=["empty","normal","crowd_control"], dead_mass_cases=["low","base","high"],
        dynamic_axle_factor_hypothesis=1.3, representative_pose="maximum-midspan-live-moment")
    if any(spec.get(k)!=v for k,v in expected.items()):
        raise ValueError("Explicit bounded, non-promoting civil mechanical comparison required")
    if (spec["observation_fractions"]!=[0.,.25,.5,.75,1.]
            or spec["resources"]["native_jobs"]!=0
            or not 0<spec["resources"]["maximum_runtime_s"]<=150
            or spec["lifting"]["actual_radius_capacity_confirmed"] is not False):
        raise ValueError("Declared observation, runtime and unqualified lifting scope required")
    values=[*spec["elastic_moduli_Pa"].values(),spec["lifting"]["nominal_hook_capacity_kg_hypothesis"],
        spec["lifting"]["rigging_mass_fraction_hypothesis"],*spec["lifting"]["cost_scaling_exponents"]]
    if any(type(v) not in (int,float) or not isfinite(v) or v<=0 for v in values):
        raise ValueError("Finite positive mechanical and lifting hypotheses required")
    if len(spec["lifting"]["cost_scaling_exponents"])!=3:
        raise ValueError("Explicit low/base/high lifting-cost exponents required")
    return spec


def maximum_axles_inside(offsets,span):
    """Maximum count in any closed span window; support loads overcount safely."""
    if (not offsets or type(span) not in (int,float) or not isfinite(span) or span<=0
            or any(type(x) not in (int,float) or not isfinite(x) for x in offsets)):
        raise ValueError("Finite axle offsets and positive span required")
    ordered=sorted(offsets)
    return max(sum(start<=x<=start+span for x in ordered) for start in ordered)


def load_context(root=ROOT):
    selected=selection.load(root); vehicle=selected["vehicle"]; spec=specification(root)
    cases=[]
    mass_keys=dict(empty="accounted_tare_kg_per_car",normal="accounted_cap_loaded_kg_per_car",
        crowd_control="accounted_160_control_kg_per_car")
    for name in spec["load_cases"]:
        offsets,force=civil.axle_train(vehicle,name)
        expected=vehicle["mass"][mass_keys[name]]*civil.G/4*spec["dynamic_axle_factor_hypothesis"]
        if force!=expected:raise ValueError("Source axle-load factor differs from the explicit comparison")
        count=maximum_axles_inside(offsets,spec["span_m"])
        cases.append(dict(name=name,offsets_m=offsets,force_N_per_full_axle=force,
            accounted_mass_kg_per_car=vehicle["mass"][mass_keys[name]],
            maximum_simultaneous_axles=count,maximum_simultaneous_axle_force_N=count*force,
            equivalent_live_moment_upper_udl_N_m=2*count*force/spec["span_m"]))
    result=dict(schema="osr-civil-common-train-load-context/1",vehicle_candidate_id=vehicle["candidate_id"],
        vehicle_evaluation_id=vehicle["evaluation_id"],selection_id=selected["selection_id"],
        cars=vehicle["physical_definition"]["vehicle"]["cars"],cases=cases,
        installed_vehicle_mass_complete=False,dynamic_factor_hypothesis=spec["dynamic_axle_factor_hypothesis"],
        axle_force_scope="Full axle force across both rails, including the declared 1.3 factor once; same complete formation offsets in every civil comparison.",
        source_sha256={**vehicle["source_sha256"],**selected["source_sha256"],
            "engineering/development_baseline/selection.py":digest(Path(root)/"engineering/development_baseline/selection.py")},**FLAGS)
    result["context_id"]=identity(result)
    return result


def sources(root=ROOT,context=None):
    root=Path(root); context=load_context(root) if context is None else context
    paths=[PRODUCER,CAMPAIGN,"engineering/design_search/civil_beam.py",
        "engineering/design_search/civil_section_model.py","engineering/station_rail/civil.py",
        "engineering/station_rail/common.py",parent.OUTPUT+"/manifest.json",parent.OUTPUT+"/result.json",
        parent.OUTPUT+"/candidates.json.gz"]
    return {**parent.sources(root),**context["source_sha256"],**{p:digest(root/p) for p in paths}}


@lru_cache(maxsize=16)
def _representative_pose(span,offsets,force):
    rows=civil.moving_envelope(span,list(offsets),force,sections=3)
    translation=rows[1]["critical_train_translation_m"]
    points=[dict(x_m=x+translation,force_N=force) for x in offsets if 0<=x+translation<=span]
    return dict(translation_m=translation,points=points,
        maximum_midspan_live_moment_Nm=rows[1]["max_live_moment_Nm"],
        scope="Exact live moment maximizer at midspan only; not a deflection-, shear- or stress-critical pose claim")


def lifting(candidate,quantity_row,spec):
    _parent_binding(candidate,quantity_row)
    assumptions=spec["lifting"]; cases=[]
    for i,case in enumerate(quantity_row["cost_estimate"]["cases"]):
        # Rail and fastening accounts are installed after beam erection. They
        # remain in the dead-load model but are not added to the concrete lift.
        allowance=case["preliminary_reinforcement_kg"]+case["unsized_prestress_reserve_kg"]
        piece=quantity_row["quantities"]["lifting_mass_kg"]+allowance
        hook=piece*(1+assumptions["rigging_mass_fraction_hypothesis"])
        ratio=hook/assumptions["nominal_hook_capacity_kg_hypothesis"]
        old=quantity_row["cost_estimate"]["line_items_iqd"]["erection"][case["case"]]
        adjusted=old*max(1.,ratio)**assumptions["cost_scaling_exponents"][i]
        cases.append(dict(name=case["case"],accounted_lift_piece_kg=piece,required_hook_kg_hypothesis=hook,
            assumed_capacity_ratio=ratio,exceeds_nominal_capacity_hypothesis=ratio>1.,
            original_erection_iqd=old,adjusted_erection_iqd=round(adjusted,2),
            erection_cost_delta_iqd=round(adjusted-old,2),
            lift_adjusted_scoped_installed_iqd=round(case["scoped_installed_iqd"]+adjusted-old,2)))
    return dict(candidate_id=candidate["candidate_id"],cases=cases,
        basis="One declared span piece plus preliminary reinforcement/prestress and rigging allowance; no lift points, transport splitting or radius-capacity confirmation. Larger crane cost follows an explicit Class C power-law hypothesis.",
        installed_lift_mass_complete=False,actual_crane_suitable=False,**FLAGS)


def _stress_upper(model,response):
    demands={}
    for cell,extreme in zip(model["cells"],response["per_cell_extrema"]):
        moment=extreme["maximum_sagging_moment_Nm"]
        for fiber in cell["section_fibers"]:
            material=fiber["material"]; d=demands.setdefault(material,dict(tension_Pa=0.,compression_Pa=0.))
            factor=fiber["modulus_Pa"]*moment/cell["EI_Nm2"]
            d["tension_Pa"]=max(d["tension_Pa"],factor*max(0.,fiber["neutral_axis_z_m"]-fiber["z_min_m"]))
            d["compression_Pa"]=max(d["compression_Pa"],factor*max(0.,fiber["z_max_m"]-fiber["neutral_axis_z_m"]))
    return dict(material_demands=demands,concrete_longitudinal_stress_calculated="research_concrete" in demands,
        resistance_credited=False,strength_allowables_available=False,
        interpretation="Model upper demands without prestress, reinforcement or rail resistance. Omitted material in a stiffness hypothesis has unknown longitudinal stress, not zero physical stress.")


def _parent_binding(candidate,row):
    parent.geometry.validate(candidate)
    if (row.get("candidate_id")!=candidate["candidate_id"]
            or row.get("evaluation_id")!=identity({k:v for k,v in row.items() if k!="evaluation_id"})
            or row.get("quantities")!=parent.geometry.quantities(candidate)):
        raise ValueError("Civil geometry and source-bound parent quantity evaluation differ")


@lru_cache(maxsize=4)
def _canonical_context(root_name,fingerprints):
    value=load_context(Path(root_name))
    if tuple(sorted(value["source_sha256"].items()))!=fingerprints:
        raise ValueError("Canonical train load context source epoch differs")
    return value


def _context_binding(context,root):
    if context.get("context_id")!=identity({k:v for k,v in context.items() if k!="context_id"}):
        raise ValueError("Train load case differs from its sealed comparison context")
    sources=context.get("source_sha256")
    if not isinstance(sources,dict) or not sources:
        raise ValueError("Explicit train load context source bindings required")
    actual={}
    for name,expected in sources.items():
        path=Path(name)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ValueError("Repository-relative train load sources required")
        actual[name]=digest(Path(root)/path)
        if actual[name]!=expected:raise ValueError("Train load context source epoch differs")
    canonical=_canonical_context(str(Path(root).resolve()),tuple(sorted(actual.items())))
    if context!=canonical:
        raise ValueError("Train load context does not reproduce from the selected physical vehicle")


def evaluate_case(candidate,quantity_row,model,load,mass_case,spec,context,*,root=ROOT):
    _parent_binding(candidate,quantity_row)
    if (model.get("candidate_id")!=candidate["candidate_id"]
            or model.get("evaluation_id")!=identity({k:v for k,v in model.items() if k!="evaluation_id"})
            or model.get("source_quantity_evaluation_id")!=quantity_row["quantities"]["evaluation_id"]
            or model not in sections.models(candidate,spec["elastic_moduli_Pa"])):
        raise ValueError("Civil section model differs from its physical geometry and elastic hypothesis")
    if mass_case not in quantity_row["cost_estimate"]["cases"]:
        raise ValueError("Dead mass case differs from the source-bound cost account")
    if (context.get("context_id")!=identity({k:v for k,v in context.items() if k!="context_id"})
            or load not in context.get("cases",[])):
        raise ValueError("Train load case differs from its sealed comparison context")
    _context_binding(context,root)
    for account in context["cases"]:
        expected_force=account["accounted_mass_kg_per_car"]*civil.G/4*spec["dynamic_axle_factor_hypothesis"]
        expected_count=maximum_axles_inside(account["offsets_m"],spec["span_m"])
        if (account["force_N_per_full_axle"]!=expected_force
                or account["maximum_simultaneous_axles"]!=expected_count
                or account["maximum_simultaneous_axle_force_N"]!=expected_count*expected_force
                or account["equivalent_live_moment_upper_udl_N_m"]!=2*expected_count*expected_force/spec["span_m"]):
            raise ValueError("Train load context contradicts its mass, axle geometry or factor")
    nominal=quantity_row["quantities"]["total_nominal_stock_mass_kg"]
    extra=mass_case["accounted_delivery_mass_kg"]-nominal
    if extra<0:raise ValueError("Counted span mass cannot be below generated nominal stock")
    cells=[dict(x_start_m=c["x_start_m"],x_end_m=c["x_end_m"],EI_Nm2=c["EI_Nm2"],
        distributed_load_N_m=(c["mass_per_length_kg_m"]+extra/spec["span_m"])*civil.G)
        for c in model["cells"]]
    observations=[spec["span_m"]*f for f in spec["observation_fractions"]]
    pose=_representative_pose(spec["span_m"],tuple(load["offsets_m"]),load["force_N_per_full_axle"])
    actual=beam.analyse(cells,pose["points"],observations)
    upper_cells=[dict(c,distributed_load_N_m=c["distributed_load_N_m"]+load["equivalent_live_moment_upper_udl_N_m"]) for c in cells]
    upper=beam.analyse(upper_cells,[],observations)
    displacement=beam.deflection_upper_bound(upper_cells,[])
    sampled=max(actual["deflection_at_observation_m"])
    residual=max(abs(actual["force_residual_N"]),abs(upper["force_residual_N"]))
    moment_residual=max(abs(actual["moment_residual_Nm"]),abs(actual["right_support_internal_moment_residual_Nm"]),
        abs(upper["moment_residual_Nm"]),abs(upper["right_support_internal_moment_residual_Nm"]))
    if sampled>displacement+1e-10 or residual>1e-6 or moment_residual>1e-5:
        raise ValueError("Civil elastic response violates equilibrium or analytical envelope")
    value=dict(candidate_id=candidate["candidate_id"],quantity_evaluation_id=quantity_row["evaluation_id"],
        section_model_id=model["evaluation_id"],elastic_hypothesis=model["name"],load_context_id=context["context_id"],
        load_case=load["name"],dead_mass_case=mass_case["case"],accounted_span_mass_kg=mass_case["accounted_delivery_mass_kg"],
        cells=cells,representative_train_pose=pose,representative_response=actual,
        all_pose_moment_upper_response=upper,all_pose_all_observation_model_deflection_upper_m=displacement,
        representative_sampled_deflection_m=sampled,stress_upper=_stress_upper(model,upper),
        force_equilibrium_residual_N=residual,moment_equilibrium_residual_Nm=moment_residual,
        execution="completed",numerical_validity="equilibrium-and-exact-order-quadrature-checked",
        engineering_screen="unresolved-material-load-transfer-and-resistance",
        dead_load_distribution="Exact nominal geometry per cell; preliminary reinforcement/prestress/rails/fasteners spread uniformly. Other installed mass remains unknown.",
        installed_dead_load_complete=False,physical_deflection_upper_bound_available=False,
        physical_strength_or_deflection_acceptance_limit=None,**FLAGS)
    value["producer_sha256"]={p:digest(Path(root)/p) for p in (PRODUCER,CAMPAIGN,"engineering/design_search/civil_beam.py")}
    value["standalone_reuse_allowed"]=False
    value["evaluation_id"]=identity(value)
    return value


def _calculate(root=ROOT):
    root=Path(root); parent.verify(root); spec=specification(root); context=load_context(root)
    epoch=sources(root,context); folder=root/parent.OUTPUT
    portfolio=json.loads((folder/"result.json").read_bytes())
    definitions=json.loads(gzip.decompress((folder/"candidates.json.gz").read_bytes()))
    quantities={r["candidate_id"]:r for r in portfolio["evaluations"]}
    cases=[]; summaries=[]; models=[]; start=time.monotonic()
    for candidate in definitions:
        if time.monotonic()-start>spec["resources"]["maximum_runtime_s"]:
            raise ValueError("Civil analytical runtime budget exhausted; previous publication is preserved")
        row=quantities[candidate["candidate_id"]]; alternatives=sections.models(candidate,spec["elastic_moduli_Pa"])
        models.extend(alternatives); local=[]
        for model in alternatives:
            for load in context["cases"]:
                for mass_case in row["cost_estimate"]["cases"]:
                    result=evaluate_case(candidate,row,model,load,mass_case,spec,context,root=root)
                    cases.append(result); local.append(result)
        primary="steel-only-longitudinal" if candidate["family"]=="hybrid_steel_concrete" else "full-section-uncracked"
        control=next(c for c in local if c["elastic_hypothesis"]==primary and c["load_case"]=="crowd_control" and c["dead_mass_case"]=="high")
        lift=lifting(candidate,row,spec)
        summary=dict(candidate_id=candidate["candidate_id"],descriptor=dict(family=candidate["family"]),profile=candidate["profile"],
            primary_elastic_hypothesis=primary,load_context_id=context["context_id"],case_evaluation_ids=[c["evaluation_id"] for c in local],
            lifting=lift,metrics=dict(crowd_high_mass_model_deflection_upper_m=control["all_pose_all_observation_model_deflection_upper_m"],
                lift_adjusted_scoped_installed_base_iqd=lift["cases"][1]["lift_adjusted_scoped_installed_iqd"],
                nominal_stock_mass_kg=row["metrics"]["nominal_stock_mass_kg"]),
            stage_1_complete=False,first_stage_1_calculations_completed=True,stage_2_admission=False,
            next_tasks=["Size and locate resistance/prestress with complete installed mass",
                "Evaluate shear, torsion, unequal rails, stability and local step/load introduction",
                "Resolve deck/girder and lifting connections, curing and mould/installation feasibility"],**FLAGS)
        summary["evaluation_id"]=identity(summary); summaries.append(summary)
    if len(cases)!=spec["maximum_cases"]:raise ValueError("Mechanical hypothesis/load/mass case coverage differs")
    archive=quality_diversity.archive(summaries,OBJECTIVES,("family",))
    value=dict(schema="osr-civil-shape-mechanics/1",source_sha256=epoch,specification=spec,
        parent_portfolio_id=portfolio["portfolio_id"],load_context=context,candidate_count=len(summaries),
        calculated_case_count=len(cases),section_models=models,evaluations=summaries,cases=cases,archive=archive,
        interpretation="Conditional model bounds and experimental ordering, not physical upper bounds or validated structural capacity. Steel-only and perfect-bond alternatives are hypotheses, not a validated physical bracket.",
        integrated_selection=None,stage_1_complete=False,native_jobs_dispatched=0,**FLAGS)
    value["execution_resource_scope"]=dict(process="current Python process",runtime_guard="checked between candidates",
        memory_limit_enforced=False,operating_system_isolation=False)
    if epoch!=sources(root,context):raise ValueError("Civil mechanics source epoch changed during evaluation")
    value["study_id"]=identity(value)
    return value


def _readme(value):
    lines=["# Civil shape mechanics", "",
        f"{value['candidate_count']} nominal span candidates have {value['calculated_case_count']} conditional stepped-beam evaluations under the same selected six-car train: empty, normal and crowd-control loads, each with low/base/high accounted span mass. The hybrid also has separate steel-only and perfect-bond hypotheses. No civil design is selected or qualified.", "",
        "| Family / profile | Primary elastic hypothesis | Crowd/high-mass model deflection bound (mm) | Base assumed hook capacity exceeded | Lift-adjusted scoped installed cost (IQD million, base) |",
        "|---|---|---:|---|---:|"]
    for row in value["evaluations"]:
        m=row["metrics"]; lift=row["lifting"]["cases"][1]
        lines.append(f"| {row['descriptor']['family']} / {row['profile']} | {row['primary_elastic_hypothesis']} | {m['crowd_high_mass_model_deflection_upper_m']*1000:.2f} | {lift['exceeds_nominal_capacity_hypothesis']} | {m['lift_adjusted_scoped_installed_base_iqd']/1e6:.2f} |")
    lines += ["", "Every value above depends on unvalidated material/load-transfer hypotheses and accounted masses. There is no universal displacement pass limit. Concrete tensile resistance, reinforcement, prestress force, rail stiffness and steel–concrete bond receive no undeclared credit. Steel-only analysis retains the full concrete dead weight. Other installed mass, shear deformation, torsion, cracking, creep, local steps, buckling, fatigue, unequal rail loading, supports and construction stages remain unresolved.", "",
        "## Mechanical calculation", "",
        "Each actual polygon-prism cell has its own modulus-weighted neutral axis and flexural rigidity. Concrete at 35 GPa and steel at 200 GPa are explicit research hypotheses, not tested article properties or design allowables. Equilibrium gives reactions and piecewise moments/shears. Unit-load virtual work integrates actual-pose deflection across every cell, axle and observation boundary using exact-order Gaussian quadrature, subject to floating-point roundoff. The representative train position maximises midspan live moment only; it is not asserted to maximise deflection or stress.", "",
        "Six full axles can occupy the declared 20 m span. Let Q be their maximum total factored force. For every train position, live moment is at most Q·x·(L−x)/L. The unit-moment influence for any displacement observation is at most x·(L−x)/L. Integrating the product of this influence envelope and the total moment envelope over each cell's EI bounds every observation and train position **within the declared beam model**. This is not a physical deflection bound when cracking, shear, slip or unknown installed loads invalidate that model. The dynamic-factor hypothesis is applied once; each axle load already covers both rails.", "",
        "The three span mass scenarios reuse the priced reinforcement/prestress/rail/fastener accounts once. Nominal geometry gravity follows its actual cells; additional accounts are spread uniformly as an explicit hypothesis. Foundation and service price reserves are not converted into beam mass. Concrete stress results are demands without credited resistance, not strength screens.", "",
        "## Manufacturing and experiment ranking", "",
        "Required hook mass includes nominal span stock, preliminary reinforcement/prestress and 25% rigging. A declared 60 t hook-capacity hypothesis is checked without assuming any crane radius or lifting-point qualification. When exceeded, erection cost is increased using the configured Class C scaling law; the result does not confirm that a suitable crane or lift exists. Manufacturing and civil labour retain the parent portfolio's two-shift basis.", "",
        "The family-cell archive compares conditional stiffness, lifting-adjusted provisional cost and stock mass. It preserves the original quantity-only archive and every rejected alternative. Experiment ordering grants no stage-two admission; resistance, interfaces and manufacture remain explicit next tasks. Calculations run in the current Python process with a runtime guard between candidates; the memory request is recorded but is not an operating-system limit or isolation boundary.", "",
        "## Reproduce", "", "```bash", "python3 -m engineering.design_search.civil_shape_mechanics build", "python3 -m engineering.design_search.civil_shape_mechanics verify", "```", "",
        "Methods: [University of Illinois beam/composite bending](https://mechref.engr.illinois.edu/sol/bending.html) and [University of Alberta virtual work](https://engcourses-uofa.ca/variational-principles/the-principle-of-virtual-work/). These explain the analytical methods; they do not validate this railway or its assumed material properties.", "",
        "[Exact inputs, hypotheses and results](result.json.gz) · [Mechanical assumptions](../../../campaigns/civil-shape-mechanics.toml) · [Source/payload receipt](manifest.json) · [Physical geometry and cost portfolio](../civil-shape-portfolio/README.md)", ""]
    return "\n".join(lines)


def _check(out):
    m=json.loads((out/"manifest.json").read_bytes())
    if m.get("manifest_id")!=identity({k:v for k,v in m.items() if k!="manifest_id"}):raise ValueError("Civil mechanics manifest identity differs")
    files={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!="manifest.json"}
    if any(p.is_symlink() or p.is_dir() for p in out.iterdir()) or files!=m.get("files_sha256"):
        raise ValueError("Civil mechanics payload differs")
    return m


def build(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);value=_calculate(root)
    out.parent.mkdir(parents=True,exist_ok=True); stage=Path(tempfile.mkdtemp(prefix=".civil-mechanics-",dir=out.parent))
    try:
        (stage/"result.json.gz").write_bytes(portable_gzip.compress(encoded(value)));(stage/"README.md").write_text(_readme(value))
        m=dict(schema="osr-civil-mechanics-publication/1",study_id=value["study_id"],source_sha256=value["source_sha256"],
            files_sha256={p.name:digest(p) for p in stage.iterdir()},**FLAGS)
        m["manifest_id"]=identity(m);(stage/"manifest.json").write_bytes(encoded(m));verify(root,stage)
        if out.exists():
            old=_check(out)
            if old==m:return verify(root,out)
            backup=root/"build/civil-shape-mechanics/replaced-publications"/old["manifest_id"]
            backup.parent.mkdir(parents=True,exist_ok=True)
            if backup.exists():raise ValueError("Prior civil mechanics packet already retained; inspect replacement")
            shutil.move(out,backup)
        stage.rename(out)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return verify(root,out)


def verify(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);m=_check(out)
    if m.get("schema")!="osr-civil-mechanics-publication/1" or m.get("source_sha256")!=sources(root):
        raise ValueError("Civil mechanics source epoch differs")
    expected=_calculate(root)
    if (json.loads(gzip.decompress((out/"result.json.gz").read_bytes()))!=expected
            or (out/"README.md").read_text()!=_readme(expected) or m.get("study_id")!=expected["study_id"]
            or any(m.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError("Civil mechanics does not reproduce")
    return dict(verified=True,study_id=expected["study_id"],manifest_id=m["manifest_id"],candidate_count=expected["candidate_count"],
        calculated_case_count=expected["calculated_case_count"],retained_candidates=len(expected["archive"]["retained_candidate_ids"]),**FLAGS)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("action",choices=("plan","build","verify"))
    action=parser.parse_args().action
    print(json.dumps({"plan":specification,"build":build,"verify":verify}[action](),indent=2))

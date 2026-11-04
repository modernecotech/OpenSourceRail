"""Rust ask/evaluate/tell search using existing physical grammar productions.

Rust generates new programs and Pareto fronts; NumPy screens large proposal
batches. Only a bounded subset receives exact nominal-stock geometry and cost,
then a smaller subset receives the existing DFMA/interface checks. Neither a
proposal nor a proxy is physical evidence. Expensive native solvers are not
dispatched by this stage-zero/partial-stage-one adapter.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
import gzip
import fcntl
from io import BytesIO
import json
import os
from math import isfinite
from pathlib import Path
import platform
import stat
import time
import tomllib
import tempfile

import numpy as np

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import design_grammar as grammar, design_portfolio, model_cost, shape_families
from . import native_search, native_refinement, search_archive, topology_mutation, search_feedback, invocation_cache, axial_analysis
from . import frame_analysis, frame_refinement, frame_native
from . import topology_revision
from . import section_torsion,section_torsion_job,frame_section_refinement
NativeSearch = native_search.NativeSearch

PRODUCER = "engineering/design_search/native_campaign.py"
CONFIG = "campaigns/rust-design-search.toml"
FLAGS = dict(design_portfolio.FLAGS, physical_journey_completed=False,
             selected_reference_changed=False)
OBJECTIVES = ("nominal_stock_kg", "factory_gate_base_iqd", "factory_process_hours")
OPEN = ["Complete installed mass/CG/inertia, attachments and equipment remain unknown",
        "Whole-body structural, fatigue, fire, braking and propulsion qualification is not supplied by search",
        "Curved/implicit solids, continuum cellular geometry and new architecture adapters require separate implementations",
        "Whole-railway installed/lifecycle comparison requires same-candidate downstream propagation",
        "No trained surrogate, refined full-body or whole-railway solver is supplied by this bounded adapter"]
EXECUTING = {Path(module.__file__): digest(module.__file__) for module in (
    grammar, design_portfolio, model_cost, shape_families, native_search,
    topology_mutation, native_refinement, search_archive, search_feedback, invocation_cache, axial_analysis,
    frame_analysis,frame_refinement,frame_native,topology_revision,section_torsion,section_torsion_job,frame_section_refinement)}
EXECUTING[Path(__file__)]=digest(__file__)


def specification(root=ROOT):
    value = tomllib.loads((Path(root)/CONFIG).read_text())
    if (value.get("schema") != "osr-native-generative-search/1"
            or value.get("purpose") != "next-experiment" or value.get("change_selected_reference") is not False
            or value.get("exploration_weights") != [50, 30, 20]):
        raise ValueError("Explicit non-promoting native search contract required")
    for key, low, high in (("generations", 0, 8), ("proposals_per_generation", 1, 10000),
            ("evaluations_per_generation", 1, 64), ("detailed_finalists", 0, 18),
            ("maximum_seconds", 1, 600), ("seed", 0, 2**64-1)):
        if type(value.get(key)) is not int or not low <= value[key] <= high:
            raise ValueError("Bounded search invocation required: " + key)
    bracing=value.get("seed_bracing")
    if not isinstance(bracing,list) or not bracing or len(set(bracing))!=len(bracing) or any(type(x) is not bool for x in bracing):
        raise ValueError("Explicit unique braced/unbraced model controls required")
    expected = {"bay_pitch_m", "frame_depth_m", "chord_wall_m", "skin_thickness_m",
                "core_thickness_m", "modular_length_m", "braced", "integrated_roof", "topology"}
    if set(value.get("axes", {})) != expected:
        raise ValueError("Explicit supported grammar axes required")
    for name, choices in value["axes"].items():
        if not isinstance(choices, list) or not choices or len(choices) != len(set(choices)):
            raise ValueError("Unique nonempty choices required")
        if name=="topology":
            valid=all(x in ("reference",*topology_mutation.OPERATORS,topology_revision.OPERATOR) for x in choices)
        elif name in ("braced", "integrated_roof"):
            valid = all(type(x) is bool for x in choices)
        else:
            valid = all(type(x) in (int, float) and isfinite(x) and x > 0 for x in choices)
        if not valid or ("reference" if name=="topology" else grammar.parameters()[name]) not in choices:
            raise ValueError("Finite typed axes containing the declared seed required: " + name)
    refinement=value.get("refinement",{})
    if (type(refinement.get("memory_mb")) is not int or refinement["memory_mb"] not in (1024,2048)
            or type(refinement.get("timeout_s")) is not int or refinement["timeout_s"] not in (30,45)
            or type(refinement.get("maximum_new_assessments")) is not int or not 0<=refinement["maximum_new_assessments"]<=64):
        raise ValueError("Bounded axial refinement resources required")
    feedback=value.get("feedback",{})
    for name,low,high in (("maximum_new_assessments",0,64),("maximum_total_assessments",0,64),("maximum_parent_weight",1,4)):
        if type(feedback.get(name)) is not int or not low<=feedback[name]<=high:
            raise ValueError("Bounded analytical parent feedback required: "+name)
    if feedback["maximum_new_assessments"]>feedback["maximum_total_assessments"]:
        raise ValueError("New feedback work cannot exceed the total observation budget")
    frame=value.get("frame_refinement",{})
    if type(frame.get("maximum_assessments")) is not int or not 0<=frame["maximum_assessments"]<=3:
        raise ValueError("Bounded zero-to-three coarse frame assessments required")
    return value


def axes(root=ROOT):
    spec = specification(root)
    return {"family": sorted(shape_families.registry(root)), **spec["axes"]}


def _sources(root):
    return {**design_portfolio.sources(root), PRODUCER: digest(Path(root)/PRODUCER),
            "engineering/design_search/native_search.py": digest(Path(root)/"engineering/design_search/native_search.py"),
            **{module.PRODUCER:digest(Path(root)/module.PRODUCER) for module in (
                topology_mutation,native_refinement,search_archive,search_feedback,invocation_cache,axial_analysis,
                frame_analysis,frame_refinement,frame_native,topology_revision,section_torsion,section_torsion_job,frame_section_refinement)},
            **{name:digest(Path(root)/name) for name in (
                "engineering/design_search/grammar_structure.py","engineering/design_search/grammar_shell.py")},
            CONFIG: digest(Path(root)/CONFIG)}


def _decode_genes(genes,domains):
    values={name:choices[index] for (name,choices),index in zip(domains.items(),genes)}
    topology=values.pop("topology","reference")
    parameters=grammar.parameters();parameters.update(values)
    return parameters,topology


def _seed_genomes(domains,bracing):
    defaults=grammar.parameters()
    return [[values.index(family if name=="family" else "reference" if name=="topology"
                else braced if name=="braced" else defaults[name]) for name,values in domains.items()]
            for family in domains["family"] for braced in bracing]


def _archive(engine,rows):
    return search_archive.archive(engine,rows,OBJECTIVES,("family","topology"))


def _load_genome(genes,domains,recipes,state,root):
    parameters,topology=_decode_genes(genes,domains)
    candidate,_=_geometry(parameters,recipes,state,root,topology)
    return candidate


def _assessment_order(rows,genes,domains):
    groups={}
    for cid,row in rows.items():groups.setdefault(tuple(sorted(row["descriptor"].items())),[]).append(cid)
    priority=lambda cid:(rows[cid]["descriptor"]["topology"]=="reference",
        not _decode_genes(genes[cid],domains)[0]["braced"],
        tuple(sorted(rows[cid]["descriptor"].items())),rows[cid]["metrics"]["factory_gate_base_iqd"],cid)
    representatives=[min(ids,key=lambda cid:(not _decode_genes(genes[cid],domains)[0]["braced"],
        rows[cid]["metrics"]["factory_gate_base_iqd"],cid)) for ids in groups.values()]
    return sorted(representatives,key=priority)+sorted(set(rows)-set(representatives),key=priority)


def _comparison_context(candidate):
    graph=candidate["structure"];basis=graph["load_basis"];nodes={n["id"]:n["at_m"] for n in graph["nodes"]}
    supports=sorted((nodes[s["node_id"]][0],nodes[s["node_id"]][1],tuple(sorted(s["dofs"]))) for s in graph["supports"])
    return identity(dict(requirement_revision=candidate["requirement_revision"],model_scope=native_refinement.grammar_structure.SCOPE,
        architecture=candidate["physical"]["architecture"],normal_people=basis["normal_people"],
        retained_equipment_accounts=candidate["retained_equipment_accounts"],materials=graph["materials"],
        support_xy_dofs=supports,gravity_m_s2=9.80665,person_mass_kg=75.,
        load_policy="Uniform tributary normal sprung mass including each candidate's own gross stock; installed mass unknown",
        support_policy="Generated lower-chord nodes at retained bogie longitudinal stations; geometry-dependent height unqualified"))


def _frame_order(assessments,rows,recipes):
    """Request topology coverage independently of pin-model admissibility."""
    def priority(assessment):
        row=rows[assessment["candidate_id"]]
        # This is an implemented research material route, not physical evidence.
        known_route=recipes[row["descriptor"]["family"]]["frame"]=="aluminium_reference"
        return (not known_route,row["metrics"]["factory_gate_base_iqd"],assessment["candidate_id"])
    groups={}
    for assessment in assessments:
        groups.setdefault(rows[assessment["candidate_id"]]["descriptor"]["topology"],[]).append(assessment)
    representatives=[min(group,key=priority) for _,group in sorted(groups.items(),key=lambda pair:(pair[0]=="reference",pair[0]))]
    selected={a["candidate_id"] for a in representatives}
    return representatives+sorted((a for a in assessments if a["candidate_id"] not in selected),key=priority)


def _generation_feedback(rows,genes,domains,recipes,root,kernel,spec,previous,reuse=None):
    """Deterministic bounded solver-free observations; replayable before mutation."""
    if not set(previous)<=set(rows):raise RuntimeError("Feedback lost a prior physical parent")
    selected=sorted(previous)
    limit=min(spec["feedback"]["maximum_total_assessments"],len(selected)+spec["feedback"]["maximum_new_assessments"])
    for cid in _assessment_order(rows,genes,domains):
        if len(selected)>=limit:break
        if cid not in previous:selected.append(cid)
    observations=[]
    for cid in selected:
        parameters,topology=_decode_genes(genes[cid],domains)
        def compute():
            candidate,_=_materialise(parameters,recipes,topology)
            if candidate["candidate_id"]!=cid or candidate["definition_id"]!=rows[cid]["definition_id"]:
                raise RuntimeError("Analytical feedback mixed a physical/definition/evaluation context")
            assessment=native_refinement.assess(candidate,root=root)
            return dict(candidate_id=cid,parent_evaluation_id=rows[cid]["evaluation_id"],
                comparison_context_id=_comparison_context(candidate),assessment=assessment)
        # A miss always rebuilds and assesses the graph. Only a freshly computed
        # identical materialisation/evaluation in this invocation may be reused.
        inputs=dict(purpose="generation-observation",parameters=parameters,recipes=recipes,topology=topology,
                    candidate_id=cid,definition_id=rows[cid]["definition_id"],parent_evaluation_id=rows[cid]["evaluation_id"])
        observations.append(compute() if reuse is None else reuse.evaluate("axial-assessment",inputs,compute))
    plan=search_feedback.plan(kernel,list(rows.values()),observations,source_sha256=_sources(root),
                             maximum_weight=spec["feedback"]["maximum_parent_weight"])
    value=dict(schema="osr-generation-feedback-snapshot/1",parent_evaluations=sorted(r["evaluation_id"] for r in rows.values()),
               observations=sorted(observations,key=lambda o:o["candidate_id"]),plan=plan)
    value["snapshot_id"]=identity(value)
    return value


def _refine(data,domains,recipes,state,root,kernel,spec,start,native_jobs,inherited=None,reuse=None,frame_native_jobs=0,section_torsion_jobs=0):
    """Model-specific next-experiment ordering, separate from baseline ranking."""
    groups={}
    for cid,row in data["rows"].items():
        groups.setdefault(tuple(sorted(row["descriptor"].items())),[]).append(cid)
    representatives=[]
    for _,ids in sorted(groups.items()):
        # Include cost-dominated candidates: unknown stiffness must not become
        # a zero penalty in the nominal-stock cost archive.
        representatives.append(min(ids,key=lambda cid:(
            not _decode_genes(data["genes_by_id"][cid],domains)[0]["braced"],
            data["rows"][cid]["metrics"]["factory_gate_base_iqd"],cid)))
    representatives.sort(key=lambda cid:(
        data["rows"][cid]["descriptor"]["topology"]=="reference",
        not _decode_genes(data["genes_by_id"][cid],domains)[0]["braced"],
        tuple(sorted(data["rows"][cid]["descriptor"].items())),cid))
    inherited=inherited or {}
    assessments=[o["assessment"] for _,o in sorted(inherited.items())];candidates={}
    contexts={cid:o["comparison_context_id"] for cid,o in inherited.items()}
    for cid in inherited:
        if (inherited[cid]["assessment"]["definition_id"]!=data["rows"][cid]["definition_id"]
                or inherited[cid]["parent_evaluation_id"]!=data["rows"][cid]["evaluation_id"]):
            raise RuntimeError("Refinement inherited a different primary definition")
    limit=min(spec["refinement"]["maximum_new_assessments"],64-len(inherited)) if spec["detailed_finalists"] else 0
    for cid in [cid for cid in representatives if cid not in inherited][:limit]:
        if time.monotonic()-start>=spec["maximum_seconds"]:break
        candidate=_load_genome(data["genes_by_id"][cid],domains,recipes,state,root)
        assessment=_assess(candidate,root,reuse)
        candidates[cid]=candidate;assessments.append(assessment)
        contexts[cid]=_comparison_context(candidate)
    ordered=sorted(assessments,key=lambda a:(a["axial_status"]!="rigid-axial-graph-analytical-only",
        data["rows"][a["candidate_id"]]["descriptor"]["topology"]=="reference",
        tuple(sorted(data["rows"][a["candidate_id"]]["descriptor"].items())),a["candidate_id"]))
    detailed=[];packages=[];dispatched=0;reused=0
    for assessment in ordered[:spec["detailed_finalists"]]:
        if time.monotonic()-start>=spec["maximum_seconds"]:break
        cid=assessment["candidate_id"]
        if cid not in candidates:
            candidates[cid]=_load_genome(data["genes_by_id"][cid],domains,recipes,state,root)
        candidate=candidates[cid]
        if candidate["candidate_id"]!=cid or candidate["definition_id"]!=data["rows"][cid]["definition_id"]:
            raise RuntimeError("Refinement finalist mixed a physical/definition context")
        parameters=candidate["parameters"]
        detail=design_portfolio._evaluate(candidate,recipes[parameters["family"]],"native-search-finalist",model_cost.assumptions(root),root)
        if detail["candidate_id"]!=cid or detail["definition_id"]!=data["rows"][cid]["definition_id"]:
            raise RuntimeError("Detailed evaluator mixed physical/definition identity")
        detailed.append(detail)
        allowed=int(dispatched<native_jobs and assessment["axial_status"]=="rigid-axial-graph-analytical-only")
        options=dict(root=root,native_jobs=allowed,memory_mb=spec["refinement"]["memory_mb"],
                     timeout_s=spec["refinement"]["timeout_s"],subdivisions=1)
        request=native_refinement.request(candidate,**options)
        output=state/"refinements"/request["request_id"]
        if allowed and not request["tool"]["available"]:
            packages.append(dict(request=request,state="solver-dependency-held",native_jobs_used=0));continue
        hit=output.exists()
        if hit:native_refinement.verify(output,candidate,**options)
        else:native_refinement.evaluate(candidate,output=output,**options)
        result=_read_cache(output/"result.json")
        dispatched+=0 if hit else result["native_jobs_used"]
        reused+=result["native_jobs_used"] if hit else 0
        packages.append(dict(request=request,result=result,output=str(output),reused=hit))
    wrappers=[dict(candidate_id=a["candidate_id"],parent_evaluation_id=data["rows"][a["candidate_id"]]["evaluation_id"],
        comparison_context_id=contexts[a["candidate_id"]],assessment=a) for a in assessments]
    final_plan=search_feedback.plan(kernel,list(data["rows"].values()),wrappers,source_sha256=_sources(root),
        maximum_weight=spec["feedback"]["maximum_parent_weight"])
    frames=[];frame_dispatched=0;frame_reused=0
    frame_order=_frame_order(assessments,data["rows"],recipes)
    frame_limit=min(spec["frame_refinement"]["maximum_assessments"],spec["detailed_finalists"])
    for axial in frame_order[:frame_limit]:
        if time.monotonic()-start>=spec["maximum_seconds"]:break
        cid=axial["candidate_id"]
        if cid not in candidates:candidates[cid]=_load_genome(data["genes_by_id"][cid],domains,recipes,state,root)
        candidate=candidates[cid]
        frame=frame_refinement.assess(candidate,root=root)
        if frame["candidate_id"]!=cid or frame["definition_id"]!=data["rows"][cid]["definition_id"]:
            raise RuntimeError("Coarse frame assessment mixed physical/definition context")
        path=state/"frame-assessments"/(frame["assessment_id"]+".json");_store(path,frame)
        record=dict(assessment=frame,output=str(path),native_state="not-requested",native=None)
        if frame_native_jobs and not frame["native_admission"]:
            record["native_state"]="held-by-frame-model-domain"
        elif frame_dispatched<frame_native_jobs and frame["model"] is not None:
            context=dict(assessment_id=frame["assessment_id"],subdivisions=2,
                producer=digest(frame_native.__file__),tool=frame_native._tool(),
                resources=frame_native._resources(),runtime=frame_native._runtime())
            output=state/"frame-native"/identity(context)
            hit=output.exists()
            native=(frame_native.verify(output,root=root) if hit else frame_native.run(
                frame["model"],output,execute=True,subdivisions=2,source_sha256=frame["source_sha256"],root=root))
            if native["model_id"]!=frame["model_id"] or any(native[k] is not False for k in frame_native.FLAGS):
                raise RuntimeError("Native frame comparison mixed model identity or disposition")
            frame_dispatched+=0 if hit else native["native_jobs_used"]
            frame_reused+=native["native_jobs_used"] if hit else 0
            record.update(native_state=native["native_state"],native=native,native_output=str(output),reused=hit)
        frames.append(record)
    section_frames=[];section_new=0;section_reused=0
    if section_torsion_jobs:
        for record in frames:
            if time.monotonic()-start>=spec["maximum_seconds"]:break
            cid=record["assessment"]["candidate_id"]
            refined=frame_section_refinement.assess(candidates[cid],state/"section-torsion",root=root,
                maximum_new_jobs=section_torsion_jobs-section_new)
            if refined["candidate_id"]!=cid or refined["definition_id"]!=data["rows"][cid]["definition_id"]:
                raise RuntimeError("Section-refined frame mixed physical/definition identity")
            output=state/"section-frame-assessments"/(refined["assessment_id"]+".json");_store(output,refined)
            section_new+=refined["new_section_jobs"];section_reused+=refined["reused_section_jobs"]
            section_frames.append(dict(assessment=refined,output=str(output)))
    feedback=dict(assessments=assessments,packages=packages,axial_model_archives=final_plan["axial_archives"],
        section_frame_assessments=section_frames,section_jobs_new=section_new,section_evidence_reused=section_reused,
        frame_assessments=frames,frame_native_jobs_new=frame_dispatched,frame_native_evidence_reused=frame_reused,
        frame_deferred_candidate_ids=[a["candidate_id"] for a in frame_order if a["candidate_id"] not in {r["assessment"]["candidate_id"] for r in frames}],
        frame_selection_purpose="Topology coverage before within-family implemented research material route and partial cost; independent of pin-model pass; no parent-weight or integrated-baseline reward",
        parent_feedback_plan=final_plan,assessment_counts=dict(inherited=len(inherited),
            additional=len(assessments)-len(inherited),maximum_additional=spec["refinement"]["maximum_new_assessments"],
            total=len(assessments),maximum_total=64),
        unassessed_candidate_ids=sorted(set(data["rows"])-{a["candidate_id"] for a in assessments}),
        held_axial_candidates=[dict(candidate_id=a["candidate_id"],status=a["axial_status"])
                               for a in assessments if a["axial_status"]!="rigid-axial-graph-analytical-only"],
        selection_purpose="Next-evaluator eligibility only; pin-graph findings do not reject or qualify a whole body",
        integrated_selection=None,native_jobs_new=dispatched,native_evidence_reused=reused)
    return detailed,feedback


def _store(path, value):
    """Immutable canonical JSON: a conflicting existing record is an error."""
    raw = encoded(value)
    if len(raw)>native_search.MAX_BYTES:
        raise RuntimeError("Search record exceeds reader budget; retain prior checkpoint and generation journals")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if _read_cache(path,parse=False) != raw:
            raise RuntimeError("Conflicting immutable search record: " + str(path))
    else:
        with path.open("xb") as handle:
            handle.write(raw)


def _read_cache(path,*,parse=True,compressed=False):
    try:
        raw=native_search._read(path)
        if compressed:
            with gzip.GzipFile(fileobj=BytesIO(raw)) as handle:
                raw=handle.read(native_search.MAX_BYTES+1)
            if len(raw)>native_search.MAX_BYTES:raise ValueError("decompressed size budget")
        return native_search._parse(raw) if parse else raw
    except (ValueError,OSError,EOFError) as exc:
        raise RuntimeError("Cache integrity/read failure: "+str(path)) from exc


def _seal(value, key="evaluation_id"):
    value[key] = identity(value)
    return value


def _check_epoch(root, expected):
    if any(digest(path)!=value for path,value in EXECUTING.items()):
        raise RuntimeError("Executing search source changed after import")
    if _sources(root) != expected:
        raise ValueError("Search sources changed during execution; retain this interrupted run")
    if any(digest(Path(root)/name)!=value for name,value in expected.items()):
        raise RuntimeError("A retained source binding differs from current file bytes")


def _geometry_key(parameters, recipes, root, topology="reference"):
    # Price, optimizer and service changes do not invalidate unchanged geometry.
    return dict(parameters=parameters, recipes=recipes, runtime=_runtime(),topology_operator=topology,
        source_sha256={name: digest(Path(root)/name) for name in (
            grammar.PRODUCER,topology_mutation.PRODUCER, "engineering/design_search/remit.py", "engineering/station_rail/common.py",
            *((topology_revision.PRODUCER,) if topology==topology_revision.OPERATOR else ()))},
        retained_equipment_sources=grammar._reference_equipment()[2])


def _materialise(parameters,recipes,topology="reference"):
    if topology==topology_revision.OPERATOR and not parameters["braced"]:
        raise ValueError("Member removal requires declared existing crossframe bracing")
    candidate = grammar.build(parameters, recipes=recipes, reason="Native-search materialisation; ancestry is bound by the proposal record")
    base=candidate
    if topology!="reference":
        producer=topology_revision if topology==topology_revision.OPERATOR else topology_mutation
        candidate=producer.mutate(base,topology,requirement_revision=base["requirement_revision"])
    return candidate,base


def _geometry(parameters, recipes, state, root, topology="reference"):
    request = _geometry_key(parameters, recipes, root,topology)
    key = identity(request); path = state/"geometry"/(key+".json.gz")
    candidate,base=_materialise(parameters,recipes,topology)
    if path.exists():
        record = _read_cache(path,compressed=True)
        if (record.get("request") != request or record.get("record_id") != identity(
                {k:v for k,v in record.items() if k != "record_id"})):
            raise RuntimeError("Geometry cache identity differs")
        if record.get("candidate") != candidate or record.get("materialisation_base")!=base:
            raise RuntimeError("Cached geometry does not replay from the declared materialiser")
        return candidate, True
    record = _seal(dict(request=request, candidate=candidate,materialisation_base=base), "record_id")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = gzip.compress(encoded(record), mtime=0)
    with path.open("xb") as handle:
        handle.write(raw)
    return candidate, False


def _evaluate(candidate, assumptions, state, root):
    # Exact material/cost dependencies, not optimizer or descriptor-cell bytes.
    dependencies = {k:v for k,v in design_portfolio.sources(root).items()
                    if k not in ("engineering/design_search/quality_diversity.py", shape_families.PRODUCER)}
    dependencies[PRODUCER]=digest(Path(root)/PRODUCER)
    request = dict(candidate_id=candidate["candidate_id"], definition_id=candidate["definition_id"],runtime=_runtime(),
        assumption_id=assumptions["assumption_id"], evaluator_sources=dependencies, fidelity=0,
        requirements=deepcopy(candidate["requirements"]) if "requirements" in candidate else candidate["requirement_revision"])
    key = identity(request); path = state/"stock-cost"/(key+".json")
    cost = design_portfolio._factory_gate_stock_estimate(candidate, assumptions, root)
    mass = sum(part["mass_kg"] for part in candidate["parts"])
    record = _seal(dict(request=request, candidate_id=candidate["candidate_id"],
        definition_id=candidate["definition_id"], descriptor={"family":candidate["parameters"]["family"],
            "topology":candidate.get("topology_mutations",[{}])[-1].get("operator","reference")},
        metrics=dict(nominal_stock_kg=mass, factory_gate_base_iqd=cost["scenarios_iqd"]["base"],
                     factory_process_hours=cost["process_hours"]["base"]), cost_estimate=cost,
        complete_installed_mass_kg=None, complete_installed_cost_iqd=None,
        execution="completed", engineering_screen="unknown", structural_analysis="not-run",
        fidelity=0, evidence_maturity="conditional-nominal-stock-and-Class-C-cost", **FLAGS))
    exists=path.exists()
    _store(path, record)  # Cheap replay prevents resealed zero-cost/mass records.
    return record, exists


def screen_programs(programs, domains, recipes):
    """Vectorised indicative stock proxy for experiment ordering, not rejection.

    The proxy counts full envelope panels and four longitudinal RHS members. It
    omits openings and detailed ribs/joints. Its error is not calibrated; it is
    never a candidate quantity, cost, stiffness or compliance result.
    """
    names = list(domains)
    def column(name):
        i = names.index(name)
        return np.asarray([domains[name][p["genes"][i]] for p in programs])
    if not programs:
        return []
    family = column("family")
    rho = np.asarray([2710. if recipes[x]["frame"] == "aluminium_reference" else 1900. for x in family])
    sandwich = np.asarray([recipes[x]["shell"] != "skin" for x in family])
    skins = np.where(sandwich, 2., 1.)
    shell_area = 2*17*3.7+17*2.65+2*2.65*3.7
    defaults = grammar.parameters(); w=defaults["chord_width_m"]; h=defaults["chord_height_m"]
    t = column("chord_wall_m").astype(float)
    proxy = (4*17*(w*h-(w-2*t)*(h-2*t))*rho
        + shell_area*skins*column("skin_thickness_m").astype(float)*1900
        + shell_area*sandwich*column("core_thickness_m").astype(float)*85.)
    return [float(x) for x in proxy]


def _definition_screen(genes,domains):
    values=dict(zip(domains,(choices[index] for index,choices in zip(genes,domains.values()))))
    if values.get("topology")==topology_revision.OPERATOR and not values.get("braced"):
        return dict(state="held-by-operator-precondition",reason="Member removal requires declared existing crossframe bracing")
    return dict(state="eligible-for-materialisation",reason=None)


def _screen_cell(genes,domains,recipes):
    values=dict(zip(domains,(choices[index] for index,choices in zip(genes,domains.values()))))
    return dict(topology=values["topology"],frame_material=recipes[values["family"]]["frame"])


def _shortlist(programs, proxies, limit, topology_axis=None,eligible=None,coverage=None):
    # Keep the proposed 50/30/20 allocation among actual evaluations, not only
    # among generated programs. Highest-remainder deterministic apportionment.
    labels = ("exploit", "alternative-family", "unconventional")
    quotas = [limit*w//100 for w in (50,30,20)]
    for i in sorted(range(3), key=lambda i: (-(limit*(50,30,20)[i]%100), i))[:limit-sum(quotas)]:
        quotas[i] += 1
    if eligible is None:eligible=[True]*len(programs)
    if len(eligible)!=len(programs) or any(type(value) is not bool for value in eligible):
        raise ValueError("Explicit same-size definition eligibility flags required")
    if coverage is not None and (len(coverage)!=len(programs) or any(not isinstance(value,str) for value in coverage)):
        raise ValueError("Explicit same-size coverage cell identities required")
    ordered = sorted((i for i in range(len(programs)) if eligible[i]), key=lambda i: (proxies[i], tuple(programs[i]["genes"])))
    chosen = []
    for label, quota in zip(labels, quotas):
        chosen.extend([i for i in ordered if programs[i]["operator"] == label][:quota])
    chosen.extend(i for i in ordered if i not in chosen and len(chosen)<limit)
    if topology_axis is not None:
        # Protect real topology experiments from a proxy that deliberately omits
        # their added members. Preserve category quotas where a swap permits it.
        for topology in sorted({programs[i]["genes"][topology_axis] for i in ordered})[:limit]:
            if any(programs[i]["genes"][topology_axis]==topology for i in chosen):continue
            candidates=[i for i in ordered if programs[i]["genes"][topology_axis]==topology]
            counts={t:sum(programs[i]["genes"][topology_axis]==t for i in chosen)
                    for t in {programs[i]["genes"][topology_axis] for i in chosen}}
            spare=[i for i in chosen if counts[programs[i]["genes"][topology_axis]]>1]
            pairs=[(candidate,victim) for candidate in candidates for victim in spare]
            if not pairs:continue
            candidate,victim=min(pairs,key=lambda pair:(
                programs[pair[0]]["operator"]!=programs[pair[1]]["operator"],
                proxies[pair[0]],-proxies[pair[1]],tuple(programs[pair[0]]["genes"])))
            chosen[chosen.index(victim)]=candidate
    if coverage is not None:
        for cell in sorted({coverage[i] for i in ordered})[:limit]:
            if any(coverage[i]==cell for i in chosen):continue
            candidates=[i for i in ordered if coverage[i]==cell]
            counts={key:sum(coverage[i]==key for i in chosen) for key in {coverage[i] for i in chosen}}
            spare=[i for i in chosen if counts[coverage[i]]>1]
            pairs=[(candidate,victim) for candidate in candidates for victim in spare]
            if not pairs:continue
            candidate,victim=min(pairs,key=lambda pair:(
                programs[pair[0]]["operator"]!=programs[pair[1]]["operator"],proxies[pair[0]],-proxies[pair[1]],tuple(programs[pair[0]]["genes"])))
            chosen[chosen.index(victim)]=candidate
    return chosen


def _checkpoint(path, value):
    value = _seal(deepcopy(value), "checkpoint_id")
    raw=encoded(value)
    if len(raw)>native_search.MAX_BYTES:
        raise RuntimeError("Checkpoint exceeds reader budget; prior checkpoint and generation journals retained")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():raise RuntimeError("Symlinked checkpoint destination is not permitted")
    if path.exists():
        native_search._regular(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".checkpoint-", delete=False) as handle:
        temporary=Path(handle.name);handle.write(raw)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _runtime():
    return dict(python_implementation=platform.python_implementation(),python_version=platform.python_version(),
                numpy_version=np.__version__,proxy_dtype="float64",coordinator_workers=1,
                numerical_runtime=native_refinement._runtime())


def _verify_frontier(data,contract_id,state,kernel,domains,recipes,reuse=None):
    """Replay Rust requests and bind resumable programs to their exact journals."""
    known={};feedback_observations={};expected_seen=[p["genes"] for p in data["attempts"] if p["operator"]=="seed"]
    seed_genes={tuple(g) for g in _seed_genomes(domains,data["contract"]["specification"]["seed_bracing"])}
    seed_records=[*data["seed_pending"],*[p for p in data["attempts"] if p["operator"]=="seed"]]
    if len(seed_records)!=len(seed_genes) or {tuple(p["genes"]) for p in seed_records}!=seed_genes:
        raise RuntimeError("Checkpoint seed coverage/uniqueness differs")
    for p in seed_records:
        if tuple(p["genes"]) not in seed_genes or p["parent_candidate_ids"] or p["generation"]!=0:
            raise RuntimeError("Checkpoint seed differs from the declared grammar registry")
    for ordinal,generation in enumerate(data["generations"],1):
        packet=native_search._parse(native_search._read(state/"generated"/(generation["generation_id"]+".json")))
        req=packet["request"]
        declared=data["contract"]["specification"]
        count=generation["parent_attempt_count"]
        if type(count) is not int or not 0<=count<=len(data["attempts"]):
            raise RuntimeError("Generation parent attempt prefix differs")
        parent_rows={};parent_genes={}
        for attempt in data["attempts"][:count]:
            if attempt.get("evaluation_id") in data["all_evaluations"]:
                cid=attempt["candidate_id"]
                parent_rows.setdefault(cid,data["all_evaluations"][attempt["evaluation_id"]])
                parent_genes.setdefault(cid,attempt["genes"])
        snapshot=_generation_feedback(parent_rows,parent_genes,domains,recipes,ROOT,kernel,
            data["contract"]["specification"],feedback_observations,reuse)
        snapshot_path=state/"feedback"/(snapshot["snapshot_id"]+".json")
        if _read_cache(snapshot_path)!=snapshot:
            raise RuntimeError("Generation parent feedback does not replay")
        feedback_observations={o["candidate_id"]:o for o in snapshot["observations"]}
        parent_archive=snapshot["plan"]["cost_archive"]
        expected_parents=[dict(candidate_id=p["candidate_id"],genes=parent_genes[p["candidate_id"]],weight=p["weight"])
                          for p in snapshot["plan"]["parents"]]
        if (generation["generation"]!=ordinal or req["generation"]!=ordinal
                or generation.get("parent_feedback_snapshot_id")!=snapshot["snapshot_id"]
                or packet.get("feedback_snapshot_id")!=snapshot["snapshot_id"]
                or req["parents"]!=expected_parents or generation["parent_archive_id"]!=parent_archive["archive_id"]
                or req["weights"]!=declared["exploration_weights"] or req["limit"]!=declared["proposals_per_generation"]
                or req["max_attempts"]!=min(1000000,declared["proposals_per_generation"]*20) or req["family_axis"]!=0
                or req["seen"]!=expected_seen or req["seed"]!=data["contract"]["specification"]["seed"]
                or req["axes"]!=[dict(name=name,choices=len(values)) for name,values in domains.items()]
                or generation["generation_id"]!=identity(dict(contract_id=contract_id,generation=generation["generation"],request=req))
                or packet["generated"]!=kernel.propose(**req)):
            raise RuntimeError("Checkpoint generation does not replay from its Rust request")
        native={tuple(p["genes"]):p for p in packet["generated"]["proposals"]}
        expected_seen.extend(p["genes"] for p in packet["generated"]["proposals"])
        proxies=dict(zip((tuple(p["genes"]) for p in packet["generated"]["proposals"]),
                         screen_programs(packet["generated"]["proposals"],domains,recipes)))
        if (len(packet["programs"])!=len(native)
                or {tuple(p["genes"]) for p in packet["programs"]}!=set(native)
                or len({p["proposal_id"] for p in packet["programs"]})!=len(native)):
            raise RuntimeError("Generation program coverage/uniqueness differs")
        for p in packet["programs"]:
            genes=tuple(p["genes"]);core=native.get(genes)
            if (core is None or any(p[k]!=core[k] for k in ("genes","operator","parent_candidate_ids"))
                    or p.get("definition_screen")!=_definition_screen(p["genes"],domains)
                    or p.get("screen_cell")!=_screen_cell(p["genes"],domains,recipes)
                    or p.get("parent_feedback_snapshot_id")!=snapshot["snapshot_id"]
                    or p.get("variable_registry_id")!=data["contract"]["variable_registry_id"]
                    or p.get("requirement_context")!=data["contract"]["requirements_context"]
                    or p["proxy_stock_kg"]!=proxies[genes] or p["generation"]!=generation["generation"]
                    or p["proposal_id"]!=identity(dict(program={k:v for k,v in p.items() if k!="proposal_id"},contract_id=contract_id))):
                raise RuntimeError("Generation program differs from its Rust provenance")
            known[p["proposal_id"]]=p
    for p in [*data["pending"],*data["deferred"],*data["attempts"]]:
        base={k:v for k,v in p.items() if k not in ("candidate_id","definition_id","evaluation_id","state","reason")}
        if p["operator"]!="seed" and known.get(p.get("proposal_id"))!=base:
            raise RuntimeError("Checkpoint program differs from immutable generation journal")
        refs=p.get("parent_evaluations",[])
        if ([r["candidate_id"] for r in refs]!=p["parent_candidate_ids"]
                or any(data["all_evaluations"].get(r["evaluation_id"],{}).get("candidate_id")!=r["candidate_id"]
                       or data["rows"].get(r["candidate_id"],{}).get("evaluation_id")!=r["evaluation_id"] for r in refs)):
            raise RuntimeError("Checkpoint parent evaluation lineage differs")
    tracked=[p["proposal_id"] for p in [*data["pending"],*data["deferred"],*data["attempts"]] if p["operator"]!="seed"]
    if len(tracked)!=len(set(tracked)) or set(tracked)!=set(known):
        raise RuntimeError("Checkpoint proposal coverage/uniqueness differs")
    if any(any(k in p for k in ("state","candidate_id","evaluation_id","definition_id"))
           for p in [*data["pending"],*data["deferred"],*data["seed_pending"]]):
        raise RuntimeError("Unexecuted checkpoint program contains a result")
    states={"evaluated-nominal-stock","duplicate-physical-geometry",
            "definition-or-model-domain-unresolved","cost-model-domain-unresolved"}
    if any(p.get("state") not in states for p in data["attempts"]):
        raise RuntimeError("Checkpoint attempt lifecycle differs")
    if data["seen"]!=expected_seen or data["next_generation"]!=len(data["generations"])+1:
        raise RuntimeError("Checkpoint continuation/seen frontier differs")
    return feedback_observations


def _assess(candidate,root,reuse=None):
    if reuse is None:return native_refinement.assess(candidate,root=root)
    # The whole canonical candidate includes definition, physical graph, loads,
    # requirements and source hypotheses; the session also guards source/runtime.
    return reuse.evaluate("axial-assessment",dict(candidate=candidate),
        lambda:native_refinement.assess(candidate,root=root))


def _run(*, root=ROOT, state=None, generations=None, binary=None, maximum_new_evaluations=None, native_jobs=0,invocation_reuse=True,frame_native_jobs=0,section_torsion_jobs=0):
    root=Path(root).resolve()
    if root != ROOT.resolve():
        raise ValueError("Execute the coordinator from its imported source checkout")
    spec=specification(root)
    target_generation=spec["generations"] if generations is None else generations
    if type(target_generation) is not int or not 0<=target_generation<=8:
        raise ValueError("Zero-to-eight generations required")
    budget=spec["evaluations_per_generation"]*target_generation if maximum_new_evaluations is None else maximum_new_evaluations
    if type(budget) is not int or not 0<=budget<=512:
        raise ValueError("Zero-to-512 new evaluation budget required")
    if type(native_jobs) is not int or not 0<=native_jobs<=3:
        raise ValueError("Zero-to-three new axial solver jobs required")
    if type(frame_native_jobs) is not int or not 0<=frame_native_jobs<=3:
        raise ValueError("Zero-to-three separately budgeted native frame jobs required")
    if type(section_torsion_jobs) is not int or not 0<=section_torsion_jobs<=3:
        raise ValueError("Zero-to-three separately budgeted section-torsion workers required")
    if type(invocation_reuse) is not bool:
        raise ValueError("Explicit boolean invocation reuse policy required")
    kernel=NativeSearch(root=root,binary=binary)
    state=Path(state) if state is not None else root/"build/native-design-search"
    if state.is_symlink():raise ValueError("Regular campaign state directory required")
    source=_sources(root);_check_epoch(root,source)
    def guard():
        _check_epoch(root,source)
        return dict(root=str(root),sources=source,runtime=_runtime())
    reuse=invocation_cache.InvocationCache(guard,enabled=invocation_reuse)
    recipes=shape_families.registry(root);domains=axes(root)
    assumptions=model_cost.assumptions(root);start=time.monotonic()
    search_spec={k:v for k,v in spec.items() if k not in (
        "generations","maximum_seconds","evaluations_per_generation","detailed_finalists")}
    contract=dict(specification=search_spec,sources=source,runtime=_runtime(),invocation_reuse=invocation_reuse,binary_sha256=kernel.receipt["binary_sha256"],
        kernel_build_receipt_id=kernel.receipt["receipt_id"],variable_registry_id=identity(dict(axes=domains,recipes=recipes)),
        requirements_context="Six 17 m cars, 44 seats plus two wheelchair places per car; same development service")
    contract_id=identity(contract);_store(state/"contracts"/(contract_id+".json"),contract)
    checkpoint_path=state/"checkpoints"/(contract_id+".json")
    if checkpoint_path.exists():
        data=native_search._parse(native_search._read(checkpoint_path))
        if data.get("checkpoint_id")!=identity({k:v for k,v in data.items() if k!="checkpoint_id"}) or data.get("contract")!=contract:
            raise RuntimeError("Campaign checkpoint source/identity differs")
        data.pop("checkpoint_id")
    else:
        seed_programs=[dict(genes=genes,operator="seed",parent_candidate_ids=[],generation=0)
                       for genes in _seed_genomes(domains,spec["seed_bracing"])]
        data=dict(contract=contract,rows={},all_evaluations={},genes_by_id={},seen=[],attempts=[],
            pending=[],deferred=[],seed_pending=seed_programs,generations=[],next_generation=1)
    feedback_observations=_verify_frontier(data,contract_id,state,kernel,domains,recipes,reuse)
    stats=dict(geometry_cache_replayed=0,geometry_new=0,cost_cache_replayed=0,cost_new=0,
               completed_attempts_resumed=len(data["attempts"]),new_successor_evaluations=0)
    used=0
    def save(force=False):
        _check_epoch(root,source)
        if force or len(data["attempts"])%8==0:_checkpoint(checkpoint_path,data)
    def evaluate(program):
        nonlocal used
        program=deepcopy(program)
        if (len(program["genes"])!=len(domains) or any(type(i) is not int or not 0<=i<len(values)
                for i,values in zip(program["genes"],domains.values()))
                or program["operator"] not in ("seed","exploit","alternative-family","unconventional")):
            raise RuntimeError("Invalid resumed proposal genes/operator")
        parameters,topology=_decode_genes(program["genes"],domains)
        program.setdefault("parent_evaluations",[dict(candidate_id=cid,evaluation_id=data["rows"][cid]["evaluation_id"])
            for cid in program["parent_candidate_ids"]])
        if ([p["candidate_id"] for p in program["parent_evaluations"]]!=program["parent_candidate_ids"]
                or any(data["all_evaluations"].get(p["evaluation_id"],{}).get("candidate_id")!=p["candidate_id"]
                       for p in program["parent_evaluations"])):
            raise RuntimeError("Proposal parent evaluation lineage differs")
        program["variable_registry_id"]=contract["variable_registry_id"]
        program["requirement_context"]=contract["requirements_context"]
        program.setdefault("proposal_id",identity(dict(program=program,contract_id=contract_id)))
        try:
            candidate,hit=_geometry(parameters,recipes,state,root,topology)
        except ValueError as exc:
            program.update(state="definition-or-model-domain-unresolved",reason=str(exc),candidate_id=None)
        else:
            stats["geometry_cache_replayed" if hit else "geometry_new"]+=1
            try:
                row,hit=_evaluate(candidate,assumptions,state,root)
            except ValueError as exc:
                program.update(state="cost-model-domain-unresolved",reason=str(exc),
                               candidate_id=candidate["candidate_id"],definition_id=candidate["definition_id"])
                data["attempts"].append(program);_store(state/"attempts"/(program["proposal_id"]+".json"),program)
                if program["operator"]!="seed":used+=1;stats["new_successor_evaluations"]+=1
                return
            stats["cost_cache_replayed" if hit else "cost_new"]+=1
            cid=candidate["candidate_id"]
            program.update(candidate_id=cid,definition_id=candidate["definition_id"],evaluation_id=row["evaluation_id"],
                state="duplicate-physical-geometry" if cid in data["rows"] else "evaluated-nominal-stock")
            # A physical alias never overwrites the first archive context or its
            # genes. Every distinct definition/evaluation remains independently linked.
            data["all_evaluations"][row["evaluation_id"]]=row
            data["rows"].setdefault(cid,row);data["genes_by_id"].setdefault(cid,program["genes"])
        data["attempts"].append(program)
        _store(state/"attempts"/(program["proposal_id"]+".json"),program)
        if program["operator"]!="seed":used+=1;stats["new_successor_evaluations"]+=1
    # Completed cheap stages are replay-checked before using a checkpoint's
    # archive. This is inexpensive integrity validation, not a saved solver run.
    by_evaluation={p.get("evaluation_id"):p for p in data["attempts"] if p.get("evaluation_id")}
    for eid,row in data["all_evaluations"].items():
        if eid not in by_evaluation or row.get("evaluation_id")!=eid:
            raise RuntimeError("Checkpoint lost an evaluation's materialisation lineage")
        program=by_evaluation[eid]
        parameters,topology=_decode_genes(program["genes"],domains)
        candidate,_=_geometry(parameters,recipes,state,root,topology);expected,_=_evaluate(candidate,assumptions,state,root)
        if row!=expected:raise RuntimeError("Checkpoint evaluation does not replay")
    for cid,row in data["rows"].items():
        if (row.get("candidate_id")!=cid or data["all_evaluations"].get(row.get("evaluation_id"))!=row
                or by_evaluation[row["evaluation_id"]]["genes"]!=data["genes_by_id"].get(cid)):
            raise RuntimeError("Checkpoint archive mixed physical/definition/gene contexts")
    while data["seed_pending"] and time.monotonic()-start<spec["maximum_seconds"]:
        program=data["seed_pending"].pop(0);data["seen"].append(program["genes"]);evaluate(program);save()
    if not data["rows"]:raise ValueError("No executable seed; retain definitions before extending adapters")
    # Resume the recorded frontier before allocating new generation work.
    while data["pending"] and used<budget and time.monotonic()-start<spec["maximum_seconds"]:
        evaluate(data["pending"].pop(0));save()
    # Once the requested generations exist, a repeated invocation advances the
    # lower-priority retained frontier instead of repeating the same shortlist.
    while (data["next_generation"]>target_generation and data["deferred"] and used<budget
            and time.monotonic()-start<spec["maximum_seconds"]):
        evaluate(data["deferred"].pop(0));save()
    archive=_archive(kernel,list(data["rows"].values()))
    while (not data["seed_pending"] and not data["pending"] and data["next_generation"]<=target_generation
            and used<budget and time.monotonic()-start<spec["maximum_seconds"]):
        generation=data["next_generation"];_check_epoch(root,source)
        snapshot=_generation_feedback(data["rows"],data["genes_by_id"],domains,recipes,root,kernel,spec,feedback_observations,reuse)
        _store(state/"feedback"/(snapshot["snapshot_id"]+".json"),snapshot)
        if time.monotonic()-start>=spec["maximum_seconds"]:break
        feedback_observations={o["candidate_id"]:o for o in snapshot["observations"]}
        parents=snapshot["plan"]["parents"]
        request=dict(seed=spec["seed"],generation=generation,limit=spec["proposals_per_generation"],
            max_attempts=min(1000000,spec["proposals_per_generation"]*20),
            axes=[dict(name=name,choices=len(values)) for name,values in domains.items()],family_axis=0,
            parents=[dict(candidate_id=p["candidate_id"],genes=data["genes_by_id"][p["candidate_id"]],weight=p["weight"])
                     for p in parents],
            seen=deepcopy(data["seen"]),weights=spec["exploration_weights"])
        generated=kernel.propose(**request);programs=generated["proposals"]
        data["seen"].extend(p["genes"] for p in programs)
        proxies=screen_programs(programs,domains,recipes)
        definition_screens=[_definition_screen(p["genes"],domains) for p in programs]
        screen_cells=[_screen_cell(p["genes"],domains,recipes) for p in programs]
        eligible=[screen["state"]=="eligible-for-materialisation" for screen in definition_screens]
        chosen=_shortlist(programs,proxies,min(spec["evaluations_per_generation"],budget-used),list(domains).index("topology"),eligible,
            [identity(cell) for cell in screen_cells])
        ordered=chosen+[i for i in sorted(range(len(programs)),key=lambda i:(not eligible[i],proxies[i],tuple(programs[i]["genes"]))) if i not in chosen]
        prepared=[]
        for i in ordered:
            program=dict(programs[i],generation=generation,proxy_stock_kg=proxies[i],
                definition_screen=definition_screens[i],screen_cell=screen_cells[i],
                parent_evaluations=[dict(candidate_id=cid,evaluation_id=data["rows"][cid]["evaluation_id"])
                    for cid in programs[i]["parent_candidate_ids"]],
                variable_registry_id=contract["variable_registry_id"],requirement_context=contract["requirements_context"],
                parent_feedback_snapshot_id=snapshot["snapshot_id"])
            program["proposal_id"]=identity(dict(program=program,contract_id=contract_id));prepared.append(program)
        generation_id=identity(dict(contract_id=contract_id,generation=generation,request=request))
        _store(state/"generated"/(generation_id+".json"),dict(request=request,generated=generated,programs=prepared,
               feedback_snapshot_id=snapshot["snapshot_id"]))
        data["generations"].append(dict(generation=generation,generation_id=generation_id,
            generated_programs=len(programs),proxy_kind="uncalibrated-full-panel-and-four-RHS-stock-heuristic",
            parent_attempt_count=len(data["attempts"]),parent_archive_id=snapshot["plan"]["cost_archive"]["archive_id"],
            parent_feedback_snapshot_id=snapshot["snapshot_id"],
            kernel_provenance=generated["provenance"]))
        data["pending"].extend(prepared[:len(chosen)])
        data["deferred"].extend(prepared[len(chosen):])
        data["next_generation"]+=1;save(force=True)
        # Spend this invocation's budget; preserve every unexecuted program.
        while data["pending"] and used<budget and time.monotonic()-start<spec["maximum_seconds"]:
            evaluate(data["pending"].pop(0));save()
        archive=_archive(kernel,list(data["rows"].values()))
    detailed,refinement=_refine(data,domains,recipes,state,root,kernel,spec,start,native_jobs,feedback_observations,reuse,frame_native_jobs,section_torsion_jobs)
    save(force=True)
    value=_seal(dict(schema="osr-native-generative-search-result/1",contract_id=contract_id,contract=contract,
        sources=source,axes=domains,candidate_count=len(data["rows"]),evaluations=sorted(data["all_evaluations"].values(),key=lambda r:r["evaluation_id"]),
        archive_contexts={cid:row["evaluation_id"] for cid,row in data["rows"].items()},
        attempts=data["attempts"],generations=data["generations"],pending=data["pending"],deferred=data["deferred"],seed_pending=data["seed_pending"],
        archive=archive,detailed_finalists=detailed,refinement=refinement,cache_statistics=stats,invocation_cache=reuse.statistics(),integrated_selection=None,
        complete_installed_mass_kg=None,maximum_seconds_is_cooperative=True,
        numerical_solver_dispatch_count=refinement["native_jobs_new"]+refinement["frame_native_jobs_new"]+refinement["section_jobs_new"],
        native_dispatch_allowed=bool(native_jobs or frame_native_jobs),
        section_torsion_dispatch_allowed=bool(section_torsion_jobs),
        cache_scope="Cheap geometry/cost replay-checked; bounded fresh analytical records reused only within this invocation; no avoided high-fidelity solver runtime is claimed",
        unresolved=OPEN,**FLAGS),"run_id")
    _store(state/"runs"/(value["run_id"]+".json"),value)
    return dict(run_id=value["run_id"],candidate_count=len(data["rows"]),
        generated_programs=sum(g["generated_programs"] for g in data["generations"]),pending_programs=len(data["pending"]),
        deferred_programs=len(data["deferred"]),
        detailed_finalists=len(detailed),cache_statistics=stats,invocation_cache=reuse.statistics(),
        numerical_solver_dispatch_count=refinement["native_jobs_new"]+refinement["frame_native_jobs_new"]+refinement["section_jobs_new"],
        native_evidence_reused=refinement["native_evidence_reused"]+refinement["frame_native_evidence_reused"],archive_backend=archive["backend"],
        coarse_frame_assessments=len(refinement["frame_assessments"]),frame_native_jobs_new=refinement["frame_native_jobs_new"],
        section_frame_assessments=len(refinement["section_frame_assessments"]),section_jobs_new=refinement["section_jobs_new"],
        section_evidence_reused=refinement["section_evidence_reused"],
        generation_feedback_snapshots=len(data["generations"]),feedback_observations=len(feedback_observations),
        analytical_assessment_counts=refinement["assessment_counts"],
        analytical_assessments=len(refinement["assessments"]),output=str(state/"runs"/(value["run_id"]+".json")),
        elapsed_s=time.monotonic()-start,integrated_selection=None,**FLAGS)


@contextmanager
def _state_lock(state):
    state=Path(state)
    if state.is_symlink():raise RuntimeError("Symlinked campaign state is not permitted")
    state.mkdir(parents=True,exist_ok=True)
    try:
        descriptor=os.open(state/"coordinator.lock",os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_NONBLOCK,0o600)
    except OSError as exc:
        raise RuntimeError("Regular campaign coordinator lock required") from exc
    with os.fdopen(descriptor,"a+b") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):raise RuntimeError("Regular campaign coordinator lock required")
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise RuntimeError("Campaign state already has an active coordinator") from exc
        try:yield
        finally:fcntl.flock(handle,fcntl.LOCK_UN)


def run(*,root=ROOT,state=None,**kwargs):
    state=Path(state) if state is not None else Path(root)/"build/native-design-search"
    with _state_lock(state):
        return _run(root=root,state=state,**kwargs)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state",type=Path);parser.add_argument("--generations",type=int)
    parser.add_argument("--binary",type=Path)
    parser.add_argument("--native-jobs",type=int,default=0,help="Opt-in new axial CalculiX jobs, zero to three")
    parser.add_argument("--frame-native-jobs",type=int,default=0,help="Separately budgeted zero-to-three conditional coarse frame comparisons")
    parser.add_argument("--section-torsion-jobs",type=int,default=0,help="Opt-in zero-to-three bounded actual-wall section workers; cached fields are replayed")
    parser.add_argument("--evaluations",type=int,help="New successor evaluations in this invocation; seeds are separate")
    parser.add_argument("--no-invocation-reuse",action="store_true",help="Diagnostic independent recomputation mode; separate campaign contract")
    args=parser.parse_args()
    print(json.dumps(run(state=args.state,generations=args.generations,binary=args.binary,
                         maximum_new_evaluations=args.evaluations,native_jobs=args.native_jobs,frame_native_jobs=args.frame_native_jobs,
                         section_torsion_jobs=args.section_torsion_jobs,
                         invocation_reuse=not args.no_invocation_reuse),indent=2))

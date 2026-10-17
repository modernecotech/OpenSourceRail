"""Source-bound mechanical design models, never an as-built physical twin.

The detailed adapter preserves the existing connected-frame calculations. The
architecture adapter compares genuinely different open-I and closed-box sill
concepts using an explicitly narrower elastic beam model. They cannot inherit
each other's connection, manufacturing or qualification evidence.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

from . import architecture_mechanical, coverage, evidence_store, mechanical_detail, mechanical_systems

ROOT = Path(__file__).resolve().parents[2]


def _check(identifier, value, limit, unit, basis):
    return dict(id=identifier, state="unknown" if value is None or limit is None
                else ("pass" if value <= limit else "fail"), value=value,
                limit=limit, unit=unit, basis=basis, acceptance="research-only")


def _part(identifier, parent, title, specifications, material=None,
          manufacturing=None, inspection=None):
    return dict(id=identifier, parent_id=parent, title=title,
                specifications=specifications, material=material,
                manufacturing=manufacturing or {"state": "unaccepted"},
                inspection=inspection or {"state": "unaccepted"})


def architecture_variant(context, kind, height_m, wall_m):
    """Evaluate only the exact controlled source context, without caller edits."""
    current = mechanical_detail._require_context(context)
    return _architecture_variant(current, kind, height_m, wall_m)


def _architecture_variant(context, kind, height_m, wall_m):
    """Evaluate an open-I or closed-box hypothesis with the same load contract.

    Constant EI, rigid transverse compatibility, linear elastic static UDL;
    crossmembers, bolsters, joints and end load introduction are not resolved.
    This is deliberately not a substitute for the detailed frame adapter.
    """
    if kind not in {"open-i", "closed-box"}:
        raise ValueError("unsupported section architecture")
    if any(isinstance(x, bool) or not isinstance(x, (int, float))
           or not math.isfinite(x) or x <= 0 for x in (height_m, wall_m)):
        raise ValueError("finite positive real dimensions required")
    cfg = mechanical_detail._inputs()
    material = cfg["material"]
    section = (mechanical_detail.i_section(context["side_member_width_m"],
                 height_m, wall_m, wall_m) if kind == "open-i" else
               mechanical_detail.box_section(context["side_member_width_m"],
                 height_m, wall_m))
    spine = mechanical_detail.box_section(context["centre_member_width_m"],
                context["centre_member_depth_m"], wall_m)
    inertia = 2 * section["inertia_m4"] + spine["inertia_m4"]
    mass = material["density_kg_m3"] * (
        2 * section["area_m2"] * context["side_member_length_m"] +
        spine["area_m2"] * context["centre_member_length_m"])
    force = context["source_car_force_n"] + mass * 9.80665
    beam = mechanical_detail.overhang_beam(context["body_length_m"],
        context["support_x_m"], force, material["young_modulus_pa"] * inertia)
    stress = beam["maximum_abs_moment_nm"] * 1.25 * max(
        height_m, context["centre_member_depth_m"]) / (2 * inertia)
    parts = [_part("frame", None, "Longitudinal concept model",
        {"scope": "three longitudinal members only; transverse assemblies absent"})]
    for name, width, depth, length, closed in [
        ("left-sill", context["side_member_width_m"], height_m,
         context["side_member_length_m"], kind == "closed-box"),
        ("right-sill", context["side_member_width_m"], height_m,
         context["side_member_length_m"], kind == "closed-box"),
        ("centre-spine", context["centre_member_width_m"],
         context["centre_member_depth_m"], context["centre_member_length_m"], True),
    ]:
        parts.append(_part(name, "frame", name,
            {"section": "box" if closed else "I", "length_m": length,
             "width_m": width, "height_m": depth}))
        plates = [("lower-flange", [length, width, wall_m]),
                  ("upper-flange", [length, width, wall_m])]
        plates += [("web-" + str(i + 1), [length, wall_m, depth-2*wall_m])
                   for i in range(2 if closed else 1)]
        for label, dimensions in plates:
            parts.append(_part(name + ":" + label, name, label,
                {"size_m": dimensions, "quantity": 1,
                 "net_mass_kg": math.prod(dimensions)*material["density_kg_m3"]},
                {"requested": material["designation_requested"], "certified": False},
                {"route": "plate profiling and welded fabrication",
                 "stock_length_and_splices": "unresolved"},
                {"dimensional_tolerances_m": None, "certificate": None}))
        parts.append(_part(name + ":welds", name, "Longitudinal web-flange seams",
            {"seam_count": 4 if closed else 4,
             "nominal_total_length_m": 4 * length, "throat_m": None,
             "scope": "topological seams only; effective weld runs unresolved"},
            {"filler": None}, {"WPS": None, "distortion_sequence": None},
            {"NDT_method": None, "acceptance": None}))
    span = context["support_x_m"][1]-context["support_x_m"][0]
    checks = [
        _check("gross-elastic-bending", stress,
               material["research_normal_stress_limit_pa"], "Pa",
               "1.25 research strength multiplier; no stability/fatigue resistance"),
        _check("service-deflection", beam["maximum_abs_deflection_m"],
               span/1000, "m", "Unaccepted support-span/1000 research screen"),
        _check("equilibrium", abs(sum(beam["reactions_n"])-force),
               max(1e-8, force*1e-12), "N", "Two-support vertical equilibrium"),
        _check("floor-and-gauge", height_m, context["side_depth_envelope_m"], "m",
               "Source side depth is at most a compatibility screen, not swept-gauge approval"),
        _check("transverse-load-path-and-connections", None, None, "N",
               "Bolsters, pads, end framing, joint stiffness and compatibility unresolved"),
        _check("local-global-buckling-fatigue-crash", None, None, "Pa",
               "Elastic gross-section model establishes no buckling, fatigue or crash resistance"),
        _check("closed-section-access-and-corrosion", None, None, "m",
               "Internal coating, weld access, drain/vent holes and inspection access unresolved"),
    ]
    failed = [x["id"] for x in checks if x["state"] == "fail"]
    return dict(id=f"concept-{kind}-{height_m:g}-{wall_m:g}", concept=kind,
        calculator_scope="longitudinal-member elastic architecture hypothesis",
        parameters={"side_height_m": height_m, "wall_m": wall_m,
                    "load_force_n": force, "total_inertia_m4": inertia,
                    "young_modulus_pa": material["young_modulus_pa"]},
        parts=parts, checks=checks,
        objectives={"modeled_longitudinal_mass_kg": mass, "complete_frame_mass_kg": None,
                    "cost_usd": None, "local_content_fraction": None},
        selection_state="rejected-by-research-check" if failed else "held-for-missing-evidence",
        failed_checks=failed, metrics={"beam": beam}, accepted=False,
        scope_exclusions=["transverse and connection masses", "shell and floor participation",
                          "torsion", "nonlinear buckling", "fatigue", "crash", "production"])


def _detailed_variant(context, variables, label):
    candidate = mechanical_detail.assess(variables, context)
    root = "connected-frame"
    parts = [_part(root, None, "Connected underframe and bolsters",
        {"quantity": 1, "coordinate_units": "m", "configuration": context["configuration_id"]})]
    cfg = mechanical_detail._inputs()
    for source in candidate["geometry"]["parts"]:
        spec = {k: deepcopy(v) for k, v in source.items() if k != "id"}
        spec["net_geometry_mass_kg"] = mechanical_detail._volume(source)*cfg["material"]["density_kg_m3"]
        parts.append(_part(source["id"], root, source["id"], spec,
            {"requested": source["material_request"], "certified": False},
            {"route": "cut/profile, finish-machine holes, fit in datum fixture",
             "machine_lead": "swift-cut-xp4000", "machine_order_confirmed": False,
             "approved_cutting_parameters": None},
            {"datum_plan": candidate["manufacturing"]["datums"],
             "tolerance_acceptance": None, "material_certificate": None}))
    for member, length in [("side-left", context["side_member_length_m"]),
                           ("side-right", context["side_member_length_m"]),
                           ("spine", context["centre_member_length_m"])]:
        parts.append(_part(member + "-longitudinal-welds", root,
            "Longitudinal flange-web weld runs",
            {"nominal_run_length_m": length, "effective_run_count": 2,
             "effective_throat_m": variables["weld_throat_m"],
             "calculation_scope": "two effective runs in existing shear-flow screen; full seam map unknown"},
            {"filler": None}, {"WPS": None, "access_and_sequence": None},
            {"NDT_plan": None, "fatigue_acceptance": None}))
        splices = max(0, math.ceil(length/variables["maximum_stock_piece_length_m"])-1)
        for index in range(splices):
            parts.append(_part(f"{member}-splice-{index+1}", root,
                "Transverse full-penetration plate splice group",
                {"station_from_member_start_m": (index+1)*length/(splices+1),
                 "groove_angle_rad": None, "root_gap_m": None,
                 "qualified_plate_joint_count": None},
                {"filler": None}, {"WPS": None, "stress_hotspot_avoidance": None},
                {"UT_plan": None, "fatigue_acceptance": None}))
    n = variables["bolts_per_support"]
    for support in (1, 2):
        parent = f"bogie-interface-pad-{support}"
        for index in range(n):
            for item in ("bolt", "nut", "washer-upper", "washer-lower"):
                parts.append(_part(f"support-{support}-{item}-{index+1}", parent,
                    item, {"quantity": 1, "nominal_diameter_m": variables["bolt_diameter_m"],
                           "coarse_pitch_m": candidate["connections"]["bolt_coarse_pitch_m"],
                           "length_m": None, "thread_engagement_m": None,
                           "offered_geometry": None},
                    {"requested_class": cfg["bolt_request"]["property_class_requested"],
                     "certificate": None},
                    {"supplier_lead": "smith-bullough-fasteners", "origin_confirmed": False,
                     "installation_torque_nm": None, "pretension_n": None},
                    {"thread_gauge": "offered drawing required", "traceability": None}))
        parts.append(_part(f"support-{support}-joint-weld", parent,
            "Support load-path weld group",
            {"effective_throat_m": variables["weld_throat_m"],
             "run_coordinates_m": None, "fatigue_detail": None},
            {"filler": None}, {"WPS": None, "PQR": None, "welder_qualification": None},
            {"VT_MT_UT_plan": "authority-approved method and acceptance required"}))
    parts.append(_part("assembly-datum-fixture", root, "Frame datum assembly fixture",
        {"length_m": cfg["research_limits"]["fixture_length_m"],
         "width_m": cfg["research_limits"]["fixture_width_m"],
         "payload_kg": cfg["research_limits"]["fixture_payload_kg"],
         "capacity_accepted": False}, None,
        {"route": "fabricate and survey fixture; clamp and weld sequence unqualified"},
        {"survey_tolerance_m": None, "proof_load_kg": None}))
    checks = [dict(x, unit=x["units"], acceptance="research-only") for x in candidate["checks"]]
    return dict(id=label, concept="fabricated-open-I-sills-closed-spine-connected-bolsters",
        parameters=deepcopy(variables), parts=parts, checks=checks,
        objectives={"modeled_plate_and_RHS_mass_kg": candidate["objectives"]["mass_kg"],
                    "as_built_mass_kg": None, "cost_usd": None,
                    "British_manufacturing_fraction": None},
        selection_state="rejected-by-research-check" if any(x["state"] == "fail" for x in checks)
                        else "held-for-missing-evidence",
        calculator_scope="existing connected-frame analytical and fabrication screens",
        assembly_sequence=candidate["manufacturing"]["sequence"],
        connections=candidate["connections"], metrics=candidate["metrics"],
        load_sensitivities=candidate["metrics"]["load_case_responses"],
        accepted=False, physical_release=False,
        mass_exclusions=["bolts", "nuts", "washers", "deposited weld metal", "coating",
                         "remaining vehicle assemblies"])


def build():
    """Return deterministic replayable design descriptions with explicit gaps."""
    contexts = mechanical_detail.contexts()
    systems, experiments, requests = [], [], []
    paths = {Path(__file__), Path(mechanical_detail.__file__), mechanical_detail.DATA,
             Path(architecture_mechanical.__file__), Path(mechanical_systems.__file__),
             Path(evidence_store.__file__), Path(coverage.__file__)}
    for context in contexts:
        paths.update(ROOT / p for p in context["source_sha256"])
        seed = mechanical_detail.seed(context)
        robust = dict(seed, side_depth_m=0.6, plate_thickness_m=0.025,
                      web_thickness_m=0.016, spine_wall_m=0.025,
                      bolster_depth_m=0.65, diaphragm_thickness_m=0.025,
                      weld_throat_m=0.008, bolt_diameter_m=0.027,
                      bolts_per_support=8, crossbearer_pitch_m=0.6,
                      maximum_stock_piece_length_m=3.8)
        variants = [_detailed_variant(context, seed, "connected-seed"),
                    _detailed_variant(context, robust, "connected-deep-heavy")]
        feedback = []
        previous = mechanical_detail.assess(seed, context)
        parent_id = "connected-seed"
        # A small actual failure-directed trajectory, independent of the fixed
        # topology comparisons. Re-evaluate geometry, self weight and every
        # parent/connection screen after each proposed change.
        for generation in range(1, 3):
            proposals = mechanical_detail._repair_proposals(previous, context)
            if not proposals:
                break
            proposal = proposals[0]
            child_id = f"connected-feedback-{generation}"
            child = _detailed_variant(context, proposal["variables"], child_id)
            child["parent_variant_id"] = parent_id
            child["proposal_basis"] = proposal["reason"]
            next_result = mechanical_detail.assess(proposal["variables"], context)
            before, after = set(previous["failed_check_ids"]), set(next_result["failed_check_ids"])
            feedback.append(dict(parent_variant_id=parent_id, child_variant_id=child_id,
                reason=proposal["reason"], resolved_failed_checks=sorted(before-after),
                newly_failed_checks=sorted(after-before), remaining_failed_checks=sorted(after),
                self_weight_recomputed=True, all_connection_checks_recomputed=True,
                acceptance="research-only; improvement not presumed"))
            variants.append(child)
            previous, parent_id = next_result, child_id
        for kind, height, wall in [("open-i", .26, .008),
                                   ("open-i", .6, .016),
                                   ("closed-box", .6, .016)]:
            variants.append(architecture_variant(context, kind, height, wall))
        system_id = context["configuration_id"] + ":underframe"
        systems.append(dict(id=system_id, title="Vehicle underframe alternatives",
            configuration_id=context["configuration_id"],
            requirements=[{"id": "static-load-conservation", "value": context["source_car_force_n"],
                           "unit": "N", "accepted": False, "basis": context["load_basis"]},
                          {"id": "physical-release", "accepted": False,
                           "basis": "Calculation screening never authorises manufacture"}],
            interfaces=[{"id": x, "state": "unknown"} for x in
                        ["bogie-support", "floor-shell", "gauge", "traction-brake-mounts"]],
            variants=variants, source_context=context,
            design_status="provisional-design-model-not-as-built-twin"))
        experiments.append(dict(id=system_id + ":architecture-comparison",
            hypothesis="Compare open-I and closed-box sill topology, then vary depth and thickness",
            candidate_ids=[x["id"] for x in variants],
            feedback_generations=feedback, feedback_generation_budget=2,
            comparison_boundary="Only compare objectives with identical calculator_scope and modeled mass coverage",
            outcome="Research screens executed; all release decisions held or rejected",
            internet_idea_generation=False, actual_solver="deterministic Python analytical adapters"))
        for gate, evidence in [
            ("accepted-loads", "AW2/AW3 distribution, track twist, braking, fatigue and crash combinations"),
            ("gauge-and-floor", "approved swept gauge, suspension movement and underfloor envelope"),
            ("materials", "certified plate/subgrade/condition by thickness and temperature"),
            ("connections", "supplier bogie drawings, bolt stack, grip, pretension, fatigue and qualified weld details"),
            ("manufacturing", "confirmed UK machine configurations, stock availability, tolerances and qualified processes"),
            ("physical-validation", "independent structural model correlation, proof/fatigue testing and first article"),
            ("physical-twin", "serialized as-built BOM, surveyed geometry, sensors, calibration and operational history"),
        ]:
            requests.append(dict(id=system_id+":"+gate, state="open", evidence_required=evidence,
                                 blocks="production-release-and-physical-twin-claim"))
    for subsystem in ["bogie-wheelset-bearing", "traction-motor-gearbox", "friction-and-regenerative-brake",
                      "suspension", "coupler-crash", "door-accessibility", "HVAC-fire",
                      "body-shell-floor-interior", "electrical-power-storage", "train-control"]:
        requests.append(dict(id="mechanical-coverage:"+subsystem, state="open",
            evidence_required="Controlled subsystem specification, interfaces, serialized BOM, validated evaluator and supplier/physical evidence",
            blocks="whole-rolling-stock-design-completion", coverage="not-implemented-by-this-adapter"))
    for path in list(paths):
        if path.suffix == ".json":
            paths.update(ROOT / name for name in evidence_store.source_closure(path))
    source_files = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(paths)}
    return dict(schema="osr-domain-design-twin/1", domain="mechanical", source_files=source_files,
        systems=systems, experiments=experiments, open_requests=requests,
        state="provisional-digital-design-model", physical_twin=False,
        complete_specification=False, production_release=False,
        supplier_evidence=deepcopy(mechanical_detail._inputs()["supplier_evidence"]),
        units="SI; each scalar dimension or check carries explicit units",
        evidence_boundary="Computed geometry and analytical research screens; unaccepted loads, interfaces and processes remain open")

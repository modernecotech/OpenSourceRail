"""Bounded phase-1 mechanical fit gate; output is research-only and immutable."""
from hashlib import sha256
import json
from pathlib import Path
from .drive_geometry import compact_drive, axis_aligned_sweep

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "engineering/powered_bogie/fit-closure-policy.json"


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode()


def identity(value):
    return sha256(canonical_bytes(value)).hexdigest()


def load_policy():
    p = json.loads(POLICY_PATH.read_text())
    if p.get("schema") != "osr-mechanical-fit-policy/1":
        raise ValueError("unsupported policy schema")
    return p


def _pose_roster(domain, limit=24):
    # Check both bounds of each coordinate independently, plus twelve mixed
    # corners. The analytic radius envelope covers every intermediate pose.
    axes = (("yaw_rad", "yaw_rad"), ("roll_rad", "roll_rad"),
            ("primary_jounce_m", "primary_jounce_m"),
            ("secondary_jounce_m", "secondary_jounce_m"),
            ("lateral_m", "lateral_m"), ("gear_relative_roll_rad", "gear_relative_roll_rad"))
    poses = []
    for key, out in axes:
        extent = domain[key]
        for value in (-extent, extent):
            row = {name: 0.0 for _, name in axes}
            row[out] = value
            poses.append(row)
    for i in range(max(0, limit-len(poses))):
        row = {}
        for j, (key, out) in enumerate(axes):
            sign = -1 if ((i*7 + j*5 + (i >> (j % 3))) % 2) else 1
            row[out] = sign * domain[key]
        poses.append(row)
    return poses[:limit]


def _variant_candidate(policy, v):
    if v["physical_change"] is False:
        return policy["parent"]["body_candidate_id"]
    definition = {"schema": "osr-powered-bogie-research-candidate/1",
        "parent_candidate_id": policy["parent"]["body_candidate_id"],
        "parent_evaluation_id": policy["parent"]["body_evaluation_id"],
        "parent_pilot_candidate_id": policy["parent"]["pilot_candidate_id"],
        "study_id": policy["study_id"],
        "contract_id": policy["contract_id"], "variant_id": v["variant_id"],
        "body_lift_m": v["body_lift_m"], "motor_source_claim": policy["official_motor_source_claim"],
        "drive_geometry": compact_drive(v["ratio"]),
        "retained_stock": "all parent body, brake, suspension and service occurrences retained",
        "support_allowances": {"pedestals_count": 24, "pedestal_gross_box_m": [.1, .1, .1],
            "emergency_support_and_anti_lift": "unknown positive mass/cost reserve, HOLD"}}
    return identity(definition), definition


def evaluate_variant(variant_id):
    p = load_policy()
    matches = [v for v in p["variants"] if v["variant_id"] == variant_id]
    if len(matches) != 1:
        raise ValueError("variant outside exact three-variant contract")
    v = matches[0]
    source_files = (POLICY_PATH, Path(__file__), Path(__file__).with_name("kinematic_tree.py"),
                    Path(__file__).with_name("drive_geometry.py"))
    sources = {x.relative_to(ROOT).as_posix(): sha256(x.read_bytes()).hexdigest()
               for x in source_files}
    c = _variant_candidate(p, v)
    candidate_id, physical_definition = c if isinstance(c, tuple) else (c, None)
    drive = compact_drive(v["ratio"]) if v["ratio"] else None
    m = p["domain"]
    poses = _pose_roster(m, p["limits"]["poses_per_variant"])
    # Contract yaw/roll/relative roll are so broad that the radius envelope is
    # intentionally coarse. Vertical and lateral domains remain explicit.
    # Gear case follows track->wheelset->gear. Motor follows track->wheelset
    # ->primary->bogie/motor. The body secondary motion is not added to either
    # bogie-fixed or wheelset-fixed hardware.
    case_sweep = axis_aligned_sweep([-.905, .5, .41], [.68, .26, .37],
        m["yaw_rad"] + m["roll_rad"] + m["gear_relative_roll_rad"],
        m["lateral_m"] + m["tolerance_m"])
    motor_sweep = axis_aligned_sweep([-.6437797247430153, -.38, .43], [.268, .094, .268],
        m["yaw_rad"] + m["roll_rad"],
        m["lateral_m"] + m["primary_jounce_m"] + m["tolerance_m"])
    if len(poses) > p["limits"]["poses_per_variant"]:
        raise ValueError("pose budget exceeded")
    evaluation_input = {"candidate_id": candidate_id, "variant": v, "policy": p,
                        "sources": sources, "pose_roster": poses,
                        "case_swept_outer_box_m": case_sweep}
    holds = ["Official STEP/drawing bytes and exact motor mounting/shaft/terminal geometry not frozen",
             "Tolerance and fabrication/assembly clearances unknown; nominal envelope cannot accept fit",
             "Only drive case envelope screened; actual wheel, brake, suspension, body and service solids unavailable to this isolated gate",
             "All twelve bogies are enumerated but cannot be individually located from a source-bound parent occurrence map in this task packet",
             "Finite 24-pose roster is representative; analytic radius sweep is conservative and may be excessively broad",
             "Body-lift pedestal load path, emergency support, anti-lift and kingpin redesign not sized",
             "Retained brake/suspension/service stock identities and masses not re-imported; parent occurrence ledger preserved by reference only",
             "No manufacturing, engineering, operational or physical acceptance"]
    if drive and (abs(drive["ratio_residual"]) > 1e-10 or
                  any(abs(s["centre_residual_m"]) > 1e-10 for s in drive["stages"])):
        holds.append("Gear ratio or pitch-centre geometry mismatch")
    result = {"schema": "osr-mechanical-fit-result/1", "contract_id": p["contract_id"],
        "study_id": p["study_id"], "candidate_id": candidate_id,
        "contract_source": p["contract_source"],
        "physical_definition": physical_definition,
        "parent_body_candidate_id": p["parent"]["body_candidate_id"],
        "parent_body_evaluation_id": p["parent"]["body_evaluation_id"],
        "pilot_candidate_id": p["parent"]["pilot_candidate_id"],
        "evaluation_id": identity(evaluation_input), "source_sha256": sources,
        "variant_id": variant_id, "execution": "completed-bounded-necessary-geometry",
        "numerical_validity": "deterministic arithmetic; no solver or native execution",
        "engineering_screen": "HOLD", "evidence_maturity": "digital research only",
        "physical_accepted": False, "engineering_accepted": False,
        "manufacturing_release": False, "operating_release": False,
        "poses_checked": len(poses), "poses": poses,
        "bogie_coverage": [{"bogie_index": i, "status": "HOLD-exact-parent-transform-unavailable"}
                           for i in range(12)],
        "continuous_swept_outer_box_m": case_sweep,
        "relative_motion_sweeps": {"gear_case_track_frame_m": case_sweep,
            "motor_casing_track_frame_m": motor_sweep,
            "body_secondary_jounce_applied_to_running_gear": False,
            "secondary_motion_domain_m": m["secondary_jounce_m"],
            "coupling_relative_motion": "HOLD: joint and flexible element stroke/angular capacity not dimensioned"},
        "installation_bounds": {
            "nominal_case_box_m": {"centre": [-.905, .5, .41], "size": [.68, .26, .37]},
            "sweep_min_ground_z_m": case_sweep[2][0],
            "required_clearance_m": m["clearance_m"],
            "ground_clearance_screen": "HOLD: swept outer box is conservative; rail, wheel, brake and running-gear solids are not assembled",
            "body_lift_trials_m": [v["body_lift_m"]],
            "floor_top_trial_bounds_after_rigid_body_lift_m": [1.1+v["body_lift_m"], 1.15+v["body_lift_m"]],
            "roof_top_trial_bounds_after_rigid_body_lift_m": [3.5+v["body_lift_m"], 3.55+v["body_lift_m"]],
            "all body items move together": True,
            "pedestal_proposal": {"count_per_train": 24, "gross_box_each_m": [.1,.1,.1],
                "material_hypothesis": "Al 5083", "mass_kg": None, "cost": None,
                "strength/bearing/load path": "HOLD; no positive weighed installed subtotal"},
            "tool_access": "HOLD: socket dimensions, approach vectors, insertion swept volumes and removal clearance are not specified",
            "removal": {"prior_body_lift_control_m": .45,
                "trial_body_lift_m": v["body_lift_m"], "drop_table_path_m": .6,
                "shaft_disengagement_and_case/wheelset_route": "HOLD: dimensions/support/hoist path unknown",
                "retention_and_hoist_WLL": "HOLD"}},
        "interfaces": {
            "motor_mount": {"contract_listed_possible_patterns_not_admitted": ["6xM10", "16xM8"],
                "binding_pattern": None, "tool_stack": None,
                "status": "HOLD: exact variant, drawing bytes, datums and load direction unverified"},
            "motor_to_gear_coupling": {"quantity_per_bogie": 2,
                "motor_axis_point_m": [-.6437797247430153,-.38,.43],
                "intermediate_axis_point_m": [-.8603582324486507,.5,.41],
                "shaft/coupling length and envelope": None,
                "angular/radial/axial capability": None, "status": "HOLD"},
            "gear_output_to_wheelset": {"axis_point_m": [-1.05,.5,.38],
                "bore/key/interference/axle fatigue/retention": None, "status": "HOLD"},
            "torque_reaction": {"axis": "Y", "proposed_bolts_per_bogie": 4,
                "proposed_bolt_size": "M20", "washer/nut stack and joint geometry": None,
                "status": "HOLD: manufacturer interface unavailable"},
            "motor_cradle": {"axis": "Z", "fastener_count": None,
                "status": "HOLD: do not reuse torque reaction bolt count for cradle"}},
        "cooling_and_service_flexibility": {
            "motor_count_per_bogie": 2, "source_claim_minimum_coolant_l_min_per_motor": 6,
            "minimum_coolant_flow_if_both_operate_l_min": 12,
            "maximum_coolant_C": 50, "rotor_airflow_required": True,
            "hoses_pump_chiller_airflow_duct_terminal_protection": "positive count/mass/space unknown; HOLD",
            "power_and_control_wiring": "positive flexible lengths, bends, clamps and connectors unknown; HOLD",
            "body service stock": "retained exactly by parent reference; no stretch or delete"},
        "installed_mass_cost_bounds": {
            "motors_per_bogie": 2, "catalogue_mass_claim_kg_each": 22.3,
            "catalogue_mass_claim_subtotal_kg_per_bogie": 44.6,
            "mass_claim_status": "vendor source bytes and exact variant frozen status pending",
            "gears_shafts_bearings_case_coupling_oil_mounts_wiring_cooling_fasteners":
                "unknown positive installed mass/cost; not zero and not covered by the 44.6kg motor subtotal",
            "support_pedestals_emergency_support_anti_lift":
                "unknown positive installed mass/cost; not zero and not covered by gross box envelope",
            "parent brake_suspension_service_and_body_stock":
                "retained by identity reference; mass not recalculated here",
            "subtotal_status": "incomplete installed assembly ledger; HOLD"},
        "drive_geometry": drive,
        "retained_occurrences": {"brakes": "preserve complete parent ledger; not reweighed",
            "suspension": "preserve complete parent ledger; not reweighed",
            "services": "preserve complete parent ledger; not reweighed",
            "new_components_per_bogie": {"gears": 4, "new_shafts": 2,
                "retained_wheelset_shafts": 1, "positive_new_gear_bearing_allowance": 6,
                "motors": 2, "couplings": 2, "case_halves": 2,
                "seals": 4, "oil": "positive quantity/mass/cost unknown; HOLD",
                "drain_fill_breather": "positive quantities/mass/cost unknown; HOLD",
                "torque_reaction_joint_bolts": 4,
                "cradle_bolts_nuts_washers": "unknown positive retained joint stack; HOLD",
                "slides": 0, "stops": "positive count/retention unspecified; HOLD",
                "all component masses and costs": "unknown, retain as positive unresolved allowances"},
            "positive_support_reserve": "24 100mm gross-box pedestals plus additional positive, unweighed emergency/anti-lift reserve; HOLD"},
        "failure_reasons": holds,
        "invalidated_downstream": ["installed mass", "body/underframe fit", "braking", "service and cooling", "CAD/BIM", "procurement", "civil interfaces", "cost/lifecycle", "controls", "release"],
        "resource_limits": p["limits"],
        "limitations": ["Phase 1 necessary-space bound only", "No CAD/FEM/native/downloads",
                        "No actual component installation acceptance", "No claim of pilot closure"]}
    result["result_id"] = identity(result)
    return result


def evaluate_all():
    p = load_policy()
    return [evaluate_variant(v["variant_id"]) for v in p["variants"]]

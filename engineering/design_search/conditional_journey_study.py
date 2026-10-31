"""Candidate-bound, assumption-only journeys kept outside operating evidence.

The map is generated from explicit low/base/high hypotheses and sent through
the existing reduced longitudinal method with its synthetic-method opt-in.
Every nested result remains test-only and has no available-motor-map identity.
"""
from __future__ import annotations

from copy import deepcopy
from itertools import product
import gzip
import json
from pathlib import Path
import tomllib

from engineering.station_rail import ROOT, braking
from engineering.station_rail.common import digest, encoded, identity
from . import railway_campaign, railway_bundle, system_motion, model_cost

PRODUCER = "engineering/design_search/conditional_journey_study.py"
CONFIG = "campaigns/conditional-journey-design-study.toml"
OUTPUT = "build/conditional-journey-study"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, physical_journey_completed=False)


def specification(root=ROOT):
    root = Path(root)
    value = tomllib.loads((root / CONFIG).read_text())
    if value.get("schema") != "osr-conditional-journey-design-study/1":
        raise ValueError("Unexpected conditional-journey study schema")
    if value.get("candidate_family") != "P1" or value.get("load_case") != "normal":
        raise ValueError("This study is fixed to normal-load P1 reference candidates")
    if value.get("grade_up_fraction") != 0 or value.get("headwind_m_s") != 0:
        raise ValueError("The current study contract is level, zero-headwind only")
    if (value.get("service") != dict(seats_per_car=44, wheelchair_places_per_car=2,
                                      target_headway_s=120.0, dwell_s=35.0)
            or value.get("lim_assumptions", {}).get("case_names") != ["low", "base", "high"]):
        raise ValueError("Study service or sensitivity case definitions changed")
    lim = value["lim_assumptions"]
    thermal = value["thermal_assumptions"]
    for key in ("peak_force_N_per_car", "peak_current_A_train", "rated_efficiency", "current_slew_A_s"):
        if len(lim.get(key, [])) != 3:
            raise ValueError("Low/base/high LIM assumption triplets are required")
    for key in ("capacity_J_K", "heat_rejection_W_K"):
        if len(thermal.get(key, [])) != 3:
            raise ValueError("Low/base/high thermal assumption triplets are required")
    if (any(x <= 0 for x in lim["peak_force_N_per_car"] + lim["peak_current_A_train"]
            + lim["current_slew_A_s"] + thermal["capacity_J_K"])
            or any(not 0 < x <= 1 for x in lim["rated_efficiency"])
            or any(x < 0 for x in thermal["heat_rejection_W_K"])):
        raise ValueError("LIM and thermal assumptions must be finite and physically bounded")
    value["assumption_id"] = identity(value)
    value["config_sha256"] = digest(root / CONFIG)
    return value


def _campaign(root):
    from . import railway_publication
    folder, value = railway_publication.current(root)
    bundles = [b for b in value["bundles"] if b.get("family_id") == "P1"]
    bodies = {b["candidate_id"] for b in value["bodies"]}
    per_body={body_id:0 for body_id in bodies}
    for bundle in bundles:per_body[bundle["body_candidate_id"]]=per_body.get(bundle["body_candidate_id"],0)+1
    if ({b["body_candidate_id"] for b in bundles} != bodies
            or any(count != 2 for count in per_body.values())):
        raise ValueError("Current campaign must retain two separate canonical P1 motor definitions per body")
    for bundle in bundles:
        railway_bundle.validate(bundle)
        req = bundle["architecture_case"]["requirements"]
        if (bundle["cars"] != 6 or req.get("speed_cap_m_s") != 20.0
                or req.get("acceleration_m_s2") != 0.4 or req.get("target_headway_s") != 120.0
                or bundle["architecture_case"]["physical_definition"]["route"]["station_spacing_m"] != 2000.0):
            raise ValueError("P1 comparison no longer shares the current 6-car / 2-km requirements")
    return folder, value, bundles


def _current_fraction(bundle, assumptions):
    case = bundle["architecture_case"]
    req = case["requirements"]
    mass = bundle["mass"]["accounted_cap_loaded_kg_per_car"]
    rotating = bundle["rotating_equivalent_kg_per_car"]
    drag0 = mass * braking.G * assumptions["rolling_coefficient"] + assumptions["bearing_N_per_car"]
    required = (mass + rotating) * req["acceleration_m_s2"] + drag0
    fraction = required / assumptions["lim_assumptions"]["peak_force_N_per_car"][1]
    if not 0 < fraction < 1:
        raise ValueError("Base assumed LIM force cannot reach the declared initial acceleration at this current fraction")
    return required, fraction


def _scenario(bundle, assumptions, current_command_A, brake_start_m):
    route = bundle["architecture_case"]["physical_definition"]["route"]
    req = bundle["architecture_case"]["requirements"]
    return system_motion.scenario(bundle, dict(
        distance_m=route["station_spacing_m"],
        powered_windows=deepcopy(bundle["architecture_case"]["commanded_power_windows_m"]),
        speed_cap_m_s=req["speed_cap_m_s"], acceleration_m_s2=req["acceleration_m_s2"],
        deceleration_m_s2=assumptions["brake_assumptions"]["service_deceleration_m_s2"],
        load="normal", grade_up_fraction=assumptions["grade_up_fraction"],
        headwind_m_s=assumptions["headwind_m_s"], dt_s=assumptions["dt_s"],
        maximum_time_s=assumptions["maximum_time_s"],
        current_command_A=current_command_A, initial_current_A=current_command_A,
        brake_start_m=brake_start_m, rail_adhesion=assumptions["rail_adhesion_hypothesis"],
        available_discs=assumptions["available_discs"],
        berth_tolerance_m=assumptions["berth_tolerance_m"],
        rolling_coefficient=assumptions["rolling_coefficient"],
        bearing_N_per_car=assumptions["bearing_N_per_car"],
        aero_N_s2_m2_per_car=assumptions["aero_N_s2_m2_per_car"]
    ))


def _map(bundle, scenario, assumptions, case_index):
    lim = assumptions["lim_assumptions"]
    thermal = assumptions["thermal_assumptions"]
    route = scenario["distance_m"]
    speed_cap = scenario["speed_cap_m_s"]
    current_limit = lim["peak_current_A_train"][case_index]
    peak_force = lim["peak_force_N_per_car"][case_index] * bundle["cars"]
    efficiency = lim["rated_efficiency"][case_index]
    axes = dict(position_m=[-assumptions["position_lower_guard_m"], route],
                speed_m_s=[0.0, speed_cap * assumptions["speed_domain_multiplier"]],
                current_A=[0.0, current_limit], temperature_C=[thermal["ambient_C"], thermal["maximum_C"]])
    samples = []
    maximum_input=peak_force*axes["speed_m_s"][-1]*(1.0/efficiency-1.0)
    maximum_input+=peak_force*assumptions["standstill_loss_equivalent_speed_m_s"]
    maximum_input+=peak_force*axes["speed_m_s"][-1]
    rated_voltage=maximum_input/current_limit
    for position, speed, current, temperature in product(*(axes[name] for name in system_motion.AXES)):
        force = peak_force * current / current_limit
        mechanical = force * speed
        loss = mechanical * (1.0 / efficiency - 1.0) + force * assumptions["standstill_loss_equivalent_speed_m_s"]
        electrical = mechanical + loss
        voltage = rated_voltage
        samples.append(dict(position_m=position, speed_m_s=speed, current_A=current,
            temperature_C=temperature, thrust_N_train=force, electrical_input_W_train=electrical,
            loss_W_train=loss, voltage_V=voltage, vertical_force_N_train=0.0))
    standstill_force=peak_force*scenario["initial_current_A"]/current_limit
    prelaunch_loss=standstill_force*assumptions["standstill_loss_equivalent_speed_m_s"]
    prelaunch_energy=prelaunch_loss*assumptions["prelaunch_excitation_s"]
    initial_temperature=thermal["initial_C"]+prelaunch_energy/thermal["capacity_J_K"][case_index]
    value = dict(schema="osr-station-available-force-map/1", candidate_id=bundle["candidate_id"],
        motor_component_id=bundle["propulsion_component_id"], scenario_id=scenario["scenario_id"],
        evidence_kind="synthetic-method-test", model_family="declared-assumption-design-study",
        powered_windows=deepcopy(scenario["powered_windows"]), axes=axes, samples=samples,
        thermal_model=dict(capacity_J_K=thermal["capacity_J_K"][case_index],
            ambient_C=thermal["ambient_C"], initial_C=initial_temperature,
            maximum_C=thermal["maximum_C"], heat_rejection_W_K=thermal["heat_rejection_W_K"][case_index]),
        electrical_limits=dict(maximum_voltage_V=lim["voltage_limit_V"], maximum_current_A=current_limit,
            current_slew_A_s=lim["current_slew_A_s"][case_index]),
        assumption_id=assumptions["assumption_id"], assumption_source_sha256=assumptions["config_sha256"])
    value["evaluation_id"] = identity(value)
    prelaunch=dict(duration_s=assumptions["prelaunch_excitation_s"],current_A=scenario["initial_current_A"],
        electrical_energy_J=prelaunch_energy,motor_loss_energy_J=prelaunch_loss*assumptions["prelaunch_excitation_s"],
        temperature_after_C=initial_temperature,
        basis="Constant-current stationary pre-excitation for the declared duration; included as an energy/initial-temperature assumption, not a measured startup sequence.")
    return value,prelaunch


def _trial(bundle, assumptions, case_index, current_fraction, brake_start_m):
    current_limit = assumptions["lim_assumptions"]["peak_current_A_train"][case_index]
    current_command = current_fraction * current_limit
    scenario = _scenario(bundle, assumptions, current_command, brake_start_m)
    force_map, prelaunch = _map(bundle, scenario, assumptions, case_index)
    result = system_motion.forward(bundle, force_map, scenario, allow_synthetic=True)
    if (result.get("test_only") is not True or result.get("available_motor_map_id") is not None
            or result.get("physical_journey_completed") is not False):
        raise ValueError("Conditional maps must remain test-only and cannot become available force")
    result["method_result_id"] = identity(result)
    return dict(scenario=scenario, force_map=force_map, prelaunch=prelaunch, forward=result)


def _fit_berth(bundle, assumptions, case_index, current_fraction):
    distance = bundle["architecture_case"]["physical_definition"]["route"]["station_spacing_m"]
    speed = bundle["architecture_case"]["requirements"]["speed_cap_m_s"]
    decel = assumptions["brake_assumptions"]["service_deceleration_m_s2"]
    low = max(0.0, distance - speed * speed / (2.0 * decel) - assumptions["brake_assumptions"]["brake_start_lower_margin_m"])
    high = distance - 1.0
    attempts = []
    final = None
    for _ in range(assumptions["brake_search_max_iterations"]):
        brake_start = (low + high) / 2.0
        final = _trial(bundle, assumptions, case_index, current_fraction, brake_start)
        motion = final["forward"]
        attempts.append(dict(brake_start_m=brake_start, state=motion.get("state"),
            final_position_m=motion.get("final_position_m"), final_speed_m_s=motion.get("final_speed_m_s"),
            predicted_stop_within_berth=motion.get("predicted_stop_within_berth")))
        if motion.get("predicted_stop_within_berth") is True:
            return final, attempts, "brake-start-fitted-to-berth-hypothesis"
        if motion.get("execution") != "completed-method-test":
            return final, attempts, "conditional-journey-method-did-not-complete"
        if motion.get("state") == "stopped" and motion.get("final_speed_m_s", 1.0) <= 1e-7:
            low = brake_start
        elif motion.get("state") == "destination-boundary" and motion.get("final_speed_m_s", 0.0) > 1e-7:
            high = brake_start
        else:
            return final, attempts, "brake-fit-held-by-controller-or-operating-limit"
    return final, attempts, "brake-fit-budget-exhausted"


def _trajectory_summary(result,prelaunch):
    trace = result.get("trace", [])
    accelerations = []
    previous_time = 0.0
    previous_speed = 0.0
    for row in trace:
        dt = row["time_s"] - previous_time
        if dt > 0:
            accelerations.append((row["speed_m_s"] - previous_speed) / dt)
        previous_time, previous_speed = row["time_s"], row["speed_m_s"]
    return dict(state=result.get("state"), elapsed_s=result.get("elapsed_s"),
        final_position_m=result.get("final_position_m"), final_speed_m_s=result.get("final_speed_m_s"),
        berth_stop=result.get("predicted_stop_within_berth"), temperature_C=result.get("temperature_C"),
        peak_current_A=max((r["current_A"] for r in trace), default=0.0),
        peak_thrust_N_train=max((r["thrust_N_train"] for r in trace), default=0.0),
        peak_electrical_input_W_train=max((r["electrical_input_W_train"] for r in trace), default=0.0),
        maximum_positive_acceleration_m_s2=max((a for a in accelerations if a > 0), default=0.0),
        minimum_acceleration_m_s2=min(accelerations, default=0.0),
        moving_electrical_energy_J=result.get("electrical_energy_J"),
        prelaunch_electrical_energy_J=prelaunch["electrical_energy_J"],
        total_conditional_electrical_energy_J=(result.get("electrical_energy_J",0.0)+prelaunch["electrical_energy_J"]),
        mechanical_propulsion_work_J=result.get("mechanical_propulsion_work_J"),
        moving_motor_loss_energy_J=result.get("magnetic_loss_energy_J"),
        prelaunch_motor_loss_energy_J=prelaunch["motor_loss_energy_J"],
        total_conditional_motor_loss_energy_J=(result.get("magnetic_loss_energy_J",0.0)+prelaunch["motor_loss_energy_J"]),
        brake_heat_J=result.get("friction_brake_heat_J"),
        energy_residual_J=result.get("energy_residual_J"),
        electrical_work_residual_J=result.get("electrical_work_residual_J"),
        maximum_speed_m_s=max((r["speed_m_s"] for r in trace), default=0.0))


def evaluate_bundle(bundle, assumptions):
    railway_bundle.validate(bundle)
    if bundle.get("family_id") != "P1":
        raise ValueError("Conditional LIM study accepts only the candidate's canonical P1 bundle")
    required_force, current_fraction = _current_fraction(bundle, assumptions)
    cases = []
    lim = assumptions["lim_assumptions"]
    thermal = assumptions["thermal_assumptions"]
    for i, name in enumerate(lim["case_names"]):
        trial, search, fit_state = _fit_berth(bundle, assumptions, i, current_fraction)
        motion = trial["forward"]
        cases.append(dict(case=name, assumption=dict(peak_force_N_per_car=lim["peak_force_N_per_car"][i],
            peak_current_A_train=lim["peak_current_A_train"][i], current_command_A=current_fraction*lim["peak_current_A_train"][i],
            current_fraction=current_fraction, rated_efficiency=lim["rated_efficiency"][i],
            current_slew_A_s=lim["current_slew_A_s"][i], thermal_capacity_J_K=thermal["capacity_J_K"][i],
            heat_rejection_W_K=thermal["heat_rejection_W_K"][i]),
            map_id=trial["force_map"]["evaluation_id"], force_map=trial["force_map"], scenario=trial["scenario"],
            prelaunch=trial["prelaunch"],forward=motion, trajectory_summary=_trajectory_summary(motion,trial["prelaunch"]),
            brake_start_search=search, brake_fit_state=fit_state,
            physical_journey_completed=False, available_motor_map_id=None, test_only=True))
    req=bundle["architecture_case"]["requirements"]
    service=assumptions["service"]
    places_per_car=service["seats_per_car"]+service["wheelchair_places_per_car"]
    places_per_train=places_per_car*bundle["cars"]
    places_per_hour=places_per_train*3600.0/service["target_headway_s"]
    result=dict(schema="osr-conditional-journey-candidate/1",candidate_id=bundle["candidate_id"],
        body_candidate_id=bundle["body_candidate_id"],bundle_id=bundle["candidate_id"],
        bundle_definition_id=bundle["definition_id"],requirement_revision=bundle["requirement_revision"],
        normal_accounted_mass_kg_per_car=bundle["mass"]["accounted_cap_loaded_kg_per_car"],
        rotating_equivalent_kg_per_car=bundle["rotating_equivalent_kg_per_car"],
        initial_force_for_target_acceleration_N_per_car=required_force,
        assumed_current_fraction_of_base_limit=current_fraction,
        powered_windows_m=deepcopy(bundle["architecture_case"]["commanded_power_windows_m"]),
        service_capacity_arithmetic=dict(seats_per_car=service["seats_per_car"],
            wheelchair_places_per_car=service["wheelchair_places_per_car"],cars=bundle["cars"],
            places_per_car=places_per_car,places_per_train=places_per_train,
            target_headway_s=service["target_headway_s"],dwell_s=service["dwell_s"],
            arithmetic_places_per_hour_direction=places_per_hour,
            requirement_places_per_hour_direction=req["capacity_pphpd"],
            headway_and_capacity_physically_demonstrated=False,
            scope="Capacity arithmetic only; this point-train journey does not model tail clearance, station occupation, protected headway or fleet sizing."),
        cases=cases,design_study_complete=True,journey_results_assumption_only=True,
        engineering_validated=False,approved_for_manufacture_or_operation=False,**FLAGS)
    if abs(places_per_hour-req["capacity_pphpd"])>1e-8:
        raise ValueError("Seat/wheelchair/headway arithmetic differs from the current baseline requirement")
    result["evaluation_id"]=identity(result)
    return result


def _sources(root, parent):
    root=Path(root)
    names={PRODUCER: digest(root/PRODUCER), CONFIG: digest(root/CONFIG),
        system_motion.PRODUCER: digest(root/system_motion.PRODUCER),
        railway_bundle.PRODUCER: digest(root/railway_bundle.PRODUCER),
        model_cost.PRODUCER: digest(root/model_cost.PRODUCER)}
    if any(digest(root/n)!=h for n,h in parent["source_sha256"].items()):
        raise ValueError("Current railway campaign source epoch changed before conditional study")
    return {**parent["source_sha256"], **names}


def run(root=ROOT):
    root=Path(root)
    from . import railway_publication
    parent_folder, parent=railway_publication.current(root)
    assumptions=specification(root)
    _, _, bundles=_campaign(root)
    sources=_sources(root,parent)
    contract=dict(schema="osr-conditional-journey-study-contract/1",parent_campaign_id=parent["campaign_id"],
        parent_contract_id=parent["contract_id"],parent_run_id=parent["run_id"],
        parent_result_sha256=digest(parent_folder/"result.json"),assumption_id=assumptions["assumption_id"],
        bundle_ids=[b["candidate_id"] for b in bundles],source_sha256=sources)
    study_id=identity(contract)
    folder=root/OUTPUT/study_id
    result_path=folder/"result.json"
    if result_path.is_file():
        return verify(root, study_id=study_id, replay=False)
    folder.mkdir(parents=True, exist_ok=True)
    rows=[]
    for bundle in bundles:
        if _sources(root,parent)!=sources:
            raise ValueError("Conditional journey source epoch changed during evaluation")
        output=evaluate_bundle(bundle,assumptions)
        record=dict(bundle_id=bundle["candidate_id"],bundle_definition_id=bundle["definition_id"],output=output)
        record["record_id"]=identity(record)
        rows.append(record)
        (folder/(bundle["candidate_id"]+".json.gz")).write_bytes(gzip.compress(encoded(record),mtime=0))
    cost_assumptions=model_cost.assumptions(root)
    result=dict(schema="osr-conditional-journey-study-result/1",study_id=study_id,contract=contract,
        row_count=len(rows),rows=rows,source_sha256=sources,
        service_shift_context=dict(production_shifts_per_day=cost_assumptions["production_shifts_per_day"],
            production_hours_per_shift=cost_assumptions["production_hours_per_shift"],
            civil_shifts_per_day=cost_assumptions["civil_shifts_per_day"],
            civil_hours_per_shift=cost_assumptions["civil_hours_per_shift"],
            operating_hours_per_day_cases=cost_assumptions["operating_hours_per_day_cases"],
            operations_shifts_per_day_cases=cost_assumptions["operations_shifts_per_day_cases"],
            operations_hours_per_shift_cases=cost_assumptions["operations_hours_per_shift_cases"],
            cost_assumption_id=identity(cost_assumptions),
            note="These cost-model shift scenarios are carried forward as economic assumptions; the journey model does not validate operating hours or staffing."),
        open_limitations=["No measured or validated LIM force map; all maps are declared assumptions",
            "No repeated 120-second thermal duty, charging, auxiliary load or rescue simulation",
            "No adverse grade/headwind, crowd load or failed-launch scenario in this baseline study",
            "Point-train motion does not prove tail clearance, dwell, protected headway, station occupation or fleet size",
            "Brake and adhesion response are unqualified model hypotheses",
            "Candidate mass remains an accounted hypothesis; complete installed mass is unknown"],
        completion=dict(conditional_design_study_cases=len(rows)*3,canonical_P1_bundles=len(bundles),
            candidate_design_study_complete=True,physical_journeys=0,engineering_validated=0,
            approved_for_manufacture_or_operation=0), **FLAGS)
    result["result_sha256"]=identity(result)
    result_path.write_bytes(encoded(result))
    return verify(root, study_id=study_id, replay=False)


def verify(root=ROOT, *, study_id=None, replay=True):
    root=Path(root)
    if study_id is None:
        paths=sorted((root/OUTPUT).glob("*/result.json"))
        if len(paths)!=1:raise ValueError("Specify the exact conditional journey study identity")
        path=paths[0];study_id=path.parent.name
    else:path=root/OUTPUT/study_id/"result.json"
    result=json.loads(path.read_bytes())
    from . import railway_publication
    parent_folder,parent=railway_publication.current(root)
    assumptions=specification(root)
    _,_,bundles=_campaign(root)
    sources=_sources(root,parent)
    contract=dict(schema="osr-conditional-journey-study-contract/1",parent_campaign_id=parent["campaign_id"],
        parent_contract_id=parent["contract_id"],parent_run_id=parent["run_id"],
        parent_result_sha256=digest(parent_folder/"result.json"),assumption_id=assumptions["assumption_id"],
        bundle_ids=[b["candidate_id"] for b in bundles],source_sha256=sources)
    if (study_id!=identity(contract) or result.get("study_id")!=study_id
            or result.get("contract")!=contract or result.get("source_sha256")!=sources
            or result.get("result_sha256")!=identity({k:v for k,v in result.items() if k!="result_sha256"})
            or len(result.get("rows",[]))!=len(bundles)
            or result.get("row_count")!=len(bundles)):
        raise ValueError("Conditional journey study receipt, source epoch or parent identity differs")
    expected={b["candidate_id"]:b for b in bundles}
    seen=set()
    for row in result["rows"]:
        bundle_id=row["bundle_id"]
        if bundle_id in seen or bundle_id not in expected:raise ValueError("Conditional study mixes or duplicates candidates")
        seen.add(bundle_id)
        if row.get("record_id")!=identity({k:v for k,v in row.items() if k!="record_id"}):
            raise ValueError("Conditional study candidate row receipt differs")
        raw_path=path.parent/(bundle_id+".json.gz")
        if json.loads(gzip.decompress(raw_path.read_bytes()))!=row:raise ValueError("Conditional study candidate record differs")
        bundle=expected[bundle_id]
        if row["bundle_definition_id"]!=bundle["definition_id"]:
            raise ValueError("Conditional journey row uses a different canonical bundle definition")
        output=row.get("output",{})
        if (output.get("evaluation_id")!=identity({k:v for k,v in output.items() if k!="evaluation_id"})
                or output.get("candidate_id")!=bundle_id
                or output.get("body_candidate_id")!=bundle["body_candidate_id"]
                or output.get("bundle_definition_id")!=bundle["definition_id"]
                or len(output.get("cases",[]))!=3):
            raise ValueError("Conditional output identity or candidate bundle differs")
        if replay and row["output"]!=evaluate_bundle(bundle,assumptions):
            raise ValueError("Conditional journey did not replay from the exact canonical candidate and assumptions")
        for case in row["output"]["cases"]:
            force_map=case.get("force_map",{})
            scenario=case.get("scenario",{});forward=case.get("forward",{})
            if (scenario.get("scenario_id")!=identity({k:v for k,v in scenario.items() if k!="scenario_id"})
                    or forward.get("method_result_id")!=identity({k:v for k,v in forward.items() if k!="method_result_id"})
                    or force_map.get("evaluation_id")!=identity({k:v for k,v in force_map.items() if k!="evaluation_id"})
                    or force_map.get("candidate_id")!=bundle_id
                    or force_map.get("motor_component_id")!=bundle["propulsion_component_id"]
                    or force_map.get("assumption_id")!=assumptions["assumption_id"]
                    or force_map.get("scenario_id")!=scenario.get("scenario_id")):
                raise ValueError("Conditional map identity, candidate or assumptions differ")
        if (row["output"].get("physical_journey_completed") is not False
                or any(c["forward"].get("test_only") is not True
                    or c["forward"].get("available_motor_map_id") is not None
                    or c["forward"].get("physical_journey_completed") is not False
                    for c in row["output"]["cases"])):
            raise ValueError("Assumption-only journey promoted synthetic force to available physical propulsion")
    if any(result.get(k) is not False for k in FLAGS):
        raise ValueError("Conditional journey cannot change physical acceptance or release")
    return dict(verified=True,study_id=study_id,candidate_count=len(bundles),
        conditional_design_study_cases=len(bundles)*3,physical_journeys=0,
        engineering_validated=0,approved_for_manufacture_or_operation=0,**FLAGS)

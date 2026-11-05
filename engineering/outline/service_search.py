"""Bounded demand-driven service screening with separate evidence maturity.

Seed values are revisable hypotheses. Transport demand, journey and reliability
targets are the declared planning obligations; no headway is universal here.
"""
from copy import deepcopy
from math import ceil, floor, isfinite, prod
from pathlib import Path

from engineering.station_rail import ROOT, braking, electrical, operations
from engineering.station_rail import common
from engineering.design_search import compact_launch, line_benchmark_service as service_model

PRODUCER = "engineering/outline/service_search.py"
MODES = ("cable-capstan", "common-drive-rollers", "compact-launch-LIM")
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    installed_mass_complete=False, manufacturing_release=False,
    operating_release=False, physical_journey_completed=False,
    selected_reference_changed=False, movement_authority=False)
_MODULES = (service_model, compact_launch, braking, electrical, operations, common)
_LOADED = {PRODUCER: common.digest(__file__), **{
    Path(module.__file__).resolve().relative_to(Path(ROOT).resolve()).as_posix(): common.digest(module.__file__)
    for module in _MODULES}}
_LOADED.update({name:common.digest(Path(ROOT)/name) for name in (
    "engineering/design_search/line_benchmark.py", "engineering/design_search/line_benchmark_civil.py")})


def _positive(value, name, *, zero=False, fraction=False):
    if (type(value) not in (int,float) or not isfinite(value)
            or (value < 0 if zero else value <= 0) or fraction and value > 1):
        raise ValueError("Finite " + ("nonnegative " if zero else "positive ") + name + " required")
    return value


def _sources(root, vehicle):
    root = Path(root)
    sources = dict(vehicle["source_sha256"])
    for name,sha in _LOADED.items():
        if name in sources and sources[name] != sha:
            raise ValueError("Vehicle and loaded source epochs conflict: " + name)
        sources[name] = sha
    if any(common.digest(root/name) != sha for name,sha in sources.items()):
        raise ValueError("Loaded service-search sources or vehicle source epoch changed")
    return dict(sorted(sources.items()))


def _domain(variables, name, maximum, *, empty=False):
    values = variables[name]
    if not isinstance(values,list) or not (0 if empty else 1) <= len(values) <= maximum:
        raise ValueError("Bounded seed list required: " + name)
    for value in values:
        _positive(value,name)
    return sorted(set(values))


def _project_headway(prepared, requirements):
    """Only headway-dependent accounting changes; all physical profiles remain."""
    result = deepcopy(prepared)
    r = deepcopy(requirements); h = r["headway_s"]; fraction = result["design"]["reserve_fraction"]
    result["requirements"] = r
    for prefix, cycle in (("", result["round_trip_s"]),
            ("minimum_unpadded_", result["minimum_unpadded_round_trip_s"])):
        active = ceil(cycle/h) if cycle is not None else None
        spare = ceil(active*fraction) if active is not None else None
        result[prefix+"active_trainsets"] = active
        result[prefix+"spare_trainsets"] = spare
        result[prefix+"total_trainsets"] = active+spare if active is not None else None
    result["totalcars"] = result["total_trainsets"]*r["cars_per_train"] if result["total_trainsets"] is not None else None
    result["capacity_pphpd"] = result["normal_places_per_train"]*3600/h
    result["fixed_seats_pphpd"] = r["cars_per_train"]*r["fixed_seats_per_car"]*3600/h
    result["wheelchair_places_pphpd"] = r["cars_per_train"]*r["wheelchair_places_per_car"]*3600/h
    result["train_km_per_day"] = 2*3600/h*r["operating_hours_per_day"]*r["route_km"]
    positions = max(1,ceil(result["design"]["terminal_turnback_s"]/h))
    result["minimum_turnback_positions_per_end"] = positions
    result["terminal_additional_positions"] = 2*(positions-1)
    resource = result["berth_resource_s"]
    result["berth_headway_necessary_screen"] = "pass" if resource is not None and resource<=h else "fail"
    result.pop("evaluation_id")
    result["evaluation_id"] = common.identity(result)
    return result


def _terminal_resources(service, headway):
    p = service["jerk_timing_profile"]
    brake = p["braking_time_s"] if service["jerk_timing_model_valid"] else None
    departure = service["tail_clearance_s_jerk_bound"]
    turnback = service["design"]["terminal_turnback_s"]
    resource = turnback+brake+departure if brake is not None else None
    positions = max(1,ceil(resource/headway)) if resource is not None else None
    return dict(turnback_s=turnback,approach_braking_s=brake,departure_tail_clearance_s=departure,
        conservative_serial_resource_s=resource,
        turnback_only_positions_per_end=service["minimum_turnback_positions_per_end"],
        planning_positions_per_end=positions,baseline_budget_positions_per_end=2,
        cost_additional_positions=2*max(0,positions-2) if positions is not None else None,
        basis="Turnback plus approach and full-tail departure bound for a parallel resource envelope; two terminal boarding positions/end are already budgeted.",
        shared_throat_conflict_free=None,platform_door_orientation_verified=False,
        actual_turnback_or_headway_qualified=False,
        limitation="Parallel platforms alone do not prove independent protected approaches, departures or signalling headway")


def _mode_screens(service, baseline_spec, headway, modes):
    rotary = baseline_spec["rotary"]
    for key in ("return_speed_m_s","coupling_reset_s"):
        _positive(rotary[key],key,zero=(key=="coupling_reset_s"))
    cycle = (service["jerk_bound"]["total_time_s"]
        + service["jerk_launch_distance_m"]/rotary["return_speed_m_s"]+rotary["coupling_reset_s"])
    result = {}
    for mode in modes:
        status = "unknown" if mode not in MODES else "pass"
        reasons = ["No cost/contact evaluator is declared for this mechanism"] if status=="unknown" else []
        if mode=="cable-capstan" and cycle>headway:
            status="fail";reasons=["One cable-launch resource cannot complete launch, return and reset within the proposed headway"]
        result[mode] = dict(status=status,reasons=reasons,
            necessary_cable_cycle_s=cycle if mode=="cable-capstan" else None,
            minimum_parallel_launch_resources=ceil(cycle/headway) if mode=="cable-capstan" else None,
            actual_contact_force_and_thermal_duty_qualified=False)
    return result


def screen(brief, variables, baseline_spec, vehicle, root=ROOT):
    """Screen cheap service cases; preserve rejects, unknowns and a bounded cursor."""
    b,v,spec = deepcopy(brief),deepcopy(variables),deepcopy(baseline_spec)
    allowed={'headways_s','speeds_kmh','accelerations_m_s2','service_decelerations_m_s2',
        'jerks_m_s3','dwell_s','headway_quantum_s','maximum_screened','mechanisms','start_index'}
    if not isinstance(v,dict) or set(v)-allowed:
        raise ValueError('Unknown or untyped service design variable')
    for key in ("route_km","maximum_headway_s","maximum_one_way_minutes","operating_hours_per_day"):
        _positive(b[key],key)
    _positive(b["peak_demand_pphpd"],"peak_demand_pphpd",zero=True)
    for key in ("planning_occupancy","availability_target","planning_availability_assumption"):
        _positive(b[key],key,fraction=True)
    if type(b["stations"]) is not int or not 2<=b["stations"]<=100:
        raise ValueError("Two to 100 stations required")
    if b["operating_hours_per_day"]>24 or not isinstance(b.get("demand_source"),str) or not b["demand_source"].strip():
        raise ValueError("Explicit demand source and at most 24 operating hours required")
    limit=v["maximum_screened"]
    if type(limit) is not int or not 1<=limit<=128:
        raise ValueError("Explicit one-to-128 cheap-screen budget required")
    quantum=_positive(v["headway_quantum_s"],"headway_quantum_s")
    headways=_domain(v,"headways_s",64,empty=True)
    speeds=_domain(v,"speeds_kmh",16)
    accelerations=_domain(v,"accelerations_m_s2",16)
    dwells=_domain(v,"dwell_s",8)
    v.setdefault("service_decelerations_m_s2",[spec["design"]["service_deceleration_m_s2"]])
    decelerations=_domain(v,"service_decelerations_m_s2",16)
    v.setdefault("jerks_m_s3",[spec["design"]["jerk_m_s3"]])
    jerks=_domain(v,"jerks_m_s3",16)
    modes=v.get("mechanisms",list(MODES))
    if not isinstance(modes,list) or not 1<=len(modes)<=8 or any(not isinstance(x,str) or not x for x in modes) or len(set(modes))!=len(modes):
        raise ValueError("Bounded unique mechanism names required")
    sources=_sources(root,vehicle)
    if vehicle.get("evaluation_id")!=common.identity({k:x for k,x in vehicle.items() if k!="evaluation_id"}):
        raise ValueError("Vehicle evaluation identity differs")
    vc=vehicle["physical_definition"]["vehicle"]
    places=vc["cars"]*(vc["fixed_seats_per_car"]+vc["wheelchair_places_per_car"])
    capacity_factor=b["planning_occupancy"]*b["planning_availability_assumption"]
    demand_limit=places*3600*capacity_factor/b["peak_demand_pphpd"] if b["peak_demand_pphpd"] else b["maximum_headway_s"]
    derived=floor(min(b["maximum_headway_s"],demand_limit)/quantum)*quantum
    derived=derived if derived>0 else None
    if derived is not None:headways=sorted(set(headways+[derived]))
    if not headways:raise ValueError("No positive headway can be generated at the declared quantum")
    contract=dict(schema="osr-outline-transport-requirements/1",route_km=b["route_km"],stations=b["stations"],
        peak_demand_pphpd=b["peak_demand_pphpd"],demand_source=b["demand_source"],
        maximum_headway_s=b["maximum_headway_s"],maximum_one_way_s=b["maximum_one_way_minutes"]*60,
        operating_hours_per_day=b["operating_hours_per_day"],availability_target=b["availability_target"],
        planning_availability_assumption=b["planning_availability_assumption"],
        planning_availability_assumption_role="Unvalidated planning input; not achieved availability evidence",
        mandatory_passenger_protection_accessibility_and_comfort=True,
        revision_rule="Headway, speed, acceleration, dwell, formation and station arrangement are design hypotheses, not universal transport obligations",
        evidence_scope="Declared planning demand; achieved availability, safe headway and passenger comfort require independent engineering evidence")
    contract["requirements_id"]=common.identity(contract)
    domains=dict(speeds_kmh=speeds,accelerations_m_s2=accelerations,service_decelerations_m_s2=decelerations,jerks_m_s3=jerks,dwell_s=dwells,headways_s=headways)
    arrays=[speeds,accelerations,decelerations,jerks,dwells,headways]
    total=prod(len(x) for x in arrays)
    start=v.get("start_index",0)
    if type(start) is not int or not 0<=start<=total:raise ValueError("Valid continuing screen cursor required")
    def at(index):
        values=[]
        for options in reversed(arrays):
            index,remainder=divmod(index,len(options));values.append(options[remainder])
        return list(reversed(values))
    cases=[];eligible=[];prepared={};projections=0;replays=0
    for index in range(start,min(total,start+limit)):
        speed,acceleration,deceleration,jerk,dwell,headway=at(index)
        r=deepcopy(spec["requirements"]);d=deepcopy(spec["design"])
        r.update(route_km=b["route_km"],stations=b["stations"],headway_s=headway,dwell_s=dwell,
            operating_hours_per_day=b["operating_hours_per_day"],minimum_capacity_pphpd=b["peak_demand_pphpd"])
        d.update(speed_m_s=speed/3.6,acceleration_m_s2=acceleration,service_deceleration_m_s2=deceleration,jerk_m_s3=jerk)
        key=common.identity(dict(requirements={k:x for k,x in r.items() if k!="headway_s"},design=d,
            vehicle_evaluation_id=vehicle["evaluation_id"]))
        if key not in prepared:
            service=service_model.evaluate(r,d,vehicle);prepared[key]=service
        else:
            service=_project_headway(prepared[key],r);projections+=1
        offered=service["capacity_pphpd"]*capacity_factor
        checks=dict(capacity=dict(status="pass" if offered+1e-9>=b["peak_demand_pphpd"] else "fail",
            planning_offered_pphpd=offered,required_pphpd=b["peak_demand_pphpd"]),
            headway=dict(status="pass" if headway<=b["maximum_headway_s"] else "fail"),
            journey=dict(status="unknown" if service["one_way_s"] is None else "pass" if service["one_way_s"]<=contract["maximum_one_way_s"] else "fail"),
            berth=dict(status="unknown" if service["berth_resource_s"] is None else "pass" if service["berth_resource_s"]<=headway else "fail"),
            reliability_assumption=dict(status="pass" if b["planning_availability_assumption"]>=b["availability_target"] else "fail",
                achieved_availability=None,target=b["availability_target"],assumption=b["planning_availability_assumption"]),
            auxiliary_energy=dict(status="unknown" if service["auxiliary"] is None else service["auxiliary"]["energy_balance_screen"]))
        fail=[name for name,row in checks.items() if row["status"]=="fail"]
        unknown=[name for name,row in checks.items() if row["status"]=="unknown"]
        status="fail" if fail else "unknown" if unknown else "pass"
        mechanism_screens=_mode_screens(service,spec,headway,modes)
        allowed=[mode for mode in modes if status=="pass" and mechanism_screens[mode]["status"]=="pass"]
        if allowed:
            replay=service_model.evaluate(r,d,vehicle);replays+=1
            if common.encoded(service)!=common.encoded(replay):
                raise ValueError("Projected service differs from independent frozen-helper replay")
        request=dict(requirements=r,design=d,reference_vehicle_candidate_id=vehicle["candidate_id"],
            reference_vehicle_evaluation_id=vehicle["evaluation_id"])
        unknown_reasons=["Actual force/contact/thermal/braking evidence unavailable",
            "Passenger acceleration, braking jerk and accessibility/comfort acceptance unverified",
            "Achieved service availability and protected headway/terminal conflicts unverified",
            "Actual route grades and site data unknown; recorded uphill-coast failures are conditional model results"]
        case=dict(request=request,service=service,screen_status=status,checks=checks,
            eligible_for_costing=bool(allowed),eligible_mechanisms=allowed,fail_reasons=fail,
            unknown_reasons=unknown+unknown_reasons,mechanism_screens=mechanism_screens,
            terminal_resource_planning=_terminal_resources(service,headway),
            known_model_failures=[dict(profile_id=p["profile_id"],grade_fraction=p["inputs"]["grade_fraction_hypothesis"],
                reason=p["reason"],maximum_coasting_reach_m=p.get("maximum_flat_coast_reach_m"))
                for p in service["grade_sensitivities"] if not p["reachable"]],
            helper_replayed_before_costing=bool(allowed),physical_screen="unknown",**FLAGS)
        case["case_id"]=common.identity(dict(request=request,service_evaluation_id=service["evaluation_id"],
            checks=checks,mechanism_screens=mechanism_screens,requirements_id=contract["requirements_id"],source_sha256=sources))
        case["program_index"]=index;cases.append(case)
        if allowed:eligible.append(case["case_id"])
    stop=start+len(cases)
    pending=[] if stop==total else [dict(kind="remaining-service-screen-region",state="ready",
        next_index=stop,remaining=total-stop,domain_id=common.identity(domains),domains=domains,
        ordering=list(domains),physical_acceptance=False)]
    if _sources(root,vehicle)!=sources:raise ValueError("Service-search source epoch changed")
    value=dict(schema="osr-outline-service-search/1",requirements_contract=contract,requirements_id=contract["requirements_id"],
        assumptions=dict(planning_occupancy=b["planning_occupancy"],planning_availability_assumption=b["planning_availability_assumption"],
            achieved_availability=None,demand_source=b["demand_source"],
            demand_is_authenticated_forecast=False,nominal_route_grade_fraction=0.,surveyed_grade_profile=None,
            assumed_load_scope="Full normal accounted passenger mass retained; occupancy does not reduce vehicle/civil loading",
            headway_seed_list_is_complete_design_space=False,reference_120s_is_universal_obligation=False),
        generation=dict(seed_headways_s=v["headways_s"],demand_derived_headway_limit_s=demand_limit,
            demand_derived_headway_s=derived,headway_quantum_s=quantum,domains=domains,
            start_index=start,stop_index=stop,total_programs=total),
        source_sha256=sources,input_ids=dict(brief_id=common.identity(b),variables_id=common.identity(v),
            baseline_spec_id=common.identity(spec),vehicle_evaluation_id=vehicle["evaluation_id"]),
        cases=cases,eligible_for_costingIDs=eligible,pending=pending,
        counters=dict(screened=len(cases),eligible_for_costing=len(eligible),rejected=sum(c["screen_status"]=="fail" for c in cases),
            unknown=sum(c["screen_status"]=="unknown" for c in cases),physical_profiles_prepared=len(prepared),
            headway_projections_reused=projections,independent_helper_replays=replays,
            total_helper_evaluations=len(prepared)+replays,native_solver_jobs=0,CAD_jobs=0),
        completion_scope="Declared provisional service screening and cost eligibility only; no physical qualification or timetable authority",**FLAGS)
    value["evaluation_id"]=common.identity(value)
    return value

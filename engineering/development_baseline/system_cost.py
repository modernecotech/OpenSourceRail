"""Class C whole-system cost scenario for the exact selected v0.6 vehicle.

The scenario uses the selected vehicle's occurrence/account inventory with a
separate 6 km synthetic route evaluation. Estimated costs complete the declared
financial scope only; no site, motor-map, journey, acceptance or release result
is implied.
"""
from copy import deepcopy
from math import ceil, fsum, sqrt
from pathlib import Path

from engineering import mass_ledger_audit
from engineering.design_search import model_cost, railway_bundle, selected_reference_journey, system_motion
from engineering.station_rail import ROOT, station_motor, vehicle as selected_vehicle
from engineering.station_rail.common import digest, identity
from engineering.development_baseline import selection

PRODUCER = "engineering/development_baseline/system_cost.py"
FLAGS = dict(
    engineering_accepted=False,
    physical_accepted=False,
    installed_mass_complete=False,
    manufacturing_release=False,
    operating_release=False,
)
IDS = ("candidate_id", "body_candidate_id", "support_component_id", "propulsion_component_id")


def sources(root=ROOT):
    root = Path(root)
    names = (
        PRODUCER,
        "engineering/development_baseline/selection.py",
        "engineering/development_baseline/vehicle_cost.py",
        "engineering/design_search/model_cost.py",
        "engineering/design_search/railway_bundle.py",
        "engineering/design_search/railway_architecture.py",
        "engineering/design_search/selected_reference_journey.py",
        "engineering/design_search/system_motion.py",
        "engineering/mass_ledger_audit.py",
        "engineering/station_rail/brief.toml",
        "engineering/station_rail/civil.py",
        "engineering/station_rail/common.py",
        "engineering/station_rail/evaluation.py",
        "engineering/station_rail/station_motor.py",
        "engineering/station_rail/vehicle.py",
        model_cost.RATE_DATA,
    )
    return {name: digest(root / name) for name in names}


def _inventory(bundle, candidate, ledger, vehicle_cost_record):
    rows = []
    for occurrence in ledger["candidate_geometry_occurrences"]:
        mass = float(occurrence["mass_kg"])
        if mass <= 1e-12:
            continue
        rows.append(dict(
            id=occurrence["occurrence_id"],
            candidate_id=bundle["candidate_id"],
            body_candidate_id=bundle["body_candidate_id"],
            scope="located-nominal-gross-body-stock",
            accounted_mass_kg=mass,
            material_id=occurrence.get("material") or "generic",
            component_definition_id=identity(occurrence),
            source_occurrence_id=occurrence["occurrence_id"],
        ))

    account_ids = {}
    for account in ledger["accounts"]:
        residual = float(account["residual_account_mass_kg"])
        if residual <= 1e-9:
            continue
        account_id = str(account["account_id"])
        row_id = ("selected-service-battery-and-services" if account_id == "services"
                  else "selected-account/" + account_id)
        account_ids[account_id] = row_id
        rows.append(dict(
            id=row_id,
            candidate_id=bundle["candidate_id"],
            body_candidate_id=bundle["body_candidate_id"],
            scope="retained-unlocated-reference-account",
            accounted_mass_kg=residual,
            material_id="finished-equipment",
            component_definition_id=identity(account),
            source_account_id=account_id,
            source_occurrence_ids=account["source_occurrence_ids"],
        ))

    cost_lines = vehicle_cost_record.get("lines")
    if not isinstance(cost_lines, list):
        raise ValueError("Selected vehicle cost lines are required to derive process families")
    operations = {}
    for line in cost_lines:
        if line.get("stage") != "factory-gate" or not line.get("process_template"):
            continue
        process = str(line["process_template"])
        operations.setdefault(process, []).append(line["line_id"])
    manufacturing = [dict(
        id="selected-process-family/" + identity(process)[:16],
        candidate_id=bundle["candidate_id"],
        body_candidate_id=bundle["body_candidate_id"],
        process_candidates=[process],
        source_cost_line_ids=sorted(line_ids),
        process_qualified=False,
    ) for process, line_ids in sorted(operations.items())]

    coverage = dict(
        candidate_id=bundle["candidate_id"],
        body_candidate_id=bundle["body_candidate_id"],
        selected_vehicle_candidate_id=candidate["candidate_id"],
        geometry_occurrences=len(ledger["candidate_geometry_occurrences"]),
        residual_account_ids=sorted(account_ids),
        unknown_joint_ids=[],
        joint_scope_basis=("No independently counted joint quantity is available. Joint and attachment mass remains in the reconciled residual accounts; no extra unit count is inferred."),
    )
    value = dict(
        candidate_id=bundle["candidate_id"],
        body_candidate_id=bundle["body_candidate_id"],
        engineering_BOM=rows,
        geometry_coverage=coverage,
        manufacturing_BOM=manufacturing,
        unweighed_architecture_equipment=[],
        architecture_scope_basis=("Wayside primary stock, converter capacity, feeders, protection, supports, cooling, access and battery chargers receive separate explicit cost lines. These proxies do not locate or qualify the installed equipment."),
        selected_vehicle_mass_ledger_id=identity(ledger),
        selected_vehicle_cost_estimate_id=vehicle_cost_record["cost_estimate_id"],
        unknown_architecture_obligations=list(bundle["unweighed_architecture_equipment"]),
    )
    value["evaluation_id"] = identity(value)
    return value


def _cost_architecture(bundle, architecture):
    """Add a conservative fleet cost basis without changing the P1 physics result."""
    value = deepcopy(architecture)
    route = bundle["architecture_case"]["physical_definition"]["route"]
    formation = bundle["architecture_case"]["physical_definition"]["formation"]
    requirements = bundle["requirements"]
    runtime = value.get("trajectory", {}).get("runtime_s")
    if not isinstance(runtime, (int, float)) or runtime <= 0:
        raise ValueError("Completed analytical segment runtime is required for the fleet estimate")
    clear_s = sqrt(2.0 * float(formation["train_length_m"]) / float(requirements["acceleration_m_s2"]))
    stations = int(route["stations"])
    cycle_terms = dict(
        segment_runtime_s=float(runtime),
        station_dwell_s=float(requirements["dwell_s"]),
        additional_tail_clearance_s=clear_s,
        terminal_turnback_s=0.0,
        terminal_basis="Periodic ring scenario; no terminal reversal allowance is included.",
        clearance_basis="Conservative extra per-station cost allowance; it may overlap with movement-profile time and is not an accepted timetable.",
    )
    cycle_s = stations * (cycle_terms["segment_runtime_s"] + cycle_terms["station_dwell_s"]
                          + cycle_terms["additional_tail_clearance_s"])
    headway = float(requirements["target_headway_s"])
    active = max(1, ceil(cycle_s / headway))
    spare = ceil(active * 0.12) + 1
    coefficients = value["quantity_coefficients"]
    coefficients.update(
        normal_service_trainsets=active,
        spare_trainsets=spare,
        purchased_cars=(active + spare) * int(bundle["cars"]),
        offered_people_per_hour_direction=int(bundle["cars"]) * int(requirements["passengers_per_car"])
            * 3600.0 / headway,
    )
    value["cost_fleet_basis"] = dict(
        fleet_cycle_s=cycle_s,
        cycle_components=cycle_terms,
        stations=stations,
        headway_s=headway,
        active_trainsets=active,
        reserve_trainsets=spare,
        reserve_policy="ceil(12% active trainsets) + one cold reserve per line",
        evidence_class="C",
        physical_headway_qualified=False,
    )
    value["source_architecture_evaluation_id"] = value.pop("evaluation_id")
    value["evaluation_id"] = identity(value)
    return value


def _propulsion_input(bundle):
    definition = station_motor.definition()
    value = dict(
        candidate_id=bundle["candidate_id"],
        body_candidate_id=bundle["body_candidate_id"],
        propulsion_component_id=bundle["propulsion_component_id"],
        selected_vehicle_propulsion_component_id=bundle["propulsion_component_id"],
        wayside_primary_definition_id=definition["motor_component_id"],
        bare_primary_kg_per_m=definition["bare_primary_stock_kg_per_m"],
        primary_definition=definition,
        available_force_map_id=None,
        electrical_thermal_duty_verified=False,
        evidence_class="C stock and process estimate only",
    )
    value["evaluation_id"] = identity(value)
    return value


def _account_renewal(candidate_id, cost_result, assumptions_record):
    line_key = "retained-equipment/selected-service-battery-and-services"
    line = next((row for row in cost_result["cost_line_items"] if row.get("line_key") == line_key), None)
    if line is None:
        raise ValueError("Selected service battery/equipment account cost line is missing")
    a = assumptions_record["assumptions"]
    years = int(assumptions_record["design_life_years"])
    rate = float(assumptions_record["real_discount_rate"])
    hours = assumptions_record["operating_hours_per_day_cases"]
    reference_hours = float(assumptions_record["maintenance_reference_operating_hours_per_day"])
    pack_lives = a["service_pack_life_years"]
    vehicle_lives = a["asset_life_years"]["rolling_stock"]
    replacement_cost = [line["scenario_iqd"][case] for case in model_cost.CASES]
    npv = []
    schedules = []
    for index, case in enumerate(model_cost.CASES):
        pack_life = float(pack_lives[index]) * reference_hours / float(hours[index])
        vehicle_life = float(vehicle_lives[index]) * reference_hours / float(hours[index])
        pack_times = [pack_life * n for n in range(1, int((years - 1) // pack_life) + 1)]
        vehicle_times = [vehicle_life * n for n in range(1, int((years - 1) // vehicle_life) + 1)]
        events = []
        case_npv = 0.0
        for year in pack_times:
            covered = any(abs(year - vehicle_year) < 1e-8 for vehicle_year in vehicle_times)
            value = 0.0 if covered else replacement_cost[index] / (1.0 + rate) ** year
            case_npv += value
            events.append(dict(
                year=round(year, 6),
                cost_iqd=round(replacement_cost[index], 2),
                present_value_iqd=round(value, 2),
                covered_by_complete_vehicle_replacement=covered,
            ))
        schedules.append(dict(
            case=case,
            assumed_life_years=float(pack_lives[index]),
            duty_adjusted_life_years=round(pack_life, 6),
            initial_account_cost_iqd=round(replacement_cost[index], 2),
            events=events,
            npv_iqd=round(case_npv, 2),
        ))
        npv.append(round(case_npv, 2))
    record = dict(
        candidate_id=candidate_id,
        scope="renewals",
        line_key="selected-service-battery-and-services-renewal",
        quantity=dict(
            design_life_years=years,
            source_account_line_id=line["line_id"],
            service_pack_life_years=pack_lives,
            event_schedule=schedules,
        ),
        unit="replacement-NPV",
        currency="IQD",
        cost_stage="lifecycle",
        scenario_iqd=dict(zip(model_cost.CASES, npv)),
        source_class="C",
        rate_evidence_class="C",
        source_ids=sorted([line["line_id"], identity(assumptions_record)]),
        physical_part_ids=["selected-service-battery-and-services"],
        calculation_basis=("Renew the already-costed service battery/equipment residual account at declared low/base/high service lives. The same account cost is used as a replacement proxy; events coincident with a whole-vehicle replacement are excluded to avoid double counting. No additional initial mass or installed battery is asserted."),
        components_iqd=None,
    )
    record["line_id"] = identity(record)
    return record, schedules


def _service_duty(bundle, assumptions_record):
    trajectory = bundle.get("_cost_trajectory", {})
    runtime = trajectory.get("runtime_s")
    brief = selected_vehicle.brief(bundle.get("_source_root", ROOT)) if hasattr(selected_vehicle, "brief") else None
    if brief is None:
        from engineering.station_rail.common import brief as load_brief
        brief = load_brief(bundle.get("_source_root", ROOT))
    service = brief["services"]
    dwell = float(brief["service"]["dwell_s"])
    charge_power = float(service["charging_power_kW_per_car_target"])
    efficiency = float(service["charging_efficiency_hypothesis"])
    interval = None if runtime is None else float(runtime) + dwell
    delivered = charge_power * dwell / 3600.0 * efficiency
    normal_load = float(brief["services"]["reference_hotel_kW_per_car"])
    adverse_load = float(brief["services"]["adverse_hotel_kW_per_car"])
    return dict(
        source="engineering/station_rail/brief.toml",
        selected_reference_hotel_kW_per_car=normal_load,
        adverse_hotel_kW_per_car=adverse_load,
        charging_power_kW_per_car=charge_power,
        charging_efficiency_hypothesis=efficiency,
        dwell_s=dwell,
        analytical_segment_runtime_s=runtime,
        assumed_interstation_cycle_s=interval,
        charger_energy_delivered_per_car_per_stop_kWh=round(delivered, 6),
        hotel_energy_per_car_per_cycle_kWh=dict(
            reference=None if interval is None else round(normal_load * interval / 3600.0, 6),
            adverse=None if interval is None else round(adverse_load * interval / 3600.0, 6),
        ),
        per_cycle_energy_margin_kWh=dict(
            reference=None if interval is None else round(delivered - normal_load * interval / 3600.0, 6),
            adverse=None if interval is None else round(delivered - adverse_load * interval / 3600.0, 6),
        ),
        repeated_duty_qualified=False,
        charge_acceptance_and_solar_yield_measured=False,
        assumption_cost_scenarios=assumptions_record["assumptions"]["auxiliary_kw_per_car"],
    )


def evaluate(record, root=ROOT, vehicle_cost_record=None):
    """Create one same-candidate 6 km synthetic system-cost scenario."""
    root = Path(root).resolve()
    selected = selection.load(root)
    candidate = selected["vehicle"]
    if vehicle_cost_record is None:
        from engineering.development_baseline import vehicle_cost
        vehicle_cost_record = vehicle_cost.evaluate(record, root)
    for key in IDS:
        if record.get(key) != candidate.get(key) or vehicle_cost_record.get(key) != candidate.get(key):
            raise ValueError("Selected-system cost inputs do not share the selected physical candidate: " + key)
    if record.get("selection_id") != selected["selection_id"] or vehicle_cost_record.get("selection_id") != selected["selection_id"]:
        raise ValueError("Selected-system cost inputs use a different development selection")
    if record.get("evaluation_id") != identity({k: v for k, v in record.items() if k != "evaluation_id"}):
        raise ValueError("Selected-system evaluation identity differs")
    if vehicle_cost_record.get("cost_estimate_id") != identity(
            {k: v for k, v in vehicle_cost_record.items() if k != "cost_estimate_id"}):
        raise ValueError("Selected-vehicle cost estimate identity differs")

    bundle = selected_reference_journey.build(root)
    if (bundle["reference_candidate_id"] != candidate["candidate_id"]
            or bundle["body_candidate_id"] != candidate["body_candidate_id"]
            or bundle["support_component_id"] != candidate["support_component_id"]
            or bundle["propulsion_component_id"] != candidate["propulsion_component_id"]
            or bundle["selection_id"] != selected["selection_id"]):
        raise ValueError("Synthetic route evaluation does not reference the exact selected v0.6 candidate")
    formation = bundle["architecture_case"]["physical_definition"]["formation"]
    bundle["requirements"] = deepcopy(bundle["architecture_case"]["requirements"])
    bundle["car_length_m"] = float(formation["car_length_m"])
    bundle["coupling_gap_m"] = float(formation["coupling_gap_m"])
    bundle["axle_loads"] = deepcopy(candidate["axle_loads"])
    bundle["definition_id"] = identity({k: v for k, v in bundle.items() if k != "definition_id"})
    railway_bundle.validate(bundle)

    parent, _ = selected_vehicle._read_parent(root)
    ledger = mass_ledger_audit.reconcile(candidate, parent)
    inventory = _inventory(bundle, candidate, ledger, vehicle_cost_record)
    architecture = railway_bundle.assess_architecture(bundle)
    architecture = _cost_architecture(bundle, architecture)
    propulsion = _propulsion_input(bundle)
    motion = system_motion.evaluate(bundle, available_map=None)
    civil = deepcopy(record["civil"])
    civil["alternatives"] = deepcopy(civil["control_alternatives"]["crowd_control"])
    civil["source_vehicle_candidate_id"] = candidate["candidate_id"]
    civil["candidate_id"] = bundle["candidate_id"]
    civil["body_candidate_id"] = bundle["body_candidate_id"]
    civil["cost_route_bundle_id"] = bundle["candidate_id"]
    civil["evaluation_id"] = identity({k: v for k, v in civil.items() if k != "evaluation_id"})

    assumptions_record = model_cost.assumptions(root)
    cost = model_cost.evaluate(bundle, inventory, architecture, propulsion, motion, civil,
                                estimate=assumptions_record, root=root)
    renewal_line, renewal_schedule = _account_renewal(bundle["candidate_id"], cost, assumptions_record)

    lines = [*cost["cost_line_items"], renewal_line]
    scope_totals = {scope: dict(zip(model_cost.CASES, values))
                    for scope, values in cost["scope_totals_iqd"].items()}
    for case in model_cost.CASES:
        scope_totals["renewals"][case] = round(scope_totals["renewals"][case] + renewal_line["scenario_iqd"][case], 2)
    base_whole_life = dict(zip(model_cost.CASES, cost["model_based_whole_life_NPV_iqd"]))
    whole_life = {case: round(base_whole_life[case] + renewal_line["scenario_iqd"][case], 2)
                  for case in model_cost.CASES}
    lifetime = deepcopy(cost["lifecycle"])
    for index, case in enumerate(model_cost.CASES):
        lifetime["renewal_NPV_iqd"][index] = round(
            lifetime["renewal_NPV_iqd"][index] + renewal_line["scenario_iqd"][case], 2)

    operating_hours = assumptions_record["operating_hours_per_day_cases"]
    assumptions = assumptions_record["assumptions"]
    duty_bundle = dict(bundle, _cost_trajectory=architecture["trajectory"], _source_root=root)
    duty = _service_duty(duty_bundle, assumptions_record)
    active = architecture["cost_fleet_basis"]["active_trainsets"]
    fleet = architecture["cost_fleet_basis"]["reserve_trainsets"] + active

    model_vehicle_lines = [line for line in cost["cost_line_items"] if line["scope"] == "rolling-stock"]
    model_vehicle_per_train = {
        case: round(fsum(line["scenario_iqd"][case] for line in model_vehicle_lines)
                    / fleet, 2) for case in model_cost.CASES
    }
    scenario_definition = dict(
        schema="osr-selected-v06-system-cost-scenario/1",
        selected_vehicle_candidate_id=candidate["candidate_id"],
        selected_body_candidate_id=candidate["body_candidate_id"],
        selection_id=selected["selection_id"],
        vehicle_evaluation_id=record["evaluation_id"],
        vehicle_cost_estimate_id=vehicle_cost_record["cost_estimate_id"],
        system_bundle_id=bundle["candidate_id"],
        system_bundle_definition_id=bundle["definition_id"],
        route_scenario=dict(
            kind="synthetic-periodic-reference-corridor",
            directional_ring_length_m=6000.0,
            stations=3,
            spacing_m=2000.0,
            trackways=2,
            guideway_family="box-beam",
            span_m=20.0,
            selected_candidate_geometry_changed=False,
        ),
        service=dict(
            cars_per_train=6,
            fixed_seats_per_car=44,
            wheelchair_places_per_car=2,
            normal_people_per_car=46,
            target_headway_s=120.0,
            operating_hours_per_day=operating_hours,
            operations_shifts_per_day=assumptions_record["operations_shifts_per_day_cases"],
            operations_hours_per_shift=assumptions_record["operations_hours_per_shift_cases"],
            service_direction_count=assumptions_record["service_directions"],
        ),
        fleet_basis=architecture["cost_fleet_basis"],
        assumption_id=cost["assumption_id"],
    )
    scenario_id = identity(scenario_definition)
    result = dict(
        schema="osr-selected-v06-whole-system-class-c-cost/1",
        development_default=True,
        purpose="research and requests for evidence",
        candidate_id=candidate["candidate_id"],
        **{key: candidate[key] for key in IDS[1:]},
        selection_id=selected["selection_id"],
        vehicle_evaluation_id=record["evaluation_id"],
        vehicle_cost_estimate_id=vehicle_cost_record["cost_estimate_id"],
        evaluation_candidate_id=bundle["candidate_id"],
        bundle_definition_id=bundle["definition_id"],
        scenario_id=scenario_id,
        scenario_definition=scenario_definition,
        estimate_class="C",
        currency="IQD",
        estimate_date=assumptions_record["estimate_date"],
        assumptions_id=cost["assumption_id"],
        assumption_source="engineering/design_search/model_cost.py::assumptions",
        input_evaluation_ids=cost["input_evaluation_ids"],
        source_sha256=sources(root),
        corridor_basis=cost["corridor_basis"],
        fleet_basis=architecture["cost_fleet_basis"],
        service_battery_duty=duty,
        cost_scope_status=[dict(scope=scope, status="class-c-estimated",
            physical_or_commercial_acceptance=False) for scope in model_cost.SCOPES],
        required_cost_scopes=list(model_cost.SCOPES),
        missing_cost_scopes=[],
        scope_totals_iqd=scope_totals,
        factory_gate_cost_iqd=cost["factory_gate_cost_iqd"],
        delivered_cost_iqd=cost["delivered_cost_iqd"],
        model_based_installed_CAPEX_iqd=cost["model_based_installed_CAPEX_iqd"],
        model_based_whole_life_NPV_iqd=whole_life,
        annual_energy_iqd=cost["annual_energy_iqd"],
        annual_operations_iqd=cost["annual_operations_iqd"],
        annual_maintenance_iqd=cost["annual_maintenance_iqd"],
        annual_reliability_iqd=cost["annual_reliability_iqd"],
        annual_electricity_kwh=cost["annual_electricity_kwh"],
        lifecycle=lifetime,
        service_pack_renewal_schedule=renewal_schedule,
        cost_line_items=lines,
        vehicle_cost_reconciliation=dict(
            separate_selected_vehicle_cost_estimate_id=vehicle_cost_record["cost_estimate_id"],
            selected_vehicle_cost_iqd_per_six_car_train=vehicle_cost_record["total_vehicle_factory_delivery_assembly_iqd_per_train"],
            independent_system_model_rolling_stock_iqd_per_train=model_vehicle_per_train,
            aggregation_rule="The system estimate prices selected-candidate geometry/account rows as fleet units; it does not add the separate vehicle estimate total.",
            account_overlap_possible=True,
        ),
        rate_evidence_summary=cost["rate_evidence_summary"],
        model_cost_complete_for_declared_case=True,
        physical_mass_complete=False,
        physical_journey_completed=False,
        service_qualified=False,
        procurement_ready=False,
        limitations=[
            "This is one 6 km synthetic periodic corridor scenario with three stations, not a city route or approved deployment.",
            "All 14 cost scopes receive low/base/high Class C estimates; no supplier quote, installed offer, city survey or commercial approval is represented.",
            "The selected physical vehicle identity is unchanged. The six-car route bundle and its cost scenario have separate evaluation identities.",
            "The 20 m box-beam quantities, foundations, stations, haul distances, factory throughput, tariffs, crew sizes and rates remain planning proxies.",
            "Vehicle residual account mass is priced as bounded equipment allowance. It remains unlocated, possible overlap is unresolved, and complete installed mass stays false.",
            "Unknown joints are not assigned an invented count. Their known residual mass allowances are costed once; any additional hardware outside those accounts remains open.",
            "The separate selected vehicle cost estimate is reported as a reconciliation reference and is not added to this whole-system total.",
            "Wayside primary stock, converter, cable/protection, cooling/support and charger costs are Class C quantities; no force map, thermal duty, electrical rating or station supply is qualified.",
            "Service energy is conditional on required mechanical work and declared 35/35/50 kW hotel loads. Charging dwell, battery charge acceptance, roof solar yield and repeated duty are not qualified.",
            "The fleet allowance adds full-tail clearance to each segment and may overlap movement time; it is a conservative costing scenario, not an accepted timetable.",
            "Physical, engineering, manufacturing and operating acceptance remain false.",
        ],
        **FLAGS,
    )
    result["scenario_id"] = scenario_id
    result["cost_estimate_id"] = identity(result)
    return result

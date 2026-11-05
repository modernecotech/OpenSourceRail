"""Candidate-bound Class C cost screen for the selected v0.6 vehicle.

The estimate prices located geometry occurrences and every reconciled mass
account with explicit low/base/high assumptions. It is a vehicle production,
delivery and assembly screen; it is not a route or whole-life cost evaluation.
"""
from collections import defaultdict
from copy import deepcopy
from math import fsum
from pathlib import Path

from engineering import mass_ledger_audit, mass_reserve_sensitivity
from engineering.design_search import model_cost
from engineering.station_rail import vehicle as selected_vehicle
from engineering.station_rail.common import digest, identity

PRODUCER = "engineering/development_baseline/vehicle_cost.py"
FLAGS = dict(
    engineering_accepted=False,
    physical_accepted=False,
    installed_mass_complete=False,
    manufacturing_release=False,
    operating_release=False,
)
TRAIN_CARS = 6


def sources(root):
    root = Path(root)
    names = (
        PRODUCER,
        "engineering/design_search/model_cost.py",
        "engineering/mass_ledger_audit.py",
        "engineering/mass_reserve_sensitivity.py",
        "campaigns/mass-reserve-sensitivity.toml",
        "engineering/development_baseline/selection.py",
        "engineering/development_baseline/propulsion_policy.py",
        "engineering/station_rail/common.py",
        "engineering/station_rail/brief.toml",
        "engineering/station_rail/vehicle.py",
        model_cost.RATE_DATA,
    )
    return {name: digest(root / name) for name in names}


def _money(values):
    if len(values) != 3:
        raise ValueError("Three cost scenarios are required")
    numbers = [round(float(value), 2) for value in values]
    if any(value < 0 for value in numbers) or numbers != sorted(numbers):
        raise ValueError("Cost scenarios must be nonnegative and monotone")
    return dict(zip(model_cost.CASES, numbers))


def _family(material):
    name = str(material or "").lower()
    if any(value in name for value in ("aluminium", "aluminum", "6082", "6061")):
        return "aluminium"
    if any(value in name for value in ("steel", "iron", "rebar")):
        return "steel"
    if any(value in name for value in ("copper", "winding")):
        return "copper"
    if any(value in name for value in ("gfrp", "glass", "composite", "core", "foam")):
        return "composite"
    return "generic"


def _process_template(family):
    return {
        "aluminium": "receive stock; cut/form; machine; join; finish; inspect",
        "steel": "receive stock; cut/form; weld; machine; protect; inspect",
        "composite": "prepare mould; lay up; infuse/cure; trim/bond; inspect",
        "copper": "prepare conductor; wind; insulate; assemble; electrically test",
        "generic": "purchase or prepare stock; fit/assemble; inspect",
    }[family]


def _line(candidate_id, key, stage, quantity, unit, totals, basis, source_ids,
          occurrence_ids=(), process_template=None, components=None):
    row = dict(
        candidate_id=candidate_id,
        line_key=key,
        stage=stage,
        quantity=quantity,
        unit=unit,
        currency="IQD",
        cost_iqd=_money(totals),
        estimate_class="C",
        rate_evidence_class="C",
        process_template=process_template,
        source_ids=sorted(set(source_ids)),
        occurrence_ids=sorted(set(occurrence_ids)),
        calculation_basis=basis,
        components_iqd=None if components is None else {
            name: _money(values) for name, values in components.items()
        },
    )
    if not row["source_ids"]:
        raise ValueError("Every selected-vehicle cost line requires evidence IDs")
    row["line_id"] = identity(row)
    return row


def _geometry_lines(candidate, ledger, assumptions_record, rates):
    assumptions = rates
    grouped = defaultdict(list)
    for occurrence in ledger["candidate_geometry_occurrences"]:
        grouped[(occurrence["account_id"], _family(occurrence.get("material")))].append(occurrence)

    skilled_wage = assumptions_record["benchmark_rates_iqd"]["wage_skilled_iqd_per_h"]
    burden = assumptions["wage_burden_multipliers"]
    second_premium = assumptions["second_shift_wage_premium"]
    third_premium = assumptions["third_shift_wage_premium"]
    production_wage = [
        model_cost._shift_adjusted_wage(
            skilled_wage * burden[i],
            assumptions_record["production_shifts_per_day"],
            second_premium[i],
            third_premium[i],
        )
        for i in range(3)
    ]
    output = []
    for (account_id, family), rows in sorted(grouped.items()):
        mass = fsum(float(row["mass_kg"]) for row in rows)
        material_rates, _ = model_cost._material_rate(assumptions, family)
        purchase_yield = assumptions["body_purchase_yield"]
        purchased_mass = [mass / purchase_yield[i] for i in range(3)]
        material = [purchased_mass[i] * material_rates[i] for i in range(3)]
        process_hours = [
            mass * assumptions["body_process_hours_per_kg"][i] + (0.02, 0.08, 0.25)[i]
            for i in range(3)
        ]
        labour = [process_hours[i] * production_wage[i] for i in range(3)]
        machine_hours = [mass * assumptions["body_machine_hours_per_kg"][i] for i in range(3)]
        equipment = [machine_hours[i] * assumptions["machine_rate_iqd_per_h"][i] for i in range(3)]
        quality = [material[i] * assumptions["body_qa_fraction"][i] for i in range(3)]
        direct = [material[i] + labour[i] + equipment[i] + quality[i] for i in range(3)]
        overhead = [direct[i] * assumptions["factory_overhead_fraction"][i] for i in range(3)]
        total = [direct[i] + overhead[i] for i in range(3)]
        output.append(_line(
            candidate["candidate_id"],
            "located-stock/" + account_id + "/" + family,
            "factory-gate",
            dict(
                net_mass_kg_per_car=round(mass, 12),
                gross_purchase_mass_kg_per_car=[round(value, 12) for value in purchased_mass],
                occurrence_count=len(rows),
                process_hours_per_car=[round(value, 12) for value in process_hours],
                machine_hours_per_car=[round(value, 12) for value in machine_hours],
            ),
            "kg",
            [value * TRAIN_CARS for value in total],
            "Occurrence masses from the reconciled selected-candidate ledger; material purchase yield, process hours/kg, two-shift labour, machine hours, QA and one factory-overhead uplift are explicit Class C inputs.",
            [identity(assumptions_record), identity({"account_id": account_id, "family": family,
                "occurrence_ids": sorted(row["occurrence_id"] for row in rows)})],
            [row["occurrence_id"] for row in rows],
            _process_template(family),
            components={
                "material": [value * TRAIN_CARS for value in material],
                "labour": [value * TRAIN_CARS for value in labour],
                "equipment": [value * TRAIN_CARS for value in equipment],
                "quality": [value * TRAIN_CARS for value in quality],
                "factory_overhead": [value * TRAIN_CARS for value in overhead],
            },
        ))
    return output


def evaluate(record, root):
    """Estimate vehicle production costs for the exact selected candidate."""
    root = Path(root).resolve()
    candidate = selected_vehicle.build(root)
    from engineering.development_baseline import selection
    selected = selection.load(root)
    expected = record["vehicle"]
    ids = ("candidate_id", "body_candidate_id", "support_component_id", "propulsion_component_id")
    if any(candidate[key] != expected[key] or record[key] != candidate[key] for key in ids):
        raise ValueError("Selected-vehicle cost inputs do not share one candidate identity")
    if record.get("selection_id") != selected["selection_id"]:
        raise ValueError("Selected-vehicle cost inputs do not share the current selection identity")
    if record.get("evaluation_id") != identity({key: value for key, value in record.items()
                                                 if key != "evaluation_id"}):
        raise ValueError("Selected-vehicle cost evaluation identity differs")
    if record.get("development_default") is not True or any(
        record.get(key) is not False for key in FLAGS
    ):
        raise ValueError("A selected development candidate with open acceptance is required")

    parent, _ = selected_vehicle._read_parent(root)
    ledger = mass_ledger_audit.reconcile(candidate, parent)
    reserve_sensitivity = mass_reserve_sensitivity.plan(root)
    reserve_cases = reserve_sensitivity["sensitivity_cases"]
    reserve_by_account = {row["account_id"]: row for row in reserve_sensitivity["reserve_accounts"]}
    if len(reserve_by_account) != len(reserve_sensitivity["reserve_accounts"]):
        raise ValueError("Mass-reserve sensitivity account identities must be unique")
    expected_reserve_ids = {
        account["account_id"] for account in ledger["accounts"]
        if float(account["residual_account_mass_kg"]) > 1e-9
    }
    if set(reserve_by_account) != expected_reserve_ids:
        raise ValueError("Mass-reserve sensitivity must cover each positive residual account exactly once")
    scenario_tare = {
        row["name"]: float(row["scenario_tare_mass_kg_per_car"])
        for row in reserve_cases
    }
    if tuple(scenario_tare) != model_cost.CASES:
        raise ValueError("Mass-reserve sensitivity cases must match the selected cost cases")
    assumptions_record = model_cost.assumptions(root)
    assumptions = model_cost._validate_assumptions(deepcopy(assumptions_record), root)
    geometry_lines = _geometry_lines(candidate, ledger, assumptions_record, assumptions)

    skilled_wage = assumptions_record["benchmark_rates_iqd"]["wage_skilled_iqd_per_h"]
    burden = assumptions["wage_burden_multipliers"]
    second_premium = assumptions["second_shift_wage_premium"]
    third_premium = assumptions["third_shift_wage_premium"]
    production_wage = [
        model_cost._shift_adjusted_wage(
            skilled_wage * burden[i],
            assumptions_record["production_shifts_per_day"],
            second_premium[i],
            third_premium[i],
        )
        for i in range(3)
    ]

    account_lines = []
    for account in ledger["accounts"]:
        residual_mass = float(account["residual_account_mass_kg"])
        if residual_mass <= 1e-9:
            continue
        reserve = reserve_by_account[account["account_id"]]
        if abs(float(reserve["existing_residual_kg"]) - residual_mass) > 1e-7:
            raise ValueError("Mass-reserve sensitivity differs from the reconciled account residual")
        scenario_mass = [float(reserve["scenario_reserve_kg"][case]) for case in model_cost.CASES]
        if abs(scenario_mass[1] - residual_mass) > 1e-7:
            raise ValueError("Base reserve scenario must equal the selected account's current residual")
        rates = assumptions["finished_equipment_iqd_per_kg"]
        cost = [scenario_mass[i] * rates[i] * TRAIN_CARS for i in range(3)]
        process_hours = [
            scenario_mass[i] * assumptions["equipment_process_hours_per_kg"][i] * TRAIN_CARS
            for i in range(3)
        ]
        account_lines.append(_line(
            candidate["candidate_id"],
            "unlocated-account/" + account["account_id"],
            "factory-gate-equipment-allowance",
            dict(
                residual_account_mass_kg_per_car=round(residual_mass, 12),
                scenario_reserve_mass_kg_per_car=[round(value, 12) for value in scenario_mass],
                gross_train_mass_kg_by_case=[round(value * TRAIN_CARS, 12) for value in scenario_mass],
                process_hours_per_train=[round(value, 12) for value in process_hours],
                disposition=account["disposition"],
            ),
            "accounted-kg",
            cost,
            "Each low/base/high cost case replaces the existing account residual with the same-index declared 0.8×/1.0×/1.2× mass reserve, then applies the finished-equipment proxy. It remains unlocated mass and is not a physical BOM or installed-mass resolution.",
            [identity(assumptions_record), identity(account), reserve_sensitivity["assumption_id"]],
            account["source_occurrence_ids"],
            "purchase or complete the specified equipment; fit; inspect",
        ))

    located_cost = [
        fsum(line["cost_iqd"][case] for line in geometry_lines)
        for case in model_cost.CASES
    ]
    residual_cost = [fsum(line["cost_iqd"][case] for line in account_lines) for case in model_cost.CASES]
    factory_gate = [located_cost[i] + residual_cost[i] for i in range(3)]

    install_hours = assumptions["vehicle_install_hours_per_car"]
    install_labour = [install_hours[i] * production_wage[i] * TRAIN_CARS for i in range(3)]
    install_equipment = [value * TRAIN_CARS for value in assumptions["vehicle_install_equipment_iqd_per_car"]]
    assembly_cost = [install_labour[i] + install_equipment[i] for i in range(3)]
    assembly_line = _line(
        candidate["candidate_id"],
        "six-car-final-vehicle-assembly",
        "final-assembly",
        dict(cars=TRAIN_CARS, labour_hours_per_car=install_hours,
             equipment_iqd_per_car=assumptions["vehicle_install_equipment_iqd_per_car"]),
        "car",
        assembly_cost,
        "Six selected cars; declared installation labour and equipment allowances, with the 2 × 8 h/day production shift wage basis.",
        [identity(assumptions_record), record["evaluation_id"]],
        process_template="fit, connect, inspect and weigh; qualification testing remains outside this estimate",
        components={"labour": install_labour, "equipment": install_equipment},
    )
    delivery_tonne_km = (
        float(candidate["mass"]["accounted_tare_kg_per_car"]) * TRAIN_CARS / 1000.0
        * assumptions_record["outbound_route_km"]
    )
    delivery_cost = [delivery_tonne_km * value for value in assumptions["transport_iqd_per_tonne_km"]]
    delivery_line = _line(
        candidate["candidate_id"],
        "reference-factory-to-assembly-delivery",
        "reference-delivery",
        dict(accounted_train_mass_t=round(float(candidate["mass"]["accounted_tare_kg_per_car"])
                                          * TRAIN_CARS / 1000.0, 12),
             reference_distance_km=assumptions_record["outbound_route_km"],
             tonne_km=round(delivery_tonne_km, 12)),
        "tonne-km",
        delivery_cost,
        "Accounted six-car train mass × declared 50 km reference distance × low/base/high transport rate; not a factory route or transport quote.",
        [identity(assumptions_record), record["evaluation_id"]],
        process_template="load, transport and unload; route, permits and handling are not separately surveyed",
    )
    total_cost = [factory_gate[i] + assembly_cost[i] + delivery_cost[i] for i in range(3)]

    tooling = [
        assumptions["body_fixture_iqd_each"][i] + assumptions["vehicle_cell_iqd_each"][i]
        for i in range(3)
    ]
    material_families = sorted({
        _family(row.get("material"))
        for row in ledger["candidate_geometry_occurrences"]
    })
    benchmark_wage = assumptions_record["benchmark_rates_iqd"]["wage_skilled_iqd_per_h"]
    loaded_production_wage = [
        benchmark_wage * assumptions["wage_burden_multipliers"][i]
        * (1 + assumptions["second_shift_wage_premium"][i] / 2)
        for i in range(3)
    ]
    assumption_values = dict(
        material_rate_iqd_per_kg={
            family: _money(model_cost._material_rate(assumptions, family)[0])
            for family in material_families
        },
        body_purchase_yield=assumptions["body_purchase_yield"],
        body_process_hours_per_kg=assumptions["body_process_hours_per_kg"],
        body_machine_hours_per_kg=assumptions["body_machine_hours_per_kg"],
        machine_rate_iqd_per_h=assumptions["machine_rate_iqd_per_h"],
        body_qa_fraction=assumptions["body_qa_fraction"],
        factory_overhead_fraction=assumptions["factory_overhead_fraction"],
        skilled_wage_benchmark_iqd_per_h=benchmark_wage,
        skilled_wage_benchmark_record_id=assumptions_record["benchmark_record_ids"]["skilled_wage"],
        wage_burden_multipliers=assumptions["wage_burden_multipliers"],
        second_shift_wage_premium=assumptions["second_shift_wage_premium"],
        loaded_two_shift_skilled_wage_iqd_per_h=loaded_production_wage,
        finished_equipment_iqd_per_kg=assumptions["finished_equipment_iqd_per_kg"],
        equipment_process_hours_per_kg=assumptions["equipment_process_hours_per_kg"],
        vehicle_install_hours_per_car=assumptions["vehicle_install_hours_per_car"],
        vehicle_install_equipment_iqd_per_car=assumptions["vehicle_install_equipment_iqd_per_car"],
        outbound_route_km=assumptions_record["outbound_route_km"],
        transport_iqd_per_tonne_km=assumptions["transport_iqd_per_tonne_km"],
        body_fixture_iqd_each=assumptions["body_fixture_iqd_each"],
        vehicle_cell_iqd_each=assumptions["vehicle_cell_iqd_each"],
        productive_utilisation=assumptions_record["productive_utilisation"],
        production_days_per_year=assumptions_record["production_days_per_year"],
    )
    overlap = candidate.get("residual_overlap_unresolved", {})
    if overlap.get("overlap_possible") is not True or overlap.get("overlap_amount_kg") is not None:
        raise ValueError("Selected vehicle cost requires its unresolved mass-overlap record")

    scope_status = []
    for scope in model_cost.SCOPES:
        if scope == "rolling-stock":
            status = "class-c-accounted-mass-estimate"
            reason = "Prices located occurrences and named residual accounts; complete installation and possible account overlap remain open."
        elif scope == "factory-tooling":
            status = "separate-capital-range"
            reason = "One body fixture and one vehicle cell are bounded; factory scale, utilization and amortization are not assigned to unit cost."
        else:
            status = "held"
            reason = "Candidate-specific route, station, fleet, operating or asset-life quantities are not available; no zero-cost substitute is used."
        scope_status.append(dict(scope=scope, status=status, reason=reason))

    value = dict(
        schema="osr-v06-selected-vehicle-class-c-cost/1",
        **{key: record[key] for key in (*ids, "evaluation_id", "selection_id")},
        development_default=True,
        estimate_class="C",
        currency="IQD",
        estimate_date=assumptions_record["estimate_date"],
        assumptions_id=assumptions_record["assumption_id"],
        assumption_values=assumption_values,
        benchmark_dataset=assumptions_record["benchmark_dataset"],
        source_sha256=sources(root),
        shifts=dict(
            production_per_day=dict(shifts=2, hours_per_shift=8,
                productive_hours_per_day=round(2 * 8 * assumptions_record["productive_utilisation"], 4)),
            civil_per_day=dict(shifts=2, hours_per_shift=8),
            operations_cases=[dict(hours_per_day=hours, shifts_per_day=shifts,
                hours_per_shift=shift_hours)
                for hours, shifts, shift_hours in zip(
                    assumptions_record["operating_hours_per_day_cases"],
                    assumptions_record["operations_shifts_per_day_cases"],
                    assumptions_record["operations_hours_per_shift_cases"])],
        ),
        vehicle_account=dict(
            cars_per_train=TRAIN_CARS,
            accounted_tare_kg_per_car=candidate["mass"]["accounted_tare_kg_per_car"],
            located_geometry_kg_per_car=ledger["summary"]["located_geometry_mass_kg"],
            residual_account_kg_per_car=ledger["summary"]["residual_reference_or_unlocated_mass_kg"],
            scenario_tare_mass_kg_per_car=scenario_tare,
            geometry_occurrences=ledger["summary"]["located_geometry_occurrence_count"],
            account_rows=ledger["summary"]["account_row_count"],
            complete_installed_mass=False,
        ),
        mass_reserve_sensitivity=dict(
            assumption_id=reserve_sensitivity["assumption_id"],
            result_id=reserve_sensitivity["result_id"],
            case_factors={row["name"]: row["reserve_factor"] for row in reserve_cases},
            interpretation="Same-index low/base/high mass factors are coupled to the vehicle cost and process-hour cases. They replace the current unlocated account balances, do not add another allowance, and do not qualify installed mass.",
        ),
        lines=geometry_lines + account_lines + [assembly_line, delivery_line],
        factory_gate_cost_iqd_per_train=_money(factory_gate),
        final_vehicle_assembly_cost_iqd_per_train=_money(assembly_cost),
        reference_delivery_cost_iqd_per_train=_money(delivery_cost),
        reference_delivery_tonne_km=round(delivery_tonne_km, 12),
        reference_delivery_distance_km=assumptions_record["outbound_route_km"],
        total_vehicle_factory_delivery_assembly_iqd_per_train=_money(total_cost),
        unit_iqd_per_car=_money([value / TRAIN_CARS for value in total_cost]),
        separate_unamortized_factory_tooling_capital_iqd=_money(tooling),
        accounting_overlap=dict(
            possible=True,
            overlap_mass_kg=None,
            net_overlap_cost_adjustment_iqd=None,
            total_assumes_gross_accounts_are_distinct=True,
            basis=overlap.get("reason"),
        ),
        whole_life_cost_iqd=None,
        city_cost_iqd=None,
        scope_status=scope_status,
        limitations=[
            "This Class C estimate is for the exact selected six-car vehicle only and does not inherit prices from railway research bundles.",
            "Located geometry prices use material-family proxies, generic process hours, machine rates, QA and overhead; no supplier prices are implied.",
            "Residual-account prices are bounded finished-equipment allowances and do not locate, identify or resolve the residual mass.",
            "All mass accounts are summed gross because the possible overlap amount is unknown; no overlap credit is silently applied.",
            "The 50 km delivery distance is a declared reference assumption, not a measured route from an identified factory.",
            "Civil quantities, route performance, stations, fleet size, energy, operations, maintenance, reliability and whole-life costs remain held.",
            "Cost ranges are coupled assumptions, not probabilities or confidence intervals; no FX conversion is performed.",
        ],
        **FLAGS,
    )
    value["cost_estimate_id"] = identity(value)
    return value

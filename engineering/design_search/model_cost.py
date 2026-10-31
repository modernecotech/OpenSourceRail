"""Candidate-bound Class C cost completion for the coupled railway campaign.

This module prices a declared synthetic corridor from candidate quantities and
explicit engineering proxies. It never turns an estimate into a supplier price,
complete installed mass, service qualification, or release.
"""
from copy import deepcopy
from math import ceil, fsum, isfinite
import json
from pathlib import Path

from engineering.station_rail.common import digest, identity
from . import railway_bundle

PRODUCER = "engineering/design_search/model_cost.py"
RATE_DATA = "engineering/sourcing/data/iraq-domestic-2026-july.json"
SCOPES = (
    "rolling-stock", "guideway", "stations-power", "factory-tooling",
    "construction", "land-utilities-depot", "fleet", "energy", "operations",
    "maintenance", "renewals", "recovery", "reliability", "disposal",
)
CASES = ("low", "base", "high")
YEARS = 30
TRACKWAYS = 2
PRODUCTION_YEARS = 3


def sources(root=Path(__file__).resolve().parents[2]):
    root = Path(root)
    return {PRODUCER: digest(root / PRODUCER), RATE_DATA: digest(root / RATE_DATA)}


def assumptions(root=Path(__file__).resolve().parents[2]):
    """Return sealed rates plus dated Iraqi benchmark references and C proxies."""
    root = Path(root)
    path = root / RATE_DATA
    data = json.loads(path.read_text())
    benchmarks = {r["benchmark_key"]: r for r in data.get("benchmarks", [])}
    keys = {
        "cement": "iq-cso-2026-07:iraq-origin:material:cement-ordinary",
        "aggregate": "iq-cso-2026-07:iraq-origin:material:gravel-crushed",
        "sand": "iq-cso-2026-07:iraq-origin:material:sand-red",
        "rebar": "iq-cso-2026-07:iraq-origin:material:rebar",
        "unskilled_wage": "iq-cso-2026-07:al-muthanna:wage:unskilled:hour-8h-day",
        "semiskilled_wage": "iq-cso-2026-07:al-muthanna:wage:semi-skilled:hour-8h-day",
        "skilled_wage": "iq-cso-2026-07:al-muthanna:wage:skilled:hour-8h-day",
    }
    refs = {}
    for name, key in keys.items():
        row = benchmarks.get(key)
        if not isinstance(row, dict) or row.get("currency") != "IQD":
            raise ValueError("Required dated Iraqi rate benchmark is absent: " + key)
        refs[name] = deepcopy(row)
    for name, unit in (("cement", "t"), ("aggregate", "m3"), ("sand", "m3"), ("rebar", "t"),
                       ("unskilled_wage", "h"), ("semiskilled_wage", "h"), ("skilled_wage", "h")):
        if refs[name].get("quantity_unit") != unit or refs[name].get("supplier_quote") is not False:
            raise ValueError("Dated benchmark unit/provenance differs: " + name)
    estimate_date = "2026-10-31"
    value = dict(
        schema="osr-coupled-class-c-cost-assumptions/1", source_class="C",
        currency="IQD", estimate_date=estimate_date,
        location="Synthetic 6 km Iraqi reference corridor; no city survey or site rates",
        corridor_trackways=TRACKWAYS, production_years=PRODUCTION_YEARS,
        production_days_per_year=250,
        design_life_years=YEARS, real_discount_rate=0.04,
        operating_hours_per_day=18, operating_days_per_year=365,
        shifts_per_day=2, hours_per_shift=8, productive_utilisation=0.75,
        outbound_route_km=50,
        benchmark_dataset=dict(path=RATE_DATA, sha256=digest(path), source_date="2026-07-31",
            source_key="iraq.cso.regional-materials-wages-2026-07",
            source_document_sha256=data["sources"]["iraq.cso.regional-materials-wages-2026-07"]["document_sha256"],
            benchmark_keys=keys,
            limitations="CSO averages are not matched supplier offers, delivered prices, employer-loaded wages or installed rates."),
        benchmark_rates_iqd=dict(
            cement_iqd_per_t=float(refs["cement"]["unit_price"]),
            aggregate_iqd_per_m3=float(refs["aggregate"]["unit_price"]),
            sand_iqd_per_m3=float(refs["sand"]["unit_price"]),
            rebar_iqd_per_kg=float(refs["rebar"]["unit_price"])/1000.0,
            wage_unskilled_iqd_per_h=float(refs["unskilled_wage"]["unit_price"]),
            wage_semiskilled_iqd_per_h=float(refs["semiskilled_wage"]["unit_price"]),
            wage_skilled_iqd_per_h=float(refs["skilled_wage"]["unit_price"])),
        benchmark_record_ids={k:v.get("record_id") or identity(v) for k,v in refs.items()},
        assumptions=dict(
            wage_burden_multipliers=[1.25, 1.5, 2.0],
            material_rate_sensitivity=[0.9, 1.0, 1.2],
            body_purchase_yield=[0.96, 0.90, 0.82],
            body_process_hours_per_kg=[0.10, 0.30, 1.00],
            body_machine_hours_per_kg=[0.02, 0.08, 0.25],
            machine_rate_iqd_per_h=[20000, 75000, 300000],
            body_qa_fraction=[0.03, 0.08, 0.20],
            factory_overhead_fraction=[0.10, 0.20, 0.30],
            generic_material_iqd_per_kg=[2500, 15000, 60000],
            aluminium_iqd_per_kg=[6000, 18000, 50000],
            steel_iqd_per_kg=[2500, 10000, 35000],
            composite_iqd_per_kg=[5000, 20000, 65000],
            copper_iqd_per_kg=[10000, 35000, 110000],
            finished_equipment_iqd_per_kg=[20000, 80000, 300000],
            unknown_account_iqd_each=[50000000, 250000000, 1000000000],
            equipment_process_hours_per_kg=[0.02, 0.08, 0.30],
            unknown_account_process_hours_each=[250, 1000, 4000],
            joint_hardware_iqd_each=[25000, 125000, 600000],
            joint_labour_h_each=[0.25, 1.0, 4.0],
            concrete_cement_t_per_m3=[0.30, 0.36, 0.45],
            concrete_aggregate_m3_per_m3=[0.55, 0.68, 0.85],
            concrete_sand_m3_per_m3=[0.28, 0.40, 0.55],
            concrete_waste_fraction=[0.02, 0.05, 0.10],
            concrete_admixture_iqd_per_m3=[5000, 20000, 80000],
            concrete_rebar_kg_per_m3=[100, 150, 250],
            prestress_iqd_per_kg=[2500, 8000, 25000],
            rail_iqd_per_kg=[3000, 10000, 35000],
            fastener_iqd_per_set=[100000, 400000, 1500000],
            beam_factory_hours_per_span=[24, 64, 180],
            beam_machine_iqd_per_span=[250000, 1200000, 5000000],
            beam_quality_iqd_per_span=[150000, 700000, 3000000],
            beam_mould_cycle_days=[2, 5, 10],
            beam_mould_iqd_each=[75000000, 250000000, 1000000000],
            body_fixture_iqd_each=[10000000, 50000000, 250000000],
            vehicle_cell_iqd_each=[250000000, 1000000000, 5000000000],
            guideway_cell_iqd_each=[100000000, 500000000, 2500000000],
            station_power_cell_iqd_each=[100000000, 500000000, 2500000000],
            vehicle_install_hours_per_car=[8, 24, 80],
            vehicle_install_equipment_iqd_per_car=[500000, 2000000, 10000000],
            concrete_iqd_per_m3_fallback=[30000, 70000, 180000],
            foundation_bearing_area_m2=[3.26, 4.90, 9.79],
            foundation_depth_m=[1.5, 2.5, 4.0],
            pier_area_m2=[0.4, 0.8, 1.5],
            pier_height_m=[4, 8, 15],
            station_platform_width_m=[3, 4, 6],
            station_platform_iqd_per_m2=[250000, 1000000, 4000000],
            station_access_iqd_each=[500000000, 2500000000, 12000000000],
            station_control_iqd_each=[100000000, 600000000, 3000000000],
            electrical_package_iqd_per_kw=[500000, 2000000, 8000000],
            power_electronics_install_iqd_per_kw=[25000, 100000, 400000],
            motor_primary_iqd_per_kg=[8000, 30000, 100000],
            motor_primary_hours_per_kg=[0.05, 0.18, 0.60],
            wayside_primary_process_hours_per_train=dict(P7=[500, 2000, 8000]),
            family_package_process_hours_per_train=dict(
                P2=[250, 1000, 4000], P3=[250, 1000, 4000], P4=[1000, 4000, 16000],
                P5=[250, 1000, 4000], P6=[1000, 4000, 16000], P7=[250, 1000, 4000]),
            converter_assembly_hours_per_kw=[0.05, 0.20, 0.80],
            motor_primary_delivery_iqd_per_track_m=[50000, 200000, 800000],
            motor_primary_install_iqd_per_track_m=[100000, 500000, 2000000],
            cable_iqd_per_motor_m=[50000, 250000, 1000000],
            converter_power_margin=[1.15, 1.30, 1.60],
            family_package_iqd_per_train=dict(
                P2=[100000000, 500000000, 2500000000], P3=[100000000, 500000000, 2500000000],
                P4=[500000000, 2500000000, 12000000000],
                P5=[100000000, 500000000, 2500000000],
                P6=[1000000000, 5000000000, 25000000000],
                P7=[100000000, 500000000, 2500000000]),
            wayside_primary_package_iqd_per_train=dict(
                P7=[250000000, 1500000000, 8000000000]),
            station_install_iqd_each=[250000000, 1000000000, 5000000000],
            footing_rebar_kg_per_m3=[100, 160, 250],
            field_hours_per_support=[8, 24, 64],
            transport_iqd_per_tonne_km=[100, 400, 1500],
            erection_crane_iqd_per_day=[2000000, 10000000, 50000000],
            spans_per_crane_day=[4, 2, 1],
            erection_hours_per_span=[20, 64, 180],
            foundation_supports_per_day=[8, 4, 2],
            rail_track_m_per_day=[300, 150, 60],
            station_completions_per_day=[0.05, 0.02, 0.008],
            rail_install_iqd_per_track_m=[25000, 100000, 400000],
            land_iqd_per_track_km=[100000000, 600000000, 3000000000],
            utilities_iqd_per_track_km=[50000000, 300000000, 1500000000],
            depot_iqd_per_trainset=[500000000, 2500000000, 12000000000],
            fleet_spares_fraction=[0.02, 0.06, 0.15],
            vehicle_delivery_iqd_per_train=[25000000, 150000000, 750000000],
            fleet_commission_iqd_per_train=[25000000, 150000000, 750000000],
            auxiliary_kw_per_car=[1, 3, 8],
            traction_efficiency=[0.95, 0.85, 0.70],
            electricity_iqd_per_kwh=[100, 250, 700],
            controllers_per_shift=[2, 4, 8],
            station_staff_per_station_per_shift=[1, 2, 4],
            operations_shift_hours=8,
            operations_reliever_multiplier=[1.1, 1.25, 1.5],
            maintenance_fraction_per_year=[0.015, 0.04, 0.09],
            decommissioning_fraction_of_installed_CAPEX=[0.01, 0.03, 0.08],
            asset_life_years=dict(rolling_stock=[25, 20, 15], motor_primary=[30, 25, 15],
                power_electronics=[20, 15, 10], guideway=[60, 50, 40], stations=[40, 30, 20]),
            rescue_iqd_each=[500000000, 2500000000, 12000000000],
            rescue_standby_iqd_per_year=[25000000, 150000000, 750000000],
            reliability_iqd_per_train_km=[25, 125, 600],
            construction_contingency_fraction=[0.10, 0.20, 0.30]),
        sensitivity_basis="Low/base/high are coupled cost scenarios, not confidence intervals or probabilities. Iraqi CSO rates are B-class statistical inputs; geometry extensions, recipes, burden factors, yield, process, plant, installation, energy, life and site rates are C-class hypotheses.",
        currency_basis="All values remain nominal IQD at the declared estimate date; no FX conversion is performed.",
    )
    value["assumption_id"] = identity(value)
    return value


def _finite(x):
    return type(x) in (int, float) and isfinite(x)


def _triple(value, name, *, positive=False):
    if (not isinstance(value, (list, tuple)) or len(value) != 3
            or any(not _finite(x) or x < 0 or (positive and x == 0) for x in value)):
        raise ValueError("Finite nonnegative low/base/high " + name + " required")
    return [float(x) for x in value]


def _sum(a, b):
    return [a[i] + b[i] for i in range(3)]


def _round(values):
    return [round(float(x), 2) for x in values]


def _scope_rows(lines, scope, stage=None):
    return [row for row in lines if row["scope"] == scope and (stage is None or row["cost_stage"] == stage)]


def _material_rate(assume, material_id):
    name = str(material_id).lower()
    if any(k in name for k in ("alum", "aluminium")):
        return assume["aluminium_iqd_per_kg"], "C"
    if any(k in name for k in ("gfrp", "glass", "composite", "pet_core", "core")):
        return assume["composite_iqd_per_kg"], "C"
    if any(k in name for k in ("steel", "iron", "rebar")):
        return assume["steel_iqd_per_kg"], "C"
    if any(k in name for k in ("copper", "winding")):
        return assume["copper_iqd_per_kg"], "C"
    return assume["generic_material_iqd_per_kg"], "C"


def _line(lines, *, candidate_id, scope, key, quantity, unit, totals, stage, basis,
          source_ids, source_class="C", rate_evidence_class=None, parts=(), components=None):
    values = _round(totals)
    if any(not _finite(v) or v < 0 for v in values):
        raise ValueError("Cost line must be finite and nonnegative: " + key)
    if len(values) != 3 or values != sorted(values):
        raise ValueError("Cost line must be a monotone low/base/high scenario: " + key)
    row = dict(candidate_id=candidate_id, scope=scope, line_key=key,
        quantity=quantity, unit=unit, currency="IQD", cost_stage=stage,
        scenario_iqd=dict(zip(CASES, values)), source_class=source_class,
        rate_evidence_class=rate_evidence_class or source_class,
        source_ids=sorted(set(source_ids)), physical_part_ids=sorted(set(parts)),
        calculation_basis=basis, components_iqd=None if components is None else
            {k:_round(v) for k,v in components.items()})
    if not row["source_ids"]:
        raise ValueError("Every model cost line needs a source or assumption identity")
    row["line_id"] = identity(row)
    lines.append(row)
    return values


def _benchmark_evidence(a, *names):
    return [a["benchmark_record_ids"][name] for name in names]


def _check_input(record, candidate_id, name):
    if not isinstance(record, dict) or record.get("candidate_id") != candidate_id:
        raise ValueError("Mixed candidate in cost input: " + name)
    if "evaluation_id" in record and record["evaluation_id"] != identity(
            {k:v for k,v in record.items() if k != "evaluation_id"}):
        raise ValueError("Cost input evaluation identity differs: " + name)


def _validate_assumptions(value, root):
    if (not isinstance(value, dict) or value.get("schema") != "osr-coupled-class-c-cost-assumptions/1"
            or value.get("assumption_id") != identity({k:v for k,v in value.items() if k != "assumption_id"})):
        raise ValueError("Sealed Class C cost assumptions required")
    if value.get("currency") != "IQD" or value.get("benchmark_dataset", {}).get("sha256") != digest(Path(root)/RATE_DATA):
        raise ValueError("Cost assumptions must use the current single-currency dated rate dataset")
    for key, item in value["assumptions"].items():
        if isinstance(item, list):
            _triple(item, key)
        elif isinstance(item, dict):
            for nested in item.values():
                if isinstance(nested, list):
                    _triple(nested, key)
    positive_fields=("corridor_trackways", "production_years", "production_days_per_year", "design_life_years", "operating_hours_per_day",
        "operating_days_per_year", "hours_per_shift", "shifts_per_day", "productive_utilisation", "outbound_route_km")
    for key in positive_fields:
        item=value.get(key)
        if not _finite(item) or item <= 0:
            raise ValueError("Positive finite cost-scope assumption required: " + key)
    if not 0 <= value.get("real_discount_rate", -1) < 1:
        raise ValueError("Real discount rate must be in [0, 1)")
    if value["corridor_trackways"] != int(value["corridor_trackways"]):
        raise ValueError("Trackway quantity must be an integer")
    if value["operating_hours_per_day"] > 24 or value["operating_days_per_year"] > 366 or value["productive_utilisation"] > 1:
        raise ValueError("Operating and production utilisation assumptions are outside their declared domains")
    if value["assumptions"].get("operations_shift_hours", 0) <= 0:
        raise ValueError("Positive operations shift hours required")
    return value["assumptions"]


def evaluate(bundle, inventory, architecture_result, propulsion_result, motion_result, civil_result,
             *, estimate=None, root=Path(__file__).resolve().parents[2]):
    """Price every declared cost scope for one exact coupled railway candidate."""
    root = Path(root)
    railway_bundle.validate(bundle)
    candidate_id = bundle["candidate_id"]
    for name, value in (("inventory", inventory), ("architecture", architecture_result),
                        ("propulsion", propulsion_result), ("motion", motion_result), ("civil", civil_result)):
        _check_input(value, candidate_id, name)
    assumptions_record = deepcopy(estimate if estimate is not None else assumptions(root))
    a = _validate_assumptions(assumptions_record, root)
    production_years = assumptions_record["production_years"]
    production_days = assumptions_record["production_days_per_year"]
    years = assumptions_record["design_life_years"]
    refs = assumptions_record["benchmark_record_ids"]
    evidence = [identity(assumptions_record), *sources(root).values()]
    input_ids = dict(bundle_definition_id=bundle["definition_id"],
        inventory_evaluation_id=inventory["evaluation_id"],
        architecture_evaluation_id=architecture_result["evaluation_id"],
        propulsion_evaluation_id=propulsion_result["evaluation_id"],
        motion_evaluation_id=motion_result["evaluation_id"],
        civil_evaluation_id=identity(civil_result))
    line_items = []
    wages = assumptions_record["benchmark_rates_iqd"]["wage_skilled_iqd_per_h"]
    burden = a["wage_burden_multipliers"]
    loaded_wage = [wages * burden[i] for i in range(3)]
    overhead = a["factory_overhead_fraction"]
    cars_per_train = bundle["cars"]
    coefficients = architecture_result["quantity_coefficients"]
    trainsets = coefficients.get("normal_service_trainsets")
    spares = coefficients.get("spare_trainsets")
    if type(trainsets) is not int or trainsets <= 0:
        route = bundle["architecture_case"]["physical_definition"]["route"]
        runtime = architecture_result.get("trajectory", {}).get("runtime_s")
        if not _finite(runtime) or runtime <= 0:
            runtime = route["station_spacing_m"] / max(1.0, bundle["requirements"]["speed_cap_m_s"] * 0.5)
        cycle = route["stations"] * (runtime + bundle["requirements"]["dwell_s"])
        trainsets = max(1, ceil(cycle / bundle["requirements"]["target_headway_s"]))
    if type(spares) is not int or spares < 0:
        spares = max(1, ceil(trainsets * 0.2))
    fleet_trainsets = trainsets + spares
    fleet_cars = fleet_trainsets * cars_per_train
    route = bundle["architecture_case"]["physical_definition"]["route"]
    route_m = float(coefficients.get("directional_route_m") or route["directional_ring_length_m"])
    station_count = int(coefficients.get("stations") or route["stations"])
    span = float(bundle["architecture_case"]["physical_definition"]["guideway"]["span_m"])
    if route_m <= 0 or span <= 0 or station_count <= 0:
        raise ValueError("Positive route, station and span quantities required for cost model")
    trackways = assumptions_record["corridor_trackways"]
    spans_per_track = ceil(route_m / span)
    span_count = spans_per_track * trackways
    support_count = (spans_per_track + 1) * trackways
    train_km_per_day = (2 * 3600.0 / bundle["requirements"]["target_headway_s"]
                        * assumptions_record["operating_hours_per_day"] * route_m * trackways / 1000.0)
    service_trains = max(1, int(trainsets))

    # Occurrence-level vehicle manufacturing, including bounded raw-stock yield.
    body_stock_rows = [r for r in inventory["engineering_BOM"]
                       if r.get("scope") == "located-nominal-gross-body-stock"]
    body_mass = fsum(float(r["accounted_mass_kg"]) for r in body_stock_rows)
    body_process_hours = [0.0, 0.0, 0.0]
    for row in body_stock_rows:
        mass = float(row["accounted_mass_kg"])
        material_rates, rate_class = _material_rate(a, row.get("material_id"))
        yield_case = a["body_purchase_yield"]
        purchased_kg = [mass / yield_case[i] for i in range(3)]
        material_cost = [purchased_kg[i] * material_rates[i] for i in range(3)]
        process_hours = [mass * a["body_process_hours_per_kg"][i] + (0.02, 0.08, 0.25)[i] for i in range(3)]
        labour_cost = [process_hours[i] * loaded_wage[i] for i in range(3)]
        machine_hours = [mass * a["body_machine_hours_per_kg"][i] for i in range(3)]
        machine_cost = [machine_hours[i] * a["machine_rate_iqd_per_h"][i] for i in range(3)]
        quality_cost = [material_cost[i] * a["body_qa_fraction"][i] for i in range(3)]
        direct = [material_cost[i] + labour_cost[i] + machine_cost[i] + quality_cost[i] for i in range(3)]
        overhead_cost = [direct[i] * overhead[i] for i in range(3)]
        total = [direct[i] + overhead_cost[i] for i in range(3)]
        fleet_total = [v * fleet_cars for v in total]
        body_process_hours = _sum(body_process_hours, [v * fleet_cars for v in process_hours])
        _line(line_items, candidate_id=candidate_id, scope="rolling-stock", key="vehicle-stock/"+row["id"],
            quantity=dict(per_car_mass_kg=mass, fleet_net_stock_kg=_round([mass*fleet_cars]*3),
                fleet_purchase_stock_kg=_round([x*fleet_cars for x in purchased_kg])), unit="kg",
            totals=fleet_total, stage="factory-gate", basis="Occurrence gross stock mass × fleet cars ÷ explicit low/base/high cut yield; material, operation-hours/kg, machine-hours/kg, QA and one factory-overhead uplift.",
            source_ids=[row["component_definition_id"], identity(assumptions_record)],
            rate_evidence_class=rate_class, parts=[row["id"]],
            components=dict(material=[v*fleet_cars for v in material_cost], labour=[v*fleet_cars for v in labour_cost],
                equipment=[v*fleet_cars for v in machine_cost], QA=[v*fleet_cars for v in quality_cost],
                factory_overhead=[v*fleet_cars for v in overhead_cost]))

    account_rows = [r for r in inventory["engineering_BOM"]
                    if r.get("scope") == "retained-unlocated-reference-account"]
    retained_kg = fsum(float(r["accounted_mass_kg"]) for r in account_rows if r.get("accounted_mass_kg") is not None)
    for row in account_rows:
        mass = row.get("accounted_mass_kg")
        if mass is None:
            quantity = fleet_cars
            unit_cost = a["unknown_account_iqd_each"]
            totals = [quantity * unit_cost[i] for i in range(3)]
            process_hours = [quantity * a["unknown_account_process_hours_each"][i] for i in range(3)]
            qty = dict(per_car_unresolved_accounts=1, fleet_accounts=quantity,
                fleet_process_hours=_round(process_hours))
            basis = "Unknown inherited equipment mass: one explicit equipment-account allowance per fleet car; this cost proxy does not resolve installed mass or overlap."
        else:
            mass = float(mass)
            quantity = mass * fleet_cars
            unit_cost = a["finished_equipment_iqd_per_kg"]
            totals = [quantity * unit_cost[i] for i in range(3)]
            process_hours = [quantity * a["equipment_process_hours_per_kg"][i] for i in range(3)]
            qty = dict(per_car_accounted_mass_kg=mass, fleet_accounted_mass_kg=quantity,
                fleet_process_hours=_round(process_hours))
            basis = "Inherited unlocated account mass × fleet cars × finished-equipment proxy rate; mass remains an accounting balance, not a located BOM."
        body_process_hours = _sum(body_process_hours, process_hours)
        _line(line_items, candidate_id=candidate_id, scope="rolling-stock", key="retained-equipment/"+row["id"],
            quantity=qty, unit="accounted-kg-or-account", totals=totals, stage="factory-gate",
            basis=basis, source_ids=[row.get("component_definition_id") or identity(row), identity(assumptions_record)],
            rate_evidence_class="C", parts=[row["id"]])

    joint_ids = inventory["geometry_coverage"].get("unknown_joint_ids", [])
    joint_count = len(joint_ids) * fleet_cars
    if joint_count:
        joint_cost = [joint_count * a["joint_hardware_iqd_each"][i] for i in range(3)]
        joint_hours = [joint_count * a["joint_labour_h_each"][i] for i in range(3)]
        joint_labour = [joint_hours[i] * loaded_wage[i] for i in range(3)]
        totals = [joint_cost[i] + joint_labour[i] for i in range(3)]
        body_process_hours = _sum(body_process_hours, joint_hours)
        _line(line_items, candidate_id=candidate_id, scope="rolling-stock", key="unresolved-joint-hardware-and-assembly",
            quantity=dict(interfaces_per_car=len(joint_ids), fleet_interfaces=joint_count), unit="joint-interface",
            totals=totals, stage="factory-gate", basis="One Class C hardware/assembly package per declared interface; detailed fastener, end-cut and bond BOM remains open.",
            source_ids=[identity(inventory["geometry_coverage"]), identity(assumptions_record)], rate_evidence_class="C", parts=joint_ids,
            components=dict(hardware=joint_cost, labour=joint_labour))

    # Delivery and final assembly are separate from factory-gate body stock.
    # The haul quantity uses only accounted vehicle mass; a fixed per-train
    # logistics allowance covers unresolved fitout without implying its mass.
    accounted_fleet_t = float(bundle["mass"]["accounted_tare_kg_per_car"]) * fleet_cars / 1000.0
    vehicle_tonne_km = accounted_fleet_t * assumptions_record["outbound_route_km"]
    vehicle_haul = [vehicle_tonne_km * a["transport_iqd_per_tonne_km"][i] for i in range(3)]
    vehicle_logistics = [fleet_trainsets * a["vehicle_delivery_iqd_per_train"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="rolling-stock", key="accounted-vehicle-haul-and-delivery",
        quantity=dict(accounted_fleet_mass_t=accounted_fleet_t,
            assumed_haul_km=assumptions_record["outbound_route_km"], tonne_km=vehicle_tonne_km,
            fleet_trainsets=fleet_trainsets), unit="tonne-km-and-trainset", totals=[vehicle_haul[i]+vehicle_logistics[i] for i in range(3)],
        stage="delivered", basis="Known accounted fleet tare × assumed haul plus per-train Class C logistics allowance for unresolved fitout, permits and handling; incomplete vehicle mass remains explicitly open.",
        source_ids=[bundle["definition_id"], identity(assumptions_record)],
        components=dict(accounted_mass_haul=vehicle_haul, unresolved_fitout_logistics=vehicle_logistics))
    vehicle_install_hours = [fleet_cars * a["vehicle_install_hours_per_car"][i] for i in range(3)]
    vehicle_install_labour = [vehicle_install_hours[i] * loaded_wage[i] for i in range(3)]
    vehicle_install_equipment = [fleet_cars * a["vehicle_install_equipment_iqd_per_car"][i] for i in range(3)]
    vehicle_install = [vehicle_install_labour[i] + vehicle_install_equipment[i] for i in range(3)]
    body_process_hours = _sum(body_process_hours, vehicle_install_hours)
    _line(line_items, candidate_id=candidate_id, scope="rolling-stock", key="vehicle-final-assembly-and-installed-checkout",
        quantity=dict(fleet_cars=fleet_cars, labour_hours=_round(vehicle_install_hours)), unit="car", totals=vehicle_install, stage="installed",
        basis="Explicit final-assembly labour-hours per car at the loaded wage scenario plus handling/test equipment; unresolved interfaces and actual commissioning requirements remain unqualified.",
        source_ids=[identity(assumptions_record), *_benchmark_evidence(assumptions_record, "skilled_wage")], rate_evidence_class="B",
        components=dict(labour=vehicle_install_labour, equipment=vehicle_install_equipment))

    # Located station-motor primary stock and power conversion are costed by
    # candidate quantity; force-map, thermal and electrical qualification stay open.
    motor_length = float(coefficients.get("linear_motor_track_m") or 0.0) * trackways
    motor_mass_rate = propulsion_result.get("bare_primary_kg_per_m")
    wayside_process_hours = [0.0, 0.0, 0.0]
    peak_power_w = architecture_result.get("trajectory", {}).get("peak_required_power_W_train")
    if not _finite(peak_power_w) or peak_power_w <= 0:
        peak_force = architecture_result.get("trajectory", {}).get("peak_required_force_N_train")
        speed = bundle["requirements"]["speed_cap_m_s"]
        peak_power_w = float(peak_force or 0.0) * speed
    if _finite(motor_mass_rate) and motor_mass_rate > 0 and motor_length > 0:
        motor_kg = motor_length * float(motor_mass_rate)
        material = [motor_kg * a["motor_primary_iqd_per_kg"][i] for i in range(3)]
        hours = [motor_kg * a["motor_primary_hours_per_kg"][i] for i in range(3)]
        wayside_process_hours = _sum(wayside_process_hours, hours)
        labour = [hours[i] * loaded_wage[i] for i in range(3)]
        direct = [material[i] + labour[i] for i in range(3)]
        overhead_cost = [direct[i] * overhead[i] for i in range(3)]
        totals = [direct[i] + overhead_cost[i] for i in range(3)]
        _line(line_items, candidate_id=candidate_id, scope="stations-power", key="station-lim-primary-stock",
            quantity=dict(track_m=motor_length, primary_kg_per_m=float(motor_mass_rate), total_primary_kg=motor_kg),
            unit="kg-primary", totals=totals, stage="factory-gate",
            basis="Declared linear-primary mass per metre × installed track length for the two-trackway scenario; material/labour and one factory overhead factor. No thrust or heat qualification implied.",
            source_ids=[propulsion_result["evaluation_id"], identity(assumptions_record)],
            components=dict(material=material, labour=labour, factory_overhead=overhead_cost))
    elif bundle["family_id"] != "P6":
        # A changed propulsion family without mass geometry still receives a
        # nonzero, explicitly bounded package estimate instead of becoming zero.
        fallback = a["wayside_primary_package_iqd_per_train"].get(bundle["family_id"], [250000000, 1500000000, 8000000000])
        primary_hours = a["wayside_primary_process_hours_per_train"].get(bundle["family_id"], [250, 1000, 4000])
        wayside_process_hours = _sum(wayside_process_hours, [fleet_trainsets*primary_hours[i] for i in range(3)])
        _line(line_items, candidate_id=candidate_id, scope="stations-power", key="unlocated-wayside-propulsion-package",
            quantity=dict(trainsets=fleet_trainsets, motor_track_m=motor_length), unit="family-package",
            totals=[fleet_trainsets * fallback[i] for i in range(3)], stage="factory-gate",
            basis="Explicit Class C primary-side package proxy because wayside primary stock mass/geometry is unavailable; secondary and onboard obligations are costed separately under rolling stock.",
            source_ids=[bundle["propulsion_component_id"], identity(assumptions_record)], rate_evidence_class="C",
            parts=[x.get("id", x.get("description", "unlocated")) for x in inventory["unweighed_architecture_equipment"]])
    power_kw = max(1.0, float(peak_power_w or 0.0) / 1000.0) * trackways
    if bundle["family_id"] != "P6":
        converter_q = [power_kw * a["converter_power_margin"][i] for i in range(3)]
        converter_cost = [converter_q[i] * a["electrical_package_iqd_per_kw"][i] for i in range(3)]
        _line(line_items, candidate_id=candidate_id, scope="stations-power", key="traction-converter-capacity",
            quantity=dict(required_peak_kw=power_kw, installed_capacity_kw=_round(converter_q)), unit="kW-installed",
            totals=converter_cost, stage="factory-gate",
            basis="Required model peak power × parallel trackways × explicit overload margin; converter package rate is Class C and does not establish voltage/current/thermal performance.",
            source_ids=[architecture_result["evaluation_id"], identity(assumptions_record)])
    cable_cost = [motor_length * a["cable_iqd_per_motor_m"][i] for i in range(3)]
    if any(cable_cost) and bundle["family_id"] != "P6":
        _line(line_items, candidate_id=candidate_id, scope="stations-power", key="traction-feeders-and-protection",
            quantity=dict(motor_track_m=motor_length), unit="track-m", totals=cable_cost, stage="factory-gate",
            basis="Feeder/protection allowance per motor-track metre; conductor cross-sections, cable routes, cooling and fault duty remain unqualified.",
            source_ids=[propulsion_result["evaluation_id"], identity(assumptions_record)])
    if motor_length > 0 and bundle["family_id"] != "P6":
        primary_delivery = [motor_length*a["motor_primary_delivery_iqd_per_track_m"][i] for i in range(3)]
        _line(line_items, candidate_id=candidate_id, scope="stations-power", key="station-primary-delivery",
            quantity=dict(primary_track_m=motor_length), unit="track-m", totals=primary_delivery, stage="delivered",
            basis="Linear primary quantity × Class C packing, haul and handling rate; route constraints, protection and actual installation lifting remain open.",
            source_ids=[identity(propulsion_result), identity(assumptions_record)])
        primary_install = [motor_length*a["motor_primary_install_iqd_per_track_m"][i] for i in range(3)]
        _line(line_items, candidate_id=candidate_id, scope="stations-power", key="station-primary-installation-and-alignment",
            quantity=dict(primary_track_m=motor_length), unit="track-m", totals=primary_install, stage="installed",
            basis="Per-track-metre installation, alignment and connection allowance; civil interfaces, measured air gap and force performance remain unqualified.",
            source_ids=[identity(propulsion_result), identity(assumptions_record)])
    if bundle["family_id"] != "P6":
        converter_hours = [power_kw*a["converter_assembly_hours_per_kw"][i] for i in range(3)]
        wayside_process_hours = _sum(wayside_process_hours, converter_hours)
        electronics_install = [power_kw*a["power_electronics_install_iqd_per_kw"][i] for i in range(3)]
        _line(line_items, candidate_id=candidate_id, scope="stations-power", key="power-electronics-installation-and-checkout",
            quantity=dict(required_peak_kw=power_kw), unit="kW-required", totals=electronics_install, stage="installed",
            basis="Required analytical peak power × Class C installation and checkout rate; installed electrical duty and supplier configuration remain open.",
            source_ids=[architecture_result["evaluation_id"], identity(assumptions_record)])

    # Explicit family-level provisional package for obligations whose physical
    # components may overlap. One package per train avoids double-counting each
    # unweighed text obligation as a separate assembly.
    obligations = inventory.get("unweighed_architecture_equipment", [])
    if obligations:
        package = a["family_package_iqd_per_train"].get(bundle["family_id"], [250000000, 1500000000, 8000000000])
        totals = [fleet_trainsets * package[i] for i in range(3)]
        package_hours_per_train = a["family_package_process_hours_per_train"].get(bundle["family_id"], [250, 1000, 4000])
        package_hours = [fleet_trainsets*package_hours_per_train[i] for i in range(3)]
        body_process_hours = _sum(body_process_hours, package_hours)
        _line(line_items, candidate_id=candidate_id, scope="rolling-stock", key="unweighed-architecture-equipment-package",
            quantity=dict(fleet_trainsets=fleet_trainsets, nonoverlapping_packages=fleet_trainsets,
                obligation_ids=[r.get("id") for r in obligations], fleet_process_hours=_round(package_hours)), unit="trainset-package", totals=totals,
            stage="factory-gate", basis="One bundled Class C estimate per trainset jointly covers the listed potentially-overlapping equipment obligations; it is a cost allowance, not a mass or installed BOM.",
            source_ids=[identity(obligations), identity(assumptions_record)], rate_evidence_class="C",
            parts=[r.get("id", "unlocated") for r in obligations])

    # Precast beam bill of quantities. Iraqi-origin CSO concrete constituents,
    # wages and rebar rates are used where directly matched; other inputs remain C.
    guideway = bundle["architecture_case"]["physical_definition"]["guideway"]
    alternatives = civil_result.get("alternatives", [])
    beam = next((r for r in alternatives if r.get("family") == guideway.get("family") and r.get("load_case") == "crowd_control"), None)
    if beam is None:
        raise ValueError("Candidate guideway must match one generated crowd-control civil section")
    concrete_volume = float(beam["concrete_m3"]) * span_count
    cement_rate = assumptions_record["benchmark_rates_iqd"]["cement_iqd_per_t"]
    aggregate_rate = assumptions_record["benchmark_rates_iqd"]["aggregate_iqd_per_m3"]
    sand_rate = assumptions_record["benchmark_rates_iqd"]["sand_iqd_per_m3"]
    rebar_rate = assumptions_record["benchmark_rates_iqd"]["rebar_iqd_per_kg"]
    mix = a["concrete_cement_t_per_m3"]
    agg = a["concrete_aggregate_m3_per_m3"]
    sand = a["concrete_sand_m3_per_m3"]
    waste = a["concrete_waste_fraction"]
    cement_cost = [concrete_volume * mix[i] * (1+waste[i]) * cement_rate for i in range(3)]
    aggregate_cost = [concrete_volume * agg[i] * (1+waste[i]) * aggregate_rate for i in range(3)]
    sand_cost = [concrete_volume * sand[i] * (1+waste[i]) * sand_rate for i in range(3)]
    admixture_cost = [concrete_volume * a["concrete_admixture_iqd_per_m3"][i] for i in range(3)]
    concrete_total = [cement_cost[i]+aggregate_cost[i]+sand_cost[i]+admixture_cost[i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="guideway", key="precast-beam-concrete-recipe",
        quantity=dict(net_concrete_m3=concrete_volume, cement_t=_round([concrete_volume*x for x in mix]),
            aggregate_m3=_round([concrete_volume*x for x in agg]), sand_m3=_round([concrete_volume*x for x in sand])),
        unit="m3-concrete", totals=concrete_total, stage="factory-gate",
        basis="Candidate beam concrete volume × declared cement/aggregate/sand recipe and waste; dated CSO Iraqi-origin constituents plus assumed admixture. Mix is not qualified.",
        source_ids=[*evidence, *_benchmark_evidence(assumptions_record, "cement", "aggregate", "sand")],
        rate_evidence_class="B", components=dict(cement=cement_cost, aggregate=aggregate_cost, sand=sand_cost, admixture=admixture_cost))
    reinforcement_kg = float(beam["reinforcement_kg"]) * span_count
    rebar_cost = [reinforcement_kg * rebar_rate * a["material_rate_sensitivity"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="guideway", key="precast-reinforcement",
        quantity=dict(reinforcement_kg=reinforcement_kg), unit="kg-rebar", totals=rebar_cost, stage="factory-gate",
        basis="Generated preliminary bar mass × CSO Iraqi-origin rebar benchmark; bar schedule, grade, anchorage and laps remain unqualified.",
        source_ids=[*evidence, *_benchmark_evidence(assumptions_record, "rebar")], rate_evidence_class="B")
    specialty_cost = [0.0, 0.0, 0.0]
    for key, field in (("prestress", "prestress_kg"), ("prestress-anchorage", "prestress_anchorage_kg"),
                       ("rails", "running_rail_kg"), ("direct-fasteners", "direct_fastener_kg")):
        mass = float(beam.get(field, 0.0) or 0.0) * span_count
        if mass <= 0:
            continue
        unit = a["prestress_iqd_per_kg"] if key.startswith("prestress") else a["rail_iqd_per_kg"] if key == "rails" else a["steel_iqd_per_kg"]
        totals = [mass * unit[i] for i in range(3)]
        specialty_cost = _sum(specialty_cost, totals)
        _line(line_items, candidate_id=candidate_id, scope="guideway", key="precast-"+key,
            quantity=dict(mass_kg=mass), unit="kg", totals=totals, stage="factory-gate",
            basis="Candidate civil quantity × Class C rate for this specialist grade/form; design, origin and current availability remain unverified.",
            source_ids=[identity(beam), identity(assumptions_record)], rate_evidence_class="C")
    fastener_sets = int(beam.get("direct_fastener_sets", 0)) * span_count
    fastener_cost = [fastener_sets * a["fastener_iqd_per_set"][i] for i in range(3)]
    if fastener_sets:
        _line(line_items, candidate_id=candidate_id, scope="guideway", key="rail-fastener-sets",
            quantity=dict(sets=fastener_sets), unit="set", totals=fastener_cost, stage="factory-gate",
            basis="Counted preliminary fastener sets × explicit complete-set Class C rate; compatibility, clips, pads, anchors and installation remain open.",
            source_ids=[identity(beam), identity(assumptions_record)], rate_evidence_class="C")
    beam_hours = [span_count * a["beam_factory_hours_per_span"][i] for i in range(3)]
    beam_labour = [beam_hours[i] * loaded_wage[i] for i in range(3)]
    beam_machine = [span_count * a["beam_machine_iqd_per_span"][i] for i in range(3)]
    beam_qa = [span_count * a["beam_quality_iqd_per_span"][i] for i in range(3)]
    beam_direct = [concrete_total[i] + rebar_cost[i] + specialty_cost[i] + beam_labour[i] + beam_machine[i] + beam_qa[i]
                   + fastener_cost[i] for i in range(3)]
    beam_overhead = [beam_direct[i] * overhead[i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="guideway", key="beam-fabrication-crew-machine-and-QA",
        quantity=dict(spans=span_count, factory_hours=_round(beam_hours)), unit="span", totals=beam_labour,
        stage="factory-gate", basis="Bounded form, prestress handling, cast, cure, inspection and demould labour hours per generated span at the dated Al-Muthanna base-wage proxy plus assumed employer burden.",
        source_ids=[identity(beam), identity(assumptions_record), *_benchmark_evidence(assumptions_record, "skilled_wage")],
        rate_evidence_class="B", components=dict(labour=beam_labour))
    _line(line_items, candidate_id=candidate_id, scope="guideway", key="beam-factory-machine-QA-overhead",
        quantity=dict(spans=span_count), unit="span", totals=[beam_machine[i]+beam_qa[i]+beam_overhead[i] for i in range(3)],
        stage="factory-gate", basis="Declared per-span plant and inspection allowance plus a single 10/20/30 percent overhead on the non-overlapping beam factory subtotal.",
        source_ids=[identity(beam), identity(assumptions_record)],
        components=dict(equipment=beam_machine, QA=beam_qa, factory_overhead=beam_overhead))

    # Production capacity and tooling are calculated from the same BOM and span
    # quantities used in the cost lines.
    body_hours = body_process_hours
    workstation_capacity = production_years*production_days*assumptions_record["hours_per_shift"]*assumptions_record["shifts_per_day"]*assumptions_record["productive_utilisation"]
    body_cells = [max(1, ceil(h / workstation_capacity)) for h in body_hours]
    unique_body_operations = len({tuple(r.get("process_candidates", [])) for r in inventory["manufacturing_BOM"]})
    fixtures = max(1, unique_body_operations)
    fixture_cost = [fixtures * a["body_fixture_iqd_each"][i] for i in range(3)]
    vehicle_cell_cost = [body_cells[i] * a["vehicle_cell_iqd_each"][i] for i in range(3)]
    beam_moulds = [max(1, ceil(span_count * a["beam_mould_cycle_days"][i] /
                                   (production_years * production_days))) for i in range(3)]
    mould_cost = [beam_moulds[i] * a["beam_mould_iqd_each"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="factory-tooling", key="vehicle-cells-and-fixtures",
        quantity=dict(factory_cells=body_cells, fixture_sets=fixtures, target_years=production_years),
        unit="factory-equipment", totals=[fixture_cost[i]+vehicle_cell_cost[i] for i in range(3)], stage="capital",
        basis="Workstations = ceil candidate vehicle hours ÷ the declared production years, calendar, shifts and productive utilisation; fixture sets follow distinct declared process classes. Equipment rates are Class C.",
        source_ids=[identity(inventory["manufacturing_BOM"]), identity(assumptions_record)],
        components=dict(fixtures=fixture_cost, workcells=vehicle_cell_cost))
    guideway_cells = [max(1, ceil(beam_hours[i]/workstation_capacity)) for i in range(3)]
    guideway_cell_cost = [guideway_cells[i]*a["guideway_cell_iqd_each"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="factory-tooling", key="precast-production-cells",
        quantity=dict(factory_cells=guideway_cells, target_years=production_years,
            required_factory_hours=_round(beam_hours)), unit="factory-equipment",
        totals=guideway_cell_cost, stage="capital",
        basis="Dedicated concrete/steel preparation, prestressing, casting and QA workcell count = ceil generated guideway factory hours ÷ declared productive capacity; Class C equipment rate.",
        source_ids=[identity(beam), identity(assumptions_record)])
    station_power_cells = [ceil(wayside_process_hours[i]/workstation_capacity) for i in range(3)]
    if any(station_power_cells):
        station_power_cell_cost = [station_power_cells[i]*a["station_power_cell_iqd_each"][i] for i in range(3)]
        _line(line_items, candidate_id=candidate_id, scope="factory-tooling", key="station-drive-production-cells",
            quantity=dict(factory_cells=station_power_cells, target_years=production_years,
                required_factory_hours=_round(wayside_process_hours)), unit="factory-equipment",
            totals=station_power_cell_cost, stage="capital",
            basis="Dedicated winding, lamination, converter assembly and QA workcell count = ceil declared wayside propulsion process hours ÷ productive capacity; all hours and equipment prices are Class C.",
            source_ids=[propulsion_result["evaluation_id"], identity(assumptions_record)])
    _line(line_items, candidate_id=candidate_id, scope="factory-tooling", key="precast-beam-mould-sets",
        quantity=dict(spans=span_count, mould_sets=beam_moulds, cycle_days=a["beam_mould_cycle_days"]),
        unit="mould-set", totals=mould_cost, stage="capital",
        basis="Mould sets = ceil(span demand × cure/cycle days ÷ declared production years and working days); the cycle and mould prices are Class C hypotheses.",
        source_ids=[identity(beam), identity(assumptions_record)])

    # Foundations, piers and installation quantities are explicit bounded proxies
    # because route geotechnics and actual site surveys are not yet available.
    bearing_area = a["foundation_bearing_area_m2"]
    depth = a["foundation_depth_m"]
    footing_volume = [support_count * bearing_area[i] * depth[i] for i in range(3)]
    footing_concrete_cost = [footing_volume[i] * a["concrete_iqd_per_m3_fallback"][i] for i in range(3)]
    pier_volume = [support_count * a["pier_area_m2"][i] * a["pier_height_m"][i] for i in range(3)]
    pier_concrete_cost = [pier_volume[i] * a["concrete_iqd_per_m3_fallback"][i] for i in range(3)]
    foundation_rebar_kg = [footing_volume[i]*a["footing_rebar_kg_per_m3"][i]
                           + pier_volume[i]*a["footing_rebar_kg_per_m3"][i] for i in range(3)]
    foundation_rebar_cost = [foundation_rebar_kg[i] * rebar_rate * a["material_rate_sensitivity"][i] for i in range(3)]
    foundation_hours = [support_count * a["field_hours_per_support"][i] for i in range(3)]
    foundation_labour = [foundation_hours[i] * loaded_wage[i] for i in range(3)]
    foundation_total = [footing_concrete_cost[i]+pier_concrete_cost[i]+foundation_rebar_cost[i]+foundation_labour[i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="construction", key="foundation-footing-pier-proxy",
        quantity=dict(supports=support_count, footing_concrete_m3=_round(footing_volume), pier_concrete_m3=_round(pier_volume),
            reinforcement_kg=_round(foundation_rebar_kg), field_hours=_round(foundation_hours)), unit="support",
        totals=foundation_total, stage="installed", basis="Candidate span/support count × bounded bearing-area, depth, pier-section and reinforcement-density hypotheses; site geotechnics, utilities, seismic loads and settlement remain open.",
        source_ids=[identity(beam), identity(assumptions_record), *_benchmark_evidence(assumptions_record, "rebar", "skilled_wage")],
        rate_evidence_class="B", components=dict(footing_concrete=footing_concrete_cost, pier_concrete=pier_concrete_cost,
            reinforcement=foundation_rebar_cost, field_labour=foundation_labour))

    span_mass_t = float(beam["total_counted_span_mass_kg"]) / 1000.0
    transport_tonne_km = span_mass_t * span_count * assumptions_record["outbound_route_km"]
    transport_cost = [transport_tonne_km * a["transport_iqd_per_tonne_km"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="construction", key="beam-heavy-haul-to-site",
        quantity=dict(span_count=span_count, counted_span_mass_t=span_mass_t, assumed_haul_km=assumptions_record["outbound_route_km"],
            tonne_km=transport_tonne_km), unit="tonne-km", totals=transport_cost, stage="delivered",
        basis="Generated preliminary span mass × two-trackway span count × explicit 50 km haul assumption × Class C heavy-haul rate; trailer payload, route and permits are unknown.",
        source_ids=[identity(beam), identity(assumptions_record)])
    erection_days = [ceil(span_count / a["spans_per_crane_day"][i]) for i in range(3)]
    crane_cost = [erection_days[i] * a["erection_crane_iqd_per_day"][i] for i in range(3)]
    erection_hours = [span_count * a["erection_hours_per_span"][i] for i in range(3)]
    erection_labour = [erection_hours[i] * loaded_wage[i] for i in range(3)]
    rail_metres = route_m * trackways * 2
    rail_install = [rail_metres * a["rail_install_iqd_per_track_m"][i] for i in range(3)]
    construction_direct = [crane_cost[i]+erection_labour[i]+rail_install[i] for i in range(3)]
    construction_contingency = [construction_direct[i] * a["construction_contingency_fraction"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="construction", key="erection-rail-installation-and-temporary-works",
        quantity=dict(spans=span_count, crane_days=erection_days, field_hours=_round(erection_hours), rail_track_m=rail_metres),
        unit="span-and-track", totals=[construction_direct[i]+construction_contingency[i] for i in range(3)], stage="installed",
        basis="Span erection productivity × crane-day and field-crew rates plus two-rail track installation; one construction contingency is applied once to this direct construction scope.",
        source_ids=[identity(beam), identity(assumptions_record), *_benchmark_evidence(assumptions_record, "skilled_wage")],
        rate_evidence_class="B", components=dict(crane=crane_cost, labour=erection_labour, rail_installation=rail_install,
            contingency=construction_contingency))

    # Stations, land, utilities and depot use explicit geometry or bounded area
    # and unit-cost proxies; passenger protection/access allowances are retained.
    platform_m2 = [station_count * 2 * float(coefficients.get("platform_train_length_m") or
                         bundle["cars"]*bundle["car_length_m"]) * a["station_platform_width_m"][i] for i in range(3)]
    platform_cost = [platform_m2[i] * a["station_platform_iqd_per_m2"][i] for i in range(3)]
    access_cost = [station_count * a["station_access_iqd_each"][i] for i in range(3)]
    control_cost = [station_count * a["station_control_iqd_each"][i] for i in range(3)]
    station_install = [station_count * a["station_install_iqd_each"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="stations-power", key="stations-platform-access-protection-control",
        quantity=dict(stations=station_count, platform_area_m2=_round(platform_m2)), unit="station",
        totals=[platform_cost[i]+access_cost[i]+control_cost[i]+station_install[i] for i in range(3)], stage="installed",
        basis="Two platform sides per station; platform area uses declared 3/4/6 m width scenarios. Access, passenger-protection, controls, fire/egress and station installation remain Class C packages.",
        source_ids=[architecture_result["evaluation_id"], identity(assumptions_record)],
        components=dict(platform=platform_cost, accessible_access_and_protection=access_cost,
            controls=control_cost, station_installation=station_install))
    track_km = route_m * trackways / 1000.0
    land = [track_km * a["land_iqd_per_track_km"][i] for i in range(3)]
    utilities = [track_km * a["utilities_iqd_per_track_km"][i] for i in range(3)]
    depot = [fleet_trainsets * a["depot_iqd_per_trainset"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="land-utilities-depot", key="right-of-way-utility-and-depot-proxies",
        quantity=dict(track_km=track_km, fleet_trainsets=fleet_trainsets), unit="track-km-and-trainset",
        totals=[land[i]+utilities[i]+depot[i] for i in range(3)], stage="capital",
        basis="Two-trackway corridor length × explicit land/utility rate plus fleet-trainset depot package; there is no city survey, land valuation, utility design or depot geometry.",
        source_ids=[identity(assumptions_record)], components=dict(land=land, utilities=utilities, depot=depot))

    # Fleet staging is an explicit spares/commissioning package, separate from
    # manufacturing the vehicles already priced in rolling-stock.
    rolling_total = [fsum(r["scenario_iqd"][case] for r in _scope_rows(line_items, "rolling-stock", "factory-gate")) for case in CASES]
    fleet_spares = [rolling_total[i] * a["fleet_spares_fraction"][i] for i in range(3)]
    fleet_commission = [fleet_trainsets * a["fleet_commission_iqd_per_train"][i] for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="fleet", key="fleet-spares-commissioning-and-delivery",
        quantity=dict(trainsets=fleet_trainsets, spare_inventory_fraction=a["fleet_spares_fraction"]), unit="fleet-package",
        totals=[fleet_spares[i]+fleet_commission[i] for i in range(3)], stage="capital",
        basis="Spare-component inventory fraction on rolling-stock factory subtotal plus per-train commissioning; does not add duplicate vehicle quantity.",
        source_ids=[identity(assumptions_record)], components=dict(spare_inventory=fleet_spares, commissioning=fleet_commission))

    # Conditional service-energy calculation uses required model work, not an
    # available-force map. Fallback calculations are explicit when duty is absent.
    trajectory = architecture_result.get("trajectory", {})
    work_j = trajectory.get("traction_mechanical_energy_J_train")
    if not _finite(work_j) or work_j <= 0:
        mass_kg = float(bundle["mass"]["accounted_tare_kg_per_car"]) * cars_per_train
        speed = float(bundle["requirements"]["speed_cap_m_s"])
        work_j = 0.5 * mass_kg * speed**2
        energy_basis = "Fallback kinetic-energy lower-bound proxy from accounted train mass and speed cap; unavailable-force/thermal duty remains unqualified."
    else:
        energy_basis = "Required mechanical traction work from the analytical candidate journey, scaled by corridor segments; no motor map, losses or measured service duty is implied."
    segment_count = max(1, ceil(route_m / float(route["station_spacing_m"])))
    daily_runs = (2 * 3600.0 / bundle["requirements"]["target_headway_s"]
                  * assumptions_record["operating_hours_per_day"] * trackways)
    aux_kw = a["auxiliary_kw_per_car"]
    mechanical_kwh_year = (float(work_j) * segment_count / 3.6e6) * daily_runs * assumptions_record["operating_days_per_year"]
    auxiliary_kwh_year = [service_trains*cars_per_train*aux_kw[i]*assumptions_record["operating_hours_per_day"]
                          * assumptions_record["operating_days_per_year"] for i in range(3)]
    electrical_kwh_year = [mechanical_kwh_year / a["traction_efficiency"][i] + auxiliary_kwh_year[i] for i in range(3)]
    energy_cost_year = [electrical_kwh_year[i] * a["electricity_iqd_per_kwh"][i] for i in range(3)]
    annuity = fsum(1/(1+assumptions_record["real_discount_rate"])**y for y in range(1, years+1))
    energy_npv = [energy_cost_year[i] * annuity for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="energy", key="conditional-annual-electricity",
        quantity=dict(mechanical_traction_kwh_per_year=mechanical_kwh_year, auxiliary_kwh_per_year=_round(auxiliary_kwh_year),
            electricity_kwh_per_year=_round(electrical_kwh_year), annual_cost_iqd=_round(energy_cost_year)),
        unit="kWh/year", totals=energy_npv, stage="lifecycle", basis=energy_basis+
            " Annual operating hours, electricity tariff, traction efficiency and real discount rate are declared scenarios.",
        source_ids=[architecture_result["evaluation_id"], identity(assumptions_record)],
        components=dict(annual_energy_npv=energy_npv))

    staffed_shifts_per_day = assumptions_record["operating_hours_per_day"] / a["operations_shift_hours"]
    operations_staff = [
        (a["controllers_per_shift"][i] + station_count*a["station_staff_per_station_per_shift"][i])
        * staffed_shifts_per_day * a["operations_reliever_multiplier"][i] for i in range(3)]
    operations_hours_year = [operations_staff[i]*a["operations_shift_hours"]
        * assumptions_record["operating_days_per_year"] for i in range(3)]
    operations_cost_year = [operations_hours_year[i]*loaded_wage[i] for i in range(3)]
    operations_npv = [operations_cost_year[i]*annuity for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="operations", key="control-room-and-station-staffing",
        quantity=dict(stations=station_count, operating_hours_per_day=assumptions_record["operating_hours_per_day"],
            staff_per_covered_shift=_round([a["controllers_per_shift"][i]+station_count*a["station_staff_per_station_per_shift"][i] for i in range(3)]),
            annual_staff_hours=_round(operations_hours_year), annual_cost_iqd=_round(operations_cost_year)),
        unit="annual-staffing", totals=operations_npv, stage="lifecycle",
        basis="Explicit control-room and station staffing per shift × daily operating coverage × relief factor × loaded dated wage proxy, discounted for the declared 30-year life. Automation, staffing rules and city operations plans remain unknown.",
        source_ids=[identity(assumptions_record), *_benchmark_evidence(assumptions_record, "skilled_wage")],
        rate_evidence_class="B", components=dict(annual_staff_cost=operations_cost_year, NPV=operations_npv))

    initial_capex_by_scope = {scope: [fsum(r["scenario_iqd"][case] for r in _scope_rows(line_items, scope)
                                               if r["cost_stage"] in {"factory-gate", "delivered", "installed", "capital"})
                                     for case in CASES] for scope in SCOPES}
    maintenance_fraction = a["maintenance_fraction_per_year"]
    maintainable = [fsum(initial_capex_by_scope[s][case] for s in ("rolling-stock", "guideway", "stations-power"))
                    for case in range(3)]
    maintenance_year = [maintainable[i] * maintenance_fraction[i] for i in range(3)]
    maintenance_npv = [maintenance_year[i] * annuity for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="maintenance", key="planned-maintenance-and-spares-lifecycle",
        quantity=dict(years=years, maintainable_scope_iqd=_round(maintainable), annual_fraction=maintenance_fraction),
        unit="annual-maintenance-fraction", totals=maintenance_npv, stage="lifecycle",
        basis="Annual maintenance fraction on rolling-stock, guideway and station-power factory/installation cost; includes routine labour/consumables, not measured maintenance history.",
        source_ids=[identity(assumptions_record)], components=dict(annual_cost=maintenance_year, NPV=maintenance_npv))

    life_keys = (("rolling-stock", "rolling_stock"), ("stations-power", "motor_primary"),
                 ("stations-power", "power_electronics"), ("guideway", "guideway"),
                 ("stations-power", "stations"))
    renewal_total = [0.0, 0.0, 0.0]
    renewal_rows = []
    for scope, life_key in life_keys:
        capex = initial_capex_by_scope[scope]
        lives = a["asset_life_years"][life_key]
        values = []
        events = []
        for i in range(3):
            count = max(0, (years - 1) // int(lives[i]))
            cost = fsum(capex[i] / (1+assumptions_record["real_discount_rate"])**(int(lives[i])*n)
                        for n in range(1, count+1))
            values.append(cost)
            events.append(dict(case=CASES[i],life_years=lives[i],replacement_count=count))
        renewal_total = _sum(renewal_total, values)
        renewal_rows.extend(events)
    _line(line_items, candidate_id=candidate_id, scope="renewals", key="bounded-asset-replacements",
        quantity=dict(years=years, asset_life_events=renewal_rows), unit="replacement-NPV", totals=renewal_total,
        stage="lifecycle", basis="Discrete replacement events from explicit Class C asset-life scenarios; component lives are not qualified or measured.",
        source_ids=[identity(assumptions_record)])

    rescue = a["rescue_iqd_each"]
    rescue_standby_year = a["rescue_standby_iqd_per_year"]
    rescue_npv = [rescue[i] + rescue_standby_year[i] * annuity for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="recovery", key="rescue-unit-and-standby",
        quantity=dict(rescue_units=1, standby_years=years), unit="rescue-package", totals=rescue_npv,
        stage="lifecycle", basis="One rescue asset and annual standby allowance for the declared corridor; tow rating, access, response time and availability are unknown.",
        source_ids=[identity(assumptions_record)])
    reliability_year = [train_km_per_day * assumptions_record["operating_days_per_year"] * a["reliability_iqd_per_train_km"][i]
                        for i in range(3)]
    reliability_npv = [reliability_year[i] * annuity for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="reliability", key="service-disruption-and-corrective-reserve",
        quantity=dict(train_km_per_day=train_km_per_day, annual_train_km=train_km_per_day*assumptions_record["operating_days_per_year"],
            years=years), unit="train-km", totals=reliability_npv, stage="lifecycle",
        basis="Annual train-km × Class C corrective/disruption reserve rate; no observed failure rates, fares, passenger delay valuations or availability evidence.",
        source_ids=[identity(assumptions_record)])

    decommissioning_base = [fsum(r["scenario_iqd"][case] for r in line_items
        if r["cost_stage"] in {"factory-gate", "delivered", "installed", "capital"}) for case in CASES]
    disposal_cash = [decommissioning_base[i] * a["decommissioning_fraction_of_installed_CAPEX"][i] for i in range(3)]
    disposal_npv = [disposal_cash[i]/(1+assumptions_record["real_discount_rate"])**years for i in range(3)]
    _line(line_items, candidate_id=candidate_id, scope="disposal", key="end-of-life-decommissioning-proxy",
        quantity=dict(disposal_year=years, base_installed_CAPEX_iqd=_round(decommissioning_base),
            decommissioning_fraction=a["decommissioning_fraction_of_installed_CAPEX"], cash_cost_iqd=_round(disposal_cash)),
        unit="end-of-life-decommissioning", totals=disposal_npv, stage="lifecycle",
        basis="Year-30 removal and disposal fraction of declared installed CAPEX, discounted to estimate date; salvage, recycling value and site-specific demolition are excluded.",
        source_ids=[identity(assumptions_record)])

    scope_totals = {scope: [fsum(r["scenario_iqd"][case] for r in _scope_rows(line_items, scope))
                            for case in CASES] for scope in SCOPES}
    missing_scopes = [s for s in SCOPES if not _scope_rows(line_items, s)]
    if missing_scopes:
        raise ValueError("Cost model did not quantify required scope(s): " + ", ".join(missing_scopes))
    zero_scopes = [s for s in SCOPES if scope_totals[s][1] <= 0]
    if zero_scopes:
        raise ValueError("Required scopes need a positive declared base-case estimate: " + ", ".join(zero_scopes))
    factory_gate = [fsum(r["scenario_iqd"][case] for r in line_items
                         if r["cost_stage"] == "factory-gate") for case in CASES]
    delivered = [fsum(r["scenario_iqd"][case] for r in line_items
                      if r["cost_stage"] in {"factory-gate", "delivered"}) for case in CASES]
    installed = [fsum(r["scenario_iqd"][case] for r in line_items
                      if r["cost_stage"] in {"factory-gate", "delivered", "installed", "capital"}) for case in CASES]
    lifecycle = [installed[i] + energy_npv[i] + operations_npv[i] + maintenance_npv[i] + renewal_total[i]
                 + rescue_npv[i] + reliability_npv[i] + disposal_npv[i] for i in range(3)]
    for title, values in (("factory gate", factory_gate), ("delivered", delivered),
                          ("installed CAPEX", installed), ("whole life", lifecycle)):
        if values != sorted(values):
            raise ValueError("Low/base/high cost scenarios are not monotone for " + title)

    body_hours_total = body_process_hours
    guideway_hours_total = beam_hours
    production_cells = [body_cells[i] + guideway_cells[i] + station_power_cells[i] for i in range(3)]
    foundation_days = [ceil(support_count/a["foundation_supports_per_day"][i]) for i in range(3)]
    rail_install_days = [ceil(rail_metres/a["rail_track_m_per_day"][i]) for i in range(3)]
    station_install_days = [ceil(station_count/a["station_completions_per_day"][i]) for i in range(3)]
    construction_days = [max(foundation_days[i], erection_days[i], rail_install_days[i], station_install_days[i])
        for i in range(3)]
    factory_vehicle_guideway = [fsum(r["scenario_iqd"][case] for r in line_items
        if r["scope"] in {"rolling-stock", "guideway"} and r["cost_stage"] == "factory-gate") for case in CASES]
    factory_station_power = [fsum(r["scenario_iqd"][case] for r in line_items
        if r["scope"] == "stations-power" and r["cost_stage"] == "factory-gate") for case in CASES]
    result = dict(schema="osr-coupled-model-cost/1", candidate_id=candidate_id,
        input_evaluation_ids=input_ids, assumption_id=identity(assumptions_record),
        source_sha256=sources(root), currency="IQD", estimate_date=assumptions_record["estimate_date"],
        estimate_class="C", rate_evidence_summary=dict(B_statistical_records=7, C_engineering_assumptions=True,
            actual_supplier_quotes=0, FX_conversion_performed=False),
        model_cost_complete_for_declared_case=True, procurement_ready=False, physical_or_safety_accepted=False,
        model_cost_missing_scopes=missing_scopes, required_cost_scopes=list(SCOPES),
        physical_mass_complete=False, physical_journey_completed=False, service_qualified=False,
        corridor_basis=dict(directional_route_m=route_m, trackways=trackways, stations=station_count,
            span_m=span, span_count=span_count, support_count=support_count,
            cars_per_train=cars_per_train, normal_trainsets=trainsets, spare_trainsets=spares,
            fleet_trainsets=fleet_trainsets, fleet_cars=fleet_cars,
            target_headway_s=bundle["requirements"]["target_headway_s"],
            offered_capacity_pphpd=coefficients["offered_people_per_hour_direction"],
            service_equivalence="Nominal formation/headway/corridor arithmetic only; journey and access remain unqualified."),
        production_plan=dict(target_years=production_years, shifts_per_day=assumptions_record["shifts_per_day"],
            hours_per_shift=assumptions_record["hours_per_shift"],
            productive_utilisation=assumptions_record["productive_utilisation"], planned_working_days=production_years*production_days,
            vehicle_body_stock_kg_per_car=body_mass, retained_account_mass_kg_per_car=retained_kg,
            vehicle_process_hours_for_fleet=_round(body_hours_total), guideway_factory_hours=_round(guideway_hours_total),
            station_power_factory_hours=_round(wayside_process_hours),
            required_vehicle_workcells=body_cells, required_guideway_workcells=guideway_cells,
            required_station_power_workcells=station_power_cells,
            required_parallel_workcells=production_cells, guideway_mould_sets=beam_moulds,
            factory_gate_vehicle_and_guideway_IQD=_round(factory_vehicle_guideway),
            factory_gate_station_power_IQD=_round(factory_station_power),
            construction_duration_days=construction_days,
            construction_schedule_days=dict(foundations=foundation_days, span_erection=erection_days,
                rail_installation=rail_install_days, stations=station_install_days,
                critical_path_duration=construction_days),
            throughput_basis="Calculated from candidate gross stock, retained equipment, final vehicle assembly, propulsion and guideway process hours, declared shifts and production duration."),
        cost_line_items=line_items, scope_totals_iqd={k:_round(v) for k,v in scope_totals.items()},
        factory_gate_cost_iqd=_round(factory_gate), delivered_cost_iqd=_round(delivered),
        model_based_installed_CAPEX_iqd=_round(installed), model_based_whole_life_NPV_iqd=_round(lifecycle),
        annual_energy_iqd=_round(energy_cost_year), annual_operations_iqd=_round(operations_cost_year),
        annual_maintenance_iqd=_round(maintenance_year),
        annual_reliability_iqd=_round(reliability_year), annual_electricity_kwh=_round(electrical_kwh_year),
        lifecycle=dict(years=years, real_discount_rate=assumptions_record["real_discount_rate"],
            energy_NPV_iqd=_round(energy_npv), operations_NPV_iqd=_round(operations_npv),
            maintenance_NPV_iqd=_round(maintenance_npv),
            renewal_NPV_iqd=_round(renewal_total), recovery_NPV_iqd=_round(rescue_npv),
            reliability_NPV_iqd=_round(reliability_npv), disposal_NPV_iqd=_round(disposal_npv),
            initial_installed_CAPEX_iqd=_round(installed)),
        exclusions_and_proxy_gaps=[
            "City-specific alignment, access, geotechnical, land, utility and depot surveys",
            "Located replacement hardware and complete physical mass/CG/inertia remain open even where account allowances are priced",
            "LIM thrust/current/thermal duty, inverter ratings and safety protection are not validated by cost estimates",
            "Material classes, equipment internals, production yields, QA, site methods and lifetime rates are Class C assumptions",
            "No supplier quotations, taxes/duty, financing, FX conversion or procurement terms are included",
            "Required work and energy are conditional analytical quantities, not an available-force map or qualified operating duty",
        ], estimate_basis="Class C model-cost complete for this declared 6 km synthetic corridor; not a city budget, supplier offer, installed accepted cost or safe design.",
        **railway_bundle.FLAGS)
    result["evaluation_id"] = identity(result)
    return result


def compare(results):
    """Compare only matching declared service/corridor assumptions; never select."""
    if not isinstance(results, (list, tuple)) or not results:
        raise ValueError("Nonempty model-cost evaluations required")
    first = results[0]
    rows = []
    ids = set()
    for result in results:
        if (result.get("schema") != "osr-coupled-model-cost/1"
                or result.get("evaluation_id") != identity({k:v for k,v in result.items() if k != "evaluation_id"})):
            raise ValueError("Model-cost evaluation identity differs")
        if any(line.get("candidate_id") != result.get("candidate_id") for line in result.get("cost_line_items", [])):
            raise ValueError("Cost line belongs to another physical candidate")
        if result["candidate_id"] in ids:
            raise ValueError("One model-cost result per physical candidate required")
        ids.add(result["candidate_id"])
        if (result["currency"], result["estimate_date"], result["assumption_id"],
                result["corridor_basis"]["offered_capacity_pphpd"], result["corridor_basis"]["target_headway_s"],
                result["corridor_basis"]["directional_route_m"], result["corridor_basis"]["trackways"],
                result["corridor_basis"]["stations"]) != (
                first["currency"], first["estimate_date"], first["assumption_id"],
                first["corridor_basis"]["offered_capacity_pphpd"], first["corridor_basis"]["target_headway_s"],
                first["corridor_basis"]["directional_route_m"], first["corridor_basis"]["trackways"],
                first["corridor_basis"]["stations"]):
            raise ValueError("Equal currency, cost assumptions, route and nominal service context required")
        rows.append(dict(candidate_id=result["candidate_id"], evaluation_id=result["evaluation_id"],
            whole_life_NPV_iqd=result["model_based_whole_life_NPV_iqd"],
            installed_CAPEX_iqd=result["model_based_installed_CAPEX_iqd"],
            cost_class=result["estimate_class"], model_cost_complete=result["model_cost_complete_for_declared_case"]))
    edges, incomparable = [], []
    for i, a in enumerate(rows):
        for b in rows[i+1:]:
            av, bv = a["whole_life_NPV_iqd"], b["whole_life_NPV_iqd"]
            if av[2] < bv[0]:
                edges.append(dict(lower_cost_candidate_id=a["candidate_id"], higher_cost_candidate_id=b["candidate_id"]))
            elif bv[2] < av[0]:
                edges.append(dict(lower_cost_candidate_id=b["candidate_id"], higher_cost_candidate_id=a["candidate_id"]))
            else:
                incomparable.append(dict(candidate_a=a["candidate_id"], candidate_b=b["candidate_id"],
                    reason="Class C whole-life ranges overlap or trade off"))
    dominated = {r["higher_cost_candidate_id"] for r in edges}
    value = dict(schema="osr-coupled-model-cost-comparison/1", candidate_rows=rows,
        robustly_dominated_candidate_ids=sorted(dominated),
        nondominated_candidate_ids=[r["candidate_id"] for r in rows if r["candidate_id"] not in dominated],
        dominance_edges=edges, incomparable_pairs=incomparable,
        selection_purpose="Class C equal-nominal-service cost exploration only",
        integrated_winner=None, selected_reference_changed=False,
        physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
        manufacturing_release=False, operating_release=False)
    value["comparison_id"] = identity(value)
    return value

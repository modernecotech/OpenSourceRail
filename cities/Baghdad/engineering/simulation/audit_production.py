"""Workshop, purchasing and partial owner cash for one Airport audit configuration."""

from copy import deepcopy
from datetime import date
from hashlib import sha256
import json
from math import ceil, isclose, isfinite
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.prototype import car
from cities.Baghdad.engineering.simulation import airport_alignment, airport_demand, audit_feeder_cost, motion_power, production
from engineering.outline.baghdad_system import _id

CIVIL_DISPLACED = {"elevated-civil", "extra-haul", "extra-foundation", "exceptional-crossings", "yard-access", "tooling"}
FEEDER_LOTS = {
    "traction-line", "traction-sites", "offsite-feed", "opex-feeder", "six-site-parallel",
    "six-site-parallel-upkeep", "renewal-grid-site-power-electronics", "renewal-line-section-protection",
    "renewal-line-power-equipment", "renewal-midpoint-tie-equipment",
}
FEEDER_RENEWAL_LOTS = {lot for lot in FEEDER_LOTS if lot.startswith("renewal-")}
RISKS = {
    "civil and alignment": "Closure bays, utilities, exceptional crossings, ground treatment, yard access and owner possessions",
    "fleet and workshop": "Installed materials and labour, line-fit and recovery tooling, interfaces, rejects, freight and depot commissioning",
    "electricity and public supply": "Connection, protection and thermal designs, traction equipment, feeder upkeep, tariff and renewals",
    "opening and lifecycle": "Demand calibration, payroll and outage duty, independent approvals, delay and claims, financing, tax and duties",
}
SCOPE_UNIT = "constant 2026 USD"
MOTION_RECORD_ID = "production_day_record_id"
ROUTE_RATE_LOTS = {"signalling", "wayside-braking", "land-utilities"}
CURRENT_DRIVER_UNITS = {"sets": "trainsets", "track_km": "track-km", "grid_sites": "DC source groups",
                        "station_sites": "station sites"}


def seal_motion(day):
    """Seal a freshly emitted compact working day before passing or caching it."""
    if MOTION_RECORD_ID in day or "trace" in day or "events" in day:
        raise ValueError("Seal a fresh compact working-day result")
    return {**day, MOTION_RECORD_ID: _id(day)}


def require_identity(record, key, identity, description):
    body = {field: value for field, value in record.items() if field != key}
    if record.get(key) != identity(body):
        raise ValueError(f"{description} record identity does not match its content")


def quantity(value, label):
    if type(value) not in (int, float) or not isfinite(value) or value < 0:
        raise ValueError(f"Expected a finite nonnegative {label}")
    return value


def make_lot(lot_id, group, count, unit, prices, basis, *, year=None):
    return dict(lot_id=lot_id, group=group, quantity=count, source_unit=unit, usd=prices, year=year,
                cost_evidence=basis)


def replace_offers(rows, context, offers):
    """Replace complete matched lots. Retain custody and origin claims separately."""
    ledger = {}
    for row in rows:
        scope = dict(context=context, lot_id=row["lot_id"], group=row["group"], quantity=row["quantity"],
                     unit=row["current_unit"], operating_year=row["year"], currency=SCOPE_UNIT,
                     renewal_events=row.get("renewal_events"),
                     pricing_basis_id=_id(row))
        row["supplier_scope"] = scope
        row["scope_id"] = _id(scope)
        ledger[row["scope_id"]] = row
    offer_records = []
    used = set()
    offer_ids = set()
    for offer in offers:
        fields = {"offer_id", "supplier", "scope_id", "buyer_review_reference", "offer_sha256",
                  "price_usd", "claimed_domestic_value_usd"}
        if not isinstance(offer, dict) or offer.keys() != fields or any(
            not isinstance(offer[key], str) or not offer[key].strip()
            for key in fields - {"price_usd", "claimed_domestic_value_usd"}
        ):
            raise ValueError("Supplier return must identify the reviewed complete scope, supplier and offer")
        if len(offer["offer_sha256"]) != 64 or any(c not in "0123456789abcdef" for c in offer["offer_sha256"]):
            raise ValueError("Supplier offer needs its full document SHA-256")
        scope_id = offer["scope_id"]
        if scope_id not in ledger or scope_id in used or offer["offer_id"] in offer_ids:
            raise ValueError("Supplier return matches no unique complete lot in this audit")
        price = quantity(offer["price_usd"], "offered lot price")
        local = offer["claimed_domestic_value_usd"]
        if price == 0 or (local is not None and quantity(local, "claimed domestic value") > price):
            raise ValueError("Require a positive lot price and claimed origin value within that price")
        row = ledger[scope_id]
        offer_records.append(dict(offer=offer.copy(), submission_id=_id(offer), displaced_usd=row["usd"],
                                  verified_domestic_value_usd=None))
        row["usd"] = dict.fromkeys(production.PRICES, price)
        row["cost_evidence"] = "buyer-referenced offer input"
        used.add(scope_id)
        offer_ids.add(offer["offer_id"])
    return offer_records


def bind_current_rate_units(rows, length):
    """Carry archived units separately from the priced scope for this route."""
    for row in rows:
        if row["lot_id"] in ROUTE_RATE_LOTS:
            row.update(quantity=length, quantity_driver="route_km", current_unit="route-km")
        else:
            row["current_unit"] = CURRENT_DRIVER_UNITS.get(row.get("quantity_driver"), row["source_unit"])
        if row["group"] == "renewal-schedule":
            row["renewal_events"] = 1


def opening_year(completion_workday):
    """Use 250 production workdays per year and the owner's year-four opening assumption."""
    return max(4, 1 + ceil(completion_workday / 250))


def factory_disruption_phasing(rows, results, nominal_cash, paid_journeys, fare):
    """Rephase the same priced lots for each factory completion, without pricing disruption claims."""
    nominal_year = nominal_cash["service_start_year"]
    phasing = {}
    for name, result in results.items():
        finish = result["last_completion_workday"]
        year = opening_year(finish)
        profiles = (None if year == nominal_year else
                    production.cash_profile(rows, year, paid_journeys, fare, False)["profiles"])
        timing_delta = {
            case: 0 if profiles is None else
            profiles[case]["priced_30y_pv_usd"] - nominal_cash["profiles"][case]["priced_30y_pv_usd"]
            for case in production.PRICES
        }
        phasing[name] = dict(
            last_completion_workday=finish, material_delay_workdays=result["material_delay_workdays"],
            availability_factor=result["availability_factor"],
            first_article_scrap_gate=result["first_article_scrap_gate"],
            civil_beam_position_occupied_workdays=result["occupied_resource_workdays"].get("civil-beam-position", 0),
            civil_beam_position_peak=result["peak_resource_occupation"].get("civil-beam-position", 0),
            mould_dwell_hours=result["mould_dwell_hours"], mould_positions=result["mould_positions"],
            service_start_year=year, opening_slip_years=year - nominal_year,
            cash_profile_reference="cash.profiles" if profiles is None else None,
            price_profiles=profiles,
            priced_30y_pv_timing_delta_usd=timing_delta,
            **(nominal_cash["profiles"] if profiles is None else profiles)["base"],
            disruption_increment_usd=None,
        )
    return phasing


def cash_basis(price):
    """Seal one scoped nominal ledger before adding optional owner risk returns."""
    cash = price["cash"]
    return _id(dict(pricing_context=price["inputs"],
                    scoped_lots=[dict(scope_id=row["scope_id"], usd=row["usd"],
                                      offer_id=row.get("offer_id")) for row in price["pricings"]],
                    accepted_offer_ids=[row["submission_id"] for row in
                                        price.get("buyer_referenced_offers",
                                                  price.get("localisation", {}).get("buyer_referenced_offers", []))],
                    nominal_profiles_id=_id(cash["profiles"]),
                    discount_rate_real=cash["discount_rate_real"],
                    service_start_year=cash["service_start_year"]))


def owner_risk_sensitivity(risk_return, *, candidate_id, alignment_id, feeder_physical_id, civil_row_id, cash_basis_id,
                           unpriced_rows, nominal_cash, priced_rows, paid_journeys):
    """Keep an uncalibrated, scope-substituted purchaser stress separate from nominal cash."""
    if risk_return is None:
        return dict(status="no itemised return", calibration="none", lines=[], revised_profiles=None,
                    cash_basis_id=cash_basis_id)
    required = {"candidate_id", "alignment_id", "feeder_physical_id", "civil_row_id",
                "cash_basis_id", "currency", "basis_date", "calibration", "lines"}
    if not isinstance(risk_return, dict) or risk_return.keys() != required:
        raise ValueError("Owner risk return needs the complete candidate-bound header")
    if (risk_return["candidate_id"] != candidate_id or risk_return["alignment_id"] != alignment_id
            or risk_return["feeder_physical_id"] != feeder_physical_id
            or risk_return["civil_row_id"] != civil_row_id
            or risk_return["cash_basis_id"] != cash_basis_id
            or risk_return["currency"] != SCOPE_UNIT or risk_return["calibration"] != "uncalibrated"):
        raise ValueError("Owner risk return must match candidate, alignment, feeder, civil row, exact cash basis and constant 2026 USD")
    try:
        date.fromisoformat(risk_return["basis_date"])
    except (TypeError, ValueError):
        raise ValueError("Owner risk return needs an ISO basis date") from None
    if not isinstance(risk_return["lines"], list) or not risk_return["lines"]:
        raise ValueError("Owner risk return needs itemised exposure lines")
    open_lots = {row["lot_id"]: row for row in unpriced_rows}
    seen_ids, substituted = set(), set()
    direct = {case: sum(row["usd"][case] for row in priced_rows if row["group"] == "opening-direct")
              for case in production.PRICES}
    # The historical 20% contingency applies after design and test factors.
    contingency_pool = {case: nominal_cash["profiles"][case]["capital_usd"] * production.OPENING_CONTINGENCY_RATE
                        / (1 + production.OPENING_CONTINGENCY_RATE) for case in production.PRICES}
    allocated = dict.fromkeys(production.PRICES, 0)
    lines = []
    for line in risk_return["lines"]:
        fields = {"risk_id", "description", "evidence_basis", "cost_exclusions", "period",
                  "operating_year", "range_usd", "cash_treatment", "substitutes_unpriced_lot_id",
                  "historical_contingency_overlap_usd", "overlap_basis"}
        if not isinstance(line, dict) or line.keys() != fields:
            raise ValueError("Owner risk line needs complete scope, timing and overlap fields")
        if (any(not isinstance(line[key], str) or not line[key].strip()
                for key in ("risk_id", "description", "evidence_basis"))
                or not isinstance(line["cost_exclusions"], list) or not line["cost_exclusions"]
                or any(not isinstance(item, str) or not item.strip() for item in line["cost_exclusions"])):
            raise ValueError("Owner risk line needs an identified evidence basis and cost exclusions")
        if line["risk_id"] in seen_ids:
            raise ValueError("Owner risk IDs must be unique")
        seen_ids.add(line["risk_id"])
        period = line["period"]
        if period not in {"opening-direct", "first-full-year-operations", "renewal-schedule"}:
            raise ValueError("Owner risk period is outside the purchaser cash ledger")
        operating_year = line["operating_year"]
        if (period == "renewal-schedule" and (type(operating_year) is not int or not 1 <= operating_year <= 30)
                or period != "renewal-schedule" and operating_year is not None):
            raise ValueError("Owner risk renewal needs an operating year within the 30-year ledger")
        values = line["range_usd"]
        if not isinstance(values, dict) or set(values) != set(production.PRICES):
            raise ValueError("Owner risk needs low, base and high cost bounds")
        costs = {case: quantity(values[case], "owner risk cost") for case in production.PRICES}
        if not costs["low"] <= costs["base"] <= costs["high"]:
            raise ValueError("Owner risk cost bounds must be ordered")
        treatment = line["cash_treatment"]
        if treatment not in {"exposure-only", "substitute-unpriced-lot"}:
            raise ValueError("Owner risk cash treatment is unknown")
        replacement = line["substitutes_unpriced_lot_id"]
        overlap = line["historical_contingency_overlap_usd"]
        if treatment == "exposure-only":
            if replacement is not None or overlap is not None or line["overlap_basis"] is not None:
                raise ValueError("Exposure-only risks cannot change the priced cash ledger")
            net = None
        else:
            if replacement not in open_lots or replacement in substituted or open_lots[replacement]["group"] != period:
                raise ValueError("Risk cash substitution needs one matching unpriced lot")
            if (not isinstance(overlap, dict) or set(overlap) != set(production.PRICES)
                    or not isinstance(line["overlap_basis"], str) or not line["overlap_basis"].strip()):
                raise ValueError("Risk cash substitution needs documented historical contingency overlap")
            overlap = {case: quantity(overlap[case], "historical contingency overlap") for case in production.PRICES}
            if any(overlap[case] > costs[case] for case in production.PRICES):
                raise ValueError("Historical contingency overlap exceeds gross exposure")
            if period != "opening-direct" and any(overlap.values()):
                raise ValueError("Opening contingency cannot offset annual or renewal exposure")
            for case in production.PRICES:
                allocated[case] += overlap[case]
                if allocated[case] > contingency_pool[case]:
                    raise ValueError("Risk allocations exceed the existing historical contingency")
            net = {case: costs[case] - overlap[case] for case in production.PRICES}
            substituted.add(replacement)
        lines.append({**deepcopy(line), "net_increment_usd": net})

    revised = None
    if substituted:
        revised = {}
        start = nominal_cash["service_start_year"]
        for case in production.PRICES:
            profile = deepcopy(nominal_cash["profiles"][case])
            additions = []
            for year_row in profile["cash_by_year"]:
                year = year_row["year"]
                increment = {"capital_usd": 0, "opex_usd": 0, "renewals_usd": 0}
                for line in lines:
                    net = line["net_increment_usd"]
                    if net is None:
                        continue
                    target = (start - 1 if line["period"] == "opening-direct" else
                              start + line["operating_year"] - 1 if line["period"] == "renewal-schedule" else None)
                    if line["period"] == "first-full-year-operations" and year >= start:
                        increment["opex_usd"] += net[case]
                    elif year == target:
                        field = "capital_usd" if line["period"] == "opening-direct" else "renewals_usd"
                        increment[field] += net[case]
                additions.append({"year": year, **increment})
                for field, value in increment.items():
                    year_row[field] += value
            profile["capital_usd"] += sum(row["capital_usd"] for row in additions)
            profile["annual_opex_usd"] += sum(line["net_increment_usd"][case] for line in lines
                                              if line["net_increment_usd"] is not None and line["period"] == "first-full-year-operations")
            profile["annual_operating_support_usd"] = profile["annual_opex_usd"] - profile["annual_fares_usd"]
            profile["annual_subsidy_per_paid_journey_usd"] = (
                profile["annual_operating_support_usd"] / paid_journeys if paid_journeys else None)
            profile["priced_30y_pv_usd"] = sum(
                (row["capital_usd"] + row["opex_usd"] + row["renewals_usd"])
                / (1 + nominal_cash["discount_rate_real"]) ** row["year"]
                for row in profile["cash_by_year"])
            profile["risk_increment_cash_by_year"] = additions
            revised[case] = profile
    return dict(status="illustrative itemised owner exposure", calibration="uncalibrated; no observed local loss data",
                return_id=_id(risk_return), cash_basis_id=cash_basis_id,
                basis_date=risk_return["basis_date"], currency=SCOPE_UNIT,
                lines=lines, historical_contingency_pool_usd=contingency_pool,
                historical_contingency_allocated_usd=allocated, substituted_unpriced_lots=sorted(substituted),
                revised_profiles=revised, nominal_profile_reference="cash.profiles")


def evaluate(alignment, vehicle, motion, civil_row, *, civil_evaluation_id=None, topology=None,
             demand=None, supplier_offers=(), risk_return=None, renewal_return=None, renewal_directory=None):
    """Join explicitly bound audit records and keep each missing scope visible."""
    airport_alignment.validate(alignment)
    require_identity(vehicle, "evaluation_id", car.identity, "Vehicle audit")
    require_identity(motion, MOTION_RECORD_ID, _id, "Moving working day")
    require_identity(civil_row, "audit_row_id", family_comparison.digest, "Civil audit row")
    routes, shop, estimate, cam, opening, _, hashes = production.sources()
    parent = opening["candidate_id"]
    scenario, metrics = motion["scenario"], motion["metrics"]
    traction = motion["physical"]["feeder"]
    topology = traction["name"] if topology is None else topology
    length = alignment["route_km"]
    physical = vehicle["physical"]
    if (topology != traction["name"] or scenario["condition"] != "normal"
            or scenario.get("alignment_id") != alignment["alignment_id"]
            or motion["source_publication_candidate_id"] != parent
            or alignment["parent_candidate_id"] != parent
            or physical["parent_candidate_id"] != parent
            or civil_row["source_train_candidate_id"] != parent
            or tuple(scenario["chainages_m"]) != tuple(km*1000 for km in alignment["chainages_km"])
            or scenario["cars"] != physical["formation_cars"] or scenario["material"] != physical["material"]
            or not isclose(civil_row["route_km"], length, rel_tol=1e-12)
            or motion["physical"].get("upstream_candidate_id") != vehicle["candidate_id"]):
        raise ValueError("Production inputs must share the ordinary working day, Airport parent, formation and alignment")
    installed_id = civil_row.get("installed_vehicle_candidate_id")
    alternate_pack = vehicle["battery"].get("alternative")
    if (alternate_pack is not None or installed_id is not None) and installed_id != vehicle["candidate_id"]:
        raise ValueError("Civil actions and fleet procurement must use the same installed vehicle revision")
    for state in ("central", "high"):
        civil_mass = civil_row["load_case_train_kg"][state]
        if not isclose(civil_mass, vehicle["mass_cases"][state]["loaded_train_kg"], abs_tol=.01, rel_tol=1e-8):
            raise ValueError("Civil and vehicle audits use different axle load budgets")
    if not any(isclose(scenario["loaded_train_kg"], row["loaded_train_kg"], abs_tol=.01)
               for row in vehicle["mass_cases"].values()):
        raise ValueError("Working day motion uses a mass outside the audited train cases")

    cfg_path = airport_alignment.ROOT / "cities/Baghdad/system.toml"
    cfg_bytes = cfg_path.read_bytes()
    days = tomllib.loads(cfg_bytes.decode())["vehicle"]["service_days_per_year"]
    operated_km = quantity(motion.get("annual_train_km"), "operated train-km")
    source_energy = metrics.get("source_kwh")
    annual_dc = quantity(source_energy, "metered-side DC energy") * days
    booked_km = quantity(motion.get("booked_annual_train_km"), "booked train-km")
    distance_km = quantity(metrics.get("distance_km"), "daily train-km")
    if not isclose(operated_km, distance_km*days, abs_tol=.01):
        raise ValueError("Annual train-km and operating-day distance disagree")
    booked_trips = metrics.get("booked_passenger_trips")
    completed_trips = metrics.get("completed_passenger_trips")
    if (type(booked_trips) is not int or type(completed_trips) is not int
            or not 0 <= completed_trips <= booked_trips or booked_trips == 0
            or (motion["gates"]["all_workings_complete"] and completed_trips != booked_trips)):
        raise ValueError("Working-day booked and completed passenger trip counts disagree")
    nonrevenue_workings = {}
    for kind in ("positioning", "yard"):
        booked = metrics.get("booked_"+kind+"_trips")
        completed = metrics.get("completed_"+kind+"_trips")
        if type(booked) is not int or type(completed) is not int or not 0 <= completed <= booked:
            raise ValueError(f"Working-day booked and completed {kind} trip counts disagree")
        nonrevenue_workings[kind] = dict(booked=booked, completed=completed)
    booked_components = {
        kind: quantity(metrics.get(f"booked_{kind}_km"), f"booked daily {kind} train-km")
        for kind in ("passenger", "positioning", "yard")
    }
    if (not isclose(booked_components["passenger"], booked_trips*length, abs_tol=.01)
            or not isclose(booked_components["positioning"], nonrevenue_workings["positioning"]["booked"]*length, abs_tol=.01)
            or not isclose(booked_km, sum(booked_components.values())*days, abs_tol=.01)):
        raise ValueError("Booked train-km and working-day passenger, positioning and yard distances disagree")
    # The historical price register values supply on the utility side.
    rectifier_efficiency = .96
    annual_grid = annual_dc / rectifier_efficiency
    historic = opening["iraq_operations"]["cases"]["central"]
    paid_fraction = historic["paid_journeys"] / historic["all_journeys"]
    if demand is not None:
        airport_demand.validate(demand, alignment)
        if (motion["demand_basis"]["od_id"] != _id(demand["hourly_od"])
                or scenario["demand_evaluation_id"] != demand["evaluation_id"]):
            raise ValueError("Demand and moving service use different OD records")
        paid_fraction = demand["annual_paid_journeys"] / demand["annual_all_journeys"] if demand["annual_all_journeys"] else 0.
    served = quantity(metrics.get("boarded_passengers"), "completed journeys") * days
    paid = served * paid_fraction
    fare = historic["net_farebox_usd_m"] * 1e6 / historic["paid_journeys"]
    demand_basis = "The matched offered OD paying share is applied to completed journeys." if demand is not None else (
        "The published historical paying share is applied to completed journeys."
    )

    ref = production.reference_quantities(routes)
    counts = civil_row["quantities"]
    placements = counts["standard_placements"]
    supports = counts["standard_supports"] if placements else 0
    sets = metrics["fleet_sets_required"]
    station_sites = len(alignment["stops"])
    grid_sites = len(traction["sites"])
    cars = scenario["cars"] * sets
    q = dict(ref, sets=sets, cars=cars, bogies=2*cars, beams=counts["standard_beams"], piers=supports,
             bearings=counts["standard_bearings"], station_sites=station_sites, grid_sites=grid_sites,
             track_km=2*length, gateways=station_sites + grid_sites + 4*(grid_sites-1))
    span = civil_row["span_m"]
    schedule_q = dict(q, beams=placements)
    results = {}
    # The longer curing trial uses the same moulds, crews, and production order.
    # Only their occupied time changes, and the alternative cycle remains unverified.
    slow_routes = deepcopy(routes)
    slow_mould = next(r for r in slow_routes["resources"] if r["id"] == "civil-beam-position")
    slow_mould["load"][0]["hours"] = 48
    for name in (*production.SCENARIOS, "48h-mould-dwell"):
        slow_cycle = name == "48h-mould-dwell"
        plan = slow_routes if slow_cycle else routes
        scenario_name = "normal" if slow_cycle else name
        reject = production.SCENARIOS[scenario_name][2]
        result = deepcopy(production.cached_simulation(json.dumps(plan), tuple(sorted(schedule_q.items())),
                                                       scenario_name, span, scenario["material"]))
        result["completed_units"]["installed_standard_placements"] = result["completed_units"].pop("installed_beams", 0)
        result["stock"] = production.cam_stock(cam, cars, ref["cars"], reject)
        result["stock"]["basis"] = "Archived steel-pattern analogue" if scenario["material"] != "steel" else "Archived steel pattern"
        mould = next(r for r in plan["resources"] if r["id"] == "civil-beam-position")
        result["mould_dwell_hours"] = mould["load"][0]["hours"]
        result["mould_positions"] = mould["required_units"]
        if slow_cycle:
            result["process_assumption_status"] = "unverified 48-hour dwell sensitivity on unchanged mould count"
        results[name] = result

    # The historical engine supplies comparable residual price rates. Remove
    # overlapping civil, production tooling and feeder lots before cash.
    inputs = dict(topology="paired6" if topology == "paired6" else "radial30", span_m=10,
                  material=scenario["material"], annual_train_km=operated_km)
    priced, dropped = production.capital_and_operations(estimate, q, ref, inputs)
    omitted = CIVIL_DISPLACED | set(dropped)
    feeder_basis = motion_power.unit_cost_basis(motion)
    if feeder_basis["status"] != "planning estimate":
        omitted = omitted | FEEDER_LOTS
    renewal_rows, renewal_scope = audit_feeder_cost.renewal_rows(
        renewal_return, renewal_directory, alignment_id=alignment["alignment_id"], feeder=traction,
        track_km=q["track_km"])
    if renewal_rows:
        omitted = omitted | FEEDER_RENEWAL_LOTS
        archived = [row for row in estimate["lots"] if row["lot_id"] in FEEDER_RENEWAL_LOTS]
        renewal_scope["displaced_archived_allowances"] = [
            dict(lot_id=row["lot_id"], historical_operating_year=row["operating_year"],
                 historical_source_quantity=row["quantity"], historical_source_unit=row["unit"],
                 historical_planning_usd={case: row[f"{case}_usd"] for case in production.PRICES},
                 status="excluded from priced cash; replacement completeness and price remain open")
            for row in archived]
    rows = [dict(row, cost_evidence="historical planning rate transferred to audit scope") for row in priced
            if row["lot_id"] not in omitted]
    if alternate_pack is not None:
        # The archive includes the original pack inside the complete fleet amount.
        # Apply its same set/formation/material factors when removing the allowance.
        fleet = next(row for row in rows if row["lot_id"] == "fleet")
        service = tomllib.loads(cfg_bytes.decode())["service_power"]
        reference_pack_usd = service["battery_price_allocation_usd_m_per_train"] * 1e6
        removed = {case: reference_pack_usd * fleet["source_quantity"] * factor
                   for case, factor in fleet["factor"].items()}
        fleet["usd"] = {case: amount - removed[case] for case, amount in fleet["usd"].items()}
        fleet["excluded_scope"] = dict(lot_id="essential-service-battery", archived_allowance_usd=removed)
        rows.append(make_lot("essential-service-battery", "opening-direct", sets, "installed pack per trainset",
                             dict.fromkeys(production.PRICES, sets * alternate_pack["installed_price_usd"]),
                             "Candidate-specific installed battery input in constant 2026 USD"))
    saloon = vehicle.get("saloon_layout")
    if saloon is not None:
        fleet = next(row for row in rows if row["lot_id"] == "fleet")
        fleet["interior_takeoff"] = dict(
            cars=cars, fixed_seats=saloon["seats_per_car"] * cars,
            wheelchair_places=saloon["wheelchair_places_per_car"] * cars,
            standing_floor_m2=saloon["standing_area_m2_per_car"] * cars,
            installed_fitout_cost_usd=None, workcell_hours=None,
            scope="Quote the revised interior within the fleet lot, including fittings, accessible paths, installation and inspection.")
        fleet["cost_evidence"] = "Parent fleet planning rate. Revised interior and installation await a complete fleet quotation."
    energy = next(row for row in rows if row["lot_id"] == "opex-power")
    energy_source = next(row for row in estimate["lots"] if row["lot_id"] == "opex-power")
    energy["quantity"] = annual_grid/1e6
    energy["source_quantity"] = energy_source["source_quantity"]
    energy["factor"] = dict.fromkeys(production.PRICES, energy["quantity"]/energy["source_quantity"])
    energy["usd"] = {case: amount*energy["factor"][case] for case, amount in energy["usd"].items()}
    if feeder_basis["status"] != "planning estimate":
        rows.extend([
            make_lot("revised-feeder-package", "opening-direct", grid_sites, "site-count with attached line scope",
                     None, "no matched source"),
            make_lot("revised-feeder-upkeep", "first-full-year-operations", grid_sites, "site-count with attached line scope",
                     None, "no matched source"),
        ])
    rows.extend(renewal_rows)
    civil_cases = civil_row["standard_only_cost_cases"]
    civil_renewal = None
    if civil_cases is not None:
        has_subtotal = any(item["installed_usd"] is None for item in civil_cases.values())
        rows.append(make_lot("audited-standard-viaduct", "opening-direct", placements, "standard placements",
                             {case: item["known_installed_subtotal_usd"] for case, item in civil_cases.items()},
                             "known civil subtotal" if has_subtotal else "section and quantity rate comparison"))
        civil_renewal = dict(
            annual_inspections_usd={case: item["annual_inspection_usd"] for case, item in civil_cases.items()},
            bearing_renewal_at_operating_year=20,
            bearing_renewal_usd={case: item["year20_bearings_usd"] for case, item in civil_cases.items()},
            status="Reconcile annual inspections against the archived mixed O&M lot. Bearing replacement entered separately.",
        )
        rows.append(make_lot("audited-standard-bearing-renewal", "renewal-schedule", q["bearings"], "standard bearings",
                             civil_renewal["bearing_renewal_usd"], "section and quantity rate comparison", year=20))

    context = dict(alignment_id=alignment["alignment_id"], vehicle_candidate_id=vehicle["candidate_id"],
                   vehicle_duty_id=vehicle["duty_id"], motion_candidate_id=motion["candidate_id"],
                   working_day_record_id=motion[MOTION_RECORD_ID], motion_evaluation_id=motion["evaluation_id"],
                   demand_evaluation_id=scenario.get("demand_evaluation_id"),
                   civil_physical_id=civil_row["physical_id"], civil_row_id=civil_row["audit_row_id"],
                   civil_evaluation_id=civil_evaluation_id, feeder=traction, source_pricing=hashes["sourcing-estimate.json"])
    bind_current_rate_units(rows, length)
    offers = replace_offers(rows, context, supplier_offers)
    for row in rows:
        row["usd_per_current_unit"] = {case: price/row["quantity"] for case, price in row["usd"].items()} if (
            row["usd"] is not None and row["quantity"] > 0
        ) else None
    known = [row for row in rows if row["usd"] is not None]
    unpriced_by_group = {
        group: [row["lot_id"] for row in rows if row["group"] == group and row["usd"] is None]
        for group in ("opening-direct", "first-full-year-operations", "renewal-schedule")
    }
    # The installed equipment and its replacement timing are still design inputs.
    # Keep that exposure outside the offer ledger until a renewal event can be scoped.
    feeder_renewal = dict(lot_id="feeder-renewals", status="equipment and replacement timing required",
                          operating_year=None, usd=None)
    if renewal_scope is not None:
        feeder_renewal["status"] = renewal_scope["residual_status"]
    unpriced_by_group["renewal-schedule"].append(feeder_renewal["lot_id"])
    unpriced_lots = [lot for lots in unpriced_by_group.values() for lot in lots]
    if feeder_basis["status"] == "held":
        feeder_rows = {row["lot_id"]: row for row in rows}
        feeder_basis["audit_ledger"] = {
            kind: {key: feeder_rows[lot][key] for key in ("lot_id", "scope_id", "cost_evidence", "usd")}
            for kind, lot in (("opening", "revised-feeder-package"), ("annual_upkeep", "revised-feeder-upkeep"))
        }
    feeder_basis["renewals"] = feeder_renewal
    if renewal_scope is not None:
        feeder_basis["renewal_scope"] = renewal_scope
        if isinstance(risk_return, dict) and isinstance(risk_return.get("lines"), list) and any(
                isinstance(line, dict) and line.get("substitutes_unpriced_lot_id") == "feeder-renewals"
                for line in risk_return["lines"]):
            raise ValueError("Owner risk cannot substitute feeder-renewals over named replacement lots")
    for name, result in results.items():
        expected = (placements, supports, sets)
        actual = tuple(result["completed_units"].get(k, 0) for k in
                       ("installed_standard_placements", "pier_positions_assumed", "proved_sets"))
        if expected != actual:
            raise ArithmeticError(f"Schedule failed to reconcile standard placements, piers and fleet in {name}")
    starts = {name: opening_year(result["last_completion_workday"]) for name, result in results.items()}
    cash = production.cash_profile(known, starts["normal"], paid, fare, len(set(starts.values())) > 1)
    cash["scope"] = dict(status="priced subtotal", unpriced_lots_by_group=unpriced_by_group,
                         owner_exposures=RISKS)
    cash["sensitivity"]["status"] = "Illustrative input stress percentiles"
    cash["sensitivity"]["confidence_interval"] = None
    cash["disruption_phasing"] = factory_disruption_phasing(known, results, cash, paid, fare)
    cash_basis_id = cash_basis(dict(inputs=context, pricings=rows, cash=cash,
                                   buyer_referenced_offers=offers))
    cash["owner_risk_sensitivity"] = owner_risk_sensitivity(
        risk_return, candidate_id=vehicle["candidate_id"], alignment_id=alignment["alignment_id"],
        feeder_physical_id=_id(dict(alignment_id=alignment["alignment_id"], feeder=traction)),
        civil_row_id=civil_row["audit_row_id"], cash_basis_id=cash_basis_id,
        unpriced_rows=[row for row in rows if row["usd"] is None] +
        [{**feeder_renewal, "group": "renewal-schedule"}], nominal_cash=cash, priced_rows=known,
        paid_journeys=paid)
    local = production.localisation(shop, q, ref)
    local["displaced_parent_lot_addresses"] = sorted(omitted)
    local["buyer_referenced_offers"] = offers
    references = dict(alignment_record_id=alignment["record_id"], vehicle_evaluation_id=vehicle["evaluation_id"],
                      motion_evaluation_id=motion["evaluation_id"], demand_evaluation_id=scenario.get("demand_evaluation_id"),
                      motion_record_id=motion[MOTION_RECORD_ID],
                      civil_evaluation_id=civil_evaluation_id, civil_row_id=civil_row["audit_row_id"],
                      source_opening_evaluation_id=opening["evaluation_id"], factory_evaluation_id=routes["evaluation_id"],
                      shop_evaluation_id=shop["evaluation_id"], estimate_evaluation_id=estimate["evaluation_id"])
    model = dict(
        schema="baghdad-airport-audited-production/1", inputs=context, child_ids=references,
        quantities=q, standard_civil_quantities=counts, span_m=span, scenarios=results, cash=cash, pricings=rows,
        civil_quotation_screen_passed=civil_row["quotation_screen_passed"], civil_failed_checks=civil_row["failed_checks"],
        civil_lifecycle_reconciliation=civil_renewal, civil_closure_bay_m=civil_row["closure_bay_m"],
        closure_schedule_and_price=None, historical_displaced_lots=sorted(omitted), unpriced_lots=unpriced_lots,
        unpriced_quantities=dict(station_panels=q["station_panels"], rectifier_cabinets=q["rectifier_cabinets"],
                                site_ground_treatment=None, closure_bay_m=civil_row["closure_bay_m"]),
        feeder_scope=feeder_basis, localisation=local, owner_risks=RISKS,
        operation_basis=dict(operated_annual_train_km=operated_km, booked_annual_train_km=booked_km,
                             booked_annual_train_km_by_working={kind: kilometres*days
                                                               for kind, kilometres in booked_components.items()},
                             mileage_scope="Booked and operated train-km cover passenger, positioning and yard movements. Operated train-km uses actual replay distance, including any partial workings.",
                             annual_modelled_dc_source_kwh=annual_dc, annual_estimated_utility_kwh=annual_grid,
                             assumed_rectifier_efficiency=rectifier_efficiency, fleet_sets_required=sets,
                             annual_completed_journeys=served, annual_paid_journeys_proxy=paid,
                             net_usd_per_paid_journey=fare, fare_basis=demand_basis,
                             booked_working_day_passenger_trips=booked_trips,
                             completed_working_day_passenger_trips=completed_trips,
                             working_day_nonrevenue_trips=nonrevenue_workings,
                             annualisation_status="completed working day scaled to operating year" if motion["gates"]["all_workings_complete"]
                             else "partial working day scaled for cost sensitivity",
                             working_day_completed=motion["gates"]["all_workings_complete"], service_days=days),
        scope_notes=[
            "Revised girder quantities replace the older span-based civil cost. Casting, erection and transport hours use inherited workcell assumptions pending trial and contractor returns.",
            "Standard straight bays enter the workshop schedule and price. Site-specific end closures, temporary works and required capacity uprates remain open.",
            "The revised tooling allocation needs a split between civil moulds already in the viaduct rate and remaining depot and recovery scope.",
            "The inherited earliest-ready scheduler can resequence work when releases move. Use modeled completion differences as scheduling sensitivities.",
            "Opening allowances carry historical design, test and contingency factors. Tax, funding and owner risks require sourced returns.",
        ],
        source_sha256={**hashes, "cities/Baghdad/system.toml": sha256(cfg_bytes).hexdigest(),
                       "production.py": sha256(Path(production.__file__).read_bytes()).hexdigest(),
                       "audit_production.py": sha256(Path(__file__).read_bytes()).hexdigest()},
        complete_installed_price_usd=None, complete_owner_present_value_usd=None, physical_acceptance="open",
        financial_selection_eligible=False,
    )
    model["evaluation_id"] = _id(model)
    return model

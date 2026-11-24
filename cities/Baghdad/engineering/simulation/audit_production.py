"""Workshop, purchasing and partial owner cash for one Airport audit configuration."""

from copy import deepcopy
from hashlib import sha256
import json
from math import ceil, isclose, isfinite
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.prototype import car
from cities.Baghdad.engineering.simulation import airport_alignment, airport_demand, motion_power, production
from engineering.outline.baghdad_system import _id

CIVIL_DISPLACED = {"elevated-civil", "extra-haul", "extra-foundation", "exceptional-crossings", "yard-access", "tooling"}
FEEDER_LOTS = {
    "traction-line", "traction-sites", "offsite-feed", "opex-feeder", "six-site-parallel",
    "six-site-parallel-upkeep", "renewal-grid-site-power-electronics", "renewal-line-section-protection",
    "renewal-line-power-equipment", "renewal-midpoint-tie-equipment",
}
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


def evaluate(alignment, vehicle, motion, civil_row, *, civil_evaluation_id=None, topology=None,
             demand=None, supplier_offers=()):
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
    for name, (_, _, reject) in production.SCENARIOS.items():
        result = deepcopy(production.cached_simulation(json.dumps(routes), tuple(sorted(schedule_q.items())),
                                                       name, span, scenario["material"]))
        result["completed_units"]["installed_standard_placements"] = result["completed_units"].pop("installed_beams", 0)
        result["stock"] = production.cam_stock(cam, cars, ref["cars"], reject)
        result["stock"]["basis"] = "Archived steel-pattern analogue" if scenario["material"] != "steel" else "Archived steel pattern"
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
    rows = [dict(row, cost_evidence="historical planning rate transferred to audit scope") for row in priced
            if row["lot_id"] not in omitted]
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
    unpriced_by_group["renewal-schedule"].append(feeder_renewal["lot_id"])
    unpriced_lots = [lot for lots in unpriced_by_group.values() for lot in lots]
    if feeder_basis["status"] == "held":
        feeder_rows = {row["lot_id"]: row for row in rows}
        feeder_basis["audit_ledger"] = {
            kind: {key: feeder_rows[lot][key] for key in ("lot_id", "scope_id", "cost_evidence", "usd")}
            for kind, lot in (("opening", "revised-feeder-package"), ("annual_upkeep", "revised-feeder-upkeep"))
        }
    feeder_basis["renewals"] = feeder_renewal
    for name, result in results.items():
        expected = (placements, supports, sets)
        actual = tuple(result["completed_units"].get(k, 0) for k in
                       ("installed_standard_placements", "pier_positions_assumed", "proved_sets"))
        if expected != actual:
            raise ArithmeticError(f"Schedule failed to reconcile standard placements, piers and fleet in {name}")
    starts = {name: max(4, 1 + ceil(result["last_completion_workday"]/250)) for name, result in results.items()}
    cash = production.cash_profile(known, starts["normal"], paid, fare, len(set(starts.values())) > 1)
    cash["scope"] = dict(status="priced subtotal", unpriced_lots_by_group=unpriced_by_group,
                         owner_exposures=RISKS)
    cash["sensitivity"]["status"] = "Illustrative input stress percentiles"
    cash["sensitivity"]["confidence_interval"] = None
    cash["disruption_phasing"] = {
        name: dict(service_start_year=year,
                   **production.cash_profile(known, year, paid, fare, False)["profiles"]["base"],
                   disruption_increment_usd=None) for name, year in starts.items()
    }
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

"""Decision inputs, their authority, and the checks that govern the use of each result."""
from collections import defaultdict

from engineering.outline.baghdad_system import _id


# Units describe each field of the solver's normalized operating contract. Adding an
# input without explaining its engineering meaning must interrupt publication.
MOTION_UNITS = {
    "acceleration_m_s2":"m/s²", "alignment_id":"revision", "aux_w":"W", "auxiliary_kw":"kW",
    "braking_m_s2":"m/s²", "capacity":"passengers", "cars":"cars", "chainages_m":"m",
    "condition":"scenario", "conductor_factor":"ratio", "delay_s":"s", "demand_evaluation_id":"revision",
    "demand_factor":"ratio", "dwell_s":"s", "efficiency":"ratio", "failed_path":"bay index",
    "failed_site":"site index", "grade_pct":"%", "headway_min":"min", "length_m":"m",
    "loaded_train_kg":"kg", "material":"material", "phase_s":"s", "places_per_train":"passengers",
    "regen_efficiency":"ratio", "resistance_m_s2":"m/s²", "speed_m_s":"m/s", "step_s":"s",
    "tare_train_kg":"kg", "topology":"configuration", "traction_w":"W",
}
OPTIONAL_MOTION_UNITS = {"grade_basis": "scenario", "grade_profile": "chainage m, elevation m above datum, segment grade %"}
DEMAND_UNITS = {
    "response_per_min":"1/min", "waiting_time_weight":"ratio", "walking_time_weight":"ratio",
    "fare_usd":"USD", "value_of_time_usd_h":"USD/h", "walk_case":"scenario",
    "path_length_each_end_or_transfer_m":"m", "walking_speed_m_s":"m/s",
    "crossing_or_lift_wait_s_per_path":"s", "transfer_friction":"enabled",
    "transfer_share_at_interchange_od":"fraction", "transfer_fixed_penalty_min":"min",
    "connecting_headway_min":"min", "transfer_interchange_stop_ids":"stop IDs",
}
LAYOUTS = ("radial30", "paired6")
DEMAND_BASIS = {
    "fixed": "Requested journeys carry forward the historical hourly origin–destination matrix.",
    "service_sensitive": "Requested journeys respond to changes in expected wait and in-vehicle time.",
    "observed": "Requested journeys use the annualised sample for this booked offer.",
}


def group_duties(days):
    duties = defaultdict(list)
    for day in days:
        duties[day["topology"]].append(day)
    return duties


def register(route, demand, vehicle, civil, climate, configs, delivery, equipment=None):
    rows = []
    def add(key, value, unit, basis, source, revision, affects, verification, bounds=None):
        status = ("unknown" if value is None or basis == "open" else
                  "supplier declaration" if "offer input" in basis else
                  "observation submission" if basis == "observed" else "planning or calculated")
        origin = ("unknown" if status == "unknown" else "supplied" if status == "supplier declaration"
                  else "submitted observation" if status == "observation submission" else "estimated")
        rows.append(dict(id=key, value=value, unit=unit, basis=basis, evidence_maturity=status, evidence_type=origin,
                         policy_class="numerical_validity_domain" if key.endswith(".step_s") else "revisable_assumption",
                         source=source, revision=revision,
                         assessed_range=bounds, affects=affects, validation=verification))
    route_stages = ["service", "motion", "power", "civil", "workshop", "cash"]
    add("route.ordered_chainages", route["chainages_km"], "km", route["geometry_mode"], "airport_alignment.evaluate",
        route["alignment_id"], route_stages, "Survey centreline, entrances, grades, obstacles and land")
    profile = route["grade_profile"]
    add("route.vertical_profile", profile, "chainage m, elevation m above datum, segment grade %",
        "observed" if profile else "open", "airport_alignment.evaluate",
        route["alignment_id"], route_stages, "Survey longitudinal profile against the same horizontal trace")
    if route["survey_source"]:
        add("route.survey_submission", route["survey_source"], "document and geometry references",
            "observed", "airport_alignment.survey_input", route["alignment_id"], route_stages,
            "Authenticate the submitted survey and approve site and profile relevance")
    add("route.historical_nominal", route["historical_route_order_screen"]["nominal_km"], "km", "schematic assumption",
        "prototype service.json", route["parent_candidate_id"], route_stages, "Compare ordered geographic lower bound")
    derived_od = {"minutes", "reference_minutes", "demand_multiplier", "scope"}
    if set(demand["generalised_cost"]) != DEMAND_UNITS.keys() | derived_od:
        raise ValueError("Classify the changed generalised-cost parameters before publishing")
    for key, unit in DEMAND_UNITS.items():
        if key in demand["generalised_cost"]:
            add("demand."+key, demand["generalised_cost"][key], unit, "planning sensitivity", "airport_demand.evaluate",
                demand["evaluation_id"], ["passenger demand", "service", "fare", "cash"], "Calibrate against local passenger counts and journey surveys")
    add("demand.hourly_od", demand["evaluation_id"], "hourly passenger OD matrix reference", demand["mode"],
        "airport_demand.evaluate", demand["alignment_id"], ["passenger loads", "energy", "fare"],
        "Check station order, observation period, paying share and applicable headway")
    loads = vehicle["mass_cases"]
    for group, mass in loads["central"]["group_kg_per_car"].items():
        add("vehicle."+group, mass, "kg/car", "component allocation", "vehicle_civil.load_case",
            vehicle["candidate_id"], ["axle loads", "motion", "braking", "civil", "production"],
            "Obtain scoped installed BOM and measure equipped mass and axle reactions",
            [loads[state]["group_kg_per_car"][group] for state in ("low","central","high")])
    for key in ("nominal_kwh", "usable_at_80pct_retention_kwh", "demand_with_reserve_kwh"):
        add("battery."+key, vehicle["battery"][key], "kWh", "planning duty", "vehicle_audit.battery_case",
            vehicle["evaluation_id"], ["essential power", "equipment", "quote"], "Test hot aged pack at the required load")
    for key in ("wheel_adhesions","brake_delays_s","net_decelerations_m_s2","published_comparator_kn"):
        unit = dict(wheel_adhesions="ratio",brake_delays_s="s",net_decelerations_m_s2="m/s²",published_comparator_kn="kN/module")[key]
        add("brake."+key, vehicle["inputs"][key], unit, "trial duty", "vehicle_audit.evaluate", vehicle["duty_id"],
            ["stopping", "usable block length", "brake procurement"], "Measure force, response, heat and protected stopping distance")
    for key in ("doubled_loaded_distortion_margin_mm", "static_stack_margin_mm"):
        add("fit."+key, vehicle["fit"][key], "mm", "dimensional comparison", "vehicle_audit.fit_case",
            vehicle["evaluation_id"], ["assembly", "passenger interface"], "Measure fitted, loaded and worn geometry")
    for group, units in {
        "hvac":{"ambient_c":"°C","setpoint_c":"°C","outdoor_relative_humidity":"fraction","cop":"ratio",
                "required_cooling_kw_thermal":"kW thermal","trial_derated_cooling_kw_thermal":"kW thermal",
                "actual_installed_cooling_kw_thermal":"kW thermal","fan_kw":"kW"},
        "door_exchange":{"doors_active":"doors","assisted_transfer_trial_s":"s","opening_and_proving_s":"s",
                         "required_door_clear_m":"m","measured_step_m":"m","measured_gap_m":"m",
                         "total_dwell_with_one_assisted_transfer_s":"s"},
    }.items():
        for key, unit in units.items():
            add(group+"."+key, climate[group][key], unit, "passenger interface study",
                "passengers.evaluate", climate["evaluation_id"], ["station dwell", "auxiliary power", "accessibility"],
                "Inspect installed interface and record performance at declared temperature and passenger load")
    for cfg in configs:
        cfg = {"positioning_slack_s":0, **cfg}
        units = {**MOTION_UNITS, "positioning_slack_s":"s",
                 **{key: unit for key, unit in OPTIONAL_MOTION_UNITS.items() if key in cfg}}
        if set(cfg) != set(units):
            raise ValueError(f"Unclassified normalized motion inputs: {set(cfg) ^ set(units)}")
        for key, value in cfg.items():
            add("motion."+cfg["topology"]+"."+key, value, units[key], "normalized study input",
                "motion_power.normalize", _id(cfg), ["working day", "feeder duty", "operating costs"],
                "Verify against route, train, control settings and instrumented working day")
    for key, unit in (("soil_kpa","kPa"),("lift_radius_m","m"),("crane_limit_t","t at radius"),
                      ("service_moving_load_factor","ratio")):
        add("civil."+key, civil[key], unit, "trial design input", "family_comparison.evaluate_high_load",
            civil["input_id"], ["structure", "installation", "cash"], "Obtain ground investigation, reviewed design and lift chart")
    for layout, model in delivery.items():
        cash = model["cash"]
        for key, unit in (("discount_rate_real", "fraction/year"), ("service_start_year", "relative year"),
                          ("constant_currency","currency and price year")):
            add("finance."+layout+"."+key, cash[key], unit, "scenario assumption", "production.cash_profile",
                model["evaluation_id"], ["cash", "lifecycle cost"], "Reconcile phasing and finance terms against buyer obligations")
        for key, value in model["quantities"].items():
            add("production."+layout+"."+key, value, "track-km" if key=="track_km" else "count",
                "workshop planning quantity", "audit_production.evaluate", model["evaluation_id"],
                ["work cells","procurement","cash"], "Reconcile release drawings, accepted articles and offers")
        for lot in model["pricings"]:
            add("price."+layout+"."+lot["lot_id"], lot["usd"], "2026 USD per scoped lot",
                lot["cost_evidence"], "audit_production.evaluate and scope "+lot["scope_id"],
                model["evaluation_id"], ["procurement","cash","contract renewal"],
                f"Verify {lot['quantity']} {lot['current_unit']} against the return and applicable operating year.")
        for key, unit in (("service_days","days/year"), ("assumed_rectifier_efficiency","ratio"),
                          ("net_usd_per_paid_journey","USD/journey")):
            add("cash."+layout+"."+key, model["operation_basis"][key], unit, "transferred operating assumption",
                "audit_production.evaluate", model["evaluation_id"], ["revenue","energy","cash"],
                "Reconcile service calendar, utility meter and fare ledger")
        add("cash."+layout+".owner_risks", model["owner_risks"], "unpriced exposures", "open",
            "audit_production.RISKS", model["evaluation_id"], ["purchaser cash", "financing"],
            "Return scope, currency, date, quantities, rates, terms and risk owners")
    for ident, item in (equipment or {}).get("layouts", {}).items():
        feeder = item["feeder_physical"]["feeder"]
        units = {"sites":"m", "droop":"Ω", "outward":"Ω/km","return_path":"Ω/km", "paths":"count", "trunk_factor":"ratio"}
        for key, unit in units.items():
            add("feeder."+feeder["name"]+"."+key, feeder[key], unit, "feeder layout and circuit assumption",
                "motion_power.make_feeder and motion_dc.Feeder", ident, ["DC voltage", "working day", "protection", "price"],
                "Survey site locations, measure circuit resistance, and match equipment and utility duty.")
    # Preserve the maturity of the operands when giving a derived value its
    # own unit and identity. A calculated value can still depend on estimates.
    calculated = {"route.ordered_chainages", "battery.usable_at_80pct_retention_kwh", "battery.demand_with_reserve_kwh"}
    derived_motion = {"aux_w","auxiliary_kw","chainages_m","length_m","loaded_train_kg","tare_train_kg","traction_w"}
    for row in rows:
        key = row["id"]
        if row["value"] is not None and (key in calculated or key.startswith("fit.")
                or key.startswith("motion.") and key.rsplit(".",1)[-1] in derived_motion
                or key.startswith("production.") or key.endswith(".required_cooling_kw_thermal")
                or key.endswith(".total_dwell_with_one_assisted_transfer_s")):
            row["evidence_type"] = "calculated"
    return rows


def completion_tests(route, demand, girder, delivery):
    """Record each digital result alongside its outstanding release evidence."""
    alignment_result = "Horizontal distance and stop-order screen"
    if route["survey_source"]:
        alignment_result = "Submitted horizontal geometry"
        if route["grade_profile"]:
            alignment_result = "Submitted horizontal and vertical geometry"
    service_result = {
        "observed": "Submitted OD replay",
        "fixed": "Fixed-demand working days",
        "service_sensitive": "Service-sensitive working days",
    }[demand["mode"]]
    return [
        dict(task="A01", work="Integration", result="Scoped input register and candidate joins",
             outstanding="Review submitted replacements against their exact alignment, formation, equipment and lot scope."),
        dict(task="A02", work="Alignment", result=alignment_result,
             outstanding="Approve surveyed levels, curves, utility and land interfaces, and all station sites."),
        dict(task="A03", work="Passenger service", result=service_result,
             outstanding="Authenticate local counts and travel times and calibrate demand response."),
        dict(task="A04", work="Braking", result="Stopping distance, failed-module force and heat bounds",
             outstanding="Measure braking and wheel-slide duty and verify protected stopping distance and recovery."),
        dict(task="A05", work="Vehicle and interfaces", result="Loaded mass, axle, battery and fit screens",
             outstanding="Weigh the equipped article and measure loaded door, suspension, removal and hot aged battery duty."),
        dict(task="A06", work="Electrical supply", result="Matched ordinary, hot and outage working days",
             outstanding="Review equipment duty, protection clearing, return circuits, safe isolation and utility terms."),
        dict(task="A07", work="Civil and erection", result="Priced stock and erection comparison" if girder
             else "No priced comparison for the requested civil scope",
             outstanding="Obtain ground and access data, signed lift chart, verified prestress, fatigue, shear, bearing and staged erection designs."),
        dict(task="A08", work="Production and procurement", result="Ordinary and disrupted workshop schedules" if delivery
             else "Workshop comparison pending a priced civil scope",
             outstanding="Return matched shop offers, measured process cycles and first-article inspection records."),
        dict(task="A09", work="Economics", result="Scoped capital and 30-year cash subtotals" if delivery
             else "Cash comparison pending a priced civil scope",
             outstanding="Complete unpriced owner, installation and renewal scope and calibrate risk and funding terms."),
        dict(task="A10", work="Independent review and publication", result="Reproducible review with a native replay receipt for the published defaults",
             outstanding="Run the exact edition in a clean installation and obtain independent physical review before release."),
    ]


def disposition(route, demand, vehicle, days, girder, delivery):
    """Gates for this issue. Missing or failed evidence excludes a production choice."""
    if not days or len({(r["condition"], r["topology"]) for r in days}) != len(days):
        raise ValueError("No power cases or duplicated duty")
    from . import motion_power
    expected = {(condition, layout) for condition in motion_power.CONDITIONS for layout in LAYOUTS}
    if expected != {(r["condition"],r["topology"]) for r in days}:
        raise ValueError("Required matched normal and degraded comparisons are incomplete")
    holds = {
        "alignment": route["review_gaps"],
        "demand": ["Validate hourly and directional demand and calibrate the response to changed service."],
        "stopping and vehicle": vehicle["physical_measurements_required"],
        "traction supply": ["Obtain converter duty, transient fault clearing, thermal ratings, return voltages, safe isolation and utility terms."],
        "civil": ["Review the closure, temporary works, foundations, torsion, shear, fatigue, bearings and prestress."],
        "procurement": ["Match the installed construction scope, production capacity, operation and renewals to supplier returns."],
    }
    layout_results = {}
    obligations = {"protection_approved", "thermal_ratings_verified", "utility_connection_approved"}
    grouped = group_duties(days)
    for layout in LAYOUTS:
        by_condition = {row["condition"]: row for row in grouped[layout]}
        conditions = [by_condition[key] for key in motion_power.CONDITIONS]
        for row in conditions:
            if set(row["failed_screens"]) != {key for key, met in row["gates"].items() if not met}:
                raise ValueError("Recorded power failures differ from the case gates")
        failures = {r["condition"]:[k for k in r["failed_screens"] if k not in obligations] for r in conditions}
        approval = {k:all(r["gates"][k] for r in conditions) for k in sorted(obligations)}
        scope = delivery.get(layout)
        physical = dict(alignment=route["alignment_id"], train=vehicle["candidate_id"],
                        feeder=conditions[0]["candidate_id"], civil=girder["physical_id"] if girder else None)
        if len({r["candidate_id"] for r in conditions}) != 1:
            raise ValueError("Supply duties returned different physical candidates")
        layout_results[layout] = dict(physical_candidate_id=_id(physical), assemblies=physical,
            numerical_valid=all(r["numerical_valid"] for r in conditions),
            operating_screen="failed" if any(failures.values()) else "passed",
            failures_by_duty=failures, supplier_and_utility_checks=approval,
            scope_cost_status="complete" if scope and scope["complete_installed_price_usd"] is not None else "partial or unpriced",
            remaining_cost_scope=scope["unpriced_lots"] if scope else None,
            qualification="open", investment_rank=None)
    return dict(candidates=layout_results, historical_alignment_screen=route["historical_route_order_screen"]["screen_passed"],
                digital_reference="review issue; physical release held", evidence_holds=holds,
                completion_tests=completion_tests(route, demand, girder, delivery), partial_cost_layouts=list(delivery),
                numerically_valid_days=sum(r["numerical_valid"] for r in days),
                passing_operational_days=sum(all(v for k,v in r["gates"].items()
                    if k not in ("protection_approved","thermal_ratings_verified","utility_connection_approved")) for r in days),
                civil_enquiry=None if girder is None else girder["label"],
                investment_selection=None, fabrication_release=False, physical_acceptance=False)


def cost_bands(prices, key):
    values = (prices["cases"][band][key] for band in ("low", "base", "high"))
    return " / ".join("unknown" if value is None else f"${value/1e6:,.2f}m" for value in values)


def markdown(data):
    route, vehicle = data["alignment"], data["vehicle"]
    hist = data["historical_route"]
    route_provenance = (
        f"The submitted alignment is {route['route_km']:.2f} km long. Approval of station sites and geometry remains open."
        if route["survey_source"] else
        f"The revised {route['route_km']:.2f} km horizontal study includes {route['mapped_road_reference_km']:.2f} km of road reference "
        f"and {route['review_connector_km']:.2f} km of proposed connections. Um Al Tubol still needs a site."
    )
    lines = ["# Railway assumption audit results", "",
             f"The original {hist['nominal_km']:g} km schematic falls {hist['bound_minus_nominal_km']:.2f} km short of the geographic minimum through five stops in order. "
             + route_provenance + " Investment selection and first-article fabrication remain held.", "",
             "## Which service can the terminal handle?", "",
             DEMAND_BASIS[data["demand"]["mode"]] + " The terminal search tests 30-second phase offsets. "
             "The moving replay includes depot movements, track reservations and actual station calls.", "",
             "| Headway | Booked dwell | Normal places per train | Annual requested journeys | Initial diagram → trial conflicts | Terminal offset | Completed / booked trips on paired supply |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for h, r in data["service_offers"].items():
        p, day = r["phases"], r["ordinary"]
        original = p["as_booked"].get("conflicts", "unavailable")
        lines.append(f"| {h} min | {r['dwell_s']:g} s | {r['normal_places_per_train']:,} | {r['annual_requested']:,.0f} | "
                     f"{original} → {p['best']['conflicts']} | {p['best']['phase_s']} s | {day['completed']} / {day['booked']} |")
    selected = data["demand"]["headway_min"]
    timing = data["service_offers"][selected]["phases"]["best"]
    lines += ["", f"The detailed comparison uses the {selected}-minute offer with a {timing['phase_s']} s terminal offset and {timing.get('positioning_slack_s',0)} s additional time for the first and last empty movements. "
              "These terminal offsets apply to the evaluated offers.",
              "", "The paired-supply replay gives these maximum arrival delays at each simulation step. " +
              ", ".join(f"{s} s step → {d['maximum_delay_s']:.0f} s delay" if d["maximum_delay_s"] is not None else f"{s} s step → no arrivals" for s,d in data["step_trials"].items())+".",
              "", "## What happens when a feeder fails?", "",
              "The two layouts use the same train, stops, demand, dwell and terminal phase. Voltages refer to live collectors. An isolated section can prevent service even when the remaining live collectors have adequate voltage.", "",
              "| Feed layout | Working condition | Trips finished / booked | Minimum V | Peak site kA | Branch RMS bound kA |",
              "| --- | --- | ---: | ---: | ---: | ---: |"]
    for d in data["power_days"]:
        v = f"{d['minimum_v']:,.1f}" if d["minimum_v"] is not None else "unavailable"
        lines.append(f"| {d['topology']} | {d['condition']} | {d['completed']} / {d['booked']} | {v} | {d['peak_site_ka']:.2f} | {d['rms_branch_ka']:.2f} |")
    lines += ["", "The combined-outage stress replay uses the high installed-mass allocation, a 2% constant grade and the same passenger offer. It tests additional sites and lower conductor resistance on the same route. Peak currents are equipment enquiries. Protection clearing and conductor temperature still require equipment data.", "",
              "| Stress layout | Trips finished / booked | Minimum live voltage | Peak site kA | Maximum arrival delay |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for d in data["high_mass_power"]:
        volts = f"{d['minimum_v']:.1f} V" if d["minimum_v"] is not None else "Open"
        delay = f"{d['maximum_delay_s']:.0f} s" if d["maximum_delay_s"] is not None else "No arrivals"
        lines.append(f"| {d['topology']} | {d['completed']} / {d['booked']} | {volts} | {d['peak_site_ka']:.2f} | {delay} |")
    lines += ["", "Use `--supply-return` with an exact feeder ID to check supplied peak and RMS current ratings, protection settings and fault duties. The assessment keeps missing equipment and site data open. [Return format and worked checks](test_audit_power_return.py)"]
    b = vehicle["battery"]
    margin = b["end_of_life_margin_kwh"]
    battery_outcome = "shortfall" if margin < 0 else "surplus" if margin > 0 else "margin"
    lines += ["", "## What changes the vehicle and civil enquiry?", "",
              f"The central and high loaded trains weigh {vehicle['mass_cases']['central']['loaded_train_kg']/1000:.2f} and {vehicle['mass_cases']['high']['loaded_train_kg']/1000:.2f} tonnes under the component allowances. "
              f"The aged essential battery has a {abs(margin):.1f} kWh {battery_outcome}. The same duty requires {b['minimum_nominal_kwh_at_80pct_retention']:.2f} kWh nominal before additional hot-weather losses. "
              "Select brake hardware after measuring response, force and repeat duty against the protected stopping distance. "
              "[Vehicle and braking results](vehicle-audit-guide.md)", ""]
    conservative_brake = next(r for r in vehicle["braking"]["high"]
        if r["downgrade_pct"] == 2 and r["coast_delay_s"] == 2 and r["target_net_deceleration_m_s2"] == 0.6)
    brake = conservative_brake["cases"]["none_wheel_brakes/1_rail_modules_out"]
    lines += [f"With wheel braking unavailable and one independent module out, the high-load 2% downhill trial needs {brake['required_force_per_available_module_kn']:.2f} kN per remaining module for a 0.6 m/s² net stop. "
              f"The {brake['proposed_comparator_per_module_kn']:.1f} kN comparison gives a {brake['stop_at_comparator']['stop_distance_m']:.1f} m stopping distance including the two-second delay. Confirm force, heat and protected distance for the fitted arrangement.", ""]
    leader = data["civil"]["quotation_leaders"]["base"]
    if leader:
        residual = leader["closure_bay_m"]
        closure = (f"There is a {residual:.2f} m residual bay on each track. The workshop and cash accounts "
                   "exclude design and installation of those closures. " if residual else "")
        lines += [f"The lowest base-rate 30-year civil quotation case is **{leader['label']}**. Its whole-stock allowance is ${leader['installed_usd']/1e6:,.2f}m. "
                  + closure + "Verify the local transport plan, ground, load chart, bearing and prestress designs. "
                  "[Civil comparison](../mechanical/civil/SPAN-FAMILIES.md)", ""]
    if data.get("feeder_price_sensitivities"):
        lines += ["## What could the revised supply cost?", "",
                  "These figures apply dated planning rates to the actual site count, track length, assumed switching and simulated current duty. Each figure covers rail-side plant and conductors. The buyer cash accounts below await scope-matched offers.", "",
                  "| Layout | Modelled rail-side subtotal, low / base / high | Annual upkeep sensitivity, low / base / high |",
                  "| --- | ---: | ---: |"]
        for layout, prices in data["feeder_price_sensitivities"].items():
            direct = cost_bands(prices, "known_rail_side_direct_subtotal_usd")
            upkeep = cost_bands(prices, "rail_side_annual_upkeep_usd")
            lines.append(f"| {layout} | {direct} | {upkeep} |")
        lines += ["", "Utility reinforcement, site-specific works, demonstrated protection and scheduled renewals require separate scope and prices.", ""]
        for prices in data["feeder_price_sensitivities"].values():
            gap = prices["priced_cash_break_even"]
            if gap and gap["operating_comparison"] and gap["operating_comparison"]["unmatched_duties"]:
                names = {"normal": "ordinary service", "hot": "hot-weather service", "site_out": "a site outage",
                         "path_out": "a feed-path outage", "combined": "a combined site and path outage",
                         "high_mass_combined": "the high-mass combined outage"}
                duties = ", ".join(names[duty] for duty in gap["operating_comparison"]["unmatched_duties"])
                lines += [f"Service differs between the layouts under {duties}. Their priced subtotals cannot establish a break-even feeder price.", ""]
                break
    lines += ["## What can a buyer price?", "", "| Layout | Fleet sets | Operated / booked train-km per year | Partial capital | Partial 30-year PV |", "| --- | ---: | ---: | ---: | ---: |"]
    for layout, p in data["production"].items():
        op, cash = p["operation_basis"], p["cash"]["profiles"]["base"]
        lines.append(f"| {layout} | {op['fleet_sets_required']} | {op['operated_annual_train_km']:,.0f} / {op['booked_annual_train_km']:,.0f} | ${cash['capital_usd']/1e6:,.2f}m | ${cash['priced_30y_pv_usd']/1e6:,.2f}m |")
    for layout, model in data["production"].items():
        timings = ", ".join(f"{name} {case['last_completion_workday']:.0f}" for name,case in model["scenarios"].items())
        lines += ["", f"The {layout} workshop completes in the following modelled workdays. {timings}. The owner cash model retains unpriced delay exposures."]
    if data["production"]:
        for layout, model in data["production"].items():
            unpriced = model["cash"]["scope"]["unpriced_lots_by_group"]
            groups = ("opening-direct", "first-full-year-operations", "renewal-schedule")
            counts = ", ".join(f"{len(unpriced.get(group, []))} {label}" for group, label in
                               zip(groups, ("opening", "annual operation", "renewal"), strict=True))
            lines += ["", f"The {layout} ledger has {counts} lots without prices. "
                      "The owner cash model lists separate unpriced risks."]
        lines += ["", "Annual figures extrapolate the modelled day. Match installed scope, service achieved, "
                  "equipment duties, maintenance and replacements before comparing offers."]
    else:
        lines += ["", "A priced civil scope is required to build the workshop and cash comparison."]
    lines += ["",
              "## What remains open for release?", "",
              "| Work | Digital result | Evidence and review still needed |", "| --- | --- | --- |"]
    for task in data["decision"]["completion_tests"]:
        lines.append(f"| {task['task']} · {task['work']} | {task['result']} | {task['outstanding']} |")
    lines += ["",
              "## Reproduce or revise the comparison", "",
              "[Download the published paired6 budgetary enquiry](audited-enquiry.zip) · "
              "[Independent SUMO and grid-side reproduction for the published 15- and 30-minute cases](audit-verification.json) · [Workshop, offers and cash scope](audit-production-guide.md)", "",
              f"The audit records {len(data['assumptions'])} scoped input entries. Run `./osr design railway audit --check` to reproduce this report or `--json` to inspect each input, constraint and result. "
              "[Execution plan and acceptance tests](ASSUMPTION-AUDIT.md) · [Route and demand inputs](ALIGNMENT-DEMAND.md)", "",
              f"Evaluation `{data['evaluation_id']}`", ""]
    return "\n".join(lines)


def review_page(data):
    """Build the small offline Workbench view from the published case, without a server."""
    from html import escape
    def table(headers, values):
        header = "".join(f'<th scope="col">{escape(h)}</th>' for h in headers)
        body = "".join("<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in row) + "</tr>"
                       for row in values)
        return f'<div class="scroll"><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div>'
    route = data["alignment"]
    runs = data["service_offers"]
    day_rows = []
    for layout, rows in group_duties(data["power_days"]).items():
        values = [(r["condition"], f"{r['completed']} / {r['booked']}", f"{r['minimum_v']:.1f}" if r['minimum_v'] is not None else "Open",
                   f"{r['peak_site_ka']:.2f}", ", ".join(k.replace("_", " ") for k in r["failed_screens"])) for r in rows]
        day_rows.append(f"<details><summary>{escape(layout)} · five working days</summary>"+
                        table(("Duty", "Trips", "Minimum V", "Peak site kA", "Failed or open checks"), values)+"</details>")
    services = table(("Headway", "Booked dwell", "Normal places per train", "Annual requested journeys",
                      "Terminal conflicts", "Trips finished / booked", "Maximum delay"),
                     [(f"{h} min", f"{s['dwell_s']:g} s", s["normal_places_per_train"],
                       f"{s['annual_requested']:,.0f}", s["phases"]["best"]["conflicts"],
                       f"{s['ordinary']['completed']} / {s['ordinary']['booked']}",
                       f"{s['ordinary']['maximum_delay_s']:,.0f} s" if s['ordinary']['maximum_delay_s'] is not None else "Open") for h,s in runs.items()])
    procurement = table(("Layout", "Fleet", "Estimated capital in priced scope", "30-year PV in priced scope"),
                        [(l, p["operation_basis"]["fleet_sets_required"], f"${p['cash']['profiles']['base']['capital_usd']/1e6:,.2f}m",
                          f"${p['cash']['profiles']['base']['priced_30y_pv_usd']/1e6:,.2f}m") for l,p in data["production"].items()])
    rail_side = table(("Layout", "Rail-side equipment, low / base / high", "Annual upkeep, low / base / high"),
                      [(name, cost_bands(prices, "known_rail_side_direct_subtotal_usd"),
                        cost_bands(prices, "rail_side_annual_upkeep_usd"))
                       for name, prices in data.get("feeder_price_sensitivities", {}).items()])
    civil = data["decision"]["civil_enquiry"]
    civil_result = (f"The civil quotation comparison identifies {escape(civil)} for pricing." if civil else
                    "The civil comparison has no passing priced standard girder for this case.")
    scope = ("The ledgers give each outstanding equipment, installation, owner and renewal scope. "
             "The priced totals reflect the returns included in this evaluation." if data["production"] else
             "The workshop and cash comparison requires a priced civil scope.")
    route_summary = (f"The submitted Airport alignment is {route['route_km']:.2f} km long. "
                     "Review the survey and verify all station sites before selecting the corridor."
                     if route["survey_source"] else
                     f"The {route['route_km']:.2f} km horizontal study includes {route['review_connector_km']:.2f} km "
                     "of proposed connections. Um Al Tubol needs a confirmed site.")
    tests = table(("Work", "Digital result", "Evidence and review still needed"),
                  [(f"{t['task']} · {t['work']}", t["result"], t["outstanding"])
                   for t in data["decision"]["completion_tests"]])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Corridor design review | OpenSourceRail</title><link rel="stylesheet" href="scenario.css">
<style>main{{max-width:72rem;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}h1{{color:#102b3a;font-size:clamp(2rem,5vw,3.6rem)}}h2{{margin-top:2.4rem}}summary{{cursor:pointer;padding:.7rem 0;font-weight:bold}}.scroll{{overflow-x:auto}}td,th{{text-align:left;padding:.6rem;vertical-align:top}}table{{width:100%;border-collapse:collapse}}tr{{border-bottom:1px solid #cbd8dc}}code{{overflow-wrap:anywhere}}</style></head>
<body><main><nav><a href="index.html">Simulation workbench</a></nav><h1>Corridor design review</h1>
<p>{route_summary}
Investment and fabrication decisions remain open.</p>
<h2>Passenger service</h2><p>{DEMAND_BASIS[data["demand"]["mode"]]} Completed trips and maximum arrival delay come from a full operating-day replay with terminal and depot movements.</p>{services}
<h2>Traction power</h2><p>Compare live collector voltages alongside delivered trips. Source-current and protection returns are still required.</p>{"".join(day_rows)}
<h2>Construction and purchaser cash</h2><p>{civil_result} {scope}</p>{procurement}
<h3>Traction supply price sensitivity</h3><p>The estimates below use planning rates for the revised layout. The purchaser ledger awaits scope-matched equipment, utility and renewal offers.</p>{rail_side}
<h2>Evidence still needed</h2>{tests}
<h2>Reproduce the decision</h2><p><code>./osr design railway audit --check</code> reproduces this view.
Use <code>--json</code> for the input register, identities and purchaser ledger.</p>
<p><a href="audited-enquiry.zip" download>Published paired6 budgetary enquiry</a> · <a href="ASSUMPTION-AUDIT.md">Delivery plan</a> · <a href="AUDIT-RESULTS.md">Engineering results</a> · <a href="audit-verification.json">Independent comparison</a></p>
</main></body></html>
"""

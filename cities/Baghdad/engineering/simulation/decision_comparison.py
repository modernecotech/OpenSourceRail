"""Cross the choices in the bounded integrated service and supply model."""
import argparse
from itertools import product
import json
from pathlib import Path

from cities.Baghdad.engineering.simulation import scenario
from engineering.design_search import requirement_policy
from engineering.performance import check_disk_reservation, disk_reservation


REPORT = Path(__file__).with_name("JOINT-COMPARISON.md")

# A gate's meaning comes from the evaluator that generated it. In particular,
# the three approval fields in motion_power are always false pending evidence.
DUTY_GATES = ("all_workings_complete", "collector_voltage_screen", "electrical_isolation_screen",
              "route_and_block_reservations")
SERVICE_TARGETS = ("capacity_screen", "service_within_arrival_envelope")
NUMERICAL_GATES = ("dc_numerical_screen", "motion_work_balance_screen")
APPROVAL_GATES = ("protection_approved", "thermal_ratings_verified", "utility_connection_approved")


def decision_basis(result):
    """Interpret the issued scenario without transferring a trial failure to a design family."""
    stages = result["stages"]
    motion = stages["motion"]
    gates = motion["gates"]
    declared = set(DUTY_GATES + SERVICE_TARGETS + NUMERICAL_GATES + APPROVAL_GATES)
    if set(gates) != declared or any(type(value) is not bool for value in gates.values()):
        raise ValueError("Review the meaning of the changed motion gates before comparing cases")
    failed_duty = [k for k in DUTY_GATES if not gates[k]]
    failed_numeric = [k for k in NUMERICAL_GATES if not gates[k]]
    failed_targets = [k for k in SERVICE_TARGETS if not gates[k]]
    vehicle = stages["vehicle"]
    span = vehicle["selected_span"]
    interfaces = vehicle["interfaces"]
    # Signed remaining margins, positive when the named trial is within its screen.
    margins = {
        "stock_lift_60t_t": span["crane_chart_60t_stock_only_margin_t"],
        "parent_cage_30pct_loss_kn": span["effective_strand_margin_kn_by_loss"]["0.3"],
        "trial_soil_200kpa_kpa": 200 - span["eccentric_footing_max_kpa"],
        "battery_80pct_age_kwh": interfaces["aged_80pct_capacity_margin_kwh"],
        "low_adhesion_2pct_downgrade": interfaces["brake_adhesion_at_0p08_margin"],
        "trial_cooling_kw": stages["passengers"]["hvac"]["trial_thermal_margin_kw"],
    }
    factory = stages["production"]
    fleet = next(lot for lot in factory["priced_lots"] if lot["lot_id"] == "fleet")
    metrics = motion["metrics"]
    policy = requirement_policy.assess({}, candidate_id=result["identity"]["physical_id"])
    mandatory = [r for r in policy["findings"] if r["category"] == "mandatory_obligation"]
    return dict(
        declared_duty="numerically unresolved" if failed_numeric else
        "misses simulated duty" if failed_duty else "completes simulated duty",
        failed_simulated_obligations=failed_duty, failed_numerical_checks=failed_numeric,
        failed_service_targets=failed_targets,
        trial_margins=margins, breached_trial_controls=[k for k, value in margins.items() if value < 0],
        open_electrical_approvals=[k for k in APPROVAL_GATES if not gates[k]],
        open_qualification=[r["criterion_id"] for r in mandatory if r["status"] == "unknown"],
        requirement_policy_evaluation_id=policy["evaluation_id"],
        supported_hard_screen=policy["declared_hard_screen"],
        signed_limits_and_independent_review_available=False,
        supply_failure=motion["failure"], minimum_collector_v=metrics["minimum_collector_v"],
        maximum_collector_v=metrics["maximum_collector_v"], peak_site_ka=metrics["peak_site_current_ka"],
        site_rms_ka=metrics["max_site_rms_current_ka"], fleet_reserve_sets=metrics["fleet_sets_required"]-metrics["diagrammed_sets"],
        direct_fleet_lot_per_set_usd=fleet["usd"]["base"] / fleet["quantity"],
        open_price_scopes=factory["decision_summary"]["open_components"],
        complete_installed_price_usd=factory["complete_installed_price_usd"],
        issued_scenario_eligible=result["decision"]["eligible"],
        comparable_for_adoption=(result["decision"]["eligible"] and not failed_numeric and not failed_duty
                                 and policy["declared_hard_screen"] == "pass" and
                                 factory["complete_installed_price_usd"] is not None),
    )


def campaign():
    for cars, minutes, topology, span in product((3, 6), (15, 20, 30), ("paired6", "radial30"), (10, 20, 25)):
        yield "crossed", dict(cars=cars, headway_min=minutes, topology=topology, span_m=span)
    for cars, topology in product((3, 6), ("paired6", "radial30")):
        yield "outage", dict(cars=cars, headway_min=15, topology=topology, condition="combined")
    for cars, minutes in product((3, 6), (15, 30)):
        yield "hot and busy", dict(cars=cars, headway_min=minutes, topology="paired6", demand="upside", ambient_c=48)
    for material in ("aluminium", "hybrid"):
        yield "body material", dict(cars=3, headway_min=20, topology="paired6", material=material)


def observation(group, result):
    stages = result["stages"]
    cfg = result["inputs"]
    motion = stages["motion"]
    metrics = motion["metrics"]
    vehicle = stages["vehicle"]
    factory = stages["production"]
    span = vehicle["selected_span"]
    cash = factory["cash"]
    review = decision_basis(result)
    return dict(
        group=group, inputs=cfg, identity=result["identity"],
        od_id=motion["demand_basis"]["od_id"],
        offered=metrics["offered_passengers"], served=metrics["boarded_passengers"],
        end_of_day=metrics["unserved_service_boundary"], unserved_capacity=metrics["unserved_capacity_at_close"],
        unserved_incomplete=metrics["unserved_incomplete_trip"], denied_attempts=metrics["denied_boarding_attempts"],
        fleet=metrics["fleet_sets_required"], active=metrics["diagrammed_sets"],
        places_per_hour=metrics["normal_places_per_hour_direction"],
        trips=metrics["completed_passenger_trips"], booked_trips=metrics["booked_passenger_trips"],
        dwell_s=result["provenance"]["assisted_dwell_s"], energy_kwh_km=motion["energy_kwh_per_train_km"],
        loaded_train_kg=vehicle["loaded_train_kg"], tare_train_kg=vehicle["tare_train_kg"],
        site_count=factory["quantities"]["grid_sites"], train_km=motion["annual_train_km"],
        minimum_voltage_v=metrics["minimum_collector_v"], price=result["decision"]["capital_usd"],
        annual=result["decision"]["annual_opex_usd"], pv=factory["decision_summary"]["priced_30y_pv_base_usd"],
        cash_start_year=cash["service_start_year"], discount=cash["discount_rate_real"],
        thermal_margin_kw=stages["passengers"]["hvac"]["trial_thermal_margin_kw"],
        supports=factory["quantities"]["piers"], bearings=factory["quantities"]["bearings"],
        prestress_margin_kn=span["effective_strand_margin_kn_by_loss"]["0.3"],
        crane_stock_margin_t=span["crane_chart_60t_stock_only_margin_t"],
        rejected_checks=[k for k, v in motion["gates"].items() if not v],
        decision_basis=review, eligible=review["comparable_for_adoption"], holds=result["decision"]["holds"],
    )


def differential(reference, alternative):
    """A price threshold is conditional on matching the promised passenger service."""
    if (reference["od_id"] != alternative["od_id"] or reference["inputs"]["grade_pct"] != alternative["inputs"]["grade_pct"]
            or reference["inputs"]["ambient_c"] != alternative["inputs"]["ambient_c"]
            or reference["inputs"]["condition"] != alternative["inputs"]["condition"]):
        raise ValueError("Compare the same demand, alignment, weather and contingency")
    start = reference["cash_start_year"]
    if start != alternative["cash_start_year"] or reference["discount"] != alternative["discount"]:
        raise ValueError("Compare aligned price dates and operating periods")
    pv_difference = reference["pv"] - alternative["pv"]
    annuity = sum((1 + reference["discount"]) ** -y for y in range(start, start + 30))
    same_offer = all(reference[k] == alternative[k] for k in ("places_per_hour", "booked_trips", "trips"))
    same_carried = abs(reference["served"] - alternative["served"]) <= 1e-5
    matched_duty = same_offer and same_carried and all(
        r["decision_basis"]["declared_duty"] == "completes simulated duty"
        and not r["decision_basis"]["failed_service_targets"] for r in (reference, alternative)
    )
    return dict(price_headroom=reference["price"] - alternative["price"],
                annual_headroom=reference["annual"] - alternative["annual"],
                priced_pv_headroom=pv_difference,
                equivalent_extra_annual_cost=pv_difference / annuity,
                same_offer_and_carried=same_offer and same_carried,
                matched_simulated_service_for_cost_enquiry=matched_duty,
                selection_comparable=matched_duty and reference["eligible"] and alternative["eligible"])


def render(rows):
    central = [r for r in rows if r["group"] == "crossed"]
    by_case = {(r["inputs"]["cars"], r["inputs"]["headway_min"], r["inputs"]["topology"], r["inputs"]["span_m"]): r
               for r in central}
    lines = [
        "# Which choices change the service and the price?",
        "",
        "This worked comparison uses the issued 12 km line to test what changes when train length, frequency, power supply and viaduct span vary together. The 36 crossed combinations use one hourly passenger demand matrix, a level alignment, 40°C air, 18 service hours and the same six stations with 125 m platforms. Ten further checks change the outage, heat and demand, or body material. A new corridor needs its own requirements.",
        "",
        "## Choose the service offer first",
        "",
        "The steel formation here carries 350 or 700 normal planning places. The diagram includes full-tail release and terminal occupation. Retiming the 20-minute service uses a ten-minute departure offset at the second terminal. Three reserve sets are a retained procurement assumption. The protected conductor supplies moving trains continuously. Emergency power and braking have separate open requirements.",
        "",
        "| Cars | Interval (min) | Places/h/direction | Active + reserve sets | Assisted dwell (s) | Journeys completed/day | Left at close/day¹ | Grid kWh/train-km | Priced capital ($m) | Annual operation ($m) |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cars, minutes in product((3, 6), (15, 20, 30)):
        r = by_case[cars, minutes, "paired6", 10]
        lines.append(f"| {cars} | {minutes} | {r['places_per_hour']:,} | {r['active']} + {r['fleet']-r['active']} | {r['dwell_s']} | {r['served']:,.1f} | {r['end_of_day']+r['unserved_capacity']+r['unserved_incomplete']:.1f} | {r['energy_kwh_km']:.2f} | {r['price']/1e6:,.2f} | {r['annual']/1e6:.2f} |")
    short = by_case[3, 15, "paired6", 10]
    long = by_case[6, 30, "paired6", 10]
    supply_deltas = [differential(by_case[c, h, "radial30", n], by_case[c, h, "paired6", n])
                     for c, h, n in product((3, 6), (15, 20, 30), (10, 20, 25))]
    ref = by_case[6, 15, "radial30", 10]
    paired = by_case[6, 15, "paired6", 10]
    delta = differential(ref, paired)
    lines.extend(["",
        f"¹ All six rows use the six-site paired supply and 10 m box. Demand is {ref['offered']:,.1f} journeys per day. The closing balance includes arrivals after the last boarding opportunity, queues left by full trains and incomplete trips. Three cars every 15 minutes and six every 30 minutes both offer 1,400 places/h/direction. The shorter interval halves the assumed random-arrival wait from 15 to 7.5 minutes. The three-car offer costs ${(long['price']-short['price'])/1e6:.2f}m less to open and ${(short['annual']-long['annual'])/1e6:.2f}m more per year to operate. It carries {short['served']-long['served']:.0f} more journeys per day. An operator must specify the acceptable wait, load and coverage before comparing prices.",
        "",
        "## What a power bid can change",
        "",
        f"At six cars every 15 minutes the two supply options complete {ref['trips']} workings each. The radial and paired cases carry {ref['served']:,.3f} and {paired['served']:,.3f} journeys per day respectively. Moving from 30 radial sites to six paired sites changes priced capital by −${delta['price_headroom']/1e6:,.2f}m and ordinary annual operating expense by −${delta['annual_headroom']/1e6:.2f}m. Both retain the published train and route quantities on this comparison.",
        "",
        f"Across all 18 matched timetable, formation and span pairs, the absolute opening-price difference between the two supplies ranges from ${min(d['price_headroom'] for d in supply_deltas)/1e6:.3f}m to ${max(d['price_headroom'] for d in supply_deltas)/1e6:.3f}m. These fixed enquiry prices contain no new conductor or rectifier sizing for a lighter train. The duty model does respond to a lighter or less frequent train. A supplier can price its revised duty and renewal schedule against the resulting envelope.",
        "",
        f"{sum(d['matched_simulated_service_for_cost_enquiry'] for d in supply_deltas)} of the 18 normal supply pairs deliver matching simulated service at the stated numerical tolerance of 0.00001 daily journeys. Their duty and current envelopes can inform competing supplier enquiries. At six cars every 15 minutes the difference in gross priced 30-year present value is ${delta['priced_pv_headroom']/1e6:,.2f}m. At {ref['discount']:.0%} real discount from the study origin, an additional constant ${delta['equivalent_extra_annual_cost']/1e6:.2f}m per operating year from year {ref['cash_start_year']} would consume that entire priced difference. Alternatively discount a supplier's actual extra installation, protection, renewals, downtime and upkeep at their due dates. Use the difference once. The paired renewal programme is open and its parent radial scopes have been removed. The break-even figure is a budget for unresolved **net** costs, conditional on meeting the same safety, reliability and service requirements.",
        "",
        "| Combined site and feed-path outage, 15 min | Cars | Passenger workings completed / booked | Completed journeys/day | Lowest collector V on energized movements | Peak site current (kA) |",
        "|---|---:|---:|---:|---:|---:|"])
    for r in rows:
        if r["group"] == "outage":
            lines.append(f"| {r['inputs']['topology']} | {r['inputs']['cars']} | {r['trips']} / {r['booked_trips']} | {r['served']:,.1f} | {r['minimum_voltage_v']:.1f} | {r['decision_basis']['peak_site_ka']:.2f} |")
    lines.extend(["", "The outage is one prescribed site and path. Read voltage alongside service completion. The normal price uses ordinary operating energy. Protection coordination, thermal duty, evacuation and local grid evidence remain open for both layouts.",
        "", "## Where the span comparison stops", "",
        "| Span (m) | Supports / bearings on 12 km | Cage margin at 30% loss, 3 / 6 cars (kN) | 60 t lift allowance minus stock (t) | Priced opening using current civil proxy ($m)² |",
        "|---:|---:|---:|---:|---:|"])
    for length in (10, 20, 25):
        small, large = (by_case[n, 15, "paired6", length] for n in (3, 6))
        lines.append(f"| {length} | {large['supports']:,} / {large['bearings']:,} | {small['prestress_margin_kn']:+,.0f} / {large['prestress_margin_kn']:+,.0f} | {large['crane_stock_margin_t']:+.1f} | {large['price']/1e6:.2f} |")
    lines.extend(["", "² This column uses six steel cars and the paired supply. The structural calculation moves the axles of each bounded train across the candidate span. The civil price model scales the parent allowance with span and support count. Once a cage or lift fails, a differently dimensioned section, support, foundation and construction method require a fresh takeoff. The price change shown here cannot be assigned to a redesigned U-girder. The service model has no span-dependent alignment or speed restriction for this straight corridor.", "",
        "## Check heat, demand and materials", "",
        "| Paired feed, upside demand at 48°C | Cars | Interval (min) | Completed journeys/day | Denied boarding attempts/day | Assisted dwell (s) | Trial cooling margin (kW thermal) |",
        "|---|---:|---:|---:|---:|---:|---:|"])
    for r in rows:
        if r["group"] == "hot and busy":
            lines.append(f"| Steel | {r['inputs']['cars']} | {r['inputs']['headway_min']} | {r['served']:,.1f} | {r['denied_attempts']:.1f} | {r['dwell_s']} | {r['thermal_margin_kw']:+.1f} |")
    lines.extend(["", "The heat and demand changes occur together. Compare formations within this group. Denied attempts count people who could board a later departure. The 3-car, 30-minute trial clears its capacity backlog by closing time but fails the capacity screen during the day. A negative cooling margin requires a changed installed HVAC system, followed by a new auxiliary load, timetable and energy calculation.", "",
        "| Three cars, 20 min, same paired supply and 10 m span | Loaded train (t) | Grid kWh/train-km | Capital ($m) | Annual operation ($m) |",
        "|---|---:|---:|---:|---:|"])
    for r in [by_case[3, 20, "paired6", 10], *(r for r in rows if r["group"] == "body material")]:
        lines.append(f"| {r['inputs']['material']} | {r['loaded_train_kg']/1000:.2f} | {r['energy_kwh_km']:.3f} | {r['price']/1e6:.2f} | {r['annual']/1e6:.2f} |")
    lines.extend(["", "Mass is an installed planning estimate. Alternative joints, repair methods, supplier quotes and a formation-specific controls replay are outstanding. The capital column includes the price model's material premium. Longer life or reduced upkeep needs a priced and evidenced scope.",
        "", "## Which decisions can this calculation support?", "",
        f"**Operating the declared duty.** {sum(r['decision_basis']['declared_duty'] == 'completes simulated duty' for r in rows)} of {len(rows)} cases complete the booked workings while meeting the modeled voltage, isolation and block checks. The radial combined outages block two directional interstation movements. A voltage reading on an energized part of that line gives no assurance of a through trip. The paired case assumes the surviving ties can be configured safely. Protection settings, clearing times, conductor and rectifier thermal ratings, utility approval and evacuation each need their own evidence.",
        "",
        "**Engineering the installed option.** The cage margin applies to the inherited box and tendon arrangement. A negative lifting margin eliminates that stock lift on the assumed chart. A positive stock margin still needs rigging, radius and ground checks. Compare a resized cage, lighter girder, segmental erection or different crane as a new physical option with its own priced operations. Footing pressure uses a trial site limit. Battery ageing, low adhesion and summer cooling margins identify specific redesign and retest work for the named duty. Changing a target requires an agreed operating envelope and demonstrated independent stopping and essential power.",
        "",
        f"**Setting the service brief.** {sum(bool(r['decision_basis']['failed_service_targets']) for r in rows)} cases miss the study's one-minute lateness or capacity criterion. The capacity check includes complete workings and fewer than 0.1 denied attempts or passengers left by capacity at closing. The operator must set acceptable waiting, coverage and recovery before the service can be selected. For the 15-minute paired case, one spare set represents ${short['decision_basis']['direct_fleet_lot_per_set_usd']/1e6:.2f}m of direct three-car fleet price or ${paired['decision_basis']['direct_fleet_lot_per_set_usd']/1e6:.2f}m for six cars. That gives the price exposure to the three-spare assumption. Any revised reserve needs a maintenance and recovery diagram and repriced depot, renewals and downtime.",
        "",
        f"**Qualification and cost.** Every case carries an open installed price and unapproved protection. The requirement policy has {len(ref['decision_basis']['open_qualification'])} mandatory criteria awaiting scoped limits or independently reviewed evidence. The modeled failed movements are observed numerical results for their stated duty. The project has no authenticated physical-limit rejection of an entire vehicle, supply or span family from this comparison. The JSON returns the named duty failures, numerical checks, trial margins, missing evidence and open cost scopes individually alongside the original integrated decision.",
        "", "## Reproduce the comparison", "",
        f"The integrated evaluator returned {sum(r['eligible'] for r in rows)} eligible selections in {len(rows)} evaluated cases. Each JSON row retains the physical and evaluation IDs, demand matrix identity, failures and open checks. Conditional prices remain available when an option fails.",
        "", "```sh", "python3 -m cities.Baghdad.engineering.simulation.decision_comparison --check",
        "python3 -m cities.Baghdad.engineering.simulation.decision_comparison --json > build/joint-decisions.json", "```",
        "", f"Comparison digest `{scenario.sha(scenario.encode(rows))}`. [Service, energy and price assumptions](SIMULATION.md) · [Factory and whole-life cost scope](production-guide.md) · [Redesigned girder and support families](../mechanical/civil/SPAN-FAMILIES.md)", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--publish", action="store_true")
    modes.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows = []
    with disk_reservation(scenario.ROOT, scenario.ROOT, "Service supply and span comparison", 128 << 20) as lease:
        for group, inputs in campaign():
            check_disk_reservation(lease)
            rows.append(observation(group, scenario.run_case(inputs)))
        check_disk_reservation(lease)
        report = render(rows)
        if args.publish:
            scenario.write_atomic(REPORT, report.encode())
        elif args.check:
            if REPORT.read_text() != report:
                raise SystemExit("Joint comparison differs from the current engineering cases")
            print(scenario.sha(scenario.encode(rows)))
        elif args.json:
            print(json.dumps(rows, sort_keys=True, indent=2, allow_nan=False))
        else:
            print(report)


if __name__ == "__main__":
    main()

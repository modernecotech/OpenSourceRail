"""Cross the choices in the bounded integrated service and supply model."""
import argparse
from itertools import product
import json
from pathlib import Path

from cities.Baghdad.engineering.simulation import scenario
from engineering.performance import check_disk_reservation, disk_reservation


REPORT = Path(__file__).with_name("JOINT-COMPARISON.md")


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
        eligible=result["decision"]["eligible"], holds=result["decision"]["holds"],
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
    return dict(price_headroom=reference["price"] - alternative["price"],
                annual_headroom=reference["annual"] - alternative["annual"],
                priced_pv_headroom=pv_difference,
                equivalent_extra_annual_cost=pv_difference / annuity,
                same_offer_and_carried=same_offer and same_carried,
                selection_comparable=same_offer and same_carried and reference["eligible"] and alternative["eligible"])


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
        f"The difference in gross priced 30-year present value is ${delta['priced_pv_headroom']/1e6:,.2f}m. At {ref['discount']:.0%} real discount from the study origin, an additional constant ${delta['equivalent_extra_annual_cost']/1e6:.2f}m per operating year from year {ref['cash_start_year']} would consume that entire priced difference. Alternatively discount a supplier's actual extra installation, protection, renewals, downtime and upkeep at their due dates. Use the difference once. The paired renewal programme is open and its parent radial scopes have been removed. The break-even figure is a budget for unresolved **net** costs, conditional on meeting the same safety, reliability and service requirements.",
        "",
        "| Combined site and feed-path outage, 15 min | Cars | Passenger workings completed / booked | Completed journeys/day |",
        "|---|---:|---:|---:|"])
    for r in rows:
        if r["group"] == "outage":
            lines.append(f"| {r['inputs']['topology']} | {r['inputs']['cars']} | {r['trips']} / {r['booked_trips']} | {r['served']:,.1f} |")
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

"""Build daily passenger train workings for the selected synthetic 30 km corridor."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib

DIR = Path(__file__).resolve().parent
ROOT = DIR.parents[2]
sys.path.insert(0, str(ROOT))
from engineering import v07_reference_journey as reference
from engineering.performance import disk_reservation, check_disk_reservation

SELECTION = ROOT / reference.SELECTED
COST = ROOT / "docs/design-engine/v07-powered-cost/input.json"
MOTION = ROOT / "docs/design-engine/v07-architecture-decision/result.json"
# Reversible clock placement of the four peak and fourteen other reference hours.
FIRST_HOUR, LAST_HOUR = 6, 24
PEAK_HOURS = (7, 8, 16, 17)
TERMINALS = ("S01", "S12")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clock(seconds):
    seconds = round(seconds)
    return f"{seconds//3600:02d}:{seconds%3600//60:02d}:{seconds%60:02d}"


def build():
    selected = tomllib.loads(SELECTION.read_text())
    cost = json.loads(COST.read_text())
    arch = json.loads(MOTION.read_text())
    service = cost["service_control"]
    joined = tomllib.loads((ROOT / reference.JOINED).read_text())
    parent = reference.evaluate(expected_parent_candidate_id=selected["physical_candidate_id"])
    if (cost["source_sha256"][str(MOTION.relative_to(ROOT))] != sha(MOTION)
            or cost["physical_candidate_id"] != joined["ancestry"]["powered_vehicle_physical_candidate_id"]
            or cost["equal_service_evaluation_id"] != arch["evaluation_id"]
            or len(PEAK_HOURS) != reference.PEAK_HOURS_PER_DAY
            or LAST_HOUR - FIRST_HOUR - len(PEAK_HOURS) != reference.OTHER_HOURS_PER_DAY):
        raise ValueError("Core pricing, level-train running and service hours must share one basis")
    [profile] = [r for r in arch["service_rows"] if r["architecture"] == "powered-wheel-continuous-supply"
                 and r["grade_magnitude"] == 0]
    headway = service["headway_s_conditional"]
    active = service["fleet_active"]
    n = service["stations"]
    dwell = service["dwell_s"]
    turn = service["terminal_turnback_s"]
    run = profile["directions"]["uphill"]["runtime_s"] * (1 + service["moving_time_allowance_fraction"])
    travel = round(run * (n-1) + dwell * (n-2), 6)
    if (not math.isclose(travel, profile["one_way_s"]["uphill"]) or not math.isclose(travel, profile["one_way_s"]["downhill"])
            or (profile["active_trainsets"], profile["spare_trainsets"]) != (active, service["fleet_spare"])
            or parent["service"]["active_trainsets"] != active or active % 2 or n != 12
            or math.ceil((2 * travel + 2 * turn) / headway) != active):
        raise ValueError("Selected service, stations and source motion/fleet no longer reconcile")
    starts = [h*3600 + s for h in range(FIRST_HOUR, LAST_HOUR) for s in range(
        0, 3600, headway if h in PEAK_HOURS else 3600 // reference.OTHER_TRAINS_PER_HOUR_PER_DIRECTION)]
    # Layover stock waits away from the boarding face; 22 ready at each end.
    ready = {end: [] for end in TERMINALS}
    for i in range(active):
        ready[TERMINALS[i % 2]].append((0, f"T{i+1:02d}"))
    trips = []
    by_set = {}
    for departure in starts:
        for origin, dest in (TERMINALS, tuple(reversed(TERMINALS))):
            available = [entry for entry in ready[origin] if entry[0] <= departure]
            if not available:
                raise ValueError(f"No ready train at {origin} for {clock(departure)}")
            # Reuse a recent arrival first. Unused peak stock stays stabled.
            train = max(available)
            ready[origin].remove(train)
            arrival = departure + travel
            ident = train[1]
            stops = []
            for i in range(n):
                name = f"S{1+(i if origin == TERMINALS[0] else n-1-i):02d}"
                at = departure + run * i + max(0, i-1) * dwell
                stops.append(dict(station=name, arrival_s=None if i == 0 else round(at, 6),
                                  departure_s=None if i == n-1 else round(at + (dwell if i else 0), 6)))
            trip = dict(trip=f"{origin}-{len(trips)//2+1:03d}", train=ident, origin=origin, dest=dest,
                        departure_s=departure, arrival_s=arrival, calls=stops)
            trips.append(trip)
            by_set.setdefault(ident, []).append(trip)
            ready[dest].append((arrival + turn, ident))

    # Every arrival takes a berth for the minimum turn, including last trips.
    # Direct reversals stay on the face through their next departure; longer
    # layovers first clear to a siding and later occupy a face for boarding.
    maximum_direct_wait = 3600 // reference.OTHER_TRAINS_PER_HOUR_PER_DIRECTION
    intervals = {end: [] for end in TERMINALS}
    siding_moves = 0
    for workings in by_set.values():
        first = workings[0]
        intervals[first["origin"]].append((first["departure_s"]-dwell, first["departure_s"], first["trip"]))
        for i, trip in enumerate(workings):
            following = workings[i+1] if i+1 < len(workings) else None
            finish = trip["arrival_s"] + turn
            if following:
                gap = following["departure_s"] - trip["arrival_s"]
                if gap < turn or following["origin"] != trip["dest"]:
                    raise ValueError("Train reverses before ready or from a different terminal")
                if gap <= maximum_direct_wait:
                    finish = following["departure_s"]
                else:
                    intervals[trip["dest"]].append((following["departure_s"]-dwell, following["departure_s"], following["trip"]))
                    siding_moves += 2
            intervals[trip["dest"]].append((trip["arrival_s"], finish, trip["trip"]))
    def assign_faces(intervals, face_limit=None):
        releases = []
        allocated, missed = [], []
        for begin, end, trip in sorted(intervals):
            berth = next((i for i, free in enumerate(releases) if free <= begin), len(releases))
            if berth == face_limit:
                missed.append(dict(begin_s=begin, end_s=end, trip=trip))
                continue
            allocated.append(dict(face=berth+1, begin_s=begin, end_s=end, trip=trip))
            if berth == len(releases):
                releases.append(end)
            else:
                releases[berth] = end
        return len(releases), allocated, missed

    allocation = {end: assign_faces(intervals[end]) for end in TERMINALS}
    faces = {end: row[0] for end, row in allocation.items()}
    two_face_holds = assign_faces(intervals[TERMINALS[-1]], faces[TERMINALS[-1]]-1)[2]

    # One usable face for inbound reversals. Count arrivals that cannot begin
    # their minimum occupation on time. Departures, routes and displaced trains
    # still need to be retimed; this is an optimistic single-resource screen.
    blocked = TERMINALS[-1]
    until = 0
    rejected = []
    for trip in trips:
        if trip["dest"] == blocked:
            if trip["arrival_s"] < until:
                rejected.append(trip["trip"])
            else:
                until = trip["arrival_s"] + turn
    failed_trip = next(t for t in trips if t["origin"] == TERMINALS[0] and t["departure_s"] == PEAK_HOURS[0]*3600)
    failed_duty = [t["trip"] for t in by_set[failed_trip["train"]] if t["departure_s"] >= failed_trip["departure_s"]]
    count = len(trips)
    summary = dict(trips_per_direction=count//2, trip_count=count, route_km=service["route_km"],
                   daily_train_km=count*service["route_km"], annual_train_km=count*service["route_km"]*reference.SERVICE_DAYS_PER_YEAR,
                   passenger_train_hours_day=count*travel/3600, minimum_turnback_train_hours_day=count*turn/3600,
                   one_way_s=travel, turn_s=turn, recovery_s=active*headway-2*(travel+turn), required_faces=faces,
                   active_sets=len(by_set), reserve_sets=service["fleet_spare"], peak_headway_s=headway,
                   offpeak_headway_s=3600 // reference.OTHER_TRAINS_PER_HOUR_PER_DIRECTION,
                   intermediate_siding_moves=siding_moves, last_arrival_s=trips[-1]["arrival_s"],
                   failed_set=failed_trip["train"], failed_from=failed_trip["trip"], exposed_trips=failed_duty,
                   blocked_face_holds=two_face_holds, single_face_rejected_arrivals=rejected, normal_places_per_train=service["normal_places_per_train"])
    paths = [SELECTION, COST, MOTION, Path(__file__).resolve(), ROOT / reference.PRODUCER, ROOT / reference.JOINED]
    sources = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    revision = hashlib.sha256(json.dumps([parent["evaluation_id"], sources], sort_keys=True).encode()).hexdigest()
    return dict(physical_candidate_id=selected["physical_candidate_id"], evaluation_id=revision,
                source_sha256=sources, summary=summary, trips=trips,
                terminal_occupation={end: row[1] for end, row in allocation.items()})


def report(data):
    s = data["summary"]
    first = data["trips"][0]
    failed = next(t for t in data["trips"] if t["trip"] == s["failed_from"])
    text = [
        "# Core 30 km passenger timetable",
        "",
        f"From 06:00 to midnight the two terminals each dispatch {s['trips_per_direction']} trains. The planning timetable gives "
        f"{s['daily_train_km']:,.0f} passenger train-km per day and {s['annual_train_km']:,.0f} per 365-day year. "
        f"The {s['active_sets']} numbered workings share {s['passenger_train_hours_day']:.1f} train-hours in passenger service "
        f"and {s['minimum_turnback_train_hours_day']:.1f} hours of minimum terminal occupation. The last train arrives at {clock(s['last_arrival_s'])} on the service-day clock.",
        "",
        "| Departures from either end | Headway | Trains/hour/direction | Normal places/hour/direction |",
        "|---|---:|---:|---:|",
    ]
    for label, headway in (("06:00–07:00, 09:00–16:00, 18:00–24:00", s["offpeak_headway_s"]),
                           ("07:00–09:00 and 16:00–18:00", s["peak_headway_s"])):
        tph = 3600 // headway
        text.append(f"| {label} | {headway} s | {tph} | {s['normal_places_per_train']*tph:,} |")
    text += [
        "",
        "The operating estimate supplies four peak and fourteen other hours. The clock times locate these hours for a workshop. "
        "Both directions stop at every station on the level, equally spaced synthetic line. Each of the eleven running intervals "
        "includes 5% motion allowance. The ten intermediate stops each allow 35 seconds. The longer published constant-peak comparison has a different daily service.",
        "",
        "| First working from S01 | " + " | ".join(c["station"] for c in first["calls"]) + " |",
        "|---" + "|---:"*len(first["calls"]) + "|",
        "| Depart (arrive at S12) | " + " | ".join(clock(c["departure_s"] if c["departure_s"] is not None else c["arrival_s"]) for c in first["calls"]) + " |",
        "",
        "## Turnbacks and fleet",
        "",
        f"A trip takes {s['one_way_s']:.2f} seconds. Two trips and two {s['turn_s']} s reversals take {2*(s['one_way_s']+s['turn_s']):,.2f} seconds. "
        f"At {s['peak_headway_s']} s headways the {s['active_sets']}-set cycle allows {s['recovery_s']:.1f} seconds of additional time per round trip. "
        f"The other {s['reserve_sets']} sets are the reserve allowance. Each duty starts with a set available at its departure end. The model stages 22 sets per end and reuses the most recent eligible arrival.",
        "",
        f"Across the day the interval calculation requires {s['required_faces']['S01']} independent berth positions at S01 and {s['required_faces']['S12']} at S12. "
        f"A train with at most 300 s until its reverse working stays on its face. Longer layovers use sidings after the minimum turn, with a further 35 s of boarding before departure. This gives {s['intermediate_siding_moves']} intermediate siding movements, plus initial deployment and final stabling. "
        "The berth count assumes every position can serve the train’s door side. Timed crossover, empty-stock and route-release paths and a compatible terminal layout are outstanding.",
        "",
        "## Two disruption cases",
        "",
        f"* **Failed ready set.** If {s['failed_set']} fails clear of the running line before its {clock(failed['departure_s'])} S01 departure and no replacement is available, "
        f"{len(s['exposed_trips'])} subsequent trips on its duty, including that departure, lose their assigned train. A ready, compatible spare in position before departure can inherit that duty, leaving {s['reserve_sets']-1} reserves. Failure on the running line additionally requires a protected recovery path and a timed clearance.",
        f"* **Blocked face at S12.** With one of its {s['required_faces']['S12']} scheduled positions closed all day, "
        f"{len(s['blocked_face_holds'])} scheduled occupation intervals cannot be admitted on time to the remaining positions. "
        "The export lists the affected trains and intervals. A supervisor must plan holding points, departures and any accessible transfer. "
        f"With **only one face available**, {s['turn_s']} s per arrival gives a theoretical ceiling of {3600//s['turn_s']} reversals/hour before dispatch conflicts. "
        f"Admitting arrivals in time order and dropping those which cannot immediately take the face leaves {len(s['single_face_rejected_arrivals'])} arrivals without a berth over the day. "
        "Price a reduced peak offer and trace its corresponding return workings before diversion or cancellation. An unavailable platform also needs a verified accessible route and passenger management.",
        "",
        "Measure loaded dwell, wheelchair boarding, door lock and despatch, full-tail clearance, train reversal and route release at both ends. Survey platform faces, crossing conflicts, sidings, depot access and rescue time. The working diagram supplies planned times and resource demands for these trials. Passenger operating approval remains open.",
        "",
        "Use `python3 docs/reference-v07/integration/timetable.py --json` for every numbered train, trip, stop call and affected disruption working. "
        "Times are seconds after service-day midnight. Use `--check` to verify this sheet. [Operating-cost service assumptions](../../../engineering/v07_reference_journey.py) · [Level running and fleet control](../../design-engine/v07-architecture-decision/result.json) · [Core cost control](../../design-engine/v07-powered-cost/input.json)",
        "",
        f"Selected train and corridor `{data['physical_candidate_id']}`. Service evaluation `{data['evaluation_id']}`.",
    ]
    return "\n".join(text) + "\n"


if __name__ == "__main__":
    options = argparse.ArgumentParser(description=__doc__)
    group = options.add_mutually_exclusive_group()
    group.add_argument("--json", action="store_true")
    group.add_argument("--check", action="store_true")
    args = options.parse_args()
    result = build()
    target = DIR / "TIMETABLE.md"
    if args.json:
        print(json.dumps(result, separators=(",", ":"), allow_nan=False))
    elif args.check:
        if target.read_text() != report(result):
            raise SystemExit("Core timetable has changed")
    else:
        with disk_reservation(ROOT, DIR, "Core timetable", 131072) as lease:
            check_disk_reservation(lease)
            target.write_text(report(result))

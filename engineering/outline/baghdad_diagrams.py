"""Build planning stop times and train workings from the Baghdad passenger offer."""
from __future__ import annotations

import argparse
from bisect import bisect_left
import csv
from collections import Counter, defaultdict, deque
from hashlib import sha256
from itertools import pairwise
import json
import math
from pathlib import Path
import sys

from engineering.outline import baghdad_system as system

ROOT = system.ROOT
CITY = ROOT / "cities/Baghdad"
PUBLICATION = CITY / "service-diagrams.json"


def first_paths(waypoints, register, review):
    """Keep every ordered RFI occurrence, even when its map position is unknown."""
    by_point = {(s["route_hint"], *s["longitude_latitude"]): s for s in register}
    reviewed = {(f["properties"]["line"], f["properties"]["order"]): f["properties"]
                for f in review["features"] if f["properties"].get("kind") == "rfi_named"}
    paths = defaultdict(list)
    for p in sorted((p for p in waypoints if p["kind"] == "rfi_named"),
                    key=lambda p: (p["line"], p["order"])):
        line = p["line"]
        found = by_point[line, p["lon"], p["lat"]] if p["lon"] is not None else None
        paths[line].append({"label": p["rfi_name"], "register_id": found["id"] if found else None,
                            "location_scope": reviewed.get((line, p["order"]), {}).get(
                                "coordinate_scope", "unlocated_name"),
                            "interchange_hint": p["rfi_name"], "id": f'{line}-{p["order"]:02d}'})
    for stops in paths.values():
        for i, stop in enumerate(stops):
            stop["fraction"] = i / (len(stops) - 1)
    return paths


def polyline_positions(coords, points):
    """Project schematic station coordinates onto their own route in local metric axes."""
    scale = math.cos(math.radians(coords[0][1]))
    vertices = [(lon * scale, lat) for lon, lat in coords]
    segments = []
    total = 0.
    for (x, y), (xx, yy) in pairwise(vertices):
        dx, dy = xx - x, yy - y
        length = math.hypot(dx, dy)
        if length:
            segments.append((x, y, dx, dy, length, total))
            total += length
    if total <= 0:
        raise ValueError("Route requires a nonzero schematic length")
    for lon, lat in points:
        px = lon * scale
        best = (float("inf"), None)
        for x, y, dx, dy, length, start in segments:
            f = max(0, min(1, ((px - x) * dx + (lat - y) * dy) / length ** 2))
            best = min(best, (math.hypot(px - x - f * dx, lat - y - f * dy),
                              (start + f * length) / total))
        yield best[1]


def metro_paths(features, register, groups, coverage):
    lines = {f["properties"]["route_id"]: f for f in features
             if f["geometry"]["type"] == "LineString"}
    junctions = coverage["access_branch_junction_screen"]["branches"]
    result, holds = {}, {}
    for group, (main, *branches) in groups.items():
        reasons = []
        for branch in branches:
            junction = junctions[branch]
            if not junction["within_tolerance"]:
                reasons.append(f'{branch} endpoint is {junction["distance_m"]:.0f} m from {main}.')
            elif junction["nearest_main_location"] != "terminus":
                reasons.append(f'{branch} joins {main} at {junction["nearest_main_location"]}; '
                               'the full section mileage has no single end-to-end path.')
        if reasons:
            holds[group] = reasons
            continue
        line = lines[main]
        coords = line["geometry"]["coordinates"]
        stops = []
        for r in register:
            p = features[r["source_feature_index"]]["properties"]
            if p.get("route_id", p.get("line")) == main:
                stops.append({"id": r["id"], "register_id": r["id"],
                              "interchange_hint": p.get("junction_group"),
                              "label": r["label"] or r["id"], "coords": r["longitude_latitude"]})
        if branches:
            if len(branches) != 1:
                raise ValueError("Unresolved terminal extension layout")
            extension = lines[branches[0]]
            branch_coords = extension["geometry"]["coordinates"]
            if branch_coords[-1] in (coords[0], coords[-1]):
                branch_coords = list(reversed(branch_coords))
            if branch_coords[0] == coords[0]:
                coords = list(reversed(branch_coords))[:-1] + coords
            elif branch_coords[0] == coords[-1]:
                coords = coords + branch_coords[1:]
            else:
                raise ValueError("Terminal map vertices must coincide for a through path")
            stops.append({"id": extension["properties"]["anchor_id"], "register_id": None,
                          "label": extension["properties"]["name"], "coords": branch_coords[-1]})
        for stop, fraction in zip(stops, polyline_positions(coords, [s["coords"] for s in stops])):
            stop["fraction"] = fraction
        stops.sort(key=lambda s: s["fraction"])
        if len(stops) < 2 or stops[0]["fraction"] > 1e-5 or stops[-1]["fraction"] < 1 - 1e-5:
            raise ValueError(f"{group} needs both terminal stops")
        stops[0]["fraction"], stops[-1]["fraction"] = 0., 1.
        for s in stops:
            del s["coords"]
        result[group] = stops
    return result, holds


def pattern(stops, run_s, dwell_s, km, speed_cap):
    moving_s = run_s - dwell_s * (len(stops) - 2)
    if moving_s <= 0:
        raise ValueError("No time left to move after scheduled dwells")
    offsets = []
    for i, stop in enumerate(stops):
        arr = round(moving_s * stop["fraction"]) + dwell_s * max(0, i - 1)
        dep = arr + (dwell_s if 0 < i < len(stops)-1 else 0)
        offsets.append({**stop, "arrival_s": arr, "departure_s": dep})
    for a, b in pairwise(offsets):
        seconds = b["arrival_s"] - a["departure_s"]
        if seconds <= 0 or km * (b["fraction"] - a["fraction"]) * 3600 / seconds > speed_cap:
            raise ValueError("Interstop schedule exceeds the speed cap or has no travel time")
    return offsets


def workings(group, plan, run_s, layover_s, peak_interval):
    """Allocate each departure to a set at the correct terminal, after its layover."""
    phase = (run_s + layover_s) % peak_interval
    times = [(3600 * (plan["start_hour_local"] + hour) + (3600 * i) // tph
              + (phase if direction else 0), direction)
             for hour, tph in enumerate(plan["departures_per_hour_direction"])
             for i in range(tph) for direction in (0, 1)]
    ready = [deque(), deque()]
    trips = []
    fleet = 0
    for departure, direction in sorted(times):
        available = ready[direction]
        if available and available[0][0] <= departure:
            _, train = available.popleft()
        else:
            fleet += 1
            train = f"{group}-{fleet:03d}"
        arrival = departure + run_s
        ready[1-direction].append((arrival + layover_s, train))
        trips.append((train, direction, departure, arrival))
    return trips, fleet


def group_diagram(group, stops, km, cfg):
    v, plan = cfg["vehicle"], cfg["service_plan"]
    layover = math.ceil(60 * plan["terminal_layover_min_each_end"])
    run = math.ceil(km * 3600 / v["commercial_speed_kmh"])
    patterns = [pattern(stops, run, v["dwell_s"], km, v["speed_cap_kmh"]),
                pattern([{**s, "fraction": 1-s["fraction"]} for s in reversed(stops)],
                        run, v["dwell_s"], km, v["speed_cap_kmh"])]
    trips, fleet = workings(group, plan, run, layover, v["peak_headway_s"])
    # An optimistic lower bound on full-tail exit. Extra platform dwell is applied
    # before clearing the upstream section because the train stops at its boundary.
    tail = math.ceil(cfg["vehicle_geometry"]["train_length_m"] * 3.6 / v["speed_cap_kmh"])
    gaps = []
    for direction, offsets in enumerate(patterns):
        departures = [d for _, side, d, _ in trips if side == direction]
        min_interval = min(b-a for a, b in pairwise(departures))
        for a, b in pairwise(offsets):
            occupy = b["departure_s"] - a["departure_s"] + tail
            gaps.append((min_interval - occupy, a["id"], b["id"]))
    margin, start, end = min(gaps)
    by_train = defaultdict(list)
    for train, side, dep, arr in trips:
        by_train[train].append((side, dep, arr))
    linked = [later[1] - earlier[2] for t in by_train.values() for earlier, later in pairwise(t)]
    start_stock = [sum(t[0][0] == side for t in by_train.values()) for side in (0, 1)]
    end_stock = [sum(t[-1][0] == 1-side for t in by_train.values()) for side in (0, 1)]
    return {"sets_starting_at_A_B": start_stock, "sets_finishing_at_A_B": end_stock,
            "scheduled_trips": len(trips), "diagrammed_sets": fleet, "one_way_km": km,
            "one_way_s_including_dwell": run, "minimum_turn_s": layover,
            "linked_turns": len(linked), "shortest_linked_turn_s": min(linked),
            "peak_terminal_positions_minimum_each_end": math.ceil(layover / v["peak_headway_s"]),
            "terminal_B_phase_s": (run + layover) % v["peak_headway_s"],
            "whole_interstop_block_conflicts_at_peak": sum(gap < 0 for gap, _, _ in gaps),
            "worst_block_clearance_margin_s": margin, "worst_block_from_to": [start, end],
            "outward_stops": patterns[0]}, trips, patterns


def interchanges(network, details, tail_s, walk_s=300):
    """Flag coincident intermediate calls if two groups require the same junction."""
    groups_at = defaultdict(set)
    for (net, group), (_, patterns) in details.items():
        if net == network:
            for call in patterns[0][1:-1]:
                hint = call.get("interchange_hint")
                if hint is not None:
                    groups_at[hint].add(group)
    shared = {hint: sorted(groups) for hint, groups in groups_at.items() if len(groups) > 1}
    calls = defaultdict(list)
    for (net, group), (trips, patterns) in details.items():
        if net != network:
            continue
        for i, (_, side, departure, _) in enumerate(trips, 1):
            for stop in patterns[side][1:-1]:
                hint = stop.get("interchange_hint")
                if hint in shared:
                    calls[hint].append((departure + stop["arrival_s"], departure + stop["departure_s"],
                                        group, f"{group}-T{i:03d}", stop["id"]))
    rows = []
    for hint, groups in sorted(shared.items()):
        events = defaultdict(Counter)
        for arrival, departure, group, _, _ in calls[hint]:
            events[arrival][group] += 1
            events[departure + tail_s][group] -= 1
        overlap = 0
        active = Counter()
        previous = min(events)
        for t, changes in sorted(events.items()):
            if sum(n > 0 for n in active.values()) > 1:
                overlap += t - previous
            active.update(changes)
            previous = t
        first = min(c for c in calls[hint] if c[2] == groups[0])
        departures = sorted((d, trip, stop) for _, d, g, trip, stop in calls[hint] if g == groups[1])
        conn = bisect_left(departures, (first[0] + walk_s,))
        example = None
        if conn < len(departures):
            dep, trip, stop = departures[conn]
            example = {"arriving_trip": first[3], "arriving_stop": first[4], "arrival_s": first[0],
                       "onward_trip": trip, "onward_stop": stop, "departure_s": dep,
                       "walk_allowance_s": walk_s, "wait_after_walk_s": dep - first[0] - walk_s}
        rows.append({"source_hint": hint, "groups": groups,
                     "overlap_seconds_if_shared_junction": overlap, "example_connection": example})
    return rows


def build():
    cfg = system.load()
    joined = json.loads((CITY / "system-results.json").read_bytes())
    register = json.loads((CITY / "station-register.json").read_bytes())
    if register != system.station_register(ROOT, cfg) or cfg["candidate_id"] != joined["candidate_id"]:
        raise ValueError("Stale Baghdad station or system identity")
    for name, digest in joined["source_sha256"].items():
        if sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Regenerate the Baghdad system ledger after changing {name}")
    receipt = {"candidate_id": cfg["candidate_id"], "source_system_evaluation_id": joined["evaluation_id"],
               "schema": "opensourcerail.baghdad.service-diagrams.1", "networks": {}}
    details = {}
    for network, n in cfg["networks"].items():
        source = joined["networks"][network]
        allowance = source["selected_service_allowance"]
        duty = allowance["service_duty"]
        lengths = duty["passenger_path_km_by_service_group"]
        points = register["networks"][network]["mapped_points"]
        if network == "first":
            review = json.loads((CITY / "maps/corridor-review.geojson").read_bytes())
            if any(sha256((ROOT / path).read_bytes()).hexdigest() != value
                   for path, value in review["source_sha256"].items()):
                raise ValueError("Stale Baghdad corridor review")
            paths = first_paths(json.loads((CITY / "maps/rfi-waypoints.json").read_bytes())["waypoints"],
                                points, review)
            receipt["corridor_review_sha256"] = sha256((CITY / "maps/corridor-review.geojson").read_bytes()).hexdigest()
            holds = {}
        else:
            features = json.loads((ROOT / cfg["map_sources"]["metropolitan_path"]).read_bytes())["features"]
            paths, holds = metro_paths(features, points, n["service_groups"], source["map_and_service_coverage"])
        if set(paths) | set(holds) != set(lengths):
            raise ValueError("Every costed service group needs a diagram or an explicit hold")
        groups = {}
        held_sets = 0
        days = cfg["vehicle"]["service_days_per_year"]
        for group, km in lengths.items():
            if group in holds:
                round_trip = 2 * (km * 3600 / cfg["vehicle"]["commercial_speed_kmh"]
                                  + 60 * duty["terminal_layover_min_each_end"])
                held_sets += math.ceil(round_trip / cfg["vehicle"]["peak_headway_s"])
            else:
                groups[group], trips, patterns = group_diagram(group, paths[group], km, cfg)
                details[network, group] = trips, patterns
        km_day = sum(g["scheduled_trips"] * g["one_way_km"] for g in groups.values())
        held_km = 2 * duty["daily_departures_per_direction_per_group"] * sum(lengths[g] for g in holds)
        if not math.isclose((km_day + held_km) * days, duty["annual_train_km"]):
            raise ValueError("Diagram mileage no longer reconciles to the operating cost ledger")
        sets = sum(g["diagrammed_sets"] for g in groups.values())
        receipt["networks"][network] = {
            "selected_candidate_id": source["selected_candidate_id"],
            "selected_system_evaluation_id": source["selected_evaluation_id"],
            "groups": groups,
            "intermediate_interchanges": interchanges(network, details, math.ceil(
                cfg["vehicle_geometry"]["train_length_m"] * 3.6 / cfg["vehicle"]["speed_cap_kmh"])),
            "held_service_group_ids": sorted(holds), "hold_reasons": holds,
            "all_groups_diagrammed": not holds, "diagrammed_sets": sets,
            "held_peak_trainsets_cost_screen": held_sets, "active_sets": n["active_trainsets"],
            "total_fleet_sets": n["fleet_trainsets"], "annual_diagrammed_train_km": km_day * days,
            "annual_held_cost_ledger_train_km": held_km * days,
            "annual_cost_ledger_train_km": duty["annual_train_km"],
            "diagrammed_train_seconds_per_day": sum(g["scheduled_trips"] *
                (g["one_way_s_including_dwell"] + g["minimum_turn_s"]) for g in groups.values())}
    receipt["evaluation_id"] = system._id({"data": receipt, "method": sha256(Path(__file__).read_bytes()).hexdigest()})
    return receipt, details


def operator_card(receipt, details):
    """Pack two actual out-and-back workings per group for the offline workshop."""
    data = {}
    for network, report in receipt["networks"].items():
        groups = {}
        for name, group in report["groups"].items():
            trips, patterns = details[network, name]
            labels = {c["id"]: c["label"] for c in patterns[0]}
            examples = {}
            for initial_direction in (0, 1):
                train = next(t for t, d, _, _ in trips if d == initial_direction)
                legs = [(i, d, dep, arr) for i, (t, d, dep, arr) in enumerate(trips, 1) if t == train][:2]
                times = defaultdict(list)
                for _, d, dep, _ in legs:
                    calls = patterns[d]
                    for j, call in enumerate(calls):
                        times[call["id"]].append(([dep + call["arrival_s"]] if j else [])
                            + ([dep + call["departure_s"]] if j+1 < len(calls) else []))
                examples[train] = {"train": train, "trips": [
                    {"id": f"{name}-T{i:03d}", "arrival": arr, "departure": dep}
                    for i, _, dep, arr in legs], "stops": [
                        {"label": c["label"], "times": times[c["id"]]} for c in patterns[legs[0][1]]]}
            connection = None
            for transfer in report["intermediate_interchanges"]:
                ex = transfer["example_connection"]
                if ex and any(trip.rsplit("-T", 1)[0] == name for trip in (ex["arriving_trip"], ex["onward_trip"])):
                    point = transfer["source_hint"] if network == "first" else f'Map junction {transfer["source_hint"]}'
                    connection = (f'{point} · {ex["arriving_trip"]} to {ex["onward_trip"]}. '
                                  f'Allow {ex["walk_allowance_s"]} s to change platforms and '
                                  f'{ex["wait_after_walk_s"]} s before departure. Walking time needs a site check.')
                    break
            a, b = group["worst_block_from_to"]
            groups[name] = {"sets": group["diagrammed_sets"], "km": group["one_way_km"],
                            "count": group["scheduled_trips"], "layover": group["minimum_turn_s"],
                            "from": labels[a], "to": labels[b], "margin": group["worst_block_clearance_margin_s"],
                            "samples": examples, "connection": connection}
        caveat = ("The seven first-network diagrams use named areas and equal timing distances. "
                  "Thirteen of 52 named occurrences still lack locations." if network == "first" else
                  "Ten citywide groups have train diagrams. Four groups await a workable branch or junction. "
                  "Station timings use scaled schematic distances.")
        data[network] = {"groups": groups, "holds": report["hold_reasons"], "caveat": caveat}
    template = (CITY / "engineering/service-diagrams.template.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    return template.replace("__DIAGRAM_DATA__", payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--write", action="store_true")
    action.add_argument("--events", choices=("first", "metropolitan"), help="Print station events as UTF-8 CSV")
    parser.add_argument("--group", help="Filter events to a service group")
    parser.add_argument("--train", help="Filter events to one diagrammed train")
    args = parser.parse_args()
    receipt, details = build()
    if args.events:
        network = receipt["networks"][args.events]
        if args.group and args.group not in network["groups"]:
            parser.error(f"Group {args.group} is unknown or held: {network['hold_reasons'].get(args.group, '')}")
        writer = csv.writer(sys.stdout)
        rows = 0
        writer.writerow(["group", "train", "trip", "direction", "stop", "register_id", "label",
                         "arrive_local_s", "depart_local_s", "next_stop"])
        for (scenario, group), (trips, patterns) in details.items():
            if scenario != args.events or args.group and args.group != group:
                continue
            for i, (train, side, departure, _) in enumerate(trips):
                if args.train and args.train != train:
                    continue
                calls = patterns[side]
                for j, call in enumerate(calls):
                    writer.writerow([group, train, f"{group}-T{i+1:03d}", "in" if side else "out",
                                     call["id"], call["register_id"], call["label"],
                                     departure + call["arrival_s"] if j else None,
                                     departure + call["departure_s"] if j < len(calls)-1 else None,
                                     calls[j+1]["id"] if j+1 < len(calls) else None])
                    rows += 1
        if rows == 0:
            parser.error("No train events match the filter")
    else:
        data = json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        outputs = {PUBLICATION: data, PUBLICATION.with_suffix(".html"): operator_card(receipt, details)}
        for path, body in outputs.items():
            if args.write:
                path.write_text(body, encoding="utf-8")
            elif path.read_text(encoding="utf-8") != body:
                raise SystemExit(f"Stale {path.name}; regenerate with --write")
        print(receipt["evaluation_id"])


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.stdout.close()

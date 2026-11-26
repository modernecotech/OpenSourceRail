"""Simplify Baghdad's mapped trunks and consolidate nearby station calls."""

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from math import cos, radians
from pathlib import Path

import numpy as np

from . import central_access, holistic_network, network_station_sites, rail_duplication
from .network_trunks import CENTRAL_ANCHORS, EAST_JUNCTION, WESTERN_M03
from .rail_consolidation import refresh_interchange_names
from .residential_layouts import LineEdit, _clip, _rebuild_memberships


@dataclass(frozen=True)
class Layout:
    name: str
    withdrawn: tuple[str, ...] = ()
    trimmed: tuple[LineEdit, ...] = ()
    eastern_through: bool = False


AIRPORT_PARALLEL = LineEdit(
    "M05", "Test C1 on the Airport approach and retain the eastern M05 corridor.",
    start_station="X-C1-M05-01",
)
EAST_BRANCH = LineEdit(
    "M06", "Retain the southwestern M06 approach to the M03 crossing, with a turnback to verify.",
    end_station=EAST_JUNCTION,
)
LAYOUTS = {
    "mapped-through-services": Layout("Through service at compatible mapped termini"),
    "parallel-withdrawals": Layout(
        "Withdraw the G04, G05 and T40 parallel overlays",
        withdrawn=("G04", "G05", "T40"),
    ),
    "east-south-trunks": Layout(
        "Retain the northern M03 reach on a continuous M06 trunk",
        withdrawn=("G04", "G05", "T40"),
        trimmed=(WESTERN_M03,),
        eastern_through=True,
    ),
    "outer-east-transfer": Layout(
        "Retain M03 across the east with M06 terminating at the crossing",
        withdrawn=("G04", "G05", "T40"),
        trimmed=(EAST_BRANCH, AIRPORT_PARALLEL),
    ),
    "fewer-radials": Layout(
        "Compare fewer overlay services and a shorter Airport parallel approach",
        withdrawn=("G02", "G04", "G05", "G07", "G20", "T40"),
        trimmed=(AIRPORT_PARALLEL,),
    ),
    "metropolitan-spines": Layout(
        "Compare concentrating service on metropolitan spines and ring connections",
        withdrawn=("G02", "G04", "G05", "G07", "G13", "G20", "M13", "T13", "T19", "T40"),
        trimmed=(AIRPORT_PARALLEL,),
    ),
}

JUNCTION_CHORD_KM = .4
MAX_JUNCTION_DEFLECTION_DEG = 30
CLOSE_SITE_M = 280.


def _join(network, first, second, stop, *, first_endpoint, second_endpoint):
    """Pair two nominated source intervals only at a common mapped position."""
    lines, stations = network["lines"], network["stations"]
    a, b = lines[first], lines[second]
    a_track, b_track = (holistic_network.Track(row["geometry"]) for row in (a, b))
    a_km, b_km = (row["station_chainage_km"][stop] for row in (a, b))
    a_index, b_index = (row["station_ids"].index(stop) for row in (a, b))
    point_a, point_b = a_track.at(a_km), b_track.at(b_km)
    station = stations[stop]["coordinates"]
    if any(network_station_sites._metres(left, right) > holistic_network.EXACT_CROSSING_M
           for left, right in ((point_a, point_b), (station, point_a), (station, point_b))):
        raise ValueError("Mapped junction does not coincide with both source track positions")
    if network_station_sites._metres(point_a, point_b) > 1e-5:
        raise ValueError("Mapped track endpoints would need a connector")
    a_end, b_end = first_endpoint * a_track.km, second_endpoint * b_track.km
    if min(abs(a_km - a_end), abs(b_km - b_end)) < JUNCTION_CHORD_KM:
        raise ValueError("Mapped junction lacks the 400 m source approach and departure chords")
    a_sign = 1 if a_end > a_km else -1
    b_sign = 1 if b_end > b_km else -1
    arrival = (np.asarray(point_a) - a_track.at(a_km + a_sign * JUNCTION_CHORD_KM))
    departure = (np.asarray(b_track.at(b_km + b_sign * JUNCTION_CHORD_KM)) - point_b)
    arrival *= holistic_network.LOCAL_METRES
    departure *= holistic_network.LOCAL_METRES
    if np.dot(arrival, departure) < np.linalg.norm(arrival) * np.linalg.norm(departure) * cos(
            radians(MAX_JUNCTION_DEFLECTION_DEG)):
        raise ValueError("Mapped junction exceeds the 30° through chord screen")
    a_geometry = a_track.between(min(a_end, a_km), max(a_end, a_km))
    b_geometry = b_track.between(min(b_end, b_km), max(b_end, b_km))
    a_stops = a["station_ids"][:a_index + 1] if a_sign == -1 else a["station_ids"][a_index:][::-1]
    b_stops = b["station_ids"][b_index:] if b_sign == 1 else b["station_ids"][:b_index + 1][::-1]
    if set(a_stops) & set(b_stops) != {stop}:
        raise ValueError("Through route would call at another station twice")
    if a_sign == 1:
        a_geometry.reverse()
    if b_sign == -1:
        b_geometry.reverse()
    geometry = holistic_network._concatenate(a_geometry, b_geometry)
    stops = a_stops + b_stops[1:]
    basis = ("Provisional through route at a common mapped junction. Verify track connection, turnout "
             "geometry, grade, capacity, clearances and interlocking.")
    result = holistic_network._physical_line(geometry, stops, stations,
                                             a["source_sections"] + b["source_sections"], basis)
    result["name"] = f"{stations[stops[0]]['name']}–{stations[stops[-1]]['name']}"
    return result, {
        "action": "through_pairing", "line_id": first, "source_line_ids": [first, second],
        "junction_station_id": stop, "basis": basis,
        "retained_source_chainage_km": {first: sorted([a_end, a_km]), second: sorted([b_end, b_km])},
        "source_directions": {first: -a_sign, second: b_sign},
    }


def _pair_terminals(network, fixed, actions):
    rejected = []
    used = set()
    lines = network["lines"]
    for first, a in list(sorted(lines.items())):
        if first in fixed or first in used or first not in lines:
            continue
        for a_end, stop in enumerate((a["station_ids"][0], a["station_ids"][-1])):
            candidates = (set(network["stations"][stop]["lines"]) & lines.keys()) - fixed - used - {first}
            for second in sorted(candidates):
                b = lines[second]
                if stop not in (b["station_ids"][0], b["station_ids"][-1]):
                    continue
                b_end = int(stop == b["station_ids"][-1])
                try:
                    merged, action = _join(network, first, second, stop, first_endpoint=1 - a_end,
                                           second_endpoint=1 - b_end)
                except ValueError as error:
                    failure = {"source_line_ids": sorted((first, second)), "junction_station_id": stop,
                               "reason": str(error)}
                    if failure not in rejected:
                        rejected.append(failure)
                    continue
                lines[first] = merged
                del lines[second]
                summaries = network.get("through_lines", {})
                source_summaries = [summaries.pop(code) for code in (first, second) if code in summaries]
                if source_summaries:
                    required = {stop for row in source_summaries for stop in row["required_intermediate_transfer_ids"]}
                    summaries[first] = {
                        "required_intermediate_transfer_ids": sorted(required),
                        "terminal_link_only": False,
                    }
                used.update((first, second))
                actions.append(action)
                break
            if first in used:
                break
    return rejected


def _membership_and_links(network):
    _rebuild_memberships(network)
    stations = network["stations"]
    network["station_site_links"] = [
        row for row in network.get("station_site_links", [])
        if set(row["station_ids"]) <= stations.keys()
        and not set(stations[row["station_ids"][0]]["lines"]) & set(stations[row["station_ids"][1]]["lines"])
    ]


def _apply(network, layout, fixed, protected):
    revised = deepcopy(network)
    lines = revised["lines"]
    actions = []
    for code in layout.withdrawn:
        if code not in lines:
            continue
        if code in fixed:
            raise ValueError(f"{code} is a protected route")
        row = lines.pop(code)
        actions.append({"action": "withdraw_line", "line_id": code, "withdrawn_calls": row["station_ids"],
                        "removed_route_km": round(row["one_way_km"], 3)})
    for edit in layout.trimmed:
        if edit.line_id not in lines or edit.line_id in fixed:
            raise ValueError(f"{edit.line_id} is unavailable for the proposed trim")
        row = lines[edit.line_id]
        lines[edit.line_id], intervals = _clip(row, edit, revised["stations"])
        actions.append({"action": "trim", "line_id": edit.line_id, "reason": edit.reason,
                        "retained_source_chainage_km": intervals,
                        "removed_route_km": round(row["one_way_km"] - lines[edit.line_id]["one_way_km"], 3),
                        "withdrawn_calls": [s for s in row["station_ids"]
                                            if s not in lines[edit.line_id]["station_chainage_km"]]})
    if layout.eastern_through:
        if {"M03", "M06"} & fixed or {"M03", "M06"} - lines.keys():
            raise ValueError("The eastern through layout requires both M03 and M06 to be available")
        east, action = _join(network, "M06", "M03", EAST_JUNCTION, first_endpoint=0, second_endpoint=1)
        a, b = network["lines"]["M06"], network["lines"]["M03"]
        retained_north_km = b["one_way_km"] - b["station_chainage_km"][EAST_JUNCTION]
        western_trim = next(row for row in actions if row["action"] == "trim" and row["line_id"] == "M03")
        western_trim["reassigned_route_km"] = round(retained_north_km, 3)
        western_trim["removed_route_km"] = round(western_trim["removed_route_km"] - retained_north_km, 3)
        action["removed_route_km"] = round(a["one_way_km"] + retained_north_km - east["one_way_km"], 3)
        action["withdrawn_calls"] = [s for s in a["station_ids"] if s not in east["station_chainage_km"]]
        lines["M06"] = east
        actions.append(action)
    rejected = _pair_terminals(revised, fixed, actions)
    _membership_and_links(revised)
    if lost := protected - revised["stations"].keys():
        raise ValueError(f"Protected stations would close: {', '.join(sorted(lost))}")
    for edit in layout.trimmed:
        for stop in (edit.start_station, edit.end_station):
            if stop and len(revised["stations"][stop]["lines"]) < 2:
                raise ValueError(f"{edit.line_id} loses the proposed interchange at {stop}")
    revised["topology"] = holistic_network.validate(revised)
    survivors = revised["stations"]
    for action in actions:
        action["closed_stations"] = [s for s in action.get("withdrawn_calls", []) if s not in survivors]
    return revised, actions, rejected


def _consolidate(network, graph, context, protected):
    """Every absorbed site must have a direct two-way walk to its final retained site."""
    revised = deepcopy(network)
    stations, lines = revised["stations"], revised["lines"]
    terminals = network_station_sites._endpoints(lines)
    anchors = protected | terminals
    raw_pairs = network_station_sites._nearby(stations)
    neighbors = {}
    for distance, first, second in raw_pairs:
        neighbors.setdefault(first, []).append((distance, second))
        neighbors.setdefault(second, []).append((distance, first))
    _, path = network_station_sites._street_paths(graph, network_station_sites._water_tree(context))
    tracks = {code: holistic_network.Track(row["geometry"]) for code, row in lines.items()}
    actions, held, links = [], [], []
    keepers, linked = set(), set()
    existing_links = {tuple(sorted(row["station_ids"])): row for row in revised["station_site_links"]}

    def walks(first, second):
        if first == second:
            if holistic_network.dry_points([first], context)[0]:
                return (0., [first]), (0., [second])
            return None, None
        return path(first, second), path(second, first)

    def priority(stop):
        row = stations[stop]
        return stop not in anchors, -len(row["lines"]), stop

    for keep in sorted(neighbors, key=priority):
        if keep not in stations:
            continue
        keeper = stations[keep]
        members = []
        for distance, retire in sorted(neighbors[keep]):
            if (retire not in stations or retire in anchors or retire in keepers
                    or distance > CLOSE_SITE_M):
                continue
            retired = stations[retire]
            first, second = (row["coordinates"] for row in (keeper, retired))
            inbound, outbound = walks(first, second)
            if outbound is None or inbound is None:
                continue
            shared = set(keeper["lines"]) & set(retired["lines"])
            distances = [round(outbound[0], 2), round(inbound[0], 2)]
            if shared:
                if len(retired["lines"]) != 1:
                    continue
                code, = shared
                line = lines[code]
                a, b = (line["station_chainage_km"][stop] for stop in (keep, retire))
                indexes = [line["station_ids"].index(stop) for stop in (keep, retire)]
                adjacent = abs(indexes[0] - indexes[1]) == 1 or (
                    line["loop"] and abs(indexes[0] - indexes[1]) == len(line["station_ids"]) - 1)
                if (not adjacent or network_station_sites._separation(line, a, b)
                        > network_station_sites.REDUNDANT_CALL_M):
                    continue
                line["station_ids"].remove(retire)
                del line["station_chainage_km"][retire]
                del stations[retire]
                action = {"kind": "retire_adjacent_call", "line_id": code,
                          "retired_chainage_km": b, "retained_chainage_km": a}
            else:
                chainages = {code: lines[code]["station_chainage_km"][stop]
                             for stop, row in ((keep, keeper), (retire, retired)) for code in row["lines"]}
                if distance > network_station_sites.EXACT_SITE_M or any(
                        network_station_sites._metres(first, tracks[code].at(km))
                        > holistic_network.SOURCE_STOP_SNAP_M for code, km in chainages.items()):
                    continue
                action = network_station_sites._merge(stations, lines, tracks, keep, retire, first, chainages,
                                                       "Co-located mapped platforms")
            actions.append(action | {"kept_station_id": keep, "retired_station_id": retire,
                                     "retired_station": retired, "replacement_walks_m": distances,
                                     "replacement_walk_geometry": [outbound[1], inbound[1]]})
            members.append(retire)
        if members:
            keepers.add(keep)

    # Keep separate stations where their routes still need calls. Add a measured
    # pedestrian interchange only if the two actual mapped walks are direct links.
    proposals = []
    for distance, first, second in network_station_sites._nearby(stations):
        if set(stations[first]["lines"]) & set(stations[second]["lines"]):
            if distance <= CLOSE_SITE_M:
                held.append({"station_ids": [first, second], "straight_m": round(distance, 2),
                             "reason": "Distinct retained calls share a route"})
            continue
        outbound, inbound = walks(stations[first]["coordinates"], stations[second]["coordinates"])
        if outbound is None or inbound is None or min(outbound[0], inbound[0]) <= network_station_sites.EXACT_SITE_M:
            if distance <= CLOSE_SITE_M:
                held.append({"station_ids": [first, second], "straight_m": round(distance, 2),
                             "reason": "No eligible two-way pedestrian interchange"})
            continue
        proposals.append((max(outbound[0], inbound[0]), first, second, distance, outbound, inbound))
    for _, first, second, distance, outbound, inbound in sorted(proposals):
        if linked & {first, second}:
            if distance <= CLOSE_SITE_M:
                held.append({"station_ids": [first, second], "straight_m": round(distance, 2),
                             "reason": "One station has a shorter walking interchange"})
            continue
        previous = existing_links.get((first, second), {})
        key = sha256(central_access.encode([first, second])).hexdigest()[:12]
        links.append({"id": previous.get("id", f"W-{key}"), "station_ids": [first, second],
                      "walks_m": [round(outbound[0], 2), round(inbound[0], 2)],
                      "geometry": [outbound[1], inbound[1]], "straight_m": round(distance, 2),
                      "status": "separate complexes linked by public street",
                      "basis": "Retained pedestrian graph with provisional dry station-to-street connectors"})
        linked.update((first, second))

    previous = {row["id"]: row for row in revised["transfers"]}
    revised["transfers"] = [
        previous.get(stop, {"id": stop, "station_ids": [stop], "walking_m": None, "basis": row["basis"]})
        | {"name": row["name"], "lines": sorted(row["lines"])}
        for stop, row in sorted(stations.items()) if len(row["lines"]) > 1
    ]
    revised["station_site_links"] = links
    _membership_and_links(revised)
    revised["topology"] = holistic_network.validate(revised)
    clusters = {keep: [row["retired_station_id"] for row in actions if row["kept_station_id"] == keep]
                for keep in sorted(keepers)}
    report = {"actions": actions, "clusters": clusters, "held": held, "walking_links": links,
              "close_site_m": CLOSE_SITE_M, "replacement_walk_limit_m": network_station_sites.WALK_LIMIT_M,
              "access_basis": "Co-located calls retain the same dry mapped station position. Distinct positions "
                              "require both mapped pedestrian paths. Confirm public frontage, step-free access, "
                              "vertical circulation and platform layouts by survey."}
    return revised, report


def _metrics(network, screen):
    pairs = network_station_sites._nearby(network["stations"], CLOSE_SITE_M)
    duplication = rail_duplication.screen(network["lines"], **screen)
    by_kind = Counter()
    for row in duplication["runs"]:
        by_kind[row["kind"]] += row["length_m"]
    return {**network["topology"], "close_site_pairs": len(pairs),
            "nearby_parallel_pair_km": round(by_kind["nearby_parallel"] / 1000, 3),
            "common_alignment_pair_km": round(by_kind["common_alignment"] / 1000, 3),
            "overlap_runs": duplication["runs"], "overlap_screen": duplication["settings"]}


def alternatives(network, *, graph, context, protected_stations=(), screen=None):
    """Return bounded planning trials preserving supplied rings and the Airport route."""
    holistic_network.validate(network)
    fixed = {code for code, row in network["lines"].items() if row["loop"]}
    fixed |= {"C1", "C2", "M09", "M10", "M11", "M15"} & network["lines"].keys()
    protected = set(protected_stations) | (set(CENTRAL_ANCHORS) & network["stations"].keys())
    protected.update(stop for code in fixed for stop in network["lines"][code]["station_ids"])
    screen = dict(screen or {})
    reference = _metrics(network, screen)
    options = {}
    for code, layout in LAYOUTS.items():
        trial = {"name": layout.name, "network": None, "actions": [], "source_metrics": reference}
        options[code] = trial
        try:
            revised, actions, rejected = _apply(network, layout, fixed, protected)
            revised, audit = _consolidate(revised, graph, context, protected)
            for fixed_code in fixed:
                intended, actual = network["lines"][fixed_code], revised["lines"][fixed_code]
                if any(intended[key] != actual[key] for key in ("geometry", "station_ids", "station_chainage_km")):
                    raise ValueError(f"{fixed_code} changed under the protected route constraint")
        except ValueError as error:
            trial["rejection_reason"] = str(error)
            continue
        revised["physical_accepted"] = revised["operating_timetable_validated"] = False
        revised["layout_revision"] = {"parent_candidate_id": network["candidate_id"],
                                      "parent_evaluation_id": network["evaluation_id"],
                                      "trial_id": code, "actions": actions,
                                      "terminal_turnback_validated": False}
        revised.setdefault("source_sha256", {})[Path(__file__).relative_to(central_access.ROOT).as_posix()] = (
            central_access.digest(Path(__file__)))
        revised = refresh_interchange_names(revised)
        trial.update(network=revised, actions=actions, station_audit=audit, metrics=_metrics(revised, screen),
                     rejected_through_pairings=rejected)
    return options

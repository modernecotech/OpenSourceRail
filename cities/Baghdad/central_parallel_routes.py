"""Bounded Baghdad route layouts that remove selected parallel guideway."""

from collections import defaultdict
from copy import deepcopy
from itertools import pairwise
from pathlib import Path

from . import holistic_network, rail_duplication, residential_layouts
from .central_access import ROOT, digest


RINGS = ("M09", "M15")
FIXED = ("C1", *RINGS)
# Each cut must remove a measured parallel interval, and an interior cut also
# needs a reasonably direct path over the surviving railway.
MIN_REMOVED_PARALLEL_M = 750
MAX_INTERIOR_DETOUR_FACTOR = 2.0
MAX_INTERIOR_LEGS = 2


def _retained_transfer(network, line_id, station_id, partner):
    line = network["lines"][line_id]
    if station_id in line["station_ids"] and partner in network["stations"][station_id]["lines"]:
        return station_id
    matches = [stop for stop in line["station_ids"] if partner in network["stations"][stop]["lines"]]
    if len(matches) != 1:
        raise ValueError(f"{line_id} needs an unambiguous {partner} interchange for a turnback")
    return matches[0]


def _end_trim(network, line_id, station_id, partner, parallel):
    stop = _retained_transfer(network, line_id, station_id, partner)
    line = network["lines"][line_id]
    return {"line_id": line_id, "parallel": parallel, "from": stop, "to": line["station_ids"][-1],
            "terminals": [stop], "reason": f"Turn {line_id} at {partner} and retain {parallel} on the parallel corridor."}


def _m04_gap(network):
    first = _retained_transfer(network, "M04", "M-135", "M09")
    last = _retained_transfer(network, "M04", "X-M01-M04-01", "M01")
    return {"line_id": "M04", "parallel": "M09", "from": first, "to": last,
            "terminals": [first, last], "branch_id": "M04-SE",
            "reason": "Turn the two M04 branches at M09 and M01 and connect them using the retained routes."}


def _c2_gap(network):
    first = _retained_transfer(network, "C2", "X-C2-M02-01", "M02")
    line = network["lines"]["C2"]
    km = line["station_chainage_km"]
    ring = [stop for stop in line["station_ids"][1:-1]
            if km[stop] > km[first] and "M15" in network["stations"][stop]["lines"]]
    if not ring:
        raise ValueError("C2 needs a shared M15 interchange between M02 and University")
    return {"line_id": "C2", "parallel": "M15", "from": first, "to": ring[0],
            "terminals": [first, ring[0]], "branch_id": "C2-U",
            "reason": "Retain both C2 branches, including Tahrir and University, with the retained network bridging the cut."}


def _rail_bridge(network, cut):
    """Find a short replacement over at most two uncut rail services."""
    # Distances describe a physical routing screen only. Waiting, walk and
    # additional changes are accounted for in the separate passenger assignment.
    start, end = cut["from"], cut["to"]
    legs = defaultdict(list)
    for code, line in sorted(network["lines"].items()):
        if code in (cut["line_id"], cut["branch_id"]):
            continue
        distances = line["station_chainage_km"]
        for first in (start, end):
            if first not in distances:
                continue
            for stop, distance in distances.items():
                if stop == first:
                    continue
                km = abs(distance - distances[first])
                if line["loop"]:
                    km = min(km, line["one_way_km"] - km)
                legs[first].append((stop, code, km))

    options = [(km, (code,), None) for stop, code, km in legs[start] if stop == end]
    end_legs = defaultdict(list)
    for stop, code, km in legs[end]:
        end_legs[stop].append((code, km))
    for stop, code, km in legs[start]:
        for next_code, next_km in end_legs[stop]:
            if code != next_code:
                options.append((km + next_km, (code, next_code), stop))
    if not options:
        raise ValueError(f"{cut['line_id']} gap has no bridge over at most {MAX_INTERIOR_LEGS} retained rail services")
    km, lines, change = min(options)
    if km > cut["removed_route_km"] * MAX_INTERIOR_DETOUR_FACTOR:
        raise ValueError(f"{cut['line_id']} gap requires {km:.2f} km over retained services for "
                         f"{cut['removed_route_km']:.2f} km of removed guideway")
    return {"lines": list(lines), "transfer_id": change, "route_km": round(km, 3)}


def _apply(network, cuts, protected_stations, runs):
    revised = deepcopy(network)
    actions = []
    for cut in cuts:
        code = cut["line_id"]
        line = network["lines"][code]
        start, end = cut["from"], cut["to"]
        if code in FIXED or line["loop"]:
            raise ValueError(f"{code} has fixed geometry")
        km = line["station_chainage_km"]
        removed = km[end] - km[start]
        targeted_m = sum(max(0., min(km[end] * 1000, bounds[1]) - max(km[start] * 1000, bounds[0]))
                         for run in runs if set(run["lines"]) == {code, cut["parallel"]}
                         for bounds in [run["chainage_m"][code]])
        if targeted_m < MIN_REMOVED_PARALLEL_M:
            raise ValueError(f"{code} cut removes only {targeted_m:.0f} m of aligned overlap with {cut['parallel']}")
        retain, prefix = residential_layouts._clip(
            line, residential_layouts.LineEdit(code, cut["reason"], end_station=start), revised["stations"])
        revised["lines"][code] = retain
        retained_stops = set(retain["station_ids"])
        intervals = prefix
        if branch := cut.get("branch_id"):
            if branch in revised["lines"]:
                raise ValueError(f"Branch ID {branch} is already in use")
            tail, suffix = residential_layouts._clip(
                line, residential_layouts.LineEdit(code, cut["reason"], start_station=end), revised["stations"])
            revised["lines"][branch] = tail
            retained_stops.update(tail["station_ids"])
            intervals = prefix + suffix
        actions.append(cut | {"action": "split" if branch else "trim",
                              "removed_route_km": round(removed, 3),
                              "removed_source_chainage_km": [km[start], km[end]],
                              "retained_source_chainage_km": intervals,
                              "screened_removed_overlap_m": round(targeted_m, 1),
                              "withdrawn_calls": [stop for stop in line["station_ids"] if stop not in retained_stops]})

    residential_layouts._rebuild_memberships(revised)
    if missing := set(protected_stations) - revised["stations"].keys():
        raise ValueError(f"Protected stations removed: {', '.join(sorted(missing))}")
    surviving_links = []
    for link in revised.get("station_site_links", []):
        closed = set(link["station_ids"]) - revised["stations"].keys()
        if not closed:
            surviving_links.append(link)
            continue
        for action in actions:
            if closed.intersection(action["withdrawn_calls"]):
                action.setdefault("removed_walking_links", []).append({
                    "id": link["id"],
                    "station_ids": link["station_ids"],
                    "walks_m": link["walks_m"],
                    "closed_station_ids": sorted(closed),
                    "reason": "A platform used by this measured walking link closes with the parallel cut.",
                })
    if "station_site_links" in revised:
        revised["station_site_links"] = surviving_links
    for action in actions:
        for stop in action["terminals"]:
            if len(revised["stations"][stop]["lines"]) < 2:
                raise ValueError(f"{action['line_id']} lost its turnback interchange at {stop}")
        action["closed_stations"] = sorted(set(action["withdrawn_calls"]) - revised["stations"].keys())
        if action.get("branch_id"):
            action["replacement_rail_path"] = _rail_bridge(revised, action)
    if len([code for code, line in revised["lines"].items() if code not in RINGS and all(
            set(line["station_ids"]) & set(revised["lines"][ring]["station_ids"]) for ring in RINGS)]) < 2:
        raise ValueError("The revised layout needs at least two direct routes serving both rings")
    revised["topology"] = holistic_network.validate(revised)
    revised["physical_accepted"] = False
    revised["operating_timetable_validated"] = False
    revised["central_parallel_layout"] = {
        "parent_candidate_id": network["candidate_id"], "parent_evaluation_id": network["evaluation_id"],
        "actions": actions, "turnback_geometry_validated": False, "shared_running_assumed": False,
    }
    revised.setdefault("source_sha256", {})[Path(__file__).relative_to(ROOT).as_posix()] = digest(Path(__file__))
    return holistic_network._identity(revised), actions


def alternatives(network, graph, context, *, screen, protected_stations):
    """Generate cuts on either the retained or an updated inner ring layout.

    The supplied walking graph and geographic context are reserved for the
    paired study. These cuts reuse mapped station sites already in the network.
    """
    runs = rail_duplication.screen(network["lines"], **screen)["runs"]
    protected = set(protected_stations) | set(network["lines"]["C1"]["station_ids"])

    def g09_c2():
        return _end_trim(network, "G09", "X-G09-C2-b31c466f28", "C2", "RG1-92")

    def g09_m01():
        return _end_trim(network, "G09", "X-G09-M01-9ae1c6a498", "M01", "RG1-92")

    def m06_t23():
        return _end_trim(network, "M06", "X-T23-M06-ccc6895978", "T23", "M03")

    options = (
        ("parallel-m06-turnback", "M06 turns back at T23", (m06_t23,)),
        ("parallel-m06-northern-gap", "M06 turns back at T23 with an M04 gap",
         (m06_t23, lambda: _m04_gap(network))),
        ("parallel-terminal-trims", "G09 to C2 and M06 to T23", (g09_c2, m06_t23)),
        ("parallel-m01-turnback", "G09 to M01 and M06 to T23", (g09_m01, m06_t23)),
        ("parallel-northern-gap", "G09 and M06 turnbacks with an M04 gap",
         (g09_m01, m06_t23, lambda: _m04_gap(network))),
        ("parallel-ring-gaps", "G09 and M06 turnbacks with M04 and C2 gaps",
         (g09_m01, m06_t23, lambda: _m04_gap(network), lambda: _c2_gap(network))),
    )
    variants = {}
    for key, name, build in options:
        actions = []
        try:
            for operation in build:
                actions.append(operation())
            revised, actions = _apply(network, actions, protected, runs)
        except ValueError as error:
            variants[key] = {"network": None, "actions": actions, "name": name, "rejection_reason": str(error)}
        else:
            variants[key] = {"network": revised, "actions": actions, "name": name, "rejection_reason": None}
    return variants

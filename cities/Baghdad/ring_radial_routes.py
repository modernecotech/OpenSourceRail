"""Test Baghdad cross-city routes on the retained wider dual rings."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import numpy as np

from . import (
    central_access, holistic_network as rail, network_station_sites, rail_duplication,
    spaced_ring_geometry, spaced_ring_layouts,
)
from .rail_consolidation import refresh_interchange_names
from .residential_layouts import LineEdit, _clip
from .ring_corridors import _refresh_transfers
from .ring_grid_comparison import PROTECTED

RINGS = {"M09", "M15"}
FIXED_ROUTES = RINGS | {"C1", "C2", "M10", "M11"}
INNER = "M15"


def _inner_crossings(network, code, graph, context):
    lines = network["lines"]
    tracks = [rail.Track(lines[line]["geometry"]) for line in (INNER, code)]
    candidates = sorted(rail._crossings(*tracks).items())
    dry = rail.dry_points([point for point, _ in candidates], context)
    for (point, chainages), usable in zip(candidates, dry, strict=True):
        offset, _ = graph[3].query(np.asarray(point) * rail.LOCAL_METRES)
        if usable and offset <= rail.TRANSFER_SNAP_M:
            yield point, chainages, float(offset)


def _add_stop(network, stop, point, chainage, lines, offset, name):
    stations = network["stations"]
    if stop in stations or rail._stations_at_crossing(stations, point):
        raise ValueError(f"An existing station occupies {name}")
    for code, km in zip(lines, chainage, strict=True):
        rail._through_station_spacing(code, stop, km, network["lines"])
    stations[stop] = {"coordinates": list(point), "lines": sorted(lines), "name": name,
                      "basis": "Dry mapped crossing near retained pedestrian graph",
                      "street_offset_m": round(offset, 1)}
    for code, km in zip(lines, chainage, strict=True):
        rail._add(network["lines"][code], stop, km)


def _walk_link(network, first, second, path):
    stations = network["stations"]
    locations = [stations[stop]["coordinates"] for stop in (first, second)]
    walks = [path(*locations), path(*reversed(locations))]
    if any(walk is None or walk[0] <= rail.EXACT_CROSSING_M for walk in walks):
        raise ValueError("No two-way dry pedestrian path within the station-link limit")
    if any({first, second} & set(link["station_ids"]) for link in network["station_site_links"]):
        raise ValueError("A nominated platform already has a walking interchange")
    key = sha256(central_access.encode([first, second])).hexdigest()[:12]
    link = {"id": f"W-{key}", "station_ids": [first, second],
            "walks_m": [round(walk[0], 2) for walk in walks],
            "geometry": [walk[1] for walk in walks],
            "straight_m": round(network_station_sites._metres(*locations), 2),
            "status": "separate complexes linked by public street",
            "basis": "Two directed dry paths on the retained pedestrian graph"}
    network["station_site_links"].append(link)
    return link


def _m02_access(network, graph, context):
    code, linked_stop = "M02", "X-C1-M02-01"
    if linked_stop not in network["lines"][code]["station_ids"]:
        raise ValueError("M02 and C1 must retain the existing crossing platform")
    if set(network["lines"][INNER]["station_ids"]) & set(network["lines"][code]["station_ids"]):
        raise ValueError("M02 already calls at the inner ring")
    _, path = network_station_sites._street_paths(graph, network_station_sites._water_tree(context))
    candidates = [
        (abs(network["lines"][code]["station_chainage_km"][linked_stop] - radial), point, ring, offset)
        for point, (ring, radial), offset in _inner_crossings(network, code, graph, context)
    ]
    if not candidates:
        raise ValueError("M02 has no dry crossing within reach of a mapped street")
    _, point, ring, offset = min(candidates)
    stop = "M15-M02-west"
    _add_stop(network, stop, point, [ring], [INNER], offset, "Inner ring · M02 west transfer")
    link = _walk_link(network, stop, linked_stop, path)
    return {"action": "walk_interchange", "line_id": INNER, "connecting_line_id": code,
            "station_id": stop, "ring_chainage_km": ring, "walking_link": link}


def _g09_terminal(network, graph, context):
    code, stop = "G09", "X-M15-G09-terminus"
    lines = network["lines"]
    original = lines[code]
    if not set(lines["M09"]["station_ids"]) & set(original["station_ids"]):
        raise ValueError("G09 needs its existing outer-ring interchange")
    candidates = [(radial, ring, point, offset) for point, (ring, radial), offset
                  in _inner_crossings(network, code, graph, context)
                  if 1. <= original["one_way_km"] - radial <= 2.]
    if len(candidates) != 1:
        raise ValueError("G09 needs one dry inner-ring crossing on its final 1–2 km")
    radial, ring, point, offset = candidates[0]
    parallel = rail_duplication.screen(lines, pair_filter=[("C1", code)])["runs"]
    replaced = sum(max(0., min(run["chainage_m"][code][1], original["one_way_km"] * 1000)
                       - max(run["chainage_m"][code][0], radial * 1000)) for run in parallel)
    if replaced < (original["one_way_km"] - radial) * 500:
        raise ValueError("Less than half the proposed G09 trim overlaps the mapped C1 parallel approach")
    # The intervening stop beyond the turnback is removed, so it cannot
    # constrain station spacing on the new passenger route.
    retained = [station for station in original["station_ids"]
                if original["station_chainage_km"][station] < radial]
    if radial - original["station_chainage_km"][retained[-1]] < rail.INTERCHANGE_SPACING_M / 1000:
        raise ValueError("The preceding retained G09 call is too close to the proposed terminal")
    _add_stop(network, stop, point, [ring], [INNER], offset, "Inner ring · G09 terminus")
    network["stations"][stop]["lines"].append(code)
    rail._add(original, stop, radial)
    lines[code], intervals = _clip(original, LineEdit(
        code, "Turn back at the inner ring and use retained C1 for the parallel eastern approach.",
        end_station=stop), network["stations"])
    return {"action": "ring_turnback", "line_id": code, "ring_id": INNER, "station_id": stop,
            "retained_source_chainage_km": intervals, "ring_chainage_km": ring,
            "removed_route_km": original["one_way_km"] - lines[code]["one_way_km"],
            "trim_length_with_mapped_c1_parallel_m": round(replaced, 1),
            "withdrawn_calls": [station for station in original["station_ids"] if station not in retained + [stop]],
            "turnback_validated": False}


def _west_southeast(network, _graph, _context):
    trunk, branch, stop = "M04", "T19", "M04-infill-28500"
    lines = network["lines"]
    junction_line, action = spaced_ring_layouts._join(
        network, trunk, branch, stop, first_endpoint=0, second_endpoint=0)
    former_trunk, intervals = _clip(lines[trunk], LineEdit(
        trunk, "Keep the original eastern branch from the mapped M04–T19 junction.",
        start_station=stop), network["stations"])
    if set(lines[trunk]["station_ids"] + lines[branch]["station_ids"]) != set(
            junction_line["station_ids"] + former_trunk["station_ids"]):
        raise ValueError("Through pairing must retain every original station")
    original_km = lines[trunk]["one_way_km"] + lines[branch]["one_way_km"]
    if abs(junction_line["one_way_km"] + former_trunk["one_way_km"] - original_km) > 1e-6:
        raise ValueError("Through pairing must account for every source track interval")
    lines[trunk], lines[branch] = junction_line, former_trunk
    # Inherit intermediate transfer obligations on the physical track that
    # the original T19 used, now operated by the M04 through service.
    summaries = network.get("through_lines", {})
    if branch in summaries:
        summaries[trunk] = summaries.pop(branch)
    return action | {"remainder_line_id": branch, "remainder_source_chainage_km": intervals,
                     "removed_route_km": 0., "retains_all_stops": True}


def _finish(network, parent, key, actions):
    gap = spaced_ring_geometry.separation(network["lines"]["M09"], network["lines"][INNER]["geometry"])
    if gap["minimum_ring_separation_m"] < spaced_ring_geometry.MIN_SEPARATION_M:
        raise ValueError("Continuous ring separation falls below the retained 5 km requirement")
    _refresh_transfers(network)
    spaced_ring_layouts._membership_and_links(network)
    protected = set(PROTECTED) & parent["stations"].keys()
    for code in FIXED_ROUTES:
        if network["lines"][code]["geometry"] != parent["lines"][code]["geometry"]:
            raise ValueError(f"{code} must retain its original continuous alignment")
        protected.update(parent["lines"][code]["station_ids"])
        if code not in RINGS and network["lines"][code] != parent["lines"][code]:
            raise ValueError(f"{code} must retain its alignment and calls")
    if any(network["stations"].get(stop, {}).get("coordinates") != parent["stations"][stop]["coordinates"]
           for stop in protected):
        raise ValueError("The trial alters a named centre or retained mainline or ring station")
    for action in actions:
        if "withdrawn_calls" in action:
            action["closed_stations"] = [stop for stop in action["withdrawn_calls"]
                                         if stop not in network["stations"]]
    network["topology"] = rail.validate(network)
    network["physical_accepted"] = network["operating_timetable_validated"] = False
    network["layout_revision"] = {
        "parent_candidate_id": parent["candidate_id"], "parent_evaluation_id": parent["evaluation_id"],
        "trial_id": key, "actions": actions, "terminal_turnback_validated": False,
    }
    source = Path(__file__)
    network.setdefault("source_sha256", {})[source.relative_to(central_access.ROOT).as_posix()] = (
        central_access.digest(source))
    return refresh_interchange_names(network)


def alternatives(network, graph, context):
    """Return bounded transfer, ring turnback and real-junction route trials."""
    options = {
        "m02-inner-walk": ("M02 transfer to the inner ring", (_m02_access,)),
        "g09-ring-turnback": ("G09 turns back at the inner ring", (_g09_terminal,)),
        "ring-interchange-trunks": ("M02 interchange and G09 turnback at the inner ring",
                                    (_m02_access, _g09_terminal)),
        "west-southeast-through": ("West–southeast through service and two new inner-ring links",
                                    (_m02_access, _g09_terminal, _west_southeast)),
        "west-southeast-junction": ("West–southeast through service at the mapped M04–T19 junction",
                                     (_west_southeast,)),
    }
    result = {}
    for key, (name, edits) in options.items():
        network_copy, actions = deepcopy(network), []
        row = {"name": name, "network": None, "actions": actions, "rejection_reason": None}
        result[key] = row
        try:
            for edit in edits:
                actions.append(edit(network_copy, graph, context))
            row["network"] = _finish(network_copy, network, key, actions)
        except ValueError as error:
            row["rejection_reason"] = str(error)
    return result

"""Compare shorter Baghdad layouts on retained guideway and station chainage."""

from collections import defaultdict
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from math import fsum
from pathlib import Path

import numpy as np

from .central_access import ROOT, WALK_M, digest
from .holistic_access import walk_to_station
from .holistic_network import Track, _concatenate, _identity, validate


PROTECTED_LINES = frozenset({"C1", "C2", "M10", "M11", "T01", "T20"})


@dataclass(frozen=True)
class LineEdit:
    line_id: str
    reason: str
    start_station: str | None = None
    end_station: str | None = None


TERMINAL_TRIMS = (
    LineEdit("M02", "End at the retained G05 transfer before the final Dhat al-Salasil stop.",
             end_station="M02-infill-51900"),
    LineEdit("M03", "End the southern branch at the M08 transfer near Arkoob al-Haji al-Sharqi.",
             start_station="X-M03-M08-01"),
    LineEdit("M04", "End the southeastern branch at the existing T13 and T23 transfer.",
             end_station="M04-infill-39000"),
    LineEdit("M12", "End the northern branch at M04.", end_station="X-M04-M12-01"),
    LineEdit("M14", "End the western branch at M04 while retaining the northern cross-city trunk.",
             start_station="X-M04-M14-01"),
)
WESTERN_TRIMS = (
    LineEdit("G02", "End the southwest extension at M09 and retain M08 and G08 transfers.",
             start_station="X-G02-M09-81b67738bd"),
    LineEdit("G08", "End the southwest extension at C1 and retain the cross-city links north of it.",
             start_station="X-G08-C1-6bba3a2720"),
    LineEdit("G20", "End the northwestern extension at G05 and keep the links to M05, M09 and M02.",
             end_station="X-G05-G20-960f64440b"),
)
FEEDER_TRIMS = (
    LineEdit("M06", "End the northeastern branch at M09 and retain the inner M03 and T05 transfers.",
             end_station="X-M06-M09-01"),
    LineEdit("M13", "End the eastern branch at M01 and retain the G11, G07 and M09 transfers.",
             end_station="X-M01-M13-01"),
    LineEdit("G13", "End at C2 and retain the central connection from the west.",
             end_station="X-G13-C2-a5c34faeae"),
)
LAYOUTS = {
    "terminal-trims": TERMINAL_TRIMS,
    "western-tail-trims": TERMINAL_TRIMS + WESTERN_TRIMS,
    "extended-feeder-trims": TERMINAL_TRIMS + WESTERN_TRIMS + FEEDER_TRIMS,
    "open-orbital-short": TERMINAL_TRIMS + (
        LineEdit("M09", "Open the outer ring between M07 and M03 and retain the western and northern arc.",
                 "X-M03-M09-01", "X-M07-M09-02"),
    ),
    "open-orbital-east": TERMINAL_TRIMS + (
        LineEdit("M09", "Open a longer outer arc between M06 and M03, with east-side transfers on the remaining arc.",
                 "X-M03-M09-01", "X-M06-M09-01"),
    ),
    "western-bypass-withdrawal": TERMINAL_TRIMS + (
        LineEdit("G02", "Test withdrawal of the full western bypass, with M12, M08, G08 and M09 retained."),
    ),
}


def _clip(line, edit, stations):
    """Clip a retained track at its own projected platform positions."""
    if line["loop"] and not (edit.start_station and edit.end_station):
        raise ValueError(f"{edit.line_id} orbital requires two nominated termini")
    order = line["station_ids"]
    first = edit.start_station or order[0]
    last = edit.end_station or order[-1]
    if first not in order or last not in order or first == last:
        raise ValueError(f"{edit.line_id} needs two distinct stations on the retained alignment")
    new_terminals = [stop for stop, requested in ((first, edit.start_station), (last, edit.end_station))
                     if requested is not None]
    if any(len(stations[stop]["lines"]) < 2 for stop in new_terminals):
        raise ValueError(f"{edit.line_id} must turn back at a retained interchange")

    chainage = line["station_chainage_km"]
    start, end = chainage[first], chainage[last]
    first_index, last_index = order.index(first), order.index(last)
    track = Track(line["geometry"])
    if first_index < last_index:
        geometry = track.between(start, end)
        survivors = order[first_index:last_index + 1]
        distances = {stop: chainage[stop] - start for stop in survivors}
        intervals = [[start, end]]
    elif line["loop"]:
        geometry = _concatenate(track.between(start, track.km),
                                track.between(0., end) if end else [])
        survivors = order[first_index:] + order[:last_index + 1]
        distances = {stop: (chainage[stop] - start if chainage[stop] >= start
                            else track.km - start + chainage[stop]) for stop in survivors}
        intervals = [[start, track.km]] + ([[0., end]] if end else [])
    else:
        raise ValueError(f"{edit.line_id} terminal order reverses an open alignment")
    length = Track(geometry).km
    if track.km - length <= 1e-7:
        raise ValueError(f"{edit.line_id} edit must shorten the retained alignment")
    distances[last] = length
    name = f"{stations[first]['name']}–{stations[last]['name']}"
    revised = line | {"geometry": geometry, "station_ids": survivors, "loop": False, "name": name,
                      "station_chainage_km": distances, "one_way_km": length,
                      "basis": f"{edit.reason} {line['basis']}"}
    return revised, intervals


def _rebuild_memberships(network):
    stations = network["stations"]
    memberships = defaultdict(list)
    for line, row in sorted(network["lines"].items()):
        for stop in row["station_ids"]:
            memberships[stop].append(line)
    network["stations"] = {stop: stations[stop] | {"lines": codes} for stop, codes in sorted(memberships.items())}
    previous = {row["id"]: row for row in network["transfers"]}
    network["transfers"] = [previous[stop] | {"lines": codes}
                            for stop, codes in sorted(memberships.items()) if len(codes) > 1]
    if "through_lines" in network:
        summaries = {}
        for code, summary in network["through_lines"].items():
            if code not in network["lines"]:
                continue
            route = network["lines"][code]["station_ids"]
            shared = [stop for stop in route if len(memberships[stop]) > 1]
            required = summary["required_intermediate_transfer_ids"]
            active = [stop for stop in required if stop in shared and stop in route[1:-1]]
            summaries[code] = summary | {"terminal_ids": [route[0], route[-1]],
                                         "transfer_ids": shared, "transfer_count": len(shared),
                                         "required_intermediate_transfer_ids": active}
            if active != required:
                summaries[code]["former_intermediate_transfer_ids"] = [stop for stop in required if stop not in active]
        network["through_lines"] = summaries


def apply_edits(network, edits, *, protected_stations=()):
    """Rebuild a layout from retained alignments and validate the passenger graph."""
    edits = tuple(edits)
    revised = deepcopy(network)
    actions = []
    edited = set()
    for edit in edits:
        code = edit.line_id
        if code in PROTECTED_LINES or code in edited:
            raise ValueError(f"{code} is protected or has more than one layout edit")
        edited.add(code)
        source = revised["lines"][code]
        if edit.start_station or edit.end_station:
            line, intervals = _clip(source, edit, revised["stations"])
            revised["lines"][code] = line
            action = "open_orbital" if source["loop"] else "trim"
            retained_stops = line["station_ids"]
            termini = [retained_stops[0], retained_stops[-1]]
            length = line["one_way_km"]
        else:
            del revised["lines"][code]
            action, termini, retained_stops, intervals, length = "withdraw_line", [], [], [], 0.
        actions.append({"line_id": code, "action": action, "reason": edit.reason,
                        "retained_source_chainage_km": intervals, "new_terminal_ids": termini,
                        "withdrawn_calls": [stop for stop in source["station_ids"] if stop not in retained_stops],
                        "removed_route_km": round(source["one_way_km"] - length, 3)})
    _rebuild_memberships(revised)
    if missing := set(protected_stations) - revised["stations"].keys():
        raise ValueError(f"Protected stations removed: {', '.join(sorted(missing))}")
    for edit, action in zip(edits, actions, strict=True):
        new_terminals = [stop for stop in (edit.start_station, edit.end_station) if stop is not None]
        if any(len(revised["stations"][stop]["lines"]) < 2 for stop in new_terminals):
            raise ValueError(f"{edit.line_id} lost a new terminal interchange after the combined edits")
        action["closed_stations"] = [stop for stop in action["withdrawn_calls"] if stop not in revised["stations"]]
        action["retained_station_calls_on_other_lines"] = [stop for stop in action["withdrawn_calls"]
                                                          if stop in revised["stations"]]
    revised["topology"] = validate(revised)
    revised["physical_accepted"] = False
    revised["operating_timetable_validated"] = False
    revised["layout_revision"] = {"parent_candidate_id": network["candidate_id"],
                                   "parent_evaluation_id": network["evaluation_id"], "actions": actions,
                                   "terminal_turnback_validated": False}
    revised.setdefault("source_sha256", {})[Path(__file__).relative_to(ROOT).as_posix()] = digest(Path(__file__))
    return _identity(revised), actions


def _coordinates(network):
    return {stop: station["coordinates"] for stop, station in network["stations"].items()}


def _loss_locations(population, lost, cell_m=1_000, count=5):
    if not lost.any():
        return []
    _, membership = np.unique(np.floor(population.xy[lost] / cell_m), axis=0, return_inverse=True)
    weights = population.counts[lost]
    totals = np.bincount(membership, weights=weights)
    centroids = np.column_stack([
        np.bincount(membership, weights=axis * weights) / totals for axis in population.coordinates[lost].T
    ])
    order = np.argsort(-totals, kind="stable")[:count]
    return [{"coordinates": np.round(centroids[i], 6).tolist(),
             "estimated_residents": round(float(totals[i]), 2)} for i in order]


def _housing_access(population, previous, actual):
    summary = {}
    for limit in WALK_M:
        covered = actual <= limit
        lost = (previous <= limit) & ~covered
        summary[str(limit)] = {
            "estimated_residents_within_walk": round(float(population.counts[covered].sum()), 2),
            "estimated_residents_losing_walk_access": round(float(population.counts[lost].sum()), 2),
            "largest_loss_cells_approx_1_km": _loss_locations(population, lost),
        }
    return summary


def alternatives(network, population, graph, centres=None):
    """Return candidate network records and exact unique-pixel walk-access changes.

    A centre keyed by a station ID also protects that stop from deletion.
    Walking access is to any retained station using the existing street graph.
    Central journeys require a separate rail transfer and travel-time calculation.
    """
    validate(network)
    protected = set(centres or {}) & network["stations"].keys() if isinstance(centres, Mapping) else ()
    previous, _ = walk_to_station(_coordinates(network), graph, population)
    original_length = fsum(line["one_way_km"] for line in network["lines"].values())
    variants = {}
    for code, edits in LAYOUTS.items():
        revised, actions = apply_edits(network, edits, protected_stations=protected)
        actual, _ = walk_to_station(_coordinates(revised), graph, population)
        access = _housing_access(population, previous, actual)
        retained_length = fsum(line["one_way_km"] for line in revised["lines"].values())
        variants[code] = {"network": revised, "actions": actions, "housing_access": access,
                          "removed_route_km": round(original_length - retained_length, 2)}
    return variants

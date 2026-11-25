"""Retained-alignment repairs for Baghdad rail duplications."""

from copy import deepcopy
from math import fsum
from pathlib import Path
import re

import numpy as np

from .central_access import ROOT, digest
from .holistic_network import (EXACT_CROSSING_M, INTERCHANGE_SPACING_M, LOCAL_METRES, TRANSFER_SNAP_M,
                               Track, _add, _identity, _terminal_margin, dry_points)
from .residential_layouts import LineEdit, PROTECTED_LINES, apply_edits


M09_BRANCH = "X-G05-M09-7ab38c970b"
EAST_BRANCH_AT_ORBITAL = LineEdit(
    "G05", "Keep G09 from the M02 terminus and turn G05 back at the existing M09 interchange.",
    start_station=M09_BRANCH,
)
EAST_BRANCH_AT_M01 = LineEdit(
    "G05", "Keep G09 from M02 to C2 and start the distinct eastern G05 branch at its M01 interchange.",
    start_station="X-G05-M01-fb56ee3f1b",
)
CENTRAL_BRANCH_AT_M01 = LineEdit(
    "G09", "Keep G05 from M02 to M04 and start the distinct G09 branch at its M01 interchange.",
    start_station="X-G09-M01-9ae1c6a498",
)
KARKH = LineEdit(
    "G02", "Use M12 out of M-187 and begin G02 at its first existing M09 interchange.",
    start_station="X-G02-M09-81b67738bd",
)
SOUTHEAST_ORBITAL = LineEdit(
    "T23", "Use T13 out of the shared M04 terminus and turn T23 back at its existing M06 interchange.",
    end_station="X-T23-M06-ccc6895978",
)
SOUTHEAST_SADR = LineEdit(
    "T13", "Use T23 out of the shared M04 terminus and turn T13 back at its existing M06 interchange.",
    start_station="X-T13-M06-8aad239570",
)
NORTHWEST = LineEdit(
    "G20", "Use M04 out of M-062 and end G20 at its existing interchange with the M02 trunk routes.",
    end_station="X-G05-G20-960f64440b",
)
G04_NEAR_M01 = LineEdit(
    "G04", "Use M01 for the closely parallel central section and end G04 at its M02 interchange.",
    end_station="X-G04-M02-9bd2ba701f",
)
G04_AT_M04 = LineEdit(
    "G04", "Retain the western route and its M02, M01 and G09 transfers. End G04 at M04 before the last parallel section.",
    end_station="X-G04-M04-0ed651dfac",
)
G04_AT_G05 = LineEdit(
    "G04", "Retain the western route and its M02, M01 and G09 transfers. End G04 at G05 before the last parallel section.",
    end_station="X-G04-G05-b8bde83065",
)
M13_NEAR_M07 = LineEdit(
    "M13", "Use M07 for the southwestern departure and start M13 at its G11 interchange.",
    start_station="X-G11-M13-801fcd1bd6",
)

LAYOUTS = {
    "northwest-m09-branch": ("G05 branch from M09", (EAST_BRANCH_AT_ORBITAL,)),
    "northwest-g09-trunk": ("G09 trunk and G05 branch from M01", (EAST_BRANCH_AT_M01,)),
    "northwest-g05-trunk": ("G05 trunk and G09 branch from M01", (CENTRAL_BRANCH_AT_M01,)),
    "karkh-m12-departure": ("M12 departure from Karkh", (KARKH,)),
    "southeast-t13-departure": ("T13 departure from southeastern M04", (SOUTHEAST_ORBITAL,)),
    "southeast-t23-departure": ("T23 departure from southeastern M04", (SOUTHEAST_SADR,)),
    "northern-m04-departure": ("M04 departure from M-062", (NORTHWEST,)),
    "g04-at-m04": ("G04 ends at M04", (G04_AT_M04,)),
    "g04-at-g05": ("G04 ends at G05", (G04_AT_G05,)),
    "g04-interchange-core": ("G04 between M02 and M04", (
        LineEdit("G04", "Retain the central G04 links from M02 to M04.",
                 start_station="X-G04-M02-9bd2ba701f", end_station="X-G04-M04-0ed651dfac"),
    )),
    "g08-north-at-g13": ("G08 retains its southern links and ends at G13", (
        LineEdit("G08", "Use northern M04 and G20 approaches and end the southern G08 route at G13.",
                 end_station="X-G08-G13-2066606f1c"),
    )),
    "g07-west-at-m13": ("G07 ends at M13", (
        LineEdit("G07", "Keep the C1 and M09 connections and remove the tail that parallels M07.",
                 end_station="X-G07-M13-8d33ab4698"),
    )),
    "g13-at-m09": ("G13 starts at M09", (
        LineEdit("G13", "Keep the central G13 links to C2 and M04 and remove the southwestern parallel approach.",
                 start_station="X-G13-M09-68597f429e"),
    )),
    "t40-at-m01": ("T40 ends at M01", (
        LineEdit("T40", "Keep the Sadr–M01 link and test removing the short leg towards the M14 parallel section.",
                 end_station="X-T40-M01-57aff7e2e4"),
    )),
    "combined-g09-trunk": ("G09 trunk with Karkh, southeast and northern trims",
                          (EAST_BRANCH_AT_M01, KARKH, SOUTHEAST_ORBITAL, NORTHWEST)),
    "combined-g05-trunk": ("G05 trunk with Karkh, southeast and northern trims",
                          (CENTRAL_BRANCH_AT_M01, KARKH, SOUTHEAST_SADR, NORTHWEST)),
    "g04-at-m02": ("G04 ends at M02", (G04_NEAR_M01,)),
    "m13-at-g11": ("M13 starts at G11", (M13_NEAR_M07,)),
    "northwest-and-close-parallels": ("G09 trunk and the G04 and M13 parallel sections",
                                      (EAST_BRANCH_AT_M01, G04_NEAR_M01, M13_NEAR_M07)),
    "combined-g09-trunk-and-parallels": (
        "G09 trunk with Karkh, southeast, northern and close-parallel trims",
        (EAST_BRANCH_AT_M01, KARKH, SOUTHEAST_ORBITAL, NORTHWEST, G04_NEAR_M01, M13_NEAR_M07),
    ),
    "combined-g09-trunk-partial-g04": (
        "G09 trunk with southeast, northern and partial G04 and M13 trims",
        (EAST_BRANCH_AT_M01, SOUTHEAST_SADR, NORTHWEST, G04_AT_M04, M13_NEAR_M07),
    ),
    "combined-g09-trunk-shorter-g04": (
        "G09 trunk with southeast, northern, shorter G04 and M13 trims",
        (EAST_BRANCH_AT_M01, SOUTHEAST_SADR, NORTHWEST, G04_AT_G05, M13_NEAR_M07),
    ),
    "combined-g09-trunk-m13": (
        "G09 trunk with southeast, northern and M13 trims",
        (EAST_BRANCH_AT_M01, SOUTHEAST_SADR, NORTHWEST, M13_NEAR_M07),
    ),
}


def _departure_trims(network, report, limit=8):
    """Offer bounded clips around detected runs using existing transfer chainages."""
    allowance_m = 250
    overshoot_m = 2_000
    seen = {(edit.line_id, edit.start_station, edit.end_station)
            for _, edits in LAYOUTS.values() for edit in edits}
    options = {}
    for run in report["runs"]:
        for code in run["lines"]:
            line = network["lines"][code]
            if code in PROTECTED_LINES or line["loop"]:
                continue
            start_m, end_m = run["chainage_m"][code]
            length_m = line["one_way_km"] * 1_000
            other, = set(run["lines"]) - {code}
            order = line["station_ids"]
            for from_start, margin_m, boundary_m in (
                (True, start_m, end_m),
                (False, length_m - end_m, length_m - start_m),
            ):
                if margin_m > allowance_m:
                    continue
                for stop in (order[1:-1] if from_start else order[-2:0:-1]):
                    if len(network["stations"][stop]["lines"]) < 2:
                        continue
                    stop_m = line["station_chainage_km"][stop] * 1_000
                    retained_boundary_m = stop_m if from_start else length_m - stop_m
                    if retained_boundary_m < boundary_m - allowance_m:
                        continue
                    if retained_boundary_m > boundary_m + overshoot_m:
                        break
                    start, end = (stop, None) if from_start else (None, stop)
                    key = (code, start, end)
                    if key not in seen:
                        seen.add(key)
                        reason = f"Shorten {code} at an existing transfer along the screened run with {other}."
                        option_id = f"screen-{code.lower()}-{'start' if from_start else 'end'}-{stop.lower()}"
                        options[option_id] = (reason, (LineEdit(code, reason, start, end),))
                    break
                if len(options) >= limit:
                    return options
    return options


def _divergence_interchange(network, graph, context, protected_stations):
    """Move the existing G09 stop 42 m to the common vertex and trim G05 there."""
    revised = deepcopy(network)
    east, central = (revised["lines"][code] for code in ("G05", "G09"))
    east_track, central_track = (Track(line["geometry"]) for line in (east, central))
    stop_id = "G09-S06"
    if stop_id not in central["station_chainage_km"]:
        raise ValueError("The G09 stop beside the divergence is absent")
    station = revised["stations"][stop_id]
    previous_coordinates = station["coordinates"]
    previous_km = central["station_chainage_km"][stop_id]
    matches = []
    for east_km in east_track.chainage[1:-1] / 1000:
        point = east_track.at(east_km)
        central_km, offset_m, _ = central_track.locate(point)
        if (offset_m > EXACT_CROSSING_M or abs(east_km - central_km) * 1000 > EXACT_CROSSING_M
                or not 0 < central_km < central_track.km):
            break
        matches.append((east_km, central_km, point))
    if not matches:
        raise ValueError("G05 and G09 have no verified common-prefix endpoint")
    east_km, central_km, point = matches[-1]
    # Require an exact common vertex before using it as the branch platform.
    previous_offset_m = float(np.linalg.norm((np.asarray(point) - previous_coordinates) * LOCAL_METRES))
    if (station["lines"] != ["G09"] or stop_id in protected_stations
            or previous_offset_m > TRANSFER_SNAP_M
            or not np.allclose(point, central_track.at(central_km), rtol=0, atol=1e-9)
            or not np.any(np.isclose(central_track.chainage, central_km * 1000, rtol=0, atol=1e-5))):
        raise ValueError("Existing G09 stop cannot be moved to the exact shared vertex")
    street_offset_m, _ = graph[3].query(np.asarray(point) * LOCAL_METRES)
    if street_offset_m > TRANSFER_SNAP_M or not dry_points([point], context)[0]:
        raise ValueError("Common vertex fails the mapped-street or dry-land screen")
    central["station_ids"].remove(stop_id)
    del central["station_chainage_km"][stop_id]
    if min(_terminal_margin(east, east_km), _terminal_margin(central, central_km)) < INTERCHANGE_SPACING_M:
        raise ValueError("Divergence station fails existing station-spacing rules")
    for line, chainage in ((east, east_km), (central, central_km)):
        _add(line, stop_id, float(chainage))
    reason = "Move the existing G09 stop to the exact shared vertex and begin G05 there."
    station.update({"coordinates": point, "lines": ["G05", "G09"],
                    "basis": "Provisional interchange at the mapped G05–G09 divergence",
                    "street_offset_m": round(float(street_offset_m), 1)})
    revised["transfers"].append({"id": stop_id, "name": station["name"], "station_ids": [stop_id],
                                 "lines": station["lines"], "walking_m": None, "basis": station["basis"]})
    revised, actions = apply_edits(
        revised, (LineEdit("G05", reason, start_station=stop_id),), protected_stations=protected_stations)
    actions.append({"line_id": "G09", "action": "move_stop", "reason": reason,
                    "station_id": stop_id, "previous_station_coordinates": previous_coordinates,
                    "new_station_coordinates": point, "previous_chainage_km": previous_km,
                    "new_chainage_km": float(central_km), "moved_distance_m": round(previous_offset_m, 1),
                    "street_offset_m": round(float(street_offset_m), 1), "removed_route_km": 0.,
                    "closed_stations": [], "withdrawn_calls": [], "retained_station_calls_on_other_lines": [],
                    "new_terminal_ids": []})
    return revised, actions


def alternatives(network, report, *, protected_stations=(), graph=None, context=None):
    """Return topology-checked clip candidates and explicit rejected trials."""
    protected_stations = frozenset(protected_stations)
    variants = {}
    options = LAYOUTS | _departure_trims(network, report)
    divergence = "northwest-g09-trunk-at-divergence"
    if graph is not None and context is not None:
        options[divergence] = ("G09 trunk with G05 interchange at the shared alignment split",
                               (EAST_BRANCH_AT_ORBITAL,))
    for code, (name, edits) in options.items():
        edited_lines = tuple(edit.line_id for edit in edits)
        if code == divergence:
            edited_lines = ("G05", "G09")
        if not set(edited_lines) <= network["lines"].keys():
            continue
        try:
            if code == divergence:
                revised, actions = _divergence_interchange(network, graph, context, protected_stations)
            else:
                revised, actions = apply_edits(network, edits, protected_stations=protected_stations)
        except ValueError as error:
            variants[code] = {"name": name, "network": None, "actions": [],
                              "edited_line_ids": list(edited_lines), "rejection_reason": str(error)}
            continue
        revised["source_sha256"][Path(__file__).relative_to(ROOT).as_posix()] = digest(Path(__file__))
        revised["layout_revision"]["consolidation_option"] = code
        revised = _identity(revised)
        difference = fsum(network["lines"][line]["one_way_km"] - revised["lines"][line]["one_way_km"]
                          for line in edited_lines)
        variants[code] = {"name": name, "network": revised, "actions": actions,
                          "edited_line_ids": list(edited_lines), "removed_route_km": round(difference, 3)}
    return variants


def refresh_interchange_names(network):
    """Keep source IDs durable and show the services that still use each stop."""
    renamed = {}
    for stop, station in network["stations"].items():
        name = station["name"]
        match = re.fullmatch(r"([A-Z]\d+)–([A-Z]\d+) interchange", name)
        codes = station["lines"]
        if not match or set(match.groups()) <= set(codes):
            continue
        if len(codes) > 1:
            replacement = "–".join(codes) + " interchange"
        else:
            code, = codes
            km = network["lines"][code]["station_chainage_km"][stop]
            replacement = f"{code} · km {km:.1f}"
        renamed[stop] = (name, replacement)
        station["name"] = replacement
    for transfer in network["transfers"]:
        if transfer["id"] in renamed:
            transfer["name"] = renamed[transfer["id"]][1]
    for line in network["lines"].values():
        for stop in (line["station_ids"][0], line["station_ids"][-1]):
            if stop in renamed:
                line["name"] = line["name"].replace(*renamed[stop])
    return _identity(network)

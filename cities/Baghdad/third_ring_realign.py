"""Rebind retained Baghdad inner-ring alignments to the current passenger network."""

from copy import deepcopy
from pathlib import Path

import numpy as np

from . import holistic_network as network
from . import residential_layouts
from . import ring_corridors as rings

ALIGNMENT_SOURCES = {
    "compact": network.CITY / "maps/baghdad-spaced-rings.geojson",
    "wider": network.CITY / "maps/baghdad-wider-ring.geojson",
}
MIN_CONNECTIONS = 3


def _remove_inner(reference):
    revised = deepcopy(reference)
    revised["lines"].pop(rings.INNER)
    residential_layouts._rebuild_memberships(revised)
    return revised


def _restore_links(revised, reference):
    stations = revised["stations"]
    kept, dropped = [], []
    for link in reference.get("station_site_links", []):
        first, last = link["station_ids"]
        if first not in stations or last not in stations:
            dropped.append(link["id"])
        elif set(stations[first]["lines"]) & set(stations[last]["lines"]):
            dropped.append(link["id"])
        else:
            kept.append(link)
    revised["station_site_links"] = kept
    return dropped


def _site(line, stations, km, name, point):
    code = f"{rings.INNER}-realign-{round(km * 1000):05d}"
    if code in stations:
        raise ValueError(f"Duplicate platform ID for revised {rings.INNER}: {code}")
    stations[code] = {
        "name": name,
        "coordinates": point,
        "lines": [rings.INNER],
        "basis": "Provisional platform on a retained mapped orbital study alignment",
    }
    network._add(line, code, km)


def _interchanges(revised, track, graph, context):
    lines, stations = revised["lines"], revised["stations"]
    candidates = [(code, point, chainages) for code in sorted(lines.keys() - {rings.INNER})
                  for point, chainages in network._crossings(track, network.Track(lines[code]["geometry"])).items()]
    points = np.asarray([row[1] for row in candidates]).reshape(-1, 2)
    offsets, _ = graph[3].query(points * network.LOCAL_METRES)
    dry = network.dry_points(points, context)
    selected = []
    for index in sorted(np.flatnonzero(dry & (offsets <= network.TRANSFER_SNAP_M)),
                        key=lambda index: (offsets[index], candidates[index])):
        code, point, chainages = candidates[index]
        try:
            stop = network._through_interchange(rings.INNER, {"line_id": code},
                                                (point, chainages), lines, stations,
                                                require_intermediate=False)
        except ValueError:
            continue
        stations[stop]["street_offset_m"] = round(float(offsets[index]), 1)
        selected.append({"station_id": stop, "line_id": code, "chainage_km": chainages[0]})
    return selected


def replace(reference, graph, context, *, alignment="wider"):
    """Screen a different published M15 alignment as a new planning candidate.

    The original study's route trace is reused. Its shared stops are recomputed
    from exact, dry crossings in the supplied network.
    """
    network.validate(reference)
    source_path = ALIGNMENT_SOURCES[alignment]
    source = network.read(source_path)
    feature = next(row for row in source["features"] if row["properties"].get("line_id") == rings.INNER
                   and row["properties"]["kind"] == "line")
    geometry = feature["geometry"]["coordinates"]
    revised = _remove_inner(reference)
    lines, stations = revised["lines"], revised["stations"]
    track = network.Track(geometry)
    line = lines[rings.INNER] = {
        "name": "Baghdad central orbital",
        "loop": True,
        "geometry": geometry,
        "one_way_km": track.km,
        "station_ids": [],
        "station_chainage_km": {},
        "source_sections": feature["properties"]["source_sections"],
        "basis": f"Mapped {alignment} M15 alignment reapplied to the current passenger network",
    }
    inner = rings._ring_polygon(line)
    outer = rings._ring_polygon(lines[rings.OUTER])
    if not outer.contains_properly(inner) or inner.equals(rings._ring_polygon(reference["lines"][rings.INNER])):
        raise ValueError("Revised M15 must use a different footprint wholly inside M09")
    source_stops = sorted(feature["properties"]["station_chainage_km"].items(), key=lambda row: row[1])
    points = np.asarray([track.at(km) for _, km in source_stops])
    offsets, _ = graph[3].query(points * network.LOCAL_METRES)
    eligible = network.dry_points(points, context) & (offsets <= network.TRANSFER_SNAP_M)
    if not eligible[0] or source_stops[0][1] != 0.:
        raise ValueError("Revised M15 origin needs a dry platform with mapped street access")
    _site(line, stations, 0., "Central orbital · reference platform", points[0].tolist())
    transfers = _interchanges(revised, track, graph, context)
    if len({row["line_id"] for row in transfers}) < MIN_CONNECTIONS:
        raise ValueError("Revised M15 has too few exact shared stations")
    for (stop, km), point, available in zip(source_stops[1:], points[1:], eligible[1:], strict=True):
        if available and network._terminal_margin(line, km) >= network.INTERCHANGE_SPACING_M:
            _site(line, stations, km, f"Central orbital · {stop}", point.tolist())
    rings._refresh_transfers(revised)
    dropped = _restore_links(revised, reference)
    residential_layouts._rebuild_memberships(revised)
    revised["topology"] = network.validate(revised)
    for source_file in (source_path, Path(__file__)):
        revised.setdefault("source_sha256", {})[source_file.relative_to(network.ROOT).as_posix()] = network.digest(source_file)
    revised["physical_accepted"] = revised["operating_timetable_validated"] = False
    revised["inner_ring_revision"] = {
        "alignment": alignment,
        "parent_candidate_id": reference["candidate_id"],
        "line_id": rings.INNER,
        "previous_km": reference["lines"][rings.INNER]["one_way_km"],
        "one_way_km": track.km,
        "minimum_M09_separation_m": inner.boundary.distance(outer.boundary),
        "station_count": len(line["station_ids"]),
        "shared_station_count": len({row["station_id"] for row in transfers}),
        "connecting_lines": sorted({row["line_id"] for row in transfers}),
        "dropped_walking_links": dropped,
    }
    return network._identity(revised)

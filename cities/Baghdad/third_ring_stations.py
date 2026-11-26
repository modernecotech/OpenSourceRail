"""Amalgamate nearby three-ring calls where the mapped alignments support one site."""

from copy import deepcopy
from functools import lru_cache
from itertools import combinations
from pathlib import Path

from . import holistic_network as model
from . import network_station_sites as sites

NEARBY_M = 650
MAX_RELOCATION_M = 350
MIN_CALL_SPACING_M = model.INTERCHANGE_SPACING_M


def _chainages(stations, lines, tracks, pair, point, protected):
    """Keep chainage origins and terminals fixed and suppress duplicate calls."""
    proposed = {}
    for code in sorted({code for stop in pair for code in stations[stop]["lines"]}):
        line, track = lines[code], tracks[code]
        calls = line["station_chainage_km"]
        current = [stop for stop in pair if stop in calls]
        fixed = [stop for stop in current if stop in protected]
        remaining = {stop: km for stop, km in calls.items() if stop not in current}
        if len(fixed) > 1 or len(remaining) + 1 < 2:
            return None
        if len(current) == 2:
            first, second = sorted(line["station_ids"].index(stop) for stop in current)
            gap = second - first
            if gap != 1 and not (line["loop"] and gap == len(calls) - 1):
                return None
        if fixed:
            km = calls[fixed[0]]
            if sites._metres(point, track.at(km)) > model.SOURCE_STOP_SNAP_M:
                return None
        else:
            km, lateral, _ = track.locate(point)
            if lateral > model.EXACT_CROSSING_M or not 0 < km < track.km:
                return None
        if any(sites._separation(line, km, calls[stop]) > MAX_RELOCATION_M + 1e-6 for stop in current):
            return None
        # An existing platform can retain its established spacing when its neighbor is absorbed.
        if not any(abs(km - calls[stop]) < 1e-8 for stop in current) and any(
                sites._separation(line, km, other) < MIN_CALL_SPACING_M - 1e-6 for other in remaining.values()):
            return None
        proposed[code] = km
    return proposed


def _walking_links(revised, keep, absorbed, point, proposed, street_path):
    """Graduate an internal transfer and preserve the paths of external links."""
    retained, finished, touched = [], [], []
    for link in revised.get("station_site_links", []):
        old = link["station_ids"]
        if not {keep, absorbed}.intersection(old):
            retained.append(link)
            continue
        pair = [keep if stop == absorbed else stop for stop in old]
        if pair[0] == pair[1]:
            # Each line remains available at one shared station, or the two
            # existing trains now serve an identical set of lines at that site.
            finished.append(link["id"])
            continue
        other = next(stop for stop in pair if stop != keep)
        if set(proposed).intersection(revised["stations"][other]["lines"]):
            return None
        if pair == old and list(point) == revised["stations"][keep]["coordinates"]:
            retained.append(link)
        else:
            locations = [point if stop == keep else revised["stations"][stop]["coordinates"] for stop in pair]
            paths = [street_path(*locations), street_path(*reversed(locations))]
            if any(path is None or path[0] <= model.EXACT_CROSSING_M for path in paths):
                return None
            retained.append(link | {"station_ids": pair, "walks_m": [round(row[0], 2) for row in paths],
                                    "geometry": [row[1] for row in paths],
                                    "straight_m": round(sites._metres(*locations), 2)})
            touched.append(link["id"])
    linked = [stop for link in retained for stop in link["station_ids"]]
    if len(linked) != len(set(linked)):
        return None
    return retained, finished, touched


def consolidate(network, *, graph, context, protected_stations=()):
    """Return the revised network and evidence for accepted and held nearby pairs.

    Keep guideways fixed. Absorption needs a dry shared location on the
    affected railway alignments and a mapped two-way street path from each
    displaced entrance. Terminals, loop origins and protected sites keep
    their IDs and coordinates. A previously amalgamated station can absorb
    another call without moving again in this pass.
    """
    model.validate(network)
    revised = deepcopy(network)
    stations, lines = revised["stations"], revised["lines"]
    tracks = {code: model.Track(line["geometry"]) for code, line in lines.items()}
    protected = set(protected_stations) | sites._endpoints(lines)
    snap, street_path = sites._street_paths(graph, sites._water_tree(context))
    actions, held = [], []

    @lru_cache(maxsize=None)
    def crossings(first, second):
        return model._crossings(tracks[first], tracks[second])

    def priority(stop):
        row = stations[stop]
        return stop not in protected, -len(row["lines"]), stop

    def plan(keep, absorbed):
        originals = [stations[stop]["coordinates"] for stop in (keep, absorbed)]
        positions = {tuple(originals[0])}
        if keep not in protected:
            positions.add(tuple(originals[1]))
            codes = sorted(set(stations[keep]["lines"]) | set(stations[absorbed]["lines"]))
            for first, second in combinations(codes, 2):
                positions.update(crossings(first, second))
        positions = sorted(positions, key=lambda point: (sum(sites._metres(point, p) for p in originals), point))
        reason = "No common alignment site within the relocation and call-spacing bounds."
        for point in positions:
            offsets = [sites._metres(point, original) for original in originals]
            if max(offsets) > MAX_RELOCATION_M or (set(stations[keep]["lines"]) == set(stations[absorbed]["lines"])
                                                   and point not in map(tuple, originals)):
                continue
            pair = (keep, absorbed)
            chainages = _chainages(stations, lines, tracks, pair, point, protected)
            if chainages is None:
                continue
            platforms = [tracks[code].at(km) for code, km in chainages.items()]
            if snap(point) is None or any(snap(tuple(platform)) is None for platform in platforms):
                reason = "Common site or platform failed the dry street-access screen."
                continue
            walks = {}
            for stop, original, offset in zip(pair, originals, offsets, strict=True):
                if offset <= model.EXACT_CROSSING_M:
                    continue
                outbound, inbound = street_path(original, point), street_path(point, original)
                if outbound is None or inbound is None:
                    reason = "Displaced entrance lacks a mapped two-way replacement walk within the limit."
                    break
                walks[stop] = [round(outbound[0], 2), round(inbound[0], 2)]
            else:
                links = _walking_links(revised, keep, absorbed, point, chainages, street_path)
                if links is not None:
                    return (point, chainages, walks, links), None
                reason = "Existing external walking transfers cannot be preserved in their mapped scope."
        return None, reason

    original_links = {frozenset(row["station_ids"]) for row in network.get("station_site_links", [])}
    nearby = sorted(sites._nearby(stations, NEARBY_M), key=lambda row: (
        frozenset(row[1:]) not in original_links, row))
    for distance, first, second in nearby:
        if first not in stations or second not in stations:
            continue
        keep, absorbed = sorted((first, second), key=priority)
        pair = {"station_ids": [keep, absorbed], "initial_straight_m": round(distance, 2)}
        if absorbed in protected:
            held.append(pair | {"reason": "Both stations retain fixed IDs and locations."})
            continue
        proposal, reason = plan(keep, absorbed)
        if proposal is None:
            held.append(pair | {"reason": reason})
            continue
        point, chainages, walks, links = proposal
        same_lines = set(stations[keep]["lines"]) == set(stations[absorbed]["lines"])
        kind = "Close train calls combined on retained alignment" if same_lines else "Shared mapped platform site"
        action = sites._merge(stations, lines, tracks, keep, absorbed, point, chainages, kind)
        revised["station_site_links"], graduated, rerouted = links
        actions.append(action | {"kind": "close_calls" if same_lines else "shared_site",
                                 "replacement_walks_m": walks,
                                 "graduated_walk_link_ids": graduated, "rerouted_walk_link_ids": rerouted})
        protected.add(keep)

    previous = {row["id"]: row for row in network["transfers"]}
    revised["transfers"] = [
        previous.get(stop, {"id": stop, "station_ids": [stop], "walking_m": None,
                            "basis": row.get("site_kind", row["basis"])})
        | {"name": row["name"], "lines": sorted(row["lines"])}
        for stop, row in sorted(stations.items()) if len(row["lines"]) > 1
    ]
    revised["topology"] = model.validate(revised)
    audit = {
        "source_candidate_id": network["candidate_id"],
        "source_evaluation_id": network["evaluation_id"],
        "station_sites_before": len(network["stations"]),
        "station_sites_after": len(stations),
        "train_calls_before": sum(len(line["station_ids"]) for line in network["lines"].values()),
        "train_calls_after": sum(len(line["station_ids"]) for line in lines.values()),
        "existing_walking_links_before": len(original_links),
        "existing_walking_links_after": len(revised.get("station_site_links", [])),
        "actions": actions,
        "held": held,
        "bounds": {
            "nearby_m": NEARBY_M, "max_displacement_m": MAX_RELOCATION_M,
            "max_two_way_replacement_walk_m": sites.WALK_LIMIT_M,
            "min_new_call_spacing_m": MIN_CALL_SPACING_M,
            "exact_crossing_m": model.EXACT_CROSSING_M,
            "fixed_platform_snap_m": model.SOURCE_STOP_SNAP_M,
        },
        "limitations": "GIS planning screen. Platform envelopes, vertical separation, step-free circulation, "
                       "emergency egress, land and construction need survey and design.",
    }
    source = Path(__file__)
    revised.setdefault("source_sha256", {})[source.relative_to(model.ROOT).as_posix()] = model.digest(source)
    revised["station_consolidation"] = audit
    revised["physical_accepted"] = revised["operating_timetable_validated"] = False
    return model._identity(revised), audit

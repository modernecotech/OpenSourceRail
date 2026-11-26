"""Aggregate Baghdad station calls at dry mapped rail junctions."""

from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
from shapely.geometry import LineString

from . import central_access, holistic_network
from . import network_station_sites as sites
from .network_trunks import CENTRAL_ANCHORS

ACCESS_M = 1300


def _walking(graph, water, max_m):
    # Reuse the pinned adapter's dry connector screen; walk length and route
    # water screening are specific to this comparison.
    snap, _ = sites._street_paths(graph, water)
    raw, matrix, _, _, _ = graph

    @lru_cache(maxsize=4096)
    def path(first, second):
        source, target = snap(first), snap(second)
        if source is None or target is None:
            return None
        start, a = source
        end, b = target
        if first == second:
            return 0., [list(first)]
        limit = max_m - a - b
        if limit < 0:
            return None
        distance, previous = dijkstra(matrix, directed=True, indices=start, limit=limit,
                                      return_predecessors=True)
        if not np.isfinite(distance[end]):
            return None
        nodes = [end]
        while nodes[-1] != start:
            nodes.append(int(previous[nodes[-1]]))
        points = [[float(raw["lon"][node]), float(raw["lat"][node])] for node in reversed(nodes)]
        geometry = holistic_network._concatenate([list(first)], points, [list(second)])
        if len(water.query(LineString(geometry), predicate="intersects")):
            return None
        return float(distance[end] + a + b), geometry

    def both(first, second, bound):
        outward, inward = path(tuple(first), tuple(second)), path(tuple(second), tuple(first))
        if outward is not None and inward is not None and max(outward[0], inward[0]) <= bound + 1e-6:
            return [outward, inward]
        return None

    return both


def _coverage(stations, graph, population):
    """Count 1.3 km population cells by retained walking-graph catchment."""
    if population is None:
        return lambda originals, new: None, lambda originals, new: None
    _, matrix, active, street_tree, _ = graph
    people_tree = cKDTree(population.xy)
    members = Counter()

    @lru_cache(maxsize=None)
    def pixels(position):
        xy = central_access._points([position])[0]
        nearby = np.asarray(people_tree.query_ball_point(xy, ACCESS_M * 1.03), dtype=int)
        nearby = nearby[population.offsets_m[nearby] <= central_access.SNAP_M]
        street_offset, index = street_tree.query(xy)
        if street_offset > central_access.SNAP_M or not len(nearby):
            return np.array([], dtype=int)
        distances = dijkstra(matrix, directed=True, indices=int(active[index]), limit=ACCESS_M - street_offset)
        return nearby[distances[population.nodes[nearby]] + street_offset + population.offsets_m[nearby] <= ACCESS_M]

    def delta(originals, new):
        counts = Counter()
        for position in originals:
            counts.subtract(pixels(tuple(position)))
        counts.update(pixels(tuple(new)))
        return counts

    for row in stations.values():
        members.update(pixels(tuple(row["coordinates"])))

    def loss(originals, new):
        lost = [pixel for pixel, count in delta(originals, new).items()
                if members[pixel] > 0 and members[pixel] + count <= 0]
        return float(population.counts[lost].sum()) if lost else 0.

    def apply(originals, new):
        members.update(delta(originals, new))

    return loss, apply


def _junction_trials(lines, stations, tracks, relocation_m):
    for a, b in combinations(sorted(lines), 2):
        first, second = lines[a], lines[b]
        for point, (a_km, b_km) in holistic_network._crossings(tracks[a], tracks[b]).items():
            choices = []
            for code, line, chainage in ((a, first, a_km), (b, second, b_km)):
                nearby = [(sites._separation(line, km, chainage), stop)
                          for stop, km in line["station_chainage_km"].items()]
                distance, stop = min(nearby)
                if distance > relocation_m + 1e-6 or sites._metres(stations[stop]["coordinates"], point) > relocation_m:
                    break
                choices.append((distance, stop, code, chainage))
            if len(choices) == 2 and choices[0][1] != choices[1][1]:
                yield sum(row[0] for row in choices), point, choices

    for distance, first, second in sites._nearby(stations, sites.EXACT_SITE_M):
        location = tuple(stations[first]["coordinates"])
        choices = []
        for stop in (first, second):
            code = min(stations[stop]["lines"])
            km = lines[code]["station_chainage_km"][stop]
            choices.append((0., stop, code, km))
        if all(sites._metres(location, tracks[code].at(km)) <= sites.EXACT_SITE_M
               for _, _, code, km in choices):
            yield distance, location, choices


def consolidate(network, graph, context, *, protected_stations=(), population=None,
                replacement_m=650, relocation_m=500, link_m=650):
    """Return a separate station revision with unchanged rail centrelines."""
    if not all(0 < limit <= ACCESS_M for limit in (replacement_m, relocation_m, link_m)):
        raise ValueError("Station walk and relocation trial bounds must be within 1300 m")
    revised = deepcopy(network)
    stations, lines = revised["stations"], revised["lines"]
    tracks = {code: holistic_network.Track(row["geometry"]) for code, row in lines.items()}
    links_old = {tuple(sorted(row["station_ids"])): row for row in revised.get("station_site_links", [])}
    anchors = (set(protected_stations) | set(CENTRAL_ANCHORS) | sites._endpoints(lines)
               | set(lines.get("C1", {}).get("station_ids", [])) | {stop for pair in links_old for stop in pair})
    water = sites._water_tree(context)
    walks = _walking(graph, water, max(replacement_m, link_m))
    loss, apply = _coverage(stations, graph, population)
    keepers = set()
    actions, held = [], []

    def priority(stop):
        row = stations[stop]
        return stop not in anchors, -len(row["lines"]), row["basis"] in sites.PROVISIONAL_BASES, stop

    def assess(keep, retire, location, kind):
        originals = [stations[stop]["coordinates"] for stop in (keep, retire)]
        checked = [walks(source, location, replacement_m) for source in originals]
        if any(check is None for check in checked):
            held.append({"station_ids": [keep, retire], "reason": "No dry bidirectional replacement walk found",
                         "kind": kind})
            return None
        lost = loss(originals, location)
        if lost is not None and lost > 1e-6:
            held.append({"station_ids": [keep, retire], "reason": "Additional modeled 1300 m coverage",
                         "kind": kind, "additional_residents": round(lost, 3)})
            return None
        apply(originals, location)
        return {"kept_station_id": keep, "retired_station_id": retire, "retired_station": stations[retire],
                "replacement_walks_m": [round(row[0], 2) for row in checked[1]],
                "replacement_walk_geometry": [row[1] for row in checked[1]],
                "loss_of_1300m_coverage_residents": lost,
                "source_access": {stop: {"walks_m": [round(row[0], 2) for row in check],
                                        "geometry": [row[1] for row in check]}
                                  for stop, check in zip((keep, retire), checked, strict=True)}}

    for _, point, trials in sorted(_junction_trials(lines, stations, tracks, relocation_m)):
        if any(stop not in stations for _, stop, _, _ in trials):
            continue
        keep, retire = sorted((row[1] for row in trials), key=priority)
        if retire in anchors or retire in keepers or set(stations[keep]["lines"]) & set(stations[retire]["lines"]):
            continue
        chainages = {code: lines[code]["station_chainage_km"][stop]
                     for stop in (keep, retire) for code in stations[stop]["lines"]}
        fixed = {stop for stop in (keep, retire)
                 if stop in anchors or stop in keepers or len(stations[stop]["lines"]) > 1}
        if any(sites._metres(stations[stop]["coordinates"], point) > sites.EXACT_SITE_M for stop in fixed):
            continue
        location = stations[keep]["coordinates"] if keep in fixed else list(point)
        for distance, stop, code, km in trials:
            if stop in fixed or distance <= 1e-6:
                continue
            if (distance > relocation_m or any(
                    sites._separation(lines[code], km, other_km) < sites.MIN_CALL_SPACING_M - 1e-6
                    for other, other_km in lines[code]["station_chainage_km"].items() if other != stop)):
                break
            chainages[code] = km
        else:
            if any(sites._metres(location, tracks[code].at(km)) > holistic_network.SOURCE_STOP_SNAP_M
                   for code, km in chainages.items()):
                continue
            kind = "Shared station at mapped rail alignment crossing"
            access = assess(keep, retire, location, kind)
            if access is None:
                continue
            actions.append(sites._merge(stations, lines, tracks, keep, retire, location, chainages, kind) | access)
            if keep not in anchors and stations[keep]["basis"] in sites.PROVISIONAL_BASES:
                stations[keep]["name"] = "–".join(sorted(chainages)) + " interchange"
            keepers.add(keep)

    neighbors = defaultdict(list)
    for distance, first, second in sites._nearby(stations, replacement_m):
        neighbors[first].append((distance, second))
        neighbors[second].append((distance, first))
    for keep in sorted(neighbors, key=priority):
        if keep not in stations:
            continue
        for _, retire in sorted(neighbors[keep]):
            if retire not in stations or retire in anchors or retire in keepers:
                continue
            shared = set(stations[keep]["lines"]) & set(stations[retire]["lines"])
            if not shared or len(stations[retire]["lines"]) != 1:
                continue
            code, = shared
            line = lines[code]
            ids = line["station_ids"]
            a, b = (line["station_chainage_km"][stop] for stop in (keep, retire))
            spacing = abs(ids.index(keep) - ids.index(retire))
            if len(ids) <= 2 or (spacing != 1 and (not line["loop"] or spacing != len(ids) - 1)):
                continue
            if sites._separation(line, a, b) > replacement_m + 1e-6:
                continue
            access = assess(keep, retire, stations[keep]["coordinates"], "Adjacent same-line calls")
            if access is None:
                continue
            ids.remove(retire)
            del line["station_chainage_km"][retire], stations[retire]
            actions.append(access | {"kind": "retire_adjacent_call", "line_id": code,
                                     "source_station_ids": [keep, retire],
                                     "retained_chainage_km": a, "retired_chainage_km": b})
            keepers.add(keep)

    proposals = []
    for distance, first, second in sites._nearby(stations, link_m):
        if set(stations[first]["lines"]) & set(stations[second]["lines"]):
            continue
        access = walks(stations[first]["coordinates"], stations[second]["coordinates"], link_m)
        if access is not None and min(row[0] for row in access) > 0:
            proposals.append(((first, second) not in links_old, max(row[0] for row in access),
                              first, second, distance, access))
    linked, links = set(), []
    for _, _, first, second, distance, access in sorted(proposals):
        if {first, second} & linked:
            continue
        prior = links_old.get((first, second), {})
        key = sha256(central_access.encode([first, second])).hexdigest()[:12]
        links.append({"id": prior.get("id", f"W-{key}"), "station_ids": [first, second],
                      "walks_m": [round(row[0], 2) for row in access],
                      "geometry": [row[1] for row in access], "straight_m": round(distance, 2),
                      "status": "separate complexes linked by public street",
                      "basis": "Step-excluded mapped paths with provisional dry station-to-street connectors"})
        linked.update((first, second))

    previous = {row["id"]: row for row in revised["transfers"]}
    revised["transfers"] = [
        previous.get(stop, {"id": stop, "station_ids": [stop], "walking_m": None,
                            "basis": row.get("site_kind", row["basis"])})
        | {"name": row["name"], "lines": sorted(row["lines"])}
        for stop, row in sorted(stations.items()) if len(row["lines"]) > 1
    ]
    revised["station_site_links"] = links
    revised["topology"] = holistic_network.validate(revised)
    source = Path(__file__).resolve()
    revised.setdefault("source_sha256", {})[source.relative_to(central_access.ROOT).as_posix()] = (
        central_access.digest(source))
    audit = {"source_candidate_id": network.get("candidate_id"), "station_sites_before": len(network["stations"]),
             "station_sites_after": len(stations), "actions": actions, "held": held, "links": links,
             "bounds": {"replacement_m": replacement_m, "relocation_m": relocation_m, "link_m": link_m,
                        "population_walk_m": ACCESS_M, "population_screen_applied": population is not None},
             "access_status": "Mapped walking and water screen. Verify frontage, crossings, vertical circulation, "
                              "platform structure and step-free access by survey."}
    return holistic_network._identity(revised), audit

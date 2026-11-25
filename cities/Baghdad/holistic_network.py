"""Build one connected Baghdad passenger network from retained GIS alignments."""

from collections import defaultdict, deque
from copy import deepcopy
from hashlib import sha256
from heapq import heappop, heappush
from itertools import combinations, pairwise
from math import cos, isfinite, radians
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from engineering.ferrite_maglev.pilot_corridor import walking_graph

from . import central_access
from .central_access import CITY, INPUTS, MAPPING, ROOT, digest, encode, read

CENTRAL = CITY / "central-access.json"
AIRPORT = CITY / "engineering/simulation/site-study.geojson"
AIRPORT_RECORD = AIRPORT.with_suffix(".json")
STREETS = MAPPING / "walking-streets.geojson.gz"
TRANSFER_SNAP_M = 100
SOURCE_STOP_SNAP_M = 25
INTERCHANGE_SPACING_M = 350
EXACT_CROSSING_M = 0.25
MAX_TERMINAL_LINK_KM = 8
ROAD_JOIN_MAX_M = 400
MAJOR_ROADS = {"motorway": 1.0, "trunk": 1.0, "primary": 1.0,
               "secondary": 1.10, "tertiary": 1.15}
LOCAL_METRES = np.array([111_320 * cos(radians(33.3)), 111_320])
LINE_NAMES = {
    "M01": "Mahmoudiya–Bob al-Sham",
    "M02": "Al-Madain–Dhat al-Salasil",
    "M03": "Al-Thawwar–Al-Shaoura",
    "M04": "Eastern suburban corridor",
    "M05": "Al-Amiriya–East Baghdad",
    "M06": "Al-Yusufiyah–Diyala",
    "M07": "Al-Anwar–Ishan Abu Khalifah",
    "M08": "Al-Madain outer corridor",
    "M09": "Baghdad orbital",
    "M10": "Sadr east–west",
    "M11": "Sadr north–south",
    "M12": "Karkh north–south",
    "M13": "Southwest cross-city",
    "M14": "Northern cross-city",
    "C1": "Airport–Zayouna",
    "C2": "Al-Mustansiriya–University",
}


class Track:
    """Piecewise linear horizontal alignment on the local distance grid."""

    def __init__(self, coordinates):
        self.coordinates = np.asarray(coordinates, dtype=float)
        self.points = self.coordinates * LOCAL_METRES
        self.delta = np.diff(self.points, axis=0)
        self.lengths = np.linalg.norm(self.delta, axis=1)
        if not len(self.lengths) or np.any(self.lengths <= 0) or not np.isfinite(self.lengths).all():
            raise ValueError("A line requires a continuous sequence of nonzero segments")
        self.chainage = np.r_[0.0, np.cumsum(self.lengths)]
        self.km = float(self.chainage[-1] / 1000)
        self.segment_centres = (self.points[:-1] + self.points[1:]) / 2
        self.segment_tree = cKDTree(self.segment_centres)

    def locate(self, coordinates):
        point = np.asarray(coordinates) * LOCAL_METRES
        offsets = point - self.points[:-1]
        fraction = np.clip((offsets * self.delta).sum(axis=1) / self.lengths**2, 0, 1)
        projections = self.points[:-1] + fraction[:, None] * self.delta
        distance = np.linalg.norm(point - projections, axis=1)
        i = int(distance.argmin())
        metres = self.chainage[i] + fraction[i] * self.lengths[i]
        return float(metres) / 1000, float(distance[i]), i

    def at(self, km):
        if not 0 <= km <= self.km:
            raise ValueError("Chainage is outside the line")
        metres = km * 1000
        i = min(int(np.searchsorted(self.chainage, metres, side="right")) - 1, len(self.delta) - 1)
        point = self.points[i] + (metres - self.chainage[i]) / self.lengths[i] * self.delta[i]
        return (point / LOCAL_METRES).tolist()

    def between(self, start, end):
        if not 0 <= start < end <= self.km:
            raise ValueError("Invalid alignment interval")
        middle = self.coordinates[(self.chainage > start * 1000 + 1e-5)
                                  & (self.chainage < end * 1000 - 1e-5)].tolist()
        return [self.at(start), *middle, self.at(end)]


def _concatenate(*paths):
    points = []
    for path in paths:
        for coordinate in path:
            point = list(coordinate)
            if not points or np.linalg.norm((np.asarray(points[-1]) - point) * LOCAL_METRES) > 1e-5:
                points.append(point)
    return points


def _road_connection(start, end, streets):
    """Find a provisional elevated corridor above connected major surface roads."""
    lower = np.minimum(start, end) - 0.06
    upper = np.maximum(start, end) + 0.06
    edges = defaultdict(dict)
    for feature in streets["features"]:
        tags = feature["properties"]
        kind = tags.get("highway", "").removesuffix("_link")
        if kind not in MAJOR_ROADS or tags.get("tunnel") not in (None, "no"):
            continue
        for first, second in pairwise(map(tuple, feature["geometry"]["coordinates"])):
            if (first == second or not all(lower[axis] <= point[axis] <= upper[axis]
                                           for point in (first, second) for axis in (0, 1))):
                continue
            metres = np.linalg.norm((np.asarray(first) - second) * LOCAL_METRES)
            weight = float(metres * MAJOR_ROADS[kind])
            edges[first][second] = edges[second][first] = min(weight, edges[first].get(second, weight))
    nodes = sorted(edges)
    if not nodes:
        raise ValueError("No major surface-road links for Al-Qadisiya–Mansour")
    tree = cKDTree(np.asarray(nodes) * LOCAL_METRES)
    distance, indexes = tree.query(np.asarray([start, end]) * LOCAL_METRES, k=min(12, len(nodes)))
    exit_cost = {nodes[i]: metres * 3 for metres, i in zip(distance[1], indexes[1], strict=True)
                 if metres <= ROAD_JOIN_MAX_M}
    previous = {}
    cost = {}
    queue = []
    for metres, i in zip(distance[0], indexes[0], strict=True):
        if metres <= ROAD_JOIN_MAX_M:
            node = nodes[i]
            cost[node] = float(metres * 3)
            previous[node] = None
            heappush(queue, (cost[node], node))
    best_cost, best_node = np.inf, None
    while queue:
        current, here = heappop(queue)
        if current > best_cost:
            break
        if current != cost[here]:
            continue
        if here in exit_cost and current + exit_cost[here] < best_cost:
            best_cost, best_node = current + exit_cost[here], here
        for there, segment_cost in sorted(edges[here].items()):
            trial = current + segment_cost
            if trial < cost.get(there, np.inf):
                cost[there], previous[there] = trial, here
                heappush(queue, (trial, there))
    if best_node is None:
        raise ValueError("No connected major surface-road path within terminal offset bounds")
    road = []
    while best_node is not None:
        road.append(best_node)
        best_node = previous[best_node]
    road.reverse()
    return _concatenate([start], road, [end])


def _physical_line(geometry, stop_ids, stations, source_sections, basis, loop=False):
    track = Track(geometry)
    offsets = {stop: track.locate(stations[stop]["coordinates"]) for stop in stop_ids}
    if any(lateral > SOURCE_STOP_SNAP_M for _, lateral, _ in offsets.values()):
        raise ValueError(f"Registered station outside its route: {source_sections}")
    start = offsets[stop_ids[0]][0]
    if loop:
        if not np.allclose(track.coordinates[0], track.coordinates[-1], rtol=0, atol=1e-8):
            raise ValueError("The orbital line has a gap")
        if 0 < start < track.km:
            geometry = _concatenate(track.between(start, track.km), track.between(0, start))
    else:
        end = offsets[stop_ids[-1]][0]
        if end < start:
            geometry = list(reversed(geometry))
            start, end = track.km - start, track.km - end
            track = Track(geometry)
        geometry = track.between(start, end)
    track = Track(geometry)
    chainage = {stop: track.locate(stations[stop]["coordinates"])[0] for stop in stop_ids}
    chainage[stop_ids[0]] = 0.
    if not loop:
        chainage[stop_ids[-1]] = track.km
    ids = sorted(stop_ids, key=lambda stop: (chainage[stop], stop))
    if ids != stop_ids:
        raise ValueError(f"Station order differs from the source timetable on {source_sections}")
    return {"geometry": geometry, "station_ids": ids, "station_chainage_km": chainage,
            "one_way_km": track.km, "source_sections": source_sections, "basis": basis, "loop": loop}


def _cross(left, right):
    return left[:, 0] * right[:, 1] - left[:, 1] * right[:, 0]


def _crossings(first, second):
    other_radii = second.lengths / 2
    possible = second.segment_tree.query_ball_point(first.segment_centres,
                                                     first.lengths / 2 + other_radii.max())
    result = {}
    for i, indexes in enumerate(possible):
        if not len(indexes):
            continue
        j = np.asarray(indexes)
        v = first.delta[i:i+1]
        w = second.delta[j]
        offset = second.points[j] - first.points[i]
        denominator = _cross(v, w)
        with np.errstate(divide="ignore", invalid="ignore"):
            t = _cross(offset, w) / denominator
            u = _cross(offset, v) / denominator
        # Very shallow crossings often represent extended parallel approaches.
        valid = ((t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)
                 & (np.abs(denominator) >= 0.15 * first.lengths[i] * second.lengths[j]))
        for k in np.flatnonzero(valid):
            point = (first.points[i] + t[k] * v[0]) / LOCAL_METRES
            metres_a = first.chainage[i] + t[k] * first.lengths[i]
            metres_b = second.chainage[j[k]] + u[k] * second.lengths[j[k]]
            key = tuple(np.round(point, 9).tolist())
            result[key] = (float(metres_a / 1000), float(metres_b / 1000))
    return result


def _terminal_margin(line, km):
    others = np.abs(np.fromiter(line["station_chainage_km"].values(), dtype=float) - km)
    if line["loop"]:
        others = np.minimum(others, line["one_way_km"] - others)
    return float(others.min() * 1000)


def _add(line, station_id, chainage):
    line["station_chainage_km"][station_id] = chainage
    line["station_ids"] = sorted(line["station_chainage_km"],
                                 key=lambda stop: (line["station_chainage_km"][stop], stop))


def _place_index(context):
    places = [(row["geometry"]["coordinates"], row["properties"].get("name:en")
               or row["properties"].get("name"))
              for row in context["layers"]["places"] if row["geometry"]["type"] == "Point"]
    places = [(coordinate, name) for coordinate, name in places if name]
    return cKDTree(np.asarray([coordinate for coordinate, _ in places]) * LOCAL_METRES), places


def dry_points(points, context=None):
    """Reject proposed platform points inside mapped water polygons, including riverbanks."""
    points = np.asarray(points, dtype=float).reshape((-1, 2))
    wet = np.zeros(len(points), dtype=bool)
    context = read(INPUTS[-1]) if context is None else context
    for feature in context["layers"]["water"]:
        geometry = feature["geometry"]
        if geometry["type"] == "Polygon":
            polygons = [geometry["coordinates"]]
        elif geometry["type"] == "MultiPolygon":
            polygons = geometry["coordinates"]
        else:
            continue
        for outer, *holes in polygons:
            outer = np.asarray(outer)
            candidates = np.flatnonzero(~wet & np.all((outer.min(axis=0) <= points)
                                                       & (points <= outer.max(axis=0)), axis=1))
            for index in candidates:
                x, y = points[index]
                inside = []
                for ring in (outer, *map(np.asarray, holes)):
                    ax, ay = ring[:-1].T
                    bx, by = ring[1:].T
                    crossing = (ay > y) != (by > y)
                    intercept = ax[crossing] + (y - ay[crossing]) * (bx - ax)[crossing] / (by - ay)[crossing]
                    inside.append(bool((x < intercept).sum() % 2))
                wet[index] = inside[0] and not any(inside[1:])
    return ~wet


def _interchanges(lines, stations, context, graph):
    tracks = {line: Track(row["geometry"]) for line, row in lines.items()}
    raw, _, active, _, _ = graph
    local_streets = cKDTree(np.column_stack((raw["lon"][active], raw["lat"][active])) * LOCAL_METRES)
    place_tree, places = _place_index(context)
    candidates = []
    for first, second in combinations(sorted(lines), 2):
        for point, (a, b) in _crossings(tracks[first], tracks[second]).items():
            distance, _ = local_streets.query(np.asarray(point) * LOCAL_METRES)
            if distance <= TRANSFER_SNAP_M:
                candidates.append((float(distance), first, second, point, a, b))
    dry = dry_points([row[3] for row in candidates], context)
    for street_offset, first, second, point, a, b in sorted(row for row, keep in zip(candidates, dry, strict=True)
                                                          if keep):
        codes = (first, second)
        nearby = []
        for code, km in zip(codes, (a, b), strict=True):
            line = lines[code]
            available = sorted((float(np.linalg.norm((np.asarray(stations[stop]["coordinates"]) - point)
                                                     * LOCAL_METRES)), stop)
                               for stop in line["station_ids"])
            distance, stop = available[0]
            if distance <= SOURCE_STOP_SNAP_M:
                nearby.append(stop)
            elif _terminal_margin(line, km) >= INTERCHANGE_SPACING_M:
                nearby.append(None)
            else:
                break
        if len(nearby) != 2 or (nearby[0] is not None and nearby[0] == nearby[1]):
            continue
        if any(stop is not None and len(stations[stop]["lines"]) > 1 for stop in nearby):
            continue
        count = sum(first in row["lines"] and second in row["lines"] and row["basis"] == "GIS crossing"
                    for row in stations.values()) + 1
        code = f"X-{first}-{second}-{count:02d}"
        distance, index = place_tree.query(np.asarray(point) * LOCAL_METRES)
        name = places[index][1] if distance <= 1100 else f"{first}–{second}"
        stations[code] = {"name": f"{name} interchange", "coordinates": list(point),
                          "lines": list(codes), "basis": "GIS crossing",
                          "street_offset_m": round(street_offset, 1),
                          "source_stations": [stop for stop in nearby if stop is not None]}
        for line, km, stop in zip((lines[first], lines[second]), (a, b), nearby, strict=True):
            if stop is not None:
                # Preserve the original running position of a source platform
                # within the combined interchange envelope, especially at a terminal.
                km = line["station_chainage_km"].pop(stop)
                del stations[stop]
            _add(line, code, km)


def _registered():
    # The established review checks geometry/run identity and service scope
    # before this revision uses the old route and station control points.
    _, _, _, context = central_access.original_cases()
    _, clockface, register, original, _ = map(read, INPUTS)
    sections = {f["properties"]["route_id"]: f for f in original["features"] if f["geometry"]["type"] == "LineString"}
    stations = {row["id"]: {"name": row["label"], "coordinates": row["longitude_latitude"],
                            "lines": [], "basis": "retained metropolitan mapped control"}
                for row in register["networks"]["metropolitan"]["mapped_points"]}
    stations.update({f["properties"]["anchor_id"]: {
        "name": f["properties"].get("map_label") or f["properties"].get("name") or f["properties"]["anchor_id"],
        "coordinates": f["geometry"]["coordinates"], "lines": [], "basis": "retained metropolitan mapped control",
    } for f in original["features"] if f["geometry"]["type"] == "Point" and "anchor_id" in f["properties"]})
    downtown = read(CENTRAL)["central_study"]
    airport = read(AIRPORT)
    airport_record = read(AIRPORT_RECORD)
    if airport["alignment_id"] != airport_record["alignment_id"]:
        raise ValueError("Airport route geometry and site-study record have different alignment identities")
    recorded_stops = {row["id"]: row for row in airport_record["stops"]}
    airport_track, = [f["geometry"]["coordinates"] for f in airport["features"]
                      if f["properties"]["kind"] == "study centreline"]
    airport_stations = []
    for feature in airport["features"]:
        props = feature["properties"]
        if props["kind"] == "study station":
            if props["chainage_km"] != recorded_stops[props["id"]]["chainage_km"] or not np.allclose(
                    feature["geometry"]["coordinates"], recorded_stops[props["id"]]["longitude_latitude"],
                    rtol=0, atol=1e-8):
                raise ValueError(f"Airport stop {props['id']} differs from its site record")
            airport_stations.append((props["chainage_km"], props["id"]))
            stations[props["id"]] = {"name": props["label"], "coordinates": feature["geometry"]["coordinates"],
                                     "lines": [], "basis": "corrected Airport route mapped study point"}
    if recorded_stops.keys() != {code for _, code in airport_stations}:
        raise ValueError("Airport station register and route geometry differ")
    for code, row in downtown["stations"].items():
        stations[code] = {"name": row["name"], "coordinates": row["coordinates"], "lines": [],
                          "basis": row["basis"]}
    return clockface, sections, stations, downtown, airport, airport_track, sorted(airport_stations), context


def _base_lines(clockface, sections, stations, downtown, airport, airport_track, airport_stops):
    lines = {}
    for code, timetable in sorted(clockface["timetable"]["groups"].items()):
        sources = clockface["scope"]["group_sections"][code]
        stop_ids = list(dict.fromkeys(row[0].removesuffix("-lap") for row in timetable["patterns"][0]))
        basis = "Retained citywide corridor, clipped to the terminal stations"
        track, = [sections[section]["geometry"]["coordinates"] for section in sources if section != "B-A01"]
        if code == "M05":
            sources = ["line-5", "Al-Amiriya station tie"]
            old_track = Track(track)
            target = stations["Airport-01"]["coordinates"]
            join_km, lateral, _ = old_track.locate(target)
            if lateral > ROAD_JOIN_MAX_M:
                raise ValueError("M05 replacement terminal is too far from the retained guideway")
            stop_ids = ["Airport-01", *(stop for stop in stop_ids if stop != "airport-terminal"
                                       and old_track.locate(stations[stop]["coordinates"])[0] > join_km + .35)]
            track = _concatenate([target], old_track.between(join_km, old_track.km))
            basis = ("Retained eastern corridor with the redundant western Airport approach removed. "
                     f"{lateral:.0f} m mapped tie to the Al-Amiriya interchange is a corridor allowance.")
        lines[code] = _physical_line(track, stop_ids, stations, sources, basis, timetable["loop"])
    central = downtown["lines"]["C1"]
    terminal = stations["Airport-05"]["coordinates"]
    mansour = stations["Mansour"]["coordinates"]
    connector = _road_connection(terminal, mansour, read(STREETS))
    lines["C1"] = _physical_line(
        _concatenate(airport_track, connector, central["geometry"]),
        [*(code for _, code in airport_stops), *central["station_ids"]],
        stations, [airport["alignment_id"], "Al-Qadisiya–Mansour", "C1 retained trunk"],
        "Airport GIS geometry continues via a {:.2f} km major surface-road corridor screen into the "
        "Mansour–Zayouna trunk. Road geometry leaves elevation and land take open.".format(Track(connector).km))
    central = downtown["lines"]["C2"]
    lines["C2"] = _physical_line(central["geometry"], central["station_ids"], stations,
                                  ["C2 retained trunk"], central["corridor_basis"])
    for code, line in sorted(lines.items()):
        line["name"] = LINE_NAMES[code]
        for stop in line["station_ids"]:
            stations[stop]["lines"].append(code)
    return lines


def _identity(record):
    physical = {
        "lines": {code: {key: row[key] for key in ("geometry", "station_ids", "loop")}
                  for code, row in record["lines"].items()},
        "stations": {code: row["coordinates"] for code, row in record["stations"].items()},
    }
    record["candidate_id"] = "baghdad-network-" + sha256(encode(physical)).hexdigest()[:16]
    record.pop("evaluation_id", None)
    record["evaluation_id"] = sha256(encode(record)).hexdigest()
    return record


def validate(record):
    """Check passenger graph connectivity and the chainages represented on this map."""
    stations, lines = record["stations"], record["lines"]
    adjacent = defaultdict(set)
    memberships = defaultdict(set)
    for code, line in lines.items():
        ids = line["station_ids"]
        track = Track(line["geometry"])
        chainage = line["station_chainage_km"]
        if (len(ids) < 2 or len(set(ids)) != len(ids) or set(ids) != chainage.keys()
                or chainage[ids[0]] != 0 or abs(track.km - line["one_way_km"]) > 1e-7):
            raise ValueError(f"{code} needs a single alignment with ordered stations")
        if line["loop"] and not np.allclose(track.coordinates[0], track.coordinates[-1], rtol=0, atol=1e-8):
            raise ValueError(f"{code} has an open orbital alignment")
        if not line["loop"] and abs(chainage[ids[-1]] - track.km) > 1e-7:
            raise ValueError(f"{code} has a stray path beyond its final station")
        if any(chainage[a] >= chainage[b] for a, b in pairwise(ids)):
            raise ValueError(f"{code} has scrambled station chainages")
        for station in ids:
            memberships[station].add(code)
            distance = np.linalg.norm((np.asarray(stations[station]["coordinates"]) - track.at(chainage[station]))
                                      * LOCAL_METRES)
            if distance > SOURCE_STOP_SNAP_M:
                raise ValueError(f"{station} is not on line {code}")
        for a, b in pairwise(ids + ids[:1] if line["loop"] else ids):
            adjacent[a].add(b)
            adjacent[b].add(a)
    if memberships.keys() != stations.keys() or any(
            set(row["lines"]) != memberships[code] for code, row in stations.items()):
        raise ValueError("Station-to-line memberships disagree")
    transfers = {row["id"]: row for row in record["transfers"]}
    expected = {station for station, codes in memberships.items() if len(codes) > 1}
    if len(transfers) != len(record["transfers"]) or transfers.keys() != expected or any(
            row["station_ids"] != [code] or set(row["lines"]) != memberships[code]
            for code, row in transfers.items()):
        raise ValueError("Every interchange must be recorded as a shared station on both lines")
    walking_links = record.get("station_site_links", [])
    linked_sites, link_ids = set(), set()
    for link in walking_links:
        a, b = link["station_ids"]
        walks = link["walks_m"]
        if (a == b or {a, b} - stations.keys() or {a, b} & linked_sites or link["id"] in link_ids
                or len(walks) != 2 or not all(isfinite(distance) and distance > 0 for distance in walks)):
            raise ValueError("Walking interchange needs distinct stations and a measured route in both directions")
        locations = link.get("geometry", [])
        if (memberships[a] & memberships[b] or len(locations) != 2 or any(
                len(path) < 2 or not np.allclose(path[0], stations[start]["coordinates"], rtol=0, atol=1e-8)
                or not np.allclose(path[-1], stations[end]["coordinates"], rtol=0, atol=1e-8)
                for path, (start, end) in zip(locations, ((a, b), (b, a)), strict=True))):
            raise ValueError("Walking interchange geometry must join the two separate platforms")
        linked_sites.update((a, b))
        link_ids.add(link["id"])
        adjacent[a].add(b)
        adjacent[b].add(a)
    seen = set()
    queue = deque([min(stations)])
    while queue:
        node = queue.popleft()
        if node not in seen:
            queue.extend(adjacent[node] - seen)
            seen.add(node)
    if seen != stations.keys():
        missing = sorted({line for stop in stations.keys() - seen for line in stations[stop]["lines"]})
        raise ValueError(f"Disconnected passenger lines: {', '.join(missing)}")
    result = {"lines": len(lines), "stations": len(stations), "transfer_stations": len(record["transfers"]),
              "connected_components": 1, "route_km": round(sum(row["one_way_km"] for row in lines.values()), 2)}
    if walking_links:
        result["walking_transfer_links"] = len(walking_links)
    return result


def evaluate(graph=None):
    clockface, sections, stations, downtown, airport, path, airport_stops, context = _registered()
    lines = _base_lines(clockface, sections, stations, downtown, airport, path, airport_stops)
    stations = {code: row for code, row in stations.items() if row["lines"]}
    place_tree, places = _place_index(context)
    for code, row in stations.items():
        if not row["name"]:
            distance, index = place_tree.query(np.asarray(row["coordinates"]) * LOCAL_METRES)
            area = f"Near {places[index][1]}" if distance <= 1100 else LINE_NAMES[row["lines"][0]]
            row["name"] = f"{area} · {code}"
    graph = walking_graph() if graph is None else graph
    _interchanges(lines, stations, context, graph)
    transfers = [{"id": code, "name": row["name"], "station_ids": [code], "lines": sorted(row["lines"]),
                  "walking_m": None, "basis": row["basis"]}
                 for code, row in sorted(stations.items()) if len(row["lines"]) > 1]
    sources = (*INPUTS, CENTRAL, AIRPORT, AIRPORT_RECORD, STREETS, MAPPING / "walking-graph.npz.gz",
               MAPPING / "street-source.json", Path(central_access.__file__), Path(__file__))
    record = {"schema": "osr.baghdad.holistic-network.v1", "lines": lines, "stations": stations,
              "transfers": transfers,
              "source_sha256": {path.relative_to(ROOT).as_posix(): digest(path) for path in sources},
              "assumptions": {"street_snap_m": TRANSFER_SNAP_M, "minimum_interchange_spacing_m": INTERCHANGE_SPACING_M,
                              "road_connection_end_allowance_m": ROAD_JOIN_MAX_M,
                              "interchange_water_screen": "Retained water polygons",
                              "length_basis": "Horizontal local-grid approximation"},
              "physical_accepted": False, "operating_timetable_validated": False}
    record["topology"] = validate(record)
    return _identity(record)


def insert_stations(record, additions):
    """Apply deterministic in-line station choices produced by the coverage solver."""
    revised = deepcopy(record)
    tracks = {}
    for addition in sorted(additions, key=lambda row: (row["line_id"], row["chainage_km"], row["id"])):
        code = addition["line_id"]
        chainage = float(addition["chainage_km"])
        station = addition["id"]
        line = revised["lines"][code]
        if (station in revised["stations"] or not isfinite(chainage) or not 0 < chainage < line["one_way_km"]
                or _terminal_margin(line, chainage) < INTERCHANGE_SPACING_M - 1e-6):
            raise ValueError(f"Invalid station insertion {station} on {code}")
        if code not in tracks:
            tracks[code] = Track(line["geometry"])
        revised["stations"][station] = {"name": addition["name"], "coordinates": tracks[code].at(chainage),
                                        "lines": [code], "basis": addition["basis"]}
        _add(line, station, chainage)
    revised["topology"] = validate(revised)
    return _identity(revised)


def _through_crossing(line_id, request, tracks):
    other_id = request["line_id"]
    if other_id == line_id or other_id not in tracks:
        raise ValueError(f"{line_id} interchange refers to an unknown connecting line: {other_id}")
    point = np.asarray(request["point"], dtype=float)
    if point.shape != (2,) or not np.isfinite(point).all():
        raise ValueError(f"Invalid {line_id}–{other_id} interchange point")
    crossings = _crossings(tracks[line_id], tracks[other_id])
    matches = [(coordinates, chainages) for coordinates, chainages in crossings.items()
               if np.linalg.norm((coordinates - point) * LOCAL_METRES) <= EXACT_CROSSING_M]
    if len(matches) != 1:
        raise ValueError(f"{line_id}–{other_id} requires one exact alignment crossing at the proposed interchange")
    return matches[0]


def _through_station_spacing(line_id, station_id, chainage, lines):
    line = lines[line_id]
    if (not isfinite(chainage) or not 0 < chainage < line["one_way_km"]
            or _terminal_margin(line, chainage) < INTERCHANGE_SPACING_M - 1e-6):
        raise ValueError(f"Invalid station insertion {station_id} on {line_id}: chainage or spacing")


def _stations_at_crossing(stations, point):
    return [station_id for station_id, row in stations.items()
            if np.linalg.norm((np.asarray(row["coordinates"]) - point) * LOCAL_METRES) <= EXACT_CROSSING_M]


def _through_interchange(line_id, request, crossing, lines, stations, *, require_intermediate=True):
    other_id = request["line_id"]
    point, (chainage, other_chainage) = crossing
    nearby = _stations_at_crossing(stations, point)
    memberships = stations[nearby[0]]["lines"] if nearby else []
    if len(nearby) > 1 or (line_id in memberships and (require_intermediate or other_id in memberships)):
        raise ValueError(f"Duplicate shared station at the {line_id}–{other_id} crossing")
    station_id = nearby[0] if nearby else request.get("id") or (
        f"X-{line_id}-{other_id}-" + sha256(encode(point)).hexdigest()[:10])
    approaches = [(code, km) for code, km in ((line_id, chainage), (other_id, other_chainage))
                  if code not in memberships]
    for code, km in approaches:
        _through_station_spacing(code, station_id, km, lines)
    if not nearby:
        if station_id in stations:
            raise ValueError(f"Duplicate shared station ID: {station_id}")
        stations[station_id] = {
            "name": request.get("name") or f"{line_id}–{other_id} interchange",
            "coordinates": list(point), "lines": [], "basis": "GIS crossing on a proposed through line",
        }
    station = stations[station_id]
    for code, km in approaches:
        _add(lines[code], station_id, km)
        station["lines"].append(code)
    station["lines"].sort()
    return station_id


def _connect_through_lines(codes, tracks, lines, stations, street_tree, context):
    candidates = []
    for first, second in combinations(sorted(codes), 2):
        if set(lines[first]["station_ids"]) & set(lines[second]["station_ids"]):
            continue
        for point, chainages in _crossings(tracks[first], tracks[second]).items():
            nearby = _stations_at_crossing(stations, point)
            site = stations[nearby[0]]["coordinates"] if nearby else point
            distance, _ = street_tree.query(np.asarray(site) * LOCAL_METRES)
            if distance <= TRANSFER_SNAP_M:
                candidates.append((float(distance), first, second, point, chainages, site))
    candidates.sort()
    dry = dry_points([row[5] for row in candidates], context)
    for row, keep in zip(candidates, dry, strict=True):
        distance, first, second, point, chainages, _ = row
        if not keep or set(lines[first]["station_ids"]) & set(lines[second]["station_ids"]):
            continue
        try:
            stop = _through_interchange(first, {"line_id": second}, (point, chainages), lines, stations,
                                        require_intermediate=False)
        except ValueError:
            continue
        stations[stop].setdefault("street_offset_m", round(distance, 1))


def insert_through_lines(record, additions, *, graph=None, context=None, connect_through_lines=False):
    """Add open through routes with registered endpoints and exact intermediate interchanges.

    Additions use `id`, `name`, `geometry` and two ordered `terminal_ids`.
    Each required interchange gives the existing `line_id` and crossing `point`.
    Each ordinary stop gives an `id`, `name`, and exactly one of `chainage_km`
    or `chainage_m`. Route order permits interchange requests on earlier lines.
    A `terminal_link_only` connector up to 8 km may use distinct onward routes
    at its terminals as its sole required links.
    Set `connect_through_lines` after selection to add eligible crossings among
    the proposed through lines with priority by mapped street offset.
    """
    validate(record)
    revised = deepcopy(record)
    lines, stations = revised["lines"], revised["stations"]
    summaries = revised.setdefault("through_lines", {})
    tracks = {code: Track(row["geometry"]) for code, row in lines.items()}
    context = read(INPUTS[-1]) if context is None else context
    graph = walking_graph() if graph is None else graph
    street_tree = graph[3]
    for addition in additions:
        code = addition["id"]
        terminals = list(addition["terminal_ids"])
        if code in lines:
            raise ValueError(f"Duplicate line ID: {code}")
        if (len(terminals) != 2 or terminals[0] == terminals[1]
                or not all(stop in stations for stop in terminals)):
            raise ValueError(f"{code} requires two distinct existing terminal stations")
        route_sets = [set(stations[stop]["lines"]) for stop in terminals]
        if len(set.union(*route_sets)) < 2:
            raise ValueError(f"{code} requires terminal connections to distinct existing routes")
        geometry = np.array(addition["geometry"], dtype=float)
        if geometry.ndim != 2 or geometry.shape[1] != 2 or len(geometry) < 2 or not np.isfinite(geometry).all():
            raise ValueError(f"{code} requires a continuous longitude and latitude alignment")
        terminal_points = np.asarray([stations[stop]["coordinates"] for stop in terminals])
        if np.linalg.norm((terminal_points[0] - terminal_points[1]) * LOCAL_METRES) <= EXACT_CROSSING_M:
            raise ValueError(f"{code} requires two physically distinct terminal stations")
        if np.any(np.linalg.norm((geometry[[0, -1]] - terminal_points) * LOCAL_METRES,
                                 axis=1) > EXACT_CROSSING_M):
            raise ValueError(f"{code} must start and end at its terminal stations with no stray path")
        geometry[[0, -1]] = terminal_points
        tracks[code] = track = Track(geometry)
        required = addition.get("required_interchanges", [])
        terminal_link_only = addition.get("terminal_link_only") is True
        if terminal_link_only and (track.km > MAX_TERMINAL_LINK_KM or set.intersection(*route_sets) or required):
            raise ValueError(f"{code} terminal-only connector requires at most {MAX_TERMINAL_LINK_KM} km, "
                             "disjoint terminal routes and no required intermediate interchange")
        if not terminal_link_only and not required:
            raise ValueError(f"{code} requires an intermediate interchange")
        lines[code] = {
            "name": addition["name"], "geometry": geometry.tolist(), "loop": False,
            "source_sections": addition.get("source_sections", []),
            "basis": addition.get("basis", "Proposed cross-city planning alignment"),
            "station_ids": terminals.copy(), "station_chainage_km": dict(zip(terminals, (0., track.km), strict=True)),
            "one_way_km": track.km,
        }
        for stop in terminals:
            stations[stop]["lines"] = sorted([*stations[stop]["lines"], code])
        interchanges = [_through_interchange(code, row, _through_crossing(code, row, tracks), lines, stations)
                        for row in required]
        ordinary = []
        for row in addition.get("stops", []):
            stop = row["id"]
            fields = {"chainage_km", "chainage_m"} & row.keys()
            if stop in stations or len(fields) != 1:
                raise ValueError(f"Invalid station insertion {stop} on {code}: duplicate ID or missing chainage unit")
            unit = fields.pop()
            try:
                chainage = float(row[unit]) / (1000 if unit == "chainage_m" else 1)
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid station insertion {stop} on {code}: chainage") from error
            _through_station_spacing(code, stop, chainage, lines)
            stations[stop] = {
                "name": row["name"], "coordinates": track.at(chainage), "lines": [code],
                "basis": row.get("basis", "Proposed through-line station"),
            }
            _add(lines[code], stop, chainage)
            ordinary.append(stop)
        sites = [*terminals, *interchanges, *ordinary]
        for stop, dry in zip(sites, dry_points([stations[stop]["coordinates"] for stop in sites], context),
                             strict=True):
            if not dry:
                raise ValueError(f"{stop} on {code} is inside mapped water")
        for stop in [*interchanges, *ordinary]:
            distance, _ = street_tree.query(np.asarray(stations[stop]["coordinates"]) * LOCAL_METRES)
            if distance > TRANSFER_SNAP_M:
                raise ValueError(f"{stop} on {code} is outside the mapped street access limit")
            stations[stop].setdefault("street_offset_m", round(float(distance), 1))
        summaries[code] = {"terminal_ids": terminals, "required_intermediate_transfer_ids": interchanges,
                           "terminal_link_only": terminal_link_only}

    if connect_through_lines:
        _connect_through_lines(summaries, tracks, lines, stations, street_tree, context)
    for code, summary in summaries.items():
        transfer_ids = [stop for stop in lines[code]["station_ids"] if len(stations[stop]["lines"]) > 1]
        summary["transfer_ids"] = transfer_ids
        summary["transfer_count"] = len(transfer_ids)
    prior_transfers = {row["id"]: row for row in revised["transfers"]}
    revised["transfers"] = [
        prior_transfers.get(stop, {"id": stop, "name": row["name"], "station_ids": [stop],
                                   "walking_m": None, "basis": row["basis"]}) | {"lines": sorted(row["lines"])}
        for stop, row in sorted(stations.items()) if len(row["lines"]) > 1
    ]
    revised["topology"] = validate(revised)
    revised["physical_accepted"] = False
    revised["operating_timetable_validated"] = False
    return _identity(revised)


def geojson(record):
    """Public GIS export uses the identical paths and station IDs as the passenger graph."""
    features = [{"type": "Feature", "geometry": {"type": "LineString", "coordinates": line["geometry"]},
                 "properties": {key: val for key, val in line.items() if key != "geometry"} | {
                     "kind": "line", "line_id": code}}
                for code, line in sorted(record["lines"].items())]
    features.extend({"type": "Feature", "geometry": {"type": "Point", "coordinates": station["coordinates"]},
                     "properties": {key: val for key, val in station.items() if key != "coordinates"} | {
                         "kind": "interchange" if len(station["lines"]) > 1 else "station", "station_id": code}}
                    for code, station in sorted(record["stations"].items()))
    features.extend({"type": "Feature", "geometry": {"type": "MultiLineString", "coordinates": link["geometry"]},
                     "properties": {key: val for key, val in link.items() if key != "geometry"} | {
                         "kind": "walking-interchange", "stroke": "#39254f"}}
                    for link in record.get("station_site_links", []))
    return {"type": "FeatureCollection", "candidate_id": record["candidate_id"],
            "evaluation_id": record["evaluation_id"], "features": features}

"""Assemble local city network alternatives from mapped corridors and interchanges."""

from collections import defaultdict
from copy import deepcopy
from itertools import combinations
from math import cos, radians
from pathlib import Path

from shapely.geometry import LineString

from engineering.station_rail.common import digest, identity
from . import city_alignment, network_policy

METHOD = "local-metropolitan-through-routes/1"
PRODUCER = "engineering/outline/city_metropolitan.py"
SOURCE_SHA256 = {PRODUCER: digest(Path(__file__))}
MAXIMUM_JOIN_BEND_DEG = 30.
TERMINAL_JOIN_TOLERANCE_M = .05


def _terminal_end(line, site):
    """A retained tail or a stop off its route cannot be spliced automatically."""
    for end, index in enumerate((0, -1)):
        stop = line["stops"][index]
        chainage = (0., line["route_m"])[end]
        if (stop["id"] in site["platforms"]
                and abs(stop["chainage_m"] - chainage) <= TERMINAL_JOIN_TOLERANCE_M
                and city_alignment.distance(line["coordinates"][index], [stop["lon"], stop["lat"]])
                <= TERMINAL_JOIN_TOLERANCE_M):
            return end
    return None


def _orient(line, reverse):
    points = line["coordinates"]
    stops = deepcopy(line["stops"])
    if reverse:
        points = points[::-1]
        stops.reverse()
        for stop in stops:
            stop["chainage_m"] = line["route_m"] - stop["chainage_m"]
    return points, stops


def _join(left, left_end, right, right_end, site):
    first, first_stops = _orient(left, reverse=left_end == 0)
    second, second_stops = _orient(right, reverse=right_end == 1)
    if city_alignment.distance(first[-1], second[0]) > TERMINAL_JOIN_TOLERANCE_M:
        return None
    points = [*first, *second[1:]]
    chain = city_alignment.chainages(points)
    direct = city_alignment.distance(points[0], points[-1])
    if not direct or chain[-1] / direct > network_policy.MAXIMUM_DETOUR_RATIO:
        return None
    # A tangent check over 350 m is insensitive to short GIS vertex intervals.
    joint = chain[len(first) - 1]
    a, b, c = (city_alignment._at(points, chain, position)
               for position in (joint - 350, joint, joint + 350))
    arms = city_alignment.distance(a, b), city_alignment.distance(b, c)
    chord = city_alignment.distance(a, c)
    if chord ** 2 < sum(length ** 2 for length in arms) + 2 * arms[0] * arms[1] * cos(radians(MAXIMUM_JOIN_BEND_DEG)):
        return None
    if not LineString(points).is_simple:
        return None

    stops = [*first_stops, *second_stops[1:]]
    first_stops[-1].update(chainage_m=joint, lon=first[-1][0], lat=first[-1][1],
                           dwell_s=max(first_stops[-1]["dwell_s"], second_stops[0]["dwell_s"]))
    second_length = city_alignment.chainages(second)[-1]
    for stop in second_stops[1:]:
        stop["chainage_m"] = joint + stop["chainage_m"] * (chain[-1] - joint) / second_length
    stops[0]["chainage_m"], stops[-1]["chainage_m"] = 0., chain[-1]
    if any(a["chainage_m"] >= b["chainage_m"] for a, b in zip(stops, stops[1:])):
        return None
    parent_ids = [left["line_id"], right["line_id"]]
    line_id = "through-" + identity(dict(lines=parent_ids, interchange=site["id"]))[:14]
    line = dict(line_id=line_id, shape="radial", coordinates=points, coordinate_chainages_m=chain,
                route_m=chain[-1], stops=stops, source_schedule=[], retained_capacity_targets=None,
                retained_service_and_capacity_are_current_demand=False, unserved_radial_tail_m=0.,
                geometry_reference=dict(source_line_ids=parent_ids, terminal_interchange_id=site["id"]))
    city_alignment._legs(line)
    return line, {second_stops[0]["id"]: first_stops[-1]["id"]}, joint


def _join_options(city):
    radials = {line["line_id"]: line for line in city["lines"] if line["shape"] == "radial"}
    options = []
    for site in city["interchanges"]:
        terminals = [(line_id, end) for line_id in sorted(set(site["lines"]) & radials.keys())
                     if (end := _terminal_end(radials[line_id], site)) is not None]
        for (first, a), (second, b) in combinations(terminals, 2):
            outcome = _join(radials[first], a, radials[second], b, site)
            if outcome is not None:
                joined, remap, joint = outcome
                options.append((joined, (first, a), (second, b), remap, joint))
    return sorted(options, key=lambda row: (-len(row[0]["stops"]), -row[0]["route_m"], row[0]["line_id"]))


def _interchanges(city, lines, stop_map, line_map):
    platforms = {line["line_id"]: {stop["id"] for stop in line["stops"]} for line in lines}
    result = []
    for site in city["interchanges"]:
        lines_here = sorted({line_map.get(line, line) for line in site["lines"]} & platforms.keys())
        mapped = {stop_map.get(stop, stop) for stop in site["platforms"]}
        linked = [(line, sorted(platforms[line] & mapped)) for line in lines_here]
        if len(linked) >= 2 and all(len(stops) == 1 for _, stops in linked):
            result.append({**site, "lines": lines_here, "platforms": [stops[0] for _, stops in linked]})
    return result


def _with_join(city, option):
    line, (first, first_end), (second, second_end), stop_map, joint = option
    lines = [row for row in city["lines"] if row["line_id"] not in (first, second)]
    lines.append(line)
    originals = {row["line_id"]: row for row in city["lines"]}
    spans = {first: (0., joint, first_end == 0),
             second: (joint, line["route_m"] - joint, second_end == 1)}
    sections = []
    for section in city["civil_segments"]:
        old = section["line_id"]
        if old not in spans:
            sections.append(section)
            continue
        offset, width, reverse = spans[old]
        old_length = originals[old]["route_m"]
        lo, hi = section["from_m"], section["to_m"]
        if reverse:
            lo, hi = old_length - hi, old_length - lo
        sections.append({**section, "line_id": line["line_id"], "from_m": offset + lo * width / old_length,
                         "to_m": offset + hi * width / old_length})
    return lines, sections, _interchanges(city, lines, stop_map, dict.fromkeys(spans, line["line_id"])), stop_map


def _components(city):
    by_line = {line["line_id"]: line for line in city["lines"]}
    neighbours = defaultdict(set)
    for first, second in network_policy._transfer_sites(city):
        neighbours[first].add(second)
    unseen = set(by_line)
    components = []
    while unseen:
        pending = [min(unseen)]
        connected = set()
        while pending:
            line = pending.pop()
            if line not in unseen:
                continue
            unseen.remove(line)
            connected.add(line)
            pending.extend(sorted(neighbours[line] & unseen))
        components.append(connected)
    return sorted(components, key=lambda group: (-sum(len(by_line[line]["stops"]) for line in group),
                                                 -len(group), tuple(sorted(group))))


def _proposal(city, kind, lines, sections, interchanges, stop_map=None):
    stop_map = stop_map or {}
    stops = {stop["id"] for line in lines for stop in line["stops"]}
    od = []
    for row in city["od"]:
        origin, target = (stop_map.get(row[field], row[field]) for field in ("origin", "destination"))
        if origin in stops and target in stops and origin != target:
            od.append({**row, "origin": origin, "destination": target})
    hypothesis = dict(method=METHOD, kind=kind, source_city_input_id=city["input_id"],
                      route_ids=sorted(line["line_id"] for line in lines),
                      missing_evidence=["Mapped pedestrian access and population coverage",
                                        "Named destinations and comparable journey assignments",
                                        "Surveyed infrastructure and interchange geometry"])
    child = {**city, "lines": sorted(lines, key=lambda line: line["line_id"]),
             "civil_segments": sorted(sections, key=lambda row: (row["line_id"], row["from_m"])),
             "interchanges": interchanges, "od": od,
             "source_sha256": {**city["source_sha256"], **SOURCE_SHA256},
             "alignment_hypothesis": hypothesis,
             "ancestry": dict(parent_input_id=city["input_id"], revision_operator=kind)}
    child.pop("input_id")
    child["input_id"] = identity(child)
    return dict(kind=kind, city_input=child,
                alignment_id=identity(dict(city_input_id=child["input_id"], method=METHOD)),
                selection_eligibility=dict(status="hold", access_screen="hold",
                                           missing_evidence=hypothesis["missing_evidence"]))


def search(city, applicability, *, allow_line_changes=True):
    """Start from empty and assemble local through and orbital route combinations.

    A joined alignment uses retained physical route segments. A connected
    subnetwork uses only declared interchanges on suitably co-located platforms.
    The current city outline data cannot establish their population access.
    """
    variants = []
    components = _components(city)
    options = _join_options(city) if allow_line_changes else []
    if options:
        lines, sections, transfers, remap = _with_join(city, options[0])
        variants.append(_proposal(city, "joined-through-services-research", lines, sections, transfers, remap))
    if len(components) > 1 and allow_line_changes:
        ids = components[0]
        lines = [row for row in city["lines"] if row["line_id"] in ids]
        sections = [row for row in city["civil_segments"] if row["line_id"] in ids]
        transfers = _interchanges(city, lines, {}, {})
        variants.append(_proposal(city, "connected-network-from-empty-research", lines, sections, transfers))
    return variants, dict(
        method=METHOD, assembly="from-empty-retained-corridor-library",
        linked_components=[sorted(group) for group in components],
        nested_ring_ids=applicability["ring_ids"], applicable_river=applicability["river_name"],
        potential_through_joins=len(options), generated_alternatives=[row["kind"] for row in variants],
        metropolitan_coverage_status="local-walking-population-and-destination-evidence-required",
        line_changes_screened=allow_line_changes)

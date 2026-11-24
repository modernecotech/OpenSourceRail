"""Source-bound horizontal alignment screen for the six-stop Baghdad Airport corridor."""

import gzip
from hashlib import sha256
from itertools import accumulate, pairwise
import json
from math import isfinite
from pathlib import Path

from cities.Baghdad.engineering.simulation import corridor

ROOT = corridor.CITY.parents[1]
CONTEXT = ROOT / "cities/catalogue/west-asia/Iraq/Baghdad/map-context.json.gz"
CONTEXT_SHA256 = "21ab8f69f933ee84e32158f3b5de54d29d5fea8518183457856d2745e6c78168"
STOP_IDS = tuple(f"Airport-{i:02d}" for i in range(6))
SCHEMA = "osr-baghdad-airport-horizontal-alignment/1"
SURVEY_SCHEMA = "osr-baghdad-airport-survey-centreline/1"


def identity(data):
    return sha256(json.dumps(data, sort_keys=True, allow_nan=False).encode()).hexdigest()


def coordinate(point):
    if (not isinstance(point, list) or len(point) != 2
            or any(type(value) not in (int, float) for value in point)
            or not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90)
            or not all(map(isfinite, point))):
        raise ValueError("Expected finite WGS84 longitude/latitude")
    return list(map(float, point))


def length_km(coordinates):
    return sum(corridor.distance_km(a, b) for a, b in pairwise(coordinates))


def within_coverage(point, bounds):
    west, south, east, north = bounds
    return west <= point[0] <= east and south <= point[1] <= north


def survey_input(path, parent_id, bounds):
    raw = Path(path).read_bytes()
    supplied = json.loads(raw)
    if (not isinstance(supplied, dict) or supplied.get("schema") != SURVEY_SCHEMA
            or supplied.get("parent_candidate_id") != parent_id
            or supplied.get("crs") != "EPSG:4326"
            or any(not isinstance(supplied.get(k), str) or not supplied[k].strip()
                   for k in ("document", "revision", "verification_reference"))):
        raise ValueError("Provide the matched parent, WGS84, document, revision and verification reference")
    geometry = supplied.get("geometry")
    if (not isinstance(geometry, dict) or geometry.get("type") != "LineString"
            or not isinstance(geometry.get("coordinates"), list)
            or not isinstance(supplied.get("stops"), list)
            or supplied.get("geometry_sha256") != identity({"geometry": geometry, "stops": supplied.get("stops")})):
        raise ValueError("Missing centreline, ordered stops or matching geometry digest")
    points = [coordinate(p) for p in geometry["coordinates"]]
    if len(points) < len(STOP_IDS) or len(set(map(tuple, points))) != len(points):
        raise ValueError("The centreline needs distinct vertices and a vertex for each stop")
    rows = supplied["stops"]
    if (any(not isinstance(s, dict) for s in rows) or [s.get("id") for s in rows] != list(STOP_IDS)
            or any(type(s.get("vertex")) is not int for s in rows)):
        raise ValueError("Use the six Airport stop IDs in corridor order with integer vertex indices")
    vertices = [s["vertex"] for s in rows]
    if vertices != sorted(set(vertices)) or vertices[0] != 0 or vertices[-1] != len(points) - 1:
        raise ValueError("Stop vertices must increase strictly across the entire centreline")
    if any(coordinate(s.get("coordinates")) != points[s["vertex"]] for s in rows):
        raise ValueError("Each stop coordinate must match its declared centreline vertex")
    coverage_decision = supplied.get("coverage_decision")
    outside_coverage = sum(not within_coverage(point, bounds) for point in points)
    if (outside_coverage or coverage_decision is not None) and (
            not isinstance(coverage_decision, dict)
            or coverage_decision.get("geometry_sha256") != supplied["geometry_sha256"]
            or any(not isinstance(coverage_decision.get(k), str) or not coverage_decision[k].strip()
                   for k in ("document", "review_reference", "reason"))):
        raise ValueError("A trace beyond the retained Baghdad map needs a geometry-bound coverage decision")
    return points, vertices, {
        "document": supplied["document"],
        "revision": supplied["revision"],
        "verification_reference": supplied["verification_reference"],
        "file_sha256": sha256(raw).hexdigest(),
        "geometry_sha256": supplied["geometry_sha256"],
        "vertices_outside_retained_coverage": outside_coverage,
        "coverage_decision": coverage_decision,
        "scope": "Verification reference supplied by the submitter. Independent review remains open.",
    }


def map_context(hashes):
    data = CONTEXT.read_bytes()
    fingerprint = sha256(data).hexdigest()
    if fingerprint != CONTEXT_SHA256:
        raise ValueError("Reviewed Airport Highway sections refer to another background revision")
    hashes[str(CONTEXT.relative_to(ROOT))] = fingerprint
    return json.loads(gzip.decompress(data))


def mapped_sections(places, roads):
    def highway(feature, part, start, end):
        road = roads[feature]
        props = road["properties"]
        if (props.get("name:en") != "Airport Highway" or props.get("ref") != "14"
                or props.get("kind_detail") != "motorway" or road["geometry"]["type"] != "MultiLineString"):
            raise ValueError("Reviewed mapped road feature differs from Airport Highway")
        return [coordinate(p) for p in road["geometry"]["coordinates"][part][start:end]]

    a, b, c, d, e = places
    west = highway(50, 0, 26, 28)
    middle = highway(121, 0, 0, 7)
    east = highway(107, 0, 0, 4)
    if middle[-1] != east[0]:
        raise ValueError("Reviewed Airport Highway geometry has a disconnected tile boundary")
    return [
        ("review_connector", [a, west[0]], "Terminal to Airport Highway. Airport land and access remain open."),
        ("mapped_road_reference", west, "Airport Highway reference 14, west section."),
        ("review_connector", [west[-1], b], "Airport Highway to Al Amiriya area."),
        ("review_connector", [b, middle[0]], "Al Amiriya area to Airport Highway."),
        ("mapped_road_reference", middle + east[1:], "Airport Highway reference 14, middle section."),
        ("review_connector", [east[-1], c], "Airport Highway to Hay Al Aamil area."),
        ("review_connector", [c, d], "Hay Al Aamil to Al Bayaa. Route and crossing envelope remain open."),
        ("review_connector", [d, e], "Al Bayaa to Al Qadisiya. Um Al Tubol remains unlocated."),
    ]


def stop_offset(anchor, point):
    if anchor is None or point is None:
        return None
    east = corridor.distance_km(anchor, [point[0], anchor[1]])
    north = corridor.distance_km(anchor, [anchor[0], point[1]])
    return {
        "east_km": east if point[0] >= anchor[0] else -east,
        "north_km": north if point[1] >= anchor[1] else -north,
        "distance_km": corridor.distance_km(anchor, point),
    }


def physical_record(record):
    segments = record["segments"]
    trace = segments[0]["coordinates"] + [point for segment in segments[1:] for point in segment["coordinates"][1:]]
    return {
        "schema": record["schema"], "parent_candidate_id": record["parent_candidate_id"],
        "grade_profile": record["grade_profile"], "horizontal_trace": trace,
        "stops": [(s["id"], s["longitude_latitude"], s["chainage_km"]) for s in record["stops"]],
    }


def validate(record):
    if (record["schema"] != SCHEMA or record["alignment_id"] != identity(physical_record(record))
            or record["record_id"] != identity({k: v for k, v in record.items() if k != "record_id"})
            or [s["id"] for s in record["stops"]] != list(STOP_IDS)
            or record["chainages_km"] != [s["chainage_km"] for s in record["stops"]]
            or record["route_km"] != record["chainages_km"][-1]
            or record["chainages_km"][0] != 0
            or any(b <= a for a, b in pairwise(record["chainages_km"]))):
        raise ValueError("Airport alignment ID, stop order or chainage does not match")
    if (record["grade_profile"] is not None
            or any(a["coordinates"][-1] != b["coordinates"][0] for a, b in pairwise(record["segments"]))
            or abs(length_km(physical_record(record)["horizontal_trace"]) - record["route_km"]) > 1e-9):
        raise ValueError("Airport alignment geometry or grade basis does not match the horizontal screen")
    return record


def evaluate(survey=None):
    opening, service, register, hashes = corridor.sources()
    parent_id = opening["candidate_id"]
    source_stops = service["group"]["outward_stops"]
    if [stop["id"] for stop in source_stops] != list(STOP_IDS):
        raise ValueError("Airport source stop order changed")
    lookup = {stop["id"]: stop for stop in register["networks"]["first"]["mapped_points"]}
    places = []
    for stop in source_stops:
        if stop["register_id"] is None:
            places.append(None)
            continue
        ref = lookup[stop["register_id"]]
        if ref["label"] != stop["label"] or ref["route_hint"] != "Airport":
            raise ValueError("Airport stop source differs from the station register")
        places.append(coordinate(ref["longitude_latitude"]))

    anchors = [point for point in places if point is not None]
    context = map_context(hashes)
    bounds = context["bounds_wsen"]
    if not all(within_coverage(point, bounds) for point in anchors):
        raise ValueError("Airport station register differs from the retained Baghdad map coverage")
    bound = length_km(anchors)
    survey_source = None
    if survey is None:
        sections = mapped_sections(anchors, context["layers"]["roads"])
        if not all(within_coverage(point, bounds) for _, points, _ in sections for point in points):
            raise ValueError("Reviewed Airport Highway sections differ from the retained Baghdad map coverage")
        locations = places
        mode = "mapped_road_reference_and_review_connectors"
    else:
        points, vertices, survey_source = survey_input(survey, parent_id, bounds)
        locations = [points[i] for i in vertices]
        sections = [("supplied_centreline", points[a:b + 1], "Submitted centreline between declared stop vertices.")
                    for a, b in pairwise(vertices)]
        hashes["survey_input"] = survey_source["file_sha256"]
        mode = "supplied_centreline"

    lengths = [length_km(section[1]) for section in sections]
    cumulative = list(accumulate(lengths, initial=0.0))
    segments = [
        {"kind": kind, "coordinates": points, "start_km": start, "end_km": end, "description": description}
        for (kind, points, description), start, end in zip(sections, cumulative, cumulative[1:])
    ]
    if survey is None:
        chainages = [0.0, cumulative[3], cumulative[6], cumulative[7],
                     (cumulative[7] + cumulative[8]) / 2, cumulative[8]]
    else:
        chainages = cumulative
    stops = [
        {
            "id": stop["id"], "label": stop["label"], "register_id": stop["register_id"],
            "longitude_latitude": point, "chainage_km": km, "approved_station_site": False,
            "location_scope": ("submitted_stop_vertex" if survey is not None else stop["location_scope"]),
            "chainage_scope": "horizontal path distance" if point is not None else "midpoint operating assumption",
            "offset_from_register_centroid_km": stop_offset(anchor, point) if survey is not None else None,
        }
        for stop, point, km, anchor in zip(source_stops, locations, chainages, places)
    ]
    nominal = service["group"]["one_way_km"]
    record = {
        "schema": SCHEMA, "parent_candidate_id": parent_id, "geometry_mode": mode,
        "route_km": cumulative[-1], "chainages_km": chainages, "stops": stops, "segments": segments,
        "mapped_road_reference_km": sum(length for length, segment in zip(lengths, segments)
                                        if segment["kind"] == "mapped_road_reference"),
        "review_connector_km": sum(length for length, segment in zip(lengths, segments)
                                   if segment["kind"] == "review_connector"),
        "grade_profile": None, "physical_acceptance": "open", "survey_source": survey_source,
        "historical_route_order_screen": {
            "nominal_km": nominal,
            "mapped_centroid_bound_km": bound,
            "bound_minus_nominal_km": bound - nominal,
            "screen_passed": nominal >= bound,
            "basis": "Great-circle sum through five known centroids in route order, omitting the unlocated stop.",
        },
        "retained_map_bounds_wsen": bounds,
        "review_gaps": [segment["description"] for segment in segments if segment["kind"] == "review_connector"]
        + ["Survey vertical alignment, curves, clearances, geotechnics, utilities and land.",
           "Confirm all station sites, entrances and step-free access."],
        "dwell_s": service["patterns"][0][1]["departure_s"] - service["patterns"][0][1]["arrival_s"],
        "source_sha256": {**hashes, str(Path(__file__).resolve().relative_to(ROOT)): sha256(Path(__file__).read_bytes()).hexdigest()},
    }
    record["alignment_id"] = identity(physical_record(record))
    record["record_id"] = identity(record)
    return validate(record)


def geojson(record):
    validate(record)
    features = [
        {"type": "Feature", "geometry": {"type": "LineString", "coordinates": segment["coordinates"]},
         "properties": {key: value for key, value in segment.items() if key != "coordinates"}}
        for segment in record["segments"]
    ]
    features += [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": stop["longitude_latitude"]} if stop["longitude_latitude"] else None,
         "properties": {key: value for key, value in stop.items() if key != "longitude_latitude"}}
        for stop in record["stops"]
    ]
    return {"type": "FeatureCollection", "alignment_id": record["alignment_id"],
            "source_sha256": record["source_sha256"], "features": features}

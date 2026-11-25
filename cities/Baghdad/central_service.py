"""Concept alignments and end-to-end train paths for a central Baghdad option."""

import gzip
from hashlib import sha256
from itertools import accumulate, pairwise
import json
from math import ceil, isclose
from pathlib import Path
import tomllib

from cities.Baghdad import citywide_clockface
from engineering.outline import baghdad_system as system
from engineering.outline.city_alignment import distance

CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
MAP = CITY.parent / "catalogue/west-asia/Iraq/Baghdad/map-context.json.gz"
STREETS = MAP.parent / "engineering/mapping/walking-streets.geojson.gz"
INPUT = CITY / "central-service-routes.toml"
VEHICLE = CITY / "engineering/mechanical/vehicle/section-trial.toml"


def _json(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def _centerline_crossings(coordinates, river):
    intersections = []
    for a, b in pairwise(coordinates):
        dx, dy = b[0] - a[0], b[1] - a[1]
        for c, d in river:
            ex, ey = d[0] - c[0], d[1] - c[1]
            divisor = dx * ey - dy * ex
            if not divisor:
                continue
            fx, fy = c[0] - a[0], c[1] - a[1]
            t = (fx * ey - fy * ex) / divisor
            u = (fx * dy - fy * dx) / divisor
            if 0 <= t <= 1 and 0 <= u <= 1:
                point = [round(a[0] + t * dx, 9), round(a[1] + t * dy, 9)]
                if point not in intersections:
                    intersections.append(point)
    return intersections


def _layer_index(map_context, walking_streets, source):
    way_ids = {row["way"] for row in source["stations"].values() if "way" in row}
    way_ids |= {row["way"] for row in source["waypoints"].values() if "way" in row}
    ways = {f["id"]: f for f in walking_streets["features"] if f["id"] in way_ids}
    if way_ids != ways.keys():
        raise ValueError("A route control cannot be found in the archived walking streets")
    places = {f["id"]: f for f in map_context["layers"]["places"]}
    river = []
    for feature in map_context["layers"]["water"]:
        if feature["properties"].get("name:en") == "Tigris River":
            geometry = feature["geometry"]
            lines = [geometry["coordinates"]] if geometry["type"] == "LineString" else geometry["coordinates"]
            river.extend(edge for line in lines for edge in pairwise(line))
    if not river:
        raise ValueError("Tigris centreline is missing from the retained map")
    return ways, places, river


def _point(row, ways, places):
    if "place" in row:
        return places[row["place"]]["geometry"]["coordinates"]
    if "way" in row:
        return ways[row["way"]]["geometry"]["coordinates"][row["vertex"]]
    return row["coordinates"]


def evaluate():
    source = tomllib.loads(INPUT.read_text(encoding="utf-8"))
    cfg = system.load(network="metropolitan")
    ways, places, river = _layer_index(_json(MAP), _json(STREETS), source)
    stations = {}
    for name, data in source["stations"].items():
        point = _point(data, ways, places)
        stations[name] = {
            "name": data["name"], "coordinates": point, "source": data["source"],
            "basis": data["basis"],
        }
    waypoints = {name: _point(row, ways, places) for name, row in source["waypoints"].items()}
    if stations.keys() & waypoints.keys():
        raise ValueError("A route control duplicates a station identifier")
    points = {name: row["coordinates"] for name, row in stations.items()} | waypoints
    lines, timed = {}, {}
    used = set()
    for line, spec in source["lines"].items():
        sequence = spec["sequence"]
        geometry = [points[marker] for marker in sequence]
        ids = [marker for marker in sequence if marker in stations]
        if (len(ids) < 2 or sequence[0] != ids[0] or sequence[-1] != ids[-1]
                or len(ids) != len(set(ids))):
            raise ValueError(f"{line} needs distinct terminal and intermediate stations")
        distances = list(accumulate((distance(a, b) / 1000 for a, b in pairwise(geometry)), initial=0.0))
        if any(b <= a for a, b in pairwise(distances)):
            raise ValueError(f"{line} has a zero-length map segment")
        crossings = _centerline_crossings(geometry, river)
        if len(crossings) != spec["tigris_crossings"]:
            raise ValueError(f"{line} crosses the mapped Tigris {len(crossings)} times")
        station_chainage = {marker: km for marker, km in zip(sequence, distances, strict=True)
                            if marker in stations}
        km = distances[-1]
        lines[line] = {
            "name": spec["name"], "station_ids": ids, "geometry": geometry, "one_way_km": km,
            "station_chainage_km": station_chainage, "tigris_crossings": crossings,
            "corridor_basis": spec["basis"],
        }
        used.update(ids)
        timed[line] = {
            "one_way_km": km,
            "one_way_s_including_dwell": ceil(km / source["commercial_speed_kmh"] * 3600),
            "outward_stops": [
                dict(id=marker, fraction=chainage / km, interchange_hint=source["interchange"]
                     if marker == source["interchange"] else None)
                for marker, chainage in station_chainage.items()
            ],
        }
    interchange = source["interchange"]
    if used != stations.keys() or set.intersection(*(set(row["station_ids"]) for row in lines.values())) != {interchange}:
        raise ValueError("Every defined station needs service and the lines need exactly the stated transfer")
    brake = tomllib.loads(VEHICLE.read_text(encoding="utf-8"))["braking_deceleration_m_s2"]
    service_cfg = {
        **cfg, "vehicle": dict(cfg["vehicle"], dwell_s=source["dwell_s"],
                               speed_cap_kmh=source["speed_cap_kmh"]),
        "service_plan": dict(cfg["service_plan"], terminal_layover_min_each_end=source["terminal_layover_min"]),
    }
    trials = {}
    for headway in source["headways_s"]:
        trial = citywide_clockface.evaluate(timed, service_cfg, brake, headway, include_workings=True)
        trials[str(headway)] = trial
        if trial["resource_screen_passed"]:
            break
    if not trial["resource_screen_passed"]:
        raise ValueError("No continuous central service passes the declared resource screen")
    for line, row in lines.items():
        timed_line = trial["groups"][line]
        patterns = [[r[0] for r in p] for p in timed_line["patterns"]]
        if patterns != [row["station_ids"], row["station_ids"][::-1]]:
            raise ValueError(f"{line} train working does not match its mapped stops")
        row.update({key: timed_line[key] for key in (
            "run_s", "turn_s", "sets", "departures", "yard_km_day", "block_margin_s",
            "berth_margin_s", "throat_margin_s", "patterns"
        )})
    route_km = sum(row["one_way_km"] for row in lines.values())
    days = service_cfg["vehicle"]["service_days_per_year"]
    if not isclose(route_km, sum(row["one_way_km"] for row in trial["groups"].values())):
        raise ValueError("The service and concept alignments use different distances")
    geometry = {
        "lines": {key: {field: line[field] for field in ("geometry", "station_ids")}
                  for key, line in lines.items()},
        "stations": {key: row["coordinates"] for key, row in stations.items()},
        "configuration": "independent elevated east–west and Rusafa lines with separated tracks at Tahrir",
        "train_length_m": cfg["vehicle_geometry"]["train_length_m"],
    }
    result = {
        "schema": "osr-baghdad-central-service/1", "candidate_id": system._id(geometry),
        "scope": source["scope"], "stations": stations, "lines": lines, "route_km": route_km,
        "interchange_station_id": interchange, "public_notes": source["public_notes"],
        "headway_s": trial["headway_s"], "minimum_clearances_s": trial["minimum_clearances_s"],
        "service_day_start_hour": cfg["service_plan"]["start_hour_local"],
        "service_hours_per_day": cfg["vehicle"]["service_hours_per_day"],
        "departures_per_day": sum(row["departures"] for row in lines.values()),
        "resource_screen_passed": trial["resource_screen_passed"], "service_trials": trials,
        "diagrammed_trainsets": sum(row["sets"] for row in lines.values()),
        "trainsets_with_reserve": ceil(sum(row["sets"] for row in lines.values()) / source["availability"]),
        "availability_assumption": source["availability"],
        "places_per_train_assumption": cfg["vehicle"]["normal_places_per_train"],
        "annual_passenger_train_km": days * sum(row["one_way_km"] * row["departures"] for row in lines.values()),
        "annual_yard_train_km": days * sum(row["yard_km_day"] for row in lines.values()),
        "source_sha256": {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
                          for path in (
                              INPUT, MAP, STREETS, CITY / "system.toml", VEHICLE, Path(__file__),
                              Path(system.__file__), Path(citywide_clockface.__file__),
                              Path(citywide_clockface.diagrams.__file__), Path(distance.__code__.co_filename)
                          )},
        "physical_acceptance": False, "complete_capital_usd": None,
    }
    result["evaluation_id"] = system._id(result)
    return result

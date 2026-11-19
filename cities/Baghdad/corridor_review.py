"""Publish a geographic reading of named corridors in the 2024 NIC brief."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONTEXT = HERE.parent / "catalogue/west-asia/Iraq/Baghdad/map-context.json.gz"
WAYPOINTS = HERE / "maps/rfi-waypoints.json"
LEGACY = HERE / "maps/network-148km.geojson"
OUTPUT = HERE / "maps/corridor-review.geojson"

# Quarter labels distinguish the named urban areas from larger administrative
# districts. Arabic source names below are the exact names in the retained tile.
QUARTERS = {
    "Al Adhamiya": ("الأعظمية", "Red", "A district centroid fell near Al Shaab."),
    "Al Mustansiriya": ("حي المستنصرية", "Red", "Previously unlocated in the waypoint table."),
    "Al Saydiyya": ("السيدية", "Green", "Previously unlocated in the waypoint table."),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    source = json.loads(WAYPOINTS.read_bytes())
    legacy = json.loads(LEGACY.read_bytes())
    with gzip.open(CONTEXT) as stream:
        context = json.load(stream)
    features = []
    gaps = {}
    for line in source["rfi_nominal_km"]:
        gaps[line] = []
        previous = None
        rows = sorted((row for row in source["waypoints"]
                       if row["line"] == line and row["kind"] == "rfi_named"),
                      key=lambda row: row["order"])
        for row in rows:
            name = row["rfi_name"]
            point = [row["lon"], row["lat"]]
            props = {k: v for k, v in row.items() if k not in ("lon", "lat")}
            if name in QUARTERS:
                label, expected_line, reason = QUARTERS[name]
                matches = [f for f in context["layers"]["places"]
                           if f["properties"].get("name") == label
                           and f["properties"].get("kind_detail") == "quarter"]
                if len(matches) != 1 or line != expected_line:
                    raise ValueError(f"Cannot resolve {line} {name} to one source quarter")
                place = matches[0]
                point = place["geometry"]["coordinates"]
                props.update(coordinate_scope="quarter_label", source_name=label,
                             previous_coordinate=[row["lon"], row["lat"]],
                             review_reason=reason, osm_id=None, osm_type=None, source_url=None,
                             coordinate_source="cities/catalogue/west-asia/Iraq/Baghdad/map-context.json.gz")
            if None in point:
                gaps[line].append({"order": row["order"], "name": name})
                previous = None
                continue
            props["map_label"] = name
            features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": point},
                             "properties": props})
            if previous is not None:
                order, start = previous
                features.append({"type": "Feature",
                                 "geometry": {"type": "LineString", "coordinates": [start, point]},
                                 "properties": {"kind": "named_place_sequence", "line": line,
                                                "from_order": order, "to_order": row["order"],
                                                "surveyed_alignment": False}})
            previous = (row["order"], point)
    for f in legacy["features"]:
        if f["properties"].get("kind") in ("priority_proximity_area", "proposed_population_anchor"):
            features.append(f)
    return {"type": "FeatureCollection", "name": "Baghdad first-programme geographic review",
            "purpose": "Locate named RFI areas. Lines connect successive located names only. "
                       "Population anchors mark access questions. Distances between markers do not define track quantities.",
            "official_rfi_url": source["official_rfi_url"], "rfi_nominal_km": source["rfi_nominal_km"],
            "program_km": sum(source["rfi_nominal_km"].values()), "unlocated_named_occurrences": gaps,
            "source_sha256": {p.relative_to(HERE.parents[1]).as_posix(): digest(p)
                              for p in (CONTEXT, WAYPOINTS, LEGACY)}, "features": features}


def write():
    data = build()
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data


if __name__ == "__main__":
    write()

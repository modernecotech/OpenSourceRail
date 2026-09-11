"""Validated, revision-bound station/civil/cant data for LandXML imports."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import tomllib

from .validate import ALLOWED_CIVIL_CLASSES, PRESETS


def read_sidecar(path: Path, xml_path: Path, design_path: Path, meta) -> dict:
    document = tomllib.loads(path.read_text())
    if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise ValueError("sidecar schema_version must be 1")
    if set(document) != {"schema_version", "source", "station", "civil", "cant"}:
        raise ValueError("sidecar requires source, station, civil and explicit cant sections")
    source = document["source"]
    if not isinstance(source, dict) or set(source) != {
        "landxml_sha256", "design_sha256", "alignment_name", "line_id", "crs", "vertical_datum"
    }:
        raise ValueError("sidecar source fields are missing or unknown")
    for key, value in source.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"sidecar source.{key} must be a nonempty string")
    for key, input_path in (("landxml_sha256", xml_path), ("design_sha256", design_path)):
        if source[key] != hashlib.sha256(input_path.read_bytes()).hexdigest():
            raise ValueError(f"sidecar {key} does not match the input revision")
    if source["line_id"] != meta.line_id or source["crs"] != meta.crs:
        raise ValueError("sidecar line_id/CRS disagrees with conversion metadata")
    if meta.units != "metric":
        raise ValueError("sidecar import requires metric units")
    design = tomllib.loads(design_path.read_text())
    lines = [line for line in design.get("lines", []) if (line.get("id") or line.get("name")) == meta.line_id]
    if len(lines) != 1:
        raise ValueError("sidecar line_id must resolve to exactly one design line")
    line = lines[0]
    if line.get("rolling_stock") != meta.consist or line.get("geometry") != meta.preset:
        raise ValueError("sidecar line consist/preset disagrees with design")
    if bool(line.get("is_ring") or line.get("shape") == "ring") != meta.is_ring:
        raise ValueError("sidecar line ring status disagrees with design")
    if meta.preset not in PRESETS or meta.consist not in PRESETS[meta.preset].compatible_consists:
        raise ValueError("sidecar requires a compatible preset and consist")
    known = {s["id"] for s in design.get("stations", []) if s.get("line") == meta.line_id}
    known.update(s["id"] for s in line.get("stations", []))
    if not known:
        raise ValueError("design line has no station IDs")
    document["known_station_ids"] = known
    document["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return document


def _number(row: dict, field: str) -> float:
    value = row.get(field)
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"sidecar {field} must be a finite number")
    return float(value)


def _rows(document: dict, section: str, fields: set[str], optional: set[str] | None = None) -> list[dict]:
    rows = document[section]
    if not isinstance(rows, list):
        raise ValueError(f"sidecar {section} must be an array of tables")
    for row in rows:
        if not isinstance(row, dict) or not fields <= set(row) or set(row) - fields - (optional or set()):
            raise ValueError(f"sidecar {section} fields are missing or unknown")
    return rows


def validate_sidecar(document: dict, alignment, meta) -> dict:
    """Validate without substituting inferred values for supplied evidence."""
    length = alignment.length_m
    if not math.isfinite(length) or length <= 0:
        raise ValueError("sidecar requires a positive alignment length")
    if any(not math.isfinite(value) for point in [*alignment.horizontal, *alignment.vertical]
           for value in vars(point).values()):
        raise ValueError("LandXML geometry must contain only finite numbers")
    if not alignment.horizontal or min(p.station_m for p in alignment.horizontal) != 0:
        raise ValueError("sidecar import requires zero-origin chainage")
    if abs(max(p.station_m for p in alignment.horizontal) - length) > 1e-6:
        raise ValueError("LandXML horizontal extent disagrees with declared alignment length")
    stations = _rows(document, "station", {"id", "station_m", "platform_length_m"}, {"source_name"})
    ids, source_names = set(), set()
    xml_stations = {}
    for station in alignment.stations:
        if station.placeholder_id in xml_stations:
            raise ValueError("LandXML station names must be unique for sidecar mapping")
        xml_stations[station.placeholder_id] = station.station_m
    for row in stations:
        station_id = row["id"]
        if not isinstance(station_id, str) or station_id not in document["known_station_ids"] or station_id in ids:
            raise ValueError("sidecar station ID is unknown, on another line, or duplicated")
        ids.add(station_id)
        chainage = _number(row, "station_m")
        if not 0 <= chainage <= length or _number(row, "platform_length_m") <= 0:
            raise ValueError("sidecar station chainage/platform length is outside its valid range")
        if "source_name" in row:
            name = row["source_name"]
            if not isinstance(name, str) or name not in xml_stations or name in source_names:
                raise ValueError("sidecar source_name is unknown or duplicated")
            if abs(xml_stations[name] - chainage) > 1e-6:
                raise ValueError("sidecar station chainage disagrees with LandXML")
            source_names.add(name)
    if ids != document["known_station_ids"]:
        raise ValueError("sidecar stations do not cover every station on the design line")
    if source_names != set(xml_stations):
        raise ValueError("sidecar must map every LandXML station name")

    _rows(document, "civil", {"from_station_m", "to_station_m", "class"})
    for section in ("civil", "cant"):
        if section == "cant":
            _rows(document, section, {"from_station_m", "to_station_m", "max_cant_mm", "transition_in_m", "transition_out_m"})
        spans = document[section]
        for row in spans:
            start, end = _number(row, "from_station_m"), _number(row, "to_station_m")
            if not 0 <= start < end <= length:
                raise ValueError(f"sidecar {section} span is outside the alignment")
        spans.sort(key=lambda row: row["from_station_m"])
        previous = 0.0
        for row in spans:
            start, end = row["from_station_m"], row["to_station_m"]
            if (section == "civil" and start != previous) or start < previous:
                raise ValueError(f"sidecar {section} spans overlap or leave a civil gap")
            if section == "civil":
                if not isinstance(row["class"], str) or row["class"] not in ALLOWED_CIVIL_CLASSES:
                    raise ValueError("sidecar civil class is not supported")
            else:
                cant = _number(row, "max_cant_mm")
                entry, exit = _number(row, "transition_in_m"), _number(row, "transition_out_m")
                if not 0 <= cant <= PRESETS[meta.preset].max_cant_mm:
                    raise ValueError("sidecar cant exceeds the selected preset")
                if entry < 0 or exit < 0 or entry + exit > end - start or (cant > 0 and (entry == 0 or exit == 0)):
                    raise ValueError("sidecar cant transitions do not fit the span")
            previous = end
        if section == "civil" and (not spans or previous != length):
            raise ValueError("sidecar civil spans must cover the full alignment")
    document["station"] = sorted(stations, key=lambda row: (row["station_m"], row["id"]))
    return document

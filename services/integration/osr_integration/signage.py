"""Read-only passenger display projection for the selected synthetic v0.7 railway.

Departure times are supplied by an explicit simulation snapshot. This module
never derives a timetable or produces a train-control command.
"""
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
import re


SCHEMA = "osr-passenger-signage-projection/1"
SNAPSHOT_SCHEMA = "osr-passenger-service-snapshot/1"


def _time(value):
    if not isinstance(value, str):
        raise ValueError("Timezone-aware ISO 8601 time required")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Timezone-aware ISO 8601 time required") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Timezone-aware ISO 8601 time required")
    return result.astimezone(timezone.utc)


def _station_id(line_id, index):
    return f"{line_id}:S{index:02d}"


def project(selection, handoff, snapshot, *, at_utc, stale_after_seconds=60):
    """Project a bounded simulation snapshot to accessible display text.

    The station and line identities are checked against the selected 30 km
    configuration. A stale snapshot suppresses every departure time.
    """
    if (selection.get("schema") != "opensourcerail.v07.digital-selection.1"
            or handoff.get("schema") != "osr-v07-digital-production-handoff/1"):
        raise ValueError("Selected v0.7 digital sources required")
    handoff_body = {key: value for key, value in handoff.items() if key != "evaluation_id"}
    handoff_id = sha256(json.dumps(handoff_body, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    if handoff.get("evaluation_id") != handoff_id:
        raise ValueError("Production handoff content differs from its evaluation")
    for key in ("physical_candidate_id", "selection_id"):
        if not isinstance(selection.get(key), str) or not selection[key]:
            raise ValueError("Selected candidate identities required")
        if selection[key] != handoff.get(key) or selection[key] != snapshot.get(key):
            raise ValueError("Passenger display candidate identity differs")
    if (not selection.get("evaluation_id") or not handoff.get("evaluation_id")
            or snapshot.get("selection_evaluation_id") != selection["evaluation_id"]
            or snapshot.get("evaluation_id") != handoff["evaluation_id"]):
        raise ValueError("Passenger display evaluation ancestry differs")
    line_id = handoff.get("configuration_id")
    if (not isinstance(line_id, str) or not line_id
            or snapshot.get("schema") != SNAPSHOT_SCHEMA
            or snapshot.get("source") != "simulation"
            or snapshot.get("line_id") != line_id):
        raise ValueError("Selected simulation line required")
    station_count = handoff.get("control_electronics", {}).get("equipment", {}).get(
        "station-dispatch-controller", {}).get("quantity")
    index = snapshot.get("station_index")
    if (type(station_count) is not int or station_count < 2 or type(index) is not int
            or not 1 <= index <= station_count
            or snapshot.get("station_id") != _station_id(line_id, index)):
        raise ValueError("Selected station identity required")
    if type(stale_after_seconds) is not int or not 1 <= stale_after_seconds <= 3600:
        raise ValueError("Bounded stale interval required")
    now, observed = _time(at_utc), _time(snapshot.get("observed_at_utc"))
    age = (now - observed).total_seconds()
    if age < 0:
        raise ValueError("Future service snapshot rejected")
    arrivals = snapshot.get("departures")
    if not isinstance(arrivals, list) or len(arrivals) > 12:
        raise ValueError("At most twelve source departures required")
    rows = []
    seen = set()
    for row in arrivals:
        if not isinstance(row, dict) or set(row) != {"service_id", "destination_station_index", "departure_at_utc"}:
            raise ValueError("Explicit source departure fields required")
        service = row["service_id"]
        destination = row["destination_station_index"]
        departure = _time(row["departure_at_utc"])
        if (not isinstance(service, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}", service)
                or service in seen or type(destination) is not int
                or not 1 <= destination <= station_count or destination == index
                or departure < observed):
            raise ValueError("Invalid source departure or destination")
        seen.add(service)
        rows.append({"service_id": service,
                     "destination_station_index": destination,
                     "destination_station_id": _station_id(line_id, destination),
                     "departure_at_utc": departure.isoformat().replace("+00:00", "Z")})
    rows.sort(key=lambda row: (row["departure_at_utc"], row["service_id"]))
    fresh = age <= stale_after_seconds
    visible = [row for row in rows if _time(row["departure_at_utc"]) >= now] if fresh else []
    station_label = f"Station {index}"
    if not fresh:
        message = "Service information unavailable. Follow station announcements."
    elif not visible:
        message = "No departures are published for this station."
    else:
        message = "; ".join(
            f"Service {row['service_id']} to Station {row['destination_station_index']}, "
            f"departing {row['departure_at_utc']}" for row in visible)
    return {"schema": SCHEMA, "mode": "simulation", "read_only": True,
            "movement_authority": False, "control_output": False,
            "physical_candidate_id": selection["physical_candidate_id"],
            "evaluation_id": handoff["evaluation_id"],
            "selection_evaluation_id": selection["evaluation_id"],
            "selection_id": selection["selection_id"],
            "line_id": line_id, "station_id": snapshot["station_id"],
            "station_label": station_label, "source_observed_at_utc": observed.isoformat().replace("+00:00", "Z"),
            "displayed_at_utc": now.isoformat().replace("+00:00", "Z"),
            "data_status": "fresh" if fresh else "stale", "departures": visible,
            "accessible_text": f"Planning simulation. {station_label}. {message}"}


def render_html(projection):
    """Render a static, escaped passenger-information panel without controls."""
    if (projection.get("schema") != SCHEMA or projection.get("mode") != "simulation"
            or projection.get("read_only") is not True
            or projection.get("movement_authority") is not False
            or projection.get("control_output") is not False
            or projection.get("data_status") not in {"fresh", "stale"}
            or not isinstance(projection.get("departures"), list)):
        raise ValueError("Read-only simulation projection required")
    station = escape(str(projection["station_label"]), quote=True)
    message = escape(str(projection["accessible_text"]), quote=True)
    status = projection["data_status"]
    parts = [f'<section role="region" aria-labelledby="osr-signage-heading" data-status="{status}">',
             f'<h1 id="osr-signage-heading">{station}</h1>',
             '<p class="simulation-label">Planning simulation · passenger information only</p>',
             f'<p role="status" aria-live="polite" class="{status}">{message}</p>']
    if status == "fresh" and projection["departures"]:
        parts.append('<table><caption>Published departures</caption><thead><tr>'
                     '<th scope="col">Service</th><th scope="col">Destination</th>'
                     '<th scope="col">Departure UTC</th></tr></thead><tbody>')
        for row in projection["departures"]:
            if not isinstance(row, dict) or not all(
                    isinstance(row.get(key), str) for key in
                    ("service_id", "destination_station_id", "departure_at_utc")):
                raise ValueError("Display departure fields required")
            parts.append('<tr><td>' + escape(row["service_id"], quote=True) + '</td><td>'
                         + escape(row["destination_station_id"], quote=True) + '</td><td>'
                         + escape(row["departure_at_utc"], quote=True) + '</td></tr>')
        parts.append('</tbody></table>')
    parts.append('</section>')
    return ''.join(parts)

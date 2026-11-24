"""Hourly Airport demand at fixed volume, under service sensitivities or from observed OD."""

from datetime import date
from hashlib import sha256
import json
from math import ceil, exp, isfinite
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.simulation import airport_alignment, corridor
from engineering.outline import baghdad_diagrams

SCHEMA = "osr-baghdad-airport-demand/1"
OBSERVED_SCHEMA = "osr-baghdad-airport-observed-od/2"
SERVICE_DAY_COUNT = 365
WALK_CASES = {
    "short": (100, 1.2, 20),
    "central": (300, 1.0, 60),
    "long": (600, 0.75, 120),
}
INTERCHANGE_INDICES = (1, 3)
SYSTEM = corridor.CITY / "system.toml"


def empty_matrices():
    return [[[0.0] * 6 for _ in range(6)] for _ in range(24)]


def annual_total(matrices):
    result = sum(value for matrix in matrices for row in matrix for value in row) * SERVICE_DAY_COUNT
    if not isfinite(result):
        raise ValueError("OD totals exceed the finite numerical range")
    return result


def booked_minutes(stops, cfg, dwell_s):
    route_km = stops[-1]
    vehicle = cfg["vehicle"]
    run_s = ceil(route_km * 3600 / vehicle["commercial_speed_kmh"])
    positions = [{"fraction": km / route_km} for km in stops]
    outward = baghdad_diagrams.pattern(positions, run_s, dwell_s, route_km, vehicle["speed_cap_kmh"])
    inward = baghdad_diagrams.pattern(
        [{"fraction": 1 - p["fraction"]} for p in reversed(positions)],
        run_s, dwell_s, route_km, vehicle["speed_cap_kmh"]
    )[::-1]
    times = [[0.0] * 6 for _ in stops]
    for a in range(6):
        for b in range(a + 1, 6):
            times[a][b] = (outward[b]["arrival_s"] - outward[a]["departure_s"]) / 60
            times[b][a] = (inward[a]["arrival_s"] - inward[b]["departure_s"]) / 60
    return times


def generalised_minutes(ride, headway, walk, transfer, transfer_share, transfer_penalty_min,
                        connecting_headway_min, fare_usd, value_of_time_usd_h):
    metres, speed, wait_s = WALK_CASES[walk]
    path_min = (metres / speed + wait_s) / 60
    wait_weight, walk_weight = 2, 2
    station_access_egress = 2 * path_min
    transfer_cost = (walk_weight * path_min + wait_weight * connecting_headway_min / 2
                     + transfer_penalty_min) * transfer_share if transfer else 0.0
    fare_min = fare_usd * 60 / value_of_time_usd_h
    return [
        [
            ride[a][b] + wait_weight * headway / 2 + walk_weight * station_access_egress + fare_min
            + (transfer_cost if a in INTERCHANGE_INDICES or b in INTERCHANGE_INDICES else 0.0)
            if a != b else 0.0
            for b in range(6)
        ]
        for a in range(6)
    ]


def observed_matrices(path, alignment, prior, expected_service):
    raw = Path(path).read_bytes()
    supplied = json.loads(raw)
    if (not isinstance(supplied, dict) or supplied.get("schema") != OBSERVED_SCHEMA
            or supplied.get("alignment_id") != alignment["alignment_id"]
            or supplied.get("stop_ids") != list(airport_alignment.STOP_IDS)
            or supplied.get("timezone") != "Asia/Baghdad"
            or not isinstance(supplied.get("document"), str) or not supplied["document"].strip()):
        raise ValueError("Observed OD v2 needs the matching alignment, ordered stop IDs, Baghdad local time and a source document")
    service = supplied.get("service_offer")
    if (not isinstance(service, dict) or service != expected_service
            or any(isinstance(service[key], bool) != isinstance(value, bool)
                   for key, value in expected_service.items())):
        raise ValueError("Observed OD service offer must match the booked service, fare and access context")
    try:
        first, last = (date.fromisoformat(supplied[k]) for k in ("sample_date_from", "sample_date_to"))
    except (KeyError, ValueError, TypeError) as error:
        raise ValueError("Provide the observed OD sample interval as ISO dates") from error
    sample_days = supplied.get("observed_days")
    rows = supplied.get("od")
    resolution = supplied.get("resolution")
    if (type(sample_days) is not int or not 1 <= sample_days <= (last - first).days + 1
            or not isinstance(rows, list) or not rows or resolution not in ("hourly", "daily")):
        raise ValueError("Provide sample days within the interval, nonempty OD and hourly or daily resolution")
    all_od, paid_od = empty_matrices(), empty_matrices()
    indices = {stop_id: i for i, stop_id in enumerate(airport_alignment.STOP_IDS)}
    seen = set()
    for row in rows:
        fields = {"from", "to", "all", "paying"}
        if resolution == "hourly":
            fields.add("hour")
        if not isinstance(row, dict) or row.keys() != fields:
            raise ValueError("Observed OD rows require from, to, all and paying, plus local hour for hourly data")
        a, b, total, paying = (row[k] for k in ("from", "to", "all", "paying"))
        hour = row.get("hour")
        if (not isinstance(a, str) or not isinstance(b, str) or a not in indices or b not in indices
                or a == b or (resolution == "hourly" and (type(hour) is not int or not 0 <= hour <= 23))
                or (hour, a, b) in seen
                or type(total) is not int or type(paying) is not int or not 0 <= paying <= total):
            raise ValueError("Check distinct route stops, unique OD rows, local hour and observed counts")
        try:
            daily_total, daily_paying = total / sample_days, paying / sample_days
        except OverflowError as error:
            raise ValueError("OD counts exceed the finite numerical range") from error
        seen.add((hour, a, b))
        i, j = indices[a], indices[b]
        if resolution == "hourly":
            weights = [float(h == hour) for h in range(24)]
        else:
            distribution = [matrix[i][j] for matrix in prior]
            daily = sum(distribution)
            weights = [value / daily for value in distribution] if daily else [1 / 18 if 6 <= h < 24 else 0
                                                                              for h in range(24)]
        for h, weight in enumerate(weights):
            all_od[h][i][j] = weight * daily_total
            paid_od[h][i][j] = weight * daily_paying
    source = {
        "document": supplied["document"], "file_sha256": sha256(raw).hexdigest(),
        "service_offer": service,
        "sample_date_from": str(first), "sample_date_to": str(last), "observed_days": sample_days,
        "annualisation_days": SERVICE_DAY_COUNT, "count_resolution": resolution,
        "peak_scope": ("Sample mean local hour" if resolution == "hourly" else
                       "Daily observed pairs allocated by the historic hourly profile. Hourly peak remains a model sensitivity."),
    }
    return all_od, paid_od, source


def summarize(hourly_od, chainages_km, headway_min):
    busiest = queue = passenger_km = 0.0
    for matrix in hourly_od:
        for index, row in enumerate(matrix):
            passenger_km += sum(flow * abs(chainages_km[index] - chainages_km[target])
                                for target, flow in enumerate(row))
            queue = max(queue, sum(row[:index]), sum(row[index + 1:]))
        for leg in range(5):
            beyond = [(a, b) for a in range(leg + 1) for b in range(leg + 1, 6)]
            busiest = max(busiest, sum(matrix[a][b] for a, b in beyond), sum(matrix[b][a] for a, b in beyond))
    annual_passenger_km = passenger_km * SERVICE_DAY_COUNT
    if not all(map(isfinite, (busiest, queue, annual_passenger_km))):
        raise ValueError("OD loading or passenger-km exceeds the finite numerical range")
    return {
        "busiest_departure_load": busiest * (headway_min / 60),
        "platform_queue": queue * (headway_min / 60),
        "annual_passenger_km": annual_passenger_km,
    }


def evaluate(alignment, *, headway_min=15, mode="service_sensitive", demand="central", observed=None,
             walk="central", transfer=True, transfer_share=0.35, transfer_penalty_min=5.0,
             connecting_headway_min=15.0, fare_usd=0.0, value_of_time_usd_h=3.0, response_per_min=0.025,
             dwell_s=None, formation_cars=6):
    airport_alignment.validate(alignment)
    dwell_s = alignment["dwell_s"] if dwell_s is None else dwell_s
    if (headway_min not in (15, 20, 30) or mode not in ("fixed", "service_sensitive", "observed")
            or demand not in ("downside", "central", "upside") or walk not in WALK_CASES
            or type(transfer) is not bool or (mode == "observed" and observed is None)
            or type(formation_cars) is not int or formation_cars not in (3, 6)):
        raise ValueError("Use a supported Airport service, demand mode and walking case")
    bounded = ((transfer_share, 0, 1), (transfer_penalty_min, 0, 30), (connecting_headway_min, 0, 60),
               (fare_usd, 0, 20), (value_of_time_usd_h, 0.1, 50), (response_per_min, 0, .1), (dwell_s, 5, 120))
    if any(type(value) not in (int, float) or not isfinite(value) or not low <= value <= high
           for value, low, high in bounded):
        raise ValueError("Generalised-cost sensitivities fall outside the Airport comparison domain")

    historical = corridor.evaluate({"demand": demand})
    if historical["parent_candidate_id"] != alignment["parent_candidate_id"]:
        raise ValueError("Alignment and demand prior refer to different Airport opening candidates")
    prior = historical["hourly_od"]
    raw = SYSTEM.read_bytes()
    cfg = tomllib.loads(raw.decode())
    vehicle = cfg["vehicle"]
    service_plan = cfg["service_plan"]
    service = dict(headway_min=headway_min, dwell_s=dwell_s, formation_cars=formation_cars,
                   start_hour_local=service_plan["start_hour_local"],
                   service_hours_per_day=vehicle["service_hours_per_day"],
                   terminal_layover_min_each_end=service_plan["terminal_layover_min_each_end"],
                   commercial_speed_kmh=vehicle["commercial_speed_kmh"], speed_cap_kmh=vehicle["speed_cap_kmh"],
                   fare_usd=fare_usd, walk_case=walk, transfer_friction=transfer)
    if transfer:
        service.update(transfer_share_at_interchange_od=transfer_share, transfer_fixed_penalty_min=transfer_penalty_min,
                       connecting_headway_min=connecting_headway_min)
    current_ride = booked_minutes(alignment["chainages_km"], cfg, dwell_s)
    reference_ride = booked_minutes(historical["chainages_km"], cfg, alignment["dwell_s"])
    current = generalised_minutes(current_ride, headway_min, walk, transfer, transfer_share,
                                  transfer_penalty_min, connecting_headway_min, fare_usd, value_of_time_usd_h)
    reference = generalised_minutes(reference_ride, 15, "central", True, .35, 5, 15, 0, 3)
    observed_source = None
    if observed is not None:
        hourly_od, paid_od, observed_source = observed_matrices(observed, alignment, prior, service)
        mode = "observed"
        response = None
    else:
        response = [[exp(-response_per_min * (current[a][b] - reference[a][b])) if a != b else 0.0
                     for b in range(6)] for a in range(6)] if mode == "service_sensitive" else None
        hourly_od = [[[flow * response[a][b] if response is not None else flow for b, flow in enumerate(row)]
                      for a, row in enumerate(matrix)] for matrix in prior]
        paid_fraction = historical["annual_paid_journeys"] / historical["annual_all_journeys"]
        paid_od = [[[flow * paid_fraction for flow in row] for row in matrix] for matrix in hourly_od]

    sources = {**alignment["source_sha256"], **historical["source_sha256"]}
    for path in (SYSTEM, Path(__file__).resolve(), Path(baghdad_diagrams.__file__).resolve()):
        sources[str(path.relative_to(airport_alignment.ROOT))] = sha256(path.read_bytes()).hexdigest()
    if observed_source:
        sources["observed_od_input"] = observed_source["file_sha256"]
    summary = summarize(hourly_od, alignment["chainages_km"], headway_min)
    metres, speed, delay = WALK_CASES[walk]
    total = annual_total(hourly_od)
    result = {
        "schema": SCHEMA, "alignment_id": alignment["alignment_id"], "alignment_record_id": alignment["record_id"],
        "parent_candidate_id": alignment["parent_candidate_id"], "mode": mode, "prior_demand_scenario": demand,
        "stop_ids": list(airport_alignment.STOP_IDS), "hourly_od": hourly_od,
        "annual_paid_journeys": annual_total(paid_od), "annual_all_journeys": total,
        "annual_prior_all_journeys": historical["annual_all_journeys"],
        "mean_trip_km": summary["annual_passenger_km"] / total if total else None,
        "headway_min": headway_min, "headway_wait_min": headway_min / 2, "dwell_s": dwell_s,
        "service_offer": {"departures_per_hour_per_direction": 60 / headway_min,
                          "nonuniform_headway_assessment": None, "booked_ride_minutes": current_ride,
                          "observation_context": service},
        "generalised_cost": {
            "minutes": current, "reference_minutes": reference, "demand_multiplier": response,
            "response_per_min": response_per_min, "waiting_time_weight": 2, "walking_time_weight": 2,
            "fare_usd": fare_usd, "value_of_time_usd_h": value_of_time_usd_h,
            "walk_case": walk, "path_length_each_end_or_transfer_m": metres, "walking_speed_m_s": speed,
            "crossing_or_lift_wait_s_per_path": delay, "transfer_friction": transfer,
            "transfer_share_at_interchange_od": transfer_share, "transfer_fixed_penalty_min": transfer_penalty_min,
            "connecting_headway_min": connecting_headway_min,
            "transfer_interchange_stop_ids": [airport_alignment.STOP_IDS[i] for i in INTERCHANGE_INDICES],
            "scope": "Illustrative access paths and transfer costs. Mode capture, footpaths and transfer shares require local evidence.",
        },
        "observed_source": observed_source, "source_sha256": sources, **summary,
    }
    result["evaluation_id"] = airport_alignment.identity(result)
    return result


def validate(record, alignment):
    airport_alignment.validate(alignment)
    if (record["schema"] != SCHEMA or record["alignment_id"] != alignment["alignment_id"]
            or record["alignment_record_id"] != alignment["record_id"]
            or record["stop_ids"] != list(airport_alignment.STOP_IDS)
            or record["evaluation_id"] != airport_alignment.identity(
                {key: value for key, value in record.items() if key != "evaluation_id"}
            )):
        raise ValueError("Airport demand ID, alignment or stop order does not match")
    if record["mode"] == "observed":
        source = record.get("observed_source")
        context = record["service_offer"].get("observation_context")
        if (not isinstance(source, dict) or not isinstance(context, dict)
                or source.get("service_offer") != context
                or source.get("file_sha256") != record["source_sha256"].get("observed_od_input")
                or context.get("headway_min") != record["headway_min"]
                or context.get("dwell_s") != record["dwell_s"]):
            raise ValueError("Observed OD receipt must retain its matched service offer and source digest")
    return record

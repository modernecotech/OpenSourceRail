"""Source-driven operational digital twin for Samawah Line 1.

The model keeps the full planning alignment and asset/state register in real
engineering units.  FreeCAD uses a declared 1:1000 overview representation so
the complete 25.6 km route remains readable in one review scene.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import math
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TWIN_SCHEMA = "org.opensourcerail.city-line-operational-twin.v1"
LINE_ID = "line-1"
ANIMATED_TRAIN_COUNT = 8
OVERVIEW_SCALE = "1 mm visual = 1 m real (1:1000 horizontal overview)"
OVERVIEW_ROTATION_DEG = 118.0

# Controlled LM3/S5 passenger-interface datums used by presentation renderers.
# Keeping these in the dependency-light twin module prevents the Blender scene
# from drifting away from the engineering rolling-stock model.
LM3_BODY_HEIGHT_M = 3.450
LM3_DOOR_SILL_M = 0.350
LM3_DOOR_HEIGHT_M = 2.000
LM3_WINDOW_SILL_M = 1.500
LM3_WINDOW_HEIGHT_M = 0.900
S5_PLATFORM_HEIGHT_ABOVE_TOR_M = LM3_DOOR_SILL_M


@dataclass(frozen=True)
class AlignmentPoint:
    chainage_m: float
    easting_m: float
    northing_m: float


@dataclass(frozen=True)
class CivilSegment:
    asset_id: str
    start_m: float
    end_m: float
    civil_class: str


@dataclass(frozen=True)
class Station:
    asset_id: str
    name: str
    archetype: str
    chainage_m: float
    platform_length_m: float
    latitude: float
    longitude: float
    charging_power_kw: float
    dwell_seconds: int
    is_terminal: bool
    is_depot: bool


@dataclass(frozen=True)
class EnergySite:
    asset_id: str
    station_id: str
    tier: str
    pv_nameplate_kw: float
    storage_capacity_kwh: float
    charging_power_kw: float


@dataclass(frozen=True)
class FleetPlan:
    peak_count: int
    spare_count: int
    cold_reserve_count: int
    trainset_count: int
    car_count: int
    train_length_m: float
    battery_capacity_kwh: float
    max_speed_kmh: float
    peak_headway_min: int


@dataclass(frozen=True)
class TrainMotion:
    trainset_id: str
    chainage_m: float
    direction: str
    easting_m: float
    northing_m: float
    heading_deg: float
    speed_kmh: float
    soc_percent: float


@dataclass(frozen=True)
class StationStopMotion:
    """One-second-scale motion state for the S5 operations demonstrator."""

    elapsed_s: float
    offset_m: float
    speed_kmh: float
    acceleration_mps2: float
    phase: str
    doors_open: bool


@dataclass(frozen=True)
class SamawahLineTwin:
    city_dir: Path
    line_id: str
    name: str
    length_m: float
    crs: str
    source_status: str
    alignment: tuple[AlignmentPoint, ...]
    civil_segments: tuple[CivilSegment, ...]
    stations: tuple[Station, ...]
    energy_sites: tuple[EnergySite, ...]
    fleet: FleetPlan
    service_windows: tuple[dict[str, Any], ...]
    simulation_summary: dict[str, Any]
    source_files: tuple[Path, ...]


def default_city_dir() -> Path:
    return (
        Path(__file__).resolve().parents[4]
        / "cities/catalogue"
        / "west-asia"
        / "Iraq"
        / "Samawah"
    )


def _read_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_samawah_line_twin(city_dir: Path | None = None) -> SamawahLineTwin:
    """Load Line 1 from its checked-in alignment, design, GIS, and sim data."""

    city_dir = (city_dir or default_city_dir()).resolve()
    alignment_path = city_dir / "engineering/alignment/samawah-line1.aln.toml"
    design_path = city_dir / "design.toml"
    scenario_path = city_dir / "samawah.toml"
    stations_path = city_dir / "samawah.stations.json"
    energy_path = city_dir / "engineering/gis/layers/energy_sites.geojson"
    simulation_path = city_dir / "engineering/simulation/validation-summary.json"

    alignment_data = _read_toml(alignment_path)
    design = _read_toml(design_path)
    scenario = _read_toml(scenario_path)
    station_demand = {item["id"]: item for item in _read_json(stations_path)}
    energy_geojson = _read_json(energy_path)
    simulation = _read_json(simulation_path)

    line_design = next(item for item in design["lines"] if item["name"] == LINE_ID)
    fleet_design = next(item for item in design["fleets"] if item["line"] == LINE_ID)
    scenario_fleet = next(item for item in scenario["fleets"] if item["line"] == LINE_ID)
    scenario_stations = {item["id"]: item for item in scenario["stations"]}
    design_stations = {
        item["id"]: item for item in design["stations"] if item["line"] == LINE_ID
    }

    alignment = tuple(
        AlignmentPoint(
            chainage_m=float(item["station_m"]),
            easting_m=float(item["easting_m"]),
            northing_m=float(item["northing_m"]),
        )
        for item in alignment_data["horizontal"]
    )
    civil_segments = tuple(
        CivilSegment(
            asset_id=f"OSR-SAM-L1-CIV-{index:03d}",
            start_m=float(item["from_station_m"]),
            end_m=float(item["to_station_m"]),
            civil_class=str(item["class"]),
        )
        for index, item in enumerate(alignment_data["civil"], start=1)
    )
    stations: list[Station] = []
    for item in alignment_data["station"]:
        station_id = str(item["id"])
        design_station = design_stations[station_id]
        scenario_station = scenario_stations[station_id]
        demand_station = station_demand[station_id]
        stations.append(
            Station(
                asset_id=station_id,
                name=str(
                    design_station.get("anchor_name")
                    or scenario_station.get("name")
                    or station_id
                ),
                archetype=str(design_station["archetype"]),
                chainage_m=float(item["station_m"]),
                platform_length_m=float(item["platform_length_m"]),
                latitude=float(demand_station["lat"]),
                longitude=float(demand_station["lon"]),
                charging_power_kw=float(
                    scenario_station.get("charging_power_kw", 0.0)
                ),
                dwell_seconds=int(scenario_station.get("dwell_seconds", 60)),
                is_terminal=bool(scenario_station.get("is_terminal", False)),
                is_depot=bool(scenario_station.get("is_depot", False)),
            )
        )

    energy_sites = tuple(
        EnergySite(
            asset_id=f"OSR-SAM-L1-ENERGY-{index:03d}",
            station_id=str(feature["properties"]["station"]),
            tier=str(feature["properties"]["tier"]),
            pv_nameplate_kw=float(feature["properties"]["pv_nameplate_kw"]),
            storage_capacity_kwh=float(
                feature["properties"]["storage_capacity_kwh"]
            ),
            charging_power_kw=float(feature["properties"]["charger_max_kw"]),
        )
        for index, feature in enumerate(
            (
                feature
                for feature in energy_geojson["features"]
                if feature["properties"]["line"] == LINE_ID
            ),
            start=1,
        )
    )

    consist = scenario["consist"]
    fleet = FleetPlan(
        peak_count=int(fleet_design["peak_count"]),
        spare_count=int(fleet_design["spare_count"]),
        cold_reserve_count=int(fleet_design["cold_reserve_count"]),
        trainset_count=int(fleet_design["trainset_count"]),
        car_count=int(consist["car_count"]),
        train_length_m=float(consist["length_m"]),
        battery_capacity_kwh=float(consist["battery_capacity_kwh"]),
        max_speed_kmh=float(consist["max_speed_kmh"]),
        peak_headway_min=min(int(item["headway_min"]) for item in scenario_fleet["schedule"]),
    )
    twin = SamawahLineTwin(
        city_dir=city_dir,
        line_id=LINE_ID,
        name="Samawah Line 1",
        length_m=float(line_design["length_m"]),
        crs=str(alignment_data["meta"]["crs"]),
        source_status=str(alignment_data["meta"]["source_status"]),
        alignment=alignment,
        civil_segments=civil_segments,
        stations=tuple(stations),
        energy_sites=energy_sites,
        fleet=fleet,
        service_windows=tuple(simulation["service_windows"]),
        simulation_summary=simulation,
        source_files=(
            alignment_path,
            design_path,
            scenario_path,
            stations_path,
            energy_path,
            simulation_path,
        ),
    )
    assert_twin_checks(twin)
    return twin


def point_at_chainage(twin: SamawahLineTwin, chainage_m: float) -> tuple[float, float, float]:
    """Return UTM easting, northing, and tangent heading at a chainage."""

    chainage_m = min(max(chainage_m, 0.0), twin.length_m)
    stations = [point.chainage_m for point in twin.alignment]
    right = bisect.bisect_right(stations, chainage_m)
    if right == 0:
        left_index, right_index = 0, 1
    elif right >= len(twin.alignment):
        left_index, right_index = len(twin.alignment) - 2, len(twin.alignment) - 1
    else:
        left_index, right_index = right - 1, right
    left = twin.alignment[left_index]
    target = twin.alignment[right_index]
    span = target.chainage_m - left.chainage_m
    fraction = 0.0 if span <= 0.0 else (chainage_m - left.chainage_m) / span
    easting = left.easting_m + (target.easting_m - left.easting_m) * fraction
    northing = left.northing_m + (target.northing_m - left.northing_m) * fraction
    heading = math.degrees(
        math.atan2(target.northing_m - left.northing_m, target.easting_m - left.easting_m)
    )
    return easting, northing, heading


def representative_train_states(
    twin: SamawahLineTwin,
    progress: float,
    count: int = ANIMATED_TRAIN_COUNT,
) -> tuple[TrainMotion, ...]:
    """Return evenly phased bidirectional train states for an overview frame."""

    if count < 2:
        raise ValueError("at least two representative trains are required")
    progress = progress % 1.0
    motions: list[TrainMotion] = []
    for index in range(count):
        cycle = (progress * 2.0 + index * (2.0 / count)) % 2.0
        forward = cycle <= 1.0
        leg_progress = cycle if forward else 2.0 - cycle
        # Cosine easing makes terminal approaches and reversals legible in the
        # overview without changing the source timetable or engineering state.
        eased_progress = 0.5 - 0.5 * math.cos(math.pi * leg_progress)
        chainage = twin.length_m * eased_progress
        easting, northing, heading = point_at_chainage(twin, chainage)
        direction = "outbound" if forward else "inbound"
        if not forward:
            heading = (heading + 180.0) % 360.0
        nearest_station = min(
            abs(station.chainage_m - chainage) for station in twin.stations
        )
        speed = 55.0 * math.sin(math.pi * leg_progress)
        if nearest_station < 90.0:
            speed = 0.0
        soc = 88.0 - 24.0 * (chainage / twin.length_m)
        if not forward:
            soc = 64.0 + 24.0 * (chainage / twin.length_m)
        motions.append(
            TrainMotion(
                trainset_id=f"OSR-SAM-L1-LM3-{index + 1:03d}",
                chainage_m=chainage,
                direction=direction,
                easting_m=easting,
                northing_m=northing,
                heading_deg=heading,
                speed_kmh=speed,
                soc_percent=soc,
            )
        )
    return tuple(motions)


def station_stop_motion(elapsed_s: float) -> StationStopMotion:
    """Return the physically timed approach, station stop, and departure state.

    The 46-second loop is rendered at one animation second per real second:
    36 km/h approach, 1.0 m/s² service braking, a five-second demonstration
    dwell, then 1.0 m/s² acceleration back to 36 km/h and a departure cruise.
    The shortened dwell keeps the operational sequence readable in a README
    animation; the source timetable dwell remains unchanged in the twin.
    """

    elapsed_s = min(max(float(elapsed_s), 0.0), 46.0)
    if elapsed_s < 10.0:
        return StationStopMotion(
            elapsed_s, -150.0 + 10.0 * elapsed_s, 36.0, 0.0, "APPROACH", False
        )
    if elapsed_s < 20.0:
        braking_s = elapsed_s - 10.0
        speed_mps = 10.0 - braking_s
        return StationStopMotion(
            elapsed_s,
            -50.0 + 10.0 * braking_s - 0.5 * braking_s**2,
            speed_mps * 3.6,
            -1.0,
            "SERVICE BRAKING",
            False,
        )
    if elapsed_s < 25.0:
        return StationStopMotion(elapsed_s, 0.0, 0.0, 0.0, "STATION DWELL", True)
    if elapsed_s < 35.0:
        accelerating_s = elapsed_s - 25.0
        return StationStopMotion(
            elapsed_s,
            0.5 * accelerating_s**2,
            accelerating_s * 3.6,
            1.0,
            "DEPARTING / ACCELERATING",
            False,
        )
    if elapsed_s < 45.0:
        cruise_s = elapsed_s - 35.0
        return StationStopMotion(
            elapsed_s, 50.0 + 10.0 * cruise_s, 36.0, 0.0, "DEPARTURE CRUISE", False
        )
    return StationStopMotion(
        elapsed_s, 175.0, 0.0, 0.0, "SERVICE RESET", False
    )


def twin_checks(twin: SamawahLineTwin) -> tuple[dict[str, Any], ...]:
    civil_contiguous = all(
        math.isclose(left.end_m, right.start_m, abs_tol=0.1)
        for left, right in zip(twin.civil_segments, twin.civil_segments[1:])
    )
    checks = (
        {
            "name": "alignment-chainage-complete",
            "passed": math.isclose(twin.alignment[0].chainage_m, 0.0, abs_tol=0.01)
            and math.isclose(twin.alignment[-1].chainage_m, twin.length_m, abs_tol=0.1),
            "detail": f"{len(twin.alignment)} UTM control points cover {twin.length_m:.1f} m",
        },
        {
            "name": "civil-classification-complete",
            "passed": civil_contiguous
            and math.isclose(twin.civil_segments[0].start_m, 0.0, abs_tol=0.1)
            and math.isclose(twin.civil_segments[-1].end_m, twin.length_m, abs_tol=0.1),
            "detail": f"{len(twin.civil_segments)} contiguous civil segments",
        },
        {
            "name": "all-line-stations-present",
            "passed": len(twin.stations) == 9
            and all(station.platform_length_m >= twin.fleet.train_length_m for station in twin.stations),
            "detail": "nine stations with platforms long enough for the 49.5 m LM3 consist",
        },
        {
            "name": "energy-and-depot-assets-present",
            "passed": len(twin.energy_sites) == 8
            and sum(station.is_depot for station in twin.stations) == 1,
            "detail": "eight charging/PV/storage sites and one main depot terminal",
        },
        {
            "name": "complete-line-fleet-register",
            "passed": twin.fleet.trainset_count == 53
            and twin.fleet.peak_count + twin.fleet.spare_count + twin.fleet.cold_reserve_count
            == twin.fleet.trainset_count,
            "detail": "48 peak-service + 4 spare + 1 cold-reserve LM3 trainsets",
        },
        {
            "name": "city-simulation-evidence-passes",
            "passed": bool(twin.simulation_summary["passed"])
            and all(run["invariant_violations"] == 0 for run in twin.simulation_summary["runs"]),
            "detail": "checked city scenario passed with zero nominal invariant violations",
        },
    )
    return checks


def assert_twin_checks(twin: SamawahLineTwin) -> tuple[dict[str, Any], ...]:
    checks = twin_checks(twin)
    failures = [check for check in checks if not check["passed"]]
    if failures:
        raise ValueError(
            "Samawah Line 1 twin validation failed: "
            + "; ".join(f"{item['name']}: {item['detail']}" for item in failures)
        )
    return checks


def digital_twin_manifest(
    twin: SamawahLineTwin,
    *,
    model_path: Path | None = None,
) -> dict[str, Any]:
    """Create the full line/fleet asset and state register."""

    line_asset_id = "OSR-SAM-L1"
    assets: list[dict[str, Any]] = [
        {
            "asset_id": line_asset_id,
            "asset_class": "railway.line",
            "name": twin.name,
            "state": {"availability": "available", "operating_mode": "peak-service"},
            "engineering": {
                "length_m": twin.length_m,
                "crs": twin.crs,
                "alignment_control_points": len(twin.alignment),
            },
        }
    ]
    relationships: list[dict[str, str]] = []
    assets.append(
        {
            "asset_id": "OSR-SAM-L1-TRACK",
            "asset_class": "track.double-running-line",
            "name": "Samawah Line 1 complete double-track alignment",
            "parent_asset_id": line_asset_id,
            "engineering": {"length_m": twin.length_m, "gauge_mm": 1435},
            "state": {"availability": "available", "health": "nominal"},
        }
    )
    relationships.append(
        {"subject": "OSR-SAM-L1-TRACK", "predicate": "part-of", "object": line_asset_id}
    )

    for civil in twin.civil_segments:
        assets.append(
            {
                "asset_id": civil.asset_id,
                "asset_class": f"civil.{civil.civil_class}",
                "name": f"{civil.civil_class} chainage {civil.start_m:.1f}-{civil.end_m:.1f} m",
                "parent_asset_id": line_asset_id,
                "engineering": {
                    "from_chainage_m": civil.start_m,
                    "to_chainage_m": civil.end_m,
                },
                "state": {"health": "nominal", "lifecycle_state": "planning-reference"},
            }
        )
        relationships.append(
            {"subject": civil.asset_id, "predicate": "part-of", "object": line_asset_id}
        )

    for index, station in enumerate(twin.stations, start=1):
        assets.append(
            {
                "asset_id": station.asset_id,
                "asset_class": f"station.{station.archetype}",
                "name": station.name,
                "parent_asset_id": line_asset_id,
                "engineering": {
                    "chainage_m": station.chainage_m,
                    "platform_length_m": station.platform_length_m,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    "charging_power_kw": station.charging_power_kw,
                    "dwell_seconds": station.dwell_seconds,
                },
                "state": {"availability": "available", "station_number": index},
            }
        )
        relationships.append(
            {"subject": station.asset_id, "predicate": "serves", "object": line_asset_id}
        )

    for energy in twin.energy_sites:
        assets.append(
            {
                "asset_id": energy.asset_id,
                "asset_class": "energy.station-microgrid",
                "name": f"{energy.tier} energy site at {energy.station_id}",
                "parent_asset_id": energy.station_id,
                "engineering": {
                    "pv_nameplate_kw": energy.pv_nameplate_kw,
                    "storage_capacity_kwh": energy.storage_capacity_kwh,
                    "charging_power_kw": energy.charging_power_kw,
                },
                "state": {"availability": "available", "storage_soc_percent": 50.0},
            }
        )
        relationships.append(
            {"subject": energy.asset_id, "predicate": "powers", "object": energy.station_id}
        )

    depot_station = next(station for station in twin.stations if station.is_depot)
    assets.append(
        {
            "asset_id": "OSR-SAM-L1-DEPOT-001",
            "asset_class": "depot.main-heavy",
            "name": "Al-Jaraa Line 1 main-heavy depot",
            "parent_asset_id": depot_station.asset_id,
            "engineering": {"fleet_stalls": 17, "storage_capacity_kwh": 40_000},
            "state": {"availability": "available", "health": "nominal"},
        }
    )
    relationships.append(
        {
            "subject": "OSR-SAM-L1-DEPOT-001",
            "predicate": "located-at",
            "object": depot_station.asset_id,
        }
    )

    for index, (left, right) in enumerate(zip(twin.stations, twin.stations[1:]), start=1):
        for direction in ("outbound", "inbound"):
            block_id = f"OSR-SAM-L1-BLOCK-{index:02d}-{direction.upper()}"
            assets.append(
                {
                    "asset_id": block_id,
                    "asset_class": "signalling.movement-authority-block",
                    "name": f"Block {index} {direction}",
                    "parent_asset_id": line_asset_id,
                    "engineering": {
                        "from_station": left.asset_id,
                        "to_station": right.asset_id,
                        "direction": direction,
                    },
                    "state": {"occupancy": "clear", "interlocking": "available"},
                }
            )
            relationships.append(
                {"subject": block_id, "predicate": "protects", "object": line_asset_id}
            )

    for index in range(1, twin.fleet.trainset_count + 1):
        if index <= twin.fleet.peak_count:
            allocation = "peak-service"
        elif index <= twin.fleet.peak_count + twin.fleet.spare_count:
            allocation = "spare"
        else:
            allocation = "cold-reserve"
        train_id = f"OSR-SAM-L1-LM3-{index:03d}"
        assets.append(
            {
                "asset_id": train_id,
                "asset_class": "rolling-stock.light-metro-3car",
                "name": f"Samawah Line 1 LM3 trainset {index:03d}",
                "parent_asset_id": line_asset_id,
                "engineering": {
                    "car_count": twin.fleet.car_count,
                    "length_m": twin.fleet.train_length_m,
                    "battery_capacity_kwh": twin.fleet.battery_capacity_kwh,
                    "max_speed_kmh": twin.fleet.max_speed_kmh,
                },
                "state": {
                    "allocation": allocation,
                    "health": "nominal",
                    "animated_representative": index <= ANIMATED_TRAIN_COUNT,
                },
            }
        )
        relationships.append(
            {"subject": train_id, "predicate": "allocated-to", "object": line_asset_id}
        )

    model: dict[str, Any] = {
        "format": "FreeCAD FCStd",
        "visual_scale": OVERVIEW_SCALE,
    }
    if model_path is not None:
        model.update(
            {
                "file": model_path.name,
                "size_bytes": model_path.stat().st_size,
                "sha256": _sha256(model_path),
            }
        )
    nominal_run = twin.simulation_summary["runs"][-1]
    return {
        "schema": TWIN_SCHEMA,
        "snapshot": {
            "snapshot_id": "OSR-SAM-L1-PLANNING-REFERENCE-001",
            "kind": "source-linked-planning-and-operational-example",
            "live_telemetry": False,
            "line": twin.line_id,
        },
        "limitations": [
            twin.source_status,
            "The overview geometry is deliberately scaled and symbolically exaggerated; use source UTM and chainage fields for engineering coordinates.",
            "Animated trains are representative deterministic states, not a replay of live telemetry.",
        ],
        "coordinate_system": {
            "engineering_crs": twin.crs,
            "engineering_units": "metres",
            "freecad_overview_scale": OVERVIEW_SCALE,
            "freecad_overview_rotation_deg_ccw": OVERVIEW_ROTATION_DEG,
        },
        "model": model,
        "sources": [
            {
                "file": str(path.relative_to(twin.city_dir)),
                "sha256": _sha256(path),
            }
            for path in twin.source_files
        ],
        "service": {
            "peak_headway_min": twin.fleet.peak_headway_min,
            "fleet_trainsets": twin.fleet.trainset_count,
            "animated_representatives": ANIMATED_TRAIN_COUNT,
            "windows": list(twin.service_windows),
            "validated_nominal": {
                "service_completion_ratio": nominal_run.get("service_completion_ratio"),
                "minimum_soc_percent": nominal_run["minimum_soc_percent"],
                "invariant_violations": nominal_run["invariant_violations"],
            },
        },
        "assets": assets,
        "relationships": relationships,
        "validation": {"checks": list(assert_twin_checks(twin))},
    }


def write_manifest(
    path: Path,
    twin: SamawahLineTwin,
    *,
    model_path: Path | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(digital_twin_manifest(twin, model_path=model_path), indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )

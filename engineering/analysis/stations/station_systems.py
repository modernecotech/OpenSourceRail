#!/usr/bin/env python3
"""Run deterministic multi-domain screening checks for the station family.

The checks in this module are design-reference screens, not authority approval
or construction release.  They deliberately retain the assumptions and the
unresolved deployment inputs beside each result.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sqlite3
import shutil
import subprocess
import tempfile
import tomllib
from importlib.metadata import version
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
DEFAULT_OUTPUT = Path(__file__).with_name("screening-summary.json")
ENERGYPLUS_INPUT = Path(__file__).with_name("inputs") / "energyplus" / "depot-equipment-room.idf"
ENERGYPLUS_MITIGATION_INPUT = (
    Path(__file__).with_name("inputs") / "energyplus" / "depot-cooled-controls-room.idf"
)
FDS_INPUT = Path(__file__).with_name("inputs") / "fds" / "depot-charger-room.fds"
FDS_MITIGATION_INPUT = (
    Path(__file__).with_name("inputs") / "fds" / "depot-open-charger-compound.fds"
)
MITIGATION_WORK_PACKAGES = Path(__file__).with_name("mitigation-work-packages.toml")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def structural_screen() -> dict[str, Any]:
    """Solve a 22 m Warren-truss load path in OpenSees."""

    import openseespy.opensees as ops

    span_m = 22.0
    panel_m = 2.75
    truss_depth_m = 2.0
    upper_nodes = list(range(10, 18))
    areas_m2 = {"chord": 0.0045, "web": 0.0030}
    elastic_modulus_pa = 200.0e9
    yield_pa = 355.0e6
    cases = {
        "gravity": {
            "pressure_kpa": 1.10,
            "total_load_n": -(8.5 * span_m * 1.10 * 1000.0),
        },
        "wind_uplift": {
            "pressure_kpa": 1.20,
            "total_load_n": 8.5 * span_m * 1.20 * 1000.0,
        },
    }
    results: dict[str, Any] = {}
    for case_name, case in cases.items():
        ops.wipe()
        ops.model("basic", "-ndm", 2, "-ndf", 2)
        for index in range(9):
            ops.node(index + 1, index * panel_m, 0.0)
        for index in range(8):
            ops.node(upper_nodes[index], (index + 0.5) * panel_m, truss_depth_m)
        ops.fix(1, 1, 1)
        ops.fix(9, 0, 1)
        ops.uniaxialMaterial("Elastic", 1, elastic_modulus_pa)

        element_areas: dict[int, float] = {}
        tag = 1
        for start in range(1, 9):
            ops.element("truss", tag, start, start + 1, areas_m2["chord"], 1)
            element_areas[tag] = areas_m2["chord"]
            tag += 1
        for start in range(10, 17):
            ops.element("truss", tag, start, start + 1, areas_m2["chord"], 1)
            element_areas[tag] = areas_m2["chord"]
            tag += 1
        for index, upper in enumerate(upper_nodes):
            for lower in (index + 1, index + 2):
                ops.element("truss", tag, lower, upper, areas_m2["web"], 1)
                element_areas[tag] = areas_m2["web"]
                tag += 1

        ops.timeSeries("Linear", 1)
        ops.pattern("Plain", 1, 1)
        node_load_n = float(case["total_load_n"]) / len(upper_nodes)
        for node in upper_nodes:
            ops.load(node, 0.0, node_load_n)
        ops.system("BandSPD")
        ops.numberer("Plain")
        ops.constraints("Plain")
        ops.integrator("LoadControl", 1.0)
        ops.algorithm("Linear")
        ops.analysis("Static")
        return_code = ops.analyze(1)
        max_displacement_m = max(
            math.hypot(float(ops.nodeDisp(node, 1)), float(ops.nodeDisp(node, 2)))
            for node in range(1, 18)
        )
        stresses_pa: list[float] = []
        for element, area_m2 in element_areas.items():
            force = ops.eleResponse(element, "axialForce")
            axial_force_n = float(force[0]) if force else 0.0
            stresses_pa.append(abs(axial_force_n) / area_m2)
        max_stress_pa = max(stresses_pa)
        displacement_limit_m = span_m / 240.0
        allowable_stress_pa = 0.60 * yield_pa
        passed = (
            return_code == 0
            and max_displacement_m <= displacement_limit_m
            and max_stress_pa <= allowable_stress_pa
        )
        results[case_name] = {
            "allowable_stress_mpa": allowable_stress_pa / 1.0e6,
            "converged": return_code == 0,
            "displacement_limit_mm": displacement_limit_m * 1000.0,
            "max_displacement_mm": max_displacement_m * 1000.0,
            "max_axial_stress_mpa": max_stress_pa / 1.0e6,
            "passed": passed,
            "pressure_kpa": case["pressure_kpa"],
            "safety_factor_to_yield": math.inf if max_stress_pa == 0 else yield_pa / max_stress_pa,
            "total_load_kn": abs(float(case["total_load_n"])) / 1000.0,
        }
        ops.wipe()

    return {
        "analysis_id": "OSR-AN-STN-STR-001",
        "applicable_variants": [
            "halt",
            "standard",
            "major",
            "interchange",
            "interchange-elevated",
            "terminal",
            "depot-terminal",
        ],
        "cases": results,
        "model": {
            "description": "simply supported 22 m transverse Warren-truss load path",
            "element_count": 31,
            "material": "S355 design-reference steel; E=200 GPa",
            "node_count": 17,
            "section_areas_mm2": {key: value * 1.0e6 for key, value in areas_m2.items()},
        },
        "passed": all(bool(item["passed"]) for item in results.values()),
        "tool": {"name": "OpenSeesPy", "version": version("openseespy")},
        "limitations": [
            "Global two-dimensional axial load path only; no connection, buckling, fatigue, ponding, seismic, foundation or progressive-collapse check.",
            "Catalogue gravity and uplift pressures are reproducibility assumptions, not site wind/snow/live-load values.",
            "A deployment engineer must replace loads, sections, restraints, corrosion allowance and combinations from local code and surveyed site data.",
        ],
    }


def pedestrian_case(length_m: float, width_m: float, rows: int, columns: int) -> dict[str, Any]:
    import jupedsim as jps

    simulation = jps.Simulation(
        model=jps.CollisionFreeSpeedModel(),
        geometry=[(0.0, 0.0), (length_m, 0.0), (length_m, width_m), (0.0, width_m)],
        dt=0.05,
    )
    exit_id = simulation.add_exit_stage(
        [
            (length_m - 1.0, 0.1),
            (length_m - 0.1, 0.1),
            (length_m - 0.1, width_m - 0.1),
            (length_m - 1.0, width_m - 0.1),
        ]
    )
    journey_id = simulation.add_journey(jps.JourneyDescription([exit_id]))
    for row in range(rows):
        y = width_m / 2.0 if rows == 1 else 0.45 + row * (width_m - 0.9) / (rows - 1)
        for column in range(columns):
            simulation.add_agent(
                jps.CollisionFreeSpeedModelAgentParameters(
                    position=(1.0 + column * 0.55, y),
                    journey_id=journey_id,
                    stage_id=exit_id,
                    desired_speed=1.2,
                    radius=0.2,
                )
            )
    initial_agents = simulation.agent_count()
    while simulation.agent_count() and simulation.elapsed_time() < 180.0:
        simulation.iterate()
    return {
        "clear": simulation.agent_count() == 0,
        "clearance_time_s": simulation.elapsed_time(),
        "initial_agents_per_route": initial_agents,
        "iterations": simulation.iteration_count(),
        "remaining_agents": simulation.agent_count(),
        "route_length_m": length_m,
        "route_width_m": width_m,
    }


def passenger_screen(variants: list[dict[str, Any]]) -> dict[str, Any]:
    scenarios = {
        "normal": {"width_m": 6.0, "rows": 8, "columns": 10, "limit_s": 90.0},
        "degraded": {"width_m": 2.4, "rows": 4, "columns": 20, "limit_s": 120.0},
        "egress": {"width_m": 6.0, "rows": 10, "columns": 12, "limit_s": 150.0},
    }
    route_cache: dict[tuple[float, str], dict[str, Any]] = {}
    results: dict[str, Any] = {}
    for variant in variants:
        archetype = str(variant["archetype"])
        parameters = variant["parameters"]
        length_m = float(parameters["platform_length_m"])
        route_count = int(parameters["platform_count"])
        case_results: dict[str, Any] = {}
        for name, settings in scenarios.items():
            key = (length_m, name)
            if key not in route_cache:
                route_cache[key] = pedestrian_case(
                    length_m,
                    float(settings["width_m"]),
                    int(settings["rows"]),
                    int(settings["columns"]),
                )
            result = dict(route_cache[key])
            result["acceptance_limit_s"] = settings["limit_s"]
            result["passed"] = bool(result["clear"] and result["clearance_time_s"] <= settings["limit_s"])
            result["parallel_route_count"] = route_count
            case_results[name] = result
        results[archetype] = {
            "passed": all(bool(item["passed"]) for item in case_results.values()),
            "scenarios": case_results,
        }
    return {
        "analysis_id": "OSR-AN-STN-PED-002",
        "passed": all(bool(item["passed"]) for item in results.values()),
        "tool": {"name": "JuPedSim", "version": version("jupedsim")},
        "variants": results,
        "limitations": [
            "Each platform route is screened independently; transfer conflicts, stairs, lifts, gates, trains and road crossings are not represented.",
            "The 80-agent operating cases and 120-agent egress case are deterministic test populations, not city demand or authority design populations.",
            "Local accessibility, evacuation, walking-speed distribution and assisted-evacuation criteria require deployment calibration and approval.",
        ],
    }


def swmm_input(archetype: str, area_m2: float) -> str:
    area_ha = area_m2 / 10_000.0
    width_m = max(10.0, math.sqrt(area_m2))
    return f"""[TITLE]
OpenSourceRail {archetype} station roof-drainage screen

[OPTIONS]
FLOW_UNITS           LPS
INFILTRATION         HORTON
FLOW_ROUTING         KINWAVE
START_DATE           01/01/2020
START_TIME           00:00:00
REPORT_START_DATE    01/01/2020
REPORT_START_TIME    00:00:00
END_DATE             01/01/2020
END_TIME             01:00:00
WET_STEP             00:01:00
DRY_STEP             00:05:00
ROUTING_STEP         00:00:10
REPORT_STEP          00:01:00
ALLOW_PONDING        NO

[EVAPORATION]
CONSTANT             0.0

[RAINGAGES]
Gage1 INTENSITY 0:05 1.0 TIMESERIES Storm

[SUBCATCHMENTS]
Roof Gage1 Inlet {area_ha:.6f} {width_m:.3f} 1.0 100 0

[SUBAREAS]
Roof 0.01 0.10 0.00 0.00 0 OUTLET

[INFILTRATION]
Roof 75 10 4 7 0

[JUNCTIONS]
Inlet 0 1.0 0 0 0

[OUTFALLS]
Outfall 0 FREE NO

[CONDUITS]
Drain Inlet Outfall 40 0.013 0 0 0 0

[XSECTIONS]
Drain CIRCULAR 0.300 0 0 0 1

[TIMESERIES]
Storm 01/01/2020 00:00 0
Storm 01/01/2020 00:05 75
Storm 01/01/2020 00:25 75
Storm 01/01/2020 00:30 0

[REPORT]
INPUT NO
CONTROLS NO
SUBCATCHMENTS ALL
NODES ALL
LINKS ALL

[COORDINATES]
Inlet 0 0
Outfall 40 0

[POLYGONS]
Roof -10 -10
Roof 10 -10
Roof 10 10
Roof -10 10
"""


def drainage_screen(variants: list[dict[str, Any]], input_root: Path) -> dict[str, Any]:
    from pyswmm import Links, Nodes, Simulation

    results: dict[str, Any] = {}
    input_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osr-station-swmm-") as temporary:
        run_root = Path(temporary)
        for variant in variants:
            archetype = str(variant["archetype"])
            parameters = variant["parameters"]
            area_m2 = float(parameters["platform_canopy_area_m2"]) + float(
                parameters["auxiliary_canopy_installed_area_m2"]
            )
            outlet_count = int(parameters["total_canopy_bays"]) + int(
                parameters["auxiliary_canopy_module_count"]
            )
            branch_area_m2 = area_m2 / outlet_count
            source_path = input_root / f"{archetype}.inp"
            source_path.write_text(swmm_input(archetype, branch_area_m2), encoding="utf-8")
            run_path = run_root / source_path.name
            shutil.copy2(source_path, run_path)
            peak_flow_lps = 0.0
            peak_depth_m = 0.0
            with Simulation(str(run_path)) as simulation:
                link = Links(simulation)["Drain"]
                node = Nodes(simulation)["Inlet"]
                step_count = 0
                for _ in simulation:
                    step_count += 1
                    peak_flow_lps = max(peak_flow_lps, float(link.flow))
                    peak_depth_m = max(peak_depth_m, float(node.depth))
                runoff_error = float(simulation.runoff_error)
                routing_error = float(simulation.flow_routing_error)
            rational_peak_lps = 0.95 * 75.0 * area_m2 / 3600.0
            passed = (
                step_count > 0
                and abs(runoff_error) <= 1.0
                and abs(routing_error) <= 1.0
                and peak_depth_m < 0.80
            )
            results[archetype] = {
                "canopy_catchment_area_m2": area_m2,
                "design_branch_area_m2": branch_area_m2,
                "drainage_outlet_count": outlet_count,
                "continuity": {
                    "routing_error_percent": routing_error,
                    "runoff_error_percent": runoff_error,
                },
                "input_path": str(source_path.relative_to(REPO_ROOT)),
                "input_sha256": sha256(source_path),
                "peak_conduit_flow_lps": peak_flow_lps,
                "station_aggregate_peak_flow_lps": peak_flow_lps * outlet_count,
                "peak_inlet_depth_m": peak_depth_m,
                "rational_method_peak_lps": rational_peak_lps,
                "passed": passed,
                "step_count": step_count,
            }
    return {
        "analysis_id": "OSR-AN-STN-DRA-001",
        "passed": all(bool(item["passed"]) for item in results.values()),
        "storm": {"duration_minutes": 20, "intensity_mm_per_hour": 75.0},
        "tool": {"name": "EPA SWMM via PySWMM", "version": version("pyswmm")},
        "variants": results,
        "limitations": [
            "One representative 300 mm gravity branch per platform/auxiliary roof bay with ideal free outfall; no header/manifold, surveyed levels, tailwater, blockage, climate factor, overland exceedance or municipal network.",
            "The 75 mm/h storm is a reproducibility assumption and must be replaced with local IDF rainfall and authority return period.",
            "Platform, track, depot yard, pollutants, oil interception and groundwater are outside this roof-catchment screen.",
        ],
    }


def energyplus_input(*, cooled_controls_room: bool = False) -> str:
    """Return the baseline or separated/cooled depot electrical-room model."""

    equipment_name = "Controls and switchgear losses" if cooled_controls_room else "Charger losses"
    equipment_heat_w = 10_000 if cooled_controls_room else 40_000
    ventilation = (
        ""
        if cooled_controls_room
        else "ZoneVentilation:DesignFlowRate,Equipment room ventilation,Equipment Room,Always On,Flow/Zone,4.0,,,,Exhaust,200.0,0.70,1.0,0.0,0.0,0.0;\n"
    )
    cooling = (
        """Sizing:Parameters,1.15,1.15;
HVACTemplate:Thermostat,Equipment Room Thermostat,,,,35.0;
HVACTemplate:Zone:IdealLoadsAirSystem,Equipment Room,Equipment Room Thermostat,Always On,50,13,0.0156,0.0077,NoLimit,,,LimitCapacity,,30000,,Always On,ConstantSensibleHeatRatio,0.7,,None,30,None,,,,,None,NoEconomizer,None,0.7,0.65;
Output:Variable,*,Zone Ideal Loads Supply Air Total Cooling Rate,Hourly;
"""
        if cooled_controls_room
        else ""
    )
    return f"""Version,26.1;
SimulationControl,No,No,No,Yes,No;
Building,OSR Depot Equipment Room,0.0,Suburbs,0.04,0.4,FullExterior,25,6;
Timestep,4;
Site:Location,OSR Hot-Dry Screening Location,33.3,44.4,3.0,35.0;
Site:GroundTemperature:BuildingSurface,25,25,25,25,25,25,25,25,25,25,25,25;
SizingPeriod:DesignDay,Hot dry design day,07,21,SummerDesignDay,45.0,10.0,DefaultMultipliers,,Wetbulb,24.0,,,,,101325,3.0,270,No,No,No,ASHRAEClearSky,,,,,1.0;
RunPeriod,Design day only,1,1,,1,1,,Tuesday,Yes,Yes,No,Yes,Yes;
GlobalGeometryRules,UpperLeftCorner,CounterClockWise,World;
Material,Concrete,MediumRough,0.20,1.40,2200,900,0.90,0.70,0.70;
Construction,Depot construction,Concrete;
Zone,Equipment Room,0,0,0,0,1,1,3.0,80.0;
BuildingSurface:Detailed,Floor,Floor,Depot construction,Equipment Room,,Ground,,NoSun,NoWind,1.0,4,0,8,0,10,8,0,10,0,0,0,0,0;
BuildingSurface:Detailed,Roof,Roof,Depot construction,Equipment Room,,Outdoors,,SunExposed,WindExposed,0.0,4,0,0,3,10,0,3,10,8,3,0,8,3;
BuildingSurface:Detailed,North Wall,Wall,Depot construction,Equipment Room,,Outdoors,,SunExposed,WindExposed,0.5,4,0,0,3,10,0,3,10,0,0,0,0,0;
BuildingSurface:Detailed,East Wall,Wall,Depot construction,Equipment Room,,Outdoors,,SunExposed,WindExposed,0.5,4,10,0,3,10,8,3,10,8,0,10,0,0;
BuildingSurface:Detailed,South Wall,Wall,Depot construction,Equipment Room,,Outdoors,,SunExposed,WindExposed,0.5,4,10,8,3,0,8,3,0,8,0,10,8,0;
BuildingSurface:Detailed,West Wall,Wall,Depot construction,Equipment Room,,Outdoors,,SunExposed,WindExposed,0.5,4,0,8,3,0,0,3,0,0,0,0,8,0;
ScheduleTypeLimits,Fraction,0,1,Continuous;
Schedule:Constant,Always On,Fraction,1.0;
ElectricEquipment,{equipment_name},Equipment Room,Always On,EquipmentLevel,{equipment_heat_w},,,,0.0,0.0,0.0;
{ventilation}{cooling}Output:Variable,Equipment Room,Zone Mean Air Temperature,Hourly;
Output:SQLite,SimpleAndTabular;
"""


def fds_input(*, open_sided_compound: bool = False) -> str:
    chid = "osr_depot_open_charger_compound" if open_sided_compound else "osr_depot_charger_room"
    title = (
        "OSR separated open-sided charger-compound screening scenario"
        if open_sided_compound
        else "OSR enclosed depot charger-room screening scenario"
    )
    openings = (
        """&VENT ID='OPEN_X_MIN', XB=0.0,0.0,0.0,4.0,0.0,3.0, SURF_ID='OPEN' /
&VENT ID='OPEN_X_MAX', XB=5.0,5.0,0.0,4.0,0.0,3.0, SURF_ID='OPEN' /
&VENT ID='OPEN_Y_MIN', XB=0.0,5.0,0.0,0.0,0.0,3.0, SURF_ID='OPEN' /
&VENT ID='OPEN_Y_MAX', XB=0.0,5.0,4.0,4.0,0.0,3.0, SURF_ID='OPEN' /
"""
        if open_sided_compound
        else "&VENT ID='DOOR', XB=0.0,0.0,1.5,2.5,0.0,2.2, SURF_ID='OPEN' /\n"
    )
    return f"""&HEAD CHID='{chid}', TITLE='{title}' /
&TIME T_END=60.0 /
&DUMP DT_DEVC=1.0, NFRAMES=20 /
&MESH IJK=30,24,18, XB=0.0,5.0,0.0,4.0,0.0,3.0 /
&REAC FUEL='PROPANE', SOOT_YIELD=0.10, CO_YIELD=0.02 /
&RAMP ID='FIRE_RAMP', T=0.0, F=0.0 /
&RAMP ID='FIRE_RAMP', T=10.0, F=1.0 /
&SURF ID='CHARGER_FIRE', HRRPUA=250.0, RAMP_Q='FIRE_RAMP', COLOR='RED' /
&OBST ID='CHARGER', XB=2.0,3.0,1.5,2.5,0.0,1.8 /
&VENT ID='FIRE', XB=2.0,3.0,1.5,2.5,1.8,1.8, SURF_ID='CHARGER_FIRE' /
{openings}&DEVC ID='ROOM_TEMP', XYZ=4.0,2.0,2.0, QUANTITY='TEMPERATURE' /
&DEVC ID='DOOR_VIS', XYZ=0.5,2.0,1.8, QUANTITY='VISIBILITY' /
&TAIL /
"""


def _energyplus_case(
    binary: str, input_path: Path, output: Path, trace_path: Path, limit_c: float
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [binary, "-x", "-D", "-d", str(output), str(input_path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    end_file = output / "eplusout.end"
    successful = bool(
        completed.returncode == 0
        and end_file.is_file()
        and "Completed Successfully" in end_file.read_text(errors="replace")
    )
    maximum_temperature_c: float | None = None
    maximum_cooling_kw: float | None = None
    if successful:
        database = sqlite3.connect(output / "eplusout.sql")
        try:
            maximum_temperature = database.execute(
                "SELECT MAX(d.VariableValue) FROM ReportVariableData d "
                "JOIN ReportVariableDataDictionary dd USING (ReportVariableDataDictionaryIndex) "
                "WHERE dd.VariableName = 'Zone Mean Air Temperature'"
            ).fetchone()
            maximum_temperature_c = (
                float(maximum_temperature[0])
                if maximum_temperature and maximum_temperature[0] is not None
                else None
            )
            maximum_cooling = database.execute(
                "SELECT MAX(d.VariableValue) FROM ReportVariableData d "
                "JOIN ReportVariableDataDictionary dd USING (ReportVariableDataDictionaryIndex) "
                "WHERE dd.VariableName = 'Zone Ideal Loads Supply Air Total Cooling Rate'"
            ).fetchone()
            maximum_cooling_kw = (
                float(maximum_cooling[0]) / 1000.0
                if maximum_cooling and maximum_cooling[0] is not None
                else None
            )
            trace_rows = database.execute(
                "SELECT t.Month, t.Day, t.Hour, d.VariableValue "
                "FROM ReportVariableData d "
                "JOIN ReportVariableDataDictionary dd USING (ReportVariableDataDictionaryIndex) "
                "JOIN Time t USING (TimeIndex) "
                "WHERE dd.VariableName = 'Zone Mean Air Temperature' "
                "ORDER BY d.TimeIndex"
            ).fetchall()
        finally:
            database.close()
        with trace_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["month", "day", "hour", "zone_mean_air_temperature_c"])
            writer.writerows(
                (month, day, hour, f"{float(temperature):.6f}")
                for month, day, hour, temperature in trace_rows
            )
    passed = bool(successful and maximum_temperature_c is not None and maximum_temperature_c <= limit_c)
    result: dict[str, Any] = {
        "input_path": str(input_path.relative_to(REPO_ROOT)),
        "input_sha256": sha256(input_path),
        "max_zone_air_temperature_c": maximum_temperature_c,
        "max_ideal_cooling_load_kw": maximum_cooling_kw,
        "passed": passed,
        "return_code": completed.returncode,
        "solver_completed": successful,
        "status": "solver-completed-pass" if passed else "solver-completed-finding" if successful else "solver-failed",
    }
    if successful:
        result["result_trace_path"] = str(trace_path.relative_to(REPO_ROOT))
        result["result_trace_sha256"] = sha256(trace_path)
    return result


def _fds_case(
    binary: str, input_path: Path, output: Path, trace_prefix: Path, chid: str
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [binary, str(input_path)],
        cwd=output,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    successful = completed.returncode == 0 and "completed successfully" in completed.stdout.lower()
    max_temperature_c: float | None = None
    min_visibility_m: float | None = None
    max_hrr_kw: float | None = None
    trace_paths: list[str] = []
    trace_hashes: dict[str, str] = {}
    if successful:
        device_path = output / f"{chid}_devc.csv"
        hrr_path = output / f"{chid}_hrr.csv"
        with device_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(list(handle)[1:]))
        with hrr_path.open(newline="", encoding="utf-8") as handle:
            hrr_rows = list(csv.DictReader(list(handle)[1:]))
        max_temperature_c = max(float(row["ROOM_TEMP"]) for row in rows)
        min_visibility_m = min(float(row["DOOR_VIS"]) for row in rows)
        max_hrr_kw = max(float(row["HRR"]) for row in hrr_rows)
        for source, suffix in ((device_path, "device-trace.csv"), (hrr_path, "hrr-trace.csv")):
            target = trace_prefix.with_name(f"{trace_prefix.name}-{suffix}")
            shutil.copy2(source, target)
            trace_paths.append(str(target.relative_to(REPO_ROOT)))
            trace_hashes[target.name] = sha256(target)
    passed = bool(
        successful
        and max_temperature_c is not None
        and max_temperature_c <= 60.0
        and min_visibility_m is not None
        and min_visibility_m >= 10.0
    )
    return {
        "input_path": str(input_path.relative_to(REPO_ROOT)),
        "input_sha256": sha256(input_path),
        "max_heat_release_rate_kw": max_hrr_kw,
        "max_room_device_temperature_c": max_temperature_c,
        "min_door_visibility_m": min_visibility_m,
        "passed": passed,
        "return_code": completed.returncode,
        "result_trace_paths": trace_paths,
        "result_trace_sha256": trace_hashes,
        "solver_completed": successful,
        "status": "solver-completed-pass" if passed else "solver-completed-finding" if successful else "solver-failed",
    }


def optional_solver_inputs(input_root: Path, run_root: Path) -> dict[str, Any]:
    energy_paths = {
        "baseline_ventilation_only": input_root / "energyplus" / ENERGYPLUS_INPUT.name,
        "proposed_separated_cooled_controls": input_root / "energyplus" / ENERGYPLUS_MITIGATION_INPUT.name,
    }
    fds_paths = {
        "baseline_enclosed_room": input_root / "fds" / FDS_INPUT.name,
        "proposed_separated_open_compound": input_root / "fds" / FDS_MITIGATION_INPUT.name,
    }
    for path in (*energy_paths.values(), *fds_paths.values()):
        path.parent.mkdir(parents=True, exist_ok=True)
    energy_paths["baseline_ventilation_only"].write_text(energyplus_input(), encoding="utf-8")
    energy_paths["proposed_separated_cooled_controls"].write_text(
        energyplus_input(cooled_controls_room=True), encoding="utf-8"
    )
    fds_paths["baseline_enclosed_room"].write_text(fds_input(), encoding="utf-8")
    fds_paths["proposed_separated_open_compound"].write_text(
        fds_input(open_sided_compound=True), encoding="utf-8"
    )
    results_root = Path(__file__).with_name("results")
    results_root.mkdir(parents=True, exist_ok=True)

    heat_rejection_kw = 500.0 * (1.0 - 0.94) + 10.0
    airflow_m3_s = heat_rejection_kw * 1000.0 / (1.2 * 1005.0 * 10.0)
    energy_binary = shutil.which("energyplus")
    fds_binary = shutil.which("fds")
    energy_cases: dict[str, Any] = {}
    fire_cases: dict[str, Any] = {}
    if energy_binary:
        for case_name, input_path in energy_paths.items():
            energy_cases[case_name] = _energyplus_case(
                energy_binary,
                input_path,
                run_root / "energyplus" / case_name,
                results_root / f"energyplus-{case_name}-zone-temperature.csv",
                40.0,
            )
    if fds_binary:
        for case_name, input_path in fds_paths.items():
            chid = (
                "osr_depot_charger_room"
                if case_name == "baseline_enclosed_room"
                else "osr_depot_open_charger_compound"
            )
            fire_cases[case_name] = _fds_case(
                fds_binary,
                input_path,
                run_root / "fds" / case_name,
                results_root / f"fds-{case_name}",
                chid,
            )
    energy_proposed_passed = bool(
        energy_cases.get("proposed_separated_cooled_controls", {}).get("passed")
    )
    fire_proposed_passed = bool(
        fire_cases.get("proposed_separated_open_compound", {}).get("passed")
    )
    energy_result: dict[str, Any] = {
        "analysis_id": "OSR-AN-STN-THM-001",
        "cases": energy_cases,
        "input_paths": [str(path.relative_to(REPO_ROOT)) for path in energy_paths.values()],
        "preliminary_heat_rejection_kw": heat_rejection_kw,
        "preliminary_outdoor_airflow_m3_s": airflow_m3_s,
        "proposed_installed_cooling": "2 x 30 kW packaged DX (one duty, one standby); EnergyPlus screen caps available capacity at 30 kW",
        "screening_limit_max_zone_air_temperature_c": 40.0,
        "screening_passed": energy_proposed_passed,
        "passed": energy_proposed_passed,
        "solver": "EnergyPlus",
        "solver_available": energy_binary is not None,
        "solver_completed": bool(energy_cases) and all(case["solver_completed"] for case in energy_cases.values()),
        "status": "mitigation-screen-pass" if energy_proposed_passed else "input-prepared" if not energy_binary else "mitigation-screen-finding",
        "limitations": "Both one-zone cases are uncalibrated pre-sizing screens. Supplier loss/duty maps, project weather/envelope, refrigerant and condensate design, controls, equipment limits, redundancy proof and commissioning remain deployment gates.",
    }
    fire_result: dict[str, Any] = {
        "analysis_id": "OSR-AN-STN-FIR-001",
        "cases": fire_cases,
        "input_paths": [str(path.relative_to(REPO_ROOT)) for path in fds_paths.values()],
        "scenario": "250 kW prescribed fire compared in an enclosed room and a physically separated open-sided compound; not a battery thermal-runaway model",
        "screening_limits": {"door_visibility_min_m": 10.0, "room_temperature_max_c": 60.0},
        "screening_passed": fire_proposed_passed,
        "passed": fire_proposed_passed,
        "solver": "FDS",
        "solver_available": fds_binary is not None,
        "solver_completed": bool(fire_cases) and all(case["solver_completed"] for case in fire_cases.values()),
        "status": "mitigation-screen-pass" if fire_proposed_passed else "input-prepared" if not fds_binary else "mitigation-screen-finding",
        "limitations": "Coarse prescribed-burner comparison only. Separation distance, credible supplier heat-release/propagation data, wind cases, chemistry, detection, isolation, drainage/containment, suppression, emergency response and fire-engineer acceptance remain deployment gates.",
    }
    return {"energyplus": energy_result, "fds": fire_result}


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Station systems screening",
        "",
        "Deterministic design-reference checks for all seven station variants. These are",
        "reproducible engineering screens, not construction release or authority approval.",
        "",
        f"- Screening execution: **{'passed' if report['screening_execution_passed'] else 'failed'}**",
        f"- Deployment release: **{'ready' if report['deployment_release_ready'] else 'not ready'}**",
        f"- Manifest: `{report['canonical_input']}` (`{report['manifest_sha256'][:12]}…`)",
        "",
        "## Results",
        "",
        "| Domain | Engine | Scope | Result | Remaining gate |",
        "|---|---|---|---|---|",
    ]
    structural = report["structural"]
    passenger = report["passenger"]
    drainage = report["drainage"]
    optional = report["optional_solver_inputs"]
    lines.extend(
        [
            f"| Structure | {structural['tool']['name']} {structural['tool']['version']} | 22 m shared canopy truss, gravity + uplift | {'PASS' if structural['passed'] else 'FAIL'} | Site loads, 3D stability, joints, foundations and code combinations |",
            f"| Passenger flow | {passenger['tool']['name']} {passenger['tool']['version']} | normal, degraded and egress route for 7 variants | {'PASS' if passenger['passed'] else 'FAIL'} | Calibrated demand, conflicts, assisted evacuation and authority criteria |",
            f"| Roof drainage | {drainage['tool']['name']} {drainage['tool']['version']} | 7 canopy catchments, 75 mm/h input storm | {'PASS' if drainage['passed'] else 'FAIL'} | Local rainfall, survey, tailwater, blockage and exceedance |",
            f"| Depot thermal | EnergyPlus | baseline room + separated/cooled controls-room comparison | {optional['energyplus']['status']} | Project climate, supplier losses, detailed HVAC, controls and commissioning |",
            f"| Depot fire | FDS | enclosed room + separated/open compound comparison at prescribed 250 kW | {optional['fds']['status']} | Supplier fire data, separation/wind cases, suppression and fire-engineer acceptance |",
        ]
    )
    lines.extend(["", "## Structural cases", "", "| Case | Load kN | Displacement / limit mm | Stress / allowable MPa | Result |", "|---|---:|---:|---:|---|"])
    for name, result in structural["cases"].items():
        lines.append(
            f"| `{name}` | {result['total_load_kn']:.1f} | {result['max_displacement_mm']:.2f} / {result['displacement_limit_mm']:.2f} | {result['max_axial_stress_mpa']:.1f} / {result['allowable_stress_mpa']:.1f} | {'PASS' if result['passed'] else 'FAIL'} |"
        )
    lines.extend(["", "## Passenger-flow cases", "", "| Variant | Normal s | Degraded s | Egress s | Result |", "|---|---:|---:|---:|---|"])
    for archetype, result in passenger["variants"].items():
        scenarios = result["scenarios"]
        lines.append(
            f"| `{archetype}` | {scenarios['normal']['clearance_time_s']:.2f} | {scenarios['degraded']['clearance_time_s']:.2f} | {scenarios['egress']['clearance_time_s']:.2f} | {'PASS' if result['passed'] else 'FAIL'} |"
        )
    lines.extend(["", "## Drainage cases", "", "| Variant | Catchment / branches | SWMM branch / aggregate L/s | Rational aggregate L/s | Inlet depth m | Result |", "|---|---:|---:|---:|---:|---|"])
    for archetype, result in drainage["variants"].items():
        lines.append(
            f"| `{archetype}` | {result['canopy_catchment_area_m2']:.1f} m² / {result['drainage_outlet_count']} | {result['peak_conduit_flow_lps']:.2f} / {result['station_aggregate_peak_flow_lps']:.2f} | {result['rational_method_peak_lps']:.2f} | {result['peak_inlet_depth_m']:.3f} | {'PASS' if result['passed'] else 'FAIL'} |"
        )
    if optional["energyplus"].get("solver_completed") or optional["fds"].get("solver_completed"):
        lines.extend(["", "## Depot thermal and fire design response", ""])
        energy = optional["energyplus"]
        fire = optional["fds"]
        if energy.get("solver_completed"):
            baseline = energy["cases"]["baseline_ventilation_only"]
            proposed = energy["cases"]["proposed_separated_cooled_controls"]
            lines.append(
                f"- EnergyPlus baseline: **{baseline['max_zone_air_temperature_c']:.1f} °C** (FAIL) with charger losses indoors and ventilation only. Proposed response: move charger power stages outdoors, retain a 10 kW controls/switchgear load in a cooled room, and install 2 × 30 kW packaged DX units (one duty, one standby). The one-unit-available screen reaches **{proposed['max_zone_air_temperature_c']:.1f} °C**, draws at most **{proposed['max_ideal_cooling_load_kw']:.1f} kW** and {'passes' if proposed['passed'] else 'does not pass'} the {energy['screening_limit_max_zone_air_temperature_c']:.0f} °C screen."
            )
        if fire.get("solver_completed"):
            baseline = fire["cases"]["baseline_enclosed_room"]
            proposed = fire["cases"]["proposed_separated_open_compound"]
            lines.append(
                f"- FDS enclosed-room baseline: **{baseline['max_room_device_temperature_c']:.1f} °C / {baseline['min_door_visibility_m']:.1f} m visibility** (FAIL). In the proposed physically separated, open-sided charging compound, the same prescribed ~{proposed['max_heat_release_rate_kw']:.0f} kW source gives **{proposed['max_room_device_temperature_c']:.1f} °C / {proposed['min_door_visibility_m']:.1f} m** at the screening devices and {'passes' if proposed['passed'] else 'does not pass'} the provisional 60 °C / 10 m comparison. This is a layout screen, not a fire strategy or battery propagation approval."
            )
    lines.extend(
        [
            "",
            "## Release boundary",
            "",
            "A passing row means only that the deterministic catalogue assumption completed",
            "and met its stated screening threshold. Before procurement or construction, the",
            "deployment team must substitute surveyed/site inputs, local statutory criteria,",
            "supplier performance data, detailed connections and independent competent review.",
            "EnergyPlus/FDS solver completion and a mitigation screen pass confirm only",
            "input execution and the direction of the catalogue design response. The baseline",
            "findings, supplier evidence, project-specific design and independent approvals",
            "remain open release gates.",
            "",
        ]
    )
    return "\n".join(lines)


def render_work_packages(register: dict[str, Any]) -> str:
    lines = [
        "# Depot thermal and fire mitigation work packages",
        "",
        "Generated from [`mitigation-work-packages.toml`](mitigation-work-packages.toml),",
        "which is the canonical owner/evidence/closure register.",
        "",
        f"**Design response:** {register['design_response']}",
        "",
        f"> {register['release_boundary']}",
        "",
        "| ID | Package | Owner role | Related products | State |",
        "|---|---|---|---|---|",
    ]
    for package in register["work_package"]:
        products = ", ".join(f"`{item}`" for item in package["related_product_ids"])
        lines.append(
            f"| `{package['id']}` | {package['title']} | {package['owner_role']} | "
            f"{products} | `{package['closure_state']}` |"
        )
    lines.extend(["", "## Evidence required", ""])
    for package in register["work_package"]:
        lines.extend([f"### `{package['id']}` — {package['title']}", ""])
        lines.extend(f"- {item}" for item in package["evidence_required"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--input-root", type=Path, default=Path(__file__).with_name("inputs"))
    parser.add_argument("--run-root", type=Path, default=REPO_ROOT / "build/engineering/analysis/stations")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    variants = list(manifest["variants"])
    structural = structural_screen()
    passenger = passenger_screen(variants)
    drainage = drainage_screen(variants, args.input_root / "swmm")
    optional = optional_solver_inputs(args.input_root, args.run_root)
    report = {
        "analysis_family": "OSR-AN-STN-SYS-001",
        "canonical_input": str(MANIFEST.relative_to(REPO_ROOT)),
        "deployment_release_ready": False,
        "drainage": drainage,
        "generator_sha256": sha256(Path(__file__)),
        "manifest_sha256": sha256(MANIFEST),
        "optional_solver_inputs": optional,
        "passenger": passenger,
        "schema_version": 1,
        "screening_execution_passed": bool(structural["passed"] and passenger["passed"] and drainage["passed"]),
        "structural": structural,
        "variant_count": len(variants),
    }
    atomic_json(args.output, report)
    markdown_path = args.output.with_suffix(".md")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    work_package_markdown = MITIGATION_WORK_PACKAGES.with_suffix(".md")
    work_package_markdown.write_text(
        render_work_packages(tomllib.loads(MITIGATION_WORK_PACKAGES.read_text(encoding="utf-8"))),
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    print(f"wrote {markdown_path}")
    print(f"wrote {work_package_markdown}")
    return 0 if report["screening_execution_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

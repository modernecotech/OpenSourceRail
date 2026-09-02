#!/usr/bin/env python3
"""Run deterministic multi-domain screening checks for the station family.

The checks in this module are design-reference screens, not authority approval
or construction release.  They deliberately retain the assumptions and the
unresolved deployment inputs beside each result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
DEFAULT_OUTPUT = Path(__file__).with_name("screening-summary.json")
ENERGYPLUS_INPUT = Path(__file__).with_name("inputs") / "energyplus" / "depot-equipment-room.idf"
FDS_INPUT = Path(__file__).with_name("inputs") / "fds" / "depot-charger-room.fds"


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


def energyplus_input() -> str:
    """Return a compact design-day model for the depot electrical room."""

    return """Version,26.1;
SimulationControl,No,No,No,Yes,No;
Building,OSR Depot Equipment Room,0.0,Suburbs,0.04,0.4,FullExterior,25,6;
Timestep,4;
SizingPeriod:DesignDay,Hot dry design day,07,21,SummerDesignDay,45.0,10.0,DefaultMultipliers,,Wetbulb,24.0,,,,,101325,3.0,270,No,No,No,ASHRAEClearSky,,,,1.0;
RunPeriod,Design day only,1,1,,1,1,,Tuesday,Yes,Yes,No,Yes,Yes;
GlobalGeometryRules,UpperLeftCorner,CounterClockWise,World;
Material,Concrete,MediumRough,0.20,1.40,2200,900,0.90,0.70,0.70;
Construction,Depot construction,Concrete;
Zone,Equipment Room,0,0,0,0,1,1,3.0,80.0;
BuildingSurface:Detailed,Floor,Floor,Depot construction,Equipment Room,Ground,,NoSun,NoWind,1.0,4,0,0,0,10,0,0,10,8,0,0,8,0;
BuildingSurface:Detailed,Roof,Roof,Depot construction,Equipment Room,Outdoors,,SunExposed,WindExposed,0.0,4,0,8,3,10,8,3,10,0,3,0,0,3;
BuildingSurface:Detailed,North Wall,Wall,Depot construction,Equipment Room,Outdoors,,SunExposed,WindExposed,0.5,4,0,0,3,10,0,3,10,0,0,0,0,0;
BuildingSurface:Detailed,East Wall,Wall,Depot construction,Equipment Room,Outdoors,,SunExposed,WindExposed,0.5,4,10,0,3,10,8,3,10,8,0,10,0,0;
BuildingSurface:Detailed,South Wall,Wall,Depot construction,Equipment Room,Outdoors,,SunExposed,WindExposed,0.5,4,10,8,3,0,8,3,0,8,0,10,8,0;
BuildingSurface:Detailed,West Wall,Wall,Depot construction,Equipment Room,Outdoors,,SunExposed,WindExposed,0.5,4,0,8,3,0,0,3,0,0,0,0,8,0;
ScheduleTypeLimits,Fraction,0,1,Continuous;
Schedule:Constant,Always On,Fraction,1.0;
ElectricEquipment,Charger losses,Equipment Room,Always On,EquipmentLevel,40000,,,,0.0,0.0,0.0;
ZoneVentilation:DesignFlowRate,Equipment room ventilation,Equipment Room,Always On,Flow/Zone,4.0,,,,,Exhaust,15.0,20000,1.0,0.0,0.0,0.0;
Output:Variable,Equipment Room,Zone Mean Air Temperature,Hourly;
Output:Variable,Equipment room ventilation,Zone Ventilation Standard Density Volume Flow Rate,Hourly;
Output:SQLite,SimpleAndTabular;
"""


def fds_input() -> str:
    return """&HEAD CHID='osr_depot_charger_room', TITLE='OSR depot charger-room screening scenario' /
&TIME T_END=60.0 /
&DUMP DT_DEVC=1.0, NFRAMES=20 /
&MESH IJK=30,24,18, XB=0.0,5.0,0.0,4.0,0.0,3.0 /
&REAC FUEL='PROPANE', SOOT_YIELD=0.10, CO_YIELD=0.02 /
&RAMP ID='FIRE_RAMP', T=0.0, F=0.0 /
&RAMP ID='FIRE_RAMP', T=10.0, F=1.0 /
&SURF ID='CHARGER_FIRE', HRRPUA=250.0, RAMP_Q='FIRE_RAMP', COLOR='RED' /
&OBST ID='CHARGER', XB=2.0,3.0,1.5,2.5,0.0,1.8 /
&VENT ID='FIRE', XB=2.0,3.0,1.5,2.5,1.8,1.8, SURF_ID='CHARGER_FIRE' /
&VENT ID='DOOR', XB=0.0,0.0,1.5,2.5,0.0,2.2, SURF_ID='OPEN' /
&DEVC ID='ROOM_TEMP', XYZ=4.0,2.0,2.0, QUANTITY='TEMPERATURE' /
&DEVC ID='DOOR_VIS', XYZ=0.5,2.0,1.8, QUANTITY='VISIBILITY' /
&TAIL /
"""


def optional_solver_inputs(input_root: Path, run_root: Path) -> dict[str, Any]:
    energy_path = input_root / "energyplus" / ENERGYPLUS_INPUT.name
    fds_path = input_root / "fds" / FDS_INPUT.name
    energy_path.parent.mkdir(parents=True, exist_ok=True)
    fds_path.parent.mkdir(parents=True, exist_ok=True)
    energy_path.write_text(energyplus_input(), encoding="utf-8")
    fds_path.write_text(fds_input(), encoding="utf-8")

    charger_power_kw = 500.0
    charger_efficiency = 0.94
    auxiliary_heat_kw = 10.0
    heat_rejection_kw = charger_power_kw * (1.0 - charger_efficiency) + auxiliary_heat_kw
    airflow_m3_s = heat_rejection_kw * 1000.0 / (1.2 * 1005.0 * 10.0)
    energy_binary = shutil.which("energyplus")
    fds_binary = shutil.which("fds")
    energy_result: dict[str, Any] = {
        "analysis_id": "OSR-AN-STN-THM-001",
        "input_path": str(energy_path.relative_to(REPO_ROOT)),
        "input_sha256": sha256(energy_path),
        "preliminary_heat_rejection_kw": heat_rejection_kw,
        "preliminary_outdoor_airflow_m3_s": airflow_m3_s,
        "solver": "EnergyPlus",
        "solver_available": energy_binary is not None,
        "status": "input-prepared",
        "passed": False,
        "limitations": "One depot equipment-room design-day input; climate, envelope, charger duty/loss map, controls and ventilation architecture require project data.",
    }
    fire_result: dict[str, Any] = {
        "analysis_id": "OSR-AN-STN-FIR-001",
        "input_path": str(fds_path.relative_to(REPO_ROOT)),
        "input_sha256": sha256(fds_path),
        "scenario": "250 kW prescribed charger-room fire ramp; not a battery thermal-runaway model",
        "solver": "FDS",
        "solver_available": fds_binary is not None,
        "status": "input-prepared",
        "passed": False,
        "limitations": "Demonstration mesh and prescribed burner only; credible heat-release curve, battery chemistry, ventilation, suppression, tenability criteria and fire-engineer review are unresolved.",
    }
    if energy_binary:
        output = run_root / "energyplus"
        output.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            [energy_binary, "-D", "-d", str(output), str(energy_path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        end_file = output / "eplusout.end"
        successful = completed.returncode == 0 and end_file.is_file() and "Completed Successfully" in end_file.read_text(errors="replace")
        energy_result.update({"passed": successful, "return_code": completed.returncode, "status": "solver-completed" if successful else "solver-failed"})
    if fds_binary:
        output = run_root / "fds"
        output.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            [fds_binary, str(fds_path)],
            cwd=output,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        successful = completed.returncode == 0 and "completed successfully" in completed.stdout.lower()
        fire_result.update({"passed": successful, "return_code": completed.returncode, "status": "solver-completed" if successful else "solver-failed"})
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
            f"| Depot thermal | EnergyPlus | tracked equipment-room design-day deck | {optional['energyplus']['status']} | Run solver; replace climate, heat loads, envelope and controls |",
            f"| Depot fire | FDS | tracked prescribed 250 kW charger-room deck | {optional['fds']['status']} | Credible fire source, refined mesh, tenability/suppression and fire-engineer review |",
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
    lines.extend(
        [
            "",
            "## Release boundary",
            "",
            "A passing row means only that the deterministic catalogue assumption completed",
            "and met its stated screening threshold. Before procurement or construction, the",
            "deployment team must substitute surveyed/site inputs, local statutory criteria,",
            "supplier performance data, detailed connections and independent competent review.",
            "The EnergyPlus and FDS decks are intentionally reported as pending until those",
            "solvers and project inputs produce reviewed results.",
            "",
        ]
    )
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
    print(f"wrote {args.output}")
    print(f"wrote {markdown_path}")
    return 0 if report["screening_execution_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

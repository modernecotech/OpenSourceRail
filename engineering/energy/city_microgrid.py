#!/usr/bin/env python3
"""Generate repeatable pandapower and pvlib screening outputs for one OSR city."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
import tomllib
from pathlib import Path

import pandas as pd
import pandapower as pp
import pvlib


REPO_ROOT = Path(__file__).resolve().parents[2]
CLIMATE_PRESETS = REPO_ROOT / "lib/templates/climate.toml"
POWER_FACTOR = 0.99
GRID_RECTIFIER_EFFICIENCY = 0.97
GRID_EXPORT_INVERTER_EFFICIENCY = 0.97
DAYLIGHT_PV_FACTOR = 0.60
COORDINATED_STORAGE_FACTOR = 0.50
TRANSFORMER_PLANNING_HEADROOM = 1.25


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_network(
    sites: list[dict[str, object]],
    charging_by_station: dict[str, float],
    *,
    pv_factor: float,
    storage_factor: float,
) -> pp.pandapowerNet:
    network = pp.create_empty_network(sn_mva=100.0)
    grid_bus = pp.create_bus(network, vn_kv=33.0, name="city-33kv-grid")
    pp.create_ext_grid(network, grid_bus, vm_pu=1.0, name="planning-grid-connection")
    for site in sites:
        station = str(site["station"])
        bus = pp.create_bus(network, vn_kv=0.4, name=station)
        grid_import_kw = float(site["grid_import_kw"])
        connected_charge_kw = charging_by_station.get(station, 0.0)
        # This is the AC-grid equivalent of a DC-native station. PV, storage,
        # and train charging remain on the DC bus; only residual import passes
        # through one stationary grid rectifier. The transformer must still
        # carry that rectifier's installed contingency rating.
        installed_rectifier_kw = connected_charge_kw / GRID_RECTIFIER_EFFICIENCY
        transformer_mva = max(
            max(grid_import_kw, installed_rectifier_kw)
            / POWER_FACTOR
            / 1000.0
            * TRANSFORMER_PLANNING_HEADROOM,
            0.1,
        )
        pp.create_transformer_from_parameters(
            network,
            grid_bus,
            bus,
            sn_mva=transformer_mva,
            vn_hv_kv=33.0,
            vn_lv_kv=0.4,
            vkr_percent=0.6,
            vk_percent=6.0,
            pfe_kw=1.0,
            i0_percent=0.2,
            name=f"{station}:site-transformer",
        )
        charge_kw = connected_charge_kw
        pv_kw = float(site["pv_nameplate_kw"]) * pv_factor
        storage_kw = min(charge_kw, float(site["storage_max_discharge_kw"]) * storage_factor)
        local_dc_kw = pv_kw + storage_kw
        residual_dc_kw = charge_kw - local_dc_kw
        if residual_dc_kw >= 0.0:
            rectifier_import_kw = residual_dc_kw / GRID_RECTIFIER_EFFICIENCY
            pp.create_load(
                network,
                bus,
                p_mw=rectifier_import_kw / 1000.0,
                q_mvar=rectifier_import_kw * math.tan(math.acos(POWER_FACTOR)) / 1000.0,
                name=f"{station}:grid-rectifier",
            )
        else:
            export_kw = -residual_dc_kw * GRID_EXPORT_INVERTER_EFFICIENCY
            pp.create_sgen(
                network,
                bus,
                p_mw=export_kw / 1000.0,
                q_mvar=0.0,
                name=f"{station}:grid-export-inverter",
            )
    return network


def run_case(network: pp.pandapowerNet, output: Path) -> dict[str, object]:
    try:
        pp.runpp(network, algorithm="nr", max_iteration=30, calculate_voltage_angles=False)
    except Exception as error:  # solver error is evidence and belongs in the result
        return {"converged": False, "error": f"{type(error).__name__}: {error}"}
    pp.to_json(network, str(output))
    transformer_loading = network.res_trafo.loading_percent.astype(float)
    bus_voltage = network.res_bus.vm_pu.astype(float)
    return {
        "converged": bool(network.converged),
        "minimum_bus_voltage_pu": round(float(bus_voltage.min()), 6),
        "maximum_bus_voltage_pu": round(float(bus_voltage.max()), 6),
        "maximum_transformer_loading_percent": round(float(transformer_loading.max()), 3),
        "overloaded_transformer_count": int((transformer_loading > 100.0).sum()),
        "undervoltage_bus_count": int((bus_voltage < 0.95).sum()),
        "overvoltage_bus_count": int((bus_voltage > 1.05).sum()),
    }


def clear_sky_specific_yield(latitude: float, longitude: float) -> float:
    times = pd.date_range("2025-01-01", "2026-01-01", freq="1h", inclusive="left", tz="UTC")
    location = pvlib.location.Location(latitude, longitude, tz="UTC")
    solar_position = location.get_solarposition(times)
    clear_sky = location.get_clearsky(times, model="ineichen")
    irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=max(5.0, min(abs(latitude), 35.0)),
        surface_azimuth=180.0 if latitude >= 0 else 0.0,
        solar_zenith=solar_position["apparent_zenith"],
        solar_azimuth=solar_position["azimuth"],
        dni=clear_sky["dni"],
        ghi=clear_sky["ghi"],
        dhi=clear_sky["dhi"],
    )
    return float(irradiance["poa_global"].clip(lower=0).sum() / 1000.0)


def generate(design_path: Path, output: Path) -> dict[str, object]:
    design_path = design_path.resolve()
    output = output.resolve()
    design = tomllib.loads(design_path.read_text(encoding="utf-8"))
    city = design.get("city", {})
    slug = str(city.get("slug", "")).strip()
    if not slug:
        raise RuntimeError(f"{design_path}: missing city.slug")
    scenario_path = design_path.parent / f"{slug}.toml"
    if not scenario_path.is_file():
        raise RuntimeError(f"{design_path}: missing scenario {scenario_path.name}")
    scenario = tomllib.loads(scenario_path.read_text(encoding="utf-8"))
    sites = list(scenario.get("sites", []))
    if not sites:
        raise RuntimeError(f"{scenario_path}: no energy sites")
    charging_by_station = {
        str(station["id"]): float(station.get("charging_power_kw", 0.0))
        for station in scenario.get("stations", [])
    }
    station_by_id = {str(station["id"]): station for station in design.get("stations", [])}
    missing_station_ids = sorted(
        str(site["station"]) for site in sites if str(site["station"]) not in station_by_id
    )
    missing_charger_ids = sorted(
        str(site["station"]) for site in sites if str(site["station"]) not in charging_by_station
    )
    if missing_station_ids or missing_charger_ids:
        raise RuntimeError(
            f"{slug}: energy sites missing design stations={missing_station_ids}, "
            f"charging records={missing_charger_ids}"
        )

    latitude = sum(float(station_by_id[str(site["station"])]["lat"]) for site in sites) / len(sites)
    longitude = sum(float(station_by_id[str(site["station"])]["lon"]) for site in sites) / len(sites)
    climate_data = tomllib.loads(CLIMATE_PRESETS.read_text(encoding="utf-8"))
    preset_name = str(design.get("climate", {}).get("preset", ""))
    preset = climate_data.get("presets", {}).get(preset_name)
    if preset is None:
        raise RuntimeError(f"{slug}: unknown climate preset {preset_name!r}")
    scenario_peak_sun = float(scenario.get("climate", {}).get("peak_sun_hours", preset["peak_sun_hours"]))
    scenario_ambient = float(
        scenario.get("climate", {}).get("ambient_c", preset["ambient_c_average"])
    )
    pv_nameplate_kw = sum(float(site["pv_nameplate_kw"]) for site in sites)
    storage_capacity_kwh = sum(float(site["storage_capacity_kwh"]) for site in sites)
    grid_import_kw = sum(float(site["grid_import_kw"]) for site in sites)
    connected_charging_kw = sum(charging_by_station[str(site["station"])] for site in sites)
    theoretical_specific_yield = clear_sky_specific_yield(latitude, longitude)
    planning_specific_yield = (
        scenario_peak_sun
        * 365.0
        * (1.0 - float(preset["pv_temperature_derate"]))
        * (1.0 - float(preset["dust_soiling_worst_pct"]))
    )

    output.mkdir(parents=True, exist_ok=True)
    cases = {
        "peak_charge_grid_only": run_case(
            build_network(sites, charging_by_station, pv_factor=0.0, storage_factor=0.0),
            output / "peak-charge-grid-only.json",
        ),
        "coordinated_daylight": run_case(
            build_network(
                sites,
                charging_by_station,
                pv_factor=DAYLIGHT_PV_FACTOR,
                storage_factor=COORDINATED_STORAGE_FACTOR,
            ),
            output / "coordinated-daylight.json",
        ),
    }
    findings: list[dict[str, object]] = []
    if abs(scenario_ambient - float(preset["ambient_c_average"])) > 5.0:
        findings.append(
            {
                "code": "scenario-climate-ambient-mismatch",
                "scenario_ambient_c": scenario_ambient,
                "preset_ambient_c_average": float(preset["ambient_c_average"]),
                "difference_c": round(
                    scenario_ambient - float(preset["ambient_c_average"]), 3
                ),
            }
        )
    for name, result in cases.items():
        if result.get("overloaded_transformer_count", 0):
            findings.append(
                {
                    "code": "site-transformer-overload",
                    "case": name,
                    "count": result["overloaded_transformer_count"],
                    "maximum_loading_percent": result["maximum_transformer_loading_percent"],
                }
            )
        if result.get("undervoltage_bus_count", 0) or result.get("overvoltage_bus_count", 0):
            findings.append(
                {
                    "code": "site-voltage-outside-screening-band",
                    "case": name,
                    "undervoltage_bus_count": result.get("undervoltage_bus_count", 0),
                    "overvoltage_bus_count": result.get("overvoltage_bus_count", 0),
                }
            )
    solver_passed = all(bool(result.get("converged")) for result in cases.values())
    report = {
        "analysis_family": "OSR-AN-ENE-CITY-MICROGRID",
        "analysis_id": f"OSR-AN-ENE-CITY-MICROGRID:{slug}",
        "city": slug,
        "design_input": str(design_path.relative_to(REPO_ROOT)),
        "design_sha256": source_hash(design_path),
        "scenario_input": str(scenario_path.relative_to(REPO_ROOT)),
        "scenario_sha256": source_hash(scenario_path),
        "climate_input": str(CLIMATE_PRESETS.relative_to(REPO_ROOT)),
        "climate_sha256": source_hash(CLIMATE_PRESETS),
        "climate_preset": preset_name,
        "scenario_ambient_c": scenario_ambient,
        "scenario_peak_sun_hours": scenario_peak_sun,
        "generator_sha256": source_hash(Path(__file__)),
        "site_count": len(sites),
        "pv_nameplate_kw": pv_nameplate_kw,
        "storage_capacity_kwh": storage_capacity_kwh,
        "grid_import_capacity_kw": grid_import_kw,
        "connected_charging_power_kw": connected_charging_kw,
        "clear_sky_specific_yield_kwh_per_kwp": round(theoretical_specific_yield, 1),
        "derated_planning_specific_yield_kwh_per_kwp": round(planning_specific_yield, 1),
        "derated_planning_pv_energy_mwh_per_year": round(
            pv_nameplate_kw * planning_specific_yield / 1000.0, 1
        ),
        "assumptions": {
            "power_factor": POWER_FACTOR,
            "station_power_path": "PV and storage feed a common DC bus; only residual import/export crosses the modeled AC interface",
            "grid_rectifier_efficiency": GRID_RECTIFIER_EFFICIENCY,
            "grid_export_inverter_efficiency": GRID_EXPORT_INVERTER_EFFICIENCY,
            "site_transformer_sizing_basis": "greater of installed rectifier input or declared grid import, divided by power factor, with 25% planning headroom",
            "site_transformer_planning_headroom": TRANSFORMER_PLANNING_HEADROOM,
            "coordinated_daylight_pv_fraction": DAYLIGHT_PV_FACTOR,
            "coordinated_storage_discharge_fraction": COORDINATED_STORAGE_FACTOR,
            "clear_sky_weather_status": "pvlib theoretical envelope; not measured weather",
            "planning_yield_status": "scenario peak-sun-hours with canonical temperature and worst-soiling derates",
        },
        "cases": cases,
        "design_findings": findings,
        "solver_passed": solver_passed,
        "passed": solver_passed,
        "tools": {
            "pandapower": pp.__version__,
            "pvlib": pvlib.__version__,
        },
    }
    atomic_json(output / "summary.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    metadata = tomllib.loads(args.design.read_text(encoding="utf-8"))
    slug = str(metadata.get("city", {}).get("slug", "unknown"))
    output = args.output_dir or args.design.resolve().parent / "engineering/energy"
    report = generate(args.design, output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

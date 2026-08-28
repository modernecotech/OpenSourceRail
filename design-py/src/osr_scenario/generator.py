"""Scenario generator — `design.toml` + templates → `scenarios/*.toml`."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class GeneratorError(RuntimeError):
    """Raised when the design file can't be resolved into a valid scenario."""


# ---------------------------------------------------------------------------
# Archetype / tier fallbacks (used if the templates fail to load)
# ---------------------------------------------------------------------------

# Per-archetype station operational defaults. The template is read first;
# these values are a safety net for when templates are unavailable.
_STATION_ARCHETYPE_DEFAULTS: dict[str, dict[str, Any]] = {
    "halt":                 {"charging_power_kw": 0,    "dwell_seconds": 60,  "is_depot": False},
    "standard":             {"charging_power_kw": 500,  "dwell_seconds": 60,  "is_depot": False},
    "major":                {"charging_power_kw": 500,  "dwell_seconds": 60,  "is_depot": False},
    "interchange":          {"charging_power_kw": 500,  "dwell_seconds": 60,  "is_depot": False},
    "interchange-elevated": {"charging_power_kw": 500,  "dwell_seconds": 60,  "is_depot": False},
    "terminal":             {"charging_power_kw": 500,  "dwell_seconds": 180, "is_depot": False},
    "depot-terminal":       {"charging_power_kw": 500,  "dwell_seconds": 240, "is_depot": True},
}

# Per-tier energy-site operational defaults.
_SITE_TIER_DEFAULTS: dict[str, dict[str, float]] = {
    "standard":        {"pv_nameplate_kw": 300.0, "storage_capacity_kwh": 500.0,
                         "storage_module_kwh": 500.0, "storage_max_charge_kw": 500.0,
                         "storage_max_discharge_kw": 500.0, "storage_initial_soc": 0.5,
                         "grid_import_kw": 500.0, "grid_export_kw": 500.0,
                         "charger_max_kw": 500.0, "charger_max_current_a": 825.0,
                         "charger_bus_voltage_v": 650.0, "charger_efficiency": 0.98,
                         "charger_contact_count": 2.0},
    "major":           {"pv_nameplate_kw": 300.0, "storage_capacity_kwh": 500.0,
                         "storage_module_kwh": 500.0, "storage_max_charge_kw": 500.0,
                         "storage_max_discharge_kw": 500.0, "storage_initial_soc": 0.5,
                         "grid_import_kw": 600.0, "grid_export_kw": 600.0,
                         "charger_max_kw": 500.0, "charger_max_current_a": 825.0,
                         "charger_bus_voltage_v": 650.0, "charger_efficiency": 0.98,
                         "charger_contact_count": 2.0},
    "interchange":     {"pv_nameplate_kw": 300.0, "storage_capacity_kwh": 500.0,
                         "storage_module_kwh": 500.0, "storage_max_charge_kw": 500.0,
                         "storage_max_discharge_kw": 500.0, "storage_initial_soc": 0.5,
                         "grid_import_kw": 600.0, "grid_export_kw": 600.0,
                         "charger_max_kw": 500.0, "charger_max_current_a": 825.0,
                         "charger_bus_voltage_v": 650.0, "charger_efficiency": 0.98,
                         "charger_contact_count": 2.0},
    "terminal":        {"pv_nameplate_kw": 300.0, "storage_capacity_kwh": 500.0,
                         "storage_module_kwh": 500.0, "storage_max_charge_kw": 500.0,
                         "storage_max_discharge_kw": 500.0, "storage_initial_soc": 0.6,
                         "grid_import_kw": 800.0, "grid_export_kw": 800.0,
                         "charger_max_kw": 500.0, "charger_max_current_a": 825.0,
                         "charger_bus_voltage_v": 650.0, "charger_efficiency": 0.98,
                         "charger_contact_count": 2.0},
    "depot-secondary": {"pv_nameplate_kw": 1500.0, "storage_capacity_kwh": 5000.0,
                         "storage_max_charge_kw": 2000.0, "storage_max_discharge_kw": 2000.0,
                         "storage_initial_soc": 0.6,  "grid_import_kw": 1000.0, "grid_export_kw": 1000.0},
    "depot-layup":     {"pv_nameplate_kw": 90.0,   "storage_capacity_kwh": 150.0,
                         "storage_max_charge_kw": 600.0, "storage_max_discharge_kw": 600.0,
                         "storage_initial_soc": 0.6,  "grid_import_kw": 600.0, "grid_export_kw": 100.0},
    "depot-main":      {"pv_nameplate_kw": 5000.0, "storage_capacity_kwh": 40000.0,
                         "storage_max_charge_kw": 10000.0, "storage_max_discharge_kw": 10000.0,
                         "storage_initial_soc": 0.7,  "grid_import_kw": 3000.0, "grid_export_kw": 3000.0},
}

# Archetype → energy-site tier mapping (used when design.toml carries
# no explicit `[[sites]]` blocks — i.e. auto-generated designs from
# `osr-design`). Halts get no trackside energy (shelter-only stops);
# standard / major / interchange / terminal each take the matching
# tier from energy-sites.toml. `depot-terminal` stations colocate the
# main depot's microgrid. Standalone depots by archetype: main-heavy
# = depot-main, secondary-medium = depot-secondary, and layup-minimal =
# depot-layup. A
# layup has no workshop, but it still needs an electrical top-up site for
# trains stabled between duties.
_STATION_TIER_MAP: dict[str, str] = {
    "halt": "",  # no site
    "standard": "standard",
    "major": "major",
    "interchange": "interchange",
    "interchange-elevated": "interchange",
    "terminal": "terminal",
    "depot-terminal": "depot-main",
}
_DEPOT_TIER_MAP: dict[str, str] = {
    "main-heavy": "depot-main",
    "secondary-medium": "depot-secondary",
    "layup-minimal": "depot-layup",
}

# Consist family → summary physical parameters (light-metro-3car etc.).
# Authoritative numbers live in `lib/templates/rolling-stock.toml`;
# values here are the sim-critical subset.
_CONSIST_DEFAULTS: dict[str, dict[str, int | float]] = {
    "urban-shuttle-1car": {"car_count": 1, "length_m": 21,  "mass_kg": 34_000,  "max_speed_kmh": 70.0,  "battery_capacity_kwh": 180, "passenger_capacity": 100, "seat_count": 20,  "crush_capacity": 130, "service_accel_mps2": 1.0, "roof_pv_nameplate_kw": 6.4,  "roof_pv_cleaner_kw": 0.3},
    "tram-2car":          {"car_count": 2, "length_m": 39,  "mass_kg": 68_000,  "max_speed_kmh": 70.0,  "battery_capacity_kwh": 360, "passenger_capacity": 240, "seat_count": 40,  "crush_capacity": 320, "service_accel_mps2": 1.0, "roof_pv_nameplate_kw": 12.8,  "roof_pv_cleaner_kw": 0.6},
    "light-metro-3car":   {"car_count": 3, "length_m": 49.5, "mass_kg": 78_750, "max_speed_kmh": 90.0, "battery_capacity_kwh": 540, "passenger_capacity": 360, "seat_count": 60,  "crush_capacity": 480, "service_accel_mps2": 1.0, "roof_pv_nameplate_kw": 15.12, "roof_pv_cleaner_kw": 0.9},
    "metro-4car":         {"car_count": 4, "length_m": 75,  "mass_kg": 136_000, "max_speed_kmh": 90.0,  "battery_capacity_kwh": 720, "passenger_capacity": 480, "seat_count": 80,  "crush_capacity": 640, "service_accel_mps2": 1.1, "roof_pv_nameplate_kw": 25.6, "roof_pv_cleaner_kw": 1.2},
    "metro-6car":         {"car_count": 6, "length_m": 111, "mass_kg": 204_000, "max_speed_kmh": 100.0, "battery_capacity_kwh": 1080, "passenger_capacity": 720, "seat_count": 120, "crush_capacity": 960, "service_accel_mps2": 1.1, "roof_pv_nameplate_kw": 38.4, "roof_pv_cleaner_kw": 1.8},
}

# Rolling-stock templates specify usable traction energy.  The simulator
# models a 20% protected reserve, so its capacity field must contain the
# corresponding nameplate capacity rather than applying that reserve twice.
_BATTERY_USABLE_FRACTION = 0.80
_OPPORTUNITY_CHARGING_EFFICIENCY = 0.98
_MINIMUM_TRAVERSAL_ENERGY_MARGIN = 1.10

_TRAINSET_SYSTEM_DEFAULTS: dict[str, Any] = {
    "mechanical_standard_revision": "A-DRAFT",
    "door_cassettes_per_car": 4,
    "window_cassettes_per_car": 6,
    "service_rails_per_car": 8,
    "fastener_family_count": 4,
    "connector_family_count": 2,
    "main_light_modules_per_car": 22,
    "emergency_light_modules_per_car": 4,
    "door_threshold_light_modules_per_car": 4,
    "lighting_power_w_per_car": 500.0,
    "hvac_thermal_kw_per_car": 24.0,
}


def _charging_cabinet_count(family: str) -> int:
    """Repeat the standard 500 kW module for high-throughput consists."""
    return {"metro-4car": 3, "metro-6car": 4}.get(family, 1)


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


@dataclass
class ScenarioGenerator:
    """Holds the loaded design + template context and drives emission."""

    design: dict[str, Any]
    design_path: Path
    templates_root: Path
    station_archetypes: dict[str, dict[str, Any]] = field(default_factory=dict)
    site_tiers: dict[str, dict[str, float]] = field(default_factory=dict)
    climate_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    trainset_systems: dict[str, Any] = field(default_factory=dict)
    depot_service_seconds: int = 720

    def __post_init__(self) -> None:
        # Load templates if available; fall back to baked defaults otherwise.
        st_path = self.templates_root / "stations.toml"
        if st_path.exists():
            st = tomllib.loads(st_path.read_text())
            self.station_archetypes = st.get("archetypes", {})
        en_path = self.templates_root / "energy-sites.toml"
        if en_path.exists():
            en = tomllib.loads(en_path.read_text())
            self.site_tiers = en.get("tiers", {})
        climate_path = self.templates_root / "climate.toml"
        if climate_path.exists():
            climate = tomllib.loads(climate_path.read_text())
            self.climate_presets = climate.get("presets", {})
        rolling_stock_path = self.templates_root / "rolling-stock.toml"
        self.trainset_systems = dict(_TRAINSET_SYSTEM_DEFAULTS)
        if rolling_stock_path.exists():
            rolling_stock = tomllib.loads(rolling_stock_path.read_text())
            self.trainset_systems.update(rolling_stock.get("trainset_systems", {}))
        depot_path = self.templates_root / "depots.toml"
        if depot_path.exists():
            depot = tomllib.loads(depot_path.read_text())
            turnaround = depot.get("operations", {}).get("turnaround_service", {})
            self.depot_service_seconds = int(
                turnaround.get("duration_seconds", self.depot_service_seconds)
            )

    # ------ Resolution helpers ------

    def station_defaults(self, archetype: str) -> dict[str, Any]:
        """Resolve operational defaults for a station archetype."""
        tpl = self.station_archetypes.get(archetype, {})
        # Unknown archetypes fall back to `standard` rather than {} —
        # `osr-design` may emit variants the templates don't yet name
        # (e.g. `interchange-elevated`, future tier subtypes).
        baked = _STATION_ARCHETYPE_DEFAULTS.get(
            archetype, _STATION_ARCHETYPE_DEFAULTS["standard"]
        )
        out = dict(baked)
        for k in ("charging_power_kw", "dwell_seconds"):
            if k in tpl:
                out[k] = tpl[k]
        if tpl.get("is_depot"):
            out["is_depot"] = True
        return out

    def site_defaults(self, tier: str) -> dict[str, float]:
        """Resolve operational defaults for a site tier."""
        tpl = self.site_tiers.get(tier, {})
        out = dict(_SITE_TIER_DEFAULTS.get(tier, {}))
        for k, v in tpl.items():
            out[k] = v
        return out

    # ------ Emission ------

    def emit(self) -> str:
        """Produce the scenario TOML string."""
        self._validate_opportunity_charging()
        out: list[str] = []
        out.append(self._scenario_header())
        out.append(self._climate_section())
        out.append(self._consist_section())
        out.append(self._stations_section())
        out.append(self._lines_section())
        out.append(self._fleets_section())
        out.append(self._sites_section())
        return "\n".join(out).rstrip() + "\n"

    def _validate_opportunity_charging(self) -> None:
        """Reject timetables that cannot sustain repeated line traversals.

        The onboard pack is the buffer between charging platforms; it is not
        expected to carry a train around a complete ring without charging.
        Every ring must therefore replace a climate-adjusted circuit's energy
        during its scheduled powered dwells. Every line must also keep the
        largest gap between powered stops within usable battery capacity;
        radial terminal balancing is checked by the operations simulation.
        """
        lines = self.design.get("lines", [])
        if not lines:
            return
        family = lines[0].get("rolling_stock", "light-metro-3car")
        consist = _CONSIST_DEFAULTS.get(family)
        if consist is None:
            raise GeneratorError(f"unknown rolling-stock family {family!r}")
        car_count = int(consist["car_count"])
        usable_battery_kwh = float(consist["battery_capacity_kwh"])
        cabinet_count = _charging_cabinet_count(family)

        traction = self.design.get("operations", {}).get("traction_energy", {})
        nominal_kwh_per_car_km = float(
            traction.get(
                "nominal_energy_kwh_per_car_km",
                float(traction.get("reference_energy_kwh_per_car_km", 3.0))
                * float(traction.get("modern_drive_energy_factor", 0.80)),
            )
        )
        climate = self.design.get("climate", {})
        preset = self.climate_presets.get(
            str(climate.get("preset", "temperate-continental")), {}
        )
        ambient_c = float(
            climate.get("ambient_c", preset.get("ambient_c_average", 28.0))
        )
        climate_uplift = min(max((ambient_c - 25.0) / 25.0, 0.0), 0.25)

        operations = self.design.get("operations", {})
        radial_minimum = int(
            operations.get("radial_service", {}).get(
                "minimum_charging_dwell_seconds", 120
            )
        )
        ring_policy = operations.get("ring_service", {})
        enforce_ring_balance = "opportunity_charging_required" in ring_policy
        ring_minimum = int(ring_policy.get("minimum_dwell_seconds", 120))
        energy_margin = float(
            ring_policy.get(
                "minimum_traversal_energy_margin",
                _MINIMUM_TRAVERSAL_ENERGY_MARGIN,
            )
        )

        flat_stations = self.design.get("stations", [])
        station_by_id = {str(station["id"]): station for station in flat_stations}
        stations_by_line: dict[str, list[dict[str, Any]]] = {}
        for station in flat_stations:
            stations_by_line.setdefault(str(station.get("line", "")), []).append(station)
        for stations in stations_by_line.values():
            stations.sort(key=lambda station: float(station.get("s_m", 0.0)))

        for line in lines:
            line_id = str(line.get("id") or line.get("name"))
            is_ring = bool(line.get("is_ring") or line.get("shape") == "ring")
            if is_ring and not bool(ring_policy.get("opportunity_charging_required", True)):
                raise GeneratorError(
                    f"ring line {line_id!r} disables required opportunity charging"
                )
            minimum_dwell = ring_minimum if is_ring else radial_minimum
            dwell_seconds = max(
                minimum_dwell,
                int(line.get("charging_dwell_seconds", minimum_dwell)),
            )
            line_length_m = float(line.get("length_m", 0.0))
            if line_length_m <= 0.0:
                raise GeneratorError(f"line {line_id!r} has no positive length")

            line_stations = list(stations_by_line.get(line_id, []))
            if not line_stations and line.get("stations"):
                chainage_m = 0.0
                for index, inline in enumerate(line["stations"]):
                    if index:
                        chainage_m += float(inline.get("distance_from_prev_m", 0.0))
                    station_id = str(inline["id"])
                    station = dict(station_by_id.get(station_id, {}))
                    station.setdefault("id", station_id)
                    station["s_m"] = chainage_m
                    line_stations.append(station)

            powered: list[tuple[float, float]] = []
            for station in line_stations:
                defaults = self.station_defaults(station.get("archetype", "standard"))
                power_kw = float(defaults.get("charging_power_kw", 0.0))
                if power_kw > 0.0:
                    powered.append(
                        (float(station.get("s_m", 0.0)), power_kw * cabinet_count)
                    )
            if not powered:
                raise GeneratorError(
                    f"line {line_id!r} has no powered passenger stop"
                )

            traversal_kwh = (
                line_length_m
                / 1000.0
                * car_count
                * nominal_kwh_per_car_km
                * (1.0 + climate_uplift)
            )
            delivered_kwh = (
                sum(power_kw for _, power_kw in powered)
                * dwell_seconds
                / 3600.0
                * _OPPORTUNITY_CHARGING_EFFICIENCY
            )
            required_kwh = traversal_kwh * energy_margin
            if (
                is_ring
                and enforce_ring_balance
                and delivered_kwh + 1e-6 < required_kwh
            ):
                raise GeneratorError(
                    f"line {line_id!r} opportunity charging delivers "
                    f"{delivered_kwh:.1f} kWh per traversal; "
                    f"{required_kwh:.1f} kWh is required"
                )

            powered_chainages = sorted(chainage for chainage, _ in powered)
            if is_ring:
                gaps_m = [
                    powered_chainages[index + 1] - powered_chainages[index]
                    for index in range(len(powered_chainages) - 1)
                ]
                gaps_m.append(
                    line_length_m - powered_chainages[-1] + powered_chainages[0]
                )
            else:
                gaps_m = [powered_chainages[0]]
                gaps_m.extend(
                    powered_chainages[index + 1] - powered_chainages[index]
                    for index in range(len(powered_chainages) - 1)
                )
                gaps_m.append(line_length_m - powered_chainages[-1])
            worst_gap_m = max(gaps_m, default=line_length_m)
            worst_gap_kwh = (
                worst_gap_m
                / 1000.0
                * car_count
                * nominal_kwh_per_car_km
                * (1.0 + climate_uplift)
            )
            if worst_gap_kwh > usable_battery_kwh + 1e-6:
                raise GeneratorError(
                    f"line {line_id!r} needs {worst_gap_kwh:.1f} kWh across "
                    f"its longest gap between powered stops, exceeding the "
                    f"{usable_battery_kwh:.1f} kWh usable pack"
                )

    # ---- section builders ----

    def _scenario_header(self) -> str:
        name = _scenario_name(self.design)
        source_path = self._display_design_path()
        policy = self.design.get("operations", {}).get(
            "energy_adaptive_service", {}
        )
        enabled = bool(policy.get("enabled", True))
        normal_service_soc = float(policy.get("normal_service_soc", 0.40))
        maximum_headway_multiplier = float(
            policy.get("maximum_headway_multiplier", 3.0)
        )
        protected_peak_headway_min = int(
            policy.get("protected_peak_headway_min", 3)
        )
        return (
            f"# AUTO-GENERATED from {source_path}.\n"
            f"# Do not hand-edit; run `python -m osr_scenario --design ...` to regenerate.\n"
            f"# Source of truth: {source_path}\n"
            f"\n"
            f"[scenario]\n"
            f'name = "{_escape(name)}"\n'
            f'start_time = "05:30"\n'
            f"# Clean + daily safety inspection + low-C recharge, concurrently.\n"
            f"depot_service_seconds = {self.depot_service_seconds}\n"
            f"# Preserve the 07:00–09:00 and 15:00–17:00 three-minute peaks;\n"
            f"# widen only off-peak headways when delivered charging energy is low.\n"
            f"energy_adaptive_service = {str(enabled).lower()}\n"
            f"normal_service_soc = {normal_service_soc:.2f}\n"
            f"maximum_headway_multiplier = {maximum_headway_multiplier:.1f}\n"
            f"protected_peak_headway_min = {protected_peak_headway_min}\n"
        )

    def _display_design_path(self) -> str:
        """Return a stable source path for generated comments.

        Generated scenarios are committed to the repository, so comments
        must not include developer-specific absolute paths such as
        `/home/alice/...`. The templates directory is always
        `<repo>/lib/templates`; use it to derive the repo root when
        possible, and fall back to the provided path for out-of-tree use.
        """

        repo_root = self.templates_root.parent.parent.resolve()
        try:
            return self.design_path.resolve().relative_to(repo_root).as_posix()
        except ValueError:
            return self.design_path.as_posix()

    def _climate_section(self) -> str:
        clim = self.design.get("climate", {})
        preset = clim.get("preset", "temperate-continental")
        preset_values = self.climate_presets.get(preset, {})
        ambient = clim.get(
            "ambient_c", preset_values.get("ambient_c_average", 28.0)
        )
        psh = clim.get(
            "peak_sun_hours", preset_values.get("peak_sun_hours", 5.0)
        )
        return (
            f"\n[climate]\n"
            f"ambient_c = {ambient}\n"
            f"peak_sun_hours = {psh}\n"
        )

    def _consist_section(self) -> str:
        # Pick the rolling stock family used by the majority of the lines.
        # If multiple families are in play, write a consist for the first
        # line (the sim assumes a single consist per scenario).
        lines = self.design.get("lines", [])
        family = (
            lines[0].get("rolling_stock", "light-metro-3car")
            if lines else "light-metro-3car"
        )
        cd = _CONSIST_DEFAULTS.get(family)
        if cd is None:
            return ""
        usable_battery_kwh = int(cd["battery_capacity_kwh"])
        nameplate_battery_kwh = round(
            usable_battery_kwh / _BATTERY_USABLE_FRACTION
        )
        traction_policy = self.design.get("operations", {}).get(
            "traction_energy", {}
        )
        reference_energy = float(
            traction_policy.get("reference_energy_kwh_per_car_km", 3.0)
        )
        modern_drive_factor = float(
            traction_policy.get(
                "modern_drive_energy_factor",
                0.80 if traction_policy else 1.0,
            )
        )
        nominal_energy = float(
            traction_policy.get(
                "nominal_energy_kwh_per_car_km",
                reference_energy * modern_drive_factor,
            )
        )
        energy_comment = (
            f"# {reference_energy:.1f} reference x {modern_drive_factor:.2f} "
            "PMSM/SiC factor; climate uplift follows.\n"
            if traction_policy
            else "# Nominal base before climate uplift; 4.0 remains the hot-climate planning case.\n"
        )
        return (
            f"\n[consist]\n"
            f"# From rolling-stock family '{family}'.\n"
            f"car_count = {cd['car_count']}\n"
            f"length_m = {cd['length_m']}\n"
            f"mass_kg = {cd['mass_kg']}\n"
            f"max_speed_kmh = {cd['max_speed_kmh']}\n"
            f"# {usable_battery_kwh} kWh usable with a 20% protected reserve.\n"
            f"battery_capacity_kwh = {nameplate_battery_kwh}\n"
            f"{energy_comment}"
            f"energy_kwh_per_car_km = {nominal_energy:.1f}\n"
            f"passenger_capacity = {cd['passenger_capacity']}\n"
            f"seat_count = {cd['seat_count']}\n"
            f"crush_capacity = {cd['crush_capacity']}\n"
            f"service_accel_mps2 = {cd['service_accel_mps2']}\n"
            f"\n[consist.systems]\n"
            f"mechanical_standard_revision = \"{self.trainset_systems['mechanical_standard_revision']}\"\n"
            f"door_cassettes_per_car = {self.trainset_systems['door_cassettes_per_car']}\n"
            f"window_cassettes_per_car = {self.trainset_systems['window_cassettes_per_car']}\n"
            f"service_rails_per_car = {self.trainset_systems['service_rails_per_car']}\n"
            f"fastener_family_count = {self.trainset_systems['fastener_family_count']}\n"
            f"connector_family_count = {self.trainset_systems['connector_family_count']}\n"
            f"main_light_modules_per_car = {self.trainset_systems['main_light_modules_per_car']}\n"
            f"emergency_light_modules_per_car = {self.trainset_systems['emergency_light_modules_per_car']}\n"
            f"door_threshold_light_modules_per_car = {self.trainset_systems['door_threshold_light_modules_per_car']}\n"
            f"lighting_power_w_per_car = {self.trainset_systems['lighting_power_w_per_car']}\n"
            f"hvac_thermal_kw_per_car = {self.trainset_systems['hvac_thermal_kw_per_car']}\n"
            f"\n[consist.roof_pv]\n"
            f"nameplate_kw = {cd['roof_pv_nameplate_kw']}\n"
            f"usable_factor = 0.65\n"
            f"charges_while_moving = true\n"
            f"charges_while_dwelled = true\n"
            f"\n[consist.roof_pv.air_cleaner]\n"
            f"enabled = true\n"
            f"compressor_power_kw = {cd['roof_pv_cleaner_kw']}\n"
            f"dust_loss_recovery_frac = 0.75\n"
        )

    def _stations_section(self) -> str:
        out = ["\n# Stations — one row per unique station in the design.\n"]
        lines = self.design.get("lines", [])
        family = (
            lines[0].get("rolling_stock", "light-metro-3car")
            if lines else "light-metro-3car"
        )
        cabinet_count = _charging_cabinet_count(family)
        ring_policy = self.design.get("operations", {}).get("ring_service", {})
        ring_dwell_seconds = int(ring_policy.get("minimum_dwell_seconds", 120))
        radial_policy = self.design.get("operations", {}).get("radial_service", {})
        radial_charging_dwell_seconds = int(
            radial_policy.get("minimum_charging_dwell_seconds", 120)
        )
        charging_dwell_by_line = {
            str(line.get("id") or line.get("name")): int(
                line.get(
                    "charging_dwell_seconds",
                    ring_dwell_seconds
                    if line.get("shape") == "ring" or line.get("is_ring")
                    else radial_charging_dwell_seconds,
                )
            )
            for line in self.design.get("lines", [])
        }
        ring_lines = {
            str(line.get("id") or line.get("name"))
            for line in self.design.get("lines", [])
            if line.get("shape") == "ring" or line.get("is_ring")
        }
        depot_by_station = {
            d.get("station") or d.get("station_id"): d
            for d in self.design.get("depots", [])
            if d.get("station") or d.get("station_id")
        }
        depot_station_ids = set(depot_by_station)
        # Exactly one designated powered service point per line gives every
        # operating cycle one clean/inspect/recharge slot. Prefer a physical
        # depot on its owning line; otherwise use a powered passenger terminal
        # (or powered on-ring station). `depot_service` remains the scenario
        # schema field for backward compatibility, but does not imply a depot.
        service_depot_ids: set[str] = set()
        stations_by_line: dict[str, list[dict[str, Any]]] = {}
        for station in self.design.get("stations", []):
            stations_by_line.setdefault(str(station.get("line", "")), []).append(station)
        for line_id, line_stations in stations_by_line.items():
            candidates = [s for s in line_stations if s.get("id") in depot_station_ids]
            if not candidates:
                powered = [
                    s
                    for s in line_stations
                    if int(self.station_defaults(s.get("archetype", "standard")).get("charging_power_kw", 0))
                    >= 150
                ]
                if not powered:
                    raise ValueError(
                        f"line {line_id!r} has no depot or powered passenger "
                        "station for turnaround inspection/recharge"
                    )
                terminals = [
                    s
                    for s in powered
                    if s.get("archetype") in ("terminal", "depot-terminal")
                ]
                service_depot_ids.add(str((terminals or powered)[-1]["id"]))
                continue
            main = next(
                (
                    s
                    for s in candidates
                    if depot_by_station[s["id"]].get("archetype") == "main-heavy"
                ),
                None,
            )
            service_depot_ids.add(str((main or candidates[-1])["id"]))
        for s in self.design.get("stations", []):
            arch = s.get("archetype", "standard")
            d = self.station_defaults(arch)
            line_id = str(s.get("line", ""))
            if int(d.get("charging_power_kw", 0)) > 0:
                d["charging_power_kw"] = int(d["charging_power_kw"]) * cabinet_count
                policy_minimum = (
                    ring_dwell_seconds
                    if line_id in ring_lines
                    else radial_charging_dwell_seconds
                )
                d["dwell_seconds"] = max(
                    int(d.get("dwell_seconds", 0)),
                    policy_minimum,
                    charging_dwell_by_line.get(line_id, policy_minimum),
                )
            out.append(f"[[stations]]\n")
            out.append(f'id = "{_escape(s["id"])}"\n')
            # Display name: prefer explicit `name`, then OSM-derived
            # `anchor_name`, then fall back to the id slug. The rust
            # emitter (`osr-design`) writes `anchor_name` for stations
            # tied to a POI and omits a separate `name` field.
            display_name = (
                s.get("name") or s.get("anchor_name") or s["id"]
            )
            out.append(f'name = "{_escape(display_name)}"\n')
            if d.get("charging_power_kw", 0) > 0:
                out.append(f"charging_power_kw = {d['charging_power_kw']}\n")
            out.append(f"dwell_seconds = {d['dwell_seconds']}\n")
            if arch in ("terminal", "depot-terminal"):
                out.append(f"is_terminal = true\n")
            if d.get("is_depot") or s["id"] in depot_station_ids:
                out.append(f"is_depot = true\n")
            if s["id"] in service_depot_ids:
                out.append(f"depot_service = true\n")
            out.append("\n")
        return "".join(out)

    def _lines_section(self) -> str:
        out = ["\n# Lines — per-line station sequences.\n"]
        # Build a per-line ordered station list once, since the rust
        # `osr-design` emitter writes a flat [[stations]] list keyed
        # by the station's own `line` field rather than nesting them
        # inside [[lines]].
        stations_by_line: dict[str, list[dict[str, Any]]] = {}
        for s in self.design.get("stations", []):
            stations_by_line.setdefault(s.get("line", ""), []).append(s)
        for sts in stations_by_line.values():
            sts.sort(key=lambda s: float(s.get("s_m", 0.0)))
        for line in self.design.get("lines", []):
            # Lines emitted by `osr-design` carry only `name` (which
            # acts as the slug-style id, e.g. "line-1"). Use `name`
            # for both `id` and `name` when no separate `id` exists.
            line_id = line.get("id") or line["name"]
            line_stations = list(stations_by_line.get(line_id, []))
            out.append(f"[[lines]]\n")
            out.append(f'id = "{_escape(line_id)}"\n')
            out.append(f'name = "{_escape(line["name"])}"\n')
            shape = line.get("shape", "")
            if shape == "ring" or line.get("is_ring"):
                out.append(f"is_ring = true\n")
                if "ring_wrap_length_m" in line:
                    wrap_length_m = int(line["ring_wrap_length_m"])
                elif (
                    len(line_stations) >= 2
                    and line_stations[0].get("id") == line_stations[-1].get("id")
                    and float(line_stations[-1].get("s_m", 0.0))
                    > float(line_stations[-2].get("s_m", 0.0))
                ):
                    # Older design snapshots close a ring by repeating the
                    # first station at total line chainage.  The simulator
                    # represents that final leg separately, so remove the
                    # duplicate endpoint and preserve its positive segment.
                    wrap_length_m = round(
                        float(line_stations[-1].get("s_m", 0.0))
                        - float(line_stations[-2].get("s_m", 0.0))
                    )
                    line_stations = line_stations[:-1]
                elif line_stations:
                    wrap_length_m = round(
                        float(line.get("length_m", 0.0))
                        - float(line_stations[-1].get("s_m", 0.0))
                    )
                else:
                    wrap_length_m = 0
                if wrap_length_m <= 0:
                    raise ValueError(
                        f"ring line {line_id!r} has no positive closure segment"
                    )
                out.append(f"ring_wrap_length_m = {wrap_length_m}\n")
            # Prefer an inline `stations = [...]` array if the design
            # carries one (older schema); otherwise synthesise one
            # from the flat station list ordered by `s_m`.
            inline = line.get("stations")
            if inline:
                out.append(f"stations = [\n")
                for st in inline:
                    d = int(st.get("distance_from_prev_m", 0))
                    out.append(
                        f'    {{ id = "{_escape(st["id"])}", distance_from_prev_m = {d} }},\n'
                    )
                out.append(f"]\n\n")
            else:
                out.append(f"stations = [\n")
                prev_s_m = 0.0
                for i, st in enumerate(line_stations):
                    s_m = float(st.get("s_m", 0.0))
                    distance = 0 if i == 0 else int(s_m - prev_s_m)
                    out.append(
                        f'    {{ id = "{_escape(st["id"])}", distance_from_prev_m = {distance} }},\n'
                    )
                    prev_s_m = s_m
                out.append(f"]\n\n")
        return "".join(out)

    def _fleets_section(self) -> str:
        # The rust `osr-design` emitter writes minimal [[fleets]]
        # blocks: line + peak/spare/cold-reserve/total counts. The
        # operational dispatch + schedule fields below are optional
        # (older hand-crafted designs carry them; auto-generated
        # designs default to a 3-min peak / 6-min off-peak headway,
        # 05:30–02:00 service window). All keys defensive — missing
        # ones get sensible auto-gen defaults.
        # Build a per-line list of stations (in s_m order) so we can
        # synthesize default dispatch_points at the line's two termini
        # when the design.toml doesn't carry an explicit list. The rust
        # `osr-design` emitter doesn't pre-compute dispatch points; the
        # rust scenario loader requires `dispatch_points` to be
        # non-empty (otherwise no train ever leaves the depot), so
        # without this synthesis the canonical Samawah scenario fails
        # to load.
        line_stations: dict[str, list[dict]] = {}
        for st in self.design.get("stations", []):
            line_stations.setdefault(st.get("line", ""), []).append(st)
        for stns in line_stations.values():
            stns.sort(key=lambda s: s.get("s_m", 0.0))
        ring_lines = {
            str(line.get("id") or line.get("name"))
            for line in self.design.get("lines", [])
            if line.get("shape") == "ring" or line.get("is_ring")
        }
        ring_policy = self.design.get("operations", {}).get("ring_service", {})

        out = ["\n# Fleets — copied from design.toml [[fleets]].\n"]
        for f in self.design.get("fleets", []):
            line_id = f["line"]
            out.append(f"[[fleets]]\n")
            out.append(f'line = "{_escape(line_id)}"\n')
            out.append(f"trainset_count = {int(f['trainset_count'])}\n")
            dispatch_points = list(f.get("dispatch_points") or [])
            if not dispatch_points:
                stns = line_stations.get(line_id, [])
                if len(stns) >= 2:
                    dispatch_points = [
                        {"station": stns[0]["id"], "heading": "forward"},
                        {"station": stns[-1]["id"], "heading": "reverse"},
                    ]
            out.append(f"dispatch_points = [\n")
            for dp in dispatch_points:
                out.append(
                    f'    {{ station = "{_escape(dp["station"])}", heading = "{_escape(dp["heading"])}" }},\n'
                )
            out.append(f"]\n")
            out.append(f'service_start = "{_escape(f.get("service_start", "05:30"))}"\n')
            out.append(f'service_end = "{_escape(f.get("service_end", "02:00"))}"\n')
            radial_schedule = [
                # Auto-gen default: peak 3-min headway both peaks,
                # 6-min off-peak. Matches RFC 0014 §4 fleet sizing.
                {"from": "05:30", "to": "07:00", "headway_min": 6},
                {"from": "07:00", "to": "09:00", "headway_min": 3},
                {"from": "09:00", "to": "15:00", "headway_min": 6},
                {"from": "15:00", "to": "17:00", "headway_min": 3},
                {"from": "17:00", "to": "23:30", "headway_min": 6},
                {"from": "23:30", "to": "02:00", "headway_min": 12},
            ]
            ring_schedule = [
                {"from": "05:30", "to": "07:00", "headway_min": int(ring_policy.get("off_peak_headway_min", 12))},
                {"from": "07:00", "to": "09:00", "headway_min": int(ring_policy.get("peak_headway_min", 6))},
                {"from": "09:00", "to": "15:00", "headway_min": int(ring_policy.get("off_peak_headway_min", 12))},
                {"from": "15:00", "to": "17:00", "headway_min": int(ring_policy.get("peak_headway_min", 6))},
                {"from": "17:00", "to": "23:30", "headway_min": int(ring_policy.get("off_peak_headway_min", 12))},
                {"from": "23:30", "to": "02:00", "headway_min": int(ring_policy.get("late_headway_min", 24))},
            ]
            schedule = f.get("schedule") or (
                ring_schedule if line_id in ring_lines else radial_schedule
            )
            out.append(f"schedule = [\n")
            for w in schedule:
                out.append(
                    f'    {{ from = "{_escape(w["from"])}", to = "{_escape(w["to"])}", headway_min = {int(w["headway_min"])} }},\n'
                )
            out.append(f"]\n\n")
        return "".join(out)

    def _sites_section(self) -> str:
        # Sites can be either:
        #   (a) declared explicitly in design.toml `[[sites]]` (older
        #       hand-crafted designs), or
        #   (b) synthesised from the station + depot archetypes that the
        #       rust `osr-design` emitter writes (auto-generated designs).
        # Each archetype maps to a default energy-site tier per RFC 0010
        # (stations) + RFC 0014 (depots). The mapping below is the
        # canonical default — explicit `[[sites]]` always wins.
        explicit = self.design.get("sites", [])
        if explicit:
            sites_to_emit = [
                {"station": s["station"], "tier": s.get("tier", "standard"), "_overrides": s}
                for s in explicit
            ]
        else:
            sites_to_emit = self._synthesise_sites_from_archetypes()
        if not sites_to_emit:
            return ""
        lines = self.design.get("lines", [])
        family = (
            lines[0].get("rolling_stock", "light-metro-3car")
            if lines else "light-metro-3car"
        )
        cabinet_count = _charging_cabinet_count(family)
        out = ["\n# Trackside energy sites — expanded from tier references.\n"]
        for s in sites_to_emit:
            tier = s["tier"]
            d = self.site_defaults(tier)
            if cabinet_count > 1:
                d["charger_max_kw"] = float(d.get("charger_max_kw", 500.0)) * cabinet_count
                d["charger_max_current_a"] = float(
                    d.get("charger_max_current_a", 825.0)
                ) * cabinet_count
                d["charger_contact_count"] = int(
                    d.get("charger_contact_count", 2)
                ) * cabinet_count
                d["grid_import_kw"] = float(
                    d.get("grid_import_kw", 500.0)
                ) * cabinet_count
                d["grid_export_kw"] = float(
                    d.get("grid_export_kw", 500.0)
                ) * cabinet_count
                if tier in {"standard", "major", "interchange", "terminal"}:
                    d["storage_capacity_kwh"] = float(
                        d.get("storage_capacity_kwh", 500.0)
                    ) * cabinet_count
                    d["storage_max_charge_kw"] = float(
                        d.get("storage_max_charge_kw", 500.0)
                    ) * cabinet_count
                    d["storage_max_discharge_kw"] = float(
                        d.get("storage_max_discharge_kw", 500.0)
                    ) * cabinet_count
            # Per-site explicit overrides.
            overrides = s.get("_overrides", {})
            for k in (
                "pv_nameplate_kw", "storage_capacity_kwh",
                "storage_max_charge_kw", "storage_max_discharge_kw",
                "storage_initial_soc", "grid_import_kw", "grid_export_kw",
                "storage_module_kwh", "charger_max_kw", "charger_max_current_a",
                "charger_bus_voltage_v", "charger_efficiency", "charger_contact_count",
            ):
                if k in overrides:
                    d[k] = overrides[k]
            out.append(f"[[sites]]\n")
            out.append(f'station = "{_escape(s["station"])}"\n')
            out.append(f'tier = "{_escape(tier)}"\n')
            out.append(f"pv_nameplate_kw = {float(d['pv_nameplate_kw'])}\n")
            out.append(f"storage_capacity_kwh = {float(d['storage_capacity_kwh'])}\n")
            out.append(f"storage_max_charge_kw = {float(d['storage_max_charge_kw'])}\n")
            out.append(f"storage_max_discharge_kw = {float(d['storage_max_discharge_kw'])}\n")
            out.append(f"storage_initial_soc = {float(d['storage_initial_soc'])}\n")
            out.append(f"grid_import_kw = {float(d['grid_import_kw'])}\n")
            out.append(f"grid_export_kw = {float(d['grid_export_kw'])}\n")
            out.append(f"storage_module_kwh = {float(d.get('storage_module_kwh', 500.0))}\n")
            out.append(f"charger_max_kw = {float(d.get('charger_max_kw', 500.0))}\n")
            out.append(f"charger_max_current_a = {float(d.get('charger_max_current_a', 825.0))}\n")
            out.append(f"charger_bus_voltage_v = {float(d.get('charger_bus_voltage_v', 650.0))}\n")
            out.append(f"charger_efficiency = {float(d.get('charger_efficiency', 0.98))}\n")
            out.append(f"charger_contact_count = {int(d.get('charger_contact_count', 2))}\n\n")
        return "".join(out)

    def _synthesise_sites_from_archetypes(self) -> list[dict[str, Any]]:
        sites: list[dict[str, Any]] = []
        seen_stations: set[str] = set()
        # Stations get sites by archetype.
        for s in self.design.get("stations", []):
            arch = s.get("archetype", "standard")
            tier = _STATION_TIER_MAP.get(arch, "")
            if not tier:
                continue
            sites.append({"station": s["id"], "tier": tier})
            seen_stations.add(s["id"])
        # Depots co-located with terminals already have a depot-main
        # site (via `depot-terminal` archetype). Standalone depots add
        # their own site keyed by their station_id, unless that station
        # already emitted one.
        for d in self.design.get("depots", []):
            arch = d.get("archetype", "main-heavy")
            tier = _DEPOT_TIER_MAP.get(arch, "")
            if not tier:
                continue
            # Rust emits depot rows keyed by `station = "..."`; older
            # python-side designs used `station_id`. Accept both.
            station_id = d.get("station") or d.get("station_id")
            if not station_id:
                continue
            if station_id in seen_stations:
                # A depot tier supersedes the passenger-station tier at the
                # same terminal; one physical microgrid supplies both.
                for site in sites:
                    if site["station"] == station_id:
                        site["tier"] = tier
                        break
                continue
            sites.append({"station": station_id, "tier": tier})
            seen_stations.add(station_id)
        return sites


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def generate_scenario(
    design: dict[str, Any],
    design_path: Path,
    templates_root: Path,
) -> str:
    """Convert a loaded design dict into a scenario TOML string."""
    gen = ScenarioGenerator(
        design=design, design_path=design_path, templates_root=templates_root
    )
    return gen.emit()


def generate_from_path(
    design_path: Path,
    templates_root: Path | None = None,
) -> str:
    """Read `design_path` + generate the scenario TOML."""
    if templates_root is None:
        # Walk up from the design file looking for `lib/templates/`
        # (post-reorg; the old `designs/templates/` is kept as a
        # fallback so any in-flight branch still resolves).
        cur = design_path.parent
        for _ in range(10):
            for rel in ("lib/templates", "templates", "designs/templates"):
                candidate = cur / rel
                if candidate.exists() and (candidate / "stations.toml").exists():
                    templates_root = candidate
                    break
            if templates_root is not None:
                break
            if cur.parent == cur:
                break
            cur = cur.parent
        if templates_root is None:
            raise GeneratorError(
                f"could not locate lib/templates/ starting from {design_path}"
            )
    design = tomllib.loads(design_path.read_text())
    return generate_scenario(design, design_path, templates_root)


def _escape(s: str) -> str:
    """Minimal TOML string escape."""
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def _scenario_name(design: dict[str, Any]) -> str:
    design_meta = design.get("design", {})
    city_meta = design.get("city", {})
    return (
        design_meta.get("name")
        or city_meta.get("name")
        or _title_from_slug(city_meta.get("slug") or design_meta.get("id"))
        or "Unnamed"
    )


def _title_from_slug(slug: Any) -> str:
    if not slug:
        return ""
    parts = str(slug).replace("_", "-").split("-")
    return " ".join(part.capitalize() for part in parts if part)

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
    "halt":           {"charging_power_kw": 0,    "dwell_seconds": 20,  "is_depot": False},
    "standard":       {"charging_power_kw": 0,    "dwell_seconds": 30,  "is_depot": False},
    "major":          {"charging_power_kw": 500,  "dwell_seconds": 45,  "is_depot": False},
    "interchange":    {"charging_power_kw": 500,  "dwell_seconds": 45,  "is_depot": False},
    "terminal":       {"charging_power_kw": 1000, "dwell_seconds": 60,  "is_depot": False},
    "depot-terminal": {"charging_power_kw": 1000, "dwell_seconds": 240, "is_depot": True},
}

# Per-tier energy-site operational defaults.
_SITE_TIER_DEFAULTS: dict[str, dict[str, float]] = {
    "standard":        {"pv_nameplate_kw": 300.0,  "storage_capacity_kwh": 2000.0,
                         "storage_max_charge_kw": 800.0,  "storage_max_discharge_kw": 800.0,
                         "storage_initial_soc": 0.5,  "grid_import_kw": 500.0, "grid_export_kw": 500.0},
    "major":           {"pv_nameplate_kw": 400.0,  "storage_capacity_kwh": 2500.0,
                         "storage_max_charge_kw": 1000.0, "storage_max_discharge_kw": 1000.0,
                         "storage_initial_soc": 0.5,  "grid_import_kw": 600.0, "grid_export_kw": 600.0},
    "interchange":     {"pv_nameplate_kw": 500.0,  "storage_capacity_kwh": 3000.0,
                         "storage_max_charge_kw": 1000.0, "storage_max_discharge_kw": 1000.0,
                         "storage_initial_soc": 0.5,  "grid_import_kw": 600.0, "grid_export_kw": 600.0},
    "terminal":        {"pv_nameplate_kw": 500.0,  "storage_capacity_kwh": 3000.0,
                         "storage_max_charge_kw": 1500.0, "storage_max_discharge_kw": 1500.0,
                         "storage_initial_soc": 0.6,  "grid_import_kw": 800.0, "grid_export_kw": 800.0},
    "depot-secondary": {"pv_nameplate_kw": 1500.0, "storage_capacity_kwh": 5000.0,
                         "storage_max_charge_kw": 2000.0, "storage_max_discharge_kw": 2000.0,
                         "storage_initial_soc": 0.6,  "grid_import_kw": 1000.0, "grid_export_kw": 1000.0},
    "depot-main":      {"pv_nameplate_kw": 5000.0, "storage_capacity_kwh": 40000.0,
                         "storage_max_charge_kw": 10000.0, "storage_max_discharge_kw": 10000.0,
                         "storage_initial_soc": 0.7,  "grid_import_kw": 3000.0, "grid_export_kw": 3000.0},
}

# Climate preset → ambient temperature (sim design ambient).
_CLIMATE_PRESET_AMBIENT_C: dict[str, float] = {
    "hot-desert":       42.0,
    "humid-tropical":   38.0,
    "temperate":        28.0,
    "continental":      30.0,
    "mediterranean":    35.0,
}

# Consist family → summary physical parameters (light-metro-3car etc.).
# Authoritative numbers live in `lib/templates/rolling-stock.toml`;
# values here are the sim-critical subset.
_CONSIST_DEFAULTS: dict[str, dict[str, int | float]] = {
    "tram-2car":        {"car_count": 2, "length_m": 32,  "mass_kg": 66_000,  "max_speed_kmh": 80.0, "battery_capacity_kwh": 180,  "service_accel_mps2": 1.0},
    "light-metro-3car": {"car_count": 3, "length_m": 68,  "mass_kg": 120_000, "max_speed_kmh": 80.0, "battery_capacity_kwh": 320,  "service_accel_mps2": 1.0},
    "metro-4car":       {"car_count": 4, "length_m": 90,  "mass_kg": 160_000, "max_speed_kmh": 90.0, "battery_capacity_kwh": 460,  "service_accel_mps2": 1.1},
    "metro-6car":       {"car_count": 6, "length_m": 138, "mass_kg": 240_000, "max_speed_kmh": 90.0, "battery_capacity_kwh": 720,  "service_accel_mps2": 1.1},
}


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

    # ------ Resolution helpers ------

    def station_defaults(self, archetype: str) -> dict[str, Any]:
        """Resolve operational defaults for a station archetype."""
        tpl = self.station_archetypes.get(archetype, {})
        out = dict(_STATION_ARCHETYPE_DEFAULTS.get(archetype, {}))
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
        out: list[str] = []
        out.append(self._scenario_header())
        out.append(self._climate_section())
        out.append(self._consist_section())
        out.append(self._stations_section())
        out.append(self._lines_section())
        out.append(self._fleets_section())
        out.append(self._sites_section())
        return "\n".join(out).rstrip() + "\n"

    # ---- section builders ----

    def _scenario_header(self) -> str:
        name = self.design.get("design", {}).get("name", "Unnamed")
        slug = self.design.get("design", {}).get("id", "unnamed")
        return (
            f"# AUTO-GENERATED from {self.design_path}.\n"
            f"# Do not hand-edit; run `python -m osr_scenario --design ...` to regenerate.\n"
            f"# Source of truth: {self.design_path}\n"
            f"\n"
            f"[scenario]\n"
            f'name = "{_escape(name)}"\n'
            f'start_time = "06:00"\n'
        )

    def _climate_section(self) -> str:
        clim = self.design.get("climate", {})
        preset = clim.get("preset", "temperate")
        ambient = _CLIMATE_PRESET_AMBIENT_C.get(preset, 28.0)
        psh = clim.get("peak_sun_hours", 5.0)
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
        return (
            f"\n[consist]\n"
            f"# From rolling-stock family '{family}'.\n"
            f"car_count = {cd['car_count']}\n"
            f"length_m = {cd['length_m']}\n"
            f"mass_kg = {cd['mass_kg']}\n"
            f"max_speed_kmh = {cd['max_speed_kmh']}\n"
            f"battery_capacity_kwh = {cd['battery_capacity_kwh']}\n"
            f"service_accel_mps2 = {cd['service_accel_mps2']}\n"
        )

    def _stations_section(self) -> str:
        out = ["\n# Stations — one row per unique station in the design.\n"]
        for s in self.design.get("stations", []):
            arch = s.get("archetype", "standard")
            d = self.station_defaults(arch)
            out.append(f"[[stations]]\n")
            out.append(f'id = "{_escape(s["id"])}"\n')
            out.append(f'name = "{_escape(s["name"])}"\n')
            if d.get("charging_power_kw", 0) > 0:
                out.append(f"charging_power_kw = {d['charging_power_kw']}\n")
            out.append(f"dwell_seconds = {d['dwell_seconds']}\n")
            if arch in ("terminal", "depot-terminal"):
                out.append(f"is_terminal = true\n")
            if d.get("is_depot"):
                out.append(f"is_depot = true\n")
            out.append("\n")
        return "".join(out)

    def _lines_section(self) -> str:
        out = ["\n# Lines — per-line station sequences.\n"]
        for line in self.design.get("lines", []):
            out.append(f"[[lines]]\n")
            out.append(f'id = "{_escape(line["id"])}"\n')
            out.append(f'name = "{_escape(line["name"])}"\n')
            if line.get("is_ring"):
                out.append(f"is_ring = true\n")
                if "ring_wrap_length_m" in line:
                    out.append(
                        f"ring_wrap_length_m = {int(line['ring_wrap_length_m'])}\n"
                    )
            out.append(f"stations = [\n")
            for st in line.get("stations", []):
                d = int(st.get("distance_from_prev_m", 0))
                out.append(
                    f'    {{ id = "{_escape(st["id"])}", distance_from_prev_m = {d} }},\n'
                )
            out.append(f"]\n\n")
        return "".join(out)

    def _fleets_section(self) -> str:
        out = ["\n# Fleets — copied from design.toml [[fleets]].\n"]
        for f in self.design.get("fleets", []):
            out.append(f"[[fleets]]\n")
            out.append(f'line = "{_escape(f["line"])}"\n')
            out.append(f"trainset_count = {int(f['trainset_count'])}\n")
            out.append(f"dispatch_points = [\n")
            for dp in f.get("dispatch_points", []):
                out.append(
                    f'    {{ station = "{_escape(dp["station"])}", heading = "{_escape(dp["heading"])}" }},\n'
                )
            out.append(f"]\n")
            out.append(f'service_start = "{_escape(f.get("service_start", "05:30"))}"\n')
            out.append(f'service_end = "{_escape(f.get("service_end", "23:30"))}"\n')
            out.append(f"schedule = [\n")
            for w in f.get("schedule", []):
                out.append(
                    f'    {{ from = "{_escape(w["from"])}", to = "{_escape(w["to"])}", headway_min = {int(w["headway_min"])} }},\n'
                )
            out.append(f"]\n\n")
        return "".join(out)

    def _sites_section(self) -> str:
        sites = self.design.get("sites", [])
        if not sites:
            return ""
        out = ["\n# Trackside energy sites — expanded from tier references.\n"]
        for s in sites:
            tier = s.get("tier", "standard")
            d = self.site_defaults(tier)
            # Per-site explicit overrides.
            for k in (
                "pv_nameplate_kw", "storage_capacity_kwh",
                "storage_max_charge_kw", "storage_max_discharge_kw",
                "storage_initial_soc", "grid_import_kw", "grid_export_kw",
            ):
                if k in s:
                    d[k] = s[k]
            out.append(f"[[sites]]\n")
            out.append(f'station = "{_escape(s["station"])}"\n')
            out.append(f"pv_nameplate_kw = {float(d['pv_nameplate_kw'])}\n")
            out.append(f"storage_capacity_kwh = {float(d['storage_capacity_kwh'])}\n")
            out.append(f"storage_max_charge_kw = {float(d['storage_max_charge_kw'])}\n")
            out.append(f"storage_max_discharge_kw = {float(d['storage_max_discharge_kw'])}\n")
            out.append(f"storage_initial_soc = {float(d['storage_initial_soc'])}\n")
            out.append(f"grid_import_kw = {float(d['grid_import_kw'])}\n")
            out.append(f"grid_export_kw = {float(d['grid_export_kw'])}\n\n")
        return "".join(out)


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

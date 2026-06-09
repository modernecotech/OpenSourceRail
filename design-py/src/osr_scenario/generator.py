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
    "halt":                 {"charging_power_kw": 250,  "dwell_seconds": 60,  "is_depot": False},
    "standard":             {"charging_power_kw": 500,  "dwell_seconds": 60,  "is_depot": False},
    "major":                {"charging_power_kw": 500,  "dwell_seconds": 60,  "is_depot": False},
    "interchange":          {"charging_power_kw": 500,  "dwell_seconds": 60,  "is_depot": False},
    "interchange-elevated": {"charging_power_kw": 500,  "dwell_seconds": 60,  "is_depot": False},
    "terminal":             {"charging_power_kw": 1000, "dwell_seconds": 60,  "is_depot": False},
    "depot-terminal":       {"charging_power_kw": 1000, "dwell_seconds": 240, "is_depot": True},
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

# Archetype → energy-site tier mapping (used when design.toml carries
# no explicit `[[sites]]` blocks — i.e. auto-generated designs from
# `osr-design`). Halts get no trackside energy (shelter-only stops);
# standard / major / interchange / terminal each take the matching
# tier from energy-sites.toml. `depot-terminal` stations colocate the
# main depot's microgrid. Standalone depots by archetype: main-heavy
# = depot-main, secondary-medium = depot-secondary, layup-minimal =
# no site (overnight stabling only, no infrastructure).
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
    "layup-minimal": "",  # no site
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
    "urban-shuttle-1car": {"car_count": 1, "length_m": 21,  "mass_kg": 34_000,  "max_speed_kmh": 70.0,  "battery_capacity_kwh": 120, "passenger_capacity": 100, "seat_count": 20,  "crush_capacity": 130, "service_accel_mps2": 1.0},
    "tram-2car":          {"car_count": 2, "length_m": 39,  "mass_kg": 68_000,  "max_speed_kmh": 70.0,  "battery_capacity_kwh": 240, "passenger_capacity": 240, "seat_count": 40,  "crush_capacity": 320, "service_accel_mps2": 1.0},
    "light-metro-3car":   {"car_count": 3, "length_m": 51,  "mass_kg": 102_000, "max_speed_kmh": 90.0,  "battery_capacity_kwh": 360, "passenger_capacity": 360, "seat_count": 60,  "crush_capacity": 480, "service_accel_mps2": 1.0},
    "metro-4car":         {"car_count": 4, "length_m": 75,  "mass_kg": 136_000, "max_speed_kmh": 90.0,  "battery_capacity_kwh": 480, "passenger_capacity": 480, "seat_count": 80,  "crush_capacity": 640, "service_accel_mps2": 1.1},
    "metro-6car":         {"car_count": 6, "length_m": 111, "mass_kg": 204_000, "max_speed_kmh": 100.0, "battery_capacity_kwh": 720, "passenger_capacity": 720, "seat_count": 120, "crush_capacity": 960, "service_accel_mps2": 1.1},
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
        source_path = self._display_design_path()
        return (
            f"# AUTO-GENERATED from {source_path}.\n"
            f"# Do not hand-edit; run `python -m osr_scenario --design ...` to regenerate.\n"
            f"# Source of truth: {source_path}\n"
            f"\n"
            f"[scenario]\n"
            f'name = "{_escape(name)}"\n'
            f'start_time = "06:00"\n'
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
            f"passenger_capacity = {cd['passenger_capacity']}\n"
            f"seat_count = {cd['seat_count']}\n"
            f"crush_capacity = {cd['crush_capacity']}\n"
            f"service_accel_mps2 = {cd['service_accel_mps2']}\n"
        )

    def _stations_section(self) -> str:
        out = ["\n# Stations — one row per unique station in the design.\n"]
        for s in self.design.get("stations", []):
            arch = s.get("archetype", "standard")
            d = self.station_defaults(arch)
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
            if d.get("is_depot"):
                out.append(f"is_depot = true\n")
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
            out.append(f"[[lines]]\n")
            out.append(f'id = "{_escape(line_id)}"\n')
            out.append(f'name = "{_escape(line["name"])}"\n')
            shape = line.get("shape", "")
            if shape == "ring" or line.get("is_ring"):
                out.append(f"is_ring = true\n")
                if "ring_wrap_length_m" in line:
                    out.append(
                        f"ring_wrap_length_m = {int(line['ring_wrap_length_m'])}\n"
                    )
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
                line_stations = stations_by_line.get(line_id, [])
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
            schedule = f.get("schedule") or [
                # Auto-gen default: peak 3-min headway both peaks,
                # 6-min off-peak. Matches RFC 0014 §4 fleet sizing.
                {"from": "05:30", "to": "07:00", "headway_min": 6},
                {"from": "07:00", "to": "10:00", "headway_min": 3},
                {"from": "10:00", "to": "16:00", "headway_min": 6},
                {"from": "16:00", "to": "19:00", "headway_min": 3},
                {"from": "19:00", "to": "23:30", "headway_min": 6},
                {"from": "23:30", "to": "02:00", "headway_min": 12},
            ]
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
        out = ["\n# Trackside energy sites — expanded from tier references.\n"]
        for s in sites_to_emit:
            tier = s["tier"]
            d = self.site_defaults(tier)
            # Per-site explicit overrides.
            overrides = s.get("_overrides", {})
            for k in (
                "pv_nameplate_kw", "storage_capacity_kwh",
                "storage_max_charge_kw", "storage_max_discharge_kw",
                "storage_initial_soc", "grid_import_kw", "grid_export_kw",
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
            out.append(f"grid_export_kw = {float(d['grid_export_kw'])}\n\n")
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
            if not station_id or station_id in seen_stations:
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

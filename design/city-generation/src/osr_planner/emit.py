"""Emit a `design.toml` from a planned network.

Takes the planner's in-memory plan (stations + lines) and produces
the same TOML schema `osr_scenario` consumes. Keeps all downstream
tooling (scenario generation, map rendering, stats, drift tests)
working unchanged for auto-planned cities.
"""

from __future__ import annotations

import math

from .anchors import haversine_m
from .lines import LinePlan
from .stations import StationCandidate


def design_toml(
    *,
    slug: str,
    country_iso: str,
    city_name: str,
    center_lat: float,
    center_lon: float,
    bbox: tuple[float, float, float, float],
    population: int,
    climate_preset: str,
    peak_sun_hours: float,
    stations: list[StationCandidate],
    lines: list[LinePlan],
    fleet_size_per_line: "callable | None" = None,
) -> str:
    """Format the network as a valid `design.toml` string."""

    out: list[str] = []
    out.append(_header(slug, city_name))
    out.append(_design_block(slug, city_name))
    out.append(_location_block(country_iso, city_name, center_lat, center_lon, bbox))
    out.append(_climate_block(climate_preset, peak_sun_hours))
    out.append(_fare_cost_blocks(country_iso))

    # Identify multi-line stations → interchange archetype.
    memberships: dict[str, list[str]] = {s.id: [] for s in stations}
    for line in lines:
        for sid in line.station_ids:
            memberships.setdefault(sid, []).append(line.id)
    archetype_for: dict[str, str] = {s.id: s.archetype for s in stations}
    for sid, lines_here in memberships.items():
        if len(lines_here) >= 2 and archetype_for.get(sid) not in ("terminal", "depot-terminal"):
            archetype_for[sid] = "interchange"
    # Mark terminals from each line.
    for line in lines:
        if not line.station_ids:
            continue
        a, b = line.station_ids[0], line.station_ids[-1]
        for t in (a, b):
            if archetype_for.get(t) == "standard":
                archetype_for[t] = "terminal"

    out.append(_stations_block(stations, archetype_for))
    out.append(_lines_block(lines, stations))
    out.append(_fleets_block(lines, stations, fleet_size_per_line))
    out.append(_sites_block(stations, archetype_for))
    out.append(_depots_block(lines, stations, archetype_for))
    out.append(_wayside_block(lines, stations, archetype_for))
    out.append(_phases_block(lines))

    return "\n".join(out).rstrip() + "\n"


def _header(slug: str, city_name: str) -> str:
    return (
        f"# AUTO-GENERATED from osr_planner for {city_name!r}.\n"
        f"# Regenerate with:\n"
        f"#   python -m osr_planner --slug {slug} --bbox ... --population ...\n"
        f"# Every station is a real OSM anchor; every line is PCA-ordered\n"
        f"# for low curvature; interchanges are auto-promoted so any OD pair\n"
        f"# is reachable in ≤ 1 transfer.\n"
    )


def _design_block(slug: str, city_name: str) -> str:
    return (
        f"\n[design]\n"
        f'schema_version = 1\n'
        f'id            = "{slug}"\n'
        f'name          = "{_esc(city_name)} — auto-planned"\n'
        f'scenario_out  = "cities/catalogue/{slug}/{_leaf(slug).lower()}.toml"\n'
        f'\n'
        f"[design.templates]\n"
        + "".join(
            f'{k:<16} = "lib/templates/{v}.toml"\n'
            for k, v in [
                ("rolling_stock", "rolling-stock"),
                ("stations", "stations"),
                ("energy_sites", "energy-sites"),
                ("climate", "climate"),
                ("structures", "structures"),
                ("depots", "depots"),
                ("signalling", "signalling"),
                ("comms", "comms"),
                ("switches", "switches"),
                ("level_crossings", "level-crossings"),
                ("accessibility", "accessibility"),
                ("platform_doors", "platform-doors"),
                ("passenger_info", "passenger-info"),
                ("fare_systems", "fare-systems"),
                ("track_geometry", "track-geometry"),
                ("country_costs", "country-costs"),
                ("fleet_sizing", "fleet-sizing"),
                ("demand_profiles", "demand-profiles"),
                ("service_hours", "service-hours"),
                ("climate_adapters", "climate-adapters"),
            ]
        )
    )


def _location_block(
    iso: str, city: str, lat: float, lon: float,
    bbox: tuple[float, float, float, float],
) -> str:
    s, w, n, e = bbox
    return (
        f"\n[location]\n"
        f'country     = "{iso}"\n'
        f'city        = "{_esc(city)}"\n'
        f"center_lat  = {lat:.4f}\n"
        f"center_lon  = {lon:.4f}\n"
        f"bbox        = {{ south = {s:.3f}, west = {w:.3f}, north = {n:.3f}, east = {e:.3f} }}\n"
    )


def _climate_block(preset: str, psh: float) -> str:
    return (
        f"\n[climate]\n"
        f'preset         = "{preset}"\n'
        f"peak_sun_hours = {psh}\n"
    )


def _fare_cost_blocks(iso: str) -> str:
    return (
        f'\n[fare]\nsystem = "generic-qr"\n'
        f'\n[costs]\ncountry = "{iso}"\n'
    )


def _stations_block(
    stations: list[StationCandidate],
    archetype_for: dict[str, str],
) -> str:
    lines = ["\n# Stations — one row per unique station in the plan.\n"]
    for s in stations:
        lines.append(f"[[stations]]\n")
        lines.append(f'id        = "{s.id}"\n')
        lines.append(f'name      = "{_esc(s.name)}"\n')
        lines.append(f'archetype = "{archetype_for.get(s.id, s.archetype)}"\n')
        lines.append(f"lat       = {s.lat:.4f}\n")
        lines.append(f"lon       = {s.lon:.4f}\n\n")
    return "".join(lines)


def _lines_block(
    lines: list[LinePlan], stations: list[StationCandidate]
) -> str:
    by_id = {s.id: s for s in stations}
    out = ["\n# Lines — PCA-ordered station sequences.\n"]
    for line in lines:
        out.append(f"[[lines]]\n")
        out.append(f'id                    = "{line.id}"\n')
        out.append(f'name                  = "{_esc(line.name)}"\n')
        out.append(f"is_ring               = false\n")
        out.append(f'rolling_stock         = "light-metro-3car"\n')
        out.append(f'geometry              = "standard-urban"\n')
        out.append(f'comms_backbone        = "single-ring-10g"\n')
        out.append(f'service_hours         = "conservative-religious"\n')
        out.append(f"track_count           = 2\n")
        out.append(f"default_max_speed_mps = 22\n")
        out.append(f"stations = [\n")
        prev: tuple[float, float] | None = None
        for sid in line.station_ids:
            s = by_id.get(sid)
            if s is None:
                continue
            dist = 0 if prev is None else int(round(haversine_m(prev, (s.lat, s.lon))))
            out.append(
                f'    {{ id = "{sid}", distance_from_prev_m = {dist}, civil_class = "at-grade" }},\n'
            )
            prev = (s.lat, s.lon)
        out.append(f"]\n")
        # Track-polyline from the planner. Shared downstream so the
        # renderer draws the line the planner actually chose — the
        # per-station-pair shortest-path the renderer would otherwise
        # recompute can take long arterial detours between two
        # stations whose planner-level path was part of a larger,
        # already-solved shortest walk.
        if line.polyline:
            out.append("track_polyline = [\n")
            for lat, lon in line.polyline:
                out.append(f"    [{lat:.6f}, {lon:.6f}],\n")
            out.append("]\n")
        out.append("\n")
    return "".join(out)


def _fleets_block(
    lines: list[LinePlan],
    stations: list[StationCandidate],
    fleet_size_per_line: "callable | None",
) -> str:
    by_id = {s.id: s for s in stations}
    if fleet_size_per_line is None:
        # Default: roughly 1 trainset per 3 km of route.
        def fleet_size_per_line(line: LinePlan) -> int:
            pts = [
                (by_id[sid].lat, by_id[sid].lon)
                for sid in line.station_ids if sid in by_id
            ]
            total_m = sum(haversine_m(a, b) for a, b in zip(pts, pts[1:]))
            return max(3, min(10, round(total_m / 3_000)))
    out = ["\n# Fleets — one entry per line.\n"]
    for line in lines:
        if not line.station_ids:
            continue
        n_train = fleet_size_per_line(line)
        a, b = line.station_ids[0], line.station_ids[-1]
        out.append(f"[[fleets]]\n")
        out.append(f'line                = "{line.id}"\n')
        out.append(f"trainset_count      = {n_train}\n")
        out.append(f"spare_count         = 1\n")
        out.append(f"cold_reserve_count  = 1\n")
        out.append(f"dispatch_points = [\n")
        out.append(f'    {{ station = "{a}", heading = "forward" }},\n')
        out.append(f'    {{ station = "{b}", heading = "reverse" }},\n')
        out.append(f"]\n")
        out.append(f'service_start = "05:30"\n')
        out.append(f'service_end   = "23:30"\n')
        out.append(f"schedule = [\n")
        for w in _default_schedule():
            out.append(
                f'    {{ from = "{w[0]}", to = "{w[1]}", headway_min = {w[2]} }},\n'
            )
        out.append(f"]\n\n")
    return "".join(out)


def _default_schedule() -> list[tuple[str, str, int]]:
    return [
        ("05:30", "07:00", 10),
        ("07:00", "09:00", 5),
        ("09:00", "15:00", 8),
        ("15:00", "17:00", 5),
        ("17:00", "22:00", 10),
        ("22:00", "23:30", 15),
    ]


def _sites_block(
    stations: list[StationCandidate],
    archetype_for: dict[str, str],
) -> str:
    """One site per interchange / terminal / major / depot."""
    out = ["\n# Trackside energy sites.\n"]
    tier_for = {
        "terminal":       "terminal",
        "depot-terminal": "depot-main",
        "interchange":    "interchange",
        "major":          "major",
        "standard":       None,
    }
    for s in stations:
        tier = tier_for.get(archetype_for.get(s.id, s.archetype))
        if tier is None:
            continue
        out.append(f"[[sites]]\n")
        out.append(f'station = "{s.id}"\n')
        out.append(f'tier    = "{tier}"\n\n')
    return "".join(out)


def _depots_block(
    lines: list[LinePlan],
    stations: list[StationCandidate],
    archetype_for: dict[str, str],
) -> str:
    """Main depot at the highest-index line's first terminal (to push
    depots to the edge of the network). Secondary layup at the last
    line's second terminal."""
    if not lines or not stations:
        return ""
    # Pick terminals as depot candidates.
    terminals = [
        sid for sid, a in archetype_for.items()
        if a in ("terminal", "depot-terminal")
    ]
    if not terminals:
        return ""
    main = terminals[0]
    layup = terminals[-1] if len(terminals) > 1 else None
    fleet_total = sum(max(5, round(_line_length_km(L, stations) / 3)) for L in lines)
    stalls = min(20, max(8, round(fleet_total * 1.25)))

    parts = ["\n# Depots — main + secondary layup.\n"]
    parts.append(f"[[depots]]\n")
    parts.append(f'station            = "{main}"\n')
    parts.append(f'archetype          = "main-heavy"\n')
    parts.append(f"fleet_stalls       = {stalls}\n")
    parts.append(f"pv_canopy_m2       = {stalls * 400}\n")
    parts.append(f"pv_nominal_kwp     = {stalls * 60}\n")
    parts.append(f"battery_kwh        = {stalls * 200}\n")
    parts.append(f"wheel_lathe        = true\n")
    parts.append(f"overhaul_bay       = true\n")
    parts.append(f"wash_track         = true\n")
    parts.append(f"has_training_wing  = true\n\n")
    if layup and layup != main:
        parts.append(f"[[depots]]\n")
        parts.append(f'station            = "{layup}"\n')
        parts.append(f'archetype          = "layup-minimal"\n')
        parts.append(f"fleet_stalls       = 4\n")
        parts.append(f"pv_canopy_m2       = 800\n")
        parts.append(f"pv_nominal_kwp     = 120\n")
        parts.append(f"battery_kwh        = 250\n")
        parts.append(f"wheel_lathe        = false\n")
        parts.append(f"overhaul_bay       = false\n")
        parts.append(f"wash_track         = false\n")
        parts.append(f"has_training_wing  = false\n\n")
    return "".join(parts)


def _line_length_km(line: LinePlan, stations: list[StationCandidate]) -> float:
    by_id = {s.id: s for s in stations}
    pts = [
        (by_id[sid].lat, by_id[sid].lon)
        for sid in line.station_ids if sid in by_id
    ]
    return sum(haversine_m(a, b) for a, b in zip(pts, pts[1:])) / 1000.0


def _wayside_block(
    lines: list[LinePlan],
    stations: list[StationCandidate],
    archetype_for: dict[str, str],
) -> str:
    out = ["\n# Wayside consensus peers.\n"]
    out.append("wayside_nodes = [\n")
    for line in lines:
        for sid in line.station_ids:
            arch = archetype_for.get(sid, "standard")
            if arch == "depot-terminal" or arch == "terminal":
                kit = "depot-throat"
            elif arch == "interchange":
                kit = "interlocking"
            else:
                kit = "station"
            out.append(
                f'    {{ station = "{sid}", kit = "{kit}", comms = "dual-5g-lora", region = "{line.id}" }},\n'
            )
    out.append("]\n")
    return "".join(out)


def _phases_block(lines: list[LinePlan]) -> str:
    """One phase per line; first line is Phase A."""
    out = ["\n# Construction phases — one per line.\n"]
    for i, line in enumerate(lines):
        out.append(f"[[phases]]\n")
        out.append(f'id              = "{chr(ord("A") + i)}"\n')
        out.append(f'name            = "{_esc(line.name)}"\n')
        out.append(f"stations        = [\n")
        for sid in line.station_ids:
            out.append(f'    "{sid}",\n')
        out.append(f"]\n")
        out.append(f"duration_months = 24\n\n")
    return "".join(out)


def _esc(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def _leaf(slug: str) -> str:
    return slug.rsplit("/", 1)[-1]

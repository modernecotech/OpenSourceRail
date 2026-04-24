"""Compute summary statistics for a city design.

Used for:
- Regenerating the §3.4 system-totals table in the deployment RFC.
- CI drift-detection: fail the test if RFC prose contradicts design.toml.
- One-line queries from a shell: `python -m osr_scenario.stats`.
"""

from __future__ import annotations

import argparse
import math
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DesignStats:
    slug: str
    name: str
    line_count: int
    unique_station_count: int
    route_km: float
    revenue_fleet: int
    spare_fleet: int
    cold_reserve_fleet: int
    total_fleet: int
    depot_count: int
    interchange_count: int  # unique stations that appear on ≥ 2 lines
    peak_headway_min: float

    @property
    def total_with_reserve(self) -> int:
        return self.revenue_fleet + self.spare_fleet + self.cold_reserve_fleet

    def as_markdown_table(self) -> str:
        lines = [
            "| Metric | Value |",
            "|---|---|",
            f"| Route-km (double track) | ~{self.route_km:.0f} km |",
            f"| Stations (unique) | {self.unique_station_count} |",
            f"| Lines | {self.line_count} |",
            f"| Multi-line interchanges | {self.interchange_count} |",
            f"| Fleet (revenue) | {self.revenue_fleet} × trainsets |",
            f"| Fleet (spare + cold-reserve) | {self.spare_fleet + self.cold_reserve_fleet} × trainsets |",
            f"| Fleet (total) | {self.total_with_reserve} × trainsets |",
            f"| Depots | {self.depot_count} |",
            f"| Best peak headway | {self.peak_headway_min:.0f} min |",
        ]
        return "\n".join(lines)


def compute_stats(design_path: Path) -> DesignStats:
    doc = tomllib.loads(design_path.read_text())

    slug = doc.get("design", {}).get("id", "unknown")
    name = doc.get("design", {}).get("name", "unnamed")

    stations = doc.get("stations", [])
    lines = doc.get("lines", [])
    fleets = doc.get("fleets", [])
    depots = doc.get("depots", [])

    # Route length: sum distance_from_prev_m in each line.
    route_m = 0
    for line in lines:
        for st in line.get("stations", []):
            route_m += int(st.get("distance_from_prev_m", 0))
        if line.get("is_ring"):
            route_m += int(line.get("ring_wrap_length_m", 0))
    route_km = route_m / 1000.0

    # Fleet totals.
    revenue = sum(int(f.get("trainset_count", 0)) for f in fleets)
    spare = sum(int(f.get("spare_count", 0)) for f in fleets)
    cold = sum(int(f.get("cold_reserve_count", 0)) for f in fleets)

    # Count stations that appear on multiple lines (interchanges).
    appearances: dict[str, int] = {}
    for line in lines:
        for st in line.get("stations", []):
            appearances[st["id"]] = appearances.get(st["id"], 0) + 1
    interchange_count = sum(1 for v in appearances.values() if v > 1)

    # Peak headway: smallest `headway_min` across all fleets' schedules.
    peak_headway = math.inf
    for f in fleets:
        for w in f.get("schedule", []):
            peak_headway = min(peak_headway, float(w.get("headway_min", math.inf)))
    if peak_headway == math.inf:
        peak_headway = 0.0

    return DesignStats(
        slug=slug,
        name=name,
        line_count=len(lines),
        unique_station_count=len(stations),
        route_km=route_km,
        revenue_fleet=revenue,
        spare_fleet=spare,
        cold_reserve_fleet=cold,
        total_fleet=revenue + spare + cold,
        depot_count=len(depots),
        interchange_count=interchange_count,
        peak_headway_min=peak_headway,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="osr_scenario.stats",
        description="Compute summary stats for a city design.toml.",
    )
    ap.add_argument("--design", type=Path, default=None)
    ap.add_argument(
        "--format",
        choices=["markdown", "plain"],
        default="plain",
    )
    args = ap.parse_args(argv)
    if args.design is None:
        args.design = _find_repo_root() / "designs/middle-east/iraq/samawah/design.toml"
    s = compute_stats(args.design)
    if args.format == "markdown":
        print(s.as_markdown_table())
    else:
        print(f"design:           {s.name}")
        print(f"lines:            {s.line_count}")
        print(f"unique stations:  {s.unique_station_count}")
        print(f"interchanges:     {s.interchange_count}")
        print(f"route:            {s.route_km:.1f} km")
        print(f"revenue fleet:    {s.revenue_fleet}")
        print(f"spare + reserve:  {s.spare_fleet + s.cold_reserve_fleet}")
        print(f"depots:           {s.depot_count}")
        print(f"peak headway:     {s.peak_headway_min:.0f} min")
    return 0


def _find_repo_root() -> Path:
    cur = Path(__file__).resolve()
    for parent in cur.parents:
        if (parent / "Cargo.toml").exists():
            return parent
    return Path.cwd()


if __name__ == "__main__":
    raise SystemExit(main())

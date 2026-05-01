#!/usr/bin/env python3
"""Generate `designs/INDEX.md` from city `design.toml` files."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGNS = REPO_ROOT / "designs"
OUT = DESIGNS / "INDEX.md"


def _load(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def _coverage(city_dir: Path) -> float:
    matches = list(city_dir.glob("*.design-quality.yaml"))
    if not matches:
        return 0.0
    text = matches[0].read_text()
    m = re.search(r"coverage_score:\s*([0-9.]+)", text)
    if not m:
        m = re.search(r"coverage:\s*([0-9.]+)", text)
    return float(m.group(1)) if m else 0.0


def _eur(value: float) -> str:
    if value >= 1_000_000_000:
        return f"€{value / 1_000_000_000:.2f}bn"
    return f"€{value / 1_000_000:.0f}M"


def main() -> int:
    rows = []
    for design_path in sorted(DESIGNS.glob("*/*/*/design.toml")):
        city_dir = design_path.parent
        design = _load(design_path)
        city = design.get("city", {})
        costs = design.get("costs", {})
        lines = design.get("lines", [])
        fleets = design.get("fleets", [])
        route_km = sum(float(line.get("length_m", 0.0)) for line in lines) / 1000.0
        total_eur = float(costs.get("total_eur", 0.0))
        charging_eur = float(costs.get("charging_microgrid_eur", costs.get("power_eur", 0.0)))
        family = lines[0].get("rolling_stock", "?") if lines else "?"
        rows.append(
            {
                "path": city_dir.relative_to(REPO_ROOT),
                "city": city.get("name") or city_dir.name.replace("-", " "),
                "country": city.get("country", "??"),
                "family": family,
                "lines": len(lines),
                "stations": len(design.get("stations", [])),
                "route_km": route_km,
                "fleet": sum(int(f.get("trainset_count", 0)) for f in fleets),
                "coverage": _coverage(city_dir),
                "capex": total_eur,
                "capex_per_km": total_eur / route_km if route_km else 0.0,
                "charging": charging_eur,
            }
        )

    rows.sort(key=lambda r: (r["capex_per_km"], -r["coverage"]))

    out = [
        "# OpenSourceRail Design Catalogue Index",
        "",
        "Generated from `designs/*/*/*/design.toml`. Sorted by CAPEX per route-km, then coverage.",
        "",
        "| City | ISO | Family | Lines | Stations | km | Fleet | Coverage | CAPEX | CAPEX/km | Charging microgrids |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        out.append(
            f"| [{r['city']}]({r['path']}/) | {r['country']} | `{r['family']}` | "
            f"{r['lines']} | {r['stations']} | {r['route_km']:.0f} | {r['fleet']} | "
            f"{r['coverage']:.0%} | {_eur(r['capex'])} | {_eur(r['capex_per_km'])} | "
            f"{_eur(r['charging'])} |"
        )

    OUT.write_text("\n".join(out) + "\n")
    print(f"wrote {OUT.relative_to(REPO_ROOT)} ({len(rows)} cities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

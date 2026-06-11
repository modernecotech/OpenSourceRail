#!/usr/bin/env python3
"""Generate `designs/README.md` from city `design.toml` files."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGNS = REPO_ROOT / "designs"
OUT = DESIGNS / "README.md"


def _load(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def _coverage(city_dir: Path) -> float:
    matches = list(city_dir.glob("*.design-quality.yaml"))
    if not matches:
        return 0.0
    text = matches[0].read_text()
    m = re.search(r"high_demand_coverage:\s*([0-9.]+)", text)
    if not m:
        m = re.search(r"coverage_score:\s*([0-9.]+)", text)
    if not m:
        m = re.search(r"coverage:\s*([0-9.]+)", text)
    return float(m.group(1)) if m else 0.0


EUR_TO_USD = 1.0 / 0.92


def _usd(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}bn"
    return f"${value / 1_000_000:.0f}M"


def _markdown_href(path: Path) -> str:
    """Return a Markdown-safe relative href for a design directory.

    Several generated country folders contain spaces (for example
    `Saudi Arabia`, `Sri Lanka`, `DR Congo`). Percent-encode each path
    segment so Markdown renderers do not treat those links as plain text
    or truncate them at the first space.
    """

    return "/".join(quote(part) for part in path.parts)


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
        total_usd = float(
            costs.get("total_usd", float(costs.get("total_eur", 0.0)) * EUR_TO_USD)
        )
        charging_usd = float(
            costs.get(
                "charging_microgrid_usd",
                float(costs.get("charging_microgrid_eur", costs.get("power_eur", 0.0))) * EUR_TO_USD,
            )
        )
        family = lines[0].get("rolling_stock", "?") if lines else "?"
        rows.append(
            {
                "path": city_dir.relative_to(DESIGNS),
                "city": city.get("name") or city_dir.name.replace("-", " "),
                "country": city.get("country", "??"),
                "family": family,
                "lines": len(lines),
                "stations": len(design.get("stations", [])),
                "route_km": route_km,
                "fleet": sum(int(f.get("trainset_count", 0)) for f in fleets),
                "coverage": _coverage(city_dir),
                "capex": total_usd,
                "capex_per_km": total_usd / route_km if route_km else 0.0,
                "charging": charging_usd,
            }
        )

    rows.sort(key=lambda r: (r["capex_per_km"], -r["coverage"]))

    out = [
        "# Generated City Designs",
        "",
        "This folder is the generated design catalogue. It is intentionally the single place for city outputs so the repo does not scatter deployment models across docs, scripts, and examples.",
        "",
        "## What Each City Folder Contains",
        "",
        "City folders follow:",
        "",
        "```text",
        "designs/<region>/<country>/<City>/",
        "```",
        "",
        "Typical contents:",
        "",
        "| File | Purpose |",
        "|---|---|",
        "| `README.md` | Human-readable generated design report |",
        "| `design.toml` | Machine-readable design summary |",
        "| `<slug>.toml` | Simulator scenario |",
        "| `*-network-map.png` | Network map render |",
        "| route GeoJSON | Line/station geometry |",
        "| design-quality YAML | Soft/hard design gate results |",
        "",
        "## Regenerate A City",
        "",
        "```bash",
        "scripts/regenerate-city.sh samawah",
        "```",
        "",
        "## Regenerate The Catalogue",
        "",
        "```bash",
        "scripts/regenerate-all.sh --jobs 4",
        "```",
        "",
        "The source city list and country assumptions live in [../lib/city-batches/world-sample.toml](../lib/city-batches/world-sample.toml) and [../lib/templates/](../lib/templates/).",
        "",
        "## Representative Designs",
        "",
        "- [Samawah, Iraq](west-asia/Iraq/Samawah/README.md): brownfield deployment instance",
        "- [Baghdad, Iraq](west-asia/Iraq/Baghdad/README.md): megacity network",
        "- [Karachi, Pakistan](south-asia/Pakistan/Karachi/README.md): largest catalogue catchment",
        "- [Lyon, France](europe/France/Lyon/README.md): high-OSM-density solver test",
        "",
        "For hand-authored scenarios, use [../lib/examples/](../lib/examples/).",
        "",
        "## City Catalogue",
        "",
        "Generated from `designs/*/*/*/design.toml`. Sorted by USD CAPEX per route-km, then high-demand coverage.",
        "",
        "High-demand coverage is the share of high-demand raster cells (demand >= 0.5) within about 400 m of a planned line. It is a demand / catchment proxy, not a land-area percentage.",
        "",
        "| City | ISO | Family | Lines | Stations | km | Fleet | High-demand coverage | CAPEX | CAPEX/km | Charging microgrids |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        href = _markdown_href(r["path"])
        out.append(
            f"| [{r['city']}]({href}/) | {r['country']} | `{r['family']}` | "
            f"{r['lines']} | {r['stations']} | {r['route_km']:.0f} | {r['fleet']} | "
            f"{r['coverage']:.0%} | {_usd(r['capex'])} | {_usd(r['capex_per_km'])} | "
            f"{_usd(r['charging'])} |"
        )

    OUT.write_text("\n".join(out) + "\n")
    print(f"wrote {OUT.relative_to(REPO_ROOT)} ({len(rows)} cities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

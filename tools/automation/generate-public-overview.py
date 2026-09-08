#!/usr/bin/env python3
"""Generate the concise public overview from canonical repository metrics."""

from __future__ import annotations

import argparse
import html
import json
import runpy
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HTML_OUTPUT = REPO_ROOT / "docs/open-source-rail-overview.html"
MARKDOWN_OUTPUT = REPO_ROOT / "docs/open-source-rail-overview.md"
TRAINSET_COST = (
    REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.json"
)
TRAINSET_MANIFEST = (
    REPO_ROOT
    / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
)
DEVELOPING_WORLD_REGIONS = {
    "central-africa",
    "east-africa",
    "latin-america",
    "north-africa",
    "south-africa",
    "south-asia",
    "southeast-asia",
    "west-africa",
    "west-asia",
}
REFERENCED_ASSETS = (
    REPO_ROOT / "docs/assets/solar-metro-trainset.png",
    REPO_ROOT / "docs/screenshots/city-studio/gui-acceptance.png",
    REPO_ROOT / "docs/screenshots/civil/bonsai-ifc4x3-civil-coordination.png",
)


def compact_usd(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value / 1_000:.0f}k"


def rounded_billions(value: float) -> str:
    return f"about ${value / 1_000_000_000:.0f}B"


def overview_values() -> dict[str, str]:
    """Return the canonical public metrics shared by both renderers."""

    missing = [path for path in REFERENCED_ASSETS if not path.is_file()]
    if missing:
        joined = ", ".join(str(path.relative_to(REPO_ROOT)) for path in missing)
        raise FileNotFoundError(f"missing overview asset(s): {joined}")
    trainset = json.loads(TRAINSET_COST.read_text(encoding="utf-8"))
    trainset_manifest = json.loads(TRAINSET_MANIFEST.read_text(encoding="utf-8"))
    design_paths = sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml"))
    public_paths = [
        path
        for path in design_paths
        if path.relative_to(REPO_ROOT / "cities/catalogue").parts[0] in DEVELOPING_WORLD_REGIONS
    ]
    cities = len(public_paths)
    countries = len(
        {path.relative_to(REPO_ROOT / "cities/catalogue").parts[1] for path in public_paths}
    )
    estimate = compact_usd(float(trainset["total_build_cost_usd"]))
    planning_unit = compact_usd(float(trainset["rounded_local_owner_unit_usd"]))
    portfolio = runpy.run_path(str(REPO_ROOT / "tools/automation/generate-portfolio-summary.py"))
    metric_cities, metric_countries, capital, _ = portfolio["portfolio_metrics"]()
    if metric_cities != cities or metric_countries != countries:
        raise ValueError("public overview and portfolio-summary city/country scopes disagree")
    osr_total = float(capital["total"])
    foreign_total = float(capital["foreign_total"])
    osr_external = float(capital["external"])
    foreign_external = float(capital["foreign_external"])
    external_avoided = foreign_external - osr_external
    return {
        "cities": str(cities),
        "countries": str(countries),
        "regions": str(len(DEVELOPING_WORLD_REGIONS)),
        "estimate": estimate,
        "planning_unit": planning_unit,
        "local_share": f"{capital['local'] / capital['total']:.0%}",
        "local_value": rounded_billions(capital["local"]),
        "external_need": rounded_billions(capital["external"]),
        "osr_local_per_100m": f"${100 * float(capital['local']) / osr_total:.1f}M",
        "osr_external_per_100m": f"${100 * osr_external / osr_total:.1f}M",
        "foreign_total_per_100m": f"${100 * foreign_total / osr_total:.1f}M",
        "foreign_local_per_100m": (
            f"${100 * (foreign_total - foreign_external) / osr_total:.1f}M"
        ),
        "foreign_external_per_100m": f"${100 * foreign_external / osr_total:.1f}M",
        "external_avoided_per_100m": f"${100 * external_avoided / osr_total:.1f}M",
        "external_reduction": f"{external_avoided / foreign_external:.1%}",
        "trainset_product_rows": str(len(trainset_manifest["product_items"])),
    }


def render() -> str:
    """Render the self-contained landscape HTML/print edition."""

    values = {key: html.escape(value) for key, value in overview_values().items()}
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OpenSourceRail — One-page overview</title>
  <style>
    @page {{ size: A4 landscape; margin: 9mm; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: #10233d; background: #edf3f8; font: 10pt/1.35 "DejaVu Sans", Arial, sans-serif; }}
    main {{ position: relative; width: 100%; height: 190mm; overflow: hidden; padding: 4mm; background: #f9fcff; border: 1px solid #c8d6e6; }}
    header {{ display: grid; grid-template-columns: 1.25fr 1fr; gap: 7mm; align-items: center; }}
    h1 {{ margin: 0; font-size: 29pt; line-height: 1; }}
    h2 {{ margin: 0 0 2mm; font-size: 13pt; }}
    p {{ margin: 0 0 1.5mm; }}
    .tag {{ display: inline-block; margin-bottom: 3mm; padding: 1.2mm 3mm; border-radius: 9mm; color: white; background: #0a6840; font-weight: 700; }}
    .hero {{ width: 100%; height: 44mm; object-fit: contain; background: white; border: 1px solid #c8d6e6; border-radius: 3mm; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 3mm; margin: 3mm 0; }}
    .metric, .card {{ padding: 2.3mm; background: white; border: 1px solid #c8d6e6; border-radius: 2.5mm; }}
    .metric strong {{ display: block; color: #0a6840; font-size: 17pt; }}
    .metric span {{ color: #526277; font-size: 8pt; }}
    .content {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; }}
    .compare {{ width: 100%; margin: 1.5mm 0; border-collapse: collapse; font-size: 7.5pt; }}
    .compare th, .compare td {{ padding: .65mm; border-bottom: 1px solid #dce5ef; text-align: right; }}
    .compare th:first-child, .compare td:first-child {{ text-align: left; }}
    ul {{ margin: 0; padding-left: 4.5mm; }}
    li {{ margin-bottom: 1.1mm; font-size: 8.7pt; }}
    .shots {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2mm; }}
    .shots img {{ width: 100%; height: 37mm; object-fit: cover; border: 1px solid #c8d6e6; }}
    .foot {{ position: absolute; right: 4mm; bottom: 4mm; left: 4mm; display: grid; grid-template-columns: 1.25fr 1fr; gap: 3mm; }}
    .foot .card {{ padding: 2mm; }}
    .foot h2 {{ font-size: 11pt; }}
    .foot p {{ margin-bottom: 1mm; font-size: 8pt; line-height: 1.25; }}
    .small {{ color: #526277; font-size: 7.6pt; }}
    a {{ color: #0757a0; }}
  </style>
</head>
<body>
<main>
  <!-- Generated by tools/automation/generate-public-overview.py; do not hand-edit. -->
  <header>
    <div>
      <span class="tag">Build rail locally · retain skills · reduce foreign-capital dependence</span>
      <h1>OpenSourceRail</h1>
      <p><strong>An open urban-rail platform designed to keep ordinary engineering, fabrication, integration, software and long-term maintenance capability in the adopting country.</strong></p>
      <p>The same deterministic workspace connects city design, GIS, CAD/IFC, simulation, operations, costs and assurance. Its {values['cities']} developing-world planning models estimate {values['local_share']} domestic value; all values remain planning sensitivities rather than bids or funding commitments.</p>
    </div>
    <img class="hero" src="assets/solar-metro-trainset.png" alt="OpenSourceRail light-metro reference trainset">
  </header>

  <section class="metrics">
    <div class="metric"><strong>{values['local_value']}</strong><span>roughly {values['local_share']} modeled domestic value across {values['countries']} country programmes</span></div>
    <div class="metric"><strong>{values['cities']} cities</strong><span>developing-world public evidence models; one European model is comparison-only</span></div>
    <div class="metric"><strong>{values['planning_unit']}</strong><span>local factory-gate LM3 planning target; generated build record {values['estimate']}</span></div>
    <div class="metric"><strong>{values['trainset_product_rows']} rows</strong><span>traceable LM3 parts and assemblies with visible supplier and release gaps</span></div>
  </section>

  <section class="content">
    <div class="card">
      <h2>Why local delivery changes finance</h2>
      <p class="small">Open design lets a country procure ordinary civil work, fabrication, software, integration and maintenance locally, importing specialist components only where needed.</p>
      <table class="compare">
        <tr><th>$100M same-scope example</th><th>OSR</th><th>Turnkey</th></tr>
        <tr><td>Total price</td><td>$100.0M</td><td>{values['foreign_total_per_100m']}</td></tr>
        <tr><td>No external capital</td><td>{values['osr_local_per_100m']}</td><td>{values['foreign_local_per_100m']}</td></tr>
        <tr><td>External capital</td><td><strong>{values['osr_external_per_100m']}</strong></td><td><strong>{values['foreign_external_per_100m']}</strong></td></tr>
      </table>
      <p class="small"><strong>{values['external_avoided_per_100m']} less external capital ({values['external_reduction']}) before interest.</strong> When debt-financed, external capital becomes loan principal. The editable default is a 2× turnkey price and 90% external share—not a vendor bid.</p>
    </div>
    <div class="card">
      <h2>Design, regenerate and operate</h2>
      <ul>
        <li>Edit lines, stations, alignments, demand and line/day/hour service over local GIS.</li>
        <li>Generate IFC4.3, CAD, quantities, costs and Git-reviewable city packages.</li>
        <li>Run deterministic train, station, energy, wayside, point/crossing and depot software together.</li>
        <li>Use one Workbench for City Studio, simulation, OCC training and Ops Core.</li>
      </ul>
    </div>
    <div class="shots">
      <img src="screenshots/city-studio/gui-acceptance.png" alt="City Studio deterministic browser acceptance">
      <img src="screenshots/civil/bonsai-ifc4x3-civil-coordination.png" alt="Bonsai IFC4.3 civil coordination model">
    </div>
  </section>

  <section class="foot">
    <div class="card">
      <h2>Buildable pathway, visible gaps</h2>
      <p>Reference packages cover all {values['trainset_product_rows']} LM3 product rows, nine timed manufacturing methods, 30 mould/tooling families, modular rolling stock, stations, civil works, battery traction, renewable charging, operations and assurance. Supplier freeze, detailed drawings, proof testing, certification and authority approval remain explicit release gates.</p>
    </div>
    <div class="card">
      <h2>Review or collaborate</h2>
      <p><a href="https://github.com/modernecotech/OpenSourceRail">github.com/modernecotech/OpenSourceRail</a></p>
      <p>Review the assumptions, reproduce the generators, open a technical issue or propose an evidence-backed contribution through the public repository.</p>
    </div>
  </section>
</main>
</body>
</html>
"""


def render_markdown() -> str:
    """Render the repository-facing edition that GitHub displays natively."""

    values = overview_values()
    return f"""# OpenSourceRail — one-page overview

> **Build rail locally · retain skills · reduce foreign-capital dependence**

![OpenSourceRail light-metro reference trainset](assets/solar-metro-trainset.png)

**An open urban-rail platform designed to keep ordinary engineering,
fabrication, integration, software and long-term maintenance capability in the
adopting country.**

The same deterministic workspace connects city design, GIS, CAD/IFC,
simulation, operations, costs and assurance. Its {values['cities']}
developing-world planning models estimate {values['local_share']} domestic
value; all values remain planning sensitivities rather than bids or funding
commitments.

| {values['local_value']} | {values['cities']} cities | {values['planning_unit']} | {values['trainset_product_rows']} rows |
|---|---|---|---|
| Roughly {values['local_share']} modeled domestic value across {values['countries']} country programmes | Developing-world public evidence models; one European model is comparison-only | Local factory-gate LM3 planning target; generated build record {values['estimate']} | Traceable LM3 parts and assemblies with visible supplier and release gaps |

## Why local delivery changes finance

Open design lets a country competitively procure ordinary civil work, vehicle
structures and interiors, wiring, software, integration and maintenance
locally, importing specialist components only where domestic suppliers are not
yet qualified.

For the **same modelled railway scope**, suppose the OpenSourceRail case is
**$100M**. The foreign-turnkey column uses the editable default sensitivity: a
2.0× delivered price with 90% requiring foreign currency or international
capital.

| Where the money goes | Localisation-first OpenSourceRail | Foreign-vendor turnkey sensitivity |
|---|---:|---:|
| Total programme price | **$100.0M** | **{values['foreign_total_per_100m']}** |
| Value not requiring external capital | {values['osr_local_per_100m']} | {values['foreign_local_per_100m']} |
| External-capital requirement | **{values['osr_external_per_100m']}** `██░░░░░░░░` | **{values['foreign_external_per_100m']}** `█████████░` |

That is **{values['external_avoided_per_100m']} less external capital
({values['external_reduction']}) before interest**. When debt-financed, the
external requirement becomes loan principal; interest depends on country terms.
This is a controlled sensitivity—not a vendor quotation or financing offer.

## Design, regenerate and operate

- Edit lines, stations, alignments, demand and line/day/hour service over local
  GIS.
- Generate IFC4.3, CAD, quantities, costs and Git-reviewable city packages.
- Run deterministic train, station, energy, wayside, point/crossing and depot
  software together.
- Use one Workbench for City Studio, simulation, OCC training and Ops Core.

| City Studio | Civil IFC coordination |
|---|---|
| ![City Studio deterministic browser acceptance](screenshots/city-studio/gui-acceptance.png) | ![Bonsai IFC4.3 civil coordination model](screenshots/civil/bonsai-ifc4x3-civil-coordination.png) |

## Buildable pathway, visible gaps

Reference packages cover all {values['trainset_product_rows']} LM3 product
rows, nine timed manufacturing methods, 30 mould/tooling families, modular
rolling stock, stations, civil works, battery traction, renewable charging,
operations and assurance. Supplier freeze, detailed drawings, proof testing,
certification and authority approval remain explicit release gates.

## Review or collaborate

Review the assumptions, reproduce the generators, open a technical issue or
propose an evidence-backed contribution through the
[public repository](https://github.com/modernecotech/OpenSourceRail).

For offline printing, [download the landscape HTML edition](open-source-rail-overview.html?raw=1).

<!-- Generated by tools/automation/generate-public-overview.py; do not hand-edit. -->
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected_outputs = {
        HTML_OUTPUT: render(),
        MARKDOWN_OUTPUT: render_markdown(),
    }
    if args.check:
        stale = [
            path
            for path, expected in expected_outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        for path in stale:
            print(f"stale: {path.relative_to(REPO_ROOT)}")
        if stale:
            return 1
        print("current: " + ", ".join(str(path.relative_to(REPO_ROOT)) for path in expected_outputs))
        return 0
    for output, expected in expected_outputs.items():
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", dir=output.parent, delete=False, encoding="utf-8"
        ) as handle:
            handle.write(expected)
            temporary = Path(handle.name)
        temporary.replace(output)
        print(f"wrote {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

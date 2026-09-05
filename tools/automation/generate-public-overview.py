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
    catalogue = len(design_paths)
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
    return {
        "catalogue": str(catalogue),
        "cities": str(cities),
        "countries": str(countries),
        "regions": str(len(DEVELOPING_WORLD_REGIONS)),
        "estimate": estimate,
        "planning_unit": planning_unit,
        "local_share": f"{capital['local'] / capital['total']:.0%}",
        "local_value": rounded_billions(capital["local"]),
        "external_need": rounded_billions(capital["external"]),
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
    main {{ width: 100%; min-height: 190mm; padding: 7mm; background: #f9fcff; border: 1px solid #c8d6e6; }}
    header {{ display: grid; grid-template-columns: 1.25fr 1fr; gap: 7mm; align-items: center; }}
    h1 {{ margin: 0; font-size: 29pt; line-height: 1; }}
    h2 {{ margin: 0 0 2mm; font-size: 13pt; }}
    p {{ margin: 0 0 2.5mm; }}
    .tag {{ display: inline-block; margin-bottom: 3mm; padding: 1.2mm 3mm; border-radius: 9mm; color: white; background: #0a6840; font-weight: 700; }}
    .hero {{ width: 100%; height: 64mm; object-fit: contain; background: white; border: 1px solid #c8d6e6; border-radius: 3mm; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 3mm; margin: 5mm 0; }}
    .metric, .card {{ padding: 3mm; background: white; border: 1px solid #c8d6e6; border-radius: 2.5mm; }}
    .metric strong {{ display: block; color: #0a6840; font-size: 17pt; }}
    .metric span {{ color: #526277; font-size: 8pt; }}
    .content {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; }}
    ul {{ margin: 0; padding-left: 4.5mm; }}
    li {{ margin-bottom: 1.1mm; font-size: 8.7pt; }}
    .shots {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2mm; }}
    .shots img {{ width: 100%; height: 37mm; object-fit: cover; border: 1px solid #c8d6e6; }}
    .foot {{ display: grid; grid-template-columns: 1.25fr 1fr; gap: 4mm; margin-top: 4mm; }}
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
      <h2>Local manufacture and economic value</h2>
      <ul>
        <li>Localise civil materials, vehicle structures/interiors, wiring, cabinets, installation, software integration and maintenance.</li>
        <li>Limit imported value to specialist machinery and components not yet qualified domestically; current aggregate planning need is {values['external_need']}.</li>
        <li>Reuse one shared national trainset factory and open tooling instead of purchasing a separate opaque production system for every city.</li>
        <li>Retain engineering knowledge, supplier development, skilled employment and lifecycle maintenance capability.</li>
      </ul>
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
      <p class="small">The engineering catalogue contains {values['catalogue']} models. European comparison designs are retained for technical inspection but excluded from public evidence totals and examples.</p>
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

## Local manufacture and economic value

- Localise civil materials, vehicle structures and interiors, wiring,
  cabinets, installation, software integration and maintenance.
- Limit imported value to specialist machinery and components not yet
  qualified domestically; current aggregate planning need is
  {values['external_need']}.
- Reuse one shared national trainset factory and open tooling instead of
  purchasing a separate opaque production system for every city.
- Retain engineering knowledge, supplier development, skilled employment and
  lifecycle maintenance capability.

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

The engineering catalogue contains {values['catalogue']} models. European
comparison designs are retained for technical inspection but excluded from
public evidence totals and examples.

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

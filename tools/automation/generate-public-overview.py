#!/usr/bin/env python3
"""Generate the public overview from the selected v0.6 candidate."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from html import escape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
HTML_OUTPUT = REPO_ROOT / 'docs/open-source-rail-overview.html'
MARKDOWN_OUTPUT = REPO_ROOT / 'docs/open-source-rail-overview.md'


def primary_markdown() -> str:
    from engineering.development_baseline import selection

    selected = selection.load(REPO_ROOT)
    config = selected['selection']
    vehicle = config['vehicle']
    service = config['service']
    artwork = json.loads((REPO_ROOT / 'docs/assets/v0.6/illustrations.json').read_text())
    illustrations = '\n\n'.join(
        f"### {image['title']}\n\n![{image['alt']}]({Path(image.get('display_file', image['file'])).relative_to('docs').as_posix()})\n\n{image['caption']}"
        for image in artwork['illustrations']
    )
    return f'''# OpenSourceRail: open railway design and delivery

OpenSourceRail connects city planning, railway engineering, manufacturing,
construction, business workflows and open train-control software. Its purpose is
to build local design authority, production and repair capability while
comparing whole-life cost and passenger service. These are project objectives;
economic superiority and physical qualification have not been demonstrated.

## Selected v0.6 vehicle reference

The selected wheel-supported vehicle reference has
{vehicle['cars']} cars of {vehicle['body_length_m']:g} m. Each car is planned for
{vehicle['fixed_seats_per_car']} fixed seats and
{vehicle['wheelchair_places_per_car']} wheelchair places, with no planned
standing. Passive steel-wheel bogies run on conventional rails carried by
concrete guideway. The retained passive aluminium secondary is an interface
reference; it does not select installed station LIM propulsion. The reference
vehicle has no normal-service traction motor, traction battery or permanent
magnet. Independent braking, service power, protection and rescue remain required.

Installed propulsion architecture, powered length, acceleration, braking and
headway must be evaluated together for each candidate. Neither 900 m nor 100 m
is a prescribed installation. The named retained service control uses
{service['launch_speed_cap_m_s'] * 3.6:g} km/h launch speed,
{service['headway_s']:g} seconds headway and {service['dwell_s']:g} seconds dwell;
these are reproducibility controls, not selected operating requirements. Its
{service['normal_capacity_pphpd_arithmetic']:,.0f} passengers/hour/direction is
capacity arithmetic, not a demonstrated protected service. The selected vehicle
is a development reference without manufacturing or passenger-operation release.

Reference and alternative describe selection and comparison roles. Evaluated
results retain their declared calculation and evidence scope. Prototype
validation and release require separate physical evidence and review.

![Counted v0.6 vehicle proposal](design-engine/current/vehicle-overview.svg)

*Partial stock geometry and equipment accounts; not a complete installed or approved train.*

## Concept illustrations

These illustrations show the intended passenger experience, local assembly and
construction approach. They are concept artwork. Detailed dimensions,
accessibility, equipment placement and construction methods require controlled
engineering records; the images do not establish physical performance.

{illustrations}

## Planning, engineering and delivery

The [planning workspace](workbench/planning/index.html) verifies current city
geography and route sources, then supports route, stop, service and OD proposals.
Run `./osr plan compile edits.json --output build/my-plan` to create an immutable
handoff bound to the selected candidate; run `./osr plan verify build/my-plan`
to verify its source files and identities. The handoff contains proposals only.
It excludes vehicle, propulsion, fleet, civil quantity, cost, performance and
cashflow results; those require candidate-specific evaluation. Planning
revisions do not grant movement authority.

From a verified handoff, create an immutable six-car factory work package
with:

```sh
./osr twin factory-draft compile build/planning-handoff --output build/factory-plan
./osr twin factory-draft verify build/planning-handoff build/factory-plan
```

The draft uses the selected candidate's Class C cost ledger and source-linked
low/base/high process hours under two 8-hour production shifts. It schedules one
serialized planning lane and does not infer crew size, parallel capacity or
calendar dates. Civil and railway-operations schedules, purchasing and
manufacturing release remain held.

The [coordinated design workflow](design-engine/coupled-railway/README.md)
propagates one candidate through geometry, mass, engineering analysis, BOM,
CAD/IFC, manufacturing, procurement, construction and controls. The
[current export manifest](design-engine/current/exports/manifest.json) and
[delivery package index](design-engine/coupled-railway/delivery-index.json)
bind research records to candidate identities. ERPNext exports are disabled
drafts. Complete installed equipment, an available operating motor map,
force-driven journeys and fully supported lifecycle costs remain open.

## Business and operating software

[ERPNext and Frappe HR](../deployment/erpnext/README.md) support draft business,
workforce, procurement, manufacturing, quality and maintenance workflows.
[FUXA and the gateway](../deployment/supervision/README.md) support equipment
observations, alarms, history and review-linked records. Site masters,
permissions, device bindings and reviewed imports require deployment-specific
configuration. These services do not commission a railway or supply movement
authority.

Cost scenarios use two 8-hour shifts for production and civil work. Operations
are modelled at two shifts for 16/18-hour service and three shifts for a 24-hour
case. These are planning assumptions, not approved staffing or operating plans.

## Start here

Run `./install.sh`, then `./osr status` and `./osr workbench`. Use
`./osr design railway plan` for coordinated research, `./osr build` to refresh
current evidence and `./osr verify` to check sources and payloads. `./osr sim
baghdad` reports the current city-evaluation hold.

[Project introduction](../README.md) · [Current engineering](design-engine/current/README.md) ·
[Architecture](ARCHITECTURE.md) · [Roadmap](ROADMAP.md) ·
[Candidate delivery](design-engine/coupled-railway/delivery-index.json) ·
[Reader](../OpenSourceRail-Book.pdf) · [Contribute](../CONTRIBUTING.md).

Software: Apache 2.0. Open physical designs: CERN-OHL-S v2. Documentation: CC-BY-SA 4.0.
See [licensing](../LICENSE.md) for the applicable path and upstream terms.

<!-- Generated by tools/automation/generate-public-overview.py; do not hand-edit. -->
'''


def primary_html() -> str:
    import mistune

    markdown = primary_markdown()
    content = mistune.html(markdown)
    title = escape(markdown.splitlines()[0].removeprefix('# '))
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{title}</title>'
        '<style>body{font:17px/1.6 system-ui;max-width:1050px;margin:32px auto;padding:0 24px;color:#173341}'
        'img{width:100%;height:auto}table{display:block;overflow:auto;border-collapse:collapse}'
        'td,th{padding:10px;text-align:left;border-bottom:1px solid #ccd}a{color:#006b65}'
        'h1{line-height:1.15}code{overflow-wrap:anywhere}@media print{body{font-size:11px}img{max-height:260px;object-fit:contain}}</style>'
        + content + '\n</html>\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected_outputs = {HTML_OUTPUT: primary_html(), MARKDOWN_OUTPUT: primary_markdown()}
    if args.check:
        stale = [path for path, expected in expected_outputs.items()
                 if not path.is_file() or path.read_text(encoding='utf-8') != expected]
        for path in stale:
            print(f'stale: {path.relative_to(REPO_ROOT)}')
        if stale:
            return 1
        print('current: ' + ', '.join(str(path.relative_to(REPO_ROOT)) for path in expected_outputs))
        return 0
    for output, expected in expected_outputs.items():
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile('w', dir=output.parent, delete=False, encoding='utf-8') as handle:
            handle.write(expected)
            temporary = Path(handle.name)
        temporary.replace(output)
        print(f'wrote {output.relative_to(REPO_ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

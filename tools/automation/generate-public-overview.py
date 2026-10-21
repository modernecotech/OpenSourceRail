#!/usr/bin/env python3
"""Generate the public overview from current maglev design inputs."""
from __future__ import annotations
import argparse
import json
import sys
import tempfile
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
HTML_OUTPUT = REPO_ROOT / 'docs/open-source-rail-overview.html'
MARKDOWN_OUTPUT = REPO_ROOT / 'docs/open-source-rail-overview.md'


def primary_markdown() -> str:
    """Current architecture and explicitly provisional digital evidence."""
    from engineering.ferrite_maglev import model, cities, station_structure, configuration, interchange_hubs
    current = model.load()[1]
    selected = configuration.selected(current)
    civil = selected.civil
    index = json.loads(cities.INDEX.read_text())
    count = index['city_count']
    body = station_structure.body()
    hubs=interchange_hubs.read_summary()
    hub_conflicts=sum(len(row['spacing_conflicts']) for row in interchange_hubs.study()['baseline']['line_screens'])
    operating_mass=model.mass(current,current['mass']['ferrite_base'],50.)
    return f'''# OpenSourceRail v0.5.2 development — fixed-zone ferrite maglev

**Fewer moving parts, local manufacture and compact elevated urban routes.**

![OpenSourceRail maglev station concept](../OpenSourceRail%20maglev%20station%20concept.png)

*Illustrative development concept, without physical or manufacturing acceptance.*

Fixed linear synchronous motors launch and receive the train at stations.
Selected longer legs add located midway acceleration; remaining guideway is unpowered; onboard ferrite PM-biased active support,
guidance and passenger services remain independently powered. Removing main
traction equipment from the train shifts electrical plant to stations. Support
coils/drives, cooling, sensing, protection, doors, HVAC and emergency equipment
remain necessary. Contactless running aims to reduce contact noise and wear;
actual losses, acoustic performance and maintenance require measurement.

## Body, civil works and local capability

Baghdad uses six 17 m bodies. The central tare target is {body['tare_target_kg']/1000:.1f} t/car,
including a 5.2 t equipped structural GFRP body, 3 t ferrite, 30 kWh services
storage and an existing 1.8 t growth reserve. Four passenger doors per car are the
body takeoff. Counted frame families, supported panels, couplers and hardpoint
candidates now have calculated dimensions and margins; frame/emergency-brake
growth consumes this reserve. Joined-body strength, complete equipment, fatigue,
CG and inertia remain unqualified.
The50kWh wider-corridor reference is {operating_mass['tare_kg']/1000:.1f}t tare/
{operating_mass['aw3_kg']/1000:.1f}t AW3 per car. Its pack increase is included once;
the primary detail/emergency screens use that heavier mass alongside the retained30kWh case.

The current ordinary civil candidate is a {civil.span_m:g} m, {civil.width_m:.2f} × {civil.depth_m:.2f} m closed concrete box with
{civil.web_m*1000:g} mm webs, {civil.flange_m*1000:g} mm flanges and end infills. The supplied
1.80 m-depth case remains a separate comparison. Hollow columns/caps and alternative
foundation families are compared by quantity. Necessary passive iron, anchors,
bearings, connections and final survey remain in scope. Ground-specific selection,
prestress/handling details, fixed/guided bearings and emergency load paths have
numerical screens; physical structural and construction acceptance remain open.

The research target omits a continuous external walkway. Vertical spiral chutes
are the preferred alternative under investigation, without walkway-removal
approval. Safe landing, assisted evacuation, deployment, stopping/recovery and
fire response must work at every allowed stopping location.

![Vertical spiral escape chute concept](../Vertical%20spiral%20escape%20chute%20concept.png)

*Illustrative concept; no qualified railway device or all-stop evacuation claim.*

The 99% elevated-mainline objective and straight tangents aim to reach constrained
corridors with less surface occupation. Rights, buildings, utilities, access,
wildlife, water, curvature and foundation feasibility govern each route.

Local precast/GFRP production, steel fabrication, cartridge assembly, station/booster
winding cassettes, interiors, wiring, Rust software and integration can build
domestic capability. Prioritise verified British manufacture when selecting UK
machinery. A UK distributor or integrator does not establish manufacturing origin.
Complete local content remains unknown until the bill and input origins exist.

## Operating and cost boundaries

Urban passenger stops target at least {current["operating_strategy"]["urban_minimum_stop_spacing_m"]/1000:g} km spacing and about
{current["operating_strategy"]["urban_target_stop_spacing_m"]/1000:g} km on average. Suburban stops target
{current["operating_strategy"]["suburban_minimum_stop_spacing_m"]/1000:g}–{current["operating_strategy"]["suburban_maximum_stop_spacing_m"]/1000:g} km with fixed midway acceleration where required.
Junctions transfer passengers between independent fixed lines, without train-routing
switches. Retained close junctions remain spacing/access exceptions requiring a
solution. Straight alignments are planning candidates subject to land, buildings,
utilities, grades, access and evacuation.

The 1 km/{current["vehicle"]["runtime_reference_seconds"]:g} s/{current["vehicle"]["scheduled_headway_seconds"]:g} s station and moving packets remain component
benchmarks. The supplied 90 s/190 s case is a separate authored comparison.
Longer urban/suburban profiles have their own finite-zone, power, services,
clearance and actual Rust fault tests. Capacity shortfalls and unimplemented
sectioned protection stay visible; a timer does not prove a clear railway.

The retained benchmark uses {current["power"]["candidate_station_charger_kw_per_car"]:g} kW/car charger input at
{current["power"]["station_charger_efficiency_assumption"]*100:g}% assumed conversion efficiency. Longer cases compare their own pack,
charger and dwell choices. Independently equipped rescue nodes, faster winches
and 30/50/60 kWh packs have explicit rope/drum/portal/foundation, drive/power,
mass and cost comparisons. A midpoint accelerator is not automatically a refuge,
charging station or rescue site. Rope/termination, access, essential loads,
physical hardware and real ground remain unqualified.

City subtotals separately count eight scopes: fleet, ordinary and terminal civil
work, station electrical targets, a conditional footing increment, booster
electrical plant, booster mount stock and independent rescue kits. Complete
station/transfer hubs, grid reinforcement, land, factory capital, evacuation,
qualification, finance and other unpriced work remain additional. Fewer passenger
platforms do not by themselves establish a total saving.

## Baghdad interchange investigation

The default Baghdad plan remains {hubs['baseline_stops']} proposed stops with {hub_conflicts} transfer-spacing
conflicts. A separate [interchange investigation](design-engine/ferrite-maglev/interchange-hubs/README.md)
compares extended walking links on unchanged guideways with coordinated
shared-site hub concepts that change guideway geometry. No alternative is selected.

![Retained Baghdad corridors, extended transfer links and unselected shared-site concept](design-engine/ferrite-maglev/interchange-hubs/overview.svg)

Original boarding/access records remain traceable. The extended links retain
reference walks and partial electrical target credits, without complete connector
costs or ridership-weighted benefits. Shared-site concepts draw involved fixed
lines through one location, but station tangents, curves, levels, platforms and
actual internal walks remain undesigned;100m is only a compact-walk sensitivity.
Lift resilience, peak transfer pulses, shade, resting places, evacuation, land
and complete construction/maintenance costs must enter selection. Trains never
switch between lines in these passenger-transfer proposals.

## Inspect and reproduce the current work

| Current digital capability | Scope |
|---|---|
| City planning | {count} primary packages; located operating stops, access assignments, passenger-transfer spacing conflicts, boosters, rescue nodes, motion/headway/capacity screens and eight-part cost subtotals |
| Operating study | Separate urban/suburban profiles with finite station/booster zones, services/charging and electrical/protection fault cases |
| Interchange investigation | Unselected Baghdad extended-access variants and shared-site guideway concepts; default plan and open acceptance preserved |
| Manufactured details | Counted frame/panel/hardpoint/coupler/stator interfaces, prestress/handling and emergency load-path screens, foundation cost deltas and open qualification |
| Controls | Actual Rust support replay and integrated station/resource campaign with full-tail clearance and fault cases; one local controller and virtual detectors |
| Simulation and media | Retained 1 km six-car moving numerical run with repeated flexible spans and couplers, calculated-motion video, partial native detail CAD/images and visibility videos |
| Engineering acceptance | **0 accepted physical releases; design, manufacture and operational gates remain open** |

Ring benchmarks and block-orientation seeds receive no railway lift or mass-saving
credit. The moving run uses ideal independently allocated magnetic forces, rigid
cars, linear beams and virtual sensing. Real force maps, shared-field phase,
flexible bodies, lateral/soil/contact response, hardware timing and distributed
controller handover remain open. The moving video uses calculated positions with
declared amplification; other videos show final-position stock visibility,
without collision or erection-strength acceptance.

Use `./osr build` to verify dependencies and rebuild stale implemented studies.
`./osr design station`, `./osr design structure` and `./osr design protocol`
reproduce their separate evidence. `./osr workbench` opens the review UI;
`./osr book` builds the current reader edition. The scheduled runner refreshes
implemented evaluators after source changes; it does not invent physical evidence.

[Open the Workbench](workbench/maglev/index.html),
[review calculations, CAD and videos](design-engine/ferrite-maglev/reference/index.html),
[read implementation and open work](../engineering/ferrite_maglev/README.md),
[inspect moving six-car evidence](design-engine/ferrite-maglev/moving-train/README.md),
[inspect the manufactured dossier](design-engine/ferrite-maglev/manufactured-dossier/README.md),
[inspect wider-stop corridor evidence](design-engine/ferrite-maglev/corridor/README.md),
[inspect booster and rescue quantities](design-engine/ferrite-maglev/booster-kit/README.md),
[compare Baghdad interchange alternatives](design-engine/ferrite-maglev/interchange-hubs/README.md),
[review v0.5.2 development notes](releases/v0.5.2.md),
or [download the reader book](../OpenSourceRail-Book.pdf).

Published v0.5.1 remains preserved. This document describes v0.5.2 development on
main and does not announce a new release.

<!-- Generated by tools/automation/generate-public-overview.py; do not hand-edit. -->
'''

def primary_html() -> str:
    import mistune
    content = mistune.html(primary_markdown())
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>OpenSourceRail v0.5.2 development — fixed-zone ferrite maglev</title>'
        '<style>body{font:17px/1.6 system-ui;max-width:1050px;margin:32px auto;padding:0 24px;color:#173341}'
        'img{width:100%;height:auto}table{display:block;overflow:auto;border-collapse:collapse}'
        'td,th{padding:10px;text-align:left;border-bottom:1px solid #ccd}a{color:#006b65}'
        'h1{line-height:1.15}code{overflow-wrap:anywhere}@media print{body{font-size:11px}img{max-height:260px;object-fit:contain}}</style>'
        +content+'\n</html>\n')

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected_outputs = {HTML_OUTPUT: primary_html(), MARKDOWN_OUTPUT: primary_markdown()}
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

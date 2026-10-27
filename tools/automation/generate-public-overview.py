#!/usr/bin/env python3
"""Generate the public overview for the selected, explicitly typed reference."""
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


def legacy_markdown() -> str:
    """Retained maglev rendering; reproduce historical outputs at their revision."""
    from engineering.ferrite_maglev import model, cities, station_structure, configuration, interchange_hubs
    current = model.load()[1]
    selected = configuration.selected(current)
    civil = selected.civil
    index = json.loads(cities.INDEX.read_text())
    count = index['city_count']
    body = station_structure.body()
    hubs=interchange_hubs.read_summary()
    hub_conflicts=sum(len(row['spacing_conflicts']) for row in interchange_hubs.study()['baseline']['line_screens'])
    from engineering.ferrite_maglev import candidate_magnetics
    detailed=candidate_magnetics.definition()
    operating_mass=model.mass(current,current['mass']['ferrite_base'],50.)
    return f'''# OpenSourceRail v0.5.2 development — fixed-zone ferrite maglev

**Fewer moving parts, local manufacture and compact elevated urban routes.**

**Low CAPEX, OPEX and long-term debt repayment are central design objectives.**
The detailed city briefs restore line-by-line service, energy, manufacture and
whole-life affordability views for the PM-maglev station-launched monorail.
Each current city has low/reference/high scope-covering capital budgets, annual
operating cash and debt schedules, with explicit unquoted assumptions.
They distinguish resource cost from borrower cash and imported inputs from
foreign-currency debt. Complete engineered costs and a proven comparative
advantage remain open; no former railway savings percentage is inherited.

Station-led GOA4 dispatch concentrates launch and receiving control at known
sites. The following train may use a released berth/resource only after valid
full-tail clearance and protected authority; a launch command alone cannot
release occupancy. Independent active support, separation, safe arrival,
passenger protection and recovery remain necessary. The city defaults retain
exclusive whole-leg headways while the progressive multi-train candidate
undergoes separate qualification.

![OpenSourceRail maglev station concept](../OpenSourceRail%20maglev%20station%20concept.png)

*Illustrative development concept, without physical or manufacturing acceptance.*

Fixed linear synchronous motors launch and receive the train at stations.
Selected longer legs add located midway acceleration; remaining guideway is unpowered; onboard ferrite PM-biased active support,
guidance and passenger services remain independently powered. Removing main
traction equipment from the train shifts electrical plant to stations. Support
coils/drives, cooling, sensing, protection, doors, HVAC and emergency equipment
remain necessary. Contactless running aims to reduce contact noise and wear;
actual losses, acoustic performance and maintenance require measurement.

## Current detailed candidate

The [new detailed-system chain](design-engine/ferrite-maglev/system-detailed/README.md) accounts **{detailed['controlled_tare_kg']/1000:.3f}t tare/{detailed['controlled_aw3_kg']/1000:.3f}t AW3 per car** for one dimensioned candidate. Actual stock, current circuits, loads, manufacturing quantities and native identities agree on its revision. Corrected thin return-rail saturation prevents requiredAW3 support; propulsion demagnetisation/convergence failures and structural/protection holds remain; no complete engineered or adopted train is claimed. Earlier targets and actuator passes below retain their original configuration.

The [owner/builder planner](workbench/planning/index.html) restores city edit proposals,16GIS layers and generic delivery workfront/procurement/cash plans. Independent SUMO, IFC/IDS/BCF, typed field negative controls and native business navigation have explicit bounded scopes.

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
clearance and actual Rust fault tests. A separate local multi-train prototype
now executes progressive Rust reservations and stopping-distance envelopes.
Capacity shortfalls and unqualified route-wide sectioned protection stay visible;
a timer does not prove a clear railway.

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
lines through one location; the original100m compact walk is only a sensitivity.
The separate geometry study below fits new approaches, powered zones, platforms
and actual internal paths without selecting or qualifying a hub.
Lift resilience, peak transfer pulses, shade, resting places, evacuation, land
and complete construction/maintenance costs must enter selection. Trains never
switch between lines in these passenger-transfer proposals.

The separate [access engineering study](design-engine/ferrite-maglev/hub-access/README.md)
adds physical connector/support quantities, accessible routes, passenger pulses
and lift-outage comparisons. Assumed loads, flow rates and geometry remain
provisional; no option is selected and no complete construction price is claimed.

The [shared-hub geometry study](design-engine/ferrite-maglev/shared-hub-layout/README.md)
develops new station tangents, both directional powered zones, bounded approach
transitions, platforms and actual door-to-door paths. Rejected fits remain
visible; new quantities receive no previous civil price credit. This separate
study does not turn the original100m sensitivity into a measured transfer walk.

The [longitudinal-stock sweep](design-engine/ferrite-maglev/body-stiffness/README.md)
tests failure-directed alternatives after the GFRP stiffness hold. Exact drilled
steel stock and changed spacers add their mass to the complete retained AW3
basis. The unchanged phase criterion retains passes and failures; thin-wall
joints, heavier loads, qualified materials and flexible-body behavior remain
open. No stock alternative changes the city default.

## Requirement closure and physical evidence

The [qualification programme](design-engine/ferrite-maglev/qualification/README.md)
gives each applicable requirement a deliverable, prerequisites and a route to
actual test or acceptance evidence. Specimen/rig procedures and typed raw records
cover materials, magnetic forces and losses, controls, civil stages, services,
egress and recovery. Prepared procedures and synthetic records do not constitute
physical tests. Qualified limits, exact revisions and authenticated independent
decisions remain necessary.

The [multi-train capacity study](design-engine/ferrite-maglev/line-capacity/README.md)
compares local progressive ownership with exclusive whole-leg protection and
retains adverse cases. It does not promote city schedules or approve an operating
railway. Portable study bundles now use bounded, checksum-verified numbered
archives so that the complete retained source set can exceed one archive's size
without dropping evidence.

## Inspect and reproduce the current work

| Current digital capability | Scope |
|---|---|
| City planning | {count} primary packages; located operating stops, access assignments, passenger-transfer spacing conflicts, boosters, rescue nodes, motion/headway/capacity screens and eight-part cost subtotals |
| Operating study | Separate urban/suburban profiles with finite station/booster zones, services/charging and electrical/protection fault cases |
| Interchange investigation | Unselected Baghdad extended-access variants and shared-site guideway concepts; default plan and open acceptance preserved |
| Access engineering | Connector/support quantity and passenger/lift-outage alternatives, without site or structural acceptance |
| Multi-train prototype | Actual local Rust progressive reservations, full-tail release and stopping-envelope/adverse controls; city capacity holds retained |
| Qualification programme | Exact requirement task chains, physical test protocols and guarded raw-evidence assessment; no simulated acceptance |
| Manufactured details | Counted frame/panel/hardpoint/coupler/stator interfaces, prestress/handling and emergency load-path screens, foundation cost deltas and open qualification |
| Assembled structure | Fitted native material regions, mounting holes and fasteners, retained collision controls and geometry-derived partial mass/inertia; omitted equipment remains explicit |
| Shared-hub geometry | Both directional approaches and finite powered zones, platforms, access obstacles and actual door paths; no site selection or former price credit |
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

def primary_markdown() -> str:
    import tomllib
    config=tomllib.loads((REPO_ROOT/'engineering/development-baseline.toml').read_text())
    family=config['family']
    if family=='pm_maglev_station_powered':return legacy_markdown()
    if family!='wheel_rail_station_lim':raise ValueError('No public overview adapter for selected family: '+family)
    from engineering.development_baseline import selection
    current=selection.load(REPO_ROOT)
    v=current['selection']['vehicle'];s=current['selection']['service']
    artwork=json.loads((REPO_ROOT/'docs/assets/v0.6/illustrations.json').read_text())
    illustrations='\n\n'.join(
        f"### {image['title']}\n\n![{image['alt']}]({Path(image['file']).relative_to('docs').as_posix()})\n\n{image['caption']}"
        for image in artwork['illustrations'])
    return f'''# OpenSourceRail: open railway design and delivery

OpenSourceRail aims to retain design authority, manufacturing, software, integration
and maintenance capability in-country. It connects three products: a design and
delivery platform, reference railway hardware and factories, and open GoA4 controls.
Low whole-life cost, local value added, repairability and repeatable construction
are objectives, not established savings.

## The v0.6 reference

The selected research configuration is **station-powered freewheeling wheel rail**.
It has {v['cars']} cars of {v['body_length_m']:g} m, each with {v['fixed_seats_per_car']} fixed seats and
{v['wheelchair_places_per_car']} wheelchair places, and no planned standing. Passive bogies run on
conventional rails carried by precast concrete. Station double-sided LIMs act on
passive onboard aluminium secondaries; normal-service traction motors, traction
batteries and suspension magnets are absent from the train.

The targets are {s['launch_speed_cap_m_s']*3.6:g} km/h, {s['headway_s']:g}-second headway and
{s['dwell_s']:g}-second dwell. Capacity arithmetic gives {s['normal_capacity_pphpd_arithmetic']:,.0f}
passengers/hour/direction, not a demonstrated protected service. Auxiliary batteries,
HVAC, doors, independent brakes, onboard ATP, station-led supervision and recovery
remain necessary. Passengers transfer between fixed lines; depot switching is a
separate exception to the no-mainline-switch policy.

![Counted v0.6 vehicle proposal](design-engine/current/vehicle-overview.svg)

*Partial stock geometry and equipment accounts, not a complete installed or approved train.*

## v0.6 concept illustrations

These five supplied illustrations show the intended railway, passenger experience,
local assembly and construction. They are concept artwork. Dimensions, equipment
placement, accessibility and construction details require controlled engineering
records; the images do not establish physical performance or qualification.

{illustrations}

## The wider platform remains

The lifecycle is plan, design, procure, manufacture, construct, commission, operate,
maintain and renew. [ERPNext/Frappe HR](../deployment/erpnext/README.md) retains
business, workforce, procurement, quality and maintenance functions.
[FUXA and the gateway](../deployment/supervision/README.md) retain observations,
alarms, history and review-linked lifecycle records. The
[planning workspace](workbench/planning/index.html) retains local city/service
editing and exports over historical packets; its v0.6 compilation is unconnected.
These services require configured roles, masters, device bindings and reviewed
imports; the engineering Workbench does not automatically commission them.

The [coordinated design experiment](design-engine/coupled-railway/README.md)
propagates revised bodies through inventory, interfaces, propulsion demand,
braking, civil loads and manufacturing/economic coverage. CAD/IFC stock,
EBOM/MBOM and assembly/procurement records share candidate identities. ERPNext
exports are disabled research drafts. Complete installed equipment, available
operating motor maps, force-driven journeys and whole-life prices remain open.

All 266 retained city geographies remain inputs. **v0.6 performance regeneration
is held**; earlier fleets, budgets and winding lengths are not current results.
Imported inputs retain their actual origin. No local-content percentage or
economic superiority is inferred from a lightweight material subtotal.

## Start and inspect

Run `./install.sh`, then `./osr workbench`. Use `./osr design railway plan` for
coordinated research, `./osr build` to refresh current evidence and `./osr verify`
to check its sources and payloads. `./osr sim baghdad` reports the city hold.

[Project introduction](../README.md) · [Current engineering](design-engine/current/README.md) ·
[Adoption path](first-adoptable-product.md) · [Architecture](ARCHITECTURE.md) ·
[Roadmap](ROADMAP.md) · [Reader](../OpenSourceRail-Book.pdf) · [Contribute](../CONTRIBUTING.md).

The [v0.4 introduction](https://github.com/modernecotech/OpenSourceRail/blob/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/README.md)
and [v0.5 archive](archives/v0.5-maglev/README.md) retain earlier platform and
engineering detail. Historical examples, numerical methods and business closure
do not provide current physical, manufacturing or operating acceptance.

Software: Apache 2.0. Open physical designs: CERN-OHL-S v2. Documentation: CC-BY-SA 4.0.
See [licensing](../LICENSE.md) for the applicable path and upstream terms.

<!-- Generated by tools/automation/generate-public-overview.py; do not hand-edit. -->
'''


def primary_html() -> str:
    import mistune
    from html import escape
    markdown=primary_markdown();content=mistune.html(markdown)
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>'+escape(markdown.splitlines()[0].removeprefix('# '))+'</title>'
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

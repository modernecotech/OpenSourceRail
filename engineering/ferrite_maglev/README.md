# OpenSourceRail v0.5 fixed-zone ferrite-maglev engineering

The primary design uses fixed linear synchronous motors at stations for launch
and receiving braking, plus located midway acceleration on longer legs. Guideway
outside these finite powered zones remains unpowered. Onboard ferrite PM-biased
active support/guidance and services storage remain independent. Structural GFRP
sandwich bodies, repeated narrow concrete guidebeams and Rust control packages
are the leading studies. **Accepted engineering and physical releases: zero.**

## Run and inspect

```bash
./osr build
./osr design station
./osr design structure
./osr design protocol
./osr design corridor
./osr design booster-kit
./osr design line-capacity
./osr design stopped-recovery
./osr design hub-access
./osr design qualification
./osr design assembled-body
./osr design body-stiffness
./osr design shared-hub-layout
./osr design iterate
./osr design check
./osr design verify
./osr city baghdad
./osr sim baghdad --cycles 2
./osr workbench
./osr test
./osr book
cargo test --locked -p osr-maglev-control --all-targets
```

[Current report](../../docs/design-engine/ferrite-maglev/reference/index.html) ·
[Workbench](../../docs/workbench/maglev/index.html) · [city directory](city-index.md) ·
[architecture](../../docs/ARCHITECTURE.md).

`./osr capabilities` publishes executable sources and scope.
`./osr catalogue plan --city baghdad` resolves a selected regeneration, and
`./osr catalogue run --city baghdad` rebuilds that city. `./osr readiness` reports
source and acceptance gates. `./osr design release-check` remains held while
engineering acceptance is open.

The [dependency runner](workflow.py) verifies implemented native, numerical,
control, city and publication prerequisites. An interprocess lock excludes
concurrent timer/manual builds. Progress is retained under
`build/maglev-workflow/latest.json`. The runner rebuilds stale evidence and holds
dependent work after failures; missing evaluators and physical measurements
remain additional engineering work.

The [stopped-controller recovery study](../../docs/design-engine/ferrite-maglev/stopped-recovery/README.md) executes fresh-epoch reconciliation for stationary consists at declared berths. It retains complete checkpoints and event histories, repeats every replay during verification, and requires new contracts after recovery. Moving recovery, multi-controller handover, authenticated installed storage and physical interfaces remain open.

## Current inputs and design records

| Concern | Source |
|---|---|
| Architecture | [Infrastructure policy](../../lib/templates/infrastructure.toml) |
| Vehicle/civil configuration | [Configuration](reference-configuration.toml), [reader](configuration.py), [primary inputs](../../ferrite-maglev-study.toml) |
| Wider-spacing operating corridors | [Urban/suburban model](corridor.py), [actual trajectories, Rust replay and limits](../../docs/design-engine/ferrite-maglev/corridor/README.md) |
| Booster and independent recovery hardware | [Kit model](booster_kit.py), [quantities and alternatives](../../docs/design-engine/ferrite-maglev/booster-kit/README.md), [native kit](../../docs/design-engine/ferrite-maglev/booster-native/native-cad.json) |
| Station motion and electrical plant | [Operating model](station.py), [published trajectory/overlap/power study](../../docs/design-engine/ferrite-maglev/station-powered/README.md) |
| GFRP, magnet orientations and civil production | [Structure model](station_structure.py), [study inputs](station-structure.toml), [published quantities](../../docs/design-engine/ferrite-maglev/station-structure/README.md) |
| Requirements and allocation | [Requirements](data/requirements.json), [systems register](transition.py) |
| Costs and manufacture | [Process model](manufacturing.py), [planning rates](data/cost-rates.json) |
| Magnetic/native geometry | [Geometry](geometry.py), [field controls](field.py), [native exporter](../factory_examples/native.py), [station-native packet](../../docs/design-engine/ferrite-maglev/station-native/native-cad.json) |
| Station reservation protocol | [Offline protocol evidence](../../docs/design-engine/ferrite-maglev/station-protocol/README.md), persistent Rust interlocking ownership |
| Moving six-car twin | [Numerical model](moving_train.py), [run/controls/video](../../docs/design-engine/ferrite-maglev/moving-train/README.md) |
| Manufactured details | [Dossier](closure.py), [specifications/margins/obligations](../../docs/design-engine/ferrite-maglev/manufactured-dossier/README.md), [native solids](../../docs/design-engine/ferrite-maglev/manufactured-native/native-cad.json) |
| Integrated station/control campaign | [Executable campaign](system_campaign.py), [command/input/output evidence](../../docs/design-engine/ferrite-maglev/system-campaign/README.md) |
| City geography/service | Each city's `city.json`; [compiler](cities.py), [operating-plan generator](operating_plan.py) |
| Baghdad interchange alternatives | [Investigation model](interchange_hubs.py), [unselected access/shared-site comparisons](../../docs/design-engine/ferrite-maglev/interchange-hubs/README.md), [map](../../docs/design-engine/ferrite-maglev/interchange-hubs/overview.svg) |
| Interchange access engineering | [Model](hub_access.py), [connector/support and passenger-flow alternatives](../../docs/design-engine/ferrite-maglev/hub-access/README.md) |
| Sectioned multi-train prototype | [Model](line_capacity.py), [actual Rust reservations and adverse controls](../../docs/design-engine/ferrite-maglev/line-capacity/README.md) |
| Qualification tasks and physical records | [Task/assessment engine](qualification.py), [requirement chains, rig procedures and raw schemas](../../docs/design-engine/ferrite-maglev/qualification/README.md) |
| Assembled structural candidate | [Generator and native checks](assembled_body.py), [fitted regions, load-path changes and partial mass/inertia](../../docs/design-engine/ferrite-maglev/assembled-body/README.md) |
| Longitudinal stock alternatives | [Repeatable generator and verifier](body_stiffness.py), [drilled stock, added full-AW3 mass and actual moving comparisons](../../docs/design-engine/ferrite-maglev/body-stiffness/README.md); no joined-body or default adoption |
| Shared-hub station geometry | [Bounded fitter](shared_hub_layout.py), [directional approaches, platforms and actual door paths](../../docs/design-engine/ferrite-maglev/shared-hub-layout/README.md) |
| Portable evidence bundles | [Streaming multipart writer/verifier](release_bundle.py), [command](../../tools/automation/package-maglev-release.py); exact committed sources, bounded archives, no physical-release authority |
| Onboard support control | [Rust package](../../crates/osr-maglev-control/README.md), [offline host profile](../../deployment/maglev.toml) |

Baghdad uses six 17 m bodies with 0.5 m assumed coupler gaps. The retained 30 kWh tare target is 14.2 t/car, including a 5.2 t equipped GFRP body, 3 t ferrite and an existing 1.8 t growth reserve. The 50 kWh operating reference is 14.4 t tare / 26.4 t AW3 per car (158.4 t six-car AW3); the pack increase is included once in mass. Four passenger doors per car are the body takeoff. The manufactured dossier uses that heavier case for hardpoints, passive supports, civil demands and exact brake energy/thermal quantities, alongside a named 30 kWh benchmark. Its counted primary-frame overrun and heavier brake proposal consume growth reserve; battery mass is not charged a second time. Unweighed hardware, joined-body behavior, fatigue, CG and inertia remain open.

The primary ordinary box uses 25 m spans, 0.80 m width, 100 mm webs, 150 mm flanges and end infills. Selected depth, stiffness and mass derive from current configuration and retained numerical evidence; the supplied 1.80 m case is a comparison. The detail dossier adds prestress/handling alternatives, one fixed and one guided bearing per span, longitudinal brake-load distribution and hollow-support/footing sensitivities. A larger footing is a conditional priced proposal under declared soil/load assumptions, not a geotechnical selection.

## Implemented checks and open boundaries

The qualification programme assigns each applicable requirement an exact revision,
deliverables and prerequisites through physical measurement and independent
acceptance. It provides specimen/rig procedures and typed raw-data assessment;
prepared procedures and synthetic examples remain unaccepted. Use
`tools/automation/osr-python -m engineering.ferrite_maglev.qualification --help`
for the evidence assessment entrypoint. The multi-train and hub-access packets
are additional studies; they do not select a hub, approve protection or change
city defaults from an isolated passing scenario.

The separate [Baghdad interchange investigation](../../docs/design-engine/ferrite-maglev/interchange-hubs/README.md) leaves the default273 stops and10 spacing conflicts unchanged. It compares24 extended-transfer placements on unchanged guideways and bounded disjoint network scenarios, retaining rejected extent controls and overlapping-pair constraints. Seven coordinated shared-site concepts instead draw changed guideway chords to a common location. None is selected or physically qualified. The original shared-site packet leaves tangents, levels, structures and internal walks undefined; its100m walk remains a sensitivity assumption. The separate shared-hub geometry study now fits candidate approaches, powered zones, platforms and actual door paths, retaining failed layouts and open structural/site acceptance. Extended-link quantities and electrical target credits exclude complete connectors, station civil and passenger-time economics. No equal-capacity savings or compact-hub proof follows from grouping IDs.

| Capability | Implemented scope | Evidence still required |
|---|---|---|
| Station trajectory | Jerk-limited launch, zero-thrust coast and receiving brake; energy closure and assumed magnetic-band overlap | Measured drag/magnetic losses, actual grades/wind, useful thrust, voltage/current/thermal limits and robust arrival margins |
| Station electrical costs | Fixed-group/section alternatives and separate power/charging target-rate rows | Configured equipment, supplier quotations, grid capacity, real duty and complete station scope |
| Body/civil quantities | GFRP panel mass cases, interface ownership, beam/end-infill quantities, support/foundation screens and target costs | Orthotropic structural analysis, member/joint/prestress/rebar detailing, soils, tolerances and construction-stage acceptance |
| Magnet orientations | Point-dipole ring reference and finite-block orientation inventories | Nonlinear finite-geometry steel/coil force/loss/demagnetization maps and measured shared-field behavior; no ring-gain credit |
| Native geometry | Partial panel/interface/civil/station definitions, export/reopening checks, retained images and visibility sequences | Complete production geometry, joints, equipment, drawings and qualified manufacturing tolerances |
| Rust support control | Module allocation, virtual replay, protection interfaces and support-preserving stop obligations | Actual magnetic/sensor plant, independent protection, physical I/O and measured timing |
| Launch ownership | Offline corridor/receiving-berth reservation, committed occupancy and full-clearance protocol checks | Authenticated complete-consist sensing, real receiving readiness, independent stopping and qualified system integration |
| Moving six-car replay | Six independent rigid-car states, actual Rust support allocation, repeated vertical flexible spans, longitudinal spring/damper chain, numerical controls and rejected comparisons | Measured magnetic maps, shared-field phase, normal/thrust coupling, flexible bodies, lateral/torsional/joint/soil/contact response and physical timing |
| Manufactured details | Counted frame stock, supported panels, joints, couplers, stator/bearing interfaces and handling/emergency load paths | Orthotropic laminates, joined load transfer, tolerances, fatigue/crash, calibrated limits and independent qualification |
| Integrated campaign | Actual Rust resource ownership and station control over incoming trip, dwell, next departure and negative cases | Authenticated sensors/plant, distributed handover, real receiving readiness and independent physical protection |
| Adaptive design | Previous-result-guided vehicle/beam/gain proposals, ancestry, Pareto observations and separate confirmation | Completed parts and qualified evaluators/plant before manufacturing or operating selection |
| Factory and city delivery | Conditional two-shift bottleneck capacities, duty/fleet, route quantities and process needs | Measured cure/crew/logistics rates, surveys, route recovery, complete economics and accepted instances |

The [adaptive search](iteration.py), configured in [iteration.toml](iteration.toml),
has explicit evaluation/stagnation budgets and exact-source restart receipts.
Failed confirmation disqualifies the exact revision. [Published history](../../docs/design-engine/ferrite-maglev/iterative/README.md)
retains proposals, ancestry, traces and recommendation. Mass/inertia allocations
and preference weights remain research assumptions. An analytical recommendation
does not automatically change acceptance criteria or reference configuration.

## Operation, manufacture and costs

The primary operating strategy targets urban stops at least 1.5 km apart and about 2 km on average, with 4–5 km suburban legs and located midway boosters where required. Fixed-line junctions are passenger transfers, without physical train-routing switches. The retained 1 km/88s/180s component benchmark is distinct from those longer operational profiles. The source-bound station-powered packet preserves the supplied 90 s/190 s benchmark. Actual city intervals and headways derive from bounded motion, overlap and full-tail-clearance searches. Stops are placed at passenger transfers and appropriate intervals, with retained access assignments. Nearby mandatory transfers that violate minimum spacing are reported explicitly; straight-chord alignment candidates preserve crossing nodes but do not approve clearances, bends or land. Terminal-loop proposals remain separately unqualified. Original access counts, operating stops, selected capacity and any shortfall are explicit.

A committed train in a coast or booster corridor keeps protected resources until positive full-consist clearance; timeout cannot revoke physical occupancy. The actual Rust campaign joins this ownership to station control for two consecutive legs, and retains receiver/sensor/drive/resistor/stale/phase/uncommitted fault cases. Virtual detectors and one local controller do not establish distributed handover. Independent friction-brake and winch recovery proposals now have force, energy, reserve and civil load-path calculations; calibrated friction/thermal hardware, access, curved recovery and physical stopping/holding remain unqualified.

At 60 kW/car hot services, the authored 90 s trip plus 15 s disconnected dwell consumes 10.5 kWh/train. Replacing this in 45 s takes 840 kW plus 360 kW direct services, or 1.20 MW/train **before losses**. The retained benchmark uses240 kW/car input and90% assumed conversion. Longer operating cases evaluate their own charger, battery, dwell and repeated services-energy requirements; those ratings are not inherited from the1km benchmark. The failing 200 kW input comparison is retained. Charger rating, taper, ageing, thermal duty and grid capability remain open.

City priced-scope subtotals separately label fleet, ordinary elevated guideway, terminal-loop civil work, station electrical targets, a conditional larger-footing increment, located booster plant and independent rescue kits. The footing delta accounts for concrete, reinforcement and earthworks under an unqualified soil/load proposal. The authored USD 4.255 million versus USD 3.313 million ordinary route-km comparison remains a narrow historical target-rate comparison, not the price of the new complete operating plan. No supplier quote or complete installed programme price exists. Stations, land, depot, external grid, evacuation, factories, acceptance, recovery, finance and other unpriced scope remain additional.


The booster kit counts2.5 m face cassettes,12.5 m electrical sections, mounts,
bolts, cabinet pads and actual spatial reactions at fixed/guided bearings.
Equivalent I²R duty is integrated without inventing winding temperatures. Complete
winding/core/cooling masses and nonlinear magnetic/electrical/thermal maps remain
open. The partial native scene contains defined mount/drum/portal/anchor stock,
without claiming a complete motor or assembled interference check.

Recovery alternatives compare ≤1km accessible node spacing with midpoint-only
nodes,30/50/60 kWh packs and0.5/1 m/s towing. The5 km/300 s hot study retains the
failing30 kWh midpoint-only slow-winch case. Standalone rope/drum/portal/foundation,
rated drive/power allowances and QA/access costs are additional; co-location with
an existing station, pier or booster earns no automatic saving. Cable deployment,
certified terminations, essential power, actual soils, rescue/evacuation access and
assisted passenger operation remain physical gates.

City manufacturing records carry material quantities, process routes, equipment
needs and construction approaches. Candidate processes include controlled GFRP
infusion/RTM and bonding, precast mould/cage/prestress/cure work, reaction-iron and
carrier fabrication, station coil winding, cartridge assembly, wiring and tests.
The production model takes the minimum of factory, foundation, pier, delivery,
erection and final survey capacities. Its 56.25 route-m/planned-day target is not
measured output. Demould, connection strength, crane-at-radius, ground and final
QA gates remain unexecuted.

Prefer verified British manufacture when considering UK machinery. A UK supplier
or integrator does not establish manufacturing origin. Complete local content
remains unknown until origin-traced bills and configured offers exist.

## Evacuation and publication

The preferred research layout has one beam per direction without a continuous
external walkway. Necessary magnetic faces, supports and connections remain.
[Vertical spiral chute research](evacuation.py) covers variable height, anchorage,
landings, assistance, fire/weather, partial failure, rescue and driverless use.
Walkway removal needs accepted route and onboard alternatives at every allowed
stopping point.

The moving-train video uses calculated six-car positions and beam states with declared visual amplification. Legacy CAD videos show final-position visibility; the assembled-body movie adds illustrative installation translations. None establishes collision-free erection, crane performance or chute deployment. CAD integrity,
PDE residuals, virtual controller ticks and consistent publication hashes each
establish only their checked digital scope. [Closure work](../../docs/ROADMAP.md#primary-maglev-closure-queue)
and [v0.5.2 development notes](../../docs/releases/v0.5.2.md) remain explicit.

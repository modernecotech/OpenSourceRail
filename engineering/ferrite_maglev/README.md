# OpenSourceRail v0.5 station-powered ferrite-maglev engineering

The primary design uses station-mounted linear synchronous motors for launch and
receiving braking, with unpowered interstation coasting. Onboard ferrite PM-biased
active support/guidance and services storage remain independent. Structural GFRP
sandwich bodies, repeated narrow concrete guidebeams and Rust control packages
are the leading studies. **Accepted engineering and physical releases: zero.**

## Run and inspect

```bash
./osr build
./osr design station
./osr design structure
./osr design protocol
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

## Current inputs and design records

| Concern | Source |
|---|---|
| Architecture | [Infrastructure policy](../../lib/templates/infrastructure.toml) |
| Vehicle/civil configuration | [Configuration](reference-configuration.toml), [reader](configuration.py), [primary inputs](../../ferrite-maglev-study.toml) |
| Station motion and electrical plant | [Operating model](station.py), [published trajectory/overlap/power study](../../docs/design-engine/ferrite-maglev/station-powered/README.md) |
| GFRP, magnet orientations and civil production | [Structure model](station_structure.py), [study inputs](station-structure.toml), [published quantities](../../docs/design-engine/ferrite-maglev/station-structure/README.md) |
| Requirements and allocation | [Requirements](data/requirements.json), [systems register](transition.py) |
| Costs and manufacture | [Process model](manufacturing.py), [planning rates](data/cost-rates.json) |
| Magnetic/native geometry | [Geometry](geometry.py), [field controls](field.py), [native exporter](../factory_examples/native.py), [station-native packet](../../docs/design-engine/ferrite-maglev/station-native/native-cad.json) |
| Station reservation protocol | [Offline protocol evidence](../../docs/design-engine/ferrite-maglev/station-protocol/README.md), persistent Rust interlocking ownership |
| City geography/service | Each city's `city.json`; [compiler](cities.py) |
| Onboard support control | [Rust package](../../crates/osr-maglev-control/README.md), [offline host profile](../../deployment/maglev.toml) |

Baghdad uses six 17 m bodies, with 104.5 m assumed overall length pending coupler
and gangway design. The central tare target is 14.2 t/car, including a 5.2 t
equipped GFRP body, 3 t ferrite, 30 kWh services battery and full 1.8 t growth
reserve. Four passenger doors per car are the current body takeoff. Density,
laminate/core substitutions, unsized members and body-side/magnetic-carrier
ownership are explicit. These budgets are distinct from weighed hardware and a
complete manufactured-parts BOM.

The ordinary guidebeam candidate is a 25 m, 0.80 × 1.80 m closed box with 100 mm
webs, 150 mm flanges and two 0.4 m end infills. Concrete plus unchanged passive
iron is about 43.1 t before outstanding reinforcement/attachment detail mass and
rigging. Hollow columns, caps and shallow/single-shaft/pile-group foundations are
quantity studies; qualified ground selection remains absent.

## Implemented checks and open boundaries

| Capability | Implemented scope | Evidence still required |
|---|---|---|
| Station trajectory | Jerk-limited launch, zero-thrust coast and receiving brake; energy closure and assumed magnetic-band overlap | Measured drag/magnetic losses, actual grades/wind, useful thrust, voltage/current/thermal limits and robust arrival margins |
| Station electrical costs | Fixed-group/section alternatives and separate power/charging target-rate rows | Configured equipment, supplier quotations, grid capacity, real duty and complete station scope |
| Body/civil quantities | GFRP panel mass cases, interface ownership, beam/end-infill quantities, support/foundation screens and target costs | Orthotropic structural analysis, member/joint/prestress/rebar detailing, soils, tolerances and construction-stage acceptance |
| Magnet orientations | Point-dipole ring reference and finite-block orientation inventories | Nonlinear finite-geometry steel/coil force/loss/demagnetization maps and measured shared-field behavior; no ring-gain credit |
| Native geometry | Partial panel/interface/civil/station definitions, export/reopening checks, retained images and visibility sequences | Complete production geometry, joints, equipment, drawings and qualified manufacturing tolerances |
| Rust support control | Module allocation, virtual replay, protection interfaces and support-preserving stop obligations | Actual magnetic/sensor plant, independent protection, physical I/O and measured timing |
| Launch ownership | Offline corridor/receiving-berth reservation, committed occupancy and full-clearance protocol checks | Authenticated complete-consist sensing, real receiving readiness, independent stopping and qualified system integration |
| Coupled replay | One stationary rigid car exchanging ideal support forces with a flexible vertical beam | Moving six-car loads, flexible vehicle, lateral/torsional/joint/soil response and correlated faults/ride/stability |
| Adaptive design | Previous-result-guided vehicle/beam/gain proposals, ancestry, Pareto observations and separate confirmation | Completed parts and qualified evaluators/plant before manufacturing or operating selection |
| Factory and city delivery | Conditional two-shift bottleneck capacities, duty/fleet, route quantities and process needs | Measured cure/crew/logistics rates, surveys, route recovery, complete economics and accepted instances |

The [adaptive search](iteration.py), configured in [iteration.toml](iteration.toml),
has explicit evaluation/stagnation budgets and exact-source restart receipts.
Failed confirmation disqualifies the exact revision. [Published history](../../docs/design-engine/ferrite-maglev/iterative/README.md)
retains proposals, ancestry, traces and recommendation. Mass/inertia allocations
and preference weights remain research assumptions. An analytical recommendation
does not automatically change acceptance criteria or reference configuration.

## Operation, manufacture and costs

The operating reference is a 90 s flat 1 km trip with 0.8 m/s² acceleration and
service deceleration, 0.6 m/s³ jerk and 190 s scheduled headway. The 180 s case
has little clearance margin at the assumed 60 s dwell. Grade, wind, drag,
arrival speed and receiving-brake availability must be resolved per span.
A coasting train already committed to a corridor cannot be stopped by expiring
its permission. Persistent ownership and positive tail clearance are required.
Receiver faults, independent stopping/holding and a train stranded outside powered
zones remain separate design requirements; a distant stator cannot restart it.

At 60 kW/car hot services, a 90 s trip uses 9 kWh/train. If 45 s of a 60 s dwell
is available for charging, the remaining 15 s adds 1.5 kWh to battery demand.
Restoring 10.5 kWh in 45 s takes 840 kW, plus 360 kW direct services: **1.20 MW/train
before charger losses**. Battery reserve, repeated charge duty and ageing remain
unqualified. The 60 s charging alternative needs a distinct rated interface.

The supplied civil target-rate comparison falls from about USD 4.255 million to
USD 3.313 million per two-direction ordinary route-km. It is an incomplete
no-walkway scope and the USD 22,000 ordinary-support price is a procurement target.
Station propulsion/charging equipment is additional, separately labelled scope.
Reserve does not price missing station structures, evacuation, land, factory
capital, qualification, recovery, finance or other programme work. Lower mass
alone earns no proportional ground or support saving.

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

Videos are final-position visibility sequences. They do not simulate motion,
collision-free erection, crane operation or chute deployment. CAD integrity,
PDE residuals, virtual controller ticks and consistent publication hashes each
establish only their checked digital scope. [Closure work](../../docs/ROADMAP.md#primary-maglev-closure-queue)
and [v0.5.2 development notes](../../docs/releases/v0.5.2.md) remain explicit.

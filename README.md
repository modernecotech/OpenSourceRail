# OpenSourceRail

**v0.5.2 development — ferrite maglev with fixed powered zones, local manufacture and compact elevated routes.** Fixed linear motors at stations launch and receive the train; selected longer legs add located midway accelerator zones. The remaining guideway is unpowered. Onboard ferrite PM-biased active support and guidance remain independent of traction. Repeated concrete guidebeams, structural GFRP sandwich panels and open Rust controls are the current design strategy.

![OpenSourceRail ferrite-maglev station concept in Baghdad](OpenSourceRail%20maglev%20station%20concept.png)

*Illustrative development concept. Baghdad uses six 17 m bodies; complete engineering and physical acceptance remain open.*

**[Calculations, native CAD, images and videos](docs/design-engine/ferrite-maglev/reference/index.html) · [City packages](engineering/ferrite_maglev/city-index.md) · [Implementation and open work](engineering/ferrite_maglev/README.md)**

## Why this design

- **Simplify the train.** Fixed wayside linear synchronous motors remove the main propulsion windings, traction inverter and large traction-energy battery from the vehicle. Normal running gear avoids wheelsets, gearboxes and rotating traction motors. Support coils, drives, sensors, cooling, protection, doors, HVAC and emergency systems remain necessary.
- **Reduce noise and wear.** Contactless running removes rolling contact from normal operation. Acoustic performance, magnetic losses, energy use and reliability need measurement.
- **Build more value locally.** Prioritise concrete casting, reinforcement/prestress work, composite panels, carriers, winding cassettes, interiors, wiring, Rust software and integration. Prefer verified British manufacture for UK machinery procurement. Imported cells, semiconductors, sensors and materials retain their actual origin in local-content accounting.
- **Reach constrained city corridors.** Compact viaducts aim to reduce surface occupation and disruption, expanding useful station locations. The planning objective is 99% elevated mainline with straight tangents where rights, buildings, utilities, waterways, wildlife and access permit.
- **Optimise the complete installed system.** Include vehicle mass, station electrical plant, guideway, foundations, factory processes, logistics, erection, maintenance and recovery. Savings in onboard equipment must be compared against the station/booster power equipment and independent rescue facilities added along the route.

The guideway target is one concrete beam per direction, with necessary reaction iron, supports, foundations and connections. Removing a continuous external walkway requires an accepted evacuation alternative. Vertical spiral controlled-descent chutes are the preferred research candidate; safe landings at every stopping location, assisted evacuation, fire, weather, deployment and rescue remain open.

![Vertical spiral escape chute concept](Vertical%20spiral%20escape%20chute%20concept.png)

*Illustrative concept; no qualified train installation or walkway-removal approval is claimed.*

## Current design and evidence

The six-car Baghdad study retains a **14.2 t/car tare target**, including a **5.2 t equipped GFRP body**, 3 t ferrite and a 30 kWh services battery. Four passenger doors per car are the body-study basis. The wider-profile urban/suburban comparisons use 50 kWh/car: **14.4 t tare and 26.4 t AW3 per car**, with the added pack mass included once. The manufactured design dossier uses this heavier case for hardpoints, passive support, civil loads and the emergency-brake proposal, and retains the 30 kWh case separately. Counted frame members, supported panels, joints and couplers remain provisional. Frame and exact brake growth consume part of the existing 1.8 t/car reserve; they are not free mass. Complete equipment, joined-body strength, fatigue, centre of gravity and inertia remain unqualified.

The current ordinary civil candidate is a **25 m, 0.80 m wide closed concrete box**, with 100 mm webs, 150 mm flanges and explicit end infills. Its selected depth, mass and stiffness are recorded in the [current configuration](ferrite-maglev-study.toml) and source-bound report. The supplied 1.80 m-deep case remains a comparative benchmark. Prestress/handling, anchored bearings, hollow columns and larger-footing candidates now have calculated detail screens. Ground-dependent selection, connection tests and construction acceptance remain open.

Passenger stops target **at least 1.5 km spacing and about 2 km on urban lines**, with **4–5 km on suburban lines** and fixed midway acceleration where the calculated trajectory requires it. Junction stations serve **passenger transfers between independent fixed lines**; they do not switch trains between routes. Straight corridors are the planning objective, subject to real land, buildings, utilities, grades and evacuation access. Retained nearby junctions that conflict with the minimum spacing stay visible as exceptions requiring a transfer/access decision.

The new [corridor study](docs/design-engine/ferrite-maglev/corridor/README.md) evaluates longer motion profiles, finite installed motor zones, voltage/current, services charging, protected-resource timing and actual Rust fault responses. It retains capacity shortfalls and missing physical geometry confirmation. The 1 km/88 s/180 s station and moving studies are explicitly retained **component benchmarks**; they do not prove the wider-spacing plan.

The separate [multi-train prototype](docs/design-engine/ferrite-maglev/line-capacity/README.md) executes progressive reservations, full-tail release and conservative stopping envelopes through the Rust ledger. It retains adverse cases and compares exclusive whole-leg operation. It does not approve route-wide protection or change city capacity assumptions.

Longer gaps need explicit services storage and recovery. The [booster/rescue kit study](docs/design-engine/ferrite-maglev/booster-kit/README.md) compares independent accessible rescue nodes at intervals up to 1 km, 0.5/1 m/s winches and 30/50/60 kWh services packs. Rope, drum, portal, foundations, independent power, mass and unquoted cost targets are counted. A midway accelerator is not automatically a rescue facility. Larger packs and faster winches carry their extra mass, electrical rating and cost; located access, certified hardware and essential-load assumptions remain unqualified.

City bills separately show fleet, ordinary and terminal civil work, station electrical plant, conditional footing increments, located booster hardware and rescue kits. Fewer passenger platforms do not establish a complete saving: power zones, transfer hubs, access, recovery, land and physical acceptance still need their full quantities and costs. Complete installed cost remains unknown.

## Baghdad interchange alternatives

The default Baghdad plan remains **273 proposed stops with 10 transfer-spacing conflicts**. The [interchange investigation](docs/design-engine/ferrite-maglev/interchange-hubs/README.md) compares two different ideas: extended passenger links on unchanged train guideways, and coordinated shared-site hub concepts that move the involved guideways. None is selected. Trains continue on independent fixed lines, without routing switches.

![Baghdad retained corridors, extended transfer links and unselected shared-site hub concept](docs/design-engine/ferrite-maglev/interchange-hubs/overview.svg)

Grouping nearby stations does not shorten the physical walk. The extended-link options retain original boarding platforms and calculate reference connector lengths, walking sensitivities, changed operating duties and partial cost credits. The original shared-site concepts draw the involved lines through one location; their 350 m tangents and 100 m compact walk were comparison assumptions. The separate geometry study below now fits powered zones, directional approaches, platforms and passenger routes. Lifts, shade, resting places, peak passenger flows, evacuation and complete access costs must be qualified before a hub can replace a spacing exception. [Inspect the original alternatives and source evidence](docs/design-engine/ferrite-maglev/interchange-hubs/study.json.gz).

The [access engineering study](docs/design-engine/ferrite-maglev/hub-access/README.md) now counts connector modules, supports and access structures and compares passenger pulses and lift outages. A reference path along a train alignment is not itself a buildable pedestrian bridge; the physical access corridor and platform interfaces need their own clearance and site checks. No hub is selected from provisional flow or quantity results.

The [station benchmark](docs/design-engine/ferrite-maglev/station-powered/README.md), [body/civil quantities](docs/design-engine/ferrite-maglev/station-structure/README.md), [manufactured detail dossier](docs/design-engine/ferrite-maglev/manufactured-dossier/README.md), [native details](docs/design-engine/ferrite-maglev/manufactured-native/native-cad.json) and [integrated Rust campaign](docs/design-engine/ferrite-maglev/system-campaign/README.md) retain exact sources and open gates.

The [moving six-car study](docs/design-engine/ferrite-maglev/moving-train/README.md) now runs actual Rust support controllers against six rigid cars, repeated flexible spans and a longitudinal coupler chain. Its [video](docs/design-engine/ferrite-maglev/moving-train/moving-train.mp4) uses calculated motion with declared visual amplification. Ideal independently allocated magnetic forces, linear beams and virtual sensing limit the result; measured maps, shared-field phase, flexible bodies, lateral/soil/contact response and hardware timing remain open. The older stationary single-car demonstration is retained as a separate limited case. Legacy CAD videos show final-position visibility; the assembled-body movie adds illustrative installation translations, without collision-free assembly acceptance.

The adaptive designer generates vehicle/beam/Rust variants and retains failed comparisons and confirmation evidence. Ring-field benchmarks and orientation seeds receive no railway lift or mass-saving credit. The retained integrated benchmark and new corridor campaign exercise protected resources and fault responses through actual Rust, with virtual occupancy; cross-controller handover is still open. Independent friction-brake and station-winch proposals have numerical sizing and structural load-path screens, without qualified stopping or recovery hardware.

**Accepted engineering and physical releases: 0.** Complete production drawings, qualified materials, site investigations, calibrated dynamics, hardware tests and independent acceptance remain necessary. Published [v0.5.1](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.5.1) is preserved; [v0.5.2 development notes](docs/releases/v0.5.2.md) describe this revision.

The [qualification programme](docs/design-engine/ferrite-maglev/qualification/README.md) gives every applicable requirement a dependency chain and evidence route, including physical specimen/rig procedures and typed raw measurements. Its assessor rejects stale revisions, substituted data and simulated physical evidence. Prepared protocols do not constitute completed tests. Digital study bundles use numbered, bounded archives with exact committed source hashes and independent verification, rather than dropping evidence to fit one archive.

The [assembled structural candidate](docs/design-engine/ferrite-maglev/assembled-body/README.md) places fitted material regions, mounting holes and fasteners together and derives partial mass and inertia from reopened native solids. It retains the earlier crossmember/guideway interference as a rejected control. Its images and assembly visibility video show the defined structure; omitted equipment, joined-body behavior and physical qualification remain open. The [shared-hub geometry study](docs/design-engine/ferrite-maglev/shared-hub-layout/README.md) fits both directional approaches, powered zones, platforms and door-to-door paths, preserving rejected layouts and counting new geometry without assuming former civil prices.

A [fresh full-mass stiffness sensitivity](engineering/assurance/v052-drives-development/body-axial-summary.json) records a moving-system hold: the body-derived series stiffness produces about11.4° magnetic phase spread against the existing5° confirmation criterion, although its gap screens pass. The100MN/m reference produces1.75°. These are rigid-car comparisons with complete retained traces and a [source receipt](engineering/assurance/v052-drives-development/body-axial-receipt.json); they do not qualify flexible bodies or promote the new structure into the operating model.

The [repeatable longitudinal-stock sweep](docs/design-engine/ferrite-maglev/body-stiffness/README.md) tests four steel-spine alternatives after that failure, counting drilled walls, longer crush spacers and added full-AW3 mass. Three alternatives pass the same phase screen. They remain unselected: material, thin-wall joints, heavier structural loads and flexible-body behavior still require verification. The GFRP result and all rejected comparisons remain visible.

## Run it

The [active-control and launch construction package](docs/design-engine/ferrite-maglev/drive-construction/README.md) now spells out the electrical construction. Ferrite provides bias flux; active gap/guidance feedback regulates onboard coil current. A car SBC supervises allocation, proposed local MCU loops regulate current, and independent protection/support power must handle faults. The [BOM](docs/design-engine/ferrite-maglev/drive-construction/bom.csv) counts 432 coils and 288 current circuits per six-car train. Separate wayside three-phase LSM converters launch and receive trains. Winding schedules, connections, voltage/current/thermal alternatives, braking-energy screens and actual Rust coupon tests are retained. Magnetic maps, complete coil geometry, electronics and moving-train actuator integration remain open; these quantities do not silently change vehicle mass or city costs.

The compact support winding passes declared depth/packing and current screens; larger-pack and lower-turn failures remain retained. The launch comparison exposes substantial losses: the one-turn urban case reaches about **3.13 MW peak copper heating** when both long fixed groups carry current, with **7.18 kWh terminal winding heat per trip** under the stated hot-resistance assumptions. A current/voltage pass does not select the cheapest or most efficient system. Group length, independent current allocation, converter count, shared magnetic maps and real thermal duty still need comparison; existing city electrical targets are unquoted planning allowances.

The [UK procurement supplement](engineering/ferrite_maglev/README.md#uk-power-module-procurement) adds Dynex's British manufacturing capability as the first candidate for launch power modules and custom assemblies, alongside an explicitly imported Infineon comparison. Exact order origins remain unconfirmed; a UK brand or address is not manufacturing evidence for a particular batch.

```bash
./osr build                    # rebuild stale implemented studies and publications
./osr design station           # launch, coast, receive, power and overlap study
./osr design drives            # active coils, current/FOC software, launch construction and BOM
./osr design structure         # GFRP, magnetic seeds, civil and production quantities
./osr design corridor          # wider-spacing fixed-zone trajectories and controls
./osr design booster-kit       # booster quantities and independently equipped rescue alternatives
./osr design line-capacity     # local multi-train reservation and stopping-envelope prototype
./osr design hub-access        # interchange structure, passenger pulse and outage studies
./osr design qualification     # requirement task chains and physical test protocols
./osr design assembled-body    # fitted structural regions, native checks and partial mass
./osr design body-stiffness    # failure-directed stock alternatives at full AW3 mass
./osr design shared-hub-layout # station approaches, platforms and actual passenger paths
./osr design protocol          # offline station launch/reservation checks
./osr design iterate           # bounded vehicle/beam/Rust study and confirmation
./osr city baghdad             # regenerate Baghdad planning and costing
./osr sim baghdad --cycles 2   # offline services-energy replay
./osr workbench                # local review UI
./osr test                     # current automated checks
./osr readiness                # source and acceptance gates
./osr book                     # source-bound reader PDF
```

The [stopped-controller recovery study](docs/design-engine/ferrite-maglev/stopped-recovery/README.md) tests local recovery from prepared and committed checkpoints, including two trains and adverse evidence. A new fenced epoch, quarantine and complete fresh stopped proofs are required; old contracts stay retired and fresh prepare/commit is mandatory. Moving recovery, cross-controller handover and installed authentication remain open.

The dependency runner resumes implemented work after interruption and holds downstream output when a prerequisite fails. The Workbench has no live train-control authority. A committed coasting train needs protected receiving capability; a receiver fault, stranded train and stationary recovery each require an engineered response.

## Find your way

| Task | Start here |
|---|---|
| Understand the design | [Architecture](docs/ARCHITECTURE.md), [overview](docs/open-source-rail-overview.md), [roadmap](docs/ROADMAP.md) |
| Review engineering | [Current report](docs/design-engine/ferrite-maglev/reference/index.html), [configuration](engineering/ferrite_maglev/reference-configuration.toml), [implementation](engineering/ferrite_maglev/README.md) |
| Plan a city | [City catalogue](engineering/ferrite_maglev/city-index.md), [Baghdad package](cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/README.md) |
| Review manufacture and costs | [Process model](engineering/ferrite_maglev/manufacturing.py), [body/civil study](engineering/ferrite_maglev/station_structure.py), [planning rates](engineering/ferrite_maglev/data/cost-rates.json) |
| Review controls | [Rust maglev controls](crates/osr-maglev-control/README.md), [offline profile](deployment/maglev.toml) |
| Reproduce evidence | [Capabilities](docs/capabilities/README.md), [reader book](OpenSourceRail-Book.pdf) |

Architecture policy is in [infrastructure.toml](lib/templates/infrastructure.toml). Current inputs and evaluators are in [engineering/ferrite_maglev](engineering/ferrite_maglev/README.md). Each city has a `city.json` input and generated `engineering/maglev` package. Manifests bind source and output bytes; they do not approve engineering.

Software is Apache 2.0, open physical designs use CERN-OHL-S v2, and documentation is CC-BY-SA 4.0. See [LICENSE.md](LICENSE.md) and [LICENSES](LICENSES/README.md).

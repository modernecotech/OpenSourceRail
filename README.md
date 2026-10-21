# OpenSourceRail

**v0.5.2 development — station-powered ferrite maglev, local manufacture and compact elevated routes.** Fixed station linear motors launch and receive the train; it coasts through unpowered interstation spans. Onboard ferrite PM-biased active support and guidance remain independent of traction. Repeated concrete guidebeams, structural GFRP sandwich panels and open Rust controls are the current design strategy.

![OpenSourceRail ferrite-maglev station concept in Baghdad](OpenSourceRail%20maglev%20station%20concept.png)

*Illustrative development concept. Baghdad uses six 17 m bodies; complete engineering and physical acceptance remain open.*

**[Calculations, native CAD, images and videos](docs/design-engine/ferrite-maglev/reference/index.html) · [City packages](engineering/ferrite_maglev/city-index.md) · [Implementation and open work](engineering/ferrite_maglev/README.md)**

## Why this design

- **Simplify the train.** Station-mounted linear synchronous motors remove the main propulsion windings, traction inverter and large traction-energy battery from the vehicle. Normal running gear avoids wheelsets, gearboxes and rotating traction motors. Support coils, drives, sensors, cooling, protection, doors, HVAC and emergency systems remain necessary.
- **Reduce noise and wear.** Contactless running removes rolling contact from normal operation. Acoustic performance, magnetic losses, energy use and reliability need measurement.
- **Build more value locally.** Prioritise concrete casting, reinforcement/prestress work, composite panels, carriers, winding cassettes, interiors, wiring, Rust software and integration. Prefer verified British manufacture for UK machinery procurement. Imported cells, semiconductors, sensors and materials retain their actual origin in local-content accounting.
- **Reach constrained city corridors.** Compact viaducts aim to reduce surface occupation and disruption, expanding useful station locations. The planning objective is 99% elevated mainline with straight tangents where rights, buildings, utilities, waterways, wildlife and access permit.
- **Optimise the complete installed system.** Include vehicle mass, station electrical plant, guideway, foundations, factory processes, logistics, erection, maintenance and recovery. Savings in onboard equipment must be compared against the equipment added at stations.

The guideway target is one concrete beam per direction, with necessary reaction iron, supports, foundations and connections. Removing a continuous external walkway requires an accepted evacuation alternative. Vertical spiral controlled-descent chutes are the preferred research candidate; safe landings at every stopping location, assisted evacuation, fire, weather, deployment and rescue remain open.

![Vertical spiral escape chute concept](Vertical%20spiral%20escape%20chute%20concept.png)

*Illustrative concept; no qualified train installation or walkway-removal approval is claimed.*

## Current design and evidence

The six-car Baghdad study uses a **14.2 t/car tare target**, including a **5.2 t equipped structural GFRP body**, 3 t ferrite, a 30 kWh services battery and the full 1.8 t growth reserve. Four passenger doors per car are the body-study basis. These are component budgets and calculated panel quantities; complete members, joints, equipment mass, centre of gravity and inertia remain unresolved.

The ordinary civil candidate is a **25 m span, 0.80 × 1.80 m closed concrete box**, with 100 mm webs, 150 mm flanges and explicit end infills. Hollow columns, caps and alternative foundation families are compared by quantity. Ground-dependent foundation selection and prestress, reinforcement, connection and erection qualification remain open.

The launch study solves a jerk-limited 90 s flat 1 km trip, station winding overlap, power and receiving braking. The present schedule basis is **190 s headway**. Grade, drag, wind, arrival-speed and receiving-brake readiness are explicit route gates; the nominal flat trajectory does not prove a route is operable. A 45 s charge within a 60 s dwell requires **1.20 MW per berthed train** under the hot-services assumption, before charger losses. Station electrical targets are priced separately from the incomplete civil subtotal.

[Station operating study](docs/design-engine/ferrite-maglev/station-powered/README.md), [body and civil quantities](docs/design-engine/ferrite-maglev/station-structure/README.md), [partial native geometry](docs/design-engine/ferrite-maglev/station-native/native-cad.json) and [launch protocol evidence](docs/design-engine/ferrite-maglev/station-protocol/README.md) retain their source and scope. Native images and assembly visibility videos show final-position geometry; they do not demonstrate motion, collision-free erection or deployment.

The adaptive designer generates vehicle-mass, beam and Rust-gain variants from preceding results and uses separate confirmation scenarios. Its coupled plant remains **one stationary rigid car and a vertical flexible beam with ideal force actuators**. Moving six-car magnetic/structural dynamics, measured force/loss maps and physical controller timing are not implemented evidence. Ring-field benchmarks and block orientation seeds receive no railway lift or mass-saving credit.

**Accepted engineering and physical releases: 0.** Complete production drawings, qualified materials, site investigations, calibrated dynamics, hardware tests and independent acceptance remain necessary. Published [v0.5.1](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.5.1) is preserved; [v0.5.2 development notes](docs/releases/v0.5.2.md) describe this revision.

## Run it

```bash
./osr build                    # rebuild stale implemented studies and publications
./osr design station           # launch, coast, receive, power and overlap study
./osr design structure         # GFRP, magnetic seeds, civil and production quantities
./osr design protocol          # offline station launch/reservation checks
./osr design iterate           # bounded vehicle/beam/Rust study and confirmation
./osr city baghdad             # regenerate Baghdad planning and costing
./osr sim baghdad --cycles 2   # offline services-energy replay
./osr workbench                # local review UI
./osr test                     # current automated checks
./osr readiness                # source and acceptance gates
./osr book                     # source-bound reader PDF
```

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

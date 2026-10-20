# OpenSourceRail

**v0.5 — fewer moving parts, local manufacture and compact elevated urban routes.** OpenSourceRail develops ferrite PM-biased maglev to simplify vehicles, guideways and the factories that build them. Fixed onboard magnetic modules, passive reaction iron, repeatable concrete guidebeams and open Rust controls are the current design basis.

![OpenSourceRail ferrite-maglev station concept in Baghdad](OpenSourceRail%20maglev%20station%20concept.png)

*Development concept. Baghdad uses six 17 m car bodies; complete engineering and physical acceptance remain open.*

**[Calculations, native CAD, images and videos](docs/design-engine/ferrite-maglev/reference/index.html) · [City packages](engineering/ferrite_maglev/city-index.md) · [Implementation and open work](engineering/ferrite_maglev/README.md)**

## Why this design

- **Simplify normal running gear.** Fixed magnetic modules and powered linear electromagnetic propulsion eliminate conventional rotating traction motors, gearboxes and wheelsets. Windings, power electronics, cooling, sensors, protection and passenger equipment remain necessary.
- **Reduce noise and wear.** Contactless running removes rolling contact from normal operation. Actual acoustic performance, energy use, maintenance and reliability require measurement.
- **Build more value locally.** Prioritise guidebeam casting, structural fabrication, ferrite-cartridge assembly, winding, panels, interiors, wiring and integration. Rust controls on off-the-shelf computers support local development and repair. Imported cells, semiconductors, sensors and materials retain their actual origin in local-content accounting.
- **Reach constrained city corridors.** Compact viaducts aim to reduce surface occupation and disruption, expanding useful station locations. The planning objective is 99% elevated mainline with straight tangents where land rights, buildings, utilities, water, wildlife and station access permit.
- **Optimise the installed system.** Foundations, piers, beams, joints, stations, services, vehicle mass, transport, factory processes and erection belong in the same comparison. Offsite manufacture and inspection should reduce site work and support repeatable assembly.

The guideway target is one concrete beam per direction, with necessary reaction iron, supports, foundations and connections. Removing a continuous external walkway depends on an accepted evacuation alternative. Vertical spiral controlled-descent chutes are the preferred research candidate; all-stop landing access, assisted evacuation, fire, weather, deployment, rescue and maintenance still require validation.

![Vertical spiral escape chute concept](Vertical%20spiral%20escape%20chute%20concept.png)

*Illustrative concept; no qualified train installation or walkway-removal approval is claimed.*

## Current work

The repository connects a current requirements and systems register to bounded magnetic, vehicle, civil and control studies. Native FreeCAD/STEP packets include a partial magnetic interface, civil bay, beam-only variant, evacuation entry, support envelopes and the six-car Baghdad station arrangement. Retained images and short assembly visibility videos show those exact models. They illustrate final-position parts, rather than validated motion or erection trajectories.

City packages use explicit geography and service inputs to recalculate formations, fleet, charging, guideway quantities and provisional costs. The cost model uses current material quantities and manufacturing process allowances. Complete programme costs, supplier quotations and origin-traced local-content percentages remain open. Plans include processes and equipment needs; these are not released shop instructions.

**Accepted engineering and physical releases: 0.** Passing calculations, CAD export, software tests or publication checks establishes only the checked digital scope. Complete production drawings, qualified materials, ground investigations, calibrated magnetic/dynamic models, physical hardware tests and independent acceptance are still needed.

## Run it

```bash
./osr build                    # rebuild stale implemented studies and publications
./osr city baghdad             # regenerate the Baghdad planning package
./osr sim baghdad --cycles 2   # offline charging/SOC replay
./osr workbench                # local review UI
./osr test                     # current automated checks
./osr readiness                # current source and acceptance gates
./osr book                     # source-bound reader PDF
```

The dependency runner resumes implemented work after interruption and holds downstream outputs when a prerequisite fails. It does not create missing physical evidence or certify completion. The local Workbench is a review interface without live train-control authority.

## Find your way

| Task | Start here |
|---|---|
| Understand the design | [Architecture](docs/ARCHITECTURE.md), [overview](docs/open-source-rail-overview.md), [roadmap](docs/ROADMAP.md) |
| Review engineering | [Current report](docs/design-engine/ferrite-maglev/reference/index.html), [configuration](engineering/ferrite_maglev/reference-configuration.toml), [implementation](engineering/ferrite_maglev/README.md) |
| Plan a city | [City catalogue](engineering/ferrite_maglev/city-index.md), [Baghdad package](cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/README.md) |
| Review manufacturing and costs | [Process and cost model](engineering/ferrite_maglev/manufacturing.py), [planning rates](engineering/ferrite_maglev/data/cost-rates.json), city package manufacturing records |
| Review controls | [Rust maglev controls](crates/osr-maglev-control/README.md), [offline development profile](deployment/maglev.toml) |
| Reproduce evidence | [Capabilities](docs/capabilities/README.md), [reader book](OpenSourceRail-Book.pdf) |

## Source of truth

Architecture policy is in [infrastructure.toml](lib/templates/infrastructure.toml). Current engineering inputs, quantities, requirements, process assumptions and evaluators are in [engineering/ferrite_maglev](engineering/ferrite_maglev/README.md). Each city has a `city.json` input and a generated `engineering/maglev` package. Publication manifests bind source and output hashes; hashes identify bytes and do not approve engineering.

Software is Apache 2.0, open physical designs use CERN-OHL-S v2, and documentation is CC-BY-SA 4.0. See [LICENSE.md](LICENSE.md) and [LICENSES](LICENSES/README.md).

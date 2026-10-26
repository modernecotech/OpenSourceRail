# OpenSourceRail

OpenSourceRail develops simple, affordable urban transport that can be manufactured and maintained locally. Lightweight trains run on repeated concrete beams with passive steel facings. Permanent magnets, suspension controls and essential passenger services stay on the train; station windings provide launch and controlled arrival. Passengers transfer between fixed lines.

Our approach is to compare the complete system: vehicle weight and comfort, magnetic support, station power, civil construction, service frequency and whole-life cost. Open calculations, reusable components and repairable assemblies are intended to keep cost and complexity down.

## Current development default

The **comfort-first six-car design is the repository default**, selected by [development-baseline.toml](engineering/development-baseline.toml). The same vehicle, body and magnet identities drive the current engineering packet, all city calculations, delivery records, Workbench and reader. It is selected for development; stable physical operation and manufacturing release remain unestablished.

| Design choice | Default |
|---|---|
| Formation | Six 17 m cars; 104.5 m train including gaps |
| Passengers per car | 44 fixed seats + two wheelchair places; no planned standing |
| Seating | Four abreast where structure permits; wall seating at doors |
| Passenger doors | Two on one side; platform and evacuation design must match |
| Structure and fitout | Aluminium extrusion frame, retained GFRP sides, lightweight sandwich floor/roof and benches |
| Windows | Retained laminated glass; plastic remains an unqualified alternative |
| Suspension research | Onboard neodymium Halbach PM assembly with active stabilization still to close |
| Service target | 120-second headway; 276 people/train; **8,280 passengers/hour/direction** |
| Retained-stop network proposal | 72 km/h launch cap, 35-second dwell; station winding selected for each leg |
| Accounted mass | 17.357 t tare/car; 20.807 t at the 46-person cap; complete installed mass/CG still unknown |

The lower passenger cap is a comfort and load-management choice. It reduces normal load but also lowers capacity from the former 14,400 comparison. Two-minute departures remain a target supported by analytical and software-method tests, not a demonstrated safe operating headway. Crowd loading, accessibility, emergency exit and passenger admission still require verification.

Read the [current engineering dossier](docs/design-engine/current/README.md), [all-city comparison](docs/design-engine/current/cities.json), [remaining work](docs/ROADMAP.md) or [illustrated reader](OpenSourceRail-Book.pdf). [README coverage](docs/design-engine/current/readme-coverage.md) identifies historical documents without rewriting their evidence.

## Use the repository

```bash
./install.sh
./osr status
./osr readiness
./osr workbench
./osr sim baghdad
./osr build
./osr verify
./osr book --check
./osr test
```

`./osr` and `./osr infrastructure` select the same current design. The Workbench opens the current candidate and its city packages. Build regenerates current analytical planning and delivery exports; unavailable physical adapters return an explicit hold. Numerical convergence or a completed software job never grants physical acceptance.

The default Baghdad retained-stop calculation requires **906 six-car trainsets** and approximately **390.5 km of directional station winding** under its declared flat-route, drag, acceleration, dwell and reserve hypotheses. Four motor-interval overlaps, physical braking, hot-weather HVAC and actual costs remain open. Changing vehicle mass, load or service assumptions requires regeneration; the former fleet and financing totals do not transfer to this design.

## What still needs to work

One equipped physical configuration must establish stable multiaxis hover, control authority, thermal duty, complete mass/CG/inertia, structure and braking before a magnetic-force-driven journey can be demonstrated. Current capture-energy and hot-roof-core screens fail their declared cases. Supplier data, prototypes, site investigation and independent confirmation are required. See the [live design gates](docs/design-engine/current/summary.json).

Native FreeCAD/STEP evidence describes the exact retained material assembly. Actual Rust `osr-maglev-control` executions test protection protocols with synthetic healthy gaps and assumed braking. Ideal-force Chrono journeys are method benchmarks. None demonstrates this train hovering or completing a physical 2 km journey.

## Historical methods and contributions

The [pre-default archive](docs/archives/pre-comfort-default/README.md) pins the earlier reader, plans and numerical receipts to their real source revision. `./osr legacy verify` checks that historical evidence; regeneration belongs in an isolated checkout. The [ferrite reference implementation](engineering/ferrite_maglev/README.md) and [retained controller deployment settings](deployment/maglev.toml) remain available as named historical methods.

Start with [engineering guidance](engineering/README.md), [project instructions](AGENTS.md), [tools](tools/README.md) and the [documentation index](docs/INDEX.md). Keep every output tied to its candidate and evaluation; unknown stock, performance and cost stay unknown.

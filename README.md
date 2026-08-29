# OpenSourceRail

OpenSourceRail is an open-source, deterministic platform for designing,
testing, building and operating affordable urban rail systems. It connects
city and service planning, GIS, CAD/IFC, rolling stock, embedded software,
simulation, operations, costs and assurance in one Git-reviewable workflow.

It is intended to give public authorities, universities, engineering teams
and operators a common model rather than a collection of disconnected maps,
spreadsheets and vendor applications. A planner can change a station, route,
service period or fleet assumption, regenerate the affected artifacts, run the
integrated simulation, and review the resulting engineering and cost evidence.

> [!IMPORTANT]
> Repository outputs are planning and engineering-screening evidence. They are
> not feasibility studies, supplier bids, construction releases, safety
> certificates, funding approvals or government endorsements.

![OpenSourceRail light-metro reference trainset](docs/assets/solar-metro-trainset.png)

**Start here:** read or download the [complete PDF book](OpenSourceRail-Book.pdf),
open the [one-page overview](docs/open-source-rail-overview.html), or install and
start the Workbench with `./install.sh` followed by `./scripts/osr`.

The public evidence scope covers **265 cities in 43 developing countries**.
The engineering catalogue contains 266 models; one European comparison model
is retained for technical inspection but excluded from portfolio totals,
public evidence totals and front-page examples.

## Feature Highlights

| Capability | Current implementation |
|---|---|
| Deterministic city generation | Reproducible network, station, fleet, energy, engineering, finance and operations packages under [designs/](designs/README.md). |
| Integrated Workbench | [City Studio, simulation, OCC training and Ops Core](docs/workbench/README.md) share city, actor, immutable revision, approved baseline, run and selected-asset context without merging authority boundaries. |
| Interactive network and service planning | Edit lines, stations and alignment over 16 switchable local GIS layers; inspect roads, buildings, water, existing rail, demand, buildability, places and engineering assets; plan OD demand and service by line/day/time; compile content-addressed revisions for Git review. |
| Software in the loop | One deterministic simulation connects train, station, energy, wayside, point/crossing, regenerative-braking and depot components to OCC evidence. |
| Civil BIM and GIS | Generate OSR-ALN, GIS, IFC4.3, IDS/BCF, quantities, classifications and 4D construction review through the [Bonsai civil workflow](docs/civil/bonsai-ifc-workflow.md). |
| Buildable modular trainset | The LM3 product tree includes simplified captive fasteners, service rails, plug-in illumination, fixture adapters, adjustable doors and dry-serviceable windows. |
| Automatic cost propagation | CAD-indexed quantities feed the civil rate contract, city CAPEX, finance, IFC properties, national briefs and the developing-world [portfolio summary](docs/portfolio-summary.md). |
| Operations and assurance | Manufacturing, QA, maintenance, assets, work orders, acceptance evidence and a machine-checkable safety case remain linked to source artifacts. |
| Deterministic browser testing | Pinned Playwright acceptance verifies the integrated browser applications, adapters, engineering jobs and restart persistence. |

The current city cost model uses about **$0.9M per 3-car light-metro trainset**.
The generated LM3 build record currently estimates $885k before
rounding to that planning unit. Each country carries one shared lean railway
production setup at **$60k per supported vehicle/car module**; supplier
qualification, homologation, warranty, spares and deployment-specific work
remain separate evidence or cost gates.

## Current System

| City Studio | Civil IFC coordination | Operations and evidence |
|---|---|---|
| ![City Studio deterministic GIS workspace](docs/screenshots/city-studio/gis-workspace.png) | ![Bonsai IFC4.3 coordination model](docs/screenshots/civil/bonsai-ifc4x3-civil-coordination.png) | ![Operations portal acceptance dashboard](docs/screenshots/operations-portal/acceptance-dashboard.png) |

| Trainset assembly | Simulation | Fabrication and civil sequence |
|---|---|---|
| ![LM3 full body and bogie assembly](docs/screenshots/freecad/blender-full-body-assembly.png) | ![OpenSourceRail simulator](docs/screenshots/sim-gui.png) | ![Fabrication and assembly digital twin](docs/assets/digital-twin-animation.gif) |

## Find Your Way

This README is the repository's only human-facing front door. Use this table
instead of browsing the folder tree or the generated file inventory.

| I want to… | Go here |
|---|---|
| Understand the whole system | [Architecture](docs/ARCHITECTURE.md) and [software diagrams](docs/software-architecture-diagrams.md) |
| Design a city, line, station or service | [Workbench](docs/workbench/README.md) and [City Studio](docs/city-studio.md) |
| Explore a country or city | [City catalogue](designs/README.md); each local page contains only local evidence |
| Review costs or the portfolio | [Cost model](docs/cost-model.md) and [developing-world portfolio](docs/portfolio-summary.md) |
| Review trains, civil works or stations | [LM3 trainset](docs/rolling-stock/light-metro-3car/README.md), [civil](docs/civil/README.md) and [stations](docs/stations/README.md) |
| Review software, hardware or operations | [Simulation coverage](docs/simulation-software-coverage.md), [hardware](hardware/README.md) and [operations](docs/operations/README.md) |
| Review safety, certification or open gaps | [Certification](docs/certification/README.md), [safety case](docs/safety-case/README.md) and [roadmap](docs/ROADMAP.md) |
| Contribute or make a release | [Contributing](CONTRIBUTING.md) and [release checklist](docs/releases.md) |
| Share a short non-technical summary | [Generated one-page overview](docs/open-source-rail-overview.html) |
| Read the complete documentation | [Complete PDF book](OpenSourceRail-Book.pdf); rebuild it with `./scripts/osr book` |

## Run The Platform

### One-command Linux setup

On Debian, Ubuntu, Mint, Fedora, RHEL, Rocky, AlmaLinux, CentOS, openSUSE or
Arch Linux, install the entire platform with one command:

```bash
./install.sh
```

It first reports what is already installed. Declining the installation makes
no changes; accepting installs only missing native libraries and keeps Rust,
Node.js, Python, uv, Trunk and browser tools under your home folder. It then
asks whether to add the larger FreeCAD, Blender/Bonsai, QGIS, CloudCompare and
SUMO applications, and whether to start the GUI. There are no setup options or
environment variables to configure.

After setup, one command regenerates the shared design and cost data, product
catalogues, browser and native applications, BOMs, IFC4.3 reference packages,
the root PDF book, and documentation checks:

```bash
./scripts/osr build
```

It uses the checked-in city models and therefore does not silently reroute all
265 public city plans from changing internet data. Route changes are made in
City Studio or regenerated explicitly with their source locks.

Run the integrated Workbench:

```bash
./scripts/osr
```

Open <http://127.0.0.1:8090/>. The local development server is not an
authenticated public deployment.

Run the deterministic simulator:

```bash
./scripts/osr sim --duration 3600 --status-every 300
```

The generated applications are under `build/frontend/`, native executables are
under `target/release/`, engineering/BIM/BOM outputs are under `build/`, and
the reader book is [OpenSourceRail-Book.pdf](OpenSourceRail-Book.pdf). The
tracked FreeCAD review assemblies are in
[`mechanical-py/catalog/freecad/`](mechanical-py/catalog/freecad/).

## What The Repository Contains

| Area | Inspectable result | Status boundary |
|---|---|---|
| City portfolio | 265 developing-world models with routes, stations, fleets, GIS layers, energy, costs and local evidence | Deterministic planning models; local survey and demand calibration remain required |
| City Studio | Layered GIS editing, route/station tools, service-by-line/day/hour controls, revision comparison and engineering jobs | Local planning workspace, not an approved design-authoring or live-control system |
| Civil and stations | Parametric component catalogue, OSR-ALN, IFC4.3 federation, IDS/BCF checks, quantities and 4D review | IFC/Bonsai coordinates information; released structural calculations and drawings remain external gates |
| Rolling stock | LM3 product tree, CAD review assemblies, BOM, mechanical fixtures, embedded roles and simulation adapters | Design-reference package, not homologated manufacturing data |
| Operations | OCC training, Ops Core, manufacturing/QA/maintenance records and safety evidence links | Training and assurance workflow; no live railway command authority |

## Evidence And Revision Model

```text
city/project sources
        ↓
validated candidate + source locks
        ↓
immutable Git-reviewable revision
        ↓
GIS / OSR-ALN / IFC / CAD / cost / simulation artifacts
        ↓
approval evidence → training/operations baseline
```

Planning and training views cannot emit live OCC commands. A revision hash is
not an approval; approval records are append-only and must reference independent
review evidence. Generated city packages still require survey, calibrated
demand, utility and ground data, supplier selection, first-article testing,
competent engineering review and national authorization.

## Source Of Truth

Change the source in the middle column and regenerate the output on the right.
Generated files are review evidence, not parallel inputs.

| Concern | Edit here | Derived or explanatory material |
|---|---|---|
| System boundaries and decisions | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and accepted [`docs/rfcs/`](docs/rfcs/README.md) | Diagrams, guides and component summaries |
| Software and simulation behaviour | [`crates/`](crates/README.md) plus their tests | WASM applications, simulation traces and coverage reports |
| Shared planning assumptions | [`lib/templates/`](lib/templates/) and [`lib/recipes/`](lib/recipes/) | City designs, finance, energy and engineering evidence |
| City catalogue membership | [`lib/city-batches/world-sample.toml`](lib/city-batches/world-sample.toml) | [`designs/`](designs/README.md) catalogue and national briefs |
| Interactive city revisions | [`projects/`](projects/README.md) | Content-addressed candidates and exported city packages |
| Mechanical, station and reusable civil-component geometry | [`mechanical-py/src/osr_mech/`](mechanical-py/src/osr_mech/) | FreeCAD review assemblies, BOMs, travelers and screenshots |
| Survey, GIS and railway alignment | Accepted deployment GIS plus OSR-ALN project sources | QGIS layers, GeoPackages, corridor exports and IFC alignment references |
| Federated civil BIM | Parametric component geometry plus approved alignment and engineering inputs | IFC4.3 generated by [`civil_bonsai_ifc.py`](engineering/interchange/civil_bonsai_ifc.py), checked with IfcOpenShell and reviewed in Bonsai |
| Civil rates and city costs | [`lib/templates/civil-cost-calibration.toml`](lib/templates/civil-cost-calibration.toml), geometry and reviewed assumptions | Generated rate contract, [cost model](docs/cost-model.md) and city CAPEX |
| Hardware integration | [`hardware/`](hardware/README.md) and governing RFCs | BOMs, wiring packs and release evidence |
| Operations and safety requirements | [`docs/operations/`](docs/operations/README.md), [`docs/certification/`](docs/certification/README.md) and [`formal/`](formal/README.md) | Portal data, safety-case views and acceptance reports |

The [artifact policy](docs/repository-artifact-policy.md) defines what Git keeps.
The generated [Markdown inventory](docs/INDEX.md) is for search and CI only; it
does not define architecture, status or reading order.

## Verification

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --all-targets
PYTHONPATH=mechanical-py/src pytest mechanical-py/tests -q
pytest design-py/tests -q
npm run test:frontend
python3 scripts/repo-health.py --quiet
python3 scripts/check-markdown-links.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md),
[CHANGELOG.md](CHANGELOG.md) and the [release checklist](docs/releases.md).

## License

- Software: Apache 2.0
- Hardware designs: CERN-OHL-S v2
- Documentation: CC-BY-SA 4.0

See [LICENSE.md](LICENSE.md) and [LICENSES/](LICENSES/README.md) for the path
mapping and complete texts.

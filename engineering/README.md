# OpenSourceRail engineering

<!-- osr-system-context:start -->
OpenSourceRail develops affordable rail that local companies can build, maintain and improve. The published digital release joins a costed vehicle, civil works, controls, production plan and Workbench journey; Baghdad has separate elevated city planning alternatives. The earlier v0.6 passive-wheel, station-launch design remains research, not the installed drive selection for the v0.7 reference or Baghdad. Each candidate retains its own geometry, mass, service, power, cost and evidence. Safety and accessibility remain requirements. Digital results do not grant fabrication or passenger-operation approval.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

## Selected digital design and retained research

The [v0.7 digital reference](../docs/reference-v07/README.md) joins one powered-wheel train, civil design, controls, cost and production plan. [Baghdad](../cities/Baghdad/README.md) has separate city-specific planning candidates. Their installed quantities and assumptions are in the [engineering status](../docs/ENGINEERING-STATUS.md).

[development-baseline.toml](development-baseline.toml) retains the v0.6 passive-wheel, station-launch research reference. [station_rail/](station_rail/README.md) owns its physical definition, counted vehicle, service energy, civil alternatives, motion requirements and candidate delivery records. [development_baseline/](development_baseline/README.md) supplies the CLI, planning handoff and Workbench adapters. The table below describes that retained research system.

| Responsibility | Current owner and boundary |
|---|---|
| Vehicle and wheel support | `station_rail/vehicle.py`: passive bogies, body load paths, fitout and accounted mass; complete installation, stiffness and wheel dynamics remain unqualified |
| Station drive and services | `station_rail/operations.py`, `electrical.py`, `native_drive.py`: required force, finite zones, service SOC and conditional field/heat bounds; available motor map remains unknown |
| Conventional civil works | `station_rail/civil.py`: box, twin-beam and U-beam alternatives, moving axle envelopes, tendons and construction quantities; complete site and lateral/torsional design remain open |
| Controls | Rust ATP, interlocking, OCC, TCMS, doors and SCADA with candidate-bound wheel/station interfaces; physical braking, sensing and fault evidence remain open |
| Digital twin and delivery | Candidate-bound CAD/IFC, engineering BOM, manufacturing, procurement, assembly and controls exports; incomplete equipment, costs and release evidence remain explicit |
| City planning | 266 geographic inputs and editable route/service proposals; v0.6 performance regeneration is held pending physical and economic evidence |

Coordinated research starts with `./osr design railway` and the [coupled experiment](../docs/design-engine/coupled-railway/README.md). It binds architecture, adaptive diagnosis and generated bodies to the same inventory, propulsion, braking, civil and manufacturing evaluations. Native structural and transient adapters declare their own validity domains; unknown installed mass and prices prevent whole-system selection.

The [sourcing and cost engine](sourcing/README.md) connects dated supplier, material, commodity, FX and civil-price evidence to exact candidate requirement groups. RFQs are disabled drafts; no price source establishes component approval or an installed railway cost.

The [adaptive variables](../docs/design-engine/v06-adaptive-design/README.md) and [structural grammar](../docs/design-engine/generative-structure/README.md) support physical revisions across materials, load paths and assemblies. Composite qualification, joints, buckling, complete installed geometry and physically driven journeys require their own evidence.

The opt-in [SolidCraft / FieldCraft backend pilot](../docs/design-engine/craft-backends/README.md) compares source-bound CAD subsets and mechanical controls against FreeCAD and CalculiX. It retains the existing BIM, electromagnetic and delivery routes. Run `./osr design backends plan` to inspect its scope. The [12-span viaduct comparison](../docs/design-engine/viaduct-backends/README.md) extends this path to reusable CAD/analysis/delivery interfaces, exact STEP readbacks, two matched solid-FEM studies and candidate-specific manufacturing/cost records.

The [vehicle parts and assembly catalogue](../docs/design-engine/vehicle-parts/README.md) develops a separate six-car detail proposal into 605 named leaf types in 40 assemblies, with material and stock schedules, counted fixings, fabrication, inspection and removal methods, and scoped estimates. Use `./osr design parts plan` or open **Vehicle parts** in the Workbench.

## Run the current workflow

[Native city GIS](../docs/gis/README.md) exports the exact selected city geometry,
offline backgrounds, service and cost tables to pinned RustGIS projects. Use
`./osr gis open --city baghdad` or the city atlas download link. Current mapping
does not require QGIS; historical project metadata remains readable.

```bash
./osr status
./osr build
./osr verify
./osr workbench
./osr plan --help
./osr twin export
```

All engineering, manufacturing and operating release flags remain false. See the [current dossier](../docs/design-engine/current/README.md) and [project roadmap](../docs/ROADMAP.md) for evidence and open tasks.

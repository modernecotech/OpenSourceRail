# OpenSourceRail architecture

OpenSourceRail develops simple, affordable, locally maintainable urban transport. The repository default is a comfort-first six-car train with onboard neodymium Halbach permanent magnets and active suspension/guidance controls. Ordinary guideway consists of concrete beams with passive steel facings. Finite station winding groups provide propulsion and controlled arrival; passenger transfers connect fixed lines.

## Authoritative design

[development-baseline.toml](../engineering/development-baseline.toml) selects the exact body, magnet and retained-stop network proposal. The [current dossier](design-engine/current/README.md), [all-city index](design-engine/current/cities.json), [delivery exports](design-engine/current/exports/manifest.json), [Workbench](workbench/current/index.html) and [reader](../OpenSourceRail-Book.pdf) resolve to that same selection.

Six 17 m cars carry 44 fixed seats plus two wheelchair places/car, with zero planned standing and two doors on one side. An aluminium extrusion frame, retained GFRP sides, lightweight sandwich floor/roof and benches form the counted body proposal. Laminated glass is retained; plastic glazing and EPM load trimming remain alternatives requiring evidence.

The target is 120-second headway, 276 normal passengers/train and 8,280 passengers/hour/direction. The retained-stop network proposal uses a 72 km/h launch cap and 35-second dwell. Existing route geometry is retained; longer finite station winding options are selected explicitly for each leg. Admission control, one-sided platforms, accessibility and evacuation must match the seating policy.

## Current component contracts

| Domain | Current relationship and remaining boundary |
|---|---|
| Vehicle | Counted material, supplier references and unlocated allocations; 17.357 t accounted tare and 20.807 t capped load/car. Complete installed stock, CG/inertia and joined structural modes unknown. |
| Suspension | Onboard PMs/active controls against passive steel facings. Installed 3D force/current/temperature maps, operating gap, stability and reserve remain unqualified. |
| Station drive | Selected 2 km prototype shares 800 m winding between launch and receipt, 12.5 m addresses, at least two concurrent train phase/current branches/direction. Actual switchgear, force, voltage and thermal duty remain open. |
| Civil | New 2.26 m-facing envelope and counted supports; conservative prototype quantities. Rebar/prestress, anchors, moving loads, bearings, piers, foundations and site evidence remain open. |
| Operations | Actual coast/brake leg requirements, resource screens and fleet are recalculated for every city. Rust protocol fixtures use synthetic healthy gaps and assumed braking; safe physical headway unknown. |
| Delivery | Same-candidate engineering BOM, manufacturing, procurement, assembly, controls and partial IFC. Supplier prices, labour, dates, crews and releases unknown. |
| Qualification | Execution, numerical validity, engineering screen and physical acceptance remain separate. Development selection grants no manufacturing or motion authority. |

## Software and evidence

`engineering/development_baseline/` authenticates the immutable physical packet and regenerates current service, cities and delivery records. `./osr`, infrastructure/design aliases, status, build, verify, reader and Workbench all use this selection. Unsupported physical adapters return a hold. Native car CAD/STEP is reverified from its portable archive; new Rust controls execute the actual selected analytical profile. Neither establishes stable hover or an end-to-end physical journey.

The two current failed necessary screens are capture energy and unshaded hot-roof-core temperature. Remaining physical gates are unknown. A physical-force journey must start from demonstrated hover and use the same vehicle structure, mass, current, electrical, thermal and braking maps.

Historical ferrite calculations, prior city quantities, deployment references and reader remain [pinned evidence](archives/pre-comfort-default/README.md). Their configuration and costs do not transfer silently to the new default. Regenerate historical pipelines only in an isolated checkout.

```bash
./osr status
./osr build
./osr verify
./osr workbench
./osr legacy verify
```

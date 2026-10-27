# OpenSourceRail engineering

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Maglev documents below are retained historical research, not the selected v0.6 physical design.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

## Current ownership

[development-baseline.toml](development-baseline.toml) selects the v0.6 wheel/LIM research candidate. [station_rail/](station_rail/README.md) owns its physical definition, counted vehicle, service energy, conventional civil alternatives, reference motion and delivery records. [development_baseline/](development_baseline/README.md) supplies CLI and Workbench adapters. Lower whole-life cost and physical operation remain open.

| Responsibility | Owner and boundary |
|---|---|
| Vehicle and wheel support | `station_rail/vehicle.py`: passive bogies, revised load paths, fitout and accounted mass; complete installation, stiffness and wheel dynamics unqualified |
| Station drive and services | `station_rail/operations.py`, `electrical.py`, `native_drive.py`: required force, finite zones, service SOC and conditional field/heat bounds; actual motor map unknown |
| Conventional civil works | `station_rail/civil.py`: box, twin-beam and U-beam alternatives, moving axle envelopes, tendons and construction quantities; complete site and lateral/torsional design open |
| Controls | Existing Rust ATP/interlocking/OCC/TCMS/doors/SCADA; new wheel-station interfaces require physical braking, sensing and fault evidence |
| Comparison and delivery | Candidate-bound research exports and same-service comparison; missing equipment, prices, process qualification and releases remain explicit |
| Geographic inputs | 266 city maps and route contexts retained; numerical city regeneration held pending reference physical and economic evidence |

The [v0.5 maglev archive](../docs/archives/v0.5-maglev/README.md) preserves the former selected design and its scientific results. `comfort_design/`, `suspension_closure/`, `magnetic_confirmation/`, `halbach_scaling/`, `thermal_closure/` and existing magnetic `trip_dynamics/` packets remain historical methods. Their accepted inputs, costs and simulation assumptions cannot silently become v0.6 evidence.

Function-first research uses [adaptive variables and continued search](../docs/design-engine/v06-adaptive-design/README.md) and the [executed structural grammar](../docs/design-engine/generative-structure/README.md). `design_search/design_grammar.py` composes stock/material/load-path/assembly productions; typed interfaces, failure diagnosis, physical rewrites, source-bound native axial checks and CAD export share candidate identities. These research adapters do not replace the selected vehicle or supply missing full-body, joint, buckling, installed-mass or journey evidence.

## Historical research configuration - not the selected development baseline

The [ferrite reference package](ferrite_maglev/README.md) owns the requirements, configuration, structural studies and generated evidence of its historical revision. Its old masses, fleet and financial sensitivities are not current quantities. [Station](ferrite_maglev/station.py), [structure/production](ferrite_maglev/station_structure.py) and [fourteen-case dynamics](../docs/design-engine/ferrite-maglev/full-dynamics/README.md) remain identified research records.

Historical source and payload identity is preserved by the [pinned archive](../docs/archives/pre-comfort-default/README.md). The [documentation index](../docs/INDEX.md) is navigation; the selector and source-bound engineering records establish the design state.

```bash
./osr status
./osr verify
./osr workbench
./osr legacy verify
```

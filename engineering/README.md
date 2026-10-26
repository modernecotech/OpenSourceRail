# OpenSourceRail engineering

<!-- osr-system-context:start -->
OpenSourceRail develops simple, affordable, locally maintainable urban transport. The development default is six 17 m comfort cars, each with 44 seats plus two wheelchair places and no planned standing; the 120-second service target gives 8,280 normal passengers/hour/direction. All permanent magnets and suspension controls remain onboard; concrete beams carry passive steel facings, while station windings provide launch and receiving power. Lightweight assemblies, repeated civil works and repairable local production support the low-cost ethos. Stable physical operation and manufacturing release remain open.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

## Current ownership

[development-baseline.toml](development-baseline.toml) selects the current six-car comfort/NdFeB development candidate. [development_baseline/](development_baseline/README.md) resolves that selection and publishes its matched service, city and delivery records. It does not qualify the physical railway or demonstrate economic superiority.

The [physical-feasibility follow-up](../docs/design-engine/physical-feasibility-round/README.md) is the current P0 investigation: coupled guideway/material quantities, suspension force/current limitations, passive capture and roof alternatives, and equal-service comparisons. Its proposed parts remain research alternatives; the selected default and its failed/unknown physical gates stay explicit.

| Responsibility | Owner and boundary |
|---|---|
| Candidate registry and comparison | [design_search/](design_search/README.md); equal-service quantities and Pareto alternatives, never zero-valued unknown costs |
| Installed vehicle | `equipped_vehicle/`, selected `comfort_design/` assembly and retained native CAD; incomplete installed stock/CG/inertia remain unknown |
| Suspension | `suspension_closure/`, `magnetic_confirmation/`, `halbach_scaling/`; component field/current investigations with numerical validity limits |
| Roof, HVAC and capture bounds | `thermal_closure/`; counted proposed stock and analytical/thermal/impact cases, not qualified safety hardware |
| Coupled motion | [trip_dynamics/](trip_dynamics/README.md); physically matched inputs are required before a supported journey can execute |
| Qualification and delivery | `assurance/`, current candidate-bound exports and authenticated measurements; manufacturing/operating releases remain held |

The global default is a starting candidate for city-specific design. Demand, grades, climate, stations, access, foundations, suppliers and economics need local evidence. Applying one configuration to a city catalogue is not proof of suitability.

## Historical research configuration - not the selected development baseline

The [ferrite reference package](ferrite_maglev/README.md) owns the requirements, configuration, structural studies and generated evidence of its historical revision. Its old masses, fleet and financial sensitivities are not current quantities. [Station](ferrite_maglev/station.py), [structure/production](ferrite_maglev/station_structure.py) and [fourteen-case dynamics](../docs/design-engine/ferrite-maglev/full-dynamics/README.md) remain identified research records.

Historical source and payload identity is preserved by the [pinned archive](../docs/archives/pre-comfort-default/README.md). The [documentation index](../docs/INDEX.md) is navigation; the selector and source-bound engineering records establish the design state.

```bash
./osr status
./osr verify
./osr workbench
./osr legacy verify
```

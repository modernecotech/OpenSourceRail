# Rubavu — comfort-first OpenSourceRail development design

OpenSourceRail seeks simple, affordable, locally maintainable transport: repeated lightweight trains, concrete beams with passive steel facings, onboard permanent magnets and suspension controls, and powered launch/receiving zones at stations. The current development default gives passengers four-abreast seating and a controlled low standing load. Transfers connect fixed lines.

**Selected for development; physical operation is not yet established.** This city uses the same six-car comfort candidate as the system default. Existing geographic corridors and stops are retained.

![Retained city geography and network context](../maglev/network.svg)

The retained map preserves its underlying city detail. Its older engineering annotations are historical; the current vehicle and service calculations below supersede those annotations. Route and station sites remain proposals.


| Current development basis | Result |
|---|---:|
| Formation | 6 × 17 m cars |
| Per-car accommodation | 44 seats + 2 wheelchair places; no planned standing |
| Passenger doors | Two doors on one side per car |
| Accounted tare / cap-loaded material mass per car | 17.357 / 20.807 t |
| Complete installed mass, CG and inertia | Unknown |
| Launch-speed cap / target headway / dwell | 72 km/h / 120 s / 35 s |
| Arithmetic normal capacity | 8,280 passengers/hour/direction |
| Retained 14,400 pphpd comparison | Not met by this comfort capacity |
| Lines / retained route / proposed stops | 4 / 46.9 km / 28 |
| Peak active + spare + cold reserve trainsets | 93 + 13 + 4 |
| Total trainsets / cars | 110 / 660 |
| Additional stops imposed by this default | 0 |
| Counted mainline station winding, directional | 41.2 km |
| Mainline powered coverage / overlapping intervals | 39.3% / 0 |

Fleet is recalculated from each actual coast/brake leg, retained terminal-time hypotheses, 35-second dwell, a 120-second target interval, 12% rounded-up spares and one cold reserve per line. Every reachable arrival selects the shortest full-engagement option from 350/450/600/800/900/1,000 m. These motors occupy substantial route length; each direction needs at least two independently routed train phase/current branches. Terminal motors and safe operational headway remain unqualified.

Analytical result: **conditional-analytical-survivor**; 0 lines have unreachable coasting legs and 0 lines have station-library failures. Failed cases stay in the data; their complete fleet/quantity totals remain unknown.

The selected prototype civil interface counts **865.1 tonnes of steel per directional kilometre**, before unclosed reinforcement, prestress, end blocks, bearings, piers and foundations. This heavy extrapolation is a redesign input, not an optimised viaduct or an installed bill. All current CAPEX, OPEX, debt service, imported-content and price-coverage totals remain unknown pending matched designs and quotations.

Stable multiaxis hover, a complete equipped vehicle, actual station thrust/electrical/thermal limits, fault stopping, civil acceptance and safe two-minute operation remain open. The mass ledger, energy requirements, winding layout, source hashes and failures are retained in the machine-readable record.

[Primary planning method](../../../../../../../docs/design-engine/current/README.md) · [Current calculation and source identities](summary.json) · [Historical ferrite planning package](../maglev/README.md) · [Historical city front page at the pinned source](https://github.com/modernecotech/OpenSourceRail/blob/578ee3950b872bf30fbf9e4207b2bda85951bdd7/cities/catalogue/east-africa/Rwanda/Rubavu/README.md)

Candidate `957f7e4e2e0e98b575810fb0c568554968fc1eb0715fb673827a16bcf63d400b`  
Body `1eca1897b983bf62ec315cdc39aca2e2387f93ad6ab0c195bc278e14c8fb120b`  
Magnet `397ddf033ab98afaea053acaa3047249a3329f542f1f5e52a6eb1b466b9662e0`  
Selection `c76af04990ab43d9644b884eb1a7d103851aa53fcc963505bdb0b7580ae74e77`  
Evaluation `bdc12b45370cf97a7238091a3e1b5dc02eca4cb9dd88adb4c16ad5a45e352ce9`

| Line | Fleet | Circuit minutes | Directional winding km | Coast failures |
|---|---:|---:|---:|---:|
| line-1 | 26 | 43.9 | 10.6 | 0 |
| line-2 | 34 | 56.1 | 11.2 | 0 |
| line-3 | 31 | 50.8 | 12.2 | 0 |
| line-4 | 19 | 31.7 | 7.2 | 0 |

Hotel-energy coefficient: **558 kWh per peak operating hour per actual kW/car**. Actual auxiliary load, conversion efficiency, terminal energy and complete operating energy remain unknown.

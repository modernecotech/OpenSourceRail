# Civil Marketplace Cost Anchors

Planning-grade OSR city costs now use **USD marketplace/direct-procurement
floors** as the source currency. Generated `design.toml` files still keep
`*_eur` mirrors at 0.92 USD->EUR for schema compatibility.

These are not turnkey EPC bid prices. They are component-priced floors for
direct procurement, local fabrication, self-performed assembly, repeatable
QA, and the no-tunnel/no-catenary OSR civil discipline.

## At-Grade Double Track

Base unit: **850,000 USD per route-km**.

| Component | Marketplace anchor | Planning basis |
|---|---:|---|
| UIC60/60E1 rail | Alibaba UIC60 rail listings show about **600-700 USD/t** for 60E1/UIC60 rail: <https://www.alibaba.com/showroom/railway-rail-uic60.html> | Double track uses ~241 t/km of rail, so rail steel lands near 145-170 k USD/km before freight |
| Concrete sleepers | Alibaba concrete-sleeper listings show **15-55 USD/sleeper** common ranges: <https://www.alibaba.com/showroom/concrete-sleeper-price.html> | ~3,300 sleepers/km for double track gives ~50-180 k USD/km |
| Clips, baseplates, pads | Alibaba rail-fastening listings show clips around **0.5-2.5 USD** and assemblies/baseplates around **4-6 USD**: <https://www.alibaba.com/showroom/rail-fastening-system.html> | Double-track fastening hardware, pads, fishplates, weld kits, and small parts budgeted as a bundled allowance |
| Ballast, drainage, cable trough, installation | Local quarry/supplier item rather than rail-specific Alibaba commodity | Residual allowance plus local labour/equipment brings the installed direct-procurement floor to **850 k USD/km** |

## Elevated Guideway And Bridges

| Civil class | Unit | Marketplace anchors | Included scope |
|---|---:|---|---|
| Elevated viaduct | **4.0 M USD/km** | Prefab bridge steel/trestle listings around **820-1,280 USD/t** and **990-1,200 USD/t**: <https://www.alibaba.com/showroom/prefab-bridges.html>, <https://www.alibaba.com/showroom/prefabricated-steel-trestle.html>; precast/box-girder formwork and bridge products: <https://www.alibaba.com/showroom/precast-concrete-beams-bridge.html> | Repeatable precast U-girders, piers, pile caps, bearings, parapets, trackform, local launching/erection crew |
| Bridge / water crossing | **6.0 M USD/km** | Same bridge/trestle anchors plus pile/foundation equipment examples: <https://www.alibaba.com/showroom/reinforced-concrete-pile.html> | Longer spans, harder foundations, flood/scour detailing, and bridge-specific protection |
| Elevated interchange premium | **2.0 M USD/site** | Uses the elevated guideway component stack above | Added stacked platform/approach complexity where an at-grade crossing is forced to grade-separate |

## Stations

Station costs assume prefab portal-frame canopies, precast platform edges,
commodity lifts/escalators where required, simple MEP, lighting, signs,
fare gates, CCTV, and local assembly. No underground concourse, no bespoke
architectural cladding, no continuous traction-power plant.

| Archetype | Unit |
|---|---:|
| `halt` | 120 k USD |
| `standard` | 300 k USD |
| `major` | 600 k USD |
| `terminal` | 500 k USD |
| `depot-terminal` | 650 k USD |
| `interchange` | 900 k USD |
| `interchange-elevated` | 1.2 M USD |

Marketplace anchors:

- Prefab steel canopy / portal-frame buildings: Alibaba steel-canopy and
  prefab steel-structure listings show common ranges around **15-65
  USD/m2** for simple steel structures: <https://www.alibaba.com/showroom/steel-canopy-structures.html>
- Escalators: Alibaba escalator listings show common public/commercial
  units in the **9,000-30,000 USD** band, with some lower small-unit
  entries: <https://www.alibaba.com/showroom/escalator.html>
- Lifts/elevators: Alibaba outdoor/passenger lift listings show small
  lift entries from roughly **1,300-4,000 USD** and broader commercial
  elevator bands above that: <https://www.alibaba.com/showroom/elevator-outdoor.html>

## Depots And Charging Interfaces

Depot costs were also brought onto the same direct-procurement floor because
the station/track recalculation otherwise left the fixed-asset stack mixed.

| Depot archetype | Unit |
|---|---:|
| `main-heavy` | 7.5 M USD |
| `secondary-medium` | 4.0 M USD |
| `layup-minimal` | 900 k USD |

Station/depot charging microgrid interface:

| Stop archetype | Unit |
|---|---:|
| `halt` | 75 k USD |
| `standard` | 150 k USD |
| `major` / `terminal` | 250 k USD |
| `interchange` / `interchange-elevated` | 350 k USD |
| `depot-terminal` | 450 k USD |

This bucket is only conductive chargers, switchgear, short cable runs,
inverter interface, and local microgrid tie-in. PV panels, stationary
storage, train batteries, and onboard charge hardware are counted elsewhere.

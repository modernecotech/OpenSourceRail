# Civil Marketplace Cost Anchors

Planning-grade OSR city costs now use **USD marketplace/direct-procurement
floors** as the source currency. Generated `design.toml` files still keep
`*_eur` mirrors at 0.92 USD->EUR for schema compatibility.
The canonical machine-readable rates live in
[`lib/templates/capex-costs.toml`](../../lib/templates/capex-costs.toml);
this note is the civil-work audit trail.

These are not turnkey EPC bid prices. They are component-priced floors for
direct procurement, local fabrication, self-performed assembly, repeatable
QA, and the no-tunnel/no-catenary OSR civil discipline.

## At-Grade Double Track

Base unit: **3,000,000 USD per route-km**.

| Component | Marketplace anchor | Planning basis |
|---|---:|---|
| UIC60/60E1 rail | Alibaba UIC60 rail listings show about **600-700 USD/t** for 60E1/UIC60 rail: <https://www.alibaba.com/showroom/railway-rail-uic60.html> | Double track uses ~241 t/km of rail, so rail steel lands near 145-170 k USD/km before freight |
| Slab/plinth concrete and reinforcement | Local concrete, rebar, mesh, formwork, and precast suppliers rather than a rail-specific commodity | Ballastless urban track shifts spend from sleepers/ballast/tamping into slab, plinth, embedment, and drainage works |
| Direct-fixation fasteners, baseplates, pads | Alibaba rail-fastening listings show clips around **0.5-2.5 USD** and assemblies/baseplates around **4-6 USD**: <https://www.alibaba.com/showroom/rail-fastening-system.html> | Double-track fastening hardware, pads, baseplates, weld kits, and small parts budgeted as a bundled allowance |
| Ballastless slab/embedded trackform, drainage, cable trough, installation | Local concrete/rebar/precast and civil supplier item rather than rail-specific Alibaba commodity | Residual allowance plus local labour/equipment, freight, QA, welding, direct-fixation installation, drainage, and urban possession logistics brings the installed planning floor to **3.0 M USD/km** |

## Elevated Guideway And Bridges

| Civil class | Unit | Marketplace anchors | Included scope |
|---|---:|---|---|
| Elevated viaduct | **12.0 M USD/km** | Prefab bridge steel/trestle listings around **820-1,280 USD/t** and **990-1,200 USD/t**: <https://www.alibaba.com/showroom/prefab-bridges.html>, <https://www.alibaba.com/showroom/prefabricated-steel-trestle.html>; precast/box-girder formwork and bridge products: <https://www.alibaba.com/showroom/precast-concrete-beams-bridge.html> | Repeatable precast U-girders, piers, pile caps, bearings, parapets, deck slab/trackform, local launching/erection crew, plus transport, QA, foundation, and commissioning allowance |
| Bridge / water crossing | **18.0 M USD/km** | Same bridge/trestle anchors plus pile/foundation equipment examples: <https://www.alibaba.com/showroom/reinforced-concrete-pile.html> | Longer spans, harder foundations, flood/scour detailing, bridge-specific protection, water-working contingency, and inspection access |
| Elevated interchange premium | **4.5 M USD/site** | Uses the elevated guideway component stack above | Added stacked platform/approach complexity where an at-grade crossing is forced to grade-separate |

## Stations

Station costs assume prefab portal-frame canopies, ground-level
platform slabs with lowered guideway channels, direct pedestrian
access, simple MEP, lighting, signs, fare gates, CCTV, and local
assembly. Commodity lifts/escalators and overbridges appear only where
an elevated/stacked interchange or local road-barrier override requires
them. No underground concourse, no bespoke architectural cladding, no
continuous traction-power plant.

| Archetype | Unit |
|---|---:|
| `halt` | 600 k USD |
| `standard` | 2.5 M USD |
| `major` | 4.5 M USD |
| `terminal` | 4.5 M USD |
| `depot-terminal` | 5.0 M USD |
| `interchange` | 8.0 M USD |
| `interchange-elevated` | 12.0 M USD |

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
- Footbridges: station foot-overbridge examples range from sub-1 M USD
  low-cost-market steel packages to multi-million USD rail overbridges
  once access cores, possessions, utilities, and crowd-flow width are
  included. Examples include a 12 m wide Guindy station FOB reported at
  about Rs 6.5 crore
  (<https://www.newindianexpress.com/cities/chennai/2023/mar/14/new-foot-overbridge-at-guindy-railway-station-to-ease-passenger-flow-2555815.html>)
  and UK station-footbridge commentary noting costs above GBP 4 M each
  (<https://www.ingenia.org.uk/articles/the-flat-pack-footbridge-for-train-stations/>).
  OSR uses a modular low-cost floor but no longer treats the access
  bridge as free.

## Depots And Charging Interfaces

Depot costs were also brought onto the same direct-procurement floor because
the station/track recalculation otherwise left the fixed-asset stack mixed.

| Depot archetype | Unit |
|---|---:|
| `main-heavy` | 12.0 M USD |
| `secondary-medium` | 7.0 M USD |
| `layup-minimal` | 2.0 M USD |

Station/depot charging microgrid interface:

| Stop archetype | Unit |
|---|---:|
| `halt` | 120 k USD |
| `standard` | 250 k USD |
| `major` | 450 k USD |
| `terminal` | 500 k USD |
| `interchange` | 700 k USD |
| `interchange-elevated` | 850 k USD |
| `depot-terminal` | 1.0 M USD |

This bucket is only conductive chargers, switchgear, short cable runs,
inverter interface, and local microgrid tie-in. PV panels, stationary
storage, train batteries, and onboard charge hardware are counted elsewhere.

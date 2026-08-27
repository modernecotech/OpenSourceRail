# Civil Marketplace Cost Anchors

Planning-grade OSR city costs use USD as the source currency. Generated
`design.toml` files keep `*_eur` mirrors at 0.92 USD->EUR for schema
compatibility. The reviewed civil benchmarks and cost-share assumptions live
in [`civil-cost-calibration.toml`](../../lib/templates/civil-cost-calibration.toml);
the active CAD-indexed rates are generated in
[`civil-cost-model.toml`](../../lib/templates/civil-cost-model.toml). General
CAPEX units remain in
[`capex-costs.toml`](../../lib/templates/capex-costs.toml). This note is the
civil marketplace audit trail.

These are not turnkey EPC bid prices. The benchmarks and generated targets
assume direct procurement, local fabrication, self-performed assembly,
repeatable QA, and the no-tunnel/no-catenary OSR civil discipline.

## At-Grade Double Track

Active design target: **2,584,000 USD per route-km**. Retained marketplace
benchmark: **3,000,000 USD per route-km**.

| Component | Marketplace anchor | Planning basis |
|---|---:|---|
| UIC60/60E1 rail | Alibaba UIC60 rail listings show about **600-700 USD/t** for 60E1/UIC60 rail: <https://www.alibaba.com/showroom/railway-rail-uic60.html> | Double track uses ~241 t/km of rail, so rail steel lands near 145-170 k USD/km before freight |
| Slab/plinth concrete and reinforcement | Local concrete, rebar, mesh, formwork, and precast suppliers rather than a rail-specific commodity | Ballastless urban track shifts spend from sleepers/ballast/tamping into slab, plinth, embedment, and drainage works |
| Direct-fixation fasteners, baseplates, pads | Alibaba rail-fastening listings show clips around **0.5-2.5 USD** and assemblies/baseplates around **4-6 USD**: <https://www.alibaba.com/showroom/rail-fastening-system.html> | Double-track fastening hardware, pads, baseplates, weld kits, and small parts budgeted as a bundled allowance |
| Ballastless slab/embedded trackform, drainage, cable trough, installation | Local concrete/rebar/precast and civil supplier item rather than rail-specific Alibaba commodity | Residual allowance plus local labour/equipment, freight, QA, welding, direct-fixation installation, drainage, and urban possession logistics formed the retained **3.0 M USD/km benchmark**; current slipform/CAD quantities index it to **2.584 M USD/km** |

## Elevated Guideway And Bridges

| Civil class | Design target | Retained benchmark | Marketplace anchors and included scope |
|---|---:|---:|---|
| Elevated viaduct | **9.748 M USD/km** | **12.0 M USD/km** | Broad listings remain early procurement anchors; [`viaduct-quantity-cost-model.toml`](viaduct-quantity-cost-model.toml) records 40 Pi25 bays, 80 beams, 30 link slabs, ten deck gaps, 200 bearings/km, trackform, walkways, zone foundations, yard, transport, erection, utilities, traffic management, checking, testing and contingency |
| Bridge / water crossing | **18.0 M USD/km** | **18.0 M USD/km** | Bridge/trestle anchors plus pile/foundation equipment examples: <https://www.alibaba.com/showroom/reinforced-concrete-pile.html>; bridge-specific redesign and foundation schedules remain outstanding |
| Elevated interchange premium | **4.5 M USD/site** | — | Uses the elevated guideway stack plus stacked-platform and approach complexity where an interchange must grade-separate |

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

Depot costs were also brought onto the same direct-procurement basis because
the station/track recalculation otherwise left the fixed-asset stack mixed.
The current units include the distributed overnight-stabling policy: healthy
trainsets can sleep at powered stations, so layups are station stabling kits
and the main depot no longer needs parking capacity for every set.

| Depot archetype | Unit |
|---|---:|
| `main-heavy` | 8.0 M USD |
| `secondary-medium` | 3.0 M USD |
| `layup-minimal` | 400 k USD |

Station/depot charging microgrid interface:

| Stop archetype | Unit |
|---|---:|
| `halt` | 0 USD unless energy-model promoted |
| `standard` | 100 k USD |
| `major` | 100 k USD |
| `terminal` | 100 k USD |
| `interchange` | 100 k USD |
| `interchange-elevated` | 125 k USD |
| `depot-terminal` | 250 k USD |

This bucket includes the standard 500 kWh stationary-LFP module, shared
500 kW DC/DC cabinet, conductive contacts, switchgear, short cable runs,
protection/control, and a local installation allowance. PV panels, train
batteries, depot-scale storage, building/civil work, and onboard hardware are
counted elsewhere. The equipment-only RFQ target is $55k–75k per normal site;
the planning unit carries integration and uncertainty.

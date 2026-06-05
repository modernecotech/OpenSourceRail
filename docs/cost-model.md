# OpenSourceRail Cost Model

This file is the audit trail for the planning-grade costs emitted into
each city `design.toml` and README. The source currency is now **USD**,
matching marketplace listings and `lib/templates/country-finance.toml`.
Generated `*_eur` fields are compatibility mirrors at 0.92 USD->EUR.
The machine-readable source of truth is
[`lib/templates/capex-costs.toml`](../lib/templates/capex-costs.toml);
this document records the assumptions behind those rates.

The detailed civil marketplace anchors live in
[`docs/civil/marketplace-cost-anchors.md`](civil/marketplace-cost-anchors.md).

## Rolling Stock

Rolling stock is budgeted at the **delivered production planning unit of
1.4 M USD per self-contained car**. A trainset is `cars × 1.4 M USD`
with `*_eur` mirrors retained at 0.92 USD->EUR.

The current
[`light-metro-3car` BOM](rolling-stock/light-metro-3car/bom-skeleton.md)
still provides the raw procurement lower bound: 592,840 USD direct
material plus the BOM's 35% assembly allowance = 800,334 USD per 3-car
consist. City CAPEX no longer uses that value directly. The planning
unit now adds the production and delivery costs that a deployable train
must actually carry.

| Per-car cost bucket | Basis | Cost |
|---|---|---:|
| Direct material BOM floor | Welded frame, panels, glazing, doors, bogies, traction, batteries, HVAC, electronics, interiors | $267 k |
| Production labour + shop overhead | Cut/bend/weld, fit-out, harnessing, paint, factory supervision, utilities, rework reserve | $420 k |
| Fixtures, tooling, QA, certification evidence | Jigs/fixtures, dimensional QA, EN 15085/45545 evidence, supplier audits, homologation dossier amortisation | $310 k |
| Logistics, warranty, spares, commissioning | Freight, duty, insurance, initial spares/tools, manuals/training, site testing, acceptance runs | $403 k |
| **Total per car** | Delivered production planning unit | **$1.4 M** |

| Family | USD / trainset | EUR mirror |
|---|---:|---:|
| `urban-shuttle-1car` | $1.4 M | EUR 1.288 M |
| `tram-2car` | $2.8 M | EUR 2.576 M |
| `light-metro-3car` | $4.2 M | EUR 3.864 M |
| `metro-4car` | $5.6 M | EUR 5.152 M |
| `metro-6car` | $8.4 M | EUR 7.728 M |

The base value assumes direct procurement, local final assembly, common
bogie modules, composite non-structural cladding, COTS
doors/windows/HVAC/interior modules, open control electronics, and no
proprietary CBTC onboard bundle. It **does** include labour, shop
overhead, tooling amortisation, QA, fire/smoke/toxicity evidence,
homologation dossier allowance, freight, duty, insurance, warranty,
initial spares/tools, manuals/training, commissioning, and acceptance
testing.

The rolling-stock BOM carries line-level low/base/high bands in
[`build/bom/rolling_stock_bom.csv`](../build/bom/rolling_stock_bom.csv).
For the `light-metro-3car`, the direct-material band is
466,844-907,244 USD before labour; adding the BOM's 35% assembly
allowance gives a 630,239-1,224,779 USD marketplace-floor consist band,
with the base case landing at 800,334 USD. This remains an audit lower
bound, not the city CAPEX unit.

## Railway Production Plant

Each city also carries a separate local railway production-plant setup
allowance. The base case is **100 k USD per vehicle/car module**, not
per trainset; the earlier **200 k USD per vehicle/car module** value is
kept as a high sensitivity check rather than the default.

This line covers lean local production/assembly setup: basic tooling,
fixtures, plant services, commissioning bay setup, material handling,
and production-readiness work. It is deliberately separate from the
delivered trainset unit above, so procurement costs and city plant setup
remain auditable instead of being hidden in one large rolling-stock
number.

| Example | Base plant allowance | High sensitivity |
|---|---:|---:|
| 1-car vehicle module | $100 k | $200 k |
| 3-car `light-metro-3car` trainset | $300 k | $600 k |
| 55 x 3-car trainsets | $16.5 M | $33.0 M |

## Civil Works

Civil work is costed as a direct-procurement floor for standard-gauge,
double-track OSR alignments:

| Civil class | Unit cost | Included scope |
|---|---:|---|
| At-grade | $3.0 M / route-km | UIC60 rail, ballastless slab/embedded trackform, direct-fixation fasteners, drainage, cable troughs, local installation |
| Elevated | $12.0 M / route-km | Repeatable precast guideway spans, piers, foundations, bearings, parapets, deck slab/trackform, erection |
| Bridge | $18.0 M / route-km | Longer-span/water-crossing version of the elevated stack with heavier foundation and protection allowance |
| Elevated-interchange premium | $4.5 M / site | Added stacked-platform and approach complexity where an interchange must grade-separate |

These values are intentionally below turnkey metro-bid benchmarks because
OSR excludes tunnels, overhead catenary, proprietary signalling civil
plant, bespoke station architecture, and contractor-led EPC margin.

## Stations

Station costs are prefab portal-frame canopy + precast platform edge +
ordinary median/platform access works + commodity vertical circulation +
simple MEP/signs/CCTV/fare gates. Standard and larger urban stations
include a covered pedestrian overbridge or concourse to reach central
platforms safely from both sides of the street or corridor; halts carry a
smaller protected-crossing/compact-access allowance.

| Station archetype | Unit cost |
|---|---:|
| `halt` | $600 k |
| `standard` | $2.5 M |
| `major` | $4.5 M |
| `terminal` | $4.5 M |
| `depot-terminal` | $5.0 M |
| `interchange` | $8.0 M |
| `interchange-elevated` | $12.0 M |

## Depots

| Depot archetype | Unit cost |
|---|---:|
| `main-heavy` | $12.0 M |
| `secondary-medium` | $7.0 M |
| `layup-minimal` | $2.0 M |

Depot scope is at-grade portal-frame workshop sheds, pit tracks, stinger
tracks, portable wheel lathe allowance, local PV/storage tie-in, and no
overhead bridge crane or traction substation.

## Charging Microgrids

There is no route traction-power system in the OSR baseline: no OCS,
third rail, feeder substations, or continuous traction distribution
along the railway. The energy infrastructure cost in city designs is
therefore **station/depot charging microgrid interface CAPEX**.

| Station archetype | Unit cost | Included scope |
|---|---:|---|
| `halt` | $120 k | 250 kW class charger, local protection, compact LV tie |
| `standard` | $250 k | 500 kW class conductive charger, switchgear, inverter interface |
| `major` | $450 k | Larger queueing/anchor-stop charger and buffer tie |
| `terminal` | $500 k | End-of-line charger with higher turnback utilization |
| `interchange` | $700 k | Multi-platform charger/switchgear allowance |
| `interchange-elevated` | $850 k | Elevated multi-platform charger/switchgear allowance |
| `depot-terminal` | $1.0 M | Passenger-stop charger plus depot/yard charging interface |

Station PV canopies, large stationary Na-ion packs, depot buildings,
and train batteries are **not** re-billed here. They appear in station,
energy-site/depot, and rolling-stock scopes respectively.

## Train-Control Wayside

Residual train-control wayside is budgeted at **$50 k per route-km**.
The expensive ATP/ATO function lives onboard in the trainset cost. The
wayside scope is sparse W-Nodes at switches/stations, passive balises,
validation beacons, LoRa gateways, and OCC interfaces.

## Revenue Neutrality

City READMEs now include a post-opening operating-neutral revenue case. The
model keeps a 5% median-income monthly pass as the affordability marker,
uses a 6% monthly-pass fare for the break-even case, expands daily
ridership from the generated catchment-based planning bracket, and adds
station shop leases plus advertising boards. The operating-neutral column
solves the daily paid trips
needed so:

```text
farebox + station-shop leases + advertising
= annual OPEX
```

Construction-period equity, interest-only grace payments, and post-grace
debt service remain public capital commitments; the operating-neutral
case applies only to steady-state operations after opening.

## EPC

EPC integration and project management is **7% of subtotal**:

```text
civil + stations + depots + rolling_stock
+ railway_production_plant
+ residual_train_control_wayside + charging_microgrids
```

Country labour/material multipliers are applied downstream through
`lib/templates/country-costs.toml` when a local tender view is needed.

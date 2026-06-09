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

Station costs are prefab portal-frame canopy + ground-level platform
slab/guideway channel + direct pedestrian access + simple
MEP/signs/CCTV/fare gates. Overbridges, lifts, stairs, and concourses
are not the default at-grade station assumption; they appear only where
an elevated/stacked interchange or local road-barrier override requires
them.

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

## Dedicated Solar Plant

Generated city READMEs now add a separate utility-scale solar plant
or contracted offsite solar PPA asset when the timetable traction-energy
model exceeds station/depot PV generation. The plant is sized from the
annual shortfall after on-site PV, with a **115% planning coverage
margin**, and uses:

| Item | Planning rate |
|---|---:|
| Utility PV field | $700/kW |
| Grid interconnection / PPA tie-in | $100/kW |
| Annual plant O&M | 1.5% of plant CAPEX |

This plant is carried as infrastructure CAPEX. Its O&M is carried in
annual traction-energy OPEX; grid/PPA energy purchases are charged only
for any residual import after on-site PV plus the dedicated plant.

## Train-Control Wayside

Residual train-control wayside is budgeted at **$50 k per route-km**.
The expensive ATP/ATO function lives onboard in the trainset cost. The
wayside scope is sparse W-Nodes at switches/stations, passive balises,
validation beacons, LoRa gateways, and OCC interfaces.

## Revenue Neutrality

City READMEs now include a post-opening operating-neutral revenue case. The
model uses an 8% median-income monthly pass for the stronger service/revenue
case, derives annual paid trips from practical system capacity and the
configured low/high `capacity_utilization_*` bracket, and adds station
shop leases plus advertising boards. The operating-neutral column solves
the capacity utilisation needed so:

```text
farebox + station-shop leases + advertising
= annual OPEX
```

OPEX uses the generated fleet schedule for train-km. On-site PV
generation offsets traction demand first, the dedicated solar plant
covers the remaining planned shortfall, and only residual import is
charged as grid/PPA energy using `grid_energy_usd_per_kwh` from
`lib/templates/country-finance.toml`. Driverless labour is no longer a
flat route-km scalar: the README roster scales with service hours,
lines, revenue fleet, station archetypes, high-case paid trips, annual
train-km, depots, and the RFC 0015 shift of safety staff from train cabs
to OCC and platform posts.

Construction-period equity and interest-only grace payments on the
repayable tranche remain public capital commitments. The base finance
stack assumes **no climate/development grant**: 20% government equity
during construction and 80% green concessional loan. The operating-neutral
case applies only to steady-state operations after opening. Where the
capacity-use scenario produces revenue above OPEX, that
operating surplus is netted against repayable-debt support in the
government commitment summary; the gross post-grace debt-service figure
remains visible in the CAPEX funding stack.

## Broad Economic Benefits

Generated city READMEs include a `Broad economic benefits` screening
section sourced from `lib/templates/economic-benefits.toml`. It is not a
formal benefit-cost analysis; it is a transparent first-pass calculation
for channels that matter to cities and development lenders but do not
appear as railway revenue.

The annual benefit/activity proxy quantifies:

| Channel | Model basis |
|---|---|
| Travel time + reliability | Annual paid trips from capacity use × minutes saved × median-income value-of-time proxy |
| Congestion relief | Paid trips × average trip length × road mode-shift share ÷ vehicle occupancy |
| Environmental effect | Avoided road CO2e minus rail residual-grid CO2e, valued with the social-carbon proxy |
| Local road externalities | Avoided road vehicle-km × air/noise/safety proxy |
| Commerce and entertainment | Relevant trip shares × a median-income local-spend proxy |

The access table reports education, healthcare, commerce, and
entertainment/community access-events per year. It uses station anchors
(`anchor_kind` / `anchor_name`) where available, with conservative base
shares so sparse-OSM cities do not report zero service-access benefit.

The CAPEX recirculation table estimates how much of the initial capital
programme is retained locally through civil works, station fabrication,
depot works, railway production-plant setup, rolling-stock assembly,
charging microgrids, EPC labour, and solar-plant delivery. The retained
CAPEX is then multiplied by the construction local-supplier / wage
multiplier and converted to approximate construction job-years using the
country median-income table. These rows are economic-activity indicators,
not fiscal income.

## EPC

EPC integration and project management is **7% of subtotal**:

```text
civil + stations + depots + rolling_stock
+ railway_production_plant
+ residual_train_control_wayside + charging_microgrids
```

Dedicated solar plant CAPEX is then added as a separate infrastructure
bucket when the generated energy plan requires it.

Country labour/material multipliers are applied downstream through
`lib/templates/country-costs.toml` when a local tender view is needed.

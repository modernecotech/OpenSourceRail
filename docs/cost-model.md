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

Rolling stock is budgeted at the **marketplace-BOM floor of 267 k USD per
self-contained car**. A trainset is simply `cars × 266,778 USD`
(`cars × 245,436 EUR` in the compatibility mirror).

The value is derived from the current
[`light-metro-3car` BOM](rolling-stock/light-metro-3car/bom-skeleton.md):
592,840 USD direct material plus the BOM's 35% assembly allowance =
800,334 USD per 3-car consist.

| Bucket | Base | Low | High | Notes |
|---|---:|---:|---:|---|
| Body shell, glazing, doors, interior | $106 k | $83 k | $166 k | Welded steel frame, composite cladding, COTS doors/windows/interior, articulation share |
| Bogies and brakes | $51 k | $41 k | $75 k | Two 2-axle bogies per car, wheelsets, suspension, discs, pads, sensors |
| Traction, battery, HVAC, solar + charging | $93 k | $73 k | $142 k | PMSM motors, gearbox, SiC inverter, 120 kWh pack share, roof PV, charge hardware |
| Electronics and train-control | $16 k | $12 k | $23 k | T-ECU/S, T-ECU/A, T-OBS sensors, radios, cameras, PIS, event recorder |
| Accessibility and safety kit | $1 k | $1 k | $2 k | Passenger call buttons, signs, emergency lighting, first-aid/fire kit |
| **Total** | **$267 k** | **$210 k** | **$409 k** | Marketplace listed-price floor after assembly allowance |

The base value assumes direct procurement, local cut/bend/weld final
assembly, common bogie modules, composite non-structural cladding,
COTS doors/windows/HVAC/interior modules, open control electronics,
and no proprietary CBTC onboard bundle. It does **not** include freight,
duty, rail fire/smoke/toxicity evidence, homologation, warranty, or
supplier qualification.

The rolling-stock BOM carries line-level low/base/high bands in
[`build/bom/rolling_stock_bom.csv`](../build/bom/rolling_stock_bom.csv).
For the `light-metro-3car`, the direct-material band is
466,844-907,244 USD before labour; adding the BOM's 35% assembly
allowance gives a 630,239-1,224,779 USD marketplace-floor consist band,
with the base case landing at 800,334 USD.

## Civil Works

Civil work is costed as a direct-procurement floor for standard-gauge,
double-track OSR alignments:

| Civil class | Unit cost | Included scope |
|---|---:|---|
| At-grade | $2.0 M / route-km | UIC60 rail, concrete sleepers, clips/pads/baseplates, ballast, drainage, cable troughs, local installation |
| Elevated | $9.0 M / route-km | Repeatable precast guideway spans, piers, foundations, bearings, parapets, trackform, erection |
| Bridge | $13.0 M / route-km | Longer-span/water-crossing version of the elevated stack with heavier foundation and protection allowance |
| Elevated-interchange premium | $4.5 M / site | Added stacked-platform and approach complexity where an interchange must grade-separate |

These values are intentionally below turnkey metro-bid benchmarks because
OSR excludes tunnels, overhead catenary, proprietary signalling civil
plant, bespoke station architecture, and contractor-led EPC margin.

## Stations

Station costs are prefab portal-frame canopy + precast platform edge +
commodity vertical circulation + simple MEP/signs/CCTV/fare gates.

| Station archetype | Unit cost |
|---|---:|
| `halt` | $300 k |
| `standard` | $800 k |
| `major` | $1.6 M |
| `terminal` | $1.4 M |
| `depot-terminal` | $2.0 M |
| `interchange` | $2.5 M |
| `interchange-elevated` | $3.5 M |

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
+ residual_train_control_wayside + charging_microgrids
```

Country labour/material multipliers are applied downstream through
`lib/templates/country-costs.toml` when a local tender view is needed.

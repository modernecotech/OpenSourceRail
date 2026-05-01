# OpenSourceRail Cost Model

This file is the audit trail for the planning-grade costs emitted into
each city `design.toml` and README. It is intentionally conservative
about what belongs in each bucket so the same function is not paid for
twice.

## Rolling Stock

Rolling stock is budgeted at **€1.0 M per self-contained car**. A
trainset is simply `cars × €1.0 M`.

| Bucket | Base | Low | High | Notes |
|---|---:|---:|---:|---|
| Body shell, glazing, doors, interior | €300 k | €240 k | €420 k | Welded steel frame, composite cladding, COTS doors/windows/interior |
| Bogies and brakes | €220 k | €180 k | €320 k | One powered bogie plus one trailer bogie per car |
| Traction package | €180 k | €140 k | €280 k | PMSM motors, gearbox, SiC inverter, cooling, HV contactors |
| Battery and BMS | €120 k | €90 k | €180 k | 120 kWh usable under-seat Na-ion pack |
| Driverless onboard stack | €90 k | €70 k | €160 k | T-ECU/S, T-ECU/A, T-OBS sensors, radios, event recorder |
| HVAC, auxiliaries, QA margin | €90 k | €70 k | €160 k | HVAC, lighting, PIS, wiring, assembly QA |
| **Total** | **€1.0 M** | **€790 k** | **€1.52 M** | Base is the catalogue value |

The base value assumes direct procurement, local cut/bend/weld final
assembly, common bogie modules, composite non-structural cladding,
COTS doors/windows/HVAC/interior modules, open control electronics,
and no proprietary CBTC onboard bundle. The high value is a risk
envelope for first-article procurement or low-volume import-heavy
builds.

## Charging Microgrids

There is no route traction-power system in the OSR baseline: no OCS,
third rail, feeder substations, or continuous traction distribution
along the railway. The energy infrastructure cost in city designs is
therefore **station/depot charging microgrid interface CAPEX**.

| Station archetype | Unit cost | Included scope |
|---|---:|---|
| `halt` | €125 k | 250 kW class charger, local protection, compact LV tie |
| `standard` | €250 k | 500 kW class conductive charger, switchgear, inverter interface |
| `major` | €400 k | Larger queueing/anchor-stop charger and buffer tie |
| `terminal` | €400 k | End-of-line charger with higher turnback utilization |
| `interchange` / `interchange-elevated` | €600 k | Multi-platform charger/switchgear allowance |
| `depot-terminal` | €750 k | Passenger-stop charger plus depot/yard charging interface |

Station PV canopies, large stationary Na-ion packs, depot buildings,
and train batteries are **not** re-billed here. They appear in station,
energy-site/depot, and rolling-stock scopes respectively.

## Train-Control Wayside

Residual train-control wayside is budgeted at **€15 k per route-km**.
The expensive ATP/ATO function lives onboard in the trainset cost. The
wayside scope is sparse W-Nodes at switches/stations, passive balises,
validation beacons, LoRa gateways, and OCC interfaces.

## EPC

EPC integration and project management is **7% of subtotal**:

```text
civil + stations + depots + rolling_stock
+ residual_train_control_wayside + charging_microgrids
```

Country labour/material multipliers are applied downstream through
`lib/templates/country-costs.toml`.

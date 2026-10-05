# Basra — Urban Rail Network

**Country:** IQ · **Population:** 3,955,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Basra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$19.32 bn (90.2%) of external capital** and **$23.75 bn of external interest**. Capital plus saved interest totals **$43.06 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **255.904 km to 245.947 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **105 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **428 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **428 metro-6car trainsets / 2568 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Basra rail network on OpenStreetMap](basra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 105 / 18 |
| Route length | 287.4 km double track |
| Coverage / transfer reachability | 65.9% / 81% |
| Estimated station catchment | 2,606,345 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 428 × 6-car `metro-6car` trainsets (386 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 39.7 km | 16 | 80 | S Inner ↔ N Outer |
| line-2 | 17.3 km | 8 | 37 | SE Inner ↔ N Mid |
| line-3 | 42.6 km | 17 | 85 | E Outer ↔ NW Mid |
| line-4 | 35.0 km | 12 | 65 | NW Mid ↔ E Outer |
| line-5 | 35.7 km | 14 | 70 | SW Outer ↔ NE Mid |
| line-6 | 26.4 km | 10 | 48 | NW Inner ↔ SW Mid |
| line-7 | 90.8 km | 28 | 43 | N Mid ↔ N Mid |
| **Total** | **287.4 km** | **105 unique** | **428** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,022 one-way journeys / 112,540 train-km/day |
| Annual traction demand | 1,064.7 GWh |
| Station/depot PV / storage | 59.3 MW / 442.0 MWh |
| Aggregate charging power | 176.0 MW |
| Dedicated solar plant | 490.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 16.9 km / 272 kWh |
| Lowest traversal charging margin | line-6: 185 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $9.29 bn |
| Stations | $502 M |
| Depots | $191 M |
| Rolling stock | $719 M |
| Dedicated solar plant | $393 M |
| Residual train control | $14 M |
| Charging microgrids | $36 M |
| EPC / project services | $753 M |
| **Total city programme** | **$11.90 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $1.16 bn |
| chinese export credit | $341 M |
| domestic bonds | $3.47 bn |
| government | $6.94 bn |

The procurement schedule requires **49 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$2.68 bn**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $258 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 31 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,014 assets / 5,716 tasks | [`basra-operations-manifest.json`](operations/basra-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`basra.toml`](basra.toml) | Expanded simulator scenario |
| [`basra.corridor.geojson`](basra.corridor.geojson) | GIS corridor and stations |
| [`basra.design-quality.yaml`](basra.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh basra
```

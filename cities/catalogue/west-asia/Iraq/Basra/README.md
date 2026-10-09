# Basra — Urban Rail Network

**Country:** IQ · **Population:** 3,955,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Basra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$14.90 bn (87.8%) of external capital** and **$18.32 bn of external interest**. Capital plus saved interest totals **$33.21 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **25 lines**, including **18 additional residential lines**. **83.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **255.904 km to 354.559 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **300 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**25 line-local depots** provide **972 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **972 metro-6car trainsets / 5832 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Basra rail network on OpenStreetMap](basra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 25 / 300 / 61 |
| Route length | 458.3 km double track |
| Direct transfers / reachable line pairs | 20.0% / 100.0% |
| Residents within 800 m radial station catchments | 1,532,278 (2020 raster; 66.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 972 × 6-car `metro-6car` trainsets (872 peak revenue) |
| Peak network throughput | 720,000 passengers/hour |
| Practical service capacity | 6,562,080 passenger-trips/day |
| Annual paid-trip planning range | 1197.6–1916.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 39.7 km | 26 | 94 | S Mid ↔ N Outer |
| line-2 | 17.3 km | 10 | 41 | SE Inner ↔ N Mid |
| line-3 | 42.6 km | 25 | 95 | E Outer ↔ NW Mid |
| line-4 | 35.0 km | 22 | 79 | NW Inner ↔ E Outer |
| line-5 | 35.4 km | 25 | 86 | SW Outer ↔ E Mid |
| line-6 | 26.4 km | 18 | 68 | N Inner ↔ SW Mid |
| line-7 | 90.5 km | 52 | 51 | N Mid ↔ N Mid |
| line-8 |  9.0 km | 6 | 24 | NE Inner ↔ SE Inner |
| line-9 | 10.9 km | 7 | 27 | SW Mid ↔ W Mid |
| line-10 |  7.2 km | 7 | 25 | NW Inner ↔ N Inner |
| line-11 |  5.9 km | 5 | 19 | SE Inner ↔ S Inner |
| line-12 |  6.2 km | 5 | 17 | N Outer ↔ NW Outer |
| line-13 |  9.8 km | 8 | 30 | N Mid ↔ N Mid |
| line-14 |  9.4 km | 7 | 27 | E Inner ↔ NE Inner |
| line-15 | 15.2 km | 9 | 36 | SW Inner ↔ W Mid |
| line-16 |  5.8 km | 4 | 15 | SW Mid ↔ S Mid |
| line-17 |  6.4 km | 5 | 19 | SE Inner ↔ S Inner |
| line-18 |  5.9 km | 4 | 16 | N Outer ↔ N Outer |
| line-19 |  8.7 km | 7 | 26 | N Mid ↔ N Outer |
| line-20 |  7.6 km | 4 | 18 | NE Inner ↔ E Inner |
| line-21 | 10.0 km | 9 | 32 | S Inner ↔ N Inner |
| line-22 | 13.8 km | 9 | 31 | NW Inner ↔ NW Mid |
| line-23 | 14.4 km | 9 | 32 | E Outer ↔ SE Mid |
| line-24 |  6.6 km | 5 | 17 | SW Mid ↔ S Outer |
| line-25 | 18.7 km | 12 | 47 | SW Mid ↔ W Mid |
| **Total** | **458.3 km** | **300 unique** | **972** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 11,392 one-way journeys / 192,068 train-km/day |
| Annual traction demand | 1,817.1 GWh |
| Station/depot PV / storage | 186.5 MW / 1,410.0 MWh |
| Aggregate charging power | 460.0 MW |
| Dedicated solar plant | 739.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-25: 18.7 km / 302 kWh |
| Lowest traversal charging margin | line-9: 68 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.55 bn |
| Stations | $1.41 bn |
| Depots | $546 M |
| Rolling stock | $1.63 bn |
| Dedicated solar plant | $592 M |
| Residual train control | $23 M |
| Charging microgrids | $93 M |
| EPC / project services | $578 M |
| **Total city programme** | **$9.43 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $877 M |
| chinese export credit | $663 M |
| domestic bonds | $2.63 bn |
| government | $5.26 bn |

The procurement schedule requires **104 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$1.21 bn**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $265 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 60 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,597 assets / 13,937 tasks | [`basra-operations-manifest.json`](operations/basra-operations-manifest.json) |

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

# Najaf — Urban Rail Network

**Country:** IQ · **Population:** 1,540,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Najaf-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.49 bn (88.6%) of external capital** and **$7.98 bn of external interest**. Capital plus saved interest totals **$14.47 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **16 lines**, including **10 additional residential lines**. **74.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **128.166 km to 145.187 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **152 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**16 line-local depots** provide **439 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **439 metro-4car trainsets / 1756 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Najaf rail network on OpenStreetMap](najaf-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 16 / 152 / 31 |
| Route length | 197.8 km double track |
| Direct transfers / reachable line pairs | 25.8% / 100.0% |
| Residents within 800 m radial station catchments | 780,012 (2020 raster; 57.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 439 × 4-car `metro-4car` trainsets (389 peak revenue) |
| Peak network throughput | 307,200 passengers/hour |
| Practical service capacity | 2,767,680 passenger-trips/day |
| Annual paid-trip planning range | 505.1–808.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.3 km | 15 | 48 | S Mid ↔ NE Mid |
| line-2 | 32.4 km | 26 | 81 | SE Outer ↔ NW Mid |
| line-3 | 16.0 km | 12 | 40 | N Inner ↔ SE Mid |
| line-4 | 23.7 km | 16 | 51 | E Inner ↔ NW Outer |
| line-5 | 27.4 km | 16 | 56 | SW Outer ↔ SE Mid |
| line-6 | 28.4 km | 26 | 21 | W Inner ↔ W Inner |
| line-7 |  4.8 km | 3 | 12 | W Inner ↔ SW Inner |
| line-8 |  4.6 km | 3 | 12 | S Inner ↔ SW Inner |
| line-9 |  5.7 km | 7 | 21 | NW Mid ↔ NW Inner |
| line-10 |  3.0 km | 3 | 11 | NW Inner ↔ N Inner |
| line-11 |  9.6 km | 5 | 19 | SE Outer ↔ SE Outer |
| line-12 |  5.9 km | 4 | 13 | NW Mid ↔ N Inner |
| line-13 |  4.6 km | 6 | 18 | W Inner ↔ NW Inner |
| line-14 |  4.3 km | 3 | 12 | E Inner ↔ E Mid |
| line-15 |  3.5 km | 4 | 13 | E Inner ↔ NE Inner |
| line-16 |  3.6 km | 3 | 11 | W Inner ↔ NW Mid |
| **Total** | **197.8 km** | **152 unique** | **439** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 7,208 one-way journeys / 85,382 train-km/day |
| Annual traction demand | 538.5 GWh |
| Station/depot PV / storage | 115.1 MW / 815.5 MWh |
| Aggregate charging power | 199.5 MW |
| Dedicated solar plant | 150.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-11: 9.6 km / 103 kWh |
| Lowest traversal charging margin | line-11: 34 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.90 bn |
| Stations | $973 M |
| Depots | $269 M |
| Rolling stock | $492 M |
| Dedicated solar plant | $120 M |
| Residual train control | $9.9 M |
| Charging microgrids | $42 M |
| EPC / project services | $258 M |
| **Total city programme** | **$4.07 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $389 M |
| chinese export credit | $181 M |
| domestic bonds | $1.17 bn |
| government | $2.33 bn |

The procurement schedule requires **56 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$877 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $115 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,277 assets / 6,627 tasks | [`najaf-operations-manifest.json`](operations/najaf-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`najaf.toml`](najaf.toml) | Expanded simulator scenario |
| [`najaf.corridor.geojson`](najaf.corridor.geojson) | GIS corridor and stations |
| [`najaf.design-quality.yaml`](najaf.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh najaf
```

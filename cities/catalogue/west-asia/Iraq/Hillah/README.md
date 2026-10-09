# Hillah — Urban Rail Network

**Country:** IQ · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hillah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.03 bn (88.3%) of external capital** and **$3.73 bn of external interest**. Capital plus saved interest totals **$6.76 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **70.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **42.347 km to 55.069 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **67 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **381 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **381 light-metro-3car trainsets / 1143 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Hillah rail network on OpenStreetMap](hillah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 67 / 11 |
| Route length | 107.0 km double track |
| Direct transfers / reachable line pairs | 23.6% / 100.0% |
| Residents within 800 m radial station catchments | 500,443 (2020 raster; 55.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 381 × 3-car `light-metro-3car` trainsets (340 peak revenue) |
| Peak network throughput | 158,400 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.9 km | 10 | 60 | NE Outer ↔ S Outer |
| line-2 | 17.8 km | 11 | 63 | N Outer ↔ SE Inner |
| line-3 | 18.1 km | 12 | 61 | W Mid ↔ E Outer |
| line-4 | 10.0 km | 6 | 37 | SW Inner ↔ NW Mid |
| line-5 |  8.0 km | 5 | 29 | W Mid ↔ SW Inner |
| line-6 | 10.0 km | 6 | 37 | W Mid ↔ NW Outer |
| line-7 |  4.0 km | 3 | 15 | SE Mid ↔ E Mid |
| line-8 |  2.9 km | 2 | 11 | NE Mid ↔ NE Mid |
| line-9 |  4.5 km | 3 | 17 | NE Mid ↔ E Mid |
| line-10 |  4.3 km | 3 | 16 | S Outer ↔ S Outer |
| line-11 |  9.6 km | 6 | 35 | W Mid ↔ SW Outer |
| **Total** | **107.0 km** | **67 unique** | **381** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 49,751 train-km/day |
| Annual traction demand | 235.3 GWh |
| Station/depot PV / storage | 66.1 MW / 458.5 MWh |
| Aggregate charging power | 24.0 MW |
| Dedicated solar plant | 47.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 10.0 km / 80 kWh |
| Lowest traversal charging margin | line-10: 11 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $936 M |
| Stations | $274 M |
| Depots | $184 M |
| Rolling stock | $343 M |
| Dedicated solar plant | $38 M |
| Residual train control | $5.3 M |
| Charging microgrids | $5.0 M |
| EPC / project services | $122 M |
| **Total city programme** | **$1.91 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $181 M |
| chinese export credit | $103 M |
| domestic bonds | $542 M |
| government | $1.08 bn |

The procurement schedule requires **42 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$607 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $60 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 778 assets / 4,584 tasks | [`hillah-operations-manifest.json`](operations/hillah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hillah.toml`](hillah.toml) | Expanded simulator scenario |
| [`hillah.corridor.geojson`](hillah.corridor.geojson) | GIS corridor and stations |
| [`hillah.design-quality.yaml`](hillah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hillah
```

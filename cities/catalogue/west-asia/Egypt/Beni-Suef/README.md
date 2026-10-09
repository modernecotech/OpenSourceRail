# Beni-Suef — Urban Rail Network

**Country:** EG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beni-Suef-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.71 bn (88.5%) of external capital** and **$2.10 bn of external interest**. Capital plus saved interest totals **$3.81 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **54.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **39.986 km to 47.756 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **37 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **202 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **202 light-metro-3car trainsets / 606 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Beni-Suef rail network on OpenStreetMap](beni-suef-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 37 / 8 |
| Route length | 56.8 km double track |
| Direct transfers / reachable line pairs | 38.1% / 100.0% |
| Residents within 800 m radial station catchments | 391,606 (2020 raster; 42.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 202 × 3-car `light-metro-3car` trainsets (179 peak revenue) |
| Peak network throughput | 100,800 passengers/hour |
| Practical service capacity | 937,440 passenger-trips/day |
| Annual paid-trip planning range | 171.1–273.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.2 km | 6 | 38 | S Outer ↔ E Mid |
| line-2 | 10.2 km | 8 | 36 | N Inner ↔ S Outer |
| line-3 |  7.8 km | 6 | 27 | W Inner ↔ SE Mid |
| line-4 |  2.7 km | 2 | 11 | NW Inner ↔ E Inner |
| line-5 | 12.6 km | 7 | 45 | W Inner ↔ NE Outer |
| line-6 |  9.1 km | 5 | 31 | N Inner ↔ NW Outer |
| line-7 |  3.2 km | 3 | 14 | S Mid ↔ S Mid |
| **Total** | **56.8 km** | **37 unique** | **202** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 26,432 train-km/day |
| Annual traction demand | 125.0 GWh |
| Station/depot PV / storage | 42.5 MW / 292.5 MWh |
| Aggregate charging power | 16.0 MW |
| Dedicated solar plant | 16.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 9.6 km / 78 kWh |
| Lowest traversal charging margin | line-4: 25 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $519 M |
| Stations | $174 M |
| Depots | $110 M |
| Rolling stock | $182 M |
| Dedicated solar plant | $13 M |
| Residual train control | $2.8 M |
| Charging microgrids | $3.4 M |
| EPC / project services | $69 M |
| **Total city programme** | **$1.07 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $223 M (20.8%) |
| Domestic / local capital | $851 M (79.2%) |
| Annual public construction commitment | $116 M / yr for 5 years |
| Annual post-grace debt service | $86 M / yr |
| External capital saved vs default turnkey sensitivity | $1.71 bn |
| Capital + lifetime external interest saved | $3.81 bn |
| Annual OPEX | $30 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 428 assets / 2,474 tasks | [`beni-suef-operations-manifest.json`](operations/beni-suef-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beni-suef.toml`](beni-suef.toml) | Expanded simulator scenario |
| [`beni-suef.corridor.geojson`](beni-suef.corridor.geojson) | GIS corridor and stations |
| [`beni-suef.design-quality.yaml`](beni-suef.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beni-suef
```

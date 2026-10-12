# Uige — Urban Rail Network

**Country:** AO · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Uige-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$337 M (88.4%) of external capital** and **$414 M of external interest**. Capital plus saved interest totals **$751 M**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **1 lines**, including **0 additional residential lines**. **14.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **12.025 km to 12.025 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **6 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**1 line-local depots** provide **39 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **39 light-metro-3car trainsets / 117 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Uige rail network on OpenStreetMap](uige-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 1 / 6 / 0 |
| Route length | 12.0 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 23,573 (2020 raster; 9.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 39 × 3-car `light-metro-3car` trainsets (35 peak revenue) |
| Peak network throughput | 14,400 passengers/hour |
| Practical service capacity | 133,920 passenger-trips/day |
| Annual paid-trip planning range | 24.4–39.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.0 km | 6 | 39 | W Outer ↔ SE Mid |
| **Total** | **12.0 km** | **6 unique** | **39** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 465 one-way journeys / 5,592 train-km/day |
| Annual traction demand | 26.5 GWh |
| Station/depot PV / storage | 6.5 MW / 42.5 MWh |
| Aggregate charging power | 3.0 MW |
| Dedicated solar plant | 9.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.0 km / 23 kWh |
| Lowest traversal charging margin | line-1: 56 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $117 M |
| Stations | $20 M |
| Depots | $17 M |
| Rolling stock | $35 M |
| Dedicated solar plant | $7.9 M |
| Residual train control | $601 k |
| Charging microgrids | $750 k |
| EPC / project services | $13 M |
| **Total city programme** | **$212 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $44 M (20.9%) |
| Domestic / local capital | $168 M (79.1%) |
| Annual public construction commitment | $24 M / yr for 5 years |
| Annual post-grace debt service | $18 M / yr |
| External capital saved vs default turnkey sensitivity | $337 M |
| Capital + lifetime external interest saved | $751 M |
| Annual OPEX | $5.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 78 assets / 462 tasks | [`uige-operations-manifest.json`](operations/uige-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`uige.toml`](uige.toml) | Expanded simulator scenario |
| [`uige.corridor.geojson`](uige.corridor.geojson) | GIS corridor and stations |
| [`uige.design-quality.yaml`](uige.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh uige
```

# Antananarivo — Urban Rail Network

**Country:** MG · **Population:** 3,058,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Antananarivo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$20.71 bn (87.4%) of external capital** and **$26.75 bn of external interest**. Capital plus saved interest totals **$47.46 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **40 lines**, including **31 additional residential lines**. **81.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **266.865 km to 406.371 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **429 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**40 line-local depots** provide **1399 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **1399 metro-6car trainsets / 8394 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Antananarivo rail network on OpenStreetMap](antananarivo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 40 / 429 / 109 |
| Route length | 544.7 km double track |
| Direct transfers / reachable line pairs | 17.3% / 100.0% |
| Residents within 800 m radial station catchments | 2,278,308 (2020 raster; 65.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 1399 × 6-car `metro-6car` trainsets (1250 peak revenue) |
| Peak network throughput | 1,152,000 passengers/hour |
| Practical service capacity | 10,579,680 passenger-trips/day |
| Annual paid-trip planning range | 1930.8–3089.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.3 km | 21 | 78 | S Mid ↔ NE Mid |
| line-2 | 24.4 km | 19 | 70 | SE Mid ↔ NW Mid |
| line-3 | 29.6 km | 20 | 71 | SW Outer ↔ E Inner |
| line-4 | 22.6 km | 18 | 64 | E Mid ↔ SW Outer |
| line-5 | 26.4 km | 17 | 65 | NW Inner ↔ S Outer |
| line-6 | 32.5 km | 22 | 81 | SE Outer ↔ W Mid |
| line-7 | 29.5 km | 19 | 69 | W Mid ↔ NE Outer |
| line-8 | 29.2 km | 26 | 89 | SE Mid ↔ NW Outer |
| line-9 | 71.7 km | 55 | 47 | W Mid ↔ W Mid |
| line-10 |  5.9 km | 5 | 19 | NW Inner ↔ N Inner |
| line-11 |  7.1 km | 8 | 27 | N Inner ↔ N Mid |
| line-12 |  8.6 km | 7 | 26 | W Inner ↔ N Inner |
| line-13 | 12.4 km | 19 | 59 | NE Inner ↔ S Mid |
| line-14 |  6.1 km | 5 | 19 | N Inner ↔ NE Mid |
| line-15 |  8.1 km | 7 | 25 | NE Mid ↔ E Inner |
| line-16 |  9.6 km | 5 | 23 | N Inner ↔ N Mid |
| line-17 |  9.1 km | 7 | 27 | NW Inner ↔ SW Inner |
| line-18 |  6.7 km | 7 | 25 | NE Mid ↔ NE Mid |
| line-19 |  7.9 km | 5 | 20 | S Mid ↔ SW Mid |
| line-20 | 11.3 km | 9 | 34 | SE Inner ↔ S Mid |
| line-21 |  8.1 km | 7 | 24 | N Inner ↔ N Mid |
| line-22 |  6.5 km | 6 | 20 | NE Mid ↔ N Mid |
| line-23 |  6.6 km | 5 | 17 | NW Mid ↔ NW Mid |
| line-24 |  9.0 km | 6 | 24 | N Mid ↔ N Mid |
| line-25 |  7.6 km | 8 | 26 | S Mid ↔ S Mid |
| line-26 | 11.1 km | 10 | 34 | NE Mid ↔ NE Outer |
| line-27 |  6.4 km | 5 | 18 | NW Mid ↔ W Inner |
| line-28 |  5.9 km | 4 | 17 | S Mid ↔ SW Mid |
| line-29 |  6.1 km | 4 | 16 | NE Mid ↔ N Mid |
| line-30 | 10.4 km | 9 | 32 | NE Inner ↔ SW Inner |
| line-31 |  6.7 km | 7 | 25 | SE Inner ↔ NW Inner |
| line-32 |  6.2 km | 6 | 20 | NW Mid ↔ NW Mid |
| line-33 |  6.2 km | 4 | 16 | NW Mid ↔ NW Outer |
| line-34 | 10.0 km | 5 | 21 | NE Mid ↔ SE Inner |
| line-35 |  7.6 km | 5 | 20 | SW Mid ↔ S Mid |
| line-36 |  8.1 km | 6 | 23 | NE Mid ↔ N Mid |
| line-37 |  8.8 km | 6 | 20 | S Outer ↔ S Mid |
| line-38 |  6.4 km | 11 | 34 | W Mid ↔ NW Mid |
| line-39 |  8.1 km | 5 | 20 | NE Mid ↔ N Outer |
| line-40 | 11.7 km | 9 | 34 | S Mid ↔ SE Inner |
| **Total** | **544.7 km** | **429 unique** | **1399** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 18,368 one-way journeys / 236,627 train-km/day |
| Annual traction demand | 2,238.7 GWh |
| Station/depot PV / storage | 300.5 MW / 2,270.0 MWh |
| Aggregate charging power | 750.0 MW |
| Dedicated solar plant | 1,123.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 11.9 km / 178 kWh |
| Lowest traversal charging margin | line-33: 94 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $5.36 bn |
| Stations | $2.73 bn |
| Depots | $830 M |
| Rolling stock | $2.35 bn |
| Dedicated solar plant | $899 M |
| Residual train control | $27 M |
| Charging microgrids | $154 M |
| EPC / project services | $802 M |
| **Total city programme** | **$13.16 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.98 bn (22.7%) |
| Domestic / local capital | $10.18 bn (77.3%) |
| Annual public construction commitment | $1.23 bn / yr for 10 years |
| Annual post-grace debt service | $1.12 bn / yr |
| External capital saved vs default turnkey sensitivity | $20.71 bn |
| Capital + lifetime external interest saved | $47.46 bn |
| Annual OPEX | $308 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 30 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 3,779 assets / 20,185 tasks | [`antananarivo-operations-manifest.json`](operations/antananarivo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`antananarivo.toml`](antananarivo.toml) | Expanded simulator scenario |
| [`antananarivo.corridor.geojson`](antananarivo.corridor.geojson) | GIS corridor and stations |
| [`antananarivo.design-quality.yaml`](antananarivo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh antananarivo
```

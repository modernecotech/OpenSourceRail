# Bamenda — Urban Rail Network

**Country:** CM · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bamenda-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.62 bn (88.3%) of external capital** and **$3.29 bn of external interest**. Capital plus saved interest totals **$5.91 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **54.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **45.381 km to 65.939 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **65 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **308 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **308 light-metro-3car trainsets / 924 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bamenda rail network on OpenStreetMap](bamenda-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 65 / 12 |
| Route length | 83.0 km double track |
| Direct transfers / reachable line pairs | 19.2% / 100.0% |
| Residents within 800 m radial station catchments | 164,160 (2020 raster; 42.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 308 × 3-car `light-metro-3car` trainsets (271 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.7 km | 13 | 61 | E Outer ↔ W Mid |
| line-2 | 14.4 km | 10 | 46 | SE Mid ↔ W Outer |
| line-3 | 10.5 km | 9 | 39 | NW Outer ↔ SW Mid |
| line-4 |  3.6 km | 3 | 14 | S Mid ↔ SW Mid |
| line-5 |  2.8 km | 2 | 11 | NW Inner ↔ S Inner |
| line-6 |  3.0 km | 3 | 14 | SW Mid ↔ SW Mid |
| line-7 |  4.6 km | 3 | 17 | NE Mid ↔ NE Outer |
| line-8 |  2.8 km | 2 | 11 | S Mid ↔ SE Inner |
| line-9 |  8.6 km | 6 | 30 | E Outer ↔ SE Mid |
| line-10 |  2.0 km | 2 | 10 | NW Mid ↔ NW Mid |
| line-11 |  8.6 km | 7 | 31 | W Inner ↔ W Mid |
| line-12 |  3.4 km | 3 | 14 | NE Inner ↔ E Mid |
| line-13 |  2.1 km | 2 | 10 | NE Mid ↔ E Mid |
| **Total** | **83.0 km** | **65 unique** | **308** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 38,613 train-km/day |
| Annual traction demand | 182.7 GWh |
| Station/depot PV / storage | 79.1 MW / 543.5 MWh |
| Aggregate charging power | 30.0 MW |
| Dedicated solar plant | 28.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 5.6 km / 42 kWh |
| Lowest traversal charging margin | line-7: 19 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $715 M |
| Stations | $324 M |
| Depots | $195 M |
| Rolling stock | $277 M |
| Dedicated solar plant | $23 M |
| Residual train control | $4.2 M |
| Charging microgrids | $6.2 M |
| EPC / project services | $106 M |
| **Total city programme** | **$1.65 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $349 M (21.1%) |
| Domestic / local capital | $1.30 bn (78.9%) |
| Annual public construction commitment | $141 M / yr for 7 years |
| Annual post-grace debt service | $115 M / yr |
| External capital saved vs default turnkey sensitivity | $2.62 bn |
| Capital + lifetime external interest saved | $5.91 bn |
| Annual OPEX | $44 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 702 assets / 3,930 tasks | [`bamenda-operations-manifest.json`](operations/bamenda-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bamenda.toml`](bamenda.toml) | Expanded simulator scenario |
| [`bamenda.corridor.geojson`](bamenda.corridor.geojson) | GIS corridor and stations |
| [`bamenda.design-quality.yaml`](bamenda.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bamenda
```

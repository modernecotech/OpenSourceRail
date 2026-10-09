# Hoima — Urban Rail Network

**Country:** UG · **Population:** 200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hoima-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.38 bn (89.3%) of external capital** and **$1.73 bn of external interest**. Capital plus saved interest totals **$3.12 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **8 lines**, including **5 additional residential lines**. **61.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **24.120 km to 39.423 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **35 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **126 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **126 tram-2car trainsets / 252 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Hoima rail network on OpenStreetMap](hoima-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 35 / 7 |
| Route length | 47.2 km double track |
| Direct transfers / reachable line pairs | 32.1% / 100.0% |
| Residents within 800 m radial station catchments | 63,064 (2020 raster; 48.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 126 × 2-car `tram-2car` trainsets (109 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 714,240 passenger-trips/day |
| Annual paid-trip planning range | 130.3–208.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.3 km | 7 | 25 | S Inner ↔ NW Outer |
| line-2 |  8.1 km | 5 | 19 | SE Outer ↔ N Inner |
| line-3 |  5.4 km | 5 | 16 | SW Inner ↔ E Mid |
| line-4 |  7.0 km | 5 | 18 | SE Mid ↔ W Inner |
| line-5 |  7.9 km | 6 | 20 | NW Mid ↔ S Mid |
| line-6 |  2.0 km | 2 | 8 | NW Outer ↔ N Mid |
| line-7 |  4.0 km | 3 | 12 | NW Inner ↔ NE Inner |
| line-8 |  2.4 km | 2 | 8 | SE Outer ↔ SE Outer |
| **Total** | **47.2 km** | **35 unique** | **126** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,720 one-way journeys / 21,931 train-km/day |
| Annual traction demand | 69.2 GWh |
| Station/depot PV / storage | 47.5 MW / 332.5 MWh |
| Aggregate charging power | 16.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 4.5 km / 22 kWh |
| Lowest traversal charging margin | line-8: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $424 M |
| Stations | $196 M |
| Depots | $108 M |
| Rolling stock | $71 M |
| Residual train control | $2.4 M |
| Charging microgrids | $3.5 M |
| EPC / project services | $56 M |
| **Total city programme** | **$860 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $165 M (19.2%) |
| Domestic / local capital | $695 M (80.8%) |
| Annual public construction commitment | $105 M / yr for 7 years |
| Annual post-grace debt service | $89 M / yr |
| External capital saved vs default turnkey sensitivity | $1.38 bn |
| Capital + lifetime external interest saved | $3.12 bn |
| Annual OPEX | $21 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 335 assets / 1,751 tasks | [`hoima-operations-manifest.json`](operations/hoima-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hoima.toml`](hoima.toml) | Expanded simulator scenario |
| [`hoima.corridor.geojson`](hoima.corridor.geojson) | GIS corridor and stations |
| [`hoima.design-quality.yaml`](hoima.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hoima
```

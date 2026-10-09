# Bloemfontein — Urban Rail Network

**Country:** ZA · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bloemfontein-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.33 bn (88.0%) of external capital** and **$2.86 bn of external interest**. Capital plus saved interest totals **$5.19 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **6 additional residential lines**. **79.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **59.903 km to 60.882 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **54 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **287 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **287 light-metro-3car trainsets / 861 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bloemfontein rail network on OpenStreetMap](bloemfontein-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 54 / 10 |
| Route length | 81.5 km double track |
| Direct transfers / reachable line pairs | 27.8% / 100.0% |
| Residents within 800 m radial station catchments | 211,850 (2020 raster; 62.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 287 × 3-car `light-metro-3car` trainsets (256 peak revenue) |
| Peak network throughput | 129,600 passengers/hour |
| Practical service capacity | 1,205,280 passenger-trips/day |
| Annual paid-trip planning range | 220.0–351.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.8 km | 15 | 80 | SE Outer ↔ N Outer |
| line-2 | 22.3 km | 13 | 76 | NW Outer ↔ S Mid |
| line-3 | 12.4 km | 8 | 42 | NE Mid ↔ SW Mid |
| line-4 |  3.5 km | 3 | 14 | SE Mid ↔ SE Mid |
| line-5 |  3.2 km | 3 | 14 | SE Mid ↔ SE Mid |
| line-6 |  4.2 km | 3 | 15 | E Inner ↔ E Inner |
| line-7 |  4.9 km | 4 | 18 | S Inner ↔ S Mid |
| line-8 |  2.5 km | 2 | 11 | E Inner ↔ NW Inner |
| line-9 |  4.6 km | 3 | 17 | W Inner ↔ NW Inner |
| **Total** | **81.5 km** | **54 unique** | **287** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,185 one-way journeys / 37,876 train-km/day |
| Annual traction demand | 179.2 GWh |
| Station/depot PV / storage | 57.9 MW / 381.5 MWh |
| Aggregate charging power | 26.0 MW |
| Dedicated solar plant | 67.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.0 km / 29 kWh |
| Lowest traversal charging margin | line-4: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $668 M |
| Stations | $242 M |
| Depots | $145 M |
| Rolling stock | $258 M |
| Dedicated solar plant | $54 M |
| Residual train control | $4.1 M |
| Charging microgrids | $5.4 M |
| EPC / project services | $93 M |
| **Total city programme** | **$1.47 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $318 M (21.6%) |
| Domestic / local capital | $1.15 bn (78.4%) |
| Annual public construction commitment | $157 M / yr for 5 years |
| Annual post-grace debt service | $118 M / yr |
| External capital saved vs default turnkey sensitivity | $2.33 bn |
| Capital + lifetime external interest saved | $5.19 bn |
| Annual OPEX | $50 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 22 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 618 assets / 3,564 tasks | [`bloemfontein-operations-manifest.json`](operations/bloemfontein-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bloemfontein.toml`](bloemfontein.toml) | Expanded simulator scenario |
| [`bloemfontein.corridor.geojson`](bloemfontein.corridor.geojson) | GIS corridor and stations |
| [`bloemfontein.design-quality.yaml`](bloemfontein.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bloemfontein
```

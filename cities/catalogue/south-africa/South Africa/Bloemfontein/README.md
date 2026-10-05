# Bloemfontein — Urban Rail Network

**Country:** ZA · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bloemfontein-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.47 bn (87.9%) of external capital** and **$1.81 bn of external interest**. Capital plus saved interest totals **$3.29 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **59.903 km to 47.177 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **23 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **183 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **183 light-metro-3car trainsets / 549 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Bloemfontein rail network on OpenStreetMap](bloemfontein-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 2 |
| Route length | 58.6 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 89,814 (2020 raster; 26.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 183 × 3-car `light-metro-3car` trainsets (165 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.8 km | 9 | 75 | SE Outer ↔ N Mid |
| line-2 | 22.3 km | 9 | 69 | NW Outer ↔ S Mid |
| line-3 | 12.4 km | 5 | 39 | NE Mid ↔ SW Mid |
| **Total** | **58.6 km** | **23 unique** | **183** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 27,227 train-km/day |
| Annual traction demand | 128.8 GWh |
| Station/depot PV / storage | 21.0 MW / 130.0 MWh |
| Aggregate charging power | 11.5 MW |
| Dedicated solar plant | 72.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.3 km / 31 kWh |
| Lowest traversal charging margin | line-3: 45 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $490 M |
| Stations | $94 M |
| Depots | $62 M |
| Rolling stock | $165 M |
| Dedicated solar plant | $58 M |
| Residual train control | $2.9 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $57 M |
| **Total city programme** | **$931 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $203 M (21.7%) |
| Domestic / local capital | $729 M (78.3%) |
| Annual public construction commitment | $99 M / yr for 5 years |
| Annual post-grace debt service | $75 M / yr |
| External capital saved vs default turnkey sensitivity | $1.47 bn |
| Capital + lifetime external interest saved | $3.29 bn |
| Annual OPEX | $29 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 333 assets / 2,080 tasks | [`bloemfontein-operations-manifest.json`](operations/bloemfontein-operations-manifest.json) |

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

# Kabul — Urban Rail Network

**Country:** AF · **Population:** 4,601,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kabul-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.61 bn (88.0%) of external capital** and **$7.25 bn of external interest**. Capital plus saved interest totals **$12.86 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **194.539 km to 170.699 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **84 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **320 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **320 metro-6car trainsets / 1920 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Kabul rail network on OpenStreetMap](kabul-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 84 / 15 |
| Route length | 195.0 km double track |
| Direct transfers / reachable line pairs | 76.2% / 100.0% |
| Residents within 800 m radial station catchments | 1,160,429 (2020 raster; 28.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 320 × 6-car `metro-6car` trainsets (288 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.5 km | 12 | 51 | NE Outer ↔ SW Mid |
| line-2 | 26.3 km | 12 | 53 | SE Mid ↔ NW Outer |
| line-3 | 18.5 km | 10 | 42 | W Mid ↔ NE Mid |
| line-4 | 26.0 km | 9 | 47 | SW Outer ↔ E Outer |
| line-5 | 29.1 km | 14 | 61 | W Mid ↔ E Outer |
| line-6 | 18.5 km | 9 | 40 | SE Outer ↔ N Inner |
| line-7 | 53.0 km | 18 | 26 | W Mid ↔ W Mid |
| **Total** | **195.0 km** | **84 unique** | **320** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,022 one-way journeys / 78,332 train-km/day |
| Annual traction demand | 741.1 GWh |
| Station/depot PV / storage | 57.5 MW / 430.0 MWh |
| Aggregate charging power | 164.0 MW |
| Dedicated solar plant | 310.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 8.7 km / 125 kWh |
| Lowest traversal charging margin | line-4: 241 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.84 bn |
| Stations | $493 M |
| Depots | $166 M |
| Rolling stock | $538 M |
| Dedicated solar plant | $248 M |
| Residual train control | $9.7 M |
| Charging microgrids | $33 M |
| EPC / project services | $216 M |
| **Total city programme** | **$3.54 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $767 M (21.6%) |
| Domestic / local capital | $2.78 bn (78.4%) |
| Annual public construction commitment | $490 M / yr for 10 years |
| Annual post-grace debt service | $450 M / yr |
| External capital saved vs default turnkey sensitivity | $5.61 bn |
| Capital + lifetime external interest saved | $12.86 bn |
| Annual OPEX | $79 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 799 assets / 4,409 tasks | [`kabul-operations-manifest.json`](operations/kabul-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kabul.toml`](kabul.toml) | Expanded simulator scenario |
| [`kabul.corridor.geojson`](kabul.corridor.geojson) | GIS corridor and stations |
| [`kabul.design-quality.yaml`](kabul.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kabul
```

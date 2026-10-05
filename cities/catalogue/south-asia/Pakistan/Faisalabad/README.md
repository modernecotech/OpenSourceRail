# Faisalabad — Urban Rail Network

**Country:** PK · **Population:** 3,556,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Faisalabad-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.34 bn (88.1%) of external capital** and **$5.44 bn of external interest**. Capital plus saved interest totals **$9.79 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **146.999 km to 132.174 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **66 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **245 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **245 metro-6car trainsets / 1470 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Faisalabad rail network on OpenStreetMap](faisalabad-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 66 / 9 |
| Route length | 150.8 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 1,435,419 (2020 raster; 28.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 245 × 6-car `metro-6car` trainsets (221 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.5 km | 11 | 52 | SW Mid ↔ NE Outer |
| line-2 | 19.5 km | 10 | 43 | NE Mid ↔ W Mid |
| line-3 | 20.3 km | 10 | 43 | SE Mid ↔ W Mid |
| line-4 | 20.9 km | 10 | 45 | NW Mid ↔ S Mid |
| line-5 | 23.4 km | 9 | 43 | N Mid ↔ SW Outer |
| line-6 | 39.2 km | 16 | 19 | W Inner ↔ W Inner |
| **Total** | **150.8 km** | **66 unique** | **245** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 61,019 train-km/day |
| Annual traction demand | 577.3 GWh |
| Station/depot PV / storage | 47.1 MW / 354.0 MWh |
| Aggregate charging power | 126.0 MW |
| Dedicated solar plant | 225.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 11.9 km / 199 kWh |
| Lowest traversal charging margin | line-5: 158 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.43 bn |
| Stations | $380 M |
| Depots | $133 M |
| Rolling stock | $412 M |
| Dedicated solar plant | $181 M |
| Residual train control | $7.5 M |
| Charging microgrids | $26 M |
| EPC / project services | $167 M |
| **Total city programme** | **$2.74 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $589 M (21.5%) |
| Domestic / local capital | $2.15 bn (78.5%) |
| Annual public construction commitment | $372 M / yr for 7 years |
| Annual post-grace debt service | $320 M / yr |
| External capital saved vs default turnkey sensitivity | $4.34 bn |
| Capital + lifetime external interest saved | $9.79 bn |
| Annual OPEX | $65 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 620 assets / 3,398 tasks | [`faisalabad-operations-manifest.json`](operations/faisalabad-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`faisalabad.toml`](faisalabad.toml) | Expanded simulator scenario |
| [`faisalabad.corridor.geojson`](faisalabad.corridor.geojson) | GIS corridor and stations |
| [`faisalabad.design-quality.yaml`](faisalabad.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh faisalabad
```

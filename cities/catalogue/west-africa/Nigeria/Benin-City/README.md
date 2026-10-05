# Benin-City — Urban Rail Network

**Country:** NG · **Population:** 1,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Benin-City-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.78 bn (88.6%) of external capital** and **$3.48 bn of external interest**. Capital plus saved interest totals **$6.26 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **103.509 km to 87.708 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **47 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **162 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **162 metro-4car trainsets / 648 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Benin-City rail network on OpenStreetMap](benin-city-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 47 / 10 |
| Route length | 105.9 km double track |
| Coverage / transfer reachability | 67.0% / 90% |
| Estimated station catchment | 1,206,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 162 × 4-car `metro-4car` trainsets (145 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.6 km | 8 | 30 | N Mid ↔ SW Mid |
| line-2 | 22.1 km | 10 | 40 | S Outer ↔ N Mid |
| line-3 | 23.7 km | 9 | 41 | NW Mid ↔ SE Outer |
| line-4 | 22.6 km | 8 | 38 | NE Outer ↔ SW Mid |
| line-5 | 24.0 km | 12 | 13 | NW Mid ↔ NW Mid |
| **Total** | **105.9 km** | **47 unique** | **162** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 43,689 train-km/day |
| Annual traction demand | 275.6 GWh |
| Station/depot PV / storage | 36.1 MW / 255.5 MWh |
| Aggregate charging power | 63.0 MW |
| Dedicated solar plant | 139.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.7 km / 147 kWh |
| Lowest traversal charging margin | line-4: 144 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $979 M |
| Stations | $256 M |
| Depots | $90 M |
| Rolling stock | $181 M |
| Dedicated solar plant | $111 M |
| Residual train control | $5.3 M |
| Charging microgrids | $13 M |
| EPC / project services | $107 M |
| **Total city programme** | **$1.74 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $358 M (20.5%) |
| Domestic / local capital | $1.38 bn (79.5%) |
| Annual public construction commitment | $205 M / yr for 7 years |
| Annual post-grace debt service | $173 M / yr |
| External capital saved vs default turnkey sensitivity | $2.78 bn |
| Capital + lifetime external interest saved | $6.26 bn |
| Annual OPEX | $41 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 426 assets / 2,292 tasks | [`benin-city-operations-manifest.json`](operations/benin-city-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`benin-city.toml`](benin-city.toml) | Expanded simulator scenario |
| [`benin-city.corridor.geojson`](benin-city.corridor.geojson) | GIS corridor and stations |
| [`benin-city.design-quality.yaml`](benin-city.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh benin-city
```

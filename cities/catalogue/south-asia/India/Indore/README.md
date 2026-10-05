# Indore — Urban Rail Network

**Country:** IN · **Population:** 3,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Indore-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.16 bn (87.8%) of external capital** and **$10.03 bn of external interest**. Capital plus saved interest totals **$18.19 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **300.920 km to 247.029 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **102 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **487 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **487 metro-6car trainsets / 2922 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Indore rail network on OpenStreetMap](indore-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 102 / 16 |
| Route length | 321.0 km double track |
| Coverage / transfer reachability | 47.6% / 43% |
| Estimated station catchment | 1,523,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 487 × 6-car `metro-6car` trainsets (441 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 35.8 km | 11 | 64 | NE Mid ↔ SW Outer |
| line-2 | 33.9 km | 11 | 65 | S Mid ↔ N Mid |
| line-3 | 34.0 km | 10 | 64 | NW Mid ↔ S Outer |
| line-4 | 34.2 km | 13 | 65 | SE Outer ↔ NW Mid |
| line-5 | 36.1 km | 11 | 70 | S Inner ↔ NE Outer |
| line-6 | 28.7 km | 9 | 54 | NW Inner ↔ E Mid |
| line-7 | 35.7 km | 12 | 65 | SW Outer ↔ NE Inner |
| line-8 | 82.8 km | 25 | 40 | NW Mid ↔ NW Mid |
| **Total** | **321.0 km** | **102 unique** | **487** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 130,043 train-km/day |
| Annual traction demand | 1,230.3 GWh |
| Station/depot PV / storage | 62.8 MW / 472.0 MWh |
| Aggregate charging power | 166.0 MW |
| Dedicated solar plant | 573.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 17.0 km / 275 kWh |
| Lowest traversal charging margin | line-6: 177 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.89 bn |
| Stations | $417 M |
| Depots | $217 M |
| Rolling stock | $818 M |
| Dedicated solar plant | $459 M |
| Residual train control | $16 M |
| Charging microgrids | $34 M |
| EPC / project services | $308 M |
| **Total city programme** | **$5.16 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.13 bn (21.9%) |
| Domestic / local capital | $4.03 bn (78.1%) |
| Annual public construction commitment | $444 M / yr for 5 years |
| Annual post-grace debt service | $319 M / yr |
| External capital saved vs default turnkey sensitivity | $8.16 bn |
| Capital + lifetime external interest saved | $18.19 bn |
| Annual OPEX | $126 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 35 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,068 assets / 6,195 tasks | [`indore-operations-manifest.json`](operations/indore-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`indore.toml`](indore.toml) | Expanded simulator scenario |
| [`indore.corridor.geojson`](indore.corridor.geojson) | GIS corridor and stations |
| [`indore.design-quality.yaml`](indore.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh indore
```

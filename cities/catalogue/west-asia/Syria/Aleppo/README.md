# Aleppo — Urban Rail Network

**Country:** SY · **Population:** 1,639,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aleppo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.78 bn (88.9%) of external capital** and **$4.89 bn of external interest**. Capital plus saved interest totals **$8.67 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **160.184 km to 129.880 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **56 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **202 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **202 metro-4car trainsets / 808 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Aleppo rail network on OpenStreetMap](aleppo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 56 / 9 |
| Route length | 159.6 km double track |
| Coverage / transfer reachability | 56.2% / 40% |
| Estimated station catchment | 921,118 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 202 × 4-car `metro-4car` trainsets (181 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.7 km | 11 | 43 | SW Outer ↔ NE Mid |
| line-2 | 24.2 km | 9 | 40 | SE Outer ↔ NW Outer |
| line-3 | 13.6 km | 5 | 24 | NE Mid ↔ SW Mid |
| line-4 | 20.7 km | 8 | 36 | W Outer ↔ E Mid |
| line-5 | 23.3 km | 8 | 38 | N Outer ↔ S Outer |
| line-6 | 54.0 km | 15 | 21 | W Mid ↔ W Mid |
| **Total** | **159.6 km** | **56 unique** | **202** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 61,643 train-km/day |
| Annual traction demand | 388.8 GWh |
| Station/depot PV / storage | 44.7 MW / 313.5 MWh |
| Aggregate charging power | 82.5 MW |
| Dedicated solar plant | 171.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 67 kWh |
| Lowest traversal charging margin | line-3: 151 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.46 bn |
| Stations | $259 M |
| Depots | $108 M |
| Rolling stock | $226 M |
| Dedicated solar plant | $137 M |
| Residual train control | $8.0 M |
| Charging microgrids | $17 M |
| EPC / project services | $146 M |
| **Total city programme** | **$2.36 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $472 M (20.0%) |
| Domestic / local capital | $1.89 bn (80.0%) |
| Annual public construction commitment | $362 M / yr for 10 years |
| Annual post-grace debt service | $333 M / yr |
| External capital saved vs default turnkey sensitivity | $3.78 bn |
| Capital + lifetime external interest saved | $8.67 bn |
| Annual OPEX | $50 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 20 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 523 assets / 2,833 tasks | [`aleppo-operations-manifest.json`](operations/aleppo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aleppo.toml`](aleppo.toml) | Expanded simulator scenario |
| [`aleppo.corridor.geojson`](aleppo.corridor.geojson) | GIS corridor and stations |
| [`aleppo.design-quality.yaml`](aleppo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh aleppo
```

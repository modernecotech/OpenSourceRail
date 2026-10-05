# Fez — Urban Rail Network

**Country:** MA · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fez-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.30 bn (89.1%) of external capital** and **$2.83 bn of external interest**. Capital plus saved interest totals **$5.14 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **106.603 km to 80.993 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **36 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **109 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **109 metro-4car trainsets / 436 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Fez rail network on OpenStreetMap](fez-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 36 / 7 |
| Route length | 92.2 km double track |
| Coverage / transfer reachability | 53.1% / 83% |
| Estimated station catchment | 690,300 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 109 × 4-car `metro-4car` trainsets (97 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.9 km | 8 | 34 | NE Mid ↔ SW Outer |
| line-2 | 15.1 km | 7 | 29 | W Mid ↔ SE Mid |
| line-3 | 17.3 km | 7 | 29 | E Outer ↔ W Inner |
| line-4 | 40.9 km | 14 | 17 | W Inner ↔ W Mid |
| **Total** | **92.2 km** | **36 unique** | **109** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 33,360 train-km/day |
| Annual traction demand | 210.4 GWh |
| Station/depot PV / storage | 29.3 MW / 206.5 MWh |
| Aggregate charging power | 52.5 MW |
| Dedicated solar plant | 86.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 67 kWh |
| Lowest traversal charging margin | line-3: 160 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $886 M |
| Stations | $187 M |
| Depots | $67 M |
| Rolling stock | $122 M |
| Dedicated solar plant | $69 M |
| Residual train control | $4.6 M |
| Charging microgrids | $11 M |
| EPC / project services | $89 M |
| **Total city programme** | **$1.44 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $281 M (19.6%) |
| Domestic / local capital | $1.15 bn (80.4%) |
| Annual public construction commitment | $100 M / yr for 5 years |
| Annual post-grace debt service | $69 M / yr |
| External capital saved vs default turnkey sensitivity | $2.30 bn |
| Capital + lifetime external interest saved | $5.14 bn |
| Annual OPEX | $38 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 312 assets / 1,628 tasks | [`fez-operations-manifest.json`](operations/fez-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fez.toml`](fez.toml) | Expanded simulator scenario |
| [`fez.corridor.geojson`](fez.corridor.geojson) | GIS corridor and stations |
| [`fez.design-quality.yaml`](fez.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fez
```

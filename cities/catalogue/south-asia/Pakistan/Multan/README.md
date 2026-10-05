# Multan — Urban Rail Network

**Country:** PK · **Population:** 2,197,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Multan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.47 bn (89.1%) of external capital** and **$3.09 bn of external interest**. Capital plus saved interest totals **$5.56 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **107.847 km to 86.305 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **39 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **128 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **128 metro-4car trainsets / 512 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Multan rail network on OpenStreetMap](multan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 39 / 8 |
| Route length | 101.6 km double track |
| Coverage / transfer reachability | 52.7% / 50% |
| Estimated station catchment | 1,157,819 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 128 × 4-car `metro-4car` trainsets (114 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.2 km | 7 | 30 | NE Outer ↔ SW Outer |
| line-2 | 16.6 km | 7 | 30 | NE Outer ↔ SW Outer |
| line-3 | 15.3 km | 5 | 25 | S Mid ↔ N Outer |
| line-4 | 14.5 km | 6 | 26 | W Mid ↔ E Outer |
| line-5 | 39.0 km | 14 | 17 | N Outer ↔ N Mid |
| **Total** | **101.6 km** | **39 unique** | **128** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 38,167 train-km/day |
| Annual traction demand | 240.7 GWh |
| Station/depot PV / storage | 35.2 MW / 251.0 MWh |
| Aggregate charging power | 58.5 MW |
| Dedicated solar plant | 76.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 78 kWh |
| Lowest traversal charging margin | line-3: 106 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $942 M |
| Stations | $194 M |
| Depots | $84 M |
| Rolling stock | $143 M |
| Dedicated solar plant | $61 M |
| Residual train control | $5.1 M |
| Charging microgrids | $12 M |
| EPC / project services | $97 M |
| **Total city programme** | **$1.54 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $300 M (19.5%) |
| Domestic / local capital | $1.24 bn (80.5%) |
| Annual public construction commitment | $212 M / yr for 7 years |
| Annual post-grace debt service | $182 M / yr |
| External capital saved vs default turnkey sensitivity | $2.47 bn |
| Capital + lifetime external interest saved | $5.56 bn |
| Annual OPEX | $35 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 352 assets / 1,857 tasks | [`multan-operations-manifest.json`](operations/multan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`multan.toml`](multan.toml) | Expanded simulator scenario |
| [`multan.corridor.geojson`](multan.corridor.geojson) | GIS corridor and stations |
| [`multan.design-quality.yaml`](multan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh multan
```

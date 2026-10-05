# Onitsha — Urban Rail Network

**Country:** NG · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Onitsha-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.57 bn (88.7%) of external capital** and **$4.48 bn of external interest**. Capital plus saved interest totals **$8.05 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **125.684 km to 107.946 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **55 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **185 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **185 metro-4car trainsets / 740 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Onitsha rail network on OpenStreetMap](onitsha-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 55 / 5 |
| Route length | 173.9 km double track |
| Coverage / transfer reachability | 65.6% / 60% |
| Estimated station catchment | 984,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 185 × 4-car `metro-4car` trainsets (165 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.8 km | 7 | 31 | W Mid ↔ E Mid |
| line-2 | 30.0 km | 9 | 48 | NW Outer ↔ SE Outer |
| line-3 | 29.0 km | 10 | 46 | SW Outer ↔ NE Outer |
| line-4 | 15.0 km | 6 | 26 | SE Outer ↔ SW Inner |
| line-5 | 82.0 km | 23 | 34 | NW Outer ↔ W Outer |
| **Total** | **173.9 km** | **55 unique** | **185** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 61,789 train-km/day |
| Annual traction demand | 389.7 GWh |
| Station/depot PV / storage | 35.5 MW / 252.5 MWh |
| Aggregate charging power | 60.0 MW |
| Dedicated solar plant | 215.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 28.3 km / 283 kWh |
| Lowest traversal charging margin | line-4: 129 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.42 bn |
| Stations | $186 M |
| Depots | $94 M |
| Rolling stock | $207 M |
| Dedicated solar plant | $172 M |
| Residual train control | $8.7 M |
| Charging microgrids | $12 M |
| EPC / project services | $135 M |
| **Total city programme** | **$2.24 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $454 M (20.3%) |
| Domestic / local capital | $1.78 bn (79.7%) |
| Annual public construction commitment | $264 M / yr for 7 years |
| Annual post-grace debt service | $222 M / yr |
| External capital saved vs default turnkey sensitivity | $3.57 bn |
| Capital + lifetime external interest saved | $8.05 bn |
| Annual OPEX | $51 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 20 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 482 assets / 2,606 tasks | [`onitsha-operations-manifest.json`](operations/onitsha-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`onitsha.toml`](onitsha.toml) | Expanded simulator scenario |
| [`onitsha.corridor.geojson`](onitsha.corridor.geojson) | GIS corridor and stations |
| [`onitsha.design-quality.yaml`](onitsha.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh onitsha
```

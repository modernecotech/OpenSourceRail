# Larkana — Urban Rail Network

**Country:** PK · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Larkana-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.20 bn (89.2%) of external capital** and **$1.50 bn of external interest**. Capital plus saved interest totals **$2.70 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **29.348 km to 24.452 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **107 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **107 light-metro-3car trainsets / 321 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Larkana rail network on OpenStreetMap](larkana-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 11 / 1 |
| Route length | 33.9 km double track |
| Coverage / transfer reachability | 44.6% / 100% |
| Estimated station catchment | 223,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 107 × 3-car `light-metro-3car` trainsets (96 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.0 km | 7 | 67 | SW Outer ↔ NE Outer |
| line-2 | 12.8 km | 4 | 40 | S Inner ↔ N Outer |
| **Total** | **33.9 km** | **11 unique** | **107** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 15,741 train-km/day |
| Annual traction demand | 74.5 GWh |
| Station/depot PV / storage | 11.8 MW / 86.0 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 25.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.8 km / 79 kWh |
| Lowest traversal charging margin | line-2: 180 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $496 M |
| Stations | $43 M |
| Depots | $39 M |
| Rolling stock | $96 M |
| Dedicated solar plant | $20 M |
| Residual train control | $1.7 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $48 M |
| **Total city programme** | **$747 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $145 M (19.4%) |
| Domestic / local capital | $602 M (80.6%) |
| Annual public construction commitment | $103 M / yr for 7 years |
| Annual post-grace debt service | $88 M / yr |
| External capital saved vs default turnkey sensitivity | $1.20 bn |
| Capital + lifetime external interest saved | $2.70 bn |
| Annual OPEX | $18 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 181 assets / 1,160 tasks | [`larkana-operations-manifest.json`](operations/larkana-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`larkana.toml`](larkana.toml) | Expanded simulator scenario |
| [`larkana.corridor.geojson`](larkana.corridor.geojson) | GIS corridor and stations |
| [`larkana.design-quality.yaml`](larkana.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh larkana
```

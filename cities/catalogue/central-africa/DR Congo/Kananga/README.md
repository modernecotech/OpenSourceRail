# Kananga — Urban Rail Network

**Country:** CD · **Population:** 1,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kananga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.26 bn (90.8%) of external capital** and **$2.92 bn of external interest**. Capital plus saved interest totals **$5.17 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **37.401 km to 32.698 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **13 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **33 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **33 metro-4car trainsets / 132 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kananga rail network on OpenStreetMap](kananga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 13 / 2 |
| Route length | 34.7 km double track |
| Coverage / transfer reachability | 71.3% / 100% |
| Estimated station catchment | 855,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 33 × 4-car `metro-4car` trainsets (28 peak revenue) |
| Peak network throughput | 38,400 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.2 km | 5 | 23 | SE Outer ↔ NW Mid |
| line-2 | 21.5 km | 8 | 10 | N Inner ↔ NW Mid |
| **Total** | **34.7 km** | **13 unique** | **33** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 698 one-way journeys / 11,137 train-km/day |
| Annual traction demand | 70.2 GWh |
| Station/depot PV / storage | 13.3 MW / 96.5 MWh |
| Aggregate charging power | 19.5 MW |
| Dedicated solar plant | 30.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.7 km / 37 kWh |
| Lowest traversal charging margin | line-2: 156 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.14 bn |
| Stations | $56 M |
| Depots | $30 M |
| Rolling stock | $37 M |
| Dedicated solar plant | $25 M |
| Residual train control | $1.7 M |
| Charging microgrids | $4.3 M |
| EPC / project services | $89 M |
| **Total city programme** | **$1.38 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $229 M (16.6%) |
| Domestic / local capital | $1.15 bn (83.4%) |
| Annual public construction commitment | $153 M / yr for 10 years |
| Annual post-grace debt service | $137 M / yr |
| External capital saved vs default turnkey sensitivity | $2.26 bn |
| Capital + lifetime external interest saved | $5.17 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 106 assets / 528 tasks | [`kananga-operations-manifest.json`](operations/kananga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kananga.toml`](kananga.toml) | Expanded simulator scenario |
| [`kananga.corridor.geojson`](kananga.corridor.geojson) | GIS corridor and stations |
| [`kananga.design-quality.yaml`](kananga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kananga
```

# Galle — Urban Rail Network

**Country:** LK · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Galle-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.34 bn (88.1%) of external capital** and **$1.68 bn of external interest**. Capital plus saved interest totals **$3.03 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **49.775 km to 39.061 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **19 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **171 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **171 light-metro-3car trainsets / 513 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Galle rail network on OpenStreetMap](galle-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 0 |
| Route length | 55.6 km double track |
| Coverage / transfer reachability | 35.7% / 0% |
| Estimated station catchment | 178,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 171 × 3-car `light-metro-3car` trainsets (154 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.5 km | 8 | 63 | SE Outer ↔ W Outer |
| line-2 | 18.9 km | 5 | 58 | NW Outer ↔ SE Outer |
| line-3 | 16.2 km | 6 | 50 | NE Outer ↔ W Mid |
| **Total** | **55.6 km** | **19 unique** | **171** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 25,868 train-km/day |
| Annual traction demand | 122.4 GWh |
| Station/depot PV / storage | 19.2 MW / 127.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 58.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 52 kWh |
| Lowest traversal charging margin | line-3: 50 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $472 M |
| Stations | $58 M |
| Depots | $59 M |
| Rolling stock | $154 M |
| Dedicated solar plant | $47 M |
| Residual train control | $2.8 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $52 M |
| **Total city programme** | **$847 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $182 M (21.5%) |
| Domestic / local capital | $665 M (78.5%) |
| Annual public construction commitment | $99 M / yr for 7 years |
| Annual post-grace debt service | $84 M / yr |
| External capital saved vs default turnkey sensitivity | $1.34 bn |
| Capital + lifetime external interest saved | $3.03 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 297 assets / 1,890 tasks | [`galle-operations-manifest.json`](operations/galle-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`galle.toml`](galle.toml) | Expanded simulator scenario |
| [`galle.corridor.geojson`](galle.corridor.geojson) | GIS corridor and stations |
| [`galle.design-quality.yaml`](galle.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh galle
```

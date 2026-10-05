# Port-Harcourt — Urban Rail Network

**Country:** NG · **Population:** 3,000,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Port-Harcourt-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.13 bn (88.9%) of external capital** and **$5.17 bn of external interest**. Capital plus saved interest totals **$9.30 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **158.976 km to 131.824 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **52 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **204 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **204 metro-4car trainsets / 816 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Port-Harcourt rail network on OpenStreetMap](port-harcourt-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 52 / 10 |
| Route length | 171.7 km double track |
| Coverage / transfer reachability | 32.0% / 100% |
| Estimated station catchment | 960,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 204 × 4-car `metro-4car` trainsets (183 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.9 km | 10 | 56 | SE Outer ↔ NW Outer |
| line-2 | 24.3 km | 9 | 40 | NE Outer ↔ SW Mid |
| line-3 | 25.4 km | 9 | 40 | S Mid ↔ N Outer |
| line-4 | 28.2 km | 8 | 43 | SE Mid ↔ N Outer |
| line-5 | 60.0 km | 16 | 25 | NW Mid ↔ NW Mid |
| **Total** | **171.7 km** | **52 unique** | **204** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 65,918 train-km/day |
| Annual traction demand | 415.8 GWh |
| Station/depot PV / storage | 37.3 MW / 261.5 MWh |
| Aggregate charging power | 69.0 MW |
| Dedicated solar plant | 230.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.7 km / 137 kWh |
| Lowest traversal charging margin | line-4: 144 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.64 bn |
| Stations | $255 M |
| Depots | $97 M |
| Rolling stock | $228 M |
| Dedicated solar plant | $184 M |
| Residual train control | $8.6 M |
| Charging microgrids | $14 M |
| EPC / project services | $157 M |
| **Total city programme** | **$2.58 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $517 M (20.0%) |
| Domestic / local capital | $2.06 bn (80.0%) |
| Annual public construction commitment | $305 M / yr for 7 years |
| Annual post-grace debt service | $257 M / yr |
| External capital saved vs default turnkey sensitivity | $4.13 bn |
| Capital + lifetime external interest saved | $9.30 bn |
| Annual OPEX | $58 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 498 assets / 2,762 tasks | [`port-harcourt-operations-manifest.json`](operations/port-harcourt-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`port-harcourt.toml`](port-harcourt.toml) | Expanded simulator scenario |
| [`port-harcourt.corridor.geojson`](port-harcourt.corridor.geojson) | GIS corridor and stations |
| [`port-harcourt.design-quality.yaml`](port-harcourt.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh port-harcourt
```

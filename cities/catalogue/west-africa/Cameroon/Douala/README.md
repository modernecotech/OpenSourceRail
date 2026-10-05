# Douala — Urban Rail Network

**Country:** CM · **Population:** 3,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Douala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.00 bn (87.7%) of external capital** and **$6.26 bn of external interest**. Capital plus saved interest totals **$11.26 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **170.992 km to 138.688 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **61 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **278 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **278 metro-6car trainsets / 1668 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Douala rail network on OpenStreetMap](douala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 61 / 8 |
| Route length | 180.6 km double track |
| Coverage / transfer reachability | 43.2% / 70% |
| Estimated station catchment | 1,684,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 278 × 6-car `metro-6car` trainsets (251 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,205,280 passenger-trips/day |
| Annual paid-trip planning range | 220.0–351.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.3 km | 12 | 60 | SE Mid ↔ NW Mid |
| line-2 | 39.2 km | 14 | 76 | NW Outer ↔ SE Mid |
| line-3 | 38.3 km | 12 | 71 | NE Mid ↔ SW Outer |
| line-4 | 27.0 km | 7 | 51 | SE Inner ↔ NW Outer |
| line-5 | 43.9 km | 16 | 20 | NE Inner ↔ N Inner |
| **Total** | **180.6 km** | **61 unique** | **278** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 73,772 train-km/day |
| Annual traction demand | 697.9 GWh |
| Station/depot PV / storage | 39.4 MW / 296.0 MWh |
| Aggregate charging power | 106.0 MW |
| Dedicated solar plant | 412.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 17.5 km / 263 kWh |
| Lowest traversal charging margin | line-4: 242 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.76 bn |
| Stations | $259 M |
| Depots | $131 M |
| Rolling stock | $467 M |
| Dedicated solar plant | $330 M |
| Residual train control | $9.0 M |
| Charging microgrids | $22 M |
| EPC / project services | $185 M |
| **Total city programme** | **$3.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $702 M (22.2%) |
| Domestic / local capital | $2.46 bn (77.8%) |
| Annual public construction commitment | $269 M / yr for 7 years |
| Annual post-grace debt service | $221 M / yr |
| External capital saved vs default turnkey sensitivity | $5.00 bn |
| Capital + lifetime external interest saved | $11.26 bn |
| Annual OPEX | $74 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 22 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 626 assets / 3,593 tasks | [`douala-operations-manifest.json`](operations/douala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`douala.toml`](douala.toml) | Expanded simulator scenario |
| [`douala.corridor.geojson`](douala.corridor.geojson) | GIS corridor and stations |
| [`douala.design-quality.yaml`](douala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh douala
```

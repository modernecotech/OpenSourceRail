# Kano — Urban Rail Network

**Country:** NG · **Population:** 4,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kano-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$10.80 bn (88.0%) of external capital** and **$13.54 bn of external interest**. Capital plus saved interest totals **$24.35 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **358.026 km to 308.746 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **131 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **635 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **635 metro-6car trainsets / 3810 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kano rail network on OpenStreetMap](kano-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 131 / 17 |
| Route length | 400.3 km double track |
| Coverage / transfer reachability | 46.7% / 33% |
| Estimated station catchment | 1,961,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 635 × 6-car `metro-6car` trainsets (572 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.0 km | 12 | 71 | W Mid ↔ E Mid |
| line-2 | 43.2 km | 15 | 81 | SE Outer ↔ NW Mid |
| line-3 | 39.8 km | 14 | 75 | SW Outer ↔ NE Mid |
| line-4 | 36.0 km | 13 | 71 | SE Outer ↔ W Mid |
| line-5 | 36.2 km | 13 | 69 | NE Outer ↔ SW Inner |
| line-6 | 31.0 km | 10 | 59 | N Inner ↔ S Mid |
| line-7 | 48.8 km | 15 | 89 | NE Outer ↔ S Mid |
| line-8 | 44.1 km | 12 | 81 | SE Inner ↔ NW Outer |
| line-9 | 83.2 km | 27 | 39 | NW Mid ↔ W Mid |
| **Total** | **400.3 km** | **131 unique** | **635** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 166,797 train-km/day |
| Annual traction demand | 1,578.0 GWh |
| Station/depot PV / storage | 77.1 MW / 574.0 MWh |
| Aggregate charging power | 232.0 MW |
| Dedicated solar plant | 676.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 19.1 km / 320 kWh |
| Lowest traversal charging margin | line-7: 213 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.95 bn |
| Stations | $518 M |
| Depots | $271 M |
| Rolling stock | $1.07 bn |
| Dedicated solar plant | $541 M |
| Residual train control | $20 M |
| Charging microgrids | $47 M |
| EPC / project services | $411 M |
| **Total city programme** | **$6.82 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.47 bn (21.6%) |
| Domestic / local capital | $5.35 bn (78.4%) |
| Annual public construction commitment | $797 M / yr for 7 years |
| Annual post-grace debt service | $673 M / yr |
| External capital saved vs default turnkey sensitivity | $10.80 bn |
| Capital + lifetime external interest saved | $24.35 bn |
| Annual OPEX | $161 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 63 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,388 assets / 8,080 tasks | [`kano-operations-manifest.json`](operations/kano-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kano.toml`](kano.toml) | Expanded simulator scenario |
| [`kano.corridor.geojson`](kano.corridor.geojson) | GIS corridor and stations |
| [`kano.design-quality.yaml`](kano.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kano
```

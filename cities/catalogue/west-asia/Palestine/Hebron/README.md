# Hebron — Urban Rail Network

**Country:** PS · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hebron-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.27 bn (88.3%) of external capital** and **$1.59 bn of external interest**. Capital plus saved interest totals **$2.85 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **52.348 km to 40.281 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **154 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **154 light-metro-3car trainsets / 462 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hebron rail network on OpenStreetMap](hebron-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 50.1 km double track |
| Coverage / transfer reachability | 48.2% / 33% |
| Estimated station catchment | 385,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 154 × 3-car `light-metro-3car` trainsets (139 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.6 km | 6 | 51 | S Outer ↔ N Mid |
| line-2 | 14.4 km | 5 | 43 | SW Mid ↔ NE Mid |
| line-3 | 19.1 km | 6 | 60 | E Outer ↔ NW Outer |
| **Total** | **50.1 km** | **17 unique** | **154** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,313 train-km/day |
| Annual traction demand | 110.3 GWh |
| Station/depot PV / storage | 18.9 MW / 126.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 41.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 9.1 km / 65 kWh |
| Lowest traversal charging margin | line-2: 50 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $443 M |
| Stations | $70 M |
| Depots | $58 M |
| Rolling stock | $139 M |
| Dedicated solar plant | $33 M |
| Residual train control | $2.5 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $50 M |
| **Total city programme** | **$796 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $168 M (21.1%) |
| Domestic / local capital | $629 M (78.9%) |
| Annual public construction commitment | $68 M / yr for 7 years |
| Annual post-grace debt service | $56 M / yr |
| External capital saved vs default turnkey sensitivity | $1.27 bn |
| Capital + lifetime external interest saved | $2.85 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 5 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 269 assets / 1,703 tasks | [`hebron-operations-manifest.json`](operations/hebron-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hebron.toml`](hebron.toml) | Expanded simulator scenario |
| [`hebron.corridor.geojson`](hebron.corridor.geojson) | GIS corridor and stations |
| [`hebron.design-quality.yaml`](hebron.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hebron
```

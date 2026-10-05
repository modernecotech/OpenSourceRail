# Patna — Urban Rail Network

**Country:** IN · **Population:** 2,520,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Patna-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.40 bn (89.1%) of external capital** and **$5.41 bn of external interest**. Capital plus saved interest totals **$9.82 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **133.021 km to 113.948 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **55 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **199 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **199 metro-4car trainsets / 796 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Patna rail network on OpenStreetMap](patna-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 55 / 9 |
| Route length | 159.5 km double track |
| Coverage / transfer reachability | 54.2% / 40% |
| Estimated station catchment | 1,365,840 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 199 × 4-car `metro-4car` trainsets (178 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.5 km | 8 | 45 | NE Mid ↔ SW Outer |
| line-2 | 18.0 km | 7 | 31 | S Mid ↔ N Mid |
| line-3 | 15.8 km | 5 | 25 | N Mid ↔ SE Mid |
| line-4 | 21.5 km | 9 | 38 | NE Mid ↔ SW Mid |
| line-5 | 24.7 km | 8 | 39 | S Inner ↔ NW Outer |
| line-6 | 52.1 km | 18 | 21 | NE Mid ↔ N Mid |
| **Total** | **159.5 km** | **55 unique** | **199** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 62,072 train-km/day |
| Annual traction demand | 391.5 GWh |
| Station/depot PV / storage | 43.8 MW / 309.0 MWh |
| Aggregate charging power | 78.0 MW |
| Dedicated solar plant | 206.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 15.7 km / 156 kWh |
| Lowest traversal charging margin | line-3: 120 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.79 bn |
| Stations | $264 M |
| Depots | $109 M |
| Rolling stock | $223 M |
| Dedicated solar plant | $165 M |
| Residual train control | $8.0 M |
| Charging microgrids | $16 M |
| EPC / project services | $169 M |
| **Total city programme** | **$2.74 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $537 M (19.6%) |
| Domestic / local capital | $2.21 bn (80.4%) |
| Annual public construction commitment | $240 M / yr for 5 years |
| Annual post-grace debt service | $170 M / yr |
| External capital saved vs default turnkey sensitivity | $4.40 bn |
| Capital + lifetime external interest saved | $9.82 bn |
| Annual OPEX | $63 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 24 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 512 assets / 2,779 tasks | [`patna-operations-manifest.json`](operations/patna-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`patna.toml`](patna.toml) | Expanded simulator scenario |
| [`patna.corridor.geojson`](patna.corridor.geojson) | GIS corridor and stations |
| [`patna.design-quality.yaml`](patna.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh patna
```

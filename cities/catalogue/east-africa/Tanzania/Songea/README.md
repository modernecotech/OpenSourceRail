# Songea — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Songea-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$261 M (89.2%) of external capital** and **$327 M of external interest**. Capital plus saved interest totals **$588 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **13.038 km to 7.794 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **5 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **28 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **28 tram-2car trainsets / 56 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Songea rail network on OpenStreetMap](songea-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 5 / 1 |
| Route length | 11.9 km double track |
| Coverage / transfer reachability | 38.3% / 100% |
| Estimated station catchment | 95,750 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 28 × 2-car `tram-2car` trainsets (24 peak revenue) |
| Peak network throughput | 19,200 passengers/hour |
| Practical service capacity | 178,560 passenger-trips/day |
| Annual paid-trip planning range | 32.6–52.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  3.8 km | 2 | 10 | SE Mid ↔ NE Outer |
| line-2 |  8.1 km | 3 | 18 | W Outer ↔ E Mid |
| **Total** | **11.9 km** | **5 unique** | **28** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 5,549 train-km/day |
| Annual traction demand | 17.5 GWh |
| Station/depot PV / storage | 10.6 MW / 81.0 MWh |
| Aggregate charging power | 2.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 8.1 km / 40 kWh |
| Lowest traversal charging margin | line-2: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $89 M |
| Stations | $19 M |
| Depots | $27 M |
| Rolling stock | $16 M |
| Residual train control | $597 k |
| Charging microgrids | $550 k |
| EPC / project services | $11 M |
| **Total city programme** | **$162 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $31 M (19.4%) |
| Domestic / local capital | $131 M (80.6%) |
| Annual public construction commitment | $15 M / yr for 7 years |
| Annual post-grace debt service | $12 M / yr |
| External capital saved vs default turnkey sensitivity | $261 M |
| Capital + lifetime external interest saved | $588 M |
| Annual OPEX | $4.3 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 0 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 62 assets / 337 tasks | [`songea-operations-manifest.json`](operations/songea-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`songea.toml`](songea.toml) | Expanded simulator scenario |
| [`songea.corridor.geojson`](songea.corridor.geojson) | GIS corridor and stations |
| [`songea.design-quality.yaml`](songea.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh songea
```

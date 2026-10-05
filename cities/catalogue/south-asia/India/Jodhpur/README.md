# Jodhpur — Urban Rail Network

**Country:** IN · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jodhpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.07 bn (89.6%) of external capital** and **$5.01 bn of external interest**. Capital plus saved interest totals **$9.08 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **123.531 km to 105.587 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **49 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **171 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **171 metro-4car trainsets / 684 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Jodhpur rail network on OpenStreetMap](jodhpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 49 / 8 |
| Route length | 136.0 km double track |
| Coverage / transfer reachability | 34.8% / 70% |
| Estimated station catchment | 452,399 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 171 × 4-car `metro-4car` trainsets (153 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.0 km | 9 | 41 | S Outer ↔ N Outer |
| line-2 | 20.3 km | 8 | 35 | W Mid ↔ NE Outer |
| line-3 | 19.6 km | 8 | 34 | S Outer ↔ NW Inner |
| line-4 | 24.7 km | 9 | 42 | SE Outer ↔ W Mid |
| line-5 | 46.4 km | 15 | 19 | NW Inner ↔ W Inner |
| **Total** | **136.0 km** | **49 unique** | **171** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 52,427 train-km/day |
| Annual traction demand | 330.7 GWh |
| Station/depot PV / storage | 36.4 MW / 257.0 MWh |
| Aggregate charging power | 64.5 MW |
| Dedicated solar plant | 131.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 11.4 km / 123 kWh |
| Lowest traversal charging margin | line-3: 160 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.73 bn |
| Stations | $227 M |
| Depots | $90 M |
| Rolling stock | $192 M |
| Dedicated solar plant | $105 M |
| Residual train control | $6.8 M |
| Charging microgrids | $13 M |
| EPC / project services | $158 M |
| **Total city programme** | **$2.53 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $475 M (18.8%) |
| Domestic / local capital | $2.05 bn (81.2%) |
| Annual public construction commitment | $222 M / yr for 5 years |
| Annual post-grace debt service | $157 M / yr |
| External capital saved vs default turnkey sensitivity | $4.07 bn |
| Capital + lifetime external interest saved | $9.08 bn |
| Annual OPEX | $57 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 445 assets / 2,406 tasks | [`jodhpur-operations-manifest.json`](operations/jodhpur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jodhpur.toml`](jodhpur.toml) | Expanded simulator scenario |
| [`jodhpur.corridor.geojson`](jodhpur.corridor.geojson) | GIS corridor and stations |
| [`jodhpur.design-quality.yaml`](jodhpur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jodhpur
```

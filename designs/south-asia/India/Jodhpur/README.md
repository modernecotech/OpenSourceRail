# Jodhpur — Urban Rail Network

**Country:** IN · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jodhpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.44 bn (88.0%) of external capital** and **$3.00 bn of external interest**. Capital plus saved interest totals **$5.43 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Jodhpur rail network on OpenStreetMap](jodhpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 52 / 7 |
| Route length | 150.2 km double track |
| Coverage / transfer reachability | 53.3% / 70% |
| Estimated station catchment | 692,900 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 175 × 4-car `metro-4car` trainsets (157 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.9 km | 9 | 42 | S Outer ↔ N Outer |
| line-2 | 21.4 km | 9 | 37 | W Mid ↔ NE Outer |
| line-3 | 22.5 km | 8 | 35 | S Outer ↔ NW Mid |
| line-4 | 26.3 km | 10 | 41 | SE Outer ↔ W Mid |
| line-5 | 51.0 km | 16 | 20 | NW Inner ↔ NW Inner |
| **Total** | **150.2 km** | **52 unique** | **175** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 57,969 train-km/day |
| Annual traction demand | 365.6 GWh |
| Station/depot PV / storage | 18.8 MW / 109.0 MWh |
| Aggregate charging power | 70.5 MW |
| Dedicated solar plant | 170.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 13.0 km / 139 kWh |
| Lowest traversal charging margin | line-3: 126 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $812 M |
| Stations | $271 M |
| Depots | $8.0 M |
| Rolling stock | $196 M |
| Dedicated solar plant | $136 M |
| Residual train control | $7.5 M |
| Charging microgrids | $15 M |
| EPC / project services | $92 M |
| **Total city programme** | **$1.54 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $332 M (21.6%) |
| Domestic / local capital | $1.21 bn (78.4%) |
| Annual public construction commitment | $133 M / yr for 5 years |
| Annual post-grace debt service | $95 M / yr |
| External capital saved vs default turnkey sensitivity | $2.44 bn |
| Capital + lifetime external interest saved | $5.43 bn |
| Annual OPEX | $35 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 463 assets / 2,006 tasks | [`jodhpur-operations-manifest.json`](operations/jodhpur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jodhpur.toml`](jodhpur.toml) | Expanded simulator scenario |
| [`jodhpur.corridor.geojson`](jodhpur.corridor.geojson) | GIS corridor and stations |
| [`jodhpur.design-quality.yaml`](jodhpur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh jodhpur
```

# Damietta — Urban Rail Network

**Country:** EG · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damietta-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$893 M (86.5%) of external capital** and **$1.10 bn of external interest**. Capital plus saved interest totals **$1.99 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Damietta rail network on OpenStreetMap](damietta-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 24 / 2 |
| Route length | 73.5 km double track |
| Coverage / transfer reachability | 71.7% / 67% |
| Estimated station catchment | 286,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 156 × 3-car `light-metro-3car` trainsets (140 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 24.1 km | 8 | 51 | N Outer ↔ S Outer |
| line-2 | 22.6 km | 7 | 47 | SE Mid ↔ NW Outer |
| line-3 | 26.8 km | 9 | 58 | SW Outer ↔ NE Outer |
| **Total** | **73.5 km** | **24 unique** | **156** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 34,176 train-km/day |
| Annual traction demand | 161.7 GWh |
| Station/depot PV / storage | 11.6 MW / 51.0 MWh |
| Aggregate charging power | 11.5 MW |
| Dedicated solar plant | 71.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-2: 56 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $217 M |
| Stations | $111 M |
| Depots | $8.0 M |
| Rolling stock | $140 M |
| Dedicated solar plant | $57 M |
| Residual train control | $3.7 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $34 M |
| **Total city programme** | **$573 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $140 M (24.3%) |
| Domestic / local capital | $434 M (75.7%) |
| Annual public construction commitment | $60 M / yr for 5 years |
| Annual post-grace debt service | $46 M / yr |
| External capital saved vs default turnkey sensitivity | $893 M |
| Capital + lifetime external interest saved | $1.99 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 304 assets / 1,467 tasks | [`damietta-operations-manifest.json`](operations/damietta-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damietta.toml`](damietta.toml) | Expanded simulator scenario |
| [`damietta.corridor.geojson`](damietta.corridor.geojson) | GIS corridor and stations |
| [`damietta.design-quality.yaml`](damietta.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh damietta
```
